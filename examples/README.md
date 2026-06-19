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

## Perl Utilities

```bash
perl Perl/data_tools/jsonl_validate.pl --file examples/prompts/prompts.jsonl --require messages
perl Perl/config_tools/env_audit.pl --env examples/env/.env.sample --example examples/env/.env.example
perl Perl/log_tools/log_summary.pl --file examples/logs/app.log
```
