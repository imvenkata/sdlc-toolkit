---
description: "Run a token-efficient local code review of staged, unstaged, or current-branch changes."
agent: code-review
---

Use the `code-review` agent to review the local changes. Default to Quick mode unless I explicitly ask for Standard or Deep.

Focus on P1/P2 correctness, security, regression, data loss, compatibility, and rollback issues. Do not edit files. Use the shared output format from `.github/skills/code-review/SKILL.md`.
