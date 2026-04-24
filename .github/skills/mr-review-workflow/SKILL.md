---
name: mr-review-workflow
version: "3.0.0"
description: "Single source of truth for MR review detection patterns: security scan patterns, code quality signals, file classification rules, issue parsing patterns, and write-back templates. Referenced by the MR Reviewer orchestrator and its sub-agents."
---

# MR Review — Reference Material

This skill provides reference patterns for the MR Reviewer agent. It does NOT duplicate the workflow (which lives in the agent file). Instead, it holds the detailed checklists, scan patterns, and classification rules that the agent references during analysis.

## Issue Parsing Patterns

When extracting issue references from MR descriptions, match these patterns:

```
Closes #N          closes #N
Fixes #N           fixes #N
Resolves #N        resolves #N
Related to #N
Implements #N
See #N
https://gitlab.com/.../issues/N
```

When extracting acceptance criteria from issues, search for:
1. Checkbox lists: `- [ ]` and `- [x]` items
2. Named sections: "Acceptance Criteria", "Definition of Done", "Requirements", "Expected Behavior", "DoD"
3. User stories: "As a [role], I want [feature], so that [benefit]"
4. Technical specs: code blocks, API specifications, schema definitions
5. Comments/discussions that modify or clarify original criteria

---

## Security Scan Patterns

Scan diffs for these patterns. Each match is a finding.

### Critical (🔴)
| Pattern | Risk | Example |
|---------|------|---------|
| Hardcoded secrets | Credential exposure | `password = "..."`, `API_KEY = "sk-..."`, `token: "glpat-..."` |
| SQL concatenation | SQL injection | `query = "SELECT * FROM users WHERE id=" + id` |
| `eval()` / `exec()` on input | Remote code execution | `eval(request.body)` |
| `innerHTML` / `dangerouslySetInnerHTML` | XSS | `el.innerHTML = userInput` |
| Disabled SSL/TLS | MITM attack | `verify=False`, `rejectUnauthorized: false` |
| Auth bypass | Unauthorized access | Missing auth middleware on new endpoint |

### Medium (🟡)
| Pattern | Risk |
|---------|------|
| Missing input validation | Unexpected input handling |
| Overly permissive CORS (`*`) | Cross-origin abuse |
| Sensitive data in logs | Data leakage |
| Missing rate limiting on endpoints | DoS vulnerability |
| Disabled security headers | Browser security weakened |

### Low (🟢)
| Pattern | Risk |
|---------|------|
| TODO/FIXME in security-related code | Incomplete implementation |
| Missing Content-Security-Policy | Best practice gap |
| Broad exception catching | Swallowed errors |

---

## Code Quality Signals

### Positive Signals (raise score)
- Clear, descriptive names (no single-letter vars outside loops)
- Functions under ~50 lines, doing one thing (SRP)
- Error cases handled explicitly (try/catch, null checks, Result types)
- Named constants instead of magic numbers/strings
- Appropriate logging with correct levels

### Negative Signals (lower score)
- Deeply nested conditionals (>3 levels)
- Duplicated code blocks (DRY violation)
- Commented-out code blocks
- Functions with >5 parameters
- Missing error handling on I/O operations
- Inconsistent naming within the same file

---

## File Classification Reference

| Category | Patterns | Review Priority |
|----------|----------|----------------|
| API/Routes | `routes/`, `api/`, `controllers/`, `endpoints/`, `views/` | 🔴 Critical |
| Auth | `auth/`, `middleware/`, `permissions/`, `policies/`, `guards/` | 🔴 Critical |
| DB/Migrations | `migrations/`, `models/`, `schema`, `db/`, `entities/` | 🔴 Critical |
| Core Logic | `services/`, `handlers/`, `workers/`, `domain/`, `usecases/` | 🟡 Important |
| Config | `*.yml`, `*.yaml`, `*.toml`, `.env*`, `Dockerfile`, `.gitlab-ci.yml` | 🟡 Important |
| Dependencies | `package.json`, `requirements.txt`, `Gemfile`, `go.mod`, `Cargo.toml` | 🟡 Important |
| Tests | `test/`, `spec/`, `__tests__/`, `*_test.*`, `*_spec.*`, `*Test.*` | 🟢 Standard |
| Docs | `*.md`, `docs/`, `README*`, `CHANGELOG*`, `LICENSE` | 🟢 Standard |
| Generated | `dist/`, `build/`, `*.generated.*`, `*.min.*`, `*.map` | ⚪ Skip |

---

## Breaking Change Indicators

Always flag these as risk findings:
- Removed or renamed exported functions/classes/constants
- Changed function signatures on shared/public code
- Modified API response schemas (added required fields, removed fields, changed types)
- Database schema changes without corresponding migration
- Changed environment variable names
- Removed backwards compatibility shims
- Changed event/message contracts (message queues, webhooks)

---

## Write-Back Format Templates

### Draft Note Format
```
### [🔴/🟡/🟢] [Finding Category]

**File**: `[path]:[line]`
**Issue**: [what's wrong]
**Risk**: [why it matters]
**Recommendation**: [how to fix]
```

### Summary Comment Format
```
## 🤖 AI Review — [Mode] Mode

**Score: [X/Y]** — **[VERDICT]**

### Key Findings
- 🔴 [critical finding 1]
- 🟡 [medium finding 1]

### Action Items
1. [must-fix item]
2. [should-fix item]

*Full review available in chat. Run `@mr-reviewer Deep review` for extended analysis.*
```
