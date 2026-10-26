#!/usr/bin/env python3
"""Boardkit: draw the "designed board" look into draw.io XML for Feishu whiteboard import.

Primitives map 1:1 to independent shapes (Feishu imports them as editable nodes):

    b = Board(2100, 2260, title="my-board")
    b.section(100, 356, 1900, 334, "01", "统一工作入口", "同一个入口，两种方式")
    b.card(136, 472, 880, 196, "飞书自然语言", "提出目标 / 定制需求",
           bullets=["用自然语言描述发版", "Gateway 交给用户 Runtime"],
           accent=BLUE, icon="言", caption="Gateway → 用户 Agent Runtime")
    b.arrow([(660, 600), (760, 600)], VIOLET, label="检索上下文")
    b.save("out.drawio")

Run `python3 lint_board.py out.drawio` to catch text overflow before importing.
"""

from __future__ import annotations

import html
import sys

# ---------------------------------------------------------------- palette
INK = "#0A1B33"
BODY = "#41546E"
MUTED = "#8A99AD"

BLUE = "#2563EB"
BLUE_D = "#1D4ED8"
TEAL = "#0D9488"
GREEN = "#059669"
VIOLET = "#7C3AED"
AMBER = "#B45309"
SLATE = "#475569"
NAVY = "#0F2F6B"

TINT = {
    BLUE: ("#EFF5FF", "#C7DAF4", BLUE_D),
    TEAL: ("#F0FAF8", "#B9E3DC", TEAL),
    GREEN: ("#F5FCF8", "#BFE2CE", "#166534"),
    VIOLET: ("#FAF8FF", "#D8CBF5", VIOLET),
    AMBER: ("#FFFCF6", "#EBCF9F", AMBER),
    SLATE: ("#F6F8FB", "#CBD5E1", SLATE),
}

SECTION_TINT = {
    BLUE: ("#F4F8FE", "#D6E4F7"),
    VIOLET: ("#F7F8FE", "#DBE2F2"),
    AMBER: ("#F8F9FC", "#DCE3ED"),
}

MIN_FONT = 13


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
    """Greedy wrap; CJK breaks per char, latin per word."""
    lines: list[str] = []
    for para in s.split("\n"):
        line, width = "", 0.0
        token, tw = "", 0.0
        for ch in para:
            cw = text_width(ch, size)
            is_cjk = ord(ch) >= 0x2E80
            if is_cjk:
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


# ---------------------------------------------------------------- board
class Board:
    def __init__(self, width: int = 2100, height: int = 2260, title: str = "board", name: str = ""):
        self.w, self.h = width, height
        self.title, self.name = title, name or title
        self.cells: list[str] = []
        self._id = 2

    # -- low level
    def _nid(self, prefix):
        self._id += 1
        return f"{prefix}{self._id}"

    def _vertex(self, prefix, value, style, x, y, w, h):
        self.cells.append(
            f'<mxCell id="{self._nid(prefix)}" value="{html.escape(value, quote=True)}" '
            f'style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )

    # -- text
    def text(self, x, y, w, h, s, size=17, color=BODY, bold=False,
             align="left", valign="middle"):
        style = (
            "text;html=1;strokeColor=none;fillColor=none;rounded=0;whiteSpace=wrap;"
            f"align={align};verticalAlign={valign};fontSize={size};fontColor={color};"
        )
        if bold:
            style += "fontStyle=1;"
        value = s.replace("\n", "<br>")
        self._vertex("t", value, style, x, y, w, h)
        return self

    # -- shapes
    def rect(self, x, y, w, h, fill="#FFFFFF", stroke="none", sw=1.0, r=4, dashed=False):
        style = (
            "rounded=1;whiteSpace=wrap;html=1;"
            f"fillColor={fill};strokeColor={stroke};strokeWidth={sw};arcSize={r};"
        )
        if dashed:
            style += "dashed=1;dashPattern=9 7;"
        self._vertex("r", "", style, x, y, w, h)
        return self

    def circle(self, x, y, d, fill, stroke, s="", color=INK, size=20, sw=2):
        style = (
            "ellipse;whiteSpace=wrap;html=1;"
            f"fillColor={fill};strokeColor={stroke};strokeWidth={sw};fontSize={size};"
            f"fontStyle=1;fontColor={color};align=center;verticalAlign=middle;"
        )
        self._vertex("c", s, style, x, y, d, d)
        return self

    def badge(self, x, y, w, h, s, fill, color="#FFFFFF", size=22, r=18, sw=0, stroke="none"):
        style = (
            "rounded=1;whiteSpace=wrap;html=1;"
            f"arcSize={r};fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
            f"fontSize={size};fontStyle=1;fontColor={color};align=center;verticalAlign=middle;"
        )
        self._vertex("b", s, style, x, y, w, h)
        return self

    def pill(self, x, y, w, h, s, fill, stroke, color, size=14, sw=1.5):
        return self.badge(x, y, w, h, s, fill, color, size, 50, sw, stroke)

    # -- composites
    def card(self, x, y, w, h, title, sub=None, bullets=(), accent=BLUE,
             icon=None, caption=None, caption_align="right", fill=None, r=5,
             title_size=24, bullet_size=15, bullet_w=None, dark=False, sub_color=None):
        """Standard card: icon circle + title + subtitle + bullets + optional caption.

        `caption` becomes a pill in the bottom-right when it contains "→",
        otherwise small meta text. Bullets auto-narrow to clear the pill.
        """
        light, border, accent_text = TINT.get(accent, ("#F6F8FB", "#CBD5E1", accent))
        fill = fill or "#FFFFFF"
        self.rect(x, y, w, h, fill, border, 2, r)
        tx = x + 28
        if icon:
            self.circle(x + 28, y + 26, 50, light, border, icon, accent, 20)
            tx = x + 96
        self.text(tx, y + 22, x + w - tx - 28, 32, title, title_size,
                  "#FFFFFF" if dark else INK, True)
        if sub:
            self.text(tx, y + 56, x + w - tx - 28, 24, sub, 15,
                      sub_color or ("#A9C6F5" if dark else accent_text))
        pill_caption = bool(caption and "→" in caption)
        bw = bullet_w or (w - 360 if pill_caption else w - 56)
        by = y + 100 if icon else y + 92
        for i, b in enumerate(bullets):
            self.text(x + 28, by + i * 30, bw, 24, b, bullet_size,
                      "#EAF2FF" if dark else BODY)
        if caption:
            if pill_caption:
                self.pill(x + w - 320, y + h - 54, 292, 38, caption, light, border, accent_text, 13)
            else:
                self.text(x + 28, y + h - 38, w - 56, 22, caption, 13,
                          MUTED if not dark else "#7FA3D8", False, caption_align)
        return self

    def section(self, x, y, w, h, num, title, sub=None, right=None,
                accent=BLUE, badge_fill=None, badge_color="#FFFFFF", r=3):
        fill, stroke = SECTION_TINT.get(accent, ("#F7F8FB", "#DCE3ED"))
        self.rect(x, y, w, h, fill, stroke, 1.5, r)
        self.badge(x + 36, y + 26, 54, 54, num, badge_fill or accent, badge_color, 22)
        self.text(x + 106, y + 24, w - 460, 34, title, 28, INK, True)
        if sub:
            self.text(x + 106, y + 58, w - 460, 26, sub, 16, "#64748B")
        if right:
            self.text(x + w - 500, y + 38, 464, 24, right, 14, "#8FA0B5", False, "right")
        return y + 116

    # -- arrows
    def edge(self, points, color, width=2.6, dashed=False, start=False, end=True):
        pts = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points[1:-1])
        style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
            f"strokeColor={color};strokeWidth={width};"
            "endArrow=block;endFill=1;endSize=7;"
        )
        if dashed:
            style += "dashed=1;dashPattern=9 7;"
        if start:
            style += "startArrow=block;startFill=1;startSize=7;"
        if not end:
            style += "endArrow=none;"
        sx, sy = points[0]
        tx, ty = points[-1]
        self.cells.append(
            f'<mxCell id="{self._nid("e")}" value="" style="{style}" edge="1" parent="1">'
            '<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{sx}" y="{sy}" as="sourcePoint"/>'
            f'<mxPoint x="{tx}" y="{ty}" as="targetPoint"/>'
            f'<Array as="points">{pts}</Array></mxGeometry></mxCell>'
        )
        return self

    def arrow(self, points, color, label=None, width=2.6, dashed=False, start=False,
              label_size=13, label_dy=-31):
        """Edge plus a centered label placed above the midpoint of the gap."""
        self.edge(points, color, width, dashed, start)
        if label:
            (x1, y1), (x2, y2) = points[0], points[-1]
            if abs(x2 - x1) >= abs(y2 - y1):
                mid, span = (x1 + x2) / 2, abs(x2 - x1)
                self.text(mid - max(span, 90) / 2, min(y1, y2) + label_dy,
                          max(span, 90), 22, label, label_size, color, True, "center")
            else:
                mid = (y1 + y2) / 2
                self.text(x1 + 12, mid - 11, 200, 22, label, label_size, color, True)
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
        style = c.get("style") or ""
        out.append(dict(style=style, value=c.get("value") or "", edge=c.get("edge") == "1",
                        x=float(g.get("x") or 0), y=float(g.get("y") or 0),
                        w=float(g.get("width") or 0), h=float(g.get("height") or 0)))
    return page, out


def lint_file(path, min_font=MIN_FONT):
    page, cells = _parse_cells(open(path, encoding="utf-8").read())
    issues = []
    for c in cells:
        if c["edge"]:
            continue
        st = dict(kv.split("=", 1) for kv in c["style"].split(";") if "=" in kv)
        if c["x"] < 0 or c["y"] < 0 or c["x"] + c["w"] > page[0] or c["y"] + c["h"] > page[1]:
            issues.append(f"off-canvas at ({c['x']:.0f},{c['y']:.0f}) {c['value'][:24]!r}")
        if "fontSize" in st:
            size = float(st["fontSize"])
            if size < min_font:
                issues.append(f"font {size:g} < {min_font}: {c['value'][:24]!r}")
            if c["value"] and st.get("whiteSpace") == "wrap":
                text = c["value"].replace("<br>", "\n")
                text = html.unescape(text)
                longest = max(text_width(line, size) for line in text.split("\n"))
                if longest > c["w"] + 2:
                    issues.append(
                        f"overflow {longest:.0f}px > {c['w']:.0f}px (size {size:g}): {text[:30]!r}")
    return page, issues


