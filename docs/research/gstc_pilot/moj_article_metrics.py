#!/usr/bin/env python3
"""Score the published extractor against the article-level MOJ gold.

Everything measured before this was per occurrence of the word «مادة», read
through a 1300-character window. This scores the same extractor against 32
whole judgments read end to end, and reports at both units:

  occurrence   every citation in the text, the unit the pilot has always used
  article      one row per (judgment, instrument, article), the unit the
               HILJ paper's claim about *which articles a court applies*
               actually needs

The gold also records citations that lie OUTSIDE the sampling frame: articles
under a plural «المواد», a second article sharing one head noun, an article
numbered with «اللائحة» as its head noun, a bare «(1/29) من نظام الإثبات».
Those never enter a frame-based precision or recall, so they are reported
separately as the frame's own blind spot.

    python3 moj_article_metrics.py
"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
sys.path.insert(0, str(HERE.parent / "canon"))
from moj_splits import judgments                  # noqa: E402
import arabic_ordinals as A                       # noqa: E402
import match_instruments as M                     # noqa: E402
import voice_attribution as V                     # noqa: E402

GOLD = HERE / "moj_article_gold.json"
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "moj_article_metrics_results.json"


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - r) / d * 100, (c + r) / d * 100)


def pct(k, n):
    if not n:
        return "     —"
    lo, hi = wilson(k, n)
    return f"{k/n*100:5.1f}% [{lo:.1f}, {hi:.1f}]"


def gold_key(row, index, order, last):
    """(article, track) for a human row, resolved through the same matcher."""
    num = row.get("articleNumber")
    if num is None or not row.get("instrument"):
        return None
    tid, kind = M.match(row["instrument"], index, order, last)
    if tid and kind == "named":
        last.note(tid)
    return (num, tid) if tid else (num, None)


def extractor_keys(text, index, order):
    """What the published pipeline reports for one judgment, in text order."""
    last = M.Recent()
    keys = []
    for art, raw in V.CITE.findall(text):
        tid, kind = M.match(raw, index, order, last)
        if tid and kind == "named":
            last.note(tid)
        num, _ = A.parse(art)
        keys.append((num, tid))
    return keys


def main():
    spec = json.loads(GOLD.read_text(encoding="utf-8"))
    rows = spec["rows"]
    if not rows:
        sys.exit("no rows merged into moj_article_gold.json yet")
    ids = {c["id"] for c in spec["judgments"]}
    text = {r["id"]: (r.get("text") or "") for r in judgments() if r["id"] in ids}
    index, order = M.build(REGISTRY)

    by_j = collections.defaultdict(list)
    for r in rows:
        by_j[r["judgment"]].append(r)

    occ_frame = occ_cite = occ_out = occ_noncite = 0
    unresolved_instrument = 0
    gold_occ = collections.defaultdict(list)      # judgment -> [(num, tid)]
    gold_court = collections.defaultdict(list)
    out_of_frame = []
    for jid, rs in by_j.items():
        last = M.Recent()
        for r in rs:
            if r.get("isCitation") is False:
                occ_frame += 1
                occ_noncite += 1
                continue
            if r.get("outOfFrame"):
                occ_out += 1
                out_of_frame.append(r)
                continue
            occ_frame += 1
            occ_cite += 1
            k = gold_key(r, index, order, last)
            if k is None or k[1] is None:
                unresolved_instrument += 1
            if k:
                gold_occ[jid].append(k)
                if r.get("voice") == "court":
                    gold_court[jid].append(k)

    tp = fp = fn = 0
    utp = ufp = ufn = 0
    misses = collections.Counter()
    per_j = []
    for jid in sorted(ids):
        got = extractor_keys(text[jid], index, order)
        want = gold_occ[jid]
        g, w = collections.Counter(got), collections.Counter(want)
        inter = g & w
        tp += sum(inter.values())
        fp += sum((g - w).values())
        fn += sum((w - g).values())
        for k, n in (w - g).items():
            misses[k] += n
        gs, ws = set(got), set(want)
        utp += len(gs & ws)
        ufp += len(gs - ws)
        ufn += len(ws - gs)
        per_j.append({"judgment": jid, "goldOccurrences": len(want),
                      "goldUnique": len(ws), "extractorOccurrences": len(got),
                      "extractorUnique": len(gs),
                      "occurrenceMatched": sum(inter.values()),
                      "uniqueMatched": len(gs & ws)})

    n_gold_u = sum(p["goldUnique"] for p in per_j)
    n_ext_u = sum(p["extractorUnique"] for p in per_j)

    print(f"32 whole judgments, {sum(len(v) for v in by_j.values())} rows read by hand\n")
    print("FRAME")
    print(f"  «مادة» occurrences in frame              {occ_frame:6}")
    print(f"    citations                              {occ_cite:6}")
    print(f"    anaphoric or numberless, not citations {occ_noncite:6}"
          f"   ({occ_noncite/occ_frame*100:.1f}%)")
    print(f"  citations OUTSIDE the frame              {occ_out:6}"
          f"   ({occ_out/(occ_cite+occ_out)*100:.1f}% of all citations read)")
    print(f"  citations with no instrument recoverable {unresolved_instrument:6}")

    print("\nOCCURRENCE LEVEL  (every citation, the pilot's usual unit)")
    print(f"  gold citations in frame  {occ_cite}")
    print(f"  extractor answers        {tp+fp}")
    print(f"  precision  {pct(tp, tp+fp)}")
    print(f"  recall     {pct(tp, tp+fn)}")

    print("\nARTICLE LEVEL  (one row per judgment x instrument x article)")
    print(f"  gold unique articles     {n_gold_u}")
    print(f"  extractor unique         {n_ext_u}")
    print(f"  precision  {pct(utp, utp+ufp)}")
    print(f"  recall     {pct(utp, utp+ufn)}")
    print(f"  occurrences per applied article, gold: "
          f"{occ_cite/n_gold_u:.2f}")

    # statutory only: a citation whose instrument resolves to a registry
    # track. Contract articles and the one citation that names no instrument
    # at all are not failures of an extractor built to read statutes, and are
    # reported apart rather than folded into recall.
    stp = sfn = 0
    for jid in sorted(ids):
        got = collections.Counter(extractor_keys(text[jid], index, order))
        want = collections.Counter(k for k in gold_occ[jid] if k[1])
        stp += sum((got & want).values())
        sfn += sum((want - got).values())
    print("\n  statutory citations only (instrument resolves to a track)")
    print(f"    gold {stp+sfn}   recall  {pct(stp, stp+sfn)}")

    # why each statutory miss was missed, decided by re-reading the sentence
    # the human row records rather than by guessing from the key
    # Why each statutory miss was missed. The order matters: a citation whose
    # instrument CITE cannot reach is lost before its number is ever parsed,
    # so pattern failures are tested before number failures.
    CAUSE = [
        ("instrument named anaphorically («من ذات النظام»)",
         r"من ذات|من هذا|آنف|المذكور"),
        ("instrument named by a possessive suffix («من لائحته»)",
         r"لائحته|possessive"),
        ("instrument named once at the end of a list",
         r"named once|one head noun|member of the (?:leading )?list|"
         r"named once at the end"),
        ("instrument named before the article", r"INSTRUMENT-FIRST"),
        ("paragraph after the instrument («المادة (29) فقرة (1) من …»)",
         r"postfix paragraph"),
        ("article and paragraph packed into one number",
         r"packed|/"),
        ("cited inside quoted statutory text", r"inside the quoted text"),
    ]
    causes = collections.Counter()
    for jid in sorted(ids):
        got = collections.Counter(extractor_keys(text[jid], index, order))
        seen = collections.Counter()
        last = M.Recent()
        for r in by_j[jid]:
            if r.get("isCitation") is False or r.get("outOfFrame"):
                continue
            k = gold_key(r, index, order, last)
            if not k or not k[1]:
                continue
            seen[k] += 1
            if seen[k] <= got.get(k, 0):
                continue
            probe = (r.get("notes") or "") + " || " + (r.get("articleForm") or "")
            for label, pat in CAUSE:
                if re.search(pat, probe):
                    causes[label] += 1
                    break
            else:
                causes["no single cause identified"] += 1
    print("\n  why the missed statutory citations were missed")
    for k, v in causes.most_common():
        print(f"    {v:>3}  {k}")

    court = sum(len(v) for v in gold_court.values())
    print(f"\nVOICE\n  gold citations in the court's own voice  {court} of "
          f"{occ_cite}  ({court/occ_cite*100:.1f}%)")

    print("\nOUT-OF-FRAME CITATIONS READ BY HAND")
    for r in out_of_frame:
        print(f"  {r['articleForm']:<28} {(r['instrument'] or '—')[:40]}")

    print("\nMISSED, most frequent first")
    for (num, tid), n in misses.most_common(12):
        print(f"  {n:>3}  المادة {str(num):<6} {tid or '(instrument unmatched)'}")

    OUT.write_text(json.dumps(
        {"judgments": len(ids), "rowsRead": len(rows),
         "frame": {"occurrences": occ_frame, "citations": occ_cite,
                   "nonCitations": occ_noncite, "outOfFrame": occ_out,
                   "noInstrument": unresolved_instrument},
         "occurrenceLevel": {"goldCitations": occ_cite, "extractor": tp + fp,
                             "tp": tp, "fp": fp, "fn": fn},
         "articleLevel": {"goldUnique": n_gold_u, "extractorUnique": n_ext_u,
                          "tp": utp, "fp": ufp, "fn": ufn},
         "statutoryOnly": {"gold": stp + sfn, "tp": stp, "fn": sfn},
         "missCauses": dict(causes),
         "courtVoiceCitations": court,
         "perJudgment": per_j}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
