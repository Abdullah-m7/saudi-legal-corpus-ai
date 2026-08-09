#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Which tracks say in their own text that they replace something the
supersession graph has no edge for?

WHY THIS EXISTS. The supersession graph is HAND-CLASSIFIED, and deliberately so:
its own policy says every edge was read and classified against documented text,
never inferred from a decree being older or from topical similarity. That is the
right policy and it has one consequence nobody had accounted for — the graph
cannot notice a supersession that arrives after it was written. It ages silently.

It aged. «نظام إيرادات الدولة» was ingested with an article 29 that says, in so
many words, that it replaces the State Revenue Law of Royal Decree M/68 — a law
this corpus holds — and the graph gained no edge, because nothing was watching.

This audit does not add edges. It reads the corpus's own article text for the two
things a Saudi instrument says when it supersedes, and reports every case the
graph does not already carry, so a human classifies it. Reporting, not inferring,
is what keeps the hand-classification policy intact.

TWO CLAUSES, AND ONLY ONE IS AN EDGE:

  NAMED       «يحل هذا النظام محل نظام مكافحة الرشوة الصادر بالمرسوم الملكي رقم 15»
              — names the instrument replaced. This is a relationship between two
              identifiable instruments and belongs in the graph.
  CONFLICT    «ويلغي كل ما يتعارض معه من أحكام»
              — names nothing at all. It repeals whatever happens to conflict.
              Recorded separately: turning it into an edge would mean inventing
              the other end.

A MEASUREMENT MISTAKE WORTH KEEPING. The first pass matched «يحل ... محل» and
reported 198 records. Reading them showed most are a DIFFERENT SENSE of the same
verb: «يعين من يحل محله» — appointing someone to stand in for an absent committee
member — and «يحل نائب الرئيس محل الرئيس». The word is identical and the meaning
is not. The discriminator is what follows «محل»: an INSTRUMENT NOUN, never a
pronoun or a person. A verb only means what its object says it means.

Read-only. Exit 0; this is an audit, not a gate.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "corpus_unified_index",
                     "corpus_unified_llm_index.jsonl")
REGISTRY = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
GRAPH = os.path.join(ROOT, "data", "corpus_supersession_graph",
                     "corpus_supersession_graph.json")
OUT = os.path.join(ROOT, "reports", "unrecorded_supersessions",
                   "unrecorded_supersessions.json")

_INSTRUMENT = (r"نظام|النظام|لائحة|اللائحة|قواعد|القواعد|تنظيم|التنظيم|"
               r"ترتيبات|الترتيبات|آلية|الآلية|ضوابط|الضوابط|تعليمات|التعليمات")

# «يحل [هذا النظام] محل <instrument> ...» — the replaced instrument is NAMED.
NAMED_RE = re.compile(
    r"يحل\s+(?:هذا\s+|هذه\s+)?(?:النظام|اللائحة|القواعد|التنظيم|الترتيبات|الآلية|الضوابط)?\s*"
    r"محل\s+(?:" + _INSTRUMENT + r")\b"
    r"|(?:يُلغى|يلغى|وتُلغى|وتلغى)\s+(?:" + _INSTRUMENT + r")\s+[ء-ي]")
# «ويلغي كل ما يتعارض معه من أحكام» — names nothing.
CONFLICT_RE = re.compile(
    r"(?:يلغي|يُلغي|ويلغي|ويُلغي|وتلغي|وتُلغي|تلغي)\s+"
    r"(?:هذا\s+النظام\s+|هذه\s+اللائحة\s+)?(?:كل|جميع)?\s*ما\s+يتعارض")


def track_of_corpus_component():
    """{(corpus, law_component): track_id} via the registry's Arabic data_path."""
    layer = {}
    for line in open(INDEX, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            layer[r["source_layer"]] = (r["corpus"], r["law_component"])
    out = {}
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    for t in reg["tracks"]:
        path = (t.get("language_layers", {}).get("arabic") or {}).get("data_path")
        if path:
            key = layer.get(os.path.basename(path))
            if key:
                out.setdefault(key, t["track_id"])
    return out


def main():
    graph = json.load(open(GRAPH, encoding="utf-8"))
    with_edge = {e["from_track_id"] for e in graph["edges"]}
    # A track can be ACCOUNTED FOR without carrying an edge: the graph's
    # ambiguous_or_excluded_cases section exists precisely for signals that are
    # real but must not become edges — e.g. an implementing regulation that
    # restates its parent law's repeal clause, which repeals nothing itself.
    # Counting those as "unrecorded" would keep re-reporting a case a human has
    # already decided, and an audit that never goes quiet stops being read.
    excluded = {t for c in graph.get("ambiguous_or_excluded_cases", [])
                for t in c.get("tracks_involved", [])}
    t_of = track_of_corpus_component()

    named, conflict = [], []
    for line in open(INDEX, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        text = r.get("text_ar") or ""
        tid = t_of.get((r["corpus"], r["law_component"]))
        row = {"track_id": tid, "corpus": r["corpus"],
               "law_component": r["law_component"],
               "article_number": r["article_number"],
               "unit_label_ar": r.get("unit_label_ar"),
               "record_id": r["record_id"]}
        m = NAMED_RE.search(text)
        if m:
            named.append(dict(row, clause=text[max(0, m.start() - 20):m.start() + 220].strip()))
            continue
        m = CONFLICT_RE.search(text)
        if m:
            conflict.append(dict(row, clause=text[max(0, m.start() - 20):m.start() + 160].strip()))

    unrecorded = [r for r in named if r["track_id"]
                  and r["track_id"] not in with_edge
                  and r["track_id"] not in excluded]
    recorded = [r for r in named if r["track_id"] in with_edge]
    set_aside = [r for r in named if r["track_id"] and r["track_id"] not in with_edge
                 and r["track_id"] in excluded]

    print("supersession graph: %d edges over %d tracks" % (len(graph["edges"]), len(with_edge)))
    print("articles naming a replaced instrument: %d over %d tracks"
          % (len(named), len({r['track_id'] for r in named if r['track_id']})))
    print("  already carried by an edge:  %d" % len(recorded))
    print("  set aside on purpose (ambiguous_or_excluded_cases): %d" % len(set_aside))
    print("  UNRECORDED (needs classifying): %d over %d tracks"
          % (len(unrecorded), len({r['track_id'] for r in unrecorded})))
    print("conflict-repeal clauses naming nothing: %d (not edge candidates)" % len(conflict))
    print("\nunrecorded, by track:")
    for r in unrecorded[:30]:
        print("   %-46s %s %s" % (r["track_id"], r.get("unit_label_ar") or r["article_number"],
                                  re.sub(r"\s+", " ", r["clause"])[:96]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "رسمُ النسخ في هذا المستودع **مُصنَّف يدوياً** عن قصد: سياستُه تقول إن كل ضلع "
            "قُرئ وصُنِّف مقابل نصٍّ موثَّق، لا استُنتج من قِدَم مرسوم ولا من تشابه موضوعي. "
            "وهذه سياسةٌ صحيحة، ولها أثرٌ واحد لم يُحسب: **الرسم لا يستطيع أن يلاحظ نسخاً "
            "وصل بعد كتابته، فيتقادم بصمت**. وقد تقادم فعلاً. هذا التدقيق **لا يضيف "
            "أضلاعاً**؛ يقرأ نصوص المواد عن العبارتين اللتين تقولهما الأداة السعودية حين "
            "تنسخ، ويعرض ما لا يحمله الرسم ليُصنِّفه إنسان. **العرضُ لا الاستنتاج** هو ما "
            "يُبقي سياسة التصنيف اليدوي سليمة."),
        "graph_edges": len(graph["edges"]),
        "graph_tracks_with_edges": len(with_edge),
        "articles_naming_a_replaced_instrument": len(named),
        "already_carried_by_an_edge": len(recorded),
        "set_aside_in_ambiguous_or_excluded_cases": len(set_aside),
        "set_aside": set_aside,
        "unrecorded_count": len(unrecorded),
        "conflict_repeal_clauses_naming_nothing": len(conflict),
        "unrecorded": unrecorded,
        "conflict_repeal_only": conflict,
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
