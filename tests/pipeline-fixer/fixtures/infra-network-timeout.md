# Fixture: Infrastructure — Network Timeout (DNS Failure)

## Metadata

| Field | Value |
|-------|-------|
| **Error Category** | Infrastructure — Network |
| **Stage** | `build` |
| **Expected Confidence** | 4/5 |
| **Retry-able** | Yes |
| **SKILL.md Pattern** | `dial tcp: lookup` / `network timeout` |

## Input

### Job Log (sanitised)

```
$ npm ci
npm ERR! code ETIMEDOUT
npm ERR! syscall connect
npm ERR! errno ETIMEDOUT
npm ERR! network request to https://registry.npmjs.org/express failed, reason: connect ETIMEDOUT 104.16.23.35:443
npm ERR! network This is a problem related to network connectivity.
npm ERR! network In most cases you are behind a proxy or have bad network settings.
npm ERR! network
npm ERR! network If you are behind a proxy, please make sure that the
npm ERR! network 'proxy' config is set properly. See: 'npm help config'

npm ERR! A complete log of this run can be found in:
npm ERR!     /root/.npm/_logs/2026-04-25T10_30_45_123Z-debug-0.log
ERROR: Job failed: exit code 1
```

### CI Config

```yaml
build:
  stage: build
  image: node:20-alpine
  script:
    - npm ci
    - npm run build
```

### Stage Map

```
scan:    sast (✅)
build:   build_app (❌ FAILED)
test:    unit_tests (⏭️ skipped)
```

## Expected Output

### Diagnosis

| Field | Expected |
|-------|----------|
| **Category** | Infrastructure — Network |
| **Root Cause** | npm registry unreachable due to network timeout (ETIMEDOUT) — transient infrastructure issue |
| **File** | N/A (infrastructure) |
| **Confidence** | 4/5 |
| **Retry-able** | Yes |

### Fix

**No code fix needed.** Expected action: `retry_pipeline_job(project_id, job_id)`.

> "This appears to be a transient network issue. Retrying the job before proposing any code changes."

### Key Report Fields

- Error Category: Infrastructure — Network
- Recommendation: Retry first
- Auto-fix Safe: Yes (retry, not code change)
