#!/usr/bin/env python3
"""Build the blind packet a second reader needs, and score it when it returns.

Nothing in this repository's hand labels has an agreement statistic. One
reader produced the article classification and the functional reading of the
hybrid judgments. Those findings are published as an interpretive layer --
written rules, an ambiguity class, stated provenance, and a sensitivity
analysis against an independently assigned label set -- and they do not wait
on this packet. It is OPTIONAL EXTERNAL REPLICATION: what a second reader
adds is an agreement statistic, which strengthens the labels; what a second
reader does not do is authorise them.

The packet is blind in a specific sense. The sheets carry the article text or
the reasons and nothing else -- no class, no rate, no citation rank, no
stratum label, no hypothesis. The stratification exists (it has to, or the
sample is all art. 16) but it is invisible on the sheet and the items are
shuffled under a fixed seed.

    python3 second_reader.py articles --out <path>
    python3 second_reader.py judgments --out <path>
    python3 second_reader.py score --answers <csv>
"""
import argparse
import collections
import csv
import gzip
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import voice_attribution as V              # noqa: E402
from function import articles              # noqa: E402
from gold import scrub                     # noqa: E402
from windows import judgments, year_of     # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
GOLD = HERE / "completeness_gold.json"
HYBRID = HERE / "hybrid_gold.json"
KEY = HERE / "second_reader_key.json"
SEED = 4113
N_ARTICLES = 60
N_JUDGMENTS = 40
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")


def court_docs():
    out = collections.defaultdict(
        lambda: [collections.Counter(), set(), 0])
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["role"] != "court_reasoning":
                continue
            d = out[r["j"]]
            d[0][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d[1].add((r["inst"], r["art"]))
            d[2] = r["y"]
    return out


def strata_articles(gold, n, hit):
    """Cover the range the hypothesis lives on, without showing the reader it.

    Three attraction bands, crossed with the first reader's class. The bands
    use the outcome variable, which is exactly why they may not appear on the
    sheet: they are a sampling device, not information given to the reader.
    """
    rows = []
    for k, lab in gold["labels"].items():
        inst, art = k.rsplit(":", 1)
        key = (inst, int(art))
        if not n[key]:
            continue
        rate = 100 * hit[key] / n[key]
        rows.append((key, lab["class"],
                     "low" if rate < 15 else "mid" if rate < 40 else "high"))
    return rows


def article_sheet(out_path):
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    docs = court_docs()
    n, hit = collections.Counter(), collections.Counter()
    for types, arts, _ in docs.values():
        mixed = any(types[t] for t in NONSTATUTE)
        for a in arts:
            n[a] += 1
            if mixed:
                hit[a] += 1
    rows = strata_articles(gold, n, hit)
    buckets = collections.defaultdict(list)
    for key, cls, band in rows:
        buckets[(cls, band)].append(key)
    rng = random.Random(SEED)
    picked = []
    for b in sorted(buckets):
        ks = sorted(buckets[b])
        rng.shuffle(ks)
        picked += ks[:max(1, round(N_ARTICLES * len(ks) / len(rows)))]
    picked = sorted(set(picked))
    rng.shuffle(picked)
    A = articles()
    lines = ["TASK A --- what kind of provision is this?", "",
             "Read ANNOTATION_GUIDE.md first. For each article below give one "
             "class, and say whether you hesitated.", ""]
    key = {}
    for i, k in enumerate(picked):
        ident = f"A{i:03d}"
        key[ident] = {"article": f"{k[0]}:{k[1]}",
                      "firstReader": gold["labels"][f"{k[0]}:{k[1]}"]["class"]}
        t = re.sub(r"\s+", " ", A[k]["text"])
        lines += ["=" * 78, f"{ident}   {k[0]}   article {k[1]}", "",
                  t[:1600], ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return key, len(picked)


def judgment_sheet(out_path):
    docs = court_docs()
    cand = []
    for j, (types, arts, y) in docs.items():
        if y not in (1444, 1445, 1446):
            continue
        if not types["statute"]:
            continue
        kinds = tuple(sorted(t for t in NONSTATUTE if types[t]))
        if kinds:
            cand.append((j, kinds))
    by = collections.defaultdict(list)
    for j, kinds in cand:
        by[kinds[0]].append(j)          # stratify on the leading authority
    rng = random.Random(SEED + 1)
    picked = []
    for kind in sorted(by):
        ks = sorted(by[kind])
        rng.shuffle(ks)
        picked += ks[:max(2, round(N_JUDGMENTS * len(ks) / len(cand)))]
    picked = sorted(set(picked))
    rng.shuffle(picked)
    picked = picked[:N_JUDGMENTS]
    want = set(picked)
    texts = {r["id"]: r["text"] for r in judgments() if r["id"] in want}
    lines = ["TASK B --- what is the non-statutory authority doing here?", "",
             "Read ANNOTATION_GUIDE.md first. For each judgment give one role "
             "and answer the deletion question.", ""]
    key = {}
    prior = {it["judgment"]: it["id"]
             for it in json.loads(HYBRID.read_text(encoding="utf-8"))["items"]}
    for i, j in enumerate(picked):
        ident = f"B{i:03d}"
        key[ident] = {"judgment": j, "alsoInFirstSample": prior.get(j)}
        t = texts.get(j, "")
        rea = [t[a:b] for a, b, v in V.segments(t, {}) if v == "reasoning"]
        lines += ["=" * 78, f"{ident}", "",
                  scrub(re.sub(r"\s+", " ", " ".join(rea))[:3200]), ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return key, len(picked)


def answer_form(key, path, columns):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(columns)
        for ident in sorted(key):
            w.writerow([ident] + [""] * (len(columns) - 1))


def kappa(a, b):
    """Cohen's kappa for two label sequences over the same items."""
    assert len(a) == len(b) and a
    labels = sorted(set(a) | set(b))
    n = len(a)
    obs = sum(1 for x, y in zip(a, b) if x == y) / n
    exp = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return round((obs - exp) / (1 - exp), 3) if exp < 1 else 1.0


def score(answers):
    key = json.loads(KEY.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(answers, encoding="utf-8")))
    got = {r["id"]: r for r in rows if r.get("id")}
    mine, theirs = [], []
    for ident, k in sorted(key.get("articles", {}).items()):
        r = got.get(ident)
        if r and r.get("class"):
            mine.append(k["firstReader"])
            theirs.append(r["class"].strip().upper())
    if not mine:
        print("no article answers found in the form")
        return 1
    agree = sum(1 for x, y in zip(mine, theirs) if x == y)
    print(f"Task A: {agree}/{len(mine)} agree "
          f"({100*agree/len(mine):.1f} %), Cohen's kappa {kappa(mine, theirs)}")
    dis = collections.Counter(
        (x, y) for x, y in zip(mine, theirs) if x != y)
    for (x, y), c in dis.most_common(8):
        print(f"   first reader {x} -> second reader {y}: {c}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("articles"); a.add_argument("--out", required=True)
    b = sub.add_parser("judgments"); b.add_argument("--out", required=True)
    s = sub.add_parser("score"); s.add_argument("--answers", required=True)
    args = ap.parse_args()
    if args.cmd == "score":
        return score(args.answers)
    key = json.loads(KEY.read_text(encoding="utf-8")) if KEY.exists() else {}
    if args.cmd == "articles":
        k, n = article_sheet(args.out)
        key["articles"] = k
        answer_form(k, HERE / "second_reader_articles.csv",
                    ["id", "class", "ambiguous", "secondChoice", "notes"])
    else:
        k, n = judgment_sheet(args.out)
        key["judgments"] = k
        answer_form(k, HERE / "second_reader_judgments.csv",
                    ["id", "role", "deletable", "notes"])
    key["seed"] = SEED
    key["blind"] = ("the sheets carry the article text or the reasons and "
                    "nothing else: no class, no rate, no rank, no stratum, "
                    "no hypothesis")
    KEY.write_text(json.dumps(key, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{n} items -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
