#!/usr/bin/env python3
"""Folder tree for guide/NAVIGATION*.md, built from the real tree and the computed facts.

`render(lang, F)` walks the files git knows about (tracked or not ignored), checks that every path of the
spec exists, and aborts when a tracked top-level entry is missing from the spec, so the printed tree
cannot drift from the repository. Comments are in `en` / `ru`; `{key}` placeholders are facts.
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (path, English comment, Russian comment, children)
SPEC = [
    ("README.md", "front page (English)", "главная страница (английская)"),
    ("README.ru.md", "front page (Russian)", "главная страница (русская)"),
    ("guide/", "detail pages X.md + X.ru.md; assets/ = generated SVG", "страницы-детали X.md + X.ru.md; assets/ = сгенерированные SVG"),
    ("archive/", "the previous README, kept byte for byte", "прежний README, сохранён байт в байт"),
    ("tools/", "showcase tooling: facts, visuals, excerpts, no-loss check", "инструменты витрины: факты, визуалы, выдержки, проверка без потерь"),
    ("tests/", "regression gate for the showcase", "регрессионный гейт витрины"),
    ("analysis/", "Track 8 and Track 1 analysis at the root: synthesis, taxonomy, ECP validation", "анализ Трека 8 и Трека 1 в корне: синтез, таксономия, валидация КП", [
        ("analysis/cross-archive-synthesis.md", "Track 8: overlaps between Lazar, Chernobrov, Dubna", "Трек 8: пересечения Лазара, Черноброва, Дубны"),
        ("analysis/uap-taxonomy.md", "Track 8: three-category origin vocabulary", "Трек 8: словарь происхождения из трёх категорий"),
        ("analysis/external-podcasts.md", "Track 8: external podcasts and documentaries", "Трек 8: внешние подкасты и документалки"),
        ("analysis/cross_comparison.md", "Track 1: descriptive overlap of the responses", "Трек 1: описательное пересечение ответов"),
        ("analysis/ecp_validation_report.md", "Track 1: responses against the disclosed reference", "Трек 1: ответы против раскрытого референса"),
    ]),
    ("experiments/", "protocols: ECP, AI pipeline, corporate scan", "протоколы: КП, ИИ-конвейер, корпоративный скан"),
    ("reports/", "Track 1 reports", "отчёты Трека 1", [
        ("reports/percipient_reports/", "{percipient_reports} session reports (percipients not named on these pages)", "{percipient_reports} отчёта сеанса (перципиенты на этих страницах не названы)"),
        ("reports/ai_reports/", "{ai_reports} AI reports: CV pipeline, LLM visual, control test", "{ai_reports} ИИ-отчёта: CV-конвейер, LLM-визуал, контрольный тест"),
    ]),
    ("pipeline/", "Track 1 code: {pipeline_stages} stages (detect, segment, features, SigLIP2, anomaly, depth)", "код Трека 1: {pipeline_stages} стадий (детекция, сегментация, признаки, SigLIP2, аномалии, глубина)"),
    ("data/", "Track 1 data: {pipeline_outputs} stage outputs, control images, sketches inventory", "данные Трека 1: {pipeline_outputs} выходов стадий, контрольные изображения, опись зарисовок"),
    ("charts/", "Track 1 charts: two ECP matrices and Mermaid renders", "диаграммы Трека 1: две матрицы КП и рендеры Mermaid"),
    ("mermaid/", "Mermaid sources and renders of the archive tracks ({mermaid_folders} folders)", "исходники и рендеры Mermaid треков-архивов ({mermaid_folders} папок)"),
    ("bob-lazar-archive/", "Track 2: {lazar_transcripts} transcripts, analysis, catalog", "Трек 2: {lazar_transcripts} транскриптов, анализ, каталог"),
    ("chernobrov-archive/", "Track 3: {chernobrov_transcripts} transcripts, analysis, books", "Трек 3: {chernobrov_transcripts} транскриптов, анализ, книги"),
    ("dubna-element-115-analysis/", "Track 4: JINR interview, claims, {t4_diagrams} diagrams", "Трек 4: интервью ОИЯИ, утверждения, {t4_diagrams} схем"),
    ("osint-intelligence-analysis/", "Track 5: method layer, {t5_md} pages", "Трек 5: методологический слой, {t5_md} страниц"),
    ("people-analysis/", "Track 6: {people_files} public-source profiles", "Трек 6: {people_files} профилей по открытым источникам"),
    ("corporate-economic-analysis/", "Track 7: companies, analysis, theoretical foundations", "Трек 7: компании, анализ, теоретические основы"),
    ("uap-scientific-publications/", "Track 9: {t9_md} pages of literature catalog", "Трек 9: {t9_md} страниц каталога литературы"),
    ("gershtein-archive/", "Track 10: {gershtein_transcripts} transcripts, articles, books", "Трек 10: {gershtein_transcripts} транскриптов, статьи, книги"),
    ("war-gov-pursue-archive/", "Track 11: {pursue_cards} cards, {pursue_topical} topical files, MASTER claims", "Трек 11: {pursue_cards} карточек, {pursue_topical} тематических файлов, MASTER"),
    ("graph/", "knowledge graph: {graph_nodes} nodes, {graph_edges} links", "граф знаний: {graph_nodes_ru}, {graph_edges_ru}", [
        ("graph/README.md", "how to build and view (its own numbers are stale)", "как собрать и посмотреть (собственные цифры устарели)"),
        ("graph/build_blueprint.py", "builds the JSON from fragments", "собирает JSON из фрагментов"),
        ("graph/fragments/", "per-track entity extractions", "поэтрековые извлечения сущностей"),
        ("graph/uap_kumu.json", "generated graph", "сгенерированный граф"),
        ("graph/preview.html", "browser viewer", "браузерный просмотр"),
        ("graph/REFERENCES-LAYER.md", "references and campaign layer: sources, claims, experiments (separate builder and viewer)", "слой ссылок и кампании: источники, утверждения, эксперименты (отдельный сборщик и просмотр)"),
    ]),
    ("references/", "literature base: sources.json, bibliography.bib, reading notes", "база литературы: sources.json, bibliography.bib, заметки о прочитанном"),
    ("scripts/", "fetch_literature.py: downloads open-access PDFs into references/pdf/ (not tracked)", "fetch_literature.py: скачивает PDF открытого доступа в references/pdf/ (не отслеживается)"),
    ("docs/", "placeholder (empty)", "заглушка (пусто)"),
    ("hardware/", "placeholder (empty)", "заглушка (пусто)"),
]
IGNORED_TOP = {".git", ".gitignore", ".gitattributes", ".DS_Store"}


def tracked():
    out = subprocess.run(["git", "ls-files", "-z", "-co", "--exclude-standard"], capture_output=True, text=True,
                         cwd=ROOT).stdout.split("\0")
    return [x for x in out if x]


def render(lang, F):
    files = tracked()
    tops = {x.split("/")[0] for x in files}
    spec_tops = {e[0].rstrip("/").split("/")[0] for e in SPEC}
    missing = sorted(t for t in tops - spec_tops if t not in IGNORED_TOP)
    if missing:
        raise SystemExit("tools/tree.py: tracked top-level entries missing from SPEC: %s" % missing)
    col = 1 if lang == "en" else 2
    rows = []

    def exists(path):
        q = path.rstrip("/")
        return any(f == q or f.startswith(q + "/") for f in files) or os.path.exists(os.path.join(ROOT, q))

    def emit(entries, prefix, top):
        for i, e in enumerate(entries):
            last = i == len(entries) - 1
            if not exists(e[0]):
                raise SystemExit("tools/tree.py: path in SPEC does not exist: %s" % e[0])
            name = e[0] if top else e[0].rstrip("/").split("/")[-1] + ("/" if e[0].endswith("/") else "")
            rows.append((prefix + ("└── " if last else "├── "), name, e[col].format(**F)))
            if len(e) > 3 and e[3]:
                emit(e[3], prefix + ("    " if last else "│   "), False)

    rows.append(("", "ASRP_UAP_Reverse_Engineering_Study/", ""))
    emit(SPEC, "", True)
    width = max(len(a) + len(b) for a, b, c in rows if c) + 2
    out = []
    for a, b, c in rows:
        out.append((a + b).ljust(width) + "# " + c if c else a + b)
    return "\n".join(out)
