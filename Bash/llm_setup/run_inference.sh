#!/usr/bin/env bash
# CLI wrapper for Ollama inference via the REST API using curl.

set -euo pipefail

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
DEFAULT_MODEL="llama3"

usage() {
    echo "Usage: $0 --prompt <text> [options]"
    echo ""
    echo "Options:"
    echo "  --prompt TEXT      The prompt to send (required)"
    echo "  --model  NAME      Model name (default: $DEFAULT_MODEL)"
    echo "  --system TEXT      Optional system prompt"
    echo "  --stream           Stream output token by token"
    echo "  --host   URL       Ollama base URL (default: $OLLAMA_HOST)"
    echo "  --json             Print the raw JSON response"
    echo ""
    echo "Examples:"
    echo "  $0 --prompt \"Explain Docker in one sentence\""
    echo "  $0 --model mistral --prompt \"Write a haiku about Kubernetes\""
    echo "  $0 --stream --prompt \"Tell me a short story\""
    echo "  $0 --system \"You are a senior SRE\" --prompt \"How do I debug OOM kills?\""
    exit 0
}

die() { echo "[ERROR] $*" >&2; exit 1; }

parse_args() {
    PROMPT=""
    MODEL="$DEFAULT_MODEL"
    SYSTEM=""
    STREAM=false
    JSON_OUT=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prompt) shift; PROMPT="$1"; shift ;;
            --model)  shift; MODEL="$1";  shift ;;
            --system) shift; SYSTEM="$1"; shift ;;
            --host)   shift; OLLAMA_HOST="$1"; shift ;;
            --stream) STREAM=true; shift ;;
            --json)   JSON_OUT=true; shift ;;
            -h|--help) usage ;;
            *) die "Unknown argument: $1" ;;
        esac
    done

    if [[ -z "$PROMPT" ]]; then
        die "--prompt is required"
    fi
}

check_deps() {
    command -v curl &>/dev/null || die "'curl' is required but not installed"
    command -v python3 &>/dev/null || die "'python3' is required but not installed"
}

check_server() {
    curl -sf "$OLLAMA_HOST/api/tags" &>/dev/null || \
        die "Ollama server not reachable at $OLLAMA_HOST. Start it with 'ollama serve'."
}

# All JSON assembly is done in Python to correctly handle special characters,
# quotes, and newlines in model names, prompts, and system messages.
build_payload() {
    local stream_val="false"
    $STREAM && stream_val="true"

    python3 -c "
import json, sys
model  = sys.argv[1]
prompt = sys.argv[2]
system = sys.argv[3]
stream = sys.argv[4] == 'true'
msgs = []
if system:
    msgs.append({'role': 'system', 'content': system})
msgs.append({'role': 'user', 'content': prompt})
print(json.dumps({'model': model, 'messages': msgs, 'stream': stream}))
" "$MODEL" "$PROMPT" "$SYSTEM" "$stream_val"
}

run_streaming() {
    local payload="$1"
    curl -sf -N \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$OLLAMA_HOST/api/chat" | python3 -c '
import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
        c = d.get("message", {}).get("content", "")
        if c:
            print(c, end="", flush=True)
    except Exception:
        pass
'
    echo ""
}

run_blocking() {
    local payload="$1"
    local response
    response=$(curl -sf \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$OLLAMA_HOST/api/chat")

    if $JSON_OUT; then
        printf '%s\n' "$response"
    else
        printf '%s\n' "$response" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print(d.get("message", {}).get("content", ""))
'
    fi
}

main() {
    check_deps
    parse_args "$@"
    check_server

    local payload
    payload="$(build_payload)"

    if $STREAM; then
        run_streaming "$payload"
    else
        run_blocking "$payload"
    fi
}

main "$@"
