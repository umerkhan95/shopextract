# Resolved design questions — #34

- Keep dataclass scalar defaults: replacing USD/0/True with nullable fields would
  break existing consumers. A separate trust view exposes unsupported legacy values.
- Use escaped JSON Pointers: nested collection indices and attribute keys have a
  precise representation; IDs identify observations independently of field paths.
  Paths refer to a particular record revision; reordering variants requires remapping.
- Require retained data for pointers: a live URL is not captured source evidence.
  Excerpts are bounded relevant fragments in the future capture layer; source roles
  default to unverified and never establish manufacturer authority by domain alone.
- Use tagged Decimal/UTC values rather than floats or ambiguous strings. Escape
  dictionaries containing `$type` so arbitrary raw structured data survives a round trip.
- Separate raw model/rule score from validated confidence. Calibration evidence is
  declared through method/dataset/version; the library validates shape, not statistical
  truth. Existing platform/matching confidence APIs retain their current semantics.
- No Spec Kit CLI or agent configuration installation: initialize the minimal local
  constitution and planning templates needed for this repository's requested workflow.
- No authority algorithm, persistence migration, extraction capture or portable Product
  export in #34. These require the approved interfaces and belong to dependent tickets.

Evidence used: issue #34 and parent #22; existing `_models.py`, `_normalize.py`,
`identity.py`, snapshot `asdict` usage and existing JSON/export interfaces. No external
research/model sweep was needed for these local compatibility choices.

## #36 decisions
- Separate supplier offers from manufacturer specifications; a manufacturer price
  is not evidence of a supplier offer. Only explicit verified_manufacturer source
  roles confer specification precedence; hostname matching proves nothing.
- Freshness excludes candidates rather than making the newest conflicting peer
  automatically correct. Use the oldest referenced evidence to reject partially
  stale support conservatively, and require evaluation time for reproducibility.
- Resolution retains all observations/evidence and returns a copy. Preserve input
  unsupported states and existing validation metadata; do not manufacture scores.
- Conservative typed equivalence avoids treating false as numeric zero, units as
  interchangeable, or differently-cased identifiers as the same specification.
- Matching integration is explanatory references only: automatic resolution must
  not silently change canonical identity or the existing matching score meanings.
