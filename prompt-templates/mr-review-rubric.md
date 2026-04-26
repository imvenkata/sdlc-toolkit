# MR Review Scoring Rubric — Enterprise Edition

> **Version**: 3.0.0
>
> This file defines scoring criteria and verdict thresholds ONLY. Detection patterns, security checklists, quality signals, and file classification rules live in `.github/skills/mr-review-workflow/SKILL.md` — the single source of truth.

## Scoring: 7 Dimensions × 5 Points = 35 Total

---

### 1. Requirements Alignment (1-5)

| Score | Criteria |
|-------|----------|
| **5** | Every acceptance criterion from linked issue(s) has a clear, traceable implementation in the diff. No gaps. Full criterion → `file:line` mapping. |
| **4** | All major criteria met. One minor criterion partially addressed. |
| **3** | Most criteria covered. 1-2 minor gaps identified but not blocking. |
| **2** | Several criteria partially met. Notable gaps in implementation. |
| **1** | Major requirements not addressed. MR does not fulfill the issue. |
| **N/A** | No linked issues or no acceptance criteria defined in any linked issue. |

**If N/A:** Write exactly: `Requirements Alignment: N/A — [reason: no linked issues / no acceptance criteria defined]`. Remove this dimension from the total and apply the dynamic N/A adjustment formula.

**Assessment method:**
1. List each acceptance criterion from the linked issue(s) — check description AND discussions
2. For each criterion, find the corresponding code change in the diff
3. Mark as: ✅ Met | ⚠️ Partial | ❌ Missing
4. Cite the evidence: `file:line` or "no corresponding change found"

*The requirements-tracer sub-agent produces the traceability matrix used for scoring this dimension.*

---

### 2. Completeness (1-5)

| Score | Criteria |
|-------|----------|
| **5** | Implementation complete with tests, docs, migrations, error handling, and all supporting artifacts. |
| **4** | Core implementation complete. Minor supporting artifacts present. |
| **3** | Core implementation works but missing some tests or docs. Acceptable for Draft MRs. |
| **2** | Incomplete implementation. Several supporting artifacts missing. |
| **1** | Partial implementation. Core functionality not fully working. |
| **N/A** | MR has 0 changed files, or all changed files were excluded (binary, lock files). |

**If N/A:** Write exactly: `Completeness: N/A — [reason]`. Remove from total.

**Checklist:**
- [ ] Unit/integration tests added or updated for new code paths
- [ ] Documentation updated (if public API or user-facing change)
- [ ] Database migrations included (if schema changed)
- [ ] Error handling implemented for all new failure paths
- [ ] Edge cases considered and handled (null, empty, boundary values)
- [ ] Configuration/environment changes documented
- [ ] CHANGELOG updated (if project convention requires it)
- [ ] New dependencies justified and version-pinned

*The code-quality-reviewer sub-agent produces the completeness assessment used for scoring this dimension.*

---

### 3. Security & Risk (1-5)

| Score | Criteria |
|-------|----------|
| **5** | No security concerns. No breaking changes. Input validated. Auth checked. No sensitive data exposure. |
| **4** | Minor risks identified but properly mitigated in the code. |
| **3** | Some risks present. Partial mitigation. |
| **2** | Notable risks without mitigation. Needs attention before merge. |
| **1** | Critical: security vulnerabilities, data loss potential, secrets exposed, or unguarded breaking changes. |
| **N/A** | MR contains no code changes (e.g. docs-only, label-only). |

**If N/A:** Write exactly: `Security & Risk: N/A — docs-only or non-code change`. Remove from total.

*The security-scanner sub-agent produces the security findings used for scoring this dimension. Refer to SKILL.md § Security Scan Patterns and § Breaking Change Indicators for the authoritative pattern lists.*

---

### 4. Code Quality (1-5)

| Score | Criteria |
|-------|----------|
| **5** | Clean, readable, well-structured. Proper error handling. Good naming. DRY. |
| **4** | Good quality. Minor improvements possible. |
| **3** | Acceptable. Some naming issues or minor redundancy. |
| **2** | Below standard. Poor structure or missing error handling. |
| **1** | Very poor. Hard to read, no error handling, significant redundancy. |
| **N/A** | No reviewable code diffs available (all files binary, excluded, or diff fetch failed). |

**If N/A:** Write exactly: `Code Quality: N/A — [reason]`. Remove from total.

*The code-quality-reviewer sub-agent produces the quality findings used for scoring this dimension. Refer to SKILL.md § Code Quality Signals for the authoritative signal lists.*

---

### 5. Consistency (1-5)

| Score | Criteria |
|-------|----------|
| **5** | Perfectly matches existing codebase patterns, conventions, and architecture. |
| **4** | Follows conventions with minor deviations. |
| **3** | Some inconsistencies with project patterns. |
| **2** | Noticeably different from existing code style. |
| **1** | Completely ignores project conventions. |
| **N/A** | Insufficient existing codebase context to assess conventions (e.g. new project / single file). |

**If N/A:** Write exactly: `Consistency: N/A — [reason]`. Remove from total.

|-------|----------|
| **5** | Pipeline green, all approvals met, no conflicts, branch up to date with target. |
| **4** | Pipeline green, minor approval pending or slightly behind target. |
| **3** | Pipeline green but required approvals missing, OR pipeline has non-blocking (`allow_failure`) failures. |
| **2** | Pipeline failing on non-critical stage, OR significant approval gaps. |
| **1** | Pipeline failing on critical stage (build/test), merge blocked, conflicts present. |
| **N/A** | No pipeline has been run on this MR's branch. |

**If N/A:** Write exactly: `CI/CD Health: N/A — no pipeline found on source branch`. Remove from total.

**Data sources:**
- Pipeline status from `list_pipelines` + `get_pipeline`
- Approval state from `get_merge_request_approval_state`
- Conflict check from `get_merge_request_conflicts`
- Behind count from `get_merge_request` metadata

**Hard rule:** If pipeline is failing on build or test stage, MR cannot score above NEEDS_WORK regardless of other dimensions.

*This dimension is scored directly by the orchestrator using MCP pipeline data.*

---

### 7. Scope & Atomicity (1-5)

| Score | Criteria |
|-------|----------|
| **5** | Focused MR. <15 files changed. Single concern. Clear scope. |
| **4** | 15-25 files. Mostly related with minor scope creep. |
| **3** | 25-40 files. Related but could potentially be split. |
| **2** | 40-60 files. Mixed concerns. Should be split. |
| **1** | >60 files OR clearly unrelated changes bundled together. |

**Scope assessment factors:**
- Total files changed
- Number of directories touched
- Whether changes span multiple domains/services
- Whether the MR title describes a single concern
- Whether splitting would reduce review complexity

*This dimension is scored directly by the orchestrator using file change metadata.*

---

## Verdict Thresholds

### Fixed-Dimension Modes

| Score Range | Verdict | Action |
|-------------|---------|--------|
| **≥ 28/35** (≥80%) | ✅ **PASS** | Ready to merge. Address minor notes as follow-ups. |
| **21-27/35** (60-79%) | 🟡 **NEEDS_WORK** | Address flagged findings before merging. Re-review recommended. |
| **< 21/35** (<60%) | 🔴 **REJECT** | Significant rework needed. Do not merge in current state. |

### Quick Mode (4 dimensions, /20)

| Score Range | Verdict |
|-------------|---------|
| **≥ 16/20** | ✅ **PASS** |
| **12-15/20** | 🟡 **NEEDS_WORK** |
| **< 12/20** | 🔴 **REJECT** |

### Dynamic N/A Adjustment

When any dimension is scored N/A, remove it from the total and apply percentage-based thresholds:

```
adjusted_max = (scored_dimensions × 5)
PASS threshold  = ceiling(adjusted_max × 0.80)
NEEDS_WORK range = ceiling(adjusted_max × 0.60) to (PASS threshold - 1)
REJECT threshold = below ceiling(adjusted_max × 0.60)
```

*Example: 2 dimensions N/A → 5 scored → max = 25. Pass ≥ 20, Needs Work 15-19, Reject < 15.*

---

## Override Rules

These rules take precedence over raw scores:

1. **Pipeline failing on critical stage** (build/test) → maximum verdict is **NEEDS_WORK**
2. **Any 🔴 Critical security finding** → maximum verdict is **NEEDS_WORK**
3. **MR has unresolved blocking threads** → note in report, recommend resolution first
4. **MR has no linked issues** → Requirements Alignment = N/A, adjust total accordingly
