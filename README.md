# Claude Development Workflow

Shared development patterns, ADR indexes, and workflow skills for Claude Code projects.

## Setup

### Add to Project
```bash
cd your-project
git submodule add <repo-url> .claude-workflow
```

### Enable Skills
After adding submodule, configure `.claude/settings.json`:
```json
{
  "skills": {
    "context": { "enabled": true, "source": "../.claude-workflow/skills/context.skill.md" },
    "reflect": { "enabled": true, "source": "../.claude-workflow/skills/reflect.skill.md" },
    "refine": { "enabled": true, "source": "../.claude-workflow/skills/refine.skill.md" }
  }
}
```

### Project Memory Structure
Create in your project:
```
memory/
├── patterns/draft/
├── patterns/active/
├── sessions/
└── state/workflow-state.md
```

## Workflow

```
/context → Implement → /reflect → (when triggered) → /refine
```

1. **Pre-implementation**: Run `/context` to load relevant ADRs and patterns
2. **Implementation**: Follow loaded guidance, write tests (T1)
3. **Post-implementation**: Run `/reflect` to capture learnings
4. **Refinement**: Run `/refine` when triggers met (5 drafts OR milestone OR 2 weeks)

## Structure

```
indexes/          Token-optimized lookups
patterns/         Implementation guidance (draft→active→promoted)
skills/           Skill definitions
hooks/            Pre/post implementation prompts
templates/        File templates
```

## Skills

| Skill | Purpose |
|-------|---------|
| `/context` | Load relevant ADRs/patterns before implementation |
| `/reflect` | Capture learnings after implementation |
| `/refine` | Process accumulated patterns |

## Updates

```bash
git submodule update --remote
```
