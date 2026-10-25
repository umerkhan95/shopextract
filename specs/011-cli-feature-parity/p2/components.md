# P2 reusable component model
P0 CoreGroup owns root policy/error envelope; extend scanner by actual group and
child params. Register nested groups as plain Click groups with CoreCommand
children; only root owns bootstrap. New command canonical paths listed once in
_cli_core machine whitelist and envelope-only default routing set.
P1 _cli_data bounded reader reused unchanged; concrete CatalogInput adapter
adds flat record field validation retaining original dictionary shape and portable
product references. _portable product codecs own evidence/typed Product fields.
_cli_analysis report encoder accepts ONLY known report model dataclasses through
explicit allowlisted schema field names, Product via product_to_record, native
trees/Decimals via evidence codec; rejects unknown objects rather than str fallback.
Matching files schema-version1: publisher_aliases mapping, semantic_candidates
list[list[int]] with actual catalog lengths checked. Semantic adapter is a closure
owned by CLI and indexed by original record object identity; no executable input.
Network operations reuse _cli_extract.run_operation with ExecutionPolicy(), single
deadline and no ambient model/browser permission. Native compare/competitive own
currency-safe/source-aware algorithms, no CLI duplication of ranking/matching.
SourceStatus constructor called after extraction, errors sanitized. Wrapper applies
partial/error policy after safe native report; native legacy behavior preserved.
Export uses native to_json/csv/feed/parquet; temporary same-directory stage, native
portable Products only for requested companion. Shared atomic publication supports
payload and companion, backups via same-directory copy, rollback direct replacement
or deletion for absent target. Recovery errors retain artifacts and name paths.
CLI validates paths/aliases/format/input and companion support before writing.
No global environment mutation, dynamic imports from files or repeated algorithms.
G3 amendment supersedes closure adapter: native optional semantic_candidate_indices
list rows indexed by native source loop i, preserving duplicates and sources with
rule candidates that skip semantic lookup. CLI passes declarative data only. URL
catalog unknown lengths: validate max bounds before fetch, actual bounds after
fetch, no network callback allowed. This is native matching extension, not duplicate
CLI logic. Test duplicate Product rows + preceding rule-matched row, selecting
semantic indices at later positions correctly; rows out of actual range reject.
