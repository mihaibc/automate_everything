#!/usr/bin/env bash
# Create a Python virtual environment for local AI tooling.

set -euo pipefail

VENV_DIR=".venv-local-ai"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIREMENTS=""
INSTALL_DEFAULTS=true
DRY_RUN=false

DEFAULT_PACKAGES=(
    "huggingface-hub>=0.23.0"
    "requests>=2.31.0"
    "sentence-transformers>=3.0.0"
    "tiktoken>=0.7.0"
)

info() { echo "[INFO] $*"; }
die() { echo "[ERROR] $*" >&2; exit 1; }

usage() {
    echo "Usage: $0 [--venv PATH] [--requirements FILE] [--no-default-packages] [--dry-run]"
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --venv) shift; VENV_DIR="$1"; shift ;;
            --requirements) shift; REQUIREMENTS="$1"; shift ;;
            --no-default-packages) INSTALL_DEFAULTS=false; shift ;;
            --dry-run) DRY_RUN=true; shift ;;
            -h|--help) usage ;;
            *) die "Unknown argument: $1" ;;
        esac
    done
}

run_cmd() {
    if [[ "$DRY_RUN" == "true" ]]; then
        printf '[DRY-RUN]'
        printf ' %q' "$@"
        printf '\n'
    else
        "$@"
    fi
}

main() {
    parse_args "$@"
    command -v "$PYTHON_BIN" >/dev/null 2>&1 || die "Python not found: $PYTHON_BIN"

    run_cmd "$PYTHON_BIN" -m venv "$VENV_DIR"
    run_cmd "$VENV_DIR/bin/python" -m pip install --upgrade pip

    if [[ "$INSTALL_DEFAULTS" == "true" ]]; then
        run_cmd "$VENV_DIR/bin/python" -m pip install "${DEFAULT_PACKAGES[@]}"
    fi

    if [[ -n "$REQUIREMENTS" ]]; then
        [[ -f "$REQUIREMENTS" ]] || die "requirements file not found: $REQUIREMENTS"
        run_cmd "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS"
    fi

    info "Activate with: source $VENV_DIR/bin/activate"
}

main "$@"
