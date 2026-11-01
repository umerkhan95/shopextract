# Behavior/test design before breakdown

Scenario IDs and exact expected outcomes: spec.md. Distinct uncovered risk:
A single completeness percentage mistaken for commerce integration or platform approval; actual CLI/report/projection with pinned source rules and zero external requests.

Fixture author uses tiny sanitized saved audit sources plus deterministic factories
seed0. Mock external HTTP/DNS/clocks/library boundaries only; actual algorithms,
normalizers,encoders,CLI/tool/persistence paths execute. Design all new edge cases
before tests/fixes; retain accepted native/freeProductGroup/empty-normalize controls.

Acceptance/stress cap64 concrete cases per child,one worker,120s subprocess,
1MiB ordinary input (child02 byte-boundary fixtures up to32MiB+1),256MiB target
retained test memory,stop first unexpected failure and one diagnosed repair.
Enumerate exact collected cases before red run;64 is maximum,not promised coverage.
Save one smoke before expansion. Distinct missing/null/empty/zero/conflict and
just-below/at/above limits from SCs are separate assertions; seed variation is not
new coverage. Independent reviewer checks fixture realism and real-path execution.

Live plan: N/A for local-file command; zero-network assertion is executable. External Google approval/ACP checkout are explicitly not assessed,not claimed as passing live integration.
Offline: focused acceptance/affected checks then configured scripts/run_tests.py
240s-family/480s-total (never increase). Prior timeout does not satisfy this gate;
record unrun families and unknown failure nodes honestly. Separate synthetic
mechanism,stress and actual live evidence; inconclusive live is never a pass.

ExecutableG2 design BEFORE tests:17cases. Googlemissingcontext+invalidcurrency+
missingID3;actualCLI strict/nonstrict retainreport2; schema partial/groupseparate2;
OpenAIcompleteavailabilityunknown,missingseller,missingbrand,unknowncurrency4;
explicitCLI sellercontext,no inferredmerchant1;variantsbasiccomplete=>needscontext1;
ACPperfectcatalogalwaysunassessed1;reorderedinputdeterministic1;CLIinvalidtarget
beforeunreadablepath1;malformedcontextbeforeassessment1. ActualCLI/profilehelpers,
zeroHTTP assertion via failingnetworktransport,not mockedassessor. Boundedmax1000
records/100variantcoverageentries/report,existing32MiB reader/depth64/1Mnodes;
strictpartialexit3 preservesdata,non-strictoperationexit0;120souteroneworker.
FirstsingleCLI redsmoke savedbeforefullnew. No live/approvalclaims/no sourcefetch.

G2 repair BEFORE tests:7newcases,total24. QualifiedGooglefullcontext positive
readyONLYlimitedprofile;completeSchemafivefieldcoverage positive (cannotalwaysfalse).
ActualportableCLIcapturednative validfacts/defaultstockTrue unsupported =>OpenAI
availabilityunknown/basicprofileready with explicitseller. Fourtargetrootmetadata
cases assert schema_version1.0,nonemptyrule_set,source_date2026-11-01,provenance
and actualtargetprimarylink (not genericplaceholder). Invalidtargetproof strengthens
to E_USAGE+reader-callcounter0 instead of relying sanitizer-specific errorwording.

G3 bounds before tests:11 additional cases,total35. Helper top1000/1001 checks
positive complete OpenAI versus explicit record_budget_exceeded/all1001 omitted;
two-parent aggregate variants100/101 checks global budget (not per parent); nested
groups depth8/9 checks root-depth convention; active cycle must return diagnostic,
not recurse. Description UTF-8 bytes8192/8193 checks field cap.200 large but each
within-field inputs exceed8MiB aggregate projection budget and return bounded
report with projection_byte_budget_exceeded. Actual CLI1000-record positive and
1001-record E_USAGE are two assertions in one boundary case. No network/large raw
copies; shared string fixtures keep memory bounded. Firstsmall cap smoke precedes
full new set,120s ceiling. Resource overflow is needs_context,not vocabularyinvalid.

G3 compatibility amendment BEFORE production/tests:actualsaved audit has25products,
265variants andprovenancedepth11. Distinguish1000sourcevariants/depth64 from100
assessedvariantnodes/depth8;neverwalk/copyrawprovenance. Existing100/101groupcases
nowassert100assessed coverage+explicitomission at101,retaining2topitems ratherthan
rejectinginput. Sourcevariants1000/1001 twoadditionalhelperboundaries;actualportable
native25/265 CLI withdeep11 provenance mustexit0/report25items andvariant-grouping
needs_context,not E_USAGE. AdditionalUTF8multibytefieldcase guards bytes,notchars.
Total39cases (35prior+4),120s ceiling/no sourcesfetch/rawaudit reread.

Implementation inspection before repair:3 distinct cases,total42. A depth-truncated
variant subtree containing two descendants must count all3 omitted nodes,not just
its root. Uncaptured URL variant reference returns needs_context/no network rather
than raising; malformed numeric variant container returns explicit needs_context
shape diagnostic,not vocabulary-invalid or an unbounded crash. Both remain bounded
by existing source graph guard. No broader schema validation is introduced.

Sorting resource inspection BEFORE repair: `_key` serializes child JSON strings
inside parent JSON, causing repeated escaping with depth. Use a small depth12
mechanism probe: key representation must stay below20KiB; this is ample for its
small scalar input and detects nonlinear encoding without unsafe deep execution.
Build bounded structured key shape and serialize once. After that repair, execute
real public helper source-graph depth64/65 boundaries (assessment still8). These
three cases bring total45; deep probes deferred until the small mechanism is safe.

Three final real CLI forwarding controls,total48,designed before tests: qualified
Google --context succeeds within named subset, --country overrides that context to
unsupportedXX/needs_context, complete rawSchema file succeeds within coverage scope.
These verify the user paths as well as helper positive controls; no new behavior.

Functional review repair before code:7 cases,total55. Four identifier fields
(item_id/external_id/sku/productGroupID) with cyclic or small oversized containers
must produce unsupported_identifier_shape before sorting/serialization,with no
copied payload. Preserve legitimate schema URL/image/brand/offer containers and
select a bounded explicit productID label. Two differing-brand fixtures require
identity-first and then URL-first ordering,with structured shape only as stable
tiebreaker. Existing depth12 key-size assertion counts all key components if the
private sorting key becomes a tuple; same20KiB bound,no weakened resource contract.
