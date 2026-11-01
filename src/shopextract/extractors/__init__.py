"""Product data extractors for various e-commerce platforms."""
from importlib import import_module as _import_module

_EXPORTS = {'ShopifyExtractor': ('.shopify', 'ShopifyExtractor'),
 'WooCommerceExtractor': ('.woocommerce', 'WooCommerceExtractor'),
 'MagentoExtractor': ('.magento', 'MagentoExtractor'),
 'MagentoGraphQLExtractor': ('.magento_graphql', 'MagentoGraphQLExtractor'),
 'ShopwareExtractor': ('.shopware', 'ShopwareExtractor'),
 'BigCommerceExtractor': ('.bigcommerce', 'BigCommerceExtractor'),
 'UnifiedCrawlExtractor': ('.unified', 'UnifiedCrawlExtractor'),
 'CSSExtractor': ('.css', 'CSSExtractor'),
 'GoogleFeedExtractor': ('.feed', 'GoogleFeedExtractor'),
 'LLMExtractor': ('.llm', 'LLMExtractor')}

__all__ = ['ShopifyExtractor',
 'WooCommerceExtractor',
 'MagentoExtractor',
 'MagentoGraphQLExtractor',
 'ShopwareExtractor',
 'BigCommerceExtractor',
 'UnifiedCrawlExtractor',
 'CSSExtractor',
 'GoogleFeedExtractor',
 'LLMExtractor']


def __getattr__(name):
    try:
        module, attribute = _EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    value = getattr(_import_module(module, __name__), attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS))
