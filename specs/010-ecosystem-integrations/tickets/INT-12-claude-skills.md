# INT-12: Claude skill installation and workflow integration

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#74](https://github.com/umerkhan95/shopextract/issues/74).
Related planned work: [INT-04 / #66](https://github.com/umerkhan95/shopextract/issues/66), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-20 / #82](https://github.com/umerkhan95/shopextract/issues/82).

Status: planned;2026-10-24. Owner: Claude skill maintainer. Dependencies: INT-11 and
INT-04 corresponding tool route. Covers FR17/18, SC16/17/18. Skills provide trusted
instructions; existing MCP connector still owns tool execution/authentication.

Document product, Code and separate API routes. Claude product users can upload a skill-folder ZIP
under Customize/Skills, toggle it, and share where organization policy permits;
[Claude skills help](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
describes personal visibility and Team/Enterprise sharing controls. A personal upload
does not automatically provision an organization. Package folder/name/frontmatter must
validate and contain no connection secrets.

Claude Code uses project `.claude/skills/<name>/SKILL.md` or personal
`~/.claude/skills/<name>/SKILL.md`, with documented activation/metadata per
[Code skill guidance](https://code.claude.com/docs/en/skills). Installation instructions
must name project versus user scope, avoid replacing unrelated skills and show how
to identify discovered version after update. Local skill discovery does not register
an MCP server: configure INT-04 separately.

API/workspace route is distinct: [Managed Agents skills](https://platform.claude.com/docs/en/managed-agents/skills)
uploads custom bundles and attaches `skill_id` plus pinned version to an agent.
This is not automatic synchronization from Claude web uploads or arbitrary Messages
API requests. Child must verify the exact API route/runtime feature availability;
[Messages API skills](https://platform.claude.com/docs/en/build-with-claude/skills-guide)
is now separately researched: container.skills with code execution and pinned skill
version; no container network or runtime package install. Application-side tools fetch
approved data, then provide sanitized owned inputs. This route is not Managed Agents
or product-upload synchronization and requires separate actual API/model testing.

- [ ] Personal ZIP upload, Code local directory and API workspace routes each have exact prerequisites and separate status.
- [ ] Intended extraction/matching review activates; unrelated prompt does not; missing tool/auth returns explicit prerequisite.
- [ ] Fresh install/update version is observed in each eligible target; duplicate scope or stale loader state is diagnosed without overwriting user config.
- [ ] Untrusted product instructions cannot change policy, enable extra tools or leak keys; archive/script safety follows INT-11.

Use three fixed prompts and controlled real tool path; live ceiling one fresh install
plus one update per owned host profile. Account, organization sharing rights, API
billing/runtime and supported skill version remain blockers until observed. No skill
ZIP, API skill, Code configuration or organization policy is created/changed here.

Claude Code plugin distribution is INT-20; next-session priority is its local-only
packaging/skill slice with#24, not API/remote foundations. Current task only documents.
