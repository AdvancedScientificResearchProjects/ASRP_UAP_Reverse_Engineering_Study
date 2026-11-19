**English | [Русский](OPEN.ru.md)**

[← UAP Reverse Engineering Study](../README.md) · [Guide index](README.md)

<div align="center">

# Open questions

</div>

## What is unresolved

Inconsistencies inside the repository are listed here and not corrected: the source files are unchanged. "Not verified" marks items that rest on a source outside this repository.

| # | Item | What the files say | Where |
|---|---|---|---|
| 1 | Graph statistics | `graph/README.md` says 275 entities, 447 links, 64 facts; the JSON has <!--n:graph_nodes-->499<!--/n--> elements, <!--n:graph_edges-->896<!--/n--> connections, <!--n:graph_facts-->83<!--/n--> facts. Its tracks table also still calls Track 7 a placeholder while the README lists it as available | `graph/README.md`, `graph/uap_kumu.json` |
| 2 | PURSUE counts | Previous README: 164 per-document cards, 8 topical syntheses, 6362 lines in MASTER; the track README mixes Release 01 only (158 cards, 7 topicals, 161 records) with both releases (225); files on disk: <!--n:pursue_cards-->222<!--/n--> per-document, <!--n:pursue_topical-->10<!--/n--> topical, MASTER <!--n:pursue_master_lines-->9306<!--/n--> lines | `war-gov-pursue-archive/README.md`, `archive/README_2026-11-19_pre-showcase.md` |
| 3 | Lazar counts | "Unique appearances: 24" against "25 main + 1 external" transcript files; <!--n:lazar_transcripts-->26<!--/n--> transcript files on disk | `bob-lazar-archive/` |
| 4 | Stale Russian sentence | The Russian text of the previous README says all ten active tracks are available and Track 10 is reserved; the table lists eleven, and Track 10 has <!--n:gershtein_transcripts-->62<!--/n--> transcripts | `archive/README_2026-11-19_pre-showcase.md` |
| 5 | Blinding is worse than "2 of 3" | The validation report also records the first percipient as only partly blind (saw the object earlier without explanation) | `analysis/ecp_validation_report.md` |
| 6 | Scoring without a baseline | Ten "verifiable" parameters were scored after the reference was disclosed; the cross comparison uses a different 14-theme table; the protocol has only a TP/FP template, no chance baseline | `analysis/`, `experiments/protocol_ecp.md` |
| 7 | AI result against the reference | The control test puts the artifact nearest a dark echinoid fossil (<!--n:score_nearest_fossil-->0.9870<!--/n-->) while the reference says "biometal"; unresolved, laboratory analysis required | `reports/ai_reports/AI-2026-04-09-control-test.md` |
| 8 | 0.98 versus 0.89 | The previous README's key AI findings table gives 0.98 (a crop score at stage 5); the control test scores the full photo <!--n:score_full4-->0.8912<!--/n--> | `archive/README_2026-11-19_pre-showcase.md`, control-test report |
| 9 | Control image count | The README says "14 reference images"; the test uses <!--n:control_images-->13<!--/n--> controls plus the artifact photo (a copy of it is the 14th file) | `data/raw/control-images/` |
| 10 | Source photograph | `data/raw/UAP-FRAG-001.jpg` is required by the pipeline and absent (Issue #4), so the pipeline cannot be re-run from this clone | `pipeline/README.md` |
| 11 | Patent vs graph | The graph links the FBHFS application to "UAP-adjacent oncology"; the README says no patent underlies this study; the only oncology text is speculation in a Chernobrov book extract | `graph/uap_kumu.json`, `chernobrov-archive/analysis/books/chunks/TPV-01_part2_extract.md` |
| 12 | ASRP.drift number | The README writes "KZ 413554" in the Application column; not verified here | `archive/README_2026-11-19_pre-showcase.md` |
| 13 | Graph-only outreach | DoE / Los Alamos, Stanford, NCI, Cortical Labs, Boeing and the DARPA portal exist only as graph nodes without sources | [Evidence](EVIDENCE.md#claims-found-only-in-the-graph) |
| 14 | FBI date | 2026-04-19 rests on a single-author YouTube recap, graded as such in the track README. Not verified | `people-analysis/README.md` |
| 15 | Dubna interview in two places | The ASRP.media interview is archived in Track 4 and, separately, in the Lazar archive catalog; the tracks do not cross-link | `bob-lazar-archive/catalog/asrp_media_115_interview.md` |
| 16 | Course repository | The hub mentions a course but never names or links its repository | `archive/README_2026-11-19_pre-showcase.md` |
| 17 | Unlisted folder | `mermaid/` (<!--n:mermaid_png-->60<!--/n--> PNG) is not in the previous README's structure tree | `mermaid/` |
| 18 | Sketch consent | The percipient sketch inventory says sketches are not to be reproduced outside the ECP study without the percipient's and project lead's consent; one sketch is dated 2026-04-02, two days before the session | `data/raw/percipient-sketches/INVENTORY.md` |
| 19 | Repository name | The README and the pipeline README call the repository `UAP_Reverse_Engineering_Study`; the folder is `ASRP_UAP_Reverse_Engineering_Study` | `pipeline/README.md` |

## What would settle the main questions

- A repeat session with individual blinding, control objects and a computed chance baseline.
- Laboratory analysis of the object (SEM-EDS, XRF, gamma spectroscopy over time).
- Same-condition photographs of a genuine echinoid fossil and the artifact, and a second vision model.
- Sources (letters, replies, dates) for each outreach statement in the graph, or removal of those nodes.
- A decision on the OSF preregistration and on whether any patent filing is intended.
