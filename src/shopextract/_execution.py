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
    progress: ProgressCheckpoint | None = None


class ProgressCheckpoint:
    """Owned accepted references; bounded portable freeze only after cancellation."""
    def __init__(self,*,max_products=1000,max_bytes=8*1024*1024,max_nodes=250000,max_depth=56):
        for value,ceiling in ((max_products,1000),(max_bytes,8*1024*1024),(max_nodes,250000),(max_depth,56)):
            if type(value) is not int or not 0<value<=ceiling:raise ValueError('Invalid checkpoint limit')
        self.max_products,self.max_bytes,self.max_nodes,self.max_depth=max_products,max_bytes,max_nodes,max_depth
        self.sources=[];self.generic=None;self.generic_views={};self.limited=False;self.attempted=set()
        self.result_platform=None;self.observation_scope='';self.restore_short_gtin=False;self.shop_url=None

    def configure_result(self,result_platform,observation_scope,restore_short_gtin=False,max_products=None,shop_url=None):
        self.result_platform=result_platform;self.observation_scope=observation_scope
        self.restore_short_gtin=restore_short_gtin;self.shop_url=shop_url
        if max_products is not None:
            if type(max_products) is not int or not 0<max_products<=1000:raise ValueError('Invalid checkpoint product limit')
            self.max_products=min(self.max_products,max_products)

    def register_source(self,rows,normalization_platform,shop_url,*,normalized=False,tier=None):
        from ._models import ExtractionTier
        if not isinstance(rows,list):raise ValueError('Checkpoint requires an accepted list')
        if any(s['rows'] is rows and s['normalized']==normalized for s in self.sources):return True
        if len(self.sources)>=8:self.limited=True;return False
        source=dict(rows=rows,platform=normalization_platform,shop_url=shop_url,normalized=normalized,tier=tier or ExtractionTier.API)
        if normalized:self.sources.insert(0,source)
        else:self.sources.append(source)
        return True

    def add_generic(self,rows,shop_url):
        from ._models import Platform,ExtractionTier
        if self.generic is None:
            candidate=[]
            if not self.register_source(candidate,self.result_platform or Platform.GENERIC,shop_url,tier=ExtractionTier.UNIFIED_CRAWL):return
            self.generic=candidate
        if not rows:return
        if shop_url not in self.generic_views and len(self.generic_views)>=self.max_products:
            self.limited=True;return
        previous=self.generic_views.get(shop_url,[])
        remaining=self.max_products-len(self.generic)+len(previous)
        if len(rows)>remaining:self.limited=True
        self.generic_views[shop_url]=rows[:remaining]
        self.generic[:]=[row for view in self.generic_views.values() for row in view]

    def snapshot(self):
        from ._models import ExtractionResult,ExtractionTier
        from ._normalize import normalize
        from ._portable import product_to_record,product_from_record
        from .export._bundle import _json_bytes
        from ._bounded_json import preflight_catalog_json
        from ._quality import QualityScorer
        from ._scope import catalog_scope
        for source in self.sources:
            payloads=[];size=nodes=0;limited=self.limited
            for row in source['rows'][:self.max_products+1]:
                if len(payloads)>=self.max_products:limited=True;break
                try:
                    product=row if source['normalized'] else normalize(row,source['platform'],self.shop_url or source['shop_url'],restore_short_gtin=self.restore_short_gtin)
                    if product is None:continue
                    payload=_json_bytes(product_to_record(product))
                    if size+len(payload)>self.max_bytes:limited=True;break
                    shape=preflight_catalog_json(payload)
                    if nodes+shape.nodes>self.max_nodes or shape.depth>self.max_depth:limited=True;break
                    payloads.append(payload);size+=len(payload);nodes+=shape.nodes
                except (ValueError,TypeError,AttributeError,ArithmeticError,RecursionError):
                    limited=True
            if not payloads:continue
            products=[product_from_record(json.loads(payload)) for payload in payloads]
            platform=self.result_platform or source['platform'];tier=source['tier']
            raw=[p.raw_data for p in products]
            attempted=1 if tier==ExtractionTier.API else max(1,len(self.attempted))
            source_urls={p.raw_data.get('_capture',{}).get('url') for p in products}
            return ExtractionResult(products=products,raw_products=raw,platform=platform,tier=tier,
                observation_scope=self.observation_scope or catalog_scope(source['shop_url'],platform),
                quality_score=QualityScorer().score_batch(raw),urls_attempted=attempted,
                urls_succeeded=1 if tier==ExtractionTier.API else min(attempted,len(source_urls)),
                catalog_complete=False,errors=['Operation timed out; accepted bounded checkpoint retained'],
                incompleteness_reasons=['operation_timeout']+(['checkpoint_budget_reached'] if limited else []))
        return None


def configure_progress_result(platform,scope,*,restore_short_gtin=False,shop_url=None):
    state=current_state()
    if state is not None and state.progress is not None:
        state.progress.configure_result(platform,scope,restore_short_gtin=restore_short_gtin,shop_url=shop_url)


def register_progress_source(rows,platform,shop_url,*,normalized=False,tier=None):
    state=current_state()
    if state is not None and state.progress is not None:
        state.progress.register_source(rows,platform,shop_url,normalized=normalized,tier=tier)


def record_progress_rows(rows,shop_url):
    state=current_state()
    if state is not None and state.progress is not None:state.progress.add_generic(rows,shop_url)


def record_progress_attempt(url):
    state=current_state()
    if state is not None and state.progress is not None and len(state.progress.attempted)<1000:state.progress.attempted.add(url)


_STATE = contextvars.ContextVar('shopextract_execution', default=None)


def current_state() -> ExecutionState | None:
    return _STATE.get()


def remaining_execution_seconds():
    """Return the owned operation budget, or None for legacy unowned calls."""
    state=current_state()
    return max(0.0,state.deadline-time.monotonic()) if state is not None else None


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
        state.progress=None
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
