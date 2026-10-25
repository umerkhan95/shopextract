"""Context-local opt-in execution limits; absent policy preserves library defaults."""
from __future__ import annotations

import asyncio
import contextvars
import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LLMBudget:
    model: str
    key: str
    temperature: float = 0.2
    max_calls: int = 1
    max_output_tokens: int = 512
    max_input_bytes: int = 8192


@dataclass(frozen=True)
class ExecutionPolicy:
    browser: bool = False
    llm: LLMBudget | None = None
    secrets: tuple[str, ...] = ()


@dataclass
class ExecutionState:
    policy: ExecutionPolicy
    deadline: float
    llm_calls: int = 0
    warnings: list[str] = field(default_factory=list)
    llm_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


_STATE = contextvars.ContextVar('shopextract_execution', default=None)


def current_state() -> ExecutionState | None:
    return _STATE.get()


def current_policy() -> ExecutionPolicy | None:
    state = current_state()
    return state.policy if state else None


def browser_allowed() -> bool:
    policy = current_policy()
    return policy is None or policy.browser


@contextmanager
def execution_policy(policy: ExecutionPolicy, timeout: float = 30):
    state = ExecutionState(policy, time.monotonic() + timeout)
    token = _STATE.set(state)
    try:
        yield state
    finally:
        _STATE.reset(token)


def safe_error(message: str) -> str:
    policy = current_policy()
    for secret in (policy.secrets if policy else ()):
        if secret:
            message = message.replace(secret, '[redacted]')
    return message


async def bounded_llm(urls: list[str]) -> list[dict]:
    state = current_state()
    if state is None or state.policy.llm is None:
        return []
    async with state.llm_lock:
        return await _bounded_llm(urls)


async def _bounded_llm(urls: list[str]) -> list[dict]:
    """Native fallback boundary: sequential capped input and explicit completions.

    Existing local endpoints may be selected, but no server/model is started.
    Counts provider submissions, including failed/cancelled submissions. Provider
    billing after cancellation is outside this operation's control.
    """
    state = current_state()
    if state is None or state.policy.llm is None:
        return []
    import httpx
    from litellm import acompletion
    from ._capture import capture

    budget = state.policy.llm
    products = []
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in urls:
            if state.llm_calls >= budget.max_calls:
                state.warnings.append('LLM call budget exhausted')
                break
            remaining = state.deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            try:
                content = bytearray()
                async with client.stream('GET', url, timeout=remaining) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        content.extend(chunk[:budget.max_input_bytes - len(content)])
                        if len(content) >= budget.max_input_bytes:
                            break
                source = content.decode('utf-8', errors='ignore')
                remaining = state.deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError()
                # No await between shared counter check/increment. A concurrent
                # nested helper may have consumed the final slot during HTTP.
                if state.llm_calls >= budget.max_calls:
                    state.warnings.append('LLM call budget exhausted')
                    break
                state.llm_calls += 1
                reply = await asyncio.wait_for(acompletion(
                    model=budget.model, api_key=budget.key or None,
                    messages=[{'role': 'system', 'content': 'Extract the main product from this page. Return only a JSON object or array of product objects with title, price, currency, image_url, product_url, sku, description, vendor, in_stock when visible. Do not invent missing facts.'},
                              {'role': 'user', 'content': source}],
                    temperature=budget.temperature, max_tokens=budget.max_output_tokens,
                    num_retries=0, timeout=remaining,
                ), timeout=remaining)
                text = reply.choices[0].message.content
                parsed = json.loads(text, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                values = parsed if isinstance(parsed, list) else [parsed]
                if not all(isinstance(item, dict) for item in values):
                    raise ValueError()
                for item in values:
                    capture(item, url, 'llm_bounded', excerpt=source)
                products.extend(values)
            except (asyncio.TimeoutError, httpx.TimeoutException):
                raise TimeoutError() from None
            except Exception:
                # Do not expose provider error bodies, credentials or prompts.
                state.warnings.append('LLM extraction failed or returned invalid product JSON')
    return products
