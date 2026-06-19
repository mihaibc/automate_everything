import json
import sys
import types
from argparse import Namespace

import pytest


def test_prompt_builder_replaces_variables(load_script):
    prompt_builder = load_script("Python/ai_utils/prompt_builder.py")

    result = prompt_builder.apply_vars("Summarize {topic} for {audience}", ["topic=Docker", "audience=SREs"])

    assert result == "Summarize Docker for SREs"


def test_prompt_builder_loads_template_file(tmp_path, load_script):
    prompt_builder = load_script("Python/ai_utils/prompt_builder.py")
    template = tmp_path / "template.txt"
    template.write_text("Hello {name}", encoding="utf-8")

    assert prompt_builder.apply_vars(prompt_builder.load_template(str(template)), ["name=Ada"]) == "Hello Ada"


def test_prompt_builder_warns_for_bad_and_missing_vars(capsys, load_script):
    prompt_builder = load_script("Python/ai_utils/prompt_builder.py")

    result = prompt_builder.apply_vars("Hello {name} from {place}", ["bad", "name=Ada"])

    assert result == "Hello Ada from {place}"
    err = capsys.readouterr().err
    assert "malformed var" in err
    assert "unresolved placeholders" in err


def test_prompt_builder_builds_openai_style_messages(load_script):
    prompt_builder = load_script("Python/ai_utils/prompt_builder.py")

    payload = prompt_builder.build_prompt("Be concise", "Explain CI", model="llama3")

    assert payload == {
        "model": "llama3",
        "messages": [
            {"role": "system", "content": "Be concise"},
            {"role": "user", "content": "Explain CI"},
        ],
    }


def test_batch_inference_load_prompts_skips_invalid_lines(tmp_path, capsys, load_script):
    batch = load_script("Python/ai_utils/batch_inference.py")
    input_file = tmp_path / "prompts.jsonl"
    input_file.write_text(
        "\n".join(
            [
                json.dumps({"messages": [{"role": "user", "content": "hello"}]}),
                "not-json",
                json.dumps({"name": "missing prompt"}),
                json.dumps({"prompt": "native ollama prompt"}),
            ]
        ),
        encoding="utf-8",
    )

    prompts = batch.load_prompts(str(input_file))

    assert [prompt["_line"] for prompt in prompts] == [1, 4]
    assert "skipping line 2" in capsys.readouterr().err


def test_batch_inference_run_single_extracts_openai_response(monkeypatch, load_script):
    batch = load_script("Python/ai_utils/batch_inference.py")
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

    def post(url, json, headers, timeout):
        captured.update({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return Response()

    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(post=post))

    result = batch.run_single({"_line": 1, "messages": [{"role": "user", "content": "hi"}]}, "http://host/v1", "llama3", 9, "key")

    assert result["status"] == "ok"
    assert result["output"] == "ok"
    assert captured["url"] == "http://host/v1/chat/completions"
    assert captured["json"]["model"] == "llama3"
    assert captured["headers"]["Authorization"] == "Bearer key"


def test_batch_inference_run_single_reports_http_errors(monkeypatch, load_script):
    batch = load_script("Python/ai_utils/batch_inference.py")

    class Response:
        def raise_for_status(self):
            raise RuntimeError("boom")

        def json(self):
            return {}

    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(post=lambda *args, **kwargs: Response()))

    result = batch.run_single({"_line": 2, "prompt": "hi"}, "http://host/v1", "llama3", 9, "")

    assert result["status"] == "error"
    assert "boom" in result["error"]


def test_embedding_search_math_helpers(load_script):
    embedding = load_script("Python/ai_utils/embedding_search.py")

    assert embedding.normalize([3.0, 4.0]) == [0.6, 0.8]
    assert embedding.cosine([1.0, 0.0], [0.5, 0.5]) == 0.5
    assert embedding.normalize([0.0, 0.0]) == [0.0, 0.0]


def test_embedding_search_outputs_json_results(tmp_path, monkeypatch, capsys, load_script):
    embedding = load_script("Python/ai_utils/embedding_search.py")

    class Vec(list):
        def tolist(self):
            return list(self)

    class Model:
        def encode(self, values, show_progress_bar=False):
            return [Vec([1.0, 0.0]) for _ in values]

    monkeypatch.setattr(embedding, "get_model", lambda name: Model())
    index = tmp_path / "embedding_index.json"
    index.write_text(
        json.dumps({"model": "fake", "documents": [{"path": "a.txt", "embedding": [1.0, 0.0]}]}),
        encoding="utf-8",
    )

    embedding.cmd_search(Namespace(query="auth", index=str(index), top=5, model=None, json=True))

    results = json.loads(capsys.readouterr().out)
    assert results[0]["file"] == "a.txt"


def test_embedding_search_rejects_corrupt_index(tmp_path, capsys, load_script):
    embedding = load_script("Python/ai_utils/embedding_search.py")
    index = tmp_path / "bad.json"
    index.write_text("not-json", encoding="utf-8")

    with pytest.raises(SystemExit):
        embedding.cmd_search(Namespace(query="auth", index=str(index), top=5, model=None, json=False))

    assert "corrupt" in capsys.readouterr().err


def test_token_counter_counts_with_fake_tiktoken(monkeypatch, load_script):
    token_counter = load_script("Python/ai_utils/token_counter.py")

    class Encoding:
        def encode(self, text):
            return text.split()

    monkeypatch.setitem(sys.modules, "tiktoken", types.SimpleNamespace(get_encoding=lambda name: Encoding()))

    assert token_counter.count_tokens("hello world", "gpt-4") == 2


def test_token_counter_reports_missing_dependency(monkeypatch, capsys, load_script):
    token_counter = load_script("Python/ai_utils/token_counter.py")
    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "tiktoken":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(SystemExit):
        token_counter.count_tokens("hello", "gpt-4")

    assert "tiktoken not installed" in capsys.readouterr().err


def test_token_counter_reports_unknown_model(monkeypatch, capsys, load_script):
    token_counter = load_script("Python/ai_utils/token_counter.py")

    def fail(*args, **kwargs):
        raise RuntimeError("unknown")

    monkeypatch.setitem(sys.modules, "tiktoken", types.SimpleNamespace(get_encoding=fail, encoding_for_model=fail))

    with pytest.raises(SystemExit):
        token_counter.count_tokens("hello", "not-a-model")

    assert "unknown model" in capsys.readouterr().err


def test_generate_modelfile(load_script):
    modelfile = load_script("Python/local_ai/generate_modelfile.py")

    content = modelfile.build_modelfile("llama3", "Be concise.", ["temperature 0.2"])

    assert content == 'FROM llama3\nPARAMETER temperature 0.2\nSYSTEM """\nBe concise.\n"""\n'


def test_generate_modelfile_writes_file(tmp_path, load_script):
    modelfile = load_script("Python/local_ai/generate_modelfile.py")
    output = tmp_path / "Modelfile"

    assert modelfile.main(["--from", "llama3", "--parameter", "num_ctx 4096", "--output", str(output)]) == 0

    assert output.read_text(encoding="utf-8") == "FROM llama3\nPARAMETER num_ctx 4096\n"


def test_ollama_model_report_formats_size(load_script):
    report = load_script("Python/local_ai/ollama_model_report.py")

    assert report.format_size(1024 * 1024 * 3) == "3.0 MB"
    assert report.format_size(None) == "unknown"


def test_ollama_model_report_fetches_and_outputs_json(monkeypatch, capsys, load_script):
    report = load_script("Python/local_ai/ollama_model_report.py")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"models":[{"name":"llama3","size":1048576}]}'

    monkeypatch.setattr(report, "urlopen", lambda url, timeout: Response())

    assert report.main(["--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["name"] == "llama3"


def test_ollama_model_report_handles_unreachable_host(monkeypatch, capsys, load_script):
    report = load_script("Python/local_ai/ollama_model_report.py")
    monkeypatch.setattr(report, "urlopen", lambda url, timeout: (_ for _ in ()).throw(TimeoutError("slow")))

    assert report.main([]) == 1
    assert "could not reach" in capsys.readouterr().err


def test_download_hf_model_patterns(load_script):
    downloader = load_script("Python/local_ai/download_hf_model.py")

    assert downloader.parse_patterns("*.gguf, tokenizer.json") == ["*.gguf", "tokenizer.json"]
    assert downloader.parse_patterns(None) is None


def test_download_hf_model_dry_run(tmp_path, capsys, load_script):
    downloader = load_script("Python/local_ai/download_hf_model.py")

    path = downloader.download_model("org/model", tmp_path / "models", ["*.gguf"], None, dry_run=True)

    assert path == tmp_path / "models"
    assert "Would download" in capsys.readouterr().out


def test_download_hf_model_calls_snapshot_download(monkeypatch, tmp_path, load_script):
    downloader = load_script("Python/local_ai/download_hf_model.py")
    captured = {}

    def snapshot_download(**kwargs):
        captured.update(kwargs)
        return str(tmp_path / "model")

    monkeypatch.setitem(sys.modules, "huggingface_hub", types.SimpleNamespace(snapshot_download=snapshot_download))

    path = downloader.download_model("org/model", tmp_path / "models", ["*.gguf"], "main", dry_run=False)

    assert path == tmp_path / "model"
    assert captured["repo_id"] == "org/model"
    assert captured["allow_patterns"] == ["*.gguf"]


def test_download_hf_model_reports_missing_dependency(monkeypatch, tmp_path, load_script):
    downloader = load_script("Python/local_ai/download_hf_model.py")
    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "huggingface_hub":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(RuntimeError, match="huggingface-hub"):
        downloader.download_model("org/model", tmp_path / "models", None, None, dry_run=False)


def test_benchmark_ollama_run_once_and_summary(monkeypatch, load_script):
    benchmark = load_script("Python/local_ai/benchmark_ollama.py")
    captured = {}

    def post_json(url, payload, timeout):
        captured.update({"url": url, "payload": payload, "timeout": timeout})
        return {"message": {"content": "hello"}, "eval_count": 20}

    monkeypatch.setattr(benchmark, "post_json", post_json)

    result = benchmark.run_once("http://host", "llama3", "hi", 5)

    assert captured["url"] == "http://host/api/chat"
    assert captured["payload"]["model"] == "llama3"
    assert result["eval_count"] == 20
    assert benchmark.summarize([result])["runs"] == 1


def test_benchmark_ollama_rejects_invalid_runs(capsys, load_script):
    benchmark = load_script("Python/local_ai/benchmark_ollama.py")

    assert benchmark.main(["--runs", "0"]) == 1
    assert "must be >= 1" in capsys.readouterr().err
