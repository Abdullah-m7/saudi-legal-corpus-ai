#!/usr/bin/env python3
"""What do the non-commercial judgments cite, and how does it differ?

The published record is 95 per cent commercial-court, which is what the
Ministry publishes and not what was collected: the portal's own courtTypes
axis is degree (first instance / appeal / Supreme Court), not subject, and
the sweep took all of it. But 2,541 judgments in the corpus are not from the
commercial court, and nothing in this project has ever looked at them.

They matter out of proportion to their number. 1,749 come from the Supreme
Court and the Supreme Judicial Council sitting in permanent panel, which is
to say they are principle-setting decisions, published because they settle a
point of law rather than because they closed a file.

This script profiles them against the commercial mass, using the same
extractor, matcher and voice attribution the applied-law paper used, so the
two are comparable by construction.

    python3 noncommercial_profile.py  ->  ../noncommercial_paper/profile.json
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arabic_ordinals as A            # noqa: E402
import match_instruments as M          # noqa: E402
import voice_attribution as V          # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE.parent / "noncommercial_paper" / "profile.json"
CITE = V.CITE
COMMERCIAL = "المحكمة التجارية"


def court_of():
    """id -> court name, from the index rather than the shard."""
    out = {}
    for line in (HERE / "judgments_index.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out[r["id"]] = (r.get("courtName") or "").strip()
    return out


def main():
    index, order = M.build(REGISTRY)
    reg = json.load(REGISTRY.open(encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    # The set of instruments that govern how a case is heard rather than what
    # it is about, as the applied-law paper defined it: reused, not redefined.
    procedural = M.PROCEDURAL
    size = {}
    for t in tracks:
        rc = t.get("record_counts") or {}
        v = rc.get("arabic_articles") or rc.get("total")
        if isinstance(v, int) and v > 0:
            size[t["track_id"]] = v

    courts = court_of()
    # per court group: judgments, citations, matched, procedural, instruments
    stat = collections.defaultdict(lambda: {
        "judgments": 0, "citing": 0, "citations": 0, "matched": 0,
        "procedural": 0, "instruments": collections.Counter(),
        "articles": collections.defaultdict(set), "chars": 0})

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            court = courts.get(d["id"], d.get("court", "")).strip()
            group = "commercial" if (court == COMMERCIAL
                                     or "التجاري" in court) else court
            s = stat[group]
            s["judgments"] += 1
            s["chars"] += d.get("characters") or len(d.get("text") or "")
            last = M.Recent()
            found = 0
            for art, raw in CITE.findall(d.get("text") or ""):
                s["citations"] += 1
                found += 1
                tid, kind = M.match(raw, index, order, last)
                if not tid:
                    continue
                if kind == "named":
                    last.note(tid)
                s["matched"] += 1
                s["instruments"][tid] += 1
                if tid in procedural:
                    s["procedural"] += 1
                num, _ = A.parse(art)
                if num is not None and not (tid in size and num > size[tid]):
                    s["articles"][tid].add(num)
            if found:
                s["citing"] += 1

    rows = []
    for group, s in sorted(stat.items(), key=lambda kv: -kv[1]["judgments"]):
        m = s["matched"]
        rows.append({
            "court": group,
            "judgments": s["judgments"],
            "meanChars": round(s["chars"] / s["judgments"]) if s["judgments"] else 0,
            "judgmentsCiting": s["citing"],
            "citingShare": round(100 * s["citing"] / s["judgments"], 1)
            if s["judgments"] else 0.0,
            "citations": s["citations"],
            "matched": m,
            "proceduralShare": round(100 * s["procedural"] / m, 1) if m else None,
            "distinctInstruments": len(s["instruments"]),
            "distinctArticles": sum(len(v) for v in s["articles"].values()),
            "topInstruments": s["instruments"].most_common(5),
        })

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    head = f"{'court':<42}{'judg':>7}{'chars':>8}{'cite%':>7}{'cites':>8}{'proc%':>7}{'insts':>7}"
    print(head); print("-" * len(head))
    for r in rows:
        if r["judgments"] < 5:
            continue
        print(f"{r['court'][:41]:<42}{r['judgments']:>7}{r['meanChars']:>8}"
              f"{r['citingShare']:>7}{r['matched']:>8}"
              f"{(r['proceduralShare'] if r['proceduralShare'] is not None else 0):>7}"
              f"{r['distinctInstruments']:>7}")


if __name__ == "__main__":
    main()
