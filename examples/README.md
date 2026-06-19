# Examples

Small inputs for trying the repository without inventing files first.

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
