---
description: "Run a token-efficient GitLab merge request review through GitLab MCP."
agent: code-review-pull
---

Use the `code-review-pull` agent to review the GitLab merge request I provide. Default to Standard mode unless I explicitly ask for Quick or Deep.

Fetch MR context through GitLab MCP, load any previous `ai-review-state:v1` marker from MR notes, and run an incremental review when the current head differs from the last reviewed head. List changed files before fetching full MR diffs, batch diff retrieval 3-5 files at a time, and ask before posting anything back to GitLab. Use stable finding IDs and the shared output format from `.github/skills/code-review/SKILL.md`.

After the report, stay in follow-up mode for same-session actions such as posting the summary, posting state, drafting selected findings, posting inline comments, replying to known threads, resolving known threads, approving, or unapproving. Preview every GitLab write action and wait for explicit confirmation before executing.
