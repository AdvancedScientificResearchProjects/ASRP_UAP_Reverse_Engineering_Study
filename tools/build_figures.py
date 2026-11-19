#!/usr/bin/env python3
"""Builds guide/FIGURES.md and guide/FIGURES.ru.md: every figure file the repository tracks, one row per figure.

    python3 tools/build_figures.py

Rows are grouped by the folder that owns the figure; renders of the same diagram in a mirror folder
(mermaid/<x>/ next to <x>/diagrams/) are listed in one row. "What it shows" is the figure's own title taken
from its Mermaid source (.mmd) or its SVG <title>; when neither carries one, the first labels of the source are
quoted. Raw photographs (data/raw/control-images) are not figures and are counted, not listed. Figures that carry
names of percipients are withheld; figures that name private persons are linked, not described.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AREAS = [  # key, folders (owner first, mirrors after), EN title, RU title
    ("charts", ["charts/mermaid", "mermaid/charts-root", "charts"], "Track 1: ECP experiment (charts/)", "Трек 1: эксперимент ECP (charts/)"),
    ("bob-lazar", ["bob-lazar-archive/diagrams", "mermaid/bob-lazar"], "Track 2: Bob Lazar archive", "Трек 2: архив Боба Лазара"),
    ("chernobrov", ["chernobrov-archive/diagrams", "mermaid/chernobrov"], "Track 3: Chernobrov archive", "Трек 3: архив Черноброва"),
    ("dubna", ["dubna-element-115-analysis/diagrams", "mermaid/dubna-element-115"], "Track 4: Dubna / Element 115", "Трек 4: Дубна / элемент 115"),
    ("people", ["people-analysis/diagrams", "mermaid/people"], "Track 5: people analysis", "Трек 5: анализ людей"),
    ("osint", ["osint-intelligence-analysis/diagrams", "mermaid/osint-intelligence"], "Track 6: OSINT / intelligence analysis", "Трек 6: OSINT / анализ разведданных"),
    ("corp", ["corporate-economic-analysis/diagrams", "mermaid/corporate-economic"], "Track 7: corporate / economic analysis", "Трек 7: корпоративный / экономический анализ"),
    ("gershtein", ["gershtein-archive/diagrams", "mermaid/gershtein"], "Gershtein archive", "Архив Гершteina".replace("teina", "тейна")),
    ("pursue", ["war-gov-pursue-archive/diagrams", "mermaid/war-gov-pursue"], "War.gov PURSUE archive", "Архив War.gov PURSUE"),
]
WITHHELD_STEMS = {"retry_1"}
WITHHELD_FILES = {"charts/ecp_response_agreement_matrix.svg", "charts/ecp_reference_validation_matrix.svg"}
PRIVATE_PERSON_STEMS = {"fbi11_to_track7_employer_overlay", "affiliation_graph", "investigation_status", "timeline_2022_2026", "cardillo_gabriella_framework"}
REDRAWN = {  # stem -> new svg slug (EN/RU pair under guide/assets/diagrams)
    "root_1": "overview-pipeline", "root_3": "evidence-flow", "root_4": "ai-pipeline", "root_5": "timeline-flow",
    "detective_board": "detective-board", "validation_pipeline": "validation-pipeline", "institutional_cluster_map": "cluster-map",
    "lazar_s4_contractor_bridge": "s4-contractor-bridge", "cross_archive_links": "cross-archive-links", "uap_taxonomy": "uap-taxonomy", "dubna_lazar_amentum_llnl_fuel_loop": "fuel-loop",
}
SHOWN_LINK = {}
CYR = re.compile("[А-Яа-яЁё]")


def tracked():
    out = subprocess.check_output(["git", "-C", ROOT, "ls-files"], text=True).splitlines()
    return [f for f in out if re.search(r"\.(svg|png|jpe?g|mmd)$", f, re.I) and not f.startswith("guide/")]


def clean(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip(" \"'")


def pick(title, lang):
    parts = [p.strip() for p in re.split(r"\s+/\s+", title)]
    if len(parts) >= 2:
        ru = [p for p in parts if CYR.search(p)]
        en = [p for p in parts if not CYR.search(p)]
        if lang == "ru" and ru:
            return ru[0]
        if lang == "en" and en:
            return en[0]
    return title


def source_text(path):
    return open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read()


def describe(files, lang):
    for f in files:
        if f.endswith(".mmd"):
            t = source_text(f)
            m = re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M)
            if m:
                return pick(clean(m.group(1)), lang)
            m = re.search(r"^\s*title\s+(.+)$", t, re.M)
            if m:
                return pick(clean(m.group(1)), lang)
            m = re.search(r'^%% Source: README.md section "(.+?)"', t, re.M)
            if m:
                return pick(clean(m.group(1)), lang)
            found = []
            for m in re.finditer(r'\["?([^\]"]+)"?\]|\(\("?([^)"]+)', t):
                lines = (m.group(1) or m.group(2)).split("<br/>")
                en = next((tidy(l) for l in lines if not CYR.search(l) and len(tidy(l)) >= 4), "")
                ru = next((tidy(l) for l in lines if CYR.search(l)), "")
                v = (ru or en) if lang == "ru" else en
                if v and v not in found:
                    found.append(v)
            if found:
                return ("First boxes: " if lang == "en" else "Первые блоки: ") + "; ".join(found[:3])
    for f in files:
        if f.endswith(".svg"):
            t = source_text(f)
            m = re.search(r"<title[^>]*>([^<]+)</title>", t)
            if m and langpick(clean(m.group(1)), lang):
                return langpick(clean(m.group(1)), lang)
            texts = [clean(x) for x in re.findall(r"<text[^>]*>([^<]+)</text>", t)]
            texts = [x for x in texts if len(x) > 3]
            if texts:
                good = [x for x in (langpick(y, lang) for y in texts) if len(x) >= 6]
                if good:
                    return ("Labels in the figure: " if lang == "en" else "Подписи на рисунке: ") + "; ".join(good[:3])
    return ""


EMOJI = re.compile("[\U00010000-\U0010ffff\u2600-\u27bf\u2b00-\u2bff\ufe0f\u200d]")


def tidy(x):
    x = EMOJI.sub("", x)
    x = re.sub(r"\s+", " ", x).strip(" /·-—:;,")
    while x.endswith(")") and x.count(")") > x.count("("):
        x = x[:-1].strip()
    while x.startswith("(") and x.count("(") > x.count(")"):
        x = x[1:].strip()
    if x.count("(") > x.count(")"):
        x = x[: x.rindex("(")].strip(" /·-—:;,")
    return x


def langpick(label, lang):
    """One language of a (possibly bilingual) label; '' when the label has none in `lang`."""
    parts = [tidy(p) for p in re.split(r"\s+[/·]\s+", label)]
    parts = [p for p in parts if p]
    if len(parts) > 1:
        want = [p for p in parts if bool(CYR.search(p)) == (lang == "ru")]
        if want:
            return want[0]
    one = tidy(label)
    if lang == "en":
        return "" if CYR.search(one) else one
    return one if CYR.search(one) else ""


def onlylang(s, lang):
    out = [langpick(x, lang) for x in s.split("; ")]
    return "; ".join(x for x in out if len(x) >= 6)


def rel(f):
    return "../" + f


def build(lang):
    files = tracked()
    byfolder = {}
    for f in files:
        byfolder.setdefault(os.path.dirname(f), []).append(f)
    L = []
    en = lang == "en"
    H = {
        "title": "Figure gallery" if en else "Галерея рисунков",
        "intro": ("Every figure the repository tracks is reachable from the pages: the diagrams drawn for these pages are embedded in the guide, and every other figure is listed here, one row per figure, grouped by the folder that owns it. "
                  "Renders of the same diagram in a mirror folder (`mermaid/`) are listed in one row. The raw photographs in `data/raw/control-images/` are inputs, not figures, and are not listed."
                  if en else
                  "Каждый рисунок, который отслеживает репозиторий, достижим со страниц: схемы, нарисованные для этих страниц, встроены в руководство, все остальные перечислены здесь, по одной строке на рисунок, по папкам-владельцам. "
                  "Рендеры одной и той же диаграммы в зеркальной папке (`mermaid/`) собраны в одну строку. Исходные фотографии в `data/raw/control-images/` это входные данные, а не рисунки, и здесь не перечислены."),
        "cols": ("| Figure | What it shows | Files | Where shown |\n|---|---|---|---|" if en else "| Рисунок | Что показывает | Файлы | Где показан |\n|---|---|---|---|"),
        "withheld": "withheld: names of private persons (memory-policy)" if en else "скрыто: имена частных лиц (memory-policy)",
    }
    H["withheld"] = "withheld: names of private persons" if en else "скрыто: имена частных лиц"
    if en:
        L += ["**English | [Русский](FIGURES.ru.md)**", "", "[← UAP Reverse Engineering Study](../README.md) · [Guide index](README.md)", ""]
    else:
        L += ["**[English](FIGURES.md) | Русский**", "", "[← Исследование по реверс-инжинирингу НАЯ](../README.ru.md) · [Индекс руководства](README.ru.md)", ""]
    L += ["# " + H["title"], "", H["intro"], ""]
    n_rows = 0
    n_withheld = 0
    for key, folders, t_en, t_ru in AREAS:
        groups = {}
        for fol in folders:
            for f in byfolder.get(fol, []) + byfolder.get(fol + "/rendered", []):
                stem = os.path.splitext(os.path.basename(f))[0]
                if f in WITHHELD_FILES:
                    groups.setdefault(("W", os.path.basename(f)), []).append(f)
                else:
                    groups.setdefault(stem, []).append(f)
        if not groups:
            continue
        L += ["## " + (t_en if en else t_ru), "", H["cols"]]
        for stem in sorted(groups, key=lambda k: str(k)):
            fl = sorted(groups[stem])
            links = ", ".join("[`%s`](%s)" % (f, rel(f)) for f in fl if not f.endswith(".mmd")) if False else None
            if isinstance(stem, tuple):
                name = stem[1]
                L.append("| `%s` | %s | `%s` | %s |" % (name, H["withheld"], fl[0], ("matrices redrawn anonymously: ECP agreement and validation figures" if en else "матрицы перерисованы анонимно: рисунки согласованности и валидации ECP")))
                n_withheld += 1
                n_rows += 1
                continue
            if stem in WITHHELD_STEMS:
                L.append("| `%s` | %s | %s | %s |" % (stem, H["withheld"], "<br>".join("`%s`" % f for f in fl), ("redrawn without names: Session Blinding Sequence, `blinding-sequence` figure" if en else "перерисовано без имён: рисунок «Кто что слышал перед ответом» (`blinding-sequence`)")))
                n_withheld += 1
                n_rows += 1
                continue
            desc = describe(fl, lang)
            if stem in PRIVATE_PERSON_STEMS:
                desc = ("names individual persons; linked, not described on these pages" if en else "называет отдельных людей; ссылка без описания на этих страницах")
            if not desc:
                desc = "(the source gives no title)" if en else "(в источнике нет названия)"
            order = {".svg": 0, ".png": 1, ".mmd": 2, ".jpg": 1, ".jpeg": 1}
            fl.sort(key=lambda f: (order.get(os.path.splitext(f)[1], 3), f))
            links = []
            for f in fl:
                ext = os.path.splitext(f)[1][1:]
                links.append("[%s](%s)" % ((f if f.count("/") < 4 else f), rel(f)) if False else "[`%s`](%s)" % (f, rel(f)))
            where = "-"
            if stem in REDRAWN:
                slug = REDRAWN[stem]
                where = ("redrawn: [`%s`](assets/diagrams/%s.%s.svg)" % (slug, slug, lang))
            elif stem in SHOWN_LINK:
                where = "[%s](%s.%s)" % (SHOWN_LINK[stem], SHOWN_LINK[stem], "md" if en else "ru.md")
            elif stem == "protocol_ai_1" or stem == "protocol_ai_retry_1":
                where = "-"
            L.append("| `%s` | %s | %s | %s |" % (stem, desc.replace("|", "/"), "<br>".join(links), where))
            n_rows += 1
        L.append("")
    L += ["## " + ("Not listed" if en else "Не перечислено"), "",
          ("- `data/raw/control-images/`: 14 raw photographs used as inputs of the AI control test, see [Track 1](EXPERIMENT.md)." if en else
           "- `data/raw/control-images/`: 14 исходных фотографий, входные данные контрольного теста ИИ, см. [трек 1](EXPERIMENT.ru.md)."),
          ("- `data/raw/percipient-sketches/`: one sketch drawn by a percipient; it may not be reproduced outside the ECP study without consent, so it is not shown or described here." if en else
           "- `data/raw/percipient-sketches/`: один рисунок, сделанный перципиентом; его нельзя воспроизводить вне исследования ECP без согласия, поэтому он здесь не показан и не описан."),
          ""]
    return "\n".join(L), n_rows, n_withheld


def main():
    for lang, name in (("en", "guide/FIGURES.md"), ("ru", "guide/FIGURES.ru.md")):
        txt, n, w = build(lang)
        open(os.path.join(ROOT, name), "w", encoding="utf-8").write(txt)
        print("wrote", name, "rows", n, "withheld", w)


if __name__ == "__main__":
    main()
