---
name: pipeline-fixer
version: "3.1.0"
description: "Single source of truth for CI/CD pipeline fixing: error pattern lookup tables by stage, CI config diagnostics, log sanitisation patterns, advanced CI config patterns, example YAML fixes, and commit conventions. Referenced by the Pipeline Fixer orchestrator and its sub-agents."
---

# Pipeline Fixer — Reference Material

Error pattern tables, CI config diagnostics, log sanitisation rules, and fix examples. Used by the Pipeline Fixer orchestrator and its sub-agents during analysis. No workflow duplication — the workflow lives in the agent file.

---

## Error Pattern Lookup Tables

### Scan Stage
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `sast-analyzer: error` | Scanner version mismatch | Pin scanner version or update template |
| `secret_detection: found N secrets` | Hardcoded secrets in code | Move to CI/CD variables, update code |
| `container_scanning: vulnerability` | Base image CVE | Update base image in Dockerfile |
| `allow_failure not set` | Scan blocking pipeline | Add `allow_failure: true` if advisory |

### Build Stage
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `ModuleNotFoundError` / `Cannot find module` | Missing dependency | Add to dependency file |
| `SyntaxError` / `Unexpected token` | Code syntax error | Fix syntax in source file |
| `error TS` (TypeScript) | Type error | Fix type annotation/cast |
| `docker build: COPY failed` | File missing from Docker context | Fix COPY path or `.dockerignore` |
| `go build: undefined` | Missing import | Fix import statement |
| `No matching version` / `Could not resolve` | Dep version conflict | Fix version constraint |
| `ENOMEM` / `heap out of memory` | Insufficient memory | Increase `NODE_OPTIONS=--max-old-space-size` or runner resources |

### Test Stage
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `AssertionError` / `Expected X got Y` | Test failure or regression | Fix code or update assertion |
| `ECONNREFUSED` / `Connection refused` | Service not available | Add `services:` to job config |
| `Timeout` / `exceeded deadline` | Slow test or missing timeout | Increase timeout or optimize |
| `fixture not found` / `FileNotFoundError` | Missing test fixture | Create fixture or fix path |
| `SQLITE_CANTOPEN` / `database is locked` | DB issue in CI | Use in-memory DB or add service |

### Publish Stage
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `unauthorized` / `access denied` | Registry auth failure | Fix Docker login step / check vars |
| `manifest unknown` | Wrong image tag | Fix tag construction in CI config |
| `no space left on device` | Disk full | Add cleanup step or use smaller base |
| `denied: requested access` | Push permission | Verify `CI_REGISTRY_USER` / `CI_REGISTRY_PASSWORD` |

### Deploy Stage
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `kubectl: error` | K8s config issue | Fix manifest or kubeconfig |
| `health check failed` | App not starting | Check env vars, port, probes |
| `ImagePullBackOff` | Can't pull image | Verify image name/tag, registry auth |
| `CrashLoopBackOff` | App crash loop | Check app logs, env vars, config |
| `ssh: connect to host` | SSH failure | Verify SSH key, host config |
| `helm: release failed` | Helm chart error | Check values.yaml, chart version |

### Azure Function App Deploy
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `ERROR: Please run 'az login'` / `AADSTS` | Azure CLI not authenticated | Add `az login --service-principal` step with correct `--tenant` |
| `ERROR: The subscription '...' could not be found` | Wrong subscription context | Add `az account set --subscription $AZURE_SUBSCRIPTION_ID` |
| `ERROR: The Resource '...' was not found` | Function App name mismatch or wrong RG | Verify `AZURE_FUNCTIONAPP_NAME` and `AZURE_RESOURCE_GROUP` variables |
| `ERROR: (AuthorizationFailed)` / `does not have authorization` | Service principal missing RBAC role | Assign `Contributor` role on the Function App resource scope |
| `Deployment failed with status code 409` | Function App locked or slot busy | Wait and retry, or use staging slot with swap |
| `Deployment failed with status code 503` / `Site Unavailable` | Function App stopped or platform issue | Start app first: `az functionapp start`, then retry deploy |
| `zip deployment failed` / `remote build failed` | Package build failure during remote build | Switch to local build (`ENABLE_ORYX_BUILD=false`) or fix build deps |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` error | Remote build conflict | Set `SCM_DO_BUILD_DURING_DEPLOYMENT=true` for Node.js, `false` for pre-built |
| `func azure functionapp publish: error` | Azure Functions Core Tools failure | Verify tools version matches runtime: `func --version` |
| `Missing value for AzureWebJobsStorage` | Storage account not configured | Set `AzureWebJobsStorage` connection string in app settings |
| `Timeout waiting for SCM site` | Kudu SCM site unresponsive | Retry — transient. If persistent, restart SCM: `az webapp restart` |
| `WEBSITE_RUN_FROM_PACKAGE=1` + file not found | Deployment package not uploaded | Verify blob URL in `WEBSITE_RUN_FROM_PACKAGE` or use zip deploy |
| `Could not find a part of the path '/home/site/wwwroot/host.json'` | Function App package corrupt | Redeploy with clean package: `--build remote` |
| `System.Private.CoreLib: Access to the path is denied` | File lock during deployment | Stop the function app before deploy or use `WEBSITE_ADD_SITENAME_BINDINGS_IN_APPHOST_CONFIG=1` |
| `Failed to start language worker` / `Worker was unable to load` | Runtime version mismatch | Set `FUNCTIONS_EXTENSION_VERSION=~4` and correct `linuxFxVersion` |
| `az functionapp config appsettings set: error` | App settings update failure | Check JSON format: `--settings "KEY=VALUE"` not `--settings KEY VALUE` |
| `Health check failed for slot` / `Swap failed` | Staging slot health check failing | Fix health endpoint or adjust `healthcheckpath` in config |

### Infrastructure (Retry-able)
| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `OOMKilled` / `out of memory` | Runner OOM | Increase runner resources or optimize |
| `network timeout` / `TLS handshake` | Network issue | Retry — transient |
| `dial tcp: lookup` | DNS resolution failure | Retry — transient |
| `runner system failure` | Runner crash | Retry — runner issue |
| `stuck or timeout` | Job hung | Retry with increased timeout |

---

## CI Config Diagnostics

| Symptom | Likely CI Config Issue | Fix |
|---------|----------------------|-----|
| Pipeline won't create | YAML syntax error | Fix indentation, quoting, anchors |
| "unknown stage" | Job references undefined stage | Add stage to `stages:` list |
| "dependency cycle" | Circular `needs` | Reorganize job dependencies |
| Job skipped unexpectedly | `rules:`/`only:`/`except:` mismatch | Fix trigger conditions |
| "image not found" | Wrong `image:` reference | Fix image name/tag |
| Next job can't find files | `artifacts:paths` wrong | Match artifact path to build output |
| "file not found in include" | Wrong `include:` path | Fix path and ref |
| Variable undefined | Missing `variables:` or CI/CD setting | Add to config or project settings |
| Service container unreachable | `services:` misconfigured | Check image, alias, and connection string |

---

## Log Sanitisation Patterns

Before processing job logs, the log-analyser sub-agent MUST redact these patterns:

### Token / Key Patterns
| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| GitLab PAT | `glpat-[A-Za-z0-9_-]{20,}` | `[REDACTED_TOKEN]` |
| GitHub PAT | `ghp_[A-Za-z0-9]{36,}` | `[REDACTED_TOKEN]` |
| AWS Access Key | `AKIA[A-Z0-9]{16}` | `[REDACTED_TOKEN]` |
| Generic API key | `(?i)(api[_-]?key|apikey)\s*[:=]\s*\S+` | `<key_name>=[REDACTED]` |
| Bearer token | `(?i)authorization:\s*bearer\s+\S+` | `Authorization: Bearer [REDACTED]` |

### Credential Patterns
| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| Password assignments | `(?i)(password|passwd|pwd|secret)\s*[:=]\s*\S+` | `<var_name>=[REDACTED]` |
| Connection strings with creds | `://[^:]+:[^@]+@` | `://[user]:[REDACTED]@` |
| Private keys | `-----BEGIN [A-Z ]+ PRIVATE KEY-----` ... `-----END` | `[REDACTED_PRIVATE_KEY]` |
| Docker registry login | `-p\s+\$?\{?CI_REGISTRY_PASSWORD\}?` | `-p [REDACTED]` |
| Base64 blobs in assignments | `(?i)(secret|token|key)\s*[:=]\s*[A-Za-z0-9+/=]{40,}` | `<var_name>=[REDACTED_BASE64]` |

### AWS / Cloud Specific
| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| AWS Secret Key | `(?i)aws_secret_access_key\s*[:=]\s*\S+` | `aws_secret_access_key=[REDACTED]` |
| AWS Session Token | `(?i)aws_session_token\s*[:=]\s*\S+` | `aws_session_token=[REDACTED]` |

### GCP / Azure / Other Cloud
| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| GCP service account key | `"private_key"\s*:\s*"-----BEGIN` (in JSON) | `"private_key": "[REDACTED_GCP_KEY]"` |
| GCP OAuth token | `ya29\.[A-Za-z0-9_-]{20,}` | `[REDACTED_GCP_TOKEN]` |
| Azure SAS token | `\?sv=.*\&sig=[A-Za-z0-9%+/=]+` | `?sv=...\&sig=[REDACTED_SAS]` |
| Azure connection string | `(?i)(AccountKey|SharedAccessKey)\s*=\s*[A-Za-z0-9+/=]+` | `<key_name>=[REDACTED]` |
| Azure SP client secret | `(?i)(client_secret|AZURE_CLIENT_SECRET)\s*[:=]\s*\S+` | `client_secret=[REDACTED]` |
| Azure tenant/subscription IDs in errors | (Keep — not sensitive, needed for diagnosis) | Do not redact |

### Third-Party Services
| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| Slack webhook URL | `https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+` | `[REDACTED_SLACK_WEBHOOK]` |
| Discord webhook URL | `https://discord(app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+` | `[REDACTED_DISCORD_WEBHOOK]` |
| npm registry token | `//registry\.npmjs\.org/:_authToken=\S+` | `//registry.npmjs.org/:_authToken=[REDACTED]` |
| PyPI token | `pypi-[A-Za-z0-9_-]{50,}` | `[REDACTED_PYPI_TOKEN]` |

### Interactive Prompts & Internal
| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| SSH passphrase prompt | `Enter passphrase for key` | `Enter passphrase for key [REDACTED]` |
| SSH host key | `ECDSA key fingerprint is SHA256:` | Keep (not sensitive — public info) |

### Custom Sanitisation Patterns

> Teams can extend this section with organisation-specific patterns without modifying the base patterns above.

| Pattern | Regex Hint | Replacement |
|---------|-----------|-------------|
| *Internal hostnames* | `(?i)[a-z0-9-]+\.(internal|corp|local)\.[a-z]+` | `[REDACTED_INTERNAL_HOST]` |
| *Add your patterns here* | — | — |

---

## Advanced CI Config Patterns

### YAML Anchors & Aliases
When fixing CI config that uses anchors (`&`) and aliases (`*` / `<<:`), preserve them:
```yaml
.defaults: &defaults
  image: node:18
  tags: [docker]

build:
  <<: *defaults
  stage: build
  script:
    - npm ci && npm run build
```
**Common issue**: Anchor defined but alias reference broken. Fix the alias, don't inline the anchor content.

### DAG Pipelines (`needs:`)
When jobs use `needs:` instead of stage ordering:
```yaml
build:
  stage: build
  script: npm run build

test:
  stage: test
  needs: ["build"]
  script: npm test
```
**Common issues**:
- `needs:` references a job that doesn't exist (renamed/removed)
- Circular `needs:` dependency
- `needs:` job is in a later stage (not allowed)

### Multi-Project Pipelines
```yaml
trigger_downstream:
  stage: deploy
  trigger:
    project: group/downstream-project
    branch: main
    strategy: depend
```
**Common issues**: Wrong project path, branch doesn't exist, insufficient permissions.

### Component CI (CI/CD Catalog)
```yaml
include:
  - component: $CI_SERVER_FQDN/group/component@1.0.0
```
**Common issues**: Component version not found, component inputs not provided.

### Rules & Workflow
```yaml
workflow:
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```
**Common issue**: Pipeline doesn't trigger because no `workflow:rules` match the current context.

---

## Example YAML Fixes

### Add service for test database
```yaml
test:
  stage: test
  services:
    - name: postgres:15
      alias: db
  variables:
    DATABASE_URL: "postgresql://postgres:postgres@db:5432/test"
```

### Fix Docker login for publish
```yaml
publish:
  stage: publish
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Make scan non-blocking
```yaml
sast:
  stage: scan
  allow_failure: true
```

### Increase Node.js memory for build
```yaml
build:
  stage: build
  variables:
    NODE_OPTIONS: "--max-old-space-size=4096"
  script:
    - npm ci
    - npm run build
```

### Fix cache configuration
```yaml
.cache-template: &cache-config
  cache:
    key: "${CI_COMMIT_REF_SLUG}"
    paths:
      - node_modules/
    policy: pull-push

build:
  <<: *cache-config
  stage: build
  script:
    - npm ci --cache .npm
    - npm run build
```

### Azure Function App — Service Principal login
```yaml
.azure-login: &azure-login
  before_script:
    - az login --service-principal
        --username $AZURE_CLIENT_ID
        --password $AZURE_CLIENT_SECRET
        --tenant $AZURE_TENANT_ID
    - az account set --subscription $AZURE_SUBSCRIPTION_ID
```
**Common issue**: Missing `--tenant` or wrong subscription. Always set subscription explicitly.

### Azure Function App — Zip deploy (Node.js)
```yaml
deploy-function:
  stage: deploy
  image: mcr.microsoft.com/azure-cli:latest
  <<: *azure-login
  script:
    - cd $CI_PROJECT_DIR
    - zip -r function-app.zip . -x '.git/*' 'node_modules/*' '.gitlab-ci.yml'
    - az functionapp deployment source config-zip
        --resource-group $AZURE_RESOURCE_GROUP
        --name $AZURE_FUNCTIONAPP_NAME
        --src function-app.zip
        --build-remote true
  environment:
    name: dev
  only:
    - develop
```
**Common issues**: Missing `--build-remote true` for Node.js (causes missing `node_modules`). Wrong zip contents (including `.git/` inflates package).

### Azure Function App — Publish with Core Tools
```yaml
deploy-function:
  stage: deploy
  image: mcr.microsoft.com/azure-functions/node:4-node20
  <<: *azure-login
  script:
    - npm ci --production
    - func azure functionapp publish $AZURE_FUNCTIONAPP_NAME
        --javascript
        --no-build
  environment:
    name: dev
```
**Common issues**: Mismatch between `--javascript`/`--typescript` flag and actual runtime. Using `--no-build` without running `npm ci` first.

### Azure Function App — Slot deploy with swap
```yaml
deploy-staging:
  stage: deploy
  image: mcr.microsoft.com/azure-cli:latest
  <<: *azure-login
  script:
    - az functionapp deployment source config-zip
        --resource-group $AZURE_RESOURCE_GROUP
        --name $AZURE_FUNCTIONAPP_NAME
        --slot staging
        --src function-app.zip
        --build-remote true
    - az functionapp start
        --resource-group $AZURE_RESOURCE_GROUP
        --name $AZURE_FUNCTIONAPP_NAME
        --slot staging
    # Health check before swap
    - |
      HEALTH=$(curl -s -o /dev/null -w '%{http_code}' https://$AZURE_FUNCTIONAPP_NAME-staging.azurewebsites.net/api/health)
      if [ "$HEALTH" != "200" ]; then
        echo "Health check failed with HTTP $HEALTH"
        exit 1
      fi
    - az functionapp deployment slot swap
        --resource-group $AZURE_RESOURCE_GROUP
        --name $AZURE_FUNCTIONAPP_NAME
        --slot staging
        --target-slot production
  environment:
    name: production
  when: manual
```
**Common issues**: Swap fails with 409 if slot is stopped. Health check path not configured. Missing `az functionapp start` before health check.

### Azure Function App — App settings from CI variables
```yaml
configure-app:
  stage: deploy
  image: mcr.microsoft.com/azure-cli:latest
  <<: *azure-login
  script:
    - az functionapp config appsettings set
        --resource-group $AZURE_RESOURCE_GROUP
        --name $AZURE_FUNCTIONAPP_NAME
        --settings
          "APPINSIGHTS_INSTRUMENTATIONKEY=$APPINSIGHTS_KEY"
          "AzureWebJobsStorage=$STORAGE_CONNECTION_STRING"
          "FUNCTIONS_EXTENSION_VERSION=~4"
          "WEBSITE_NODE_DEFAULT_VERSION=~20"
          "CUSTOM_SETTING=$CUSTOM_VALUE"
```
**Common issue**: Using `KEY VALUE` format instead of `"KEY=VALUE"`. Missing quotes around values with special characters.

---

## Commit Message Convention

```
fix(<scope>): <what was fixed> — iteration <N>/<max>

Pipeline: #<pipeline_id>
Job: <job_name> (stage: <stage>)
Error: <one-line error summary>
```

Scopes: `ci`, `build`, `test`, `deps`, `docker`, `deploy`, `azure`, `scan`
