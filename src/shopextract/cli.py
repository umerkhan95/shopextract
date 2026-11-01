"""CLI entry point for shopextract using Click."""

from __future__ import annotations

import asyncio
import json
import sys

import click

from ._cli_core import CoreGroup, emit_success, emit_diagnostic, settings
from ._cli_extract import execution_options
from ._models import Platform


@click.group(cls=CoreGroup)
@click.version_option(package_name="shopextract")
@click.option("--config", type=click.Path(), help="Strict versioned CLI JSON config file.", expose_value=False)
@click.option("--output-format", type=click.Choice(["legacy", "json"]), help="Response format (before command).", expose_value=False)
@click.option("--diagnostics", type=click.Choice(["normal", "quiet"]), help="Stderr diagnostic verbosity.", expose_value=False)
def main() -> None:
    """Extract, compare, and monitor product data from any e-commerce store."""


@main.command()
@click.argument("url")
@click.option("--max", "-n", "max_urls", default=20, help="Max product URLs to process.")
@click.option("--format", "-f", "fmt", type=click.Choice(["csv", "json"]), default="json",
              help="Output format.")
@click.option("-o", "--output", "output_path", default=None, help="Output file path.")
@click.option("--compact", is_flag=True, help="Deduplicate captured provenance in bounded catalog transport.")
@click.option("--platform", type=click.Choice([p.value for p in Platform]))
@click.option("--shop-url")
@click.option("--enrich-identifiers", is_flag=True)
@click.option("--enrich-variants", is_flag=True, help="Read bounded Woo variant details (opt in).")
@click.option("--restore-short-gtin", is_flag=True)
@click.option("--storefront", type=click.Path(), help="Closed native storefront JSON options file.")
@execution_options()
def extract(url: str, max_urls: int, fmt: str, output_path: str | None, **options) -> None:
    """Extract products from an e-commerce store."""
    from ._cli_extract import explicit_controls, extract_store
    if settings().output_format == "json" or explicit_controls():
        extract_store(url, max_urls, fmt, output_path, options)
    else:
        asyncio.run(_extract(url, max_urls, fmt, output_path))


@main.command()
@click.argument("url")
@click.option("--timeout", type=float, default=None, help="Operation deadline seconds (0,300], bounded default30.")
def detect(url: str, timeout: float | None) -> None:
    """Detect the e-commerce platform of a store."""
    if settings().output_format == "json" or timeout is not None:
        from ._cli_extract import validate_timeout, validate_url
        validate_url(url)
        deadline = validate_timeout(timeout)
        async def bounded():
            await asyncio.wait_for(_detect(url), deadline)
        asyncio.run(bounded())
    else:
        asyncio.run(_detect(url))


@main.command()
@click.argument("url")
@click.option("--max", "-n", "max_urls", default=100, help="Max URLs to discover.")
@click.option("--platform", type=click.Choice([p.value for p in Platform]))
@execution_options(llm=False)
def discover(url: str, max_urls: int, platform: str | None, **options) -> None:
    """Discover URLs (robots checked,16 requests,30s worker cap; coverage unverified)."""
    from ._cli_extract import explicit_controls, discover_urls
    if settings().output_format == "json" or explicit_controls():
        discover_urls(url, max_urls, platform, options)
    else:
        asyncio.run(_discover(url, max_urls))


@main.command()
@click.argument("query")
@click.option("--stores", "-s", multiple=True, required=True, help="Store URLs to compare.")
@click.option('--max-per-store',type=int,default=None)
@click.option('--threshold',type=float,default=None)
@click.option('--timeout',type=float,default=None)
def compare(query: str, stores: tuple[str, ...], max_per_store, threshold, timeout) -> None:
    """Compare prices for a product across stores."""
    if settings().output_format == 'json' or any(v is not None for v in (max_per_store,threshold,timeout)):
        from ._cli_analysis import compare_command
        compare_command(query,list(stores),50 if max_per_store is None else max_per_store,.6 if threshold is None else threshold,timeout)
    else:
        asyncio.run(_compare(query, list(stores)))


@main.command()
@click.argument("url")
@click.option('--db',type=click.Path(),default=None)
@click.option('--max','max_urls',type=int,default=None)
@click.option('--timeout',type=float,default=None)
def snapshot(url: str, db, max_urls, timeout) -> None:
    """Take a snapshot of a store's catalog."""
    if settings().output_format == 'json' or any(v is not None for v in (db,max_urls,timeout)):
        from ._cli_monitor import snapshot_command, DEFAULT_DB
        snapshot_command(url,db or DEFAULT_DB,20 if max_urls is None else max_urls,timeout)
    else:
        asyncio.run(_snapshot(url))


@main.command()
@click.argument("domain")
@click.option('--db',type=click.Path(),default=None)
@click.option('--reliable',is_flag=True)
@click.option('--previous',type=click.IntRange(1))
@click.option('--current',type=click.IntRange(1))
@click.option('--recheck',type=click.IntRange(1))
def changes(domain: str, db, reliable, previous, current, recheck) -> None:
    """Show changes between snapshots for a domain."""
    if settings().output_format == 'json' or db is not None or reliable or any(v is not None for v in (previous,current,recheck)):
        from ._cli_monitor import changes_command, DEFAULT_DB
        changes_command(domain,db or DEFAULT_DB,reliable,previous,current,recheck)
    else:
        asyncio.run(_changes(domain))


@main.command()
@click.argument("domain")
@click.argument("product")
@click.option('--db',type=click.Path(),default=None)
@click.option('--canonical-id',default=None)
def history(domain: str, product: str, db, canonical_id) -> None:
    """Show price history for a product; retain PRODUCT with --canonical-id."""
    if settings().output_format == 'json' or db is not None or canonical_id is not None:
        from ._cli_monitor import history_command, DEFAULT_DB
        history_command(domain,product,db or DEFAULT_DB,canonical_id)
    else:
        asyncio.run(_history(domain, product))


@main.command()
@click.argument("url")
@click.option("--max", "-n", "max_urls", default=20, help="Max product URLs to analyze.")
@click.option('--timeout',type=float,default=None)
def analyze(url: str, max_urls: int, timeout) -> None:
    """Analyze a store's catalog statistics."""
    if settings().output_format == 'json' or timeout is not None:
        from ._cli_analysis import analyze_command
        analyze_command(url,max_urls,timeout)
    else:
        asyncio.run(_analyze(url, max_urls))


@main.command(name="validate")
@click.argument("file", type=click.Path())
@click.option("--marketplace", "-m", default="google_shopping",
              type=click.Choice(["google_shopping", "idealo", "amazon", "ebay"]),
              help="Target marketplace for validation.")
def validate_cmd(file: str, marketplace: str) -> None:
    """Validate products from a JSON file against marketplace rules."""
    if settings().output_format == 'json' or file == '-':
        from ._cli_analysis import validate_command
        validate_command(file,marketplace)
    else:
        _validate_file(file, marketplace)


@main.command(name="extract-one")
@click.argument("url")
@execution_options()
def extract_one_cmd(url, **options):
    """Extract one raw product, bounded; browser/LLM require explicit activation."""
    from ._cli_extract import extract_single
    extract_single(url, options)


@main.command(name="feed")
@click.argument("url")
@click.option("--shop-url", default="")
@click.option("--max", "max_products", type=click.IntRange(1,1000), default=1000)
@click.option("--timeout", type=float, default=None)
def feed_cmd(url, shop_url, max_products, timeout):
    """Extract a feed URL, retaining at most --max products explicitly."""
    from ._cli_extract import extract_feed
    extract_feed(url, shop_url, max_products, timeout)


@main.command(name="normalize")
@click.argument("file", type=click.Path())
@click.option("--platform", type=click.Choice([p.value for p in Platform]), default="generic")
@click.option("--shop-url", default="")
@click.option("--restore-short-gtin", is_flag=True)
def normalize_cmd(file, platform, shop_url, restore_short_gtin):
    """Normalize bounded raw JSON FILE (or - stdin) into portable product records."""
    from ._cli_extract import normalize_file
    normalize_file(file, platform, shop_url, restore_short_gtin)


@main.command(name="quality")
@click.argument("file", type=click.Path())
def quality_cmd(file):
    """Score bounded raw JSON or portable result FILE (- for stdin)."""
    from ._cli_extract import quality_file
    quality_file(file)


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
    data = {"platform": result.platform.value, "confidence": result.confidence,
            "signals": result.signals}
    if settings().output_format == "json":
        emit_success(data)
    else:
        click.echo(json.dumps(data, indent=2))


async def _discover(url: str, max_urls: int) -> None:
    from . import discover as do_discover
    urls = await do_discover(url, max_urls=max_urls)
    for u in urls:
        click.echo(u)
    emit_diagnostic(f"\n{len(urls)} URLs discovered")


async def _compare(query: str, stores: list[str]) -> None:
    from .compare import compare as compare_prices
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
    from .monitor import snapshot as take_snapshot
    count = await take_snapshot(url)
    click.echo(json.dumps({
        "url": url,
        "product_count": count,
    }, indent=2))


async def _changes(domain: str) -> None:
    from .monitor import changes as detect_changes
    changes_list = detect_changes(domain)
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
    entries = price_history(domain, product)
    click.echo(json.dumps(
        [{"timestamp": ts.isoformat(), "price": price} for ts, price in entries],
        indent=2,
    ))


async def _analyze(url: str, max_urls: int) -> None:
    from .analyze import analyze as catalog_stats
    stats = await catalog_stats(url, max_products=max_urls)
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
    emit_diagnostic(f"Platform: {result.platform.value}  "  # type: ignore[attr-defined]
               f"Tier: {result.tier.value}  "  # type: ignore[attr-defined]
               f"Products: {result.product_count}  "  # type: ignore[attr-defined]
               f"Quality: {result.quality_score:.2f}",  # type: ignore[attr-defined]
               )


from ._cli_analysis import register as _register_analysis
_register_analysis(main)



from ._cli_monitor import register as _register_monitor
_register_monitor(main)

from ._cli_categories import register as _register_categories
_register_categories(main)

from ._cli_operations import register as _register_operations
_register_operations(main)

from ._cli_discovery import register as _register_discovery
_register_discovery(main)

from ._readiness import register as _register_readiness
_register_readiness(main)

if __name__ == "__main__":
    main()
