#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Legal LLM-ready layer — Book Four, Section 4
(الأسهم وأدوات الدين والصكوك / 股份、债务工具与融资凭证).

Structured Arabic legal-understanding records over the merged Book Four Section 4
model-1b provisions (shares_debt_instruments_sukuk). One record per provision:
  [108], [113], [115], [117]  (4 records, provision-covered only).

`legal_rule_summary_ar` is NOT authored here — it is read verbatim from the
corresponding provision's `arabic_reference_summary` in
`data/articles/book4_provisions_103_120.json`, keyed by the provision's
`source_article_numbers`, so the layer can never drift from the provision text.
Only the DERIVED metadata (subject, basis type, actors, ... queries) is defined here.

It does NOT create records for the uncovered Section-4 articles (103, 104, 105, 106,
107, 109, 110, 111, 112, 114, 116, 118, 119, 120) — Article 110 in particular is
explicitly OUT OF SCOPE (owner Option 1 reclassified it not_explicit_in_source). It
does NOT modify the provisions / English reference / Chinese data, and makes no
network calls.

Writes: data/arabic_legal_llm/book4_section4_ar_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json")
OUT = os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section4_ar_legal_llm.json")

EXPLICIT = {108, 113, 115, 117}
UNCOVERED = [103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120]
GROUPS = [[108], [113], [115], [117]]

_TRUST_NOTE = ("طبقة فهم قانوني عربية مبنية على الأحكام المراجَعة داخليًا للباب الرابع "
               "(شركة المساهمة) — قسم الأسهم وأدوات الدين والصكوك؛ ليست نصًا رسميًا ولا استشارة قانونية.")


def _load_canonical_summaries():
    """Map tuple(source_article_numbers) -> arabic_reference_summary from the
    Section 4 provisions. legal_rule_summary_ar is sourced from this map, never
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
        "ar-llm-book4-prov015", [108],
        "أنواع الأسهم وفئاتها في شركة المساهمة",
        "mixed",
        actors_ar=["شركة المساهمة", "المساهمون", "حملة فئة معينة", "الجمعية العامة غير العادية",
                   "الجمعية الخاصة بحملة الفئة"],
        rights_ar=["جواز إنشاء فئات داخل النوع الواحد بحقوق أو امتيازات أو قيود مختلفة"],
        obligations_ar=["تساوي الأسهم من النوع أو الفئة ذاتها في الحقوق والالتزامات"],
        conditions_ar=["موافقة جمعية خاصة بحملة الفئة — إضافةً إلى الجمعية غير العادية — لتعديل حقوق تلك الفئة"],
        legal_effects_ar=["تمييز الأسهم إلى ثلاثة أنواع: عادية وممتازة وقابلة للاسترداد",
                          "حماية حقوق حملة الفئة عند تعديلها"],
        cross_references_ar=["تعديل حقوق الأسهم وأدوات الدين (المادة 110 — غير مغطاة في المصدر)"],
        keywords_ar=["أنواع الأسهم", "فئات الأسهم", "الأسهم الممتازة", "القابلة للاسترداد",
                     "الجمعية الخاصة"],
        search_queries_ar=["ما أنواع أسهم شركة المساهمة؟",
                           "ما الفرق بين نوع السهم وفئته؟",
                           "كيف تُعدَّل حقوق فئة من الأسهم؟"],
        risk_flags=["share_type_vs_class_distinction"]),

    rec(
        "ar-llm-book4-prov016", [113],
        "البيع الإجباري: حق السحب (Drag-along) وحق الإلحاق (Tag-along)",
        "permissive",
        actors_ar=["المساهمون الأكثرية", "المساهمون الأقلية", "المشتري حسن النية", "شركة المساهمة"],
        rights_ar=["حق الأكثرية في إلزام الأقلية بقبول عرض شراء جميع الأسهم بالسعر والشروط نفسها (حق السحب)",
                   "حق الأقلية في إلزام الأكثرية بضمان بيع أسهمها بالشروط نفسها عند البيع (حق الإلحاق)"],
        conditions_ar=["النصّ على ذلك في النظام الأساس",
                       "موافقة مساهمين يمثلون 90% على الأقل من حقوق التصويت",
                       "أن يكون المشتري حسن النية"],
        exceptions_ar=["عدم الإخلال بأحكام نظام السوق المالية"],
        legal_effects_ar=["نفاذ آليتي السحب والإلحاق وفق النظام الأساس"],
        cross_references_ar=["نظام السوق المالية (CMA)"],
        keywords_ar=["حق السحب", "حق الإلحاق", "90%", "نظام السوق المالية", "الأقلية"],
        search_queries_ar=["ما حق السحب وحق الإلحاق في شركة المساهمة؟",
                           "ما النسبة اللازمة لتقرير حق السحب في النظام الأساس؟",
                           "هل يمكن إلزام الأقلية ببيع أسهمها؟"],
        risk_flags=["drag_along_tag_along_90pct"]),

    rec(
        "ar-llm-book4-prov017", [115],
        "التخلف عن سداد قيمة الأسهم وبيعها",
        "procedural",
        actors_ar=["المساهم المتخلف عن الدفع", "مجلس الإدارة", "شركة المساهمة", "المشتري في المزاد"],
        rights_ar=["حق المساهم المتخلف في استرداد الفائض بعد استيفاء المستحق"],
        obligations_ar=["سداد المساهم قيمة سهمه في موعدها"],
        conditions_ar=["إبلاغ المساهم المتخلف قبل البيع",
                       "بيع السهم في مزاد علني أو في السوق المالية"],
        legal_effects_ar=["استيفاء المستحق من حصيلة البيع وردّ الفائض",
                          "رجوع الشركة على سائر أموال المتخلف عند عدم كفاية الحصيلة",
                          "إيقاف حقوق السهم (الأرباح والتصويت) حتى تمام البيع أو السداد"],
        liability_ar=["مسؤولية المساهم المتخلف عن العجز في حصيلة البيع من سائر أمواله"],
        keywords_ar=["التخلف عن الدفع", "بيع السهم", "المزاد", "إيقاف الحقوق", "استيفاء المستحق"],
        search_queries_ar=["ماذا يحدث عند تخلف المساهم عن سداد قيمة سهمه؟",
                           "هل يجوز بيع أسهم المساهم المتخلف؟",
                           "هل تُوقَف حقوق السهم عند التخلف عن الدفع؟"],
        risk_flags=["default_share_sale_rights_suspension"]),

    rec(
        "ar-llm-book4-prov018", [117],
        "إصدار أدوات الدين والصكوك التمويلية القابلة للتداول",
        "permissive",
        actors_ar=["شركة المساهمة", "الجمعية العامة غير العادية", "حملة الأدوات والصكوك"],
        rights_ar=["جواز إصدار شركة المساهمة أدوات دين أو صكوكاً تمويلية قابلة للتداول"],
        conditions_ar=["الإصدار وفق أحكام نظام السوق المالية",
                       "صدور قرار من الجمعية العامة غير العادية للأدوات القابلة للتحويل إلى أسهم",
                       "تحديد الحد الأقصى للأسهم المقابلة في قرار الجمعية غير العادية"],
        legal_effects_ar=["نفاذ إصدار الأدوات أو الصكوك القابلة للتداول",
                          "ربط الإصدار القابل للتحويل بسقفٍ للأسهم"],
        cross_references_ar=["نظام السوق المالية (CMA)", "اختصاصات الجمعية غير العادية (المادة 85)"],
        keywords_ar=["أدوات الدين", "الصكوك التمويلية", "قابلة للتحويل", "الجمعية غير العادية",
                     "نظام السوق المالية"],
        search_queries_ar=["هل يجوز لشركة المساهمة إصدار صكوك؟",
                           "ما شروط إصدار أدوات دين قابلة للتحويل إلى أسهم؟",
                           "من يقرّر إصدار الصكوك القابلة للتحويل؟"],
        risk_flags=["convertible_sukuk_egm_cap"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == EXPLICIT, covered
    assert not (covered & set(UNCOVERED)), covered
    assert 110 not in covered, "Article 110 must NOT get an Arabic LLM record"
    for r in RECORDS:
        assert r["record_type"] == "provision", r["record_id"]
        assert r["legal_rule_summary_ar"] == CANON[tuple(r["article_numbers"])], r["record_id"]

    payload = {
        "layer_id": "sa-companies-arabic-legal-llm",
        "scope": "book4_section4_shares_debt_instruments_sukuk",
        "book": 4,
        "section_key": "shares_debt_instruments_sukuk",
        "section_title_ar": "الأسهم وأدوات الدين والصكوك",
        "article_range": "103-120",
        "explicit_articles": sorted(EXPLICIT),
        "provision_groups": GROUPS,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": "arabic_reference_summary (data/articles/book4_provisions_103_120.json)",
        "purpose_ar": "طبقة بيانات قانونية عربية منظّمة لتمكين البحث والاسترجاع والاستدلال القانوني العربي فوق أحكام الأسهم وأدوات الدين والصكوك المراجَعة داخليًا.",
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
