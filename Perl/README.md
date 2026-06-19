# Perl Developer Utilities

Dependency-light Perl scripts for developer text, repo, config, data, and log workflows. Commands below assume you are running from the repository root.

## Scripts

| Script | Purpose |
| --- | --- |
| `data_tools/jsonl_validate.pl` | Validate JSONL files and required top-level keys. |
| `repo_tools/todo_report.pl` | Report `TODO`, `FIXME`, `HACK`, and `NOTE` markers. |
| `config_tools/env_audit.pl` | Compare `.env` and `.env.example` without printing secret values. |
| `text_tools/replace_in_files.pl` | Preview or apply regex replacements across files. |
| `log_tools/log_summary.pl` | Summarize generic application logs by severity and repeated message. |
| `repo_tools/repo_lint.pl` | Run lightweight repository hygiene checks. |

## Examples

```bash
perl Perl/data_tools/jsonl_validate.pl --file examples/prompts/prompts.jsonl --require messages
perl Perl/repo_tools/todo_report.pl --path . --format markdown
perl Perl/config_tools/env_audit.pl --env examples/env/.env.sample --example examples/env/.env.example
perl Perl/text_tools/replace_in_files.pl --path examples --find Ollama --replace LocalAI --include md --dry-run
perl Perl/log_tools/log_summary.pl --file examples/logs/app.log --top 5
perl Perl/repo_tools/repo_lint.pl --path . --max-line 120
```

## Testing

```bash
perl -c Perl/data_tools/jsonl_validate.pl
prove -lr tests/perl
```

## Contribution Guidance

Perl scripts should use core modules where practical, support `--help`, avoid printing secrets, and include `Test::More` coverage. See [CONTRIBUTING.md](../CONTRIBUTING.md).
