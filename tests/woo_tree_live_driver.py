"""One explicitly bounded public read-only feature-009 observation.

Run after offline checks: PYTHONPATH=src .venv/bin/python tests/woo_tree_live_driver.py
An optional --expanded run is permitted only after the saved smoke passes.
"""
import argparse
import asyncio
from dataclasses import asdict
import json
from pathlib import Path
import time
from urllib.parse import parse_qs, urlsplit

from shopextract._models import Platform
from shopextract.categories.contracts import CategoryScope
from shopextract.categories.woo_tree import (
    WooTreeLimits, fetch_woocommerce_category_tree, woo_tree_to_record,
)

EVIDENCE = Path(__file__).resolve().parents[1] / 'specs/009-woocommerce-category-tree/evidence'
STORE = 'https://demo.athemes.com/botiga'


def coverage_check(tree):
    """Independent bounded observation oracle, using receipts rather than graph output."""
    receipts, totals, raw_ids = [], [], []
    for number, receipt in enumerate(tree.pages, 1):
        rows = json.loads(receipt.body)
        query = parse_qs(urlsplit(receipt.source_url).query)
        if query != {'page': [str(number)], 'per_page': [str(tree.limits.per_page)],
                     'hide_empty': ['false'], 'orderby': ['slug'], 'order': ['asc']}:
            return False
        receipts.append(len(rows))
        for row in rows:
            identity = row.get('id') if isinstance(row, dict) else None
            if type(identity) is int and identity > 0:
                raw_ids.append(str(identity))
            elif isinstance(identity, str) and identity.strip():
                raw_ids.append(identity)
        if receipt.total is None and receipt.total_pages is None:
            if number != 1 or len(rows) >= tree.limits.per_page:
                return False
            continue
        if not all(isinstance(v, str) and v.isascii() and v.isdecimal()
                   for v in (receipt.total, receipt.total_pages)):
            return False
        total, pages = int(receipt.total), int(receipt.total_pages)
        if pages != (total + tree.limits.per_page - 1) // tree.limits.per_page:
            return False
        totals.append((total, pages))
    if not totals or len(set(totals)) != 1:
        return False
    total, pages = totals[0]
    if any(count != min(tree.limits.per_page, max(0, total - i * tree.limits.per_page))
           for i, count in enumerate(receipts)):
        return False
    observed_all = (len(receipts) >= max(1, pages) and sum(receipts) == total
                    and len(set(raw_ids)) == len(raw_ids) == total)
    if tree.outcome == 'complete':
        return observed_all and not tree.reasons and tree.confirmed_empty == (total == 0)
    if observed_all or tree.confirmed_empty:
        return False
    exhausted = set(tree.reasons)
    if not exhausted or exhausted - {'request_limit', 'category_limit'}:
        return False
    if 'request_limit' in exhausted and len(tree.attempts) != tree.limits.requests:
        return False
    next_size = min(tree.limits.per_page, max(0, total - sum(receipts)))
    if 'category_limit' in exhausted and tree.limits.categories - sum(receipts) >= next_size:
        return False
    return True


async def run(expanded=False):
    if expanded:
        previous = json.loads((EVIDENCE / 'live-smoke.json').read_text())
        if previous.get('smoke_passed') is not True:
            raise RuntimeError('Saved passing smoke required before expansion')
    limits = WooTreeLimits() if expanded else WooTreeLimits(
        requests=3, per_page=2, categories=6, response_bytes=262144,
        retained_bytes=786432, seconds=10)
    name = 'live-expanded' if expanded else 'live-smoke'
    output = dict(provenance='actual_public_store_observation', store_url=STORE,
                  limits=asdict(limits), smoke_passed=False)
    start = time.monotonic()
    try:
        tree = await asyncio.wait_for(fetch_woocommerce_category_tree(
            CategoryScope(Platform.WOOCOMMERCE, STORE), limits=limits),
            timeout=limits.seconds + 4)
        record = woo_tree_to_record(tree)
        output.update(outcome=tree.outcome, reasons=list(tree.reasons),
                      confirmed_empty=tree.confirmed_empty, pages=len(tree.pages),
                      nodes=len(tree.nodes), attempts=len(tree.attempts),
                      parent_edges=len(tree.parent_edges),
                      issue_codes=sorted({i.code for i in tree.issues}), record=record)
        assertions = {
            'bounded_attempts': len(tree.attempts) <= limits.requests,
            'requested_empty_categories': all('hide_empty=false' in p.source_url for p in tree.pages),
            'real_id_parent_facets': bool(tree.nodes) and all(
                {'id', 'parent'} <= {f.facet for f in d.facts if f.state == 'observed'}
                for n in tree.nodes for d in n.declarations),
            'pointers_match_receipts': all(
                f.raw_value == json.loads(tree.pages[d.page - 1].body)[d.index][f.facet]
                and f.source_url == tree.pages[d.page - 1].source_url
                and f.observed_at == tree.pages[d.page - 1].observed_at
                for n in tree.nodes for d in n.declarations for f in d.facts
                if f.state == 'observed'),
            'partial_not_empty': tree.outcome == 'complete' or not tree.confirmed_empty,
            'coverage_agrees_with_headers_and_counts': coverage_check(tree),
        }
        output['assertions'] = assertions
        output['smoke_passed'] = all(assertions.values()) and tree.outcome in {'complete', 'partial'} and set(tree.reasons) <= {'request_limit', 'category_limit'}
        output['status'] = 'passed' if output['smoke_passed'] else 'blocked_or_inconclusive'
    except Exception as error:
        output.update(status='blocked_or_inconclusive', error_type=type(error).__name__)
    output['elapsed_seconds'] = round(time.monotonic() - start, 3)
    (EVIDENCE / (name + '.json')).write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if k != 'record'}, ensure_ascii=False))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--expanded', action='store_true')
    asyncio.run(run(parser.parse_args().expanded))
