#!/usr/bin/env python3
"""Style example: radial topology on a dark ground.

Structure being drawn: one stateful core with six capability channels.
Why this style: there is no hierarchy to stack and no sequence to lay out — the
truth is "everything orbits the core", so the drawing is radial with straight
spokes and a dark technical register that suits an operator audience.

    python3 hub_network.py [out.drawio]
"""

import math
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

b = Board(1600, 1100, title="hub-network", theme="midnight", name="辐射拓扑（示例）")
t = b.t
CX, CY, R = 800, 620, 330
CORE_R = 110

# ---------------------------------------------------------------- header
b.text(80, 52, 600, 18, "AGENT RUNTIME / TOPOLOGY", 11, t.muted, True)
b.text(80, 74, 900, 52, "一个核心，六条能力链路", 36, t.ink, True)
b.text(80, 132, 1000, 22, "没有层级、没有先后：所有能力与核心等距，半径表示调用距离", 14, t.body)
b.text(1200, 78, 320, 18, "示例 · 虚构系统", 11, t.muted, False, "right")

# ---------------------------------------------------------------- rings + core
b.ellipse(CX - 380, CY - 380, 760, 760, stroke="#151F29", dashed=True)
b.ellipse(CX - 260, CY - 260, 520, 520, stroke="#1B2836", dashed=True)
b.ellipse(CX - CORE_R, CY - CORE_R, CORE_R * 2, CORE_R * 2, "#101A24", t.acc("primary").base, 1.6)
b.text(CX - 100, CY - 26, 200, 24, "AGENT CORE", 17, t.ink, True, "center")
b.text(CX - 100, CY + 2, 200, 18, "stateful · n=1", 11, t.muted, False, "center")

# ---------------------------------------------------------------- peers
peers = [
    ("E", "外部 API", "webhooks · 同步调用", "lime"),
    ("NE", "工具网关", "MCP · 内部服务", "primary"),
    ("NW", "知识库", "检索 · 4.2k 文档", "violet"),
    ("W", "消息入口", "IM · 邮件 · 工单", "primary"),
    ("SW", "记忆存储", "向量 + KV", "violet"),
    ("SE", "任务队列", "异步执行 · 重试", "amber"),
]
angles = {"E": 0, "NE": 60, "NW": 120, "W": 180, "SW": 240, "SE": 300}
BW, BH = 210, 86

boxes = {}
for key, title, meta, acc_key in peers:
    rad = math.radians(angles[key])
    px, py = CX + R * math.cos(rad), CY - R * math.sin(rad)
    boxes[key] = (px - BW / 2, py - BH / 2, title, meta, acc_key)


def hit_box(cx, cy, box, ux, uy):
    bx, by, bw, bh = box[0], box[1], BW, BH
    tmin, tmax = 0.0, 1e9
    for o, u, lo, hi in ((cx, ux, bx, bx + bw), (cy, uy, by, by + bh)):
        if abs(u) < 1e-9:
            if o < lo or o > hi:
                return None
        else:
            t1, t2 = (lo - o) / u, (hi - o) / u
            if t1 > t2:
                t1, t2 = t2, t1
            tmin, tmax = max(tmin, t1), min(tmax, t2)
    return tmin if tmin <= tmax else None


labels = {"E": "invoke", "W": "ingest", "NE": "tool calls"}
for key, (bx, by, title, meta, acc_key) in boxes.items():
    a = t.acc(acc_key)
    cx, cy = bx + BW / 2, by + BH / 2
    d = math.hypot(cx - CX, cy - CY)
    ux, uy = (cx - CX) / d, (cy - CY) / d
    t_end = hit_box(CX, CY, (bx, by), ux, uy) or R
    start = (CX + ux * (CORE_R + 4), CY + uy * (CORE_R + 4))
    end = (CX + ux * (t_end - 2), CY + uy * (t_end - 2))
    b.edge([start, end], a.base, 1.3, straight=True)
    if key in labels:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        b.text(mx - 45, my - 22, 90, 16, labels[key], 11, a.text, False, "center")

for key, (bx, by, title, meta, acc_key) in boxes.items():
    a = t.acc(acc_key)
    b.rect(bx, by, BW, BH, t.surface, t.line, 1.1, 6)
    b.line(bx, by + 10, 2.5, BH - 20, a.base)
    b.text(bx + 16, by + 18, BW - 28, 22, title, 15, t.ink, True)
    b.text(bx + 16, by + 42, BW - 28, 18, meta, 11, t.muted)

# ---------------------------------------------------------------- legend + footer
b.text(80, 936, 120, 16, "LEGEND", 11, t.muted, True)
for i, (acc_key, label) in enumerate([("primary", "控制面 · 入口与工具"),
                                      ("violet", "数据面 · 知识与会话"),
                                      ("amber", "异步执行")]):
    y = 960 + i * 24
    b.ellipse(80, y + 4, 7, 7, t.acc(acc_key).base, "none")
    b.text(98, y, 220, 18, label, 11, t.body)

b.text(1200, 1040, 320, 18, "midnight / radial", 11, t.muted, False, "right")

out = sys.argv[1] if len(sys.argv) > 1 else "hub-network.drawio"
path, size, cells = b.save(out)
print(f"board: {path} ({size} bytes, {cells} cells, {b.w}x{b.h})")
