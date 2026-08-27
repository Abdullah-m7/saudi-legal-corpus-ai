#!/usr/bin/env python3
"""A compact index over the corpus, so a check runs in a second.

The citator stores one file per article and the busiest is 22 MB. That is the
right shape for reading an article and the wrong shape for answering twenty
questions about a draft. This reduces each article to what a check needs —
counts, the voice profile, the appellate fate of the judgments applying it,
and the articles that travel with it — and writes files small enough to load
whole.

  articles.json    every article the courts have cited, with its neighbours
  judgments.json   every judgment in the corpus, not merely every judgment in
                   the citator: a judgment that cites no statute still exists,
                   and a draft may rely on it

Judgment numbers are not unique — the same number recurs across courts and
years — so the judgment index maps a number to every record carrying it, and
the checker reports all of them rather than guessing which one was meant.
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CITATOR = HERE.parent / "citator"
JUDGMENTS = HERE.parent / "arabic_paper" / "judgments"
OUT = HERE / "index"
sys.path.insert(0, str(HERE.parent / "arabic_paper"))

import appellate_outcome as AO      # noqa: E402

CO_KEEP = 8          # neighbours worth naming
CO_MIN = 0.05        # and only where they share 5% of the article's judgments


def articles_index():
    """One pass over the citator: facts per article, and its judgment set."""
    index = json.loads((CITATOR / "index.json").read_text(encoding="utf-8"))
    articles, sets = {}, {}
    for inst in index["by_instrument"]:
        tid = inst["track_id"]
        meta = json.loads((CITATOR / "instruments" / f"{tid}.json").read_text(
            encoding="utf-8"))
        for num in meta["articles"]:
            d = json.loads((CITATOR / "articles" / tid / f"{num}.json").read_text(
                encoding="utf-8"))
            key = f"{tid}/{num}"
            sets[key] = {e["judgment_id"] for e in d["judgments"]}
            articles[key] = {
                "instrument": d["instrument"], "label": d["label"],
                "section": d.get("section"),
                "article_number": d["article_number"],
                "legal_status": d.get("legal_status"),
                "official_text": d.get("official_text"),
                "citations": d["citations"], "judgments": len(sets[key]),
                "by_voice": d["by_voice"],
                "recital_by_court": d.get("recital_by_court", 0),
                "by_appeal": d.get("by_appeal", {}),
                "file": f"articles/{tid}/{num}.json",
            }
    return articles, sets


def neighbours(articles, sets):
    """Which articles are cited in the same judgments, and how often."""
    keys = [k for k in sets if sets[k]]
    for key in keys:
        mine = sets[key]
        near = sorted(
            ((len(mine & sets[o]), o) for o in keys if o != key),
            reverse=True)
        articles[key]["neighbours"] = [
            {"key": o, "shared": s, "share": s / len(mine)}
            for s, o in near[:CO_KEEP] if s / len(mine) >= CO_MIN]


def judgments_index():
    """Every judgment in the corpus, with what became of it on appeal."""
    out = collections.defaultdict(list)
    n = 0
    for shard in sorted(JUDGMENTS.glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            appeal_text = (r.get("sections") or {}).get("appealTextofRulling")
            out[r["judgment_number"]].append({
                "id": r["id"], "court": r["court"], "city": r["city"],
                "date": r["hijri_date"],
                "appeal": (AO.outcome(appeal_text)[0] if appeal_text
                           else "no_appeal"),
            })
    return out, n


def main():
    OUT.mkdir(exist_ok=True)
    articles, sets = articles_index()
    neighbours(articles, sets)
    judgments, n = judgments_index()

    (OUT / "articles.json").write_text(
        json.dumps(articles, ensure_ascii=False), encoding="utf-8")
    (OUT / "judgments.json").write_text(
        json.dumps(judgments, ensure_ascii=False), encoding="utf-8")

    dupes = sum(1 for v in judgments.values() if len(v) > 1)
    print(f"{len(articles):,} articles")
    print(f"{n:,} judgments under {len(judgments):,} distinct numbers "
          f"({dupes:,} numbers borne by more than one judgment)")
    for f in ("articles.json", "judgments.json"):
        print(f"  {f:<18}{(OUT / f).stat().st_size/1e6:>8.1f} MB")


if __name__ == "__main__":
    main()
