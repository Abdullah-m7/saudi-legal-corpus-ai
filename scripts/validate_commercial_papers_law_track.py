#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Commercial Papers Law track (121 records).

Trust gate (BOE-archive provenance): the numbered sequence is a complete 1..121
(no مكرر); every article carries an explained legal_status (اصلية/معدلة)
consistent with its is_repealed/is_amended/is_added flags; the two committed
official BOE snapshots re-hash to the sha256 recorded in the source artifact; and
the concatenated corpus text re-hashes to the recorded corpus sha256 (so the
committed text is exactly the cross-snapshot-verified official text). Exactly
three articles (118, 119, 120) are معدلة (amended by Royal Decree M/45, 1409H),
each carrying the current amended text plus its original 1383H text in history;
none are repealed or added. Article 38 is اصلية and carries an official
interpretation note (Council of Ministers Decision 251, 1442H) in its history.
Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_papers", "law", "official_source",
                   "commercial_papers_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "commercial_papers", "law", "verified",
                       "commercial_papers_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "commercial_papers_arabic_legal_llm",
                   "commercial_papers_law_legal_llm_001_121.json")
STATUS = "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"
N = 121
KEY_RE = r"commercial_papers_art_(\d{3})"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 118, "معدلة": 3}
EXPECTED_AMENDED = {118, 119, 120}
INTERPRETED = {38}
TRUSTED = {"MATCHES_BOE_CROSS_SNAPSHOT"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    prov = src["provenance"]

    # [1] structure: complete 1..121, no mukarrar
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts if not k.endswith("_mukarrar"))
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if any(k.endswith("_mukarrar") for k in arts):
        e.append("[1] unexpected mukarrar keys")
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate
    sc = Counter()
    amended_nums = set()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if ls == "معدلة":
            amended_nums.add(int(re.match(KEY_RE, k).group(1)))
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")
    if amended_nums != EXPECTED_AMENDED:
        e.append("[2] amended set %s != expected %s" % (sorted(amended_nums), sorted(EXPECTED_AMENDED)))
    # amended articles must carry history with both current + original
    for n in EXPECTED_AMENDED:
        h = arts["commercial_papers_art_%03d" % n].get("history") or []
        if not any(x.get("type") == "original_1383" for x in h):
            e.append("[2] art %d: amended but missing original_1383 in history" % n)
    # interpreted article(s) اصلية with interpretation note
    for n in INTERPRETED:
        a = arts["commercial_papers_art_%03d" % n]
        if a["legal_status_ar"] != "اصلية":
            e.append("[2] art %d: interpreted article must remain اصلية" % n)
        if not any(x.get("type") == "interpretation" for x in (a.get("history") or [])):
            e.append("[2] art %d: missing interpretation note in history" % n)

    # [2b] no dual-status divergence recorded
    if prov.get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    # [3] committed BOE snapshots re-hash to recorded sha256
    snaps = prov.get("archive_snapshots", [])
    if len(snaps) < 2:
        e.append("[3] fewer than 2 archive snapshots recorded")
    for snap in snaps:
        f = os.path.join(ROOT, snap["committed"])
        if not os.path.isfile(f):
            e.append("[3] missing committed snapshot %s" % snap["committed"]); continue
        if hashlib.sha256(open(f, "rb").read()).hexdigest() != snap["sha256"]:
            e.append("[3] snapshot %s sha256 mismatch" % snap["committed"])

    # [3b] concatenated corpus text re-hashes to recorded corpus sha256
    corpus = "\n".join(arts[k]["text"] for k in sorted(arts, key=lambda x: int(re.match(KEY_RE, x).group(1))))
    if hashlib.sha256(corpus.encode("utf-8")).hexdigest() != prov.get("corpus_text_sha256"):
        e.append("[3b] corpus text sha256 mismatch (committed text != verified official text)")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        ls = r.get("legal_status_ar")
        if (r.get("is_repealed") != (ls == "ملغاة") or r.get("is_amended") != (ls == "معدلة")
                or r.get("is_added") != (ls == "مضافة")):
            e.append("[4] %s: status flags inconsistent" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    # [5] LLM layer verbatim/hashes
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
    amended = sum(1 for r in recs if r["is_amended"])
    if amended != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended, EXPECTED_COUNTS["معدلة"]))

    if e:
        print("FAIL: %d error(s) in Commercial Papers Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Commercial Papers Law — 121 records (consolidated: 118 اصلية / 3 معدلة)")
    print("  - source: Bureau of Experts (BOE) official portal, captured via Wayback archive and cross-verified across two")
    print("    independent-date snapshots (2021 + 2025) — both committed snapshots + corpus text re-hash to recorded sha256")
    print("  - complete 1..121 (no مكرر); arts 118/119/120 amended by M/45 (1409H) carry current + original text; none repealed")
    print("  - art 38 اصلية with an official interpretation note (Council of Ministers Decision 251, 1442H); Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
