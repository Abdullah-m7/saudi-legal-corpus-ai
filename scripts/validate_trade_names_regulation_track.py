#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Trade Names Law
track (اللائحة التنفيذية لنظام الأسماء التجارية; 18 articles + 1 annex = 19
records, ALL اصلية; FLAT structure -- no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and sources/
trade_names_regulation/law/official_source/trade_names_regulation_official_
source.json's verification_methodology_note / disambiguation_note_ar for the
full account: this regulation was issued as clause "ثانيا" of a JOINT/omnibus
Ministry of Commerce Decision No. 288 that also approves three OTHER distinct
instruments (a Commercial Register regulation, a branch-register correction
mechanism, and pre-effectiveness trade-name controls) -- only clause ثانيا is
ingested here. No direct .gov.sa-hosted copy of this regulation's text was
reachable this pass (uqn.gov.sa is an unrenderable SPA; laws.boe.gov.sa has no
dedicated page; mc.gov.sa direct fetch failed at the connection level).
PRIMARY TEXT: qanoonsa.com (which explicitly disclaims official-source
status), cross-checked via a byte-identical Wayback Machine snapshot of the
same page and an independent secondary source (ndmlaw.sa) with verbatim
matches -> TIER_3. This validator does not re-adjudicate provenance; it only
checks internal self-consistency and that every discrepancy is still
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "trade_names_regulation", "law", "official_source",
                   "trade_names_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "trade_names_regulation", "law", "verified",
                       "trade_names_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "trade_names_regulation", "law", "verified",
                       "trade_names_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "trade_names_regulation_arabic_legal_llm",
                   "trade_names_regulation_legal_llm_001_019.json")
N_ARTICLES = 18
N_TOTAL = 19
KEY_RE = r"trade_names_regulation_(art|annex)_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": N_TOTAL, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

VERIFICATION_TIER = "TIER_3"
FLAGGED_DISCREPANCY_KEYS = {
    "trade_names_regulation_joint_decision_disambiguation",
    "trade_names_regulation_annex4_out_of_scope",
    "trade_names_regulation_commercial_register_annexes_out_of_scope",
    "trade_names_regulation_boe_no_dedicated_page",
    "trade_names_regulation_uqn_gazette_spa_unreachable",
    "trade_names_regulation_mc_gov_sa_direct_fetch_failed",
    "trade_names_regulation_qanoonsa_primary_text_disclaimer",
    "trade_names_regulation_prior_research_hijri_date_corrected",
    "trade_names_regulation_old_regulation_no_explicit_repeal",
    "trade_names_regulation_tables_flattened",
    "trade_names_regulation_numeral_format_inconsistency",
    "trade_names_regulation_rlm_marks_stripped",
    "trade_names_regulation_draft_consultation_predecessor",
}
AR = "ء-ي"
RLM = "‏"


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

    if len(arts) != N_TOTAL:
        e.append("[1] %d records != %d (18 articles + 1 annex)" % (len(arts), N_TOTAL))
    if src.get("article_count") != N_ARTICLES:
        e.append("[1] article_count field != %d" % N_ARTICLES)
    if src.get("annex_count") != 1:
        e.append("[1] annex_count field != 1")
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    art_nums = sorted(int(re.match(KEY_RE, k).group(2)) for k in arts
                       if re.match(KEY_RE, k).group(1) == "art")
    if art_nums != list(range(1, N_ARTICLES + 1)):
        e.append("[1b] article numbers not contiguous 1..%d: got %s" % (N_ARTICLES, art_nums))
    annex_keys = [k for k in arts if re.match(KEY_RE, k).group(1) == "annex"]
    if annex_keys != ["trade_names_regulation_annex_001"]:
        e.append("[1c] expected exactly one annex key trade_names_regulation_annex_001, got %s"
                 % annex_keys)

    # FLAT regulation: chapter_structure MUST be empty (no separate باب/فصل structure)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1d] this regulation is flat; chapter_structure must be [] but is %r" % (chs,))

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if a.get("verification_tier") != VERIFICATION_TIER:
            e.append("[2] %s: verification_tier must be %s" % (k, VERIFICATION_TIER))
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if re.search(r"[A-Za-z]", a["text"]):
            e.append("[2] %s: unexpected latin leftovers" % k)
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat regulation" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if RLM in a["text"] or "‎" in a["text"]:
            e.append("[2] %s: residual RLM/LRM mark present (must be stripped)" % k)
        if (ls == "معدلة") or (ls == "مضافة") or (ls == "ملغاة"):
            e.append("[2] %s: no article/annex is amended/added/repealed this pass" % k)
        if a.get("history"):
            e.append("[2i] %s: no article is amended/added this pass; history must be empty" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        is_annex = re.match(KEY_RE, k).group(1) == "annex"
        if bool(a.get("is_annex")) != is_annex:
            e.append("[2j] %s: is_annex flag/key-pattern mismatch" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not src.get("disambiguation_note_ar"):
        e.append("[2d] missing disambiguation_note_ar explaining the joint-decision split")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding decision)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "٢٨٨" not in decrees and "288" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 288")

    if src.get("decree") != "قرار وزير التجارة رقم (٢٨٨)" \
            or src.get("decree_date_hijri") != "20/9/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified MoC Decision "
                 "288, 20/9/1446H (20 Ramadan 1446H)")
    if src.get("gazette_issue") != "5079":
        e.append("[2j] gazette_issue must be 5079")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments confirmed to the "
                 "founding text)")
    if not src.get("preamble_ar", "").strip():
        e.append("[2l] preamble_ar must not be empty -- the full operative decision text was "
                 "located and verified this pass")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("trade_names_regulation_art_001", {}).get("text", "")
    for token in ("الحجز:", "القيد:", "المرسوم الملكي رقم (م / ٨٣)"):
        if token not in art1:
            e.append("[2j] Article 1 missing expected defined term %r" % token)
    art8 = arts.get("trade_names_regulation_art_008", {}).get("text", "")
    if "(ستين)" not in art8:
        e.append("[2j] Article 8 missing expected 60-day reservation period")
    art14 = arts.get("trade_names_regulation_art_014", {}).get("text", "")
    if "المقابل المالي" not in art14:
        e.append("[2j] Article 14 missing expected fee-schedule cross-reference")
    art18 = arts.get("trade_names_regulation_art_018", {}).get("text", "")
    if "الجريدة الرسمية" not in art18:
        e.append("[2j] Article 18 missing expected gazette-publication clause")
    annex = arts.get("trade_names_regulation_annex_001", {}).get("text", "")
    if "٢٠٠" not in annex and "مائتا" not in annex:
        e.append("[2j] Annex 1 missing expected 200-riyal Arabic-name reservation fee")
    # no repeal language anywhere (expected: supersession is via the parent LAW's own
    # Article 23, not a textual repeal clause inside this regulation)
    for k, a in arts.items():
        if "يلغى" in a["text"] or "يلغي" in a["text"] or "الملغاة" in a["text"]:
            e.append("[2j] %s: unexpected repeal-language token found (no repeal is expected "
                     "or confirmed for this founding regulation)" % k)

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_TOTAL:
        e.append("[4] %d verified records != %d" % (len(ver), N_TOTAL))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("is_amended") is not False or r.get("is_added") is not False \
                or r.get("is_repealed") is not False:
            e.append("[4] %s: is_amended/is_added/is_repealed must all be False" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_TOTAL:
        e.append("[4b] summary record_count != %d" % N_TOTAL)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if not summary.get("disambiguation_note_ar"):
        e.append("[4b] summary missing disambiguation_note_ar")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_TOTAL or len(recs) != N_TOTAL:
        e.append("[5] llm count != %d" % N_TOTAL)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Trade Names Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Trade Names Law "
         "(اللائحة التنفيذية لنظام الأسماء التجارية)")
    print("  - 18 articles + 1 annex = 19 records, ALL اصلية (0 معدلة, 0 مضافة, 0 ملغاة)")
    print("  - FLAT regulation (chapter_structure == [], section_ar empty by design)")
    print("  - Ministry of Commerce Decision No. (288), clause \"ثانيا\", dated 20 Ramadan 1446H")
    print("    (20 March 2025G); published Umm al-Qura Gazette No. 5079 (30 March 2025G)")
    print("  - JOINT/omnibus decision: only clause ثانيا ingested here; clauses أولا/ثالثا")
    print("    (Commercial Register-side) and رابعا (pre-effectiveness trade-name controls,")
    print("    a distinct instrument) are disclosed as out-of-scope, NOT ingested")
    print("  - VERIFICATION TIER: TIER_3 -- no direct .gov.sa-hosted copy of this regulation's")
    print("    text reachable this pass (uqn.gov.sa SPA unrenderable; laws.boe.gov.sa has no")
    print("    dedicated page; mc.gov.sa direct fetch failed). PRIMARY: qanoonsa.com (self-")
    print("    disclaimed as non-official), cross-checked via a byte-identical Wayback snapshot")
    print("    and an independent secondary source (ndmlaw.sa) with verbatim-matching quotes")
    print("  - Prior research's stated Hijri date (30 Rabi' II 1446H) was found INCORRECT and")
    print("    corrected here via independent Hijri<->Gregorian conversion")
    print("  - NO repeal of any predecessor instrument found in this regulation's own text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
