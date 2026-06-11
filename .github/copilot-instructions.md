# SDLC Toolkit — Global Copilot Instructions

## Project Overview
This repository contains AI-powered SDLC agents that integrate GitLab (via MCP) with GitHub Copilot to improve developer productivity, code quality, and decision-making.

## Architecture
- **Agents** (`.github/agents/`): Custom Copilot agents for specific SDLC workflows
  - **User-facing agents**: `code-review`, `code-review-pull`, `pipeline-fixer`, `root-cause`, `sprint-intel`, `impact-analysis`, `release-notes`
  - **Sub-agents**: Specialist agents invoked by orchestrators (`user-invocable: false`):
    - Code Review / Code Review Pull → `review-security`, `review-requirements`
    - Pipeline Fixer → `log-analyser`, `fix-generator`
- **Skills** (`.github/skills/`): Reusable reference material loaded by agents only when relevant
- **Prompt files** (`.github/prompts/`): Thin shortcuts for repeatable Copilot Chat invocations
- **Templates** (`prompt-templates/`): Structured output templates for non-review SDLC workflows

### Sub-Agent Convention
- Sub-agents receive data from their orchestrator — they do NOT make MCP calls directly
- Sub-agents set `user-invocable: false` and `tools: []` in frontmatter
- Orchestrators declare their sub-agents via `agents:` allowlist and use `tools: ["agent"]`
- Each sub-agent returns compact structured findings that the orchestrator verifies before reporting

### Security Convention
- Job logs and CI output MUST be sanitised before passing to sub-agents — tokens, passwords, and credentials are redacted
- Sanitisation patterns are defined in each skill's reference material (e.g., `pipeline-fixer/SKILL.md § Log Sanitisation Patterns`)
- Reports must note the sanitisation count for auditability

## GitLab MCP Integration
All agents communicate with GitLab through the `@zereight/mcp-gitlab` MCP server configured in `.vscode/mcp.json`. The MCP server exposes 141+ tools across projects, merge requests, issues, pipelines, milestones, and more.

## Key Conventions

### MCP Tool Usage
- Always use `project_id` as a numeric ID or URL-encoded path (e.g., `group%2Fproject`)
- For MR lookups, provide `mergeRequestIid` OR `branchName`, never both
- Use the two-step code review workflow: `list_merge_request_changed_files` → `get_merge_request_file_diff` (batch 3-5 files per call)
- For `list_issues`, default scope is "created by current user" — use `scope: "all"` for broader searches

### Review Agent Boundaries
- `code-review` reviews local diffs only and must not use GitLab MCP or mutate files
- `code-review-pull` reviews GitLab MRs and must ask before posting any MR comments
- Reusable review policy lives in `.github/skills/code-review/SKILL.md`
- GitLab MR workflow details live in `.github/skills/gitlab-review/SKILL.md`

### Output Standards
- Review agents must use the final format in `.github/skills/code-review/SKILL.md`
- Non-review agents must use the relevant templates in `prompt-templates/`
- Every claim or data point must trace back to a specific MCP tool response — no hallucination
- Scores and metrics must show their derivation when a workflow uses scoring
- When in doubt, state uncertainty explicitly rather than inventing information

### Destructive Operations
These MCP tools modify GitLab state — always confirm before executing:
- `create_merge_request_thread` — posts review comments
- `create_note` — posts comments on issues/MRs
- `create_issue` — creates new issues
- `update_issue` — modifies existing issues
- `merge_merge_request` — merges MRs
- `push_files` — commits file changes
