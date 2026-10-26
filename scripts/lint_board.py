#!/usr/bin/env python3
"""Lint a .drawio board before importing it anywhere.

Checks, style-agnostic: text overflow, font floor, shapes outside the page,
and text/background contrast (WCAG ratio against the shape actually behind the
text). Exit code 1 when an error is found.

    python3 lint_board.py board.drawio [--min-font=11] [--no-contrast]
"""

import sys

from boardkit import lint_file


def main(argv):
    path = next((a for a in argv[1:] if not a.startswith("--")), None)
    if not path:
        print("usage: lint_board.py <file.drawio> [--min-font=11] [--no-contrast]")
        return 2
    min_font = 11
    for a in argv[1:]:
        if a.startswith("--min-font="):
            min_font = float(a.split("=", 1)[1])
    no_contrast = "--no-contrast" in argv

    page, issues = lint_file(path, min_font=min_font, check_contrast=not no_contrast)
    errors = [i for i in issues if i[0] == "error"]
    warns = [i for i in issues if i[0] == "warn"]

    print(f"canvas {page[0]}x{page[1]}")
    if not issues:
        print("lint: clean")
        return 0
    print(f"lint: {len(errors)} error(s), {len(warns)} warning(s)")
    for level, msg in issues[:40]:
        print(f"  {level}: {msg}")
    if len(issues) > 40:
        print(f"  ... {len(issues) - 40} more")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
