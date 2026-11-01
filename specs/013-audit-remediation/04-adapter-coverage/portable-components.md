# Nullable variant stock compatibility — existing component reuse, G3

Change only Variant.in_stock annotation to bool|None,keeping defaultTrue and field
order/positions. Existing type-derived portable codec admits explicitunknownNone;
no alternate validator,Product migration or schema version rewrite. Packaged
transport schemas do not separately constrain this field. Bool values stayvalid,
text remains invalid,source contracts and all other guards remain unchanged.

The five predesigned real normalization/codec cases cover nullable/known values,
source-support fidelity and old constructor behavior. New null values require a
consumer that supports unknown variant availability; describe that distinction
without turning missing stock into false/in-stock. No broader model migration.
