# Behavior and test design (before task breakdown)

## Scenario matrix
| FR | SC | Given / input fixture | When | Exact expected outcome | Negative / boundary cases | Offline check | Live assertion / applicability |
| --- | --- | --- | --- | --- | --- | --- | --- |

## State and compatibility contracts
Record transitions, invariants, failure/recovery behavior and compatibility.
Derive expectations from requirements; resolve ambiguities before implementation.

## Red-test plan
Name executable acceptance tests and the expected missing-behavior failures.
Record actual red evidence after the skeleton exists, before production logic.

## Bounded live plan
Define targets, assertions, maximum requests/items, timeout, retry/resource limits,
stop conditions and saved evidence paths. Start with one smoke case. Record
access prerequisites; do not replace required live checks with mocks.
