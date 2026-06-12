# SDLC Toolkit — AI Agents for GitLab × GitHub Copilot

A suite of 11 AI-powered agents (7 user-facing + 4 specialist sub-agents) that integrate GitLab (via MCP) with GitHub Copilot to improve developer productivity, code quality, and decision-making across the software development lifecycle.

## Agents

### User-Facing Agents

| Agent | Command | Purpose |
|-------|---------|---------| 
| **Code Review** | `@code-review` | Reviews local staged, unstaged, or branch diffs without GitLab access |
| **Code Review Pull** | `@code-review-pull` | Reviews GitLab MRs with token-efficient incremental MCP context gathering |
| **Pipeline Fixer** | `@pipeline-fixer` | Iteratively diagnoses and fixes CI/CD pipeline failures across all stages |
| **Root Cause Analyzer** | `@root-cause` | Investigates pipeline failures with evidence-based hypothesis ranking |
| **Sprint Intelligence** | `@sprint-intel` | Generates data-driven sprint health reports from milestone data |
| **Impact Analyzer** | `@impact-analysis` | Maps blast radius of changes via dependency tracing |
| **Release Notes** | `@release-notes` | Generates categorized release notes from milestone MRs/issues |

### Specialist Sub-Agents (invoked by orchestrators only)

| Sub-Agent | Orchestrator | Purpose | Model |
|-----------|-------------|---------|-------|
| **Log Analyser** | Pipeline Fixer | Log sanitisation, error extraction, failure classification | `gpt-5-mini` |
| **Fix Generator** | Pipeline Fixer | Minimal fix generation with confidence scoring | `claude-sonnet-4.6` |
| **Review Security** | Code Review / Code Review Pull | Risk-gated security, privacy, auth, and breaking-change review | inherited |
| **Review Requirements** | Code Review / Code Review Pull | Risk-gated acceptance criteria and requirement coverage review | inherited |

## Architecture

```
sdlc-toolkit/
├── .vscode/mcp.json                     # MCP server config (read-write + read-only)
├── .github/
│   ├── copilot-instructions.md          # Global conventions
│   ├── hooks/                           # Safety guardrails
│   │   ├── pre-push-validation.json     # Block pushes to protected branches
│   │   ├── prompt-guard.json            # Detect prompt injection & privilege escalation
│   │   └── session-audit.json           # Compliance audit logging
│   ├── agents/                          # Custom Copilot agents
│   │   ├── pipeline-fixer.agent.md      # ── Orchestrator ──────────────────────┐
│   │   ├── log-analyser.agent.md        #    └─ Sub-agent (log parsing)        │
│   │   ├── fix-generator.agent.md       #    └─ Sub-agent (fix generation)     │
│   │   ├── code-review.agent.md         # ── Local review orchestrator ─────────┤
│   │   ├── code-review-pull.agent.md    # ── GitLab MR review orchestrator ─────┤
│   │   ├── review-security.agent.md     #    └─ Risk-gated sub-agent           │
│   │   ├── review-requirements.agent.md #    └─ Risk-gated sub-agent           │
│   │   ├── root-cause.agent.md          # ── Standalone ────────────────────────┤
│   │   ├── sprint-intel.agent.md        # ── Standalone ────────────────────────┤
│   │   ├── impact-analysis.agent.md     # ── Standalone ────────────────────────┤
│   │   └── release-notes.agent.md       # ── Standalone ────────────────────────┘
│   ├── prompts/                         # Reusable Copilot Chat shortcuts
│   │   ├── code-review.prompt.md
│   │   └── code-review-pull.prompt.md
│   └── skills/                          # Reusable skill modules
│       ├── gitlab-data-fetcher/
│       ├── code-review/
│       ├── gitlab-review/
│       ├── review-state/
│       ├── root-cause-analysis/
│       ├── sprint-analysis/
│       ├── impact-analysis/
│       ├── release-notes-gen/
│       └── pipeline-fixer/
├── prompt-templates/                    # Structured output templates
│   ├── rca-evidence-template.md
│   ├── sprint-report-template.md
│   ├── impact-report-template.md
│   ├── release-notes-template.md
│   └── pipeline-fix-template.md
└── tests/                               # Validation fixtures
    └── pipeline-fixer/
        ├── README.md                    # Validation strategy
        └── fixtures/                    # Golden-path test scenarios
```

### Orchestrator → Sub-Agent Architecture

```mermaid
graph TD
    U["Developer"] --> PF["@pipeline-fixer"]
    U --> CR["@code-review"]
    U --> CPR["@code-review-pull"]
    U --> RC["@root-cause"]
    U --> SI["@sprint-intel"]
    U --> IA["@impact-analysis"]
    U --> RN["@release-notes"]

    PF -->|"logs + CI config"| LA["log-analyser<br/>(gpt-5-mini)"]
    PF -->|"diagnosis + source"| FG["fix-generator<br/>(claude-sonnet-4.6)"]
    LA -->|"diagnosis"| PF
    FG -->|"fix + confidence"| PF

    CR -->|"risk-gated diffs"| RS["review-security"]
    CPR -->|"risk-gated diffs"| RS
    CPR -->|"criteria + diffs"| RR["review-requirements"]
    RS -->|"findings only"| CR
    RS -->|"findings only"| CPR
    RR -->|"requirement gaps"| CPR

    PF -.->|"handoff"| CPR
    PF -.->|"escalation"| RC
```

### Design Principles

- **Zero infrastructure** — everything runs locally via Copilot Chat + MCP
- **Deterministic outputs** — shared review schemas and templates keep findings consistent
- **Evidence-based** — every claim traces to a diff, source line, CI signal, or GitLab MCP response
- **Iterative** — the Pipeline Fixer loops (diagnose → fix → push → verify) up to 3 times
- **Safety first** — write operations require confirmation; hooks block unsafe pushes
- **Cost-aware** — token usage estimated per iteration for budget visibility
- **Auditable** — session audit hooks + machine-readable GitLab notes for compliance

## Prerequisites

1. **VS Code** with GitHub Copilot extension
2. **GitLab Personal Access Token** with `api` scope
3. **Node.js** (for `npx` to run the MCP server)

## Setup

### 1. Set Environment Variables

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_API_URL="https://gitlab.com/api/v4"  # or your self-hosted instance
```

### 2. Open in VS Code

```bash
cd sdlc-toolkit
code .
```

### 3. Verify MCP Server

The `.vscode/mcp.json` is pre-configured with two server entries:
- `gitlab-mcp` — read-write (for pipeline-fixer, code-review-pull)
- `gitlab-readonly` — read-only (for root-cause, sprint-intel, impact-analysis, release-notes)

VS Code will start the GitLab MCP server automatically when you open Copilot Chat.

### 4. Verify Agents

Open Copilot Chat → click the agent picker → you should see all 7 user-facing agents listed. Sub-agents are not shown in the picker.

## Usage Examples

### Pipeline Fixer
```
@pipeline-fixer Fix pipeline #456 in project my-group/my-project
@pipeline-fixer Fix the latest pipeline on branch feature/auth in project my-group/my-project
@pipeline-fixer Diagnose pipeline #456 in project my-group/my-project
@pipeline-fixer Auto-fix pipeline #456 in project my-group/my-project
@pipeline-fixer help
```

### Local Code Review
```
@code-review Quick review current changes
@code-review Review staged changes
@code-review Deep review current branch
```

### GitLab MR Review
```
@code-review-pull Review MR !42 in project my-group/my-project
@code-review-pull Quick review MR !42 in project my-group/my-project
@code-review-pull Deep review MR !42 in project my-group/my-project
@code-review-pull Review MR on branch feature/auth in project my-group/my-project
```

### Root Cause Analysis
```
@root-cause Analyze pipeline #789 in project my-group/my-project
@root-cause Debug issue #67 in project my-group/my-project
```

### Sprint Health
```
@sprint-intel Report on milestone "Sprint 24" in project my-group/my-project
```

### Impact Analysis
```
@impact-analysis Analyze MR !55 in project my-group/my-project
```

### Release Notes
```
@release-notes Generate notes for milestone "v2.5.0" in project my-group/my-project
```

## Safety & Guardrails

The toolkit includes lifecycle hooks (`.github/hooks/`) for enterprise safety:

| Hook | Purpose |
|------|---------|
| `pre-push-validation.json` | Blocks pushes to protected branches in auto-fix mode |
| `prompt-guard.json` | Detects prompt injection and privilege escalation attempts |
| `session-audit.json` | Logs all agent sessions and destructive tool usage for compliance |

## Customization

### Changing Label Conventions
Edit the categorization rules in:
- `.github/skills/release-notes-gen/SKILL.md` — label-to-category mapping
- `.github/skills/sprint-analysis/SKILL.md` — blocker label detection

### Adding New Risk Patterns
Edit `.github/skills/impact-analysis/SKILL.md` to add file path patterns and risk classifications.

### Review Policy
Edit `.github/skills/code-review/SKILL.md` to adjust severity definitions, token budgets, skip rules, final output format, and verifier rules.

### GitLab Review Workflow
Edit `.github/skills/gitlab-review/SKILL.md` to adjust GitLab MCP batching, excluded file patterns, linked issue parsing, and write-back behavior.

### Incremental Review State
Edit `.github/skills/review-state/SKILL.md` to adjust reviewed-SHA memory, duplicate suppression, state markers, and follow-up ledger behavior.

### Pipeline Fixer Patterns
Edit `.github/skills/pipeline-fixer/SKILL.md` to add stage-specific error patterns, fix strategies, and custom log sanitisation patterns for your CI/CD setup.

### Adding Test Fixtures
See `tests/pipeline-fixer/README.md` for the fixture template and validation checklist.

## License

MIT
