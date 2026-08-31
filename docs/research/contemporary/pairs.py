#!/usr/bin/env python3
"""Claim and response: does the court answer the legal proposition put to it?

The transition matrix counts what each side invoked. It cannot see whether
the court's reasons *engage* what the litigant argued. That needs paired units
-- a party's legal proposition and the passage of the reasons that answers it
-- and pairing cannot be assumed. So this is a FEASIBILITY pilot: a small
sample, read by hand, to find out whether the pairing can be identified at all
before anything is built on it.

Sampling frame: judgments of 1444-1446 in which a party cites a specific
statutory article and the court's reasons cite at least one article. Those are
the cases where a response either exists or is conspicuously absent.

    python3 pairs.py sheet --out <path>
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
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from gold import scrub                # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
LAYER = HERE / "authority_mentions.jsonl.gz"
OUT = HERE / "pairs_gold.json"
SEED = 131
N = 12
YEARS = {1444, 1445, 1446}


def candidates():
    party = collections.defaultdict(set)
    court = collections.defaultdict(set)
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["y"] not in YEARS:
                continue
            if r.get("art") is None:
                continue
            if r["role"] == "party_argument":
                party[r["j"]].add((r["inst"], r["art"]))
            elif r["role"] == "court_reasoning":
                court[r["j"]].add((r["inst"], r["art"]))
    return {j: (party[j], court[j]) for j in party if court.get(j)}


def sheet(out_path):
    cand = candidates()
    rng = random.Random(SEED)
    keys = sorted(cand)
    rng.shuffle(keys)
    keys = keys[:N]
    want = set(keys)
    texts = {r["id"]: r["text"] for r in judgments()
             if r["id"] in want and year_of(r) in YEARS}
    lines = [f"CLAIM-RESPONSE PILOT  seed {SEED}   {N} judgments where a party "
             f"cites an article and the court's reasons cite one",
             "",
             "For each: is the party's legal proposition identifiable, and is "
             "there a passage of the reasons that answers it?", ""]
    items = []
    for i, j in enumerate(keys):
        p, c = cand[j]
        t = texts.get(j, "")
        spans = V.segments(t, {})
        rec = [t[a:b] for a, b, v in V.segments(t, {}) if v == "recital"]
        rea = [t[a:b] for a, b, v in V.segments(t, {}) if v == "reasoning"]
        items.append({"id": f"C{i:02d}", "judgment": j,
                      "partyArticles": sorted(f"{x}:{y}" for x, y in p),
                      "courtArticles": sorted(f"{x}:{y}" for x, y in c)})
        lines += ["=" * 78,
                  f"C{i:02d}   party cites: " + ", ".join(
                      f"{x.split('_')[0]}:{y}" for x, y in sorted(p)),
                  f"      court cites: " + ", ".join(
                      f"{x.split('_')[0]}:{y}" for x, y in sorted(c)),
                  "-" * 30 + " RECITAL (trimmed) " + "-" * 29,
                  scrub(re.sub(r"\s+", " ", " ".join(rec))[:1500]),
                  "-" * 30 + " REASONS " + "-" * 39,
                  scrub(re.sub(r"\s+", " ", " ".join(rea))[:2200]), ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    OUT.write_text(json.dumps(
        {"seed": SEED, "n": N, "items": items, "labels": []},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} judgments -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    a = ap.parse_args()
    sheet(a.out)
