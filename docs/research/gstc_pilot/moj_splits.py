#!/usr/bin/env python3
"""A MOJ development set built exactly as the GSTC one was.

The point of a second source is comparison, and a comparison between two sets
built to different rules measures the rules. So: the same frame («مادة» with
any proclitic, over canonicalised text, independent of extractor success), the
same split unit, the same seed, the same masking, the same schema of labels.

The one difference is forced by the data. GSTC gives ten documents, so the
split unit is the document. MOJ gives tens of thousands of judgments, so the
split unit is the judgment and the sample is drawn over judgments rather than
over five of them.

    python3 moj_splits.py
"""

import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE))
from canonical import trace                       # noqa: E402
from splits import FRAME, PER_SPLIT, SEED, WINDOW, scrub   # noqa: E402

SHARDS = sorted((HERE.parent / "arabic_paper" / "judgments").glob("*.jsonl"))
OUT_DEV = HERE / "moj_dev.json"
OUT_TEST = HERE / "moj_test_frozen.json"
DOCS_PER_SPLIT = 200


def judgments():
    for shard in SHARDS:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)


def main():
    if not SHARDS:
        sys.exit("no MOJ shards under arabic_paper/judgments")
    ids = []
    texts = {}
    for d in judgments():
        text = d.get("text") or ""
        if FRAME.search(text):
            ids.append(d["id"])
            texts[d["id"]] = text
    rng = random.Random(SEED)
    ids = sorted(ids)
    rng.shuffle(ids)
    chosen = ids[:2 * DOCS_PER_SPLIT]
    assignment = {"dev": sorted(chosen[:DOCS_PER_SPLIT]),
                  "test": sorted(chosen[DOCS_PER_SPLIT:])}

    out = {}
    for split, keep in assignment.items():
        items = []
        for jid in keep:
            canon, tr = trace(texts[jid])
            for i, m in enumerate(FRAME.finditer(canon)):
                ctx = canon[max(0, m.start() - WINDOW): m.start() + WINDOW]
                items.append({"doc": jid, "frameIndex": i,
                              "rawOffset": tr[m.start()],
                              "token": m.group(0),
                              "context": " ".join(scrub(ctx).split())})
        rng2 = random.Random(SEED + (0 if split == "dev" else 1))
        sample = rng2.sample(items, min(PER_SPLIT, len(items)))
        for i, it in enumerate(sample):
            it["id"] = f"moj-{split}-{i:03d}"
            it["label"] = None
        out[split] = {
            "split": split, "source": "MOJ judgments gateway",
            "documents": keep, "frameSize": len(items), "sampled": len(sample),
            "seed": SEED + (0 if split == "dev" else 1),
            "frameRule": "every occurrence of «مادة» with any prefix, in "
                         "canonicalised text; independent of extractor success",
            "splitUnit": "judgment",
            "canonicalRules": "all", "contextsScrubbed": True,
            "anchor": "rawOffset is the byte in the judgment text; frameIndex "
                      "is the ordinal under the full canonicalisation",
            "items": sample,
        }
    OUT_DEV.write_text(json.dumps(out["dev"], ensure_ascii=False, indent=1)
                       + "\n", encoding="utf-8")
    OUT_TEST.write_text(json.dumps(out["test"], ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    for s in ("dev", "test"):
        print(f"{s.upper():5} {len(out[s]['documents'])} judgments, "
              f"frame {out[s]['frameSize']:,}, sampled {out[s]['sampled']}")
    assert not (set(assignment["dev"]) & set(assignment["test"]))
    print("no judgment appears in both splits")


if __name__ == "__main__":
    main()
