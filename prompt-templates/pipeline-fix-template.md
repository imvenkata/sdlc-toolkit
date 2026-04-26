# Pipeline Fix Report Template

> **Version**: 3.1.0
>
> This file defines the output template for pipeline fix reports. Error patterns and fix examples live in `.github/skills/pipeline-fixer/SKILL.md` — the single source of truth.

---

## Pipeline Fix Report

| Field | Value |
|-------|-------|
| **Project** | `[project_id]` |
| **Branch** | `[branch]` |
| **Original Pipeline** | `#[pipeline_id]` |
| **Final Status** | `✅ Fixed` / `❌ Not Fixed (after [N] iterations)` |
| **Total Iterations** | `[N]` |
| **Log Sanitisation** | `[N] sensitive values redacted` |

---

## Pipeline Structure

```
[stage_1]: [job_1] (✅/❌), [job_2] (✅/❌)
[stage_2]: [job_3] (✅/❌), [job_4] (⏭️ skipped)
...
```

---

## Iteration History

### Iteration 1

| Field | Value |
|-------|-------|
| **Pipeline** | `#[id]` |
| **Failed Stage** | `[stage]` |
| **Failed Job** | `[job_name]` |
| **Error Category** | `CI Config / Build / Test / Scan / Publish / Deploy / Infrastructure` |
| **Confidence** | `[1-5]/5 [🟢/🟡/🟠/🔴]` |

**Error Extract:**
```
[Exact error lines from job log — max 20 lines, SANITISED]
```

> ⚠️ Log output has been sanitised. [N] sensitive values were redacted before analysis.

**Diagnosis:**
[One paragraph: what caused the failure and why — from log-analyser sub-agent]

**Proposed Fix — Confidence: [N]/5 [emoji]**

| Field | Value |
|-------|-------|
| **Root Cause** | [one sentence] |
| **Category** | CI Config / Source / Dependency / Docker |
| **File** | `[file_path]` |
| **Auto-fix Safe** | Yes (confidence ≥ 4) / No (confidence ≤ 3) |

**Diff:**
```diff
- [old line]
+ [new line]
```

**Why**: [Error → Cause → Fix chain — from fix-generator sub-agent]

**Commit:** `[sha_short]` — `[commit message]`
**Result:** `✅ Passed` / `❌ Failed (different error)` / `❌ Failed (same error)`

---

### Iteration 2
[Same structure as above]

---

### Iteration 3
[Same structure as above]

---

## Final State

### If Fixed ✅
```markdown
## ✅ Pipeline Fixed!

**Passing Pipeline**: #[final_pipeline_id]
**Iterations Required**: [N]
**Total Files Modified**: [N]

### Changes Made
| File | Change Summary | Confidence |
|------|---------------|------------|
| `[file]` | `[what was changed]` | [N]/5 |

### Commits
| SHA | Message |
|-----|---------|
| `[sha]` | `[message]` |

### Next Steps
- Review the fix: `@mr-reviewer Quick review MR ![iid] in project [id]`
```

### If Not Fixed ❌
```markdown
## ❌ Pipeline Not Fixed After [N] Iterations

### Current Failure
| Field | Value |
|-------|-------|
| **Pipeline** | `#[id]` |
| **Stage** | `[stage]` |
| **Job** | `[job]` |
| **Error** | `[summary]` |
| **Last Confidence** | `[N]/5` |

### What Was Tried
| # | Fix | Confidence | Why It Didn't Work |
|---|-----|------------|-------------------|
| 1 | `[fix summary]` | [N]/5 | `[reason]` |
| 2 | `[fix summary]` | [N]/5 | `[reason]` |
| 3 | `[fix summary]` | [N]/5 | `[reason]` |

### Recommendations for Manual Resolution
1. `[specific action]` — `[why this might work]`
2. `[specific action]` — `[why]`
3. `[escalation suggestion]` — `[who/what to escalate to]`

### Deeper Investigation
- Run `@root-cause Analyse pipeline #[id] in project [id]` for deeper root cause analysis

### Useful Context
- CI Config: `.gitlab-ci.yml` on branch `[branch]`
- Last Error Log: Pipeline #[id], Job #[job_id]
- Related Past Issues: #[iid], #[iid]
```

---

## Cascading Failure Tracking

When fixing one stage reveals a new failure in the next stage, track the cascade:

| Iteration | Fixed Stage | New Failure Stage | Confidence | Status |
|-----------|------------|-------------------|------------|--------|
| 1 | `build` | `test` (now runs, previously skipped) | 5/5 | Expected |
| 2 | `test` | `publish` (now runs) | 4/5 | Expected |
| 3 | `publish` | — | 4/5 | ✅ All passing |

*Note: Cascading failures are normal — each fix allows the next stage to run, potentially revealing new issues.*

---

## Review Metadata

| Field | Value |
|-------|-------|
| **Mode** | `[Diagnose/Fix/Auto-fix]` |
| **Model** | `[model used]` |
| **Sub-agents** | `[log-analyser, fix-generator]` |
| **Log lines processed** | `[count]` |
| **Values sanitised** | `[count]` |
| **Estimated tokens** | `[cumulative total across iterations]` |
| **Confidence capped** | `[Yes — capped from X to Y / No]` |
| **Audit note posted** | `[Yes — note #ID / No — reason]` |
| **Agent version** | `3.1.0` |
