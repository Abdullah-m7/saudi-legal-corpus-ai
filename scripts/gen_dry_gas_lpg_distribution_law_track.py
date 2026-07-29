#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Dry Gas / LPG Distribution Law track (نظام توزيع
الغاز الجاف وغاز البترول السائل للأغراض السكنية والتجارية). Originally issued
by Royal Decree M/126, 1/12/1438H (published Umm Al-Qura 21/3/1440H); amended
substantively by Royal Decree M/112, 9/11/1443H (published Umm Al-Qura issue
4940, 22 Jul 2022), which transferred regulatory authority from "the
Authority" (ECRA)/"the Governor" to "the Ministry" (Ministry of Energy)/"the
Minister", broadened definitions, introduced competitive-bidding licensing,
and toughened penalties/inspection. Administered by the Ministry of Energy.
This track builds the CURRENT (post-M/112) consolidated text only.

BRAND-NEW BASE-LAW TRACK -- not previously in this corpus.

WHICH INSTRUMENT, AND HOW CONFIRMED -- laws.boe.gov.sa (this corpus's usual
primary source), www.moenergy.gov.sa / cdn.moenergy.gov.sa (the administering
Ministry's own site), ecra.gov.sa (the former regulator) and web.archive.org
were ALL unreachable this pass (connection resets, HTTP 503/502/ENOTFOUND, and
an explicit egress-policy block on web.archive.org). An alternate official
document was found instead: a consolidated Arabic PDF (11 pages) bearing the
Ministry of Energy's own letterhead on every page, plus its official parallel
English translation (14 pages, footer: "This translation is provided for
guidance. The governing text is the Arabic text."), both hosted on the
Ministry of Investment's (MISA) public legal-documents portal
(misa.gov.sa/activities/laws) and fetched directly via HTTP 200. Both PDFs are
"redline-by-footnote" documents: each amended/added/deleted article, paragraph
or sub-paragraph carries a numbered footnote reading "amended/added/deleted by
Royal Decree No. (M/112) dated 9/11/1443H".

PDF-EXTRACTION ARTIFACT AND ITS FIX -- pdftotext (-layout and -raw) revealed a
systematic ligature-reversal bug specific to this PDF's body-text font: every
"lam-alef" (لا) sequence is extracted reversed as "alef-lam" (ال), corrupting
~60 distinct words (e.g. "اللائحة" -> "الالئحة", "المادة" -> "املادة",
"الاستثمار" -> "االستثمار"). The footnote font was unaffected. Fixed by
rendering all 11 pages to PNG (200dpi) and transcribing each article directly
from the page images (a vision/rendered-page-image pass of the SAME official
document) -- not from the raw pdftotext output.

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE. A single official document
(the Ministry of Energy's own consolidated PDF) was verified via an
independent rendered-page-image pass of that SAME document after the ligature
bug was found -- this is explicitly one of this corpus's two TIER_1 patterns.
Reinforced by: (a) exact structural agreement with the official parallel
English translation (identical amended/added/deleted footnotes, article by
article, with zero exceptions); (b) verbatim agreement with Royal Decree
M/112's own operative amendment text as reproduced on qanoonsa.com (a private
aggregator -- not a second official leg under this corpus's strict Tier-1
definition, but a full verbatim cross-check of every amendment operation);
(c) partial agreement (Articles 1-10) with a second legal-tech platform,
qanoniah.com, reached via a JS-rendering reader before that reader started
refusing further requests (apparently a preview-only gate on that platform,
not a technical failure).

21 articles, no chapter/باب/فصل subdivision (flat structure); 17 معدلة
(amended by M/112, matching the task's "reportedly touched ~17 articles"),
3 اصلية (Articles 5, 6, 21 -- unchanged), 1 ملغاة (Article 9 -- repealed
outright, its pre-1443H content unrecoverable from any source reached this
session; the official document itself shows only "(ملغاة)" in its place).

previous_text_ar (pre-M/112 wording) is included ONLY for the 5 articles
(2, 10, 11, 14, 15) where the entire prior article could be reconstructed
with full confidence by mechanically reversing a single, precisely-worded
operation stated verbatim in the M/112 decree text itself (a word
substitution, or a specific phrase addition/deletion). For the remaining 12
amended articles, no previous_text_ar is asserted -- either the decree
replaced the whole article/paragraph outright (prior wording never quoted
anywhere reached), multiple candidate substitution points made the exact
prior wording unrecoverable with confidence (Articles 17, 18), or whole
paragraphs were deleted with content unrecoverable (Article 12). See
known_unresolved_discrepancies in the source artifact for full detail on
every one of these, plus a documented decree-number typo (footnote 29 in the
official PDF cites "M/126" where "M/112" is clearly meant) and the two
Implementing-Regulation/Bylaws follow-up candidates not built this pass.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "dry_gas_lpg_distribution_law", "law", "official_source",
                   "dry_gas_lpg_distribution_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "dry_gas_lpg_distribution_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "dry_gas_lpg_distribution_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "dry_gas_lpg_distribution_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "dry_gas_lpg_distribution_law_arabic_legal_llm",
                        "dry_gas_lpg_distribution_law_legal_llm_001_021.json")

LAW_ID = "sa-dry-gas-lpg-distribution-law-m126-1438-amended-m112-1443"
LAW_AR = "نظام توزيع الغاز الجاف وغاز البترول السائل للأغراض السكنية والتجارية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_REPEALED = "REPEALED"
KEY_RE = r"dry_gas_lpg_distribution_law_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللوائح اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير").split())


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
        top_status = a["status"]
        text_complete = a.get("text_complete", True)
        governing_note = ("Arabic governs; this is the CURRENT (post-M/112) Dry Gas/LPG "
                           "Distribution Law -- originally Royal Decree M/126 (1/12/1438H), "
                           "substantively amended by Royal Decree M/112 (9/11/1443H). "
                           "Brand-new base-law track, not previously in this corpus. "
                           "laws.boe.gov.sa, moenergy.gov.sa and ecra.gov.sa were all checked "
                           "first but unreachable this pass. Governing text is the Ministry of "
                           "Energy's own consolidated PDF (hosted via misa.gov.sa), verified via "
                           "an independent rendered-page-image pass after a systematic "
                           "pdftotext ligature-extraction bug was found. "
                           "TIER_1_PRIMARY_MULTI_SOURCE. See verification_methodology_note and "
                           "known_unresolved_discrepancies in the source artifact before relying "
                           "on this track, especially regarding previous_text_ar availability "
                           "(only 5 of 17 amended articles) and the repealed Article 9 (content "
                           "unrecoverable).")
        ver.append({"law_key": "dry_gas_lpg_distribution_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "DRY_GAS_LPG_DISTRIBUTION_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": governing_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "dry-gas-lpg-distribution-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "dry_gas_lpg_distribution_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام توزيع الغاز الجاف وغاز البترول السائل"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/126, 1/12/1438H, as "
                                                          "substantively amended by Royal Decree "
                                                          "M/112, 9/11/1443H (Council of "
                                                          "Ministers Resolution 610, 8/11/1443H; "
                                                          "Shura Council Resolution 27/152, "
                                                          "27/7/1443H) -- the currently in-force "
                                                          "Dry Gas/LPG Distribution Law. Verbatim "
                                                          "text from the Ministry of Energy's own "
                                                          "consolidated PDF (hosted via "
                                                          "misa.gov.sa), verified via an "
                                                          "independent rendered-page-image pass; "
                                                          "cross-verified against Royal Decree "
                                                          "M/112's operative text (qanoonsa.com) "
                                                          "and the official parallel English "
                                                          "translation. laws.boe.gov.sa, "
                                                          "moenergy.gov.sa, ecra.gov.sa and "
                                                          "web.archive.org were all unreachable "
                                                          "this pass. TIER_1_PRIMARY_MULTI_SOURCE."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/126) وتاريخ 1/12/1438هـ، بصيغته المعدلة جوهريا بموجب المرسوم الملكي رقم (م/112) وتاريخ 9/11/1443هـ (قرار مجلس الوزراء رقم (610) وتاريخ 8/11/1443هـ؛ قرار مجلس الشورى رقم (27/152) وتاريخ 27/7/1443هـ) — النظام النافذ حاليا. النص الحرفي من مستند وزارة الطاقة الرسمي المدمج (مستضاف عبر misa.gov.sa)، مؤكَّد عبر قراءة بصرية مباشرة مستقلة لصور صفحاته، ومقارَن بنص المرسوم الملكي (م/112) التشغيلي (qanoonsa.com) والنسخة الإنجليزية الرسمية الموازية. تعذّر الوصول إلى laws.boe.gov.sa وmoenergy.gov.sa وecra.gov.sa وweb.archive.org جميعها هذه الجولة. المستوى TIER_1.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "dry_gas_lpg_distribution_law",
               "layer": "DRY_GAS_LPG_DISTRIBUTION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "amendment_decree": src.get("amendment_decree"),
               "amendment_decree_date_hijri": src.get("amendment_decree_date_hijri"),
               "amendment_council_of_ministers_decision": src.get("amendment_council_of_ministers_decision"),
               "amendment_shura_council_decision": src.get("amendment_shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "amendment_gazette_publication_hijri": src.get("amendment_gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-dry-gas-lpg-distribution-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (21 مادة؛ 3 أصلية، 17 معدلة، 0 مضافة، 1 ملغاة؛ بلا تقسيم إلى فصول)",
               "title_en": ("The Saudi Arabian Dry Gas and Liquefied Petroleum Gas Distribution "
                            "Law for Residential and Commercial Purposes (Royal Decree M/126, "
                            "1/12/1438H, as amended by Royal Decree M/112, 9/11/1443H) — Arabic "
                            "LLM-ready layer (21 records: 3 original, 17 amended, 0 added, "
                            "1 repealed; no chapter subdivision)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 21], "text_status": STATUS_AMENDED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Dry Gas/LPG Distribution Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
