#!/usr/bin/env python3
"""FINAL VALIDATION GATE for the contemporary map. Design frozen before labels.

Sample 1 (seed 23) found six defects and is burned by having driven them.
Sample 2 (seed 47) validated the repaired types: 126/126 correct. Two things
it did NOT establish, and this gate exists for exactly those two and nothing
else:

  (a) three recall fixes made AFTER sample 2 was read -- bare «متقرر فقهاً»,
      «مجموع فتاوى» without the article, and «في لائحتها الأولى» -- have never
      been checked against text.

  (b) sample 2 validated the TYPE of each mention. The headline result is
      about the VOICE: that a litigant argues from the contract and the bench
      does not. If the voice assignment is wrong, that result is an artefact
      of the classifier and not a fact about the corpus. Voice has never been
      hand-checked.

THE DESIGN IS FROZEN HERE, BEFORE ANY LABEL IS READ.

  arm 1  RECALL FIXES     9 hits of each of the three repaired rules
  arm 2  VOICE            12 mentions of each assigned voice, any type
  arm 3  DIVERGENCE CELLS 8 mentions of each of the five types the claim
                          turns on, in each of the two voices it contrasts

  PASS CRITERIA, pre-declared:
    arm 1   >= 7 of 9 correct for each repaired rule
    arm 2   >= 85 % of voice assignments correct overall, and >= 80 % within
            each of court_reasoning and party_argument
    arm 3   the DIRECTION of every one of the five contrasts survives: for
            each type, the hand-corrected court/party ratio keeps its sign

  If arm 2 or arm 3 fails, the court-party result is withdrawn, not patched.
  If arm 1 fails, the offending rule is disabled and the map re-run without
  it. In neither case is a fourth sample drawn.

    python3 gate.py sheet --out <path>
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
from gold import scrub                # noqa: E402
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "gate.json"
SEED = 71
YEARS = set(VIEWS["contemporary_3y"])
CONTEXT = 300

RECALL_FIXES = ("fiqh.unattributed", "fiqh.book", "statute.possessive")
VOICES = ("court_reasoning", "party_argument", "recital", "operative")
CLAIM_TYPES = ("contract", "legal_maxim", "custom", "fiqh_source", "statute")
PER_RULE, PER_VOICE, PER_CELL = 9, 12, 8


def draw():
    index, order = M.build(REGISTRY)
    rng = random.Random(SEED)
    res = collections.defaultdict(list)
    seen = collections.Counter()

    def offer(key, cap, item):
        seen[key] += 1
        if len(res[key]) < cap:
            res[key].append(item)
        elif rng.random() < cap / seen[key]:
            res[key][rng.randrange(cap)] = item

    n = 0
    for rec in judgments():
        if year_of(rec) not in YEARS:
            continue
        n += 1
        text, sections = rec["text"], rec.get("sections") or {}
        for m in A.mentions(text, sections, index, order):
            if m.get("inQuote"):
                continue
            vc = A.voice(m)
            item = {"judgment": rec["id"], "rule": m["rule"], "type": m["type"],
                    "at": m["at"], "segment": m["segment"],
                    "speaker": m["speaker"], "voice": vc}
            if m["rule"] in RECALL_FIXES:
                offer(("arm1", m["rule"]), PER_RULE, item)
            if vc in VOICES:
                offer(("arm2", vc), PER_VOICE, item)
            if m["type"] in CLAIM_TYPES and vc in ("court_reasoning",
                                                   "party_argument"):
                offer(("arm3", m["type"], vc), PER_CELL, item)
    return res, n


def sheet(out_path):
    res, n = draw()
    want = {i["judgment"] for v in res.values() for i in v}
    texts = {r["id"]: r["text"] for r in judgments() if r["id"] in want}
    lines = [f"GATE  seed {SEED}  drawn from {n:,} judgments of 1444-1446",
             "DESIGN FROZEN. Pass criteria are in gate.py and were written "
             "before this sheet existed.", ""]
    items = []
    for key in sorted(res, key=str):
        arm = key[0]
        lines += ["#" * 78, f"{arm}  {' / '.join(key[1:])}", "#" * 78, ""]
        for it in res[key]:
            it["id"] = f"{arm[-1]}{len(items):03d}"
            it["arm"] = arm
            it["key"] = " / ".join(key[1:])
            items.append(it)
            t = texts[it["judgment"]]
            a, b = max(0, it["at"] - CONTEXT), min(len(t), it["at"] + CONTEXT)
            lines += ["=" * 78,
                      f"{it['id']}  type={it['type']}  rule={it['rule']}",
                      f"      voice={it['voice']}  segment={it['segment']}"
                      f"  speaker cue={it['speaker']}",
                      "-" * 78, scrub(t[a:b]), ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    OUT.write_text(json.dumps(
        {"seed": SEED, "view": "contemporary_3y", "judgmentsInView": n,
         "design": {"arm1": list(RECALL_FIXES), "arm2": list(VOICES),
                    "arm3": list(CLAIM_TYPES),
                    "perRule": PER_RULE, "perVoice": PER_VOICE,
                    "perCell": PER_CELL},
         "items": items, "labels": []},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} items -> {out_path}")
    for key in sorted(res, key=str):
        print(f"  {' / '.join(str(k) for k in key):<44}{len(res[key]):>4} "
              f"drawn from {seen_total(res, key)}")


def seen_total(res, key):
    return len(res[key])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    a = ap.parse_args()
    sheet(a.out)
