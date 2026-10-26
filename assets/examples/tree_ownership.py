#!/usr/bin/env python3
"""Style example: monochrome ownership tree, type and rules only.

Structure being drawn: a module tree with owners and two unauthored areas.
Why this style: the content is hierarchy + status, not boxes with capabilities,
so boxes would add noise. One signal color is spent on what actually needs
attention (unowned modules).

    python3 tree_ownership.py [out.drawio]
"""

import os
import sys

_candidates = [
    os.environ.get("BOARDKIT_DIR"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"),
    os.path.expanduser("~/skills-manager/architecture-board-builder/scripts"),
]
for _p in _candidates:
    if _p and os.path.isdir(_p):
        sys.path.insert(0, _p)
        break

from boardkit import Board  # noqa: E402

b = Board(1600, 640, title="tree-ownership", theme="mono", name="归属树（示例）")
t = b.t
signal = t.acc("signal")

# ---------------------------------------------------------------- header
b.text(80, 50, 500, 18, "OWNERSHIP MAP / SAMPLE", 11, t.muted, True)
b.text(80, 72, 900, 52, "模块与负责人", 36, t.ink, True)
b.text(80, 130, 1000, 22, "谁维护哪一块，比目录结构更值得画出来", 14, t.body)
b.text(1160, 78, 360, 18, "9 个模块 · 2 个待认领", 11, t.muted, False, "right")

# ---------------------------------------------------------------- root
b.text(700, 190, 200, 26, "platform/", 20, t.ink, True, "center")
b.line(730, 222, 140, 1.4, t.ink)
b.edge([(800, 222), (800, 250)], t.line, 1.1, end=False, straight=True)
b.line(320, 250, 960, 1.1, t.line)

GROUPS = [
    (320, "ingest/", "owners: 2", [
        ("api-gateway", "core", False, ""),
        ("log-agent", "infra", False, ""),
        ("sftp-bridge", "", True, "待认领"),
    ]),
    (800, "compute/", "owners: 2", [
        ("scheduler", "core", False, ""),
        ("stream-runner", "data", False, ""),
        ("batch-runner", "data", False, ""),
        ("lineage", "", False, "规划中"),
    ]),
    (1280, "store/", "owners: 3", [
        ("warehouse", "data", False, ""),
        ("object-store", "infra", False, ""),
        ("cache", "", True, "待认领"),
    ]),
]

for cx, name, owners, rows in GROUPS:
    b.line(cx, 250, 1.1, 32, t.line)
    b.text(cx - 110, 288, 220, 24, name, 15, t.ink, True, "center")
    b.text(cx - 110, 312, 220, 18, owners, 11, t.muted, False, "center")
    top, bottom = 336, 348 + (len(rows) - 1) * 44 + 10
    for i, (module, owner, unowned, note) in enumerate(rows):
        y = 348 + i * 44
        planned = note == "规划中"
        color = signal.text if unowned else t.body
        b.line(cx - 130, y + 9, 16, 1.1, t.line, dashed=unowned or planned)
        b.text(cx - 104, y, 150, 20, module, 13, color)
        meta = note or owner
        b.text(cx + 10, y + 1, 110, 18, meta, 11,
               signal.text if unowned else t.muted, False, "right")
    b.line(cx - 130, top, 1.1, bottom - top, t.line)

# ---------------------------------------------------------------- footer
b.text(80, 572, 900, 18, "实线 = 已归属 · 虚线 = 规划中 · 红色 = 待认领", 11, t.muted)
b.text(1160, 572, 360, 18, "mono / tree", 11, t.muted, False, "right")

out = sys.argv[1] if len(sys.argv) > 1 else "tree-ownership.drawio"
path, size, cells = b.save(out)
print(f"board: {path} ({size} bytes, {cells} cells, {b.w}x{b.h})")
