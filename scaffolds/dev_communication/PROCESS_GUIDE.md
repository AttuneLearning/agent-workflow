# Dev Communication Process Guide

A complete guide to inter-team communication, issue tracking, and architecture decision management.

---

## Overview

The dev communication system connects three workflows:

```
Issues → Messages → Architecture Suggestions → ADRs
```

**Core principle:** Messages cross team boundaries. Issues stay local. Each team triages its own inbound messages and creates its own issues.

See `.claude-workflow/teams/protocol.yaml` for the universal communication protocol.

---

## Directory Structure

```
dev_communication/
├── {team}/                      # Per-team workspace
│   ├── definition.yaml          # Team identity, responsibilities, stack
│   ├── status.md                # Current focus and blockers
│   ├── inbox/                   # Messages TO this team
│   └── issues/                  # Issue tracking
│       ├── queue/               # Ready to work
│       ├── active/              # In progress
│       └── completed/           # Done
│
├── shared/                      # Cross-team resources
│   ├── registry.yaml            # Active teams in this project
│   ├── dependencies.md          # Cross-team blockers
│   ├── architecture/            # ADRs, suggestions, gaps
│   ├── guidance/                # Development guidelines
│   ├── specs/                   # Feature specifications
│   ├── plans/                   # Planning documents
│   └── contracts/               # API endpoint contracts
│
├── templates/                   # Message and issue templates
├── archive/                     # Completed message threads
├── index.md                     # Issue tracking dashboard
└── PROCESS_GUIDE.md             # This document
```

---

## Issue Management

Issues track discrete work items for each team.

### Issue Lifecycle

```
queue/          →        active/         →       completed/
   │                        │                        │
   │ Create                 │ Start work             │ Finish work
   ▼                        ▼                        ▼
┌──────────┐          ┌──────────┐           ┌──────────┐
│ Waiting  │    →     │ In Work  │     →     │   Done   │
└──────────┘          └──────────┘           └──────────┘
```

### Creating an Issue

Use `/comms issue` or manually create a file:

**Location:** `{team}/issues/queue/`

**Filename:** `{TEAM}-ISS-{NNN}_{brief_description}.md`

**Template:** `templates/issue-template.md`

**Important:** Only create issues in **your own** team's queue. To request work from another team, send a message to their inbox.

### Moving Issues

| Action | File Move |
|--------|-----------|
| Start work | `queue/` → `active/` |
| Complete | `active/` → `completed/` |

---

## Cross-Team Messaging

Messages enable async communication between teams.

### Message Flow

```
Team A                                    Team B
──────                                    ──────
              {team_b}/inbox/
Sends ──────────────────────────────► Receives + triages

              {team_a}/inbox/
Receives ◄────────────────────────── Sends
```

### When to Send Messages

| Scenario | Action |
|----------|--------|
| Need work from other team | Send request → They triage and create issue |
| Completed cross-team work | Send notification |
| Question about their code/API | Send inquiry |
| Found bug in their code | Send bug report with evidence |
| New or changed API contracts | Send contract proposal |

### Sending a Message

**Location:** `{recipient_team}/inbox/`

**Filename:** `YYYY-MM-DD_{subject_slug}.md`

**Template:** `templates/message-request.md`

### Processing Incoming Messages

When you receive a message:

1. **Request** → Triage and create a local issue if accepted
2. **Bug report** → Verify and create a local issue if confirmed
3. **Response** → Update the related issue
4. **Info** → Acknowledge and archive

Archive processed messages to `archive/`.

---

## Architecture Decisions

### The Pipeline

```
Trigger           →    Suggestion    →    Review    →    ADR
(work completed)       (draft idea)      (approve)      (formal record)
```

### Creating a Suggestion

Use `/adr suggest [topic]` or manually create in `shared/architecture/suggestions/`.

### Formal ADRs

**Location:** `shared/architecture/decisions/`

**Format:** `ADR-{DOMAIN}-{NNN}-{TITLE}.md`

---

## Session Protocol

**On Session Start:**
1. `/comms` — Check inbox and pending issues
2. `/adr` — Check architecture status

**During Work:**
- Move issues through lifecycle
- Send messages for cross-team requests
- Define contracts before implementation

**On Session End:**
1. Update team status file (`{team}/status.md`)
2. New pattern? → `/adr suggest`
3. Affects other team? → `/comms send`
4. Ensure all messages are processed

---

## Quick Reference

### Commands

| Command | Description |
|---------|-------------|
| `/comms` | Check inbox and pending issues |
| `/comms send` | Send message to other team |
| `/comms issue` | Create new issue |
| `/comms status` | Update team status |
| `/comms move ISS-XXX {stage}` | Move issue (active/completed) |
| `/adr` | Show architecture status |
| `/adr suggest [topic]` | Create architecture suggestion |

### Priority Levels

| Priority | Response Time | Use When |
|----------|---------------|----------|
| Critical | Immediate | Blocking production/other team |
| High | Same session | Important, time-sensitive |
| Medium | Next session | Normal priority |
| Low | When convenient | Nice to have |
