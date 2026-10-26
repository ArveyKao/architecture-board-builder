---
name: architecture-board-builder
description: Build bold, editable architecture and component-architecture boards as draw.io files, preview them locally, and import them into Feishu whiteboards. Use when asked to 画架构图 / 组件架构图 / 拓扑图 / 能力视图 / 平台图, to create or restyle a 飞书画板 (board) so it is 更醒目, or to regenerate such a diagram from a spec.
---

# Architecture Board Builder

## Overview

Turn a system story into a designed board — not a flowchart. The pipeline is:
**spec → `boardkit` builder → lint → PNG preview → Feishu whiteboard import**.
Every shape stays editable after import.

Read [references/design-system.md](references/design-system.md) before laying out a
new board, and [references/feishu-whiteboard.md](references/feishu-whiteboard.md)
before touching a Feishu board.

## Workflow

1. **Write the story before the shapes.** List the components, their 3–4
   responsibilities, the 3–6 relationships that matter, and the *one* thing that
   is the core of the system. If everything is equally important, the board will
   have no focal point.
2. **Assign zones.** Three numbered semantic layers (usually 入口 → 平台 → 执行),
   one idea per zone. Put the core component in a single dark block inside the
   middle zone.
3. **Write a builder script.** Start from
   [assets/examples/order_platform.py](assets/examples/order_platform.py); it
   reproduces the reference design end to end. Keep coordinates literal — the
   layout is the design.
4. **Lint, then look.** Run `lint_board.py`, then render `preview.png` and
   actually read the image. Fix text overflow, uneven gaps, arrows crossing
   cards, and any second focal point.
5. **Deliver.** Import into the target whiteboard; if replacing, select all and
   delete first (import appends). Verify in the board *and* in the document
   thumbnail after a reload.
6. **Keep sources.** Leave the `.drawio`, `preview.png`, and builder script next
   to the work; never treat an exported image as the backup.

## Quick start

```bash
SK=~/skills-manager/architecture-board-builder
mkdir -p /tmp/board && cd /tmp/board
cp "$SK/assets/examples/order_platform.py" board.py
python3 board.py                                    # -> order-platform.drawio
python3 "$SK/scripts/lint_board.py" order-platform.drawio
python3 "$SK/scripts/preview_svg.py" order-platform.drawio preview.html
"$SK/scripts/shot.sh" preview.html preview.png 2100 2260 2
```

Then open `preview.png` and iterate. `shot.sh` uses headless Chrome; pass
`CHROME=/path` if it is not in `/Applications`.

## The rules that carry the look

- **One dark block.** A single deep-navy focal card (`#0F2F6B`); everything else
  light. Two dark blocks cancel each other out.
- **Numbered zones.** `01 / 02 / 03` colored badges on tinted containers, each
  with a 28px title and a 16px subtitle. This is the narrative spine.
- **Fixed card anatomy.** Icon circle (single Chinese character), 24px title,
  15px subtitle in the accent's dark tone, ≤ 4 bullets at 15px, optional bottom
  pill showing where it hands off.
- **Color = category.** Blue entry/router, teal legacy path, green skills,
  violet knowledge/data, amber execution, slate resources. Max four accents.
- **Arrows carry verbs.** 3px, colored, labeled in the gap (`检索上下文`,
  `加载技能`); dashed means optional or planned. Never a bare 1px gray line.
- **Type floor 13.** Nothing below 13px on a 2100-wide canvas; the document
  thumbnail is ~5× smaller.

Full specs, spacing formulas and the three layout recipes (layered bands,
hub-and-spoke, swimlane pipeline) live in
[references/design-system.md](references/design-system.md).

## Working from an existing board

- There is no shape-level export. Open the board, screenshot it, and rebuild the
  content in a builder script; keep the original until the new one is verified.
- Importing a `.drawio` **appends** to the board. To replace: click empty canvas,
  `Meta+A`, `Delete`, then import.
- Confirm which block is the target by opening it and reading the title — block
  ids do not match visual order.
- After import, zoom with `ctrl + wheel` and check wrapping; then leave the board
  and reload the document to confirm persistence.

## Resources

- `scripts/boardkit.py` — primitives (`text`, `rect`, `card`, `section`, `pill`,
  `badge`, `circle`, `edge`, `arrow`), palette, text measurement and `lint`.
- `scripts/preview_svg.py` — draw.io → HTML/SVG preview with wrapping and
  arrowheads.
- `scripts/lint_board.py` — text overflow, font floor, off-canvas shapes.
- `scripts/shot.sh` — headless Chrome screenshot at 1x/2x.
- `scripts/serve_cors.py` — local CORS static server for the Feishu import step.
- `assets/examples/order_platform.py` — reference builder (fictional order-fulfilment system).
- `assets/examples/order-platform.drawio` + `preview.png` — reference output.
