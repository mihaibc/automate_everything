# Examples

Small inputs for trying the repository without inventing files first. Commands below assume you are running from the repository root.

## Prompt Builder

```bash
python Python/ai_utils/prompt_builder.py \
  --system examples/templates/system.txt \
  --user examples/templates/user.txt \
  --vars topic=Ollama
```

## Batch Inference

```bash
python Python/ai_utils/batch_inference.py \
  --input examples/prompts/prompts.jsonl \
  --output results.jsonl
```

`results.jsonl` is ignored by git so local runs do not dirty your working tree.
