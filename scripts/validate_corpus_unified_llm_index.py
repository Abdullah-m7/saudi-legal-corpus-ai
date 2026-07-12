#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the unified Arabic LLM retrieval index.

Checks the index is complete and consistent with the source enrichment layers,
that records are well-formed and unique, and that a set of built-in sanity
queries route to the expected law.  Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
SUMMARY = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index_summary.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from search_corpus_unified import search  # noqa: E402

EXPECTED_TOTAL = 4343
EXPECTED_PER_CORPUS = {"companies_law": 281, "pdpl": 81, "investment": 53, "civil": 721, "gtpl": 256, "labor": 571, "evidence": 322, "personal_status": 293, "sharia_procedure": 880, "criminal_procedure": 403, "enforcement": 371, "judiciary": 85, "board_of_grievances": 26}
REQUIRED = ["record_id", "corpus", "law_id", "law_component", "law_title_ar",
            "article_number", "llm_title_ar", "retrieval_title_ar", "article_path",
            "keywords_ar", "search_queries_ar", "text_ar", "text_status", "source_layer"]

# (query, expected corpus of the top hit, expected article_number of the top hit)
SANITY = [
    ("تسرب البيانات الشخصية", "pdpl", 24),
    ("المصادرة غير المباشرة", "investment", 5),
    ("انتخاب أعضاء مجلس الإدارة", "companies_law", 68),
    ("عقد المقايضة", "civil", 361),
    ("المزايدة العكسية", "gtpl", None),
    ("ساعات العمل الإضافية", "labor", None),
    ("تحويل عقد العمل المؤقت تسعين يوما", "labor", 1),
    ("جدول المخالفات والجزاءات", "labor", None),
    ("ترخيص التوسط في توظيف السعوديين", "labor", None),
    ("استقبال وإيواء العمالة المستقدمة", "labor", 52),
    ("الترتيبات التيسيرية للإعاقات البصرية", "labor", 4),
    ("نموذج عقد عمل موسمي", "labor", None),
    ("حجية الدليل الرقمي في الإثبات", "evidence", 55),
    ("التوقيع الرقمي في إجراءات الإثبات", "evidence", 2),
    ("قيد الخبراء أمام المحاكم", "evidence", 2),
    ("الخطبة والوعد بالزواج", "personal_status", 1),
    ("المهر ملك للمرأة", "personal_status", 38),
    ("انتفاء الخلوة بين الزوجين", "personal_status", 1),
    ("طرق الاعتراض على الأحكام الاستئناف والنقض", "sharia_procedure", 176),
    ("يجوز رد القاضي لأحد الأسباب دعوى مماثلة أو خصومة مع أحد الخصوم", "sharia_procedure", 96),
    ("تكون المرافعة علنية ما لم ترَ المحكمة إجراءها سرا", "sharia_procedure", 64),
    ("الجلسة التحضيرية في القضايا التجارية عرض الصلح", "sharia_procedure", 170),
    ("يكتب التاريخ الهجري أولا بحسب تقويم أم القرى", "sharia_procedure", 16),
    ("لا يجوز القبض على أي إنسان أو توقيفه إلا بأمر من السلطة المختصة", "criminal_procedure", 35),
    ("الأحكام النهائية هي الأحكام المكتسبة للقطعية", "criminal_procedure", 210),
    ("يباشر المحقق معاينة مكان وقوع الجريمة بنفسه وله ندب أحد رجال الضبط الجنائي", "criminal_procedure", 54),
    ("ضبط الأموال والأرصدة لدى البنوك في مرحلة التحقيق", "criminal_procedure", 58),
    ("التنفيذ الجبري لا يكون إلا بسند تنفيذي لحق محقق الوجود حال الأداء", "enforcement", 9),
    ("يختص قاضي التنفيذ بالفصل في منازعات التنفيذ", "enforcement", 3),
    ("يكون توقيع المحضر في مكان المال المحجوز إن أمكن وعلى كل صفحة من صفحاته", "enforcement", 134),
    ("الحجز على العقار حجز على غلته ويبلغ المستأجر بالحجز التنفيذي", "enforcement", 143),
    ("القضاة مستقلون لا سلطان عليهم في قضائهم لغير أحكام الشريعة الإسلامية", "judiciary", 1),
    ("لا يجوز نقل أعضاء السلك القضائي أو ندبهم داخل السلك القضائي إلا بقرار من المجلس الأعلى للقضاء", "judiciary", 49),
    ("ديوان المظالم هيئة قضاء إداري مستقلة يرتبط مباشرة بالملك", "board_of_grievances", 1),
    ("تختص المحاكم الإدارية بالفصل في دعاوى إلغاء القرارات الإدارية النهائية وإساءة استعمال السلطة", "board_of_grievances", 13),
    ("يُنشأ في الديوان مجلس يسمى مجلس القضاء الإداري ويتكون من رئيس ديوان المظالم واثنين من ذوي الخبرة والاختصاص", "board_of_grievances", 4),
]


def main():
    errors = []
    for p in (INDEX, SUMMARY):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    records = [json.loads(l) for l in open(INDEX, encoding="utf-8") if l.strip()]

    if len(records) != EXPECTED_TOTAL:
        errors.append("[1] expected %d records, found %d" % (EXPECTED_TOTAL, len(records)))

    per = {}
    ids = set()
    for r in records:
        per[r["corpus"]] = per.get(r["corpus"], 0) + 1
        for k in REQUIRED:
            if k not in r:
                errors.append("[2] %s: missing field %r" % (r.get("record_id"), k))
        if not str(r.get("text_ar", "")).strip():
            errors.append("[2] %s: empty text_ar" % r.get("record_id"))
        if r["record_id"] in ids:
            errors.append("[3] duplicate record_id %s" % r["record_id"])
        ids.add(r["record_id"])

    for corpus, n in EXPECTED_PER_CORPUS.items():
        if per.get(corpus) != n:
            errors.append("[4] corpus %s: expected %d, found %d" % (corpus, n, per.get(corpus)))

    # [5] index text matches the source enrichment layers verbatim
    src_text = {}
    for rel in (
        "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
        "data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json",
        "data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
        "data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json",
        "data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json",
        "data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
        "data/gtpl_arabic_legal_llm/gtpl_law_legal_llm_001_099.json",
        "data/gtpl_arabic_legal_llm/gtpl_regulation_legal_llm_001_157.json",
        "data/labor_arabic_legal_llm/labor_law_legal_llm_001_245.json",
        "data/labor_arabic_legal_llm/labor_regulation_legal_llm_001_040.json",
        "data/labor_arabic_legal_llm/labor_annex1_legal_llm_001_072.json",
        "data/labor_arabic_legal_llm/labor_annex1_violation_tables_llm.json",
        "data/labor_arabic_legal_llm/labor_annex3_legal_llm_001_020.json",
        "data/labor_arabic_legal_llm/labor_annex4_legal_llm_001_072.json",
        "data/labor_arabic_legal_llm/labor_annex2_accessibility_tables_llm.json",
        "data/labor_arabic_legal_llm/labor_annex5_contract_forms_llm.json",
        "data/evidence_arabic_legal_llm/evidence_law_legal_llm_001_129.json",
        "data/evidence_arabic_legal_llm/evidence_electronic_rules_legal_llm_001_024.json",
        "data/evidence_arabic_legal_llm/evidence_procedural_manuals_legal_llm_001_135.json",
        "data/evidence_arabic_legal_llm/evidence_expertise_rules_legal_llm_001_034.json",
        "data/personal_status_arabic_legal_llm/personal_status_law_legal_llm_001_252.json",
        "data/personal_status_arabic_legal_llm/personal_status_regulation_legal_llm_001_041.json",
        "data/sharia_procedure_arabic_legal_llm/sharia_procedure_law_legal_llm_001_243.json",
        "data/sharia_procedure_arabic_legal_llm/sharia_procedure_regulation_legal_llm_001_637.json",
        "data/criminal_procedure_arabic_legal_llm/criminal_procedure_law_legal_llm_001_222.json",
        "data/criminal_procedure_arabic_legal_llm/criminal_procedure_regulation_legal_llm_001_181.json",
        "data/enforcement_arabic_legal_llm/enforcement_law_legal_llm_001_098.json",
        "data/enforcement_arabic_legal_llm/enforcement_regulation_legal_llm_001_273.json",
        "data/judiciary_arabic_legal_llm/judiciary_law_legal_llm_001_085.json",
        "data/board_of_grievances_arabic_legal_llm/board_of_grievances_law_legal_llm_001_026.json",
    ):
        env = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        for r in env["records"]:
            src_text[r["record_id"]] = r.get("article_text_ar") or r.get("official_text_ar")
    for r in records:
        if r["text_ar"] != src_text.get(r["record_id"]):
            errors.append("[5] %s: text_ar differs from source layer" % r["record_id"])

    # [6] summary consistency
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("total_records") != len(records):
        errors.append("[6] summary total_records mismatch")

    # [7] sanity queries route to the expected law/article
    for q, corpus, art in SANITY:
        hits = search(q, top=1, index=records)
        if not hits:
            errors.append("[7] query %r returned no hits" % q)
            continue
        top = hits[0]
        rid = top["record_id"]
        rec = next((x for x in records if x["record_id"] == rid), {})
        if rec.get("corpus") != corpus or (art is not None and top["article_number"] != art):
            errors.append("[7] query %r -> top %s/art %s (expected %s/art %s)"
                          % (q, rec.get("corpus"), top["article_number"], corpus, art))

    if errors:
        print("FAIL: %d error(s) in unified LLM index:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    print("PASS: unified LLM retrieval index over %d records" % len(records))
    print("  - companies_law 281 + pdpl 81 + investment 53 + civil 721 + gtpl 256 + labor 571 + evidence 322 + personal_status 293 + sharia_procedure 880 + criminal_procedure 403 + enforcement 371 + judiciary 85 + board_of_grievances 26; unique ids; text verbatim from source layers")
    print("  - %d sanity queries each route to the expected law/article" % len(SANITY))
    return 0


if __name__ == "__main__":
    sys.exit(main())
