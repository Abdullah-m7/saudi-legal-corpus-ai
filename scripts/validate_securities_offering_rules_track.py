#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the قواعد طرح الأوراق المالية والالتزامات المستمرة track.

150 records: 112 numbered articles and 38 APPENDIX records. All اصلية.

The appendix records are the reason this validator differs from its siblings.
The annex block of these Rules carries no «المادة» heading, so it was absorbed
whole into article 112 until the ingestion pipeline learned to cut it at the
gazette's own «الملحق N:» marks. Two properties therefore have to be checked
here and nowhere else:

  * the cut left article 112 intact — it must still be the «النشر والنفاذ»
    provision and must not have grown back into a 268,000-char block;
  * every appendix record says so about itself (is_appendix, «الملحق» label,
    section «الملاحق»), because an appendix cited as «المادة N» is a false
    citation and the corpus must not make one possible.

VERIFICATION TIER: TIER_1 -- full text fetched directly from the Umm Al-Qura
Official Gazette's own server-rendered HTML page. This validator only checks
internal self-consistency of the ingested text and that every discrepancy is
disclosed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "securities_offering_rules"
SRC = os.path.join(ROOT, "sources", KEY, "official_source",
                   "%s_official_source.json" % KEY)
RECORDS = os.path.join(ROOT, "sources", KEY, "verified",
                       "%s_verified_records.jsonl" % KEY)
SUMMARY = os.path.join(ROOT, "sources", KEY, "verified",
                       "%s_verified_summary.json" % KEY)
LLM = os.path.join(ROOT, "data", "%s_arabic_legal_llm" % KEY,
                   "%s_legal_llm_001_150.json" % KEY)

N_ARTICLES = 112
N_APPENDICES = 38
N_RECORDS = 150
ART_RE = r"%s_art_(\d{3})$" % KEY
APX_RE = r"%s_appendix_(\d{3})$" % KEY
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
FLAGGED_DISCREPANCY_KEYS = {
    "%s_source_is_gazette_html_only" % KEY,
    "%s_units_that_are_not_articles" % KEY,
    "%s_appendix_lettered_variants" % KEY,
}
# Article 112 is the whole point of the annex split: before it, this record held
# the entire annex block. Anchoring on its opening words is what would catch a
# regression that quietly re-absorbed them.
ART_112_OPENS = "النشر والنفاذ"
ART_112_MAX_CHARS = 400
AR = "ء-ي"
TASHKEEL = re.compile("[ً-ٰٟ]")  # excludes Arabic-Indic digits U+0660-0669


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
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure counts
    if len(arts) != N_RECORDS:
        e.append("[1] %d records != %d" % (len(arts), N_RECORDS))
    for f, want in (("article_count", N_ARTICLES), ("appendix_count", N_APPENDICES),
                    ("record_count", N_RECORDS)):
        if src.get(f) != want:
            e.append("[1] %s field != %d" % (f, want))
    nums, apx = [], []
    for k, a in arts.items():
        m, ma = re.match(ART_RE, k), re.match(APX_RE, k)
        if m:
            nums.append(int(m.group(1)))
            if a.get("is_appendix") is not False:
                e.append("[1] %s: is_appendix must be False" % k)
        elif ma:
            apx.append(int(ma.group(1)))
            if a.get("is_appendix") is not True:
                e.append("[1] %s: is_appendix must be True" % k)
        else:
            e.append("[1] %s: does not match article or appendix key pattern" % k)
    EXPECTED_NUMBERS = list(range(1, N_ARTICLES + 1))
    MISSING_IN_SOURCE = []
    if sorted(nums) != EXPECTED_NUMBERS:
        e.append("[1] article numbers differ from the source's own numbering")
    if sorted(apx) != list(range(1, N_APPENDICES + 1)):
        e.append("[1] appendix records are not a complete 1..%d run" % N_APPENDICES)
    if src.get("missing_article_numbers") != MISSING_IN_SOURCE:
        e.append("[1] declared missing_article_numbers != %s" % MISSING_IN_SOURCE)

    # [1b] the annex split held
    a112 = arts.get("%s_art_112" % KEY)
    if not a112:
        e.append("[1b] article 112 is missing")
    else:
        if not (a112.get("text") or "").startswith(ART_112_OPENS):
            e.append("[1b] article 112 no longer opens on «%s»" % ART_112_OPENS)
        if len(a112.get("text") or "") > ART_112_MAX_CHARS:
            e.append("[1b] article 112 is %d chars — the annex block has been re-absorbed"
                     % len(a112.get("text") or ""))
    for k, a in arts.items():
        if not re.match(APX_RE, k):
            continue
        if not (a.get("number_label_ar") or "").startswith("الملحق"):
            e.append("[1b] %s: appendix label must be the source's «الملحق N»" % k)
        if a.get("section_ar") != "الملاحق":
            e.append("[1b] %s: appendix section_ar must be الملاحق" % k)

    # [2] per-record content + status
    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != "MATCHES_UQN_GAZETTE":
            e.append("[2] %s: expected status MATCHES_UQN_GAZETTE" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: structure_status divergence" % k)
        if ls != "اصلية":
            e.append("[2] %s: all records must be اصلية" % k)
        if a.get("history"):
            e.append("[2] %s: article-level history must be empty" % k)
        t = a.get("text", "")
        if not t.strip():
            e.append("[2] %s: empty text" % k)
        if len(t.strip()) < 15:
            e.append("[2] %s: suspiciously short text" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if TASHKEEL.search(t):
            e.append("[2] %s: residual tashkeel" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel" % k)
        for bad, lbl in (("\xa0", "non-breaking space"), ("​", "zero-width"),
                         ("‏", "bidi mark"), ("‎", "bidi mark"),
                         ("“", "curly quote"), ("”", "curly quote")):
            if bad in t:
                e.append("[2f] %s: residual %s artifact" % (k, lbl))
        if "نسخة تجريبية" in t or "الرئيسية القرارات" in t:
            e.append("[2f] %s: site navigation boilerplate leaked into article text" % k)
        if re.search(r"(?<!\sفي)(?<!\sمن)(?<!\sعلى)(?<!\sإلى)(?<!\sالى)(?<!\sوفق)(?<!\sحسب)"
                 r"(?<!\sضمن)(?<!\sوفقا)(?<!\sبحسب)(?<!\sوفقاً)(?<!\sبموجب)"
                 r"\s(الباب|الفصل)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر"
                 r"|(?:الحادي|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)\s+عشر"
                 r"|العشرون|التمهيدي)\s*:?\s*[^\n]{0,90}$", t):
            e.append("[2f] %s: trailing chapter heading leaked into article text" % k)
    if sc.get("اصلية", 0) != N_RECORDS:
        e.append("[2] اصلية count %d != %d" % (sc.get("اصلية", 0), N_RECORDS))

    # [2c] chapter_structure coverage
    cov, apx_cov = set(), set()
    for ch in src.get("chapter_structure") or []:
        for field, sink in (("articles", cov), ("appendices", apx_cov)):
            spec = ch.get(field, "")
            if "-" in spec:
                lo, hi = (int(x) for x in spec.split("-"))
            elif spec.isdigit():
                lo = hi = int(spec)
            else:
                continue
            sink |= set(range(lo, hi + 1))
    if set(EXPECTED_NUMBERS) - cov:
        e.append("[2c] chapter_structure does not cover articles %s"
                 % sorted(set(EXPECTED_NUMBERS) - cov))
    if set(range(1, N_APPENDICES + 1)) - apx_cov:
        e.append("[2c] chapter_structure does not cover the appendix records")

    # [2d] methodology + disclosed discrepancies
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies") or []
    missing = FLAGGED_DISCREPANCY_KEYS - {d["article_key"] for d in disc}
    if missing:
        e.append("[2e] expected discrepancy entries missing: %s" % sorted(missing))

    # [2j] anchor facts
    if src.get("gazette_publication_date_hijri") != "23/1/1448":
        e.append("[2j] gazette_publication_date_hijri must be 23/1/1448")
    if src.get("gazette_publication_date_gregorian") != "2026-07-08":
        e.append("[2j] gazette_publication_date_gregorian must be 2026-07-08")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("document") != "قواعد طرح الأوراق المالية والالتزامات المستمرة":
        e.append("[2j] document title mismatch")
    if src.get("base_law_track") != "capital_market_law":
        e.append("[2j] base_law_track must be capital_market_law")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_RECORDS:
        e.append("[4] %d verified records != %d" % (len(ver), N_RECORDS))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_appendix") is not bool(a.get("is_appendix")):
            e.append("[4] %s: is_appendix != source" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_RECORDS:
        e.append("[4b] summary record_count != %d" % N_RECORDS)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source")

    # [5] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_RECORDS or len(recs) != N_RECORDS:
        e.append("[5] llm count != %d" % N_RECORDS)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("text_summarized_or_paraphrased") is not False:
            e.append("[5] %s: text_summarized_or_paraphrased must be False" % r["article_key"])
        if r.get("is_appendix") and "المادة" in (r.get("article_title_ar") or ""):
            e.append("[5] %s: an appendix must not be titled «المادة»" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Rules on the Offer of Securities track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Rules on the Offer of Securities and Continuing Obligations")
    print("  - 150 records: 112 articles + 38 appendices; all 150 اصلية")
    print("  - the annex split held: article 112 is the «النشر والنفاذ» provision alone,")
    print("    and every appendix declares itself one rather than posing as an article")
    print("  - Full text fetched directly from the Umm Al-Qura Official Gazette's own")
    print("    server-rendered HTML (the official publication of record for Saudi laws)")
    print("  - VERIFICATION TIER: TIER_1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
