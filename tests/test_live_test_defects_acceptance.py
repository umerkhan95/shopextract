"""SC-01..SC-14 offline acceptance checks for the reviewed live-test fixes.

All network boundaries use MockTransport or local deterministic fixtures. No
test contacts a commercial site; SC-13 remains explicitly live-only.
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from click.testing import CliRunner

from shopextract import _cli_core, _cli_data
from shopextract._models import ExtractionResult, Platform, Product
from shopextract.cli import main

ROOT = Path(__file__).resolve().parents[1]
MATCH_FIXTURE = ROOT / "tests/fixtures/airfryer_matching_fixture.json"


def invoke(*args, input=None, env=None):
    return CliRunner().invoke(main, ["--output-format", "json", *args], input=input, env=env)


def response(result):
    assert result.stdout.startswith("{"), result.output[:500]
    return json.loads(result.stdout)


@pytest.mark.asyncio
async def test_sc01_discovery_keeps_category_scope_and_caps_requests():
    from shopextract._discover import discover

    category = "https://fixture.invalid/shop/category/fryers"
    calls = []

    def handler(request):
        calls.append(str(request.url))
        if request.url.path == "/shop/category/fryers" and request.url.params.get("page") == "2":
            return httpx.Response(200, text=(
                '<html><main><h1>Fryers</h1><a href="/shop/products/airfryer-b">Second air fryer</a>'
                '<a rel="next" href="?page=3">Next</a></main></html>'))
        if request.url.path == "/shop/category/fryers":
            return httpx.Response(200, text=(
                '<html><main><h1>Fryers</h1><a href="/shop/products/airfryer-a">Air fryer</a>'
                '<a href="/shop/category/kettles">Kettles</a><a rel="next" href="?page=2">Next</a>'
                '</main></html>'))
        if request.url.path.endswith("sitemap.xml"):
            return httpx.Response(200, text=(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://fixture.invalid/shop/products/airfryer-a</loc></url>'
                '<url><loc>https://fixture.invalid/shop/products/kettle-b</loc></url>'
                '</urlset>'))
        return httpx.Response(404)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        urls = await discover(category, platform=Platform.GENERIC, max_urls=10, client=client)
    assert len(calls) <= 16
    calls.clear()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        root_urls = await discover("https://fixture.invalid/shop", platform=Platform.GENERIC,
                                   max_urls=10, client=client)
    assert len(calls) <= 16
    assert root_urls == ["https://fixture.invalid/shop/products/airfryer-a",
                         "https://fixture.invalid/shop/products/kettle-b"]
    assert urls == ["https://fixture.invalid/shop/products/airfryer-a",
                    "https://fixture.invalid/shop/products/airfryer-b"], urls


def test_sc02_failure_envelope_preserves_cause_retryability_and_partial_diagnostics():
    failure = _cli_core.CliFailure("E_OPERATION", "network failed")
    # Existing exception remains source-compatible while carrying C1 metadata.
    failure.cause = "network_unreachable"
    failure.retryable = True
    failure.errors = ["connect timeout"]
    failure.incompleteness_reasons = ["source_timeout"]
    failure.retry_after_seconds = None
    failed = _cli_core.make_response(failure=failure)
    error = failed["error"]
    assert failed["ok"] is False
    assert {key: error[key] for key in (
        "code", "message", "cause", "retryable", "errors", "incompleteness_reasons"
    )} == {
        "code": "E_OPERATION", "message": "network failed", "cause": "network_unreachable",
        "retryable": True, "errors": ["connect timeout"],
        "incompleteness_reasons": ["source_timeout"],
    }
    assert error.get("retry_after_seconds") is None

    result = _cli_core.make_response({"products": [{"title": "A"}], "errors": ["429"],
                                      "incompleteness_reasons": ["rate_limited"]})
    assert result["ok"] is True and result["error"] is None
    assert result["data"]["errors"] == ["429"]


def test_sc02_cli_partial_extract_serializes_products_and_source_diagnostics(monkeypatch):
    import shopextract

    async def partial(*args, **kwargs):
        return ExtractionResult(products=[Product(title="Kept product")],
            errors=["source returned 429 after first page"], catalog_complete=False,
            incompleteness_reasons=["rate_limited"])

    monkeypatch.setattr(shopextract, "extract", partial)
    result = invoke("extract", "https://fixture.invalid", "--platform", "shopify")
    value = response(result)
    assert value["ok"] is True and value["error"] is None
    assert len(value["data"]["products"]) == 1
    assert value["data"]["errors"] == ["source returned 429 after first page"]
    assert value["data"]["incompleteness_reasons"] == ["rate_limited"]


def test_sc02_cli_zero_product_result_maps_429_failure_fields(monkeypatch):
    import shopextract

    async def rate_limited(*args, **kwargs):
        return ExtractionResult(errors=["HTTP 429"], catalog_complete=False,
                                incompleteness_reasons=["rate_limited"])

    monkeypatch.setattr(shopextract, "extract", rate_limited)
    result = invoke("extract", "https://fixture.invalid", "--platform", "shopify")
    value = response(result)
    assert value["ok"] is False and value["error"]["code"] == "E_OPERATION"
    assert value["error"]["cause"] == "rate_limited"
    assert value["error"]["retryable"] is True
    assert value["error"]["errors"] == ["HTTP 429"]
    assert value["error"]["incompleteness_reasons"] == ["rate_limited"]
    assert value["data"] is None


@pytest.mark.asyncio
async def test_sc03_url_guard_exists_and_rejects_blocked_classes_before_resolution():
    try:
        safety = importlib.import_module("shopextract._url_safety")
    except ImportError:
        pytest.fail("C2 _url_safety policy is missing")
    validate = getattr(safety, "validate_url_target", None)
    assert callable(validate), "C2 public URL guard is missing"

    for url in ("http://127.0.0.1/x", "http://10.1.2.3/x", "http://169.254.1.1/x",
                "http://[::1]/x", "http://[fe80::1]/x", "http://224.0.0.1/x",
                "http://[ff02::1]/x", "http://240.0.0.1/x", "http://[2001:db8::1]/x",
                "http://169.254.169.254/latest/meta-data/"):
        with pytest.raises(safety.UnsafeURLTarget):
            await validate(url)


@pytest.mark.asyncio
async def test_sc03_ipv4_mapped_ipv6_loopback_is_rejected():
    safety = importlib.import_module("shopextract._url_safety")
    with pytest.raises(safety.UnsafeURLTarget):
        await safety.validate_url_target("http://[::ffff:127.0.0.1]/metadata")


@pytest.mark.asyncio
async def test_sc03_public_redirect_to_private_target_makes_no_second_request():
    from shopextract.extractors.unified import UnifiedCrawlExtractor

    calls = []

    def route(request):
        calls.append((request.url.host, request.url.path))
        if request.url.host == "public.fixture.invalid":
            return httpx.Response(302, headers={"location": "http://127.0.0.1/secret"})
        return httpx.Response(200, text="must not reach private redirect")

    async with httpx.AsyncClient(transport=httpx.MockTransport(route), follow_redirects=True) as client:
        fetched = await UnifiedCrawlExtractor(http_client=client)._fetch_html_httpx(
            "https://public.fixture.invalid/start")
    assert fetched is None
    assert calls == [("public.fixture.invalid", "/start")]


@pytest.mark.asyncio
async def test_sc03_mixed_public_and_private_dns_answer_is_rejected(monkeypatch):
    import asyncio
    import socket

    safety = importlib.import_module("shopextract._url_safety")
    validate = safety.validate_url_target
    loop = asyncio.get_running_loop()

    async def mixed_answers(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))]

    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, *args, **kwargs: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port)),
    ])
    monkeypatch.setattr(loop, "getaddrinfo", mixed_answers)
    with pytest.raises(safety.UnsafeURLTarget):
        await validate("https://fixture.invalid/product")


@pytest.mark.asyncio
async def test_sc03_product_image_private_target_makes_no_request():
    from shopextract.validate.images import check_images

    calls = []
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: (calls.append(request) or httpx.Response(200, headers={"content-type": "image/png"})))) as client:
        await check_images([{"title": "Synthetic", "image_url": "http://127.0.0.1/private.png"}], client=client)
    assert calls == [], "source-controlled unsafe image URL reached the transport"


@pytest.mark.asyncio
async def test_sc03_feed_private_target_raises_policy_error_before_transport(monkeypatch):
    import shopextract.extractors.feed as feed
    safety = importlib.import_module("shopextract._url_safety")
    original = httpx.AsyncClient
    calls = []

    def factory(*args, **kwargs):
        def respond(request):
            calls.append(request)
            return httpx.Response(200, text="id,title\\n1,Fixture\\n",
                                  headers={"content-type": "text/csv"})
        kwargs["transport"] = httpx.MockTransport(respond)
        return original(*args, **kwargs)

    monkeypatch.setattr(feed.httpx, "AsyncClient", factory)
    with pytest.raises(safety.UnsafeURLTarget):
        await feed.GoogleFeedExtractor()._fetch_feed("http://127.0.0.1/feed.csv")
    assert calls == []


@pytest.mark.asyncio
async def test_sc03_operator_environment_is_the_local_feed_opt_in(monkeypatch):
    import shopextract.extractors.feed as feed
    original = httpx.AsyncClient
    calls = []
    monkeypatch.setenv("SHOPEXTRACT_ALLOW_PRIVATE_URLS", "1")

    def factory(*args, **kwargs):
        def respond(request):
            calls.append(request)
            return httpx.Response(200, text="id,title\\n1,Fixture\\n",
                                  headers={"content-type": "text/csv"})
        kwargs["transport"] = httpx.MockTransport(respond)
        return original(*args, **kwargs)

    monkeypatch.setattr(feed.httpx, "AsyncClient", factory)
    body, content_type = await feed.GoogleFeedExtractor()._fetch_feed("http://127.0.0.1/feed.csv")
    assert body and "csv" in content_type
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_sc03_mcp_private_dns_is_rejected_without_wire_request():
    import asyncio
    from shopextract.tools import ToolConfig, ToolRuntime

    calls = []
    async def private_resolver(host, context):
        return ["127.0.0.1"]
    def wire(request):
        calls.append(request)
        return httpx.Response(200, json={"products": []})

    runtime = ToolRuntime(ToolConfig(allowed_origins=("https://fixture.invalid",)),
                          resolver=private_resolver,
                          wire_transport=httpx.MockTransport(wire))
    try:
        submitted = await runtime.call("extract", {"schema_version": "1.0",
                                                     "url": "https://fixture.invalid/product"})
        job_id = submitted["data"]["job_id"]
        state = None
        for _ in range(100):
            state = await runtime.call("job_status", {"schema_version": "1.0", "job_id": job_id})
            if state["data"]["state"] not in ("queued", "running"):
                break
            await asyncio.sleep(0.01)
        assert state["data"]["state"] == "failed", state
        assert state["data"]["error"]["code"] == "permission_denied"
        assert calls == []
    finally:
        await runtime.aclose()


def test_sc03_crawl4ai_uses_proxy_hook_and_browser_config_disallows_bypass():
    from shopextract.extractors._browser import get_browser_config, get_crawl_config

    browser = get_browser_config()
    run = get_crawl_config()
    assert getattr(run, "proxy_config", None), "Crawl4AI arun must receive guarded per-crawl proxy_config"
    proxy = getattr(browser, "proxy", None)
    assert proxy, "browser config must route through the guarded local proxy"
    assert not getattr(proxy, "bypass", None), "browser proxy bypass list must be empty"


@pytest.mark.skip(reason="Blocked: no production-facing OS/network-sandbox egress audit seam exists yet")
def test_sc03_browser_direct_egress_cannot_bypass_proxy():
    pytest.fail("T3 stays blocked until browser socket egress can be observed and denied")


def test_sc04_saved_airfryer_oracle_requires_shared_indexed_model_code_decisions():
    from shopextract.compare.identity_match import match_products
    from shopextract.compare.match import fuzzy_match

    fixture = json.loads(MATCH_FIXTURE.read_text())
    left = fixture["left"]["products"]
    right = fixture["right"]["products"]
    expected = {(pair["index_a"], pair["index_b"]) for pair in fixture["positive_pairs"]}
    wrong = {(pair["index_a"], pair["index_b"]) for pair in fixture["known_wrong_pairs"]}
    decisions = match_products(left, right)
    exact = {(d.index_a, d.index_b) for d in decisions if d.relation.value == "exact"}
    assert expected <= exact and not (wrong & exact)
    fuzzy = fuzzy_match(left, right, threshold=0.5)
    assert all(hasattr(d, "index_a") and hasattr(d, "relation") for d in fuzzy)
    fuzzy_exact = {(d.index_a, d.index_b) for d in fuzzy if d.relation.value == "exact"}
    assert expected <= fuzzy_exact and not (wrong & fuzzy_exact)


@pytest.mark.asyncio
async def test_sc05_detection_requires_demandware_evidence_and_surfaces_probe_error():
    from shopextract._detect import detect

    def handler(request):
        if request.url.path == "/":
            return httpx.Response(200, text=(
                '<html><script>var dwsid="x";</script>'
                '<script src="/static/default/js/app.js"></script>'
                '<a href="https://cdn.shopify.com/s/files/1/image.jpg">image</a>'
                '<script>Shopify.shop="false-signal.myshopify.com"</script></html>'))
        return httpx.Response(404)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=False) as client:
        result = await detect("https://fixture.invalid", client=client)
    assert result.platform.value == "demandware"
    assert result.signals
    assert not any("shopify" in str(signal).lower() for signal in result.signals)


@pytest.mark.asyncio
async def test_sc05_detection_context_preserves_probe_failure_details():
    from shopextract import _detect

    detect_context = getattr(_detect, "detect_context", None)
    assert callable(detect_context), "detection context must retain probe failures"

    async def denied(request):
        return httpx.Response(403)

    async with httpx.AsyncClient(transport=httpx.MockTransport(denied), follow_redirects=False) as client:
        result = await detect_context("https://fixture.invalid", client=client)
    assert result.errors


@pytest.mark.asyncio
@pytest.mark.parametrize(("status", "body", "content_type"), [
    (200, "<html>login page</html>", "text/html"),
    (200, "not-json", "application/json"),
    (302, '{"version":"6.5"}', "application/json"),
])
async def test_sc05_shopware_probe_rejects_non_json_and_redirects(status, body, content_type):
    from shopextract import _detect
    from shopextract._models import Platform

    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(
            status, text=body, headers={"content-type": content_type,
                                        "location": "https://fixture.invalid/login"})),
            follow_redirects=False) as client:
        signals = {platform: [] for platform in Platform}
        await _detect._probe_shopware_api(client, "https://fixture.invalid", signals)
    assert signals[Platform.SHOPWARE] == []


@pytest.mark.asyncio
@pytest.mark.parametrize(("namespaces", "expected"), [
    (["wp/v2", "wp-site-health/v1"], False),
    (["wc/v3", "wp/v2"], True),
])
async def test_sc05_woocommerce_probe_requires_wc_namespace(namespaces, expected):
    from shopextract import _detect
    from shopextract._models import Platform

    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"namespaces": namespaces}))) as client:
        signals = {platform: [] for platform in Platform}
        await _detect._probe_woocommerce_api(client, "https://fixture.invalid", signals)
    assert bool(signals[Platform.WOOCOMMERCE]) is expected


def test_sc05_weak_shopify_cdn_cannot_win_against_one_strong_woo_signal():
    from shopextract._detect import _determine_platform
    from shopextract._models import Platform

    signals = {platform: [] for platform in Platform}
    signals[Platform.SHOPIFY] = ["cdn:cdn.shopify.com"]
    signals[Platform.WOOCOMMERCE] = ["api:/wp-json/wc/v3"]
    platform, _ = _determine_platform(signals)
    assert platform is Platform.WOOCOMMERCE


def test_sc05_single_shopify_cdn_signal_is_not_sufficient():
    from shopextract._detect import _determine_platform
    from shopextract._models import Platform

    signals = {platform: [] for platform in Platform}
    signals[Platform.SHOPIFY] = ["cdn:cdn.shopify.com"]
    platform, _ = _determine_platform(signals)
    assert platform is Platform.GENERIC


@pytest.mark.asyncio
async def test_sc05_shopify_redirect_to_json_catalog_is_not_a_strong_signal():
    from shopextract import _detect
    from shopextract._models import Platform

    def route(request):
        if request.url.path == "/products.json":
            return httpx.Response(302, headers={"location": "/redirected-products.json"})
        return httpx.Response(200, json={"products": [{"id": 1}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(route), follow_redirects=True) as client:
        signals = {platform: [] for platform in Platform}
        await _detect._probe_shopify_api(client, "https://fixture.invalid", signals)
    assert signals[Platform.SHOPIFY] == []


def test_sc06_extract_output_file_stdout_is_summary_only(monkeypatch, tmp_path):
    import shopextract

    async def extract(*args, **kwargs):
        return ExtractionResult(products=[Product(title="Synthetic", price=Decimal("2.00"),
            raw_data={"large": "raw source"})], raw_products=[{"large": "raw source"}],
            catalog_complete=True, platform=Platform.GENERIC)

    monkeypatch.setattr(shopextract, "extract", extract)
    target = tmp_path / "products.json"
    result = invoke("extract", "https://fixture.invalid", "-o", str(target))
    assert result.exit_code == 0, result.output[:500]
    value = response(result)
    assert value["ok"] is True and value["error"] is None
    assert value["data"] == {"output_path": str(target), "product_count": 1, "completeness": "complete"}
    assert "products" in json.loads(target.read_text())["data"]


def test_sc06_partial_extract_file_stdout_reports_partial_summary(monkeypatch, tmp_path):
    import shopextract

    async def extract(*args, **kwargs):
        return ExtractionResult(products=[Product(title="Partial")], catalog_complete=False,
                                incompleteness_reasons=["catalog_coverage_unverified"])

    monkeypatch.setattr(shopextract, "extract", extract)
    target = tmp_path / "partial.json"
    result = invoke("extract", "https://fixture.invalid", "-o", str(target))
    assert result.exit_code == 3, result.output[:500]
    value = response(result)
    assert value["ok"] is True and value["error"] is None
    assert value["data"] == {"output_path": str(target), "product_count": 1, "completeness": "partial"}


def test_sc06_extract_prewrite_failure_reports_requested_path_without_file(monkeypatch, tmp_path):
    import shopextract
    from shopextract._cli_core import CliFailure

    async def broken(*args, **kwargs):
        raise CliFailure("E_OPERATION", "source failed")

    monkeypatch.setattr(shopextract, "extract", broken)
    target = tmp_path / "not-written.json"
    result = invoke("extract", "https://fixture.invalid", "-o", str(target))
    value = response(result)
    assert value["ok"] is False and value["error"]["code"] == "E_OPERATION"
    assert value["error"].get("cause") == "source_error"
    assert value["data"] == {"output_path": str(target), "product_count": 0, "completeness": None}
    assert not target.exists()


def test_sc06_extract_early_validation_failure_reports_requested_path_without_file(tmp_path):
    target = tmp_path / "invalid-url.json"
    result = invoke("extract", "file:///etc/passwd", "-o", str(target))
    value = response(result)
    assert result.exit_code == 2
    assert value["ok"] is False and value["error"]["code"] == "E_USAGE"
    assert value["data"] == {"output_path": str(target), "product_count": 0,
                              "completeness": None}
    assert not target.exists()


def test_sc06_extract_zero_product_failure_has_null_completeness(monkeypatch, tmp_path):
    import shopextract

    async def no_products(*args, **kwargs):
        return ExtractionResult(errors=["no product links found"], catalog_complete=False,
                                incompleteness_reasons=["no_product_links"])

    monkeypatch.setattr(shopextract, "extract", no_products)
    target = tmp_path / "empty.json"
    result = invoke("extract", "https://fixture.invalid", "-o", str(target))
    value = response(result)
    assert result.exit_code == 1
    assert value["ok"] is False and value["error"]["code"] == "E_OPERATION"
    assert value["data"] == {"output_path": str(target), "product_count": 0,
                              "completeness": None}
    assert not target.exists()


def test_sc06_extract_atomic_write_failure_keeps_extracted_summary(monkeypatch, tmp_path):
    import shopextract
    import shopextract._cli_extract as command
    from shopextract._cli_core import CliFailure

    async def extract(*args, **kwargs):
        return ExtractionResult(products=[Product(title="Synthetic")], catalog_complete=False,
                                incompleteness_reasons=["catalog_coverage_unverified"])

    def fail_write(*args, **kwargs):
        raise CliFailure("E_OPERATION", "Cannot write result file; existing output was preserved.")

    monkeypatch.setattr(shopextract, "extract", extract)
    monkeypatch.setattr(command, "atomic_json", fail_write)
    target = tmp_path / "failed-write.json"
    target.write_text("old artifact")
    result = invoke("extract", "https://fixture.invalid", "-o", str(target))
    value = response(result)
    assert value["ok"] is False and value["error"].get("cause") == "source_error"
    assert value["data"] == {"output_path": str(target), "product_count": 1,
                              "completeness": "partial"}
    assert target.read_text() == "old artifact"


def test_sc06_other_output_commands_keep_their_summaries_and_artifact_files(tmp_path):
    from shopextract._portable import product_to_record

    source = tmp_path / "catalog.json"
    source.write_text(json.dumps([product_to_record(Product(title="Portable fixture"))]))

    export_file = tmp_path / "export.json"
    exported = invoke("export", str(source), "--format", "json", "--output", str(export_file))
    assert exported.exit_code == 0, exported.output[:500]
    export_value = response(exported)
    assert export_value["data"]["output"] == str(export_file)
    assert "products" not in export_value["data"]
    assert export_value["data"]["format"] == "json"
    assert export_value["data"]["product_count"] == 1
    assert export_value["data"]["bytes"] == export_file.stat().st_size
    assert isinstance(json.loads(export_file.read_text()), list)

    raw_stdout = invoke("export", str(source), "--format", "json", "--output", "-")
    assert raw_stdout.exit_code == 0, raw_stdout.output[:500]
    assert isinstance(json.loads(raw_stdout.stdout), list), raw_stdout.stdout[:500]

    bundle_file = tmp_path / "bundle.json"
    bundled = invoke("evidence", "bundle", "create", str(source), "--output", str(bundle_file))
    assert bundled.exit_code == 0, bundled.output[:500]
    assert response(bundled)["data"] == {"output": str(bundle_file)}
    assert "products" not in response(bundled)["data"]
    assert "records" in json.loads(bundle_file.read_text())

    payload = tmp_path / "payload.csv"
    payload.write_text("title,price\nPortable fixture,1.00\n")
    sidecar_file = tmp_path / "sidecar.json"
    sidecar = invoke("evidence", "sidecar", "create", str(source), "--payload", str(payload),
                     "--format", "csv", "--output", str(sidecar_file))
    assert sidecar.exit_code == 0, sidecar.output[:500]
    assert response(sidecar)["data"] == {"output": str(sidecar_file)}
    assert "sha256" in json.loads(sidecar_file.read_text())

    from shopextract.categories.contracts import CategoryScope
    from shopextract.categories.woo_tree import WooCategoryTree, WooTreeLimits, woo_tree_to_record
    tree = WooCategoryTree(scope=CategoryScope(Platform.WOOCOMMERCE, "https://fixture.invalid"),
        limits=WooTreeLimits(), outcome="unavailable", confirmed_empty=False,
        reasons=("transport_error",), pages=(), nodes=(), rejected=(), parent_edges=(),
        issues=(), attempts=())
    tree_source = tmp_path / "tree.json"
    tree_source.write_text(json.dumps(woo_tree_to_record(tree)))
    tree_file = tmp_path / "tree-export.json"
    tree_result = invoke("categories", "tree", "export", str(tree_source), "--output", str(tree_file))
    assert tree_result.exit_code == 1, tree_result.output[:500]
    tree_response = response(tree_result)
    assert tree_response["ok"] is False and tree_response["error"]["code"] == "E_OPERATION"
    tree_data = tree_response["data"]
    assert set(tree_data) == {"output", "outcome", "reasons", "node_count", "confirmed_empty"}
    assert tree_data["output"] == str(tree_file)
    assert tree_data["outcome"] == "unavailable" and tree_file.exists()
    assert json.loads(tree_file.read_text()) == json.loads(tree_source.read_text())


def test_sc06_bundle_and_sidecar_load_commands_write_portable_artifacts(tmp_path):
    from shopextract._portable import product_to_record

    source = tmp_path / "source.json"
    source.write_text(json.dumps([product_to_record(Product(title="Load fixture"))]))

    bundle = tmp_path / "bundle.json"
    created = invoke("evidence", "bundle", "create", str(source), "--output", str(bundle))
    assert created.exit_code == 0, created.output[:500]
    restored_bundle = tmp_path / "from-bundle.json"
    loaded = invoke("evidence", "bundle", "load", str(bundle), "--output", str(restored_bundle))
    assert loaded.exit_code == 0, loaded.output[:500]
    assert response(loaded)["data"] == {"output": str(restored_bundle)}
    assert json.loads(restored_bundle.read_text())[0]["product"]["title"] == "Load fixture"

    payload = tmp_path / "payload.csv"
    payload.write_text("title,price\nLoad fixture,1.00\n")
    sidecar = tmp_path / "sidecar.json"
    sidecar_result = invoke("evidence", "sidecar", "create", str(source), "--payload",
                            str(payload), "--format", "csv", "--output", str(sidecar))
    assert sidecar_result.exit_code == 0, sidecar_result.output[:500]
    restored_sidecar = tmp_path / "from-sidecar.json"
    loaded_sidecar = invoke("evidence", "sidecar", "load", str(sidecar), "--payload",
                            str(payload), "--output", str(restored_sidecar))
    assert loaded_sidecar.exit_code == 0, loaded_sidecar.output[:500]
    assert response(loaded_sidecar)["data"] == {"output": str(restored_sidecar)}
    assert json.loads(restored_sidecar.read_text())[0]["product"]["title"] == "Load fixture"


def test_sc06_actual_atomic_replace_failure_preserves_existing_artifact(monkeypatch, tmp_path):
    import shopextract
    import shopextract._cli_data as cli_data

    async def extract(*args, **kwargs):
        return ExtractionResult(products=[Product(title="New value")], catalog_complete=True)

    real_replace = os.replace
    target = tmp_path / "existing.json"
    target.write_text("old value")

    def fail_target_replace(source, destination):
        if Path(destination) == target:
            raise OSError("injected replace failure")
        return real_replace(source, destination)

    monkeypatch.setattr(shopextract, "extract", extract)
    monkeypatch.setattr(cli_data.os, "replace", fail_target_replace)
    result = invoke("extract", "https://fixture.invalid", "-o", str(target))
    value = response(result)
    assert value["ok"] is False and value["error"]["code"] == "E_OPERATION"
    assert value["data"] == {"output_path": str(target), "product_count": 1,
                              "completeness": "complete"}
    assert target.read_text() == "old value"


@pytest.mark.asyncio
async def test_sc06_categories_tree_complete_export_has_exact_metadata(tmp_path):
    from datetime import datetime, timezone
    from shopextract.categories.contracts import CategoryScope
    from shopextract.categories.woo_tree import (
        WooTreeLimits, fetch_woocommerce_category_tree, woo_tree_to_record,
    )

    async def acquire():
        async def public_resolver(host, context):
            return ["93.184.216.34"]

        def wire(request):
            return httpx.Response(200, json=[{"id": 1, "name": "Fryers", "slug": "fryers", "parent": 0}],
                headers={"X-WP-Total": "1", "X-WP-TotalPages": "1"})

        return await fetch_woocommerce_category_tree(
            CategoryScope(Platform.WOOCOMMERCE, "https://fixture.invalid"),
            limits=WooTreeLimits(per_page=2), resolver=public_resolver,
            wire_transport=httpx.MockTransport(wire),
            utc_now=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc))

    tree = await acquire()
    assert tree.outcome == "complete"
    source = tmp_path / "tree.json"
    source.write_text(json.dumps(woo_tree_to_record(tree)))
    target = tmp_path / "tree-export.json"
    result = invoke("categories", "tree", "export", str(source), "--output", str(target))
    assert result.exit_code == 0, result.output[:500]
    data = response(result)["data"]
    assert data == {"output": str(target), "outcome": "complete", "reasons": [],
                    "node_count": 1, "confirmed_empty": False}
    assert json.loads(target.read_text()) == json.loads(source.read_text())


def test_sc07_default_payload_is_compact_and_evidence_is_explicit_opt_in():
    from datetime import datetime, timezone
    from shopextract import Evidence, TrustContract

    products = [Product(title=f"A{index}", raw_data={"private": "x" * 15000}) for index in range(40)]
    evidence_id = "e_00000000-0000-4000-8000-000000000001"
    evidence = Evidence(evidence_id, "https://fixture.invalid/catalog", datetime(2026, 1, 1, tzinfo=timezone.utc),
                        "api", "fixture source record")
    products[0].evidence_contract = TrustContract([evidence], [])
    result = ExtractionResult(products=products,
                              raw_products=[{"private": "x" * 15000} for _ in range(40)],
                              platform=Platform.GENERIC)
    compact = _cli_data.extraction_data(result)
    assert "raw_products" not in compact
    assert "raw_data" not in compact["products"][0]["product"]
    assert "evidence_contract" not in compact["products"][0]
    assert "variant_contracts" not in compact["products"][0]
    assert len(json.dumps(compact, separators=(",", ":")).encode()) <= 512 * 1024
    try:
        full = _cli_data.extraction_data(result, include_evidence=True)
    except TypeError as error:
        pytest.fail(f"serializer lacks --include-evidence contract: {error}")
    assert full["raw_products"] == result.raw_products
    record = full["products"][0]
    assert record["product"]["raw_data"] == products[0].raw_data
    assert record["evidence_contract"]["evidence"][0]["evidence_id"] == evidence_id
    assert record["variant_contracts"] == []


def test_sc07_forty_large_normalized_titles_remain_just_under_default_size_cap():
    result = ExtractionResult(products=[Product(title=f"P{index}-" + "x" * 10300)
                                        for index in range(40)],
                              platform=Platform.GENERIC)
    compact = _cli_data.extraction_data(result)
    encoded = json.dumps(compact, separators=(",", ":")).encode()
    assert int(0.75 * 512 * 1024) < len(encoded) <= 512 * 1024


def test_sc08_shopify_missing_price_context_zero_compare_at_and_canonical_url():
    from shopextract._normalize import normalize

    raw = {"id": 1, "title": "Anex fryer", "handle": "anex-fryer", "vendor": "Anex",
           "variants": [{"id": 2, "price": "10.00", "compare_at_price": "0", "sku": "AG-2017"}],
           "images": []}
    product = normalize(raw, Platform.SHOPIFY, "https://shop.invalid/collections/fryers")
    assert not product.currency, "currency must not be fabricated without price-context evidence"
    assert product.compare_at_price is None
    assert product.product_url == "https://shop.invalid/products/anex-fryer"

    request_price = {"id": 3, "title": "Anex fryer", "body_html": "Price on request",
                     "variants": [{"id": 4, "price": "0", "available": True}]}
    unavailable = normalize(request_price, Platform.SHOPIFY, "https://shop.invalid")
    assert unavailable.price is None and unavailable.in_stock is None


@pytest.mark.parametrize(("shop_currency", "price_currency", "expected"), [
    ("EUR", "EUR", "EUR"), ("USD", "CAD", ""), ("", "EUR", "EUR"),
])
def test_sc08_currency_must_match_extracted_price_context(shop_currency, price_currency, expected):
    from shopextract._normalize import normalize

    raw = {"id": 10, "title": "Context fryer", "_shop_currency": shop_currency,
           "variants": [{"id": 11, "price": "25.00", "price_currency": price_currency}]}
    product = normalize(raw, Platform.SHOPIFY, "https://shop.invalid")
    assert product.currency == expected


def test_sc09_normalizer_accepts_extract_envelope_and_rejects_false_or_unrelated():
    from shopextract._cli_data import products_from_value
    from shopextract._portable import product_to_record

    record = product_to_record(Product(title="Synthetic"))
    envelope = {"schema_version": "1.0", "ok": True, "data": {"products": [record]}}
    assert len(products_from_value(envelope)) == 1
    assert products_from_value({"schema_version": "1.0", "ok": True,
                                "data": {"products": []}}) == []
    rejected = ({"schema_version": "1.0", "ok": False, "data": {"products": []}},
                {"@type": "Product", "name": "not an extract"}, {"schema_version": "1.0", "data": {}})
    for value in rejected:
        with pytest.raises(_cli_core.CliFailure) as failure:
            products_from_value(value)
        assert failure.value.code == "E_VALIDATION" and failure.value.message


def test_sc09_raw_object_array_compatibility_and_invalid_item_drop():
    one = {"title": "Raw fixture", "price": "10.00", "sku": "RAW-1"}
    object_result = invoke("normalize", "-", "--platform", "generic", input=json.dumps(one))
    assert object_result.exit_code == 0, object_result.output[:500]
    assert response(object_result)["data"]["product_count"] == 1

    array_result = invoke("normalize", "-", "--platform", "generic",
                          input=json.dumps([one, {"description": "no product evidence"}]))
    assert array_result.exit_code == 0, array_result.output[:500]
    array_data = response(array_result)["data"]
    assert array_data["product_count"] == 1 and array_data["dropped_indices"] == [1]


def test_sc10_brand_breakdown_casefolds_and_uses_stable_display_spelling():
    from shopextract.analyze.stats import brand_breakdown

    products = [{"vendor": " Dawlance "}, {"vendor": "dawlance"}, {"vendor": "DAWLANCE"},
                {"vendor": "Other"}]
    result = brand_breakdown(products)
    assert len(result) == 2
    daw_lance = next((key for key in result if key.casefold() == "dawlance"), None)
    assert daw_lance is not None and result[daw_lance] == 75.0
    assert result["Other"] == 25.0
    assert [p["vendor"] for p in products[:3]] == [" Dawlance ", "dawlance", "DAWLANCE"]


def test_sc10_brand_display_group_is_independent_of_input_order():
    from shopextract.analyze.stats import brand_breakdown

    vendors = ["Dawlance", "dawlance", "DAWLANCE", "Other"]
    forward = [{"vendor": value} for value in vendors]
    reverse = [{"vendor": value} for value in reversed(vendors)]
    assert brand_breakdown(forward) == brand_breakdown(reverse)
    result = brand_breakdown(forward)
    daw_lance = next((key for key in result if key.casefold() == "dawlance"), None)
    assert daw_lance is not None and result[daw_lance] == 75.0
    assert result["Other"] == 25.0


def test_sc11_duplicate_candidate_index_preserves_three_positives_and_two_conflict_negatives():
    from shopextract.validate.duplicates import find_duplicates

    products = [
        {"id": "dup-001-a", "title": "Anex AG-2017 Deluxe Air Fryer", "vendor": "Anex", "sku": "AG-2017"},
        {"id": "dup-001-b", "title": "Anex AG-2017 Deluxe Air Fryer", "vendor": "Anex", "sku": "AG-2017"},
        {"id": "dup-002-a", "title": "Westpoint WF-4257 Air Fryer", "vendor": "Westpoint", "sku": "WF-4257"},
        {"id": "dup-002-b", "title": "Westpoint WF-4257 Air Fryer", "vendor": "Westpoint", "sku": "WF-4257"},
        {"id": "dup-003-a", "title": "Dawlance DW-1130 Air Fryer", "vendor": "Dawlance", "sku": "DW-1130"},
        {"id": "dup-003-b", "title": "Dawlance DW-1130 Air Fryer", "vendor": "Dawlance", "sku": "DW-1130"},
        {"id": "dup-004-a", "title": "Anex AG-2121 Deluxe Air Fryer", "vendor": "Anex", "sku": "AG-2121"},
        {"id": "dup-004-b", "title": "Anex AG-2123 Deluxe Air Fryer", "vendor": "Anex", "sku": "AG-2123"},
        {"id": "dup-005-a", "title": "QX 900 air fryer", "vendor": "Brand A"},
        {"id": "dup-005-b", "title": "QX 900 air fryer", "vendor": "Brand B"},
    ]
    products.extend({"title": f"Unique product {index} with token{index}",
                     "vendor": f"V{index}"} for index in range(335))
    started = time.monotonic()
    pairs = find_duplicates(products, method="title", threshold=0.9)
    elapsed = time.monotonic() - started
    assert {(a, b) for a, b, _ in pairs} == {(0, 1), (2, 3), (4, 5)}
    assert elapsed < 3.0


def test_sc11_duplicate_threshold_includes_at_and_below_but_excludes_above_boundary():
    from difflib import SequenceMatcher
    from shopextract.validate.duplicates import find_duplicates

    products = [{"title": "Anex AG-2017 Deluxe Air Fryer", "vendor": "Anex", "sku": "AG-2017"},
                {"title": "Anex AG-2017 Delux Air Fryer", "vendor": "Anex", "sku": "AG-2017"}]
    ratio = SequenceMatcher(None, products[0]["title"].lower(), products[1]["title"].lower()).ratio()
    assert find_duplicates(products, method="title", threshold=ratio) == [(0, 1, ratio)]
    assert find_duplicates(products, method="title", threshold=ratio - 0.001) == [(0, 1, ratio)]
    assert find_duplicates(products, method="title", threshold=ratio + 0.001) == []


def test_sc11_rare_shared_model_token_survives_candidate_blocking():
    from shopextract.validate.duplicates import find_duplicates

    products = [
        {"title": "HEPA filter cartridge ZXQ-9307", "vendor": "FilterCo"},
        {"title": "ZXQ-9307 replacement component", "vendor": "FilterCo"},
    ]
    products.extend({"title": f"Unrelated household item model ITEM-{index}",
                     "vendor": f"Brand{index}"} for index in range(80))
    pairs = find_duplicates(products, method="title", threshold=0.25)
    assert any((left, right) == (0, 1) for left, right, _ in pairs)


def test_sc12_cloud_notice_env_is_set_before_first_crawl4ai_import():
    env = dict(os.environ)
    env["CRAWL4AI_NO_CLOUD_NOTICE"] = "0"
    check = subprocess.run([sys.executable, "-c",
        "import os; import shopextract.extractors._browser; "
        "print('ENV=' + str(os.environ.get('CRAWL4AI_NO_CLOUD_NOTICE')))"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=10)
    assert check.returncode == 0, check.stderr[:500]
    assert "ENV=1" in check.stdout
    combined = (check.stdout + "\n" + check.stderr).lower()
    assert "crawl4ai cloud" not in combined and "cloud notice" not in combined


def test_sc12_normal_diagnostics_still_emit_a_cli_diagnostic(monkeypatch):
    import shopextract
    from click.testing import CliRunner

    async def discovered(*args, **kwargs):
        return ["https://fixture.invalid/products/item"]

    monkeypatch.setattr(shopextract, "discover", discovered)
    result = CliRunner(mix_stderr=False).invoke(
        main, ["--output-format", "legacy", "--diagnostics", "normal", "discover", "https://fixture.invalid"])
    assert result.exit_code == 0, result.output[:500]
    assert "1 URLs discovered" in result.stderr
    assert "1 URLs discovered" not in result.stdout


@pytest.mark.skip(reason="SC-13 is the separately bounded live-only haiermall observation")
def test_sc13_live_rendered_dom_title_price_and_parsed_product():
    raise AssertionError("Never contact live sources from offline acceptance tests")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Blocked: no stable injected seam exposes detector page HTML consumption by extraction")
async def test_sc14_extraction_reuses_detection_context_without_second_root_fetch():
    pytest.fail("Blocked until extraction accepts and consumes the detector context seam")


@pytest.mark.asyncio
@pytest.mark.parametrize(("retry_after", "expected_wait", "expected_result"), [
    (29, [29.0], True),
    (30, [], False),
    (31, [], False),
])
async def test_sc14_retry_after_boundaries_use_injected_remaining_clock(
        monkeypatch, retry_after, expected_wait, expected_result):
    from shopextract.extractors import _retry

    remaining = [30.0]
    waits = []

    def fake_remaining():
        return remaining[0]

    async def fake_sleep(delay):
        waits.append(delay)
        remaining[0] -= delay

    monkeypatch.setattr(_retry, "remaining_execution_seconds", fake_remaining)
    monkeypatch.setattr(_retry.asyncio, "sleep", fake_sleep)
    result = await _retry.wait_for_retry(str(retry_after))

    assert waits == expected_wait
    assert result is expected_result


@pytest.mark.asyncio
async def test_sc14_detection_probes_origin_sequentially_and_stops_at_shopify_signal():
    import asyncio
    from shopextract._detect import detect

    calls = []
    active = 0
    max_active = 0

    class Recorder(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            nonlocal active, max_active
            active += 1
            max_active = max(max_active, active)
            calls.append((request.method, request.url.host, request.url.path))
            await asyncio.sleep(0)
            active -= 1
            if request.url.path == "/products.json":
                return httpx.Response(200, json={"products": [{"id": 1}]}, request=request)
            return httpx.Response(404, request=request)

    async with httpx.AsyncClient(transport=Recorder(), follow_redirects=False) as client:
        result = await detect("https://fixture.invalid/collections/fryers?page=2", client=client)

    assert result.platform is Platform.SHOPIFY
    assert len(calls) <= 2, calls
    assert max_active == 1, f"probe requests overlapped: {calls}"
    assert all(host == "fixture.invalid" for _, host, _ in calls)
    product_probe = next(index for index, (_, _, path) in enumerate(calls)
                         if path == "/products.json")
    assert all(path not in ("/wp-json/", "/graphql", "/rest/V1/store/storeConfigs",
                            "/api/_info/config") for _, _, path in calls[product_probe + 1:])
    assert sum(path == "/collections/fryers" for _, _, path in calls) <= 1


@pytest.mark.skip(reason="Blocked: detector has no injected execution-clock/retry policy seam; 29/30/31 is only covered at the retry helper boundary")
@pytest.mark.asyncio
async def test_sc14_detection_429_retry_after_uses_operation_deadline_boundary():
    pytest.fail("Blocked until detector accepts an injected execution clock/retry policy")


@pytest.mark.parametrize(("error_text", "reason", "cause", "retryable", "retry_after"), [
    ("HTTP 429 Retry-After: 31", "rate_limited", "rate_limited", True, 31),
    ("HTTP 403 Forbidden", "blocked", "blocked", False, None),
    ("DNS lookup failed", "dns_failure", "dns_failure", False, None),
    ("connection refused", "network_unreachable", "network_unreachable", True, None),
    ("connection timed out", "source_timeout", "network_unreachable", True, None),
    ("no product links found", "no_product_links", "no_product_links", False, None),
    ("unexpected source parser failure", "source_failed", "source_error", False, None),
])
def test_sc02_zero_product_failure_maps_source_error_matrix(
        monkeypatch, error_text, reason, cause, retryable, retry_after):
    import shopextract

    async def failed(*args, **kwargs):
        result = ExtractionResult(errors=[error_text], catalog_complete=False,
                                  incompleteness_reasons=[reason])
        if retry_after is not None:
            result.retry_after_seconds = retry_after
        return result

    monkeypatch.setattr(shopextract, "extract", failed)
    result = invoke("extract", "https://fixture.invalid", "--platform", "generic")
    value = response(result)
    assert value["ok"] is False and value["data"] is None
    assert value["error"]["cause"] == cause
    assert value["error"]["retryable"] is retryable
    assert value["error"]["errors"] == [error_text]
    assert value["error"]["incompleteness_reasons"] == [reason]
    if retry_after is not None:
        assert value["error"]["retry_after_seconds"] == retry_after


def test_sc02_internal_deadline_has_source_error_cause_and_is_retryable(monkeypatch):
    import shopextract._cli_extract as command
    from shopextract._cli_core import CliFailure

    def deadline(*args, **kwargs):
        raise CliFailure("E_TIMEOUT", "Operation deadline exceeded")

    monkeypatch.setattr(command, "run_operation", deadline)
    value = response(invoke("extract", "https://fixture.invalid", "--platform", "generic"))
    assert value["ok"] is False
    assert value["error"]["cause"] == "source_error"
    assert value["error"]["retryable"] is True


def test_sc02_feed_no_product_links_preserves_failure_metadata(monkeypatch):
    import shopextract

    async def feed(*args, **kwargs):
        return ExtractionResult(errors=["No product links found in feed"], catalog_complete=False,
                                incompleteness_reasons=["no_product_links"])

    monkeypatch.setattr(shopextract, "from_feed", feed)
    value = response(invoke("feed", "https://fixture.invalid/feed.csv"))
    assert value["ok"] is False
    assert value["error"]["cause"] == "no_product_links"
    assert value["error"]["retryable"] is False
    assert value["error"]["errors"] == ["No product links found in feed"]
    assert value["error"]["incompleteness_reasons"] == ["no_product_links"]
