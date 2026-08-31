#!/usr/bin/env python3
"""Did codification displace fiqh, or only dilute it?

The by-year table in `claim_results.json` shows the bench's fiqh mentions
falling from 22.7 per cent of its citations in 1441 to 10.0 in 1446 while the
share of judgments whose reasons *mix* statute with non-statutory authority
rises from 18 to 32. Those two facts cannot both be read as a trend in the
same quantity: the first is a share of mentions, and a share of mentions falls
whenever the other term grows, whether or not the numerator moves.

So this separates the two questions the single number confuses:

    prevalence   in how many reasoned judgments does the bench invoke this
                 authority at all -- the question "does the court still
                 reason from fiqh"
    intensity    how many times does it invoke it in the judgments where it
                 does at all -- the question "how much work is it doing"
    share        what fraction of everything the bench cites is this -- the
                 quantity that falls by arithmetic when statute grows

Quoted spans are excluded throughout: a judgment that reproduces art. 164's
own words «العرف، أو العادة المستقرة» is not the court invoking custom.

Denominators are reasoned judgments, from the judgment layer, so a year in
which more judgments carry no reasons at all cannot move the series.

    python3 hybrid.py measure
    python3 hybrid.py sheet --out <path>
"""
import argparse
import collections
import gzip
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import voice_attribution as V             # noqa: E402
from gold import scrub                    # noqa: E402
from windows import judgments, year_of    # noqa: E402
from map import wilson                    # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
DOCS = HERE / "authority_layer.jsonl.gz"
OUT = HERE / "hybrid_results.json"
GOLD = HERE / "hybrid_gold.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
# 1442 has 240 reasoned judgments in this layer and 1446 has 1,209; the series
# is reported for every year but only 1443-1446 carries enough to read.
YEARS = (1442, 1443, 1444, 1445, 1446)
SEED = 907
N = 14


def reasoned_by_year():
    n = collections.Counter()
    with gzip.open(DOCS, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or not r.get("reasoned"):
                continue
            n[r["year"]] += 1
    return n


def court_mentions():
    """judgment -> (year, Counter of type, set of instruments) for the bench."""
    out = {}
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            if r["role"] != "court_reasoning":
                continue
            e = out.setdefault(r["j"], [r["y"], collections.Counter(), set()])
            e[1][r["t"]] += 1
            if r.get("inst"):
                e[2].add(r["inst"])
    return out


def measure():
    denom, court = reasoned_by_year(), court_mentions()
    res = {"denominator": "reasoned judgments in the year",
           "quotedExcluded": True, "years": {}, "ccl_only": {}}

    def series(keep):
        rows = {}
        for y in YEARS:
            n = sum(1 for j, (yy, c, i) in court.items()
                    if yy == y and keep(c, i)) if keep is not KEEP_ALL \
                else denom[y]
            docs = [(c, i) for j, (yy, c, i) in court.items()
                    if yy == y and keep(c, i)]
            tot = sum(sum(c.values()) for c, _ in docs)
            row = {"n": n, "courtMentions": tot, "authority": {}}
            for t in ("statute",) + NONSTATUTE:
                k = sum(1 for c, _ in docs if c[t])
                m = sum(c[t] for c, _ in docs)
                row["authority"][t] = {
                    "docs": k,
                    "prevalencePct": round(k / n * 100, 1) if n else 0.0,
                    "prevalenceCI": wilson(k, n),
                    "intensity": round(m / k, 2) if k else 0.0,
                    "shareOfCourtMentionsPct":
                        round(m / tot * 100, 1) if tot else 0.0,
                }
            k = sum(1 for c, _ in docs if any(c[t] for t in NONSTATUTE))
            row["anyNonStatutePrevalencePct"] = \
                round(k / n * 100, 1) if n else 0.0
            row["anyNonStatuteCI"] = wilson(k, n)
            k = sum(1 for c, _ in docs
                    if c["statute"] and any(c[t] for t in NONSTATUTE))
            row["hybridPrevalencePct"] = round(k / n * 100, 1) if n else 0.0
            rows[str(y)] = row
        return rows

    res["years"] = series(KEEP_ALL)
    # holding the procedural posture roughly fixed: judgments whose reasons
    # cite the Commercial Courts Law, the modal instrument. courtType is
    # 'Lawsuit' for 26,598 of 27,027 reasoned judgments, so there is no
    # chamber to control for; the instrument is the only handle the data has.
    res["ccl_only"] = series(lambda c, i: "commercial_courts_law" in i)
    res["seams"] = seams()
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    for lab, rows in (("all reasoned", res["years"]),
                      ("CCL-citing", res["ccl_only"])):
        print(f"\n{lab}: year   n   fiqh prev%  fiqh intens  fiqh share%  "
              f"any non-statute prev%")
        for y in YEARS:
            r = rows[str(y)]["authority"]["fiqh_source"]
            print(f"  {y}  {rows[str(y)]['n']:6}  {r['prevalencePct']:8}  "
                  f"{r['intensity']:9}  {r['shareOfCourtMentionsPct']:9}  "
                  f"{rows[str(y)]['anyNonStatutePrevalencePct']:9}")
    print(f"\n-> {OUT.name}")


KEEP_ALL = lambda c, i: True    # noqa: E731


def seams():
    """Which statutory articles pull non-statutory authority in beside them?

    For every article the bench cites often enough to measure, the share of
    the judgments citing it whose reasons also carry a non-statutory
    authority. The hand sample says the fiqh arrives at particular seams in
    the statute; if that is right the rate should vary by article far more
    than it varies between procedural and substantive articles, and this
    measures both.
    """
    labels = json.loads((HERE / "function_labels.json").read_text(
        encoding="utf-8"))["labels"]
    docs = collections.defaultdict(
        lambda: [set(), collections.Counter()])
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r["role"] != "court_reasoning" or r.get("q"):
                continue
            d = docs[r["j"]]
            d[1][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d[0].add((r["inst"], r["art"]))
    n = len(docs)
    base = sum(1 for d in docs.values()
               if any(d[1][t] for t in NONSTATUTE))
    cnt, hit = collections.Counter(), collections.Counter()
    cls, clsh = collections.Counter(), collections.Counter()
    for arts, types in docs.values():
        mixed = any(types[t] for t in NONSTATUTE)
        seen = set()
        for a in arts:
            cnt[a] += 1
            if mixed:
                hit[a] += 1
            c = (labels.get(f"{a[0]}:{a[1]}") or {}).get("class")
            if c:
                seen.add(c)
        for c in seen:
            cls[c] += 1
            if mixed:
                clsh[c] += 1
    rows = [{"instrument": k[0], "article": k[1], "n": cnt[k],
             "nonStatutePct": round(hit[k] / cnt[k] * 100, 1),
             "function": (labels.get(f"{k[0]}:{k[1]}") or {}).get("function"),
             "class": (labels.get(f"{k[0]}:{k[1]}") or {}).get("class")}
            for k in cnt if cnt[k] >= 300]
    rows.sort(key=lambda r: -r["nonStatutePct"])
    return {"docs": n, "basePct": round(base / n * 100, 1),
            "minArticleN": 300, "articles": rows,
            "byClass": {c: {"n": cls[c],
                            "nonStatutePct": round(clsh[c] / cls[c] * 100, 1)}
                        for c in sorted(cls)}}


def sheet(out_path):
    """A hand-reading sheet of hybrid judgments: what is the fiqh doing?"""
    court = court_mentions()
    cand = [j for j, (y, c, i) in court.items()
            if y in (1444, 1445, 1446) and c["statute"]
            and any(c[t] for t in NONSTATUTE)]
    rng = random.Random(SEED)
    cand.sort()
    rng.shuffle(cand)
    keys = cand[:N]
    want = set(keys)
    texts = {r["id"]: r["text"] for r in judgments() if r["id"] in want}
    lines = [f"HYBRID REASONING  seed {SEED}   {N} judgments whose reasons cite "
             f"both statute and a non-statutory authority", "",
             "For each, what is the non-statutory authority doing? interpreting "
             "the text / filling a gap / supporting a result the text already "
             "reached / defining an undefined term / ornament / deciding a "
             "question the statute does not cover", ""]
    items = []
    for i, j in enumerate(keys):
        y, c, inst = court[j]
        t = texts.get(j, "")
        rea = [t[a:b] for a, b, v in V.segments(t, {}) if v == "reasoning"]
        items.append({"id": f"H{i:02d}", "judgment": j, "year": y,
                      "types": {k: v for k, v in sorted(c.items())},
                      "instruments": sorted(inst)})
        lines += ["=" * 78,
                  f"H{i:02d}  {y}   bench cites: " + ", ".join(
                      f"{k}x{v}" for k, v in sorted(c.items())),
                  f"     instruments: " + ", ".join(
                      x.split("_")[0] for x in sorted(inst)),
                  "-" * 32 + " REASONS " + "-" * 37,
                  scrub(re.sub(r"\s+", " ", " ".join(rea))[:3000]), ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    if not GOLD.exists():
        GOLD.write_text(json.dumps(
            {"seed": SEED, "n": N, "items": items, "labels": []},
            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} judgments -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("measure")
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    a = ap.parse_args()
    (measure() if a.cmd == "measure" else sheet(a.out))
