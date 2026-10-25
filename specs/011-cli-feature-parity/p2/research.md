# P2 bounded local research 2026-10-25
Existing native signatures inspected: compare/price,catalog,match,identity_match,
evaluation; analyze/stats,competitive; validate/images,duplicates,marketplace;
export/__init__,_bundle; Product/Variant and portable codecs. No web required.
Native compare_catalogs takes two URLs, threshold=.8,max_products200 and optional
aliases/semantic provider/identifier options. Native compare threshold=.6,max50.
Native position/gaps max200 fetch URLs, brands takes mapping. Images timeout10,
concurrency20. Stats buckets float list, outlier multiplier2. Native identity
algorithm owns matching; no duplicate business logic. PricePosition float inputs
lose currency: additive currency parameter must filter raw matches before get_price.
Compare additive group mode must group Match records before _build_result. Native
stats floats documented approximate. No claim of exact float recovery.
New flat catalog codec must validate concrete fields yet retain missing/false/zero
without normalizing data; typed Product conversion only for identity/export evidence.
Portable records use _portable, reports explicit typed encoders (no default=str).
Native CSV/feed sidecar accepts Product only; JSON/Parquet lack companion support.
Native _prepare/asdict may serialize dynamic evidence only via sidecar; preserve
portable source Products for companion. Native export stage path with same suffix.
P1 default ExecutionPolicy isolates implicit ambient model/browser fallback.
P0 flat bootstrap inadequate for nested group children; extend from actual Click
params without runtime activation. No installs/paid/model work. Counters unavailable.
