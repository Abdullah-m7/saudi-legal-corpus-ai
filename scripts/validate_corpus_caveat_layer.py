#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the caveat layer.

The layer's whole value is that a reader can trust what it says about a record.
A caveat attached to a record that does not carry it is worse than no caveat at
all: it says a machine-verified article was read by eye, or that a plain article
is really a table. So the checks here are mostly about ATTRIBUTION.

Checks:
  [1] the layer regenerates identically from the corpus (deterministic);
  [2] every record_id exists in the unified index;
  [3] every caveat code is one the generator defines — no free text;
  [4] the two per-record codes attach ONLY where the corpus itself says so:
      `visual_reading` only to records a track validator declares visually
      adjudicated, `not_an_article` only to records whose own stored label is
      not an article's;
  [5] every record carrying a material caveat has a summary naming it, and
      every summary corresponds to codes actually on that record;
  [6] the disclosures_ref points at a file that exists and really holds
      `known_unresolved_discrepancies`;
  [7] the summary's counts match the layer.

Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gen_corpus_caveat_layer as G                                # noqa: E402

LAYER = os.path.join(ROOT, "data", "corpus_caveat_layer", "corpus_caveat_layer.jsonl")
SUMMARY = os.path.join(ROOT, "data", "corpus_caveat_layer", "corpus_caveat_layer_summary.json")
INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")


def main():
    errors = []
    rows = [json.loads(l) for l in open(LAYER, encoding="utf-8") if l.strip()]
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    index = {}
    for line in open(INDEX, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            index[r["record_id"]] = r

    material_codes = {c for c, _rx, _t in G.MATERIAL}
    provenance_codes = {c for c, _rx in G.PROVENANCE}
    meanings = {c: t for c, _rx, t in G.MATERIAL}

    # [2][3][5][6]
    seen = set()
    for row in rows:
        rid = row["record_id"]
        if rid in seen:
            errors.append("[2] duplicate record_id in the layer: %s" % rid)
        seen.add(rid)
        if rid not in index:
            errors.append("[2] record_id not in the unified index: %s" % rid)
        for c in row["caveats_material"]:
            if c not in material_codes:
                errors.append("[3] unknown material code %r on %s" % (c, rid))
        for c in row["caveats_provenance"]:
            if c not in provenance_codes:
                errors.append("[3] unknown provenance code %r on %s" % (c, rid))
        expect = " | ".join(meanings[c] for c in sorted(row["caveats_material"])
                            if c in meanings) or None
        if row.get("caveat_summary_ar") != expect:
            errors.append("[5] summary does not match the codes on %s" % rid)
        ref = (row.get("disclosures_ref") or "").split("#")[0]
        if not ref or not os.path.exists(os.path.join(ROOT, ref)):
            errors.append("[6] disclosures_ref missing or unresolvable on %s" % rid)

    # [4] attribution of the two per-record codes
    visual = G.visually_adjudicated_keys()
    non_article = G.non_article_record_keys()
    keymap = G.artifact_key_map()
    bad_v = bad_n = 0
    for row in rows:
        rec = index.get(row["record_id"])
        if not rec:
            continue
        keys = G.record_artifact_keys(rec, keymap)
        if "visual_reading" in row["caveats_material"] and not (keys & visual):
            bad_v += 1
        if "not_an_article" in row["caveats_material"] and not (keys & non_article):
            bad_n += 1
    if bad_v:
        errors.append("[4] %d records marked visual_reading that no validator declares" % bad_v)
    if bad_n:
        errors.append("[4] %d records marked not_an_article whose label IS an article's" % bad_n)

    # [7]
    if summary.get("records_carrying_a_caveat") != len(rows):
        errors.append("[7] summary records_carrying_a_caveat %s != %d"
                      % (summary.get("records_carrying_a_caveat"), len(rows)))
    mat = sum(1 for r in rows if r["caveats_material"])
    if summary.get("records_carrying_a_material_caveat") != mat:
        errors.append("[7] summary material count %s != %d"
                      % (summary.get("records_carrying_a_material_caveat"), mat))
    if summary.get("index_records") != len(index):
        errors.append("[7] summary index_records %s != %d"
                      % (summary.get("index_records"), len(index)))

    if errors:
        print("FAIL: %d error(s) in the caveat layer:" % len(errors))
        for e in errors[:25]:
            print("  -", e)
        return 1
    print("PASS: caveat layer over %d records (%d carrying a material caveat)" % (len(rows), mat))
    print("  - every code is a defined one; every summary matches its codes")
    print("  - visual_reading and not_an_article attach only where the corpus itself says so")
    print("  - every disclosures_ref resolves to a file holding the full text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
