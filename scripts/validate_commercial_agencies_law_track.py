#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Commercial Agencies Law track (6 records).

Trust gate (BOE-archive provenance): the numbered sequence is a complete 1..6
(no مكرر); every article carries an explained legal_status consistent with its
is_repealed/is_amended/is_added flags; the two committed official BOE snapshots
re-hash to the sha256 recorded in the source artifact; and the concatenated
corpus text re-hashes to the recorded corpus sha256 (so the committed text is
exactly the cross-snapshot-verified official text). Exactly three articles
(4, 5, 6) are معدلة, each carrying its history: arts 4 (M/32, 1400H) and 5 (M/8,
1393H) carry the current amended text plus the original; art 6's own text was not
replaced and its history records the M/5 (1389H) addition. None are repealed.
Tatweel is banned EXCEPT the 'هـ' digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_agencies", "law", "official_source",
                   "commercial_agencies_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "commercial_agencies", "law", "verified",
                       "commercial_agencies_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "commercial_agencies_arabic_legal_llm",
                   "commercial_agencies_law_legal_llm_001_006.json")
STATUS = "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"
N = 6
KEY_RE = r"commercial_agencies_art_(\d{3})"
EXPECTED_COUNTS = {"اصلية": 3, "معدلة": 3}
EXPECTED_AMENDED = {4, 5, 6}
REPLACEMENT_AMENDED = {4, 5}
ADDITION_AMENDED = {6}
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts if not k.endswith("_mukarrar"))
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    sc = Counter()
    amended = set()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        ls = a.get("legal_status_ar")
        sc[ls] += 1
        if ls == "معدلة":
            amended.add(int(re.match(KEY_RE, k).group(1)))
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")
    if amended != EXPECTED_AMENDED:
        e.append("[2] amended set %s != expected %s" % (sorted(amended), sorted(EXPECTED_AMENDED)))
    for n in REPLACEMENT_AMENDED:
        h = arts["commercial_agencies_art_%03d" % n].get("history") or []
        if not any(x.get("type") == "original" for x in h):
            e.append("[2] art %d: replacement amendment missing original in history" % n)
    for n in ADDITION_AMENDED:
        h = arts["commercial_agencies_art_%03d" % n].get("history") or []
        if not any(x.get("type") == "addition" for x in h):
            e.append("[2] art %d: addition amendment missing addition note in history" % n)

    if prov.get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    snaps = prov.get("archive_snapshots", [])
    if len(snaps) < 2:
        e.append("[3] fewer than 2 archive snapshots recorded")
    for snap in snaps:
        f = os.path.join(ROOT, snap["committed"])
        if not os.path.isfile(f):
            e.append("[3] missing committed snapshot %s" % snap["committed"]); continue
        if hashlib.sha256(open(f, "rb").read()).hexdigest() != snap["sha256"]:
            e.append("[3] snapshot %s sha256 mismatch" % snap["committed"])

    corpus = "\n".join(arts[k]["text"] for k in sorted(arts, key=lambda x: int(re.match(KEY_RE, x).group(1))))
    if hashlib.sha256(corpus.encode("utf-8")).hexdigest() != prov.get("corpus_text_sha256"):
        e.append("[3b] corpus text sha256 mismatch (committed text != verified official text)")

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
    amended_llm = sum(1 for r in recs if r["is_amended"])
    if amended_llm != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended_llm, EXPECTED_COUNTS["معدلة"]))

    if e:
        print("FAIL: %d error(s) in Commercial Agencies Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Commercial Agencies Law — 6 records (consolidated: 3 اصلية / 3 معدلة)")
    print("  - source: Bureau of Experts (BOE) official portal via Wayback archive; two independent-date snapshots")
    print("    (2023 + 2025, byte-identical) + corpus text re-hash to recorded sha256; Royal Decree M/11 (1382H); ساري")
    print("  - arts 4 (M/32 1400H) + 5 (M/8 1393H) replaced: current text + original in history; art 6 addition (M/5 1389H)")
    print("  - complete 1..6 (no مكرر); none repealed; decorative in-word tatweel removed; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
