#!/usr/bin/env python3
"""Ensure every script has an explicit automated test mapping."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_FILE = ROOT / "tests" / "script_test_map.json"
SCRIPT_GLOBS = {
    "Bash": "*.sh",
    "Perl": "*.pl",
    "PowerShell": "*.ps1",
    "Python": "*.py",
    "scripts": "*.py",
}


def discover_scripts() -> set[str]:
    scripts: set[str] = set()
    for directory, pattern in SCRIPT_GLOBS.items():
        base = ROOT / directory
        if not base.exists():
            continue
        for path in base.rglob(pattern):
            if path.is_file():
                scripts.add(path.relative_to(ROOT).as_posix())
    return scripts


def load_mapping() -> dict[str, list[str]]:
    return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))


def validate_mapping() -> list[str]:
    errors: list[str] = []
    scripts = discover_scripts()
    mapping = load_mapping()
    mapped = set(mapping)

    missing = sorted(scripts - mapped)
    extra = sorted(mapped - scripts)

    for path in missing:
        errors.append(f"Missing test mapping for script: {path}")
    for path in extra:
        errors.append(f"Mapping references missing script: {path}")

    for script, tests in sorted(mapping.items()):
        if not tests:
            errors.append(f"Mapping for {script} has no test files")
        for test in tests:
            if not (ROOT / test).is_file():
                errors.append(f"Mapping for {script} references missing test file: {test}")

    return errors


def main() -> int:
    errors = validate_mapping()
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Script test mapping: {len(load_mapping())} scripts covered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
