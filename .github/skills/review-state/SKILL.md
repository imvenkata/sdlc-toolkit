---
name: review-state
description: Incremental GitLab MR review state for code-review-pull. Stores compact reviewed SHA, findings, ledger, and user action memory in MR comments.
---

# Review State

Use this skill only with `code-review-pull`. It lets the agent review only changes since the last posted AI review while avoiding duplicate findings and repeated comments.

## State Source

Find previous state by reading MR notes with `get_merge_request_notes` and selecting the newest note containing:

```md
<!-- ai-review-state:v1
```

If no state marker exists, run a normal full review and set `incremental=false` in the new state.

State is persisted only after explicit user confirmation through `post summary` or `post state`. Never create or update MR notes automatically.

## State Marker

Every posted MR summary comment must include exactly one hidden state marker after the summary footer:

```md
<!-- ai-review-state:v1
{"project":"<project>","mr":"!<iid>","reviewed_head":"<sha>","target_branch":"<branch>","mode":"<quick|standard|deep>","incremental":false,"reviewed_files":["<path>"],"skipped_files":[{"path":"<path>","reason":"<reason>"}],"findings":[{"id":"P2-1","severity":"P2","fingerprint":"<hash>","path":"<path>","line":123,"title":"<short title>","status":"open","anchor":"inline-ready","thread_id":null,"note_id":null}],"actions":[{"target":"SUMMARY","status":"posted","note_id":123}],"supersedes":null}
-->
```

Keep the JSON compact. Do not include full diffs, long evidence, secrets, logs, or source snippets in state.

## Fingerprints

Each P1/P2/Nit finding needs a stable fingerprint so later reviews can identify duplicates.

Fingerprint input:

```text
<severity>|<path>|<normalized title>|<normalized issue>|<changed symbol or nearest function if known>
```

Normalize by lowercasing, trimming whitespace, removing line numbers, and collapsing repeated spaces. Use a short hash of that input. If hashing is unavailable, use the normalized input itself as a `fingerprint_source` and keep it short.

## Incremental Review Flow

1. Resolve MR and capture current head SHA.
2. Fetch MR notes and parse the newest `ai-review-state:v1` marker.
3. If state exists and `reviewed_head` equals current head, do not refetch diffs. Report that the MR is unchanged since the last AI review and offer follow-up actions from the state ledger.
4. If state exists and `reviewed_head` differs from current head:
   - Use `get_branch_diffs` with `from=<reviewed_head>` and `to=<current_head>` when available.
   - If `get_branch_diffs` is unavailable or too large, use `list_merge_request_versions` / `get_merge_request_version` to identify changed files since the prior SHA.
   - Fall back to `list_merge_request_changed_files` plus selected current diffs only when version/compare data is unavailable.
5. Review only new or changed files/hunks within the mode budget.
6. Carry forward previous findings using statuses:
   - `open`: still appears relevant or not rechecked.
   - `fixed`: changed lines or source evidence indicate the issue was corrected.
   - `stale`: file or hunk changed enough that the old finding cannot be anchored confidently.
   - `superseded`: replaced by a new finding with a new ID.
   - `accepted`: user acknowledged in chat.
   - `dismissed`: user explicitly rejected or marked not applicable.
7. Do not repost findings whose fingerprint already exists with status `open`, `accepted`, or `dismissed`.
8. New findings continue numbering after the highest previous ID for each severity.

## Output For Incremental Runs

For incremental runs, add a short line near `Scope`:

```md
Incremental: reviewed changes from `<previous_sha>` to `<current_sha>`
```

Under `Verification`, include:

```md
- Previous AI review: found at `<previous_sha>` / not found
- Duplicate suppression: <N> previous findings carried forward, <M> duplicates suppressed
```

## State Updates After Follow-Up

After a confirmed follow-up action, update the in-chat ledger and include the new state if the user posts another summary/state note.

Action status values:

- `posted`: summary or top-level comment posted.
- `drafted`: draft note created.
- `published`: draft note published.
- `threaded`: inline thread created.
- `replied`: discussion reply posted.
- `resolved`: discussion resolved.
- `approved`: MR approved.
- `unapproved`: approval withdrawn.
- `accepted`: chat-only acknowledgement.
- `dismissed`: chat-only rejection.

Do not update existing posted GitLab notes. Create a new confirmed state-bearing summary or state note instead.
