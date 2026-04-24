---
name: impact-analysis
description: "Dependency mapping and risk classification workflow for assessing the blast radius of code changes. Use when analyzing how a change affects the broader codebase."
---

# Impact Analysis Workflow

This skill defines how to systematically map the impact of code changes across a codebase.

## Change Extraction

From MR diffs, extract these categories of changes:

### Symbol Changes
- **Functions/Methods**: renamed, signature changed, deleted, new
- **Classes/Types**: renamed, interface changed, deleted, new
- **Constants/Exports**: renamed, value changed, deleted, new
- **API Endpoints**: path changed, method changed, request/response schema changed

### File Classification
Classify each changed file by type:
| Type | Patterns | Default Risk |
|------|----------|-------------|
| API Routes | `routes/`, `api/`, `controllers/` | 🔴 Critical |
| Shared Libraries | `shared/`, `lib/`, `common/`, `utils/`, `helpers/` | 🔴 Critical |
| Database | `migrations/`, `models/`, `schema` | 🔴 Critical |
| Auth | `auth/`, `middleware/auth`, `permissions` | 🔴 Critical |
| Config | `.env`, `config/`, `settings` | 🟡 Moderate |
| Service Logic | `services/`, `handlers/`, `workers/` | 🟡 Moderate |
| UI Components | `components/`, `views/`, `pages/` | 🟢 Low |
| Tests | `test/`, `spec/`, `__tests__/` | 🟢 Low |
| Docs | `docs/`, `*.md`, `README` | 🟢 Low |

## Dependency Tracing

### Direct Consumer Search
For each changed exported symbol:
```
search_project_code(project_id, query="<symbol_name>")
```
Filter out:
- The file where the symbol is defined (self-reference)
- Comments and strings (if distinguishable)
- Test files (track separately)

### Directory Analysis (Fallback)
If code search is unavailable:
```
get_repository_tree(project_id, path="<parent_dir>", ref="<branch>")
```
Look for:
- `index.*` files (re-exports)
- Files with similar naming patterns
- Test directories alongside source

### Test Coverage Check
For each changed file `src/foo/bar.py`:
Search for test files:
- `test/foo/test_bar.py`
- `test/foo/bar_test.py`
- `src/foo/__tests__/bar.test.py`
- `spec/foo/bar_spec.py`

```
search_project_code(project_id, query="bar")  // basename search
```
Filter for test directories.

## Conflict Detection

```
list_merge_requests(project_id, state="opened", per_page=10)
```
For each open MR:
```
list_merge_request_changed_files(project_id, mergeRequestIid=<iid>)
```
Compute intersection with current MR's changed files.

Conflict risk levels:
- 🔴 **High**: Same file modified in both MRs (especially same functions)
- 🟡 **Medium**: Files in same directory/module modified
- 🟢 **Low**: No overlap

## Risk Escalation Rules

Always escalate (flag as 🔴 regardless of other factors):
1. Deleted exports/public APIs
2. Changed function signatures on shared code
3. Database schema modifications
4. Authentication/authorization changes
5. Changes to CI/CD pipeline configuration
6. Dependency version major bumps

## Reporting

Group findings by:
1. **Critical risks first** — anything that could break other services/consumers
2. **Conflict alerts** — overlapping open MRs
3. **Coverage gaps** — changed code without tests
4. **Recommendations** — ordered by priority (P0/P1/P2)
