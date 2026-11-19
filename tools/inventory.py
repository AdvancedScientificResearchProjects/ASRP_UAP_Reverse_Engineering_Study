#!/usr/bin/env python3
"""Content inventory of a Markdown file (used for the no-loss check).

Usage:
    python3 tools/inventory.py <markdown-file> [<out.json>]

Extracts every element class that must survive a restructuring:
headings + GitHub anchors, links, images, badges, tables (row by row),
numbers, dates, identifiers (e-mails, handles, code spans), proper names,
legal/attribution lines, code blocks and language-tagged text segments.

Standard library only. Deterministic: same input -> same output.
"""
import json
import re
import sys
import unicodedata

SEP = "**/**"
URL_RE = re.compile(r"https?://[^\s<>\")\]]+")
MDLINK_RE = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)\)")
NUM_RE = re.compile(r"(?<![\w.])\d[\d.,/:\-–]*\d|(?<![\w.])\d")
CODE_RE = re.compile(r"`([^`\n]+)`")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
HANDLE_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_.]{3,}")
MONTHS = (
    "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|"
    "январ|феврал|март|апрел|ма[йя]|июн|июл|август|сентябр|октябр|ноябр|декабр|"
    "янв|фев|авг|сен|окт|ноя|дек"
)
DATE_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}\.\d{2}\.\d{4}\b|\b20\d\d-Q[1-4]\b|\bQ[1-4] 20\d\d\b|"
    r"\b\d{1,2} (?:%s)[а-яa-z.]* ?(?:19|20)\d\d\b|\b(?:%s)[а-яa-z.]* (?:19|20)\d\d\b" % (MONTHS, MONTHS),
    re.I,
)
LEGAL_RE = re.compile(
    r"©|all rights reserved|все права|licen[sc]e|лиценз|CC BY|copyright|авторск|NDA|"
    r"disclaimer|оговорк|UBO|бенефициар|public offer|оферт|written permission|письменн|"
    r"consent|соглас|GDPR|152-ФЗ|regulatory|clinical-efficacy|not a merit|proprietary",
    re.I,
)
NAME_RE = re.compile(r"\b[A-ZА-ЯЁ][\w'’.-]*(?:[ -][A-ZА-ЯЁ][\w'’.-]*)+")


def github_slug(text, seen=None):
    """GitHub heading anchor (validated against the old README's own TOC)."""
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    t = t.replace("**", "").replace("`", "").strip().lower()
    out = []
    for ch in t:
        cat = unicodedata.category(ch)
        if ch in "-_ " or cat[0] in "LNM":
            out.append(ch)
    slug = "".join(out).replace(" ", "-")
    if seen is not None:
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        if n:
            slug = "%s-%d" % (slug, n)
    return slug


def lang_of(s):
    cyr = len(re.findall(r"[А-Яа-яЁё]", s))
    lat = len(re.findall(r"[A-Za-z]", s))
    if cyr == 0 and lat == 0:
        return "none"
    if cyr >= 0.5 * (cyr + lat):
        return "ru"
    if cyr <= 0.1 * (cyr + lat):
        return "en"
    return "mixed"


def norm_url(u):
    return u.rstrip(".,;:*").rstrip(")")


def segments_of(line):
    """Split a source line into the smallest language-pure text pieces."""
    body = line
    if body.lstrip().startswith("|"):
        cells = [c for c in body.strip().strip("|").split("|")]
    else:
        cells = [body]
    out = []
    for c in cells:
        for piece in c.split(SEP):
            p = piece.strip().strip("*").strip()
            p = re.sub(r"^[>#\-\s\d.]*", "", p) if not p[:1].isalnum() else p
            if p:
                out.append(p)
    return out


def inventory(text):
    lines = text.split("\n")
    inv = {
        "chars": len(text),
        "lines": len(lines),
        "headings": [],
        "links": [],
        "images": [],
        "badges": [],
        "urls": [],
        "internal_targets": [],
        "tables": [],
        "table_rows": [],
        "numbers": [],
        "dates": [],
        "emails": [],
        "handles": [],
        "code_spans": [],
        "code_blocks": [],
        "names": [],
        "legal_lines": [],
        "segments": [],
        "blockquote_lines": 0,
        "list_items": 0,
    }
    seen = {}
    in_code = False
    code_buf = []
    table_open = False
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            if in_code:
                inv["code_blocks"].append({"end_line": i, "text": "\n".join(code_buf)})
                code_buf = []
            in_code = not in_code
            continue
        if in_code:
            code_buf.append(line)
            for s in segments_of(line):
                inv["segments"].append({"line": i, "lang": lang_of(s), "text": s, "code": True})
            continue
        m = re.match(r"^(#{1,6}) (.*)$", line)
        if m:
            title = m.group(2).strip()
            inv["headings"].append(
                {"line": i, "level": len(m.group(1)), "text": title, "anchor": github_slug(title, seen)}
            )
        if line.startswith(">"):
            inv["blockquote_lines"] += 1
        if re.match(r"^\s*(?:[-*]|\d+\.) ", line):
            inv["list_items"] += 1
        if line.lstrip().startswith("|"):
            if re.match(r"^\s*\|[\s:|-]+\|\s*$", line):
                pass
            else:
                if not table_open:
                    inv["tables"].append({"line": i, "header": line.strip(), "rows": 0})
                    table_open = True
                else:
                    inv["tables"][-1]["rows"] += 1
                    inv["table_rows"].append({"line": i, "text": line.strip()})
        else:
            table_open = False
        for mm in MDLINK_RE.finditer(line):
            bang, label, target = mm.groups()
            rec = {"line": i, "text": label, "target": target}
            if bang:
                (inv["badges"] if "img.shields.io" in target else inv["images"]).append(rec)
            else:
                inv["links"].append(rec)
            if not target.startswith("http"):
                inv["internal_targets"].append({"line": i, "target": target})
        for u in URL_RE.findall(line):
            inv["urls"].append(norm_url(u))
        if LEGAL_RE.search(line):
            inv["legal_lines"].append({"line": i, "text": line.strip()})
        for s in segments_of(line):
            inv["segments"].append({"line": i, "lang": lang_of(s), "text": s, "code": False})
    # token classes are collected on the text with URLs removed (URLs are checked separately)
    plain = URL_RE.sub(" ", text)
    inv["numbers"] = sorted(set(NUM_RE.findall(plain)))
    inv["dates"] = sorted(set(m.group(0) for m in DATE_RE.finditer(plain)))
    inv["emails"] = sorted(set(EMAIL_RE.findall(plain)))
    inv["handles"] = sorted(set(HANDLE_RE.findall(plain)))
    inv["code_spans"] = sorted(set(CODE_RE.findall(plain)))
    inv["names"] = sorted(set(m.group(0).strip(" .") for m in NAME_RE.finditer(plain)))
    inv["urls"] = sorted(set(inv["urls"]))
    inv["counts"] = {
        k: (len(v) if isinstance(v, list) else v) for k, v in inv.items() if k not in ("counts",)
    }
    return inv


def main():
    src = sys.argv[1]
    text = open(src, encoding="utf-8").read()
    inv = inventory(text)
    inv["source"] = src
    out = json.dumps(inv, ensure_ascii=False, indent=1)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w", encoding="utf-8").write(out + "\n")
    print(json.dumps(inv["counts"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
