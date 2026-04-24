---
name: sprint-analysis
description: "Metrics computation and risk assessment workflow for sprint/milestone health reporting. Use when analyzing sprint progress from GitLab milestone data."
---

# Sprint Analysis Workflow

This skill defines how to compute sprint metrics and assess sprint health from GitLab milestone data.

## Data Collection Sequence

### 1. Find the Milestone
```
list_milestones(project_id, search="<title>", state="active")
```
If no title given, get all active milestones and let user choose.

### 2. Get All Issues in Milestone
```
get_milestone_issue(project_id, milestone_id=<id>)
```
Categorize each issue:
- **State**: `opened` or `closed`
- **Labels**: extract priority, type, blocked status
- **Assignee**: for workload distribution
- **Weight**: if available, for weighted velocity
- **Created at**: to detect scope creep (created after milestone start)
- **Closed at**: for velocity calculation

### 3. Get All MRs in Milestone
```
get_milestone_merge_requests(project_id, milestone_id=<id>)
```
Categorize each MR:
- **State**: `opened`, `merged`, `closed`
- **Author**: for contributor stats
- **Created at / Merged at**: for throughput calculation

### 4. Get Burndown Data
```
get_milestone_burndown_events(project_id, milestone_id=<id>)
```
This may not be available on all tiers. If unavailable, skip and note in report.

### 5. Get Blocked Issues
```
list_issues(project_id, milestone="<title>", labels="blocked", state="opened", scope="all")
```
Also try: `labels="blocker"`, `labels="impediment"`

## Metrics Formulas

All metrics must show the formula and inputs used.

```
Total Issues         = count(all issues in milestone)
Closed Issues        = count(issues where state == "closed")
Open Issues          = Total - Closed
Completion Rate      = (Closed / Total) × 100

Total MRs            = count(all MRs in milestone)
Merged MRs           = count(MRs where state == "merged")
Open MRs             = count(MRs where state == "opened")
MR Merge Rate        = (Merged / Total MRs) × 100

Blocker Count        = count(issues with "blocked" label, state "opened")

Days Elapsed         = today - milestone.start_date
Days Remaining       = milestone.due_date - today
Sprint Duration      = milestone.due_date - milestone.start_date

Daily Velocity Needed = Open Issues / max(Days Remaining, 1)
Actual Daily Velocity = Closed Issues / max(Days Elapsed, 1)

Scope Creep Count    = count(issues where created_at > milestone.start_date)
At-Risk Items        = count(open issues that have no MR linked in description)
```

## Health Assessment Logic

```
IF Completion Rate >= 70% AND Blocker Count == 0:
    Health = 🟢 On Track

ELSE IF Completion Rate >= 40% OR (Days Remaining > Sprint Duration / 2):
    Health = 🟡 At Risk

ELSE IF Completion Rate < 40% OR Blocker Count > 3 OR
        (Days Remaining < 3 AND Open Issues / Total > 0.3):
    Health = 🔴 Off Track
```

## Workload Distribution

Group issues by assignee:
```
For each unique assignee:
    assigned_total  = count(issues assigned to this person)
    assigned_closed = count(closed issues assigned to this person)
    assigned_open   = count(open issues assigned to this person)
    completion      = (assigned_closed / assigned_total) × 100
```

## Recommendations Engine

Generate recommendations based on data:

| Condition | Recommendation |
|-----------|---------------|
| Blocker Count > 0 | "Unblock [N] issues to maintain velocity" |
| At-Risk Items > 0 | "Create MRs for [N] open issues with no linked implementation" |
| Scope Creep > 20% of original | "Scope has grown by [N] items — consider deferring low-priority additions" |
| MR Merge Rate < 50% | "[N] MRs pending review — allocate review bandwidth" |
| Days Remaining < 3 AND Open > 30% | "Consider moving [N] items to next sprint" |
| One assignee has > 40% of open items | "Workload imbalance — [name] has [N] open items" |
