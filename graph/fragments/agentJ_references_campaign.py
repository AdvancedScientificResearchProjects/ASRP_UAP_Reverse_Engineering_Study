# ════════════════════════════════════════════════════════════════════
# REFERENCES AND CAMPAIGN LAYER — external sources, claims, campaign
# ════════════════════════════════════════════════════════════════════
# exec()'d inside build_references_layer.py — E(), C() and P() are already defined.
# Added 20 Nov 2026. Source nodes are NOT typed by hand: they are read from
# ../references/sources.json (one node per record, id = record["graph_id"]).
# Edit the literature base there, then rebuild. Every claim below names where
# it is stated (file:line or source) and what kind of basis it has.
#
# Edge vocabulary of this layer:
#   cites             ASRP folder or campaign -> source
#   same_work_as      new source node -> older source node of the base graph
#   supports          source -> claim or fact   (the source says it)
#   contradicts       source -> claim or fact   (the source says otherwise)
#   cited_for         source -> claim   (cited for it; verdict overstated / misreported / not checked)
#   relevant_to       source -> claim   (context; does not settle it)
#   states            person, source or ASRP folder -> claim
#   restates          claim -> fact of the base graph
#   measured_in       claim -> experiment
#   replicates        experiment -> experiment
#   tests / funds     planned experiment -> claim ; campaign -> planned experiment
#   used_by_campaign  anything -> campaign
#
# Claim nodes carry: status (proven / stated / open / refuted), basis
# (measurement / official count / testimony / ASRP text / model), stated_in.
# Testimony is never given status "proven".
# No private individuals are named: session participants appear as a role.
# Memory ids (asrp.memory/brain/entities.yaml) are attached with P(...).
import json as _json

_REPO = Path(__file__).parent.parent
_SRC = _json.loads((_REPO / "references" / "sources.json").read_text(encoding="utf-8"))["sources"]
_BY = {r["id"]: r for r in _SRC}
def _g(i): return _BY[i]["graph_id"]

# ── memory ids for nodes that already exist in the base graph ────────
P("pj-uap", memory_id="uap-reverse-engineering")
P("p-lazar", memory_id="bob-lazar")
P("inst-jinr", memory_id="jinr-dubna")
P("p-chernobrov", memory_id="vadim-chernobrov")
P("src-asrp-media-2025", memory_id="asrp-media-dubna-interview-2025")

# ── ASRP folders that cite outside sources (one cluster node per folder) ──
_FOLD = [("cluster-dubna-115-archive", "dubna-element-115-analysis/", "Dubna / Element 115 archive (Track 4)", "Архив «Дубна / Элемент 115» (Трек 4)"),
         ("cluster-lazar-archive", "bob-lazar-archive/", "Bob Lazar interview archive (Track 2)", "Архив интервью Боба Лазара (Трек 2)")]
for _id, _path, _en, _ru in _FOLD:
    E(_id, _en, "cluster", label_ru=_ru,
      description="Folder %s of the study repository. Node added so that 'cites' edges have a starting point." % _path,
      description_ru="Папка %s репозитория исследования. Узел добавлен как начало рёбер «cites»." % _path)
    C("pj-uap", _id, ctype="has_track")
_CITER = {"dubna-element-115-analysis/": "cluster-dubna-115-archive", "bob-lazar-archive/": "cluster-lazar-archive",
          "uap-scientific-publications/": "cluster-uap-publications", "war-gov-pursue-archive/": "cluster-pursue-release-01"}

# ── CAMPAIGN (draft in the crowdfunding workspace; nothing is launched) ──
E("campaign-uap-archive-book", "UAP archive book / One Fragment, One Lab Report (Kickstarter draft)", "campaign",
  label_ru="Книга-архив UAP / One Fragment, One Lab Report (черновик Kickstarter)",
  description="Planned crowdfunding campaign with two possible forms: a printed archive book built from the PURSUE records, and the funding of one outside laboratory report on the fragment UAP-FRAG-001, to be printed whatever it says. Draft only: not submitted, not launched (20 Nov 2026).",
  description_ru="Планируемая краудфандинговая кампания в двух возможных формах: печатная книга-архив по записям PURSUE и оплата одного отчёта внешней лаборатории о фрагменте UAP-FRAG-001, который будет напечатан при любом результате. Только черновик: не подана, не запущена (20 ноября 2026 г.).",
  status="draft")
for _n in ("pj-uap", "phen-uap-frag-001", "cluster-pursue-release-01", "cluster-pursue-release-02", "f-ai-ctrl-within-fossil-range",
           "f-ecp-blinding-compromised", "src-ai-ctrl-report", "src-ecp-session-2026"):
    C(_n, "campaign-uap-archive-book", ctype="used_by_campaign")

# ── EXPERIMENTS, DATASETS, ROLES ─────────────────────────────────────
_EV = [("ev-exp-dubna-2003", "Dubna experiment, 2003: 48Ca on 243Am, four decay chains", "Эксперимент в Дубне, 2003: 48Ca на 243Am, четыре цепочки распада", "2003",
        "U400 cyclotron and gas-filled recoil separator, JINR, with Livermore co-authors. Three chains of 288-115 and one of 287-115. Published 2004.",
        "Циклотрон У-400 и газонаполненный сепаратор, ОИЯИ, с соавторами из Ливермора. Три цепочки 288-115 и одна 287-115. Опубликовано в 2004 г.", None),
       ("ev-exp-dubna-2010-2012", "Dubna re-run, 1 Nov 2010 to 26 Feb 2012: 28 + 4 + 1 chains", "Повтор в Дубне, 1.11.2010 – 26.02.2012: 28 + 4 + 1 цепочек", "2010-11-01",
        "Same reaction at several energies: 28 chains of 288-115, four events of 289-115, one chain of 287-115.",
        "Та же реакция при нескольких энергиях: 28 цепочек 288-115, четыре события 289-115, одна цепочка 287-115.", "ev-exp-dubna-2003"),
       ("ev-exp-gsi-tasca", "GSI Darmstadt experiment led by Lund: thirty chains (published 2013)", "Эксперимент в GSI (Дармштадт) под руководством Лунда: тридцать цепочек (опубл. 2013)", "2013",
        "Independent laboratory, same reaction, with X-ray and gamma coincidence spectroscopy. Thirty chains 'consistent with previous assignments'.",
        "Независимая лаборатория, та же реакция, со спектроскопией совпадений рентгеновских и гамма-квантов. Тридцать цепочек, «согласующихся с прежним отнесением».", "ev-exp-dubna-2003"),
       ("ev-exp-lbnl-2015", "Berkeley experiment: 46 chains (published 2015)", "Эксперимент в Беркли: 46 цепочек (опубл. 2015)", "2015",
        "Second independent laboratory. States that X-rays did not allow a definitive identification of the atomic number.",
        "Вторая независимая лаборатория. Указано, что рентгеновские линии не позволили окончательно определить атомный номер.", "ev-exp-dubna-2003"),
       ("ev-exp-lbnl-fiona", "Berkeley FIONA: direct mass number of 288Mc, two events (published 2018)", "Беркли, FIONA: прямое измерение массового числа 288Mc, два события (опубл. 2018)", "2018",
        "First direct measurement of the mass number of a superheavy nucleus; confirms the earlier indirect assignment.",
        "Первое прямое измерение массового числа сверхтяжёлого ядра; подтверждает прежнее косвенное отнесение.", "ev-exp-dubna-2003"),
       ("ev-exp-shef-first", "Super Heavy Element Factory, first experiment: 55 + 6 chains (published 2022)", "Фабрика сверхтяжёлых элементов, первый опыт: 55 + 6 цепочек (опубл. 2022)", "2022",
        "55 chains of 288Mc and 6 chains assigned to 289Mc. The second experiment (also published 2022) found the new isotope 286Mc.",
        "55 цепочек 288Mc и 6 цепочек, отнесённых к 289Mc. Во втором опыте (тоже опубл. 2022) найден новый изотоп 286Mc.", "ev-exp-dubna-2003"),
       ("ev-exp-ubatuba-2017-18", "Ubatuba sample: two laboratories, HR-ICP-MS, 2017 and 2018", "Образец из Убатубы: две лаборатории, HR-ICP-MS, 2017 и 2018", "2017",
        "One sample measured by two commercial laboratories. Magnesium isotope ratios within terrestrial limits; trace elements inconclusive; the laboratories disagreed.",
        "Один образец измерен двумя коммерческими лабораториями. Изотопные отношения магния в земных пределах; по следовым элементам вывода нет; лаборатории разошлись.", None),
       ("ev-exp-lab-report-planned", "Planned: one outside laboratory report on UAP-FRAG-001 (not started)", "План: один отчёт внешней лаборатории о UAP-FRAG-001 (не начат)", None,
        "The funded work of the campaign. Named methods in the draft: examination by a palaeontologist, X-ray fluorescence, electron microscopy with element analysis, X-ray diffraction, a long gamma count against an empty chamber, a CT scan. No laboratory chosen, no protocol written (20 Nov 2026).",
        "Работа, оплачиваемая кампанией. Методы из черновика: осмотр палеонтологом, рентгенофлуоресцентный анализ, электронная микроскопия с элементным анализом, рентгеновская дифракция, длительный гамма-счёт с пустой камерой, КТ. Лаборатория не выбрана, протокол не написан (20 ноября 2026 г.).", None)]
for _id, _en, _ru, _date, _d, _dru, _rep in _EV:
    _kw = {"date": _date} if _date else {"status": "planned"}
    E(_id, _en, "event", label_ru=_ru, description=_d, description_ru=_dru, kind="experiment", **_kw)
    if _rep:
        C(_id, _rep, ctype="replicates")
C("inst-jinr", "ev-exp-dubna-2003", ctype="conducted")
C("inst-jinr", "ev-exp-dubna-2010-2012", ctype="conducted")
C("inst-jinr", "ev-exp-shef-first", ctype="conducted")
C("inst-llnl", "ev-exp-dubna-2003", ctype="took-part-in")
C("inst-gsi", "ev-exp-gsi-tasca", ctype="conducted")
C("campaign-uap-archive-book", "ev-exp-lab-report-planned", ctype="funds")
C("ev-exp-lab-report-planned", "phen-uap-frag-001", ctype="examines")
for _s, _e in (("oganessian2004", "ev-exp-dubna-2003"), ("oganessian2005", "ev-exp-dubna-2003"), ("oganessian2012", "ev-exp-dubna-2010-2012"),
               ("oganessian2013", "ev-exp-dubna-2010-2012"), ("rudolph2013", "ev-exp-gsi-tasca"), ("gates2015", "ev-exp-lbnl-2015"),
               ("gates2018", "ev-exp-lbnl-fiona"), ("oganessian2022a", "ev-exp-shef-first"), ("oganessian2022b", "ev-exp-shef-first"),
               ("powell2022", "ev-exp-ubatuba-2017-18")):
    C(_e, _g(_s), ctype="reported_in")

E("ds-control-test-results", "Control-test scores (data/processed/control-test-results.json)", "dataset",
  label_ru="Оценки контрольного теста (data/processed/control-test-results.json)",
  description="Image-classifier scores for the fragment photograph and the control images, 9 April 2026. The only numeric dataset about the fragment; it describes pictures, not the object.",
  description_ru="Оценки классификатора изображений для фотографии фрагмента и контрольных изображений, 9 апреля 2026 г. Единственный числовой набор данных о фрагменте; описывает изображения, а не сам объект.")
C("ev-ai-ctrl-test", "ds-control-test-results", ctype="produced")
C("ds-control-test-results", "campaign-uap-archive-book", ctype="used_by_campaign")
E("ds-nuclear-data-evaluations", "Evaluated half-lives (NUBASE2020, ENSDF)", "dataset",
  label_ru="Оценённые периоды полураспада (NUBASE2020, ENSDF)",
  description="Evaluated tables of measured half-lives. Moscovium: 286Mc 20 ms (2022 paper), 287Mc 37 ms, 288Mc about 0.17 s, 289Mc about 0.3 s, 290Mc about 0.65 s. Neighbours: 286Nh about 10 s, 289Fl about 2 s.",
  description_ru="Оценённые таблицы измеренных периодов полураспада. Московий: 286Mc 20 мс (статья 2022 г.), 287Mc 37 мс, 288Mc около 0,17 с, 289Mc около 0,3 с, 290Mc около 0,65 с. Соседи: 286Nh около 10 с, 289Fl около 2 с.")
for _s in ("nubase2020", "iaea_livechart", "morse2022", "singh2019"):
    C(_g(_s), "ds-nuclear-data-evaluations", ctype="publishes")
E("role-session-participants", "Participants of the 4 April 2026 session (role, no names)", "cluster",
  label_ru="Участники сеанса 4 апреля 2026 г. (роль, без имён)",
  description="Three people described the object in one group session. They are private individuals and appear here only as a role.",
  description_ru="Три человека описывали объект в одном групповом сеансе. Это частные лица; здесь они представлены только как роль.")
C("role-session-participants", "ev-ecp", ctype="participated-in")
E("role-outside-laboratory", "Outside laboratory (role; not chosen)", "cluster",
  label_ru="Внешняя лаборатория (роль; не выбрана)",
  description="The laboratory that would examine the fragment and write the report. Not chosen. It should not know the story of the object before it reports.",
  description_ru="Лаборатория, которая исследует фрагмент и напишет отчёт. Не выбрана. До выдачи отчёта она не должна знать историю объекта.")
C("role-outside-laboratory", "ev-exp-lab-report-planned", ctype="conducts", status="planned")

# ── EXTERNAL SOURCES (generated from references/sources.json) ────────
for _r in _SRC:
    _a = _r["authors"]
    _fam = _a[0].split(",")[0] if ("," in _a[0] and len(_a[0]) < 40) else _a[0].split(" (")[0]
    _n = len([x for x in _a if not x.startswith("et al")])
    _who = _fam + (" et al." if (len(_a) > 2 or any(x.startswith("et al") for x in _a)) else (" & " + _a[1].split(",")[0] if _n == 2 else ""))
    _lab = "%s (%s) %s" % (_who, _r["year"], _r["title"][:58] + ("…" if len(_r["title"]) > 58 else ""))
    _loc = " ".join(x for x in [_r["venue"] or "", _r["volume"] or "", (": " + _r["pages"]) if _r["pages"] else ""] if x)
    _idl = ("DOI %s" % _r["doi"]) if _r["doi"] else (_r["url"] or "no identifier")
    _v = _r["verdict"] or "no reading note"
    _note = _r["reading_note"] or "none"
    E(_r["graph_id"], _lab, "source", label_ru=_lab,
      description="%s. %s. %s Verified: %s. Verdict: %s. Note: %s." % (_loc, _idl, _r["why_en"], "yes" if _r["verified"] else "NO", _v, _note),
      description_ru="%s. %s. %s Проверено: %s. Вердикт: %s. Заметка: %s." % (_loc, _idl, _r["why_ru"], "да" if _r["verified"] else "НЕТ", _v, _note),
      doi=_r["doi"], url=_r["url"], note=_r["reading_note"], verdict=_r["verdict"], verified=_r["verified"],
      track=_r["track"], theme=_r["theme"], evidence_level=_r["evidence_level"], source_id=_r["id"], kind=_r["kind"])
    if _r["legacy_graph_id"]:
        C(_r["graph_id"], _r["legacy_graph_id"], ctype="same_work_as")
    _done = set()
    for _c in _r["cited_in"]:
        for _k, _p in _CITER.items():
            if _c.startswith(_k) and _p not in _done:
                C(_p, _r["graph_id"], ctype="cites", where=_c)
                _done.add(_p)
    for _camp in _r["used_by_campaign"]:
        C(_r["graph_id"], _camp, ctype="used_by_campaign", how="context for the page; not yet named on it")

# ── CLAIMS ───────────────────────────────────────────────────────────
# (id, EN label, RU label, status, basis, stated_in, EN description, RU description, stated-by nodes)
_CL = [
 ("claim-mc-halflives-measured", "Every measured isotope of element 115 lives less than about one second",
  "Все измеренные изотопы 115-го элемента живут меньше примерно одной секунды", "proven", "measurement",
  "references/notes/nubase2020.md",
  "Five isotopes are known, 286Mc to 290Mc. Evaluated half-lives run from 20 ms (286Mc) to about 0.65 s (290Mc, ENSDF; 0.84 s in NUBASE2020). Each value rests on a few atoms to a few dozen.",
  "Известно пять изотопов, 286Mc–290Mc. Оценённые периоды полураспада — от 20 мс (286Mc) до примерно 0,65 с (290Mc, ENSDF; 0,84 с в NUBASE2020). Каждое значение основано на нескольких атомах или нескольких десятках.", []),
 ("claim-115-stable-isotope-fuel", "A stable isotope of element 115 exists and was used as fuel",
  "Существует стабильный изотоп 115-го элемента, и он использовался как топливо", "refuted", "testimony",
  "bob-lazar-archive/analysis/MASTER_technical_claims.md:144",
  "Single-witness testimony, first broadcast in 1989 and repeated since. No sample, no measurement. As far as measurement reaches it is contradicted: no isotope of element 115 lives longer than about a second. A stable isotope that has never been made cannot be excluded by measurement, and no published model read here predicts one.",
  "Свидетельство одного человека, впервые в эфире в 1989 г. и повторяемое позже. Образца нет, измерений нет. В пределах измеренного опровергнуто: ни один изотоп 115-го не живёт дольше примерно секунды. Никогда не полученный стабильный изотоп измерением исключить нельзя, но ни одна прочитанная здесь опубликованная модель его не предсказывает.",
  ["p-lazar", "src-klas-1989b"]),
 ("claim-115-500-pounds", "About 500 pounds of element 115 were held at the site", "На объекте хранилось около 500 фунтов 115-го элемента",
  "stated", "testimony", "bob-lazar-archive/analysis/MASTER_technical_claims.md:174",
  "Testimony. The published production record is single atoms: 61 decay chains in the first experiment of the purpose-built factory.",
  "Свидетельство. Опубликованный результат производства — единичные атомы: 61 цепочка распада в первом опыте специально построенной фабрики.",
  ["p-lazar", "src-klas-1989b"]),
 ("claim-115-prediction-nontrivial", "Naming element 115 in 1989 was a non-trivial prediction",
  "Назвать 115-й элемент в 1989 г. было нетривиальным предсказанием", "open", "ASRP text",
  "dubna-element-115-analysis/analysis/lazar-dubna-connection.md:55",
  "ASRP's own wording. Overstated: long-lived superheavy elements near Z = 114 had been predicted in print since 1966, and element 115 had a systematic name from 1979.",
  "Формулировка самого ASRP. Преувеличено: долгоживущие сверхтяжёлые элементы вблизи Z = 114 предсказывались в печати с 1966 г., а у 115-го с 1979 г. было систематическое название.",
  ["cluster-dubna-115-archive"]),
 ("claim-113-118-none-over-1s", "No isotope of elements 113 to 118 exceeds about one second",
  "Ни один изотоп элементов 113–118 не живёт дольше примерно одной секунды", "refuted", "ASRP text",
  "dubna-element-115-analysis/analysis/MASTER_claims.md:65",
  "ASRP's own wording. True for element 115, false for the range: 286Nh about 10 s and 289Fl about 2 s in the evaluated tables.",
  "Формулировка самого ASRP. Верно для 115-го, неверно для диапазона: по оценённым таблицам 286Nh около 10 с, 289Fl около 2 с.",
  ["cluster-dubna-115-archive"]),
 ("claim-iupac-accepted-after-gsi", "IUPAC accepted element 115 following the 2013 GSI and Lund replication",
  "IUPAC признал 115-й элемент вслед за повторением в GSI и Лунде в 2013 г.", "open", "ASRP text",
  "dubna-element-115-analysis/analysis/jinr-facts-and-history.md:93",
  "ASRP's own wording. True as a sequence in time; the causal reading is not supported by the IUPAC texts read, which credit the Dubna, Livermore and Oak Ridge collaboration. The body of the IUPAC report was not read.",
  "Формулировка самого ASRP. Как последовательность во времени верно; причинная связь не подтверждается прочитанными текстами IUPAC, которые отдают приоритет коллаборации Дубны, Ливермора и Ок-Риджа. Основной текст отчёта IUPAC не прочитан.",
  ["cluster-dubna-115-archive"]),
 ("claim-115-credit-jinr-llnl", "Discovery of element 115 is credited to JINR and LLNL", "Открытие 115-го элемента приписано ОИЯИ и LLNL",
  "refuted", "ASRP text", "dubna-element-115-analysis/analysis/MASTER_claims.md:44",
  "ASRP's own wording. IUPAC names three institutions for elements 115 and 117: JINR, LLNL and Oak Ridge National Laboratory.",
  "Формулировка самого ASRP. IUPAC называет для элементов 115 и 117 три организации: ОИЯИ, LLNL и Ок-Риджскую национальную лабораторию.",
  ["cluster-dubna-115-archive"]),
 ("claim-shef-70-atoms-40-days", "The factory made about 70 atoms of element 115 in 40 days",
  "Фабрика получила около 70 атомов 115-го элемента за 40 дней", "stated", "testimony",
  "dubna-element-115-analysis/analysis/superheavy-factory-2020.md:37",
  "Said by an unnamed institute representative in a 2021 interview. The published paper on the first experiment reports 61 chains; the duration is not in its abstract.",
  "Сказано неназванным представителем института в интервью 2021 г. Опубликованная статья о первом опыте сообщает о 61 цепочке; длительности в аннотации нет.",
  ["src-asrp-media-2025"]),
 ("claim-knapp-could-not-rule-out", "Three physicists 'could not rule out a stabilized version of element 115'",
  "Трое физиков «не смогли исключить стабилизированную версию 115-го элемента»", "stated", "testimony",
  "dubna-element-115-analysis/analysis/lazar-dubna-connection.md:61",
  "Second-hand testimony in a 2018 film; the physicists are not named and no publication is given. Cannot be checked.",
  "Свидетельство из вторых рук в фильме 2018 г.; физики не названы, публикация не указана. Проверить нельзя.",
  ["p-knapp", "src-bl18"]),
 ("claim-island-long-lived-not-stable", "Theory predicts long-lived, not stable, nuclei near Z = 114, N = 184",
  "Теория предсказывает вблизи Z = 114, N = 184 долгоживущие, но не стабильные ядра", "stated", "model",
  "references/notes/giuliani2019.md",
  "Early calculations (1966) gave 'lifetimes ranging from minutes to millions of years'; later models revised them. One model's longest-lived nuclei are copernicium isotopes at about 100 years. No known isotope is near N = 184.",
  "Ранние расчёты (1966 г.) давали «времена жизни от минут до миллионов лет»; позднейшие модели их пересмотрели. В одной из моделей самые долгоживущие ядра — изотопы коперниция, около 100 лет. Ни один известный изотоп не близок к N = 184.", []),
 ("claim-odni-144-reports", "ODNI 2021: 144 reports, one identified, the others unexplained", "ODNI 2021: 144 сообщения, одно объяснено, остальные нет",
  "proven", "official count", "references/notes/odni2021.md",
  "A count stated by the issuing body (p. 4). It is a count of reports, not of objects, and 'unexplained' is the report's word for lack of data.",
  "Подсчёт, приведённый самим ведомством (с. 4). Это число сообщений, а не объектов, и «не объяснено» в отчёте означает нехватку данных.", []),
 ("claim-nasa-no-et-reason", "NASA 2023: 'no reason to conclude that existing UAP reports have an extraterrestrial source'",
  "NASA 2023: «нет оснований заключать, что имеющиеся сообщения об UAP имеют внеземной источник»", "proven", "official statement",
  "references/notes/nasa2023.md",
  "Statement of the study team (PDF p. 35), together with its list of what is wrong with the data: calibration, single measurements, missing metadata, no baselines.",
  "Заявление исследовательской группы (с. 35 PDF) вместе с перечнем недостатков данных: калибровка, единичные измерения, нет метаданных, нет базовых измерений.", []),
 ("claim-aaro-quoted-finding", "AARO 2024 sentence printed in quotation marks in the repository",
  "Фраза AARO 2024, напечатанная в репозитории в кавычках", "open", "ASRP text",
  "uap-scientific-publications/analysis/government-reports-uap.md:61",
  "The repository quotes 'AARO found no verifiable evidence of recovered extraterrestrial technology or active reverse-engineering programmes' without a page. The report could not be fetched; the wording is unchecked.",
  "Репозиторий приводит в кавычках фразу без указания страницы. Отчёт получить не удалось; формулировка не проверена.",
  ["cluster-uap-publications"]),
 ("claim-ubatuba-mg-terrestrial", "Ubatuba sample: magnesium isotope ratios within terrestrial limits; trace elements inconclusive",
  "Образец из Убатубы: изотопные отношения магния в земных пределах; по следовым элементам вывода нет", "proven", "measurement",
  "references/notes/powell2022.md",
  "Result of the 2017-2018 tests as published in 2022. One sample, two laboratories that disagreed with each other, provenance not established.",
  "Результат испытаний 2017–2018 гг., опубликованный в 2022 г. Один образец, две разошедшиеся между собой лаборатории, происхождение не установлено.", []),
 ("claim-frag-no-lab-measurement", "No laboratory measurement of UAP-FRAG-001 exists", "Лабораторных измерений UAP-FRAG-001 не существует",
  "proven", "ASRP text", "ASRP_Crowdfunding_Research/campaigns/uap-archive-book/assets/sample/chapter-11-our-own-test.md:11",
  "The study's own statement about its record: one session, three model reports on a picture, 'No laboratory measurement of any kind'.",
  "Собственное утверждение исследования о своих материалах: один сеанс, три отчёта моделей по изображению, «никаких лабораторных измерений».",
  ["campaign-uap-archive-book"]),
 ("claim-frag-no-chain-of-custody", "The fragment has no chain of custody", "У фрагмента нет цепочки хранения",
  "proven", "ASRP text", "ASRP_Crowdfunding_Research/campaigns/uap-archive-book/story-and-film/story-v1.md:40",
  "Stated in the campaign draft. A custody record can start only when someone starts writing it; the earlier history stays undocumented.",
  "Сказано в черновике кампании. Запись о хранении начинается только с момента, когда её начали вести; предыдущая история остаётся недокументированной.",
  ["campaign-uap-archive-book"]),
 ("claim-frag-photo-provenance", "Provenance of the fragment photograph is not documented", "Происхождение фотографии фрагмента не задокументировано",
  "open", "ASRP text", "ASRP_Crowdfunding_Research/campaigns/uap-archive-book/assets/sample/chapter-11-our-own-test.md:67",
  "Known gap: the input file the software expects is missing from the repository, and who took the remaining picture, when and with what, is not recorded. Must be resolved or stated before the picture is shown on a campaign page.",
  "Известный пробел: входного файла, ожидаемого программой, в репозитории нет, а кто, когда и чем сделал оставшийся снимок, не записано. До показа снимка на странице кампании это нужно выяснить или прямо указать.",
  ["campaign-uap-archive-book"]),
 ("claim-cb-time-shift", "A device slowed time by about 3 % over 30 minutes (2001)", "Установка замедлила время примерно на 3 % за 30 минут (2001)",
  "stated", "testimony", "chernobrov-archive/analysis/MASTER_chernobrov_claims.md",
  "The author's own account in lectures and books. No independent measurement, no peer-reviewed reproduction, patent application discontinued.",
  "Собственный рассказ автора в лекциях и книгах. Независимых измерений нет, рецензированного воспроизведения нет, патентная заявка прекращена.",
  ["p-chernobrov"]),
 ("claim-mg-petrozavodsk-launch", "The 1977 Petrozavodsk phenomenon was the launch of Kosmos-955", "Петрозаводский феномен 1977 г. — запуск «Космоса-955»",
  "stated", "published attribution", "gershtein-archive/analysis/MASTER_gershtein_claims.md",
  "An attribution made by a published author in lectures and books; recorded as his statement. No outside source was checked for it in this pass.",
  "Объяснение, данное публикующимся автором в лекциях и книгах; записано как его утверждение. Внешние источники в этом проходе не проверялись.",
  ["p-gershtein"]),
 ("claim-pursue-225-records", "PURSUE releases 01 and 02 hold 225 records from seven agencies", "Релизы PURSUE 01 и 02 содержат 225 записей семи ведомств",
  "stated", "ASRP count of an official release", "war-gov-pursue-archive/README.md:4",
  "The repository's count, backed by its manifest with file fingerprints. The official portal refused a script on 20 Nov 2026, so the count was not re-checked against the portal.",
  "Подсчёт репозитория, подкреплённый манифестом с отпечатками файлов. Официальный портал 20 ноября 2026 г. отказал скрипту, поэтому сверка с порталом не проведена.",
  ["cluster-pursue-release-01"]),
]
for _id, _en, _ru, _st, _basis, _where, _d, _dru, _by in _CL:
    E(_id, _en, "claim", label_ru=_ru, description=_d, description_ru=_dru, status=_st, basis=_basis, stated_in=_where)
    for _b in _by:
        C(_b, _id, ctype="states")

# ── SOURCE -> CLAIM / FACT EDGES (each backed by references/notes/<id>.md) ──
_ED = [
 ("oganessian2004", "f-mc115-synth-2003", "supports"), ("oganessian2005", "f-mc115-synth-2003", "supports"),
 ("rudolph2013", "f-gsi-replication-2013", "supports"), ("gates2015", "f-gsi-replication-2013", "relevant_to"),
 ("gates2018", "f-mc115-synth-2003", "supports"), ("iupac2016", "f-mc115-iupac-name", "supports"), ("ohrstrom2016", "f-mc115-iupac-name", "supports"),
 ("nubase2020", "f-mc115-halflives", "supports"), ("iaea_livechart", "f-mc115-halflives", "supports"),
 ("nubase2020", "claim-mc-halflives-measured", "supports"), ("iaea_livechart", "claim-mc-halflives-measured", "supports"),
 ("morse2022", "claim-mc-halflives-measured", "supports"), ("oganessian2022b", "claim-mc-halflives-measured", "supports"),
 ("oganessian2010", "claim-mc-halflives-measured", "supports"),
 ("nubase2020", "claim-115-stable-isotope-fuel", "contradicts"), ("iaea_livechart", "claim-115-stable-isotope-fuel", "contradicts"),
 ("nubase2020", "f-lazar-115-stability-disputed", "supports"), ("karpov2012", "claim-115-stable-isotope-fuel", "relevant_to"),
 ("oganessian2022a", "claim-115-500-pounds", "contradicts"), ("oganessian2022a", "claim-shef-70-atoms-40-days", "relevant_to"),
 ("giuliani2019", "claim-115-prediction-nontrivial", "contradicts"), ("chatt1979", "claim-115-prediction-nontrivial", "relevant_to"),
 ("myers1966", "claim-115-prediction-nontrivial", "relevant_to"), ("giuliani2019", "f-lazar-115-existence-correct", "cited_for"),
 ("nubase2020", "claim-113-118-none-over-1s", "contradicts"), ("iaea_livechart", "claim-113-118-none-over-1s", "contradicts"),
 ("karol2016", "claim-iupac-accepted-after-gsi", "cited_for"), ("iupac2015", "claim-iupac-accepted-after-gsi", "cited_for"),
 ("forsberg2016", "claim-iupac-accepted-after-gsi", "relevant_to"), ("barber2011", "claim-iupac-accepted-after-gsi", "relevant_to"),
 ("iupac2015", "claim-115-credit-jinr-llnl", "contradicts"), ("karol2016", "claim-115-credit-jinr-llnl", "contradicts"),
 ("roberto2017", "claim-115-credit-jinr-llnl", "contradicts"),
 ("karpov2012", "claim-knapp-could-not-rule-out", "relevant_to"),
 ("giuliani2019", "claim-island-long-lived-not-stable", "supports"), ("karpov2012", "claim-island-long-lived-not-stable", "supports"),
 ("oganessian2015", "claim-island-long-lived-not-stable", "relevant_to"), ("nilsson1969", "claim-island-long-lived-not-stable", "relevant_to"),
 ("sobiczewski1966", "claim-island-long-lived-not-stable", "relevant_to"),
 ("odni2021", "claim-odni-144-reports", "supports"), ("odni2022", "claim-odni-144-reports", "relevant_to"),
 ("nasa2023", "claim-nasa-no-et-reason", "supports"), ("aaro2024", "claim-aaro-quoted-finding", "cited_for"),
 ("powell2022", "claim-ubatuba-mg-terrestrial", "supports"), ("knuth2025", "claim-ubatuba-mg-terrestrial", "supports"),
 ("sturrock2001", "claim-ubatuba-mg-terrestrial", "relevant_to"), ("coplen2002", "claim-ubatuba-mg-terrestrial", "relevant_to"),
 ("ciaaw_mg", "claim-ubatuba-mg-terrestrial", "relevant_to"), ("meija2016", "claim-ubatuba-mg-terrestrial", "relevant_to"),
 ("galy2003", "claim-ubatuba-mg-terrestrial", "relevant_to"), ("vallee1998", "claim-ubatuba-mg-terrestrial", "relevant_to"),
 ("nolan2022", "claim-frag-no-lab-measurement", "relevant_to"), ("nasa2023", "claim-frag-photo-provenance", "relevant_to"),
 ("unodc2009", "claim-frag-no-chain-of-custody", "relevant_to"), ("iaea2015", "claim-frag-no-chain-of-custody", "relevant_to"),
 ("jcgm2008", "claim-frag-no-lab-measurement", "relevant_to"), ("eurachem2014", "claim-frag-no-lab-measurement", "relevant_to"),
 ("iso17025", "claim-frag-no-lab-measurement", "relevant_to"), ("pursue2026", "claim-pursue-225-records", "cited_for"),
 ("mc290proposal2025", "claim-115-stable-isotope-fuel", "relevant_to"), ("asrpmedia2025", "claim-shef-70-atoms-40-days", "supports"),
 ("stoyer2007", "f-mc115-synth-2003", "relevant_to"), ("oganessian2012", "f-mc115-synth-2003", "supports"),
 ("oganessian2013", "f-mc115-synth-2003", "supports"), ("singh2019", "claim-mc-halflives-measured", "supports"),
]
for _s, _t, _k in _ED:
    C(_g(_s), _t, ctype=_k, verdict=_BY[_s]["verdict"], note=_BY[_s]["reading_note"])

# claims -> experiments, base facts, campaign
for _c, _e in (("claim-mc-halflives-measured", "ev-exp-dubna-2003"), ("claim-mc-halflives-measured", "ev-exp-dubna-2010-2012"),
               ("claim-mc-halflives-measured", "ev-exp-shef-first"), ("claim-mc-halflives-measured", "ev-exp-gsi-tasca"),
               ("claim-ubatuba-mg-terrestrial", "ev-exp-ubatuba-2017-18"), ("f-ai-ctrl-within-fossil-range", "ev-ai-ctrl-test")):
    C(_c, _e, ctype="measured_in")
for _c, _f in (("claim-mc-halflives-measured", "f-mc115-halflives"), ("claim-115-stable-isotope-fuel", "f-lazar-115-stability-disputed"),
               ("claim-115-prediction-nontrivial", "f-lazar-115-existence-correct"), ("claim-mg-petrozavodsk-launch", "f-mg-petrozavodsk-as-cosmos955"), ("claim-iupac-accepted-after-gsi", "f-gsi-replication-2013")):
    C(_c, _f, ctype="restates")
C("f-cb-tm-no-peer-review", "claim-cb-time-shift", ctype="challenges")
C("f-cb-patent-never-granted", "claim-cb-time-shift", ctype="relevant_to")
C("claim-mc-halflives-measured", "phen-mc115", ctype="describes")
C("claim-island-long-lived-not-stable", "phen-island-stab", ctype="describes")
C("ds-nuclear-data-evaluations", "claim-mc-halflives-measured", ctype="supports")
for _c in ("claim-frag-no-lab-measurement", "claim-frag-no-chain-of-custody", "claim-frag-photo-provenance"):
    C(_c, "phen-uap-frag-001", ctype="describes")
    C("ev-exp-lab-report-planned", _c, ctype="tests" if _c == "claim-frag-no-lab-measurement" else "must_state")
for _c in ("claim-frag-no-lab-measurement", "claim-frag-no-chain-of-custody", "claim-frag-photo-provenance", "claim-pursue-225-records",
           "claim-ubatuba-mg-terrestrial", "claim-nasa-no-et-reason", "claim-odni-144-reports", "claim-mc-halflives-measured"):
    C(_c, "campaign-uap-archive-book", ctype="used_by_campaign")

# source -> source links
C(_g("villarroel2025"), _g("bruehl2025"), ctype="companion_of")
C(_g("knuth2025"), _g("powell2022"), ctype="cites")
C(_g("knuth2025"), _g("vallee1998"), ctype="cites")
C(_g("knuth2025"), _g("sturrock2001"), ctype="cites")
C(_g("knuth2025"), _g("coplen2002"), ctype="cites")
C(_g("powell2022"), _g("sturrock2001"), ctype="cites")
C(_g("eurachem2014"), _g("iso17025"), ctype="cites")
