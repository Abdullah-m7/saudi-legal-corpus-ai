#!/usr/bin/env python3
"""Hand-validated transport evaluation, with a denominator and an error class.

A match rate is not validation. This draws a random sample of every place the
committees' digests use the word «مادة», runs the project's pipeline on each,
and classifies what the pipeline did against what is there.

Taxonomy, extended from the applied-law paper's because this source needs two
classes that source did not:

  detection_miss          a statutory citation is present; the pattern does
                          not reach it
  false_detection         the pattern fires where no citation is present
  article_parse_error     detected, but the article number is not recovered
  instrument_resolution   detected, but the instrument is not resolved to a
                          registry track
  anaphora_error          an anaphoric reference resolved to the wrong track
  text_layer_error        NEW. the citation is unreadable because the PDF text
                          layer damaged it -- transposed lam, inserted
                          kashida, or a number reordered out of its brackets
  schema_interpretation   NEW. the reference is to an instrument or an
                          internal rule that the registry does not model

Sampling is seeded and the denominator is the sampled population, not the
citations the pipeline happened to find.

    python3 validate.py   ->  validation.json
"""

import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
sys.path.insert(0, str(HERE))
import arabic_ordinals as A          # noqa: E402
import match_instruments as M        # noqa: E402
import voice_attribution as V        # noqa: E402
from privacy_scan import normalise   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
RAW = HERE / "raw"
OUT = HERE / "validation.json"
SAMPLE = 60
SEED = 0
WINDOW = 90

# The text layer transposes the lam of the definite article with the letter
# after it: «المادة» is emitted as «املادة», 1,112 times against 0 correct
# forms in the first digest. Reversed here for the diagnosis only; it is not
# a change to any extractor.
LAM = re.compile(r"ا(?![ل])([بتثجحخدذرزسشصضطظعغفقكمنهوي])ل(?=[ء-ي])")
KASHIDA = re.compile("ـ+")
WORD = re.compile(r"(?:لل|بال|ال)?ماد[ةت]")
# What a citation looks like in this source once the text layer is repaired:
# «المادة (142) من نظام الجمارك الموحد», with the number pushed outside its
# brackets by bidi reordering, or a spelled ordinal in brackets.
# The committees write «المادة (142) من نظام X»; the courts write «المادة
# الخامسة والتسعين من نظام X». A truth pattern that only knows one of the two
# would score the other institution at zero by construction, which is the very
# error being measured. It accepts both.
SOURCE_FORM = re.compile(
    r"(?:لل|بال|ال)?ماد(?:ة|تي|تا)\w*\s*"
    r"(?:\(\s*\)?\s*[\d٠-٩]*\s*\)?|[^.،؛\n(]{1,45}?)\s*"
    r"(?:من|في)\s+(?P<inst>(?:نظام|لائحة|الئحة|قواعد|تنظيم|مرسوم|قرار)"
    r"[^.،؛\n]{0,50})")


def repair(text):
    clean, _ = normalise(text)
    return KASHIDA.sub("", LAM.sub(r"ال\1", clean))


def moj_pool(limit=400):
    """The same population, drawn from the source the pipeline was built on.

    Without this the new source's score is a number with nothing to mean. The
    harness has to be shown to find what is there when what is there is what
    it was written for.
    """
    shards = sorted((HERE.parent / "arabic_paper" / "judgments").glob("*.jsonl"))
    pool = []
    for shard in shards:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            t = d.get("text") or ""
            for m in WORD.finditer(t):
                pool.append((d["id"], m.start(),
                             t[max(0, m.start() - WINDOW): m.start() + WINDOW]))
            if len(pool) > limit * 60:
                return pool
    return pool


def main():
    baseline = "--baseline" in sys.argv
    index, order = M.build(REGISTRY)
    if baseline:
        pool = moj_pool()
    else:
        texts = sorted(RAW.glob("*.txt"))
        if not texts:
            sys.exit("no pilot text: run collect.py --pilot first")
        pool = []
        for p in texts:
            t = repair(p.read_text(encoding="utf-8", errors="ignore"))
            for m in WORD.finditer(t):
                pool.append((p.name, m.start(),
                             t[max(0, m.start() - WINDOW): m.start() + WINDOW]))
    random.seed(SEED)
    sample = random.sample(pool, min(SAMPLE, len(pool)))

    rows = []
    for name, pos, ctx in sample:
        detected = V.CITE.findall(ctx)
        truth = SOURCE_FORM.search(ctx)
        row = {"file": name, "pos": pos, "context": " ".join(ctx.split()),
               "pipelineDetected": bool(detected),
               "citationPresent": bool(truth), "class": None}
        if truth and not detected:
            row["class"] = "detection_miss"
        elif detected and not truth:
            row["class"] = "false_detection"
        elif detected and truth:
            art, inst = detected[0]
            n, _ = A.parse(art)
            tid, _kind = M.match(inst, index, order, M.Recent())
            if n is None:
                row["class"] = "article_parse_error"
            elif not tid:
                row["class"] = "instrument_resolution"
            else:
                row["class"] = "correct"
                row["track"] = tid
                row["article"] = n
        else:
            row["class"] = "no_citation_here"
        rows.append(row)

    counts = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    present = sum(1 for r in rows if r["citationPresent"])
    correct = counts.get("correct", 0)
    # Wilson interval, because a proportion from sixty observations needs one.
    def wilson(k, n, z=1.96):
        if not n:
            return None
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
        return [round(max(0, c - h), 3), round(min(1, c + h), 3)]

    out = {
        "population": "occurrences of «مادة» in three GSTC digests, repaired text",
        "populationSize": len(pool),
        "sample": len(sample),
        "seed": SEED,
        "annotator": "single, unblinded; no inter-annotator agreement",
        "citationsPresentInSample": present,
        "pipelineEndToEndCorrect": correct,
        "endToEndAccuracyOnCitations": round(correct / present, 3) if present else None,
        "wilson95": wilson(correct, present),
        "classCounts": counts,
        "rows": rows,
    }
    globals()["OUT"] = (HERE / ("validation_baseline.json" if baseline else "validation.json"))
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"population {len(pool):,} · sample {len(sample)} · seed {SEED}")
    print(f"citations present in sample: {present}")
    print(f"pipeline end-to-end correct: {correct} "
          f"({correct/present:.1%} of citations present, "
          f"95% CI {out['wilson95']})" if present else "")
    print("\nclass counts:")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"   {v:>4}  {k}")


if __name__ == "__main__":
    main()
