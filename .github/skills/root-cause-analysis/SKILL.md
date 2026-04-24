---
name: root-cause-analysis
description: "Evidence gathering and hypothesis ranking workflow for debugging pipeline failures and bugs. Use when investigating why something broke."
---

# Root Cause Analysis Workflow

This skill defines the systematic evidence-gathering process for root cause analysis.

## Evidence Gathering Strategy

### For Pipeline Failures

**Step 1: Pipeline overview**
```
get_pipeline(project_id, pipeline_id=<id>)
```
Record: status, ref, sha, created_at, failure_reason

**Step 2: Identify failed jobs**
```
list_pipeline_jobs(project_id, pipeline_id=<id>)
```
Filter for jobs with `status: "failed"`.

**Step 3: Extract error messages from failed jobs**
```
get_pipeline_job_output(project_id, job_id=<id>, page=1)
```
Search output for these error patterns (in order of priority):
1. Lines containing `Error:`, `FATAL:`, `FAILED`, `Exception`
2. Lines containing `Traceback`, `at ` (stack trace frames)
3. Lines containing `exit code`, `signal`, `OOM`, `timeout`
4. Lines containing `assert`, `expect`, `should` (test failures)
5. Dependency errors: `npm ERR!`, `pip install`, `ModuleNotFoundError`

**Step 4: Get recent commits on the branch**
```
list_commits(project_id, ref_name="<branch>", per_page=10)
```

**Step 5: Analyze suspicious commits**
Commits are "suspicious" if they:
- Modified files referenced in the error message
- Changed CI configuration (`.gitlab-ci.yml`, `Dockerfile`)
- Updated dependencies (`package.json`, `requirements.txt`, `Gemfile`)
- Were authored close to the failure time

For each suspicious commit:
```
get_commit_diff(project_id, sha="<sha>")
```

**Step 6: Search for historical precedent**
```
list_issues(project_id, labels="bug", state="all", per_page=20, scope="all")
```
Look for issues with similar error messages or affected components.

### For Bug Issues

**Step 1: Get issue details**
```
get_issue(project_id, issue_iid=<iid>)
```

**Step 2: Get related issues**
```
list_issue_links(project_id, issue_iid=<iid>)
```

**Step 3: Find recent MRs affecting the area**
```
list_merge_requests(project_id, state="merged", per_page=10)
```
Check which MRs modified files in the affected component.

**Step 4: Check pipeline status on main branch**
```
list_pipelines(project_id, ref="main", per_page=5)
```

## Evidence Classification

| Type | Definition | Reliability |
|------|-----------|-------------|
| **Direct** | Error message or stack trace explicitly identifies the cause | ⭐⭐⭐ High |
| **Correlational** | A code change coincides with failure onset | ⭐⭐ Medium |
| **Circumstantial** | Similar pattern seen in past issues | ⭐ Low |

## Hypothesis Construction Rules

1. Each hypothesis must reference at least one piece of evidence
2. Rank by evidence strength: direct > correlational > circumstantial
3. Maximum 3 hypotheses — if more, merge the weakest
4. "Insufficient evidence" is a valid conclusion — state what additional data would help
5. For each hypothesis, provide: evidence chain, explanation, recommended action
6. Distinguish between "likely cause" and "confirmed cause"

## Common Failure Patterns

| Pattern | Indicators | Usual Cause |
|---------|-----------|-------------|
| **Dependency failure** | `npm ERR!`, `pip install failed` | Package registry down, version conflict |
| **Test regression** | `AssertionError`, `expected X got Y` | Code change broke existing behavior |
| **Build failure** | `SyntaxError`, `TypeError`, compile errors | Typo, missing import, type mismatch |
| **Timeout** | `Job exceeded time limit` | Performance regression, infinite loop |
| **OOM** | `Out of memory`, `killed` | Memory leak, large data processing |
| **Config error** | `ENV not set`, `file not found` | Missing env var, wrong path |
| **Flaky test** | Same test fails intermittently | Race condition, external dependency |
