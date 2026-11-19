**English | [Русский](NAVIGATION.ru.md)**

[← UAP Reverse Engineering Study](../README.md) · [Guide index](README.md)

<div align="center">

# Navigation and structure

</div>

## Where things are

The tree is generated from the repository's real file list (`tools/tree.py`); counts are computed.

<!-- tree -->
```
ASRP_UAP_Reverse_Engineering_Study/
├── README.md                       # front page (English)
├── README.ru.md                    # front page (Russian)
├── guide/                          # detail pages X.md + X.ru.md; assets/ = generated SVG
├── archive/                        # the previous README, kept byte for byte
├── tools/                          # showcase tooling: facts, visuals, excerpts, no-loss check
├── tests/                          # regression gate for the showcase
├── analysis/                       # Track 8 and Track 1 analysis at the root: synthesis, taxonomy, ECP validation
│   ├── cross-archive-synthesis.md  # Track 8: overlaps between Lazar, Chernobrov, Dubna
│   ├── uap-taxonomy.md             # Track 8: three-category origin vocabulary
│   ├── external-podcasts.md        # Track 8: external podcasts and documentaries
│   ├── cross_comparison.md         # Track 1: descriptive overlap of the responses
│   └── ecp_validation_report.md    # Track 1: responses against the disclosed reference
├── experiments/                    # protocols: ECP, AI pipeline, corporate scan
├── reports/                        # Track 1 reports
│   ├── percipient_reports/         # 3 session reports (percipients not named on these pages)
│   └── ai_reports/                 # 3 AI reports: CV pipeline, LLM visual, control test
├── pipeline/                       # Track 1 code: 10 stages (detect, segment, features, SigLIP2, anomaly, depth)
├── data/                           # Track 1 data: 11 stage outputs, control images, sketches inventory
├── charts/                         # Track 1 charts: two ECP matrices and Mermaid renders
├── mermaid/                        # Mermaid sources and renders of the archive tracks (9 folders)
├── bob-lazar-archive/              # Track 2: 26 transcripts, analysis, catalog
├── chernobrov-archive/             # Track 3: 22 transcripts, analysis, books
├── dubna-element-115-analysis/     # Track 4: JINR interview, claims, 9 diagrams
├── osint-intelligence-analysis/    # Track 5: method layer, 5 pages
├── people-analysis/                # Track 6: 11 public-source profiles
├── corporate-economic-analysis/    # Track 7: companies, analysis, theoretical foundations
├── uap-scientific-publications/    # Track 9: 49 pages of literature catalog
├── gershtein-archive/              # Track 10: 62 transcripts, articles, books
├── war-gov-pursue-archive/         # Track 11: 222 cards, 10 topical files, MASTER claims
├── graph/                          # knowledge graph: 499 nodes, 896 links
│   ├── README.md                   # how to build and view (its own numbers are stale)
│   ├── build_blueprint.py          # builds the JSON from fragments
│   ├── fragments/                  # per-track entity extractions
│   ├── uap_kumu.json               # generated graph
│   └── preview.html                # browser viewer
├── docs/                           # placeholder (empty)
└── hardware/                       # placeholder (empty)
```
<!-- /tree -->

Notes. `mermaid/` (<!--n:mermaid_folders-->9<!--/n--> sub-folders, <!--n:mermaid_png-->60<!--/n--> rendered PNG) holds the Mermaid sources and renders of the archive tracks and was not in the previous README's tree. `docs/` and `hardware/` contain only placeholders. The three percipient reports in `reports/percipient_reports/` carry participant names; these pages do not name them.

**Folders as the previous README described them** (its own wording and counts; the tree above has the counts computed from the files).

| Folder | Described as |
|---|---|
| `analysis/` | Cross-archive synthesis (Track 8); the Track 1 cross comparison and ECP validation report also live here |
| `dubna-element-115-analysis/` | Track 4; 9 rendered diagrams |
| `osint-intelligence-analysis/` | Track 5 (methodology); 4 analysis files; 4 diagrams |
| `people-analysis/` | Track 6 (11 scientists cluster); 3 analysis files (Cardillo / FBI / cluster summary); 11 per-person files; 5 diagrams; raw: YouTube transcript (public) |
| `corporate-economic-analysis/` | Track 7 (defense-prime constellation); 8 analysis files + `adversarial-osint-runs/`; 8 company profiles + index (incl. Honeywell); 2 HSP scan dossiers (depersonalized) + public scanning roster (27 entries); `theoretical-foundations/` v3 sub-archive (Morgan / Frolov / scalar-vortex literature catalog); 9 diagrams (3 v1 + 4 v3 + 2 v4) |
| `uap-scientific-publications/` | Track 9 (v4); 6 analysis files (taxonomy / peer-reviewed physics / peer-reviewed social / grey lit / govt reports / observation programs); 13 source-provenance files (Kean, Pasulka, Eghigian, Wendt-Duvall, NASA, ODNI, AARO, Hessdalen, Nimitz, Galileo, SCU + 2 cross-refs); raw Perplexity research dumps (tool output) |
| `experiments/` | Track 1 + Track 7 protocols: ECP protocol v2.0, AI protocol v3.1, corporate HSP scan protocol v1.2 |
| `data/` | Track 1 research data: raw input data and pipeline output |

## Reading routes

| If you want | Read |
|---|---|
| The one experiment and its numbers | [Track 1](EXPERIMENT.md), then `analysis/ecp_validation_report.md` |
| What is shown and what is only claimed | [Evidence](EVIDENCE.md) |
| The AI result and why 0.98 is not the headline | [Track 1, AI results](EXPERIMENT.md#ai-and-computer-vision-results) |
| One of the archives | [Tracks](TRACKS.md), then the track's lead file |
| What is inconsistent or unfinished | [Open questions](OPEN.md) |
| Privacy and what is withheld | [Ethics, IP and security](ETHICS.md) |
| The knowledge graph | `graph/preview.html` (serve the `graph/` folder locally; see `graph/README.md`); its own numbers are stale, the JSON has <!--n:graph_nodes-->499<!--/n--> nodes and <!--n:graph_edges-->896<!--/n--> links |

## Archive branches

The repository has two archive branches that are earlier snapshots of the hub, not separate studies: `archive/bob-lazar-archive` (<!--n:branch_lazar_files-->265<!--/n--> files, <!--n:branch_lazar_commits-->34<!--/n--> commits, last commit <!--n:branch_lazar_last-->2026-04-22<!--/n-->: an early hub with the Lazar and Chernobrov archives) and `archive/gershtein-archive` (<!--n:branch_gershtein_files-->726<!--/n--> files, <!--n:branch_gershtein_commits-->78<!--/n--> commits, last commit <!--n:branch_gershtein_last-->2026-05-09<!--/n-->: before the PURSUE track and the root restructure). They are left untouched.

## Navigation index

The previous README ended with a one-line index of its sections. The same entry points are now the quick-navigation table on the front page and the [guide index](README.md).
