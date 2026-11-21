# nubase2020 — Kondev (2021)

*Reading note, 20 Nov 2026. Up: [references](../README.md). Record: `references/sources.json`, id `nubase2020`; graph node `ref-kondev-2021-nubase2020-evaluation-nuclear`.*

**Source.** Kondev, F. G.; Wang, M.; Huang, W. J.; Naimi, S.; Audi, G.. The NUBASE2020 evaluation of nuclear physics properties. Chinese Physics C 45(3) : 030001.
DOI [10.1088/1674-1137/abddae](https://doi.org/10.1088/1674-1137/abddae).

**What was read.** full text (open copy at the IAEA Atomic Mass Data Center), table pages 030001-178 and 030001-179.

**Design and sample.** Evaluation of all published measurements of nuclear ground-state properties (not an experiment). For superheavy nuclei each value rests on a handful of atoms; asymmetric uncertainties are 'symmetrized' in the main column and the original values are given in the remarks.

## What the source says

- 287Mc: "60 ms 30", remark "symmetrized from 17Og01=37(+44-13)" (table, p. 030001-179).
- 288Mc: "177 ms 20", remark "symmetrized from 17Og01=174(+22-18); other 16Fo10=170(20)" (p. 030001-179).
- 289Mc: "410 ms 150", remarks "symmetrized from 17Og01=330(+120-80)" and "10Og01=220(+260-80)" (p. 030001-179).
- 290Mc: "840 ms 360" (p. 030001-179). ENSDF, through the IAEA service, gives 0.65 s +0.49 −0.20 for the same nucleus.
- Neighbours: 286Nh "12 s 5", remark "symmetrized from 17Og01=9.5(+6.3-2.7) (recommended)" (pp. 030001-178 and -179); 289Fl "2.1 s 0.6" (p. 030001-179).
- 286Mc is not in this 2020 table; it was reported in 2022 with 20 (+98, −9) ms (`oganessian2022b`).

## What the ASRP text says about it

- `dubna-element-115-analysis/analysis/MASTER_claims.md:65` — "heaviest known moscovium isotope ²⁹⁰Mc has a half-life on the order of hundreds of milliseconds; no isotope in the 113–118 range exceeds ~1 s."
- `dubna-element-115-analysis/analysis/lazar-dubna-connection.md:44` — "All known isotopes through ²⁹⁰Mc have half-lives on the order of milliseconds to ~1 second ... No stable isotope has been observed."
- `dubna-element-115-analysis/analysis/lazar-dubna-connection.md:63` — "²⁹⁰Mc's half-life from ~0.65 s".
- `dubna-element-115-analysis/analysis/kazakhstan-uap-geological.md:62` — "a lifetime of roughly one second".

## Verdict

**misreported**

For moscovium itself the repository is right: every measured isotope lives less than about a second, and the 0.65 s figure for 290Mc is the ENSDF value. The second half of MASTER_claims.md:65 is wrong: in the range 113–118 the evaluated half-life of 286Nh is about 10 s and that of 289Fl about 2 s. Reword to 'no isotope of element 115 exceeds about one second; the longest-lived known nuclei of elements 113 and 114 live a few seconds'. None of this helps the stable-isotope claim: seconds are not stability.
