---
name: develop
description: Mandatory development lifecycle - processes issues with full verification
argument-hint: "[issue-id|all|quick <file>]"
---

# Development Lifecycle Skill

Enforces the mandatory development lifecycle for all code changes per ADR-DEV-002.

## Usage

```
/develop                    # Process next issue in queue
/develop UI-ISS-082         # Process specific issue
/develop all                # Process all issues in queue
/develop quick <file>       # Quick mode for trivial changes
```

## Team Detection (Portable)

Determine team from working directory path:
- Path contains `/cadencelms_ui/` → `team=ui`
- Path contains `/cadencelms_api/` → `team=api`

**Inbox pattern:** `dev_communication/messaging/*-to-{team}/`
- UI team reads: `*-to-ui/` (e.g., `api-to-ui/`)
- API team reads: `*-to-api/` (e.g., `ui-to-api/`)

---

## Phase 0: Message Polling & Unblocking (AUTOMATIC)

**Run BEFORE processing any issue and BETWEEN issues when processing multiple.**

### Polling Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    POLLING LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  START: /develop invoked                                    │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────┐                                            │
│  │ Poll Inbox  │◄────────────────────────┐                  │
│  └──────┬──────┘                         │                  │
│         │                                │                  │
│         ▼                                │                  │
│  ┌─────────────┐    new message?    ┌────┴────┐            │
│  │Check Blocked│───────yes─────────►│ Process │            │
│  └──────┬──────┘                    │  Issue  │            │
│         │                           └────┬────┘            │
│         │ no new messages                │                  │
│         ▼                                │                  │
│  ┌─────────────┐                         │                  │
│  │  Timeout?   │                         │                  │
│  │ (20 min)    │                         │                  │
│  └──────┬──────┘                         │                  │
│         │                                │                  │
│    yes  │  no                            │                  │
│         │   └────────────────────────────┘                  │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │    END      │◄─── Issue completed                        │
│  └─────────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Termination Conditions

| Condition | Action |
|-----------|--------|
| Issue development completed | Stop polling, move to Phase 5 |
| 20 minutes no new messages | Stop polling, report timeout |
| All issues in batch completed | Stop polling, final summary |
| User interrupt | Stop polling, store session state |

### Step 0.1: Poll Inbox for New Messages

```
inbox_path = dev_communication/messaging/*-to-{team}/
timeout = 20 minutes of inactivity
```

**Steps:**
1. Record last activity timestamp
2. List all files in inbox directory
3. For each message file:
   - Read the message
   - Check if it's a RESPONSE type (has `In-Response-To:` field)
   - Check if it answers a pending question
   - If new message found: reset inactivity timer
4. Check inactivity timeout (20 minutes since last new message)

### Step 0.2: Check for Blocked Issues

```
blocked_issues = dev_communication/issues/{team}/active/
```

**Steps:**
1. List all files in active issues
2. For each issue, check for `Blocked-By:` or `Status: BLOCKED` fields
3. Build list of blocked issues and their blocking reasons

### Step 0.3: Match Responses to Blocked Issues

**For each new response message:**
1. Extract the `In-Response-To:` reference
2. Find matching blocked issue by:
   - Message thread reference
   - Issue ID mentioned in response
   - Subject/topic match
3. If match found:
   - Update issue status from BLOCKED to IN PROGRESS
   - Add response content to issue notes
   - Log: "Unblocked {issue_id} - received response: {subject}"
   - Reset inactivity timer

### Step 0.4: Report Polling Results

**Output format:**
```
## Message Poll Results

### Polling Status
- Last activity: {timestamp}
- Inactivity: {minutes} min (timeout at 20 min)

### New Messages ({count})
- [filename] - [subject] - [type: Request/Response]

### Unblocked Issues ({count})
- {issue_id} - unblocked by: {message_filename}

### Still Blocked ({count})
- {issue_id} - waiting for: {blocking_reason}
```

### Step 0.5: Check Termination

**Continue polling if:**
- Active issue still in progress AND
- Inactivity < 20 minutes AND
- Blocked issues exist waiting for responses

**Stop polling if:**
- Current issue completed → proceed to next issue or finish
- Inactivity >= 20 minutes → report timeout, proceed with available work
- No blocked issues remain → proceed with development

---

## Lifecycle Phases

**ALL PHASES ARE MANDATORY** (except where noted for quick mode)

---

### Phase 1: Context Loading

**Steps:**
1. Check `/comms` for relevant messages (already done in Phase 0)
   - Review any new messages from `*-to-{team}/` inbox
   - Note messages that affect current work

2. Load relevant context from `/memory`
   - Search `memory/patterns/` for related patterns
   - Search `memory/entities/` for related entities
   - Search `memory/context/` for domain knowledge

3. Identify applicable ADRs based on change type:
   | Change Type | Required ADRs |
   |-------------|---------------|
   | New API endpoint | ADR-API-001, ADR-DEV-001 |
   | New UI component | ADR-UI-001, ADR-DEV-001 |
   | New feature | ADR-DEV-001, domain-specific |
   | Bug fix | ADR-DEV-001 (regression test) |
   | Auth changes | ADR-AUTH-001, ADR-SEC-001 |

4. Read and understand issue requirements
   - Extract acceptance criteria
   - Identify test requirements per ADR-DEV-001

---

### Phase 2: Implementation

**Steps:**
1. Create implementation plan (if complex)
   - Break into subtasks
   - Identify files to modify

2. Write code following patterns and ADRs
   - Follow patterns from `/memory`
   - Follow conventions from applicable ADRs
   - Use existing abstractions

3. Update TypeScript types as needed

---

### Phase 3: Verification (MANDATORY - BLOCKING)

**CANNOT proceed to next phase without ALL checks passing**

**UI Team Commands:**
```bash
# 1. Type check (MUST be 0 errors)
npx tsc --noEmit

# 2. Unit tests for changed code
npx vitest run {changed_test_files}

# 3. Integration tests
npx vitest run --config vitest.integration.config.ts
```

**API Team Commands:**
```bash
# 1. Type check (MUST be 0 errors)
npx tsc --noEmit

# 2. Unit tests
npm run test:unit -- {changed_test_files}

# 3. Integration tests
npm run test:integration
```

**On Failure:**
- Type errors: Fix ALL errors before proceeding
- Test failures: Fix failing tests or write missing tests
- Regressions: Investigate, fix root cause, add regression test

---

### Phase 4: Documentation

**Steps:**
1. Update `/memory` if new pattern discovered
   - Use `/memory` skill to add pattern

2. Create ADR suggestion if architectural decision made
   - Use `/adr suggest`

3. Send `/comms` if cross-team impact
   - Use `/comms send`

4. Update issue with implementation notes (required)

---

### Phase 5: Completion

**Steps:**
1. Verify ALL acceptance criteria are met

2. Move issue to completed
   - Use `/comms move {issue_id} completed`

3. Store session summary for compaction recovery
   - Create `memory/sessions/{date}-{issue-slug}.md` with:
     - Issue ID and title
     - Files created/modified
     - Tests written
     - Patterns used/discovered
     - Pending items (if any)

---

## Quick Mode

For trivial changes only (typos, comments, single-line fixes):

```
/develop quick src/shared/ui/button.tsx
```

**Enabled for:**
- Documentation updates
- Comment changes
- Single-line bug fixes
- Typo corrections

**Skips:**
- Integration tests
- Memory update
- ADR suggestion

**Still requires:**
- Type check (must pass)
- Unit tests (if test file exists)

---

## Error Handling

| Error Type | Action |
|------------|--------|
| Type error | Fix immediately, do not proceed |
| Test failure | Analyze failure, fix code or test, re-run |
| Regression | Investigate, fix root cause, add regression test |
| Context compaction | Store session state before compaction |

---

## Test Requirements by Change Type (from ADR-DEV-001)

| Change Type | Required Tests |
|-------------|----------------|
| Bug fix | Regression test proving fix |
| New endpoint | Integration test |
| New UI component | Unit test for rendering |
| New feature | Integration + happy path |
| Refactor | Existing tests must pass |

---

## File Locations

```
dev_communication/
├── issues/{team}/{queue,active,completed}/  # Team issues
├── messaging/
│   ├── api-to-ui/    # API → UI messages (UI inbox)
│   ├── ui-to-api/    # UI → API messages (API inbox)
│   └── archive/      # Completed threads
└── coordination/
    └── dependencies.md  # Cross-team blockers

memory/
├── patterns/   # Development patterns
├── entities/   # Component/entity docs
├── context/    # Domain knowledge
└── sessions/   # Session summaries

dev_communication/architecture/
├── decisions/  # ADRs
└── gaps/       # Known gaps
```

## Portable Team Detection

**Auto-detect from working directory:**
```
if (cwd contains "cadencelms_ui")  → team = "ui"
if (cwd contains "cadencelms_api") → team = "api"
```

**Derived paths:**
```
inbox      = dev_communication/messaging/*-to-{team}/
outbox     = dev_communication/messaging/{team}-to-*/
issues     = dev_communication/issues/{team}/
```

**Examples:**
| Team | Inbox | Outbox | Issues |
|------|-------|--------|--------|
| ui | `api-to-ui/` | `ui-to-api/` | `issues/ui/` |
| api | `ui-to-api/` | `api-to-ui/` | `issues/api/` |

## References

- **ADR:** `dev_communication/architecture/decisions/ADR-DEV-002-DEVELOPMENT-LIFECYCLE.md`
- **Config:** `memory/prompts/team-configs/development-lifecycle.md`
- **Testing:** `dev_communication/architecture/decisions/ADR-DEV-001-TESTING-STRATEGY.md`
