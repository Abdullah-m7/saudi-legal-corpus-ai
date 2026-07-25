#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Real Estate
Brokerage Law track (اللائحة التنفيذية لنظام الوساطة العقارية; 27 records,
ALL اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 8 فصول, article 1 unsectioned).

VERIFICATION TIER -- see the generator's module docstring and
sources/real_estate_brokerage_regulation/law/official_source/
real_estate_brokerage_regulation_official_source.json's
verification_methodology_note for the full account: governing text is a
direct VISUAL transcription of REGA's own hosted 23-page PDF (fetched
directly, HTTP 200; automated text-layer extraction produces known Arabic
lam-alef/RTL reordering artifacts and was NOT used as the governing text),
cross-verified word-for-word against the raw text of the official Umm
al-Qura Gazette portal's own page (fetched directly, not via a summarizing
tool) -- identical across all 27 articles except one immaterial one-word
preposition variant in Article 14 item 10 (see FLAGGED_DISCREPANCY_KEYS).
Decision identity (132/ق, 24/06/1444H) independently confirmed by two
further secondary sources. This is TIER_1 -- the strongest tier in this
corpus's own taxonomy. This validator does not re-adjudicate provenance; it
only checks internal self-consistency and that every discrepancy is still
recorded, INCLUDING an explicit honesty check that a claimed-but-unverified
subsequent amendment is disclosed and NOT applied to any article.

MATERIAL FACTS checked: 8 فصول (chapter_structure covering articles 2-27;
article 1 is unsectioned definitions), continuous 1-27 numbering, all
articles اصلية (this is the FIRST Implementing Regulation under the base
law, so there is no predecessor regulation to supersede), and that
law_component is "regulation" throughout (distinguishing every record here
from the separate base-law track, track_id: real_estate_brokerage)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_brokerage_regulation", "law", "official_source",
                   "real_estate_brokerage_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_brokerage_regulation", "law", "verified",
                       "real_estate_brokerage_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "real_estate_brokerage_regulation", "law", "verified",
                       "real_estate_brokerage_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "real_estate_brokerage_regulation_arabic_legal_llm",
                   "real_estate_brokerage_regulation_legal_llm_001_027.json")
PDF = os.path.join(ROOT, "inputs", "real_estate_brokerage_regulation_official_pdfs",
                   "real_estate_brokerage_regulation_rega_official_ar.pdf")
N = 27
KEY_RE = r"real_estate_brokerage_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 27, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 8
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STATUS_MAIN = "REGA_OFFICIAL_PDF_VISUALLY_VERIFIED_X_UQN_GAZETTE_FULLTEXT_CROSSCHECK_TIER1_BOE_UNREACHABLE"
FLAGGED_DISCREPANCY_KEYS = {
    "real_estate_brokerage_regulation_no_preamble_page_in_source_pdf",
    "real_estate_brokerage_regulation_pdf_text_layer_ligature_reordering_artifacts",
    "real_estate_brokerage_regulation_article14_preposition_variant",
    "real_estate_brokerage_regulation_unverified_amendment_claim_5_23_m_23",
    "real_estate_brokerage_regulation_gazette_date_minor_variance",
    "real_estate_brokerage_regulation_boe_unreachable",
    "real_estate_brokerage_regulation_annex_tables_out_of_scope",
    "real_estate_brokerage_regulation_no_predecessor_regulation_to_supersede",
}
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
    for p in (SRC, RECORDS, SUMMARY, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d فصول, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    for c in chapters:
        if not c.get("label_ar", "").startswith("الفصل"):
            e.append("[1c] chapter entry %r: expected a فصل label" % c)
        if not c.get("title_ar", "").strip():
            e.append("[1c] chapter entry %r: missing title_ar" % c)

    # article 1 must be unsectioned; articles 2-27 must each carry a non-empty section_ar
    if (arts.get("real_estate_brokerage_regulation_art_001", {}).get("section_ar") or "") != "":
        e.append("[1d] article 1 expected to be unsectioned (section_ar == '')")
    for n in range(2, N + 1):
        k = "real_estate_brokerage_regulation_art_%03d" % n
        if not (arts.get(k, {}).get("section_ar") or "").strip():
            e.append("[1d] %s: missing section_ar (expected a فصل title)" % k)

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_MAIN:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_MAIN, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: unexpected latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if not a.get("secondary_cross_check"):
            e.append("[2] %s: missing secondary_cross_check tag" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no amendments expected; history must be empty" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2b] unexpected section-vs-structure divergence recorded")
    if src["provenance"].get("pdf_has_text_layer") is not True:
        e.append("[2b] expected pdf_has_text_layer=True (digitally-authored PDF, not a scan)")
    if src["provenance"].get("pdf_text_layer_reliable") is not False:
        e.append("[2b] expected pdf_text_layer_reliable=False (known ligature/RTL artifacts)")
    if "UNREACHABLE" not in (src["provenance"].get("boe_portal_status") or ""):
        e.append("[2b] expected documented BOE portal unreachability status")

    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed REGA PDF sha256 mismatch")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))
        # honesty check: the unverified-amendment discrepancy must explicitly say it was NOT applied
        amend_disc = next((d for d in disc
                           if d["article_key"] == "real_estate_brokerage_regulation_unverified_amendment_claim_5_23_m_23"),
                          None)
        if amend_disc is None or "404" not in amend_disc.get("description", ""):
            e.append("[2e] unverified-amendment discrepancy must document the direct-fetch HTTP 404 finding")

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record founding decision)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "132" not in decrees:
            e.append("[2k] amendment_history must reference founding decision 132/ق")

    # spot-checks anchoring key facts
    art1 = arts.get("real_estate_brokerage_regulation_art_001", {}).get("text", "")
    if "الترخيص" not in art1 or "م/130" not in art1:
        e.append("[2j] Article 1 missing expected definitions block / base-law citation (م/130)")
    art3 = arts.get("real_estate_brokerage_regulation_art_003", {}).get("text", "")
    if "(18)" not in art3:
        e.append("[2j] Article 3 missing expected minimum-age (18) requirement")
    art21 = arts.get("real_estate_brokerage_regulation_art_021", {}).get("text", "")
    if "(25%)" not in art21 or "العربون" not in art21:
        e.append("[2j] Article 21 missing expected 25%% earnest-money commission clause")
    art27 = arts.get("real_estate_brokerage_regulation_art_027", {}).get("text", "")
    if "تُنشر اللائحة" not in art27:
        e.append("[2j] Article 27 missing expected publication/entry-into-force clause")

    # NO named repeal of a predecessor regulation anywhere (there is none to repeal)
    for k, a in arts.items():
        if re.search(r"يلغي اللائحة|يلغى اللائحة|إلغاء اللائحة|تحل محل اللائحة", a["text"]):
            e.append("[2j] %s: unexpected predecessor-repeal clause (none should exist)" % k)

    if src.get("decree") != "قرار مجلس إدارة الهيئة العامة للعقار رقم (132/ق)" \
            or src.get("decree_date_hijri") != "24/06/1444":
        e.append("[2j] decree/decree_date_hijri mismatch with Decision No. 132/ق, 24/06/1444H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendments)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
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
        if r.get("is_amended"):
            e.append("[4] %s: is_amended must be False (no amendments in this regulation)"
                     % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")
    if not summary.get("known_unresolved_discrepancies"):
        e.append("[4b] summary missing known_unresolved_discrepancies")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: llm law_component must be 'regulation'" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Real Estate Brokerage Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Real Estate Brokerage Law")
    print("  (اللائحة التنفيذية لنظام الوساطة العقارية)")
    print("  - 27 records: ALL اصلية (no confirmed amendments), 0 ملغاة, 0 مضافة")
    print("  - 8 فصول (chapters, articles 2-27), article 1 unsectioned definitions, numbering 1-27")
    print("  - VERIFICATION TIER: TIER_1 -- REGA's own hosted PDF visually transcribed (automated")
    print("    text-layer extraction has known Arabic ligature/RTL artifacts, not used), cross-")
    print("    verified word-for-word against the Umm al-Qura Gazette portal's own raw page text")
    print("    (fetched directly); identical except one immaterial preposition variant (Art 14/10)")
    print("  - Decision: REGA Board Decision No. (132/ق), 24/06/1444H; issued under Article 23 of")
    print("    the base law (Royal Decree M/130, track_id: real_estate_brokerage, law_component")
    print("    'law'); this track's law_component is 'regulation'")
    print("  - NO predecessor regulation superseded (first Implementing Regulation under this law)")
    print("  - a claimed subsequent amendment (\"5-23-م-23\") could NOT be independently verified")
    print("    (direct fetch of its source URL returned HTTP 404) and was NOT applied to any article")
    print("  - laws.boe.gov.sa connection-reset this round; not separately indexed as expected for a")
    print("    REGA Board-issued instrument")
    return 0


if __name__ == "__main__":
    sys.exit(main())
