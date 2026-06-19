import json


def test_prompt_builder_replaces_variables(load_script):
    prompt_builder = load_script("Python/ai_utils/prompt_builder.py")

    result = prompt_builder.apply_vars("Summarize {topic} for {audience}", ["topic=Docker", "audience=SREs"])

    assert result == "Summarize Docker for SREs"


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


def test_embedding_search_math_helpers(load_script):
    embedding = load_script("Python/ai_utils/embedding_search.py")

    assert embedding.normalize([3.0, 4.0]) == [0.6, 0.8]
    assert embedding.cosine([1.0, 0.0], [0.5, 0.5]) == 0.5


def test_generate_modelfile(load_script):
    modelfile = load_script("Python/local_ai/generate_modelfile.py")

    content = modelfile.build_modelfile("llama3", "Be concise.", ["temperature 0.2"])

    assert content == 'FROM llama3\nPARAMETER temperature 0.2\nSYSTEM """\nBe concise.\n"""\n'


def test_ollama_model_report_formats_size(load_script):
    report = load_script("Python/local_ai/ollama_model_report.py")

    assert report.format_size(1024 * 1024 * 3) == "3.0 MB"
    assert report.format_size(None) == "unknown"


def test_download_hf_model_patterns(load_script):
    downloader = load_script("Python/local_ai/download_hf_model.py")

    assert downloader.parse_patterns("*.gguf, tokenizer.json") == ["*.gguf", "tokenizer.json"]
    assert downloader.parse_patterns(None) is None
