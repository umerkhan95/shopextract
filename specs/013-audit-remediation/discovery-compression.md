# Discovery compressed-response integration — design before repair

After full offline driver4 passed2229 cases344.10s, four bounded HTTP live cases
passed. Khaadi robots200 body/policy was unavailable: one request, no forbidden
request/emission; live merchant expansion stopped. Its precise cause was not
captured and is NOT attributed as fact. Independent source risk: _read consumes
aiter_bytes (decoded), then reconstructs Response with original Content-Encoding,
causing second decode for compressed wire responses. Prove with controlled real
HTTPX decoder, no new merchant request; preserve actual inconclusive observation.

FR-C: copied decoded Response drops Content-Encoding/old Content-Length, lets
HTTPX set decoded length; preserve status/URL/content-type/cookies/otherheaders.
Decoded bytes still counted against existing response/robots caps BEFORE copied
Response. No limits, policy, fallback or retry changes. One _read return seam.
SC-C1 gzip robots+XML through real client/guard/local discovery returns allowed
URL and policy, original string contents unchanged. SC-C2 gzip JSON API response
remains parseable, original contenttype/cookie/status/url retained and decoded
length correct. SC-C3 compressed129-byte decoded body under128-byte lower-only
fixture cap rejected with budget diagnostic (even small wirebody). First smoke,
three cases<=10s, then19discovery+affected controls<=120s. G1/G2/G3 review before
source repair; source full driver freshness recorded, no retrospective live pass.
