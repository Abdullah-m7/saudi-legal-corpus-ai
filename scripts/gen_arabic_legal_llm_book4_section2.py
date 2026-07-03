#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Legal LLM-ready layer — Book Four, Section 2 (مجلس الإدارة والحوكمة).

Structured Arabic legal-understanding records over the newly merged Book Four
Section 2 model-1b provisions (board_and_governance). One record per provision:
  [67, 68], [71], [72], [75], [77]  (5 records, provision-covered articles only).

`legal_rule_summary_ar` is NOT authored here — it is read verbatim from the
corresponding provision's `arabic_reference_summary` in
`data/articles/book4_provisions_067_083.json`, keyed by the provision's
`source_article_numbers`, so the layer can never drift from the provision text.
Only the DERIVED metadata (subject, basis type, actors, rights, ... queries) is
defined in this file.

It does NOT create records for the uncovered Section-2 articles (69, 70, 73, 74,
76, 78–83), does NOT modify the provisions / English reference / Chinese data, and
makes no network calls.

Writes: data/arabic_legal_llm/book4_section2_ar_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json")
OUT = os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section2_ar_legal_llm.json")

EXPLICIT = {67, 68, 71, 72, 75, 77}
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]
GROUPS = [[67, 68], [71], [72], [75], [77]]

_TRUST_NOTE = ("طبقة فهم قانوني عربية مبنية على الأحكام المراجَعة داخليًا للباب الرابع "
               "(شركة المساهمة) — قسم مجلس الإدارة والحوكمة؛ ليست نصًا رسميًا ولا استشارة قانونية.")


def _load_canonical_summaries():
    """Map tuple(source_article_numbers) -> arabic_reference_summary from the
    Section 2 provisions. legal_rule_summary_ar is sourced from this map, never
    hardcoded, so the layer stays byte-identical to the provision summaries."""
    with open(SRC, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    canon = {}
    for p in doc["provisions"]:
        canon[tuple(p["source_article_numbers"])] = p["arabic_reference_summary"]
    return canon


CANON = _load_canonical_summaries()


def rec(record_id, article_numbers, legal_subject_ar, legal_basis_type,
        actors_ar=None, rights_ar=None, obligations_ar=None, prohibitions_ar=None,
        conditions_ar=None, exceptions_ar=None, legal_effects_ar=None,
        liability_ar=None, monetary_thresholds=None, deadlines_ar=None,
        competent_authorities_ar=None, cross_references_ar=None, keywords_ar=None,
        search_queries_ar=None, risk_flags=None):
    # legal_rule_summary_ar is pulled verbatim from the provision data.
    summary = CANON[tuple(article_numbers)]
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
        "ar-llm-book4-prov005", [67, 68],
        "تكوين مجلس الإدارة ومدة العضوية وعزل الأعضاء",
        "mixed",
        actors_ar=["مجلس الإدارة", "عضو مجلس الإدارة", "الجمعية العامة العادية"],
        rights_ar=["جواز إعادة انتخاب عضو المجلس", "حق الجمعية العامة العادية في عزل أعضاء المجلس"],
        obligations_ar=["تكوين المجلس من ثلاثة (3) أعضاء على الأقل من ذوي الصفة الطبيعية"],
        conditions_ar=["ألا تزيد مدة عضوية المجلس على أربع (4) سنوات"],
        legal_effects_ar=["عزل أعضاء المجلس بقرار الجمعية العامة العادية ولو نصّ النظام الأساس على غير ذلك"],
        deadlines_ar=["مدة العضوية: لا تزيد على أربع (4) سنوات"],
        cross_references_ar=["اختصاصات الجمعية العامة العادية (القسم الثالث)"],
        keywords_ar=["مجلس الإدارة", "تكوين المجلس", "مدة العضوية", "عزل العضو", "الجمعية العامة العادية"],
        search_queries_ar=["كم عدد أعضاء مجلس إدارة شركة المساهمة؟",
                           "ما مدة عضوية مجلس الإدارة؟",
                           "هل يجوز عزل عضو مجلس الإدارة؟"]),

    rec(
        "ar-llm-book4-prov006", [71],
        "الإفصاح عن المصالح وتجنّب التصويت ومسؤولية أعضاء المجلس",
        "mandatory",
        actors_ar=["عضو مجلس الإدارة", "المجلس", "الجمعية العامة"],
        obligations_ar=["الإفصاح فور العلم عن أي مصلحة مباشرة أو غير مباشرة في أعمال وعقود الشركة",
                        "إثبات المصلحة في محضر الاجتماع"],
        prohibitions_ar=["عدم مشاركة العضو صاحب المصلحة في التصويت عليها في المجلس أو الجمعية العامة"],
        conditions_ar=["إثبات العضو اعتراضه في المحضر لدفع المسؤولية",
                       "إثبات الغائب عدم علمه بالقرار أو تعذّر اعتراضه بعد علمه به"],
        legal_effects_ar=["إعفاء العضو المعترض أو الغائب من المسؤولية بحسب الأحوال"],
        liability_ar=["مسؤولية العضو عن عدم الإفصاح أو التصويت على مصلحته",
                      "إعفاء من أثبت اعتراضه في المحضر"],
        keywords_ar=["الإفصاح", "تعارض المصالح", "محضر الاجتماع", "الامتناع عن التصويت", "مسؤولية العضو"],
        search_queries_ar=["متى يجب على عضو المجلس الإفصاح عن مصلحته؟",
                           "هل يصوّت العضو على قرار له فيه مصلحة؟",
                           "كيف يُعفى عضو المجلس من المسؤولية؟"]),

    rec(
        "ar-llm-book4-prov007", [72],
        "حظر تمويل أعضاء مجلس الإدارة وأقاربهم",
        "prohibition",
        actors_ar=["الشركة", "عضو مجلس الإدارة", "أقارب العضو", "البنوك وشركات التمويل"],
        prohibitions_ar=["حظر تقديم الشركة قرضاً لأي من أعضاء مجلس إدارتها",
                         "حظر ضمان أو كفالة الشركة لقرض يعقده العضو مع الغير",
                         "امتداد الحظر إلى أقارب العضو (الأصول والفروع والأزواج)"],
        exceptions_ar=["البنوك وشركات التمويل وفق شروط تعاملها العامة",
                       "برامج تحفيز العاملين المعتمدة"],
        legal_effects_ar=["بطلان كل عقد يخالف حظر التمويل"],
        keywords_ar=["حظر القروض", "تمويل الأعضاء", "الكفالة والضمان", "الأقارب", "بطلان العقد"],
        search_queries_ar=["هل يجوز للشركة إقراض عضو مجلس الإدارة؟",
                           "هل يمتد حظر التمويل إلى أقارب العضو؟",
                           "ما استثناءات حظر تمويل أعضاء المجلس؟"],
        risk_flags=["related_party_financing_prohibition"]),

    rec(
        "ar-llm-book4-prov008", [75],
        "بيع الأصول الجوهرية وموافقة الجمعية العامة",
        "mandatory",
        actors_ar=["الشركة", "مجلس الإدارة", "الجمعية العامة"],
        obligations_ar=["الحصول على موافقة الجمعية العامة على بيع أصول تزيد قيمتها على 50% من إجمالي أصول الشركة"],
        conditions_ar=["احتساب النسبة تراكمياً سواء تمّ البيع بصفقة واحدة أو عدّة صفقات",
                       "بدء الاحتساب من أول صفقة خلال الاثني عشر (12) شهراً السابقة"],
        deadlines_ar=["نافذة الاحتساب التراكمي: اثنا عشر (12) شهراً سابقة"],
        legal_effects_ar=["توقّف نفاذ البيع الجوهري على موافقة الجمعية العامة"],
        keywords_ar=["بيع الأصول الجوهرية", "50% من الأصول", "موافقة الجمعية العامة", "الاحتساب التراكمي"],
        search_queries_ar=["متى يلزم موافقة الجمعية العامة على بيع أصول الشركة؟",
                           "ما نسبة الأصول التي تستوجب موافقة الجمعية العامة؟",
                           "كيف تُحتسب صفقات بيع الأصول خلال السنة؟"],
        risk_flags=["material_asset_disposal_threshold"]),

    rec(
        "ar-llm-book4-prov009", [77],
        "صلاحيات مجلس الإدارة تجاه الغير والتزام الشركة",
        "mixed",
        actors_ar=["مجلس الإدارة", "الشركة", "الغير", "الجمعية العامة"],
        rights_ar=["تمتّع المجلس بأوسع الصلاحيات اللازمة لتحقيق أغراض الشركة"],
        exceptions_ar=["ما يدخل في اختصاص الجمعية العامة على وجه الحصر",
                       "عدم التزام الشركة إذا كان الغير سيّئ النية أو يعلم بتجاوز التصرّف حدود الصلاحيات"],
        legal_effects_ar=["التزام الشركة بتصرّفات المجلس باسمها ولو تجاوزت حدود صلاحياته"],
        cross_references_ar=["اختصاصات الجمعية العامة (القسم الثالث)"],
        keywords_ar=["صلاحيات المجلس", "اختصاص الجمعية العامة", "التزام الشركة", "سوء النية", "تجاوز الصلاحيات"],
        search_queries_ar=["ما حدود صلاحيات مجلس الإدارة؟",
                           "هل تلتزم الشركة بتصرّف تجاوز فيه المجلس صلاحياته؟",
                           "متى لا تلتزم الشركة بتصرّف المجلس مع الغير؟"]),
]


def main():
    # Guardrails: exactly the 5 provision groups, provision-covered articles only.
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
        "scope": "book4_section2_board_and_governance",
        "book": 4,
        "section_key": "board_and_governance",
        "section_title_ar": "مجلس الإدارة والحوكمة",
        "article_range": "67-83",
        "explicit_articles": sorted(EXPLICIT),
        "provision_groups": GROUPS,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": "arabic_reference_summary (data/articles/book4_provisions_067_083.json)",
        "purpose_ar": "طبقة بيانات قانونية عربية منظّمة لتمكين البحث والاسترجاع والاستدلال القانوني العربي فوق أحكام مجلس الإدارة والحوكمة المراجَعة داخليًا.",
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
