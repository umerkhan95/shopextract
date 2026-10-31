"""Explicit operator snapshot preparation uses real source/resource paths."""
from hashlib import sha256
import importlib
import json

import pytest

from shopextract.taxonomies.google.contracts import GoogleTaxonomyIntegrityError
from shopextract.taxonomies.google.loader import load_google_taxonomy


SOURCE = "---\n- id: 1\n  full_name: Root\n- id: 2\n  full_name: Root > Leaf\n"
COMMIT = "a" * 40
URL = "https://raw.example.test/" + COMMIT + "/full_names.yml"
DERIVED = "# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Root\n2 - Root > Leaf\n"


def operation():
    try:
        module = importlib.import_module("shopextract.taxonomies.google.source_snapshot")
    except ModuleNotFoundError as error:
        if error.name != "shopextract.taxonomies.google.source_snapshot":
            raise
        pytest.fail("Explicit Google snapshot preparation is not implemented", pytrace=False)
    return module.prepare_google_snapshot


def prepare(source, root, **kwargs):
    return operation()(source, root, source_commit=COMMIT, source_url=URL,
                       expected_sha256=sha256(source.read_bytes()).hexdigest(), **kwargs)


def test_snapshot_preparation_reuses_exact_resource_identity(tmp_path):
    path = tmp_path / "full_names.yml"
    path.write_text(SOURCE)
    root = tmp_path / "catalogs"
    directory = prepare(path, root)
    taxonomy = load_google_taxonomy(catalog_root=root)
    assert taxonomy.manifest.counts.categories == 2
    assert taxonomy.manifest.counts.roots == 1
    assert taxonomy.manifest.counts.leaves == 1
    assert taxonomy.manifest.source_kind == "shopify_google_snapshot"
    provenance = taxonomy.manifest.source_provenance
    assert provenance.source_commit == COMMIT and provenance.source_url == URL
    assert provenance.source_sha256 == sha256(SOURCE.encode()).hexdigest()
    assert provenance.derived_sha256 == taxonomy.manifest.source_sha256 == sha256(DERIVED.encode()).hexdigest()
    assert directory == prepare(path, root)
    assert taxonomy.category("2").parent_id == "1"


def test_snapshot_wrong_hash_precedes_source_decoding(tmp_path):
    source = tmp_path / "bad.yml"
    source.write_text("not: [valid: yaml")
    with pytest.raises(GoogleTaxonomyIntegrityError, match="SHA256"):
        operation()(source, tmp_path / "out", source_commit=COMMIT, source_url=URL,
                    expected_sha256="0" * 64)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("bad", [
    "- id: 1\n  id: 2\n  full_name: Root\n",
    "- &entry {id: 1, full_name: Root}\n- *entry\n",
    "- !!python/object:evil {}\n",
    "- {id: true, full_name: Root}\n",
    "- {id: '01', full_name: Root}\n",
    "- {id: 1, full_name: Root, extra: unknown}\n",
    '- {id: 1, full_name: "Root\\n2 - Injected"}\n',
    "[]\n",
])
def test_invalid_snapshot_never_publishes(bad, tmp_path):
    source = tmp_path / "bad.yml"
    source.write_text(bad)
    with pytest.raises(GoogleTaxonomyIntegrityError):
        prepare(source, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_invalid_next_snapshot_preserves_prior_resource(tmp_path):
    source = tmp_path / "full_names.yml"
    source.write_text(SOURCE)
    root = tmp_path / "out"
    directory = prepare(source, root)
    before = load_google_taxonomy(catalog_root=root)
    source.write_text(SOURCE + "- {id: 2, full_name: Other}\n")
    with pytest.raises(GoogleTaxonomyIntegrityError):
        prepare(source, root)
    assert directory.is_dir()
    assert load_google_taxonomy(catalog_root=root).manifest.fingerprint == before.manifest.fingerprint


@pytest.mark.parametrize("document", [
    b"value: 2026-10-31\n", b"value: .nan\n", b"value: .inf\n",
    b'{"value":"\\ud800"}', b'{"\\ud800":"value"}',
])
def test_shared_document_requires_finite_unicode_primitives(document):
    from shopextract.taxonomies.google.source_document import decode_source_document
    with pytest.raises(GoogleTaxonomyIntegrityError):
        decode_source_document(document)


@pytest.mark.parametrize("separator", ["\x85", "\u2028", "\u2029"])
def test_snapshot_unicode_line_separator_cannot_inject_category(tmp_path, separator):
    source = tmp_path / "injected.json"
    source.write_text(json.dumps([{"id": 1, "full_name": "Root" + separator + "2 - Injected"}]))
    with pytest.raises(GoogleTaxonomyIntegrityError):
        prepare(source, tmp_path / "out")
    assert not (tmp_path / "out").exists()
