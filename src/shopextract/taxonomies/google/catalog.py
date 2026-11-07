"""Validated immutable category indexes; no filesystem, network or mapping logic."""
from dataclasses import asdict, dataclass, fields
from types import MappingProxyType
from typing import Mapping

from .contracts import (
    NAMESPACE, MAX_CATALOG_BYTES, GoogleCategory, GoogleCounts, GoogleManifest,
    GoogleTaxonomyIntegrityError, canonical, category_id, digest, fingerprint_text,
    locale_text, provenance_record, source_url_text, version_text,
)


@dataclass(frozen=True)
class GoogleTaxonomy:
    manifest: GoogleManifest
    _categories: Mapping[str, GoogleCategory]
    _paths: Mapping[str, GoogleCategory]

    @property
    def registry_version(self):
        return self.manifest.version + ":" + self.manifest.locale + "@sha256:" + self.manifest.fingerprint

    def category(self, value):
        if not isinstance(value, str):
            raise TypeError("Google category ID must be text")
        return self._categories.get(value)

    def resolve_path(self, value):
        if not isinstance(value, str):
            raise TypeError("Google category path must be text")
        return self._paths.get(value)

    def ancestors(self, value):
        node = self.category(value)
        return tuple(self._categories[key] for key in node.ancestor_ids) if node else ()

    def children(self, value):
        node = self.category(value)
        return tuple(self._categories[key] for key in node.child_ids) if node else ()

    def iter_categories(self):
        return iter(self._categories.values())


def _nodes(pairs):
    paths, ids = {}, {}
    for identifier, path in pairs:
        category_id(identifier)
        if not isinstance(path, str) or len(path.encode("utf-8")) > 8192:
            raise GoogleTaxonomyIntegrityError("Invalid Google category path")
        segments = path.split(" > ")
        if (not path or len(segments) > 64 or
                any(not part or part != part.strip() or ">" in part or
                    any(ord(c) < 32 for c in part) for part in segments)):
            raise GoogleTaxonomyIntegrityError("Malformed Google category path")
        if identifier in ids or path in paths:
            raise GoogleTaxonomyIntegrityError("Duplicate Google category ID/path")
        ids[identifier], paths[path] = path, identifier
    if not ids:
        raise GoogleTaxonomyIntegrityError("Google taxonomy cannot be empty")
    parents, ancestors, children = {}, {}, {key: [] for key in ids}
    for key, path in ids.items():
        segments = path.split(" > ")
        prefixes = [" > ".join(segments[:length]) for length in range(1, len(segments))]
        if any(prefix not in paths for prefix in prefixes):
            raise GoogleTaxonomyIntegrityError("Google category parent path missing")
        lineage = tuple(paths[prefix] for prefix in prefixes)
        ancestors[key] = lineage
        parents[key] = lineage[-1] if lineage else None
        if lineage:
            children[lineage[-1]].append(key)
    return {key: GoogleCategory(key, ids[key].split(" > ")[-1], ids[key], parents[key],
                               tuple(sorted(children[key], key=int)), ancestors[key])
            for key in sorted(ids, key=int)}


def build_catalog(pairs, *, version, locale, source_url, source_sha256, provenance=None):
    version_text(version)
    locale_text(locale)
    source_url_text(source_url)
    fingerprint_text(source_sha256)
    source = provenance_record(provenance, source_sha256, source_url)
    nodes = _nodes(pairs)
    counts = GoogleCounts(len(nodes), sum(n.parent_id is None for n in nodes.values()),
                          sum(not n.child_ids for n in nodes.values()),
                          sum(n.parent_id is not None for n in nodes.values()))
    payload = dict(schema_version=1, namespace=NAMESPACE, version=version, locale=locale,
                   source_url=source_url, source_sha256=source_sha256,
                   source_kind=source.source_kind if source else "google_txt",
                   source_provenance=asdict(source) if source else None,
                   categories=[asdict(node) for node in nodes.values()])
    encoded = canonical(payload)
    if len(encoded) > MAX_CATALOG_BYTES:
        raise GoogleTaxonomyIntegrityError("Generated Google catalog exceeds byte limit")
    identity = digest(encoded)
    manifest = GoogleManifest(1, NAMESPACE, version, locale, source_url, source_sha256,
                              identity, counts, payload["source_kind"], source, identity)
    return GoogleTaxonomy(manifest, MappingProxyType(nodes),
                          MappingProxyType({n.full_name: n for n in nodes.values()}))


def catalog_payload(catalog):
    manifest = catalog.manifest
    return dict(schema_version=1, namespace=NAMESPACE, version=manifest.version,
                locale=manifest.locale, source_url=manifest.source_url,
                source_sha256=manifest.source_sha256, source_kind=manifest.source_kind,
                source_provenance=asdict(manifest.source_provenance) if manifest.source_provenance else None,
                categories=[asdict(node) for node in catalog.iter_categories()])


def catalog_from_payload(payload):
    keys = {"schema_version", "namespace", "version", "locale", "source_url", "source_sha256",
            "source_kind", "source_provenance", "categories"}
    if not isinstance(payload, dict) or set(payload) != keys:
        raise GoogleTaxonomyIntegrityError("Invalid generated Google catalog fields")
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1 or payload["namespace"] != NAMESPACE:
        raise GoogleTaxonomyIntegrityError("Unsupported Google catalog schema/namespace")
    records = payload["categories"]
    required = {field.name for field in fields(GoogleCategory)}
    if not isinstance(records, list) or any(not isinstance(row, dict) or set(row) != required for row in records):
        raise GoogleTaxonomyIntegrityError("Invalid Google category record fields")
    catalog = build_catalog(((row["id"], row["full_name"]) for row in records),
        version=payload["version"], locale=payload["locale"], source_url=payload["source_url"],
        source_sha256=payload["source_sha256"], provenance=payload["source_provenance"])
    # Rebuilding relationships checks retained derived data, order and semantic fields.
    if canonical(catalog_payload(catalog)) != canonical(payload):
        raise GoogleTaxonomyIntegrityError("Google catalog derived data does not match source paths")
    return catalog
