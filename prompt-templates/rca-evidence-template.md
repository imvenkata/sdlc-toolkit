# Root Cause Analysis — Evidence Report Template

Use this template to structure RCA output. Fill in every section from MCP data.

---

## Failure Summary

| Field | Value |
|-------|-------|
| **Type** | `[Pipeline Failure / Bug / Regression / Test Failure]` |
| **Pipeline** | `#[pipeline_id]` |
| **Branch** | `[ref / branch name]` |
| **Commit** | `[sha_short]` — `[commit title]` |
| **Failed At** | `[created_at timestamp]` |
| **Failed Job(s)** | `[job_name_1], [job_name_2]` |
| **Error Signature** | `[First 200 chars of key error message]` |
| **Last Passing Pipeline** | `#[id]` at `[timestamp]` (if identifiable) |

---

## Evidence Table

Each row must reference a specific MCP tool response. Do not invent evidence.

| # | Source | Tool Used | Evidence | Classification | Relevance |
|---|--------|-----------|----------|---------------|-----------|
| 1 | Job: `[name]` | `get_pipeline_job_output` | `[exact error excerpt]` | Direct | ⭐⭐⭐ |
| 2 | Commit: `[sha_short]` | `get_commit_diff` | `[what changed]` | Correlational | ⭐⭐ |
| 3 | Issue: `#[iid]` | `list_issues` | `[similar past failure]` | Circumstantial | ⭐ |

---

## Hypothesis Ranking

### Hypothesis 1: [Title] — Confidence: `HIGH/MEDIUM/LOW`

**Supporting evidence:** Evidence #[N], #[N]
**Explanation:** [How the evidence connects to this hypothesis]
**Recommended action:**
```
[Specific fix — code snippet, command, or configuration change]
```
**Action type:** `Fix / Rollback / Investigate`

### Hypothesis 2: [Title] — Confidence: `HIGH/MEDIUM/LOW`

**Supporting evidence:** Evidence #[N]
**Explanation:** [...]
**Recommended action:** [...]

### Hypothesis 3: [Title] — Confidence: `HIGH/MEDIUM/LOW`

**Supporting evidence:** Evidence #[N]
**Explanation:** [...]
**Investigation needed:** [What additional data would confirm/deny this]

---

## Recommended Actions

| Priority | Action | Type | Owner |
|----------|--------|------|-------|
| 🔴 P0 — Immediate | `[action]` | Fix / Rollback | `[assignee if known]` |
| 🟡 P1 — Soon | `[action]` | Investigate / Prevent | — |
| 🟢 P2 — Follow-up | `[action]` | Prevent / Document | — |

---

## Related Issues

| Issue | Title | Similarity | Status |
|-------|-------|-----------|--------|
| `#[iid]` | `[title]` | `[how it relates]` | `Open/Closed` |

---

## Timeline

| Time | Event | Source |
|------|-------|--------|
| `[timestamp]` | Last successful pipeline | `list_pipelines` |
| `[timestamp]` | `[Commit/MR that may have caused it]` | `list_commits` |
| `[timestamp]` | Pipeline `#[id]` failed | `get_pipeline` |
| `[timestamp]` | Issue `#[iid]` opened | `get_issue` |

---

## Confidence Assessment

| Factor | Status |
|--------|--------|
| Direct error evidence available | ✅/❌ |
| Causal commit identified | ✅/❌/⚠️ Suspected |
| Historical precedent found | ✅/❌ |
| Fix verified | ✅/❌/⚠️ Untested |
| Overall confidence | `HIGH/MEDIUM/LOW` |
