#!/usr/bin/env bash
# Report common local AI acceleration options on Linux and macOS.

set -euo pipefail

info() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*"; }

detect_nvidia() {
    if command -v nvidia-smi >/dev/null 2>&1; then
        info "NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
        return 0
    fi
    return 1
}

detect_amd() {
    if command -v rocm-smi >/dev/null 2>&1; then
        info "AMD ROCm device detected"
        rocm-smi --showproductname --showmeminfo vram
        return 0
    fi
    return 1
}

detect_apple() {
    if [[ "$(uname -s)" != "Darwin" ]]; then
        return 1
    fi

    info "Apple system detected"
    if command -v system_profiler >/dev/null 2>&1; then
        system_profiler SPDisplaysDataType | awk '/Chipset Model|VRAM|Metal/ {print "  " $0}'
    fi
    return 0
}

detect_linux_pci() {
    if command -v lspci >/dev/null 2>&1; then
        info "PCI display devices"
        lspci | grep -Ei 'vga|3d|display' || true
        return 0
    fi
    return 1
}

main() {
    found=false

    if detect_nvidia; then found=true; fi
    if detect_amd; then found=true; fi
    if detect_apple; then found=true; fi
    if detect_linux_pci; then found=true; fi

    if [[ "$found" == "false" ]]; then
        warn "No GPU tooling found. CPU inference should still work, but setup scripts cannot confirm acceleration."
    fi

    echo ""
    info "Local AI tips"
    echo "  - Ollama uses available acceleration automatically when supported."
    echo "  - llama.cpp can be built with Metal on macOS, CUDA for NVIDIA, or CPU-only everywhere."
}

main "$@"
