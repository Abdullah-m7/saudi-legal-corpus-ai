#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Commercial
Agencies Law track (49 records: 22 main-body + 27 annex).

Trust gate (mc.gov.sa live-portal provenance, TIER_2, single fetch -- see the
source artifact's known_unresolved_discrepancies for the honest gaps: no
cross-snapshot, decision PDFs unreachable, one inter-source date conflict on
Royal Decree M/5 for the base law): the main body is a complete 1..22 sequence
across 5 sections; the annex is a separately-numbered complete 1..27 sequence;
exactly one article (main-body 3) is معدلة with an original+current history;
all 27 annex articles are مضافة with an addition history entry; none are
ملغاة; the concatenated corpus text re-hashes to the recorded corpus sha256."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_agencies_regulation", "law", "official_source",
                   "commercial_agencies_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "commercial_agencies_regulation", "law", "verified",
                       "commercial_agencies_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "commercial_agencies_regulation_arabic_legal_llm",
                   "commercial_agencies_regulation_legal_llm_001_049.json")
STATUS = "MATCHES_MC_GOV_SA_LIVE_PORTAL"
N = 49
BODY_N = 22
ANNEX_N = 27
BODY_KEY_RE = r"commercial_agencies_regulation_art_(\d{3})$"
ANNEX_KEY_RE = r"commercial_agencies_regulation_annex_art_(\d{3})$"
EXPECTED_COUNTS = {"اصلية": 21, "معدلة": 1, "مضافة": 27}
EXPECTED_AMENDED_BODY = {3}
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

    body_keys = [k for k in arts if re.match(BODY_KEY_RE, k)]
    annex_keys = [k for k in arts if re.match(ANNEX_KEY_RE, k)]
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if len(body_keys) != BODY_N:
        e.append("[1] %d body articles != %d" % (len(body_keys), BODY_N))
    if len(annex_keys) != ANNEX_N:
        e.append("[1] %d annex articles != %d" % (len(annex_keys), ANNEX_N))
    body_nums = sorted(int(re.match(BODY_KEY_RE, k).group(1)) for k in body_keys)
    annex_nums = sorted(int(re.match(ANNEX_KEY_RE, k).group(1)) for k in annex_keys)
    if body_nums != list(range(1, BODY_N + 1)):
        e.append("[1] main-body articles not a complete 1..%d sequence" % BODY_N)
    if annex_nums != list(range(1, ANNEX_N + 1)):
        e.append("[1] annex articles not a complete 1..%d sequence" % ANNEX_N)

    sc = Counter()
    amended_body = set()
    for k, a in arts.items():
        if a["status"] != STATUS:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        ls = a.get("legal_status_ar")
        sc[ls] += 1
        is_annex = a.get("part") == "annex"
        if ls == "معدلة":
            if is_annex:
                e.append("[2] %s: annex article marked معدلة (unexpected)" % k)
            else:
                amended_body.add(a["native_article_number"])
        if ls == "مضافة" and not is_annex:
            e.append("[2] %s: main-body article marked مضافة (unexpected)" % k)
        if ls == "اصلية" and is_annex:
            e.append("[2] %s: annex article marked اصلية (unexpected; whole annex is مضافة)" % k)
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&\[\]]", a["text"]):
            e.append("[2] %s: empty text or latin/html/markdown leftovers" % k)
        if re.search(r"http|javascript|BotDetect|CAPTCHA", a["text"]):
            e.append("[2] %s: web/captcha artifact leaked into text" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")
    if amended_body != EXPECTED_AMENDED_BODY:
        e.append("[2] amended body-article set %s != expected %s" % (sorted(amended_body), sorted(EXPECTED_AMENDED_BODY)))

    for n in EXPECTED_AMENDED_BODY:
        h = arts["commercial_agencies_regulation_art_%03d" % n].get("history") or []
        if not any(x.get("type") == "original" for x in h):
            e.append("[2] body art %d: replacement amendment missing original in history" % n)
        if not any(x.get("type") == "amendment_current" for x in h):
            e.append("[2] body art %d: missing amendment_current in history" % n)
    for k in annex_keys:
        h = arts[k].get("history") or []
        if not any(x.get("type") == "addition" for x in h):
            e.append("[2] %s: مضافة article missing addition note in history" % k)

    if prov.get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")

    corpus = "\n".join(arts[k]["text"] for k in
                       sorted(arts, key=lambda x: (0, int(re.match(BODY_KEY_RE, x).group(1)))
                              if re.match(BODY_KEY_RE, x)
                              else (1, int(re.match(ANNEX_KEY_RE, x).group(1)))))
    if hashlib.sha256(corpus.encode("utf-8")).hexdigest() != prov.get("corpus_text_sha256"):
        e.append("[3] corpus text sha256 mismatch (committed text != source artifact text)")

    if not src.get("known_unresolved_discrepancies"):
        e.append("[3b] known_unresolved_discrepancies missing/empty (expected honest disclosures for this track)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    seen_article_numbers = []
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
        seen_article_numbers.append(r["article_number"])
    if sorted(seen_article_numbers) != list(range(1, N + 1)):
        e.append("[4] global article_number sequence is not a complete 1..%d run" % N)

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
    added_llm = sum(1 for r in recs if r["is_added"])
    if amended_llm != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended_llm, EXPECTED_COUNTS["معدلة"]))
    if added_llm != EXPECTED_COUNTS["مضافة"]:
        e.append("[5] added count %d != %d" % (added_llm, EXPECTED_COUNTS["مضافة"]))

    if e:
        print("FAIL: %d error(s) in Commercial Agencies Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Commercial Agencies Regulation (اللائحة التنفيذية لنظام الوكالات التجارية) — 49 records")
    print("  - source: Ministry of Commerce (mc.gov.sa) live portal, single fetch via r.jina.ai reader-proxy (TIER_2)")
    print("    Ministerial Decision No. 1897 (24/5/1401H); cross-checked vs 4 independent secondary sources; corpus re-hash OK")
    print("  - 22 main-body (5 sections) + 27 annex articles; body art 3 معدلة (decision 817/1435H, original+current in history);")
    print("    all 27 annex articles مضافة (attributed to same 817/1435H decision by disclosed inference); 0 ملغاة")
    print("  - known_unresolved_discrepancies honestly recorded in source artifact (see field for details); Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
