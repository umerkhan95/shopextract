"""Watch mode — continuous monitoring with alerts (#13)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from urllib.parse import urlparse

from .._models import Change
from .changes import changes as detect_changes
from .snapshot import _domain_from_url, snapshot as take_snapshot

logger = logging.getLogger(__name__)

_DEFAULT_INTERVAL = 3600  # 1 hour
_DEFAULT_DB_PATH = "~/.shopextract/snapshots.db"

# Module-level alert registry: list of (domain, product_title, when, callback)
_alerts: list[tuple[str, str, Callable[[Change], bool], Callable[[Change], None]]] = []


async def watch(
    url: str,
    *,
    interval: int = _DEFAULT_INTERVAL,
    db_path: str = _DEFAULT_DB_PATH,
) -> AsyncGenerator[Change, None]:
    """Continuously monitor a store for changes.

    Takes a snapshot every `interval` seconds, yields Change
    objects when differences are detected.
    """
    domain = _domain_from_url(url)

    # Take initial snapshot
    await take_snapshot(url, db_path=db_path)
    logger.info("Watch started for %s (interval=%ds)", domain, interval)

    while True:
        await asyncio.sleep(interval)
        await take_snapshot(url, db_path=db_path)
        detected = detect_changes(domain, db_path=db_path)

        for change in detected:
            _fire_alerts(domain, change)
            yield change


def alert(
    url: str,
    product: str,
    when: Callable[[Change], bool],
    callback: Callable[[Change], None],
) -> None:
    """Register an alert for a product at a store.

    Args:
        url: Store URL to monitor.
        product: Product title to watch.
        when: Predicate that receives a Change, returns True to fire.
        callback: Called when predicate returns True.
    """
    domain = _domain_from_url(url)
    _alerts.append((domain, product.lower().strip(), when, callback))
    logger.info("Alert registered: %s / %s", domain, product)


def _fire_alerts(domain: str, change: Change) -> None:
    """Check and fire matching alerts for a change."""
    title_lower = change.title.lower().strip()
    for alert_domain, alert_product, when_fn, callback_fn in _alerts:
        if alert_domain != domain:
            continue
        if alert_product and alert_product != title_lower:
            continue
        try:
            if when_fn(change):
                callback_fn(change)
        except Exception:
            logger.exception("Alert callback failed for %s", change.title)
