**English | [Русский](README.ru.md)**

# References

Up: [repository front page](../README.md) · graph layer: [`../graph/REFERENCES-LAYER.md`](../graph/REFERENCES-LAYER.md)

This folder is the literature base of the UAP Reverse-Engineering Study: the outside sources the repository leans on, checked one by one. Built 20 November 2026. It does not replace the Track 9 catalogue in [`../uap-scientific-publications/`](../uap-scientific-publications/README.md) or the Track 4 source list in [`../dubna-element-115-analysis/catalog/sources.md`](../dubna-element-115-analysis/catalog/sources.md); it checks them. Where a card there has a placeholder or an error, the corrected record is here and the card is left untouched.

| File | Purpose |
|---|---|
| `sources.json` | One record per source: `id`, `title`, `authors`, `year`, `venue`, `volume`, `pages`, `doi`, `pmid`, `pmcid`, `arxiv`, `isbn`, `url`, `kind`, `track`, `theme`, `evidence_level` (L1 ASRP in-house or testimony published by ASRP / L2 published but contested or outside mainstream venues / L3 mainstream papers, evaluated data, official reports, standards), `open_access`, `oa_pdf_url` (legal open copies only), `verified`, `verification`, `note`, `why_en` / `why_ru`, `cited_in` (file and line where an ASRP text uses it), `used_by_campaign`, `reading_note`, `verdict`, `verdict_basis`, `graph_id` (node id in `../graph/uap_references_kumu.json`), `legacy_graph_id` (older node for the same work in `../graph/uap_kumu.json`). |
| `bibliography.bib` | BibTeX for every verified entry. Keys match the `id` values. |
| `notes/<id>.md` | Reading note: what the source says (short quotes with page or section), design and sample, what the ASRP text says about it (path and line), and a verdict. |
| `pdf/` | PDFs are **not tracked by git** (`.gitignore` in this folder). Created by `../scripts/fetch_literature.py`; `pdf/MANIFEST.json` lists SHA-256, size, source address and failures. |

## What is in the base

63 records, 59 verified, 36 reading notes (19 of them rest on a full text).

| Group | Records | How found |
|---|---:|---|
| Element 115: discovery, later experiments, recognition and naming | 17 | The Track 4 source list and timeline; DOIs resolved in Crossref; abstracts from INSPIRE-HEP; two IUPAC statements fetched from iupac.org |
| Measured half-lives and the island of stability | 13 | NUBASE2020 (open copy), the IAEA nuclear data service, Nuclear Data Sheets, one review and four theory papers |
| Official UAP reports | 5 | Track 9 cards; PDFs fetched from dni.gov and science.nasa.gov; two sources could not be fetched (see Known gaps) |
| Instrument-based and statistical UAP studies | 14 | Track 9 cards; every DOI re-resolved |
| Material analysis of alleged fragments | 8 | Track 9 cards, the reference list of Knuth et al. 2025, USGS and CIAAW |
| What a laboratory report rests on | 5 | Guides of JCGM, Eurachem, IAEA and UNODC; ISO/IEC 17025 by name only |
| ASRP's own interview with an institute representative | 1 | Track 4 |

## Verdicts

- `matches`: the ASRP sentence says what the source says.
- `overstated`: the source exists and is on the topic, but the ASRP sentence claims more.
- `misreported`: the source says something else, or the bibliographic details in the repository are wrong (wrong DOI, wrong venue, wrong author names).
- `not checked (no full text)`: the text could not be read and the abstract does not settle it.
- `n/a (context source: no ASRP text cites it)`.

Totals on 20 November 2026: 15 matches, 2 overstated, 8 misreported, 3 not checked, 8 context.

`verdict_basis` says what was read: full text, abstract only, or record only. A verdict reached from an abstract is safe only when the abstract itself contains or plainly excludes the claim; each note says so.

## Measured numbers for element 115

These are the numbers to use wherever the repository compares measurement with public claims of a stable isotope. Sources and exact quotations: [`notes/nubase2020.md`](notes/nubase2020.md), [`notes/oganessian2022b.md`](notes/oganessian2022b.md).

| Isotope | Half-life | Source |
|---|---|---|
| 286Mc | 20 ms (+98, −9) | Oganessian et al. 2022, Phys. Rev. C 106, 064306 (abstract) |
| 287Mc | 37 ms (+44, −13) | ENSDF, Nuclear Data Sheets 182 (2022); NUBASE2020 p. 030001-179 |
| 288Mc | 0.17 s (ENSDF); 177 ± 20 ms (NUBASE2020) | NUBASE2020 p. 030001-179 |
| 289Mc | 296 ms (+97, −59) (ENSDF); 410 ± 150 ms (NUBASE2020) | NUBASE2020 p. 030001-179 |
| 290Mc | 0.65 s (+0.49, −0.20) (ENSDF); 840 ± 360 ms (NUBASE2020) | NUBASE2020 p. 030001-179 |

No stable isotope has been observed. Nearby nuclei of other elements live longer: 286Nh about 10 s, 289Fl about 2 s.

## Rules

- **Never commit PDFs.** Paywalled papers are cited by DOI only.
- **Never add a reference from memory.** Resolve the DOI (Crossref) and compare title, authors and year, or fetch the official page. If a source cannot be confirmed, set `verified: false` and give the reason in `verification`.
- Quotes from sources stay short. Never invent numbers; write NOT FOUND.
- Testimony is not measurement. A statement made in an interview, a broadcast or a book is recorded as a claim with its speaker and status, never as a measured value.
- No personal data. Published authors are named as authors of what they published. Private individuals are not named; one self-published manuscript by a private individual is recorded without the author's name.
- When adding a source: edit `sources.json`, add the BibTeX entry, write a note if an ASRP claim leans on it, and rebuild the graph layer (`python3 graph/build_references_layer.py`).

## Fetching open-access PDFs

```bash
python3 scripts/fetch_literature.py --dry-run   # list what would be downloaded
python3 scripts/fetch_literature.py             # download into references/pdf/
python3 scripts/fetch_literature.py --only nubase2020 --force
```

Standard library only. The script sends the generic User-Agent `literature-fetcher/1.0` and keeps a file only if the response is a PDF. On 20 November 2026 it fetched 19 of 21; the two MDPI papers (`knuth2019`, `domine2025`) answered HTTP 403 and were read through the Europe PMC open full-text XML instead.

## Known gaps

- Four records are `verified: false`: the AARO historical report of 2024 (HTTP 403 and a timeout), the PURSUE portal (HTTP 403), ISO/IEC 17025 (a browser check that was not solved), and one self-published manuscript with no public address.
- The two IUPAC technical reports (2011 and 2016) were judged from their abstracts and from IUPAC's own statements; the publisher pages asked for a browser check. Why element 115 was accepted is in the body of the 2016 report and still has to be read.
- The Physical Review papers are paywalled; their notes rest on abstracts.
- Nolan et al. 2022, Vallée 1998 and Sturrock 2001 were not read.
- The annual UAP reports for 2023 and 2024 and the later AARO reports are not in the base.
- The sources behind the Chernobrov, Gershtein and Lazar archives are books, lectures and broadcasts held in those folders; they are represented in the graph as claims with status `stated`, not as checked literature.

---

Last updated: 20 November 2026 · Standard: UNIFIED_ASRP_STANDARD v6.1
