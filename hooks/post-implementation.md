---
name: post-implementation
type: advisory
auto_dismiss: 15000
triggers:
  - keywords: [done, complete, finished, implemented]
  - events: [commit, test_pass]
---

# Post-Implementation Hook

Advisory reminder after implementation phase completes.

## Display

```
+--------------------------------------------------+
|  Capture learnings from this implementation?     |
|                                                  |
|  Run `/reflect` to detect patterns and gaps      |
|                                                  |
|  [Reflect]  [Skip]          (auto-dismiss: 15s)  |
+--------------------------------------------------+
```

## Behavior

- **Trigger**: Implementation completion signals
- **Auto-dismiss**: 15 seconds
- **Default action**: Skip (non-blocking)
- **Cooldown**: Until next implementation cycle

## Detection Logic

```
IF (
  (message indicates completion OR commit detected OR tests pass)
  AND files were modified in session
  AND no /reflect in current cycle
)
THEN show advisory
```

## Actions

| Button | Action |
|--------|--------|
| Reflect | Execute `/reflect` on current session |
| Skip | Dismiss, mark cycle as reflected |
| (timeout) | Same as Skip |

## Implementation Cycle

A cycle is defined as:
- Start: First file modification after idle or `/context`
- End: Commit, explicit completion, or 2+ hours idle

## Configuration

```json
{
  "post-implementation": {
    "enabled": true,
    "auto_dismiss": 15000,
    "require_on_commit": false,
    "min_files_changed": 2
  }
}
```
