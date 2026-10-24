# INT-20: Anthropic Claude Code plugin distribution

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#82](https://github.com/umerkhan95/shopextract/issues/82).
Related planned work: [INT-04 / #66](https://github.com/umerkhan95/shopextract/issues/66), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-12 / #74](https://github.com/umerkhan95/shopextract/issues/74).

Status: researched/planned;2026-10-24. Owner: Claude plugin maintainer. Dependencies:
INT-04 MCP routes, INT-11 portable pack, INT-12 Claude skills; no duplicate core.
Covers FR20/17/18, SC20/16/17/18.

[Claude Code plugins](https://code.claude.com/docs/en/plugins) bundle skills, MCP and
other components as one unit. Build a minimal plugin with trusted workflow skills and
approved tool connection declaration only; no hooks, agents, monitors or shell bootstrap
in baseline. This is a Claude Code plugin, not an IDE extension or automatic Claude
web/API store synchronization.

[Manifest reference](https://code.claude.com/docs/en/plugins-reference) locates metadata
at `.claude-plugin/plugin.json` and ordinary components at plugin root. Proposed layout
has `skills/shopextract-review/SKILL.md` and `.mcp.json`, using current validated manifest
fields and contained relative paths. Pin/test exact Code version/parser before generating
an install artifact. Keep server credentials outside distributed files; configuration
substitution must not introduce unsafe shell interpolation or overwrite other MCP names.

Private folder load/test comes first, then versioned package/marketplace distribution;
public Anthropic directory and organization rollout are separate external decisions.
Skill activation does capability/auth preflight; enabling plugin is not consent for
merchant writes or arbitrary origins. Existing local stdio lifetime remains ephemeral,
remote job state follows shared service contract.

INT-12 now separately maps [Messages API skills](https://platform.claude.com/docs/en/build-with-claude/skills-guide)
via `container.skills` plus code execution. That container has no network/runtime
package installation: fetch data through application-owned tools first, then provide
sanitized owned inputs for skill processing; it cannot call ShopExtract HTTP from inside
its skill script. Managed Agents route remains separately configured.

- [ ] Clean plugin validation/load exposes skill+MCP without unintended components; invalid manifest/traversal/secret fixtures reject.
- [ ] Fresh/update/disable/re-enable preserves intended selected version and owner-bound tools; collisions are diagnosed, no config overwrite.
- [ ] Missing server/auth/scopes leaves explicit prerequisite; model/source text cannot enable unavailable exports/maintenance.
- [ ] Product ZIP, Code plugin, Managed Agents and Messages container rows retain separate actual verification/distribution states.

Future clean-profile smoke one install/update/three prompts, ≤6tools/two products/120s.
API tests additionally require exact model/token/pricing$1 preflight. No plugin/skill
built, installed, uploaded, run or published here.
