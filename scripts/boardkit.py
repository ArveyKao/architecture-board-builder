#!/usr/bin/env python3
"""Boardkit: draw.io primitives that stay out of the way of layout decisions.

The kit gives you geometry, text metrics, themes and lint — not a house style.

    from boardkit import Board, theme
    b = Board(1600, 1000, title="my-board", theme="paper")

    t = b.t
    a = t.acc("primary")
    b.group(80, 120, 1440, 640, title="Runtime", accent=a, dashed=True)
    b.node(120, 180, 280, 120, "Scheduler", sub="per-tenant queues", accent=a)
    b.edge([(400, 240), (520, 240)], straight=True, color=a.base, label="claim")
    b.save("out.drawio")

Themes only supply tokens (background, ink, lines, accents, radius). Two boards
with the same tokens can still look completely different — that is the point.

Run `python3 lint_board.py out.drawio` before importing: text overflow, font
floor, off-canvas shapes and low text/background contrast.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field


# ---------------------------------------------------------------- themes
@dataclass
class Accent:
    base: str
    soft: str
    edge: str
    text: str


@dataclass
class Theme:
    name: str
    bg: str
    ink: str
    body: str
    muted: str
    line: str
    surface: str
    radius: float = 4
    stroke: float = 1.5
    font: str = "PingFang SC"
    accents: dict = field(default_factory=dict)

    def acc(self, key="primary") -> Accent:
        if key in self.accents:
            return self.accents[key]
        keys = list(self.accents)
        return self.accents[keys[0]] if keys else Accent("#333333", "#F2F2F2", "#CCCCCC", "#333333")


THEMES = {
    # Warm editorial: paper, hairlines, one hot accent. Good for doc illustrations.
    "paper": Theme(
        name="paper", bg="#FAF8F3", ink="#17140F", body="#3F3A32",
        muted="#6E6557", line="#DAD2C2", surface="#FFFFFF", radius=2, stroke=1.3,
        accents={
            "primary": Accent("#B4552D", "#F7E7DC", "#E3C1AB", "#8E3F1F"),
            "secondary": Accent("#3F5D4E", "#E7EEE9", "#C6D6CC", "#2F4A3C"),
            "signal": Accent("#A98A1C", "#F7EFD6", "#E5D5A2", "#7C6510"),
            "quiet": Accent("#6B665C", "#EFECE5", "#D6D0C4", "#4C473F"),
        },
    ),
    # Cool product UI: white cards, tinted icons, clear borders. Safe default.
    "slate": Theme(
        name="slate", bg="#FFFFFF", ink="#0A1B33", body="#41546E",
        muted="#64748B", line="#D9E3F0", surface="#FFFFFF", radius=5, stroke=1.6,
        accents={
            "primary": Accent("#2563EB", "#EFF5FF", "#C7DAF4", "#1D4ED8"),
            "secondary": Accent("#0D9488", "#F0FAF8", "#B9E3DC", "#0B6B63"),
            "success": Accent("#059669", "#F5FCF8", "#BFE2CE", "#166534"),
            "knowledge": Accent("#7C3AED", "#FAF8FF", "#D8CBF5", "#5B21B6"),
            "exec": Accent("#B45309", "#FFFCF6", "#EBCF9F", "#8A3F06"),
            "neutral": Accent("#475569", "#F6F8FB", "#CBD5E1", "#334155"),
        },
    ),
    # Dark technical: near-black ground, fine strokes, luminous accents.
    "midnight": Theme(
        name="midnight", bg="#0A0D12", ink="#E8F1FF", body="#A9BACD",
        muted="#7F93A8", line="#1E2A36", surface="#0E141B", radius=4, stroke=1.2,
        accents={
            "primary": Accent("#4CC9F0", "#0E2A33", "#1C4A57", "#9BE3F7"),
            "violet": Accent("#A78BFA", "#1A1730", "#33295C", "#C7B6FF"),
            "lime": Accent("#A3E635", "#16210E", "#32421A", "#CDF08A"),
            "amber": Accent("#FBBF24", "#241B08", "#453412", "#FDE08B"),
        },
    ),
    # Monochrome: type and rules only, one signal color used sparingly.
    "mono": Theme(
        name="mono", bg="#FFFFFF", ink="#111111", body="#444444",
        muted="#6F6F6F", line="#C9C9C9", surface="#F5F5F5", radius=0, stroke=1.1,
        accents={
            "primary": Accent("#111111", "#F2F2F2", "#C9C9C9", "#111111"),
            "quiet": Accent("#666666", "#F5F5F5", "#D5D5D5", "#555555"),
            "signal": Accent("#B3261E", "#FBEAE8", "#E7C3BE", "#8C1D17"),
        },
    ),
}


def theme(name: str) -> Theme:
    if name not in THEMES:
        raise KeyError(f"unknown theme {name!r}; choose from {', '.join(THEMES)}")
    return THEMES[name]


# ---------------------------------------------------------------- text metrics
def text_width(s: str, size: float) -> float:
    """Rough advance width: CJK/fullwidth = 1em, latin lower 0.53em, upper 0.62em."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80:
            w += size
        elif ch == " ":
            w += size * 0.3
        elif ch in "il.,:;!|'`()[]":
            w += size * 0.3
        elif ch.isupper():
            w += size * 0.62
        else:
            w += size * 0.53
    return w


def wrap(s: str, size: float, maxw: float) -> list[str]:
    lines: list[str] = []
    for para in s.split("\n"):
        line, width = "", 0.0
        token, tw = "", 0.0
        for ch in para:
            cw = text_width(ch, size)
            if ord(ch) >= 0x2E80:
                if token:
                    if width + tw > maxw and line:
                        lines.append(line); line, width = "", 0.0
                    line += token; width += tw; token, tw = "", 0.0
                if width + cw > maxw and line:
                    lines.append(line); line, width = "", 0.0
                line += ch; width += cw
            elif ch == " ":
                if token:
                    if width + tw > maxw and line:
                        lines.append(line); line, width = "", 0.0
                    line += token; width += tw; token, tw = "", 0.0
                if width + cw > maxw and line:
                    lines.append(line); line, width = "", 0.0
                line += ch; width += cw
            else:
                token += ch; tw += cw
        if token:
            if width + tw > maxw and line:
                lines.append(line); line, width = "", 0.0
            line += token; width += tw
        lines.append(line)
    return lines or [""]


def _lum(color: str) -> float:
    c = color.lstrip("#")[:6]
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    try:
        r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return 1.0
    def f(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- board
class Board:
    def __init__(self, width: int, height: int, title: str = "board",
                 theme: str | Theme = "slate", name: str = "", paint_bg: bool = True):
        self.w, self.h = width, height
        self.title, self.name = title, name or title
        self.t: Theme = globals()["theme"](theme) if isinstance(theme, str) else theme
        self.cells: list[str] = []
        self._id = 2
        if paint_bg and self.t.bg.lower() != "#ffffff":
            self.rect(0, 0, width, height, fill=self.t.bg, stroke="none", r=0)

    # -- internals
    def _nid(self, prefix):
        self._id += 1
        return f"{prefix}{self._id}"

    def _vertex(self, prefix, value, style, x, y, w, h):
        self.cells.append(
            f'<mxCell id="{self._nid(prefix)}" value="{html.escape(value, quote=True)}" '
            f'style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )

    def _accent(self, accent):
        if accent is None:
            return None
        return accent if isinstance(accent, Accent) else self.t.acc(accent)

    # -- text
    def text(self, x, y, w, h, s, size=15, color=None, bold=False, italic=False,
             align="left", valign="middle", font=None):
        t = self.t
        color = color or t.body
        style = (
            "text;html=1;strokeColor=none;fillColor=none;rounded=0;whiteSpace=wrap;"
            f"align={align};verticalAlign={valign};fontSize={size};fontColor={color};"
        )
        if font or t.font:
            style += f"fontFamily={font or t.font};"
        fs = (1 if bold else 0) + (2 if italic else 0)
        if fs:
            style += f"fontStyle={fs};"
        self._vertex("t", s.replace("\n", "<br>"), style, x, y, w, h)
        return self

    # -- shapes
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=None, r=None, dashed=False):
        t = self.t
        style = (
            "rounded=1;whiteSpace=wrap;html=1;"
            f"fillColor={fill};strokeColor={stroke or 'none'};"
            f"strokeWidth={sw if sw is not None else t.stroke};"
            f"arcSize={r if r is not None else t.radius};"
        )
        if dashed:
            style += "dashed=1;dashPattern=8 6;"
        self._vertex("r", "", style, x, y, w, h)
        return self

    def line(self, x, y, w, h, color=None, sw=None, dashed=False):
        return self.rect(x, y, w, h, fill=color or self.t.line, stroke="none", sw=0,
                         r=0, dashed=dashed)

    def ellipse(self, x, y, w, h, fill="none", stroke=None, sw=None, dashed=False,
                s="", color=None, size=15, bold=False):
        t = self.t
        style = (
            "ellipse;whiteSpace=wrap;html=1;"
            f"fillColor={fill};strokeColor={stroke or 'none'};"
            f"strokeWidth={sw if sw is not None else t.stroke};"
            f"fontSize={size};fontColor={color or t.ink};align=center;verticalAlign=middle;"
        )
        if bold:
            style += "fontStyle=1;"
        if dashed:
            style += "dashed=1;dashPattern=8 6;"
        self._vertex("o", s.replace("\n", "<br>"), style, x, y, w, h)
        return self

    def badge(self, x, y, w, h, s, fill=None, color=None, size=13, r=50, stroke="none",
              sw=1.0, bold=True):
        t = self.t
        style = (
            "rounded=1;whiteSpace=wrap;html=1;"
            f"arcSize={r};fillColor={fill or t.surface};strokeColor={stroke};strokeWidth={sw};"
            f"fontSize={size};fontColor={color or t.ink};align=center;verticalAlign=middle;"
        )
        if bold:
            style += "fontStyle=1;"
        self._vertex("b", s, style, x, y, w, h)
        return self

    # -- composites
    def node(self, x, y, w, h, title, sub=None, lines=(), accent="primary",
             fill=None, stroke=None, sw=None, r=None, icon=None, caption=None,
             title_size=20, sub_size=13, line_size=13, align="left",
             title_color=None, dashed=False, icon_size=20, icon_d=40, pad=20):
        """A box that carries a name, an optional role line and optional bullets.

        Nothing about the look is fixed: pass `fill`/`stroke`/`r` or rely on the
        accent. `caption` ending in "→" becomes a pill; otherwise it is meta text.
        """
        a = self._accent(accent)
        t = self.t
        fill = fill if fill is not None else (a.soft if a else "none")
        stroke = stroke if stroke is not None else (a.edge if a else "none")
        self.rect(x, y, w, h, fill, stroke, sw, r, dashed)
        tx = x + pad
        if icon:
            self.ellipse(x + pad, y + pad, icon_d, icon_d, fill=t.bg, stroke=stroke,
                         s=icon, color=a.base if a else t.ink, size=icon_size, bold=True)
            tx = x + pad + icon_d + 16
        title_color = title_color or t.ink
        self.text(tx, y + pad - 2, x + w - tx - pad, 26, title, title_size,
                  title_color, True, align=align)
        if sub:
            self.text(tx, y + pad + 24, x + w - tx - pad, 20, sub, sub_size,
                      a.text if a else t.muted, align=align)
        by = y + (pad + 52 if (sub or icon) else 34)
        for i, line in enumerate(lines):
            self.text(x + pad, by + i * 24, w - pad * 2, 20, line, line_size, t.body)
        if caption:
            if "→" in caption:
                self.badge(x + w - 12 - max(150, text_width(caption, 12) + 24), y + h - 34,
                           max(150, text_width(caption, 12) + 24), 24, caption,
                           fill=t.bg, color=a.text if a else t.muted, stroke=stroke, size=12)
            else:
                self.text(x + pad, y + h - 28, w - pad * 2, 18, caption, 12, t.muted,
                          align="right")
        return self

    def group(self, x, y, w, h, title=None, accent=None, fill=None, stroke=None,
              dashed=False, r=None, title_align="left", title_size=12, title_color=None,
              num=None, num_bg=None, pad=16):
        """A container. Draw it before its children.

        `num` renders a small square badge left of the title (a numbering device,
        not a requirement).
        """
        a = self._accent(accent)
        t = self.t
        fill = fill if fill is not None else "none"
        stroke = stroke if stroke is not None else (a.edge if a else t.line)
        self.rect(x, y, w, h, fill, stroke, None, r, dashed)
        tx = x + pad
        if num:
            self.badge(x + pad, y + pad, 26, 26, str(num), fill=num_bg or (a.base if a else t.ink),
                       color=t.bg, size=12, r=4, bold=True)
            tx = x + pad + 34
        if title:
            self.text(tx, y + pad - 1, w - (tx - x) - pad, 24, title, title_size,
                      title_color or (a.text if a else t.muted), True, align=title_align)
        return self

    # -- arrows
    def edge(self, points, color=None, width=None, dashed=False, start=False, end=True,
             straight=False, arrow_size=8):
        t = self.t
        color = color or t.line
        width = width if width is not None else t.stroke
        pts = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points[1:-1])
        style = (
            f"edgeStyle={'none' if straight else 'orthogonalEdgeStyle'};rounded=0;html=1;"
            f"strokeColor={color};strokeWidth={width};"
        )
        style += ("endArrow=block;endFill=1;endSize=8;"
                  if end else "endArrow=none;")
        if dashed:
            style += "dashed=1;dashPattern=8 6;"
        if start:
            style += "startArrow=block;startFill=1;startSize=8;"
        sx, sy = points[0]
        tx_, ty_ = points[-1]
        self.cells.append(
            f'<mxCell id="{self._nid("e")}" value="" style="{style}" edge="1" parent="1">'
            '<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{sx}" y="{sy}" as="sourcePoint"/>'
            f'<mxPoint x="{tx_}" y="{ty_}" as="targetPoint"/>'
            f'<Array as="points">{pts}</Array></mxGeometry></mxCell>'
        )
        return self

    def arrow(self, points, label=None, color=None, width=None, dashed=False,
              straight=False, start=False, label_size=11, label_dy=-22,
              label_align="center", label_color=None):
        """Edge plus a label anchored near the middle of the run.

        Labels default to body text (not the stroke color) so thin hairlines stay
        readable; pass `label_color` when the label should carry the accent.
        """
        self.edge(points, color, width, dashed, start, True, straight)
        if not label:
            return self
        stroke = color or self.t.line
        color = label_color or (stroke if color else self.t.body)
        if color == self.t.line:
            color = self.t.body
        (x1, y1), (x2, y2) = points[0], points[-1]
        if abs(x2 - x1) >= abs(y2 - y1):
            cx, span = (x1 + x2) / 2, abs(x2 - x1)
            w = max(span, 80)
            self.text(cx - w / 2, min(y1, y2) + label_dy, w, 18, label, label_size,
                      color, True, label_align)
        else:
            cy = (y1 + y2) / 2
            self.text(x1 + 10, cy - 9, 180, 18, label, label_size, color, True)
        return self

    # -- output
    def save(self, path="board.drawio"):
        xml = (
            '<mxfile host="app.diagrams.net" modified="2026-01-01T00:00:00.000Z" '
            'agent="architecture-board-builder" version="24.0.0">'
            f'<diagram id="{self.title}" name="{self.name}">'
            f'<mxGraphModel dx="1500" dy="1000" grid="0" gridSize="10" guides="1" '
            'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="{self.w}" pageHeight="{self.h}" math="0" shadow="0">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            + "".join(self.cells)
            + "</root></mxGraphModel></diagram></mxfile>"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
        return path, len(xml), self._id - 1


# ---------------------------------------------------------------- lint
def _parse_cells(xml_text):
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_text)
    model = root.find(".//mxGraphModel")
    page = (int(model.get("pageWidth")), int(model.get("pageHeight")))
    out = []
    for c in root.iter("mxCell"):
        g = c.find("mxGeometry")
        if g is None:
            continue
        out.append(dict(
            style=c.get("style") or "",
            value=c.get("value") or "",
            edge=c.get("edge") == "1",
            x=float(g.get("x") or 0), y=float(g.get("y") or 0),
            w=float(g.get("width") or 0), h=float(g.get("height") or 0),
        ))
    return page, out


def _props(style: str) -> dict:
    return dict(kv.split("=", 1) for kv in style.split(";") if "=" in kv)


def lint_file(path, min_font=11, check_contrast=True):
    page, cells = _parse_cells(open(path, encoding="utf-8").read())
    bg = "#FFFFFF"
    if cells and cells[0]["w"] >= page[0] * 0.98 and cells[0]["h"] >= page[1] * 0.98:
        bg = _props(cells[0]["style"]).get("fillColor", bg)

    issues, stacked = [], []
    for c in cells:
        if c["edge"]:
            continue
        st = _props(c["style"])
        fill = st.get("fillColor", "none")
        is_text = c["style"].startswith("text;") or "strokeColor=none;fillColor=none;rounded=0" in c["style"]
        if c["x"] < 0 or c["y"] < 0 or c["x"] + c["w"] > page[0] + 1 or c["y"] + c["h"] > page[1] + 1:
            issues.append(("error", f"off-canvas at ({c['x']:.0f},{c['y']:.0f}) {c['value'][:24]!r}"))
        if not is_text:
            if fill not in ("none", "", None):
                stacked.append((c["x"], c["y"], c["w"], c["h"], fill))
            continue

        size = float(st.get("fontSize", 12))
        text = html.unescape(c["value"]).replace("<br>", "\n")
        if size < min_font:
            issues.append(("error", f"font {size:g} < {min_font}: {text[:24]!r}"))
        if text:
            longest = max(text_width(line, size) for line in text.split("\n"))
            if longest > c["w"] + 2:
                issues.append(("error",
                               f"overflow {longest:.0f}>{c['w']:.0f}px ({size:g}): {text[:28]!r}"))

        if check_contrast and text:
            cx, cy = c["x"] + c["w"] / 2, c["y"] + c["h"] / 2
            under = bg
            for sx, sy, sw_, sh, sfill in stacked:
                if sx <= cx <= sx + sw_ and sy <= cy <= sy + sh:
                    under = sfill
            fg = st.get("fontColor", "#000000")
            ratio = contrast(fg, under)
            if ratio < 3.0:
                issues.append(("error", f"contrast {ratio:.1f}:1 {fg} on {under}: {text[:24]!r}"))
            elif ratio < 4.5 and size < 18:
                issues.append(("warn", f"contrast {ratio:.1f}:1 {fg} on {under}: {text[:24]!r}"))
    return page, issues


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3 or sys.argv[1] != "lint":
        print("usage: boardkit.py lint <file.drawio>")
        raise SystemExit(2)
    page, issues = lint_file(sys.argv[2])
    print(f"canvas {page[0]}x{page[1]}")
    if not issues:
        print("lint: clean")
        raise SystemExit(0)
    errs = [i for i in issues if i[0] == "error"]
    print(f"lint: {len(errs)} error(s), {len(issues) - len(errs)} warning(s)")
    for level, msg in issues[:40]:
        print(f"  {level}: {msg}")
    if len(issues) > 40:
        print(f"  ... {len(issues) - 40} more")
    raise SystemExit(1 if errs else 0)
