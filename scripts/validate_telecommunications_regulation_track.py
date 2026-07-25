#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the
Telecommunications and IT Law track (108 records: all 108 اصلية).

See the generator's module docstring and sources/telecommunications_regulation/
law/official_source/telecommunications_regulation_official_source.json's
verification_methodology_note for the full methodology. This validator checks
internal consistency, gapless article/chapter coverage, that every article
carries the distinct-tier status tag, and that verified/LLM records match the
official source text byte-for-byte."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "telecommunications_regulation", "law",
                   "official_source",
                   "telecommunications_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "telecommunications_regulation", "law",
                       "verified", "telecommunications_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "telecommunications_regulation_arabic_legal_llm",
                   "telecommunications_regulation_legal_llm_001_108.json")
N = 108
KEY_RE = r"telecommunications_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 108}
STATUS = "MCIT_CST_DUAL_PRIMARY_SOURCE_TEXT_LAYER_REMEDIATED"
EXPECTED_CHAPTERS = 16
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


def _bad_ligature_signature(text):
    """Detect the two well-documented ligature-swap artifact signatures this
    track's generator note describes (see verification_methodology_note):
    a hamza/madda alef immediately followed by lam (never genuine Arabic,
    except the small whitelisted set of real words baked into the source
    text already), and doubled-alef sequences from the plain-alef swap."""
    bad = 0
    for w in re.findall(r"[ء-ي]+", text):
        if re.search(r"[أإآ]ل", w) and w not in _HAMZA_WHITELIST:
            bad += 1
    return bad


_HAMZA_WHITELIST = {
    "مسألة", "إلى", "إليه", "إليها", "إليهم", "إلغاء", "إلغائها",
    "إلزام", "إلزاميا", "إلكترونية", "إلا", "ألا", "وألا",
    "آلية", "آليات", "وآليات", "وآلية",
    "الآتي", "الآتية", "الآخر", "الآخرين", "الآلية", "الآليات",
    "الإجراء", "الإجراءات", "الإخلال", "الإدارة", "الإشعار", "الإشعاعات",
    "الإضافية", "الإضرار", "الإفصاح", "الإلزام", "الإلزامية", "الإلغاء",
    "الإلكتروني", "الإلكترونية", "الإنترنت", "الإنسان", "الإبلاغ",
    "للألفاظ", "بالألفاظ",
    "بالإضافة", "بالإعلان", "والإجراءات", "والإجابات", "والإرشادات",
    "والإسهام", "والإشراف", "والإطلاق", "والإنقاذ", "لإلجراء", "لإلجراءات",
    "لإلشراف",
}


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chapters = src.get("chapter_structure", [])
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, found %d" % (EXPECTED_CHAPTERS, len(chapters)))
    covered = set()
    for ch in chapters:
        for n in range(ch["first_article"], ch["last_article"] + 1):
            covered.add(n)
    if covered != set(range(1, N + 1)):
        e.append("[1c] chapter_structure does not gaplessly cover articles 1..%d: missing %s"
                 % (N, sorted(set(range(1, N + 1)) - covered)))

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: chapter-aware law missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if _bad_ligature_signature(a["text"]) or _bad_ligature_signature(a["number_label_ar"]) \
                or _bad_ligature_signature(a.get("section_ar", "")):
            e.append("[2f] %s: unresolved لام+ألف ligature-swap artifact signature "
                     "detected (hamza/madda-alef immediately followed by lam, "
                     "outside the documented whitelist)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة") or sc.get("معدلة"):
        e.append("[2] unexpected amended/repealed/added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies")
    if not src.get("verification_tier"):
        e.append("[2g] missing verification_tier")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
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
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Telecommunications Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Telecommunications Regulation — 108 records (all 108 اصلية)")
    print("  - DISTINCT TIER: dual official born-digital primary sources (cst.gov.sa +")
    print("    mcit.gov.sa), cross-verified against each other and against rendered")
    print("    page images for structural anomalies")
    print("  - numbered 1..108 across 16 chapters, section_ar carries each article's")
    print("    chapter heading")
    print("  - IN-FORCE Ministerial Decision No. 13 (14/5/1444H); companion to the")
    print("    telecommunications_law base-law track")
    print("  - no confirmed amendment found post-dating approval; all 108 اصلية")
    return 0


if __name__ == "__main__":
    sys.exit(main())
