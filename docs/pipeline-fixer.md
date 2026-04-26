# Pipeline Fixer Agent — How It Works

> **Version**: 3.1.0
>
> This document explains the architecture, workflow, and safety mechanisms of the Pipeline Fixer agent — an AI-powered CI/CD pipeline debugger that integrates GitLab with GitHub Copilot via MCP.

---

## Overview

The Pipeline Fixer is an **orchestrator agent** that coordinates two specialist sub-agents to diagnose and fix CI/CD pipeline failures. It operates in three modes with increasing autonomy:

| Mode | Reads | Writes | Approval |
|------|-------|--------|----------|
| **Diagnose** | ✅ | ❌ | None needed |
| **Fix** | ✅ | ✅ | Asks before every push |
| **Auto-fix** | ✅ | ✅ | Automatic if confidence ≥ 4/5 |

---

## Architecture

```mermaid
graph TB
    subgraph "Developer Environment"
        DEV["👩‍💻 Developer<br/>VS Code + Copilot Chat"]
    end

    subgraph "Orchestrator Layer"
        PF["🔧 Pipeline Fixer<br/>pipeline-fixer.agent.md<br/>(claude-sonnet-4.5)"]
    end

    subgraph "Sub-Agent Layer"
        LA["🔍 Log Analyser<br/>log-analyser.agent.md<br/>(gpt-5-mini)"]
        FG["🛠️ Fix Generator<br/>fix-generator.agent.md<br/>(claude-sonnet-4.6)"]
    end

    subgraph "GitLab MCP Server (@zereight/mcp-gitlab)"
        direction TB
        MCP_P["get_pipeline · list_pipelines<br/>create_pipeline · retry_pipeline"]
        MCP_J["list_pipeline_jobs<br/>get_pipeline_job_output<br/>retry_pipeline_job"]
        MCP_F["get_file_contents<br/>create_or_update_file<br/>push_files"]
        MCP_B["create_branch<br/>create_note"]
    end

    subgraph "Safety Layer"
        H1["🛡️ pre-push-validation"]
        H2["🛡️ prompt-guard"]
        H3["🛡️ session-audit"]
    end

    subgraph "Reference Material"
        SK["📚 SKILL.md<br/>Error patterns<br/>Sanitisation rules"]
        TM["📝 pipeline-fix-template.md<br/>Report structure"]
    end

    DEV -->|"@pipeline-fixer Fix pipeline #123<br/>in project my-app"| PF
    H2 -.->|"validates prompt"| PF
    H3 -.->|"logs session"| PF

    PF -->|"raw logs + CI config<br/>+ stage map + metadata"| LA
    LA -->|"sanitised diagnosis<br/>+ confidence score"| PF

    PF -->|"diagnosis + source files<br/>+ CI config + iteration history"| FG
    FG -->|"proposed fix + diff<br/>+ confidence + rationale"| PF

    PF <-->|"Phase 1: Diagnose"| MCP_P
    PF <-->|"Phase 1: Fetch logs"| MCP_J
    PF <-->|"Phase 2: Fetch/Push files"| MCP_F
    PF <-->|"Phase 3-4: Branch/Trigger"| MCP_B
    H1 -.->|"validates pushes"| MCP_F

    PF -.->|"references"| SK
    PF -.->|"formats output"| TM

    style PF fill:#4A90D9,stroke:#2C5F8A,color:#fff
    style LA fill:#7CB342,stroke:#558B2F,color:#fff
    style FG fill:#FF7043,stroke:#D84315,color:#fff
    style MCP_P fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_J fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_F fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_B fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style H1 fill:#FFB74D,stroke:#E65100,color:#000
    style H2 fill:#FFB74D,stroke:#E65100,color:#000
    style H3 fill:#FFB74D,stroke:#E65100,color:#000
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Orchestrator makes all MCP calls** | Sub-agents have `tools: []` — they can't access GitLab directly. This centralises all external I/O in one place for auditability. |
| **gpt-5-mini for log analysis** | Log parsing is pattern matching — fast and cheap is better than powerful. |
| **claude-sonnet-4.6 for fix generation** | Generating correct minimal code fixes requires strong reasoning. |
| **claude-sonnet-4.5 for orchestration** | Coordination needs large context windows and good planning. |

---

## Workflow — Phase by Phase

```mermaid
flowchart TD
    START(["@pipeline-fixer Fix pipeline #123"])
    
    subgraph "Phase 1: DIAGNOSE"
        P1A["1a. Fetch pipeline overview<br/><code>get_pipeline()</code>"]
        P1B["1b. Fetch CI config<br/><code>get_file_contents(.gitlab-ci.yml)</code>"]
        P1C["1c. Fetch included configs<br/><code>get_file_contents()</code> per include"]
        P1D["1d. List all jobs<br/><code>list_pipeline_jobs()</code>"]
        P1E["1e. Fetch failed job logs<br/><code>get_pipeline_job_output()</code>"]
        P1F["1f. Build stage map"]
        P1G["1g. Delegate to log-analyser"]
    end

    subgraph "Phase 2: FIX"
        P2A["2a. Fetch source files<br/>based on diagnosis category"]
        P2B["2b. Delegate to fix-generator"]
        P2C["2c. Validate confidence<br/>(cap at diagnosis level)"]
        P2D["2d. Present fix to user"]
    end

    subgraph "Phase 3: PUSH"
        P3A{"Confidence ≥ 4?"}
        P3B{"Protected<br/>branch?"}
        P3C["Create fix branch<br/><code>create_branch(fix/ci-...)</code>"]
        P3D["Push fix<br/><code>create_or_update_file()</code>"]
        P3E["Ask user:<br/>'Push this fix? (Y/N)'"]
    end

    subgraph "Phase 4: TRIGGER"
        P4A["Trigger new pipeline<br/><code>create_pipeline()</code>"]
    end

    subgraph "Phase 5: VERIFY"
        P5A["Check pipeline status<br/><code>get_pipeline()</code>"]
        P5B{"Status?"}
        P5C["✅ Report success"]
        P5D{"Iteration < 3?"}
        P5E["❌ Report failure<br/>Suggest @root-cause"]
    end

    POST["Post audit note to GitLab"]

    START --> P1A --> P1B --> P1C --> P1D --> P1E --> P1F --> P1G
    P1G --> P2A --> P2B --> P2C --> P2D
    P2D --> P3A

    P3A -->|"Auto-fix mode"| P3B
    P3A -->|"Fix mode"| P3E
    P3E -->|"Yes"| P3B
    P3E -->|"No"| POST

    P3B -->|"Yes"| P3C --> P3D
    P3B -->|"No"| P3D

    P3D --> P4A --> P5A --> P5B

    P5B -->|"success"| P5C --> POST
    P5B -->|"failed"| P5D
    P5B -->|"running"| P5A

    P5D -->|"Yes"| P1A
    P5D -->|"No"| P5E --> POST

    style START fill:#4A90D9,stroke:#2C5F8A,color:#fff
    style P5C fill:#4CAF50,stroke:#2E7D32,color:#fff
    style P5E fill:#F44336,stroke:#C62828,color:#fff
    style P3E fill:#FF9800,stroke:#E65100,color:#fff
```

---

## Sub-Agent Communication

The orchestrator passes structured data to each sub-agent and receives structured results back. Sub-agents never talk to each other directly.

```mermaid
sequenceDiagram
    participant D as Developer
    participant O as Orchestrator
    participant L as Log Analyser
    participant F as Fix Generator
    participant G as GitLab (MCP)

    D->>O: @pipeline-fixer Fix pipeline #123 in project X

    Note over O: Phase 1 — Gather Data
    O->>G: get_pipeline(project, 123)
    G-->>O: pipeline metadata
    O->>G: get_file_contents(.gitlab-ci.yml)
    G-->>O: CI config YAML
    O->>G: list_pipeline_jobs(project, 123)
    G-->>O: job list (build ❌, test ⏭️)
    O->>G: get_pipeline_job_output(job_id)
    G-->>O: raw job log

    Note over O: Phase 1 — Delegate Analysis
    O->>L: Raw log + CI config + stage map + job metadata
    Note over L: 1. Sanitise log (redact tokens)<br/>2. Extract error lines<br/>3. Classify failure<br/>4. Identify root cause<br/>5. Score confidence
    L-->>O: Diagnosis (category, cause, file, confidence 5/5)

    Note over O: Phase 2 — Fetch & Fix
    O->>G: get_file_contents(package.json)
    G-->>O: source file content
    O->>F: Diagnosis + source file + CI config + iteration 1
    Note over F: 1. Generate minimal diff<br/>2. Score confidence<br/>3. Assess risk<br/>4. Write commit message
    F-->>O: Fix (diff, confidence 5/5, rationale)

    Note over O: Confidence Validation
    Note over O: fix_confidence (5) ≤ diagnosis_confidence (5) ✅

    Note over O: Phase 3 — Push (with approval)
    O->>D: Proposed fix — push to branch? (Y/N)
    D-->>O: Yes

    O->>G: create_or_update_file(package.json, fix)
    G-->>O: commit SHA

    Note over O: Phase 4 — Trigger
    O->>G: create_pipeline(project, branch)
    G-->>O: pipeline #124

    Note over O: Phase 5 — Verify
    O->>G: get_pipeline(project, 124)
    G-->>O: status: success ✅

    Note over O: Audit
    O->>G: create_note(pipeline audit JSON)

    O->>D: ✅ Pipeline Fixed! Report with iteration history.
```

---

## Safety Mechanisms

### Layered Protection

```mermaid
graph LR
    subgraph "Layer 1: Input"
        PG["Prompt Guard<br/>Block injection &<br/>privilege escalation"]
    end

    subgraph "Layer 2: Analysis"
        SAN["Log Sanitisation<br/>23 regex patterns<br/>redact secrets"]
    end

    subgraph "Layer 3: Decision"
        CONF["Confidence Gate<br/>Auto-fix only if ≥ 4/5<br/>Inheritance rule enforced"]
    end

    subgraph "Layer 4: Execution"
        PPV["Pre-Push Validation<br/>Block protected branches<br/>Force fix/ci-* pattern"]
    end

    subgraph "Layer 5: Audit"
        SA["Session Audit<br/>Log all tool usage<br/>SOC2 compliance"]
    end

    PG --> SAN --> CONF --> PPV --> SA

    style PG fill:#FFB74D,stroke:#E65100
    style SAN fill:#81C784,stroke:#388E3C
    style CONF fill:#64B5F6,stroke:#1565C0
    style PPV fill:#FFB74D,stroke:#E65100
    style SA fill:#CE93D8,stroke:#7B1FA2
```

### Safety Rules Summary

| Rule | Mechanism | What It Prevents |
|------|-----------|-----------------|
| **Never push without approval** (Fix mode) | Orchestrator asks "Push? (Y/N)" | Unintended code changes |
| **Confidence gate** (Auto-fix mode) | Falls back to Fix mode if confidence < 4 | Low-confidence auto-pushes |
| **Protected branch detection** | Creates `fix/ci-*` branch | Pushes to main/production |
| **Max 3 iterations** | Hard stop after 3 loops | Infinite fix loops |
| **Log sanitisation** | 23 regex patterns applied before analysis | Credential exposure to AI |
| **Confidence inheritance** | Fix confidence ≤ diagnosis confidence | Over-confident fixes |
| **Pre-push hook** | Blocks pushes to protected branches | Hook-level enforcement |
| **Prompt guard** | Blocks injection and privilege escalation | Prompt attacks |
| **Audit logging** | All sessions and tool usage logged | Non-repudiation |

---

## Invocation Modes — Decision Tree

```mermaid
flowchart TD
    INPUT["User invokes @pipeline-fixer"]
    
    HELP{"'help' keyword?"}
    MODE{"Mode keyword?"}
    
    DIAG["DIAGNOSE<br/>Read-only analysis<br/>No sub-agent: fix-generator<br/>Output: diagnosis report"]
    FIX["FIX<br/>Proposes fixes<br/>Asks before pushing<br/>Output: fix + report"]
    AUTO["AUTO-FIX<br/>Push if confidence ≥ 4<br/>Poll for verification<br/>Loop up to 3×"]
    
    CARD["Return quick reference card<br/>and STOP"]
    
    INPUT --> HELP
    HELP -->|"Yes"| CARD
    HELP -->|"No"| MODE
    
    MODE -->|"'Diagnose'"| DIAG
    MODE -->|"'Fix' or default"| FIX
    MODE -->|"'Auto-fix'"| AUTO

    style DIAG fill:#4CAF50,stroke:#2E7D32,color:#fff
    style FIX fill:#2196F3,stroke:#1565C0,color:#fff
    style AUTO fill:#FF9800,stroke:#E65100,color:#fff
    style CARD fill:#9E9E9E,stroke:#616161,color:#fff
```

---

## Error Classification

The log-analyser classifies failures into categories using patterns from SKILL.md:

```mermaid
graph TD
    LOG["Job Log Output"]
    
    LOG --> CI["CI Config Error<br/>YAML syntax, unknown stage,<br/>missing variable"]
    LOG --> BUILD["Build Error<br/>Missing dep, syntax error,<br/>type error, Docker COPY"]
    LOG --> TEST["Test Error<br/>Assertion failure, missing fixture,<br/>timeout"]
    LOG --> FLAKY["Flaky Test<br/>Intermittent timeout,<br/>connection reset"]
    LOG --> SCAN["Scan Error<br/>Scanner crash, findings,<br/>scan timeout"]
    LOG --> PUB["Publish Error<br/>Registry auth, tag error,<br/>disk full"]
    LOG --> DEPLOY["Deploy Error<br/>K8s error, health check,<br/>SSH failure"]
    LOG --> INFRA["Infrastructure<br/>OOM, network timeout,<br/>DNS failure, runner crash"]

    CI -->|"No"| FIX_CODE["Fix: Code/Config Change"]
    BUILD -->|"No"| FIX_CODE
    TEST -->|"No"| FIX_CODE
    SCAN -->|"Depends"| FIX_CODE
    PUB -->|"Maybe"| FIX_CODE
    DEPLOY -->|"Maybe"| FIX_CODE

    FLAKY -->|"Yes"| RETRY["Action: Retry Job"]
    INFRA -->|"Yes"| RETRY

    FIX_CODE --> FG_AGENT["→ Fix Generator"]
    RETRY --> RETRY_API["→ retry_pipeline_job()"]

    style INFRA fill:#FFB74D,stroke:#E65100
    style FLAKY fill:#FFB74D,stroke:#E65100
    style FIX_CODE fill:#64B5F6,stroke:#1565C0
    style RETRY fill:#81C784,stroke:#388E3C
```

---

## Cross-Agent Handoffs

The Pipeline Fixer connects to other agents in the toolkit:

```mermaid
graph LR
    PF["🔧 Pipeline Fixer"]
    
    MR["📋 MR Reviewer<br/>@mr-reviewer"]
    RC["🔍 Root Cause<br/>@root-cause"]

    PF -->|"Fix branch created<br/>+ pipeline passes"| MR
    PF -->|"3 iterations exhausted<br/>without fix"| RC

    style PF fill:#4A90D9,stroke:#2C5F8A,color:#fff
    style MR fill:#7CB342,stroke:#558B2F,color:#fff
    style RC fill:#FF7043,stroke:#D84315,color:#fff
```

**Handoff triggers:**
- **→ MR Reviewer**: When the fixer creates a `fix/ci-*` branch and the pipeline passes, it suggests: _"Run `@mr-reviewer Quick review MR !<iid>` to review the fix before merging."_
- **→ Root Cause**: When 3 iterations fail to fix the pipeline, it suggests: _"Run `@root-cause Analyse pipeline #<id>` for a deeper investigation."_

---

## File Map

```
sdlc-toolkit/
├── .github/
│   ├── agents/
│   │   ├── pipeline-fixer.agent.md    ← Orchestrator (you invoke this)
│   │   ├── log-analyser.agent.md      ← Sub-agent (log parsing)
│   │   └── fix-generator.agent.md     ← Sub-agent (fix generation)
│   ├── skills/
│   │   └── pipeline-fixer/
│   │       └── SKILL.md               ← Error patterns + sanitisation rules
│   └── hooks/
│       ├── pre-push-validation.json   ← Block unsafe pushes
│       ├── prompt-guard.json          ← Block prompt injection
│       └── session-audit.json         ← Compliance logging
├── prompt-templates/
│   └── pipeline-fix-template.md       ← Report output structure
└── tests/
    └── pipeline-fixer/
        ├── README.md                  ← Validation strategy
        └── fixtures/                  ← Golden-path test scenarios
```
