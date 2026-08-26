#!/usr/bin/env python3
"""Who cites the statute — the parties, or the court?

The concentration measured in applied_law.py counts every citation in a
judgment's text. But a judgment's text is not one voice. It opens with the
parties' pleadings, quoted at length, and only later reaches the bench's own
reasoning. A statute cited by a claimant's advocate is not a statute the
court applied.

The API cannot make this distinction: judgmentFacts, judgmentReasons and
judgmentRuling exist as fields and are null in all 50,666 records, exactly
like isAppeal. Everything arrives in one block.

The documents carry their own structure instead. Saudi commercial judgments
run الوقائع → الأسباب → حكمت الدائرة, and those headings are present in 63%,
64% and 83% of the corpus. This segments on them and counts citations
separately in each part.

Segments
  pleadings   from the start (or الوقائع) to the الأسباب heading
  reasoning   from الأسباب to حكمت الدائرة
  operative   from حكمت الدائرة to the end

A judgment whose headings are missing or out of order is not segmented and
is counted as unsegmentable rather than forced into a shape it does not have.
"""

import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"

FACTS = re.compile(r"الوقائع\s*[:：]")
REASONS = re.compile(r"(?<!فلهذه\s)الأسباب\s*[:：]")
RULING = re.compile(r"حكمت\s+الدائرة")

CITE = re.compile(
    r"الماد[ةه]\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+((?:نظام|لائحة|النظام|اللائحة)\s+[^\.،؛\n\)]{2,60})")
STOP = re.compile(
    r"\s+(?:الصادر|الصادرة|المعدل|كما|وذلك|على أن|التي|الذي|حيث|وقد|وحيث|"
    r"المبني|المشار|رقم\s*\(?م\s*/|بموجب|فإن|وأن|إذا|قررت|رأت|ونصها|ونصه|"
    r"والمادة|ومادة|لسنة|لعام)\b")


def normalise(s):
    s = " ".join(str(s or "").split())
    s = re.sub(r"[ًٌٍَُِّْـ]", "", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return s.replace("ة", "ه").replace("ى", "ي")


def clean(name):
    name = " ".join(name.split())
    m = STOP.search(name)
    if m:
        name = name[:m.start()]
    return name.strip(" ،.:()").strip()


def segment(text):
    """Return (pleadings, reasoning, operative) or None if the shape is absent."""
    r = REASONS.search(text)
    k = RULING.search(text, r.end() if r else 0)
    if not r or not k:
        return None
    f = FACTS.search(text)
    start = f.start() if f and f.start() < r.start() else 0
    return text[start:r.start()], text[r.end():k.start()], text[k.start():]


def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    titles = {normalise(t["display_name_ar"]): t["track_id"]
              for t in tracks if t.get("display_name_ar")}
    order = sorted(titles, key=len, reverse=True)

    PROCEDURAL = {
        "commercial_courts_law", "commercial_courts_implementing_regulation",
        "sharia_procedure_law", "sharia_procedure_implementing_regulation",
        "evidence_law", "evidence_procedural_manuals", "arbitration_law",
        "arbitration_implementing_regulation",
        "law_practice_implementing_regulation", "enforcement_law",
        "enforcement_implementing_regulation",
    }

    def cites(part):
        out = []
        for _, raw in CITE.findall(part):
            name = normalise(clean(raw))
            if not name:
                continue
            for title in order:
                if title in name or name in title:
                    out.append(titles[title])
                    break
        return out

    counts = {k: collections.Counter() for k in ("pleadings", "reasoning", "operative")}
    n = segmented = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            n += 1
            parts = segment(json.loads(line)["text"])
            if not parts:
                continue
            segmented += 1
            for key, part in zip(("pleadings", "reasoning", "operative"), parts):
                counts[key].update(cites(part))

    print(f"{n:,} judgments; {segmented:,} segmented ({segmented/n:.1%}); "
          f"{n-segmented:,} lack the headings and are excluded\n")
    print(f"{'segment':<12} {'citations':>10} {'instruments':>12} "
          f"{'procedural':>11} {'top-10 share':>13}")
    for key in ("pleadings", "reasoning", "operative"):
        c = counts[key]
        tot = sum(c.values())
        if not tot:
            print(f"{key:<12} {0:>10}")
            continue
        proc = sum(v for k, v in c.items() if k in PROCEDURAL)
        top10 = sum(v for _, v in c.most_common(10))
        print(f"{key:<12} {tot:>10,} {len(c):>12} "
              f"{proc/tot:>10.1%} {top10/tot:>12.1%}")

    print("\nmost-cited, by segment:")
    for key in ("pleadings", "reasoning"):
        print(f"  — {key}")
        for tid, v in counts[key].most_common(6):
            print(f"      {v:>7,}  {tid}")

    (HERE / "cite_by_voice_results.json").write_text(json.dumps(
        {"judgments": n, "segmented": segmented,
         "counts": {k: dict(v) for k, v in counts.items()}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote cite_by_voice_results.json")


if __name__ == "__main__":
    main()
