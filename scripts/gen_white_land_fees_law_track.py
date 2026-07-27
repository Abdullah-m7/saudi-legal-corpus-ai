#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian White Land and Vacant Properties Fees Law track
(نظام رسوم الأراضي البيضاء والعقارات الشاغرة). Originally issued as "نظام رسوم
الأراضي البيضاء" by Royal Decree M/4, 12/2/1437H; substantively amended and
renamed by Royal Decree M/244, 7/11/1446H, which expanded scope to vacant
built properties and raised the fee cap to 10%. Administered by the Ministry
of Municipalities and Housing (MOMAH). This track builds the CURRENT
(post-M/244) consolidated text only.

BRAND-NEW BASE-LAW TRACK -- not previously in this corpus. Distinct from the
existing rett_law (Real Estate Transaction Tax) track, which is untouched.

WHICH INSTRUMENT, AND HOW CONFIRMED -- confirmed via momah.gov.sa (the
administering Ministry's own site: a Ministry-issued redline/comparison PDF
showing each article's pre-M/244 text followed, where amended, by its
post-M/244 text) cross-checked against qadha.org.sa (an independent
professionally-compiled/annotated legal reference book, Nov 2025) and
alhamoudilawyers.com (a law-firm secondary source). laws.boe.gov.sa (this
corpus's usual primary source, lawId 6932e745-0f61-4f25-9e4a-a9a700f21d6b) was
checked FIRST but was unreachable this pass (connection reset; web.archive.org
returned HTTP 403).

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. For 14 of 15
articles the governing text is momah.gov.sa's own official redline PDF,
cross-verified verbatim against qadha.org.sa. Article 3 is the one exception:
momah's own redline PDF omits the M/244 amendment marker for Article 3
(apparently a stale slide), contradicted by (a) qadha.org.sa's fuller text,
(b) alhamoudilawyers.com, (c) this SAME momah PDF's own amended Article 4,
which cross-references "الفقرة (3) من المادة (الثالثة)" -- a paragraph that
only exists in the amended Article 3 -- and (d) this task's own stated fact
that M/244 "raised the fee cap to 10%". Article 3's text is therefore taken
from qadha.org.sa, cross-verified by the other three signals. See
known_unresolved_discrepancies in the source artifact for full detail.

15 articles, no chapter/باب/فصل subdivision (flat structure); 13 معدلة
(amended by M/244), 2 اصلية (unchanged: Articles 10 and 15). Diacritics
stripped uniformly; the two source PDFs' distinct "الأراض ي"/"الأرايض"
extraction glitches for the word "الأراضي" are normalized to the standard
spelling (a display-layer normalization only, disclosed in
known_unresolved_discrepancies).

Two Implementing Regulations exist under this Law (white land fees; vacant
property fees) -- NOT built this pass (see known_unresolved_discrepancies);
flagged as follow-up candidates.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "white_land_fees_law", "law", "official_source",
                   "white_land_fees_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "white_land_fees_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "white_land_fees_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "white_land_fees_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "white_land_fees_law_arabic_legal_llm",
                        "white_land_fees_law_legal_llm_001_015.json")

LAW_ID = "sa-white-land-fees-law-m4-1437-amended-m244-1446"
LAW_AR = "نظام رسوم الأراضي البيضاء والعقارات الشاغرة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
KEY_RE = r"white_land_fees_law_art_(\d{3})(?:_mukarrar(\d*))?$"
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
        article3_caveat = (
            " CAVEAT: this article's text is sourced from qadha.org.sa (secondary), NOT "
            "momah.gov.sa, because momah.gov.sa's own redline PDF omits the M/244 amendment "
            "marker for this article -- see known_unresolved_discrepancies "
            "(white_land_fees_law_article3_momah_pdf_gap) before relying on this specific "
            "article." if n == 3 else "")
        ver.append({"law_key": "white_land_fees_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "WHITE_LAND_FEES_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this is the CURRENT (post-M/244) "
                                              "White Land and Vacant Properties Fees Law -- "
                                              "originally Royal Decree M/4 (12/2/1437H), "
                                              "substantively amended/renamed by Royal Decree "
                                              "M/244 (7/11/1446H). Brand-new base-law track, not "
                                              "previously in this corpus. laws.boe.gov.sa was "
                                              "checked FIRST but unreachable this pass "
                                              "(connection reset; web.archive.org returned HTTP "
                                              "403). Governing text for 14/15 articles is "
                                              "momah.gov.sa (the administering Ministry's own "
                                              "redline PDF), cross-verified against qadha.org.sa. "
                                              "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED." +
                                              article3_caveat +
                                              " See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "white-land-fees-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "white_land_fees_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام رسوم الأراضي البيضاء والعقارات الشاغرة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/4, 12/2/1437H, as "
                                                          "substantively amended/renamed by "
                                                          "Royal Decree M/244, 7/11/1446H "
                                                          "(Council of Ministers Resolution 758, "
                                                          "1/11/1446H; Shura Council Resolution "
                                                          "24/255, 26/10/1446H) -- the currently "
                                                          "in-force White Land and Vacant "
                                                          "Properties Fees Law. Verbatim text "
                                                          "(14/15 articles) from momah.gov.sa "
                                                          "(administering Ministry's own redline "
                                                          "PDF), cross-verified against "
                                                          "qadha.org.sa; laws.boe.gov.sa and "
                                                          "web.archive.org both unreachable this "
                                                          "pass. Article 3 sourced from "
                                                          "qadha.org.sa due to a gap in momah's "
                                                          "own PDF -- see "
                                                          "known_unresolved_discrepancies. "
                                                          "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/4) وتاريخ 12/2/1437هـ، بصيغته المعدلة جوهريا والمُعاد تسميتها بموجب المرسوم الملكي رقم (م/244) وتاريخ 7/11/1446هـ (قرار مجلس الوزراء رقم (758) وتاريخ 1/11/1446هـ؛ قرار مجلس الشورى رقم (24/255) وتاريخ 26/10/1446هـ) — نظام رسوم الأراضي البيضاء والعقارات الشاغرة النافذ حاليا. النص الحرفي (14 من 15 مادة) من momah.gov.sa (الموقع الرسمي للوزارة المشرفة)، متقاطع مع qadha.org.sa؛ laws.boe.gov.sa وweb.archive.org كلاهما غير قابلين للوصول هذه الجولة. المادة الثالثة مصدرها qadha.org.sa بسبب سهو في مستند momah.gov.sa ذاته -- انظر known_unresolved_discrepancies. المستوى TIER_2.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "white_land_fees_law",
               "layer": "WHITE_LAND_FEES_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-white-land-fees-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة؛ 2 أصلية، 13 معدلة، 0 مضافة، 0 ملغاة؛ بلا تقسيم إلى فصول)",
               "title_en": ("The Saudi Arabian White Land and Vacant Properties Fees Law "
                            "(Royal Decree M/4, 12/2/1437H, as amended by Royal Decree M/244, "
                            "7/11/1446H) — Arabic LLM-ready layer (15 records: 2 original, 13 "
                            "amended, 0 added, 0 repealed; no chapter subdivision)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": STATUS_AMENDED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready White Land Fees Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
