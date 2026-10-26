#!/usr/bin/env python3
"""Lint a .drawio board before importing it into Feishu.

Checks: text wider than its box, fonts below the legibility floor, shapes
outside the page. Exit code 1 when issues are found.

    python3 lint_board.py board.drawio [--min-font 13]
"""

import sys

from boardkit import lint_file, MIN_FONT


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    min_font = MIN_FONT
    for a in argv[1:]:
        if a.startswith("--min-font"):
            min_font = float(a.split("=", 1)[1])
    if not args:
        print("usage: lint_board.py <file.drawio> [--min-font=13]")
        return 2

    page, issues = lint_file(args[0], min_font=min_font)
    print(f"canvas {page[0]}x{page[1]}")
    if not issues:
        print("lint: clean")
        return 0
    print(f"lint: {len(issues)} issue(s)")
    for i in issues[:40]:
        print("  -", i)
    if len(issues) > 40:
        print(f"  ... {len(issues) - 40} more")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
