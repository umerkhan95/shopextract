"""Strict finite source-document decoding shared by snapshot and crosswalk."""
import json
import math

from .contracts import (
    GoogleTaxonomyDependencyError, GoogleTaxonomyError, GoogleTaxonomyIntegrityError,
)


def _object(items):
    result = {}
    for key, value in items:
        if key in result:
            raise GoogleTaxonomyIntegrityError("Duplicate source-document key")
        result[key] = value
    return result


def decode_source_document(data: bytes):
    """Decode primitive JSON/YAML; callers own bytes, hashes and semantic schema."""
    if not isinstance(data, bytes):
        raise TypeError("Source document must be bytes")
    try:
        text = data.decode("utf-8")
        if text.startswith("\ufeff"):
            raise GoogleTaxonomyIntegrityError("Source-document UTF-8 BOM is unsupported")
        if text.lstrip().startswith(("{", "[")):
            def invalid_constant(_):
                raise GoogleTaxonomyIntegrityError("Nonfinite source-document JSON")
            value = json.loads(text, object_pairs_hook=_object, parse_constant=invalid_constant)
        else:
            try:
                import yaml
            except ImportError:
                raise GoogleTaxonomyDependencyError(
                    "YAML source loading requires the 'taxonomy-build' extra (PyYAML)") from None
            for token in yaml.scan(text):
                if isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken, yaml.tokens.TagToken)):
                    raise GoogleTaxonomyIntegrityError("Source YAML anchors, aliases and tags are unsupported")

            class StrictLoader(yaml.SafeLoader):
                pass

            def mapping(loader, node):
                items = []
                for key_node, value_node in node.value:
                    key = loader.construct_object(key_node, deep=True)
                    if not isinstance(key, str) or key == "<<":
                        raise GoogleTaxonomyIntegrityError("Invalid source YAML key")
                    items.append((key, loader.construct_object(value_node, deep=True)))
                return _object(items)

            StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
            value = yaml.load(text, Loader=StrictLoader)
        stack, nodes = [(value, 0)], 0
        while stack:
            item, depth = stack.pop()
            nodes += 1
            if nodes > 500000 or depth > 64:
                raise GoogleTaxonomyIntegrityError("Source-document structure limit exceeded")
            if isinstance(item, dict):
                for key in item:
                    if not isinstance(key, str):
                        raise GoogleTaxonomyIntegrityError("Source document requires string keys")
                    key.encode("utf-8")
                stack.extend((child, depth + 1) for child in item.values())
            elif isinstance(item, list):
                stack.extend((child, depth + 1) for child in item)
            elif isinstance(item, str):
                item.encode("utf-8")
            elif item is None or type(item) in (bool, int):
                pass
            elif type(item) is float and math.isfinite(item):
                pass
            else:
                raise GoogleTaxonomyIntegrityError("Source document requires finite primitive JSON-like values")
        return value
    except GoogleTaxonomyError:
        raise
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise GoogleTaxonomyIntegrityError("Invalid source-document encoding or structure") from error
    except Exception as error:
        if type(error).__module__.startswith("yaml"):
            raise GoogleTaxonomyIntegrityError("Invalid source-document YAML") from error
        raise
