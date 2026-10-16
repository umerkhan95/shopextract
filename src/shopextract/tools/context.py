"""Per-operation ownership declarations; execution and accounting remain unimplemented."""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from .runtime import Limits


class AuxiliaryOwner(Protocol):
    async def run(self, kind: Literal['resolve', 'domain'], payload: bytes,
                  context: 'OperationContext') -> bytes: ...
    async def cancel_and_reap(self, context: 'OperationContext') -> None: ...


@dataclass
class OperationBudget:
    limits: Limits
    requests_used: int = 0
    redirects_used: int = 0
    graph_bytes_reserved: int = 0


@dataclass(frozen=True)
class OperationContext:
    job_id: str
    deadline: float  # absolute monotonic deadline, never reset by nested work
    cancelled: asyncio.Event
    budget: OperationBudget
    auxiliary: AuxiliaryOwner
    observed_at: datetime  # trusted UTC source-receipt clock input
    request_accounting: object | None = None  # optional durable parent callback


class Resolver(Protocol):
    async def __call__(self, host: str, context: OperationContext) -> list[str]: ...
