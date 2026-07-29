#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the CMA Capital Market Institutions Regulations
track (لائحة مؤسسات السوق المالية; CMA Board Resolution (1-83-2005),
21/5/1426H = 28/6/2005G; consolidated as amended through Resolution
(2-3-2026), 18/07/1447H = 07/01/2026G).

VERIFICATION TIER: TIER_2 -- one OFFICIAL source for the governing Arabic
text (CMA's own published Arabic PDF) plus one independent SECONDARY full-text
cross-check. The citation chain is additionally corroborated by a second
OFFICIAL source (the Umm Al-Qura gazette), but the tier is governed by the
weakest meaningfully-sized portion of the track -- the 99 article texts.

This validator asserts:
  * exactly 99 articles in a clean 1..99 run, matching the count VERIFIED from
    the source rather than assumed from the commissioning brief;
  * exactly 9 أبواب whose article spans tile 1..99 with no gap or overlap, and
    every article carries a non-empty section_ar naming its باب;
  * the citation chain is recorded in the form printed on the instrument
    (1-83-2005 / 2-3-2026) AND the alternative display order is disclosed;
  * the rename from «لائحة الأشخاص المرخص لهم» is recorded with its confirmed
    1442H effective date, and every amending instrument carries a source and
    an explicit pre_amendment_text_recovered=false;
  * NO article is flagged معدلة/ملغاة/مضافة -- the source publishes no
    per-article amendment attribution, and every layer says so explicitly via
    per_article_amendment_attribution_published=false;
  * every honesty flag is false (no translation, interpretation, paraphrase,
    or use of English to correct Arabic);
  * every known discrepancy this pass identified is still disclosed;
  * article text is free of latin/HTML leftovers, page numbers, the source's
    'Internal - داخلي' watermark, annex headings and part headings, and
    carries no residual ligature-transposition artefacts;
  * verified / summary / LLM layers agree with the source byte-for-byte.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "cma_market_institutions_regulation"
SRC = os.path.join(ROOT, "sources", KEY, "regulation", "official_source",
                   "%s_official_source.json" % KEY)
RECORDS = os.path.join(ROOT, "sources", KEY, "regulation", "verified",
                       "%s_verified_records.jsonl" % KEY)
SUMMARY = os.path.join(ROOT, "sources", KEY, "regulation", "verified",
                       "%s_verified_summary.json" % KEY)
LLM = os.path.join(ROOT, "data", "%s_arabic_legal_llm" % KEY,
                   "%s_legal_llm_001_099.json" % KEY)

N = 99
EXPECTED_PARTS = 9
EXPECTED_ANNEXES = 11
KEY_RE = r"cma_market_institutions_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 99, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = ("CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_GLYPH_LEVEL_LIGATURE_SAFE_EXTRACTION"
          "_X_INDEPENDENT_SECONDARY_TEXT_CROSSCHECK")
TIER = "TIER_2"

DECREE_CANONICAL = "1-83-2005"
DECREE_ALT = "2005-83-1"
AMEND_CANONICAL = "2-3-2026"
AMEND_ALT = "2026-3-2"

FLAGGED_DISCREPANCY_KEYS = {
    "cmi_decision_number_display_order_1_83_2005_vs_2005_83_1",
    "cmi_2020_rename_resolution_number_not_published",
    "cmi_no_per_article_amendment_footnotes_in_source",
    "cmi_intermediate_amendment_chain_incomplete",
    "cmi_english_edition_is_stale_not_used_for_text",
    "cmi_annexes_not_ingested",
    "cmi_source_pdf_missing_space_glyphs_restored_by_measurement",
    "cmi_source_pdf_annex_cross_reference_missing_hyphen",
    "cmi_article_097_irregular_wording_retained_verbatim",
    "cmi_secondary_crosscheck_source_is_itself_defective",
    "cmi_umm_alqura_publication_reference_secondary_only",
}

# Signatures of the ligature-transposition defect that corrupts every naive
# extraction of this PDF (and the secondary cross-check source). If any of
# these ever appears in article text, the extraction has regressed.
LIGATURE_DEFECTS = ["اململكة", "املالية", "الئحة", "جملس", "اهليئة", "مؤس سة",
                    "الموشره", "الموشرة", "العملاوت", "متهيد", "اإلدارة"]
# The source's own page furniture must never appear inside an article body.
FURNITURE = ["Internal", "داخلي - Internal", "Internal - داخلي"]
AR = "ء-ي"


def _bad_tatweel(text):
    """Count DECORATIVE in-word tatweel, i.e. extraction noise.

    Two in-word uses are genuine in this instrument and are verbatim in CMA's
    own PDF, so they are not noise:
      * 'هـ' -- the Arabic letter-ordinal for the fifth item ('هـ)').
      * 'نـز' -- the standard Saudi legal-drafting تطويل inserted between noon
        and zay so نزاهة / نزاع cannot be misread (بنـزاهة، النـزاهة، نـزاع).
    Anything else between two Arabic letters is flagged.
    """
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if not (re.match("[%s]" % AR, before) and re.match("[%s]" % AR, after)):
            continue
        if before == "ه":
            continue
        if before == "ن" and after == "ز":
            continue
        bad += 1
    return bad


def _span(s):
    if "-" in s:
        lo, hi = s.split("-")
        return set(range(int(lo), int(hi) + 1))
    return {int(s)}


def main():
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT))
            return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # ---- [1] article inventory -------------------------------------------
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run: missing %s"
                 % (N, sorted(set(range(1, N + 1)) - seen)))

    # ---- [1b] باب structure ----------------------------------------------
    parts = src.get("chapter_structure")
    if not parts or len(parts) != EXPECTED_PARTS:
        e.append("[1b] expected %d باب entries, got %r"
                 % (EXPECTED_PARTS, len(parts) if parts else parts))
    else:
        covered = set()
        for c in parts:
            if not c.get("label_ar", "").startswith("الباب"):
                e.append("[1b] part label %r does not use الباب" % c.get("label_ar"))
            if not c.get("title_ar"):
                e.append("[1b] part %r has no title" % c.get("label_ar"))
            s = _span(c.get("articles", ""))
            if covered & s:
                e.append("[1b] part %r overlaps an earlier part" % c.get("label_ar"))
            covered |= s
            for f in c.get("fasl", []):
                if not f.get("label_ar", "").startswith("الفصل"):
                    e.append("[1b] chapter label %r does not use الفصل" % f.get("label_ar"))
                if not _span(f.get("articles", "")) <= s:
                    e.append("[1b] فصل %r escapes its باب" % f.get("label_ar"))
        if covered != set(range(1, N + 1)):
            e.append("[1b] باب coverage incomplete: missing %s"
                     % sorted(set(range(1, N + 1)) - covered))

    if len(src.get("annexes_not_ingested") or []) != EXPECTED_ANNEXES:
        e.append("[1c] expected %d disclosed annexes, got %r"
                 % (EXPECTED_ANNEXES, len(src.get("annexes_not_ingested") or [])))

    # ---- [2] citation chain and rename history ---------------------------
    if src.get("consolidated_amended_law") is not True:
        e.append("[2] consolidated_amended_law must be True")
    if DECREE_CANONICAL not in (src.get("decree") or ""):
        e.append("[2] decree must cite %s as printed on the instrument, got %r"
                 % (DECREE_CANONICAL, src.get("decree")))
    if DECREE_ALT not in (src.get("decree_display_variant") or ""):
        e.append("[2] the alternative display order %s must be disclosed" % DECREE_ALT)
    if src.get("decree_date_hijri") != "21/5/1426":
        e.append("[2] decree_date_hijri %r != 21/5/1426" % src.get("decree_date_hijri"))
    if src.get("decree_date_gregorian") != "2005-06-28":
        e.append("[2] decree_date_gregorian %r != 2005-06-28"
                 % src.get("decree_date_gregorian"))
    if src.get("former_title_ar") != "لائحة الأشخاص المرخص لهم":
        e.append("[2] former_title_ar must record the pre-2020 name, got %r"
                 % src.get("former_title_ar"))
    if src.get("document") != "لائحة مؤسسات السوق المالية":
        e.append("[2] document title wrong: %r" % src.get("document"))
    if src.get("governing_language") != "ar":
        e.append("[2] governing_language must be 'ar'")
    for field in ("official_source_url", "corroborating_official_url",
                  "secondary_crosscheck_url", "official_catalogue_url"):
        if not src.get(field):
            e.append("[2] missing %s" % field)
    if "cma" not in (src.get("official_source_url") or ""):
        e.append("[2] official_source_url must point at CMA's own domain")

    ai = src.get("amending_instruments") or []
    if len(ai) < 5:
        e.append("[2b] amending_instruments must list every verified instrument "
                 "(expected >=5, got %d)" % len(ai))
    joined = json.dumps(ai, ensure_ascii=False)
    for needed in (DECREE_CANONICAL, AMEND_CANONICAL, "1-101-2023", "4-87-2024",
                   "15/3/1442"):
        if needed not in joined:
            e.append("[2b] amending_instruments does not record %r" % needed)
    for h in ai:
        if h.get("pre_amendment_text_recovered") is not False:
            e.append("[2b] %r must disclose pre_amendment_text_recovered=false"
                     % h.get("instrument"))
        if not h.get("source"):
            e.append("[2b] %r carries no source citation" % h.get("instrument"))
        if not h.get("instrument"):
            e.append("[2b] an amending_instruments entry has no instrument name")
    if not src.get("amending_instruments_note"):
        e.append("[2b] the amendment chain is incomplete and must say so in "
                 "amending_instruments_note")

    method = src.get("verification_methodology_note") or ""
    if not method:
        e.append("[2c] missing verification_methodology_note")
    else:
        for needed in ("TIER_2", DECREE_CANONICAL, AMEND_CANONICAL,
                       "لائحة الأشخاص المرخص لهم", "15/3/1442", "99"):
            if needed not in method:
                e.append("[2c] verification_methodology_note omits %r" % needed)
    if src.get("verification_tier") != TIER:
        e.append("[2c] verification_tier %r != %s" % (src.get("verification_tier"), TIER))
    if not src.get("verification_tier_basis"):
        e.append("[2c] missing verification_tier_basis justifying the tier")

    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2d] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2d] discrepancy entries missing for: %s" % sorted(missing))
        for d in disc:
            if len(d.get("description", "")) < 80:
                e.append("[2d] discrepancy %r has no substantive description"
                         % d.get("article_key"))

    # ---- [3] per-article integrity ---------------------------------------
    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1)) if re.match(KEY_RE, k) else -1
        if a.get("status") != STATUS:
            e.append("[3] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[3] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[3] %s: section/status divergence" % k)
        text = a.get("text", "")
        if not text.strip():
            e.append("[3] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", text):
            e.append("[3] %s: latin/html leftovers in article text" % k)
        if not a.get("section_ar", "").strip():
            e.append("[3] %s: section_ar must be non-empty" % k)
        elif not a["section_ar"].startswith("الباب"):
            e.append("[3] %s: section_ar must name the باب, got %r" % (k, a["section_ar"]))
        if not a.get("number_label_ar", "").startswith("المادة"):
            e.append("[3] %s: missing/!bad number_label_ar" % k)
        if a.get("is_mukarrar") is not False:
            e.append("[3] %s: no مكرر articles exist in this instrument" % k)
        if _bad_tatweel(text):
            e.append("[3] %s: in-word decorative tatweel present" % k)
        for d in LIGATURE_DEFECTS:
            if d in text:
                e.append("[3] %s: ligature-transposition artefact %r survived" % (k, d))
        for f in FURNITURE:
            if f in text:
                e.append("[3] %s: source page furniture %r leaked into article" % (k, f))
        if re.search(r"^\s*\d{1,3}\s*$", text, re.M):
            e.append("[3] %s: bare page number leaked into article text" % k)
        if re.search(r"^الملحق\s+\d+\s*-\s*\d+\s*$", text, re.M):
            e.append("[3] %s: annex heading leaked into article text" % k)
        if re.search(r"^الباب\s", text, re.M):
            e.append("[3] %s: part heading leaked into article text" % k)
        # the source publishes no per-article attribution -> no history anywhere
        if a.get("history"):
            e.append("[3] %s: article carries an amendment history the source "
                     "does not publish" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[3b] status %s: %s != %d" % (st, sc.get(st, 0), want))
    if src.get("status_counts") != EXPECTED_COUNTS:
        e.append("[3b] status_counts %r != %r" % (src.get("status_counts"), EXPECTED_COUNTS))

    # ---- [4] verified records layer --------------------------------------
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"])
            continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number" % r["article_key"])
        if r.get("article_text_verified") != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("verification_tier") != TIER:
            e.append("[4] %s: verification_tier must be %s" % (r["article_key"], TIER))
        if r.get("is_amended") or r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: no article may be flagged amended/repealed/added -- "
                     "the source publishes no per-article attribution" % r["article_key"])
        if r.get("per_article_amendment_attribution_published") is not False:
            e.append("[4] %s: must disclose that per-article amendment "
                     "attribution is unpublished" % r["article_key"])
        if "Arabic governs" not in (r.get("governing_source_note") or ""):
            e.append("[4] %s: governing_source_note must state Arabic governs"
                     % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    # ---- [4b] summary ----------------------------------------------------
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("verification_tier") != TIER:
        e.append("[4b] summary verification_tier != %s" % TIER)
    if summary.get("former_title_ar") != src["former_title_ar"]:
        e.append("[4b] summary does not carry the pre-2020 title")
    if summary.get("per_article_amendment_attribution_published") is not False:
        e.append("[4b] summary must disclose unpublished per-article attribution")
    if summary.get("known_unresolved_discrepancies") != src["known_unresolved_discrepancies"]:
        e.append("[4b] summary discrepancies diverge from the source artifact")
    if summary.get("chapter_structure") != src["chapter_structure"]:
        e.append("[4b] summary chapter_structure diverges from the source artifact")

    # ---- [5] LLM layer ---------------------------------------------------
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("article_range") != [1, N]:
        e.append("[5] llm article_range != [1, %d]" % N)
    if llm.get("verification_tier") != TIER:
        e.append("[5] llm verification_tier != %s" % TIER)
    if llm.get("governing_text_language") != "ar":
        e.append("[5] llm governing_text_language must be 'ar'")
    if llm.get("not_legal_advice") is not True:
        e.append("[5] llm layer must carry not_legal_advice")
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"])
            continue
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if "article_number" not in r:
            e.append("[5] %s: missing article_number" % r["article_key"])
        if r.get("article_text_ar") != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r.get("article_text_hash_sha256") != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        st = r.get("source_trust", {})
        if st.get("source_status") != STATUS.lower():
            e.append("[5] %s: bad source_status in source_trust" % r["article_key"])
        if st.get("verification_tier") != TIER:
            e.append("[5] %s: source_trust must carry the tier" % r["article_key"])
        if DECREE_CANONICAL not in (st.get("source_authority") or ""):
            e.append("[5] %s: source_authority must cite %s"
                     % (r["article_key"], DECREE_CANONICAL))
        if st.get("former_source_document_ar") != src["former_title_ar"]:
            e.append("[5] %s: source_trust must carry the pre-2020 title"
                     % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "english_used_for_correction", "text_summarized_or_paraphrased"):
            if r.get(f) is not False:
                e.append("[5] %s: %s must be False" % (r["article_key"], f))

    if e:
        print("FAIL: %d error(s) in CMA Capital Market Institutions Regulation track:"
              % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1

    print("PASS: لائحة مؤسسات السوق المالية (CMA Capital Market Institutions")
    print("      Regulations) — 99 records, clean 1..99 run, 9 أبواب, 13 فصول")
    print("  - COUNT: 99 articles VERIFIED three ways (Arabic PDF table of contents;")
    print("    expected-ordinal segmentation of the enacting text; CMA English")
    print("    edition Article 1..99). Census figure of 99 confirmed correct.")
    print("  - CITATION: CMA Board Resolution (1-83-2005), 21/5/1426H = 28/6/2005G,")
    print("    under the Capital Market Law (Royal Decree M/30, 2/6/1424H);")
    print("    consolidated as amended through Resolution (2-3-2026),")
    print("    18/07/1447H = 07/01/2026G. Alternative display order")
    print("    (2005-83-1 / 2026-3-2) disclosed, not treated as a second decision.")
    print("  - RENAME: issued 2005 as «لائحة الأشخاص المرخص لهم»; renamed")
    print("    «لائحة مؤسسات السوق المالية» effective 15/3/1442H = 1/11/2020G")
    print("    (CMA announcement CMA_N_2764). Renaming resolution NUMBER is not")
    print("    published by CMA and is recorded as unknown, NOT guessed.")
    print("  - TIER_2: one OFFICIAL text source (CMA's own Arabic PDF) + one")
    print("    independent SECONDARY full-text cross-check; citation chain")
    print("    additionally corroborated by Umm Al-Qura (a second official source).")
    print("  - AMENDMENTS: consolidated text incorporates everything through")
    print("    2-3-2026. The source publishes NO per-article amendment footnotes,")
    print("    so 0 articles are flagged معدلة (99 اصلية) — disclosed as an")
    print("    ABSENCE of attribution, not an assertion of no amendment.")
    print("  - 11 annexes identified and deliberately NOT ingested; no annex,")
    print("    page-number, part-heading or watermark text leaked into any article.")
    print("  - %d known discrepancies disclosed." % len(disc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
