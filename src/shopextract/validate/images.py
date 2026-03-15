"""Image URL validation via HEAD requests.

Checks each product's image_url for broken links and non-image content types.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from .._models import ImageIssue

logger = logging.getLogger(__name__)

_VALID_IMAGE_TYPES = frozenset({
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "image/svg+xml", "image/avif", "image/tiff", "image/bmp",
})

_CONCURRENCY = 20
_TIMEOUT = 10.0


async def check_images(
    products: list[dict],
    *,
    timeout: float = _TIMEOUT,
    concurrency: int = _CONCURRENCY,
) -> list[ImageIssue]:
    """Check image URLs for broken links and wrong content types.

    Args:
        products: List of product dicts with 'image_url' field.
        timeout: HTTP timeout per request in seconds.
        concurrency: Max concurrent HEAD requests.

    Returns:
        List of ImageIssue for broken or invalid images.
    """
    issues: list[ImageIssue] = []
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True,
    ) as client:
        tasks = [
            _check_single(client, semaphore, idx, product, issues)
            for idx, product in enumerate(products)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    return issues


async def _check_single(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    idx: int,
    product: dict,
    issues: list[ImageIssue],
) -> None:
    """Check a single product's image URL."""
    image_url = (product.get("image_url") or "").strip()
    title = str(product.get("title", "")).strip()

    if not image_url:
        issues.append(ImageIssue(
            product_index=idx, product_title=title,
            image_url="", error="No image URL provided",
        ))
        return

    async with semaphore:
        try:
            resp = await client.head(image_url)
            content_type = (resp.headers.get("content-type") or "").split(";")[0].strip().lower()

            if resp.status_code >= 400:
                issues.append(ImageIssue(
                    product_index=idx, product_title=title,
                    image_url=image_url, status_code=resp.status_code,
                    content_type=content_type,
                    error=f"HTTP {resp.status_code}",
                ))
            elif content_type and content_type not in _VALID_IMAGE_TYPES:
                issues.append(ImageIssue(
                    product_index=idx, product_title=title,
                    image_url=image_url, status_code=resp.status_code,
                    content_type=content_type,
                    error=f"Non-image content type: {content_type}",
                ))
        except httpx.TimeoutException:
            issues.append(ImageIssue(
                product_index=idx, product_title=title,
                image_url=image_url, error="Request timed out",
            ))
        except httpx.HTTPError as exc:
            issues.append(ImageIssue(
                product_index=idx, product_title=title,
                image_url=image_url, error=f"HTTP error: {exc}",
            ))
