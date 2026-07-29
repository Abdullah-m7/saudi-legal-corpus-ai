#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian Traffic Law track
(اللائحة التنفيذية لنظام المرور, Ministerial Resolution -- Minister of Interior --
No. 2249, dated 10/3/1441H, issued under the Traffic Law, Royal Decree M/85,
26/10/1428H). This is the companion-regulation follow-up candidate explicitly
flagged by this corpus's own traffic_law track (see sources/traffic/law/
official_source/traffic_law_official_source.json, known_unresolved_discrepancies
key traffic_implementing_regulation_not_extracted). This track ingests it.

SUPERSESSION: Resolution 2249/1441H explicitly REPLACES the prior Implementing
Regulation issued by Ministerial Resolution No. 7019, 3/7/1429H -- verbatim in
clause (ثانياً) of the resolution text on page 1 of the primary source.

VERIFICATION TIER -- see traffic_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. BOE has
NO dedicated lawId page for this Implementing Regulation at all (only for the base
Traffic Law) -- consistent with BOE not cataloguing Ministerial-level (Minister-
of-Interior) executive regulations as standalone lawId records. All .gov.sa hosts
(moi/idc/ncar) were connection-reset this pass; an archive.org copy
(ia902504.us.archive.org) was also connection-reset -- the block was recorded and
NOT circumvented (no proxies, no alternate hostnames).

PRIMARY SOURCE: an official SCANNED PDF of the Ministry of Interior's issued
document (93 pages; page 1 is Resolution 2249 itself, stamped and signed by the
Minister of Interior). Obtained from a Google Drive copy shared by a legal-
curation account on X (@Law3li) explicitly labelled as Resolution 2249,
10/3/1441H, and confirmed to be that resolution (not the older 1429 one) via the
page-1 resolution text and qanoniah.com metadata (issuance tool no. 2249, date
1441-03-10, status ساري, Umm Al-Qura Gazette issue 4812, 2020-01-03).

EXTRACTION (two independent pipelines + direct cross-check): the file is a scan
with NO text layer, so text was extracted via (1) direct vision reading of
170-dpi page renders (the PRIMARY text source; more reliable than OCR for
Arabic) and (2) an independent tesseract-ara OCR pass used as a cross-check layer
(where vision and OCR agree, confidence is raised; where they diverge -- notably
the deep "N/M/K..." clause numbering that OCR cannot read reliably -- the direct
vision reading governs). Extraction fidelity was cross-validated against the
born-digital text of the first 8 articles freely served by qanoniah.com's API
(api.qanoniah.com): 100% character match for Articles 1, 3, 4, 5, 6, 8 and 99.0%
for Article 2 (all differences cosmetic -- spacing / tanwin-alif rendering /
colon spacing -- plus a few OCR typos in qanoniah's OWN text). Article 7 matched
only 51.5% -- as EXPECTED, since Article 7 is an amended article (clause 7/1/3/2),
so qanoniah's current text (4845 chars) legitimately diverges from this original-
1441 scan (4126 chars), independently confirming both the amendment and that the
scan is the original issuance.

STRUCTURE: 8 chapters, 85 numbered articles (First..Eighty-fifth) plus one
"المادة الخمسون مكرر" (commercial-centre traffic licensing) = 86 records. The
regulation parallels the base law article-by-article in numbering and chapter
titles but with detailed implementing content (deep "N/M/K..." sub-clauses). This
track extracts ONLY the regulation's own implementing provisions per article
(the "N/M" sub-clauses), NOT the base-law article text shown (in bold) above them
-- that base-law text lives in the separate traffic_law track and is not
re-ingested here, matching how qanoniah represents this regulation. For articles
with no implementing sub-clauses in the regulation (1, 2, 23, 27, 53, 69, 70, and
the closing 80-85) the article text is the provision as presented in the document
(a restatement), matching what qanoniah does for Articles 1 and 2.

INGESTED VERSION: the founding text of Resolution 2249 (10/3/1441H) UPDATED with
all five confirmed subsequent amending decisions of the Minister of Interior,
each independently re-verified against uqn.gov.sa (the official Umm al-Qura
gazette) in the maintenance pass of 15/2/1448H, with qanoonsa.com as a second
source where it indexes the item:

  3148  26/2/1443H  -- adds 47/2   (UQ 4904, 15-10-2021)
  18243 5/12/1443H  -- REPLACES Article 23 in full (UQ 30/12/1443, 29-07-2022)
  5622  1/4/1444H   -- amends 7/1/3/2 (UQ 4956, 11-11-2022)
  1924  1/5/1447H   -- DELETES 21/1/4 (UQ 5119, 31-10-2025)
  5330  16/12/1447H -- adds 16/1/5, 17/2/13, 50/12, 51/7, 54/9, 59/5, 68/4
                       (المركبات ذاتية القيادة; UQ 5163, 12-06-2026)

None of them adds an article, so the record count stays 86.

DELETIONS ARE FLAGGED, NEVER REMOVED. Clause 21/1/4 (the SAR 200,000 bank
guarantee for vehicle showrooms), deleted by Decision 1924, is preserved verbatim
in Article 21's text with an explicit deletion note beneath it, and Article 21 is
reclassified اصلية -> معدلة. Article 80 remains ملغاة on the strength of an
explicit footnote in the primary scan itself (Council of Ministers Resolution
636, 23/10/1438H); its (repealed) text is likewise preserved verbatim.

DISCLOSED GAP -- Article 47/2. Decision 3148's paragraph 47/2 consists of a
chapeau, a 32-row violation/penalty table, and a licence-suspension provision
47/2/1. ONLY THE CHAPEAU IS INGESTED, verbatim. The gazette's own text page stops
at the chapeau ("تتمة اللائحة مرفقة نسخة PDF") and the annexed gazette PDF's text
layer is corrupted by a ToUnicode/font-encoding defect that extracts Arabic as
Latin mojibake. The table was NOT transcribed from the corrupted layer and NOT
reconstructed; the gap is flagged inline in Article 47's text and in
known_unresolved_discrepancies (key
traffic_regulation_art47_2_penalty_table_gazette_pdf_gap).

86 records: 74 اصلية, 11 معدلة (7, 16, 17, 21, 23, 47, 50, 51, 54, 59, 68),
1 ملغاة (80), 0 مضافة. The المادة الخمسون مكرر is classified اصلية
(is_mukarrar=True), since it is part of the original 1441 issuance, not a later
addition to the regulation.

Diacritics (tashkeel) are stripped uniformly for consistency with this corpus's
other tracks (the "هـ" Hijri-date marker is retained -- it is not decorative
tatweel). Arabic governs; no translation / paraphrase / interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "traffic", "regulation", "official_source",
                   "traffic_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "traffic", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "traffic_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "traffic_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "traffic_regulation_arabic_legal_llm",
                        "traffic_regulation_legal_llm_001_086.json")

LAW_ID = "sa-traffic-regulation-2249-1441"
LAW_AR = "اللائحة التنفيذية لنظام المرور"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
STATUS_REPEALED = "REPEALED"
KEY_RE = r"traffic_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"traffic_regulation_art_007", "traffic_regulation_art_016",
                "traffic_regulation_art_017", "traffic_regulation_art_021",
                "traffic_regulation_art_023", "traffic_regulation_art_047",
                "traffic_regulation_art_050", "traffic_regulation_art_051",
                "traffic_regulation_art_054", "traffic_regulation_art_059",
                "traffic_regulation_art_068"}
REPEALED_KEYS = {"traffic_regulation_art_080"}
ADDED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها التالية "
            "إليه عليها منهم بينهم المركبة المرور الإدارة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in REPEALED_KEYS:
        return STATUS_REPEALED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "traffic", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "TRAFFIC_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": a.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the official "
                                              "scanned Ministry of Interior document of Ministerial "
                                              "Resolution No. 2249 (10/3/1441H) -- page 1 is the "
                                              "stamped/signed resolution itself -- extracted via "
                                              "direct vision reading cross-checked against an "
                                              "independent tesseract-ara OCR pass. laws.boe.gov.sa "
                                              "was checked first per standard methodology but has "
                                              "no dedicated lawId page for this Implementing "
                                              "Regulation at all. Articles 1-8 were independently "
                                              "cross-validated character-for-character against "
                                              "qanoniah.com's born-digital text (100% for six "
                                              "articles, 99.0% for Article 2; Article 7's 51.5% "
                                              "divergence confirms its amendment). This resolution "
                                              "SUPERSEDES the prior 7019/1429H regulation. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- in "
                                              "particular the scanned-source vision+OCR extraction "
                                              "tier for Articles 9-85, the five gazette-confirmed "
                                              "amending decisions applied on top of it (3148, "
                                              "18243, 5622, 1924, 5330), the DISCLOSED GAP in "
                                              "Article 47/2 (its 32-row penalty table is NOT "
                                              "ingested -- the annexed gazette PDF's text layer is "
                                              "corrupted and was neither transcribed nor "
                                              "reconstructed), the flagged-not-removed deletion of "
                                              "clause 21/1/4, and the source-attested repeal of "
                                              "Article 80."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "traffic-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "traffic/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المرور" % a["number_label_ar"]],
                    "text_status": a["status"], "verification_tier": a.get("verification_tier"),
                    "source_trust": {"source_authority": ("Ministerial Resolution (Minister of "
                                                          "Interior) No. (2249) (10/3/1441H), "
                                                          "issued under the Traffic Law (Royal "
                                                          "Decree M/85) -- official scanned MOI "
                                                          "document (page 1 = the stamped/signed "
                                                          "resolution), vision+OCR extraction, "
                                                          "Articles 1-8 cross-validated against "
                                                          "qanoniah.com born-digital text; "
                                                          "SUPERSEDES Resolution 7019/1429H; "
                                                          "laws.boe.gov.sa has no dedicated lawId "
                                                          "page for this Implementing Regulation"),
                                     "source_authority_ar": "القرار الوزاري (قرار وزير الداخلية) رقم (2249) وتاريخ 10/3/1441هـ، الصادر استنادا إلى نظام المرور (المرسوم الملكي م/85) — المصدر الرسمي المُصوَّر لوثيقة وزارة الداخلية (صفحته الأولى القرار المختوم الموقَّع)، مُستخرَج بالقراءة البصرية المباشرة مع تحقق تقاطعي بـ tesseract-ara، والمواد (1-8) مُطابَقة مع نص qanoniah.com الرقمي الأصلي؛ يحل محل القرار الوزاري 7019/1429هـ؛ بوابة هيئة الخبراء لا تملك صفحة مخصصة لهذه اللائحة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "traffic",
               "layer": "TRAFFIC_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "supersedes": "القرار الوزاري رقم (7019) وتاريخ 3/7/1429هـ",
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-traffic-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (86 سجلا؛ 74 أصلية، 11 معدلة، 1 ملغاة، 0 مضافة)",
               "title_en": ("Implementing Regulation of the Saudi Arabian Traffic Law — Arabic "
                            "LLM-ready layer (86 records: 74 original, 11 amended, 1 repealed, "
                            "0 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 85], "includes_mukarrar": True,
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "supersedes": "القرار الوزاري رقم (7019) وتاريخ 3/7/1429هـ",
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Traffic Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
