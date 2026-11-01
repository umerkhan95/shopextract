# Design before breakdown

SC-RM1 KWD1.234 exact precision;PKR3,720 grouping;USD9007199254740993.10 exact;
zero explicitEUR accepted. SC-RM2 bare$12.50/¥1200 have amount but no invented
currency;knowncontextCAD resolves$;explicitUSD conflictscontextCAD =>unsupported.
SC-RM3 malformed separators/nonfinite/negative rejected,not observedzero.
SC-RM4 actual known200 browser Product+SKU gets exactKWD amount and source-supported
currency;empty generic policy withsame markdown remains rejected. Existingexplicit
EUR/USD/GBP fixtures and03browserowner/multi/free controls reused.

Real `_markdown_price.extract`/Normalizer/browser paths,no duplicate conversion.
Seed0,<=16cases,64KiB strings,oneworker,120s red/green;firstsmallsmokesaved. Local
mechanism change needs no new merchant request; later bounded live afterfullgreen.

G2 refinement:17cases (prior16plus actualbrowserKWD1.234). This unique owned Product+SKU must normalize exactDecimal1.234/KWD and both fields observed with resolved evidence from actual URL, retained markdown/excerpt containing KWD1.234. Risk: utility pass can conceal caller precisionloss or unsupported fabricated evidence.

Fixture correction after firstgreenattempt16pass1fail: crawler helper defaultURLwasroot despite requestedproductURL; explicit result.url=URL aligns actualobservedURL. Evidence excerpts live in retained_data.source_excerpt by existing contract,not Evidence.excerpt; assert that exact established slot. No expectation for precision/support weakened.

Functional refinement BEFORE repair:7distinctcases. Bare£/₩ have unknowncurrency; capturedFKP/KPW context resolves respective symbols without conflict. Space-groupedEUR1 234,50 withoutlocale rejected WHOLE (neverprefix1); explicitfr locale accepted1234.50 using shared money conversion. Actualbrowser structuredCADoffer+metadataUSD conflict retainsprice12.50,normalizedcurrencyempty/unsupported,partialdiagnostic; originalcapturedCAD retained,never falseobserved currency. Risk: existingoffer bypasses missingfield-only merge. Totals24cases; oneboundedred thenrepair,notexpandedresearch.

Secondfunctionalrefinement BEFORE repair:2cases. Actualbrowser pureOGproduct(priceCAD)+metadataUSD projects emptycurrency/unsupported+incomplete but retains originalCADcapture. Actualbrowser structuredusd+metadataUSD is samecanonicalauthority,USDobserved withoutcurrency_conflict. Risk: parallelOGowner branch missingclearing and lexicalcase falseconflict. Total26.
