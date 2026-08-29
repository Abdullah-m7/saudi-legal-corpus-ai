#!/usr/bin/env python3
"""Score the citation grammar against the hand-labelled GSTC_DEV set.

One row per stage, because a single aggregate number cannot say which stage
failed -- and the whole reason the splits and the labels exist is that the
previous single number (0.0 per cent on GSTC, 90.9 on MOJ) could not.

Stages are scored on the items where a correct answer exists: article number
on every gold citation, paragraph only where the gold has one, instrument only
where the gold resolves one. Refusing to answer where the gold refuses counts
as correct; answering there counts as wrong. That asymmetry is deliberate --
a parser that guesses an instrument for «المادة الحادية عشر» is not 100 per
cent, it is confidently wrong.

    python3 evaluate.py                 # full grammar
    python3 evaluate.py --ablate anaphora attribution
    python3 evaluate.py --json
"""

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE.parent / "citation"))
sys.path.insert(0, str(HERE))
from canonical import canonicalise                       # noqa: E402
import grammar                                           # noqa: E402
from instruments import same as same_instrument          # noqa: E402
from splits import FRAME, RAW                            # noqa: E402

DEV = HERE / "gstc_dev.json"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * max(0.0, centre - half), 1),
            round(100 * min(1.0, centre + half), 1))


def norm_paragraph(label):
    if not label:
        return None
    text = "".join(ch for ch in str(label) if ch not in " ()،؛.")
    text = text.replace("-", "/").replace("\\", "/")
    for word in ("الفقرة", "البند", "فقرة", "بند"):
        text = text.replace(word, "")
    parts = [p for p in text.split("/") if p]
    return "/".join(sorted(parts))


def load_dev(rules=None):
    """Each item with its document text and the offset it sits at *now*.

    Items are located by frameIndex, not by the offset stored when they were
    sampled. Any repair to the canonicalisation layer that changes length
    moves every later offset, and an evaluation that followed stale offsets
    would score the grammar against the wrong words while reporting a number
    that looked fine.
    """
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    cache, items = {}, []
    for item in dev["items"]:
        doc = item["doc"]
        if doc not in cache:
            src = (RAW / doc.replace(".pdf", ".txt")).read_text(
                encoding="utf-8", errors="ignore")
            text = canonicalise(src, rules)["canonical"]
            cache[doc] = (text, [m.start() for m in FRAME.finditer(text)])
        text, frame = cache[doc]
        idx = item.get("frameIndex")
        if idx is None or idx >= len(frame):
            sys.exit(f"{item['id']}: frameIndex {idx} not in this document's "
                     f"frame of {len(frame)}; the frame itself has changed")
        items.append((item, text, frame[idx]))
    return items


def predict_at(text, offset, stages):
    """The grammar's record for the occurrence at `offset`, or None."""
    window_start = max(0, offset - 4000)
    for rec in grammar.parse(text[window_start:offset + 400], stages):
        if rec["offset"] + window_start == offset:
            rec = dict(rec)
            rec["offset"] = offset
            return rec
    return None


def score(stages=None, rules=None):
    stages = list(grammar.STAGES) if stages is None else stages
    tally = {k: [0, 0] for k in ("detection", "article", "paragraph",
                                 "instrument", "segment", "exact")}
    errors = []
    for item, text, offset in load_dev(rules):
        gold = item["label"]
        pred = predict_at(text, offset, stages)
        found = pred is not None

        tally["detection"][1] += 1
        if found == gold["isCitation"]:
            tally["detection"][0] += 1
        elif not gold["isCitation"]:
            errors.append((item["id"], "false detection", pred and pred["articleForm"]))
        else:
            errors.append((item["id"], "detection miss", gold["articleForm"]))

        if not gold["isCitation"]:
            continue

        tally["article"][1] += 1
        ok_article = found and pred["articleNumber"] == gold["articleNumber"]
        if ok_article:
            tally["article"][0] += 1
        elif found:
            errors.append((item["id"], "article",
                           f"{pred['articleNumber']} != {gold['articleNumber']}"))

        ok_para = True
        if gold["paragraph"] or (found and pred["paragraph"]):
            tally["paragraph"][1] += 1
            ok_para = found and (norm_paragraph(pred["paragraph"])
                                 == norm_paragraph(gold["paragraph"]))
            if ok_para:
                tally["paragraph"][0] += 1
            else:
                errors.append((item["id"], "paragraph",
                               f"{pred and pred['paragraph']!r} != "
                               f"{gold['paragraph']!r}"))

        tally["instrument"][1] += 1
        ok_inst = found and same_instrument(pred["instrument"], gold["instrument"])
        if ok_inst:
            tally["instrument"][0] += 1
        else:
            errors.append((item["id"], "instrument",
                           f"{pred and pred['instrument']!r} != "
                           f"{gold['instrument']!r}"))

        tally["segment"][1] += 1
        ok_seg = found and pred["segment"] == gold["segment"]
        if ok_seg:
            tally["segment"][0] += 1
        else:
            errors.append((item["id"], "segment",
                           f"{pred and pred['segment']!r} != {gold['segment']!r}"))

        tally["exact"][1] += 1
        if ok_article and ok_para and ok_inst:
            tally["exact"][0] += 1

    out = {"stages": stages,
           "canonicalRules": rules if rules is not None else "all",
           "metrics": {}}
    for key, (k, n) in tally.items():
        lo, hi = wilson(k, n)
        out["metrics"][key] = {"correct": k, "of": n,
                               "pct": round(100 * k / n, 1) if n else None,
                               "ci95": [lo, hi]}
    out["errors"] = [{"id": i, "stage": s, "detail": d} for i, s, d in errors]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ablate", nargs="*", default=[],
                    help="stages to switch off")
    ap.add_argument("--canon-rules", nargs="*", default=None,
                    help="canonicalisation rules to apply (default: all)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--errors", action="store_true")
    a = ap.parse_args()
    stages = [s for s in grammar.STAGES if s not in a.ablate]
    result = score(stages, a.canon_rules)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print("stages on:", ", ".join(result["stages"]))
        print(f"{'stage':12} {'correct':>10}   {'pct':>6}   95% CI")
        for key in ("detection", "article", "paragraph", "instrument",
                    "segment", "exact"):
            m = result["metrics"][key]
            print(f"{key:12} {m['correct']:5d}/{m['of']:<4d}  {m['pct']:6.1f}   "
                  f"[{m['ci95'][0]}, {m['ci95'][1]}]")
        if a.errors:
            print()
            for e in result["errors"]:
                print(f"  {e['id']}  {e['stage']:16} {e['detail']}")
