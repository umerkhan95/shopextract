"""Extract products and export as marketplace feeds.

Demonstrates:
- Extracting products from a store
- Validating against marketplace requirements
- Exporting as Google Shopping XML feed
- Exporting as idealo TSV feed
- Exporting as CSV, JSON, and Parquet

Usage:
    python examples/marketplace_feed.py
"""

import asyncio
from dataclasses import asdict

import shopextract


async def main() -> None:
    store_url = "https://example-store.com"

    # --- Extract products ---
    print("--- Extracting Products ---")
    result = await shopextract.extract(store_url, max_urls=20)
    print(f"Extracted {result.product_count} products ({result.platform}, {result.tier})")

    # Convert Product dataclasses to dicts for export/validation
    products = [asdict(p) for p in result.products]

    # --- Validate for Google Shopping ---
    print("\n--- Google Shopping Validation ---")
    report = shopextract.validate(products, marketplace="google_shopping")
    print(f"Total: {report.total}  Valid: {report.valid}  Invalid: {report.invalid}")
    print(f"Warnings: {report.warnings}  Pass rate: {report.pass_rate:.0f}%")

    if report.issues[:5]:
        print("\nFirst 5 issues:")
        for issue in report.issues[:5]:
            severity = "WARN" if issue.severity == "warning" else "ERROR"
            print(f"  [{severity}] #{issue.product_index} ({issue.product_title[:30]}): "
                  f"{issue.field} - {issue.error}")

    # --- Validate for idealo ---
    print("\n--- idealo Validation ---")
    report = shopextract.validate(products, marketplace="idealo")
    print(f"Total: {report.total}  Valid: {report.valid}  Invalid: {report.invalid}")
    print(f"Pass rate: {report.pass_rate:.0f}%")

    # --- Check image URLs ---
    print("\n--- Image Validation ---")
    image_issues = await shopextract.check_images(products[:10])
    if image_issues:
        for issue in image_issues[:5]:
            print(f"  {issue.product_title[:40]}: {issue.error}")
    else:
        print("  All images OK")

    # --- Check for duplicates ---
    print("\n--- Duplicate Detection ---")
    dupes = shopextract.find_duplicates(products, method="title", threshold=0.9)
    if dupes:
        for idx_a, idx_b, sim in dupes[:5]:
            title_a = products[idx_a].get("title", "")[:30]
            title_b = products[idx_b].get("title", "")[:30]
            print(f"  #{idx_a} '{title_a}' <-> #{idx_b} '{title_b}' ({sim:.0%})")
    else:
        print("  No duplicates found")

    # --- Export ---
    print("\n--- Exporting ---")

    shopextract.to_json(products, "products.json")
    print("  Wrote products.json")

    shopextract.to_csv(products, "products.csv")
    print("  Wrote products.csv")

    shopextract.to_feed(products, "google_feed.xml", format="google_shopping")
    print("  Wrote google_feed.xml (Google Shopping RSS 2.0)")

    shopextract.to_feed(products, "idealo_feed.tsv", format="idealo")
    print("  Wrote idealo_feed.tsv (idealo TSV)")

    # Parquet export requires shopextract[data]
    try:
        shopextract.to_parquet(products, "products.parquet")
        print("  Wrote products.parquet")
    except ImportError:
        print("  Skipping parquet (install shopextract[data] for parquet support)")

    # DataFrame for analysis
    try:
        df = shopextract.to_dataframe(products)
        print(f"\n  DataFrame shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
    except ImportError:
        print("  Skipping DataFrame (install shopextract[data] for pandas support)")


if __name__ == "__main__":
    asyncio.run(main())
