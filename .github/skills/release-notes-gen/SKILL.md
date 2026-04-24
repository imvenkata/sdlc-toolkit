---
name: release-notes-gen
description: "Workflow for generating structured release notes from GitLab milestone data. Use when creating release documentation from merged MRs and resolved issues."
---

# Release Notes Generation Workflow

This skill defines how to generate publication-ready release notes from GitLab milestone data.

## Data Collection

### 1. Find Milestone
```
list_milestones(project_id, search="<version>")
```

### 2. Get Merged MRs
```
get_milestone_merge_requests(project_id, milestone_id=<id>)
```
Filter for `state == "merged"`.

For each MR, get full details if labels aren't in the list response:
```
get_merge_request(project_id, mergeRequestIid=<iid>)
```

### 3. Get Resolved Issues
```
get_milestone_issue(project_id, milestone_id=<id>)
```
Filter for `state == "closed"`.

## Categorization Rules

Map labels to categories (first match wins):

```
Label Match                → Category        → Emoji → Priority
-----------------------------------------------------------------
breaking-change, breaking  → Breaking Changes → ⚠️    → 1 (always first)
security, vulnerability    → Security         → 🔒    → 2
feature, enhancement, new  → Features         → 🚀    → 3
bug, fix, hotfix           → Bug Fixes        → 🐛    → 4
performance, optimization  → Performance      → ⚡    → 5
chore, refactor, tech-debt → Maintenance      → 🔧    → 6
docs, documentation        → Documentation    → 📚    → 7
dependencies, deps         → Dependencies     → 📦    → 8
(no match)                 → Other Changes    → 📋    → 9
```

If an MR has multiple matching labels, use the highest-priority category.

## Entry Format

Each entry follows this format:
```
- **[MR/Issue Title]** (![iid]) — [one-line summary from description or title]
  - Author: @[username]
  - Resolves: #[issue_iid] (if issue is linked)
```

### Title Cleanup Rules
1. Remove conventional commit prefixes: `feat:`, `fix:`, `chore:`, etc.
2. Remove issue references from title: `[#123]`, `(#123)`
3. Capitalize first letter
4. Keep it under 100 characters

### Description Extraction
For the one-line summary:
1. Use the MR title if it's descriptive
2. If the MR description has a "## Summary" or "## What" section, use the first sentence
3. If no good summary exists, use the cleaned title

## Deduplication

If an MR references an issue (via `Closes #N`), and that issue is also in the milestone:
- List the entry once, under the MR
- Add `Resolves: #N` to the entry
- Don't create a separate entry for the issue

## Highlights Section

Select 2-3 items for the highlights:
1. All breaking changes (always highlighted)
2. The feature with the most files changed
3. Any security fix

Write a 2-3 sentence summary combining these highlights.

## Statistics

Compute:
```
Total MRs Merged  = count(merged MRs)
Issues Resolved   = count(closed issues, deduplicated)
Contributors      = count(unique MR authors)
```

## Optional: Post to GitLab

Only with explicit user confirmation:

**As milestone description:**
```
edit_milestone(project_id, milestone_id, description="<notes>")
```

**As GitLab release:**
```
create_release(project_id, tag_name="<tag>", name="<title>", description="<notes>")
```
