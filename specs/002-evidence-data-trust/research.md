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
