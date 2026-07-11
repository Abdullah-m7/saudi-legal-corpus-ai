#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Labor Annex 5 track (unified model employment contract forms).

Source: annex 5 of the official HRSD Labor implementing-regulation PDF — the
four model contract forms (permanent bilingual, part-time, casual/temporary,
seasonal): 101 units + the permanent form's 8-row bilingual glossary table =
102 records. Arabic governs; the permanent form's printed English column is
carried verbatim as a NON-GOVERNING text_en_reference field (it is part of
the official form, not our translation). Fill-in blanks kept as printed.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "annex5", "official_source",
                   "labor_annex5_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "labor", "annex5", "verified")
RECORDS = os.path.join(OUT_VER, "labor_annex5_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "labor_annex5_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                        "labor_annex5_contract_forms_llm.json")

LAW_ID = "sa-labor-model-contract-forms"
DOC_AR = "النماذج الموحدة لعقد العمل"
STATUS = "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED_BILINGUAL_FORM"
FORM_AR = {"permanent": "نموذج عقد العمل الدائم",
           "part_time": "نموذج عقد عمل لبعض الوقت",
           "casual_temporary": "نموذج عقد عمل عرضي/مؤقت",
           "seasonal": "نموذج عقد عمل موسمي"}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي هذا العقد الطرف الطرفين").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [DOC_AR]


def _glossary_texts(g):
    """Mechanical linearization of the bilingual glossary table (cells verbatim)."""
    ar_lines, en_lines = ["جدول المصطلحات"], ["Glossary of terms"]
    for row in g["rows"]:
        term_ar, term_en, def_ar, def_en = row
        ar_lines.append("%s: %s" % (term_ar, def_ar))
        en_lines.append("%s: %s" % (term_en, def_en))
    return "\n".join(ar_lines), "\n".join(en_lines)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    n = 0
    for form in src["forms"]:
        fk = form["form_key"]
        form_ar = FORM_AR[fk]
        items = [("unit", u) for u in form["units"]]
        if form.get("glossary_table"):
            items.append(("glossary", form["glossary_table"]))
        for kind, item in items:
            n += 1
            if kind == "unit":
                key = item["unit_key"]
                label = item.get("unit_label_ar") or key
                text_ar = item["text_ar"]
                text_en = item.get("text_en_reference", "") if form.get("bilingual") else ""
                verification = item.get("verification", "")
                rtype = "verified_arabic_form_unit"
            else:
                key = "%s_glossary_table" % fk
                label = "جدول المصطلحات"
                text_ar, text_en = _glossary_texts(item)
                verification = "ocr+image"
                rtype = "verified_arabic_table"
            ver.append({"law_key": "labor", "law_component": "model_contract_forms",
                        "language": "ar",
                        "record_layer": "LABOR_ANNEX5_CONTRACT_FORMS_VERIFIED",
                        "article_number": n, "article_key": key,
                        "form_key": fk, "form_title_ar": form_ar,
                        "number_label_ar": label,
                        "article_text_verified": text_ar,
                        "text_en_reference": text_en,
                        "english_reference_note": ("Printed English column of the official "
                                                   "bilingual form; NON-governing reference; "
                                                   "not our translation." if text_en else ""),
                        "verification_status": "ACTIVE",
                        "verification_method": verification,
                        "ocr_similarity_ar": item.get("ocr_similarity_ar") if kind == "unit" else None,
                        "official_text_status": STATUS,
                        "governing_source_note": ("Arabic governs; annex 5 of the official HRSD "
                                                  "PDF; fill-in blanks kept as printed (see "
                                                  "source artifact)."),
                        "translation_performed": False, "legal_interpretation_performed": False,
                        "summarized_or_paraphrased": False, "english_used_for_correction": False})
            llm.append({"law_id": LAW_ID, "law_component": "model_contract_forms",
                        "article_number": n, "article_key": key,
                        "form_key": fk, "form_title_ar": form_ar,
                        "article_title_ar": label,
                        "record_id": "labor-annex5-llm-%03d-%s" % (n, fk.replace("_", "-")),
                        "record_type": rtype, "language": "ar",
                        "governing_text_language": "ar", "article_text_ar": text_ar,
                        "article_text_hash_sha256": hashlib.sha256(text_ar.encode("utf-8")).hexdigest(),
                        "text_en_reference": text_en,
                        "llm_title_ar": "%s — %s — %s" % (DOC_AR, form_ar, label),
                        "retrieval_title_ar": "%s - %s" % (form_ar, label),
                        "article_path": "labor/annex5/%s/%03d" % (fk, n),
                        "keywords_ar": _kw(text_ar),
                        "search_queries_ar": ["%s %s" % (form_ar, label),
                                              "النموذج الموحد لعقد العمل %s" % form_ar.replace("نموذج ", ""),
                                              "بنود %s" % form_ar],
                        "text_status": STATUS,
                        "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                         "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                         "source_status": "hrsd_official_pdf_ocr_image_cross_checked_bilingual_form",
                                         "source_document_ar": DOC_AR,
                                         "verification_status": "ACTIVE"},
                        "translation_performed": False, "legal_interpretation_performed": False,
                        "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "labor", "layer": "LABOR_ANNEX5_CONTRACT_FORMS_VERIFIED",
               "record_count": len(ver),
               "forms": {f["form_key"]: len(f["units"]) for f in src["forms"]},
               "glossary_rows": len(src["forms"][0]["glossary_table"]["rows"]),
               "official_text_status": STATUS,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-labor-annex5-contract-forms-legal-llm", "law_id": LAW_ID,
               "law_component": "model_contract_forms",
               "title_ar": DOC_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (102 سجلًّا: 4 نماذج عقود + جدول مصطلحات)",
               "title_en": "Unified model employment contract forms (Labor Annex 5) — Arabic LLM-ready layer (102 records)",
               "record_type": "verified_arabic_form_unit", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Labor Annex 5 records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
