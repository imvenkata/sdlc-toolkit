# SDLC Toolkit — AI Agents for GitLab × GitHub Copilot

A suite of 6 AI-powered agents that integrate GitLab (via MCP) with GitHub Copilot to improve developer productivity, code quality, and decision-making across the software development lifecycle.

## Agents

| Agent | Command | Purpose |
|-------|---------|---------|
| **MR Reviewer** | `@mr-reviewer` | Reviews MRs against linked requirements with 5-dimension scoring |
| **Root Cause Analyzer** | `@root-cause` | Investigates pipeline failures with evidence-based hypothesis ranking |
| **Sprint Intelligence** | `@sprint-intel` | Generates data-driven sprint health reports from milestone data |
| **Impact Analyzer** | `@impact-analysis` | Maps blast radius of changes via dependency tracing |
| **Release Notes** | `@release-notes` | Generates categorized release notes from milestone MRs/issues |
| **Pipeline Fixer** | `@pipeline-fixer` | Iteratively diagnoses and fixes CI/CD pipeline failures across all stages |

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

The `.vscode/mcp.json` is pre-configured. VS Code will start the GitLab MCP server automatically when you open Copilot Chat.

### 4. Verify Agents

Open Copilot Chat → click the agent picker → you should see all 6 agents listed.

## Usage Examples

### MR Review
```
@mr-reviewer Review MR !42 in project my-group/my-project
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

### Pipeline Fixer
```
@pipeline-fixer Fix pipeline #456 in project my-group/my-project
@pipeline-fixer Fix the latest pipeline on branch feature/auth in project my-group/my-project
@pipeline-fixer verify pipeline #457 in project my-group/my-project
```

## Architecture

```
sdlc-toolkit/
├── .vscode/mcp.json                     # MCP server config
├── .github/
│   ├── copilot-instructions.md          # Global conventions
│   ├── agents/                          # Custom Copilot agents
│   │   ├── mr-reviewer.agent.md
│   │   ├── root-cause.agent.md
│   │   ├── sprint-intel.agent.md
│   │   ├── impact-analysis.agent.md
│   │   ├── release-notes.agent.md
│   │   └── pipeline-fixer.agent.md
│   └── skills/                          # Reusable skill modules
│       ├── gitlab-data-fetcher/
│       ├── mr-review-workflow/
│       ├── root-cause-analysis/
│       ├── sprint-analysis/
│       ├── impact-analysis/
│       ├── release-notes-gen/
│       └── pipeline-fixer/
└── prompt-templates/                    # Structured output templates
    ├── mr-review-rubric.md
    ├── rca-evidence-template.md
    ├── sprint-report-template.md
    ├── impact-report-template.md
    ├── release-notes-template.md
    └── pipeline-fix-template.md
```

### Design Principles

- **Zero infrastructure** — everything runs locally via Copilot Chat + MCP
- **Deterministic outputs** — scoring rubrics, formulas, and templates ensure consistent results
- **Evidence-based** — every claim traces to a specific GitLab MCP tool response
- **Iterative** — the Pipeline Fixer loops (diagnose → fix → push → verify) up to 3 times
- **Safety first** — write operations (comments, releases, code pushes) require explicit confirmation

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
Edit `.github/skills/pipeline-fixer/SKILL.md` to add stage-specific error patterns and fix strategies for your CI/CD setup.

## License

MIT
