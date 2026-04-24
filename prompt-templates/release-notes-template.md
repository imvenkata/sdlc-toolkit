# Release Notes Template

Use this template to structure release notes output.

---

# Release Notes: [Milestone/Version Title]

**Release Date**: `[due_date or today's date]`
**Milestone**: `[milestone title]`

---

## Highlights

[2-3 sentence summary of the most significant changes. Always mention breaking changes first, then key features, then security fixes.]

---

## ⚠️ Breaking Changes

> **These changes may require action from consumers of this project.**

- **[Clean Title]** (`![iid]`) — [One-line description of what broke and what to do]
  - Author: @[username]
  - Migration: [Steps if apparent, or "See MR for details"]

*If none: "No breaking changes in this release."*

---

## 🚀 Features

- **[Clean Title]** (`![iid]`) — [One-line description]
  - Author: @[username]
  - Resolves: #[issue_iid] *(if linked)*

---

## 🐛 Bug Fixes

- **[Clean Title]** (`![iid]`) — [What was fixed]
  - Author: @[username]
  - Resolves: #[issue_iid]

---

## ⚡ Performance

- **[Clean Title]** (`![iid]`) — [What improved]
  - Author: @[username]

---

## 🔒 Security

- **[Clean Title]** (`![iid]`) — [Security fix description]
  - Author: @[username]

---

## 🔧 Maintenance

- **[Clean Title]** (`![iid]`) — [What was refactored/cleaned]
  - Author: @[username]

---

## 📚 Documentation

- **[Clean Title]** (`![iid]`) — [Docs change]
  - Author: @[username]

---

## 📦 Dependencies

- **[Clean Title]** (`![iid]`) — [Dependency update]
  - Author: @[username]

---

## 📋 Other Changes

- **[Clean Title]** (`![iid]`) — [Description]
  - Author: @[username]

---

## Contributors

Thank you to the following contributors for this release:

- @[username1]
- @[username2]
- @[username3]

---

## Statistics

| Metric | Value |
|--------|-------|
| **MRs Merged** | `[N]` |
| **Issues Resolved** | `[N]` |
| **Contributors** | `[N]` |

---

*Notes:*
- *Omit any section that has no entries (except Breaking Changes — always show, even if "None")*
- *Order entries within each section by MR iid (ascending)*
- *Deduplicate MR/issue pairs — list once under the MR entry with `Resolves: #N`*
