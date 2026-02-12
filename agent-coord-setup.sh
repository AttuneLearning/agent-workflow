#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
CLAUDE_SETUP="$SCRIPT_DIR/claude-workflow/setup.sh"
CODEX_INSTALL="$SCRIPT_DIR/codex-workflow/install.sh"

MODE="both" # claude | codex | both
TEAM=""
LIST_TEAMS=0
declare -a CODEX_ARGS=()

usage() {
  cat <<'EOF'
Unified agent coordination setup.

Usage:
  ./agent-coord-setup.sh [options]

Modes:
  --both                 Run Claude setup, then Codex install (default)
  --claude-only          Run only .claude-workflow/setup.sh
  --codex-only           Run only .codex-workflow/install.sh

Codex options:
  --team <id>            Team id for Codex install (required for codex modes unless prompted)
  --list-teams           List Codex teams and exit
  --target <path>        Forwarded to Codex installer
  --pack-name <name>     Forwarded to Codex installer
  --workspace-root <p>   Forwarded to Codex installer
  --force                Forwarded to Codex installer
  --dry-run              Forwarded to Codex installer
  --no-local-config      Forwarded to Codex installer

Other:
  -h, --help             Show this help
EOF
}

require_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "Error: required file not found: $file" >&2
    exit 1
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --both)
        MODE="both"
        shift
        ;;
      --claude-only)
        MODE="claude"
        shift
        ;;
      --codex-only)
        MODE="codex"
        shift
        ;;
      --team)
        [[ $# -ge 2 ]] || { echo "Error: --team requires a value" >&2; exit 2; }
        TEAM="$2"
        shift 2
        ;;
      --list-teams)
        LIST_TEAMS=1
        shift
        ;;
      --target|--pack-name|--workspace-root)
        [[ $# -ge 2 ]] || { echo "Error: $1 requires a value" >&2; exit 2; }
        CODEX_ARGS+=("$1" "$2")
        shift 2
        ;;
      --force|--dry-run|--no-local-config)
        CODEX_ARGS+=("$1")
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Error: unknown option: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done
}

run_claude_setup() {
  require_file "$CLAUDE_SETUP"
  echo ""
  echo "==> Running Claude workflow setup"
  bash "$CLAUDE_SETUP"
}

prompt_team_if_needed() {
  if [[ -n "$TEAM" ]]; then
    return
  fi
  echo ""
  echo "Codex team not specified."
  bash "$CODEX_INSTALL" --list-teams
  read -r -p "Enter team id for Codex install: " TEAM
  if [[ -z "$TEAM" ]]; then
    echo "Error: team id is required for Codex install." >&2
    exit 2
  fi
}

run_codex_install() {
  require_file "$CODEX_INSTALL"

  if [[ "$LIST_TEAMS" -eq 1 ]]; then
    bash "$CODEX_INSTALL" --list-teams
    return
  fi

  prompt_team_if_needed

  echo ""
  echo "==> Running Codex workflow install for team: $TEAM"
  bash "$CODEX_INSTALL" --team "$TEAM" "${CODEX_ARGS[@]}"
}

main() {
  parse_args "$@"

  case "$MODE" in
    claude)
      run_claude_setup
      ;;
    codex)
      run_codex_install
      ;;
    both)
      run_claude_setup
      run_codex_install
      ;;
    *)
      echo "Error: invalid mode: $MODE" >&2
      exit 2
      ;;
  esac

  echo ""
  echo "agent-coord-setup complete."
}

main "$@"
