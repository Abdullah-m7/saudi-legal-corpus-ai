#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Do this corpus's cross-references actually reach anything?

The cross-reference graph names a target for 6,145 citations — a track and an
article number. Until this audit nobody had asked the only question that makes
that useful: DOES THE TARGET EXIST? A citation the corpus cannot follow is a
first-class retrieval defect. A model told to check «المادة (٢١٧) من النظام»
either lands on the provision or it does not, and the graph is what decides.

Two failure modes, and the second is the dangerous one:

  DANGLING   the target track exists and has no such article number. Visible:
             a reader who follows the link gets nothing.
  MISTARGETED  the target resolves to a real article OF THE WRONG INSTRUMENT.
             Invisible: a reader gets a confident, plausible, wrong provision.

The audit that found the second mode is the reason this file exists. Before it,
1,110 references inside implementing regulations pointed at the regulation
itself because «من النظام» was read as a self-marker, when inside a subordinate
instrument it names the PARENT LAW. They all «resolved». See
gen_corpus_cross_reference_graph.build_parent_law_map for the fix.

Read-only. Exit 0 = the measured numbers are printed; this is an audit, not a
gate, and it does not fail the build.
"""
from __future__ import annotations

import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "corpus_unified_index",
                     "corpus_unified_llm_index.jsonl")
REGISTRY = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
GRAPH = os.path.join(ROOT, "data", "corpus_cross_reference_graph",
                     "corpus_cross_reference_graph.json")
OUT = os.path.join(ROOT, "reports", "cross_reference_resolution",
                   "cross_reference_resolution.json")


def resolution_table():
    """{track_id: set(article numbers it actually holds)}.

    Built by joining the registry's per-track Arabic data_path to the unified
    index's source_layer, because the registry's track_id and the index's
    corpus key are deliberately different strings for 121 of the tracks."""
    layer = collections.defaultdict(set)
    for line in open(INDEX, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            layer[r["source_layer"]].add(r["article_number"])
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    out = {}
    for t in reg["tracks"]:
        path = (t.get("language_layers", {}).get("arabic") or {}).get("data_path")
        if path:
            base = os.path.basename(path)
            if base in layer:
                out[t["track_id"]] = layer[base]
    return out


def main():
    have = resolution_table()
    graph = json.load(open(GRAPH, encoding="utf-8"))
    refs = graph["references"]

    counts = collections.Counter()
    dangling = []
    for r in refs:
        tid, num = r.get("target_track_id"), r.get("target_article_number")
        kind = r.get("type")
        if not tid:
            counts["target_not_named"] += 1
            continue
        if tid not in have:
            counts["target_track_absent_from_index"] += 1
            continue
        if num is None:
            counts["no_article_number"] += 1
            continue
        if num in have[tid]:
            counts["resolves"] += 1
        else:
            counts["dangling"] += 1
            dangling.append(r)

    by_type = collections.Counter(r["type"] for r in refs)
    dang_by_type = collections.Counter(r["type"] for r in dangling)
    worst = collections.Counter(
        (r["target_track_id"], r["target_article_number"]) for r in dangling)

    print("references: %d over %d records" % (len(refs), graph["total_records_scanned"]))
    print("by type:      ", dict(by_type))
    print("resolution:   ", dict(counts))
    followable = counts["resolves"]
    checkable = counts["resolves"] + counts["dangling"]
    if checkable:
        print("followable:    %d of %d checkable targets (%.1f%%)"
              % (followable, checkable, 100.0 * followable / checkable))
    print("dangling by type:", dict(dang_by_type))
    print("\nworst dangling targets:")
    for (tid, num), n in worst.most_common(15):
        held = have.get(tid) or {0}
        print("   %-52s art %-5s x%-3d (track holds up to %d)"
              % (tid, num, n, max(held)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "قياسٌ لسؤالٍ لم يُسأل قبل اليوم: هل تصل إحالات المستودع إلى وجهاتها؟ "
            "رسمُ الإحالات يسمّي لكل استشهاد مساراً ورقمَ مادة، ولا يعني ذلك أن "
            "الوجهة موجودة. والإخفاق نوعان: إحالةٌ معلَّقة يراها القارئ، وإحالةٌ "
            "تصل إلى مادةٍ حقيقية في **الأداة الخطأ** — وهذه أخطر، لأن الجواب "
            "الخاطئ الواثق أضرُّ من الجواب الغائب."),
        "total_references": len(refs),
        "by_type": dict(by_type),
        "resolution": dict(counts),
        "dangling_by_type": dict(dang_by_type),
        "worst_dangling_targets": [
            {"target_track_id": t, "target_article_number": n, "citations": c,
             "target_holds_up_to": max(have.get(t) or {0})}
            for (t, n), c in worst.most_common(40)],
        "dangling": dangling,
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
