# Impact Analysis Report Template

Use this template to structure impact analysis output.

---

## Change Summary

| Field | Value |
|-------|-------|
| **Source** | MR `![iid]` — `[title]` / Branch `[name]` |
| **Author** | `@[username]` |
| **Target Branch** | `[target]` |
| **Files Changed** | `[N]` |
| **Lines Added** | `+[N]` |
| **Lines Removed** | `-[N]` |
| **Overall Risk** | `🔴 Critical` / `🟡 Moderate` / `🟢 Low` |

---

## Changed Files by Risk Level

| Risk | File | Change | Classification Reason |
|------|------|--------|----------------------|
| 🔴 | `[path]` | `Modified/Added/Deleted` | `[e.g., shared library, API route]` |
| 🟡 | `[path]` | `Modified` | `[e.g., service logic, 5 downstream refs]` |
| 🟢 | `[path]` | `Added` | `[e.g., test file, documentation]` |

---

## Dependency Map

### Changed Symbols & Their Consumers

| Symbol | Defined In | Change Type | Consumer Count | Consumers | Risk |
|--------|-----------|-------------|----------------|-----------|------|
| `function_name()` | `[file]` | Signature changed | `[N]` | `[file1, file2, ...]` | 🔴 |
| `ClassName` | `[file]` | Method added | `[N]` | `[files]` | 🟡 |
| `CONSTANT` | `[file]` | Value changed | `[N]` | `[files]` | 🟡 |

### Visual Dependency Graph
```
[changed_file] → [consumer_1] → [indirect_consumer]
[changed_file] → [consumer_2]
```

---

## Conflict Detection

| Open MR | Author | Overlapping Files | Conflict Risk |
|---------|--------|-------------------|---------------|
| `![iid]`: `[title]` | `@[user]` | `[file1, file2]` | 🔴/🟡/🟢 |

If no conflicts: "No overlapping changes detected in [N] open MRs."

---

## Test Coverage Assessment

| Changed File | Related Test Files | Status |
|-------------|-------------------|--------|
| `[src/file]` | `[test/file_test]` | ✅ Tests exist |
| `[src/file]` | None found | ❌ No tests — **action needed** |
| `[src/file]` | `[test/file_test]` | ⚠️ Tests exist but may not cover new changes |

---

## Escalation Flags

| Flag | Detected | Details |
|------|----------|---------|
| Deleted exports | ✅/❌ | `[list of deleted symbols]` |
| API contract changes | ✅/❌ | `[endpoints affected]` |
| DB schema changes | ✅/❌ | `[migration files]` |
| Auth/security changes | ✅/❌ | `[files]` |
| CI/CD config changes | ✅/❌ | `[files]` |
| Major dependency bumps | ✅/❌ | `[packages]` |

---

## Recommendations

| Priority | Action | Reason |
|----------|--------|--------|
| 🔴 P0 | `[action]` | `[why — reference specific finding]` |
| 🟡 P1 | `[action]` | `[why]` |
| 🟢 P2 | `[action]` | `[why]` |

---

## Merge Readiness Checklist

- [ ] All 🔴 critical risks reviewed and mitigated
- [ ] Tests added/updated for changed interfaces
- [ ] No unresolved conflicts with open MRs
- [ ] Breaking changes documented
- [ ] Downstream consumers notified (if API changed)
- [ ] Migration plan documented (if DB changed)
