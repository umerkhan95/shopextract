"""Versioned opt-in maintenance goals, budgets and advisory contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Protocol

JobState = Literal['queued', 'running', 'paused', 'partial', 'completed', 'cancelled', 'failed']


class MaintenanceError(Exception):
    def __init__(self, code: str, message: str | None = None):
        self.code = code
        super().__init__(code if message is None else code + ': ' + message)


@dataclass(frozen=True)
class Budgets:
    requests: int = 20
    products: int = 100
    tokens: int = 0
    cost_micros: int = 0
    input_bytes: int = 256 * 1024
    evidence_bytes: int = 16 * 1024 * 1024
    report_bytes: int = 2 * 1024 * 1024
    attempt_seconds: float = 10


@dataclass(frozen=True)
class Goal:
    baseline: tuple[dict[str, Any], ...]
    supplier_origin: str
    product_urls: tuple[str, ...]
    deadline: str
    fields: tuple[str, ...] = ('description',)
    profiles: Mapping[str, str] = field(default_factory=dict)
    baseline_mode: Literal['supplied', 'captured'] = 'supplied'
    budgets: Budgets = field(default_factory=Budgets)
    freshness_seconds: float = 3600
    schema_version: str = '1.0'


@dataclass(frozen=True)
class AdvisorBound:
    input_tokens: int
    max_output_tokens: int
    cost_micros: int
    model: str
    price_version: str


@dataclass(frozen=True)
class AdvisorReservation:
    reservation_id: str
    bound: AdvisorBound


@dataclass(frozen=True)
class AdvisorUsage:
    input_tokens: int
    output_tokens: int
    cost_micros: int


@dataclass(frozen=True)
class AdvisorResult:
    model: str
    price_version: str
    advisory: Mapping[str, Any]
    evidence_ids: tuple[str, ...]
    usage: AdvisorUsage | None  # None explicitly means unknown; keep full reservation


class Investigator(Protocol):
    """bound is local/no-spend. Invocation must honor the accepted reservation.

    Model/price identity must equal reservation.bound; finite nonnegative known
    usage is validated against input/max-output/cost reservation. Unknown usage
    retains the complete reservation. Malformed/overrun/mismatched output never
    authorizes facts and stops further model dispatch with an explicit violation.
    """
    def bound(self, payload: Mapping[str, Any]) -> AdvisorBound: ...
    async def investigate(self, payload: Mapping[str, Any], *,
                          reservation: AdvisorReservation, timeout: float) -> AdvisorResult: ...


class RequestAccounting(Protocol):
    """Called before EVERY GuardedTransport raw dispatch, including redirects.

    Persist intent/reservation before returning. Exception prevents dispatch.
    Completion is committed with portable result/evidence; uncertain failure keeps
    reservation. Existing tool callers without this optional hook are unchanged.
    """
    def before_request(self, method: str, url: str) -> str: ...
    def after_request(self, method: str, url: str, status: int) -> None: ...


FailureHook = Callable[[str, Mapping[str, Any]], None]
