#!/usr/bin/env bash
# Pull one or more Ollama models and print a summary table.

set -euo pipefail

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
DEFAULT_MODELS=("llama3" "mistral" "phi3" "codellama")

info()  { echo "[INFO]  $*"; }
ok()    { echo "[OK]    $*"; }
warn()  { echo "[WARN]  $*"; }
die()   { echo "[ERROR] $*" >&2; exit 1; }

usage() {
    echo "Usage: $0 [--models \"model1 model2 ...\"]"
    echo ""
    echo "Options:"
    echo "  --models    Space-separated list of model names (default: ${DEFAULT_MODELS[*]})"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 --models \"llama3 gemma2\""
    exit 0
}

parse_args() {
    MODELS=("${DEFAULT_MODELS[@]}")
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --models)
                shift
                IFS=' ' read -r -a MODELS <<< "$1"
                shift
                ;;
            -h|--help) usage ;;
            *) die "Unknown argument: $1" ;;
        esac
    done
}

check_server() {
    if ! curl -sf "$OLLAMA_HOST" &>/dev/null; then
        die "Ollama server not reachable at $OLLAMA_HOST. Run install_ollama.sh first or start with 'ollama serve'."
    fi
}

pull_model() {
    local model="$1"
    info "Pulling '$model'..."
    if ollama pull "$model"; then
        ok "Pulled '$model'"
        return 0
    else
        warn "Failed to pull '$model'"
        return 1
    fi
}

print_summary() {
    echo ""
    echo "┌──────────────────────────────────────────────────────────┐"
    echo "│                   Installed Models                       │"
    echo "├──────────────────┬──────────────────┬────────────────────┤"
    printf "│ %-16s │ %-16s │ %-18s │\n" "Name" "Size" "Modified"
    echo "├──────────────────┼──────────────────┼────────────────────┤"

    while IFS= read -r line; do
        name=$(echo "$line" | awk '{print $1}')
        size=$(echo "$line" | awk '{print $3, $4}')
        modified=$(echo "$line" | awk '{print $5, $6}')
        printf "│ %-16s │ %-16s │ %-18s │\n" "$name" "$size" "$modified"
    done < <(ollama list | tail -n +2)

    echo "└──────────────────┴──────────────────┴────────────────────┘"
}

main() {
    parse_args "$@"

    info "=== Ollama Model Puller ==="
    check_server

    info "Models to pull: ${MODELS[*]}"
    echo ""

    succeeded=()
    failed=()

    for model in "${MODELS[@]}"; do
        if pull_model "$model"; then
            succeeded+=("$model")
        else
            failed+=("$model")
        fi
    done

    print_summary

    echo ""
    info "Results: ${#succeeded[@]} pulled, ${#failed[@]} failed"
    if (( ${#failed[@]} > 0 )); then
        warn "Failed models: ${failed[*]}"
    fi
}

main "$@"
