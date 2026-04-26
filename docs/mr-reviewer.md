# MR Reviewer Agent — How It Works

> **Version**: 3.0.0
>
> This document explains the architecture, workflow, and scoring mechanisms of the MR Reviewer agent — an AI-powered merge request reviewer that integrates GitLab with GitHub Copilot via MCP.

---

## Overview

The MR Reviewer is an **orchestrator agent** that coordinates three specialist sub-agents to produce a comprehensive, scored merge request review. It operates in three depth modes:

| Mode | Dimensions | Max Score | Data Fetched | Duration |
|------|-----------|-----------|--------------|----------|
| **Quick** | 4 | /20 | MR metadata + diffs + issues | ~20s |
| **Standard** | 7 | /35 | + discussions, pipeline, approvals, conflicts | ~45s |
| **Deep** | 7 | /35 | + cross-MR overlap, MR versions, notes, issue discussions | ~90s |

---

## Architecture

```mermaid
graph TB
    subgraph "Developer Environment"
        DEV["👩‍💻 Developer<br/>VS Code + Copilot Chat"]
    end

    subgraph "Orchestrator Layer"
        MR["📋 MR Reviewer<br/>mr-reviewer.agent.md<br/>(claude-sonnet-4.5)"]
    end

    subgraph "Sub-Agent Layer"
        SS["🛡️ Security Scanner<br/>security-scanner.agent.md<br/>(gpt-4o-mini)"]
        RT["📎 Requirements Tracer<br/>requirements-tracer.agent.md<br/>(claude-sonnet-4.6)"]
        CQ["🔍 Code Quality Reviewer<br/>code-quality-reviewer.agent.md<br/>(claude-sonnet-4)"]
    end

    subgraph "GitLab MCP Server (@zereight/mcp-gitlab)"
        direction TB
        MCP_MR["get_merge_request<br/>list_merge_request_changed_files<br/>get_merge_request_file_diff"]
        MCP_IS["get_issue · list_issue_discussions<br/>list_issue_links"]
        MCP_CI["list_pipelines · get_pipeline<br/>list_pipeline_jobs"]
        MCP_AP["get_merge_request_approval_state<br/>get_merge_request_conflicts"]
        MCP_WB["create_note · create_draft_note<br/>create_merge_request_thread<br/>bulk_publish_draft_notes"]
    end

    subgraph "Reference Material"
        SK["📚 SKILL.md<br/>File classification<br/>Security patterns<br/>Quality signals"]
        RB["📝 mr-review-rubric.md<br/>7-dimension scoring<br/>Verdict thresholds"]
        PP["🐍 python-patterns.md<br/>Language-specific<br/>review patterns"]
    end

    DEV -->|"@mr-reviewer Review MR !42<br/>in project my-app"| MR

    MR -->|"file diffs"| SS
    MR -->|"issues + criteria + diffs"| RT
    MR -->|"diffs + language hint"| CQ
    SS -->|"security findings<br/>(🔴/🟡/🟢)"| MR
    RT -->|"traceability matrix<br/>(coverage %)"| MR
    CQ -->|"quality + consistency<br/>+ completeness"| MR

    MR <-->|"Phase 1: Context"| MCP_MR
    MR <-->|"Phase 1: Issues"| MCP_IS
    MR <-->|"Phase 1: Pipeline"| MCP_CI
    MR <-->|"Phase 1: Approvals"| MCP_AP
    MR <-->|"Phase 4: Write-back"| MCP_WB

    MR -.->|"references"| SK
    MR -.->|"scores with"| RB
    CQ -.->|"uses"| PP

    style MR fill:#4A90D9,stroke:#2C5F8A,color:#fff
    style SS fill:#E53935,stroke:#B71C1C,color:#fff
    style RT fill:#7CB342,stroke:#558B2F,color:#fff
    style CQ fill:#FF7043,stroke:#D84315,color:#fff
    style MCP_MR fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_IS fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_CI fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_AP fill:#AB47BC,stroke:#7B1FA2,color:#fff
    style MCP_WB fill:#AB47BC,stroke:#7B1FA2,color:#fff
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Orchestrator makes all MCP calls** | Sub-agents have `tools: []` — they receive only the data they need, never access GitLab directly. |
| **gpt-4o-mini for security scanning** | Security pattern matching is rule-based — fast and cheap is sufficient. |
| **claude-sonnet-4.6 for requirements tracing** | Mapping acceptance criteria to code changes requires strong reasoning. |
| **claude-sonnet-4 for code quality** | Quality assessment benefits from understanding code structure and idioms. |
| **7 scoring dimensions** | Covers the full spectrum from requirements to CI health, enabling objective verdicts. |

---

## Workflow — Phase by Phase

```mermaid
flowchart TD
    START(["@mr-reviewer Review MR !42"])

    subgraph "Phase 1: Context Gathering"
        P1A["1a. Fetch MR metadata<br/><code>get_merge_request()</code>"]
        P1B["1b. Parse issue refs from description"]
        P1C["1c. Fetch linked issues<br/><code>get_issue()</code> per ref"]
        P1D["1d. List changed files<br/><code>list_merge_request_changed_files()</code>"]
        P1E["1e. Classify files by priority<br/>🔴 Critical / 🟡 Important / 🟢 Standard / ⚪ Low"]
        P1F["1f. Fetch diffs (batched 3-5)<br/><code>get_merge_request_file_diff()</code>"]
        P1G["1g. Fetch pipeline status<br/><code>list_pipelines() → get_pipeline()</code>"]
        P1H["1h. Fetch approvals + conflicts<br/><code>get_merge_request_approval_state()</code><br/><code>get_merge_request_conflicts()</code>"]
    end

    subgraph "Phase 2: Sub-Agent Delegation"
        P2A["Dispatch to security-scanner<br/>(file diffs)"]
        P2B["Dispatch to requirements-tracer<br/>(issues + criteria + diffs)"]
        P2C["Dispatch to code-quality-reviewer<br/>(diffs + language hint)"]
    end

    subgraph "Phase 3: Scoring & Report"
        P3A["Aggregate sub-agent findings"]
        P3B["Score 7 dimensions (1-5 each)"]
        P3C["Apply override rules"]
        P3D["Calculate verdict<br/>PASS / NEEDS_WORK / REJECT"]
        P3E["Generate report"]
    end

    subgraph "Phase 4: Write-Back"
        P4A{"Post findings<br/>to MR?"}
        P4B["A: Draft notes → bulk publish"]
        P4C["B: Inline threads with position"]
        P4D["C: Summary comment"]
    end

    START --> P1A --> P1B --> P1C --> P1D --> P1E --> P1F --> P1G --> P1H

    P1H --> P2A
    P1H --> P2B
    P1H --> P2C

    P2A --> P3A
    P2B --> P3A
    P2C --> P3A

    P3A --> P3B --> P3C --> P3D --> P3E

    P3E --> P4A
    P4A -->|"A"| P4B
    P4A -->|"B"| P4C
    P4A -->|"C"| P4D
    P4A -->|"N"| END(["Done"])
    P4B --> END
    P4C --> END
    P4D --> END

    style START fill:#4A90D9,stroke:#2C5F8A,color:#fff
    style P3D fill:#FF9800,stroke:#E65100,color:#fff
    style END fill:#4CAF50,stroke:#2E7D32,color:#fff
```

---

## Sub-Agent Communication

The orchestrator passes raw GitLab data to each sub-agent and receives structured findings. Sub-agents never talk to each other or to GitLab directly.

```mermaid
sequenceDiagram
    participant D as Developer
    participant O as Orchestrator
    participant SS as Security Scanner
    participant RT as Requirements Tracer
    participant CQ as Code Quality Reviewer
    participant G as GitLab (MCP)

    D->>O: @mr-reviewer Review MR !42 in project X

    Note over O: Phase 1 — Context Gathering
    O->>G: get_merge_request(project, 42)
    G-->>O: MR metadata (title, desc, branch, labels, author)
    O->>G: get_issue(project, 15) [parsed from desc]
    G-->>O: Issue with acceptance criteria
    O->>G: list_merge_request_changed_files(project, 42)
    G-->>O: 12 changed files
    Note over O: Classify files by priority tier
    O->>G: get_merge_request_file_diff(project, 42, [f1,f2,f3])
    G-->>O: file diffs (batch 1)
    O->>G: get_merge_request_file_diff(project, 42, [f4,f5,f6])
    G-->>O: file diffs (batch 2)
    O->>G: list_pipelines(project, ref=branch)
    G-->>O: pipeline #789 — status: success ✅
    O->>G: get_merge_request_approval_state(project, 42)
    G-->>O: 1/2 approvals
    O->>G: get_merge_request_conflicts(project, 42)
    G-->>O: no conflicts

    Note over O: Phase 2 — Parallel Delegation
    par Security Analysis
        O->>SS: file diffs + review mode
        Note over SS: Scan for:<br/>- Hardcoded secrets<br/>- SQL injection<br/>- Auth bypass<br/>- Breaking changes
        SS-->>O: 1 🟡 finding (unvalidated input at auth.ts:45)
    and Requirements Tracing
        O->>RT: Issue #15 criteria + file diffs
        Note over RT: Map each criterion<br/>to implementation:<br/>✅ Met / ⚠️ Partial / ❌ Missing
        RT-->>O: 4/5 criteria met (80% coverage)
    and Code Quality
        O->>CQ: file diffs + "TypeScript" hint
        Note over CQ: Assess:<br/>- Naming & structure<br/>- Error handling<br/>- DRY compliance<br/>- Consistency
        CQ-->>O: Quality: 4/5, Consistency: 4/5, Completeness: 3/5
    end

    Note over O: Phase 3 — Score & Report
    Note over O: 1. Requirements: 4/5 (from RT)<br/>2. Completeness: 3/5 (from CQ)<br/>3. Security: 4/5 (from SS)<br/>4. Code Quality: 4/5 (from CQ)<br/>5. Consistency: 4/5 (from CQ)<br/>6. CI/CD Health: 5/5 (pipeline green)<br/>7. Scope: 5/5 (12 files)
    Note over O: Total: 29/35 → PASS ✅

    O->>D: Review Report — 29/35 — PASS ✅

    Note over O: Phase 4 — Write-Back
    D->>O: Post as summary comment (C)
    O->>G: create_note(MergeRequest, 42, report)
    G-->>O: note posted ✅
```

---

## Scoring System

### 7 Dimensions

```mermaid
graph LR
    subgraph "Sub-Agent Scored"
        D1["1. Requirements<br/>Alignment"]
        D2["2. Completeness"]
        D3["3. Security<br/>& Risk"]
        D4["4. Code Quality"]
        D5["5. Consistency"]
    end

    subgraph "Orchestrator Scored"
        D6["6. CI/CD Health"]
        D7["7. Scope &<br/>Atomicity"]
    end

    RT_A["Requirements<br/>Tracer"] --> D1
    CQ_A["Code Quality<br/>Reviewer"] --> D2
    SS_A["Security<br/>Scanner"] --> D3
    CQ_A --> D4
    CQ_A --> D5

    MCP_A["Pipeline +<br/>Approval Data"] --> D6
    MCP_A --> D7

    D1 --> TOTAL["Total Score<br/>/35"]
    D2 --> TOTAL
    D3 --> TOTAL
    D4 --> TOTAL
    D5 --> TOTAL
    D6 --> TOTAL
    D7 --> TOTAL

    TOTAL --> V{"Verdict"}
    V -->|"≥ 28 (80%)"| PASS["✅ PASS"]
    V -->|"21-27 (60-79%)"| NEEDS["🟡 NEEDS_WORK"]
    V -->|"< 21 (< 60%)"| REJECT["🔴 REJECT"]

    style PASS fill:#4CAF50,stroke:#2E7D32,color:#fff
    style NEEDS fill:#FF9800,stroke:#E65100,color:#fff
    style REJECT fill:#F44336,stroke:#C62828,color:#fff
```

### Scoring Scale (per dimension)

| Score | Meaning |
|-------|---------|
| **5** | Excellent — no concerns |
| **4** | Good — minor improvements possible |
| **3** | Acceptable — some gaps |
| **2** | Below standard — needs attention |
| **1** | Poor — significant rework needed |
| **N/A** | Cannot assess — dimension removed from total |

### Verdicts

| Mode | Pass (≥80%) | Needs Work (60-79%) | Reject (<60%) |
|------|-------------|---------------------|----------------|
| **Quick** (/20) | ≥ 16 | 12-15 | < 12 |
| **Standard/Deep** (/35) | ≥ 28 | 21-27 | < 21 |

### Dynamic N/A Adjustment

When a dimension is scored N/A (e.g., no linked issues → Requirements = N/A), it is removed from the total and thresholds recalculate:

```
adjusted_max = scored_dimensions × 5
Pass ≥ ceiling(adjusted_max × 0.80)
Needs Work ≥ ceiling(adjusted_max × 0.60)
Reject < ceiling(adjusted_max × 0.60)
```

*Example: 2 dims N/A → 5 scored → max = 25. Pass ≥ 20, Needs Work 15-19, Reject < 15.*

### Override Rules

These take precedence over raw scores:

| Condition | Override |
|-----------|----------|
| Pipeline failing on build/test | Max verdict = **NEEDS_WORK** |
| Any 🔴 Critical security finding | Max verdict = **NEEDS_WORK** |
| No linked issues | Requirements = N/A (adjust total) |
| Unresolved blocking threads | Noted in report |

---

## Depth Modes — What Each Fetches

```mermaid
graph TD
    subgraph "Quick Mode (4 dimensions, ~20s)"
        Q1["MR metadata"]
        Q2["Linked issues"]
        Q3["Changed files + diffs"]
        Q4["Security scan ✅"]
        Q5["Code quality ✅"]
        Q6["Requirements (inline) ✅"]
    end

    subgraph "Standard Mode adds (+3 dimensions, ~45s)"
        S1["MR discussions"]
        S2["Approval state"]
        S3["Pipeline status + jobs"]
        S4["Conflict check"]
        S5["Requirements tracer ✅"]
        S6["CI/CD Health ✅"]
        S7["Scope & Atomicity ✅"]
    end

    subgraph "Deep Mode adds (~90s)"
        D1["Cross-MR file overlap (max 10 MRs)"]
        D2["MR versions history"]
        D3["MR notes"]
        D4["Issue discussions"]
        D5["Issue links"]
    end

    style Q4 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Q5 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Q6 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style S5 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style S6 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style S7 fill:#4CAF50,stroke:#2E7D32,color:#fff
```

### Sub-Agent Delegation by Mode

| Sub-Agent | Quick | Standard | Deep |
|-----------|-------|----------|------|
| **Security Scanner** | ✅ | ✅ | ✅ |
| **Requirements Tracer** | ❌ (inline check) | ✅ | ✅ |
| **Code Quality Reviewer** | ✅ | ✅ | ✅ |

In Quick mode, the orchestrator performs a lightweight requirements check itself instead of invoking the requirements-tracer sub-agent.

---

## Adaptive Diff Loading

For large MRs, the orchestrator uses a priority-based diff loading strategy:

```mermaid
flowchart TD
    FILES["list_merge_request_changed_files()"]
    CLASSIFY["Classify each file by priority"]

    CRIT["🔴 Critical<br/>auth, API routes, migrations,<br/>models, security config"]
    IMP["🟡 Important<br/>services, config, Dockerfile,<br/>dependencies, middleware"]
    STD["🟢 Standard<br/>tests, docs, utilities,<br/>README, CHANGELOG"]
    LOW["⚪ Low<br/>lock files, minified,<br/>build output, .map files"]

    ALWAYS["Always fetch diffs"]
    CONDITIONAL["Fetch in Standard/Deep"]
    SKIP["Skip — auto-excluded"]

    CHECK{">30 files?"}
    FULL["Fetch all 🔴 + 🟡 + 🟢"]
    PARTIAL["Fetch only 🔴 + 🟡<br/>Report skipped files"]
    OFFER["Offer: 'Run Deep review<br/>to analyze all files'"]

    FILES --> CLASSIFY
    CLASSIFY --> CRIT --> ALWAYS
    CLASSIFY --> IMP --> ALWAYS
    CLASSIFY --> STD --> CONDITIONAL
    CLASSIFY --> LOW --> SKIP

    ALWAYS --> CHECK
    CONDITIONAL --> CHECK
    CHECK -->|"No"| FULL
    CHECK -->|"Yes"| PARTIAL --> OFFER

    style CRIT fill:#F44336,stroke:#C62828,color:#fff
    style IMP fill:#FF9800,stroke:#E65100,color:#fff
    style STD fill:#4CAF50,stroke:#2E7D32,color:#fff
    style LOW fill:#9E9E9E,stroke:#616161,color:#fff
```

---

## Write-Back Options

After presenting the review, the orchestrator asks before writing anything to GitLab:

> "Post findings to MR? (A) Draft notes → bulk publish, (B) Inline threads, (C) Summary comment, (N) No"

```mermaid
graph TD
    ASK{"Post findings to MR?"}

    A["Option A: Draft Notes"]
    A1["create_draft_note() per finding"]
    A2["bulk_publish_draft_notes()"]

    B["Option B: Inline Threads"]
    B1["create_merge_request_thread()<br/>with position object (file:line)"]

    C["Option C: Summary Comment"]
    C1["create_note()<br/>noteable_type=MergeRequest"]

    N["Option N: No write-back"]

    ASK -->|"A"| A --> A1 --> A2
    ASK -->|"B"| B --> B1
    ASK -->|"C"| C --> C1
    ASK -->|"N"| N

    style A fill:#64B5F6,stroke:#1565C0,color:#fff
    style B fill:#FF7043,stroke:#D84315,color:#fff
    style C fill:#81C784,stroke:#388E3C,color:#fff
    style N fill:#9E9E9E,stroke:#616161,color:#fff
```

**Write-back is never automatic.** The orchestrator always asks for explicit user confirmation before posting anything to GitLab.

---

## Team Overrides

Teams can customise the review by embedding a config block in the MR description:

```markdown
<!-- mr-reviewer-config
required_labels: ["reviewed", "approved"]
branch_pattern: "^(feature|bugfix|hotfix)/"
skip_dimensions: ["Consistency"]
custom_checks:
  - "Verify CHANGELOG.md is updated"
  - "Check that new API endpoints have OpenAPI specs"
-->
```

```mermaid
flowchart LR
    MR_DESC["MR Description"]
    PARSE["Parse mr-reviewer-config block"]

    RL["required_labels<br/>Verify labels present"]
    BP["branch_pattern<br/>Validate branch name"]
    SD["skip_dimensions<br/>Score as N/A"]
    CC["custom_checks<br/>Add to completeness"]

    MR_DESC --> PARSE
    PARSE --> RL
    PARSE --> BP
    PARSE --> SD
    PARSE --> CC
```

---

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| **Transient MCP error** (timeout, 5xx) | Retry once |
| **Persistent MCP failure** (2 consecutive) | Mark affected dimension as "Unable to assess" |
| **Auth error** (401/403) | Stop review. Report auth failure. |
| **Sub-agent timeout** | Use findings from completed sub-agents. Mark failed dimensions. |
| **Diff too large** (>500 lines/file) | Flag for manual review, note in report |
| **MR with 0 files** | Skip code analysis dimensions |
| **Rate limited** | Report partial results, offer re-run |

---

## Cross-Agent Connection

The MR Reviewer connects to the Pipeline Fixer in one direction:

```mermaid
graph LR
    PF["🔧 Pipeline Fixer"]
    MR["📋 MR Reviewer"]

    PF -->|"Fix branch created<br/>+ pipeline passes"| MR

    style PF fill:#FF7043,stroke:#D84315,color:#fff
    style MR fill:#4A90D9,stroke:#2C5F8A,color:#fff
```

When the Pipeline Fixer creates a `fix/ci-*` branch and the pipeline passes, it suggests running `@mr-reviewer Quick review MR !<iid>` to review the fix before merging.

---

## File Map

```
sdlc-toolkit/
├── .github/
│   ├── agents/
│   │   ├── mr-reviewer.agent.md           ← Orchestrator (you invoke this)
│   │   ├── security-scanner.agent.md       ← Sub-agent (security analysis)
│   │   ├── requirements-tracer.agent.md    ← Sub-agent (requirements mapping)
│   │   └── code-quality-reviewer.agent.md  ← Sub-agent (quality + consistency)
│   └── skills/
│       └── mr-review-workflow/
│           ├── SKILL.md                    ← File classification, security patterns
│           └── python-patterns.md          ← Python-specific review patterns
└── prompt-templates/
    └── mr-review-rubric.md                 ← 7-dimension scoring rubric
```
