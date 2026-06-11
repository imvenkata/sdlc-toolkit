---
name: gitlab-review
description: GitLab MCP workflow for token-efficient merge request code review and confirmed write-back.
---

# GitLab Review Workflow

Use this skill only for `code-review-pull`. It defines how to gather GitLab context and post comments safely.

## Required MCP Flow

1. Resolve MR:
   - `get_merge_request(project_id="<project>", mergeRequestIid=<iid>)`
   - or `get_merge_request(project_id="<project>", branchName="<branch>")`
2. List files before diffs:
   - `list_merge_request_changed_files(project_id="<project>", mergeRequestIid=<iid>, excluded_file_patterns=[...])`
3. Fetch selected diffs in batches:
   - `get_merge_request_file_diff(project_id="<project>", mergeRequestIid=<iid>, file_paths=["a","b","c"])`
   - Batch 3-5 files per call.
4. Gather mode-specific signals:
   - Quick: metadata, changed files, selected diffs.
   - Standard: add latest pipeline summary, approvals, conflicts, linked issue criteria if present.
   - Deep: add MR discussions, issue discussions, failed job excerpts, MR versions, and cross-MR overlap when useful.

Never call full-diff methods first. Use full diff only for very small MRs when the file list proves it is safe.

## Excluded File Patterns

Use these patterns unless the user explicitly requests otherwise:

```json
[
  "(^|/)dist/",
  "(^|/)build/",
  "(^|/)node_modules/",
  "(^|/)vendor/",
  "(^|/)generated/",
  "(^|/)__generated__/",
  ".*\\.lock$",
  "package-lock\\.json$",
  "yarn\\.lock$",
  "pnpm-lock\\.yaml$",
  ".*\\.min\\.(js|css)$",
  ".*\\.map$",
  ".*\\.(png|jpg|jpeg|gif|ico|svg|pdf|zip|tar|gz|mp4|mov|mp3|woff|woff2)$"
]
```

## Linked Issues

Parse issue references from MR description:

- `Closes #123`, `Fixes #123`, `Resolves #123`
- `Related to #123`, `Implements #123`, `See #123`
- GitLab issue URLs ending in `/issues/<iid>`

Fetch issue details only for referenced issues. Extract acceptance criteria from checkbox lists and headings named Acceptance Criteria, Requirements, Expected Behavior, or Definition of Done. Do not infer criteria from title alone.

## CI And Approval Signals

For Standard and Deep:

- Latest pipeline: `list_pipelines(project_id="<project>", ref="<source_branch>", per_page=1)` then `get_pipeline`.
- Failed pipeline: fetch failed jobs only, and only short relevant excerpts if the tool supports job output.
- Approvals: `get_merge_request_approval_state`.
- Conflicts: `get_merge_request_conflicts`.

Summarize CI signals in `Verification`; do not paste logs into the review.

## Follow-Up Mode

After the initial report, stay in the same session and accept review follow-up commands. Use the action ledger from the report as the source of truth so the agent does not refetch full diffs.

Supported commands:

- `post summary`: create one MR summary comment with the final report.
- `draft P2-1`, `draft all P1/P2`: create draft notes for selected findings.
- `publish draft <id>`, `publish drafts`: publish one draft note or all draft notes.
- `post P1-1 inline`: create an inline MR thread for a finding with valid position data.
- `comment: <body>`: create a top-level MR note with the user's exact body.
- `comment on P2-1: <body>`: create a top-level note or inline thread tied to the finding, depending on anchor status.
- `reply to thread <discussion_id>: <body>`: add a discussion note to a known MR discussion.
- `resolve thread <discussion_id>`: resolve a known MR discussion.
- `approve`: approve the MR.
- `unapprove`: withdraw the current user's approval.
- `accept P2-1`: mark acknowledged in chat only; do not mutate GitLab.

If a command is ambiguous, preview the safest chat-only interpretation and ask for clarification. In particular, `accept` does not mean approve, publish, or resolve.

## Preview-Confirm-Execute

Never write before explicit user confirmation after showing a preview.

Every preview must include:

- GitLab action and MCP tool name.
- Target project, MR, finding ID, note ID, draft ID, or discussion ID.
- Exact comment body for any note, draft note, inline thread, or discussion reply.
- Current review verdict and a warning if the action conflicts with that verdict.
- Head SHA from the original review and the latest MR head SHA check.

Before executing any write action:

1. Re-fetch cheap MR metadata with `get_merge_request`.
2. Compare the latest head SHA with the reviewed head SHA.
3. Stop and ask for a fresh review if the head SHA changed.
4. Show the preview and wait for an explicit confirmation such as `confirm`, `post it`, `publish`, `approve`, or `resolve`.

Do not treat vague agreement (`ok`, `looks good`, `accept`) as confirmation for GitLab mutation.

## Allowed Write-Back Actions

After confirmation only:

- Summary comment: `create_note` with the full final report.
- Finding drafts: `create_draft_note` per selected P1/P2 finding.
- Draft publishing: `publish_draft_note` or `bulk_publish_draft_notes`.
- Draft rewrite: `update_draft_note` only for a draft note created or selected in this session.
- Inline finding thread: `create_merge_request_thread` only for high-confidence P1/P2 findings with valid position data.
- User top-level comment: `create_note`.
- Existing thread reply: `create_merge_request_discussion_note`.
- Thread resolution: `resolve_merge_request_thread` only for known discussion IDs.
- MR approval: `approve_merge_request`.
- Approval withdrawal: `unapprove_merge_request`.

Never merge, push files, update MR metadata, update posted comments, delete comments, update issues, close issues, or resolve unknown threads.

## Approval Guardrails

- Approve only after the initial review has completed and the head SHA check passes.
- If verdict is `Pass`, approval may proceed after normal confirmation.
- If verdict is `Needs Work` or `Blocked`, show the finding summary and require explicit override wording, for example `confirm approve despite findings`.
- If CI status is failed or not checked, include that in the preview.
- Do not approve draft MRs unless the user explicitly confirms that they want approval on a draft MR.

## Action Receipts

After a write action, return a compact receipt:

```md
Action: <posted summary | created draft | published drafts | posted inline | replied | resolved thread | approved | unapproved>
Target: `!<iid>` / `<finding_id>` / `<discussion_id>`
GitLab result: <note id/thread id/draft id/status or unavailable>
Head: `<sha>`
Ledger update: <new status>
```

## MR Summary Marker

Every summary comment must start with:

```md
<!-- ai-review:code-review-pull:v1 project="<project>" mr="!<iid>" head="<sha>" mode="<quick|standard|deep>" -->
```

Every summary comment must end with:

```md
<!-- ai-review-summary: {"p1":0,"p2":0,"nits":0,"reviewed_files":0,"skipped_files":0,"mode":"standard","followup_ready":true} -->
```
