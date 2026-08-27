#!/usr/bin/env python3
"""The instrument-level join, with the matcher that reads the whole citation.

Same measurement as applied_law.py, on match_instruments.py. Reports named
and anaphoric matches separately: a citation that says which instrument it
means is a stronger observation than one resolved from context, and the paper
should be able to quote either.
"""

import collections
import json
import re
from pathlib import Path

import match_instruments as M

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
CITE = re.compile(
    r"الماد[ةه]\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+((?:نظام|لائحة|النظام|اللائحة)[^\.،؛\n\)]{0,60})")

PROCEDURAL = {
    "commercial_courts_law", "commercial_courts_implementing_regulation",
    "sharia_procedure_law", "sharia_procedure_implementing_regulation",
    "evidence_law", "evidence_procedural_manuals", "arbitration_law",
    "arbitration_implementing_regulation",
    "law_practice_implementing_regulation", "enforcement_law",
    "enforcement_implementing_regulation", "bankruptcy_case_rules",
    "evidence_expertise_rules",
}


def main():
    index, order = M.build(REGISTRY)
    named = collections.Counter()
    anaph = collections.Counter()
    docs = collections.defaultdict(set)
    unmatched = collections.Counter()
    total = n = citing = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            last = M.Recent()
            hits = CITE.findall(r["text"])
            citing += bool(hits)
            for _, raw in hits:
                total += 1
                tid, kind = M.match(raw, index, order, last)
                if kind == "named":
                    named[tid] += 1
                    docs[tid].add(r["id"])
                    last.note(tid)
                elif kind == "anaphoric":
                    anaph[tid] += 1
                    docs[tid].add(r["id"])
                else:
                    unmatched[M.normalise(M.clean(raw))[:40]] += 1

    matched = sum(named.values()) + sum(anaph.values())
    cited = set(named) | set(anaph)
    combined = collections.Counter(named)
    combined.update(anaph)

    print(f"{n:,} judgments, {citing:,} of them citing a statute "
          f"({citing/n:.1%}), {total:,} citations")
    print(f"  named      {sum(named.values()):>8,}  ({sum(named.values())/total:>5.1%})")
    print(f"  anaphoric  {sum(anaph.values()):>8,}  ({sum(anaph.values())/total:>5.1%})")
    print(f"  unmatched  {total-matched:>8,}  ({(total-matched)/total:>5.1%})")
    print(f"\n{len(index):,} title variants over {len(set(index.values()))} instruments")
    print(f"  cited at least once: {len(cited)}  "
          f"({len(cited)/len(set(index.values())):.1%})")
    print(f"  never cited:         {len(set(index.values()))-len(cited)}")

    proc = sum(v for k, v in combined.items() if k in PROCEDURAL)
    print(f"\nprocedural share: {proc:,}/{matched:,} = {proc/matched:.1%}")
    ranked = combined.most_common()
    for k in (1, 5, 10, 20):
        print(f"  top {k:>2}: {sum(v for _, v in ranked[:k])/matched:.1%}")
    print("\nmost-applied:")
    for tid, c in ranked[:12]:
        print(f"   {c:>7,}  named {named[tid]:>7,}  anaphoric {anaph[tid]:>6,}  {tid}")
    print("\nlargest remaining unmatched:")
    for name, c in unmatched.most_common(8):
        print(f"   {c:>5,}  {name}")

    (HERE / "applied_law_v2_results.json").write_text(json.dumps(
        {"judgments": n, "judgments_citing": citing, "citations": total,
         "named": dict(named), "anaphoric": dict(anaph),
         "judgments_by_instrument": {k: len(v) for k, v in docs.items()},
         "unmatched": dict(unmatched.most_common(300))},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote applied_law_v2_results.json")


if __name__ == "__main__":
    main()
