# Scoped portable projection performance amendment — design before code

Recurrent full main timeout239.06s at93%, all completed nodes pass. No limit/skips
changed, oracle/maintenance NOT RUN, live gated. One cProfile of real Woo100 later404
pipeline/CLI passed3.41s; operation2.05s, extraction_data1.47s,100 product_to_record
calls1.46s;57,842 deepcopy calls,61,400 asdict traversals,400 contract validations.
Saved evidence/integration-profile*. This identifies repeated projection overhead,
not proof of the entire full-main cause. No N²/prefix or fixed speed claim.

FR-P1 private _evidence._record_values(value) preserves standard dataclasses.asdict
output for transport-supported trees, recursively creates NEW dataclass/dict/list
containers, and reuses immutable primitive/Decimal/datetime/Enum leaves instead
of deepcopy. Unknown object/container types fall back to standard asdict/deepcopy
semantics and existing validation rejects unsupported transport. No source mutation,
no global cache, no expanded public codec types. Existing byte/node/depth guards,
_product/_contract type checks, source trust validation, and timestamps unchanged.
FR-P2 TrustContract.to_dict still validates then encodes this projection. Portable
_contract_to_dict already typechecks and calls trust_view (which validates contract)
so it may encode immediately using same projection without second to_dict.validate.
No await/thread/cache seam; default/public contract validation unchanged. Product
values use same projection then existing validate_tree and encode_value. Exactly
three call sites, helper owned by evidence codec; no transport/schema/API change.

SC-P1 real captured Woo variants/free/context currency product and ALL contracts
match frozen standard asdict+encode_value reference, reload exact values/evidence.
SC-P2 spy delegates real deepcopy and observes zero deepcopy for immutable leaves
in supported nested helper input (mechanism, not a fake helper). SC-P3 mutable
projection containers independent of source; SC-P4 malformed native stock/rawobject
and tampered contract still rejected. Four cases, first red before expansion,
full<=30s capped threads. Same original Woo100 case after repair + selected portable/
evidence controls<=120s; optional SAME-control before/after counters, no new sweep.
Independent G1/G2/G3 amendment review before code; full driver remains required.

Exact ordering added to JSON equality oracle; fixture asserts one real variant.
Tamper uses object.__setattr__ only to create adversarial frozen-contract corruption
(replace validates immediately); cycle in raw_data must retain portable ValueError.
Original30s actual25/265 all-field/variant/evidence/analyze/export reload diagnostic
required after repair, no expanded benchmark/limits.

Spy positive control before final review: patch copy.deepcopy MODULE lookup used
by helper fallback (no captured alias). Mutable str subclass must invoke original
fallback and preserve detached custom state, in same SC-P2 case; immutable leaves
still zero calls. This proves the counter would see an inappropriate leaf copy.
