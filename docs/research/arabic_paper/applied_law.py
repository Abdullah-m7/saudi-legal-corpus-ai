#!/usr/bin/env python3
"""Which of the enacted statute book do the courts actually apply?

Two corpora exist in this repository and nowhere else together: 291 Saudi
instruments broken into 15,689 articles, and 50,666 judgments in full text.
Joining them asks a question neither can answer alone — not what the state
enacted, and not what a court decided, but how much of the first ever reaches
the second.

74% of judgments cite at least one «المادة … من نظام …», 85,124 citations in
all. This matches those citations to the registry and reports what share of
the statute book is ever applied, and how concentrated the applied part is.

Matching is deliberately conservative. A judgment writes an instrument's name
in running prose — "من نظام المحاكم التجارية الصادر بالمرسوم الملكي رقم..." —
so the captured span is trimmed at the phrases that follow a name, then
matched against the registry's Arabic titles. A citation that does not match
a registry title is counted as unmatched rather than guessed at: the registry
holds 291 instruments and the statute book is larger, so an unmatched
citation usually means an instrument this corpus does not carry.
"""

import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"

CITE = re.compile(
    r"الماد[ةه]\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+((?:نظام|لائحة|النظام|اللائحة)\s+[^\.،؛\n\)]{2,60})")

# A name in prose runs on into the rest of the sentence. Cut it here.
STOP = re.compile(
    r"\s+(?:الصادر|الصادرة|المعدل|كما|وذلك|على أن|التي|الذي|حيث|وقد|وحيث|"
    r"المبني|المشار|رقم\s*\(?م\s*/|بموجب|فإن|وأن|إذا|قررت|رأت|ونصها|ونصه|"
    r"والمادة|ومادة|لسنة|لعام)\b")

def clean(name):
    name = " ".join(name.split())
    m = STOP.search(name)
    if m:
        name = name[:m.start()]
    return name.strip(" ،.:()").strip()

def normalise(s):
    s = " ".join(str(s or "").split())
    s = re.sub(r"[ًٌٍَُِّْـ]", "", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("ة", "ه").replace("ى", "ي")
    return s

def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    titles = {}
    for t in tracks:
        ar = t.get("display_name_ar")
        if ar:
            titles[normalise(ar)] = t["track_id"]
    # longest first, so "اللائحة التنفيذية لنظام الشركات" wins over "نظام الشركات"
    order = sorted(titles, key=len, reverse=True)

    cited = collections.Counter()
    cited_docs = collections.defaultdict(set)
    unmatched = collections.Counter()
    total = matched = 0
    judgments = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            judgments += 1
            for _, raw in CITE.findall(r["text"]):
                total += 1
                name = normalise(clean(raw))
                if not name:
                    continue
                for title in order:
                    if title in name or name in title:
                        cited[titles[title]] += 1
                        cited_docs[titles[title]].add(r["id"])
                        matched += 1
                        break
                else:
                    unmatched[name[:40]] += 1

    print(f"{judgments:,} judgments, {total:,} statutory citations")
    print(f"  matched to the registry   {matched:,}  ({matched/total:.1%})")
    print(f"  no registry match         {total-matched:,}  ({(total-matched)/total:.1%})")
    print(f"\nregistry instruments: {len(titles)}")
    print(f"  ever cited by a court:  {len(cited)}  ({len(cited)/len(titles):.1%})")
    print(f"  never cited:            {len(titles)-len(cited)}")

    if cited:
        ranked = cited.most_common()
        top10 = sum(c for _, c in ranked[:10])
        print(f"\nconcentration: the top 10 instruments carry {top10:,} of "
              f"{matched:,} matched citations ({top10/matched:.1%})")
        print("\nmost-applied instruments:")
        for tid, c in ranked[:15]:
            print(f"   {c:>7,} citations  {len(cited_docs[tid]):>6,} judgments   {tid}")

    print("\nlargest unmatched names (instruments the registry does not carry):")
    for name, c in unmatched.most_common(10):
        print(f"   {c:>6,}  {name}")

    (HERE / "applied_law_results.json").write_text(json.dumps({
        "judgments": judgments, "citations": total, "matched": matched,
        "registry_instruments": len(titles), "instruments_cited": len(cited),
        "citations_by_instrument": dict(cited),
        "judgments_by_instrument": {k: len(v) for k, v in cited_docs.items()},
        "unmatched_names": dict(unmatched.most_common(200)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote applied_law_results.json")


if __name__ == "__main__":
    main()
