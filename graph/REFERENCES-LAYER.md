**English** (a Russian summary is at the end / краткое описание на русском в конце)

# References and campaign layer of the graph

Up: [graph README](README.md) · literature base: [`../references/`](../references/README.md)

Added 20 November 2026. This layer puts next to the facts-and-events graph the outside sources the study leans on, the claims they support or contradict, the experiments behind the measured numbers, and one crowdfunding campaign draft.

## Why it is a separate file

The repository's regression gate (`tools/verify_no_loss.py`, check H9) fails when any file that existed at tag `pre-showcase-2026-11` is changed. `build_blueprint.py`, `uap_kumu.json`, `README.md` and `preview.html` in this folder all existed at that tag. The layer therefore changes none of them:

| File | Role |
|---|---|
| `fragments/agentJ_references_campaign.py` | The layer itself, written with the same `E()` / `C()` calls as every other fragment. Source nodes are generated from `../references/sources.json`; nothing is typed twice. |
| `build_references_layer.py` | Re-runs `build_blueprint.py` (and stops if `uap_kumu.json` would change), loads it as the base, runs the fragment, checks the same invariants, writes the output. |
| `uap_references_kumu.json` | Generated: the layer only (its nodes and edges, `patches` for base nodes, name and SHA-256 of the base file). The base graph is not copied into it. Never edit by hand. |
| `preview_references.html` | Copy of `preview.html` that loads `uap_kumu.json` and `uap_references_kumu.json` and merges them by id, with colours for the new node types and Russian names for the new edge types. |

```bash
python3 graph/build_references_layer.py
# then, from graph/:  python3 -m http.server 8765  and open http://127.0.0.1:8765/preview_references.html
```

Folding the layer into the main graph is one `exec()` line in `build_blueprint.py`, followed by a rebuild, new counts in `README.md`, the `tools/` generators and an H9 waiver. That decision belongs to the repository owner and is not taken here.

## Counts (20 November 2026)

| | base (`uap_kumu.json`) | layer | total |
|---|---:|---:|---:|
| elements | 499 | 98 | 597 |
| connections | 896 | 245 | 1141 |

New elements: 63 `source`, 20 `claim`, 8 `event` (experiments, one of them planned), 4 `cluster` (two folders, two roles), 2 `dataset`, 1 `campaign`. Orphans 0, dangling connections 0, Russian label and description on every element.

## New node types

- `claim`: a statement with three extra fields. `status` is `proven`, `stated`, `open` or `refuted`. `basis` says what it rests on: `measurement`, `official count`, `official statement`, `model`, `testimony`, `published attribution`, or `ASRP text`. `stated_in` gives the file and line or the reading note. A claim that rests on testimony is never `proven`.
- `campaign`: a crowdfunding draft. Status `draft`; nothing is launched.
- `dataset`: a set of numbers (the control-test scores; the evaluated half-life tables).

Source nodes carry `doi`, `url`, `verified`, `verdict`, `note` (path of the reading note) and `source_id` (the id in `sources.json`). Where the base graph already had a node for the same work, the new node points to it with `same_work_as`; the old node is left as it is.

## Edge types of the layer

`cites` (ASRP folder, campaign or paper to source) · `supports` · `contradicts` · `cited_for` (cited for a claim, but the reading note's verdict is overstated, misreported or not checked) · `relevant_to` (context that does not settle the claim) · `states` (who or what states a claim) · `restates` (claim to an existing fact node) · `measured_in` (claim to experiment) · `replicates` (experiment to experiment) · `reported_in` (experiment to paper) · `funds`, `tests`, `must_state` (campaign and planned laboratory report) · `used_by_campaign`.

## Ids shared with the company memory

The layer file carries, under `patches`, a `memory_id` for five base nodes: `pj-uap` → `uap-reverse-engineering`, `p-lazar` → `bob-lazar`, `inst-jinr` → `jinr-dubna`, `p-chernobrov` → `vadim-chernobrov`, `src-asrp-media-2025` → `asrp-media-dubna-interview-2025`. New source ids follow the memory pattern `ref-<first author>-<year>-<three title words>`.

## People

Published authors are named as authors of what they published. The participants of the April 2026 session are private individuals and appear only as the role node `role-session-participants`. One self-published manuscript by a private individual is recorded without the author's name.

---

**Русский.** Слой добавляет к графу фактов и событий внешние источники из `../references/sources.json`, утверждения с полями «статус» и «основание», эксперименты, стоящие за измеренными числами, и черновик одной краудфандинговой кампании. Слой собирается отдельным скриптом `build_references_layer.py` в отдельный файл `uap_references_kumu.json`, потому что проверка H9 в `tools/verify_no_loss.py` запрещает менять файлы, существовавшие на момент тега `pre-showcase-2026-11`. Просмотр: `preview_references.html`. Частные лица не названы; участники сеанса представлены ролью.
