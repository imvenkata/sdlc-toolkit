---
name: gitlab-data-fetcher
description: "Reusable patterns for efficiently retrieving data from GitLab via MCP. Use this skill when you need to fetch MRs, issues, pipelines, or repository data with proper batching, pagination, and error handling."
---

# GitLab Data Fetcher — Reusable MCP Patterns

This skill provides standardized patterns for retrieving GitLab data via the `@zereight/mcp-gitlab` MCP server. All SDLC agents should use these patterns for consistency and efficiency.

## Project Identification

The `project_id` parameter accepts:
- **Numeric ID**: `12345`
- **URL-encoded path**: `my-group%2Fmy-project` (encode `/` as `%2F`)

When the user provides a path like `my-group/my-project`, always URL-encode it.

## MR Data Retrieval Pattern

### Step 1: Get MR Overview
```
get_merge_request(project_id="<project>", mergeRequestIid=<iid>)
```
Returns: title, description, state, author, labels, source/target branches, web_url.

### Step 2: Get Changed Files (paths only — lightweight)
```
list_merge_request_changed_files(project_id="<project>", mergeRequestIid=<iid>)
```
Returns: array of file paths. Use `excluded_file_patterns` to filter (e.g., `["*.lock", "*.min.js"]`).

### Step 3: Get File Diffs (batch 3-5 files per call)
```
get_merge_request_file_diff(project_id="<project>", mergeRequestIid=<iid>, file_paths=["a.py", "b.py", "c.py"])
```
**Important**: Always batch 3-5 files per call. Never request all diffs at once for large MRs.

### Step 4: Get Discussions
```
mr_discussions(project_id="<project>", mergeRequestIid=<iid>)
```

## Issue Data Retrieval Pattern

```
get_issue(project_id="<project>", issue_iid=<iid>)
```

For listing issues with filters:
```
list_issues(project_id="<project>", state="opened", labels="bug,critical", milestone="Sprint 1", scope="all")
```
**Default scope is "created by current user"** — always use `scope="all"` for comprehensive queries.

## Pipeline Data Retrieval Pattern

```
get_pipeline(project_id="<project>", pipeline_id=<id>)
list_pipeline_jobs(project_id="<project>", pipeline_id=<id>)
get_pipeline_job_output(project_id="<project>", job_id=<id>, page=1)
```
Job output can be large. Use `page` parameter for pagination. Start with page 1 and work backwards from the end for error messages.

## Repository Data Pattern

```
get_repository_tree(project_id="<project>", path="src/", ref="main", recursive=false)
get_file_contents(project_id="<project>", file_path="path/to/file", ref="main")
```

## Code Search Pattern

```
search_project_code(project_id="<project>", query="function_name")
```
**Requires GitLab Advanced Search or Exact Code Search.** If unavailable, fall back to `get_repository_tree` + `get_file_contents`.

## Pagination

Most list endpoints support:
- `per_page`: items per page (default 20, max 100)
- `page`: page number

For comprehensive data, set `per_page=100` and iterate if needed.

## Error Handling

If an MCP tool returns an error:
1. Report the error to the user with the tool name and parameters
2. Suggest checking: project_id format, permissions, feature availability
3. Continue with available data rather than aborting entirely
