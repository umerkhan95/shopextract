"""Product data extractors for various e-commerce platforms."""

from .shopify import ShopifyExtractor
from .woocommerce import WooCommerceExtractor
from .magento import MagentoExtractor
from .magento_graphql import MagentoGraphQLExtractor
from .shopware import ShopwareExtractor
from .bigcommerce import BigCommerceExtractor
from .unified import UnifiedCrawlExtractor
from .css import CSSExtractor
from .feed import GoogleFeedExtractor
from .llm import LLMExtractor

__all__ = [
    "ShopifyExtractor",
    "WooCommerceExtractor",
    "MagentoExtractor",
    "MagentoGraphQLExtractor",
    "ShopwareExtractor",
    "BigCommerceExtractor",
    "UnifiedCrawlExtractor",
    "CSSExtractor",
    "GoogleFeedExtractor",
    "LLMExtractor",
]
