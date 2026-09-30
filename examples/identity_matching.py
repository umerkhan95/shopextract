"""Offline product truth example: normalized extraction, rename history and matches.

Run from the repository: PYTHONPATH=src python examples/identity_matching.py
No network, credentials or model provider is required.
"""
from __future__ import annotations

import asyncio
import importlib
import json
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

from shopextract import ExtractionResult, changes, evaluate_matching, match_products, normalize, price_history


async def main() -> None:
    original = normalize({"title": "Notebook 8GB", "id": "42", "price": "100", "gtin": "4006381333931"}, shop_url="https://shop.example")
    renamed = normalize({"title": "Work Notebook 8GB", "id": "42", "price": "90", "gtin": "4006381333931"}, shop_url="https://shop.example")
    competitor = normalize({"title": "Notebook 8GB", "id": "99", "price": "95", "gtin": "4006381333931"}, shop_url="https://competitor.example")
    variant = normalize({"title": "Notebook 16GB", "id": "100", "price": "120", "gtin": "4006381333931"}, shop_url="https://competitor.example")
    print("Stable canonical identity:", original.canonical_product_id == renamed.canonical_product_id)
    print("Exact pair:", asdict(match_products([renamed], [competitor])[0]))
    print("Variant pair:", asdict(match_products([renamed], [variant])[0]))
    module = importlib.import_module("shopextract.monitor.snapshot")
    with TemporaryDirectory() as directory:
        db = str(Path(directory) / "history.db")
        # Substitute extraction results to exercise the production snapshot pipeline offline.
        with patch.object(module, "extract", AsyncMock(side_effect=[ExtractionResult(products=[original]), ExtractionResult(products=[renamed])])):
            await module.snapshot("https://shop.example", db_path=db)
            await module.snapshot("https://shop.example", db_path=db)
        print("Changes:", changes("shop.example", db_path=db))
        print("Rename history:", [price for _, price in price_history("shop.example", "Work Notebook 8GB", db_path=db)])
    dataset = Path(__file__).resolve().parents[1] / "tests/fixtures/matching_evaluation.json"
    report = evaluate_matching(json.loads(dataset.read_text()))
    print("Evaluation:", json.dumps({k: v for k, v in report.items() if k != "predictions"}, indent=2))
    if not report["passed"]:
        raise SystemExit("Matching acceptance thresholds failed")


if __name__ == "__main__":
    asyncio.run(main())
