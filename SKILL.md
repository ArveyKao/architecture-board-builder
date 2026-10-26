---
name: architecture-board-builder
description: Turn a system into a clear architecture diagram by choosing a visual language from its structure (layered, radial, tree, pipeline, states, matrix, anatomy…), then produce an editable draw.io file and import it as a native Feishu whiteboard. Use when asked to 画架构图 / 组件架构图 / 拓扑图 / 能力视图 / 归属图 / 状态图 / 演进图, to restyle a 飞书画板 or make a diagram clearer, or to regenerate one from a spec.
---

# Architecture Board Builder

## What this skill is for

Make the project legible. A diagram is a **model of a specific structure**, not a
template with text poured into it. So the work starts by naming the structure and
choosing the geometry that expresses it — layered bands, radial spokes, a tree, a
pipeline, a state graph, a matrix — and only then drawing.

`boardkit` supplies geometry, text metrics, four colour themes, preview and lint.
It deliberately imposes no layout.

## Workflow

1. **Read the structure.** Before any coordinates, write three lines: the entities
   (≤ 7 main blocks), each one's responsibility in ≤ 4 words, and the ≤ 6
   relationships that matter. Then name the shape: *layered / radial / tree /
   pipeline / state / matrix / anatomy / territory / timeline / comparison*.
   If you cannot name it, the picture is not ready.
2. **Choose encoding and register.** Pick one row from
   [references/structure-to-style.md](references/structure-to-style.md), and one
   register for the audience and medium (exec review, engineering deep-dive, doc
   illustration, slide, status). Then commit to five decisions: ground, type
   voice, line language, accent budget, density. Keep them for the whole board.
3. **Decide the medium.** An editable Feishu board imports as flat shapes
   (solid fills, strokes, text, arrows — no gradients or shadows); anything
   richer is better delivered as PNG/SVG. Read
   [references/feishu-whiteboard.md](references/feishu-whiteboard.md) before
   touching a board.
4. **Build.** Layout is literal in code; that is where the personality lives.
   ```python
   from boardkit import Board
   b = Board(1600, 1000, theme="paper")        # token set, not a layout
   t = b.t
   b.group(80, 160, 1440, 600, title="Runtime")
   b.node(120, 220, 260, 110, "Scheduler", sub="per-tenant queues", accent="primary")
   b.arrow([(380, 275), (520, 275)], label="claim", color=t.acc("primary").base)
   b.save("board.drawio")
   ```
   Primitives: `text`, `rect`, `line`, `ellipse`, `badge`, `node`, `group`,
   `edge(straight=…)`, `arrow(label=…)`. Themes: `paper`, `slate`, `midnight`,
   `mono` — they change tokens only.
5. **Look at it.** Lint, render a PNG, and actually read the image. Run the
   anti-template tests in `structure-to-style.md` and the checklist in
   [references/craft.md](references/craft.md) §9. Iterate at least once; the
   first render always has one weak spot.
6. **Deliver and keep sources.** Import into the whiteboard (or export the PNG),
   verify in the document, and keep `*.drawio` + preview + builder script.

## Quick start

```bash
SK=~/skills-manager/architecture-board-builder
mkdir -p /tmp/board && cd /tmp/board
cp "$SK/assets/examples/stacked_platform.py" board.py
python3 board.py                                  # -> stacked-platform.drawio
python3 "$SK/scripts/lint_board.py" stacked-platform.drawio
python3 "$SK/scripts/preview_svg.py" stacked-platform.drawio preview.html
"$SK/scripts/shot.sh" preview.html preview.png 1600 1000 2
```

## Three references, three languages

Do **not** reuse a sample layout by default; borrow the technique that fits.

| Sample | Structure | Register | Technique worth stealing |
| --- | --- | --- | --- |
| `assets/examples/stacked_platform.py` | four dependency layers | doc illustration (warm paper) | borderless strata, hairline rules, one tinted cell marking the hot path |
| `assets/examples/hub_network.py` | one core + six channels | engineering deep-dive (dark) | straight radial spokes, dashed boundary rings, one hue per channel |
| `assets/examples/tree_ownership.py` | ownership tree | minimal monochrome | type and rules only; the single red mark is spent on "unowned" |

## Invariants (independent of style)

- One dominant element. If two compete, the diagram has no point of view.
- Colour encodes exactly one meaning per hue, and the palette stays ≤ 4 accents.
- Body text ≥ 12px in a doc-embedded board (≥ 11px in a full-size export); text
  never overlaps strokes or other text.
- Prefer rearranging to crossing lines; a crossing usually means the encoding is
  wrong.
- The geometry alone should still convey the structure when all text is hidden.

Details, numbers and failure modes: [references/craft.md](references/craft.md).

## Working from an existing board

- There is no shape-level export. Open the board, screenshot it, and rebuild the
  content in a builder script; keep the original until the new one is verified.
- Importing a `.drawio` **appends** to the board. To replace: click empty canvas,
  `Meta+A`, `Delete`, then import.
- Confirm which block is the target by opening it and reading the title — block
  ids do not match visual order.
- After import, zoom with `ctrl + wheel` and check wrapping; then leave the board
  and reload the document to confirm persistence.

## If the content does not fit a picture

A relationship count below three, a pure list, or data the reader must compute
is better as prose, a table or a link. Say so instead of drawing a diagram that
adds nothing.

## Resources

- `scripts/boardkit.py` — primitives, four themes, text metrics, contrast-aware lint.
- `scripts/preview_svg.py` — draw.io → HTML/SVG preview with wrapping and arrowheads.
- `scripts/lint_board.py` — overflow, font floor, off-canvas, text/background contrast.
- `scripts/shot.sh` — headless Chrome screenshot (1x/2x).
- `scripts/serve_cors.py` — local CORS server for the Feishu import step.
- `assets/examples/` — three builder scripts, their `.drawio` files and previews.
