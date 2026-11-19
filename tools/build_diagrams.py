#!/usr/bin/env python3
"""Redraws the old Mermaid renders (PNG) that the study pages showed, as house-style EN + RU SVG pairs.

    python3 tools/build_diagrams.py

Every node, edge and label of the Mermaid source is carried over (the source stays in the repository,
the .mmd file named in each figure's foot line). Nothing is added except a status word next to a status
colour (the ASRP visual standard forbids colour alone) and a foot line saying where the picture comes from.
A small layered layout (longest-path ranks, barycentre ordering) places the boxes; tools/svgkit.py draws.

Output: guide/assets/diagrams/<slug>.{en,ru}.svg  for nine figures
    overview-pipeline (root_1) · evidence-flow (root_3) · ai-pipeline (root_4) · timeline-flow (root_5)
    s4-contractor-bridge · fuel-loop · detective-board · validation-pipeline · cluster-map
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import *  # noqa: E402,F401,F403
import svgkit  # noqa: E402

NODE_GAP = 26
EDGE_STYLE = {  # key: (colour, dashed, width)
    "s": (BLUE, False, 2), "t": (TEAL, False, 3.5), "d": (VIOLET, True, 2), "p": (MUTED, False, 1.6),
    "r": (AMBER, True, 2.6), "rt": (AMBER, False, 3.5), "bt": (BLUE, False, 3.5), "gt": (GREEN, False, 3.5),
}


def marker(cv, color):
    mid = "k" + color.strip("#")
    if mid not in cv._markers:
        cv._markers.add(mid)
        cv.o.append("<defs><marker id='%s' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' "
                    "orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10z' fill='%s'/></marker></defs>" % (mid, color))
    return mid


def measure(node, lang, w, kinds):
    scratch = Canvas(w + 10, 10, "t", "d")
    _, _, _, h = scratch.box(0, 0, w, **node_args(node, lang, kinds))
    return h


def node_args(node, lang, kinds):
    lines = node[lang]
    col, st = kinds[node["k"]]
    st = node.get("st", {}).get(lang, st[lang]) if st else None
    return dict(title=lines[0], lines=lines[1:], status=[(st, col)] if st else [], stroke=col, center=True, pad=12)


def layout(nodes, edges, direction, lang, w, kinds, gap_main=84):
    ids = list(nodes)
    # drop duplicates and merge anti-parallel pairs into one two-headed edge
    seen, es = {}, []
    for a, b, sty, *lab in edges:
        key = (a, b)
        if key in seen:
            continue
        seen[key] = True
        both = (b, a) in seen
        if both:
            for e in es:
                if (e["a"], e["b"]) == (b, a):
                    e["both"] = True
            continue
        es.append({"a": a, "b": b, "s": sty, "lab": lab[0] if lab else None, "both": False})
    # rank by longest path after removing back edges found by DFS
    out = {i: [] for i in ids}
    for e in es:
        out[e["a"]].append(e["b"])
    state, back = {}, set()

    def dfs(u):
        state[u] = 1
        for v in out[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2
    for i in ids:
        if i not in state:
            dfs(i)
    fwd = [(e["b"], e["a"]) if (e["a"], e["b"]) in back else (e["a"], e["b"]) for e in es]
    rank = {i: 0 for i in ids}
    for _ in range(len(ids) + 2):
        for a, b in fwd:
            if rank[b] < rank[a] + 1:
                rank[b] = rank[a] + 1
    for i in ids:
        if "rank" in nodes[i]:
            rank[i] = nodes[i]["rank"]
    # sizes: main axis / cross axis
    size = {}
    for i in ids:
        h = measure(nodes[i], lang, w, kinds)
        size[i] = (w, h)
    lr = direction == "LR"
    csz = {i: (size[i][1] if lr else size[i][0]) for i in ids}
    msz = {i: (size[i][0] if lr else size[i][1]) for i in ids}
    # dummies for long edges
    chains = []
    dummy_rank, dn = {}, 0
    for e, (a, b) in zip(es, fwd):
        path = [a]
        for r in range(rank[a] + 1, rank[b]):
            d = "~%d" % dn
            dn += 1
            dummy_rank[d] = r
            csz[d], msz[d] = 8, 0
            path.append(d)
        path.append(b)
        chains.append(path)
    allrank = dict(rank)
    allrank.update(dummy_rank)
    nr = max(allrank.values()) + 1
    rows = [[] for _ in range(nr)]
    for i in list(ids) + list(dummy_rank):
        rows[allrank[i]].append(i)
    up, dn_ = {}, {}
    for p in chains:
        for x, y in zip(p, p[1:]):
            dn_.setdefault(x, []).append(y)
            up.setdefault(y, []).append(x)
    pos = {}

    def reindex():
        for r in rows:
            for k, n in enumerate(r):
                pos[n] = k
    reindex()
    for it in range(8):
        rng = range(1, nr) if it % 2 == 0 else range(nr - 2, -1, -1)
        nb = up if it % 2 == 0 else dn_
        for r in rng:
            rows[r].sort(key=lambda n: (sum(pos[m] for m in nb[n]) / len(nb[n])) if n in nb else pos[n])
            for k, n in enumerate(rows[r]):
                pos[n] = k
    # cross coordinates
    cc = {}
    for r in rows:
        tot = sum(csz[n] for n in r) + NODE_GAP * (len(r) - 1)
        y = -tot / 2
        for n in r:
            cc[n] = y + csz[n] / 2
            y += csz[n] + NODE_GAP
    for it in range(10):
        rng = list(range(1, nr)) if it % 2 == 0 else list(range(nr - 2, -1, -1))
        nb = up if it % 2 == 0 else dn_
        for r in rng:
            row = rows[r]
            want = [(sum(cc[m] for m in nb[n]) / len(nb[n])) if n in nb else cc[n] for n in row]
            new = []
            for k, n in enumerate(row):
                y = want[k]
                if k:
                    y = max(y, new[-1] + (csz[row[k - 1]] + csz[n]) / 2 + NODE_GAP)
                new.append(y)
            for k in range(len(row) - 2, -1, -1):  # push back up if the tail was pushed too far
                lim = new[k + 1] - (csz[row[k]] + csz[row[k + 1]]) / 2 - NODE_GAP
                if new[k] > lim:
                    new[k] = lim
            shift = sum(want[k] - new[k] for k in range(len(row))) / len(row)
            for k, n in enumerate(row):
                cc[n] = new[k] + shift
        for r in rows:  # re-enforce spacing after shifts
            for k in range(1, len(r)):
                lo = cc[r[k - 1]] + (csz[r[k - 1]] + csz[r[k]]) / 2 + NODE_GAP
                if cc[r[k]] < lo:
                    cc[r[k]] = lo
    lo = min(cc[n] - csz[n] / 2 for n in cc)
    for n in cc:
        cc[n] -= lo
    # main coordinates
    labw = [0] * nr
    for e, p in zip(es, chains):
        if e["lab"]:
            lines = e["lab"][lang]
            lw = max(text_width(l, FS_SMALL, True) for l in lines) if lines else 0
            r = allrank[p[0]]
            labw[r] = max(labw[r], lw if lr else 0)
    rmain = [max([msz[n] for n in r] + [0]) for r in rows]
    mm, m = {}, 0
    for r in range(nr):
        for n in rows[r]:
            mm[n] = m + rmain[r] / 2
        m += rmain[r] + gap_main + min(labw[r], 190) * 0.6 + (14 if not lr and any(e["lab"] and allrank[p[0]] == r for e, p in zip(es, chains)) else 0)
    m -= gap_main + min(labw[nr - 1], 190) * 0.6
    mext = max(mm[n] + msz[n] / 2 for n in ids)
    cext = max(cc[n] + csz[n] / 2 for n in cc)

    def xy(n):
        return (mm[n], cc[n]) if lr else (cc[n], mm[n])
    rects = {}
    for i in ids:
        cx, cy = xy(i)
        rects[i] = (cx - size[i][0] / 2, cy - size[i][1] / 2, size[i][0], size[i][1])
    w_, h_ = (mext, cext) if lr else (cext, mext)
    routes = []
    for e, p in zip(es, chains):
        flip = (e["a"], e["b"]) in back
        pts = []
        for k, n in enumerate(p):
            if n in rects:
                x, y, ww, hh = rects[n]
                cx, cy = x + ww / 2, y + hh / 2
                if lr:
                    px = x + ww if k == 0 else x
                    pts.append((px, cy))
                else:
                    py = y + hh if k == 0 else y
                    pts.append((cx, py))
            else:
                pts.append(xy(n))
        routes.append((e, pts, flip))
    return rects, routes, (w_, h_), lr


def curve(pts, lr):
    d = "M%.1f,%.1f" % pts[0]
    for a, b in zip(pts, pts[1:]):
        if lr:
            dx = (b[0] - a[0]) / 2
            d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (a[0] + dx, a[1], b[0] - dx, b[1], b[0], b[1])
        else:
            dy = (b[1] - a[1]) / 2
            d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (a[0], a[1] + dy, b[0], b[1] - dy, b[0], b[1])
    return d


def mid_of(pts):
    if len(pts) == 2:
        a, b = pts
        return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return pts[len(pts) // 2]


def draw(spec, lang):
    t = spec["text"][lang]
    nodes, kinds = spec["nodes"], spec["kinds"]
    rects, routes, (gw, gh), lr = layout(nodes, spec["edges"], spec["dir"], lang, spec["w"], kinds)
    # legend rows and foot lines
    leg_rows = []
    row, used = [], 0
    for item in spec["legend"]:
        label = item[2][lang]
        wd = text_width(label, FS_SMALL) + 70
        if row and used + wd > 1000:
            leg_rows.append(row)
            row, used = [], 0
        row.append(item)
        used += wd
    if row:
        leg_rows.append(row)
    pad = 28
    W = max(int(gw + 2 * pad), 1100)
    foot_lines = []
    for s in t["foot"]:
        s = re.sub(r"(from|из) (\S+/\S+\.mmd[;.]?)", r"\1\n\2\n", s)
        for part in s.split("\n"):
            if len(part) > 64 and " " not in part.strip():
                k = part.rindex("/") + 1
                parts = [part[:k], part[k:]]
            else:
                parts = [part]
            for pt in parts:
                foot_lines += wrap(pt, FS_SMALL, W - 48)
    y0 = 108
    H = int(y0 + gh + 26 + 26 * len(leg_rows) + 22 * len(foot_lines) + 24)
    cv = Canvas(W, H, t["title"], t["desc"], t["title"], t["sub"], t["tag"])
    ox = (W - gw) / 2
    cv.o.append("<g transform='translate(%.1f,%.1f)'>" % (ox, y0))
    # edges first
    labels = []
    for e, pts, flip in routes:
        col, dashed, wd = EDGE_STYLE[e["s"]]
        mk = marker(cv, col)
        dash = " stroke-dasharray='7 6'" if dashed else ""
        ends = ""
        if e["s"] != "p":
            ends = " marker-end='url(#%s)'" % mk
            if flip:
                ends = " marker-start='url(#%s)'" % mk
            if e["both"]:
                ends = " marker-start='url(#%s)' marker-end='url(#%s)'" % (mk, mk)
        cv.o.append("<path d='%s' fill='none' stroke='%s' stroke-width='%s'%s%s stroke-opacity='0.9'/>"
                    % (curve(pts, lr), col, wd, dash, ends))
        if e["lab"]:
            labels.append((mid_of(pts), e["lab"][lang]))
    for (mx, my), lines in labels:
        wmax = max(text_width(l, FS_SMALL, True) for l in lines) + 12
        hh = 17 * len(lines) + 6
        cv.o.append("<rect x='%.1f' y='%.1f' width='%.1f' height='%d' rx='6' fill='%s' fill-opacity='0.92'/>"
                    % (mx - wmax / 2, my - hh / 2, wmax, hh, BG1))
        for k, ln in enumerate(lines):
            cv.o.append(text("%.1f" % mx, "%.1f" % (my - hh / 2 + 17 * k + 16), ln, FS_SMALL, INK, "middle", 600, 0, wmax))
    for i, (x, y, w, h) in rects.items():
        cv.box(x, y, w, **node_args(nodes[i], lang, kinds))
    cv.o.append("</g>")
    ly = y0 + gh + 30
    for row in leg_rows:
        x = 24
        for kind, col, label in row:
            label = label[lang]
            if kind == "dot":
                cv.o.append("<circle cx='%s' cy='%s' r='5' fill='%s'/>" % (x + 6, ly - 4, col))
                tx = x + 20
            else:
                mk = marker(cv, col)
                dash = " stroke-dasharray='7 6'" if kind == "dashed" else ""
                sw = 3.5 if kind == "thick" else 2
                end = "" if kind == "plain" else " marker-end='url(#%s)'" % mk
                cv.o.append("<line x1='%s' y1='%s' x2='%s' y2='%s' stroke='%s' stroke-width='%s'%s%s/>"
                            % (x, ly - 4, x + 40, ly - 4, col, sw, dash, end))
                tx = x + 50
            cv.o.append(text(tx, ly, label, FS_SMALL, MUTED, "start", 400, 0, W - tx - 24))
            x = tx + text_width(label, FS_SMALL) + 30
        ly += 26
    fy = ly - 4
    for ln in foot_lines:
        cv.o.append(text(24, fy, ln, FS_SMALL, MUTED, "start", 400, 0, W - 48))
        fy += 22
    return "\n".join(cv.o + ["</svg>\n"])


def two(en, ru=None):
    return {"en": en, "ru": ru if ru is not None else en}


def N(k, en, ru=None, st=None, rank=None):
    d = {"k": k, "en": en, "ru": ru if ru is not None else en}
    if st:
        d["st"] = {"en": st[0], "ru": st[1]}
    if rank is not None:
        d["rank"] = rank
    return d


def L(en, ru=None):
    return {"en": en if isinstance(en, list) else [en], "ru": (ru if ru is not None else en) if isinstance(ru if ru is not None else en, list) else [ru]}


def foot_src(path, extra_en=(), extra_ru=()):
    return {"en": ["Redrawn from the Mermaid source `%s`; the previous PNG render stays in the repository." % path.replace("`", "")] + list(extra_en),
            "ru": ["Перерисовано из Mermaid-источника %s; прежний PNG остаётся в репозитории." % path] + list(extra_ru)}


SPECS = {}

# --- root_1: research overview ---------------------------------------------------------------
K1 = {"in": (TEAL, None), "step": (BLUE, None), "hyp": (VIOLET, {"en": "◇ HYPOTHESIS", "ru": "◇ ГИПОТЕЗА"}), "syn": (GOLD, None)}
SPECS["overview-pipeline"] = dict(
    dir="TB", w=260, kinds=K1,
    nodes={
        "A": N("in", ["UAP-FRAG-001", "artifact imagery"], ["UAP-FRAG-001", "изображение артефакта"]),
        "B": N("step", ["AI visual and material analysis"], ["ИИ-анализ визуальных и материальных характеристик"]),
        "C": N("step", ["Archival and comparative analysis"], ["Архивный и сравнительный анализ"]),
        "D": N("step", ["ECP percipient sessions"], ["КП-сеансы перципиентов"]),
        "E": N("step", ["Three recorded percipient reports"], ["Три зафиксированных отчёта перципиентов"]),
        "F": N("step", ["Cross-response comparison"], ["Сравнение ответов"]),
        "G": N("hyp", ["Material and structure hypotheses"], ["Гипотезы о материале и структуре"]),
        "H": N("hyp", ["Context and provenance hypotheses"], ["Гипотезы о контексте и происхождении"]),
        "I": N("step", ["Reference validation"], ["Валидация по референсу"]),
        "J": N("syn", ["Cross-pipeline synthesis"], ["Межконвейерный синтез"]),
    },
    edges=[("A", "B", "s"), ("A", "C", "s"), ("A", "D", "s"), ("D", "E", "s"), ("E", "F", "s"), ("B", "G", "s"), ("C", "H", "s"),
           ("F", "I", "s"), ("G", "J", "s"), ("H", "J", "s"), ("I", "J", "s")],
    legend=[("dot", TEAL, two("input object", "исходный объект")), ("dot", BLUE, two("analysis step", "шаг анализа")),
            ("dot", VIOLET, two("hypothesis, not a result", "гипотеза, не результат")), ("dot", GOLD, two("synthesis", "синтез"))],
    text={"en": {"title": "Research overview", "sub": "End-to-end pipeline map of Track 1", "tag": "ORIGINAL FIGURE 1",
                 "desc": "Flow diagram. UAP-FRAG-001 artifact imagery feeds three branches: AI visual and material analysis leading to material and structure hypotheses; archival and comparative analysis leading to context and provenance hypotheses; and ECP percipient sessions leading to three recorded percipient reports, cross-response comparison and reference validation. All three branches meet in the cross-pipeline synthesis.",
                 "foot": foot_src("charts/mermaid/root_1.mmd")["en"]},
          "ru": {"title": "Обзор исследования", "sub": "Сквозная карта конвейера трека 1", "tag": "ИСХОДНАЯ СХЕМА 1",
                 "desc": "Схема потока. Изображение артефакта UAP-FRAG-001 даёт три ветви: ИИ-анализ визуальных и материальных характеристик ведёт к гипотезам о материале и структуре; архивный и сравнительный анализ ведёт к гипотезам о контексте и происхождении; КП-сеансы перципиентов ведут к трём отчётам, сравнению ответов и валидации по референсу. Все три ветви сходятся в межконвейерном синтезе.",
                 "foot": foot_src("charts/mermaid/root_1.mmd")["ru"]}},
)

# --- root_3: evidence synthesis flow ---------------------------------------------------------
SPECS["evidence-flow"] = dict(
    dir="LR", w=250, kinds=K1,
    nodes={
        "A": N("in", ["Raw percipient statements"], ["Необработанные утверждения перципиентов"]),
        "B": N("step", ["Normalized themes"], ["Нормализованные темы"]),
        "C": N("step", ["Cross-response agreement"], ["Согласованность ответов"]),
        "D": N("step", ["Reference validation"], ["Валидация по референсу"]),
        "E": N("hyp", ["Repository-level hypotheses"], ["Гипотезы на уровне репозитория"]),
        "F": N("step", ["Primary reports"], ["Первичные отчёты"]),
    },
    edges=[("A", "B", "s"), ("B", "C", "s"), ("C", "D", "s"), ("D", "E", "s"), ("A", "F", "s"), ("F", "C", "s")],
    legend=[("dot", TEAL, two("input", "вход")), ("dot", BLUE, two("analysis step", "шаг анализа")), ("dot", VIOLET, two("hypothesis, not a result", "гипотеза, не результат"))],
    text={"en": {"title": "Evidence synthesis flow", "sub": "From raw statements to repository-level hypotheses", "tag": "ORIGINAL FIGURE 3",
                 "desc": "Flow diagram, left to right. Raw percipient statements become normalized themes, then cross-response agreement, then reference validation, then repository-level hypotheses. A second path runs from the raw statements through the primary reports into the cross-response agreement.",
                 "foot": foot_src("charts/mermaid/root_3.mmd")["en"]},
          "ru": {"title": "Схема синтеза доказательств", "sub": "От необработанных утверждений к гипотезам репозитория", "tag": "ИСХОДНАЯ СХЕМА 3",
                 "desc": "Схема слева направо. Необработанные утверждения перципиентов превращаются в нормализованные темы, затем в согласованность ответов, затем в валидацию по референсу, затем в гипотезы на уровне репозитория. Второй путь идёт от необработанных утверждений через первичные отчёты к согласованности ответов.",
                 "foot": foot_src("charts/mermaid/root_3.mmd")["ru"]}},
)

# --- root_4: AI pipeline ---------------------------------------------------------------------
K4 = {"in": (TEAL, None), "step": (BLUE, None), "claim": (VIOLET, {"en": "◇ CLAIMED CONVERGENCE", "ru": "◇ ЗАЯВЛЕННАЯ КОНВЕРГЕНЦИЯ"})}
SPECS["ai-pipeline"] = dict(
    dir="LR", w=250, kinds=K4,
    nodes={
        "A": N("in", ["UAP-FRAG-001", "Input photo"], ["UAP-FRAG-001", "Входное фото"]),
        "B": N("step", ["Segmentation", "IoU 0.977"], ["Сегментация", "IoU 0.977"]),
        "C": N("step", ["SigLIP2", "coral/sea urchin fossil", "0.98 sigmoid"], ["SigLIP2", "коралл/окаменелость", "0.98 sigmoid"]),
        "D": N("step", ["EfficientAD", "No surface anomalies"], ["EfficientAD", "Аномалий не обнаружено"]),
        "E": N("step", ["Depth Anything", "Relative depth map"], ["Depth Anything", "Карта глубины"]),
        "F": N("step", ["LLM Visual", "Cidaridae match"], ["LLM Visual", "Совпадение Cidaridae"]),
        "G": N("claim", ["Cross-method convergence", "AI + ECP: coral-like"], ["Межметодная конвергенция", "AI + ECP: coral-like"]),
    },
    edges=[("A", "B", "s"), ("B", "C", "s"), ("B", "D", "s"), ("B", "E", "s"), ("C", "F", "s"), ("F", "G", "s")],
    legend=[("dot", TEAL, two("input", "вход")), ("dot", BLUE, two("method and its output", "метод и его результат")),
            ("dot", VIOLET, two("claim of the original figure", "утверждение исходной схемы"))],
    text={"en": {"title": "AI pipeline summary", "sub": "Methods run on the UAP-FRAG-001 photo", "tag": "ORIGINAL FIGURE 4",
                 "desc": "Flow diagram, left to right. The input photo is segmented (IoU 0.977). The segment goes to three methods: SigLIP2 (coral or sea urchin fossil, 0.98 sigmoid), EfficientAD (no surface anomalies) and Depth Anything (relative depth map). SigLIP2 feeds the LLM visual step (Cidaridae match), which leads to the box cross-method convergence, AI plus ECP: coral-like.",
                 "foot": ["Redrawn from the Mermaid source charts/mermaid/root_4.mmd; the previous PNG render stays in the repository.",
                          "The 0.98 is a score on the cropped photo; the full photo scores %s in the control test (see the AI control figure). The convergence box is the original figure's claim; blinding was compromised for 2 of 3 percipients." % "0.89"]},
          "ru": {"title": "Сводка конвейера ИИ", "sub": "Методы, применённые к фото UAP-FRAG-001", "tag": "ИСХОДНАЯ СХЕМА 4",
                 "desc": "Схема слева направо. Входное фото сегментируется (IoU 0.977). Сегмент идёт в три метода: SigLIP2 (коралл или окаменелый морской ёж, 0.98 sigmoid), EfficientAD (аномалий поверхности нет) и Depth Anything (карта относительной глубины). SigLIP2 ведёт к шагу LLM Visual (совпадение Cidaridae), он ведёт к блоку межметодной конвергенции, AI + ECP: coral-like.",
                 "foot": ["Перерисовано из Mermaid-источника charts/mermaid/root_4.mmd; прежний PNG остаётся в репозитории.",
                          "0.98 это оценка на обрезанном фото; полное фото в контрольном тесте получает 0.89 (см. рисунок контрольного теста ИИ). Блок конвергенции это утверждение исходной схемы; ослепление нарушено у 2 из 3 перципиентов."]}},
)

# --- root_5: timeline ------------------------------------------------------------------------
K5 = {"mid": (BLUE, None), "end": (GREEN, {"en": "■ FIRST OR LAST STEP", "ru": "■ ПЕРВЫЙ ИЛИ ПОСЛЕДНИЙ ШАГ"})}
SPECS["timeline-flow"] = dict(
    dir="LR", w=200, kinds=K5,
    nodes={
        "A": N("end", ["2026-04-04", "ECP Session"], ["2026-04-04", "Сеанс КП"]),
        "B": N("mid", ["2026-04-06", "Cross-comparison"], ["2026-04-06", "Сравнение"]),
        "C": N("mid", ["2026-04-06", "Validation"], ["2026-04-06", "Валидация"]),
        "D": N("mid", ["2026-04-07", "AI Pipeline"], ["2026-04-07", "ИИ Конвейер"]),
        "E": N("mid", ["2026-04-07", "LLM Analysis"], ["2026-04-07", "LLM Анализ"]),
        "F": N("end", ["2026-04-07", "Report Published"], ["2026-04-07", "Отчёт Опубликован"]),
    },
    edges=[("A", "B", "s"), ("B", "C", "s"), ("C", "D", "s"), ("D", "E", "s"), ("E", "F", "s")],
    legend=[("dot", BLUE, two("step", "шаг")), ("dot", GREEN, two("first or last step", "первый или последний шаг"))],
    text={"en": {"title": "Timeline", "sub": "Six steps, 4 to 7 April 2026", "tag": "ORIGINAL FIGURE 5",
                 "desc": "Chain of six steps, left to right: ECP session 2026-04-04, cross-comparison 2026-04-06, validation 2026-04-06, AI pipeline 2026-04-07, LLM analysis 2026-04-07, report published 2026-04-07. The first and the last are marked.",
                 "foot": foot_src("charts/mermaid/root_5.mmd")["en"]},
          "ru": {"title": "Временная шкала", "sub": "Шесть шагов, 4-7 апреля 2026", "tag": "ИСХОДНАЯ СХЕМА 5",
                 "desc": "Цепочка из шести шагов слева направо: сеанс КП 2026-04-04, сравнение 2026-04-06, валидация 2026-04-06, ИИ-конвейер 2026-04-07, LLM-анализ 2026-04-07, отчёт опубликован 2026-04-07. Первый и последний шаги отмечены.",
                 "foot": foot_src("charts/mermaid/root_5.mmd")["ru"]}},
)

# --- Track 7: Lazar S-4 contractor bridge ----------------------------------------------------
KB = {"test": (GOLD, {"en": "◇ TESTIMONY", "ru": "◇ ПОКАЗАНИЯ"}), "anchor": (AMBER, {"en": "◇ EMPLOYER NAMED BY LAZAR", "ru": "◇ РАБОТОДАТЕЛЬ ПО ЛАЗАРУ"}),
      "ma": (BLUE, {"en": "▪ CORPORATE LINEAGE", "ru": "▪ КОРПОРАТИВНАЯ ЛИНИЯ"}), "succ": (GREEN, {"en": "▪ SUCCESSOR LINE", "ru": "▪ ПРЕЕМНИК ЛИНИИ"}),
      "hyp": (VIOLET, {"en": "◇ HYPOTHESIS", "ru": "◇ ГИПОТЕЗА"}), "cl": (MUTED, {"en": "▪ GRAPH CLUSTER", "ru": "▪ КЛАСТЕР ГРАФА"})}
SPECS["s4-contractor-bridge"] = dict(
    dir="LR", w=270, kinds=KB,
    nodes={
        "KLAS": N("test", ["KLAS-TV 1989", "Bob Lazar interview"], ["KLAS-TV 1989", "интервью Боба Лазара"]),
        "LZRTAPE": N("test", ["Lazar Tape 1991", "EG&G Special Projects named"], ["Lazar Tape 1991", "назван EG&G Special Projects"]),
        "JRE": N("test", ["JRE 1315 / 2479", "2019 / 2025 restatement"], ["JRE 1315 / 2479", "повтор показаний 2019 / 2025"]),
        "EGNG": N("anchor", ["EG&G Special Projects (Las Vegas)", "Lazar's named employer-of-record"], ["EG&G Special Projects (Las Vegas)", "Названный работодатель"]),
        "URS": N("ma", ["URS Corp (2002)"]),
        "AECOM": N("ma", ["AECOM (2014)"]),
        "AMTM": N("succ", ["Amentum (2020)", "NYSE: AMTM (2024)", "EG&G lineage successor"], ["Amentum (2020)", "NYSE: AMTM (2024)", "правопреемник линии EG&G"]),
        "HYP1": N("hyp", ["hyp-egng-s4-contractor", "EG&G named as S-4 contractor", "(single-source / Lazar)"], ["hyp-egng-s4-contractor", "EG&G — подрядчик S-4", "(один источник / Лазар)"]),
        "HYP2": N("hyp", ["hyp-amentum-egng-legacy", "Amentum is EG&G successor", "(documented)"], ["hyp-amentum-egng-legacy", "Amentum — преемник EG&G", "(задокументировано)"]),
        "CT2": N("cl", ["Track 2: Lazar archive", "cluster-track2"], ["Трек 2: архив Лазара", "cluster-track2"]),
        "CT7": N("cl", ["Track 7: Corporate analysis", "cluster-track7-corporate"], ["Трек 7: корпоративный анализ", "cluster-track7-corporate"]),
    },
    edges=[("CT2", "KLAS", "p"), ("CT2", "LZRTAPE", "p"), ("CT2", "JRE", "p"),
           ("KLAS", "EGNG", "s", two(["names"], ["называет"])), ("LZRTAPE", "EGNG", "s", two(["names"], ["называет"])),
           ("JRE", "EGNG", "s", two(["restates"], ["повторяет"])), ("EGNG", "HYP1", "d"), ("HYP1", "EGNG", "d"),
           ("EGNG", "URS", "s", two(["acquired-by"], ["поглощена"])), ("URS", "AECOM", "s", two(["acquired-by"], ["поглощена"])),
           ("AECOM", "AMTM", "s", two(["spinoff"], ["spinoff"])), ("AMTM", "HYP2", "d"), ("HYP2", "AMTM", "d"),
           ("CT7", "AMTM", "p"), ("CT7", "EGNG", "p")],
    legend=[("solid", BLUE, two("link", "связь")), ("dashed", VIOLET, two("hypothesis link", "связь с гипотезой")), ("plain", MUTED, two("cluster membership (no arrow)", "принадлежность кластеру (без стрелки)"))],
    text={"en": {"title": "Lazar S-4 contractor bridge", "sub": "Testimony to EG&G to Amentum, with two graph hypotheses", "tag": "TRACK 7 DIAGRAM",
                 "desc": "Graph. Three testimony sources of Track 2 (KLAS-TV 1989, Lazar Tape 1991, JRE 2019 and 2025) name EG&G Special Projects as Lazar's employer. EG&G was acquired by URS (2002), URS by AECOM (2014), and Amentum was spun off from AECOM (2020). Two hypotheses are linked to the graph: EG&G as S-4 contractor (single source, Lazar) and Amentum as EG&G successor (documented). Track 7 groups Amentum and EG&G.",
                 "foot": ["Redrawn from corporate-economic-analysis/diagrams/lazar_s4_contractor_bridge.mmd; the previous PNG render stays in the repository.",
                          "The employer and S-4 claims rest on Lazar's testimony alone; the repository does not verify them."]},
          "ru": {"title": "Мост Лазар - подрядчик S-4", "sub": "От показаний к EG&G и Amentum, две гипотезы графа", "tag": "ДИАГРАММА ТРЕКА 7",
                 "desc": "Граф. Три источника показаний из трека 2 (KLAS-TV 1989, Lazar Tape 1991, JRE 2019 и 2025) называют EG&G Special Projects работодателем Лазара. EG&G поглощена URS (2002), URS поглощена AECOM (2014), Amentum выделена из AECOM (2020). К графу привязаны две гипотезы: EG&G как подрядчик S-4 (один источник, Лазар) и Amentum как преемник EG&G (задокументировано). Трек 7 объединяет Amentum и EG&G.",
                 "foot": ["Перерисовано из corporate-economic-analysis/diagrams/lazar_s4_contractor_bridge.mmd; прежний PNG остаётся в репозитории.",
                          "Утверждения о работодателе и S-4 опираются только на показания Лазара; репозиторий их не проверяет."]}},
)

# --- Track 7: fuel loop ----------------------------------------------------------------------
KF = {"thesis": (VIOLET, {"en": "◇ HYPOTHESIS", "ru": "◇ ГИПОТЕЗА"}), "anchor": (GOLD, {"en": "◇ TESTIMONY ANCHOR", "ru": "◇ ОПОРА: ПОКАЗАНИЯ"}),
      "low": (AMBER, {"en": "◌ LOW CONFIDENCE (CLAIM)", "ru": "◌ НИЗКАЯ УВЕРЕННОСТЬ (УТВЕРЖДЕНИЕ)"}),
      "high": (GREEN, {"en": "■ HIGH CONFIDENCE", "ru": "■ ВЫСОКАЯ УВЕРЕННОСТЬ"}), "med": (BLUE, {"en": "◧ MEDIUM CONFIDENCE", "ru": "◧ СРЕДНЯЯ УВЕРЕННОСТЬ"}),
      "hist": (MUTED, {"en": "▪ HISTORICAL LINEAGE", "ru": "▪ ИСТОРИЧЕСКАЯ ЛИНИЯ"})}
SPECS["fuel-loop"] = dict(
    dir="TB", w=250, kinds=KF,
    nodes={
        "THESIS": N("thesis", ["Fuel-supply-chain hypothesis", "(closed-loop reading across Tracks 2 / 4 / 7)"], ["Гипотеза цепочки топливоснабжения", "(замкнутое прочтение по трекам 2 / 4 / 7)"]),
        "LAZAR": N("anchor", ["Bob Lazar (Track 2)", "S-4 testimony 1989+"], ["Боб Лазар (трек 2)", "показания о S-4, 1989+"]),
        "S4R": N("low", ["S-4 reactor narrative", "115 = fuel claim"], ["Нарратив реактора S-4", "утверждение: 115 = топливо"]),
        "MC": N("high", ["Element 115 / Moscovium", "(synthesised 2003-2004)"], ["Элемент 115 / московий", "(синтезирован 2003-2004)"]),
        "JINR": N("high", ["JINR (Dubna)", "Flerov Lab"], ["ОИЯИ (Дубна)", "Лаборатория Флёрова"]),
        "LLNL": N("high", ["LLNL", "243Am target supplier"], ["LLNL", "поставщик мишени 243Am"]),
        "PHYS": N("high", ["Phys. Rev. C 69 (2004)", "JINR+LLNL synthesis paper"], ["Phys. Rev. C 69 (2004)", "статья о синтезе JINR+LLNL"]),
        "LLNS": N("med", ["LLNS LLC consortium", "Bechtel + UC + Battelle + BWXT + AECOM-now-Amentum"], ["Консорциум LLNS LLC", "Bechtel + UC + Battelle + BWXT + AECOM (ныне Amentum)"]),
        "AMTM": N("high", ["Amentum (NYSE: AMTM)", "EG&G successor"], ["Amentum (NYSE: AMTM)", "преемник EG&G"]),
        "EGNG": N("hist", ["EG&G (1947)", "Lazar's stated employer (Track 7)"], ["EG&G (1947)", "заявленный работодатель Лазара (трек 7)"]),
        "URS": N("hist", ["URS (2002)"]),
        "AECOM": N("hist", ["AECOM (2014)"]),
    },
    edges=[("LAZAR", "EGNG", "s", two(["names as employer"], ["называет работодателем"])), ("LAZAR", "S4R", "s", two(["names as fuel"], ["называет топливом"])),
           ("S4R", "MC", "s", two(["fuel claim"], ["утверждение про топливо"])), ("JINR", "MC", "s", two(["co-synthesised"], ["совместный синтез"])),
           ("LLNL", "JINR", "s", two(["supplied target 243Am"], ["поставила мишень"])), ("PHYS", "MC", "s", two(["documents synthesis"], ["документирует синтез"])),
           ("LLNS", "LLNL", "s", two(["operates"], ["управляет"])), ("AMTM", "LLNS", "s", two(["consortium member"], ["член консорциума"])),
           ("EGNG", "URS", "s"), ("URS", "AECOM", "s"), ("AECOM", "AMTM", "s"),
           ("THESIS", "LAZAR", "d"), ("THESIS", "MC", "d"), ("THESIS", "LLNL", "d"), ("THESIS", "AMTM", "d"), ("THESIS", "EGNG", "d"),
           ("AMTM", "EGNG", "d", two(["closes loop back to"], ["замыкает контур к"]))],
    legend=[("solid", BLUE, two("link", "связь")), ("dashed", VIOLET, two("the hypothesis reads these as one loop", "гипотеза читает их как один контур"))],
    text={"en": {"title": "Fuel-supply-chain loop: Dubna, Lazar, Amentum, LLNL", "sub": "A closed-loop reading across Tracks 2, 4 and 7", "tag": "TRACK 7 DIAGRAM",
                 "desc": "Graph around one hypothesis. Lazar names EG&G as employer and element 115 as the S-4 reactor fuel. Element 115 (moscovium) was synthesised in 2003 and 2004 by JINR Dubna with an americium-243 target from LLNL, documented in Phys. Rev. C 69 (2004). LLNS LLC operates LLNL and Amentum is a consortium member. EG&G (1947) became URS (2002), AECOM (2014) and Amentum, which closes the loop back to EG&G. Confidence grades are the original figure's.",
                 "foot": ["Redrawn from corporate-economic-analysis/diagrams/dubna_lazar_amentum_llnl_fuel_loop.mmd; the previous PNG render stays in the repository.",
                          "The loop is a hypothesis of the original figure; confidence grades are its own and the repository does not verify them."]},
          "ru": {"title": "Контур топливоснабжения", "sub": "Дубна, Лазар, Amentum, LLNL: замкнутое прочтение по трекам 2, 4, 7", "tag": "ДИАГРАММА ТРЕКА 7",
                 "desc": "Граф вокруг одной гипотезы. Лазар называет работодателем EG&G, а топливом реактора S-4 элемент 115. Элемент 115 (московий) синтезирован в 2003 и 2004 в ОИЯИ (Дубна) с мишенью америций-243 от LLNL, что задокументировано в Phys. Rev. C 69 (2004). LLNS LLC управляет LLNL, Amentum входит в консорциум. EG&G (1947) стала URS (2002), AECOM (2014) и Amentum, что замыкает контур к EG&G. Оценки уверенности принадлежат исходной схеме.",
                 "foot": ["Перерисовано из corporate-economic-analysis/diagrams/dubna_lazar_amentum_llnl_fuel_loop.mmd; прежний PNG остаётся в репозитории.",
                          "Контур это гипотеза исходной схемы; оценки уверенности её собственные, репозиторий их не проверяет."]}},
)

# --- Track 4: detective board ----------------------------------------------------------------
KD = {"person": (GOLD, {"en": "▪ PERSON", "ru": "▪ ЛИЦО"}), "place": (BLUE, {"en": "▪ PLACE", "ru": "▪ МЕСТО"}),
      "event": (GREEN, {"en": "■ EVENT", "ru": "■ СОБЫТИЕ"}), "claim": (VIOLET, {"en": "◇ CLAIM", "ru": "◇ УТВЕРЖДЕНИЕ"}),
      "ev": (TEAL, {"en": "▪ EVIDENCE", "ru": "▪ ДОКАЗАТЕЛЬСТВО"}), "flag": (AMBER, {"en": "✕ RED FLAG", "ru": "✕ КРАСНЫЙ ФЛАГ"})}
SPECS["detective-board"] = dict(
    dir="LR", w=250, kinds=KD,
    nodes={
        "BL": N("person", ["Bob Lazar", "physicist claimant", "1989"], ["Боб Лазар", "физик-заявитель", "1989"]),
        "YO": N("person", ["Yu. Ts. Oganessian", "academician, JINR lab director", "1989-present"], ["Ю. Ц. Оганесян", "академик, директор ЛЯР", "1989 - наст. время"]),
        "KG": N("person", ["George Knapp", "investigative journalist", "KLAS-89, BL18"], ["George Knapp", "журналист-расследователь", "KLAS-89, BL18"]),
        "RC": N("person", ["Robert Cardillo", "former NGA director", "LinkedIn 2026"], ["Robert Cardillo", "бывший директор NGA", "LinkedIn 2026"]),
        "DB": N("person", ["Denis Banchenko", "ASRP alliance CEO", "2021-2026"], ["Денис Банченко", "глава альянса ASRP", "2021-2026"]),
        "S4": N("place", ["S-4 / Area 51", "Nevada, USA", "alleged site"], ["S-4 / Area 51", "Невада, США", "заявленное место"]),
        "DUBNA": N("place", ["JINR Dubna", "Moscow Oblast", "synthesis site"], ["ОИЯИ Дубна", "Московская область", "место синтеза"]),
        "LLNL": N("place", ["LLNL", "Livermore, USA", "target supplier"], ["LLNL", "Ливермор, США", "поставщик мишени"]),
        "GSI": N("place", ["GSI Darmstadt", "Germany", "replication site"], ["GSI Дармштадт", "Германия", "место репликации"]),
        "ASRP": N("place", ["ASRP.media", "publisher", "2025"], ["ASRP.media", "издатель", "2025"]),
        "C1": N("claim", ["CLAIM 1989", "'115 is stable fuel for S-4 craft'"], ["УТВЕРЖДЕНИЕ 1989", "«115 - стабильное топливо для аппарата в S-4»"]),
        "E1": N("ev", ["Am-243 target", "USA-supplied", "critical"], ["Мишень америций-243", "поставлена из США", "критически важно"]),
        "E2": N("ev", ["Ca-48 beam", "Russia-supplied"], ["Пучок кальций-48", "поставлен из России"]),
        "E3": N("ev", ["Phys. Rev. C 69, 021601(R)", "2 Feb 2004", "co-authors: JINR + LLNL"], ["Phys. Rev. C 69, 021601(R)", "2 февр. 2004", "соавторы: ОИЯИ + LLNL"]),
        "E4": N("ev", ["ASRP.media interview", "28 Sep 2021", "anonymous JINR rep", "published 9 Dec 2025"], ["Интервью ASRP.media", "28 сент. 2021", "анонимный представитель ОИЯИ", "опубликовано 9 дек. 2025"]),
        "E5": N("ev", ["Cardillo LinkedIn engagement", "22 Apr 2026"], ["Взаимодействие Cardillo в LinkedIn", "22 апр. 2026"]),
        "E6": N("ev", ["Aug 2013", "GSI + Lund", "independent confirmation"], ["Авг. 2013", "GSI + Lund", "независимое подтверждение"]),
        "O1": N("flag", ["No stable isotope observed"], ["Стабильный изотоп не наблюдался"]),
        "O2": N("flag", ["Single atoms only", "sub-second life"], ["Только единичные атомы", "жизнь < 1 сек"]),
        "O3": N("flag", ["psycho-linguistic footnote by ASRP", "not JINR voice"], ["Психолингвистическая сноска ASRP", "не голос ОИЯИ"]),
        "RES": N("event", ["Moscovium Mc, Z = 115", "IUPAC 28 Nov 2016", "Russia + USA collaboration"], ["Московий Mc, Z = 115", "IUPAC 28 нояб. 2016", "сотрудничество России и США"]),
    },
    edges=[("BL", "S4", "d", two(["alleges"], ["утверждает"])), ("BL", "C1", "d", two(["claims exist"], ["заявляет"])),
           ("C1", "O1", "r", two(["fails against reality"], ["не выдерживает проверки"])), ("C1", "O2", "r", two(["fails against reality"], ["не выдерживает проверки"])),
           ("LLNL", "DUBNA", "rt", two(["ships target"], ["отправляет мишень"])), ("LLNL", "E1", "s"), ("DUBNA", "E2", "s"),
           ("E1", "E3", "bt"), ("E2", "E3", "bt"), ("E3", "RES", "gt"),
           ("YO", "DUBNA", "s", two(["leads lab"], ["возглавляет лабораторию"])), ("E3", "GSI", "s"), ("GSI", "E6", "s"), ("E6", "RES", "t"),
           ("KG", "BL", "d", two(["canvasses physicists"], ["опрашивает физиков"])), ("DB", "ASRP", "s"), ("ASRP", "E4", "s"),
           ("E4", "O3", "d", two(["adds"], ["добавляет"])), ("DB", "RC", "s", two(["posts on LinkedIn"], ["пишет в LinkedIn"])), ("RC", "E5", "s")],
    legend=[("solid", BLUE, two("link", "связь")), ("dashed", VIOLET, two("alleged link or claim", "заявленная связь или утверждение")),
            ("dashed", AMBER, two("claim fails against reality", "утверждение не выдерживает проверки")),
            ("thick", AMBER, two("target shipment", "поставка мишени")), ("thick", BLUE, two("inputs to the paper", "вход статьи")),
            ("thick", GREEN, two("paper to result", "статья к результату")), ("thick", TEAL, two("independent confirmation to result", "независимое подтверждение к результату"))],
    text={"en": {"title": "Element 115 detective board", "sub": "People, places, evidence and red flags around the 1989 claim", "tag": "TRACK 4 DIAGRAM",
                 "desc": "Board of people, places, evidence and red flags. Lazar alleges S-4 and claims in 1989 that element 115 is stable fuel; that claim fails against reality because no stable isotope was observed and only single atoms with sub-second life exist. LLNL ships an americium-243 target to JINR Dubna, which supplies a calcium-48 beam; both feed the Phys. Rev. C 69, 021601(R) paper of 2 February 2004 and the result moscovium, Z = 115, named by IUPAC on 28 November 2016. GSI and Lund confirmed it independently in August 2013. A second thread links Banchenko, ASRP.media, the 2021 interview published in December 2025, and a LinkedIn engagement by Cardillo in April 2026.",
                 "foot": ["Redrawn from dubna-element-115-analysis/diagrams/detective_board.mmd; the previous PNG render stays in the repository.",
                          "Claims are the track's own; the claim box is a 1989 statement and the red flags are the track's counter-evidence."]},
          "ru": {"title": "Детективная доска: элемент 115", "sub": "Люди, места, доказательства и красные флаги вокруг заявления 1989", "tag": "ДИАГРАММА ТРЕКА 4",
                 "desc": "Доска людей, мест, доказательств и красных флагов. Лазар утверждает S-4 и в 1989 году заявляет, что элемент 115 это стабильное топливо; утверждение не выдерживает проверки: стабильный изотоп не наблюдался, есть только единичные атомы с жизнью менее секунды. LLNL отправляет мишень америций-243 в ОИЯИ (Дубна), который даёт пучок кальция-48; оба ведут к статье Phys. Rev. C 69, 021601(R) от 2 февраля 2004 и к результату московий, Z = 115, названный IUPAC 28 ноября 2016. GSI и Lund независимо подтвердили его в августе 2013. Вторая нить связывает Банченко, ASRP.media, интервью 2021 года, опубликованное в декабре 2025, и взаимодействие Cardillo в LinkedIn в апреле 2026.",
                 "foot": ["Перерисовано из dubna-element-115-analysis/diagrams/detective_board.mmd; прежний PNG остаётся в репозитории.",
                          "Утверждения принадлежат самому треку; блок утверждения это заявление 1989 года, красные флаги это контрдоводы трека."]}},
)

# --- Track 6 (OSINT): validation pipeline ----------------------------------------------------
KV = {"step": (BLUE, {"en": "▪ STEP", "ru": "▪ ШАГ"}), "gate": (GOLD, {"en": "▪ GATE", "ru": "▪ КРИТЕРИИ"}),
      "pass": (GREEN, {"en": "✓ PASSES", "ru": "✓ ВЫПОЛНЕНО"}), "fail": (AMBER, {"en": "✕ FAILURE MODE", "ru": "✕ ТИП ОШИБКИ"})}
SPECS["validation-pipeline"] = dict(
    dir="TB", w=240, kinds=KV,
    nodes={
        "S1": N("step", ["1. Parameter isolation", "change one variable at a time"], ["1. Изоляция параметров", "менять по одной переменной"]),
        "S2": N("step", ["2. Threshold search", "sharp transition at specific value?"], ["2. Поиск порога", "резкий переход при определённом значении?"]),
        "S3": N("step", ["3. Temporal structure", "stable signature?"], ["3. Временная структура", "устойчивая сигнатура?"]),
        "S4": N("step", ["4. Multi-channel verification", "EM, optics, current, mechanics"], ["4. Мультиканальная проверка", "ЭМ, оптика, ток, механика"]),
        "S5": N("step", ["5. Scaling", "structure preserved as energy/size grows?"], ["5. Масштабирование", "структура сохраняется при росте энергии и размера?"]),
        "S6": N("step", ["6. Modelling", "plasma / EM / nonlinear dynamics"], ["6. Моделирование", "плазма / ЭМ / нелинейная динамика"]),
        "S7": N("step", ["7. Hypothesis crash-test", "change medium / material / frequency"], ["7. Краш-тест гипотезы", "сменить среду / материал / частоту"]),
        "G": N("gate", ["5 acceptance criteria gate"], ["Критерии приёмки (5)"]),
        "R1": N("pass", ["Reproducible"], ["Воспроизводится"]),
        "R2": N("pass", ["Has threshold"], ["Имеет порог"]),
        "R3": N("pass", ["Has signature"], ["Имеет сигнатуру"]),
        "R4": N("pass", ["Scales"], ["Масштабируется"]),
        "R5": N("pass", ["Does NOT fit existing model"], ["НЕ укладывается в модель"]),
        "NEW": N("pass", ["New physical regime"], ["Новый физический режим"], st=("✓ OUTCOME", "✓ ИТОГ")),
        "ER1": N("fail", ["Single strange signal"], ["Одиночный странный сигнал"]),
        "ER2": N("fail", ["Ignored noise/artifacts"], ["Шум/артефакты не учтены"]),
        "ER3": N("fail", ["Mixed processes"], ["Смешение процессов"]),
    },
    edges=[("S1", "S2", "s"), ("S2", "S3", "s"), ("S3", "S4", "s"), ("S4", "S5", "s"), ("S5", "S6", "s"), ("S6", "S7", "s"), ("S7", "G", "s"),
           ("G", "R1", "s"), ("G", "R2", "s"), ("G", "R3", "s"), ("G", "R4", "s"), ("G", "R5", "s"),
           ("R1", "NEW", "s"), ("R2", "NEW", "s"), ("R3", "NEW", "s"), ("R4", "NEW", "s"), ("R5", "NEW", "s"),
           ("G", "ER1", "r"), ("G", "ER2", "r"), ("G", "ER3", "r")],
    legend=[("solid", BLUE, two("sequence", "последовательность")), ("dashed", AMBER, two("what the gate rejects", "что отсеивает проверка"))],
    text={"en": {"title": "OSINT validation pipeline", "sub": "Seven steps, five acceptance criteria, three failure modes", "tag": "TRACK 6 DIAGRAM",
                 "desc": "Method scheme, top to bottom. Seven steps in a chain: parameter isolation, threshold search, temporal structure, multi-channel verification, scaling, modelling, hypothesis crash-test. They lead to a gate of five acceptance criteria: reproducible, has threshold, has signature, scales, does not fit the existing model. If all five hold the outcome is a new physical regime. The gate also rejects three failure modes: a single strange signal, ignored noise and artifacts, mixed processes.",
                 "foot": ["Redrawn from osint-intelligence-analysis/diagrams/validation_pipeline.mmd; the previous PNG render stays in the repository.",
                          "A scheme of the track's method, not a result: the picture does not say that any case has passed the gate."]},
          "ru": {"title": "Конвейер валидации OSINT", "sub": "Семь шагов, пять критериев приёмки, три типа ошибок", "tag": "ДИАГРАММА ТРЕКА 6",
                 "desc": "Схема метода сверху вниз. Семь шагов в цепочке: изоляция параметров, поиск порога, временная структура, мультиканальная проверка, масштабирование, моделирование, краш-тест гипотезы. Они ведут к проверке по пяти критериям приёмки: воспроизводится, имеет порог, имеет сигнатуру, масштабируется, не укладывается в существующую модель. Если выполнены все пять, итог: новый физический режим. Проверка также отсеивает три типа ошибок: одиночный странный сигнал, неучтённые шум и артефакты, смешение процессов.",
                 "foot": ["Перерисовано из osint-intelligence-analysis/diagrams/validation_pipeline.mmd; прежний PNG остаётся в репозитории.",
                          "Схема метода трека, не результат: рисунок не утверждает, что какой-либо случай прошёл проверку."]}},
)

# --- Track 5 (people): institutional cluster map ---------------------------------------------
KC = {"lab": (BLUE, {"en": "▪ INSTITUTION", "ru": "▪ УЧРЕЖДЕНИЕ"}), "dis": (GOLD, {"en": "◌ DISAPPEARED", "ru": "◌ ИСЧЕЗ(ЛА)"}),
      "kill": (AMBER, {"en": "✕ KILLED (SUSPECT)", "ru": "✕ УБИТ(А)"}), "died": (VIOLET, {"en": "◧ DIED, UNCLEAR", "ru": "◧ УМЕР(ЛА), ПРИЧИНА НЕЯСНА"}),
      "found": (MUTED, {"en": "▪ FOUND DEAD", "ru": "▪ ТЕЛО НАЙДЕНО"})}
SPECS["cluster-map"] = dict(
    dir="LR", w=250, kinds=KC,
    nodes={
        "LANL": N("lab", ["Los Alamos National Lab (LANL)"], ["Лос-Аламос (LANL)"]),
        "JPL": N("lab", ["NASA JPL", "Jet Propulsion Lab"]),
        "MIT": N("lab", ["MIT Plasma Science & Fusion Center"], ["МТИ Плазма"]),
        "AFRL": N("lab", ["Air Force Research Lab (AFRL)"], ["Air Force Research Lab (AFRL)"]),
        "CALTECH": N("lab", ["Caltech"], ["Калифорнийский ИТ (Caltech)"]),
        "KCNSC": N("lab", ["Kansas City National Security Campus"]),
        "IFES": N("lab", ["Institute For Exotic Sciences (Alabama)"]),
        "NOVA": N("lab", ["Novarti (Massachusetts)"]),
        "P1": N("dis", ["Cassias 06.2025"], st=("◌ DISAPPEARED", "◌ ИСЧЕЗЛА")),
        "P2": N("dis", ["Chavez 05.2025"], st=("◌ DISAPPEARED", "◌ ИСЧЕЗ")),
        "P3": N("dis", ["Hassen-Tores 2025"], st=("◌ DISAPPEARED", "◌ ИСЧЕЗЛА")),
        "P4": N("died", ["Maiwald"], st=("◧ DIED, UNCLEAR", "◧ УМЕР, ПРИЧИНА НЕЯСНА")),
        "P5": N("died", ["Higgs"], st=("◧ DIED, UNCLEAR", "◧ УМЕР, ПРИЧИНА НЕЯСНА")),
        "P6": N("dis", ["McCasland 02.2026"], st=("◌ DISAPPEARED", "◌ ИСЧЕЗ")),
        "P7": N("kill", ["Loureiro 12.2025"], st=("✕ KILLED (SUSPECT)", "✕ УБИТ")),
        "P8": N("kill", ["Grillmar 02.2026", "shot at home"], ["Grillmar 02.2026", "застрелен"], st=("✕ KILLED (SUSPECT)", "✕ УБИТ")),
        "P9": N("dis", ["Garcia 2025"], st=("◌ DISAPPEARED", "◌ ИСЧЕЗ")),
        "P10": N("died", ["Eskridge 2022"], st=("◧ DIED, UNCLEAR", "◧ УМЕРЛА, ПРИЧИНА НЕЯСНА")),
        "P11": N("found", ["Thomas", "found dead in lake"], ["Thomas", "тело в озере"], st=("▪ FOUND DEAD", "▪ ТЕЛО НАЙДЕНО")),
    },
    edges=[("LANL", "P1", "s"), ("LANL", "P2", "s"), ("JPL", "P3", "s"), ("JPL", "P4", "s"), ("JPL", "P5", "s"), ("AFRL", "P6", "s"),
           ("MIT", "P7", "s"), ("CALTECH", "P8", "s"), ("KCNSC", "P9", "s"), ("IFES", "P10", "s"), ("NOVA", "P11", "s")],
    legend=[("dot", BLUE, two("institution", "учреждение")), ("dot", GOLD, two("disappeared", "исчез(ла)")), ("dot", AMBER, two("killed (suspect named)", "убит(а) (назван подозреваемый)")),
            ("dot", VIOLET, two("died, cause unclear", "умер(ла), причина неясна")), ("dot", MUTED, two("found dead in a lake", "найден(а) мёртвым в озере"))],
    text={"en": {"title": "Institutional cluster map", "sub": "Eleven cases by the institution each person is linked to", "tag": "TRACK 5 DIAGRAM",
                 "desc": "Eight institutions on the left, eleven cases on the right. Los Alamos: Cassias (disappeared June 2025) and Chavez (disappeared May 2025). NASA JPL: Hassen-Tores (disappeared 2025), Maiwald and Higgs (died, unclear). AFRL: McCasland (disappeared February 2026). MIT Plasma Science and Fusion Center: Loureiro (killed, suspect, December 2025). Caltech: Grillmar (shot at home, February 2026). Kansas City National Security Campus: Garcia (disappeared 2025). Institute For Exotic Sciences, Alabama: Eskridge (died, unclear, 2022). Novarti, Massachusetts: Thomas (found dead in a lake).",
                 "foot": ["Redrawn from people-analysis/diagrams/institutional_cluster_map.mmd; the previous PNG render stays in the repository.",
                          "Statuses are as recorded in the track; the track attributes none of the cases to UAP-related activity. Individual cases are not verified on these pages."]},
          "ru": {"title": "Карта институциональных кластеров", "sub": "Одиннадцать случаев по учреждению, с которым связан человек", "tag": "ДИАГРАММА ТРЕКА 5",
                 "desc": "Восемь учреждений слева, одиннадцать случаев справа. Лос-Аламос: Cassias (исчезла в июне 2025) и Chavez (исчез в мае 2025). NASA JPL: Hassen-Tores (исчезла в 2025), Maiwald и Higgs (умерли, причина неясна). AFRL: McCasland (исчез в феврале 2026). МТИ, Центр науки о плазме и термоядерного синтеза: Loureiro (убит, подозреваемый назван, декабрь 2025). Caltech: Grillmar (застрелен дома, февраль 2026). Kansas City National Security Campus: Garcia (исчез в 2025). Institute For Exotic Sciences, Алабама: Eskridge (умерла, причина неясна, 2022). Novarti, Массачусетс: Thomas (тело найдено в озере).",
                 "foot": ["Перерисовано из people-analysis/diagrams/institutional_cluster_map.mmd; прежний PNG остаётся в репозитории.",
                          "Статусы приведены как записаны в треке; трек не связывает ни один случай с деятельностью, относящейся к НЛО. Отдельные случаи на этих страницах не проверяются."]}},
)


def main():
    for slug, spec in SPECS.items():
        for lang in ("en", "ru"):
            write("guide/assets/diagrams/%s.%s.svg" % (slug, lang), draw(spec, lang))


if __name__ == "__main__":
    main()
