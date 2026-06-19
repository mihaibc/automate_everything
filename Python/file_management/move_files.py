#!/usr/bin/env python3
"""Move files by extension with dry-run and collision protection."""

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MoveResult:
    source: Path
    destination: Path
    action: str


def normalize_extensions(file_extensions: list[str]) -> tuple[str, ...]:
    """Return lowercase extensions with a leading dot."""
    normalized = []
    for extension in file_extensions:
        clean = extension.strip().lower()
        if not clean:
            continue
        if not clean.startswith("."):
            clean = f".{clean}"
        normalized.append(clean)

    if not normalized:
        raise ValueError("at least one file extension is required")

    return tuple(dict.fromkeys(normalized))


def resolve_destination(path: Path, collision: str) -> tuple[Path, str]:
    """Resolve filename collisions according to the selected strategy."""
    if not path.exists():
        return path, "moved"

    if collision == "skip":
        return path, "skipped"
    if collision == "overwrite":
        return path, "overwritten"
    if collision == "error":
        raise FileExistsError(f"destination already exists: {path}")

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate, "renamed"
        counter += 1


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def iter_matching_files(src_folder: Path, dest_folder: Path, extensions: tuple[str, ...], recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    files = []
    for path in src_folder.glob(pattern):
        if path.is_dir():
            continue
        if is_relative_to(path, dest_folder):
            continue
        if path.suffix.lower() in extensions:
            files.append(path)
    return sorted(files)


def move_files(
    src_folder: str | Path,
    dest_folder: str | Path,
    file_extensions: list[str],
    *,
    dry_run: bool = False,
    recursive: bool = True,
    collision: str = "rename",
) -> list[MoveResult]:
    """
    Move files with specified extensions from the source folder to the destination folder.

    Returns a list of MoveResult values describing each move, skip, or rename.
    """
    source = Path(src_folder).expanduser().resolve()
    destination = Path(dest_folder).expanduser().resolve()
    extensions = normalize_extensions(file_extensions)

    if not source.is_dir():
        raise NotADirectoryError(f"source folder does not exist: {source}")

    if source == destination:
        raise ValueError("source and destination must be different directories")

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    results = []
    for file_path in iter_matching_files(source, destination, extensions, recursive):
        target, action = resolve_destination(destination / file_path.name, collision)
        results.append(MoveResult(source=file_path, destination=target, action=action))

        if dry_run or action == "skipped":
            continue

        shutil.move(str(file_path), str(target))

    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move files from one folder to another by extension.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--source", required=True, help="Directory to search")
    parser.add_argument("--destination", required=True, help="Directory where matching files are moved")
    parser.add_argument(
        "--extensions",
        required=True,
        help="Comma-separated extensions, such as pdf,jpg or .pdf,.jpg",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned moves without changing files")
    parser.add_argument("--no-recursive", action="store_true", help="Only scan the top-level source directory")
    parser.add_argument(
        "--collision",
        choices=["rename", "skip", "overwrite", "error"],
        default="rename",
        help="How to handle existing destination files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    extensions = args.extensions.split(",")

    try:
        results = move_files(
            args.source,
            args.destination,
            extensions,
            dry_run=args.dry_run,
            recursive=not args.no_recursive,
            collision=args.collision,
        )
    except (FileExistsError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not results:
        print("No matching files found.")
        return 0

    for result in results:
        prefix = "Would move" if args.dry_run else result.action.capitalize()
        print(f"{prefix}: {result.source} -> {result.destination}")

    print(f"Total: {len(results)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
