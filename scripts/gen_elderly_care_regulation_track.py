#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation track of the Saudi Arabian Elderly
Rights and Care Law (اللائحة التنفيذية لنظام حقوق كبير السن ورعايته), issued
pursuant to Article 22 of the parent Law (نظام حقوق كبير السن ورعايته, Royal
Decree M/47, 3/6/1443H -- tracked separately in this corpus as elderly_care_law,
shared internal law_key: elderly_care).

VERIFICATION TIER -- see sources/elderly_care_regulation/law/official_source/
elderly_care_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

IMPORTANT CORRECTION regarding the issuing instrument: Council of Ministers
Resolution No. 292 (1/6/1443H) is NOT this Regulation's issuing instrument --
it is the resolution that approved the parent LAW itself (independently
confirmed via a Wayback-archived snapshot of the official laws.boe.gov.sa
portal page and nezams.com, both carrying identical verbatim preamble text --
see the elderly_care_law track). Resolution 292's own clause (ثانياً) only
DIRECTS that this Regulation be prepared jointly with the Ministry of Finance
for financially-relevant provisions; the parent Law's own Article 22 states
the MINISTER (not the Council of Ministers) shall issue the Regulation within
ninety days of the Law's publication. The exact ministerial decision number
and date could NOT be confirmed this pass (see below) -- decree and
decree_date_hijri in the source artifact explicitly record this as unconfirmed
rather than guessing a plausible-looking number.

TIER_4 (single clean source, confirmed partial coverage -- matching this
corpus's health_system_regulation precedent exactly). laws.boe.gov.sa has NO
dedicated lawId page for this Regulation (only the parent Law's page exists).
An official PDF hosted directly on hrsd.gov.sa (fetched directly, HTTP 200,
14 pages) confirms the Regulation's existence, general structure, and the
Minister's signature, but its embedded Arabic font has a severe encoding
defect (confirmed independently via two different extraction tools --
pdftotext -layout and PyMuPDF/fitz -- producing the same corrupted character
substitutions), making it unusable for verbatim text beyond rough structural
identification. The ONLY source through which real verbatim article text
could be retrieved was qanoniah.com's public API (api.qanoniah.com/v1/files/
BJmxzW4K1LGAqvYnvwQd5pNgk, unauthenticated), which enforces a CONFIRMED
10-index-item free-preview cap (matching the same cap documented in this
corpus's health_system_regulation track for the same platform) -- 2 of the 10
index entries are null-content section headers ("التعريفات" / "الأحكام
العامة"), yielding exactly 8 real verbatim articles (this Regulation's OWN
independent numbering, Articles 1-8, cross-referencing parent-Law Articles
1, 2, (3 and 6), 4, 5, 6, 7, and (8 and 6) respectively -- recorded explicitly
per-article in implements_law_articles, not inferred from number equality).

8 records, all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة. The TOTAL article count of
this Regulation could NOT be confirmed this pass -- unreliable (but
suggestive) fragments from the corrupted hrsd.gov.sa PDF indicate the
Regulation continues at least through provisions referencing parent-Law
Articles up to approximately Article 20, plus closing publication/
effective-date articles -- i.e. the true total is very likely greater than 8,
but this is EXCLUDED from this track, not fabricated or guessed.

TASHKEEL/HTML-entity normalization performed at the official_source-build
stage only (table/list/paragraph tag stripping, HTML entity decoding, nbsp
and double-space collapsing) -- no legal text altered. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "elderly_care_regulation", "law", "official_source",
                   "elderly_care_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "elderly_care_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "elderly_care_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "elderly_care_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "elderly_care_regulation_arabic_legal_llm",
                        "elderly_care_regulation_legal_llm_001_008.json")

LAW_KEY = "elderly_care"
LAW_ID = "sa-elderly-care-regulation-1444"
LAW_AR = "اللائحة التنفيذية لنظام حقوق كبير السن ورعايته"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"elderly_care_regulation_art_(\d{3})$"


def _kw(text, k=6):
    stop = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
                "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
                "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
                "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
                "إليه عليها منهم بينهم الوزارة الوزير مراعاة نصت عليه").split())
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in stop:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    return int(m.group(1))


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa has NO dedicated lawId page for this "
            "Regulation (only the parent Law's page exists). An official PDF on hrsd.gov.sa "
            "confirms this Regulation's existence and general structure but has a severe "
            "font-encoding defect (confirmed via two independent extraction tools) making it "
            "unusable for verbatim text. The ONLY source providing real verbatim article text "
            "was qanoniah.com's public API, which enforces a confirmed 10-index-item free-"
            "preview cap -- 8 real articles recovered (this Regulation's own numbering, "
            "Articles 1-8) before the cap. TOTAL article count NOT confirmed this pass "
            "(excluded, not fabricated) -> TIER_4. IMPORTANT: Council of Ministers Resolution "
            "292 is NOT this Regulation's issuing instrument (it approved the parent Law); the "
            "exact ministerial decision number/date could not be confirmed this pass. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text, provenance, or completeness.")

SRC_AUTH = ("Ministerial Decision (Minister of Human Resources and Social Development) issued "
            "pursuant to Article 22 of the parent Law (Royal Decree M/47, 3/6/1443H) -- exact "
            "decision number/date NOT confirmed this pass. Verbatim text retrieved only via "
            "qanoniah.com's public API (api.qanoniah.com), an independent legal aggregator, "
            "subject to a confirmed 10-item free-preview cap yielding 8 real articles; the "
            "official hrsd.gov.sa PDF confirms existence/structure/signature only (severe font "
            "corruption prevents verbatim use) -> TIER_4.")

SRC_AUTH_AR = ("قرار وزاري (وزير الموارد البشرية والتنمية الاجتماعية) صادر تنفيذاً للمادة "
               "الثانية والعشرين من النظام الأصلي (المرسوم الملكي م/47، 3/6/1443هـ) -- رقم "
               "القرار وتاريخه الدقيقان غير مؤكدين هذه الجولة. النص الحرفي مسترجَع فقط عبر "
               "واجهة برمجة التطبيقات العامة لموقع qanoniah.com (مُجمِّع قانوني مستقل)، الخاضعة "
               "لحد معاينة مجاني مؤكَّد بعشرة عناصر ينتج عنه 8 مواد فعلية؛ ملف hrsd.gov.sa الرسمي "
               "يؤكد الوجود والبنية والتوقيع فقط (عطل جسيم في ترميز الخط يمنع الاستخدام الحرفي) "
               "-- TIER_4.")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = a["article_number"]
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        implements = a.get("implements_law_articles", [])
        ver.append({"law_key": LAW_KEY, "law_component": "regulation", "language": "ar",
                    "record_layer": "ELDERLY_CARE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "implements_law_articles": implements,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": True,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "implements_law_articles": implements,
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": True,
                    "record_id": "elderly-care-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "elderly_care_regulation/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام حقوق كبير السن ورعايته"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": STATUS_UNCHANGED.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": LAW_KEY,
               "layer": "ELDERLY_CARE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "parent_law_article_range": src.get("parent_law_article_range"),
               "confirmed_covered_law_articles": src.get("confirmed_covered_law_articles"),
               "excluded_law_articles_not_recovered": src.get("excluded_law_articles_not_recovered"),
               "total_article_count_confirmed": src.get("total_article_count_confirmed"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-elderly-care-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": (LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (8 مواد "
                            "تنفيذية مؤكَّدة من عدد إجمالي غير مؤكَّد؛ تغطية جزئية موثَّقة "
                            "صراحة -- انظر known_unresolved_discrepancies)"),
               "title_en": ("Implementing Regulation of the Saudi Arabian Elderly Rights and "
                            "Care Law — Arabic LLM-ready layer (8 confirmed article records out "
                            "of an unconfirmed total; PARTIAL, explicitly documented coverage "
                            "-- see known_unresolved_discrepancies)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 8], "text_status": STATUS_UNCHANGED,
               "total_article_count_confirmed": src.get("total_article_count_confirmed"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Elderly Care Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
