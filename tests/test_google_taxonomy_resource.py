"""Controlled Google source/resource mechanisms; no network or dataset dependency."""
from dataclasses import asdict, FrozenInstanceError
from hashlib import sha256
import json

import pytest

from shopextract.taxonomies.google.contracts import (
    GoogleTaxonomyIntegrityError, GoogleTaxonomyLookupError,
    GoogleTaxonomyPublicationError, canonical,
)
from shopextract.taxonomies.google.loader import load_google_taxonomy
from shopextract.taxonomies.google.prepare import prepare_google_taxonomy
from shopextract.taxonomies.google.resource import read_resource
from shopextract.taxonomies.google.source import parse_google_taxonomy


TEXT = "# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Root\n2 - Root > Leaf\n"


def prepared(tmp_path, text=TEXT):
    source = tmp_path / "source.txt"
    source.write_text(text)
    root = tmp_path / "catalogs"
    directory = prepare_google_taxonomy(source, root)
    return root, directory


@pytest.mark.parametrize("text", [
    "", "\ufeff" + TEXT, TEXT.replace("2021-09-21", "2021-02-30"),
    TEXT + "2 - Other\n", TEXT + "3 - Root > Leaf\n",
    TEXT + "3 - Missing > Child\n", TEXT + "03 - Other\n",
    TEXT + "٣ - Other\n", TEXT + "3 - Root >  Double\n",
    TEXT + "3 - Root>Bad\n", TEXT + "3 - Bad\tName\n",
    TEXT + "# not a category\n", TEXT + "3 - " + "X" * 8193 + "\n",
    TEXT + " " * (2 * 1024 * 1024),
])
def test_malformed_source_cannot_build_index(text):
    with pytest.raises(GoogleTaxonomyIntegrityError):
        parse_google_taxonomy(text)


def test_catalog_records_and_indexes_are_immutable():
    taxonomy = parse_google_taxonomy(TEXT)
    with pytest.raises(FrozenInstanceError):
        taxonomy.category("2").name = "changed"
    with pytest.raises(TypeError):
        taxonomy._categories["3"] = taxonomy.category("2")
    with pytest.raises(TypeError):
        taxonomy.category(2)
    assert taxonomy.category("999") is None and taxonomy.ancestors("999") == ()
    assert taxonomy.resolve_path("root > leaf") is None


def test_source_provenance_binds_original_and_derived_bytes():
    provenance = dict(source_kind="shopify_google_snapshot", source_url="https://raw.example.test/source.yml",
                      source_commit="a" * 40, source_sha256="b" * 64,
                      derived_sha256=sha256(TEXT.encode()).hexdigest())
    taxonomy = parse_google_taxonomy(TEXT, source_url=provenance["source_url"], provenance=provenance)
    assert taxonomy.manifest.source_kind == "shopify_google_snapshot"
    assert taxonomy.manifest.source_provenance.source_sha256 == "b" * 64
    assert taxonomy.manifest.source_sha256 != "b" * 64
    assert taxonomy.manifest.fingerprint != parse_google_taxonomy(TEXT).manifest.fingerprint
    for patch in ({"derived_sha256": "0" * 64}, {"source_commit": "bad"},
                  {"extra": "unknown"}, {"source_kind": "unspecified"}):
        with pytest.raises(GoogleTaxonomyIntegrityError):
            parse_google_taxonomy(TEXT, provenance={**provenance, **patch})


def test_prepare_idempotence_and_explicit_resource_identity(tmp_path):
    root, directory = prepared(tmp_path)
    source = tmp_path / "source.txt"
    assert prepare_google_taxonomy(source, root) == directory
    catalog = load_google_taxonomy(catalog_root=root)
    assert catalog.manifest.fingerprint == directory.name
    assert read_resource(directory).manifest == catalog.manifest
    assert (directory / "catalog.json").read_bytes() == canonical(json.loads((directory / "catalog.json").read_text()))


def test_same_release_different_resource_requires_fingerprint(tmp_path):
    root, original = prepared(tmp_path)
    source = tmp_path / "source.txt"
    source.write_text(TEXT + "3 - Other\n")
    second = prepare_google_taxonomy(source, root)
    assert second != original
    with pytest.raises(GoogleTaxonomyLookupError, match="ambiguous"):
        load_google_taxonomy(catalog_root=root)
    assert load_google_taxonomy(catalog_root=root, fingerprint=original.name).category("3") is None
    assert load_google_taxonomy(catalog_root=root, fingerprint=second.name).category("3").name == "Other"


def test_failed_publication_preserves_previous_and_cleans_stage(tmp_path, monkeypatch):
    root, original = prepared(tmp_path)
    source = tmp_path / "source.txt"
    source.write_text(TEXT + "3 - Other\n")
    import shopextract.taxonomies.google.publish as publisher

    def fail(*args):
        raise OSError("controlled rename fault")

    monkeypatch.setattr(publisher.os, "rename", fail)
    with pytest.raises(GoogleTaxonomyPublicationError):
        prepare_google_taxonomy(source, root)
    assert load_google_taxonomy(catalog_root=root).manifest.fingerprint == original.name
    assert not list(original.parent.glob(".stage-*"))


def test_resource_integrity_is_rechecked_after_prior_load(tmp_path):
    root, directory = prepared(tmp_path)
    assert load_google_taxonomy(catalog_root=root).category("2") is not None
    path = directory / "catalog.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(GoogleTaxonomyIntegrityError):
        load_google_taxonomy(catalog_root=root)


def test_forged_consistent_hash_cannot_bless_wrong_graph(tmp_path):
    _, directory = prepared(tmp_path)
    path = directory / "catalog.json"
    payload = json.loads(path.read_text())
    payload["categories"][1]["parent_id"] = None
    data = canonical(payload)
    path.write_bytes(data)
    manifest = json.loads((directory / "manifest.json").read_text())
    manifest["fingerprint"] = manifest["catalog_sha256"] = sha256(data).hexdigest()
    (directory / "manifest.json").write_bytes(canonical(manifest))
    with pytest.raises(GoogleTaxonomyIntegrityError, match="derived"):
        read_resource(directory)


@pytest.mark.parametrize("corruption", ["duplicate_key", "extra_field", "bool_count", "too_large"])
def test_strict_manifest_rejects_ambiguous_resource(tmp_path, corruption):
    _, directory = prepared(tmp_path)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    if corruption == "duplicate_key":
        path.write_text('{"schema_version":1,' + path.read_text()[1:])
    elif corruption == "extra_field":
        path.write_bytes(canonical({**manifest, "extra": True}))
    elif corruption == "bool_count":
        manifest["counts"]["roots"] = True
        path.write_bytes(canonical(manifest))
    else:
        path.write_bytes(b" " * (65536 + 1))
    with pytest.raises(GoogleTaxonomyIntegrityError):
        read_resource(directory)


@pytest.mark.parametrize("kwargs", [
    {"version": "../2021-09-21"}, {"locale": "../en-US"}, {"fingerprint": "../bad"},
])
def test_identity_path_traversal_is_rejected(tmp_path, kwargs):
    with pytest.raises(ValueError):
        load_google_taxonomy(catalog_root=tmp_path, **kwargs)


def test_resource_symlink_is_rejected(tmp_path):
    root, directory = prepared(tmp_path)
    path = directory / "catalog.json"
    saved = tmp_path / "copied.json"
    path.rename(saved)
    path.symlink_to(saved)
    with pytest.raises(GoogleTaxonomyIntegrityError):
        load_google_taxonomy(catalog_root=root)


def test_escaped_surrogate_resource_is_typed_integrity_failure(tmp_path):
    _, directory = prepared(tmp_path)
    path = directory / "catalog.json"
    payload = json.loads(path.read_text())
    payload["categories"][1]["full_name"] = "Root > \ud800"
    path.write_text(json.dumps(payload, ensure_ascii=True))
    with pytest.raises(GoogleTaxonomyIntegrityError):
        read_resource(directory)
