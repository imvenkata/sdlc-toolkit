# Azure Function App — Auth Failure Fixture

## Metadata
- **Category**: Azure Function App Deploy
- **Subcategory**: Authentication — Service Principal
- **Expected Confidence**: 4-5/5
- **Expected Action**: Fix CI config (add `--tenant` flag)
- **Retry-able**: No

## Input: Failed Job Log
```
$ az login --service-principal --username $AZURE_CLIENT_ID --password $AZURE_CLIENT_SECRET
ERROR: AADSTS700016: Application with identifier 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' was not found in the directory 'Default Directory'. This can happen if the application has not been installed by the administrator of the tenant or consented to by any user in the tenant. You may have sent your authentication request to the wrong tenant.
Trace ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Correlation ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Timestamp: 2026-04-26 10:00:00Z
ERROR: Job failed: exit code 1
```

## Input: CI Configuration
```yaml
stages:
  - build
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

deploy-dev:
  stage: deploy
  image: mcr.microsoft.com/azure-cli:latest
  before_script:
    - az login --service-principal
        --username $AZURE_CLIENT_ID
        --password $AZURE_CLIENT_SECRET
  script:
    - zip -r function-app.zip . -x '.git/*'
    - az functionapp deployment source config-zip
        --resource-group $AZURE_RESOURCE_GROUP
        --name $AZURE_FUNCTIONAPP_NAME
        --src function-app.zip
  environment:
    name: dev
  only:
    - develop
```

## Input: Stage Map
```
build:  build_app (✅)
deploy: deploy-dev (❌ FAILED)
```

## Input: Job Metadata
```json
{
  "name": "deploy-dev",
  "stage": "deploy",
  "exit_code": 1,
  "duration": 8,
  "runner": "shared-linux"
}
```

## Expected Output

### Diagnosis
- **Category**: Azure Function App Deploy
- **Root Cause**: `az login` missing `--tenant` flag — the service principal was looked up in the wrong Azure AD directory
- **Error Pattern Match**: `AADSTS700016` → wrong tenant
- **Confidence**: 4/5 or 5/5

### Proposed Fix
```diff
  before_script:
    - az login --service-principal
        --username $AZURE_CLIENT_ID
        --password $AZURE_CLIENT_SECRET
+       --tenant $AZURE_TENANT_ID
+   - az account set --subscription $AZURE_SUBSCRIPTION_ID
```

### Validation Checklist
- [ ] Agent correctly identifies `AADSTS` as an Azure auth error
- [ ] Agent does NOT classify this as a generic "script error"
- [ ] Agent proposes adding `--tenant` (not re-creating the service principal)
- [ ] Agent also adds `az account set --subscription` as a best practice
- [ ] Confidence is ≥ 4 (strong pattern match)
- [ ] `AZURE_CLIENT_SECRET` value is sanitised if it appears in the log
- [ ] Commit scope is `fix(azure):` not `fix(deploy):`
