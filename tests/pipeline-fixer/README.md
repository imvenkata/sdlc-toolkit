# Pipeline Fixer — Validation Strategy

> **Version**: 1.0.0
>
> This directory contains golden-path test fixtures for validating the Pipeline Fixer agent system. Each fixture represents a real-world failure scenario with expected agent behaviour.

---

## How to Use

### Manual Validation

1. Open VS Code with the `sdlc-toolkit` workspace
2. Open Copilot Chat → select `@pipeline-fixer`
3. For each fixture below, provide the **Input** section as context and verify the agent's output matches the **Expected Output** section

### Regression Testing

After any change to the agent, skill, or template files, re-run all fixtures to verify:
- [ ] Error pattern correctly identified
- [ ] Correct classification (category, retry-able flag)
- [ ] Appropriate confidence score
- [ ] Fix matches expected approach (if applicable)
- [ ] Sanitisation applied correctly
- [ ] Report follows template structure

---

## Fixture Inventory

| # | Fixture | Error Category | Stage | Expected Confidence | Expected Action |
|---|---------|---------------|-------|--------------------|-----------------| 
| 1 | [build-missing-dep.md](fixtures/build-missing-dep.md) | Build — Missing Dependency | `build` | 5/5 | Add dep to `package.json` |
| 2 | [test-service-missing.md](fixtures/test-service-missing.md) | Test — Service Unavailable | `test` | 4/5 | Add `services:` to CI job |
| 3 | [infra-network-timeout.md](fixtures/infra-network-timeout.md) | Infrastructure — Network | `build` | 4/5 | Retry (no code fix) |

---

## Adding New Fixtures

When adding a new fixture, follow this template:

```markdown
# Fixture: [Name]

## Metadata
| Field | Value |
|-------|-------|
| **Error Category** | [from SKILL.md lookup table] |
| **Stage** | [scan/build/test/publish/deploy] |
| **Expected Confidence** | [1-5]/5 |
| **Retry-able** | Yes/No |

## Input

### Job Log (sanitised)
[Paste a realistic job log with sensitive values already redacted]

### CI Config
[Paste the relevant .gitlab-ci.yml snippet]

### Stage Map
[Paste the stage map showing pass/fail status]

## Expected Output

### Diagnosis
[What the log-analyser should return]

### Fix (if applicable)
[What the fix-generator should return — diff format]

### Report
[Key fields that should appear in the final report]
```

---

## Validation Checklist (run after any prompt change)

- [ ] All 3 fixtures produce correct error classification
- [ ] Confidence scores match expected values (±1 tolerance)
- [ ] Sanitisation is applied to all fixture logs (no raw tokens in output)
- [ ] Fix diffs are minimal (one change per iteration)
- [ ] Report follows `pipeline-fix-template.md` structure
- [ ] Review Metadata footer is present with correct version
- [ ] Cross-agent handoff suggestions appear where expected
