#!/usr/bin/env python3
"""Writes the computed numbers (tools/facts.py) into the showcase pages.

    python3 tools/build_facts.py          # rewrite README*.md and guide/*.md in place
    python3 tools/build_facts.py --check  # exit 1 if any marker is stale or unknown

A number in prose is written `{{key}}` while authoring; this tool turns it into
`<!--n:key-->VALUE<!--/n-->` (invisible when rendered) and refreshes VALUE on every later run, so the
page never keeps a hand-typed figure.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import facts as factsmod  # noqa: E402
import tree as treemod  # noqa: E402

ROOT = factsmod.ROOT
SHORT = re.compile(r"\{\{(\w+)\}\}")
LONG = re.compile(r"<!--n:(\w+)-->.*?<!--/n-->")
BADGES = re.compile(r"<!-- badges -->\n.*?<!-- /badges -->", re.S)
TREE = re.compile(r"<!-- tree -->\n.*?<!-- /tree -->", re.S)


def targets():
    out = [os.path.join(ROOT, "README.md"), os.path.join(ROOT, "README.ru.md")]
    return [f for f in out + sorted(glob.glob(os.path.join(ROOT, "guide", "*.md"))) if os.path.exists(f)]


def render(text, F, unknown, lang="en"):
    text = BADGES.sub(lambda m: "<!-- badges -->\n%s\n<!-- /badges -->" % factsmod.badges(lang, F), text)
    text = TREE.sub(lambda m: "<!-- tree -->\n```\n%s\n```\n<!-- /tree -->" % treemod.render(lang, F), text)
    def mk(m):
        k = m.group(1)
        if k not in F:
            unknown.append(k)
            return m.group(0)
        return "<!--n:%s-->%s<!--/n-->" % (k, F[k])
    return LONG.sub(mk, SHORT.sub(mk, text))


def main():
    check = "--check" in sys.argv
    F = factsmod.facts()
    stale, unknown = [], []
    for f in targets():
        old = open(f, encoding="utf-8").read()
        new = render(old, F, unknown, "ru" if f.endswith(".ru.md") else "en")
        if new != old:
            stale.append(os.path.relpath(f, ROOT))
            if not check:
                open(f, "w", encoding="utf-8").write(new)
    if unknown:
        print("UNKNOWN fact keys:", sorted(set(unknown)))
        return 1
    if check and stale:
        print("stale numbers in:", stale)
        return 1
    print("facts: %d keys, %d file(s) %s" % (len(F), len(stale), "stale" if check else "updated"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
