"""Strict operator profile, distinct from the root CLI's three-key config."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import ipaddress

from ..._cli_core import CliFailure, read_cli_config
from ..._cli_data import read_json_file
from ..._models import Platform
from ...categories._codec import typed
from ...categories.contracts import MappingRule, CategoryScope
from ...tools.security import normalized, public


def in_scope(url, shop):
    try:
        target, origin, host, _ = normalized(url)
        _, source, _, _ = normalized(shop)
        if origin != source or urlsplit(target).scheme != 'https' or host == 'localhost' or host.endswith('.localhost'):
            return False
        try:
            ipaddress.ip_address(host)
            if not public(host):
                return False
        except ValueError:
            pass
        path = urlsplit(target).path
        for _ in range(3):
            decoded = unquote(path)
            if decoded == path:
                break
            path = decoded
        if unquote(path) != path:
            return False
        if '\\' in path or any(part in ('.', '..') for part in path.split('/')):
            return False
        base = urlsplit(shop).path.rstrip('/')
        return not base or path == base or path.startswith(base + '/')
    except Exception:
        return False


def load_live_profile(path, *, project_root=None):
    root = Path(project_root or Path.cwd()).resolve()
    try:
        value = read_json_file(str(path))
        required = {'schema_version', 'catalog_root', 'catalog_fingerprint', 'cli_config', 'sites', 'limits'}
        if not isinstance(value, dict) or set(value) != required or type(value['schema_version']) is not int or value['schema_version'] not in (1, 2):
            raise ValueError('Invalid profile fields/version')
        if any(not isinstance(value[k], str) or not value[k] for k in ('catalog_root', 'catalog_fingerprint', 'cli_config')):
            raise ValueError('Invalid profile paths')
        sites = value['sites']
        if not isinstance(sites, list) or not 1 <= len(sites) <= 2:
            raise ValueError('Expected1..2sites')
        ids = set()
        for site in sites:
            required_site = {'id', 'url', 'platform', 'source_kind', 'shop_url', 'mapping_rules'}
            if not isinstance(site, dict) or set(site) != required_site | ({'css_schema'} if site.get('source_kind') == 'html_css' else set()):
                raise ValueError('Invalid site fields')
            if not isinstance(site['id'], str) or not site['id'] or len(site['id']) > 64 or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in site['id']) or site['id'] in ids:
                raise ValueError('Invalid site ID')
            ids.add(site['id'])
            automatic = value['schema_version'] == 2 and site['platform'] == 'auto'
            platform = Platform.GENERIC if automatic else Platform(site['platform'])
            kinds = ('production',) if value['schema_version'] == 2 else ('html', 'html_css', 'shopify_products')
            if site['source_kind'] not in kinds or not in_scope(site['url'], site['shop_url']):
                raise ValueError('Invalid source origin/scope')
            if site['source_kind'] == 'shopify_products' and platform != Platform.SHOPIFY:
                raise ValueError('Shopify source requires Shopify platform')
            rules = site['mapping_rules']
            if not isinstance(rules, list) or len(rules) > 1000:
                raise ValueError('Invalid mapping rules')
            for rule in rules:
                parsed = typed(MappingRule, rule)
                if automatic and parsed.selector.scope is not None:
                    raise ValueError('Auto platform requires unscoped rules or an explicit platform')
                if parsed.selector.scope is not None and parsed.selector.scope != CategoryScope(platform, site['shop_url']):
                    raise ValueError('Mapping scope differs from site')
            if site['source_kind'] == 'html_css':
                schema = site['css_schema']
                if not isinstance(schema, dict) or set(schema) != {'baseSelector','fields'} or not isinstance(schema['baseSelector'],str) or not 1 <= len(schema['baseSelector']) <= 256 or not isinstance(schema['fields'],list) or not 1 <= len(schema['fields']) <= 20:
                    raise ValueError('Invalid CSS schema')
                for field in schema['fields']:
                    if not isinstance(field,dict) or set(field) != {'name','selector','type'} or field['name'] not in {'title','price','product_type'} or field['type'] != 'text' or not isinstance(field['selector'],str) or not 1 <= len(field['selector']) <= 256:
                        raise ValueError('Only declared text selectors are supported')
                if len({field['name'] for field in schema['fields']})!=len(schema['fields']):
                    raise ValueError('Duplicate CSS field names')
        limits = value['limits']
        maxima = (dict(invocations=2, products=4, seconds=120, output_bytes=1048576)
                  if value['schema_version'] == 2 else
                  dict(requests=8, products=4, seconds=120, response_bytes=1048576))
        if not isinstance(limits,dict) or set(limits) != set(maxima) or any(type(limits[k]) is not int or not 1 <= limits[k] <= maximum for k,maximum in maxima.items()):
            raise ValueError('Invalid live limits')
        for name in ('catalog_root', 'cli_config'):
            selected = Path(value[name]); selected = selected if selected.is_absolute() else root / selected
            value[name] = str(selected.resolve())
        read_cli_config(Path(value['cli_config']))
        return value
    except CliFailure as error:
        raise ValueError('Invalid profile or root CLI configuration') from error
