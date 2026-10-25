"""Independent live coverage oracle and explicit partial-to-complete fault check."""
from dataclasses import replace

from tests.test_woo_tree_acceptance import acquire, entry, page
from tests.woo_tree_live_driver import coverage_check
from shopextract.categories.woo_tree import WooTreeLimits


async def test_live_oracle_checks_complete_and_budget_limited_receipts():
    complete, _ = await acquire([page([entry(1), entry(2)], 2, 1)])
    assert coverage_check(complete)
    partial, _ = await acquire([page([entry(1), entry(2)], 3, 2)],
                               limits=WooTreeLimits(per_page=2, requests=1))
    assert coverage_check(partial)
    # Inject a deliberately wrong publication state; receipts remain partial.
    faulty = replace(partial, outcome='complete', confirmed_empty=True, reasons=())
    assert not coverage_check(faulty)


async def test_live_oracle_rejects_totals_that_disagree_with_receipts():
    complete, _ = await acquire([page([entry(1)], 1, 1)])
    altered = replace(complete, pages=(replace(complete.pages[0], total='2'),))
    assert not coverage_check(altered)
