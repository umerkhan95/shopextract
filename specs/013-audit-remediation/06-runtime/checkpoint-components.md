# R3 component ownership — G3 proposal

ExecutionState owns one private ProgressCheckpoint for opted-in extract-store
operations. It holds at most8 accepted source references,including the generic completed
HTTP collector; no per-page normalization, snapshots, persistence or new framework.
Native adapters bind their captured accepted lists; the actual HTML probe/batch
completion path records admitted products. Existing HTTP/browser admission stays
before that boundary. Completed pipeline normalization may register exact Products.

Pipeline configure_result supplies detected result platform, catalog/customer scope
and restore policy. Each source independently owns normalization platform and tier.
The Shopify cookie source is attached when a row is accepted, preserving its current
field-source mapping. Existing normalizer/GTIN policy executes after cancellation;
no barcode/currency defaults are promoted to observations. First usable tier follows
pipeline preference; no cross-store merge. Recovery emits standard ExtractionResult.

The owner cancels and awaits outstanding work before synchronous freeze. Existing
product_to_record/canonical JSON/preflight/product_from_record codecs enforce
1000 records,8MiB record bytes,250k aggregate nodes and depth56; record token count
is bounded by these nodes and existing lexical scanner. Private fixture limits can
only narrow ceilings. A positive retained prefix is explicitly incomplete,with
operation_timeout and any checkpoint_budget_reached reason; none yields E_TIMEOUT.
The context ends ownership and prevents restart reuse. External cancellation propagates.

run_operation's optional recovery callback is used only by extract-store; ordinary
command types and unowned library calls retain behavior. Generic/type callbacks
cannot manufacture result rows. Sync freeze/reporting follows the I/O deadline:
these are work bounds,not a total walltime guarantee. R4 isolation is separate.

Seventeen real-path/boundary tests precede implementation. Use first Woo/HTML green
smoke,then17 acceptance and affected checks under120s. Fullrepo/live/final gates
remain pending; no source fetch or historical audit reread needed for this slice.
Existing --shop-url normalization context is also retained by configure_result's
optional shop_url field; producer fetch origin does not override caller supplier
context. The normal-v-timeout restore fixtures compare supplier IDs/product URLs
under an explicit different supplier base,without any request to that base.
