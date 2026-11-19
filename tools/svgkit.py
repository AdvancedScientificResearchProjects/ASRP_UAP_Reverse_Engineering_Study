#!/usr/bin/env python3
"""Shared SVG kit for all generated ASRP visuals in this repository (one token set, one text
measurer, a few components). Used by tools/build_visuals.py and tools/build_diagrams.py.

Rules enforced here (ASRP visual standard):
  * every SVG gets <title>, <desc>, viewBox, role="img";
  * text is measured and must fit its container: `text(..., box=px)` aborts the build otherwise;
  * nothing below FS_MIN (13 px); labels longer than 70 characters must be wrapped (`wrap`);
  * a status is always written as a word and paired with a shape glyph, never colour alone;
  * colours, radii and font sizes come from the token block, not from ad hoc literals.
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

# --- design tokens ---------------------------------------------------------------------------
BG0, BG1, PANEL, LINE = "#070b18", "#0d1530", "#0b1430", "#2a3b78"
INK, MUTED = "#e6ecff", "#8ea0d6"
TEAL, VIOLET, GOLD, GREEN, AMBER, BLUE = "#4ecdc4", "#a78bfa", "#ffcf5c", "#34d399", "#ffa657", "#6f9bff"
FS_KICKER, FS_BODY, FS_SMALL, FS_MIN = 14, 15, 13, 13  # px; nothing below FS_MIN
RADIUS = 12
MAX_CHARS = 68  # the visual audit asks for wrapping of any label longer than 70 characters


def text_width(s, size, bold=False):
    """Conservative width estimate (px) so that no label can be clipped."""
    w = 0.0
    for ch in s:
        if ch == " ":
            w += 0.30
        elif ch in "il.,:;'|!·":
            w += 0.30
        elif ch in "mwMW@ШЩЖМЫЮшщжмыю":
            w += 0.90
        elif ch.isupper() or ch.isdigit():
            w += 0.68
        elif "а" <= ch <= "я" or ch == "ё":
            w += 0.60
        else:
            w += 0.56
    return w * size * (1.07 if bold else 1.0)


def fit(s, size, box, bold=False, spacing=0.0):
    w = text_width(s, size, bold) + spacing * len(s)
    if w > box:
        raise SystemExit("TEXT DOES NOT FIT (%.0f > %.0f px): %r" % (w, box, s))
    return w


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=FS_BODY, fill=INK, anchor="start", weight=400, spacing=0, box=None):
    if size < FS_MIN:
        raise SystemExit("font below minimum: %r" % s)
    if len(s) > 70:
        raise SystemExit("label longer than 70 characters, wrap it into lines: %r" % s)
    if box is not None:
        fit(s, size, box, weight >= 600, spacing)
    ls = " letter-spacing='%s'" % spacing if spacing else ""
    return ("<text x='%s' y='%s' font-family=\"%s\" font-size='%s' fill='%s' text-anchor='%s' "
            "font-weight='%s'%s>%s</text>" % (x, y, FONT, size, fill, anchor, weight, ls, esc(s)))


def svg_open(w, h, title, desc):
    return ("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 %d %d\" width=\"%d\" height=\"%d\" "
            "role=\"img\" aria-labelledby=\"t d\">\n<title id=\"t\">%s</title>\n<desc id=\"d\">%s</desc>\n"
            "<defs><linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='%s'/>"
            "<stop offset='1' stop-color='%s'/></linearGradient>"
            "<filter id='glow' x='-50%%' y='-50%%' width='200%%' height='200%%'><feGaussianBlur stdDeviation='3' "
            "result='b'/><feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter></defs>\n"
            "<rect width='%d' height='%d' rx='18' fill='url(#bg)'/>\n"
            % (w, h, w, h, esc(title), esc(desc), BG0, BG1, w, h))


def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)
    print("wrote", rel, len(content))



# --- components ------------------------------------------------------------------------------
def wrap(s, size, width, bold=False):
    """Greedy word wrap to a pixel width; returns a list of lines (never clips)."""
    lines, cur = [], ""
    for w in s.split(" "):
        trial = (cur + " " + w).strip()
        if cur and (text_width(trial, size, bold) > width or len(trial) > MAX_CHARS):
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    for ln in lines:
        fit(ln, size, width, bold)
    return lines


class Canvas:
    """A dark ASRP canvas with a heading row. Collects SVG fragments in self.o."""

    def __init__(self, w, h, title, desc, heading=None, sub=None, tag=None):
        self.w, self.h = w, h
        self.o = [svg_open(w, h, title, desc)]
        self._markers = set()
        if heading:
            self.o.append(text(24, 46, heading, 26, INK, "start", 700, 0, w - 330 if tag else w - 48))
        if sub:
            if len(sub) > 70:
                raise SystemExit("subtitle longer than 70 characters, shorten it: %r" % sub)
            self.o.append(text(24, 72, sub, FS_KICKER, MUTED, "start", 400, 0, w - 48))
        if tag:
            self.o.append(text(w - 24, 46, tag, FS_KICKER, TEAL, "end", 700, 2, 290))

    def add(self, fragment):
        self.o.append(fragment)

    def _marker(self, color):
        mid = "m" + color.strip("#")
        if mid not in self._markers:
            self._markers.add(mid)
            self.o.append("<defs><marker id='%s' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' "
                          "markerHeight='7' orient='auto'><path d='M0,0 L10,5 L0,10z' fill='%s'/></marker></defs>"
                          % (mid, color))
        return mid

    def panel(self, x, y, w, h, label=None, color=LINE, fill=PANEL, opacity=1.0):
        """A container that groups boxes; `label` sits inside its top-left corner."""
        self.o.append("<rect x='%s' y='%s' width='%s' height='%s' rx='%d' fill='%s' fill-opacity='%s' stroke='%s'/>"
                      % (x, y, w, h, RADIUS + 2, fill, opacity, color))
        if label:
            self.o.append(text(x + 16, y + 28, label, FS_KICKER, color if color != LINE else MUTED, "start", 800, 0.6, w - 32))

    def box(self, x, y, w, title=None, lines=(), status=(), stroke=TEAL, h=None, title_size=15, pad=14,
            fill=PANEL, center=False, valign="middle"):
        """A card. `lines` are muted body lines (auto-wrapped), `status` is a list of (text, colour)
        written in bold. With a fixed `h`, content is centred vertically unless valign="top".
        `center=True` centres text horizontally. Returns (x, y, w, h) so arrows can attach to it."""
        inner = w - 2 * pad
        rows = []
        if title:
            for ln in wrap(title, title_size, inner, True):
                rows.append((ln, title_size, INK, 700, title_size + 7))
        for body in lines:
            for ln in wrap(body, FS_SMALL, inner):
                rows.append((ln, FS_SMALL, MUTED, 400, FS_SMALL + 7))
        for st, col in status:
            for ln in wrap(st, FS_SMALL, inner, True):
                rows.append((ln, FS_SMALL, col, 800, FS_SMALL + 8))
        need = pad + sum(r[4] for r in rows) + pad - 4
        if h is None:
            h = need
        elif need > h:
            raise SystemExit("box %r needs %d px, has %d" % (title, need, h))
        self.o.append("<rect x='%s' y='%s' width='%s' height='%s' rx='%d' fill='%s' stroke='%s' stroke-width='1.6'/>"
                      % (x, y, w, h, RADIUS, fill, stroke))
        cy = y + pad + ((h - need) / 2 if valign == "middle" else 0)
        for ln, size, col, weight, adv in rows:
            cy += adv
            if center:
                self.o.append(text("%.1f" % (x + w / 2), "%.1f" % (cy - 5), ln, size, col, "middle", weight))
            else:
                self.o.append(text(x + pad, "%.1f" % (cy - 5), ln, size, col, "start", weight))
        return (x, y, w, h)

    def arrow(self, pts, color=TEAL, dashed=False, label=None, label_at=None, label_color=None, animate=True,
              label_box=220, anchor="middle"):
        """Polyline arrow through `pts` [(x, y), ...]. Dashed = target / not yet running; say so in a
        legend or label, the dash alone is not a status."""
        mid = self._marker(color)
        d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
        dash = " stroke-dasharray='7 6'" if dashed else ""
        anim = ("<animate attributeName='stroke-dashoffset' from='26' to='0' dur='1.6s' repeatCount='indefinite'/>"
                if dashed and animate else "")
        self.o.append("<path d='%s' fill='none' stroke='%s' stroke-width='2'%s marker-end='url(#%s)'>%s</path>"
                      % (d, color, dash, mid, anim))
        if label:
            lx, ly = label_at if label_at else ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2 - 8)
            lines = label if isinstance(label, (list, tuple)) else [label]
            for i, ln in enumerate(lines):
                self.o.append(text("%.1f" % lx, "%.1f" % (ly + i * 17), ln, FS_SMALL, label_color or INK, anchor, 600, 0, label_box))

    def label(self, x, y, s, size=FS_SMALL, color=MUTED, anchor="start", weight=400, box=None):
        self.o.append(text(x, y, s, size, color, anchor, weight, 0, box))

    def legend(self, x, y, items):
        """items: [(kind, colour, text)] with kind in {'solid', 'dashed', 'dot'}; always words."""
        for kind, col, s in items:
            if kind == "dot":
                self.o.append("<circle cx='%s' cy='%s' r='5' fill='%s'/>" % (x + 6, y - 4, col))
                tx = x + 20
            else:
                mid = self._marker(col)
                dash = " stroke-dasharray='7 6'" if kind == "dashed" else ""
                self.o.append("<line x1='%s' y1='%s' x2='%s' y2='%s' stroke='%s' stroke-width='2'%s marker-end='url(#%s)'/>"
                              % (x, y - 4, x + 40, y - 4, col, dash, mid))
                tx = x + 50
            self.o.append(text(tx, y, s, FS_SMALL, MUTED))
            x = tx + text_width(s, FS_SMALL) + 30

    def save(self, rel):
        write(rel, "\n".join(self.o + ["</svg>\n"]))
