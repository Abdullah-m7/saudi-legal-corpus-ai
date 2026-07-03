#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Legal LLM-ready layer — Book Four, Section 5
(المالية والأرباح وتغيير رأس المال / 财务、利润与资本变更).

Structured Arabic legal-understanding records over the merged Book Four Section 5
model-1b provisions (finance_profits_and_capital_changes). One record per provision:
  [123, 124], [126, 127], [128, 129, 130], [132], [133]  (5 records, provision-covered only).

`legal_rule_summary_ar` is NOT authored here — it is read verbatim from the
corresponding provision's `arabic_reference_summary` in
`data/articles/book4_provisions_121_137.json`, keyed by the provision's
`source_article_numbers`, so the layer can never drift from the provision text.
Only the DERIVED metadata (subject, basis type, actors, ... queries) is defined here.

It does NOT create records for the uncovered Section-5 articles (121, 122, 125, 131,
134, 135, 136, 137). Articles 134 & 135 in particular appear ONLY as a cross-reference
in the source's capital-reduction block and get no record. It does NOT modify the
provisions / English reference / Chinese data, and makes no network calls.

Writes: data/arabic_legal_llm/book4_section5_ar_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")
OUT = os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section5_ar_legal_llm.json")

EXPLICIT = {123, 124, 126, 127, 128, 129, 130, 132, 133}
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]
GROUPS = [[123, 124], [126, 127], [128, 129, 130], [132], [133]]

_TRUST_NOTE = ("طبقة فهم قانوني عربية مبنية على الأحكام المراجَعة داخليًا للباب الرابع "
               "(شركة المساهمة) — قسم المالية والأرباح وتغيير رأس المال؛ ليست نصًا رسميًا ولا استشارة قانونية.")


def _load_canonical_summaries():
    """Map tuple(source_article_numbers) -> arabic_reference_summary from the
    Section 5 provisions. legal_rule_summary_ar is sourced from this map, never
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
        "ar-llm-book4-prov019", [123, 124],
        "الاحتياطيات: تكوينها واستخدامها",
        "mixed",
        actors_ar=["الشركة", "الجمعية العامة العادية", "الجمعية العامة غير العادية", "مجلس الإدارة"],
        rights_ar=["جواز أن ينصّ النظام الأساس على اقتطاع نسبة من صافي الأرباح لتكوين احتياطي مخصّص"],
        obligations_ar=["قصْر استخدام الاحتياطي المخصّص على قرار الجمعية العامة غير العادية"],
        conditions_ar=["استخدام الاحتياطي غير المخصّص بقرار الجمعية العامة العادية بناءً على اقتراح مجلس الإدارة"],
        legal_effects_ar=["التمييز بين الاحتياطي المخصّص وغير المخصّص في جهة الاختصاص بالاستخدام"],
        keywords_ar=["الاحتياطي المخصّص", "الاحتياطي غير المخصّص", "صافي الأرباح", "الجمعية غير العادية"],
        search_queries_ar=["كيف يُكوَّن الاحتياطي في شركة المساهمة؟",
                           "من يقرّر استخدام الاحتياطي المخصّص؟",
                           "ما الفرق بين الاحتياطي المخصّص وغير المخصّص؟"]),

    rec(
        "ar-llm-book4-prov020", [126, 127],
        "زيادة رأس المال: شروطها وطرقها",
        "procedural",
        actors_ar=["الجمعية العامة غير العادية", "الشركة", "المساهمون", "الدائنون المحوّلة ديونهم"],
        obligations_ar=["صدور قرار الزيادة عن الجمعية العامة غير العادية",
                        "دفع رأس المال المصدر بالكامل قبل الزيادة"],
        conditions_ar=["أن يكون رأس المال المصدر قد دُفع بالكامل"],
        legal_effects_ar=["طرق الزيادة: أسهم جديدة نقدية أو عينية؛ مقابل ديون (تحويل الديون إلى أسهم)؛ "
                          "رسملة الاحتياطي (أسهم منحة)؛ أو مقابل أدوات دين أو صكوك"],
        cross_references_ar=["حق الأولوية في الاكتتاب (المواد 128–130)"],
        keywords_ar=["زيادة رأس المال", "الجمعية غير العادية", "رسملة الاحتياطي", "أسهم منحة", "تحويل الديون"],
        search_queries_ar=["ما شروط زيادة رأس مال شركة المساهمة؟",
                           "ما طرق زيادة رأس المال؟",
                           "هل يلزم دفع رأس المال بالكامل قبل الزيادة؟"],
        risk_flags=["capital_increase_egm_paid_up"]),

    rec(
        "ar-llm-book4-prov021", [128, 129, 130],
        "حق الأولوية في الاكتتاب والتنازل عنه وإلغاؤه",
        "mixed",
        actors_ar=["المساهمون وقت صدور قرار الزيادة", "الجمعية العامة غير العادية", "غير المساهمين"],
        rights_ar=["حق المساهمين في الأولوية بالاكتتاب بالأسهم النقدية الجديدة",
                   "حق المساهم في بيع حق الأولوية أو التنازل عنه"],
        conditions_ar=["إلغاء حق الأولوية أو منحه لغير المساهمين يستلزم نصّ النظام الأساس وتحقّق مصلحة الشركة"],
        exceptions_ar=["جواز إلغاء الجمعية غير العادية لحق الأولوية أو منحه لغير المساهمين لمصلحة الشركة"],
        legal_effects_ar=["نفاذ التنازل عن حق الأولوية أو إلغائه وفق الشروط"],
        cross_references_ar=["زيادة رأس المال (المادتان 126 و127)"],
        keywords_ar=["حق الأولوية", "الاكتتاب", "التنازل عن الحق", "إلغاء الأولوية", "الجمعية غير العادية"],
        search_queries_ar=["ما حق الأولوية في الاكتتاب بالأسهم الجديدة؟",
                           "هل يجوز التنازل عن حق الأولوية؟",
                           "متى يجوز إلغاء حق الأولوية؟"],
        risk_flags=["preemption_cancellation_minority_dilution"]),

    rec(
        "ar-llm-book4-prov022", [132],
        "الخسائر الفادحة: بلوغ الخسائر نصف رأس المال",
        "mandatory",
        actors_ar=["مجلس الإدارة", "الجمعية العامة غير العادية", "الشركة", "المساهمون"],
        obligations_ar=["إفصاح مجلس الإدارة عن الخسائر عند بلوغها نصف رأس المال المصدر",
                        "دعوة الجمعية العامة غير العادية للانعقاد"],
        conditions_ar=["بلوغ الخسائر نصف رأس المال المصدر"],
        legal_effects_ar=["نظر الجمعية غير العادية في استمرار الشركة أو معالجة الخسائر أو حلّها"],
        deadlines_ar=["الإفصاح خلال ستين (60) يوماً من علم المجلس بالخسائر",
                      "دعوة الجمعية غير العادية للانعقاد خلال مئة وثمانين (180) يوماً"],
        keywords_ar=["الخسائر الفادحة", "نصف رأس المال", "60 يوماً", "180 يوماً", "استمرار الشركة"],
        search_queries_ar=["ماذا يجب عند بلوغ الخسائر نصف رأس المال؟",
                           "ما مهلة الإفصاح عن الخسائر الفادحة؟",
                           "متى تُدعى الجمعية غير العادية بسبب الخسائر؟"],
        risk_flags=["grave_losses_60_180_day_egm"]),

    rec(
        "ar-llm-book4-prov023", [133],
        "تخفيض رأس المال: طرقه",
        "procedural",
        actors_ar=["الشركة", "الجمعية العامة غير العادية", "المساهمون", "الدائنون"],
        obligations_ar=["اتّباع إحدى الطرق النظامية لتخفيض رأس المال"],
        legal_effects_ar=["طرق التخفيض: إلغاء أسهم؛ تخفيض القيمة الاسمية (بإلغاء جزء يعادل الخسائر، "
                          "أو ردّ جزء للمساهم، أو إبراء الجزء غير المدفوع)؛ أو شراء الشركة أسهمها وإلغاؤها"],
        cross_references_ar=["حماية الدائنين وحقّ الاعتراض (المادتان 134 و135 — غير مغطاتين في المصدر)"],
        keywords_ar=["تخفيض رأس المال", "إلغاء الأسهم", "القيمة الاسمية", "شراء الأسهم", "حماية الدائنين"],
        search_queries_ar=["ما طرق تخفيض رأس المال؟",
                           "كيف تُحمى حقوق الدائنين عند تخفيض رأس المال؟",
                           "هل يجوز للشركة شراء أسهمها وإلغاؤها لتخفيض رأس المال؟"],
        risk_flags=["capital_reduction_creditor_protection"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == EXPLICIT, covered
    assert not (covered & set(UNCOVERED)), covered
    assert not ({134, 135} & covered), "Articles 134/135 must NOT get a record"
    for r in RECORDS:
        assert r["record_type"] == "provision", r["record_id"]
        assert r["legal_rule_summary_ar"] == CANON[tuple(r["article_numbers"])], r["record_id"]

    payload = {
        "layer_id": "sa-companies-arabic-legal-llm",
        "scope": "book4_section5_finance_profits_and_capital_changes",
        "book": 4,
        "section_key": "finance_profits_and_capital_changes",
        "section_title_ar": "المالية والأرباح وتغيير رأس المال",
        "article_range": "121-137",
        "explicit_articles": sorted(EXPLICIT),
        "provision_groups": GROUPS,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": "arabic_reference_summary (data/articles/book4_provisions_121_137.json)",
        "purpose_ar": "طبقة بيانات قانونية عربية منظّمة لتمكين البحث والاسترجاع والاستدلال القانوني العربي فوق أحكام المالية والأرباح وتغيير رأس المال المراجَعة داخليًا.",
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
