"""One reviewed remaining Magento request; persist capture before offline replay."""
import asyncio
import json
import time

import httpx

from tests.category_live_driver import OUT, CASES, BudgetTransport


async def main():
    path = OUT / 'status.json'
    status = json.loads(path.read_text())
    if sum(e['platform'] == 'magento' for e in status['network']) != 1:
        raise RuntimeError('Requires exactly one prior Magento attempt')
    marker = OUT / 'magento-diagnostic-started.json'
    with marker.open('x') as handle:
        json.dump(dict(prior_requests=len(status['network']), remaining_magento_attempts=1), handle)
    charged = max(status['seconds'], len(status['network']) * 10)
    if charged >= 120:
        raise RuntimeError('Live budget exhausted')
    deadline = time.monotonic() + 120 - charged
    row = dict(platform='magento', state='running', provenance='one remaining actual live request; replay separately offline')
    status['magento_diagnostic'] = row
    def save():
        status['seconds'] = round(120 - (deadline-time.monotonic()), 3)
        path.write_text(json.dumps(status, indent=2) + '\n')
    save()
    try:
        from shopextract.extractors.magento_graphql import MagentoGraphQLExtractor
        async with httpx.AsyncClient(transport=BudgetTransport(status, 'magento', deadline, save),
                                     timeout=10, follow_redirects=False) as client:
            result = await asyncio.wait_for(MagentoGraphQLExtractor(
                timeout=10, page_size=2, max_pages=1, http_client=client).extract(
                    CASES['magento'], max_products=2, include_categories=True),
                timeout=min(15, max(.01, deadline-time.monotonic())))
        raw = result.products[:2]
        content = json.dumps(raw, ensure_ascii=False, allow_nan=False).encode()
        if len(content) > 2097152:
            raise RuntimeError('Diagnostic fixture byte cap exceeded')
        fixture = OUT / 'magento-diagnostic-raw.json'
        fixture.write_bytes(content)  # Original capture URL/time retained before normalization.
        row.update(state='captured', products=len(raw), raw_bytes=len(content),
                   source_complete=result.complete, source_error=bool(result.error),
                   source_reason=result.completeness_reason)
        save()
        # The following is explicitly offline replay of the saved actual response.
        from shopextract import Platform
        from shopextract._normalize import normalize
        from shopextract._portable import product_to_record
        from shopextract.categories import CategoryOptions, CategoryScope, TargetRegistry, normalize_with_categories
        from shopextract.categories._codec import canonical
        from shopextract.categories.contracts import CategoryError
        options = CategoryOptions(CategoryScope(Platform.MAGENTO, CASES['magento']), TargetRegistry('live-observation', '1', ()))
        outcomes = []
        known = {'Category companion byte cap exceeded', 'Category original binding changed',
                 'Category Product platform mismatch', 'Category conversion source changed',
                 'Invalid category source binding', 'Category native ID conversion mismatch',
                 'Category label conversion mismatch', 'Category relation exceeds configured bounds',
                 'Category evidence differs from source facet'}
        for raw_product in json.loads(fixture.read_text()):
            product = normalize(raw_product, Platform.MAGENTO, CASES['magento'])
            outcome = dict(product_record_bytes=len(canonical(product_to_record(product)).encode()) if product else 0)
            try:
                value = normalize_with_categories(raw_product, Platform.MAGENTO, CASES['magento'], category_options=options)
                outcome['state'] = 'normalized' if value else 'product_unavailable'
            except CategoryError as error:
                reason = str(error)
                outcome.update(state='rejected', reason=reason if reason in known else 'unclassified_category_validation')
            outcomes.append(outcome)
        row.update(state='offline_replay_complete', offline_outcomes=outcomes)
    except Exception as error:
        row.update(state='inconclusive', reason=type(error).__name__)
    finally:
        save()
    print(json.dumps(row))


if __name__ == '__main__':
    asyncio.run(main())
