#!/usr/bin/env python3
"""Validate and maintain this repository's automation-file inventory."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

START_MARKER = "<!-- BEGIN AUTOMATED FILE INVENTORY -->"
END_MARKER = "<!-- END AUTOMATED FILE INVENTORY -->"
INVENTORY_DIRECTORIES = (".github/workflows", "scripts", "tests")
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def discover_automation_files(repository_root: Path) -> list[str]:
    """Return the supported workflow, script, and test files in stable order."""
    files: list[str] = []
    for directory in INVENTORY_DIRECTORIES:
        base = repository_root / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".yml", ".yaml"}:
                files.append(path.relative_to(repository_root).as_posix())
    return sorted(files)


def replace_inventory(readme: str, files: list[str]) -> str:
    """Replace only the explicitly managed README section."""
    if not files:
        raise ValueError("No workflow, script, or test files were found; refusing an empty inventory.")

    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise ValueError("README must contain exactly one pair of automated inventory markers.")

    start = readme.index(START_MARKER)
    end = readme.index(END_MARKER)
    if end < start:
        raise ValueError("README inventory markers are out of order.")

    items = "\n".join(f"- `{path}`" for path in files)
    section = (
        f"{START_MARKER}\n"
        "### Automation and test files\n\n"
        "This list is synchronized by `scripts/scheduled_check.py`.\n\n"
        f"{items}\n"
        f"{END_MARKER}"
    )
    return f"{readme[:start]}{section}{readme[end + len(END_MARKER):]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--update",
        action="store_true",
        help="write a changed inventory section (default: check without writing)",
    )
    mode.add_argument("--check", action="store_true", help="check the inventory without writing")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S%z")
    repository_root = Path(__file__).resolve().parent.parent
    readme_path = repository_root / "README.md"

    try:
        current = readme_path.read_text(encoding="utf-8")
        files = discover_automation_files(repository_root)
        expected = replace_inventory(current, files)
        if expected == current:
            logging.info("Automation file inventory is current; no changes are needed.")
            return 0
        if not args.update:
            logging.error("Automation file inventory is stale; run scripts/scheduled_check.py --update.")
            return 1
        readme_path.write_text(expected, encoding="utf-8", newline="\n")
        logging.info("Updated the README inventory for %d automation/test files.", len(files))
        return 0
    except (OSError, ValueError) as error:
        logging.error("Scheduled check failed: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
