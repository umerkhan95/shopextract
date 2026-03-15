"""CLI entry point for shopextract using Click."""

from __future__ import annotations

import asyncio
import json
import sys

import click


@click.group()
@click.version_option(package_name="shopextract")
def main() -> None:
    """Extract, compare, and monitor product data from any e-commerce store."""


@main.command()
@click.argument("url")
@click.option("--max", "-n", "max_urls", default=20, help="Max product URLs to process.")
@click.option("--format", "-f", "fmt", type=click.Choice(["csv", "json"]), default="json",
              help="Output format.")
@click.option("-o", "--output", "output_path", default=None, help="Output file path.")
def extract(url: str, max_urls: int, fmt: str, output_path: str | None) -> None:
    """Extract products from an e-commerce store."""
    asyncio.run(_extract(url, max_urls, fmt, output_path))


@main.command()
@click.argument("url")
def detect(url: str) -> None:
    """Detect the e-commerce platform of a store."""
    asyncio.run(_detect(url))


@main.command()
@click.argument("url")
@click.option("--max", "-n", "max_urls", default=100, help="Max URLs to discover.")
def discover(url: str, max_urls: int) -> None:
    """Discover product URLs from a store."""
    asyncio.run(_discover(url, max_urls))


@main.command()
@click.argument("query")
@click.option("--stores", "-s", multiple=True, required=True, help="Store URLs to compare.")
def compare(query: str, stores: tuple[str, ...]) -> None:
    """Compare prices for a product across stores."""
    asyncio.run(_compare(query, list(stores)))


@main.command()
@click.argument("url")
def snapshot(url: str) -> None:
    """Take a snapshot of a store's catalog."""
    asyncio.run(_snapshot(url))


@main.command()
@click.argument("domain")
def changes(domain: str) -> None:
    """Show changes between snapshots for a domain."""
    asyncio.run(_changes(domain))


@main.command()
@click.argument("domain")
@click.argument("product")
def history(domain: str, product: str) -> None:
    """Show price history for a product."""
    asyncio.run(_history(domain, product))


@main.command()
@click.argument("url")
@click.option("--max", "-n", "max_urls", default=20, help="Max product URLs to analyze.")
def analyze(url: str, max_urls: int) -> None:
    """Analyze a store's catalog statistics."""
    asyncio.run(_analyze(url, max_urls))


@main.command(name="validate")
@click.argument("file", type=click.Path(exists=True))
@click.option("--marketplace", "-m", default="google_shopping",
              type=click.Choice(["google_shopping", "idealo", "amazon", "ebay"]),
              help="Target marketplace for validation.")
def validate_cmd(file: str, marketplace: str) -> None:
    """Validate products from a JSON file against marketplace rules."""
    _validate_file(file, marketplace)


# -- Async command implementations ------------------------------------------


async def _extract(url: str, max_urls: int, fmt: str, output_path: str | None) -> None:
    from . import extract as do_extract
    result = await do_extract(url, max_urls=max_urls)
    products = [_product_to_dict(p) for p in result.products]

    if output_path:
        _write_output(products, output_path, fmt)
        click.echo(f"Wrote {len(products)} products to {output_path}")
    else:
        _print_extraction_summary(result)
        click.echo(json.dumps(products[:10], indent=2, default=str))


async def _detect(url: str) -> None:
    from . import detect as do_detect
    result = await do_detect(url)
    click.echo(json.dumps({
        "platform": result.platform.value,
        "confidence": result.confidence,
        "signals": result.signals,
    }, indent=2))


async def _discover(url: str, max_urls: int) -> None:
    from . import discover as do_discover
    urls = await do_discover(url, max_urls=max_urls)
    for u in urls:
        click.echo(u)
    click.echo(f"\n{len(urls)} URLs discovered", err=True)


async def _compare(query: str, stores: list[str]) -> None:
    from .compare import compare_prices
    result = await compare_prices(query, stores)
    click.echo(json.dumps({
        "query": result.query,
        "matches": len(result.matches),
        "cheapest": _match_dict(result.cheapest) if result.cheapest else None,
        "most_expensive": _match_dict(result.most_expensive) if result.most_expensive else None,
        "avg_price": str(result.avg_price),
        "results": [_match_dict(m) for m in result.matches],
    }, indent=2))


async def _snapshot(url: str) -> None:
    from .monitor import take_snapshot
    snap = await take_snapshot(url)
    click.echo(json.dumps({
        "domain": snap.domain,
        "timestamp": snap.timestamp.isoformat(),
        "product_count": snap.product_count,
    }, indent=2))


async def _changes(domain: str) -> None:
    from .monitor import diff_latest
    changes_list = await diff_latest(domain)
    for change in changes_list:
        click.echo(json.dumps({
            "type": change.change_type.value,
            "title": change.title,
            "detected_at": change.detected_at.isoformat(),
        }, indent=2, default=str))
    if not changes_list:
        click.echo("No changes detected (need at least 2 snapshots)")


async def _history(domain: str, product: str) -> None:
    from .monitor import price_history
    entries = await price_history(domain, product)
    click.echo(json.dumps(entries, indent=2, default=str))


async def _analyze(url: str, max_urls: int) -> None:
    from .analyze import catalog_stats
    stats = await catalog_stats(url, max_urls=max_urls)
    click.echo(json.dumps({
        "total_products": stats.total_products,
        "price_range": list(stats.price_range),
        "avg_price": stats.avg_price,
        "median_price": stats.median_price,
        "currencies": stats.currencies,
        "brands": dict(list(stats.brands.items())[:20]),
        "in_stock": stats.in_stock,
        "out_of_stock": stats.out_of_stock,
        "has_gtin": stats.has_gtin,
        "has_images": stats.has_images,
        "completeness_score": stats.completeness_score,
    }, indent=2))


# -- Sync helpers -----------------------------------------------------------


def _validate_file(file: str, marketplace: str) -> None:
    """Load products from JSON and validate against marketplace rules."""
    with open(file, encoding="utf-8") as f:
        products = json.load(f)

    if not isinstance(products, list):
        click.echo("Error: JSON file must contain a list of products", err=True)
        sys.exit(1)

    from .validate import validate
    report = validate(products, marketplace=marketplace)

    click.echo(f"Marketplace: {report.marketplace}")
    click.echo(f"Total: {report.total}  Valid: {report.valid}  Invalid: {report.invalid}")
    click.echo(f"Warnings: {report.warnings}  Pass rate: {report.pass_rate:.1f}%")

    if report.issues:
        click.echo("\nIssues:")
        for issue in report.issues:
            prefix = "WARN" if issue.severity == "warning" else "ERROR"
            click.echo(f"  [{prefix}] #{issue.product_index} "
                        f"({issue.product_title[:40]}): "
                        f"{issue.field} - {issue.error}")


def _write_output(products: list[dict], path: str, fmt: str) -> None:
    """Write products to file in the specified format."""
    from .export import to_csv, to_json
    if fmt == "csv":
        to_csv(products, path)
    else:
        to_json(products, path)


def _product_to_dict(product: object) -> dict:
    """Convert a Product dataclass to a plain dict."""
    from dataclasses import asdict
    return {k: str(v) if not isinstance(v, (str, bool, int, float, list, dict, type(None)))
            else v for k, v in asdict(product).items()}


def _match_dict(match: object) -> dict:
    """Convert a Match to a plain dict."""
    return {
        "title": match.title,  # type: ignore[attr-defined]
        "price": str(match.price),  # type: ignore[attr-defined]
        "currency": match.currency,  # type: ignore[attr-defined]
        "store": match.store,  # type: ignore[attr-defined]
        "product_url": match.product_url,  # type: ignore[attr-defined]
    }


def _print_extraction_summary(result: object) -> None:
    """Print a brief extraction summary to stderr."""
    click.echo(f"Platform: {result.platform.value}  "  # type: ignore[attr-defined]
               f"Tier: {result.tier.value}  "  # type: ignore[attr-defined]
               f"Products: {result.product_count}  "  # type: ignore[attr-defined]
               f"Quality: {result.quality_score:.2f}",  # type: ignore[attr-defined]
               err=True)


if __name__ == "__main__":
    main()
