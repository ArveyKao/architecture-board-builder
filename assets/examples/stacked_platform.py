#!/usr/bin/env python3
"""Style example: layered strata, editorial paper, no boxes.

Structure being drawn: four dependency layers of an analytics platform.
Why this style: layers stack, so the drawing is horizontal strata with a type
rail on the left and hairline separators — no cards, no numbers, no navy block.

    python3 stacked_platform.py [out.drawio]
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

b = Board(1600, 1000, title="stacked-platform", theme="paper", name="分层视图（示例）")
t = b.t
hot = t.acc("primary")
warm = t.acc("signal")

# ---------------------------------------------------------------- header
b.text(80, 56, 500, 18, "PLATFORM ANATOMY / SAMPLE", 11, t.muted, True)
b.text(80, 78, 900, 54, "分析平台的四层结构", 38, t.ink, True)
b.text(80, 138, 1000, 24, "同一份数据，四个职责层：接入 → 存储 → 计算 → 服务", 14, t.body)
b.text(1180, 84, 340, 18, "示例 · 虚构系统", 11, t.muted, False, "right")
b.line(80, 182, 1440, 1.2, t.line)

# ---------------------------------------------------------------- strata
bands = [
    ("04", "服务层", "对外契约与配额", 220, "SLA 99.9%",
     [("API 网关", "REST / gRPC"), ("查询服务", "SQL 联邦"),
      ("报表引擎", "异步导出"), ("权限中心", "租户隔离")]),
    ("03", "计算层", "算子与调度", 396, "峰值 4k QPS",
     [("批处理", "T+1 全量"), ("流计算", "秒级窗口"),
      ("特征工程", "离线特征")]),
    ("02", "存储层", "一份事实来源", 572, "日均 12 TB",
     [("对象存储", "原始文件"), ("数仓", "分层建模"),
      ("缓存", "热点数据"), ("元数据", "schema 注册")]),
    ("01", "接入层", "边缘采集", 748, "8 个来源",
     [("日志采集", "agent 推送"), ("CDC", "binlog"), ("文件同步", "SFTP / OSS")]),
]
BAND_X, BAND_W, ROW_H = 300, 1220, 132
COL_W = 230

for num, name, role, y, note, items in bands:
    b.text(80, y + 4, 190, 28, f"{num}  {name}", 19, t.ink, True)
    b.text(80, y + 38, 190, 18, role, 11, t.muted)
    b.line(BAND_X, y, BAND_W, 1.1, t.line)
    b.text(BAND_X + BAND_W - 200, y + 104, 200, 18, note, 11, t.muted, False, "right")
    for i in range(1, len(items)):
        b.line(BAND_X + 30 + i * COL_W, y + 26, 1, 84, t.line)
    for i, (title, meta) in enumerate(items):
        ix = BAND_X + 30 + i * COL_W
        if num == "03" and title == "流计算":
            b.rect(ix - 12, y + 16, COL_W - 16, 100, hot.soft, "none", 0, 2)
            b.line(ix - 12, y + 16, 2.5, 100, hot.base)
        b.text(ix, y + 24, COL_W - 24, 22, title, 15, t.ink, True)
        b.text(ix, y + 48, COL_W - 24, 18, meta, 11, t.muted)

# ---------------------------------------------------------------- dependency arrows (upward)
for y_from, y_to, label in ((748, 704, "写入"), (572, 528, "读取"), (396, 352, "查询 / API")):
    b.arrow([(900, y_from), (900, y_to)], label=label, color=t.line, width=1.2)

# ---------------------------------------------------------------- footer
b.text(80, 930, 900, 18, "分层视图只表达依赖方向；调用时序请另画一张。", 11, t.muted)
b.text(1180, 930, 340, 18, "paper / strata", 11, t.muted, False, "right")

out = sys.argv[1] if len(sys.argv) > 1 else "stacked-platform.drawio"
path, size, cells = b.save(out)
print(f"board: {path} ({size} bytes, {cells} cells, {b.w}x{b.h})")
