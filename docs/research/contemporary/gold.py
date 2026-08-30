#!/usr/bin/env python3
"""A contemporary gold sample, drawn before the classifier is believed.

Nothing is run over 28,090 judgments until the rules have been read against
text a human labelled. And a classifier cannot be validated on its own hits:
that measures precision and calls it accuracy. So the sample has two halves,
which answer the two different questions.

  PRECISION   mentions the rules fired on, stratified by rule id so a rule
              that fires 40,000 times and a rule that fires 300 times are both
              readable. For each: is this really that type of authority, is
              the segment right, is the speaker right?

  RECALL      sentences drawn at random from court reasoning, with no regard
              to whether any rule fired. For each: does this sentence invoke a
              legal authority, and of what type? A rule set is only as good as
              what it does with text it was not built from.

Drawn from contemporary_3y (1444-1446). Seed fixed, sheet written to the
scratchpad rather than the repository, because the sheet carries judgment text
and the labels are what belongs in git.

    python3 gold.py sheet --out <path>
    python3 gold.py merge --labels <path>
"""
import argparse
import collections
import os
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
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / (f"gold_{os.environ.get('GOLD_SEED', '23')}.json")
# Sample 1 (seed 23) is DEVELOPMENT: it found six defects and drove their
# repair, so it can no longer estimate precision -- the rules were fitted to
# it. Sample 2 (seed 47) is VALIDATION, drawn after the repairs and opened
# once. GOLD_SEED selects which.
SEED = int(os.environ.get("GOLD_SEED", "23"))
PER_RULE = 9          # precision items per rule id
RECALL_N = 80         # random reasoning sentences
CONTEXT = 320
YEARS = set(VIEWS["contemporary_3y"])
SENT = re.compile(r"[^.؛\n]{40,400}[.؛]")

MASKS = [
    (re.compile(r"(هوية\s*(?:وطنية\s*)?رقم\s*\(?\s*)[\d٠-٩]{6,}"), r"\1(...)"),
    (re.compile(r"(سجل\s*(?:تجاري|مدني)\s*رقم\s*\(?\s*)[\d٠-٩]{6,}"), r"\1(...)"),
    (re.compile(r"(?<!\d)(?:\+?966|0)5\d{8}(?!\d)"), "(...)"),
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "(...)"),
]


def scrub(s):
    for pat, rep in MASKS:
        s = pat.sub(rep, s)
    return s


def draw():
    """Collect candidates in one pass, then sample. Streams; nothing is held."""
    index, order = M.build(REGISTRY)
    rng = random.Random(SEED)
    by_rule = collections.defaultdict(list)     # rule -> reservoir
    recall_pool = []
    seen_rule = collections.Counter()
    n = 0
    for rec in judgments():
        if year_of(rec) not in YEARS:
            continue
        n += 1
        text, sections = rec["text"], rec.get("sections") or {}
        ms = A.mentions(text, sections, index, order)
        for m in ms:
            rid = m["rule"]
            seen_rule[rid] += 1
            # reservoir sampling, so the draw does not favour early shards
            k = seen_rule[rid]
            item = {"judgment": rec["id"], "rule": rid, "type": m["type"],
                    "at": m["at"], "segment": m["segment"],
                    "speaker": m["speaker"], "voice": A.voice(m),
                    "instrument": m["instrument"], "article": m["article"],
                    "procedural": m["procedural"]}
            if len(by_rule[rid]) < PER_RULE:
                by_rule[rid].append(item)
            elif rng.random() < PER_RULE / k:
                by_rule[rid][rng.randrange(PER_RULE)] = item
        # recall: one reasoning sentence per judgment, reservoir over the view
        spans = [(a, b) for a, b, v in V.segments(text, sections)
                 if v == "reasoning" and b - a > 400]
        if spans:
            a, b = spans[0]
            cands = [s for s in SENT.finditer(text, a, b)]
            if cands:
                s = cands[rng.randrange(len(cands))]
                cand = {"judgment": rec["id"], "at": s.start(),
                        "sentence": s.group(0)}
                if len(recall_pool) < RECALL_N:
                    recall_pool.append(cand)
                elif rng.random() < RECALL_N / n:
                    recall_pool[rng.randrange(RECALL_N)] = cand
    return by_rule, recall_pool, seen_rule, n


def sheet(out_path):
    by_rule, recall_pool, seen, n = draw()
    want = {i["judgment"] for v in by_rule.values() for i in v}
    want |= {i["judgment"] for i in recall_pool}
    texts = {r["id"]: r["text"] for r in judgments() if r["id"] in want}

    lines = [f"CONTEMPORARY GOLD  seed {SEED}  drawn from {n:,} judgments "
             f"of 1444-1446", ""]
    prec = []
    for rid in sorted(by_rule):
        for i, item in enumerate(by_rule[rid]):
            t = texts[item["judgment"]]
            a = max(0, item["at"] - CONTEXT)
            b = min(len(t), item["at"] + CONTEXT)
            item["id"] = f"P{len(prec):03d}"
            prec.append(item)
            lines += ["=" * 78,
                      f"{item['id']}  rule={rid}  proposed type={item['type']}",
                      f"      proposed segment={item['segment']}  "
                      f"speaker={item['speaker']}  voice={item['voice']}",
                      f"      instrument={item['instrument']}  "
                      f"article={item['article']}",
                      "-" * 78, scrub(t[a:b]), ""]
    lines += ["", "#" * 78, "RECALL: reasoning sentences, no rule applied",
              "#" * 78, ""]
    rec_items = []
    for i, c in enumerate(recall_pool):
        c["id"] = f"R{i:03d}"
        rec_items.append({"id": c["id"], "judgment": c["judgment"],
                          "at": c["at"]})
        lines += ["=" * 78, c["id"], "-" * 78, scrub(c["sentence"]), ""]

    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    OUT.write_text(json.dumps(
        {"seed": SEED, "perRule": PER_RULE, "recallN": RECALL_N,
         "view": "contemporary_3y", "judgmentsInView": n,
         "ruleFrequency": dict(seen.most_common()),
         "precisionItems": prec, "recallItems": rec_items,
         "precisionLabels": [], "recallLabels": []},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(prec)} precision items over {len(by_rule)} rules, "
          f"{len(rec_items)} recall sentences -> {out_path}")
    for rid, c in seen.most_common():
        print(f"  {rid:<26}{c:>9,} in the view")


def merge(labels_path):
    spec = json.loads(OUT.read_text(encoding="utf-8"))
    lab = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    spec["precisionLabels"] = lab.get("precision", [])
    spec["recallLabels"] = lab.get("recall", [])
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{len(spec['precisionLabels'])} precision labels, "
          f"{len(spec['recallLabels'])} recall labels merged")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    m = sub.add_parser("merge"); m.add_argument("--labels", required=True)
    a = ap.parse_args()
    sheet(a.out) if a.cmd == "sheet" else merge(a.labels)
