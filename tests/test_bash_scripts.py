import os
import shutil
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash") or "/bin/bash"


def write_executable(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def run_bash(script: str, *args: str, env: dict[str, str] | None = None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [BASH, str(REPO_ROOT / script), *args],
        cwd=REPO_ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def fake_bin(tmp_path: Path) -> Path:
    directory = tmp_path / "bin"
    directory.mkdir()
    return directory


def fake_curl(bin_dir: Path, body: str = '{"message":{"content":"ok"} }') -> None:
    write_executable(
        bin_dir / "curl",
        f"""#!/usr/bin/env python3
import os, sys
args = sys.argv[1:]
urls = [arg for arg in args if arg.startswith("http://") or arg.startswith("https://")]
url = urls[-1] if urls else ""
if url.endswith("/api/tags") or url.rstrip("/") == "http://localhost:11434":
    sys.exit(0 if os.environ.get("FAKE_CURL_FAIL") != "1" else 22)
payload_file = os.environ.get("FAKE_CURL_PAYLOAD_FILE")
if payload_file and "-d" in args:
    open(payload_file, "w", encoding="utf-8").write(args[args.index("-d") + 1])
if "-N" in args:
    print('{{"message":{{"content":"hi "}}}}')
    print('{{"message":{{"content":"there"}}}}')
else:
    print({body!r})
""",
    )


def fake_ollama(bin_dir: Path) -> None:
    write_executable(
        bin_dir / "ollama",
        """#!/usr/bin/env sh
case "$1" in
  --version) echo "ollama version fake" ;;
  pull)
    if [ "$2" = "bad" ]; then exit 1; fi
    echo "pulled $2"
    ;;
  list)
    printf 'NAME ID SIZE MODIFIED\\n'
    printf 'llama3 abc 4 GB today\\n'
    ;;
  serve) exit 0 ;;
  *) echo "ollama $*" ;;
esac
""",
    )


def test_run_inference_missing_prompt():
    result = run_bash("Bash/llm_setup/run_inference.sh")

    assert result.returncode == 1
    assert "--prompt is required" in result.stderr


def test_run_inference_blocking_payload_and_output(tmp_path):
    bin_dir = fake_bin(tmp_path)
    fake_curl(bin_dir, '{"message":{"content":"model response"}}')
    payload = tmp_path / "payload.json"
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "FAKE_CURL_PAYLOAD_FILE": str(payload)}

    result = run_bash(
        "Bash/llm_setup/run_inference.sh",
        "--model",
        "llama3",
        "--system",
        "Be concise",
        "--prompt",
        "say \"hi\"",
        env=env,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "model response"
    assert '"content": "say \\"hi\\""' in payload.read_text(encoding="utf-8")


def test_run_inference_streaming(tmp_path):
    bin_dir = fake_bin(tmp_path)
    fake_curl(bin_dir)
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}

    result = run_bash("Bash/llm_setup/run_inference.sh", "--stream", "--prompt", "hello", env=env)

    assert result.returncode == 0
    assert result.stdout.strip() == "hi there"


def test_pull_models_success_and_failure(tmp_path):
    bin_dir = fake_bin(tmp_path)
    fake_curl(bin_dir)
    fake_ollama(bin_dir)
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}

    ok = run_bash("Bash/llm_setup/pull_models.sh", "--models", "llama3 mistral", env=env)
    assert ok.returncode == 0
    assert "2 pulled, 0 failed" in ok.stdout

    failed = run_bash("Bash/llm_setup/pull_models.sh", "--models", "llama3 bad", env=env)
    assert failed.returncode == 1
    assert "Failed models: bad" in failed.stdout


def test_pull_models_unreachable_server(tmp_path):
    bin_dir = fake_bin(tmp_path)
    fake_curl(bin_dir)
    fake_ollama(bin_dir)
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "FAKE_CURL_FAIL": "1"}

    result = run_bash("Bash/llm_setup/pull_models.sh", "--models", "llama3", env=env)

    assert result.returncode == 1
    assert "not reachable" in result.stderr


def test_install_ollama_already_installed_and_unsupported_os(tmp_path):
    bin_dir = fake_bin(tmp_path)
    fake_curl(bin_dir)
    fake_ollama(bin_dir)
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}

    ok = run_bash("Bash/llm_setup/install_ollama.sh", env=env)
    assert ok.returncode == 0
    assert "already installed" in ok.stdout

    write_executable(bin_dir / "uname", "#!/usr/bin/env sh\necho Plan9\n")
    unsupported = run_bash("Bash/llm_setup/install_ollama.sh", env=env)
    assert unsupported.returncode == 1
    assert "Unsupported OS" in unsupported.stderr


def test_check_gpu_no_tools_nvidia_and_lspci(tmp_path):
    bin_dir = fake_bin(tmp_path)
    write_executable(bin_dir / "uname", "#!/usr/bin/env sh\necho Linux\n")
    no_tools = run_bash("Bash/local_ai/check_gpu.sh", env={"PATH": str(bin_dir)})
    assert no_tools.returncode == 0
    assert "No GPU tooling found" in no_tools.stdout

    write_executable(bin_dir / "nvidia-smi", "#!/usr/bin/env sh\necho 'Fake GPU, 8192 MiB, 555.1'\n")
    nvidia = run_bash("Bash/local_ai/check_gpu.sh", env={"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"})
    assert "NVIDIA GPU detected" in nvidia.stdout

    (bin_dir / "nvidia-smi").unlink()
    write_executable(bin_dir / "lspci", "#!/usr/bin/env sh\necho '00:02.0 VGA compatible controller'\n")
    pci = run_bash("Bash/local_ai/check_gpu.sh", env={"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"})
    assert "PCI display devices" in pci.stdout


def test_install_llama_cpp_dry_run_and_invalid_accelerator(tmp_path):
    bin_dir = fake_bin(tmp_path)
    write_executable(bin_dir / "git", "#!/usr/bin/env sh\necho git \"$@\"\n")
    write_executable(bin_dir / "cmake", "#!/usr/bin/env sh\necho cmake \"$@\"\n")
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}

    ok = run_bash(
        "Bash/local_ai/install_llama_cpp.sh",
        "--dir",
        str(tmp_path / "llama.cpp"),
        "--accelerator",
        "cpu",
        "--dry-run",
        env=env,
    )
    assert ok.returncode == 0
    assert "[DRY-RUN] git clone" in ok.stdout

    bad = run_bash("Bash/local_ai/install_llama_cpp.sh", "--accelerator", "bogus", "--dry-run", env=env)
    assert bad.returncode == 1
    assert "Unsupported accelerator" in bad.stderr


def test_setup_python_ai_env_dry_run_and_missing_requirements(tmp_path):
    ok = run_bash(
        "Bash/local_ai/setup_python_ai_env.sh",
        "--venv",
        str(tmp_path / "venv"),
        "--no-default-packages",
        "--dry-run",
    )
    assert ok.returncode == 0
    assert "[DRY-RUN]" in ok.stdout
    assert "sentence-transformers" not in ok.stdout

    missing = run_bash("Bash/local_ai/setup_python_ai_env.sh", "--requirements", str(tmp_path / "missing.txt"), "--dry-run")
    assert missing.returncode == 1
    assert "requirements file not found" in missing.stderr
