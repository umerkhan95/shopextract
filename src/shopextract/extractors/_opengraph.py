"""OpenGraph meta tags extractor (static methods only)."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class OpenGraphExtractor:
    """Extract OpenGraph meta tags from HTML."""

    @staticmethod
    def extract_from_html(html: str, url: str) -> list[dict]:
        """Extract OpenGraph tags from raw HTML content.

        Args:
            html: Raw HTML content.
            url: URL for logging purposes.

        Returns:
            List with single dict of extracted OG data. Empty list on error.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            og_tags = soup.find_all(
                "meta",
                property=lambda x: x and (x.startswith("og:") or x.startswith("product:")),
            )

            if not og_tags:
                return []

            og_data = {}
            for tag in og_tags:
                property_name = tag.get("property", "")
                content = tag.get("content", "")
                if property_name and content:
                    og_data[property_name] = content

            return [og_data] if og_data else []

        except Exception as e:
            logger.exception("OpenGraph extraction failed for %s: %s", url, e)
            return []

    @staticmethod
    def from_metadata(metadata: dict) -> list[dict]:
        """Build OG data from crawl4ai CrawlResult.metadata.

        Args:
            metadata: Dict from CrawlResult.metadata.

        Returns:
            List with single dict of OG data, or empty list.
        """
        if not metadata:
            return []

        og_data = {
            k: v for k, v in metadata.items()
            if isinstance(k, str) and k.startswith("og:") and v
        }
        return [og_data] if og_data else []
