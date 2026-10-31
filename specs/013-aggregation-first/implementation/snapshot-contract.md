# Explicit Shopify-maintained Google snapshot preparation

Date:2026-10-31. Candidate narrow G1/G2/G3 follow-up; no self-approval. This
implements the already accepted operator-supplied full source route reproducibly,
without a one-off shell conversion or hidden network/resource installation.

## Behavior and acceptance design

SFR01 `prepare_google_snapshot(source_file,catalog_root,*,source_commit,source_url,
expected_sha256,version='2021-09-21',locale='en-US')->Path` reads at most2MiB of
explicit local primary-source YAML/JSON and checks required SHA256 BEFORE parse/
conversion. Source commit40lowercasehex, source URL nonemptyHTTPS and Google
release/date/locale are caller-declared provenance, not authenticated metadata.
No request is made, no automatic download or version inference from content.
SFR02 Exact source shape is nonempty array of exact `{id,full_name}` objects.
ID is a positive integer (notbool) or canonical ASCII decimalstring; full_name
is text without line-break/control injection. Duplicate ID/path, missing parents
or invalid source graph rejects through the existing Google TXT parser. No aliases,
anchors,tags,duplicate mapping keys,nonfinite/arbitrary values or oversized tree.
SFR03 Preserve source array order in deterministic TXT: exact standard header,
each `ID - full_name` line and final newline. Original file SHA and consumed
derivedTXT SHA remain separate in source_kind=shopify_google_snapshot provenance,
with source URL and commit. Existing parser/catalog/publisher produce the same
immutable resource as explicit manual conversion. Fingerprint binds all metadata.
SFR04 Invalid input/hash/provenance/publication leaves previous catalog readable;
no derivedTXT need remain on disk and no raw dataset is bundled or committed.

| Scenario | Exact expected result / distinct risk | Real mechanism |
| --- | --- | --- |
| SSC01 two-node source | Root1/child2,2nodes/1root/1leaf; source_kind and original/derived hashes exact; repeated prepare samePath | Strict source decode→existing Googleparser→publisher→loader. |
| SSC02 wrongHash before decode | Hash failure for intentionally malformedYAML; no resource directory published | Boundedread/SHA gate, not parser exception masquerading as hash check. |
| SSC03 malformed source | Duplicate YAML key,alias/tag,wrongrowkeys,boolID,stringnoncanonicalID,newlineinjection,emptyroot reject with typedintegrity | Shared strict source decoder and existing catalogvalidator. |
| SSC04 existing resource | Invalid nextsnapshot preserves old fingerprint/resource; same bytes differentcommit gives distinct identity and ambiguousunpinned lookup | Actual immutable resource store; no overwritten old version. |
| SSC05 crosswalk regression | Extracted strictdecoder preserves valid officialforward source and existing adversarial failures | Existing crosswalk test suite plus original source hashes. |

## Responsibility and dependency contract

`source_snapshot.py` owns only explicit source schema/conversion/provenance and
orchestration. Reuse source parser/catalog/publisher; no second graph validator,
native mapper or resource writer. The shared `source_document.py` decoder has
two actual consumers: snapshot and crosswalk. It owns strict UTF8/JSON/YAML
decoding, duplicate-key/alias/tag rejection,500000nodes/depth64 finite tree; callers
own file byte limits/SHA and semantic schema. PyYAML imported only on explicit
YAML operation; missing extra is actionable GoogleTaxonomyError. Decoder never
imports either consumer. Crosswalk extraction coordinated with its owning author;
no lower source/registry/config limit changes.

Strict source decoder `decode_source_document(data:bytes)->object` raises typed
GoogleTaxonomyIntegrityError for malformed encoding/tree/duplicate/alias/tag;
returns finite primitive JSON-like dictionaries/lists/scalars only. Snapshot
resource route remains2MiB, crosswalk8MiB. Source operation120s/512MiB applies.
No new configurable policy/framework. The lazy public wrapper/export and CLI
prepare-snapshot thin adapter are separately owned by integration/coordinator.

## Tasks, red and verification

1. Author writes this behavior/test/interface/component contract then acceptance
tests; independent reviewer records narrow G1/G2/G3 and intended-red evidence.
2. Extract existing decoder with owner consent; implement snapshot adapter only
after review. Test originalhash/derivedhash/provenance and invalid-source replay.
3. Run focused snapshot+crosswalk+resource regressions, actual local full-source
preparation and compare exact parent-derivedTXT hash30039729880ec5ac4851de088ad228a6898aa253f0de5d5ebea5bb1437478fce.
Full primary source receipt stays parent-owned, no extra network/request needed.
Required full driver/final code review remain parent integration gates.
