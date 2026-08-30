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
import hashlib
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE.parent / "citation"))
sys.path.insert(0, str(HERE))
from canonical import trace                              # noqa: E402
import grammar                                           # noqa: E402
from grammar import ENUM as ENUM_WORDS                   # noqa: E402
from numerals import parse_ordinal                       # noqa: E402
from instruments import same as same_instrument          # noqa: E402
from splits import FRAME, RAW                            # noqa: E402

SETS = {"gstc": HERE / "gstc_dev.json", "moj": HERE / "moj_dev.json",
        "gstc_test": HERE / "gstc_test_frozen.json",
        "moj_test": HERE / "moj_test_frozen.json",
        "gstc_test2": HERE / "gstc_test2_frozen.json"}
DEV = SETS["gstc"]


def documents_for(spec):
    """Text of every document in a labelled set, whatever the source.

    GSTC documents are files on disk; MOJ documents are records in the
    judgments shards. The evaluation must not care which -- that is the whole
    point of running one harness over both.
    """
    if spec.get("source", "").startswith("MOJ"):
        from moj_splits import judgments
        want = set(spec["documents"])
        return {d["id"]: (d.get("text") or "")
                for d in judgments() if d["id"] in want}
    return {doc: (RAW / doc.replace(".pdf", ".txt")).read_text(
        encoding="utf-8", errors="ignore") for doc in spec["documents"]}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * max(0.0, centre - half), 1),
            round(100 * min(1.0, centre + half), 1))


ATOM = re.compile(r"\d+|[ء-ي]+")


def norm_paragraph(label):
    """Compare paragraph labels as the set of atoms they name.

    The text layer displaces the separator inside a label -- «6/ب» arrives as
    «/6ب», «9/1/أ» as «/1/9أ» -- so a string comparison reports a difference
    that is bidi reordering and not a difference of citation. Comparing the
    atoms, unordered, is blind to the reordering and still sees a genuinely
    different paragraph.
    """
    if not label:
        return None
    parts = label if isinstance(label, (list, tuple)) else [label]
    atoms = set()
    for part in parts:
        for token in re.split(r"[;؛]", str(part)):
            for atom in ATOM.findall(token):
                if atom in ("الفقرة", "البند", "فقرة", "بند", "الفقرات",
                            "البنود", "رقم", "من"):
                    continue
                if atom in ENUM_WORDS:
                    atoms.add(f"#{ENUM_WORDS[atom]}")
                    continue
                spelled = parse_ordinal(atom)
                atoms.add(str(spelled) if spelled is not None else atom)
    return "/".join(sorted(atoms)) or None


def load_dev(rules=None):
    """Each item with its document text and the offset it sits at *now*.

    Items are located by the raw byte they came from, not by the offset
    stored when they were sampled and not by their place in the frame. Both
    of those move when the canonicalisation layer changes -- offsets because
    the repairs change length, the frame because a repair can create or
    destroy occurrences of the very word the frame is built on. Only the raw
    byte is fixed, so only the raw byte can hold an item still while the
    layer beneath it is varied.
    """
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    raw_texts = documents_for(dev)
    cache, items = {}, []
    for item in dev["items"]:
        doc = item["doc"]
        if doc not in cache:
            text, tr = traced(raw_texts[doc], rules)
            back = {}
            for i, raw_i in enumerate(tr):
                back.setdefault(raw_i, i)
            cache[doc] = (text, back)
        text, back = cache[doc]
        raw_offset = item.get("rawOffset")
        if raw_offset is None or raw_offset not in back:
            sys.exit(f"{item['id']}: rawOffset {raw_offset} has no position "
                     f"under this canonicalisation")
        items.append((item, text, back[raw_offset]))
    return items


_PARSED = {}
_TRACED = {}


def traced(raw, rules):
    """trace() is O(characters) in Python and the ablation re-traces the same
    documents once per condition. Cached on the text and the rule set."""
    key = (hashlib.sha256(raw.encode("utf-8")).hexdigest(),
           tuple(rules) if rules is not None else "all")
    if key not in _TRACED:
        _TRACED[key] = trace(raw, rules)
    return _TRACED[key]


_GAZETTEER = {}


def gazetteer_for(texts, rules, key):
    """Instrument names across every document in the set, hard-terminated only."""
    if key not in _GAZETTEER:
        names = {}
        for raw in texts.values():
            canon, _ = traced(raw, rules)
            names.update(grammar.inventory(canon))
        _GAZETTEER[key] = names
    return _GAZETTEER[key]


def parse_document(text, stages, gaz=None):
    """Every record in one document, indexed by offset.

    The document is parsed whole and once. An earlier version parsed a window
    around each item, which was faster and wrong twice over: the instrument
    inventory was built from the window, so a name stated unbroken elsewhere
    in the document was invisible when it was needed, and the attribution
    stage could not see a section heading that fell before the window.
    """
    # keyed on the text itself, not on id(): a document object can be
    # collected and its address reused, and the second set then reads the
    # first set's parse. It cost two points of detection before it was seen.
    key = (hashlib.sha256(text.encode("utf-8")).hexdigest(), tuple(stages))
    if key not in _PARSED:
        _PARSED[key] = {r["offset"]: r
                        for r in grammar.parse(text, stages, gaz)}
    return _PARSED[key]


def predict_at(text, offset, stages, gaz=None):
    """The grammar's record for the occurrence at `offset`, or None."""
    return parse_document(text, stages, gaz).get(offset)


def score(stages=None, rules=None, which=None):
    global DEV
    if which:
        DEV = SETS[which]
    stages = list(grammar.STAGES) if stages is None else stages
    tally = {k: [0, 0] for k in ("detection", "article", "paragraph",
                                 "instrument", "segment", "exact")}
    errors = []
    spec = json.loads(DEV.read_text(encoding="utf-8"))
    gaz = (gazetteer_for(documents_for(spec), rules,
                         (str(DEV), tuple(rules) if rules else "all"))
           if stages is None or "instrument" in stages else None)
    for item, text, offset in load_dev(rules):
        gold = item["label"]
        pred = predict_at(text, offset, stages, gaz)
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
    ap.add_argument("--set", choices=sorted(SETS), default="gstc")
    a = ap.parse_args()
    DEV = SETS[a.set]
    stages = [s for s in grammar.STAGES if s not in a.ablate]
    result = score(stages, a.canon_rules)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"set: {a.set}   stages on:", ", ".join(result["stages"]))
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
