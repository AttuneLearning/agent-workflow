# Agent Workflow

Unified workflow package for multi-agent coordination.

## Layout

- `claude-workflow/` - Claude command/skill workflow assets
- `codex-workflow/` - Codex skill pack + installer
- `agent-coord-setup.sh` - Unified setup/installation entrypoint

## Recommended Usage (from consuming repo root)

```bash
# explicit team
./agent-coord-setup.sh --team backend

# auto-detect team from dev_communication definitions
./agent-coord-setup.sh
```

## Legacy Compatibility

Consuming repos can keep compatibility symlinks:

- `.claude-workflow -> agent-workflow/claude-workflow`
- `.codex-workflow -> agent-workflow/codex-workflow`
- `agent-coord-setup.sh -> agent-workflow/agent-coord-setup.sh`
