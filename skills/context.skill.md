---
name: context
trigger: /context
description: Load relevant ADRs and patterns before implementation
auto_trigger: false
---

# Context Loading Skill

Pre-implementation context loading for relevant ADRs and patterns.

## Usage

```
/context                    # Auto-detect work type from conversation
/context new-endpoint       # Explicit work type
/context bug-fix,testing    # Multiple work types
```

## Execution Steps

1. **Detect Work Type**
   - Parse recent messages for keywords
   - Match against `indexes/work-type-index.md`
   - If ambiguous, list detected types and ask

2. **Load Index**
   - Read `indexes/adr-index.md`
   - Read `indexes/pattern-index.md`
   - Filter to matching work types

3. **Load Relevant Files**
   - ADRs: Load only decision section (skip rationale unless requested)
   - Patterns: Load full active patterns for work type
   - Max 3 ADRs, 4 patterns per invocation

4. **Output Format**
   ```
   ## Context for: {work-type}

   ### ADRs
   - **{ID}**: {one-line decision}

   ### Patterns
   - **{name}**: {summary}
     ```{key code snippet}```

   ### Checklist
   - [ ] {pattern checklist items}
   ```

## Work Type Keywords

| Work Type | Keywords |
|-----------|----------|
| new-endpoint | route, endpoint, api, controller, REST |
| new-model | model, schema, collection, mongoose |
| new-feature | feature, implement, add, create |
| bug-fix | fix, bug, issue, broken, error |
| refactor | refactor, clean, improve, optimize |
| auth-change | auth, permission, access, role |
| testing | test, spec, jest, coverage |

## Token Budget

Target: <2000 tokens per invocation
- Index scan: ~200 tokens
- ADR summaries: ~150 tokens each (450 max)
- Pattern loads: ~300 tokens each (1200 max)
