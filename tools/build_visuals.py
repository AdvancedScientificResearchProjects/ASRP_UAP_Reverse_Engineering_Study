#!/usr/bin/env python3
"""Generates the showcase visuals of the UAP Reverse Engineering Study (never hand-edit the SVG output).

    python3 tools/build_visuals.py

Output (English and Russian twin for every picture)
    guide/assets/banner/hero-banner.{en,ru}.svg              generated illustration, not a screenshot
    guide/assets/diagrams/tracks-map.{en,ru}.svg             eleven tracks in four kinds
    guide/assets/diagrams/claimed-vs-shown.{en,ru}.svg       what is claimed, what the repository shows
    guide/assets/diagrams/ecp-agreement.{en,ru}.svg          response agreement, percipients anonymised (P1-P3)
    guide/assets/diagrams/ecp-validation.{en,ru}.svg         reference validation, percipients anonymised
    guide/assets/diagrams/blinding-sequence.{en,ru}.svg      who heard what before answering, anonymised
    guide/assets/diagrams/ai-control.{en,ru}.svg             SigLIP2: cropped score vs full photo vs controls
    guide/assets/diagrams/timeline.{en,ru}.svg               2026 study timeline and dates the archives record
    guide/assets/diagrams/ecosystem-claims.{en,ru}.svg       stated loop, siblings, claims found only in the graph
    guide/assets/icons/*.svg                                 navigation icons

Numbers come from tools/facts.py (computed at build time); the AI scores are parsed from the control-test
report and the committed JSON outputs; every date on the timeline is checked against the repository text it
is taken from. The matrices carry no percipient names: the three percipients are P1, P2, P3 in the order in
which they answered. Rules (ASRP visual standard): <title>, <desc>, viewBox on every SVG; text is measured
and must fit its container; a status is a word paired with a shape, never colour alone; one token set
(tools/svgkit.py).
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import *  # noqa: E402,F401,F403  (tokens, text(), Canvas, write(), ...)
import facts as factsmod  # noqa: E402

F = factsmod.facts()
ARCHIVE = "archive/README_2026-11-19_pre-showcase.md"


def fmt(s):
    return s.format(**F)


STATE = {
    "en": {"built": ("■ BUILT / RUNS", GREEN), "partly": ("◧ PARTLY", GOLD), "absent": ("✕ ABSENT", AMBER),
           "claimed": ("◇ CLAIMED ONLY", VIOLET), "avail": ("✓ COMMITTED", GREEN), "pending": ("◌ NOT LIVE", AMBER),
           "prelim": ("◧ PRELIMINARY", GOLD), "recorded": ("◇ CLAIMS RECORDED", VIOLET), "hyp": ("◇ HYPOTHESIS MAP", VIOLET)},
    "ru": {"built": ("■ ЕСТЬ / РАБОТАЕТ", GREEN), "partly": ("◧ ЧАСТИЧНО", GOLD), "absent": ("✕ ОТСУТСТВУЕТ", AMBER),
           "claimed": ("◇ ТОЛЬКО ЗАЯВЛЕНО", VIOLET), "avail": ("✓ В РЕПОЗИТОРИИ", GREEN), "pending": ("◌ НЕ ЗАПУЩЕНО", AMBER),
           "prelim": ("◧ ПРЕДВАРИТЕЛЬНО", GOLD), "recorded": ("◇ ЗАЯВЛЕНИЯ ЗАПИСАНЫ", VIOLET), "hyp": ("◇ КАРТА ГИПОТЕЗ", VIOLET)},
}


def foot(cv, parts, bottom, color=MUTED, weight=400):
    lines = []
    for p in ([parts] if isinstance(parts, str) else parts):
        lines += wrap(p, FS_SMALL, cv.w - 48, weight >= 600)
    y = bottom - 20 * (len(lines) - 1)
    for i, ln in enumerate(lines):
        cv.label(24, y + 20 * i, ln, FS_SMALL, color, weight=weight, box=cv.w - 48)
    return len(lines)


def checked(path, needle):
    """Abort the build when a date or figure drawn on a picture is not in the repository text it cites."""
    rel = ARCHIVE if path == "README.md" else path
    if needle not in open(os.path.join(factsmod.ROOT, rel), encoding="utf-8").read():
        raise SystemExit("build_visuals: %r not found in %s" % (needle, path))
    return needle


# --- hero banner -----------------------------------------------------------------------------
KIND_COLOR = {"exp": GOLD, "arch": TEAL, "layer": VIOLET, "lit": BLUE}
TRACK_KIND = {1: "exp", 2: "arch", 3: "arch", 4: "arch", 5: "layer", 6: "layer", 7: "layer", 8: "layer", 9: "lit", 10: "arch", 11: "arch"}

BANNER = {
    "en": {"title": "UAP Reverse Engineering", "kicker": "REVERSE ENGINEERING HUB",
           "tag": "PRIVATE · EXPLORATORY · FINDINGS PRELIMINARY",
           "sub": ["One small experiment, ten archives and layers:", "what is recorded, what is only claimed"],
           "chips": ["{tracks} tracks · {files_total} files", "1 session · {percipient_reports} percipients", "blinding broken: {blinded_compromised_n} of {percipient_reports}"],
           "foot": "gold experiment · teal archive · violet analysis · blue catalog",
           "desc": ("Generated illustration, not a screenshot. A central hub with {tracks} numbered dots for the {tracks} tracks: gold for the one "
                    "experiment (Track 1), teal for archives of external material, violet for analysis layers, blue for the literature catalog. "
                    "Title, and three figures computed from the repository: {tracks} tracks and {files_total} files, one percipient session "
                    "with {percipient_reports} percipients, blinding compromised for {blinded_compromised_n} of {percipient_reports}.")},
    "ru": {"title": "Реверс-инжиниринг НАЯ", "kicker": "ХАБ РЕВЕРС-ИНЖИНИРИНГА",
           "tag": "ПРИВАТНО · ПОИСКОВОЕ · ВЫВОДЫ ПРЕДВАРИТЕЛЬНЫЕ",
           "sub": ["Один небольшой эксперимент, десять архивов и слоёв:", "что записано и что только заявлено"],
           "chips": ["{tracks} треков · {files_ru}", "1 сеанс · {percipient_reports} перципиента", "ослепление: {blinded_compromised_n} из {percipient_reports} нарушено"],
           "foot": "золото эксперимент · бирюза архив · фиолет анализ · синий каталог",
           "desc": ("Сгенерированная иллюстрация, не скриншот. Центральный узел и {tracks} пронумерованных точек по числу треков: золотая для "
                    "единственного эксперимента (трек 1), бирюзовые для архивов внешнего материала, фиолетовые для слоёв анализа, синяя для "
                    "каталога литературы. Заголовок и три числа, посчитанные по репозиторию: {tracks} треков и {files_ru}, один сеанс "
                    "с {percipient_reports} перципиентами, ослепление нарушено у {blinded_compromised_n} из {percipient_reports}.")},
}


def banner(lang):
    c = BANNER[lang]
    desc = fmt(c["desc"])
    W, H = 1200, 330
    o = [svg_open(W, H, c["title"], desc)]
    cx, cy, rx, ry = 270, 165, 150, 108
    n = 11
    pts = [(cx + rx * math.cos(math.radians(-90 + 360 * i / n)), cy + ry * math.sin(math.radians(-90 + 360 * i / n))) for i in range(n)]
    ring = " ".join("%s%.1f,%.1f" % ("M" if i == 0 else "L", x, y) for i, (x, y) in enumerate(pts)) + " Z"
    o.append("<path d='%s' fill='none' stroke='%s' stroke-opacity='0.5'/>" % (ring, LINE))
    for i, (x, y) in enumerate(pts):
        col = KIND_COLOR[TRACK_KIND[i + 1]]
        o.append("<line x1='%d' y1='%d' x2='%.1f' y2='%.1f' stroke='%s' stroke-width='1.4' stroke-opacity='0.7' stroke-dasharray='5 7'>"
                 "<animate attributeName='stroke-dashoffset' from='24' to='0' dur='%.1fs' repeatCount='indefinite'/></line>"
                 % (cx, cy, x, y, col, 2.2 + 0.2 * i))
    o.append("<circle cx='%d' cy='%d' r='38' fill='%s' stroke='%s' stroke-width='2' filter='url(#glow)'/>" % (cx, cy, PANEL, TEAL))
    o.append(text(cx, cy + 6, "UAP", 18, INK, "middle", 800, 1))
    for i, (x, y) in enumerate(pts):
        col = KIND_COLOR[TRACK_KIND[i + 1]]
        o.append("<circle cx='%.1f' cy='%.1f' r='15' fill='%s' stroke='%s' stroke-width='2.4'/>" % (x, y, BG0, col))
        o.append(text("%.1f" % x, "%.1f" % (y + 5), str(i + 1), FS_SMALL, INK, "middle", 700))
    tx = 480
    box = W - tx - 36
    o.append(text(tx, 66, c["kicker"], FS_KICKER, TEAL, "start", 700, 2, box))
    o.append(text(W - 36, 36, c["tag"], FS_SMALL, MUTED, "end", 700, 2, 560))
    o.append(text(tx, 128, c["title"], 46, INK, "start", 800, 0, box))
    for i, line in enumerate(c["sub"]):
        o.append(text(tx, 172 + 28 * i, line, 20, MUTED, "start", 400, 0, box))
    x = tx
    for i, chip in enumerate(c["chips"]):
        chip = fmt(chip)
        w = text_width(chip, FS_KICKER, True) + 18
        if x + w > W - 16:
            raise SystemExit("chips overflow the banner: %r" % chip)
        col = [GOLD, TEAL, AMBER][i]
        o.append("<rect x='%.1f' y='246' width='%.1f' height='38' rx='19' fill='%s' fill-opacity='0.08' stroke='%s'/>" % (x, w, col, col))
        o.append(text("%.1f" % (x + w / 2), 271, chip, FS_KICKER, INK, "middle", 700))
        x += w + 8
    o.append(text(24, H - 14, c["foot"], FS_SMALL, MUTED, "start", 400, 0, W - 48))
    o.append("</svg>\n")
    return "\n".join(o)


# --- tracks map ------------------------------------------------------------------------------
TRACKMAP = {
    "en": {
        "title": "Eleven tracks in four kinds",
        "sub": "Only Track 1 is an experiment; the rest record or analyse",
        "tag": "TRACKS",
        "desc": ("Eleven track cards in four kinds. Experiment (gold): Track 1, the artifact UAP-FRAG-001 with one percipient session of "
                 "{percipient_reports} percipients, {ai_reports} AI reports and a {pipeline_stages}-stage vision pipeline. Archives of external material "
                 "(teal): Track 2 Lazar ({lazar_transcripts} transcripts), Track 3 Chernobrov ({chernobrov_transcripts}), Track 4 Dubna, Track 10 Gershtein "
                 "({gershtein_transcripts}), Track 11 PURSUE (225 records, {pursue_transcripts} transcripts). Analysis layers (violet): Track 5 OSINT "
                 "method, Track 6 people, Track 7 corporate, Track 8 synthesis. Catalog (blue): Track 9 literature. Every card ends with a state word."),
        "cards": [
            (1, "1 · Artifact + ECP session", "One object, one session of {percipient_reports} percipients, {ai_reports} AI reports, {pipeline_stages} CV stages", "prelim"),
            (2, "2 · Bob Lazar archive", "{lazar_transcripts} transcripts 1989-2026: S-4, element 115. Single-witness claims", "recorded"),
            (3, "3 · Chernobrov archive", "{chernobrov_transcripts} transcripts 1988-2017: time machine, anomalous zones. Recorded claims", "recorded"),
            (4, "4 · Dubna / Element 115", "JINR interview, {t4_diagrams} diagrams; the 2004 synthesis is a published result", "avail"),
            (5, "5 · OSINT method", "{t5_md} pages: how to filter ordinary physics from novelty", "avail"),
            (6, "6 · People analysis", "{people_files} public-source profiles; no cause of death, no attribution", "avail"),
            (7, "7 · Corporate analysis", "EG&G to Amentum lineage; fuel loop is a hypothesis map, not a pipeline", "hyp"),
            (8, "8 · Cross-archive synthesis", "3 pages at the repository root: overlaps, taxonomy, podcasts", "avail"),
            (9, "9 · Literature catalog", "{t9_md} pages of public-source provenance; claims not validated", "avail"),
            (10, "10 · Gershtein archive", "{gershtein_transcripts} interviews: Soviet programs, plasma, NDE", "recorded"),
            (11, "11 · PURSUE releases", "225 declassified records, {pursue_cards} cards; claims not imported", "avail"),
        ],
        "legend": [("gold", "experiment"), ("teal", "archive of external material"), ("violet", "analysis layer"), ("blue", "catalog")],
        "foot": "Eight tracks are archives of external material; the one experiment is Track 1.",
    },
    "ru": {
        "title": "Одиннадцать треков четырёх видов",
        "sub": "Эксперимент только трек 1; остальные фиксируют или анализируют",
        "tag": "ТРЕКИ",
        "desc": ("Одиннадцать карточек треков четырёх видов. Эксперимент (золото): трек 1, артефакт UAP-FRAG-001, один сеанс с "
                 "{percipient_reports} перципиентами, {ai_reports} ИИ-отчёта и конвейер из {pipeline_stages} стадий зрения. Архивы внешнего материала "
                 "(бирюза): трек 2 Лазар ({lazar_transcripts} транскриптов), трек 3 Чернобров ({chernobrov_transcripts}), трек 4 Дубна, трек 10 Герштейн "
                 "({gershtein_transcripts}), трек 11 PURSUE (225 записей, {pursue_transcripts} транскриптов). Слои анализа (фиолет): трек 5 метод "
                 "OSINT, трек 6 люди, трек 7 корпорации, трек 8 синтез. Каталог (синий): трек 9 литература. Каждая карточка кончается словом-состоянием."),
        "cards": [
            (1, "1 · Артефакт + сеанс КП", "Один объект, один сеанс с {percipient_reports} перципиентами, {ai_reports} ИИ-отчёта, {pipeline_stages} стадий CV", "prelim"),
            (2, "2 · Архив Боба Лазара", "{lazar_transcripts} транскриптов 1989-2026: S-4, элемент 115. Заявления одного свидетеля", "recorded"),
            (3, "3 · Архив Черноброва", "{chernobrov_transcripts} транскриптов 1988-2017: машина времени, аномальные зоны. Записанные заявления", "recorded"),
            (4, "4 · Дубна / Элемент 115", "Интервью ОИЯИ, {t4_diagrams} схем; синтез 2004 года опубликованный результат", "avail"),
            (5, "5 · Метод OSINT", "{t5_md} страниц: как отделить обычную физику от новизны", "avail"),
            (6, "6 · Анализ людей", "{people_files} профилей по открытым источникам; без причин смерти и атрибуции", "avail"),
            (7, "7 · Корпоративный анализ", "Линия EG&G до Amentum; топливная петля карта гипотез, не конвейер", "hyp"),
            (8, "8 · Кросс-архивный синтез", "3 страницы в корне: пересечения, таксономия, подкасты", "avail"),
            (9, "9 · Каталог литературы", "{t9_md} страницы провенанса по открытым источникам; заявления не валидируются", "avail"),
            (10, "10 · Архив Герштейна", "{gershtein_transcripts} интервью: советские программы, плазма, NDE", "recorded"),
            (11, "11 · Релизы PURSUE", "225 рассекреченных записей, {pursue_cards} карточки; заявления не импортируются", "avail"),
        ],
        "legend": [("gold", "эксперимент"), ("teal", "архив внешнего материала"), ("violet", "слой анализа"), ("blue", "каталог")],
        "foot": "Восемь треков это архивы внешнего материала; единственный эксперимент это трек 1.",
    },
}


def trackmap(lang):
    c = TRACKMAP[lang]
    st = STATE[lang]
    W, H = 1200, 664
    cv = Canvas(W, H, c["title"], fmt(c["desc"]), c["title"], c["sub"], c["tag"])
    cols, bw, gap = 4, 270, 24
    bh, vgap, y0 = 142, 14, 100
    for i, (num, title, body, state) in enumerate(c["cards"]):
        r, k = divmod(i, cols)
        x, y = 24 + k * (bw + gap), y0 + r * (bh + vgap)
        col = KIND_COLOR[TRACK_KIND[num]]
        lab, _ = st[state]
        cv.box(x, y, bw, title, [fmt(body)], status=[(lab, col)], stroke=col, h=bh, valign="top", title_size=15)
    # legend in the free twelfth cell
    lx, ly = 24 + 3 * (bw + gap), y0 + 2 * (bh + vgap)
    cv.label(lx, ly + 22, {"en": "KINDS", "ru": "ВИДЫ"}[lang], FS_KICKER, TEAL, weight=700)
    for j, (cname, lab) in enumerate(c["legend"]):
        col = {"gold": GOLD, "teal": TEAL, "violet": VIOLET, "blue": BLUE}[cname]
        cv.o.append("<rect x='%d' y='%d' width='16' height='16' rx='4' fill='%s'/>" % (lx, ly + 40 + j * 26, col))
        cv.label(lx + 26, ly + 54 + j * 26, lab, FS_SMALL, INK, box=bw - 30)
    foot(cv, c["foot"], H - 14)
    return "\n".join(cv.o + ["</svg>\n"])


# --- claimed vs shown ------------------------------------------------------------------------
CLAIM = {
    "en": {
        "title": "What is claimed and what the repository shows",
        "sub": "Left: README, reference or graph. Right: what the files show",
        "tag": "CLAIMED VS SHOWN",
        "cols": ["TOPIC", "CLAIMED", "SHOWN IN THE REPOSITORY", "STATE"],
        "rows": [
            ("ECP session", "Percipients identified function, system membership, material",
             "{ref_exact} of {ref_params} reference parameters match, descriptive only; blinding compromised for {blinded_compromised_n} of {percipient_reports}; no chance baseline", "partly"),
            ("Reference object", "Navigation beacon, biometal, variable radioactivity",
             "Reference statements of the Program Director; no SEM, XRF or gamma report is committed", "claimed"),
            ("AI visual result", "Biological family, score {score_crop}",
             "{score_crop} is a crop score; the full photo scores {score_full}, inside the fossil range; neither confirms nor excludes anomalous origin", "partly"),
            ("Lab analysis", "Needed to settle material and radioactivity", "Recommended in the control-test report; no laboratory result in the repository", "absent"),
            ("Archives 2, 3, 10", "S-4, gravity propulsion, time machine, Soviet programs",
             "Testimony and interviews recorded as claims; no physical material in public hands", "claimed"),
            ("Outreach nodes", "DoE/LANL first reader, Stanford, NCI, Boeing, Cortical Labs",
             "Only in the graph JSON; no letter, reply or date in the corpus", "claimed"),
            ("Patent", "Graph: FBHFS patent anchors a UAP-adjacent oncology frame", "README: no patent filing; the oncology text is a book speculation", "absent"),
            ("Course", "UAP course on Arcanum-12", "Described as in development; not live, no date, no credential", "pending"),
        ],
        "foot": ["Each row names a state in words; a plan, a protocol or a graph node is not a result.", "Sources: guide/EVIDENCE.md lists the file behind every row."],
    },
    "ru": {
        "title": "Что заявлено и что показывает репозиторий",
        "sub": "Слева: README, референс или граф. Справа: что показывают файлы",
        "tag": "ЗАЯВЛЕНО И ПОКАЗАНО",
        "cols": ["ТЕМА", "ЗАЯВЛЕНО", "ПОКАЗАНО В РЕПОЗИТОРИИ", "СОСТОЯНИЕ"],
        "rows": [
            ("Сеанс КП", "Перципиенты назвали функцию, принадлежность к системе, материал",
             "{ref_exact} из {ref_params} параметров референса совпали, только описательно; ослепление нарушено у {blinded_compromised_n} из {percipient_reports}; шансового базиса нет", "partly"),
            ("Референс", "Навигационный маяк, биометалл, переменная радиоактивность",
             "Утверждения руководителя программы; отчётов SEM, XRF или гамма в репозитории нет", "claimed"),
            ("Итог ИИ", "Биологическое семейство, оценка {score_crop}",
             "{score_crop} это оценка обрезанного фото; полное фото даёт {score_full}, внутри диапазона окаменелостей; аномальное происхождение не подтверждено и не исключено", "partly"),
            ("Лаборатория", "Нужен, чтобы решить вопрос материала и радиоактивности", "Рекомендован в отчёте контрольного теста; лабораторного результата в репозитории нет", "absent"),
            ("Архивы 2, 3, 10", "S-4, гравитационная тяга, машина времени, советские программы",
             "Свидетельства и интервью записаны как заявления; физического материала в открытом доступе нет", "claimed"),
            ("Узлы аутрича", "DoE/LANL первый читатель, Stanford, NCI, Boeing, Cortical Labs",
             "Только в JSON графа; ни письма, ни ответа, ни даты в корпусе нет", "claimed"),
            ("Патент", "Граф: патент FBHFS якорь для UAP-смежной онкологической рамки", "README: заявки нет; онкологический текст это спекуляция из книги", "absent"),
            ("Курс", "Курс по НАЯ на Arcanum-12", "Описан как разрабатываемый; не запущен, без даты и сертификата", "pending"),
        ],
        "foot": ["Каждая строка называет состояние словом; план, протокол или узел графа не результат.", "Источники: guide/EVIDENCE.ru.md называет файл за каждой строкой."],
    },
}


def claimed(lang):
    c = CLAIM[lang]
    st = STATE[lang]
    rh, gap, ytop = 100, 8, 98
    W = 1200
    H = ytop + 26 + len(c["rows"]) * (rh + gap) + 64
    cv = Canvas(W, H, c["title"], "Eight rows, left to right: topic, what is claimed, what the repository shows, a state word. " + "; ".join(
        "%s: %s" % (r[0], fmt(r[2])) for r in c["rows"]) if lang == "en" else
        "Восемь строк слева направо: тема, что заявлено, что показывает репозиторий, слово-состояние. " + "; ".join(
            "%s: %s" % (r[0], fmt(r[2])) for r in c["rows"]), c["title"], c["sub"], c["tag"])
    x0, x1, x2, x3 = 24, 196, 520, 1000
    w1, w2, w3 = 330, 468, 176
    cv.label(x0, ytop + 10, c["cols"][0], FS_KICKER, TEAL, weight=700, box=160)
    cv.label(x1, ytop + 10, c["cols"][1], FS_KICKER, TEAL, weight=700, box=w1)
    cv.label(x2, ytop + 10, c["cols"][2], FS_KICKER, TEAL, weight=700, box=w2)
    cv.label(x3, ytop + 10, c["cols"][3], FS_KICKER, TEAL, weight=700, box=w3)
    for i, (topic, claim, shown, state) in enumerate(c["rows"]):
        y = ytop + 26 + i * (rh + gap)
        label, col = st[state]
        cv.label(x0, y + rh / 2 + 5, topic, FS_SMALL + 1, INK, weight=700, box=164)
        cv.box(x1, y, w1 - 12, None, [fmt(claim)], stroke=BLUE, h=rh)
        cv.box(x2, y, w2 - 12, None, [fmt(shown)], stroke=col, h=rh)
        cv.box(x3, y, w3, None, [], status=[(label, col)], stroke=col, h=rh, center=True)
    foot(cv, c["foot"], H - 14)
    return "\n".join(cv.o + ["</svg>\n"])


# --- matrices (percipients anonymised) -------------------------------------------------------
CELL = {"exact": ("exact", GREEN, "■"), "partial": ("partial", GOLD, "◧"), "none": ("no data", MUTED, "·"),
        "wrong": ("incorrect", AMBER, "✕")}
CELL_RU = {"exact": "точно", "partial": "частично", "none": "нет данных", "wrong": "ошибочно"}
AGREE_COLOR = {"HIGH": GREEN, "MEDIUM": GOLD, "LOW": AMBER}


def matrix(lang, title, sub, tag, desc, heads, rows, foot_lines, summary_col):
    """rows: (label, [cell kinds], summary text, summary colour)."""
    rh = 56
    W = 1200
    H = 150 + len(rows) * (rh + 6) + 20 + 22 * len(foot_lines) + 20
    cv = Canvas(W, H, title, desc, title, sub, tag)
    x0, wl = 24, 400
    xc, wc = x0 + wl + 12, 130
    xs = xc + 3 * (wc + 8) + 8
    ws = W - 24 - xs
    y = 96
    cv.label(x0, y + 22, heads[0], FS_KICKER, TEAL, weight=700, box=wl)
    for k in range(3):
        cv.label(xc + k * (wc + 8) + wc / 2, y + 22, "P%d" % (k + 1), FS_KICKER, TEAL, "middle", 700)
    cv.label(xs, y + 22, heads[1], FS_KICKER, TEAL, weight=700, box=ws)
    y += 36
    for label, cells, summ, scol in rows:
        cv.o.append(text(x0, y + rh / 2 + 5, label, FS_BODY, INK, "start", 600, 0, wl))
        for k, kind in enumerate(cells):
            word = CELL[kind][0] if lang == "en" else CELL_RU[kind]
            col = CELL[kind][1]
            glyph = CELL[kind][2]
            cv.o.append("<rect x='%d' y='%d' width='%d' height='%d' rx='8' fill='%s' fill-opacity='0.10' stroke='%s'/>"
                        % (xc + k * (wc + 8), y, wc, rh, col, col))
            cv.o.append(text(xc + k * (wc + 8) + wc / 2, y + rh / 2 + 5, "%s %s" % (glyph, word), FS_SMALL, INK, "middle", 700, 0, wc - 8))
        cv.o.append("<rect x='%d' y='%d' width='%d' height='%d' rx='8' fill='%s' fill-opacity='0.10' stroke='%s'/>" % (xs, y, ws, rh, scol, scol))
        cv.o.append(text(xs + 12, y + rh / 2 + 5, summ, FS_SMALL, INK, "start", 700, 0, ws - 20))
        y += rh + 6
    foot(cv, foot_lines, H - 14)
    return "\n".join(cv.o + ["</svg>\n"])


AGREEMENT_ROWS = {  # theme EN, theme RU, cells, level  (cells read from the cross_comparison table / the original matrix)
    "rows": [("Signal or beacon-like function", "Сигнальная, маяковая функция", ["exact", "partial", "exact"], "MEDIUM"),
             ("Part of a larger system", "Часть большей системы", ["exact", "exact", "exact"], "HIGH"),
             ("No autonomous consciousness", "Нет автономного сознания", ["exact", "exact", "exact"], "HIGH"),
             ("Non-terrestrial origin", "Внеземное происхождение", ["partial", "partial", "exact"], "MEDIUM"),
             ("Non-standard mineral material", "Нестандартный минеральный материал", ["partial", "partial", "partial"], "MEDIUM"),
             ("Channel upward, above ajna", "Канал вверх, выше аджны", ["exact", "exact", "exact"], "HIGH"),
             ("No direct danger perceived", "Опасность не воспринята", ["exact", "exact", "exact"], "HIGH"),
             ("Dynamic movement or flight", "Динамика, полёт", ["wrong", "partial", "none"], "LOW")]}
LEVEL_RU = {"HIGH": "ВЫСОКАЯ", "MEDIUM": "СРЕДНЯЯ", "LOW": "НИЗКАЯ"}


def agreement(lang):
    cell_word = {"exact": "present", "partial": "partial", "none": "absent", "wrong": "contradictory"}
    CELL["exact"], CELL["wrong"] = ("present", GREEN, "■"), ("contradictory", AMBER, "✕")
    CELL["none"] = ("absent", MUTED, "·")
    CELL_RU["exact"], CELL_RU["wrong"], CELL_RU["none"] = "ясно", "противоречие", "нет сигнала"
    rows = [((r[0] if lang == "en" else r[1]), r[2], ("%s %s" % ({"en": "agreement", "ru": "согласованность"}[lang], r[3] if lang == "en" else LEVEL_RU[r[3]])), AGREE_COLOR[r[3]])
            for r in AGREEMENT_ROWS["rows"]]
    tx = {"en": ("Response agreement across three percipients", "Overlap of recorded responses only; not independent convergence", "ECP RESPONSES",
                 ["THEME", "OVERLAP LEVEL"],
                 ["P1, P2, P3 = the three percipients in the order they answered; names are withheld.",
                  "Blinding was compromised for P2 and P3: they heard earlier answers. Source: analysis/cross_comparison.md."],
                 ("Eight rows (themes), three columns (P1, P2, P3) with the words present, partial, absent or contradictory, and an overlap level. "
                  "Signal function: present, partial, present, medium. Part of a larger system: present three times, high. No autonomous consciousness: "
                  "present three times, high. Non-terrestrial origin: partial, partial, present, medium. Non-standard mineral material: partial three "
                  "times, medium. Channel upward: present three times, high. No danger: present three times, high. Dynamic movement: contradictory, "
                  "partial, absent, low. Percipient names are withheld. Blinding was compromised for P2 and P3.")),
          "ru": ("Согласованность ответов трёх перципиентов", "Пересечение только записанных ответов; не независимая конвергенция", "ОТВЕТЫ КП",
                 ["ТЕМА", "УРОВЕНЬ ПЕРЕСЕЧЕНИЯ"],
                 ["P1, P2, P3 = три перципиента в порядке ответов; имена не приводятся.",
                  "Ослепление нарушено у P2 и P3: они слышали предыдущие ответы. Источник: analysis/cross_comparison.md."],
                 ("Восемь строк (темы), три колонки (P1, P2, P3) со словами ясно, частично, нет сигнала или противоречие и уровень пересечения. "
                  "Сигнальная функция: ясно, частично, ясно, средняя. Часть большей системы: ясно трижды, высокая. Нет автономного сознания: ясно "
                  "трижды, высокая. Внеземное происхождение: частично, частично, ясно, средняя. Нестандартный минеральный материал: частично трижды, "
                  "средняя. Канал вверх: ясно трижды, высокая. Нет опасности: ясно трижды, высокая. Динамика: противоречие, частично, нет сигнала, "
                  "низкая. Имена перципиентов не приводятся. Ослепление нарушено у P2 и P3."))}[lang]
    return matrix(lang, tx[0], tx[1], tx[2], tx[5], tx[3], rows, tx[4], None)


VALID_ROWS = [("Beacon or signal device", "Маяк, сигнальное устройство", ["exact", "partial", "exact"], "2 exact, 1 partial", "2 точно, 1 частично", GOLD),
              ("Part of a larger system", "Часть большей системы", ["exact", "exact", "exact"], "3 exact", "3 точно", GREEN),
              ("No own consciousness", "Нет собственного сознания", ["exact", "exact", "exact"], "3 exact", "3 точно", GREEN),
              ("Mountains, desert terrain", "Горы, пустынная местность", ["exact", "none", "none"], "1 exact", "1 точно", GREEN),
              ("Non-terrestrial origin", "Внеземное происхождение", ["exact", "exact", "exact"], "3 exact", "3 точно", GREEN),
              ("Stationary, never flew", "Стационарный, никогда не летал", ["wrong", "none", "none"], "1 incorrect", "1 ошибочно", AMBER),
              ("Temporal navigation", "Навигация во времени", ["none", "none", "partial"], "1 indirect", "1 косвенно", GOLD),
              ("Biometal", "Биометалл", ["partial", "partial", "partial"], "3 partial", "3 частично", GOLD),
              ("Variable radioactivity", "Переменная радиоактивность", ["none", "none", "none"], "not detected", "не обнаружено", AMBER),
              ("Courier, passive carrier", "Курьер, пассивный носитель", ["exact", "exact", "none"], "2 exact", "2 точно", GREEN)]


def validation(lang):
    CELL["exact"], CELL["wrong"], CELL["none"] = ("exact", GREEN, "■"), ("incorrect", AMBER, "✕"), ("no data", MUTED, "·")
    CELL_RU["exact"], CELL_RU["wrong"], CELL_RU["none"] = "точно", "ошибочно", "нет данных"
    rows = [((r[0] if lang == "en" else r[1]), r[2], (r[3] if lang == "en" else r[4]), r[5]) for r in VALID_ROWS]
    tx = {"en": ("Responses against the disclosed reference", "{ref_exact} exact, {ref_partial} partial, {ref_miss} miss of {ref_params} parameters; descriptive only", "VALIDATION",
                 ["REFERENCE PARAMETER", "SUMMARY"],
                 ["The ten parameters were scored after the reference was disclosed; no chance baseline is computed.",
                  "Blinding was compromised for P2 and P3. Source: analysis/ecp_validation_report.md, section 4.1."],
                 ("Ten reference parameters in rows, three percipient columns P1 to P3 (exact, partial, incorrect, no data) and a summary. Beacon: 2 exact, "
                  "1 partial. System: 3 exact. No consciousness: 3 exact. Terrain: 1 exact. Non-terrestrial: 3 exact. Stationary: 1 incorrect. Temporal "
                  "navigation: 1 indirect. Biometal: 3 partial. Variable radioactivity: not detected. Courier: 2 exact. Totals: {ref_exact} of {ref_params} "
                  "with an exact match, {ref_partial} partial, {ref_miss} miss. Descriptive only because blinding was compromised.")),
          "ru": ("Ответы против раскрытого референса", "{ref_exact} точно, {ref_partial} частично, {ref_miss} промах из {ref_params} параметров; только описательно", "ВАЛИДАЦИЯ",
                 ["ПАРАМЕТР РЕФЕРЕНСА", "ИТОГ"],
                 ["Десять параметров оценены после раскрытия референса; шансовый базис не посчитан.",
                  "Ослепление нарушено у P2 и P3. Источник: analysis/ecp_validation_report.md, раздел 4.1."],
                 ("Десять параметров референса в строках, три колонки перципиентов P1-P3 (точно, частично, ошибочно, нет данных) и итог. Маяк: 2 точно, "
                  "1 частично. Система: 3 точно. Нет сознания: 3 точно. Местность: 1 точно. Внеземное: 3 точно. Стационарность: 1 ошибочно. Навигация "
                  "во времени: 1 косвенно. Биометалл: 3 частично. Переменная радиоактивность: не обнаружено. Курьер: 2 точно. Итого: {ref_exact} из "
                  "{ref_params} с точным совпадением, {ref_partial} частично, {ref_miss} промах. Только описательно, потому что ослепление нарушено."))}[lang]
    return matrix(lang, tx[0], fmt(tx[1]), tx[2], fmt(tx[5]), tx[3], rows, tx[4], None)


# --- blinding sequence -----------------------------------------------------------------------
BLIND = {
    "en": {"title": "Who heard what before answering", "sub": "One group call, questions in sequence; names withheld", "tag": "BLINDING",
           "lanes": ["Moderator", "P1", "P2", "P3"],
           "steps": [(0, 1, "Prompt first"), (1, 0, "Raw response"), (0, 2, "Prompt after P1's answer"), (2, 0, "Response, P1's answer heard"),
                     (0, 3, "Prompt after P1 and P2"), (3, 0, "Response, both answers heard")],
           "notes": {1: ("◧ PARTLY BLIND", GOLD, "saw the object earlier, without explanation"), 2: ("✕ COMPROMISED", AMBER, "heard P1 before answering"),
                     3: ("✕ COMPROMISED", AMBER, "heard P1 and P2 before answering")},
           "foot": "Future sessions must be conducted individually (validation report, section 6).",
           "desc": ("Sequence diagram of one group call with a moderator and three percipients P1, P2, P3, names withheld. The moderator prompts P1 first "
                    "and receives a raw response; prompts P2 after P1's answer, so P2 heard P1; prompts P3 after both, so P3 heard both. P1 is partly "
                    "blind (saw the object earlier without explanation); P2 and P3 are compromised. Future sessions must be individual.")},
    "ru": {"title": "Кто что слышал перед ответом", "sub": "Один групповой звонок, вопросы по очереди; имена не приводятся", "tag": "ОСЛЕПЛЕНИЕ",
           "lanes": ["Модератор", "P1", "P2", "P3"],
           "steps": [(0, 1, "Запрос первым"), (1, 0, "Ответ без подсказок"), (0, 2, "Запрос после ответа P1"), (2, 0, "Ответ, ответ P1 слышала"),
                     (0, 3, "Запрос после P1 и P2"), (3, 0, "Ответ, оба ответа слышала")],
           "notes": {1: ("◧ ЧАСТИЧНО СЛЕПОЙ", GOLD, "видел объект раньше без пояснений"), 2: ("✕ НАРУШЕНО", AMBER, "слышала P1 до ответа"),
                     3: ("✕ НАРУШЕНО", AMBER, "слышала P1 и P2 до ответа")},
           "foot": "Будущие сеансы нужно проводить индивидуально (отчёт валидации, раздел 6).",
           "desc": ("Диаграмма последовательности одного группового звонка с модератором и тремя перципиентами P1, P2, P3, имена не приводятся. "
                    "Модератор сначала запрашивает P1 и получает ответ без подсказок; запрашивает P2 после ответа P1, так что P2 слышала P1; запрашивает "
                    "P3 после обоих, так что P3 слышала оба ответа. P1 частично слепой (видел объект раньше без пояснений); у P2 и P3 ослепление "
                    "нарушено. Будущие сеансы нужно проводить индивидуально.")},
}


def blinding(lang):
    c = BLIND[lang]
    W, H = 1200, 600
    cv = Canvas(W, H, c["title"], c["desc"], c["title"], c["sub"], c["tag"])
    xs = [150, 450, 750, 1050]
    cols = [TEAL, GOLD, AMBER, AMBER]
    for x, name, col in zip(xs, c["lanes"], cols):
        cv.box(x - 80, 96, 160, name, [], stroke=col, h=44, center=True, pad=8)
        cv.o.append("<line x1='%d' y1='142' x2='%d' y2='458' stroke='%s' stroke-width='1.4' stroke-dasharray='3 6' stroke-opacity='0.7'/>" % (x, x, LINE))
    y = 176
    for a, b, label in c["steps"]:
        xa, xb = xs[a], xs[b]
        sgn = 1 if xb > xa else -1
        cv.arrow([(xa + sgn * 6, y), (xb - sgn * 6, y)], TEAL if a == 0 else GOLD, label=label, label_at=((xa + xb) / 2, y - 8), label_box=260)
        y += 46
    # notes under the lanes
    for k in (1, 2, 3):
        word, col, why = c["notes"][k]
        cv.box(xs[k] - 135, 474, 270, word, [why], stroke=col, h=82, pad=10, title_size=14, center=True, valign="top")
    foot(cv, c["foot"], H - 8)
    return "\n".join(cv.o + ["</svg>\n"])


# --- AI control test -------------------------------------------------------------------------
def control_scores():
    ct = open(os.path.join(factsmod.ROOT, "reports/ai_reports/AI-2026-04-09-control-test.md"), encoding="utf-8").read()
    rows = re.findall(r"^\| ([ABC]\d): [^|]+ \| (Similar fossil|Dissimilar bio|Negative) \| (0\.\d+) \|", ct, re.M)
    if len(rows) != 13:
        raise SystemExit("control-test table changed: %d rows" % len(rows))
    return [(i, g, float(v)) for i, g, v in rows]


AI = {
    "en": {"title": "SigLIP2: the 0.98 is a crop score, the full photo scores 0.89", "sub": "Bio/organic score, 0 to 1; 13 control images, three groups", "tag": "AI CONTROL TEST",
           "lanes": ["Artifact, cropped (stage 5)", "Artifact, full photo (control test)", "Similar fossils A1-A6", "Dissimilar biological B1-B5", "Non-biological C1-C2"],
           "band": "fossil mean ± 1 SD, n={control_n_similar} (A6 thumbnail excluded)",
           "marks": ["{score_crop}: a different input, the cropped photo", "{score_full}: Z={fossil_z}, {fossil_pct}th percentile of fossils"],
           "foot": ["Control test verdict: it neither confirms nor excludes anomalous origin; laboratory analysis is required.", "Source: reports/ai_reports/AI-2026-04-09-control-test.md; data/processed/material_hypothesis.json."],
           "desc": ("Dot plot of the SigLIP2 bio/organic score from 0 to 1 in five lanes. Artifact, cropped photo from pipeline stage 5: {score_crop}, "
                    "a different input. Artifact, full photograph from the control test: {score_full}. Similar fossils A1 to A6 range from 0.44 to 0.996, "
                    "the nearest dark fossil scores {score_nearest_fossil}. Dissimilar biological specimens score up to {score_max_dissimilar}; non-biological "
                    "controls up to 0.0226. A band marks the mean of the five similar fossils, {fossil_mean}, plus or minus one standard deviation, "
                    "{fossil_std}; the full photo lies inside it (Z={fossil_z}). The test neither confirms nor excludes anomalous origin.")},
    "ru": {"title": "SigLIP2: 0.98 это оценка обрезки, полное фото даёт 0.89", "sub": "Био-балл от 0 до 1; 13 контрольных изображений, три группы", "tag": "КОНТРОЛЬНЫЙ ТЕСТ ИИ",
           "lanes": ["Артефакт, обрезка (ст. 5)", "Артефакт, полное фото", "Похожие окаменелости A1-A6", "Другие биологические B1-B5", "Небиологические C1-C2"],
           "band": "среднее по окаменелостям ± 1 SD, n={control_n_similar} (без миниатюры A6)",
           "marks": ["{score_crop}: другой вход, обрезанное фото", "{score_full}: Z={fossil_z}, {fossil_pct}-й процентиль окаменелостей"],
           "foot": ["Вердикт контрольного теста: он не подтверждает и не исключает аномальное происхождение; нужен лабораторный анализ.", "Источник: reports/ai_reports/AI-2026-04-09-control-test.md; data/processed/material_hypothesis.json."],
           "desc": ("Точечный график био/органического балла SigLIP2 от 0 до 1 в пяти полосах. Артефакт, обрезанное фото со стадии 5 конвейера: "
                    "{score_crop}, другой вход. Артефакт, полная фотография из контрольного теста: {score_full}. Похожие окаменелости A1-A6 лежат от 0.44 до "
                    "0.996, ближайшая тёмная даёт {score_nearest_fossil}. Непохожие биологические образцы до {score_max_dissimilar}; небиологические "
                    "контроли до 0.0226. Полоса отмечает среднее пяти похожих окаменелостей {fossil_mean} плюс-минус одно стандартное отклонение "
                    "{fossil_std}; полное фото лежит внутри (Z={fossil_z}). Тест не подтверждает и не исключает аномальное происхождение.")},
}


def aicontrol(lang):
    c = AI[lang]
    W, H = 1200, 580
    cv = Canvas(W, H, c["title"], fmt(c["desc"]), c["title"], c["sub"], c["tag"])
    x0, x1 = 280, 1150
    sx = lambda v: x0 + (x1 - x0) * v
    top, lh = 130, 58
    scores = control_scores()
    mean, sd = float(F["fossil_mean"]), float(F["fossil_std"])
    # band behind the lanes
    cv.o.append("<rect x='%.1f' y='%d' width='%.1f' height='%d' fill='%s' fill-opacity='0.10' stroke='%s' stroke-opacity='0.5'/>"
                % (sx(mean - sd), top - 10, sx(mean + sd) - sx(mean - sd), 5 * lh + 10, GOLD, GOLD))
    cv.label(sx(mean - sd) + 4, top - 18, fmt(c["band"]), FS_SMALL, GOLD, weight=600, box=520)
    for i, name in enumerate(c["lanes"]):
        y = top + i * lh
        cv.o.append("<line x1='%d' y1='%d' x2='%d' y2='%d' stroke='%s' stroke-width='1' stroke-opacity='0.6'/>" % (x0, y + lh / 2, x1, y + lh / 2, LINE))
        cv.label(24, y + lh / 2 + 5, name, FS_SMALL, INK, weight=600, box=250)
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        cv.label(sx(v), top + 5 * lh + 24, ("%g" % v), FS_SMALL, MUTED, "middle")
        cv.o.append("<line x1='%.1f' y1='%d' x2='%.1f' y2='%d' stroke='%s' stroke-opacity='0.5'/>" % (sx(v), top + 5 * lh, sx(v), top + 5 * lh + 6, MUTED))
    lane = {"A": 2, "B": 3, "C": 4}
    for ident, grp, v in scores:
        y = top + lane[ident[0]] * lh + lh / 2
        col = {"A": TEAL, "B": VIOLET, "C": MUTED}[ident[0]]
        cv.o.append("<circle cx='%.1f' cy='%.1f' r='7' fill='%s' stroke='%s' stroke-width='2'/>" % (sx(v), y, BG0, col))
        dy = -14 if ident not in ("A1", "A4", "B2", "C2") else 24
        cv.o.append(text("%.1f" % sx(v), "%.1f" % (y + dy), ident, FS_SMALL, INK, "middle", 600))
    # artifact markers
    for lane_i, v, mark in ((0, float(F["score_crop"]), c["marks"][0]), (1, float(F["score_full4"]), c["marks"][1])):
        y = top + lane_i * lh + lh / 2
        cv.o.append("<path d='M%.1f %.1f l9 9 l-9 9 l-9 -9 z' fill='%s' stroke='%s' stroke-width='2'/>" % (sx(v), y - 9, GOLD, GOLD))
        cv.o.append(text("%.1f" % (sx(v) - 20), "%.1f" % (y + 5), fmt(mark), FS_SMALL, INK, "end", 700, 0, 460))
    foot(cv, c["foot"], H - 14)
    return "\n".join(cv.o + ["</svg>\n"])


# --- timeline --------------------------------------------------------------------------------
# (date, text EN, text RU, file with the date, needle searched in that file)
T26 = [
    ("2026-04-01", "First commit of the repository", "Первый коммит репозитория", None, None),
    ("2026-04-04", "ECP session ECP-2026-04-04, three percipients", "Сеанс КП ECP-2026-04-04, три перципиента", "analysis/ecp_validation_report.md", "ECP-2026-04-04"),
    ("2026-04-06", "Validation report: reference compared with responses", "Отчёт валидации: референс против ответов", "analysis/ecp_validation_report.md", "2026-04-06"),
    ("2026-04-07", "AI report: segmentation, SigLIP2, anomaly, depth", "ИИ-отчёт: сегментация, SigLIP2, аномалии, глубина", "reports/ai_reports/AI-2026-04-07-001.md", "2026-04-07"),
    ("2026-04-09", "AI control test: full photo, 13 controls", "Контрольный тест ИИ: полное фото, 13 контролей", "reports/ai_reports/AI-2026-04-09-control-test.md", "2026-04-09"),
    ("2026-04-19", "FBI consolidation claim (recap; unverified)", "Заявление ФБР о консолидации (пересказ; не проверено)", "README.md", "19 April 2026"),
    ("2026-05-08", "PURSUE Release 01: 161 records", "PURSUE Релиз 01: 161 запись", "README.md", "8 May 2026"),
    ("2026-05-22", "PURSUE Release 02: 64 records", "PURSUE Релиз 02: 64 записи", "README.md", "2026-05-22"),
    ("2026-07-18", "Last commit before the showcase", "Последний коммит до витрины", None, None),
]
T_EXT = [
    ("1989", "Lazar appearances begin (corpus 1989-2026)", "Начало выступлений Лазара (корпус 1989-2026)", "README.md", "1989–2026"),
    ("2004", "JINR+LLNL element 115 synthesis published (Phys. Rev. C)", "Опубликован синтез 115 элемента ОИЯИ+LLNL (Phys. Rev. C)", "README.md", "2004"),
    ("2021-09-28", "Dubna interview recorded", "Интервью по Дубне записано", "README.md", "28 September 2021"),
    ("2025-12-09", "Dubna interview published", "Интервью по Дубне опубликовано", "README.md", "9 December 2025"),
]


def timeline(lang):
    from datetime import date
    W, H = 1200, 800
    title = {"en": "2026 in the study, and dates the archives record", "ru": "2026 год в исследовании и даты из архивов"}[lang]
    sub = {"en": "Upper lane to scale, April to July 2026. Lower lane not to scale", "ru": "Верхняя полоса в масштабе, апрель-июль 2026. Нижняя не в масштабе"}[lang]
    items = [(d, e if lang == "en" else r, f, n) for d, e, r, f, n in T26]
    ext = [(d, e if lang == "en" else r, f, n) for d, e, r, f, n in T_EXT]
    desc = {"en": "Two lanes. Upper lane to scale, 2026-04-01 to 2026-07-18: " + "; ".join("%s %s" % (d, t) for d, t, f, n in items) +
                  ". Lower lane not to scale, dates the archives record: " + "; ".join("%s %s" % (d, t) for d, t, f, n in ext) + ".",
            "ru": "Две полосы. Верхняя в масштабе, 2026-04-01 .. 2026-07-18: " + "; ".join("%s %s" % (d, t) for d, t, f, n in items) +
                  ". Нижняя не в масштабе, даты, записанные архивами: " + "; ".join("%s %s" % (d, t) for d, t, f, n in ext) + "."}[lang]
    for d, t, f, n in items + ext:
        if f:
            checked(f, n)
    cv = Canvas(W, H, title, desc, title, sub, {"en": "TIMELINE", "ru": "ХРОНОЛОГИЯ"}[lang])
    d0, d1 = date(2026, 4, 1), date(2026, 7, 18)
    xa, xb = 60, W - 60
    xpos = lambda s: xa + (xb - xa) * (date.fromisoformat(s) - d0).days / (d1 - d0).days
    cv.label(24, 104, {"en": "THIS STUDY, 2026 (to scale)", "ru": "ЭТО ИССЛЕДОВАНИЕ, 2026 (в масштабе)"}[lang], FS_KICKER, TEAL, weight=700, box=500)
    yl = 300
    cv.o.append("<line x1='%d' y1='%d' x2='%d' y2='%d' stroke='%s' stroke-width='2.4'/>" % (xa - 20, yl, xb + 20, yl, LINE))
    # first five dates cluster in April: labels stacked below the axis; the later four sit above it, leftmost on top
    for i, (d, t, f, n) in enumerate(items):
        x = xpos(d)
        cv.o.append("<circle cx='%.1f' cy='%d' r='7' fill='%s' stroke='%s' stroke-width='2'/>" % (x, yl, BG0, TEAL if i < 5 else GOLD))
        if i < 5:
            yy = yl + 52 + i * 38
            cv.o.append("<path d='M%.1f %d L%.1f %d L%d %d' fill='none' stroke='%s' stroke-opacity='0.7'/>" % (x, yl + 8, x, yy - 5, 166, yy - 5, LINE))
            cv.label(176, yy, d, FS_SMALL, TEAL, weight=700, box=100)
            cv.label(286, yy, t, FS_SMALL, INK, box=520)
        else:
            k = i - 5
            yy = 150 + k * 34
            cv.o.append("<path d='M%.1f %d L%.1f %d L%.1f %d' fill='none' stroke='%s' stroke-opacity='0.7'/>" % (x, yl - 8, x, yy - 5, x + (-8 if i == 8 else 8), yy - 5, LINE))
            if i == 8:
                cv.label(x - 14, yy, "%s  %s" % (d, t), FS_SMALL, INK, "end", 600, box=420)
            else:
                cv.label(x + 14, yy, "%s  %s" % (d, t), FS_SMALL, INK, "start", 600, box=520)
    # month ticks
    for mth in (4, 5, 6, 7):
        s_ = "2026-%02d-01" % mth
        x = xpos(s_)
        cv.o.append("<line x1='%.1f' y1='%d' x2='%.1f' y2='%d' stroke='%s'/>" % (x, yl - 6, x, yl + 6, MUTED))
        cv.label(x + 4, yl + 22, {4: "Apr", 5: "May", 6: "Jun", 7: "Jul"}[mth] if lang == "en" else {4: "апр", 5: "май", 6: "июн", 7: "июл"}[mth], FS_SMALL, MUTED)
    cv.label(24, 604, {"en": "DATES THE ARCHIVES RECORD (not to scale)", "ru": "ДАТЫ, ЗАПИСАННЫЕ АРХИВАМИ (не в масштабе)"}[lang], FS_KICKER, VIOLET, weight=700, box=600)
    bw = (W - 48 - 3 * 14) / 4
    for i, (d, t, f, n) in enumerate(ext):
        cv.box(24 + i * (bw + 14), 624, bw, d, [t], stroke=VIOLET, h=112, title_size=15, valign="top")
    foot(cv, {"en": "Upper-lane dates are taken from the cited reports; the FBI date is from a single-author recap.",
              "ru": "Даты верхней полосы взяты из указанных отчётов; дата ФБР из пересказа одного автора."}[lang], H - 14)
    return "\n".join(cv.o + ["</svg>\n"])


# --- ecosystem and claims found only in the graph --------------------------------------------
ECO = {
    "en": {"title": "Stated loop, siblings, and claims only in the graph", "sub": "Solid: in the README. Dashed: stated or graph-only, not shown", "tag": "ECOSYSTEM",
           "loop": ["Research", "Repository", "UAP course (in development)", "Engineering-education license", "Patron and investment income"],
           "loop_note": "README: the course belongs to the commercialization model; not live.",
           "sib": ("Sibling studies and patents", ["4 Hyperbolic Field studies and ASRP.art as repositories", "4 sibling patent applications listed as references", "No patent filing for this study (README)"]),
           "graph": ("Claimed in graph JSON only", ["DoE / Los Alamos first-reader event", "Stanford admin handoff", "NCI SBIR submission", "Cortical Labs negotiations",
                                                    "Boeing, about $40M a year, labelled illustrative"]),
           "graph_note": "Each is a node with a description and no source: no letter, reply or date in the corpus.",
           "legend": [("solid", GREEN, "written in the README"), ("dashed", AMBER, "claimed, not shown")],
           "desc": ("Three blocks. Top: the stated commercialization loop in the README as five connected boxes: research, repository, UAP course in development, "
                    "engineering-education license, patron and investment income; the course is not live. Bottom left: sibling studies and patents listed as ecosystem "
                    "references, with no patent filing for this study. Bottom right, dashed: claims that exist only in the graph JSON (DoE and Los Alamos first reader, "
                    "Stanford admin handoff, NCI SBIR submission, Cortical Labs negotiations, Boeing about 40 million dollars a year, labelled illustrative) with no letter, "
                    "reply or date in the corpus.")},
    "ru": {"title": "Контур, родственные работы, утверждения графа", "sub": "Сплошное: в README. Пунктир: заявлено или только в графе", "tag": "ЭКОСИСТЕМА",
           "loop": ["Исследование", "Репозиторий", "Курс по НАЯ (в разработке)", "Инженерная образовательная лицензия", "Доход от меценатов и инвестиций"],
           "loop_note": "README: курс часть модели коммерциализации; не запущен.",
           "sib": ("Родственные работы и патенты", ["4 исследования Hyperbolic Field и ASRP.art как репозитории", "4 заявки родственных патентов даны как ссылки", "Заявки по этому исследованию нет (README)"]),
           "graph": ("Заявлено только в JSON графа", ["Событие первого читателя DoE / Лос-Аламос", "Admin-передача Stanford", "Подача NCI SBIR", "Переговоры Cortical Labs",
                                                      "Boeing, около $40 млн в год, помечено иллюстративным"]),
           "graph_note": "Каждый это узел с описанием без источника: ни письма, ни ответа, ни даты в корпусе нет.",
           "legend": [("solid", GREEN, "написано в README"), ("dashed", AMBER, "заявлено, не показано")],
           "desc": ("Три блока. Сверху: заявленный в README контур коммерциализации из пяти связанных блоков: исследование, репозиторий, курс по НАЯ в разработке, "
                    "инженерная образовательная лицензия, доход от меценатов и инвестиций; курс не запущен. Внизу слева: родственные работы и патенты как ссылки "
                    "экосистемы, заявки по этому исследованию нет. Внизу справа, пунктиром: утверждения, существующие только в JSON графа (первый читатель DoE и "
                    "Лос-Аламос, admin-передача Stanford, подача NCI SBIR, переговоры Cortical Labs, Boeing около 40 млн долларов в год, помечено иллюстративным) "
                    "без письма, ответа или даты в корпусе.")},
}


def ecosystem(lang):
    c = ECO[lang]
    W, H = 1200, 640
    cv = Canvas(W, H, c["title"], c["desc"], c["title"], c["sub"], c["tag"])
    n = len(c["loop"])
    bw, gap = 200, 25
    y, h = 106, 86
    xs = [24 + i * (bw + gap) for i in range(n)]
    for i, (x, name) in enumerate(zip(xs, c["loop"])):
        col = AMBER if i in (2, 3, 4) else TEAL
        cv.box(x, y, bw, name, [], stroke=col, h=h, center=True, pad=10, title_size=15)
        if i:
            cv.arrow([(xs[i - 1] + bw + 2, y + h / 2), (x - 3, y + h / 2)], GREEN if i < 2 else AMBER, dashed=i >= 2, animate=False)
    cv.label(24, y + h + 28, c["loop_note"], FS_SMALL, MUTED, box=W - 48)
    cv.box(24, 252, 540, c["sib"][0], c["sib"][1], stroke=BLUE, h=140, valign="top", title_size=16)
    cv.box(600, 252, 576, c["graph"][0], c["graph"][1] + [c["graph_note"]], stroke=AMBER, h=210, valign="top", title_size=16)
    cv.legend(24, 546, [(k, col, t) for k, col, t in c["legend"]])
    foot(cv, {"en": "Source: README (loop, siblings), graph/uap_kumu.json (outreach nodes or-doe, or-stanford, or-nci, or-cortical; inst-boeing).",
              "ru": "Источник: README (контур, родственные), graph/uap_kumu.json (узлы or-doe, or-stanford, or-nci, or-cortical; inst-boeing)."}[lang], H - 14)
    return "\n".join(cv.o + ["</svg>\n"])


# --- icons -----------------------------------------------------------------------------------
def icon(col, body, title):
    return ("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\" width=\"64\" height=\"64\" role=\"img\">\n"
            "<title>%s</title>\n<desc>Navigation icon: %s.</desc>\n<rect x=\"2\" y=\"2\" width=\"60\" height=\"60\" rx=\"12\" fill=\"#101826\" "
            "stroke=\"%s\" stroke-width=\"3\"/>\n<g fill='none' stroke='%s' stroke-width='2.6' stroke-linecap='round' "
            "stroke-linejoin='round'>%s</g>\n</svg>\n" % (title, title, col, col, body))


ICONS = {
    "study": (TEAL, "<circle cx='32' cy='32' r='16'/><circle cx='32' cy='32' r='5'/><path d='M32 12v8M32 44v8M12 32h8M44 32h8'/>", "the study"),
    "tracks": (GOLD, "<rect x='13' y='14' width='16' height='16' rx='3'/><rect x='35' y='14' width='16' height='16' rx='3'/>"
                     "<rect x='13' y='36' width='38' height='14' rx='3'/><path d='M21 30v6M43 30v6'/>", "tracks"),
    "experiment": (AMBER, "<path d='M26 12h12M29 12v14L17 48a4 4 0 0 0 4 6h22a4 4 0 0 0 4-6L35 26V12'/><path d='M23 40h18'/>", "the experiment"),
    "evidence": (GOLD, "<circle cx='28' cy='28' r='13'/><path d='M38 38l12 12M23 28l4 4 7-8'/>", "claimed versus shown"),
    "ecosystem": (BLUE, "<circle cx='32' cy='32' r='6'/><circle cx='32' cy='14' r='4'/><circle cx='48' cy='41' r='4'/>"
                        "<circle cx='16' cy='41' r='4'/><path d='M32 26V18M37 35l8 4M27 35l-8 4'/>", "ecosystem and IP"),
    "navigation": (GREEN, "<path d='M20 14v36M20 22h10M20 34h10M20 46h10'/><rect x='30' y='17' width='20' height='10' rx='2'/>"
                          "<rect x='30' y='29' width='20' height='10' rx='2'/><rect x='30' y='41' width='20' height='10' rx='2'/>", "navigation"),
    "open": (VIOLET, "<circle cx='32' cy='32' r='18'/><path d='M26 27a6 6 0 1 1 9 5c-2 1-3 2-3 4M32 43v2'/>", "open questions"),
    "ethics": (AMBER, "<rect x='17' y='29' width='30' height='21' rx='4'/><path d='M23 29v-6a9 9 0 0 1 18 0v6M32 38v6'/>", "ethics and security"),
    "archive": (MUTED, "<rect x='12' y='14' width='40' height='11' rx='3'/><path d='M16 25v25h32V25M26 34h12'/>", "archive"),
}


def main():
    for lang in ("en", "ru"):
        write("guide/assets/banner/hero-banner.%s.svg" % lang, banner(lang))
        write("guide/assets/diagrams/tracks-map.%s.svg" % lang, trackmap(lang))
        write("guide/assets/diagrams/claimed-vs-shown.%s.svg" % lang, claimed(lang))
        write("guide/assets/diagrams/ecp-agreement.%s.svg" % lang, agreement(lang))
        write("guide/assets/diagrams/ecp-validation.%s.svg" % lang, validation(lang))
        write("guide/assets/diagrams/blinding-sequence.%s.svg" % lang, blinding(lang))
        write("guide/assets/diagrams/ai-control.%s.svg" % lang, aicontrol(lang))
        write("guide/assets/diagrams/timeline.%s.svg" % lang, timeline(lang))
        write("guide/assets/diagrams/ecosystem-claims.%s.svg" % lang, ecosystem(lang))
    for name, (col, body, title) in ICONS.items():
        write("guide/assets/icons/%s.svg" % name, icon(col, body, title))


if __name__ == "__main__":
    main()
