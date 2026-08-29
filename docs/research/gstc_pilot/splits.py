#!/usr/bin/env python3
"""Build GSTC_DEV and GSTC_TEST_FROZEN before any parser exists to see them.

Design decisions, each of which can be got wrong silently:

  frame        every occurrence of the word «مادة» in canonicalised text, with
               any prefix. It is chosen because it does not depend on the
               extractor succeeding: a frame built from what the pipeline
               finds can only ever measure the pipeline against itself.

  split unit   the document, not the occurrence. Two samples drawn from one
               digest share its formatting, its instruments and its drafting
               hand, so an occurrence-level split leaks.

  exclusions   the two digests whose privacy scan is not clean. They stay
               available for local diagnosis but their text is not sampled
               into an artefact that gets committed.

  scrubbing    every stored context is passed through a masker first. The
               publisher's redaction is imperfect and a committed context is
               a republication.

  seed         0, and the assignment of documents to splits is recorded, so
               the split can be rebuilt exactly and audited for leakage.

TEST is not opened during development. Its contexts are written to a separate
file that the DEV workflow never reads.

    python3 splits.py
"""

import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE))
from canonical import canonicalise, digest   # noqa: E402
import privacy_scan                          # noqa: E402

RAW = HERE / "raw"
MANIFEST = HERE / "manifest.json"
OUT_DEV = HERE / "gstc_dev.json"
OUT_TEST = HERE / "gstc_test_frozen.json"
SEED = 0
PER_SPLIT = 120
WINDOW = 110
FRAME = re.compile(r"(?:لل|بال|كال|فال|وال|ال)?ماد[ةت]\w*")

# Mask what the publisher's own redaction missed, using the publisher's marker.
MASKS = [
    (re.compile(r"(هوية\s*وطنية\s*رقم\s*\(?\s*)\d{10}"), r"\1(...)"),
    (re.compile(r"(الهوية\s*الوطنية\s*رقم\s*\(?\s*)\d{10}"), r"\1(...)"),
    (re.compile(r"(سجل\s*تجاري\s*رقم\s*\(?\s*)\d{10}"), r"\1(...)"),
    (re.compile(r"(?<!\d)(?:\+?966|0)5\d{8}(?!\d)"), "(...)"),
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "(...)"),
]


def scrub(text):
    for pat, rep in MASKS:
        text = pat.sub(rep, text)
    return text


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    clean_docs, excluded = [], []
    for r in manifest["records"]:
        if not r.get("retrieved"):
            excluded.append({"file": r["file"], "why": "retrieval failed"})
        elif not r["privacy"]["clean"]:
            excluded.append({"file": r["file"],
                             "why": "privacy scan not clean; kept for local "
                                    "diagnosis, not sampled"})
        else:
            clean_docs.append(r["file"])

    rng = random.Random(SEED)
    docs = sorted(clean_docs)
    rng.shuffle(docs)
    half = len(docs) // 2
    assignment = {"dev": sorted(docs[:half]), "test": sorted(docs[half:])}

    def frame_for(files):
        items = []
        for f in files:
            txt = RAW / f.replace(".pdf", ".txt")
            if not txt.exists():
                continue
            canon = canonicalise(txt.read_text(encoding="utf-8",
                                               errors="ignore"))["canonical"]
            for m in FRAME.finditer(canon):
                ctx = canon[max(0, m.start() - WINDOW): m.start() + WINDOW]
                items.append({"doc": f, "offset": m.start(),
                              "token": m.group(0),
                              "context": " ".join(scrub(ctx).split())})
        return items

    out = {}
    for split, files in assignment.items():
        items = frame_for(files)
        rng2 = random.Random(SEED + (0 if split == "dev" else 1))
        sample = rng2.sample(items, min(PER_SPLIT, len(items)))
        for i, it in enumerate(sample):
            it["id"] = f"{split}-{i:03d}"
            it["label"] = None          # filled by annotation, never by a parser
        out[split] = {
            "split": split,
            "documents": files,
            "frameSize": len(items),
            "sampled": len(sample),
            "seed": SEED + (0 if split == "dev" else 1),
            "frameRule": "every occurrence of «مادة» with any prefix, in "
                         "canonicalised text; independent of extractor success",
            "splitUnit": "document",
            "excluded": excluded,
            "canonicalRules": "all (bidi, tatweel, digits, lam_swap, brackets)",
            "contextsScrubbed": True,
            "items": sample,
        }

    OUT_DEV.write_text(json.dumps(out["dev"], ensure_ascii=False, indent=1),
                       encoding="utf-8")
    OUT_TEST.write_text(json.dumps(out["test"], ensure_ascii=False, indent=1),
                        encoding="utf-8")
    for s in ("dev", "test"):
        d = out[s]
        print(f"{s.upper():<5} {len(d['documents'])} documents, frame "
              f"{d['frameSize']:,}, sampled {d['sampled']}")
        print(f"      {', '.join(d['documents'])}")
    print(f"excluded: {[e['file'] for e in excluded]}")
    # leakage check
    assert not (set(out['dev']['documents']) & set(out['test']['documents']))
    print("no document appears in both splits")


if __name__ == "__main__":
    main()
