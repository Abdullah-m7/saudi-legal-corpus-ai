#!/usr/bin/env python3
"""GSTC_TEST2_FROZEN: a second-generation held-out set, stratified.

The first held-out set was five documents, four of them customs, drawn from
the same ten digests that produced the development set. It gave an honest
answer -- 27.7 per cent exact -- and then spent itself informing the repair
that answer prompted. It cannot be used again.

This set is built from digests that have never been read: twelve of the
thirty-four the Secretariat publishes, being those that (a) were not in the
first development or test split and (b) pass the privacy gate. Eleven of the
thirty-three retrieved do not pass it and are excluded from sampling
entirely, which costs the dedicated VAT and customs decision volumes of 2024;
VAT and customs are covered here from the mixed-subject compendia instead,
and that substitution is a limitation of the set, recorded rather than hidden.

STRATIFICATION
--------------
The first test set failed on a fault that only customs digests carry, because
four of its five documents were customs. Subject is therefore a stratum here,
with an equal allocation rather than one proportional to volume, so that no
subject can dominate the estimate and every subject gets an interval of its
own to report.

    subject          documents
    customs          9.pdf, CustomsDefenses2024.pdf
    zakat            222, 2024-Zakat-Decisions-1, 2024-Zakat-Decisions-2,
                     8.pdf, ZakatDefenses2024
    income tax       56.pdf, 2024-Incometax-Decisions
    excise           izv.pdf
    tax, mixed       PrinciplesTaxAppealCommittees2024,
    (incl. VAT)      TaxCommitteesPleas2024

Three editorial forms are present -- decisions, extracted principles, and
compendia of pleadings -- and four publication years (2020-21, 2023, 2024).

SAMPLE SIZE
-----------
The first held-out estimate had a 95 per cent interval sixteen points wide
(27.7 [20.2, 36.6]), which cannot separate a system that is right seven times
in ten from one that is right eight and a half. Eighty occurrences per subject
stratum, five strata, gives 400: a half-width near four points overall and
near ten within a stratum. That is the smallest sample that supports the
per-family reporting the failure of the first test showed to be necessary.

    n = 400   overall half-width  ~4.2 points at p = 0.75
    n =  80   per-stratum         ~9.5 points at p = 0.75

The frame is every occurrence of «مادة» with any proclitic in canonicalised
text -- not what the extractor finds. A frame built from extractor output can
only ever measure the extractor against itself.

    python3 gstc_test2.py
"""

import collections
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE))
from canonical import trace                              # noqa: E402
from splits import FRAME, RAW, WINDOW, scrub             # noqa: E402

MANIFEST = HERE / "manifest.json"
OUT = HERE / "gstc_test2_frozen.json"
SEED = 2
PER_STRATUM = 80
USED_BEFORE = {"10.pdf", "11.pdf", "111.pdf", "12.pdf", "13.pdf", "14.pdf",
               "15.pdf", "16.pdf", "17.pdf", "18.pdf", "19.pdf", "20.pdf"}

STRATA = {
    "customs": ["9.pdf", "CustomsDefenses2024.pdf"],
    "zakat": ["222.pdf", "2024-Zakat-Decisions-1.pdf",
              "2024-Zakat-Decisions-2.pdf", "8.pdf", "ZakatDefenses2024.pdf"],
    "income tax": ["56.pdf", "2024-Incometax-Decisions.pdf"],
    "excise": ["izv.pdf"],
    "tax, mixed (incl. VAT)": ["PrinciplesTaxAppealCommittees2024.pdf",
                               "TaxCommitteesPleas2024.pdf"],
}
KIND = {"9.pdf": "principles", "8.pdf": "principles",
        "PrinciplesTaxAppealCommittees2024.pdf": "principles",
        "CustomsDefenses2024.pdf": "pleadings",
        "ZakatDefenses2024.pdf": "pleadings",
        "TaxCommitteesPleas2024.pdf": "pleadings"}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    status = {r["file"]: r for r in manifest["records"]}
    chosen = [f for files in STRATA.values() for f in files]

    for f in chosen:
        rec = status.get(f)
        if rec is None or not rec.get("retrieved"):
            sys.exit(f"{f}: not retrieved")
        if not rec["privacy"]["clean"]:
            sys.exit(f"{f}: fails the privacy gate and must not be sampled")
        if f in USED_BEFORE:
            sys.exit(f"{f}: was used in the first split")

    frames, texts = {}, {}
    for f in chosen:
        raw = (RAW / f.replace(".pdf", ".txt")).read_text(
            encoding="utf-8", errors="ignore")
        canon, tr = trace(raw)
        texts[f] = canon
        frames[f] = [(i, m.start(), tr[m.start()], m.group(0))
                     for i, m in enumerate(FRAME.finditer(canon))]

    rng = random.Random(SEED)
    items, allocation = [], {}
    for subject, files in STRATA.items():
        pool = [(f, *row) for f in files for row in frames[f]]
        take = min(PER_STRATUM, len(pool))
        allocation[subject] = {
            "documents": files, "frame": len(pool), "sampled": take,
            "byDocument": dict(collections.Counter(f for f, *_ in pool)),
        }
        for f, idx, off, raw_off, token in rng.sample(pool, take):
            ctx = texts[f][max(0, off - WINDOW): off + WINDOW]
            items.append({
                "doc": f, "subject": subject,
                "kind": KIND.get(f, "decisions"),
                "frameIndex": idx, "rawOffset": raw_off, "token": token,
                "context": " ".join(scrub(ctx).split()),
                "label": None,
            })
    rng.shuffle(items)
    for i, it in enumerate(items):
        it["id"] = f"t2-{i:03d}"

    spec = {
        "split": "test2",
        "source": "GSTC tax and customs digests, second generation",
        "role": "HELD OUT. Opened once, after the architecture is frozen and "
                "its hashes recorded. Not used in development.",
        "documents": chosen,
        "excludedFromSampling": {
            "usedInFirstSplit": sorted(USED_BEFORE),
            "failedPrivacyGate": sorted(manifest["privacyRefusals"]),
        },
        "frameSize": sum(len(v) for v in frames.values()),
        "sampled": len(items),
        "seed": SEED,
        "frameRule": "every occurrence of «مادة» with any prefix, in "
                     "canonicalised text; independent of extractor success",
        "splitUnit": "document",
        "stratification": "subject, equal allocation of 80 per stratum",
        "allocation": allocation,
        "anchor": "rawOffset is the byte in the extracted text; frameIndex is "
                  "the ordinal under the full canonicalisation",
        "canonicalRules": "all",
        "contextsScrubbed": True,
        "items": items,
    }
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{len(chosen)} documents, frame {spec['frameSize']:,}, "
          f"sampled {len(items)}")
    for subject, a in allocation.items():
        print(f"  {subject:24} frame {a['frame']:6,}  sampled {a['sampled']:3}"
              f"  {len(a['documents'])} documents")
    assert not (set(chosen) & USED_BEFORE)
    print("no document overlaps the first development or test split")


if __name__ == "__main__":
    main()
