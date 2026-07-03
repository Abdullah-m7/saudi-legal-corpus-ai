#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Four — Section 3 (الجمعية العامة / 股东大会) provisions generator.

Owner scope reconciliation (Option 1, see BOOK4_SECTION3_SCOPE_DECISION.md): the
explicit source-covered set is the articles the source PDF actually renders —
85, 87, 92, 93, 99, 101, 102. Articles 84 and 89 were reclassified to
not_explicit_in_source (89 absent in the source; 84 has no distinct block), and
Article 100 stays not_explicit_in_source (the source tags circulation as 101 only).

Model 1b: provision records only for the explicit set, grouped by the source's
thematic blocks: [85,87], [92,93], [99], [101], [102]. No records for uncovered
Section-3 articles (84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100). No invented
content.

Writes: data/articles/book4_provisions_084_102.json
Then re-runs the coverage generator so the matrix reflects the reconciliation and
provision_created.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json")

SECTION = "general_assemblies"
ALLOWED = {85, 87, 92, 93, 99, 101, 102}
UNCOVERED = [84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100]
GROUPS = [[85, 87], [92, 93], [99], [101], [102]]


def prov(n_list, pid, title_ar, title_zh, ar_summary, zh, retrieval_title,
         kw_ar, kw_zh, summary_en, terminology=None, legal_notes=None,
         risk_flags=None):
    return {
        "book": 4,
        "provision_id": pid,
        "source_article_numbers": n_list,
        "thematic_section": SECTION,
        "provision_title_ar": title_ar,
        "provision_title_zh": title_zh,
        "arabic_reference_summary": ar_summary,
        "chinese_translation": zh,
        "translation_mode": "internally_reviewed_summary",
        "coverage_status": "covered",
        "legal_notes": legal_notes or [],
        "terminology": terminology or [],
        "risk_flags": risk_flags or [],
        "source": {
            "input_pdf": "inputs/bab4_source.pdf",
            "page_hint": None,
            "official_text_check": "needs_check",
            "source_coverage_status": "explicit_in_source",
        },
        "llm": {
            "chunk_id": pid,
            "retrieval_title": retrieval_title,
            "keywords_ar": kw_ar,
            "keywords_zh": kw_zh,
            "summary_en": summary_en,
        },
    }


PROVISIONS = [
    prov(
        [85, 87], "sa-companies-book4-prov010",
        "اختصاصات الجمعية العامة العادية وغير العادية",
        "普通大会与非常大会的职权",
        "تختصّ الجمعية العامة العادية بانتخاب أعضاء مجلس الإدارة وعزلهم، وتعيين مراجع الحسابات، "
        "والنظر في القوائم المالية والتقارير، وتوزيع الأرباح، وتكوين الاحتياطيات. وتختصّ الجمعية "
        "العامة غير العادية بتعديل النظام الأساس (دون أن تحرم المساهمين من حقوقهم الأساسية، ويلزم "
        "إجماعهم لزيادة الأعباء المالية)، وبالبتّ في استمرار الشركة أو حلّها، وبالموافقة على شراء "
        "الشركة أسهمها.",
        "普通大会（OGM）职权：选举与解聘董事、任命审计师、审议财务报表与报告、分配利润、提取储备。"
        "非常大会（EGM）职权：修改公司章程（不得剥夺股东的基本权利，增加财务负担须经全体股东同意）、"
        "决定公司存续或解散、批准公司回购自身股份。",
        "Articles 85 & 87 — Powers of the Extraordinary and Ordinary General Assemblies",
        ["الجمعية العامة العادية", "الجمعية العامة غير العادية", "الاختصاصات",
         "تعديل النظام الأساس", "حلّ الشركة"],
        ["普通大会", "非常大会", "职权", "修改章程", "公司解散"],
        "The ordinary general assembly elects/dismisses directors, appoints the auditor, reviews "
        "the financial statements and reports, distributes profits and forms reserves; the "
        "extraordinary general assembly amends the bylaws (without stripping shareholders' basic "
        "rights; unanimous consent to increase financial burdens), decides the company's "
        "continuation or dissolution, and approves the company's buy-back of its own shares.",
        terminology=[
            {"ar": "الجمعية العامة العادية", "zh": "普通大会"},
            {"ar": "الجمعية العامة غير العادية", "zh": "非常大会"},
        ]),

    prov(
        [92, 93], "sa-companies-book4-prov011",
        "النصاب والأغلبية في الجمعيتين العادية وغير العادية",
        "普通大会与非常大会的法定人数与表决多数",
        "في الجمعية العامة العادية يكون النصاب في الاجتماع الأول ربع الأسهم (ويجوز أن يرفعه النظام "
        "الأساس بما لا يتجاوز النصف)، ويصحّ الاجتماع الثاني أياً كان عدد الحاضرين؛ وتصدر قراراتها "
        "بأغلبية الأصوات الممثَّلة. وفي الجمعية العامة غير العادية يكون النصاب في الاجتماع الأول نصف "
        "الأسهم (ويجوز رفعه بما لا يتجاوز الثلثين)، وفي الثاني ربعها، ويصحّ الثالث أياً كان عدد "
        "الحاضرين؛ وتصدر قراراتها بأغلبية ثلثي الأصوات الممثَّلة، فإذا تعلّق القرار بزيادة رأس المال "
        "أو تخفيضه أو إطالة مدة الشركة أو حلّها قبل أجلها أو اندماجها أو تقسيمها لزمت أغلبية ثلاثة "
        "أرباع الأصوات.",
        "普通大会（OGM）法定人数：首次会议须代表四分之一股份（章程可上调，但不超过二分之一）；第二次会议"
        "无论出席多少均有效；决议以出席所代表表决权的多数通过。非常大会（EGM）法定人数：首次须二分之一"
        "（章程可上调，但不超过三分之二），第二次须四分之一，第三次无论出席多少均有效；决议以所代表表决权"
        "的三分之二通过；若涉及增减资本、延长公司期限、提前解散、合并或分立，则须四分之三多数。",
        "Articles 92 & 93 — Quorum and Voting Majorities of the OGM and EGM",
        ["النصاب", "الأغلبية", "الجمعية العادية", "الجمعية غير العادية", "ثلاثة أرباع"],
        ["法定人数", "表决多数", "普通大会", "非常大会", "四分之三"],
        "OGM quorum: one-quarter at the first meeting (bylaws may raise it, not above one-half), "
        "the second meeting is valid regardless of attendance, decisions by majority of "
        "represented votes. EGM quorum: one-half first (may be raised, not above two-thirds), "
        "one-quarter second, third valid regardless; decisions by two-thirds of represented "
        "votes, rising to three-quarters for capital increase/decrease, term extension, early "
        "dissolution, merger or division.",
        terminology=[
            {"ar": "النصاب", "zh": "法定人数"},
            {"ar": "الأغلبية", "zh": "表决多数"},
        ],
        risk_flags=["ogm_egm_quorum_majority"]),

    prov(
        [99], "sa-companies-book4-prov012",
        "إبطال قرارات الجمعية العامة",
        "撤销股东大会决议",
        "للمساهم الذي اعترض على القرار في الاجتماع أو تغيّب عنه لعذر مشروع أن يطلب إبطال القرار "
        "المخالف للنظام أو النظام الأساس. ولا تُسمع الدعوى بعد مضيّ تسعين (90) يوماً من تاريخ صدور "
        "القرار، ويجب أن يظلّ المدّعي محتفظاً بصفة المساهم طوال الدعوى، وذلك دون إخلال بحقوق الغير "
        "حسن النية.",
        "在会上提出异议、或有正当理由缺席的股东，可请求撤销违反本法或公司章程的决议；自决议作出之日起满"
        "九十（90）日后不予受理；原告须在诉讼全程保持股东身份；不影响善意第三人的权利。",
        "Article 99 — Objection to and Annulment of Assembly Decisions",
        ["إبطال القرار", "الاعتراض", "تسعون يوماً", "صفة المساهم", "حسن النية"],
        ["撤销决议", "异议", "90日", "股东身份", "善意第三人"],
        "A shareholder who objected at the meeting or was absent for a legitimate reason may seek "
        "annulment of a decision that breaches the Law or the bylaws; the action is time-barred "
        "90 days after the decision; the claimant must retain shareholder status throughout; "
        "without prejudice to good-faith third parties.",
        terminology=[
            {"ar": "إبطال القرار", "zh": "撤销决议"},
        ],
        risk_flags=["decision_annulment_90_day_limit"]),

    prov(
        [101], "sa-companies-book4-prov013",
        "إصدار القرار بالتمرير",
        "以传阅方式作出决议",
        "في الشركات غير المدرجة، تصدر قرارات الجمعية العامة العادية بالتمرير بأغلبية الأصوات، وتصدر "
        "قرارات الجمعية العامة غير العادية بأغلبية لا تقلّ عن خمسة وسبعين بالمئة (75%) من الأصوات، "
        "ما لم يشترط النظام الأساس نسبةً أعلى فيُعمَل بها.",
        "非上市公司中，普通大会事项可以传阅方式以表决权多数通过，非常大会事项须以至少百分之七十五（75%）"
        "的表决权通过；公司章程要求更高比例的，从其规定。",
        "Article 101 — Issuing a Decision by Circulation",
        ["القرار بالتمرير", "الشركات غير المدرجة", "75%", "الجمعية غير العادية"],
        ["传阅决议", "非上市公司", "75%", "非常大会"],
        "In non-listed companies, ordinary general assembly decisions may be issued by "
        "circulation by a majority of votes, and extraordinary general assembly decisions by at "
        "least 75% of votes, unless the bylaws require a higher percentage.",
        terminology=[
            {"ar": "القرار بالتمرير", "zh": "传阅决议"},
        ],
        legal_notes=[
            "المصدر (الباب الرابع) يجمع حكم القرار بالتمرير تحت المادة 101؛ والترقيم الرسمي يوزّع "
            "الإصدار بالتمرير على المادتين 100 و101 — والمادة 100 تبقى غير مغطاة في هذا المصدر.",
        ]),

    prov(
        [102], "sa-companies-book4-prov014",
        "طلب التفتيش على الشركة",
        "申请对公司进行检查",
        "للمساهمين الذين يملكون خمسة بالمئة (5%) من رأس المال أن يطلبوا من الجهة القضائية المختصة "
        "التفتيش على الشركة عند وجود ما يدعو إلى الاشتباه في تصرّفات أعضاء مجلس الإدارة أو مراجع "
        "الحسابات، وللجهة القضائية أن تُحمِّل الطالب نفقات التفتيش.",
        "持有公司资本百分之五（5%）的股东，在有理由怀疑董事会成员或审计师行为的情形下，可向主管司法机关"
        "申请对公司进行检查；主管司法机关可判令由申请人承担检查费用。",
        "Article 102 — Request for Inspection of the Company",
        ["التفتيش على الشركة", "5%", "الجهة القضائية", "نفقات التفتيش"],
        ["公司检查", "5%", "司法机关", "检查费用"],
        "Shareholders holding 5% of capital may petition the competent judicial authority to "
        "inspect the company where directors' or the auditor's conduct is reasonably suspect; "
        "the court may charge the inspection costs to the applicant.",
        terminology=[
            {"ar": "التفتيش على الشركة", "zh": "公司检查"},
        ],
        risk_flags=["minority_5pct_inspection_right"]),
]


def main():
    # Guardrails: provisions map only to the reconciled explicit set, never to an
    # uncovered article (84,86,88,89,90,91,94,95,96,97,98,100) or another section.
    covered = set()
    for p in PROVISIONS:
        nums = set(p["source_article_numbers"])
        assert nums <= ALLOWED, "%s maps outside explicit set: %s" % (p["provision_id"], nums)
        assert not (nums & set(UNCOVERED)), "%s maps to an uncovered article" % p["provision_id"]
        assert all(84 <= n <= 102 for n in nums), "%s maps outside 84-102" % p["provision_id"]
        covered |= nums
    assert covered == ALLOWED, "provisions cover %s != explicit %s" % (sorted(covered), sorted(ALLOWED))
    assert [p["source_article_numbers"] for p in PROVISIONS] == GROUPS

    payload = {
        "book": 4,
        "book_title_ar": "الباب الرابع",
        "book_title_zh": "第四编",
        "section_key": SECTION,
        "section_title_ar": "الجمعية العامة",
        "section_title_zh": "股东大会",
        "article_range": "84-102",
        "model": "model_1b_thematic_provisions",
        "scope_note_ar": "أحكام مختارة من الباب الرابع (شركة المساهمة) للمواد المغطاة صراحةً في المصدر ضمن قسم الجمعية العامة بعد المطابقة مع المصدر: 85، 87، 92، 93، 99، 101، 102 — وليست ترجمة كاملة للقسم. (المواد 84 و89 و100 غير مغطاة في المصدر).",
        "scope_note_zh": "第四编（股份公司）股东大会一节中，经与源文件核对后明确涵盖的条款（第85、87、92、93、99、101、102条）择要；并非本节全文翻译。（第84、89、100条在源文件中未涵盖）。",
        "explicit_articles": [85, 87, 92, 93, 99, 101, 102],
        "uncovered_articles": UNCOVERED,
        "reconciliation_note": "Owner Option 1 (BOOK4_SECTION3_SCOPE_DECISION.md): reconciled to the source; 84, 89, 100 remain not_explicit_in_source.",
        "provisions": PROVISIONS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s with %d provisions (articles 85,87,92,93,99,101,102)" % (OUT, len(PROVISIONS)))

    # Refresh the coverage matrix (reflects reconciliation + provision_created).
    subprocess.run([sys.executable, os.path.join(HERE, "gen_book4_coverage.py")], check=True)


if __name__ == "__main__":
    main()
