#!/usr/bin/env python3
"""Which words does a Saudi court actually use when it construes a term?

The search over the tax boards' codices earlier stalled on a guess: a list of
phrases a committee *might* use when it picks between two definitions. A wrong
guess there produces a zero, and a zero from a broken search reads exactly
like a finding.

With the full corpus this stops being a guess. Count how often each candidate
phrase appears across 50,666 judgments and the corpus reports its own idiom:
phrases the courts never use score zero and are dropped, phrases they use
constantly become the search terms for the next pass.

Streams shard by shard; the corpus does not fit comfortably in memory.
"""

import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARDS = sorted((HERE / "judgments").glob("*.jsonl"))

CANDIDATES = {
    "construction — naming a meaning": [
        "المقصود بـ", "المقصود به", "المراد بـ", "في مفهوم", "بمفهوم",
        "بمدلول", "مدلول", "تعريف", "التعريف", "عرّف", "عرفت المادة",
        "وفق تعريف", "المعرّف في", "بحسب تعريف",
    ],
    "conflict between texts": [
        "تعارض", "التعارض", "تعارض النصوص", "الترجيح", "ترجيح",
        "الخاص يقيد العام", "يقيد العام", "العام والخاص", "التخصيص",
        "النص الخاص", "النص العام", "اللاحق ينسخ", "الأحدث",
    ],
    "characterisation of the claim": [
        "التكييف", "تكييف الدعوى", "التكييف النظامي", "التكييف القانوني",
        "تكييف العلاقة", "وصف العلاقة",
    ],
    "scope of an instrument": [
        "نطاق تطبيق", "نطاق سريان", "مجال التطبيق", "يسري هذا النظام",
        "لا يسري", "خارج نطاق",
    ],
    "the instruments behind the four conflicting terms": [
        "نظام العمل", "نظام المنافسة", "نظام التستر", "نظام التأمينات",
        "نظام ضريبة الدخل", "نظام التجارة الإلكترونية", "نظام الشركات",
        "نظام السوق المالية",
    ],
}

def main():
    docs = collections.Counter()
    hits = collections.Counter()
    total = 0
    phrases = [p for group in CANDIDATES.values() for p in group]
    for shard in SHARDS:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            text = json.loads(line)["text"]
            total += 1
            for p in phrases:
                n = text.count(p)
                if n:
                    docs[p] += 1
                    hits[p] += n

    print(f"census over {total:,} judgments\n")
    for group, items in CANDIDATES.items():
        print(f"── {group}")
        for p in sorted(items, key=lambda x: -docs[x]):
            share = docs[p] / total if total else 0
            flag = "  ← never used" if docs[p] == 0 else ""
            print(f"   {docs[p]:>6,} judgments ({share:>6.2%})  {hits[p]:>8,} times   «{p}»{flag}")
        print()

    out = HERE / "vocabulary_census.json"
    out.write_text(json.dumps(
        {"judgments": total,
         "documents": dict(docs), "occurrences": dict(hits)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
