# Fixture: Test — Service Unavailable (ECONNREFUSED)

## Metadata

| Field | Value |
|-------|-------|
| **Error Category** | Test — Service Unavailable |
| **Stage** | `test` |
| **Expected Confidence** | 4/5 |
| **Retry-able** | No |
| **SKILL.md Pattern** | `ECONNREFUSED` / `Connection refused` |

## Input

### Job Log (sanitised)

```
$ npm test
PASS src/utils/helpers.test.ts (1.2s)
FAIL src/services/auth.service.test.ts (5.3s)

  ● Auth Service › should create a new session
    connect ECONNREFUSED 127.0.0.1:5432
      at TCPConnectWrap.afterConnect (node:net:1607:16)

Test Suites: 1 failed, 2 passed, 3 total
Tests:       3 failed, 12 passed, 15 total
ERROR: Job failed: exit code 1
```

### CI Config

```yaml
test:
  stage: test
  image: node:20-alpine
  needs: ["build"]
  script:
    - npm test
```

### Stage Map

```
scan:    sast (✅)
build:   build_app (✅)
test:    unit_tests (❌ FAILED)
publish: docker_push (⏭️ skipped)
```

## Expected Output

### Diagnosis

| Field | Expected |
|-------|----------|
| **Category** | Test — Service Unavailable |
| **Root Cause** | No PostgreSQL service container configured; port 5432 refused |
| **File** | `.gitlab-ci.yml` (job: `test`) |
| **Confidence** | 4/5 |

### Fix

```diff
 test:
   stage: test
   image: node:20-alpine
+  services:
+    - name: postgres:15
+      alias: db
+  variables:
+    DATABASE_URL: "postgresql://postgres:postgres@db:5432/test"
   script:
     - npm test
```

**Confidence:** 4/5 — strong match but DB URL may differ by project.
