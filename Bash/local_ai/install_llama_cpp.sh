#!/usr/bin/env bash
# Clone and build llama.cpp for local GGUF inference.

set -euo pipefail

REPO_URL="${LLAMA_CPP_REPO_URL:-https://github.com/ggml-org/llama.cpp.git}"
INSTALL_DIR="${LLAMA_CPP_DIR:-$HOME/.local/share/llama.cpp}"
BUILD_TYPE="Release"
ACCELERATOR="auto"
DRY_RUN=false

info() { echo "[INFO] $*"; }
die() { echo "[ERROR] $*" >&2; exit 1; }

usage() {
    echo "Usage: $0 [--dir PATH] [--accelerator auto|cpu|metal|cuda|hip] [--dry-run]"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 --accelerator metal"
    echo "  $0 --dir ./vendor/llama.cpp --accelerator cpu"
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dir) shift; INSTALL_DIR="$1"; shift ;;
            --accelerator) shift; ACCELERATOR="$1"; shift ;;
            --dry-run) DRY_RUN=true; shift ;;
            -h|--help) usage ;;
            *) die "Unknown argument: $1" ;;
        esac
    done
}

require_deps() {
    command -v git >/dev/null 2>&1 || die "'git' is required"
    command -v cmake >/dev/null 2>&1 || die "'cmake' is required"
}

cmake_flags() {
    case "$ACCELERATOR" in
        auto)
            if [[ "$(uname -s)" == "Darwin" ]]; then
                echo "-DGGML_METAL=ON"
            else
                echo ""
            fi
            ;;
        cpu) echo "" ;;
        metal) echo "-DGGML_METAL=ON" ;;
        cuda) echo "-DGGML_CUDA=ON" ;;
        hip) echo "-DGGML_HIP=ON" ;;
        *) die "Unsupported accelerator: $ACCELERATOR" ;;
    esac
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
    require_deps

    info "llama.cpp target: $INSTALL_DIR"
    if [[ ! -d "$INSTALL_DIR/.git" ]]; then
        run_cmd git clone "$REPO_URL" "$INSTALL_DIR"
    else
        info "Repository already exists; pulling latest changes"
        run_cmd git -C "$INSTALL_DIR" pull --ff-only
    fi

    flags="$(cmake_flags)"
    # shellcheck disable=SC2086
    run_cmd cmake -S "$INSTALL_DIR" -B "$INSTALL_DIR/build" -DCMAKE_BUILD_TYPE="$BUILD_TYPE" $flags
    run_cmd cmake --build "$INSTALL_DIR/build" --config "$BUILD_TYPE" --parallel

    info "Done. Binaries are under: $INSTALL_DIR/build/bin"
}

main "$@"
