# Fixture: Build — Missing Dependency (ModuleNotFoundError)

## Metadata

| Field | Value |
|-------|-------|
| **Error Category** | Build — Missing Dependency |
| **Stage** | `build` |
| **Expected Confidence** | 5/5 |
| **Retry-able** | No |
| **SKILL.md Pattern** | `ModuleNotFoundError` / `Cannot find module` |

---

## Input

### Job Log (sanitised)

```
Running with gitlab-runner 17.5.0 (abc123de)
  on docker-runner-01 zYx987
Preparing the "docker" executor
Using Docker executor with image node:20-alpine ...
Pulling docker image node:20-alpine ...
Using docker image sha256:a1b2c3d4e5f6 for node:20-alpine ...
Preparing environment
Running on runner-zYx987-project-12345-concurrent-0 via runner-host-01...
Getting source from Git repository
Fetching changes with git depth set to 20...
Reinitialized existing Git repository in /builds/my-group/my-app/.git/
Checking out e4f5a6b7 as feature/add-auth...
Skipping Git submodules setup
Executing "step_script" stage of the job script
$ npm ci
npm warn deprecated @types/lodash@4.14.191: This is a stub types definition. lodash provides its own type definitions.
added 1247 packages in 18.2s
$ npm run build

> my-app@2.1.0 build
> tsc && vite build

src/services/auth.service.ts:3:26 - error TS2307: Cannot find module 'jsonwebtoken' or its corresponding type declarations.

3 import jwt from 'jsonwebtoken';
                   ~~~~~~~~~~~~~~

src/services/auth.service.ts:4:22 - error TS2307: Cannot find module '@auth/core' or its corresponding type declarations.

4 import { Auth } from '@auth/core';
                       ~~~~~~~~~~~~

Found 2 errors in the same file.

ERROR: "build" exited with code 2
Cleaning up project directory and file based variables
ERROR: Job failed: exit code 2
```

### CI Config

```yaml
stages:
  - scan
  - build
  - test
  - publish
  - deploy

build:
  stage: build
  image: node:20-alpine
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour
  cache:
    key: "${CI_COMMIT_REF_SLUG}"
    paths:
      - node_modules/
```

### Stage Map

```
scan:    sast (✅), secret_detection (✅)
build:   build_app (❌ FAILED)
test:    unit_tests (⏭️ skipped), integration (⏭️ skipped)
publish: docker_push (⏭️ skipped)
deploy:  deploy_staging (⏭️ skipped)
```

### Job Metadata

| Field | Value |
|-------|-------|
| **Job Name** | `build_app` |
| **Stage** | `build` |
| **Runner** | `docker-runner-01` |
| **Duration** | `22s` |
| **Exit Code** | `2` |

---

## Expected Output

### Diagnosis (from log-analyser)

| Field | Expected Value |
|-------|---------------|
| **Category** | Build |
| **Error** | `Cannot find module 'jsonwebtoken'` and `Cannot find module '@auth/core'` |
| **Root Cause** | Missing dependencies: `jsonwebtoken` and `@auth/core` are imported in `src/services/auth.service.ts` but not listed in `package.json` |
| **File** | `package.json` |
| **Confidence** | 5/5 |
| **Retry-able** | No |
| **Sanitisation** | 0 values redacted (log is clean) |

### Fix (from fix-generator)

**Expected approach:** Add `jsonwebtoken` and `@auth/core` to `package.json` dependencies.

**Expected diff:**
```diff
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
+   "jsonwebtoken": "^9.0.0",
+   "@auth/core": "^0.30.0"
  }
```

**Expected confidence:** 5/5 (exact pattern match from SKILL.md)

**Expected commit:**
```
fix(deps): add jsonwebtoken and @auth/core — iteration 1/3

Pipeline: #12345
Job: build_app (stage: build)
Error: Cannot find module 'jsonwebtoken'
```

### Key Report Fields

- Final Status: depends on push + re-trigger
- Error Category: Build — Missing Dependency
- Auto-fix Safe: Yes (confidence ≥ 4)
- Sanitisation notice: 0 sensitive values redacted
