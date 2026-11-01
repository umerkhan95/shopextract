"""Conservative single-product DOM enrichment shared by static/browser parsers."""
from __future__ import annotations

from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup

from .._capture import capture


def image_url(value):
    if isinstance(value, dict):
        return value.get('url') or value.get('contentUrl') or ''
    return value if isinstance(value, str) else ''


def usable_image(value) -> bool:
    if isinstance(value, list):
        return any(usable_image(item) for item in value)
    value = image_url(value)
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parts = urlsplit(value.strip())
    except ValueError:
        return False
    if parts.scheme and parts.scheme not in ('http', 'https'):
        return False
    path = unquote(parts.path).lower()
    segments = path.split('/')
    return bool(path) and 'placeholder' not in segments and segments[-1] not in (
        'placeholder.jpg', 'placeholder.jpeg', 'placeholder.png', 'placeholder.gif',
        'no_selection', 'no-image.jpg', 'no_image.jpg')


def _bind(product, path, source, capture_path):
    product.setdefault('_field_sources', {})[path] = {
        '_capture': source, 'capture_path': capture_path,
    }


def clean_product_images(product) -> None:
    """Drop placeholders without rewriting original structured-source capture."""
    for key in ('image', 'og:image', 'thumbnailUrl'):
        if key not in product:
            continue
        value = product[key]
        if isinstance(value, list):
            kept = [(i, item) for i, item in enumerate(value) if usable_image(item)]
            if len(kept) == len(value):
                continue
            old_sources = dict(product.get('_field_sources', {}))
            product[key] = [item for _, item in kept]
            for new, (old, _) in enumerate(kept):
                old_path = f'/{key}/{old}'
                prior = old_sources.get(old_path)
                context = prior['_capture'] if prior else product.get('_capture')
                if context:
                    _bind(product, f'/{key}/{new}', context,
                          prior['capture_path'] if prior else old_path)
        elif not usable_image(value):
            product.pop(key)


def enrich_product_html(products: list[dict], html: str, url: str, *, include_brand: bool = True) -> None:
    for product in products:
        clean_product_images(product)
    if len(products) != 1 or not html:
        return
    product = products[0]
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.find('main') or soup
    selected, excerpts = {}, []
    if not usable_image(product.get('image')) and not usable_image(product.get('og:image')):
        images = []
        for node in root.select('a.MagicZoom[href], a.MagicZoomPlus[href], a[data-zoom-id][href], .MagicToolboxSelectorsContainer a[href]'):
            href = node.get('href', '').strip()
            if not href or href.startswith('#'):
                continue
            value = urljoin(url, href)
            if usable_image(value) and value not in images:
                images.append(value)
                excerpts.append(str(node))
        if images:
            selected['image'] = images
    if include_brand and not product.get('brand'):
        node = root.select_one('.brand-name a')
        if node and (value := node.get_text(' ', strip=True)):
            selected['brand'] = value
            excerpts.append(str(node))
    if not product.get('sku'):
        node = root.select_one('span.sku')
        if node and (value := node.get_text(' ', strip=True)):
            selected['sku'] = value
            excerpts.append(str(node))
    if not selected:
        return
    source = capture(dict(selected), url, 'html_product_dom', excerpt='\n'.join(excerpts))['_capture']
    for key, value in selected.items():
        product[key] = value
        _bind(product, '/' + key, source, '/' + key)
        if isinstance(value, list):
            for i in range(len(value)):
                _bind(product, f'/{key}/{i}', source, f'/{key}/{i}')
