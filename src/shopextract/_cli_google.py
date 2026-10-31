"""Thin, bounded command adapters over the Google taxonomy family."""
from __future__ import annotations

import base64
from dataclasses import asdict
from functools import wraps
import json

import click

from ._cli_core import CliFailure, CoreCommand
from ._cli_data import raw_records, read_json_file
from ._cli_categories import category_output


def native_errors(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        from .taxonomies.google.contracts import (GoogleTaxonomyLookupError,
            GoogleTaxonomyPublicationError, GoogleTaxonomyDependencyError)
        try:
            return function(*args, **kwargs)
        except CliFailure:
            raise
        except (GoogleTaxonomyLookupError, GoogleTaxonomyPublicationError, OSError):
            raise CliFailure('E_OPERATION', 'Google resource unavailable or publication failed; provision the source and select its exact identity.') from None
        except GoogleTaxonomyDependencyError:
            raise CliFailure('E_DEPENDENCY', 'Source YAML preparation requires the taxonomy-build extra; ordinary catalog lookup does not.') from None
        except ImportError:
            raise CliFailure('E_DEPENDENCY', 'Source YAML preparation requires the taxonomy-build extra; ordinary catalog lookup does not.') from None
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError, RecursionError):
            raise CliFailure('E_USAGE', 'Invalid Google taxonomy source, identity, mapping, cursor or input; consult taxonomy google --help.') from None
    return wrapped


def catalog(settings):
    from .taxonomies.google import load_google_taxonomy
    return load_google_taxonomy(**settings)


def cursor_record(value):
    def pairs(items):
        record = {}
        for key, item in items:
            if key in record:
                raise ValueError('Duplicate cursor field')
            record[key] = item
        return record
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise ValueError('Invalid cursor')
    return json.loads(base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True), object_pairs_hook=pairs)


def page(taxonomy, token, limit):
    identity = dict(fingerprint=taxonomy.manifest.fingerprint,
                    version=taxonomy.manifest.version, locale=taxonomy.manifest.locale, limit=limit)
    offset = 0
    if token is not None:
        value = cursor_record(token)
        if not isinstance(value, dict) or set(value) != {*identity, 'offset'}:
            raise ValueError('Malformed cursor')
        if type(value['limit']) is not int:
            raise ValueError('Malformed cursor page size')
        if any(value[key] != expected for key, expected in identity.items()):
            raise ValueError('Cursor belongs to another catalog or page size')
        offset = value['offset']
        if type(offset) is not int or offset < 0:
            raise ValueError('Invalid cursor offset')
    nodes = tuple(taxonomy.iter_categories())
    if offset > len(nodes):
        raise ValueError('Cursor offset out of range')
    end = min(len(nodes), offset + limit)
    following = None
    if end < len(nodes):
        raw = json.dumps(dict(identity, offset=end), sort_keys=True, separators=(',', ':')).encode()
        following = base64.urlsafe_b64encode(raw).decode().rstrip('=')
    return dict(categories=[asdict(node) for node in nodes[offset:end]], count=len(nodes),
                next_cursor=following, complete=following is None, fingerprint=taxonomy.manifest.fingerprint)


def crosswalk_source(source, digest, taxonomy, shopify_root):
    from .taxonomies.google import load_shopify_google_crosswalk
    from .taxonomies.shopify import load_shopify_taxonomy
    source_catalog = load_shopify_taxonomy(catalog_root=shopify_root)
    return source_catalog, load_shopify_google_crosswalk(
        source, expected_sha256=digest, source_catalog=source_catalog, target_catalog=taxonomy)


def register(main):
    @main.group('taxonomy', cls=click.Group)
    def taxonomy_group():
        """Explicit offline taxonomy resource and mapping operations."""

    @taxonomy_group.group('google', cls=click.Group)
    @click.option('--catalog-root', type=click.Path(file_okay=False))
    @click.option('--version', default='2021-09-21', show_default=True)
    @click.option('--locale', default='en-US', show_default=True)
    @click.option('--fingerprint')
    @click.pass_context
    def google(ctx, **settings):
        """Complete Google catalog; provision operator-owned source with prepare."""
        ctx.obj = settings
    google.command_class = CoreCommand

    @google.command('info')
    @click.pass_obj
    @native_errors
    def info(settings):
        category_output({'manifest': asdict(catalog(settings).manifest), 'resource_route': 'operator-provisioned'})

    @google.command('lookup')
    @click.argument('category_id')
    @click.pass_obj
    @native_errors
    def lookup(settings, category_id):
        node = catalog(settings).category(category_id)
        if node is None:
            raise CliFailure('E_USAGE', 'Unknown Google category ID in the selected catalog.')
        category_output({'category': asdict(node)})

    @google.command('resolve-path')
    @click.argument('path')
    @click.pass_obj
    @native_errors
    def resolve_path(settings, path):
        node = catalog(settings).resolve_path(path)
        if node is None:
            raise CliFailure('E_USAGE', 'Unknown exact Google path in the selected catalog/locale.')
        category_output({'category': asdict(node)})

    @google.command('list')
    @click.option('--cursor')
    @click.option('--limit', type=click.IntRange(1, 100), default=100, show_default=True)
    @click.pass_obj
    @native_errors
    def list_categories(settings, cursor, limit):
        category_output(page(catalog(settings), cursor, limit))

    @google.command('lookup-batch')
    @click.argument('file', type=click.Path(dir_okay=False))
    @click.pass_obj
    @native_errors
    def lookup_batch(settings, file):
        values = read_json_file(file)
        if not isinstance(values, list) or not 1 <= len(values) <= 1000 or any(not isinstance(v, str) for v in values):
            raise ValueError('Expected1..1000text IDs')
        selected = catalog(settings)
        nodes = [selected.category(value) for value in values]
        category_output({'categories': [asdict(node) if node else None for node in nodes],
                         'fingerprint': selected.manifest.fingerprint})

    @google.command('validate')
    @click.argument('file', type=click.Path(dir_okay=False))
    @click.pass_obj
    @native_errors
    def validate(settings, file):
        from .taxonomies.google import parse_google_taxonomy
        from .taxonomies.google.contracts import MAX_SOURCE_BYTES
        with open(file, 'rb') as stream:
            data = stream.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError('Source exceeds limit')
        selected = parse_google_taxonomy(data.decode('utf-8'), locale=settings['locale'])
        category_output({'manifest': asdict(selected.manifest)})

    @google.command('prepare')
    @click.option('--source', required=True, type=click.Path(dir_okay=False))
    @click.option('--expected-sha256')
    @click.option('--source-url', default='')
    @click.option('--provenance', type=click.Path(dir_okay=False))
    @click.pass_obj
    @native_errors
    def prepare(settings, source, expected_sha256, source_url, provenance):
        from .taxonomies.google import prepare_google_taxonomy, parse_google_taxonomy
        from .taxonomies.google.contracts import MAX_SOURCE_BYTES
        from .taxonomies.google.resource import read_resource
        if not settings['catalog_root']:
            raise ValueError('Explicit catalog root required')
        origin = read_json_file(provenance) if provenance else None
        with open(source, 'rb') as stream:
            data = stream.read(MAX_SOURCE_BYTES + 1)
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError('Source exceeds limit')
        checked = parse_google_taxonomy(data.decode('utf-8'), locale=settings['locale'],
            expected_sha256=expected_sha256, source_url=source_url, provenance=origin)
        if checked.manifest.version != settings['version'] or (
                settings['fingerprint'] and checked.manifest.fingerprint != settings['fingerprint']):
            raise ValueError('Source differs from explicitly selected identity')
        directory = prepare_google_taxonomy(source, settings['catalog_root'], locale=settings['locale'],
            expected_sha256=checked.manifest.source_sha256, source_url=source_url, provenance=origin)
        selected = read_resource(directory, expected={'version': settings['version'], 'locale': settings['locale']})
        category_output({'directory': str(directory), 'manifest': asdict(selected.manifest)})

    @google.command('normalize')
    @click.argument('file', type=click.Path(dir_okay=False))
    @click.option('--shop-url', required=True)
    @click.option('--platform', type=click.Choice(['generic', 'shopify', 'woocommerce', 'magento', 'shopware', 'bigcommerce']), default='generic')
    @click.option('--mapping', type=click.Path(dir_okay=False))
    @click.option('--allow-unknown-source-version', is_flag=True)
    @click.option('--crosswalk', type=click.Path(dir_okay=False))
    @click.option('--crosswalk-sha256')
    @click.option('--shopify-catalog-root', type=click.Path(file_okay=False))
    @click.pass_obj
    @native_errors
    def normalize(settings, file, shop_url, platform, mapping, allow_unknown_source_version,
                  crosswalk, crosswalk_sha256, shopify_catalog_root):
        from ._models import Platform
        from ._portable import product_to_record
        from .categories._codec import typed
        from .categories.contracts import MappingRule
        from .categories.portable import categorized_product_to_record
        from .taxonomies.google import normalize_with_google_taxonomy, effective_google_category
        selected = catalog(settings)
        rules = ()
        if mapping:
            raw = read_json_file(mapping)
            if not isinstance(raw, list) or len(raw) > 1000:
                raise ValueError('Mapping rules exceed bounds')
            rules = tuple(typed(MappingRule, item) for item in raw)
        index = None
        if bool(crosswalk) != bool(crosswalk_sha256):
            raise ValueError('Crosswalk and its digest must be selected together')
        if crosswalk:
            _, index = crosswalk_source(crosswalk, crosswalk_sha256, selected, shopify_catalog_root)
        results = []
        for raw in raw_records(read_json_file(file)):
            value = normalize_with_google_taxonomy(raw, platform=Platform(platform), shop_url=shop_url,
                taxonomy=selected, mappings=rules, crosswalk=index,
                allow_unknown_source_version=allow_unknown_source_version)
            if value is None:
                raise ValueError('A product could not normalize')
            results.append(value)
        category_output({'products': [product_to_record(v.product) for v in results],
            'categorized_products': [categorized_product_to_record(v) for v in results],
            'classifications': [asdict(effective_google_category(v, taxonomy=selected)) for v in results]})

    @google.command('prepare-snapshot')
    @click.option('--source', required=True, type=click.Path(dir_okay=False))
    @click.option('--expected-sha256', required=True)
    @click.option('--source-commit', required=True)
    @click.option('--source-url', required=True)
    @click.pass_obj
    @native_errors
    def prepare_snapshot(settings, source, expected_sha256, source_commit, source_url):
        from .taxonomies.google import prepare_google_snapshot
        from .taxonomies.google.resource import read_resource
        if not settings['catalog_root'] or settings['fingerprint']:
            raise ValueError('Snapshot preparation needs a root, not a preselected fingerprint')
        directory = prepare_google_snapshot(source, settings['catalog_root'],
            source_commit=source_commit, source_url=source_url, expected_sha256=expected_sha256,
            version=settings['version'], locale=settings['locale'])
        category_output({'directory': str(directory), 'manifest': asdict(read_resource(directory).manifest)})

    @google.group('crosswalk', cls=click.Group)
    def crosswalk_group():
        """Inspect a hash-pinned official directional Shopify source crosswalk."""
    crosswalk_group.command_class = CoreCommand

    @crosswalk_group.command('audit')
    @click.option('--source', required=True, type=click.Path(dir_okay=False))
    @click.option('--expected-sha256', required=True)
    @click.option('--shopify-catalog-root', type=click.Path(file_okay=False))
    @click.option('--offset', type=click.IntRange(0), default=0)
    @click.option('--limit', type=click.IntRange(1, 100), default=100)
    @click.pass_obj
    @native_errors
    def audit(settings, source, expected_sha256, shopify_catalog_root, offset, limit):
        from collections import Counter
        from .taxonomies.google import audit_source_categories
        selected = catalog(settings)
        source_catalog, index = crosswalk_source(source, expected_sha256, selected, shopify_catalog_root)
        values = tuple(audit_source_categories(index, source_catalog))
        category_output({'source_categories': len(values), 'statuses': dict(Counter(v.status for v in values)),
            'dispositions': [asdict(v) for v in values[offset:offset + limit]],
            'next_offset': offset + limit if offset + limit < len(values) else None,
            'crosswalk_sha256': index.source_sha256})

    @google.command('verify-live')
    @click.option('--profile', required=True, type=click.Path(dir_okay=False))
    @click.option('--output-dir', required=True, type=click.Path(file_okay=False))
    @click.option('--site', 'site_id')
    @click.option('--project-root', type=click.Path(file_okay=False), help='Profile path base; defaults to invocation directory.')
    @click.option('--live', is_flag=True, help='Perform bounded fetches; policy-denied sites are skipped.')
    @native_errors
    def verify_live(profile, output_dir, site_id, project_root, live):
        from .taxonomies.google.live import verify_google_live
        report = verify_google_live(profile, output_dir, site_id=site_id, live=live, project_root=project_root)
        category_output(report, partial=report['status'] in ('blocked','needs_review'), failure=report['status']=='fail')
