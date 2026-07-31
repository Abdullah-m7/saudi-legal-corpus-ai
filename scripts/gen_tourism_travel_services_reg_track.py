#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regulation of Travel and Tourism Services track
(لائحة خدمات السفر والسياحة).

One of ten regulations the Minister of Tourism announced together under the
Tourism Law (Royal Decree M/18, 26/1/1444H, already ingested as tourism_law)
-- none of the ten was previously in this corpus.

CITATION -- Ministerial Decision No. (2290), dated 19/5/1444H, signed by
the Minister of Tourism. UNUSUALLY STRONG SOURCING: the official PDF
(cdn.mt.gov.sa) embeds, on its own page 2, a scanned image of the SIGNED
decision letter itself (reference 25.0, Minister's Office, the Minister's
own signature) -- this is a primary-document capture, not a third-party
citation. The founding Royal Decree cited in the decision's own preamble
(M/18, 26/1/1444H) independently matches this corpus's own already-ingested
tourism_law track exactly.

VERIFICATION TIER -- effectively TIER_1 (primary signed-document capture).
See the official_source JSON's verification_methodology_note. The automated
pypdf text layer garbles Article 1's two-column definition layout (term
displayed after its own definition); visual reading of each of the 30
rendered pages (170dpi) was used instead.

STRUCTURE: 31 numbered articles (المادة الأولى .. الحادية والثلاثون) across
6 chapters + 1 appendix-type record (جدول المقابل المالي, a two-part fee
table: license-category transfer fees, and other service fees).
article_count=31, appendix_count=1, record_count=32, all اصلية (fresh
issuance, no amendment history).

TEXT HANDLING: verbatim Arabic from the visually-read PDF pages. Arabic
governs; no translation / paraphrase / interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tourism_travel_services",
                   "official_source",
                   "tourism_travel_services_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "tourism_travel_services", "verified")
RECORDS = os.path.join(OUT_VER, "tourism_travel_services_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "tourism_travel_services_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "tourism_travel_services_reg_arabic_legal_llm",
                        "tourism_travel_services_reg_legal_llm_001_032.json")

LAW_ID = "sa-tourism-travel-services-reg-2290-1444"
LAW_AR = "لائحة خدمات السفر والسياحة"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"tourism_travel_services_reg_art_(\d{3})$"
APP_RE = r"tourism_travel_services_reg_appendix_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام اللوائح الوزارة الوزير المرخص").split())


def _sort_key(key):
    m = re.match(ART_RE, key)
    if m:
        return (0, int(m.group(1)))
    m = re.match(APP_RE, key)
    return (1, int(m.group(1)))


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; PRIMARY full text is an official Ministry of Tourism PDF "
                "(cdn.mt.gov.sa), which itself embeds a scanned image of the SIGNED "
                "Ministerial Decision letter (No. 2290, 19/5/1444H) on its own page 2 -- a "
                "primary-document capture, not a third-party citation. Read visually "
                "page-by-page (170dpi) because the automated pypdf text layer garbles the "
                "two-column definitions layout in Article 1. The founding Royal Decree cited "
                "in the decision's own preamble (M/18, 26/1/1444H) independently matches this "
                "corpus's own tourism_law track. TIER_1 (effectively). See "
                "verification_methodology_note and known_unresolved_discrepancies in the "
                "source artifact before relying on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        is_app = bool(a.get("is_appendix"))
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        component = "appendix" if is_app else "regulation"
        ver.append({
            "law_key": "tourism_travel_services",
            "law_component": component,
            "language": "ar",
            "record_layer": "TOURISM_TRAVEL_SERVICES_REG_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "is_appendix": is_app,
            "is_mukarrar": bool(a.get("is_mukarrar")),
            "article_key": key,
            "number_label_ar": a["number_label_ar"],
            "title_ar": a.get("title_ar") or "",
            "section_ar": a.get("section_ar") or "",
            "article_text_verified": text,
            "verification_status": a["status"],
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_amended": ls == "معدلة",
            "is_added": ls == "مضافة",
            "text_complete": a.get("text_complete", True),
            "amendment_history": a.get("history"),
            "official_text_status": STATUS_UNCHANGED,
            "governing_source_note": gov_note,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        })
        unit_ar = a["number_label_ar"] + ((" - " + a["title_ar"]) if a.get("title_ar") else "")
        llm.append({
            "law_id": LAW_ID,
            "law_component": component,
            "article_number": n,
            "is_appendix": is_app,
            "is_mukarrar": bool(a.get("is_mukarrar")),
            "article_key": key,
            "article_title_ar": unit_ar,
            "title_ar": a.get("title_ar") or "",
            "section_ar": a.get("section_ar") or "",
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_added": ls == "مضافة",
            "is_amended": ls == "معدلة",
            "text_complete": a.get("text_complete", True),
            "record_id": "tourism-travel-services-reg-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "tourism_travel_services/%s/%s" % (component, key),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من لائحة خدمات السفر والسياحة" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Ministerial Decision No. (2290), dated 19/5/1444H -- "
                                     "full text from an official mt.gov.sa-hosted PDF that "
                                     "embeds the signed decision letter itself on page 2; "
                                     "read visually page-by-page; founding Royal Decree "
                                     "citation (M/18, 26/1/1444H) matches this corpus's own "
                                     "tourism_law track"),
                "source_authority_ar": ("القرار الوزاري رقم (2290) وتاريخ 19/5/1444هـ — النص "
                                        "الكامل من ملف PDF رسمي على mt.gov.sa يتضمن نسخة "
                                        "مصورة من القرار الموقّع نفسه في صفحته الثانية؛ قُرئ "
                                        "بصرياً صفحة بصفحة؛ استشهاد المرسوم الملكي المؤسس "
                                        "(م/18، 26/1/1444هـ) يطابق مسار نظام السياحة الموجود "
                                        "بالفعل في هذا المستودع"),
                "source_status": a["status"].lower(),
                "source_document_ar": LAW_AR,
                "legal_status_ar": ls,
                "verification_status": a["status"],
            },
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "english_used_for_correction": False,
            "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({
        "law_key": "tourism_travel_services",
        "layer": "TOURISM_TRAVEL_SERVICES_REG_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "status_counts": src["status_counts"],
        "decree": src["decree"],
        "decree_date_hijri": src["decree_date_hijri"],
        "legal_basis_ar": src["legal_basis_ar"],
        "base_law_track": src["base_law_track"],
        "legal_status_ar": src["legal_status_ar"],
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "amendment_history": src.get("amendment_history", []),
        "chapter_structure": src["chapter_structure"],
        "verification_methodology_note": src["verification_methodology_note"],
        "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
        "source_artifact": os.path.relpath(SRC, ROOT),
    }, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({
        "layer_id": "sa-tourism-travel-services-reg-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (32 سجلاً: 31 مادة "
                             "عبر 6 فصول + جدول المقابل المالي؛ جميعها أصلية)",
        "title_en": ("Regulation of Travel and Tourism Services — Arabic LLM-ready layer "
                     "(32 records: 31 articles across 6 chapters + the financial-consideration "
                     "fee table; all original)"),
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(llm),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "article_range": [1, 31],
        "text_status": STATUS_UNCHANGED,
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "status_counts": src["status_counts"],
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Tourism Travel Services Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
