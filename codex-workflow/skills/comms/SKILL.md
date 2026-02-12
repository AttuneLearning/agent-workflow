---
name: comms
description: Manage dev_communication inboxes, messages, and issue lifecycle across backend/frontend teams.
---

# Comms Skill

Use this skill when the user asks to check team comms, send a cross-team message, create or move issues, or archive completed message threads.

## Team-awareness (required)

Before running actions, resolve active team defaults from:

1. `.codex-workflow/config/active-team.json` (project-local), else
2. installed pack `config/active-team.json`.

Use `team_profile.default_paths` and `issue_prefix` from that file as defaults.
If no active team config exists, ask the user which team context to use.

## Inputs to resolve

- Action: `check`, `send`, `issue`, `status`, `move`, or `archive`
- Team context: current team (`backend` or `frontend`)
- Target team (for cross-team message requests)

## Actions

### 1. Check (default)

1. List:
   - `dev_communication/backend/inbox/`
   - `dev_communication/backend/issues/queue/`
   - `dev_communication/backend/issues/active/`
   - `dev_communication/frontend/inbox/`
   - `dev_communication/frontend/issues/queue/`
   - `dev_communication/frontend/issues/active/`
2. Summarize pending messages and issue counts.

### 2. Send

1. Collect: target team, subject, priority, content, related issues.
2. Use `dev_communication/templates/message-request.md` (or response template when replying).
3. Save to target inbox:
   - `dev_communication/backend/inbox/` or
   - `dev_communication/frontend/inbox/`
4. Filename format: `YYYY-MM-DD_{subject_slug}.md`.

### 3. Issue

1. Determine next issue number from target team's existing issues.
2. Use `dev_communication/templates/issue-template.md`.
3. Save to target queue:
   - `dev_communication/backend/issues/queue/` for API issues
   - `dev_communication/frontend/issues/queue/` for UI issues
4. Filename format: `{TEAM}-ISS-{NNN}_{title_slug}.md`.

Guardrail:
- Follow team protocol: messages cross team boundaries; issue ownership is team-local unless user explicitly asks to create across teams.

### 4. Status

1. Review active issues for both teams.
2. Update the relevant status file:
   - `dev_communication/backend/status.md`
   - `dev_communication/frontend/status.md`

### 5. Move

1. Locate issue file.
2. Move between `queue/`, `active/`, `completed/`.
3. Update issue status metadata in file body.

### 6. Archive

1. Identify completed thread messages.
2. Create archive folder:
   - `dev_communication/archive/YYYY-MM-DD_{thread_subject}/`
3. Move related message files into archive folder.

## Output expectations

- Always return file paths created/updated/moved.
- For `check`, provide short, scan-friendly status by team.
- For `send` or `issue`, include exact filenames for traceability.
