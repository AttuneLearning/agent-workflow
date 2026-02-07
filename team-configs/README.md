# Team Configs

Reusable team configuration files shared across repos via the `.claude-workflow` submodule.

## Active Configs

| File | Purpose | Model |
|------|---------|-------|
| `code-reviewer-config.json` | QA/Architect code gate for /develop Phases 3-5 | Opus 4.6 |
| `agent-team-roles.json` | Agent team role definitions (lead, implementer, tester, researcher) | Opus 4.6 lead + Sonnet 4.5 teammates |
| `agent-team-hooks-guide.md` | Hook setup documentation for agent team quality gates | N/A (docs) |

## Project-Level Files (`.claude/`)

These files live in each project repo (not in the submodule) because they contain project-specific paths or settings:

| File | Purpose | Notes |
|------|---------|-------|
| `settings.json` | Project settings: permissions, plugins, env, hooks | Enables agent teams + hook wiring |
| `hooks/task-completed.sh` | TaskCompleted quality gate hook | Portable via team detection from cwd |
| `hooks/teammate-idle.sh` | TeammateIdle quality gate hook | Portable via team detection from cwd |
| `skills/develop/SKILL.md` | Full /develop skill (project-specific version) | References submodule configs |
| `skills/create-adr/SKILL.md` | ADR creation skill | Project-specific |
| `skills/traverse-architecture/SKILL.md` | Architecture analysis skill | Project-specific |
| `commands/` | Symlinks to `.claude-workflow/skills/` | Connects submodule skills to project |

## Learned Team Configs (`memory/team-configs/`)

Project-specific directory storing team compositions learned from Phase 4 reviews:

| File | Purpose |
|------|---------|
| `_template.json` | Template for new learned config entries |
| `{issue-type}--{qualifier}.json` | Learned configs (one per significant review) |
| `index.md` | Directory overview and lookup strategy |

Phase 1.5 (Team Selection) reads these to match past effective configs to new issues.
Phase 4 (Documentation) promotes successful configs here when effectiveness is "excellent" or "good".

## Legacy Files (`.claude/archive/`)

Older team configs archived from `.claude/`. Superseded by the agent team roles + preset system:

| File | Status |
|------|--------|
| `team-config.json` | Superseded by agent-team-roles.json |
| `team-config.backup.json` | Archived |
| `team-config.old.json` | Archived |
| `team-config-ui-auth.json` | Archived (covered by presets) |
| `team-config-learning-unit-ui.json` | Archived (covered by presets) |
| `bug-fix-team-config.json` | Archived (covered by bugFix pattern) |
