#!/usr/bin/env bash
set -euo pipefail

VERSION="1.0.0"

REVIEW_FILES=(
  ".github/agents/code-review.agent.md"
  ".github/agents/code-review-pull.agent.md"
  ".github/agents/review-security.agent.md"
  ".github/agents/review-requirements.agent.md"
  ".github/skills/code-review/SKILL.md"
  ".github/skills/gitlab-review/SKILL.md"
  ".github/prompts/code-review.prompt.md"
  ".github/prompts/code-review-pull.prompt.md"
)

OPTIONAL_FILES=(
  ".vscode/mcp.json"
)

target_dir="."
source_spec=""
include_mcp=false
force=false
backup=false
dry_run=false

usage() {
  cat <<'USAGE'
Install the SDLC Toolkit review agents into a project repository.

Usage:
  install-review-agents.sh [options]

Options:
  --target DIR        Project repo to install into. Defaults to current directory.
  --source SOURCE     Toolkit source. Use a local checkout path or a GitLab raw base URL.
                     Example raw base: https://gitlab.example.com/group/sdlc-toolkit/-/raw/main
  --include-mcp       Also install .vscode/mcp.json. Off by default.
  --force             Overwrite changed destination files.
  --backup            Back up changed destination files before overwriting.
  --dry-run           Print planned actions without writing.
  -h, --help          Show this help.

Environment:
  SDLC_TOOLKIT_SOURCE     Same as --source.
  SDLC_TOOLKIT_RAW_BASE   Same as --source for raw GitLab installs.

Examples:
  # From a local sdlc-toolkit checkout:
  ./scripts/install-review-agents.sh --target /path/to/project --backup

  # From a GitLab-hosted toolkit repo:
  curl -fsSL https://gitlab.example.com/group/sdlc-toolkit/-/raw/main/scripts/install-review-agents.sh \
    | bash -s -- --source https://gitlab.example.com/group/sdlc-toolkit/-/raw/main --target .
USAGE
}

log() {
  printf '%s\n' "$*"
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

is_url() {
  case "$1" in
    http://*|https://*) return 0 ;;
    *) return 1 ;;
  esac
}

normalize_source() {
  local src="$1"
  if is_url "$src"; then
    src="${src%/}"
  else
    src="$(cd "$src" && pwd)"
  fi
  printf '%s\n' "$src"
}

script_repo_root() {
  local script_path="${BASH_SOURCE[0]}"
  local script_dir

  if [[ "$script_path" == */* ]]; then
    script_dir="$(cd "$(dirname "$script_path")" && pwd)"
    if [[ -f "$script_dir/../.github/agents/code-review.agent.md" ]]; then
      cd "$script_dir/.." && pwd
      return 0
    fi
  fi

  return 1
}

fetch_file() {
  local src="$1"
  local rel="$2"
  local out="$3"

  if is_url "$src"; then
    curl -fsSL "$src/$rel" -o "$out"
  else
    [[ -f "$src/$rel" ]] || die "Missing source file: $src/$rel"
    cp "$src/$rel" "$out"
  fi
}

install_one() {
  local src="$1"
  local rel="$2"
  local tmp_dir="$3"
  local dest="$target_dir/$rel"
  local fetched="$tmp_dir/${rel//\//__}"
  local backup_path

  fetch_file "$src" "$rel" "$fetched"

  if [[ -f "$dest" ]] && cmp -s "$fetched" "$dest"; then
    log "unchanged  $rel"
    return 0
  fi

  if [[ -e "$dest" && "$force" == false && "$backup" == false ]]; then
    die "Destination exists and differs: $dest. Use --backup or --force."
  fi

  if [[ "$dry_run" == true ]]; then
    if [[ -e "$dest" ]]; then
      if [[ "$backup" == true ]]; then
        log "would back up and install  $rel"
      else
        log "would overwrite          $rel"
      fi
    else
      log "would install            $rel"
    fi
    return 0
  fi

  mkdir -p "$(dirname "$dest")"

  if [[ -e "$dest" && "$backup" == true ]]; then
    backup_path="$dest.bak.$(date +%Y%m%d%H%M%S)"
    cp "$dest" "$backup_path"
    log "backup    $rel -> ${backup_path#$target_dir/}"
  fi

  cp "$fetched" "$dest"
  log "installed $rel"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      [[ $# -ge 2 ]] || die "--target requires a directory"
      target_dir="$2"
      shift 2
      ;;
    --source)
      [[ $# -ge 2 ]] || die "--source requires a local path or raw URL"
      source_spec="$2"
      shift 2
      ;;
    --include-mcp)
      include_mcp=true
      shift
      ;;
    --force)
      force=true
      shift
      ;;
    --backup)
      backup=true
      shift
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --version)
      printf '%s\n' "$VERSION"
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

if [[ "$force" == true && "$backup" == true ]]; then
  die "Use either --force or --backup, not both."
fi

if [[ -d "$target_dir" ]]; then
  target_dir="$(cd "$target_dir" && pwd)"
elif [[ "$dry_run" == true ]]; then
  target_parent="$(dirname "$target_dir")"
  target_base="$(basename "$target_dir")"
  [[ -d "$target_parent" ]] || die "Target parent does not exist: $target_parent"
  target_dir="$(cd "$target_parent" && pwd)/$target_base"
else
  target_dir="$(mkdir -p "$target_dir" && cd "$target_dir" && pwd)"
fi

if [[ -z "$source_spec" ]]; then
  source_spec="${SDLC_TOOLKIT_SOURCE:-${SDLC_TOOLKIT_RAW_BASE:-}}"
fi

if [[ -z "$source_spec" ]]; then
  if source_spec="$(script_repo_root)"; then
    :
  else
    die "No source found. Pass --source or set SDLC_TOOLKIT_RAW_BASE."
  fi
fi

source_spec="$(normalize_source "$source_spec")"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

log "SDLC Toolkit review-agent installer v$VERSION"
log "source: $source_spec"
log "target: $target_dir"
if [[ "$dry_run" == true ]]; then
  log "mode:   dry-run"
fi

for rel in "${REVIEW_FILES[@]}"; do
  install_one "$source_spec" "$rel" "$tmp_dir"
done

if [[ "$include_mcp" == true ]]; then
  for rel in "${OPTIONAL_FILES[@]}"; do
    install_one "$source_spec" "$rel" "$tmp_dir"
  done
fi

log "done"
