#!/usr/bin/env python3
"""Whole judgments, read end to end, one row per article citation.

Every measurement in this project so far is per *occurrence of the word*
«مادة» --- 480 of them, sampled from a frame, each read through a
1300-character window. That is the right unit for asking whether the parser
resolves a citation. It is the wrong unit for the claim the HILJ paper makes,
which is about *which articles a court applies*: an article cited eleven times
in one judgment is one applied article, not eleven, and a window of 1300
characters cannot see that the same article was named three paragraphs earlier
under a different form.

So this samples whole judgments and asks a reader to read all of each one.

Stratified on the things that make a judgment hard to count rather than on
subject, because the question is about counting:

  density        judgments with many citations against judgments with few
  instruments    one instrument named against several
  anaphora       whether the text ever refers back to an instrument
  shape          recital-heavy against reasons-heavy
  vintage        before and after the Commercial Courts Law came into force

Judgments already used in MOJ_DEV or MOJ_TEST are excluded, so the gold is
about documents neither split has touched.

    python3 moj_article_gold.py sheet --out <path>
    python3 moj_article_gold.py merge --labels <path>
"""
import argparse, collections, json, random, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from canonical import trace                       # noqa: E402
from splits import FRAME, scrub                   # noqa: E402
from moj_splits import judgments                  # noqa: E402
import voice_attribution as V                     # noqa: E402

OUT = HERE / "moj_article_gold.json"
SEED = 11
PER_CELL = 2
CTL = "1444"          # Commercial Courts Law in force from 1441; corpus years
ANAPHORA = re.compile(r"هذا\s+النظام|هذه\s+الالئحة|هذه\s+اللائحة|ذات\s+النظام"
                      r"|النظام\s+ذاته|النظام\s+المذكور|الالئحة\s+المذكورة"
                      r"|المشار\s+إلي|آنف")


# The frame is defined on canonicalised text, but canonicalising fifty
# thousand judgments to *choose* a sample of twenty is minutes of regex for a
# decision that does not need that precision. Ministry judgments are typed
# text, not scanned: the transposed definite article that makes
# canonicalisation necessary for the committees' PDFs is rare here, so the raw
# count is used for stratification and the canonical text only for the
# judgments actually drawn.
RAW_FRAME = re.compile(r"(?:^|[^ء-ي])(?:ال|لل|بال|كال|فال|وال|ول|بل|ب|ل|و)?ماد[ةه]")


def profile(rec):
    text = rec.get("text") or ""
    n = len(RAW_FRAME.findall(text))
    instruments = len(set(m.group(2).strip()[:40] for m in V.CITE.finditer(text)))
    spans = V.segments(text, rec.get("sections"))
    lens = {v: 0 for v in ("recital", "reasoning", "operative")}
    for lo, hi, v in spans:
        if v in lens:
            lens[v] += hi - lo
    shape = ("reasons-heavy" if lens["reasoning"] > lens["recital"]
             else "recital-heavy")
    return {"citations": n, "instruments": instruments,
            "anaphora": bool(ANAPHORA.search(text)), "shape": shape,
            "segmentable": any(v != "unknown" for _, _, v in spans),
            "chars": len(text), "year": (rec.get("judgmentDate") or
                                         rec.get("year") or "")}


def cell(p):
    return (
        "dense" if p["citations"] >= 6 else "sparse",
        "several instruments" if p["instruments"] >= 3 else "one or two",
        "anaphora" if p["anaphora"] else "no anaphora",
        p["shape"],
    )


def build():
    used = set()
    for name in ("moj_dev.json", "moj_test_frozen.json"):
        path = HERE / name
        if path.exists():
            used |= set(json.loads(path.read_text(encoding="utf-8"))["documents"])
    pool = collections.defaultdict(list)
    for rec in judgments():
        if rec["id"] in used:
            continue
        text = rec.get("text") or ""
        if not (2_000 < len(text) < 22_000) or not FRAME.search(text):
            continue
        p = profile(rec)
        if p["citations"] == 0 or not p["segmentable"]:
            continue
        pool[cell(p)].append((rec["id"], p))
    rng = random.Random(SEED)
    chosen = []
    for c in sorted(pool):
        items = sorted(pool[c], key=lambda kv: kv[0])
        rng.shuffle(items)
        for jid, p in items[:PER_CELL]:
            chosen.append({"id": jid, "stratum": " / ".join(c), **p})
    return chosen, {" / ".join(c): len(v) for c, v in sorted(pool.items())}


def sheet(out_path):
    chosen, sizes = build()
    want = {c["id"] for c in chosen}
    texts = {r["id"]: (r.get("text") or "") for r in judgments() if r["id"] in want}
    lines = []
    for c in chosen:
        canon = trace(texts[c["id"]])[0]
        lines += ["=" * 78,
                  f"{c['id']}   {c['stratum']}",
                  f"   {c['citations']} «مادة» occurrences, "
                  f"{c['instruments']} instrument names, {c['chars']:,} chars",
                  "=" * 78, scrub(canon), ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    OUT.write_text(json.dumps(
        {"seed": SEED, "perCell": PER_CELL, "unit": "whole judgment",
         "excluded": "every judgment used in MOJ_DEV or MOJ_TEST",
         "strataAvailable": sizes, "judgments": chosen, "rows": []},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(chosen)} judgments over {len(sizes)} strata -> {out_path}")
    for k, v in sizes.items():
        print(f"  {k:64} pool {v:5}")


def merge(labels_path):
    spec = json.loads(OUT.read_text(encoding="utf-8"))
    rows = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    ids = {c["id"] for c in spec["judgments"]}
    bad = sorted({r["judgment"] for r in rows} - ids)
    if bad:
        sys.exit(f"rows for judgments not in the sample: {bad[:5]}")
    seen = {r["judgment"] for r in rows}
    if seen != ids:
        sys.exit(f"{len(ids - seen)} judgments unread: {sorted(ids - seen)[:5]}")
    spec["rows"] = rows
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    uniq = {(r["judgment"], r["instrument"], r["articleNumber"]) for r in rows}
    print(f"{len(rows)} citation occurrences, {len(uniq)} unique "
          f"article-per-judgment pairs, over {len(ids)} judgments")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    m = sub.add_parser("merge"); m.add_argument("--labels", required=True)
    a = ap.parse_args()
    sheet(a.out) if a.cmd == "sheet" else merge(a.labels)
