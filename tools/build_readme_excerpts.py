#!/usr/bin/env python3
"""Pulls sections of the detail pages into the showcase READMEs, so the front page shows the
ecosystem map, component tables, patents, legal entities, funding and so on without a second
copy of the text that could drift.

    python3 tools/build_readme_excerpts.py

A README marks a slot like this (one line each):

    <!-- excerpt PAGE H2INDEX [stop=REGEX] [mode=headings|images] -->
    ...generated, do not edit by hand...
    <!-- /excerpt -->

PAGE is a guide page stem (ARCHITECTURE), H2INDEX the zero-based index of the `##` section on that
page. README.md reads guide/PAGE.md, README.ru.md reads guide/PAGE.ru.md; both pages have the same
structure. The section is copied verbatim except that the `##` heading line is dropped (the README
supplies its own), relative links are re-based from guide/ to the repository root, and a trailing
rule is removed.

    stop=REGEX     cut the section before the first line matching REGEX
    mode=headings  emit only a bullet list of the section's `###` headings, linked to the page
    mode=images    emit only the section's images (with their alt text), linked to the page
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import github_slug  # noqa: E402

SLOT = re.compile(r"<!-- excerpt (\w+) (\d+)((?: \w+=\S+)*) -->\n.*?<!-- /excerpt -->", re.S)
IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def section(path, index):
    """Lines of the index-th `##` section (heading line excluded) and all heading anchors."""
    lines = open(path, encoding="utf-8").read().split("\n")
    seen, anchors, starts = {}, {}, []
    in_code = False
    for i, ln in enumerate(lines):
        if ln.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        m = re.match(r"^(#{1,6}) (.*)$", ln)
        if m:
            anchors[i] = github_slug(m.group(2).strip(), seen)
            if len(m.group(1)) == 2:
                starts.append(i)
    a = starts[index]
    b = starts[index + 1] if index + 1 < len(starts) else len(lines)
    return lines, a, b, anchors


def rebase(line, page_file):
    """guide/-relative links -> repository-root-relative links."""
    def fix(target):
        if re.match(r"^[a-z]+:", target):
            return target
        if target.startswith("#"):
            return "guide/" + page_file + target
        if target.startswith("../"):
            return target[3:]
        return "guide/" + target

    line = re.sub(r"\]\(([^)\s]+)\)", lambda m: "](" + fix(m.group(1)) + ")", line)
    return re.sub(r"(src|href)=\"([^\"]+)\"", lambda m: '%s="%s"' % (m.group(1), fix(m.group(2))), line)


def render(page, index, opts, ru):
    page_file = page + (".ru.md" if ru else ".md")
    lines, a, b, anchors = section(os.path.join("guide", page_file), index)
    body = list(range(a + 1, b))
    if "stop" in opts:
        rx = re.compile(opts["stop"])
        for k, i in enumerate(body):
            if rx.search(lines[i]):
                body = body[:k]
                break
    mode = opts.get("mode")
    out = []
    if mode == "headings":
        for i in body:
            m = re.match(r"^### (.*)$", lines[i])
            if m and i in anchors:
                out.append("- [%s](guide/%s#%s)" % (m.group(1).strip(), page_file, anchors[i]))
    elif mode == "images":
        for i in body:
            for alt, src in IMG.findall(lines[i]):
                head = [j for j in anchors if j <= i]
                frag = "#" + anchors[max(head)] if head else ""
                src = src[3:] if src.startswith("../") else "guide/" + src
                out.append('<a href="guide/%s%s"><img src="%s" width="100%%" alt="%s"></a>' % (page_file, frag, src, alt))
                out.append("")
    else:
        in_code = False
        for i in body:
            ln = lines[i]
            if ln.startswith("```"):
                in_code = not in_code
            out.append(ln if in_code else rebase(ln, page_file))
        while out and out[-1].strip() in ("", "---"):
            out.pop()
        while out and not out[0].strip():
            out.pop(0)
    return "\n".join(out)


def main():
    for readme, ru in (("README.md", False), ("README.ru.md", True)):
        text = open(readme, encoding="utf-8").read()

        def repl(m):
            opts = dict(o.split("=", 1) for o in m.group(3).split())
            head = "<!-- excerpt %s %s%s -->" % (m.group(1), m.group(2), m.group(3))
            return head + "\n" + render(m.group(1), int(m.group(2)), opts, ru) + "\n<!-- /excerpt -->"

        new, n = SLOT.subn(repl, text)
        open(readme, "w", encoding="utf-8").write(new)
        print("updated %s: %d excerpt(s), %d bytes" % (readme, n, len(new.encode("utf-8"))))


if __name__ == "__main__":
    main()
