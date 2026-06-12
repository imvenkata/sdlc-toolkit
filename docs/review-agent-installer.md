# Review Agent Installer

Use `scripts/install-review-agents.sh` to install the reusable code review pack into a project repository.

The installer copies only the review-pack files:

- `.github/agents/code-review.agent.md`
- `.github/agents/code-review-pull.agent.md`
- `.github/agents/review-security.agent.md`
- `.github/agents/review-requirements.agent.md`
- `.github/skills/code-review/SKILL.md`
- `.github/skills/gitlab-review/SKILL.md`
- `.github/skills/review-state/SKILL.md`
- `.github/prompts/code-review.prompt.md`
- `.github/prompts/code-review-pull.prompt.md`

It does not install or overwrite `.github/copilot-instructions.md`.

The `review-state` skill enables incremental MR reviews by storing compact `ai-review-state:v1` metadata in confirmed MR summary/state comments.

## Install From GitLab

Replace the URL with your hosted `sdlc-toolkit` project raw URL:

```bash
curl -fsSL https://gitlab.example.com/group/sdlc-toolkit/-/raw/main/scripts/install-review-agents.sh \
  | bash -s -- \
      --source https://gitlab.example.com/group/sdlc-toolkit/-/raw/main \
      --target .
```

Use `--backup` to preserve any existing changed files before replacement:

```bash
curl -fsSL https://gitlab.example.com/group/sdlc-toolkit/-/raw/main/scripts/install-review-agents.sh \
  | bash -s -- \
      --source https://gitlab.example.com/group/sdlc-toolkit/-/raw/main \
      --target . \
      --backup
```

Use `--force` only when you intentionally want to overwrite existing review-pack files.

## Install From A Local Toolkit Checkout

```bash
/path/to/sdlc-toolkit/scripts/install-review-agents.sh --target /path/to/project --backup
```

When the script is run from inside the toolkit checkout, `--source` is optional.

## Preview Changes

```bash
scripts/install-review-agents.sh --target /path/to/project --dry-run
```

The installer refuses to overwrite changed destination files unless `--backup` or `--force` is supplied.

## Optional MCP Config

The review pack assumes the consuming project already has GitLab MCP configured for Copilot. To copy this toolkit's `.vscode/mcp.json` as a starter config, pass:

```bash
scripts/install-review-agents.sh --target /path/to/project --include-mcp --backup
```

This is off by default because many projects already have their own MCP config.
