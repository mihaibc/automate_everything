#!/usr/bin/env python3
"""Check Markdown files for local links, anchors, headings, and whitespace."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def iter_lines_outside_fences(text: str):
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            in_fence = not in_fence
            yield number, line, True
            continue
        yield number, line, in_fence


def markdown_files() -> list[Path]:
    files = [*ROOT.rglob("*.md"), *ROOT.rglob("*.MD")]
    return sorted(path for path in files if ".git" not in path.parts)


def headings_for(path: Path) -> list[tuple[int, int, str]]:
    headings = []
    for number, line, in_fence in iter_lines_outside_fences(path.read_text(encoding="utf-8")):
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", line)
        if match:
            headings.append((number, len(match.group(1)), slug(match.group(2))))
    return headings


def check_file(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors = []

    headings = headings_for(path)
    anchors = {anchor for _, _, anchor in headings}
    previous_level = 0

    for number, line, _ in iter_lines_outside_fences(text):
        if line.rstrip() != line:
            errors.append(f"{rel}:{number}: trailing whitespace")

    for number, level, _ in headings:
        if previous_level and level > previous_level + 1:
            errors.append(f"{rel}:{number}: heading level jumps from H{previous_level} to H{level}")
        previous_level = level

    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            if target[1:] not in anchors:
                errors.append(f"{rel}: missing anchor {target}")
            continue
        if "://" in target:
            continue

        file_part, _, fragment = target.partition("#")
        local = (path.parent / file_part).resolve()
        if not local.exists():
            errors.append(f"{rel}: broken link {target}")
            continue
        if fragment and local.suffix.lower() in {".md", ".markdown"}:
            local_anchors = {anchor for _, _, anchor in headings_for(local)}
            if fragment not in local_anchors:
                errors.append(f"{rel}: missing linked anchor {target}")

    return errors


def main() -> int:
    errors = []
    files = markdown_files()
    for path in files:
        errors.extend(check_file(path))

    if errors:
        print("\n".join(errors))
        return 1

    print(f"Checked {len(files)} Markdown files: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
