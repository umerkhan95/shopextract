# Rendered monetary parsing — behavior follow-up

FR-RM1: rendered markdown prices reuse reviewed Decimal/context/ISO registry
conversion,never float/.2f. Explicit KWD1.234 remains1.234,PKR3,720 ->3720,explicit
zero accepted as observed amount with zero diagnostic. No defaultUSD from bare$
orJPY from¥; unknown currency omitted/unsupported while unambiguous amount may
remain. Explicit ISO/context supplies authority; conflicting codes unresolved.
FR-RM2: preserve old explicitEUR/USD/GBP positive controls and browser normalized
source support. Rendered parser supplies source extraction,not product admission;
policy markdown cannot create a product. No change to model constructors,identity
or default feed formats. Source_excerpt/transform history remains inspectable.
