#!/usr/bin/env python3
"""Every number on the showcase pages and diagrams is computed here, from the repository itself.

    python3 tools/facts.py            # print all facts

`facts()` returns a flat dict of strings. tools/build_facts.py writes them into the pages
(markers `<!--n:key-->value<!--/n-->`); tools/build_visuals.py draws the diagrams from the same dict.

Counts of files come from the git tree of the tag `pre-showcase-2026-11` (the state of the study before
the showcase pages were added), so adding guide/ or tools/ never changes them. Scores come from the
committed JSON outputs of the AI pipeline and from anchored regular expressions on the Track 1 reports
(the build fails when a sentence they read has changed). Standard library only.
"""
import json
import re
import subprocess
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS_OF = "2026-11-19"  # date of this showcase restructuring
TAG = "pre-showcase-2026-11"

# (key, folder, short name) of the eleven tracks; Track 1 lives in the root folders listed below
TRACKS = [("t2", "bob-lazar-archive"), ("t3", "chernobrov-archive"), ("t4", "dubna-element-115-analysis"),
          ("t5", "osint-intelligence-analysis"), ("t6", "people-analysis"), ("t7", "corporate-economic-analysis"),
          ("t9", "uap-scientific-publications"), ("t10", "gershtein-archive"), ("t11", "war-gov-pursue-archive")]


def p(*a):
    return os.path.join(ROOT, *a)


def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True)
    return r.stdout


def read(rel):
    return open(p(rel), encoding="utf-8").read()


def must(pattern, text, what, flags=0):
    m = re.search(pattern, text, flags)
    if not m:
        raise SystemExit("facts.py: cannot find %s (pattern %r) - the source sentence changed" % (what, pattern))
    return m


def ru_plural(n, one, few, many):
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def tree_files(ref):
    out = git("ls-tree", "-r", "-z", "--name-only", ref)
    return [x for x in out.split("\0") if x]


def facts():
    f = {"as_of": AS_OF}
    base = tree_files(TAG)
    f["base_commit"] = git("rev-parse", "--short", TAG).strip()
    f["files_total"] = str(len(base))
    f["md_total"] = str(len([x for x in base if x.endswith(".md")]))

    def under(prefix, ext=None):
        return [x for x in base if x.startswith(prefix) and (ext is None or x.endswith(ext))]

    for key, folder in TRACKS:
        f[key + "_files"] = str(len(under(folder + "/")))
        f[key + "_md"] = str(len(under(folder + "/", ".md")))
        f[key + "_diagrams"] = str(len([x for x in under(folder + "/diagrams/rendered/", ".png")]))
    f["tracks"] = str(len(re.findall(r"^\| \*\*\d+\. ", read("archive/README_2026-11-19_pre-showcase.md"), re.M)))
    f["tracks_archives"] = str(len(TRACKS) - 1)  # eight external-material archives besides the literature catalog
    f["lazar_transcripts"] = str(len(under("bob-lazar-archive/transcripts/")))
    f["chernobrov_transcripts"] = str(len(under("chernobrov-archive/transcripts/")))
    f["gershtein_transcripts"] = str(len(under("gershtein-archive/transcripts/")))
    f["pursue_transcripts"] = str(len([x for x in base if x.startswith("war-gov-pursue-archive/") and "/transcripts/" in x]))
    f["pursue_cards"] = str(len(under("war-gov-pursue-archive/analysis/per-document/")))
    f["pursue_topical"] = str(len(under("war-gov-pursue-archive/analysis/topical/")))
    f["pursue_master_lines"] = str(len(read("war-gov-pursue-archive/analysis/MASTER_pursue_claims.md").split("\n")) - 1)
    f["people_files"] = str(len(under("people-analysis/people/", ".md")))
    f["root_png"] = str(len([x for x in base if x.startswith("charts/") and x.endswith(".png")]))
    f["mermaid_png"] = str(len([x for x in base if x.startswith("mermaid/") and x.endswith(".png")]))
    f["mermaid_folders"] = str(len({x.split("/")[1] for x in base if x.startswith("mermaid/")}))

    # Track 1: percipient session, validation, AI pipeline
    f["percipient_reports"] = str(len(under("reports/percipient_reports/", ".md")))
    f["ai_reports"] = str(len(under("reports/ai_reports/", ".md")))
    val = read("analysis/ecp_validation_report.md")
    f["session_id"] = must(r"Session (ECP-\d{4}-\d{2}-\d{2})", val, "session id").group(1)
    rows = re.findall(r"^\| \*\*[^|]+\*\* \| [^|]+ \| [^|]+ \| [^|]+ \| \*\*[^|]+\*\* \|$",
                      must(r"### 4\.1\..*?(?=### 4\.2)", val, "4.1 table", re.S).group(0), re.M)
    f["ref_params"] = str(len(rows))
    f["ref_exact"] = must(r"Exact matches[^|]*\| (\d+)/10", val, "exact matches").group(1)
    f["ref_partial"] = must(r"Partial matches[^|]*\| (\d+)/10", val, "partial matches").group(1)
    f["ref_miss"] = must(r"Complete misses[^|]*\| (\d+)/10", val, "complete misses").group(1)
    f["ref_exact_or_partial"] = str(int(f["ref_exact"]) + int(f["ref_partial"]))
    f["shared_themes"] = must(r"Shared themes across all 3 responses[^|]*\| (\d+) parameters", val, "shared themes").group(1)
    f["blinded_compromised"] = must(r"blinding was compromised for (two) percipients", val, "compromised blinding").group(1)
    f["blinded_compromised_n"] = {"two": "2"}[f["blinded_compromised"]]
    f["pipeline_stages"] = str(len(under("pipeline/stages/s", ".py")))
    f["pipeline_outputs"] = str(len(under("data/processed/", ".json")))
    f["control_images"] = str(len(under("data/raw/control-images/", ".jpg")) - 1)  # minus the copy of the artifact photo
    ct = read("reports/ai_reports/AI-2026-04-09-control-test.md")
    f["control_groups"] = "3"
    f["control_n_similar"] = must(r"\*\*N \(similar fossils\)\*\* \| (\d+)", ct, "n similar fossils").group(1)
    f["fossil_mean"] = must(r"\*\*Mean / Среднее\*\* \| (0\.\d+)", ct, "fossil mean").group(1)
    f["fossil_std"] = must(r"\*\*Std \(population\) / Стд\. откл\.\*\* \| (0\.\d+)", ct, "fossil std").group(1)
    f["fossil_z"] = must(r"\*\*Z-score\*\* \| \*\*(0\.\d+)\*\*", ct, "z score").group(1)
    f["fossil_pct"] = must(r"\*\*Percentile / Процентиль\*\* \| \*\*(\d+)th\*\*", ct, "percentile").group(1)
    f["score_nearest_fossil"] = must(r"\| A1: Dark textured urchin \| Similar fossil \| (0\.\d+) \|", ct, "A1 score").group(1)
    f["score_max_negative"] = must(r"max (0\.\d+)\)", ct, "max negative control").group(1)
    f["score_max_dissimilar"] = must(r"dissimilar biological specimens \(max (0\.\d+)\)", ct, "max dissimilar").group(1)
    hyp = json.load(open(p("data", "processed", "material_hypothesis.json"), encoding="utf-8"))
    f["score_crop"] = "%.2f" % hyp["primary_hypothesis"]["score"]
    full = json.load(open(p("data", "processed", "control-test-results.json"), encoding="utf-8"))
    f["score_full"] = "%.2f" % full["UAP-FRAG-001 (full photograph)"][0]["score"]
    f["score_full4"] = "%.4f" % full["UAP-FRAG-001 (full photograph)"][0]["score"]
    sig = json.load(open(p("data", "processed", "siglip_scores.json"), encoding="utf-8"))
    f["score_stage4_top"] = "%.2f" % sig["top1_score"]

    # graph
    g = json.load(open(p("graph", "uap_kumu.json"), encoding="utf-8"))
    f["graph_nodes"], f["graph_edges"] = str(len(g["elements"])), str(len(g["connections"]))
    facts_n = [e for e in g["elements"] if e.get("type") == "fact"]
    f["graph_facts"] = str(len(facts_n))
    f["graph_facts_high"] = str(len([e for e in facts_n if e.get("confidence") == "high"]))
    f["graph_outreach"] = str(len([e for e in g["elements"] if e.get("type") == "outreach"]))
    f["graph_hypotheses"] = str(len([e for e in g["elements"] if e.get("type") == "hypothesis"]))
    gr = read("graph/README.md")
    m = must(r"\| elements / сущностей\s+\| (\d+)\s+\|", gr, "graph README elements")
    f["graph_readme_nodes"] = m.group(1)
    f["graph_readme_edges"] = must(r"\| connections / связей\s+\| (\d+)\s+\|", gr, "graph README connections").group(1)

    # branches (read-only look at the archive branches, when present in this clone)
    for key, ref in (("branch_lazar", "origin/archive/bob-lazar-archive"), ("branch_gershtein", "origin/archive/gershtein-archive")):
        n = len(tree_files(ref)) if git("rev-parse", "--verify", "--quiet", ref).strip() else 0
        f[key + "_files"] = str(n) if n else "?"
    f["branch_lazar_commits"] = git("rev-list", "--count", "origin/archive/bob-lazar-archive").strip() or "?"
    f["branch_gershtein_commits"] = git("rev-list", "--count", "origin/archive/gershtein-archive").strip() or "?"
    f["branch_lazar_last"] = git("log", "-1", "--format=%as", "origin/archive/bob-lazar-archive").strip() or "?"
    f["branch_gershtein_last"] = git("log", "-1", "--format=%as", "origin/archive/gershtein-archive").strip() or "?"
    f["commits_main"] = git("rev-list", "--count", TAG).strip()
    f["first_commit"] = git("log", "--reverse", "--format=%as", TAG).split("\n")[0]
    f["last_commit"] = git("log", "-1", "--format=%as", TAG).strip()

    # Russian number + noun phrases (the noun agrees with the number)
    for short, key, forms in (("md_pages", "md_total", ("страница", "страницы", "страниц")),
                              ("graph_nodes", "graph_nodes", ("узел", "узла", "узлов")),
                              ("graph_edges", "graph_edges", ("связь", "связи", "связей")),
                              ("files", "files_total", ("файл", "файла", "файлов"))):
        f[short + "_ru"] = "%s %s" % (f[key], ru_plural(f[key], *forms))
    for key in ("branch_lazar", "branch_gershtein"):
        n, c = f[key + "_files"], f[key + "_commits"]
        if n != "?":
            f[key + "_files_ru"] = "%s %s" % (n, ru_plural(n, "файл", "файла", "файлов"))
            f[key + "_commits_ru"] = "%s %s" % (c, ru_plural(c, "коммит", "коммита", "коммитов"))
        else:
            f[key + "_files_ru"] = f[key + "_commits_ru"] = "?"
    return f


def badges(lang, F):
    """Computed shields.io badges for the README header (the URL carries the numbers)."""
    from urllib.parse import quote
    if lang == "en":
        items = [("tracks", F["tracks"], "1f6feb", "Tracks"),
                 ("experiments", "1 session, %s percipients" % F["percipient_reports"], "8957e5", "Experiment"),
                 ("blinding compromised", "%s of %s" % (F["blinded_compromised_n"], F["percipient_reports"]), "e3b341", "Blinding"),
                 ("patent", "none", "6e7681", "Patent")]
    else:
        items = [("треков", F["tracks"], "1f6feb", "Tracks"),
                 ("эксперимент", "1 сеанс, %s перципиента" % F["percipient_reports"], "8957e5", "Experiment"),
                 ("ослепление нарушено", "у %s из %s" % (F["blinded_compromised_n"], F["percipient_reports"]), "e3b341", "Blinding"),
                 ("патент", "нет", "6e7681", "Patent")]
    return "\n".join("![%s](https://img.shields.io/badge/%s-%s-%s?style=flat-square)"
                     % (alt, quote(label.replace("-", "--").replace(" ", "_"), safe="_-"),
                        quote(msg.replace("-", "--").replace(" ", "_"), safe="_-,"), col)
                     for label, msg, col, alt in items)


if __name__ == "__main__":
    for k, v in facts().items():
        print("%-28s %s" % (k, v))
