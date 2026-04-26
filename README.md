# SDLC Toolkit — AI Agents for GitLab × GitHub Copilot

A suite of 11 AI-powered agents (6 user-facing + 5 specialist sub-agents) that integrate GitLab (via MCP) with GitHub Copilot to improve developer productivity, code quality, and decision-making across the software development lifecycle.

## Agents

### User-Facing Agents

| Agent | Command | Purpose |
|-------|---------|---------| 
| **MR Reviewer** | `@mr-reviewer` | Reviews MRs against linked requirements with 5-dimension scoring |
| **Pipeline Fixer** | `@pipeline-fixer` | Iteratively diagnoses and fixes CI/CD pipeline failures across all stages |
| **Root Cause Analyzer** | `@root-cause` | Investigates pipeline failures with evidence-based hypothesis ranking |
| **Sprint Intelligence** | `@sprint-intel` | Generates data-driven sprint health reports from milestone data |
| **Impact Analyzer** | `@impact-analysis` | Maps blast radius of changes via dependency tracing |
| **Release Notes** | `@release-notes` | Generates categorized release notes from milestone MRs/issues |

### Specialist Sub-Agents (invoked by orchestrators only)

| Sub-Agent | Orchestrator | Purpose | Model |
|-----------|-------------|---------|-------|
| **Log Analyser** | Pipeline Fixer | Log sanitisation, error extraction, failure classification | `gpt-4o-mini` |
| **Fix Generator** | Pipeline Fixer | Minimal fix generation with confidence scoring | `claude-sonnet-4.6` |
| **Security Scanner** | MR Reviewer | Security pattern detection in file diffs | `gpt-4o-mini` |
| **Requirements Tracer** | MR Reviewer | Issue acceptance criteria → code traceability | `claude-sonnet-4.6` |
| **Code Quality Reviewer** | MR Reviewer | Quality, consistency, and completeness analysis | `claude-sonnet-4` |

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
│   │   ├── mr-reviewer.agent.md         # ── Orchestrator ──────────────────────┤
│   │   ├── security-scanner.agent.md    #    └─ Sub-agent (security)           │
│   │   ├── requirements-tracer.agent.md #    └─ Sub-agent (requirements)       │
│   │   ├── code-quality-reviewer.agent.md #  └─ Sub-agent (quality)            │
│   │   ├── root-cause.agent.md          # ── Standalone ────────────────────────┤
│   │   ├── sprint-intel.agent.md        # ── Standalone ────────────────────────┤
│   │   ├── impact-analysis.agent.md     # ── Standalone ────────────────────────┤
│   │   └── release-notes.agent.md       # ── Standalone ────────────────────────┘
│   └── skills/                          # Reusable skill modules
│       ├── gitlab-data-fetcher/
│       ├── mr-review-workflow/
│       ├── root-cause-analysis/
│       ├── sprint-analysis/
│       ├── impact-analysis/
│       ├── release-notes-gen/
│       └── pipeline-fixer/
├── prompt-templates/                    # Structured output templates
│   ├── mr-review-rubric.md
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
    U --> MR["@mr-reviewer"]
    U --> RC["@root-cause"]
    U --> SI["@sprint-intel"]
    U --> IA["@impact-analysis"]
    U --> RN["@release-notes"]

    PF -->|"logs + CI config"| LA["log-analyser<br/>(gpt-4o-mini)"]
    PF -->|"diagnosis + source"| FG["fix-generator<br/>(claude-sonnet-4.6)"]
    LA -->|"diagnosis"| PF
    FG -->|"fix + confidence"| PF

    MR -->|"diffs"| SS["security-scanner<br/>(gpt-4o-mini)"]
    MR -->|"issues + diffs"| RT["requirements-tracer<br/>(claude-sonnet-4.6)"]
    MR -->|"diffs + language"| CQ["code-quality-reviewer<br/>(claude-sonnet-4)"]
    SS -->|"findings"| MR
    RT -->|"traceability"| MR
    CQ -->|"quality report"| MR

    PF -.->|"handoff"| MR
    PF -.->|"escalation"| RC
```

### Design Principles

- **Zero infrastructure** — everything runs locally via Copilot Chat + MCP
- **Deterministic outputs** — scoring rubrics, formulas, and templates ensure consistent results
- **Evidence-based** — every claim traces to a specific GitLab MCP tool response
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
- `gitlab` — read-write (for pipeline-fixer, mr-reviewer)
- `gitlab-readonly` — read-only (for root-cause, sprint-intel, impact-analysis, release-notes)

VS Code will start the GitLab MCP server automatically when you open Copilot Chat.

### 4. Verify Agents

Open Copilot Chat → click the agent picker → you should see all 6 user-facing agents listed. Sub-agents are not shown in the picker.

## Usage Examples

### Pipeline Fixer
```
@pipeline-fixer Fix pipeline #456 in project my-group/my-project
@pipeline-fixer Fix the latest pipeline on branch feature/auth in project my-group/my-project
@pipeline-fixer Diagnose pipeline #456 in project my-group/my-project
@pipeline-fixer Auto-fix pipeline #456 in project my-group/my-project
@pipeline-fixer help
```

### MR Review
```
@mr-reviewer Review MR !42 in project my-group/my-project
@mr-reviewer Quick review MR !42 in project my-group/my-project
@mr-reviewer Deep review MR !42 in project my-group/my-project
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

### Adjusting Scoring
Edit `prompt-templates/mr-review-rubric.md` to change score thresholds or add dimensions.

### Pipeline Fixer Patterns
Edit `.github/skills/pipeline-fixer/SKILL.md` to add stage-specific error patterns, fix strategies, and custom log sanitisation patterns for your CI/CD setup.

### Adding Test Fixtures
See `tests/pipeline-fixer/README.md` for the fixture template and validation checklist.

## License

MIT
