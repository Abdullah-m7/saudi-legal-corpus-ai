#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Legal LLM-ready layer — Book Four, Section 3 (الجمعية العامة / 股东大会).

Structured Arabic legal-understanding records over the merged Book Four Section 3
model-1b provisions (general_assemblies). One record per provision:
  [85, 87], [92, 93], [99], [101], [102]  (5 records, provision-covered only).

`legal_rule_summary_ar` is NOT authored here — it is read verbatim from the
corresponding provision's `arabic_reference_summary` in
`data/articles/book4_provisions_084_102.json`, keyed by the provision's
`source_article_numbers`, so the layer can never drift from the provision text.
Only the DERIVED metadata (subject, basis type, actors, ... queries) is defined here.

It does NOT create records for the uncovered Section-3 articles (84, 86, 88, 89, 90,
91, 94, 95, 96, 97, 98, 100), does NOT modify the provisions / English reference /
Chinese data, and makes no network calls.

Writes: data/arabic_legal_llm/book4_section3_ar_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json")
OUT = os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section3_ar_legal_llm.json")

EXPLICIT = {85, 87, 92, 93, 99, 101, 102}
UNCOVERED = [84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100]
GROUPS = [[85, 87], [92, 93], [99], [101], [102]]

_TRUST_NOTE = ("طبقة فهم قانوني عربية مبنية على الأحكام المراجَعة داخليًا للباب الرابع "
               "(شركة المساهمة) — قسم الجمعية العامة؛ ليست نصًا رسميًا ولا استشارة قانونية.")


def _load_canonical_summaries():
    """Map tuple(source_article_numbers) -> arabic_reference_summary from the
    Section 3 provisions. legal_rule_summary_ar is sourced from this map, never
    hardcoded, so the layer stays byte-identical to the provision summaries."""
    with open(SRC, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    return {tuple(p["source_article_numbers"]): p["arabic_reference_summary"]
            for p in doc["provisions"]}


CANON = _load_canonical_summaries()


def rec(record_id, article_numbers, legal_subject_ar, legal_basis_type,
        actors_ar=None, rights_ar=None, obligations_ar=None, prohibitions_ar=None,
        conditions_ar=None, exceptions_ar=None, legal_effects_ar=None,
        liability_ar=None, monetary_thresholds=None, deadlines_ar=None,
        competent_authorities_ar=None, cross_references_ar=None, keywords_ar=None,
        search_queries_ar=None, risk_flags=None):
    summary = CANON[tuple(article_numbers)]  # verbatim from the provision data
    return {
        "book": 4,
        "record_type": "provision",
        "record_id": record_id,
        "article_numbers": article_numbers,
        "legal_subject_ar": legal_subject_ar,
        "legal_rule_summary_ar": summary,
        "legal_basis_type": legal_basis_type,
        "actors_ar": actors_ar or [],
        "rights_ar": rights_ar or [],
        "obligations_ar": obligations_ar or [],
        "prohibitions_ar": prohibitions_ar or [],
        "conditions_ar": conditions_ar or [],
        "exceptions_ar": exceptions_ar or [],
        "legal_effects_ar": legal_effects_ar or [],
        "liability_ar": liability_ar or [],
        "monetary_thresholds": monetary_thresholds or [],
        "deadlines_ar": deadlines_ar or [],
        "competent_authorities_ar": competent_authorities_ar or [],
        "cross_references_ar": cross_references_ar or [],
        "keywords_ar": keywords_ar or [],
        "search_queries_ar": search_queries_ar or [],
        "risk_flags": risk_flags or [],
        "source_trust": {
            "official_text_check": "needs_check",
            "text_type": "internally_reviewed_summary",
            "notes": _TRUST_NOTE,
        },
    }


RECORDS = [
    rec(
        "ar-llm-book4-prov010", [85, 87],
        "اختصاصات الجمعية العامة العادية وغير العادية",
        "mixed",
        actors_ar=["الجمعية العامة العادية", "الجمعية العامة غير العادية", "مجلس الإدارة",
                   "مراجع الحسابات", "المساهمون"],
        rights_ar=["اختصاص الجمعية العادية بانتخاب أعضاء المجلس وعزلهم وتعيين مراجع الحسابات",
                   "اختصاص الجمعية غير العادية بتعديل النظام الأساس والبتّ في استمرار الشركة أو حلّها"],
        obligations_ar=["نظر الجمعية العادية في القوائم المالية والتقارير وتوزيع الأرباح وتكوين الاحتياطيات"],
        prohibitions_ar=["حظر حرمان المساهمين من حقوقهم الأساسية عند تعديل النظام الأساس"],
        conditions_ar=["إجماع المساهمين لزيادة الأعباء المالية عليهم",
                       "موافقة الجمعية غير العادية على شراء الشركة أسهمها"],
        legal_effects_ar=["تقسيم الاختصاصات بين الجمعية العادية وغير العادية"],
        cross_references_ar=["النصاب والأغلبية (المادتان 92 و93)"],
        keywords_ar=["الجمعية العامة العادية", "الجمعية العامة غير العادية", "الاختصاصات",
                     "تعديل النظام الأساس", "حلّ الشركة"],
        search_queries_ar=["ما اختصاصات الجمعية العامة العادية؟",
                           "ما اختصاصات الجمعية العامة غير العادية؟",
                           "من يعدّل النظام الأساس لشركة المساهمة؟"]),

    rec(
        "ar-llm-book4-prov011", [92, 93],
        "النصاب القانوني وأغلبية التصويت في الجمعيتين العادية وغير العادية",
        "mandatory",
        actors_ar=["الجمعية العامة العادية", "الجمعية العامة غير العادية", "المساهمون"],
        obligations_ar=["تحقّق النصاب المقرّر لصحة انعقاد الجمعية",
                        "صدور القرارات بالأغلبية المقرّرة"],
        conditions_ar=["نصاب الجمعية العادية: ربع الأسهم في الاجتماع الأول (يجوز رفعه بما لا يتجاوز النصف)",
                       "نصاب الجمعية غير العادية: نصف الأسهم أولاً (يجوز رفعه بما لا يتجاوز الثلثين) ثم الربع",
                       "صحة الاجتماع الثاني (العادية) والثالث (غير العادية) أياً كان عدد الحاضرين"],
        legal_effects_ar=["أغلبية الأصوات الممثَّلة في الجمعية العادية",
                          "أغلبية الثلثين في الجمعية غير العادية، وثلاثة الأرباع لقرارات رأس المال والمدة والحلّ والاندماج والتقسيم"],
        cross_references_ar=["اختصاصات الجمعيتين (المادتان 85 و87)"],
        keywords_ar=["النصاب", "الأغلبية", "الجمعية العادية", "الجمعية غير العادية", "ثلاثة أرباع"],
        search_queries_ar=["ما نصاب انعقاد الجمعية العامة العادية؟",
                           "ما الأغلبية اللازمة لقرارات الجمعية غير العادية؟",
                           "متى تلزم أغلبية ثلاثة أرباع الأصوات؟"],
        risk_flags=["ogm_egm_quorum_majority"]),

    rec(
        "ar-llm-book4-prov012", [99],
        "إبطال قرارات الجمعية العامة المخالفة",
        "procedural",
        actors_ar=["المساهم المعترض", "المساهم الغائب بعذر", "الجمعية العامة", "الغير حسن النية"],
        rights_ar=["حق المساهم المعترض أو الغائب بعذر مشروع في طلب إبطال القرار المخالف"],
        conditions_ar=["اعتراض المساهم في الاجتماع أو تغيّبه لعذر مشروع",
                       "بقاء المدّعي محتفظاً بصفة المساهم طوال الدعوى"],
        exceptions_ar=["عدم الإخلال بحقوق الغير حسن النية"],
        deadlines_ar=["عدم سماع الدعوى بعد مضيّ تسعين (90) يوماً من تاريخ صدور القرار"],
        legal_effects_ar=["إبطال القرار المخالف للنظام أو النظام الأساس"],
        keywords_ar=["إبطال القرار", "الاعتراض", "تسعون يوماً", "صفة المساهم", "حسن النية"],
        search_queries_ar=["متى يجوز إبطال قرار الجمعية العامة؟",
                           "ما مهلة طلب إبطال قرار الجمعية؟",
                           "هل يشترط بقاء صفة المساهم أثناء دعوى الإبطال؟"],
        risk_flags=["decision_annulment_90_day_limit"]),

    rec(
        "ar-llm-book4-prov013", [101],
        "إصدار قرارات الجمعية العامة بالتمرير في الشركات غير المدرجة",
        "procedural",
        actors_ar=["الجمعية العامة العادية", "الجمعية العامة غير العادية", "المساهمون"],
        rights_ar=["جواز إصدار قرارات الجمعية بالتمرير في الشركات غير المدرجة"],
        conditions_ar=["صدور قرارات الجمعية العادية بالتمرير بأغلبية الأصوات",
                       "صدور قرارات الجمعية غير العادية بأغلبية لا تقلّ عن 75% من الأصوات"],
        exceptions_ar=["اشتراط النظام الأساس نسبةً أعلى فيُعمَل بها"],
        legal_effects_ar=["نفاذ القرار الصادر بالتمرير عند بلوغ الأغلبية المقرّرة"],
        keywords_ar=["القرار بالتمرير", "الشركات غير المدرجة", "75%", "الجمعية غير العادية"],
        search_queries_ar=["هل يجوز إصدار قرارات الجمعية بالتمرير؟",
                           "ما نسبة الأصوات اللازمة لقرار الجمعية غير العادية بالتمرير؟"]),

    rec(
        "ar-llm-book4-prov014", [102],
        "حق الأقلية (5%) في طلب التفتيش على الشركة",
        "procedural",
        actors_ar=["المساهمون المالكون 5% من رأس المال", "الجهة القضائية المختصة",
                   "أعضاء مجلس الإدارة", "مراجع الحسابات"],
        rights_ar=["حق مساهمي الأقلية (5%) في طلب التفتيش على الشركة"],
        conditions_ar=["وجود ما يدعو إلى الاشتباه في تصرّفات أعضاء المجلس أو مراجع الحسابات"],
        legal_effects_ar=["إمكان تحميل الطالب نفقات التفتيش بقرار من الجهة القضائية"],
        competent_authorities_ar=["الجهة القضائية المختصة"],
        keywords_ar=["التفتيش على الشركة", "5%", "الأقلية", "نفقات التفتيش"],
        search_queries_ar=["من يحقّ له طلب التفتيش على الشركة؟",
                           "ما نسبة رأس المال اللازمة لطلب التفتيش؟",
                           "من يتحمّل نفقات التفتيش على الشركة؟"],
        risk_flags=["minority_5pct_inspection_right"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == EXPLICIT, covered
    assert not (covered & set(UNCOVERED)), covered
    for r in RECORDS:
        assert r["record_type"] == "provision", r["record_id"]
        assert r["legal_rule_summary_ar"] == CANON[tuple(r["article_numbers"])], r["record_id"]

    payload = {
        "layer_id": "sa-companies-arabic-legal-llm",
        "scope": "book4_section3_general_assemblies",
        "book": 4,
        "section_key": "general_assemblies",
        "section_title_ar": "الجمعية العامة",
        "article_range": "84-102",
        "explicit_articles": sorted(EXPLICIT),
        "provision_groups": GROUPS,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": "arabic_reference_summary (data/articles/book4_provisions_084_102.json)",
        "purpose_ar": "طبقة بيانات قانونية عربية منظّمة لتمكين البحث والاسترجاع والاستدلال القانوني العربي فوق أحكام الجمعية العامة المراجَعة داخليًا.",
        "disclaimer_ar": "ليست نصًا رسميًا ولا ترجمة رسمية ولا استشارة قانونية؛ النص الملزم هو العربي في جريدة أم القرى.",
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d Arabic legal LLM records (groups %s)" % (OUT, len(RECORDS), GROUPS))


if __name__ == "__main__":
    main()
