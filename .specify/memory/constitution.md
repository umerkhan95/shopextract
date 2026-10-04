# ShopExtract project principles

1. Preserve existing Product/Variant constructors, canonical identity semantics,
   extraction APIs and default feed formats. Add explicit opt-in contracts.
2. Report supported facts only with inspectable captured source support. Missing
   and legacy/default values never become observed facts through scalar defaults.
3. Preserve competing observations and transformation history. Never invent source
   URLs, observation times, manufacturer authority or calibrated probabilities.
4. Verify behavior using meaningful bounded offline fixtures and affected regression
   checks. Save results before expanding scope; no live crawl or model run needed.
5. Apply the user's bounded-usage instructions: sequential work, no parallel agents
   or inference without authorization, bounded processes, and saved progress.
6. Keep core code and contracts MIT, self-hostable and free of paid service gates.

Integration: use `.specify/templates/` as local planning templates. No CLI install,
user configuration replacement, or generated agent commands are required. Feature
work lives in `specs/002-evidence-data-trust/`; linked tickets update it in place.
