# Security Policy

## Supported Scope

This repository contains standalone automation scripts. Security fixes are accepted for the current `main` branch.

## Reporting a Vulnerability

Please open a private security advisory on GitHub when possible. If that is not available, open an issue with a minimal description and avoid posting secrets, tokens, full paths containing private data, or exploit payloads.

Useful reports include:

- Affected script path.
- Operating system and runtime version.
- Exact command used, with secrets redacted.
- Expected behavior and observed behavior.
- Impact: data loss, credential exposure, command injection, unsafe network access, or privilege escalation.

## Safety Expectations

Scripts that move, delete, download, install, or execute external tools should prefer:

- Dry-run mode for destructive actions.
- Clear confirmation or explicit flags for risky behavior.
- Quoted shell variables and strict shell mode.
- No hard-coded secrets.
- Minimal required privileges.
- Tests for path handling and error cases.
