#!/usr/bin/env python3
"""References-and-campaign layer of the UAP graph (added 20 Nov 2026).

Why a separate builder: the repository's regression gate (tools/verify_no_loss.py, check H9)
fails when any file that existed at tag pre-showcase-2026-11 changes, and that includes
build_blueprint.py, uap_kumu.json, README.md and preview.html in this folder. This script
therefore leaves all of them untouched. It

  1. re-runs build_blueprint.py and stops if uap_kumu.json would change (the base must be fresh),
  2. loads uap_kumu.json as the base graph,
  3. exec()s fragments/agentJ_references_campaign.py with the same E() / C() helpers
     (first definition of an id wins, exactly as in build_blueprint.py),
  4. checks the same invariants (0 orphans, 0 dangling edges, 100 % RU labels and descriptions),
  5. writes uap_references_kumu.json = the layer ONLY (its nodes, its edges, "patches" for base
     nodes, and the name and SHA-256 of the base file). The base graph is not copied into it.
     preview_references.html loads both files and merges them by id.

To fold the layer into the main graph later: add one exec() line for the fragment to
build_blueprint.py, rebuild, update the two counts in README.md, run the tools/ generators,
and record an H9 waiver. That is an owner decision; it is not done here.

Standard library only. Run from anywhere:  python3 graph/build_references_layer.py
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
BASE = HERE / "uap_kumu.json"
OUT = HERE / "uap_references_kumu.json"

before = hashlib.sha256(BASE.read_bytes()).hexdigest()
r = subprocess.run([sys.executable, str(HERE / "build_blueprint.py")], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit("build_blueprint.py failed:\n" + r.stdout[-1500:] + r.stderr[-1500:])
if hashlib.sha256(BASE.read_bytes()).hexdigest() != before:
    sys.exit("uap_kumu.json was stale and has been rebuilt by build_blueprint.py; review that change first, then run again.")

base = json.loads(BASE.read_text(encoding="utf-8"))
elements = list(base["elements"])
connections = list(base["connections"])
_seen_ids = {e["id"] for e in elements}
_base_n, _base_c = len(elements), len(connections)
_dup_definitions = []
_patches = {}

TYPE_ICONS = {"source": "📜", "claim": "❓", "campaign": "📣", "dataset": "🗂️", "event": "📅", "cluster": "🎯", "fact": "🧪"}


def E(eid, label, etype, label_ru=None, description_ru=None, **kwargs):
    """Same contract as build_blueprint.E: first definition of an id wins."""
    if eid in _seen_ids:
        _dup_definitions.append(eid)
        return
    _seen_ids.add(eid)
    e = {"id": eid, "label": label, "type": etype, "icon": TYPE_ICONS.get(etype, "•")}
    if label_ru:
        e["labelRu"] = label_ru
    if description_ru:
        e["descriptionRu"] = description_ru
    e.update(kwargs)
    e.setdefault("tags", [etype])
    e["layer"] = "references-2026-11-20"
    elements.append(e)


def C(efrom, eto, ctype="related-to", direction="directed", **kwargs):
    c = {"from": efrom, "to": eto, "type": ctype, "direction": direction, "layer": "references-2026-11-20"}
    c.update(kwargs)
    connections.append(c)


def P(eid, **props):
    """Extra properties for a base node, written under "patches" (the base file is not touched)."""
    _patches.setdefault(eid, {}).update(props)


exec((HERE / "fragments" / "agentJ_references_campaign.py").read_text(encoding="utf-8"))

known = {e["id"] for e in elements}
missing_patch = sorted(set(_patches) - known)
dangling = [(c["from"], c["to"], c["type"]) for c in connections if c["from"] not in known or c["to"] not in known]
linked = {c["from"] for c in connections} | {c["to"] for c in connections}
orphans = sorted(known - linked)
no_ru = [e["id"] for e in elements if not e.get("labelRu") or not e.get("descriptionRu")]
new = elements[_base_n:]
types = {}
for e in new:
    types[e["type"]] = types.get(e["type"], 0) + 1
etypes = {}
for c in connections[_base_c:]:
    etypes[c["type"]] = etypes.get(c["type"], 0) + 1

# The output holds ONLY the layer. The base graph is not copied: the viewer (and any other reader)
# loads uap_kumu.json and merges by id. "patches" are extra properties for base nodes.
OUT.write_text(json.dumps({"schema": "asrp-graph-layer/1.0", "base": BASE.name, "base_sha256": before,
                           "base_counts": {"elements": _base_n, "connections": _base_c},
                           "patches": _patches, "elements": new, "connections": connections[_base_c:]},
                          ensure_ascii=False, indent=2), encoding="utf-8")
print("Wrote %s" % OUT)
print("  base        : %d elements, %d connections (uap_kumu.json, unchanged)" % (_base_n, _base_c))
print("  layer       : +%d elements, +%d connections" % (len(new), len(connections) - _base_c))
print("  total       : %d elements, %d connections" % (len(elements), len(connections)))
print("  new by type : %s" % ", ".join("%s %d" % kv for kv in sorted(types.items(), key=lambda x: -x[1])))
print("  new edges   : %s" % ", ".join("%s %d" % kv for kv in sorted(etypes.items(), key=lambda x: -x[1])))
print("  id reuse    : %d definitions skipped because the id already exists (%s)" % (len(_dup_definitions), ", ".join(_dup_definitions) or "none"))
print("  orphans %d, dangling %d, without RU text %d, patches to unknown ids %d" % (len(orphans), len(dangling), len(no_ru), len(missing_patch)))
problems = orphans + ["%s -[%s]-> %s" % d for d in dangling] + no_ru + missing_patch
if problems:
    sys.exit("INVARIANT FAILED:\n  " + "\n  ".join(problems[:40]))
