---
name: code-review
description: Shared policy for token-efficient local and GitLab MR code reviews. Use for code-review and code-review-pull agents.
---

# Code Review Policy

Review only issues introduced or worsened by the current diff. Prefer correctness, security, data loss, privacy, compatibility, concurrency, and rollback safety over style.

## Severity

- `P1`: likely production breakage, security/privacy exposure, data loss, migration/rollback blocker, or major requirement miss.
- `P2`: should fix before merge; real bug, important missing edge case, compatibility issue, or meaningful maintainability risk.
- `Nit`: minor but useful; cap nits by mode.
- `Pre-existing`: real issue not introduced by this change; mention only if the MR makes it easier to see or worsens it.

Verdict:

- `Blocked`: review could not complete, or at least one P1 exists.
- `Needs Work`: one or more P2 findings and no P1.
- `Pass`: no P1/P2 findings.

## Modes And Budgets

| Mode | Default Use | Budget | Nits | Subagents |
|------|-------------|--------|------|-----------|
| Quick | local review, small MR, hotfix | 8 files or 600 changed lines | max 3 | only for security-sensitive changes |
| Standard | normal MR review | 20 files or 1,500 changed lines | max 5 | risk-gated |
| Deep | explicit request only | best effort, still skip low-value files | max 5 | allowed when useful |

If a budget is exceeded, review highest-risk files first and list skipped files in `Not Reviewed`.

## Skip Rules

Skip unless explicitly requested:

- generated code and generated directories
- lock files and dependency vendor trees
- build output, cache directories, minified files, source maps
- binaries, archives, media, fonts, office documents
- bot-only dependency bumps when no lock or config logic changed
- pure formatting churn already enforced by tooling

## Risk Triggers

Escalate attention or call `review-security` for changes involving:

- auth, permissions, policies, middleware, sessions, tokens
- API routes, controllers, request parsing, serialization
- database models, migrations, queries, tenant scoping
- secrets, config, environment variables, CI/CD, deployment
- dependencies, package manifests, network clients, TLS/CORS
- concurrency, queues, background jobs, caches, idempotency
- public interfaces, schemas, SDKs, events, webhooks

Call `review-requirements` only when acceptance criteria or explicit requirements are available.

## Context Packing

Start with file list and stats. Fetch/read full diffs only for reviewable files within budget. Read surrounding source only to verify a candidate finding. Do not load whole files or whole repositories for curiosity.

Use deterministic signals first when available: CI status, failing jobs, test output, linters, type checks. Summarize those signals; do not paste long logs.

## Verification Bar

Before reporting a finding:

1. Confirm the issue is introduced or worsened by this diff.
2. Confirm the changed code path can plausibly execute.
3. Cite a file and line, or explicitly state why line evidence is unavailable.
4. Remove findings based only on naming, style, or weak inference.
5. Downgrade uncertain findings to `Unable to verify` or omit them.

## Final Output

Use this for chat output and MR summary comments. Start with exactly one marker.

- Local review marker:
  `<!-- ai-review:code-review:v1 project="local" head="<sha|local>" mode="<quick|standard|deep>" -->`
- GitLab MR marker:
  `<!-- ai-review:code-review-pull:v1 project="<project>" mr="!<iid>" head="<sha>" mode="<quick|standard|deep>" -->`

Finding IDs:

- Number findings by severity in report order: `P1-1`, `P1-2`, `P2-1`, `P2-2`, `NIT-1`.
- Use the ID in the heading or nit bullet so follow-up commands can reference it.
- For GitLab MR reviews, include an action ledger. The ledger is the compact state used for same-session follow-up, so keep it accurate.
- For local reviews, omit the action ledger unless the user explicitly wants a tracking table.

```md
<!-- Insert the local or GitLab MR marker from above here. -->

# AI Code Review - <Mode>

Verdict: <Pass | Needs Work | Blocked>
Confidence: <High | Medium | Low>
Scope: <N> files changed, <M> reviewed, <K> skipped

## Findings

### P1-1 - <short title>
File: `<path>:<line>`
Issue: <specific failure mode>
Impact: <why this matters>
Evidence: <short diff/source evidence>
Fix: <concrete fix direction>
Confidence: <High|Medium>

### P2-1 - <short title>
...

## Nits
- `NIT-1` `<path>:<line>` - <minor useful note>

## Not Reviewed
- `<path>` - <reason>

## Action Ledger
| ID | Target | Anchor | Status |
|----|--------|--------|--------|
| `SUMMARY` | `!<iid>` | `n/a` | `unposted` |
| `P1-1` | `<path>:<line>` | `<inline-ready|summary-only|no-anchor>` | `unposted` |
| `P2-1` | `<path>:<line>` | `<inline-ready|summary-only|no-anchor>` | `unposted` |

## Verification
- CI: <status or not checked>
- Tests: <available signal or not checked>
- Assumptions: <only if needed>

## Follow-Up
Reply with: `post summary`, `draft P2-1`, `draft all P1/P2`, `post P1-1 inline`, `comment: ...`, `reply to thread <id>: ...`, `resolve thread <id>`, `accept P2-1`, `approve`, `unapprove`, or `no write-back`.

<!-- ai-review-summary: {"p1":0,"p2":1,"nits":2,"reviewed_files":8,"skipped_files":4,"mode":"standard","followup_ready":true} -->
```

Omit empty sections except `Verification`. Keep P1/P2 findings concise. If there are no findings, write `No P1/P2 findings.` under `Findings`. For local reviews, omit `Action Ledger` and `Follow-Up` unless explicitly requested.

## Inline Comment Format

```md
**P1-1: <short title>**

<one-sentence issue>

Impact: <why this matters>
Fix: <specific correction>

Confidence: <High|Medium>
```
