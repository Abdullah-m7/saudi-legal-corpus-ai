#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Legal LLM-ready layer — PILOT for Book Four, Section 1 (Articles 58, 59,
60, 66 only).

This builds a STRUCTURED ARABIC legal-understanding layer ON TOP of the existing
internally-reviewed Book Four Section 1 provisions. It does NOT modify any
provision/article text and does NOT create records for the uncovered articles
61–65. Everything here is derived understanding of already-reviewed provisions;
it is not official text and not legal advice.

Writes: data/arabic_legal_llm/book4_section1_ar_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json")
OUT = os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section1_ar_legal_llm.json")

ALLOWED = {58, 59, 60, 66}
_TRUST_NOTE = ("طبقة فهم قانوني عربية مبنية على الأحكام المراجَعة داخليًا للباب الرابع "
               "(شركة المساهمة)؛ ليست نصًا رسميًا ولا استشارة قانونية.")


def rec(record_id, article_numbers, legal_subject_ar, legal_rule_summary_ar,
        legal_basis_type, actors_ar=None, rights_ar=None, obligations_ar=None,
        prohibitions_ar=None, conditions_ar=None, exceptions_ar=None,
        legal_effects_ar=None, liability_ar=None, monetary_thresholds=None,
        deadlines_ar=None, competent_authorities_ar=None, cross_references_ar=None,
        keywords_ar=None, search_queries_ar=None, risk_flags=None):
    return {
        "book": 4,
        "record_type": "provision",
        "record_id": record_id,
        "article_numbers": article_numbers,
        "legal_subject_ar": legal_subject_ar,
        "legal_rule_summary_ar": legal_rule_summary_ar,
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
            "text_type": "internally_reviewed_provision",
            "notes": _TRUST_NOTE,
        },
    }


RECORDS = [
    rec(
        "ar-llm-book4-art058", [58],
        "تعريف شركة المساهمة ونطاق مسؤولية المساهم",
        "شركة المساهمة كيان يؤسسه شخص واحد أو أكثر، ينقسم رأس ماله إلى أسهم قابلة للتداول، "
        "وتكون الشركة وحدها مسؤولة عن ديونها والتزاماتها، وتنحصر مسؤولية المساهم في قيمة أسهمه "
        "المكتتب بها.",
        "definition",
        actors_ar=["المؤسِّس", "المساهم", "شركة المساهمة"],
        rights_ar=["اقتصار مسؤولية المساهم على قيمة أسهمه المكتتب بها"],
        obligations_ar=["أداء قيمة الأسهم المكتتب فيها"],
        conditions_ar=["انقسام رأس المال إلى أسهم قابلة للتداول"],
        legal_effects_ar=["استقلال ذمة الشركة عن ذمم المساهمين",
                          "المسؤولية المحدودة للمساهم"],
        liability_ar=["الشركة وحدها مسؤولة عن ديونها والتزاماتها",
                      "مسؤولية المساهم محدودة بقيمة أسهمه"],
        keywords_ar=["شركة المساهمة", "المساهم", "السهم", "المسؤولية المحدودة",
                     "الأسهم القابلة للتداول"],
        search_queries_ar=["ما مسؤولية المساهم عن ديون شركة المساهمة؟",
                           "هل يُسأل المساهم بأكثر من قيمة أسهمه؟",
                           "تعريف شركة المساهمة في النظام السعودي"]),

    rec(
        "ar-llm-book4-art059", [59],
        "الحد الأدنى لرأس المال المصدر والمبلغ المدفوع عند التأسيس",
        "يجب ألا يقل رأس المال المصدر عن خمسمائة ألف ريال، وألا يقل المدفوع منه عند التأسيس عن "
        "ربعه.",
        "mandatory",
        actors_ar=["المؤسِّسون", "شركة المساهمة"],
        obligations_ar=["ألا يقل رأس المال المصدر عن (500,000) ريال",
                        "دفع ما لا يقل عن ربع رأس المال المصدر عند التأسيس"],
        conditions_ar=["عند تأسيس الشركة"],
        monetary_thresholds=[
            {"amount": 500000, "currency": "SAR",
             "description_ar": "الحد الأدنى لرأس المال المصدر"},
        ],
        keywords_ar=["رأس المال المصدر", "الحد الأدنى لرأس المال", "المبلغ المدفوع",
                     "ربع رأس المال"],
        search_queries_ar=["ما الحد الأدنى لرأس مال شركة المساهمة؟",
                           "كم يجب دفعه من رأس المال عند تأسيس شركة المساهمة؟",
                           "هل يجب دفع رأس المال بالكامل عند التأسيس؟"],
        risk_flags=["minimum_capital_rule"]),

    rec(
        "ar-llm-book4-art060", [60],
        "رأس المال المصدر ورأس المال المصرح به وصلاحية المجلس في زيادة المصدر",
        "يمثل رأس المال المصدر الأسهم المكتتب بها، ويجوز أن ينص النظام الأساس على رأس المال المصرح "
        "به، ولمجلس الإدارة زيادة رأس المال المصدر في حدود رأس المال المصرح به بشرط أن يكون رأس "
        "المال المصدر قد دُفع بالكامل.",
        "mixed",
        actors_ar=["مجلس الإدارة", "المساهمون", "الجمعية العامة"],
        rights_ar=["صلاحية مجلس الإدارة في زيادة رأس المال المصدر في حدود رأس المال المصرح به"],
        obligations_ar=["اقتصار الزيادة على حدود رأس المال المصرح به"],
        conditions_ar=["نص النظام الأساس على رأس المال المصرح به",
                       "سداد رأس المال المصدر بالكامل قبل الزيادة"],
        legal_effects_ar=["زيادة رأس المال المصدر ضمن المصرَّح به بقرار من مجلس الإدارة"],
        cross_references_ar=["أحكام زيادة رأس المال (الجمعية غير العادية) في القسم الخامس"],
        keywords_ar=["رأس المال المصدر", "رأس المال المصرح به", "زيادة رأس المال",
                     "مجلس الإدارة", "النظام الأساس"],
        search_queries_ar=["ما الفرق بين رأس المال المصدر والمصرح به؟",
                           "هل يجوز لمجلس الإدارة زيادة رأس المال؟",
                           "شروط زيادة رأس المال المصدر في شركة المساهمة"],
        risk_flags=["distinguish_issued_vs_authorized_capital"]),

    rec(
        "ar-llm-book4-art066", [66],
        "تقييم الحصص العينية وقيود التصويت والموافقة على التخفيض",
        "تُقيَّم الحصص العينية بمعرفة مقيّم معتمد يبيّن قيمتها العادلة، ولا يشارك مقدّموها في "
        "التصويت على قرار تقييمها، وإذا تقرّر تخفيض المقابل الممنوح لقاء الحصة وجبت موافقة مقدّمها.",
        "mixed",
        actors_ar=["مقدّم الحصة العينية", "المقيّم المعتمد", "الجمعية العامة"],
        obligations_ar=["تقييم الحصص العينية بمعرفة مقيّم معتمد وفق القيمة العادلة"],
        prohibitions_ar=["حظر مشاركة مقدّمي الحصص العينية في التصويت على قرار تقييمها"],
        conditions_ar=["موافقة مقدّم الحصة على تخفيض المقابل الممنوح لقاء حصته العينية"],
        legal_effects_ar=["اعتماد القيمة العادلة للحصة العينية بقرار لا يشارك فيه مقدّمها"],
        competent_authorities_ar=["مقيّم معتمد"],
        keywords_ar=["الحصص العينية", "تقييم الحصص العينية", "مقيّم معتمد",
                     "القيمة العادلة", "حظر التصويت"],
        search_queries_ar=["كيف تُقيَّم الحصص العينية في شركة المساهمة؟",
                           "هل يصوّت مقدّم الحصة العينية على تقييمها؟",
                           "متى تجب موافقة مقدّم الحصة العينية على تخفيض المقابل؟"]),
]


def main():
    # Guardrail: pilot maps ONLY to explicit Section-1 articles present in source.
    with open(SRC, "r", encoding="utf-8") as fh:
        src_arts = {n for p in json.load(fh)["provisions"] for n in p["source_article_numbers"]}
    assert src_arts == ALLOWED, f"source provisions {src_arts} != {ALLOWED}"

    covered = set()
    for r in RECORDS:
        assert set(r["article_numbers"]) <= ALLOWED, r["record_id"]
        assert not (set(r["article_numbers"]) & {61, 62, 63, 64, 65}), r["record_id"]
        covered.update(r["article_numbers"])
    assert covered == ALLOWED, covered

    payload = {
        "layer_id": "sa-companies-arabic-legal-llm",
        "scope": "book4_section1_pilot",
        "book": 4,
        "section_key": "formation_and_capital",
        "article_range": "58-66",
        "explicit_articles": sorted(ALLOWED),
        "uncovered_articles_excluded": [61, 62, 63, 64, 65],
        "purpose_ar": "طبقة بيانات قانونية عربية منظّمة لتمكين البحث والاسترجاع والاستدلال القانوني العربي فوق الملخصات/الأحكام المرجعية المراجَعة داخليًا.",
        "disclaimer_ar": "ليست نصًا رسميًا ولا ترجمة رسمية ولا استشارة قانونية؛ النص الملزم هو العربي في جريدة أم القرى.",
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"wrote {OUT} with {len(RECORDS)} Arabic legal LLM records (articles 58,59,60,66)")


if __name__ == "__main__":
    main()
