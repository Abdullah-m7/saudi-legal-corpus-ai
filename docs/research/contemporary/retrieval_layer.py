#!/usr/bin/env python3
"""The retrieval layer: what a court had written before it cited an article.

The corpus-properties paper claims that preprocessing choices change what a
legal AI system inherits. That claim is worth nothing until a system is
actually built and measured, so this pass extracts the input to one:

    given the court's own reasoning immediately BEFORE a statutory citation,
    retrieve the article the court then cited.

Ground truth is the citation itself, resolved by the existing matcher. The
task is therefore not synthetic: no question is invented, no relevance is
judged by us, and the label is what a Saudi commercial court actually did.

One row per resolved statutory citation:

    j y p inst art voice fp nt ctx

`ctx` is the query/document material and is a BAG OF HASHED TOKENS. Every
token is normalised as companions.norm normalises, then replaced by the first
8 hex characters of its SHA-1, and the counts are stored unordered. Word
order is destroyed and no token is recoverable, so this file obeys the same
rule as every other derived layer here: NO JUDGMENT TEXT IS WRITTEN. BM25
needs term frequencies and document lengths and nothing else, so nothing is
lost for the experiment.

Leakage is handled at extraction time, before any split exists:

  * the citation being predicted is never in its own context -- the window
    ends where the citation begins;
  * EVERY statutory citation span inside the window is masked, so a nearby
    second citation of the same article cannot give the answer away, and the
    instrument's name cannot either;
  * the window is clipped to the segment the citation sits in, so a citation
    in the reasons never reads the recital.

`fp` is companions.fingerprint over the +-90 character window around the
citation, identical by construction to the unit the formula layer uses. It is
what makes the de-boilerplating arm and the verbatim-overlap control possible.

    python3 retrieval_layer.py
"""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import arabic_ordinals as AO          # noqa: E402
import authority as A                 # noqa: E402
import companions as C                # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
DATES = HERE / "judgment_dates.json.gz"
OUT = HERE / "retrieval_layer.jsonl.gz"

YEARS = {1442, 1443, 1444, 1445, 1446}
CTX = 600          # characters of preceding context, clipped to the segment
MIN_TOKENS = 5     # a window shorter than this is not a query, it is a scrap


def tokens(s):
    """The tokenisation BM25 will see: companions.norm, minus short words."""
    return [w for w in C.norm(s).split() if len(w) > 2]


def digest(tok):
    return hashlib.sha1(tok.encode()).hexdigest()[:8]


def main():
    index, order = M.build(REGISTRY)
    with gzip.open(DATES, "rt", encoding="utf-8") as fh:
        dates = {k: tuple(v) for k, v in json.load(fh)["dates"].items()}

    n = docs = skipped = 0
    with gzip.open(OUT, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": {
            "years": sorted(YEARS), "contextChars": CTX,
            "minTokens": MIN_TOKENS,
            "fields": "j y p inst art voice fp nt ctx",
            "task": "given the court's reasoning before a citation, retrieve "
                    "the cited article. Ground truth is the citation, "
                    "resolved by match_instruments.",
            "ctx": "bag of hashed tokens: sha1(token)[:8] -> count. Order is "
                   "destroyed and tokens are not recoverable. NO JUDGMENT "
                   "TEXT IS WRITTEN.",
            "masking": "every statutory citation span inside the context "
                       "window is replaced by a space, including the one "
                       "being predicted, which is outside the window anyway.",
            "fp": "companions.fingerprint over +-90 characters around the "
                  "citation -- the same unit as the formula layer.",
        }}, ensure_ascii=False) + "\n")

        for rec in judgments():
            y = year_of(rec)
            if y not in YEARS:
                continue
            d = dates.get(rec["id"])
            if not d:
                continue
            docs += 1
            text, sections = rec["text"], rec.get("sections") or {}
            spans = V.segments(text, sections)
            # every citation span in the document, so any that falls inside a
            # context window can be masked out of it
            cites = [(m.start(), m.end()) for m in V.CITE.finditer(text)]
            p = f"{d[0]}Q{(d[1] - 1) // 3 + 1}"

            for m in A.mentions(text, sections, index, order):
                if m["type"] != "statute" or not m["instrument"]:
                    continue
                art, _ = AO.parse(m["article"] or "")
                if art is None:
                    continue
                at = m["at"]
                # the window starts at the segment boundary or CTX back
                floor = 0
                for a, b, _ in spans:
                    if a <= at < b:
                        floor = a
                        break
                start = max(floor, at - CTX)
                window = list(text[start:at])
                for ca, cb in cites:
                    if cb > start and ca < at:
                        for i in range(max(ca, start) - start,
                                       min(cb, at) - start):
                            window[i] = " "
                toks = tokens("".join(window))
                if len(toks) < MIN_TOKENS:
                    skipped += 1
                    continue
                bag = {}
                for t in toks:
                    h = digest(t)
                    bag[h] = bag.get(h, 0) + 1
                fh.write(json.dumps({
                    "j": rec["id"], "y": y, "p": p,
                    "inst": m["instrument"], "art": art,
                    "voice": A.voice(m),
                    "fp": C.fingerprint(text, at, at + 1),
                    "nt": len(toks),
                    "ctx": dict(sorted(bag.items())),
                }, ensure_ascii=False) + "\n")
                n += 1

    size = OUT.stat().st_size
    print(f"{n:,} resolved citations with context from {docs:,} judgments "
          f"({skipped:,} windows too short) -> {OUT.name} "
          f"({size/1e6:.1f} MB gzipped)")


if __name__ == "__main__":
    main()
