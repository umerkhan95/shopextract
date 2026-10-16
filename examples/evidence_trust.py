"""Offline capture → resolution → SQLite restart → portable trust inspection.

Run from a checkout: PYTHONPATH=src python examples/evidence_trust.py
No network, model, credentials or optional inference runtime is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import NAMESPACE_URL, uuid5

from shopextract import Platform, normalize
from shopextract._capture import capture
from shopextract._evidence import Evidence, FieldObservation, factual_paths
from shopextract._resolution import resolve_fields
from shopextract.extractors.feed import GoogleFeedExtractor

AS_OF = datetime(2026, 10, 16, 12, 0, 0, 123456, tzinfo=timezone.utc)


def fixture_products():
    """Small labeled synthetic fixtures through the existing adapter/normalizer."""
    # Exercise the normal feed adapter parser, then pin its capture clock.
    raw = GoogleFeedExtractor._parse_csv(
        'id,title,price,availability\nzero,Zero offer,0 EUR,out_of_stock\n',
        'https://supplier.example/feed.csv',
    )[0]
    capture(raw, 'https://supplier.example/feed.csv', 'feed_csv', observed_at=AS_OF)
    zero = normalize(raw, Platform.GENERIC, 'https://supplier.example')
    nested_raw = {'id': 'nested', 'title': 'Nested offer', 'handle': 'nested',
                  'variants': [{'id': 10, 'title': 'Small', 'price': '1.2300',
                                'available': False, 'barcode': '29877030712'}]}
    capture(nested_raw, 'https://supplier.example/products.json', 'shopify_api', observed_at=AS_OF)
    nested = normalize(nested_raw, Platform.SHOPIFY, 'https://supplier.example', restore_short_gtin=True)
    missing = normalize({'@type': 'Product', 'name': 'Missing fields', 'sku': 'missing'},
                        Platform.GENERIC, 'https://supplier.example')
    assert zero is not None and nested is not None and missing is not None
    # A literal user map resembling a codec tag must remain literal.
    nested.raw_data['literal'] = {'$type': 'decimal', 'value': 'literal text'}
    nested.attributes['a/b~c'] = 'red'
    contract = nested.evidence_contract
    for label, value, role in [('supplier-color', 'red', 'supplier'),
                               ('manufacturer-color', 'blue', 'verified_manufacturer')]:
        evidence_id = 'e_' + str(uuid5(NAMESPACE_URL, 'trust-demo/' + label))
        contract.evidence.append(Evidence(
            evidence_id, 'https://' + role + '.example/spec', AS_OF, 'offline_fixture',
            retained_data={'a/b~c': value}, pointer='/a~1b~0c', source_role=role))
        contract.observations.append(FieldObservation(
            'o_' + str(uuid5(NAMESPACE_URL, 'trust-demo/obs/' + label)),
            '/attributes/a~1b~0c', 'observed', value, value, [evidence_id]))
    # An ungrounded score cannot acquire support or validated-confidence metadata.
    ungrounded = next(o for o in missing.evidence_contract.observations if o.field_path == '/description')
    ungrounded.score, ungrounded.score_kind = 0.98, 'model'
    for product in (zero, nested, missing):
        product.scraped_at = AS_OF
        for evidence in product.evidence_contract.evidence:
            if evidence.source_role == 'unverified':
                evidence.source_role = 'supplier'
        product.evidence_contract = resolve_fields(product.evidence_contract, as_of=AS_OF)
        for variant in product.variants:
            for evidence in variant.evidence_contract.evidence:
                evidence.source_role = 'supplier'
            variant.evidence_contract = resolve_fields(variant.evidence_contract, as_of=AS_OF)
    return [zero, nested, missing]


def inspect_products(products, *, snapshot_id=None, db_path=None):
    """Count every factual path, separately checking retained support retrieval."""
    from shopextract.monitor.evidence import get_evidence
    states = Counter()
    retrievable = 0
    denominator = 0
    for index, product in enumerate(products):
        owners = [(product, f'product/{index}')]
        owners.extend((v, f'product/{index}/variant/{j}') for j, v in enumerate(product.variants))
        for owner, scope in owners:
            view = owner.trust_view()
            assert set(view) == set(factual_paths(owner))
            evidence = {e.evidence_id: e for e in owner.evidence_contract.evidence}
            for field in view.values():
                denominator += 1
                states[field['state']] += 1
                if field['state'] == 'observed':
                    assert field['evidence_ids']
                    for evidence_id in field['evidence_ids']:
                        retained = evidence[evidence_id]
                        if retained.pointer is not None:
                            retained.resolve_pointer()
                        if db_path is not None:
                            lookup = get_evidence(evidence_id, snapshot_id=snapshot_id,
                                                  record_key=scope, db_path=db_path)
                            assert lookup.status == 'available'
                    retrievable += 1
                else:
                    assert field['reason'] and field['value'] is None
    return {'factual_paths': denominator, 'states': dict(states), 'retrievable_observed': retrievable}


def run_demo(output_dir: Path) -> dict:
    """Execute real storage/reopening/export APIs and save compact audit artifacts."""
    from shopextract._portable import product_to_record
    from shopextract.export import write_evidence_bundle, read_evidence_bundle
    from shopextract.monitor.evidence import save_snapshot, load_snapshot, prune_evidence
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(output_dir / 'evidence.db')
    products = fixture_products()
    snapshot_id = save_snapshot(products, 'supplier.example', db_path=db_path,
                                metadata={'observation_scope': 'bounded-trust-demo'})
    # save/load own separate connections: the load exercises a real file-backed reopen.
    restored = load_snapshot(snapshot_id, db_path=db_path)
    assert [product_to_record(p) for p in restored] == [product_to_record(p) for p in products]
    report = inspect_products(restored, snapshot_id=snapshot_id, db_path=db_path)
    bundle_path = output_dir / 'evidence-bundle.json'
    write_evidence_bundle(restored, bundle_path)
    imported = read_evidence_bundle(bundle_path)
    assert [product_to_record(p) for p in imported] == [product_to_record(p) for p in restored]
    assert inspect_products(imported) == report
    # Dry-run and protected pruning are explicit; the destructive demonstration is tested separately.
    prune_evidence(db_path=db_path, before=AS_OF, dry_run=True)
    prune_evidence(db_path=db_path, before=AS_OF, dry_run=False)
    assert [product_to_record(p) for p in load_snapshot(snapshot_id, db_path=db_path)] == [product_to_record(p) for p in restored]
    result = {'fixture': 'bounded-trust-demo', 'as_of': AS_OF.isoformat(),
              'snapshot_id': snapshot_id, **report,
              'bundle': str(bundle_path), 'database': db_path,
              'meaning': 'Fixture state and retrieval coverage; not accuracy or calibrated confidence.'}
    (output_dir / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    if args.output_dir:
        result = run_demo(args.output_dir)
    else:
        with TemporaryDirectory(prefix='evidence-trust-') as directory:
            result = run_demo(Path(directory))
            result['artifacts'] = 'Temporary; use --output-dir to retain files.'
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
