"""Regression gate: the repackaged pages must keep every element of the archived README, no existing content
file may change, and every generated piece (numbers, visuals, excerpts, legacy anchors) must equal a fresh build.

Run from the repository root:  python3 -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED = ("README.md", "README.ru.md")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def run(*args):
    return subprocess.run([sys.executable] + list(args), cwd=ROOT, capture_output=True, text=True)


def snapshot():
    out = {f: read(os.path.join(ROOT, f)) for f in GENERATED}
    g = os.path.join(ROOT, "guide")
    for n in sorted(os.listdir(g)):
        if n.endswith(".md"):
            out["guide/" + n] = read(os.path.join(g, n))
    return out


class NoLossTest(unittest.TestCase):
    def test_hard_checks_pass(self):
        r = run("tools/verify_no_loss.py")
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        self.assertIn("RESULT: PASS", r.stdout)

    def test_visuals_build_and_fit(self):
        """The generator aborts when a label does not fit its container or a font is too small."""
        r = run("tools/build_visuals.py")
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_every_diagram_has_both_languages_and_metadata(self):
        d = os.path.join(ROOT, "guide", "assets", "diagrams")
        names = sorted(os.listdir(d))
        self.assertTrue(names)
        for n in names:
            twin = n.replace(".en.svg", ".ru.svg") if n.endswith(".en.svg") else n.replace(".ru.svg", ".en.svg")
            self.assertIn(twin, names, "missing language twin for " + n)
            svg = read(os.path.join(d, n))
            for need in ("<title", "<desc", "viewBox", 'role="img"'):
                self.assertIn(need, svg, n + " lacks " + need)

    def test_numbers_excerpts_and_anchors_are_in_sync(self):
        """Computed numbers, folder tree, badges, README excerpts and legacy anchors equal a fresh build
        (no hand edits, no drift)."""
        before = snapshot()
        for tool in ("tools/build_facts.py", "tools/build_readme_excerpts.py", "tools/build_legacy_map.py",
                     "tools/build_facts.py"):
            r = run(tool)
            self.assertEqual(r.returncode, 0, tool + ": " + r.stdout[-1500:] + r.stderr[-1500:])
        self.assertEqual(before, snapshot(), "generated parts are stale: run the build tools and commit")

    def test_every_page_has_a_twin_and_backlinks(self):
        guide = os.path.join(ROOT, "guide")
        for name in sorted(os.listdir(guide)):
            if not name.endswith(".md"):
                continue
            twin = name[:-6] + ".md" if name.endswith(".ru.md") else name[:-3] + ".ru.md"
            self.assertTrue(os.path.exists(os.path.join(guide, twin)), "missing language twin for " + name)
            head = read(os.path.join(guide, name)).split("\n")[:4]
            self.assertIn(twin, head[0], "no language switch on line 1 of " + name)
            self.assertIn("README", head[2], "no back-link on line 3 of " + name)

    def test_pages_do_not_mix_languages(self):
        """English pages carry no Cyrillic prose and Russian pages no long Latin prose runs (names, paths,
        code and proper nouns excepted); a rough guard for the language-isolation rule."""
        import re
        files = ["README.md"] + ["guide/" + n for n in os.listdir(os.path.join(ROOT, "guide")) if n.endswith(".md") and not n.endswith(".ru.md")]
        allowed = ("Перспективные Научно-Исследовательские Разработки", "§", "ТОО")
        for f in files:
            text = read(os.path.join(ROOT, f))
            text = re.sub(r"`[^`]*`|```.*?```|<[^>]+>|\[[^\]]*\]\([^)]*\)", "", text, flags=re.S)
            for ln in text.split("\n"):
                for a in allowed:
                    ln = ln.replace(a, "")
                self.assertIsNone(re.search(r"[А-Яа-яЁё]{3,}", ln), "Cyrillic in English page %s: %s" % (f, ln[:100]))


if __name__ == "__main__":
    unittest.main()
