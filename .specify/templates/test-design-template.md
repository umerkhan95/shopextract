# Behavior and test design (before task breakdown)

## Scenario matrix
| FR | SC | Given / input fixture | When | Exact expected outcome | Negative / boundary cases | Offline check | Live assertion / applicability |
| --- | --- | --- | --- | --- | --- | --- | --- |

For each SC identify its distinct failure risk or interaction, the existing
coverage gap and why this test adds coverage. Include relevant just-below/at/
just-above boundaries, missing/null/empty/zero/false, malformed/escaped identities,
ordering, recovery and combined feature states. Avoid renamed duplicates or random
input variation without a different invariant. Independent reviewer checks gaps.

## State and compatibility contracts
Record transitions, invariants, failure/recovery behavior and compatibility.
Derive expectations from requirements; resolve ambiguities before implementation.

## Red-test plan
Name executable acceptance tests and the expected missing-behavior failures.
Record actual red evidence after the skeleton exists, before production logic.

## Unobservable behavior and synthetic mechanism plan
For each unobserved FR/SC, define exact expected transitions/invariants, realistic
schema-valid fixtures and labelled malformed cases before generator code. Identify
the fixture/generator author and independent coverage reviewer. Record synthetic
or derived-offline provenance, fixed seed, factory and actual production entry
points exercised. Mock external boundaries only, not the mechanism being tested.

## Bounded stress plan
Define relevant adverse cases and exact case/iteration counts, seed, input-byte/
memory limits, timeout, worker cap and stop conditions. Start with one saved smoke;
run a sequential bounded driver. Include replay/recovery, fault and budget edges
where relevant. Save minimal reproductions and prove critical assertions detect
the intended failure when appropriate. Cite still-valid saved runs instead of
repeating completed work. Required missing mechanism coverage blocks completion.

## Bounded live plan
Define targets, assertions, maximum requests/items, timeout, retry/resource limits,
stop conditions and saved evidence paths. Start with one smoke case. Record
access prerequisites; do not replace required live checks with mocks.
If live values stay unchanged or a scenario cannot be observed, agents execute
the synthetic mechanism/stress plan and report its results separately. Retain
blocked/inconclusive status for the actual live observation; do not invent it.
