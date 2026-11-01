# Rendered money components — G3 proposal

`extractors/_markdown_price.py` owns bounded price token discovery only; existing
Normalizer.money and currency registry own conversion/validation. `extract` and
`extract_price` retain positional compatibility,add optional captured currency/locale.
Amounts stay Decimal-backed text,including0 and arbitrary fractional precision;
no float/default ambiguous symbol currency. Explicit conflicting authority returns
amount with currency absent and diagnostic,not guessed resolution. Whole numeric
token validation rejects malformed groups/negative/nonfinite,not prefix matching.

`UnifiedCrawlExtractor._extract_from_crawl_result` remains admission/ownership owner.
It passes actual captured metadata/structured-offer currency context to parser,
retaining competing authorities for conflict handling,uses metadata amount presence
(including numeric0),merges only uniquely owned missing fields,and propagates
currency_conflict incomplete diagnostic. Existing rendered capture+excerpt support
owns price/currency transformations; no synthetic source or constructor changes.
One parse per crawlresult,no global mutable state; external failures retain current
partial behavior.17cases plus03 owner/free/native controls gate compatibility.
