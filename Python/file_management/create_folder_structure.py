#!/usr/bin/env python3
"""Create repeatable folder structures from built-in templates or JSON."""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_STRUCTURE = {
    "Python": ["file_management", "ai_utils", "local_ai"],
    "Bash": ["llm_setup", "local_ai"],
    "PowerShell": ["local_ai"],
    "examples": ["prompts", "templates"],
    "tests": ["fixtures"],
}


def create_folder_structure(base_path: str | Path, folder_structure: dict[str, list[str]], *, dry_run: bool = False) -> list[Path]:
    """
    Create a folder structure based on a dictionary.

    Returns the paths that were created, or would be created in dry-run mode.
    """
    base = Path(base_path).expanduser().resolve()
    created = []
    for main_folder, sub_folders in folder_structure.items():
        if not isinstance(sub_folders, list):
            raise ValueError(f"folder '{main_folder}' must map to a list of subfolders")
        for sub_folder in sub_folders:
            path = base / main_folder / sub_folder
            created.append(path)
            if not dry_run:
                path.mkdir(parents=True, exist_ok=True)
    return created


def load_structure(path: str | None) -> dict[str, list[str]]:
    if not path:
        return DEFAULT_STRUCTURE

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"could not read structure file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON structure file: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("structure file must contain a JSON object")
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a standard automation repository folder structure.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--base-path", required=True, help="Root directory where folders should be created")
    parser.add_argument("--structure-file", help="Optional JSON file mapping folders to subfolder lists")
    parser.add_argument("--dry-run", action="store_true", help="Show folders without creating them")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        structure = load_structure(args.structure_file)
        paths = create_folder_structure(args.base_path, structure, dry_run=args.dry_run)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    action = "Would create" if args.dry_run else "Created"
    for path in paths:
        print(f"{action}: {path}")
    print(f"Total: {len(paths)} folder(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
