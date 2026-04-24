# Sprint Health Report Template

Use this template to structure sprint intelligence output. All metrics must show inputs and formulas.

---

## Sprint Overview

| Field | Value |
|-------|-------|
| **Milestone** | `[title]` |
| **Period** | `[start_date]` → `[due_date]` |
| **Sprint Duration** | `[N]` days |
| **Days Elapsed** | `[N]` days |
| **Days Remaining** | `[N]` days |
| **Health** | `🟢 On Track` / `🟡 At Risk` / `🔴 Off Track` |

---

## Key Metrics

| Metric | Value | Derivation |
|--------|-------|------------|
| **Completion Rate** | `[X]%` | `[closed]/[total]` issues × 100 |
| **MR Merge Rate** | `[X]%` | `[merged]/[total]` MRs × 100 |
| **Open MRs Pending** | `[N]` | MRs in state `opened` |
| **Active Blockers** | `[N]` | Issues with `blocked` label, state `opened` |
| **Scope Creep** | `[N]` items | Issues created after `[start_date]` |
| **At-Risk Items** | `[N]` | Open issues with no linked MR |
| **Daily Velocity Needed** | `[X]` issues/day | `[open_issues]/[days_remaining]` |
| **Actual Daily Velocity** | `[X]` issues/day | `[closed_issues]/[days_elapsed]` |

---

## Issue Breakdown

| Status | Count | Percentage | Visual |
|--------|-------|------------|--------|
| ✅ Closed | `[N]` | `[X]%` | `████████░░` |
| 🔄 Open (Active) | `[N]` | `[X]%` | `██░░░░░░░░` |
| 🚫 Blocked | `[N]` | `[X]%` | `█░░░░░░░░░` |
| **Total** | `[N]` | 100% | |

---

## Blockers & Risks

### Active Blockers
| Issue | Title | Assignee | Days Blocked | Impact |
|-------|-------|----------|-------------|--------|
| `#[iid]` | `[title]` | `@[user]` | `[N]` | `[what it blocks]` |

### At-Risk Items (Open, No Implementation Started)
| Issue | Title | Assignee | Priority |
|-------|-------|----------|----------|
| `#[iid]` | `[title]` | `@[user]` / Unassigned | `[label]` |

---

## MR Status

| MR | Title | Author | Status | Age (days) |
|----|-------|--------|--------|------------|
| `![iid]` | `[title]` | `@[author]` | `Merged` ✅ / `Open` 🔄 / `Draft` 📝 | `[N]` |

---

## Team Workload

| Assignee | Open | Closed | Total | Completion |
|----------|------|--------|-------|------------|
| `@[user1]` | `[N]` | `[N]` | `[N]` | `[X]%` |
| `@[user2]` | `[N]` | `[N]` | `[N]` | `[X]%` |
| Unassigned | `[N]` | — | `[N]` | — |

---

## Health Assessment Rationale

```
Completion Rate: [X]% [✓/✗ threshold: 70%]
Blockers:        [N]  [✓/✗ threshold: 0]
Days Remaining:  [N]  [context]
Velocity Gap:    [actual] vs [needed] issues/day

→ Health: [result with explanation]
```

---

## Recommendations

| # | Recommendation | Based On | Priority |
|---|---------------|----------|----------|
| 1 | `[specific action]` | `[metric or finding]` | 🔴/🟡/🟢 |
| 2 | `[specific action]` | `[metric or finding]` | 🔴/🟡/🟢 |
| 3 | `[specific action]` | `[metric or finding]` | 🔴/🟡/🟢 |
