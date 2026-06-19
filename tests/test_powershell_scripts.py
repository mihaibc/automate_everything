import json
import os
import shutil
import stat
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh")
SAFE_PATH = "/usr/bin:/bin"

pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh is not installed")


def write_executable(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def run_pwsh(script: str, *args: str, env: dict[str, str] | None = None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [PWSH, "-NoProfile", "-File", str(REPO_ROOT / script), *args],
        cwd=REPO_ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


class LocalHandler(BaseHTTPRequestHandler):
    response = {"models": []}

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"models": []}).encode("utf-8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.response).encode("utf-8"))

    def log_message(self, format, *args):
        return None


@pytest.fixture
def local_server():
    server = HTTPServer(("127.0.0.1", 0), LocalHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_powershell_scripts_parse():
    for path in sorted((REPO_ROOT / "PowerShell").rglob("*.ps1")):
        command = (
            "$tokens=$null; $errors=$null; "
            f"[System.Management.Automation.Language.Parser]::ParseFile('{path}', [ref]$tokens, [ref]$errors) | Out-Null; "
            "if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
        )
        result = subprocess.run([PWSH, "-NoProfile", "-Command", command], text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr


def test_install_ollama_whatif_with_fake_winget(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_executable(bin_dir / "winget", "#!/usr/bin/env sh\necho winget \"$@\"\n")
    env = {"PATH": f"{bin_dir}{os.pathsep}{SAFE_PATH}"}

    result = run_pwsh("PowerShell/local_ai/Install-Ollama.ps1", "-WhatIf", env=env)

    assert result.returncode == 0
    assert "What if" in result.stdout or "not found on PATH" in result.stderr


def test_pull_ollama_models_unreachable_with_fake_ollama(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_executable(bin_dir / "ollama", "#!/usr/bin/env sh\necho ollama \"$@\"\n")
    env = {"PATH": f"{bin_dir}{os.pathsep}{SAFE_PATH}"}

    result = run_pwsh(
        "PowerShell/local_ai/Pull-OllamaModels.ps1",
        "-HostUrl",
        "http://127.0.0.1:9",
        "-Models",
        "llama3",
        env=env,
    )

    assert result.returncode == 1
    assert "not reachable" in result.stderr


def test_pull_ollama_models_success_with_fake_ollama(tmp_path, local_server):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_executable(
        bin_dir / "ollama",
        """#!/usr/bin/env sh
case "$1" in
  pull) echo "pulled $2" ;;
  list) printf 'NAME ID SIZE MODIFIED\\nllama3 abc 4GB today\\n' ;;
  *) echo ollama "$@" ;;
esac
""",
    )
    env = {"PATH": f"{bin_dir}{os.pathsep}{SAFE_PATH}"}

    result = run_pwsh(
        "PowerShell/local_ai/Pull-OllamaModels.ps1",
        "-HostUrl",
        local_server,
        "-Models",
        "llama3",
        env=env,
    )

    assert result.returncode == 0
    assert "Pulling llama3" in result.stdout
    assert "llama3" in result.stdout


def test_local_ai_endpoint_success(local_server):
    LocalHandler.response = {"message": {"content": "local model works"}}

    result = run_pwsh(
        "PowerShell/local_ai/Test-LocalAIEndpoint.ps1",
        "-HostUrl",
        local_server,
        "-Model",
        "llama3",
    )

    assert result.returncode == 0
    assert "local model works" in result.stdout
