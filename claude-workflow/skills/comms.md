---
name: comms
description: Manage inter-team communication, issues, and coordination
argument-hint: "[check|send|issue|status|move|archive]"
---

# Dev Communication Skill

Manage inter-team communication, issues, and coordination.

## Usage

```
/comms [action] [options]
```

## Actions

Based on the user's request or argument, perform one of these actions:

---

### 1. CHECK (default if no action specified)

Check inbox, pending issues, and team status.

**Trigger:** `/comms`, `/comms check`, "check messages", "any updates?"

**Steps:**
1. List files in `dev_communication/backend/inbox/` (API team's inbox — messages from UI)
2. List files in `dev_communication/backend/issues/queue/`
3. List files in `dev_communication/backend/issues/active/`
4. List files in `dev_communication/frontend/inbox/` (UI team's inbox — messages from API)
5. List files in `dev_communication/frontend/issues/queue/`
6. List files in `dev_communication/frontend/issues/active/`

**Output format:**
```
## Comms Status

### Backend Inbox (backend/inbox/)
- [filename] - [first line/subject]
- (or "No pending messages")

### Backend Issue Queue (backend/issues/queue/)
- [ISS-xxx] - [title]
- (or "No pending issues")

### Backend Active Issues (backend/issues/active/)
- [ISS-xxx] - [title] - [status]
- (or "No active issues")

### Frontend Inbox (frontend/inbox/)
- [filename] - [first line/subject]
- (or "No pending messages")

### Frontend Issue Queue (frontend/issues/queue/)
- [ISS-xxx] - [title]
- (or "No pending issues")

### Frontend Active Issues (frontend/issues/active/)
- [ISS-xxx] - [title] - [status]
- (or "No active issues")
```

---

### 2. SEND

Send a message to the other team.

**Trigger:** `/comms send`, "send message to {team}", "notify {team} team"

**Steps:**
1. Ask for message type: Request or Response
2. Ask for priority: Critical, High, Medium, Low
3. Ask for subject
4. Ask for content (or let user provide)
5. Use template from `dev_communication/templates/`
6. Generate filename: `YYYY-MM-DD_{subject_slug}.md`
7. Save to `dev_communication/frontend/inbox/` (if sending to UI) or `dev_communication/backend/inbox/` (if sending to API)
8. Confirm sent

**If responding to a message:**
1. Ask which message this responds to
2. Use response template
3. Include `In-Response-To:` field
4. Optionally move original + response to `archive/`

---

### 3. ISSUE

Create a new issue.

**Trigger:** `/comms issue`, "create issue", "new {team} issue"

**Steps:**
1. Scan `dev_communication/backend/issues/` and `dev_communication/frontend/issues/` to determine next issue number
2. Ask for: title, priority, description, requirements
3. Use template from `dev_communication/templates/issue-template.md`
4. Generate filename: `{TEAM}-ISS-{NNN}_{title_slug}.md`
5. Save to `dev_communication/backend/issues/queue/` (API issues) or `dev_communication/frontend/issues/queue/` (UI issues)
6. Confirm created

**For cross-team issues:**
1. Also create in other team's queue if their work needed
2. Link with `Related:` field
3. Send notification message to the other team's inbox

---

### 4. STATUS

Update team status.

**Trigger:** `/comms status`, "update status", "set focus"

**Steps:**
1. Review current active issues in `dev_communication/backend/issues/active/` and `dev_communication/frontend/issues/active/`
2. Ask what to update:
   - Current focus
   - Active issues
   - Blockers
   - Notes
3. Confirm updated

---

### 5. MOVE

Move an issue through lifecycle.

**Trigger:** `/comms move ISS-xxx`, "move issue to active", "complete ISS-xxx"

**Steps:**
1. Find the issue file
2. Ask target status: queue, active, completed
3. Update status field in the issue
4. Move file to appropriate folder
5. If completing:
   - Ask for completion notes
   - Update completion section
   - Set `Status: COMPLETE` in the issue file
   - Move the issue file into `issues/completed/` in the same action
   - If cross-team, ask if response message needed
6. Confirm moved

**Completion rule (mandatory):**
- Completed issues must not remain in `queue/` or `active/`.
- Completion is only valid after both status update and move to `completed/`.

---

### 6. ARCHIVE

Archive completed message threads.

**Trigger:** `/comms archive`, "archive messages"

**Steps:**
1. List messages in `dev_communication/backend/inbox/` and `dev_communication/frontend/inbox/`
2. Ask which thread to archive (or auto-detect completed)
3. Create folder: `dev_communication/archive/YYYY-MM-DD_{thread_subject}/`
4. Move related messages to archive folder
5. Confirm archived

---

## File Locations

```
dev_communication/
├── backend/
│   ├── inbox/                    # API team's inbox (messages from UI team)
│   └── issues/
│       ├── queue/                # Pending API issues
│       ├── active/               # In-progress API issues
│       └── completed/            # Completed API issues
├── frontend/
│   ├── inbox/                    # UI team's inbox (messages from API team)
│   │   └── completed/            # Acknowledged/completed messages
│   └── issues/
│       ├── queue/                # Pending UI issues
│       ├── active/               # In-progress UI issues
│       └── completed/            # Completed UI issues
├── shared/
│   ├── architecture/             # ADRs, gaps, suggestions
│   ├── guidance/                 # Development principles, checklists
│   ├── plans/                    # Shared plans
│   └── specs/                    # Feature specs
├── templates/                    # Message and issue templates
└── archive/                      # Archived message threads
```

## Team Context

Determine team from project context (check CLAUDE.md or project name):
- API project (cadencelms_api): team=backend, other-team=frontend
- UI project (cadencelms_ui): team=frontend, other-team=backend

## Auto-Suggestions

After completing work, suggest:
- "This affects {other-team} team. Send a notification? (`/comms send`)"
- "Issue complete. Move to completed? (`/comms move`)"
- "New requirement discovered. Create issue? (`/comms issue`)"
