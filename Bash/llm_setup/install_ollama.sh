#!/usr/bin/env bash
# Install Ollama on macOS or Linux, then verify and start the server.

set -euo pipefail

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"

info()  { echo "[INFO]  $*"; }
ok()    { echo "[OK]    $*"; }
warn()  { echo "[WARN]  $*"; }
die()   { echo "[ERROR] $*" >&2; exit 1; }

detect_os() {
    case "$(uname -s)" in
        Darwin) echo "macos" ;;
        Linux)  echo "linux" ;;
        *)      die "Unsupported OS: $(uname -s)" ;;
    esac
}

is_installed() {
    command -v ollama &>/dev/null
}

install_ollama() {
    local os="$1"
    info "Downloading and installing Ollama for $os..."

    if [[ "$os" == "macos" ]]; then
        if command -v brew &>/dev/null; then
            brew install ollama
        else
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
}

start_server() {
    if curl -sf "$OLLAMA_HOST" &>/dev/null; then
        ok "Ollama server already running at $OLLAMA_HOST"
        return
    fi

    info "Starting Ollama server..."
    if [[ "$(detect_os)" == "macos" ]]; then
        # On macOS, ollama app or service manages the daemon
        ollama serve &>/dev/null &
        disown
    else
        if command -v systemctl &>/dev/null; then
            sudo systemctl enable --now ollama 2>/dev/null || ollama serve &>/dev/null &
        else
            ollama serve &>/dev/null &
            disown
        fi
    fi

    info "Waiting for server to be ready..."
    local attempts=0
    until curl -sf "$OLLAMA_HOST" &>/dev/null; do
        sleep 1
        attempts=$((attempts + 1))
        if (( attempts >= 15 )); then
            die "Server did not start within 15 seconds. Run 'ollama serve' manually."
        fi
    done
    ok "Server is ready at $OLLAMA_HOST"
}

main() {
    info "=== Ollama Installer ==="
    local os
    os="$(detect_os)"
    info "Detected OS: $os"

    if is_installed; then
        ok "Ollama is already installed: $(ollama --version 2>/dev/null || echo 'version unknown')"
    else
        install_ollama "$os"
        if is_installed; then
            ok "Ollama installed successfully: $(ollama --version 2>/dev/null || echo 'version unknown')"
        else
            die "Installation completed but 'ollama' not found on PATH. Open a new shell or add Ollama to your PATH."
        fi
    fi

    start_server
    ok "Ollama is ready. Run './pull_models.sh' to download models."
}

main "$@"
