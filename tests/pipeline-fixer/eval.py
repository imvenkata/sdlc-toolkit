#!/usr/bin/env python3
"""
Pipeline Fixer — Automated Eval Harness

Runs golden-path test fixtures against the Pipeline Fixer agent (via the
Anthropic API directly) and validates outputs against expected values.

Usage:
    python eval.py                     # Run all fixtures
    python eval.py --fixture build     # Run one fixture by name
    python eval.py --verbose           # Print full agent output

Prerequisites:
    pip install anthropic pyyaml
    export ANTHROPIC_API_KEY=sk-ant-...
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import anthropic
    import yaml
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install anthropic pyyaml")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Fixture definitions — mirrors tests/pipeline-fixer/fixtures/
# ---------------------------------------------------------------------------

@dataclass
class Fixture:
    name: str
    description: str
    # Input to send to the agent
    log_excerpt: str
    ci_config: str
    stage_map: str
    job_metadata: dict
    # Expected outputs to validate
    expected_category: str          # e.g. "Build", "Test", "Infrastructure"
    expected_confidence_min: int    # Minimum acceptable confidence (1-5)
    expected_confidence_max: int    # Maximum acceptable confidence
    expected_retry: bool            # Whether a retry (not code fix) is expected
    expected_keywords: list[str]    # Keywords that MUST appear in the diagnosis
    forbidden_keywords: list[str] = field(default_factory=list)  # Must NOT appear (e.g. raw secrets)


FIXTURES: list[Fixture] = [
    Fixture(
        name="build-missing-dep",
        description="Build stage — ModuleNotFoundError for missing npm packages",
        log_excerpt="""$ npm run build
> my-app@2.1.0 build
> tsc && vite build

src/services/auth.service.ts:3:26 - error TS2307: Cannot find module 'jsonwebtoken' or its corresponding type declarations.
src/services/auth.service.ts:4:22 - error TS2307: Cannot find module '@auth/core' or its corresponding type declarations.
Found 2 errors in the same file.
ERROR: "build" exited with code 2""",
        ci_config="""build:
  stage: build
  image: node:20-alpine
  script:
    - npm ci
    - npm run build""",
        stage_map="build: build_app (❌ FAILED)\ntest: unit_tests (⏭️ skipped)",
        job_metadata={"name": "build_app", "stage": "build", "exit_code": 2, "duration": 22},
        expected_category="Build",
        expected_confidence_min=4,
        expected_confidence_max=5,
        expected_retry=False,
        expected_keywords=["jsonwebtoken", "package.json", "dependency", "Cannot find module"],
        forbidden_keywords=["glpat-", "password=", "AWS_SECRET"],
    ),
    Fixture(
        name="test-service-missing",
        description="Test stage — ECONNREFUSED because no DB service configured",
        log_excerpt="""FAIL src/services/auth.service.test.ts (5.3s)

  ● Auth Service › should create a new session
    connect ECONNREFUSED 127.0.0.1:5432
      at TCPConnectWrap.afterConnect (node:net:1607:16)

Tests: 3 failed, 12 passed, 15 total
ERROR: Job failed: exit code 1""",
        ci_config="""test:
  stage: test
  image: node:20-alpine
  needs: ["build"]
  script:
    - npm test""",
        stage_map="build: build_app (✅)\ntest: unit_tests (❌ FAILED)",
        job_metadata={"name": "unit_tests", "stage": "test", "exit_code": 1, "duration": 14},
        expected_category="Test",
        expected_confidence_min=4,
        expected_confidence_max=5,
        expected_retry=False,
        expected_keywords=["ECONNREFUSED", "postgres", "service", "5432"],
    ),
    Fixture(
        name="infra-network-timeout",
        description="Build stage — ETIMEDOUT network failure (should retry, not code fix)",
        log_excerpt="""$ npm ci
npm ERR! code ETIMEDOUT
npm ERR! syscall connect
npm ERR! errno ETIMEDOUT
npm ERR! network request to https://registry.npmjs.org/express failed, reason: connect ETIMEDOUT 104.16.23.35:443
npm ERR! network This is a problem related to network connectivity.
ERROR: Job failed: exit code 1""",
        ci_config="""build:
  stage: build
  image: node:20-alpine
  script:
    - npm ci
    - npm run build""",
        stage_map="build: build_app (❌ FAILED)\ntest: unit_tests (⏭️ skipped)",
        job_metadata={"name": "build_app", "stage": "build", "exit_code": 1, "duration": 30},
        expected_category="Infrastructure",
        expected_confidence_min=3,
        expected_confidence_max=5,
        expected_retry=True,
        expected_keywords=["ETIMEDOUT", "network", "retry"],
    ),
]


# ---------------------------------------------------------------------------
# Agent prompt builder
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a CI/CD pipeline failure diagnosis expert. 
You will receive a job log excerpt, CI configuration, stage map, and job metadata.
Perform a diagnosis and return your analysis in this exact JSON format:

{
  "category": "<Build|Test|Infrastructure|CI Config|Publish|Deploy|Scan>",
  "root_cause": "<one sentence>",
  "confidence": <1-5>,
  "retry_recommended": <true|false>,
  "files_to_fix": ["<file_path>"],
  "error_keywords": ["<key terms from the log>"],
  "diagnosis_summary": "<2-3 sentences>"
}

Rules:
- category must be one of the enum values
- confidence: 5=exact pattern match, 4=strong match, 3=probable, 2=uncertain, 1=guess
- retry_recommended: true ONLY for infrastructure/network/flaky failures
- files_to_fix: empty list if retry recommended
- Output ONLY valid JSON, no markdown fences"""


def build_user_message(fixture: Fixture) -> str:
    return f"""## Job Log
```
{fixture.log_excerpt}
```

## CI Configuration
```yaml
{fixture.ci_config}
```

## Stage Map
```
{fixture.stage_map}
```

## Job Metadata
```json
{json.dumps(fixture.job_metadata, indent=2)}
```

Diagnose this pipeline failure."""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    fixture_name: str
    passed: bool
    score: int          # 0-100
    failures: list[str]
    warnings: list[str]
    raw_response: str
    parsed: Optional[dict]
    duration_ms: int


def validate(fixture: Fixture, response_text: str, duration_ms: int) -> ValidationResult:
    failures = []
    warnings = []
    score = 100

    # Try to parse JSON
    parsed = None
    try:
        # Strip markdown fences if model added them despite instructions
        cleaned = re.sub(r"```(?:json)?\n?", "", response_text).strip()
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        failures.append(f"Response is not valid JSON: {e}")
        return ValidationResult(fixture.name, False, 0, failures, warnings, response_text, None, duration_ms)

    # 1. Category match
    actual_category = parsed.get("category", "")
    if actual_category != fixture.expected_category:
        failures.append(
            f"Category: expected '{fixture.expected_category}', got '{actual_category}'"
        )
        score -= 25

    # 2. Confidence range
    actual_confidence = parsed.get("confidence", 0)
    if not (fixture.expected_confidence_min <= actual_confidence <= fixture.expected_confidence_max):
        failures.append(
            f"Confidence: expected {fixture.expected_confidence_min}-{fixture.expected_confidence_max}, "
            f"got {actual_confidence}"
        )
        score -= 20

    # 3. Retry recommendation
    actual_retry = parsed.get("retry_recommended", False)
    if actual_retry != fixture.expected_retry:
        failures.append(
            f"Retry: expected {fixture.expected_retry}, got {actual_retry}"
        )
        score -= 20

    # 4. Expected keywords in diagnosis_summary or root_cause
    searchable = (
        (parsed.get("diagnosis_summary") or "") + " " +
        (parsed.get("root_cause") or "") + " " +
        str(parsed.get("error_keywords") or [])
    ).lower()

    missing_keywords = []
    for kw in fixture.expected_keywords:
        if kw.lower() not in searchable:
            missing_keywords.append(kw)

    if missing_keywords:
        failures.append(f"Missing expected keywords: {missing_keywords}")
        score -= min(25, 5 * len(missing_keywords))

    # 5. Forbidden keywords (security check — no raw secrets)
    full_response = response_text.lower()
    for kw in fixture.forbidden_keywords:
        if kw.lower() in full_response:
            failures.append(f"SECURITY: Forbidden keyword found in response: '{kw}'")
            score -= 30

    # 6. Warnings (non-failing)
    if actual_confidence == 5 and fixture.expected_confidence_max < 5:
        warnings.append("Overconfident: model returned 5/5 but expected max was lower")
    if duration_ms > 15000:
        warnings.append(f"Slow response: {duration_ms}ms (expected <15s)")

    passed = len(failures) == 0
    return ValidationResult(
        fixture_name=fixture.name,
        passed=passed,
        score=max(0, score),
        failures=failures,
        warnings=warnings,
        raw_response=response_text,
        parsed=parsed,
        duration_ms=duration_ms,
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_fixture(client: anthropic.Anthropic, fixture: Fixture, verbose: bool) -> ValidationResult:
    print(f"  Running: {fixture.name} — {fixture.description}")

    start = time.time()
    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(fixture)}],
        )
        duration_ms = int((time.time() - start) * 1000)
        response_text = message.content[0].text
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        result = ValidationResult(
            fixture_name=fixture.name,
            passed=False,
            score=0,
            failures=[f"API error: {e}"],
            warnings=[],
            raw_response="",
            parsed=None,
            duration_ms=duration_ms,
        )
        print(f"    ❌ API ERROR: {e}")
        return result

    result = validate(fixture, response_text, duration_ms)

    if verbose:
        print(f"\n    --- Raw Response ---\n{response_text}\n    ---\n")

    status = "✅ PASS" if result.passed else "❌ FAIL"
    print(f"    {status}  score={result.score}/100  time={duration_ms}ms")

    for f in result.failures:
        print(f"    ✗ {f}")
    for w in result.warnings:
        print(f"    ⚠ {w}")

    return result


def print_summary(results: list[ValidationResult]) -> None:
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    avg_score = sum(r.score for r in results) / max(total, 1)
    avg_time = sum(r.duration_ms for r in results) / max(total, 1)

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} fixtures passed")
    print(f"Average score: {avg_score:.0f}/100")
    print(f"Average response time: {avg_time:.0f}ms")
    print("=" * 60)

    if passed < total:
        print("\nFailed fixtures:")
        for r in results:
            if not r.passed:
                print(f"  • {r.fixture_name}")
                for f in r.failures:
                    print(f"      - {f}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline Fixer eval harness")
    parser.add_argument("--fixture", help="Run a specific fixture by name")
    parser.add_argument("--verbose", action="store_true", help="Print full agent responses")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    fixtures_to_run = FIXTURES
    if args.fixture:
        fixtures_to_run = [f for f in FIXTURES if args.fixture in f.name]
        if not fixtures_to_run:
            available = [f.name for f in FIXTURES]
            print(f"ERROR: No fixture matching '{args.fixture}'. Available: {available}")
            sys.exit(1)

    print(f"\nPipeline Fixer Eval — {len(fixtures_to_run)} fixture(s)\n")

    results = []
    for fixture in fixtures_to_run:
        result = run_fixture(client, fixture, args.verbose)
        results.append(result)
        print()

    print_summary(results)

    # Exit non-zero if any fixture failed (for CI integration)
    if any(not r.passed for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
