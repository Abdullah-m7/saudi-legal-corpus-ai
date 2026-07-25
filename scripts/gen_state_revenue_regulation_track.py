#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the State Revenue Law track
(اللائحة التنفيذية لنظام إيرادات الدولة, Ministerial Resolution No. 860,
13/3/1432H, issued by the Minister of Finance under Article 29 of the State
Revenue Law -- Royal Decree M/68, 18/11/1431H -- and later amended by
Ministerial Resolution No. 901, 24/2/1439H).

The base law (نظام إيرادات الدولة) is already tracked separately in this
corpus at sources/state_revenue/law/. This is the companion Implementing
Regulation, tracked as its own law_key "state_revenue_regulation".

VERIFICATION TIER -- see state_revenue_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the Ministry of Finance's OWN official document-library PDF
(mof.gov.sa/docslibrary/RegulationsInstructions/Documents/الانظمة/اللائحة
التنفيذية لنظام ايرادات الدولة.pdf), fetched directly (HTTP 200). Its own
cover page and printed Ministerial Resolution state the founding instrument
(860, 13/3/1432H) and the amending instrument (901, 24/2/1439H) together --
this is the CURRENT, CONSOLIDATED, 65-article text. laws.boe.gov.sa was
checked first per this corpus's standard methodology but has no reference to
this Implementing Regulation anywhere on the base law's own LawDetails page
(consistent with BOE's documented practice of not cataloguing Ministerial-
Resolution-level regulations as their own lawId records). ncar.gov.sa, a
named candidate primary source, was UNREACHABLE this pass at the TCP/TLS
layer on every attempt (see known_unresolved_discrepancies); adf.gov.sa and
the Umm Al-Qura Gazette site (uqn.gov.sa) were likewise unreachable this pass
beyond an indexed search-engine snippet.

EXTRACTION METHODOLOGY: automated text extraction (pdftotext -layout,
PyMuPDF/pdfplumber coordinate reconstruction) exhibited this corpus's
documented reversed-word-order artifact on short justified trailing lines.
Rather than algorithmically patch this, EVERY one of the source PDF's 34
pages was rendered to an image and READ DIRECTLY by the assistant, article
by article -- eliminating the extraction layer entirely for the governing
text of all 65 articles across 6 chapters.

CROSS-VERIFICATION: qanoniah.com's backend API served Articles 1-8 (the
current consolidated file) without authentication before an access gate was
reached; all 8 match the MOF PDF's transcription word for word. Articles
9-65 rest on the MOF PDF alone (single-source, visually verified) -- this
distinction is preserved via two separate per-article "status" values in
this track rather than masked behind one uniform label.

AMENDMENT SCOPE (Resolution 901, 24/2/1439H): independently confirmed via a
SEPARATE mof.gov.sa 2017 draft-amendment consultation announcement, which
enumerates exactly the same five touched articles that this track's
transcription of the CURRENT text independently corroborates in substance:
Article 46 (new 46-5), Article 47 (WHOLLY NEW -- defining "المحكمة
المختصة"), Article 49 (revised opening + new 49-9), Article 52 (amended),
Article 56 (new 56-10). The insertion of Article 47 is the confirmed,
direct reason this track has 65 articles where the 2011 original issuance
(per a directly-fetched spa.gov.sa news item) had 64 -- a full clean
renumbering was used, NOT this corpus's usual "مكرر" convention for
inserted articles.

GAPS -- disclosed, not silently filled: the pre-901 wording of Articles 46,
49, 52, 56 could not be recovered (the only located copy of the original
1432H PDF is a low-OCR-quality scan, genuinely unusable); no specific named
predecessor regulation is repealed by Article 64 (a generic repeal clause);
ncar.gov.sa/adf.gov.sa/uqn.gov.sa could not be directly fetched this pass.

No legal text is altered beyond diacritic/tatweel stripping, consistent with
this corpus's other tracks. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs. This
generator writes BOTH the verified-records layer and the LLM-ready layer.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "state_revenue_regulation", "law", "official_source",
                   "state_revenue_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "state_revenue_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "state_revenue_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "state_revenue_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "state_revenue_regulation_arabic_legal_llm",
                        "state_revenue_regulation_legal_llm_001_065.json")

LAW_ID = "sa-state-revenue-regulation-860-1432"
LAW_AR = "اللائحة التنفيذية لنظام إيرادات الدولة"
KEY_RE = r"state_revenue_regulation_art_(\d{3})(_mukarrar)?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات المجلس تضع تعمل تتولى للوزارة الجهة "
            "الجهات المدين إيراداتها إيرادات").split())

GOV_NOTE = ("Arabic governs; this track's PRIMARY source is mof.gov.sa (the Ministry of "
            "Finance's own official document-library PDF, fetched directly, HTTP 200), whose "
            "current consolidated text was transcribed by direct visual reading of every "
            "rendered page image (not automated OCR/text-extraction) to avoid this corpus's "
            "documented reversed-word-order artifact. Articles 1-8 are additionally cross-"
            "verified word-for-word against qanoniah.com's independent backend API; Articles "
            "9-65 rest on the MOF PDF alone (single-source). See verification_methodology_note "
            "and known_unresolved_discrepancies in the source artifact for the full account, "
            "including the unreachable ncar.gov.sa/adf.gov.sa/uqn.gov.sa candidate sources, the "
            "confirmed scope of Ministerial Resolution 901's amendments (Articles 46, 47, 49, "
            "52, 56), and the disclosed gap in recovering the pre-901 wording of Articles 46, "
            "49, 52, and 56.")


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
    return (int(m.group(1)), 1 if m.group(2) else 0)


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
        n, is_muk = int(m.group(1)), bool(m.group(2))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({
            "law_key": "state_revenue_regulation", "law_component": "regulation", "language": "ar",
            "record_layer": "STATE_REVENUE_REGULATION_ARABIC_VERIFIED_TEXT",
            "article_number": n, "is_mukarrar": is_muk, "article_key": key,
            "number_label_ar": a["number_label_ar"],
            "section_ar": a.get("section_ar", ""),
            "article_text_verified": text,
            "verification_status": a["status"],
            "legal_status_ar": ls,
            "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
            "amendment_history": a.get("history"),
            "original_1432h_text": a.get("original_1432h_text"),
            "official_text_status": a["status"],
            "governing_source_note": GOV_NOTE,
            "translation_performed": False, "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False, "english_used_for_correction": False,
        })
        llm.append({
            "law_id": LAW_ID, "law_component": "regulation", "article_number": n,
            "is_mukarrar": is_muk, "article_key": key,
            "article_title_ar": a["number_label_ar"],
            "section_ar": a.get("section_ar") or "",
            "legal_status_ar": ls, "is_repealed": is_repealed,
            "is_added": is_added, "is_amended": is_amended,
            "record_id": "state-revenue-regulation-llm-art-%03d" % idx,
            "record_type": "verified_arabic_article", "language": "ar",
            "governing_text_language": "ar", "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
            "article_path": "state_revenue_regulation/law/articles/%s" % key,
            "keywords_ar": _kw(text),
            "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                  "%s %s" % (LAW_AR, a["number_label_ar"]),
                                  "%s من اللائحة التنفيذية لنظام إيرادات الدولة" % a["number_label_ar"]],
            "text_status": a["status"],
            "source_trust": {"source_authority": ("Ministry of Finance (mof.gov.sa) official "
                                                   "document library -- direct HTTP 200 fetch; "
                                                   "laws.boe.gov.sa has no reference to this "
                                                   "Implementing Regulation"),
                             "source_authority_ar": "وزارة المالية (mof.gov.sa) — المكتبة الرسمية للأنظمة واللوائح",
                             "source_status": a["status"].lower(),
                             "source_document_ar": LAW_AR,
                             "legal_status_ar": ls,
                             "verification_status": a["status"]},
            "translation_performed": False, "legal_interpretation_performed": False,
            "english_used_for_correction": False, "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    json.dump({
        "law_key": "state_revenue_regulation",
        "layer": "STATE_REVENUE_REGULATION_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver),
        "status_counts": src["status_counts"],
        "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
        "amending_decree": src.get("amending_decree"),
        "amending_decree_date_hijri": src.get("amending_decree_date_hijri"),
        "effective_date_hijri": src.get("effective_date_hijri"),
        "consolidated_amended_law": True,
        "numbered_articles_max": src["numbered_articles_max"],
        "original_issuance_article_count_1432h": src.get("original_issuance_article_count_1432h"),
        "mukarrar_article_keys": src["mukarrar_article_keys"],
        "chapter_structure": src["chapter_structure"],
        "repealed_predecessor": src["repealed_predecessor"],
        "verification_methodology_note": src["verification_methodology_note"],
        "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
        "source_artifact": os.path.relpath(SRC, ROOT),
    }, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    json.dump({"layer_id": "sa-state-revenue-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (65 مادة؛ 60 أصلية، 4 معدلة، 1 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation of the State Revenue Law — Arabic "
                            "LLM-ready layer (65 records: 60 original, 4 amended, 1 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 65], "text_status": "MIXED_SEE_PER_RECORD_STATUS",
               "consolidated_amended_law": True,
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("Wrote %d verified + %d LLM-ready State Revenue Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
