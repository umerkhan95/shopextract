"""Unified crawl extractor -- one crawl, all extraction layers.

Extracts from every available data layer:
  Layer 1: JSON-LD from result.html
  Layer 2: OG tags from result.metadata + result.html
  Layer 3: Price/title from result.markdown
  Layer 4: Best image from result.media

httpx fast path: fetches HTML via httpx first. If JSON-LD yields a product
with both price and image, returns immediately (no browser).
"""

from __future__ import annotations

import hashlib
import logging
import re
from urllib.parse import urljoin
from typing import Any

import httpx

from . import _markdown_price as markdown_price_extractor
from .._models import ExtractorResult
from .._execution import browser_allowed
from .._capture import capture
from .._structured_html import extract_structured_products, StructuredHTMLResult, coverage_issues
from .._product_admission import has_product_evidence, crawl_document_allowed

from ._browser import (
    DEFAULT_HEADERS,
    StealthLevel,
    get_browser_config,
    get_crawl_config,
    get_crawler_strategy,
    get_default_user_agent,
)
from ._opengraph import OpenGraphExtractor
from ._schema_org import SchemaOrgExtractor
from ._product_html import enrich_product_html, usable_image

logger = logging.getLogger(__name__)

_MIN_IMAGE_SCORE = 3
_MAX_RESPONSE_SIZE = 10 * 1024 * 1024


class UnifiedCrawlExtractor:
    """Extract product data by crawling once and layering all parsers on the result."""

    _ESCALATION_ORDER = [StealthLevel.STANDARD, StealthLevel.STEALTH, StealthLevel.UNDETECTED]

    def __init__(
        self,
        stealth_level: StealthLevel = StealthLevel.STANDARD,
        http_client: httpx.AsyncClient | None = None,
    ):
        self._stealth_level = stealth_level
        self._http_client = http_client

    async def extract(self, shop_url: str) -> ExtractorResult:
        """Extract product data from a single URL."""
        url = shop_url
        from .._execution import record_progress_attempt,record_progress_rows
        record_progress_attempt(url)
        html = await self._fetch_html_httpx(url)
        if html:
            parsed = extract_structured_products(html, getattr(html, "source_url", url))
            products = parsed.products
            record_progress_rows(products,url)
            issues = coverage_issues(parsed.diagnostics)
            if issues:
                return ExtractorResult(products=products,complete=False,
                    error='; '.join(d['code'] for d in issues))
            for product in products:
                if "_capture" in product and hasattr(html, "observed_at"):
                    product["_capture"]["at"] = html.observed_at.isoformat()
            if products and all(self._has_price_and_image(p) for p in products):
                return ExtractorResult(products=products)
            httpx_products = products
        else:
            httpx_products = []

        if not browser_allowed():
            return ExtractorResult(products=httpx_products)

        browser_parsed = await self._extract_with_browser(url,include_diagnostics=True)
        browser_products = browser_parsed.products
        if browser_products:record_progress_rows(browser_products,url)
        issues = coverage_issues(browser_parsed.diagnostics)
        if issues:
            return ExtractorResult(products=browser_products or httpx_products,complete=False,error='; '.join(d['code'] for d in issues))
        if browser_products:
            return ExtractorResult(products=browser_products)

        if httpx_products:
            return ExtractorResult(products=httpx_products)

        return ExtractorResult(products=[])

    async def extract_batch(self, urls: list[str]) -> ExtractorResult:
        """Extract from multiple URLs using a single browser via arun_many()."""
        if not urls:
            return ExtractorResult(products=[])

        from .._execution import record_progress_rows
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher

        browser_config = get_browser_config(self._stealth_level)
        crawl_config = get_crawl_config(stealth_level=self._stealth_level, scan_full_page=True)
        dispatcher = MemoryAdaptiveDispatcher(
            max_session_permit=5,
            memory_threshold_percent=70.0,
        )

        all_products: list[dict] = []
        error: str | None = None

        try:
            crawler_strategy = get_crawler_strategy(self._stealth_level, browser_config)
            async with AsyncWebCrawler(
                config=browser_config,
                crawler_strategy=crawler_strategy,
            ) as crawler:
                results = await crawler.arun_many(urls=urls, config=crawl_config, dispatcher=dispatcher)
                for result in results:
                    if not crawl_document_allowed(result):
                        error = "Browser document failed HTTP/product admission"
                        continue
                    parsed = self._extract_from_crawl_result(result, result.url,include_diagnostics=True)
                    products=parsed.products
                    if products:record_progress_rows(products,result.url)
                    issues=coverage_issues(parsed.diagnostics)
                    if issues:error='; '.join(d['code'] for d in issues)
                    if not products:
                        error = f"Browser document has no admitted product evidence: {result.url}"
                    all_products.extend(products)
        except Exception as e:
            logger.exception("Batch unified crawl failed: %s", e)
            error = str(e)

        return ExtractorResult(products=all_products, complete=error is None, error=error)

    # -- httpx fast path ------------------------------------------------------

    async def _fetch_html_httpx(self, url: str) -> str | None:
        try:
            headers = {**DEFAULT_HEADERS, "User-Agent": get_default_user_agent()}
            client = self._http_client or httpx.AsyncClient(
                follow_redirects=True, timeout=30.0, headers=headers,
            )
            try:
                response = await client.get(url)
                response.raise_for_status()

                content_length = int(response.headers.get("content-length", 0))
                if content_length > _MAX_RESPONSE_SIZE:
                    return None

                html = response.text
                if len(html) > _MAX_RESPONSE_SIZE:
                    return None

                return _CapturedHTML(html, str(response.url))
            finally:
                if self._http_client is None:
                    await client.aclose()

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (403, 429, 503):
                logger.debug("httpx blocked (%d) for %s, will try browser", e.response.status_code, url)
            return None
        except httpx.RequestError as e:
            logger.debug("httpx request error for %s: %s", url, e)
            return None

    @staticmethod
    def _extract_structured_from_html(html: str, url: str, *, include_categories=False) -> list[dict]:
        return extract_structured_products(html,url,include_categories=include_categories).products

    # -- Browser path ---------------------------------------------------------

    async def _extract_with_browser(self, url: str, *, include_diagnostics=False):
        diagnostics=[]
        def finish(products):return StructuredHTMLResult(products,diagnostics) if include_diagnostics else products
        from crawl4ai import AsyncWebCrawler

        levels = [
            level for level in self._ESCALATION_ORDER
            if self._ESCALATION_ORDER.index(level) >= self._ESCALATION_ORDER.index(self._stealth_level)
        ]

        if not levels:
            return finish([])

        max_level = levels[-1]
        browser_config = get_browser_config(max_level)
        crawler_strategy = get_crawler_strategy(max_level, browser_config)

        try:
            async with AsyncWebCrawler(
                config=browser_config,
                crawler_strategy=crawler_strategy,
            ) as crawler:
                for level in levels:
                    crawl_config = get_crawl_config(stealth_level=level, scan_full_page=True)
                    try:
                        result = await crawler.arun(url=url, config=crawl_config)
                        if not crawl_document_allowed(result):
                            continue
                        parsed = self._extract_from_crawl_result(result, getattr(result, "url", None) or url,include_diagnostics=True)
                        products=parsed.products;diagnostics.extend(parsed.diagnostics)
                        if products:
                            return finish(products)
                    except Exception as e:
                        logger.debug("Browser crawl at stealth level %s failed for %s: %s", level.value, url, e)
                        continue
        except Exception as e:
            logger.warning("Browser startup error for %s: %s", url, e)

        return finish([])

    # -- Core extraction from CrawlResult -------------------------------------

    @staticmethod
    def _extract_from_crawl_result(result: Any, url: str, *, include_diagnostics=False):
        url = getattr(result, "url", None) or url
        html = getattr(result, "html", "") or ""
        metadata = getattr(result, "metadata", {}) or {}

        md_obj = getattr(result, "markdown", None)
        if md_obj and hasattr(md_obj, "fit_markdown"):
            fit_markdown = md_obj.fit_markdown or ""
            markdown = (md_obj.raw_markdown if hasattr(md_obj, "raw_markdown") else str(md_obj)) or ""
        elif isinstance(md_obj, str):
            markdown = md_obj or ""
            fit_markdown = ""
        else:
            markdown = ""
            fit_markdown = ""

        media = getattr(result, "media", {}) or {}

        parsed=extract_structured_products(html,url) if html else StructuredHTMLResult([],[])
        def finish(products):return StructuredHTMLResult(products,parsed.diagnostics) if include_diagnostics else products
        products=parsed.products

        # Layer 2: OG tags
        og_from_meta = OpenGraphExtractor.from_metadata(metadata) if metadata else []
        og_from_html = OpenGraphExtractor.extract_from_html(html, url) if html else []
        og = _merge_og(og_from_meta, og_from_html)
        if og:
            capture(og, url, "opengraph_crawl")

        # Layer 3: Markdown price/title
        md_text = fit_markdown or markdown
        md_data = markdown_price_extractor.extract(md_text, url) if md_text else {}

        # Layer 4: Best image from media
        best_image = _extract_best_image(media)

        if products:
            matches=[p for p in products if p.get('url')==url or p.get('@id')==url]
            owner=matches[0] if len(matches)==1 else products[0] if len(products)==1 else None
            if owner is not None:
                schema='name' in owner
                selected_image=og.get('og:image') or best_image
                if selected_image and ('/placeholder/' in selected_image.lower() or selected_image.startswith('data:')):selected_image=best_image
                offers=owner.get('offers') or {}
                structured_offer=offers[0] if isinstance(offers,list) else offers
                contexts=[v for v in [structured_offer.get('priceCurrency') if isinstance(structured_offer,dict) else None,
                    metadata.get('product:price:currency'),metadata.get('og:price:currency'),
                    og.get('product:price:currency'),og.get('og:price:currency')] if v]
                contexts=[v.strip().upper() if isinstance(v,str) else v for v in contexts]
                context=contexts[0] if contexts else None
                md_data=markdown_price_extractor.extract(md_text,url,currency=context) if md_text else {}
                from .._normalization import Normalizer
                authorities=contexts+([md_data['currency']] if md_data.get('currency') else [])
                n=Normalizer({str(i):v for i,v in enumerate(authorities)})
                currency=n.currency('currency',*['/'+str(i) for i in range(len(authorities))]) if authorities else ''
                # A found explicit markdown currency conflicting with context is unresolved.
                explicit=markdown_price_extractor.extract(md_text,url) if md_text else {}
                if explicit.get('currency') and context and explicit['currency']!=context:currency=''
                if authorities and (not currency or len(set(authorities))>1):
                    parsed.diagnostics.append({'code':'currency_conflict','message':'Captured rendered currency authorities conflict or are invalid'})
                prices=[mapping[k] for mapping in (metadata,og) for k in ('product:price:amount','og:price:amount') if k in mapping and mapping[k] is not None]
                rendered={'metadata':metadata,'markdown':md_text,'price':prices[0] if prices else md_data.get('price'),
                          'currency':currency,'image':urljoin(url,selected_image) if selected_image else None,
                          'description':og.get('og:description'),'url':og.get('og:url')}
                source=capture({'rendered':rendered},url,'browser_rendered',excerpt=md_text or None)['_capture']
                def put(path,value,source_key):
                    parts=path[1:].split('/');target=owner
                    for token in parts[:-1]:target=target[int(token)] if isinstance(target,list) else target.setdefault(token,{})
                    target[parts[-1]]=value
                    owner.setdefault('_field_sources',{})[path]={'capture_path':'/rendered/'+source_key,'_capture':source}
                for key,field in [('description','description' if schema else 'og:description'),('url','url' if schema else 'og:url')]:
                    if rendered[key] and not owner.get(field):put('/'+field,rendered[key],key)
                if rendered['image'] and not (owner.get('image') or owner.get('og:image')):put('/image' if schema else '/og:image',rendered['image'],'image')
                if schema:
                    offers=owner.get('offers')
                    if not offers:owner['offers']={};offers=owner['offers']
                    offer=offers[0] if isinstance(offers,list) else offers
                    prefix='/offers/0' if isinstance(offers,list) else '/offers'
                    if isinstance(offer,dict):
                        if 'price' not in offer and rendered['price'] is not None:put(prefix+'/price',rendered['price'],'price')
                        if contexts and not currency:
                            offer['priceCurrency']=''
                        elif not offer.get('priceCurrency') and currency:put(prefix+'/priceCurrency',currency,'currency')
                else:
                    if not any(k in owner for k in ('og:price:amount','product:price:amount')) and rendered['price'] is not None:put('/product:price:amount',rendered['price'],'price')
                    if contexts and not currency:
                        for key in ('product:price:currency','og:price:currency'):
                            if key in owner:owner[key]=''
                    elif not owner.get('product:price:currency') and currency:put('/product:price:currency',currency,'currency')
            return finish(products)

        if og or md_data:
            product: dict = {}
            if og:
                product.update(og)
            _fill_gaps_from_markdown(product, md_data)
            if best_image:
                _fill_image(product, best_image)
            if product and _has_product_signal(product, og):
                return finish([product])

        return finish([])

    @staticmethod
    def _has_price_and_image(product: dict) -> bool:
        has_price = bool(_get_price(product))
        has_image = usable_image(product.get("image")) or usable_image(product.get("og:image"))
        return has_price and has_image


# -- Helper functions (module-level, stateless) -------------------------------

def _get_price(product: dict) -> str | None:
    price = product.get("price")
    if price and str(price).strip() and str(price).strip() != "0":
        return str(price)

    offers = product.get("offers")
    if isinstance(offers, dict):
        p = offers.get("price")
        if p and str(p).strip() and str(p).strip() != "0":
            return str(p)
    elif isinstance(offers, list):
        for offer in offers:
            if isinstance(offer, dict):
                p = offer.get("price")
                if p and str(p).strip() and str(p).strip() != "0":
                    return str(p)

    for key in ("og:price:amount", "product:price:amount"):
        val = product.get(key)
        if val and str(val).strip() and str(val).strip() != "0":
            return str(val)

    return None


def _fill_gaps_from_og(product: dict, og: dict) -> None:
    if not og:
        return
    mapping = {
        "og:title": "name",
        "og:image": "og:image",
        "og:description": "description",
        "og:url": "url",
        "og:price:amount": "og:price:amount",
        "product:price:amount": "product:price:amount",
        "product:price:currency": "product:price:currency",
    }
    for og_key, product_key in mapping.items():
        val = og.get(og_key)
        if val and not product.get(product_key):
            product[product_key] = val
    if not product.get("image") and og.get("og:image"):
        product["og:image"] = og["og:image"]


def _fill_gaps_from_markdown(product: dict, md_data: dict) -> None:
    if not md_data:
        return
    if md_data.get("name") and not product.get("name") and not product.get("og:title"):
        product["name"] = md_data["name"]
    if md_data.get("price") and not _get_price(product):
        product["price"] = md_data["price"]
        if md_data.get("currency"):
            if not product.get("priceCurrency") and not product.get("product:price:currency"):
                product["priceCurrency"] = md_data["currency"]


def _fill_image(product: dict, image_url: str) -> None:
    if usable_image(image_url) and not usable_image(product.get("image")) and not usable_image(product.get("og:image")):
        product["og:image"] = image_url


def _extract_best_image(media: dict | list) -> str | None:
    images = []
    if isinstance(media, dict):
        images = media.get("images", [])
    elif isinstance(media, list):
        images = media

    if not images:
        return None

    scored = [
        img for img in images
        if isinstance(img, dict) and usable_image(img.get("src")) and isinstance(img.get("score", 0), (int, float))
    ]
    if not scored:
        return None

    scored.sort(key=lambda img: img.get("score", 0), reverse=True)
    best = scored[0]
    if best.get("score", 0) >= _MIN_IMAGE_SCORE:
        return best["src"]
    return scored[0]["src"] if scored else None


def _has_product_signal(product: dict, og: dict) -> bool:
    return has_product_evidence({**og, **product})


def _deduplicate_products(products: list[dict]) -> list[dict]:
    if len(products) <= 1:
        return products

    seen: dict[str, dict] = {}
    for product in products:
        name = (product.get("name") or product.get("og:title") or "").strip().lower()
        price = str(_get_price(product) or "")
        sku = str(product.get("sku") or product.get("productID") or "")
        key = hashlib.md5(f"{name}:{price}:{sku}".encode()).hexdigest()

        if key in seen:
            existing = seen[key]
            if sum(1 for v in product.values() if v) > sum(1 for v in existing.values() if v):
                seen[key] = product
        else:
            seen[key] = product

    return list(seen.values())


def _merge_og(og_from_meta: list[dict], og_from_html: list[dict]) -> dict:
    merged: dict = {}
    if og_from_meta:
        merged.update(og_from_meta[0])
    if og_from_html:
        for k, v in og_from_html[0].items():
            if k not in merged and v:
                merged[k] = v
    return merged


class _CapturedHTML(str):
    def __new__(cls, html, source_url):
        from datetime import datetime, timezone
        obj = super().__new__(cls, html)
        obj.source_url = source_url
        obj.observed_at = datetime.now(timezone.utc)
        return obj
