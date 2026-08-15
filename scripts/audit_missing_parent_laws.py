#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Which parent laws does this corpus CITE but not hold — and can it get them?

THE STRONGEST KIND OF GAP EVIDENCE. Every other coverage audit in this repository
reasons from the outside in: it asks a source what exists and compares. This one
reasons from the inside out. A held regulation opens by defining «النظام: نظام
كذا», and if no track carries that title then the corpus is telling you, in its
own text, that it is missing the law it implements. That is not a guess about
what might be absent; it is a citation with nothing on the other end.

WHERE THE LIST COMES FROM. scripts/gen_corpus_cross_reference_graph.py records,
per subordinate track, the evidence its parent was resolved from. The tracks
marked `self_declared_name_matches_no_held_law` named a parent and matched no
held title. This audit takes that list, counts how many citations each one
strands, and asks the archive index whether the named law is reachable at all.

AND THE ANSWER IS USUALLY NO, FOR ONE MEASURABLE REASON. The gazette's
ADDRESSABLE page archive effectively begins in 2021: of the 9,448 pages this
corpus has indexed, 457 — 4.8 per cent — carry a publication date before 2021,
about fifty a year across nine years, against roughly nineteen hundred a year
after. Older issues exist as whole-issue PDFs, not as per-document pages. So an
instrument published before 2021 is generally NOT obtainable through the gazette
channel at all, however thoroughly that channel is swept.

That bounds every coverage claim this repository makes. "The gazette archive is
exhausted" has always meant, and can only ever mean, exhausted from 2021 onward.
Instruments older than that must come from a different official source — and the
ones this corpus has tried are documented: laws.boe.gov.sa unreachable from this
sandbox, ministry portals partially reachable. Saying so is the point; a gap
whose cause is measured can be argued with, and one that is merely noticed
cannot.

Read-only. Offline — it reads only artifacts this corpus already holds. Exit 0;
an audit, not a gate.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "data", "corpus_cross_reference_graph",
                     "corpus_cross_reference_graph.json")
INDEX = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                     "gazette_title_index.json")
REGISTRY = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
OUT = os.path.join(ROOT, "reports", "missing_parent_laws",
                   "missing_parent_laws.json")

ADDRESSABLE_ARCHIVE_BEGINS = 2021

# Two of the names the graph reports are not law titles at all — they are a
# sentence the definition-parser mistook for one. Named here rather than
# silently filtered, so the count of real gaps stays honest and the parser's
# failure stays visible.
NOT_A_LAW_NAME = {
    "public_entities_governance_guide",
    "treaty_gcc_payment_systems_linkage",
}


def _norm(s):
    s = re.sub(r"[ً-ْـ]", "", s or "")
    s = (s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
          .replace("ة", "ه").replace("ى", "ي"))
    return re.sub(r"\s+", " ", s).strip()


def _declared_names():
    """Re-derive each track's own «النظام: …» from the generator, so this audit
    and the graph can never disagree about what a track said."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_corpus_cross_reference_graph",
        os.path.join(ROOT, "scripts", "gen_corpus_cross_reference_graph.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    registry = mod.load_registry()
    rows = mod.load_index()
    l2t = mod._load_layer_to_track_id(registry)
    return {k: v[0] for k, v in mod._self_declared_parent_names(rows, l2t).items()}


def main():
    graph = json.load(open(GRAPH, encoding="utf-8"))
    res = graph.get("parent_law_resolution") or {}
    basis = {}
    for tid in res.get("unresolved_tracks", []):
        basis[tid] = None
    by_evidence = res.get("by_evidence", {})

    # the tracks whose declared parent matched nothing
    names = _declared_names()
    unresolved = set(res.get("unresolved_tracks", []))
    named_but_missing = {t: names[t] for t in sorted(unresolved) if t in names}

    stranded = collections.Counter(
        r["source_track_id"] for r in graph["references"]
        if r["type"] == "parent_law_unresolved")

    index = json.load(open(INDEX, encoding="utf-8"))["index"]
    years = collections.Counter((v.get("date") or "????")[:4] for v in index.values())
    total = sum(years.values())
    pre = sum(v for k, v in years.items()
              if k.isdigit() and int(k) < ADDRESSABLE_ARCHIVE_BEGINS)

    print("parent laws NAMED by a held instrument and not held: %d"
          % len(named_but_missing))
    rows = []
    for tid, name in named_but_missing.items():
        key = _norm(name)
        hits = [(k, v) for k, v in index.items() if key[:28] in _norm(v["title"])]
        law_pages = [(k, v) for k, v in hits if _norm(v["title"]).startswith("نظام")]
        row = {
            "citing_track": tid,
            "declared_parent_name_ar": name,
            "stranded_citations": stranded.get(tid, 0),
            "pages_in_archive_index_mentioning_it": len(hits),
            "law_titled_pages_in_archive_index": [
                {"page_id": k, "date": v.get("date"), "title": v["title"]}
                for k, v in law_pages],
            "is_a_law_name": tid not in NOT_A_LAW_NAME,
        }
        rows.append(row)
        flag = "" if row["is_a_law_name"] else "   [not a law name — parser artefact]"
        print("   %-52s %2d stranded | %d law page(s)%s\n        «%s»"
              % (tid, row["stranded_citations"],
                 len(row["law_titled_pages_in_archive_index"]), flag, name[:88]))

    real = [r for r in rows if r["is_a_law_name"]]
    reachable = [r for r in real if r["law_titled_pages_in_archive_index"]]
    # Rolled up by LAW, not by citer: «نظام البلديات والقرى» is named by two
    # tracks and is one missing law, and counting it twice would overstate the
    # gap in exactly the direction that flatters nobody.
    distinct = {}
    for r in real:
        distinct.setdefault(_norm(r["declared_parent_name_ar"]), {
            "declared_parent_name_ar": r["declared_parent_name_ar"],
            "cited_by": [], "stranded_citations": 0,
            "reachable_in_archive_index": bool(r["law_titled_pages_in_archive_index"]),
        })
        d = distinct[_norm(r["declared_parent_name_ar"])]
        d["cited_by"].append(r["citing_track"])
        d["stranded_citations"] += r["stranded_citations"]
    print("\nDISTINCT missing parent laws: %d (named by %d tracks) | reachable: %d"
          % (len(distinct), len(real), len(reachable)))
    for d in distinct.values():
        print("   %-2d citation(s) stranded | cited by %s\n        «%s»"
              % (d["stranded_citations"], ", ".join(d["cited_by"]),
                 d["declared_parent_name_ar"][:86]))
    print("\nWHY: the gazette's addressable archive effectively begins in %d —"
          % ADDRESSABLE_ARCHIVE_BEGINS)
    print("     %d of %d indexed pages (%.1f%%) predate it, ~%d a year across nine"
          % (pre, total, 100.0 * pre / total, pre // 9))
    print("     years, against ~1,900 a year after. Older issues are whole-issue")
    print("     PDFs, not per-document pages, so a pre-%d instrument is generally"
          % ADDRESSABLE_ARCHIVE_BEGINS)
    print("     NOT obtainable through this channel however well it is swept.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "**أقوى أنواع أدلة النقص**: بقيةُ التدقيقات تسأل مصدراً عمّا يوجد ثم تقارن؛ "
            "وهذا يستنطق المستودعَ نفسه. لائحةٌ محمولة تفتتح بـ«النظام: نظام كذا»، فإن لم "
            "يحمل أيُّ مسارٍ ذلك العنوان **فالمستودع يقول بنصّه إنه ينقصه النظامُ الذي "
            "ينفّذه** — لا تخميناً عمّا قد يغيب، بل **استشهادٌ لا شيء في طرفه الآخر**. "
            "**والسببُ مقيس**: أرشيفُ الجريدة القابل للعنونة يبدأ عملياً في 2021 — %d من "
            "%d صفحة مفهرسة (%.1f%%) تسبقه، بمعدل خمسين في السنة عبر تسع سنين مقابل نحو "
            "ألفٍ وتسعمئة بعدها. فالأداةُ الأقدم من 2021 **غير قابلة للحصول عبر هذه القناة "
            "مهما استُقصيت**. وهذا **يحدّ كلَّ ادّعاء تغطية**: «استُنفد الأرشيف» كانت ولا "
            "تزال تعني **مستنفَداً من 2021 فصاعداً**."
            % (pre, total, 100.0 * pre / total)),
        "addressable_archive_begins": ADDRESSABLE_ARCHIVE_BEGINS,
        "archive_pages_by_year": dict(sorted(years.items())),
        "pages_before_the_archive_begins": pre,
        "pages_total": total,
        "parent_law_resolution_by_evidence": by_evidence,
        "named_but_not_held": rows,
        "real_missing_parent_laws": len(real),
        "distinct_missing_parent_laws": list(distinct.values()),
        "reachable_in_the_archive_index": len(reachable),
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
