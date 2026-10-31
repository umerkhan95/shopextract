# Taxonomy CLI integration contract

Coordinator author,2026-10-31. Thin adapters only; proposed narrow G2 supplement.
No taxonomy data bundled. Existing CoreGroup/CoreCommand/error envelopes,
read_json_file/raw_records/category_output/atomic publication own CLI bounds.

`taxonomy google` group options (before subcommand): --catalog-root PATH,
--version default2021-09-21, --locale defaulten-US, --fingerprint optional.
Commands: info; lookup ID; resolve-path PATH; list --cursor TOKEN --limit1..100;
lookup-batch FILE (strictJSON array of1..1000textIDs); validate FILE (boundedTXT);
prepare --source FILE [--expected-sha256 HASH] [--source-url URL]
[--provenance FILE]; normalize FILE --shop-url URL [--platform PLATFORM]
[--mapping FILE] [--allow-unknown-source-version] [--crosswalk FILE]
[--crosswalk-sha256 HASH] [--shopify-catalog-root PATH]; crosswalk audit
--source FILE --expected-sha256 HASH [--shopify-catalog-root PATH]
--offset0.. --limit1..100. Prepare requires explicit catalog-root. No network.
There is no mutable default-pointer update: prepare adds immutable resource;
ambiguity requires an exact fingerprint. Historical identities remain loadable.

Source TXT operations <=2MiB; root/product inputs <=1MiB/1000records as existing
CLI. Optional mapping file is an array of native typed MappingRule records,
validated through Google options and native mapper; no executable config.
Crosswalk source <=8MiB/hash checked using same Python loader, not stdin JSON.
Normalization returns categorized_products and matching ordinary products in
existing native CLI shape; existing export requires bound categories companion.
The result also reports effective Google classifications without promoting
multi-target or route conflicts. Missing/ambiguous mapping retains product.

List cursor encodes fingerprint+locale+version+numeric offset+page size with
strict fields and canonical JSON/base64URL; malformed, foreign-resource or
changed-page-size cursors reject. All target IDs enumerate once in numeric order.
Response includes current count/next_cursor/complete and catalog fingerprint.
Cursor is a revision binding, not a signed authorization token. Loader validates
local resource each operation; no private data is exposed by cursor.

Malformed/unknown lookup ID/path, bad cursor/arguments/config return E_USAGE;
missing catalog/resource/publication failures E_OPERATION. No E_INTERNAL for
expected native taxonomy failures. Every stdout response is existing compact
bounded JSON envelope; no partial file before validation. Help/capabilities/schema
never loads catalog or imports optional YAML. Add packaged Google manifest schema
to existing schema index; Python/native strict resource validation remains final.

Acceptance before code: taxonomy/google help missing command intended red;
then prepare/info/lookup/path/list/batch/normalize, pagination mismatch, corrupt
resource, malformed input and source-version permission tests. Real CliRunner
shares actual native helpers; installed subprocess smoke verifies registration.

Snapshot source-route CLI supplement: `taxonomy google --catalog-root PATH
prepare-snapshot --source FILE --expected-sha256 HASH --source-commit COMMIT
--source-url URL` calls only reviewed prepare_google_snapshot; version/locale
come from group options. Catalog root required; --fingerprint is rejected for
this publication command rather than pretending to select a generated identity
before conversion. Raw source <=2MiB, provenance preserves original and derived
hashes. No network or YAML inference on lookup. Initial expected missing-command
red is cli-snapshot-red.log before registering this thin adapter.
