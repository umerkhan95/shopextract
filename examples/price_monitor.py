"""Monitor a store for price changes over time.

Demonstrates:
- Taking catalog snapshots
- Detecting changes between snapshots
- Viewing price history for a product
- Continuous watch mode

Usage:
    python examples/price_monitor.py
"""

import asyncio

import shopextract


async def main() -> None:
    store_url = "https://example-store.com"
    domain = "example-store.com"

    # --- Take a snapshot ---
    print("--- Taking Snapshot ---")
    count = await shopextract.snapshot(store_url, max_urls=20)
    print(f"Snapshot saved: {count} products from {domain}")
    print("(Snapshots stored in ~/.shopextract/snapshots.db)")

    # --- Detect changes ---
    # In a real scenario, you'd take snapshots hours/days apart.
    # Here we take two consecutive snapshots to show the API.
    print("\n--- Taking Second Snapshot ---")
    count = await shopextract.snapshot(store_url, max_urls=20)
    print(f"Second snapshot: {count} products")

    print("\n--- Detecting Changes ---")
    detected = shopextract.changes(domain)

    if not detected:
        print("No changes detected (prices are the same between snapshots)")
    else:
        for change in detected:
            if change.change_type == shopextract.ChangeType.PRICE_CHANGE:
                print(f"  PRICE: {change.title}")
                print(f"    {change.old_price} -> {change.new_price} {change.currency}")
            elif change.change_type == shopextract.ChangeType.NEW_PRODUCT:
                print(f"  NEW: {change.title} ({change.price} {change.currency})")
            elif change.change_type == shopextract.ChangeType.REMOVED_PRODUCT:
                print(f"  REMOVED: {change.title} (was {change.last_price} {change.currency})")

    # --- Price history ---
    print("\n--- Price History ---")
    history = shopextract.price_history(domain, "Example Product")
    if history:
        for timestamp, price in history:
            print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')}: {price}")
    else:
        print("  No price history found for 'Example Product'")

    # --- Watch mode (continuous monitoring) ---
    print("\n--- Watch Mode (demo) ---")
    print("In production, watch mode runs continuously:")
    print()
    print("  async for change in shopextract.watch(url, interval=3600):")
    print('      print(f"[{change.change_type}] {change.title}")')
    print()
    print("This takes a snapshot every hour and yields changes as they occur.")


if __name__ == "__main__":
    asyncio.run(main())
