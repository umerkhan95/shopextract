# P2 interfaces
_cli_analysis.register(main) registers lazy Click commands/groups: match,
match-gtin,match-pair,match-evaluate,identity assign/inspect,analyze-file,
stats distribution/outliers/brands,competitive position/gaps/brands,images check,
duplicates,export,compare-catalogs. Existing compare/analyze/validate delegate
explicit machine/additive branches; defaults retained.
_cli_data.catalog_from_value(value)->CatalogInput(records:list[dict],
products:list[Product]|None). Portable records/envelopes retain Products; concrete
flat records decoded/validated with allowlisted typed fields, unknown extensions
JSON-safe preserved. No conversion to Product for statistics/matching flat input.
_cli_analysis.report(value) explicit known report dataclass field schemas and
portable Product encoder; Decimal codec tags, Enum values, tuples as arrays.
matching_options(files,left_count,right_count) validated declarative adapters.
network(operation,timeout) reuses P1 execution wrapper and shared noLLM/browser
policy; source-aware native optional safe APIs retain incomplete source metadata.
export_artifact(catalog,format,target,evidence_target) validates before staging,
uses native exporter, staged backup/replacement/recovery. New destinations removed
on rollback; recovery artifacts retained and named if recovery fails.
scan_bootstrap traverses actual Click groups, tracks full path and option arities;
root flags only before root child, '--' terminates options, no runtime imports.

G2 concrete declarations: _models.SourceStatus(store:str,usable:bool,
catalog_complete:bool|None,errors:list[str]); SafeComparison(query:str,
currency_groups:dict[str,ComparisonResult],unranked:list[Match],sources:list[SourceStatus]);
SafePosition(position:PricePosition,currency:str,excluded:list[dict],sources:list[SourceStatus]).
compare.price.compare(...,currency_safe:bool=False)->ComparisonResult|SafeComparison:
safe mode sequential extraction under inherited policy; source status from native
ExtractionResult; observed currency from aligned raw currency, otherwise captured
supported currency reference, never Product default; group before _build_result.
competitive.price_position(...,currency:str|None=None)->PricePosition|SafePosition:
None legacy; explicit currency filters native raw match before get_price, records
excluded store/currency and source statuses. Missing raw currency excluded.
compare_catalogs(...,source_report:bool=False)->CatalogDiff: additive sources field,
source_report mode sequential extraction, failure retained, currency comparisons
only explicit aligned raw/evidence currency. assortment_gaps(...,source_report=False)
additive sources field, sequential unchanged algorithm with explicit failures.
Source statuses serialized by fixed fields; incomplete usable sources produce exit3;
no usable sources exit1; no complete report on deadline. Exceptions sanitized.
CatalogInput.products only portable; flat_to_products(records) accepts Product's
concrete fields only, fills constructor defaults solely for identity/export projection,
Decimal string/number price conversion, Variant recursive typed fields; validates
via product_to_record then product_from_record; unknown flat extension fields stay
in records but typed projection rejects unsupported fields rather than dropping.
Portable evidence companions only; no fabrication of evidence from flat records.

G3 correction: match_products(...,semantic_candidate_indices:list[list[int]]|None=None)
and compare_catalogs(...,semantic_candidate_indices:list[list[int]]|None=None) gain
additive declarative native input. Native loop selects row by existing enumerate i;
validate full dimensions/indices before matching/extraction (URL catalogs validate
range after retrieval before matching, syntax and global limits before network).
Never use callback counters/object identity/content deduplication. Existing Python
semantic callback API remains unchanged, reject supplying both APIs together.
Coverage C01 correction: provenance must use associated Product.raw_data, not
parallel ExtractionResult.raw_products indexing; native normalization can drop
records. Existing raw array remains untouched and scalar Product currency preserved.
New group families route malformed/unknown child errors to envelope by default.
