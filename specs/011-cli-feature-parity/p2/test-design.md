# P2 behavior/test design

Synthetic seed11025; expected results specified before implementation.
SC21 root flags only before command; `stats distribution --help` works despite
bad config; unknown child/help errors; child option values '--help' are operands;
`--` stops option scanning. Existing native legacy behavior preserved. New groups
must traverse actual Click groups with child arity. Deferred P0 guard uses snapshot.
SC22 two records with same valid 00012345600012 GTIN -> exact; conflicting color ->
variant; duplicate target -> uncertain review. Fuzzy is native candidate lookup;
GTIN lookup preserves leading zeros. Pair input exactly one record per side.
Evaluate native labeled rows id/a/b/label; invalid label rejected before calls.
Identity assign preserves Decimal0.10/variant/false/evidence; inspect attrs normalizes
colour and capacity. Publisher aliases closed version1 mapping GTIN->string list;
semantic candidates closed version1 rows of target indices aligned source index,
range checked before call; files cannot name imports/callbacks. Both stdin invalid.
SC23 11 flat and portable records: total11, brand count11 (no preview). Typed decimal
0.10 and variant0.00 preserved; null/missing/false distinctions retained in flat
reports. Reject price boolean/NaN, nonstring GTIN, wrong attributes/variants/types.
Float aggregate metadata explicit; distribution buckets ascending unique finite
nonnegative; outlier multiplier finite positive. Empty collection valid.
SC24 compare USD1/EUR0.5 yields separate groups each rankable, no global cheapest.
Position USD10 with USD20/EUR1/unknown1 -> rank1 versus USD20 only; exclusions and
currency provenance retained before reduction; native legacy defaults unchanged.
SC25 marketplace missing required fields -> invalid count / exit4 machine; valid
empty input -> success; image missing URL native issue, controlled HEAD404/type
issues; invalid URL/concurrency/timeout reject before any request. Duplicates gtin
pair indexes[0,1], blank identifiers do not duplicate.
SC26 export real JSON/CSV/feed payloads; portable CSV/feed companion reimports same
product/evidence. stdout contains only artifact, optional missing parquet engine
E_DEPENDENCY actionable. Invalid format/path collision/input leaves old files.
Injected second replacement failure restores both old outputs; staging failure
leaves old output, no temp leaks; recovery failure retains named backup files.
SC27 caps input bytes1048575/1048576/1048577 (valid JSON padded); records999/1000/1001;
threshold0/1 accepted, nan/outside rejected; store count1/10/11; resources no effects.

First smoke one analyze-file. Then sequential pytest mechanism groups, <=1000
records/case, 1MiB inputs, case30s,total300s, no workers/models/public HTTP. Stress
12 groups spanning grammar, transports, matching ambiguity/config, currency,
validation/images, exporters/rollback and bounds; independent coverage review
before stress. One scoped temporary mutation must break an exact-money assertion,
then restore. Actual live observation: reuse P1 single public extraction receipt
only for shared extraction activation, not proof of all comparison sources. Public
P2 calls not authorized by parent budget; controlled HTTP separately labelled.

G1 additions: SC24 raw missing currency plus Product defaultUSD must be unranked;
explicit rawUSD grouped. Controlled source valid + failed -> partial exit3 with
source status; both failed -> exit1; shared timeout during second store -> timeout
without complete claims. SC26 initially absent second target rollback leaves it
absent; symlink/hardlink collisions rejected before stage; stdout + companion
rejected; recovery failure message names retained backup path. These target
provenance, incomplete fetch and filesystem identity gaps beyond existing tests.
SC26 correction: initially absent FIRST output + existing second companion +
injected second replacement failure -> first absent, second unchanged. Companion
staging failure after payload staging -> both unchanged, no temporary leaks.
SC22 G3 interaction: portable source rows [exactGTIN, duplicate unknown title,
duplicate unknown title] and targets [exactGTIN, unrelated] with candidate rows
[[],[1],[0]] -> index1 semantic target1 and index2 semantic target0. Native source
index rather than callback count/object identity controls rows despite first exact
row skipping callback. Reject both callback and declarative inputs concurrently.
For URL catalogs unknown lengths, preflight structural/max cap validation before
HTTP; actual dimension/range rejection after retrieval before matching is necessary.
Implementation research clarification (native stats.py get_price): native statistics
exclude nonpositive money. Distribution mechanism uses positive1/10/100 with one
in each expected bucket; separate transport test preserves zero unchanged. This
retains native statistics semantics; zero is neither silently dropped from catalog
input nor redefined as a valid aggregate price. Unknown source completeness remains
explicit metadata, matching P1, and is not alone a partial failure; known false or
errors are partial. Native failures need str(exc) before existing safe_error.
Coverage additions C01–04: first malformed raw currencyEUR dropped by normalization,
second valid WidgetUSD10 -> compare onlyUSD group; catalog counterpart EUR20 never
cheaper comparison. Shared deadline: first source completes, second sleeps past
shared10ms deadline, third never requested. Nonempty native product+variant price
observations/conflicting candidates/resolution/evidence survive CSV sidecar exact
portable roundtrip. Two preexisting files + second replacement failure -> first
restored, second unchanged, no stage/backup leaks. All new group missing/unknown
children emit default E_USAGE envelope. These close provenance, lifecycle and
recovery gaps, not additional random variations.
Final F01 grammar: Click parser boundaries reset '--' termination on descending
into child. `-- stats distribution --help` and `stats -- distribution --help`
bypass bad root config and display leaf help; leaf `stats brands -- --help` keeps
--help as filename and errors on nonexistent input. These are distinct group and
leaf terminator scopes; root flags remain valid before command only.
