#!/usr/bin/env python3
"""Render a .drawio file to a local HTML/SVG preview (no network, no draw.io app).

    python3 preview_svg.py board.drawio preview.html
    scripts/shot.sh preview.html preview.png 2100 2260 2

The preview is an approximation of how Feishu's whiteboard importer draws the
same shapes: rounded rects, dashed strokes, arrowheads, wrapped text.
Read the PNG before importing; it is much cheaper than fixing a board in place.
"""

import html
import math
import sys
import xml.etree.ElementTree as ET

from boardkit import wrap


def prop(style, key, default=None):
    for kv in style.split(";"):
        if kv.startswith(key + "="):
            return kv.split("=", 1)[1]
    return default


def build(src, out):
    root = ET.parse(src).getroot()
    model = root.find(".//mxGraphModel")
    W, H = int(model.get("pageWidth")), int(model.get("pageHeight"))
    parts = []

    for c in root.iter("mxCell"):
        g = c.find("mxGeometry")
        if g is None:
            continue
        st = c.get("style") or ""
        value = html.unescape(c.get("value") or "").replace("<br>", "\n")

        if c.get("edge") == "1":
            sp = g.find("mxPoint[@as='sourcePoint']")
            tp = g.find("mxPoint[@as='targetPoint']")
            pts = [(float(sp.get("x")), float(sp.get("y")))]
            arr = g.find("Array")
            if arr is not None:
                pts += [(float(p.get("x")), float(p.get("y"))) for p in arr.findall("mxPoint")]
            pts.append((float(tp.get("x")), float(tp.get("y"))))
            color = prop(st, "strokeColor", "#333")
            width = float(prop(st, "strokeWidth", "2"))
            dash = 'stroke-dasharray="9 7"' if prop(st, "dashed") == "1" else ""
            d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
            parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
                         f'stroke-linejoin="round" {dash}/>')
            if prop(st, "endArrow", "block") != "none":
                parts.append(_head(pts[-2], pts[-1], color))
            if prop(st, "startArrow") == "block":
                parts.append(_head(pts[1], pts[0], color))
            continue

        x, y = float(g.get("x") or 0), float(g.get("y") or 0)
        w, h = float(g.get("width") or 0), float(g.get("height") or 0)
        fill = prop(st, "fillColor", "none")
        stroke = prop(st, "strokeColor", "none")
        sw = float(prop(st, "strokeWidth", "1"))
        dash = 'stroke-dasharray="9 7"' if prop(st, "dashed") == "1" else ""

        if "ellipse" in st:
            parts.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" '
                         f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {dash}/>')
        elif fill != "none" or stroke != "none":
            rx = 0.0
            if prop(st, "rounded") == "1":
                rx = min(w, h) * float(prop(st, "arcSize", "8")) / 100
                rx = min(rx, min(w, h) / 2)
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx:.1f}" '
                         f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {dash}/>')

        if value:
            size = float(prop(st, "fontSize", "17"))
            color = prop(st, "fontColor", "#111827")
            bold = "bold" if prop(st, "fontStyle", "0") == "1" else "normal"
            align = prop(st, "align", "left")
            valign = prop(st, "verticalAlign", "middle")
            pad = 8
            maxw = max(w - pad * 2, size * 2)
            lines = wrap(value, size, maxw)
            line_h = size * 1.34
            total = line_h * len(lines)
            if valign == "top":
                first = y + size * 1.05
            elif valign == "bottom":
                first = y + h - total + line_h * 0.75
            else:
                first = y + (h - total) / 2 + size * 0.94
            anchor = {"left": "start", "center": "middle", "right": "end"}[align]
            tx = x + pad if align == "left" else (x + w - pad if align == "right" else x + w / 2)
            for i, line in enumerate(lines):
                parts.append(
                    f'<text x="{tx}" y="{first + i*line_h:.1f}" font-size="{size}" '
                    f'fill="{color}" font-weight="{bold}" text-anchor="{anchor}" '
                    f'font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, '
                    f'Helvetica, sans-serif">{html.escape(line)}</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
           + "".join(parts) + "</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write('<!doctype html><meta charset="utf-8">'
                '<body style="margin:0;background:#fff">' + svg + "</body>")
    print(f"preview: {out} ({W}x{H})")
    return out


def _head(p0, p1, color):
    (x0, y0), (x1, y1) = p0, p1
    ang = math.atan2(y1 - y0, x1 - x0)
    L = 10
    a = (x1 - L * math.cos(ang - 0.42), y1 - L * math.sin(ang - 0.42))
    b = (x1 - L * math.cos(ang + 0.42), y1 - L * math.sin(ang + 0.42))
    return (f'<path d="M {a[0]:.1f},{a[1]:.1f} L {x1},{y1} L {b[0]:.1f},{b[1]:.1f} z" '
            f'fill="{color}"/>')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: preview_svg.py <in.drawio> <out.html>")
        sys.exit(2)
    build(sys.argv[1], sys.argv[2])
