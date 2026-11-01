# Existing stock contract portability amendment — before code

Variant.in_stock:bool|None=True. No field reordering/default change or new serializer.
Existing type-derived portable validation handles the union. No explicit stock type
in packaged schemas requires a parallel validator. Other type/resource guards stay.
G1/G2 amendment review then concisecomponents/G3 before source type change.
