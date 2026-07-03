#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authoring generator for the Book Three canonical article dataset.

Book Three / الباب الثالث — شركة التوصية البسيطة / 两合公司（有限合伙性质）—
Articles 51–57. Writes the canonical JSON and the coverage matrix:

    data/articles/book3_articles_051_057.json
    data/coverage/book3_coverage_matrix.json

The JSONL derivative is produced by ``scripts/build_book3_jsonl.py``.

Editorial policy (same trust posture as Books One & Two)
--------------------------------------------------------
* Chinese text is taken from the attached reference PDF (clean layer), with minor
  QA harmonisation (contiguous 商人资格; explicit 有限合伙人 subjects).
* Arabic reference summaries are manually reconstructed Modern Standard Arabic
  (the PDF Arabic layer extracts garbled). Concise summaries, NOT statutory text.
* Nothing here is an official translation. translation_mode =
  "internally_reviewed_summary"; every article is flagged needs_check.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book3_articles_051_057.json")
COVERAGE_OUT = os.path.join(ROOT, "data", "coverage", "book3_coverage_matrix.json")

SECTIONS = {
    "def_setup": ("الفصلان الأول والثاني: التعريف والتأسيس", "第一、二节 定义与设立"),
    "partners_decisions": ("الفصل الثالث: الشركاء والقرارات", "第三节 合伙人与决议"),
    "transfer_termination": ("التنازل عن الحصص والانتهاء", "份额转让与终止"),
}

COVERAGE_NOTES = {
    51: "两合公司定义：普通合伙人无限连带、有限合伙人以出资额为限、有限合伙人不取得商人资格",
    52: "设立协议必备条款（援引第三十六条）",
    53: "有限合伙人权限：知情权；不得参与对外管理（否则连带）；对内管理与表见责任",
    54: "股东大会（可选，依设立协议）",
    55: "合伙人决议：修改协议须普通合伙人一致+有限合伙人资本多数；有限合伙人不得请求解散或表决经理任免",
    56: "份额转让（5款）",
    57: "终止事由：有限合伙人死亡/禁治产/无力偿债/破产清算/退伙不终止公司",
}


def art(number, sec, title_ar, title_zh, ar_summary, zh, retrieval_title,
        kw_ar, kw_zh, summary_en, legal_notes=None, terminology=None,
        risk_flags=None):
    section_ar, section_zh = SECTIONS[sec]
    return {
        "book": 3,
        "article_number": number,
        "article_title_ar": title_ar,
        "article_title_zh": title_zh,
        "section_ar": section_ar,
        "section_zh": section_zh,
        "arabic_reference_summary": ar_summary,
        "chinese_translation": zh,
        "translation_mode": "internally_reviewed_summary",
        "coverage_status": "covered",
        "legal_notes": legal_notes or [],
        "terminology": terminology or [],
        "risk_flags": risk_flags or [],
        "source": {
            "input_pdf": "inputs/bab3_source.pdf",
            "page_hint": None,
            "official_text_check": "needs_check",
        },
        "llm": {
            "chunk_id": f"sa-companies-book3-art{number:03d}",
            "retrieval_title": retrieval_title,
            "keywords_ar": kw_ar,
            "keywords_zh": kw_zh,
            "summary_en": summary_en,
        },
    }


ARTICLES = [
    art(51, "def_setup",
        "تعريف شركة التوصية البسيطة",
        "两合公司的定义",
        "شركة التوصية البسيطة شركة تتكوّن من فئتين من الشركاء: (1) شريك متضامن واحد على الأقل "
        "(طبيعي أو اعتباري) مسؤول شخصياً وبالتضامن في جميع أمواله عن ديون الشركة والتزاماتها؛ "
        "(2) وشريك موصٍ واحد على الأقل لا يُسأل عن ديون الشركة والتزاماتها إلا في حدود حصته في رأس "
        "المال. ولا يكتسب الشريك الموصي صفة التاجر. ويخضع الشركاء المتضامنون لأحكام الشركاء في شركة "
        "التضامن، وتُطبَّق أحكام شركة التضامن على التوصية البسيطة فيما لم يرد به نص خاص في هذا الباب.",
        "第五十一条（两合公司的定义）：由两类合伙人组成的公司：（一）至少一名普通合伙人（自然人或"
        "法人），以其全部个人财产对公司债务及义务承担无限连带责任；（二）至少一名有限合伙人，仅以"
        "其在公司资本中的出资额为限对公司债务及义务承担责任。有限合伙人不取得商人资格。普通合伙人"
        "适用无限公司（普通合伙）中合伙人的规定；本编未作特别规定的事项，适用无限公司（普通合伙）"
        "的规定。",
        "Article 51 — Definition of a Limited Partnership",
        ["شركة التوصية البسيطة", "الشريك المتضامن", "الشريك الموصي", "صفة التاجر"],
        ["两合公司", "普通合伙人", "有限合伙人", "商人资格"],
        "A limited partnership (توصية بسيطة) has general partners (unlimited joint liability) and "
        "limited partners (liable only up to their capital contribution); a limited partner does "
        "not acquire merchant status; general-partnership rules apply by default.",
        legal_notes=[
            "الشخصية الاعتبارية: شركة التوصية البسيطة السعودية كيان قائم بذاته وليست مطابقة لكيانات الشراكة المحدودة (有限合伙企业) في القانون الصيني؛ الترجمة 两合公司（有限合伙性质）وظيفية.",
            "الشريك الموصي لا يكتسب صفة التاجر (有限合伙人不取得商人资格) ومسؤوليته محدودة بمقدار حصته.",
        ],
        terminology=[
            {"ar": "شركة التوصية البسيطة", "zh": "两合公司（有限合伙性质）"},
            {"ar": "الشريك المتضامن", "zh": "普通合伙人（无限责任合伙人）"},
            {"ar": "الشريك الموصي", "zh": "有限合伙人"},
        ],
        risk_flags=["limited_partner_liability_cap"]),

    art(52, "def_setup",
        "بيانات عقد التأسيس",
        "设立协议必备条款",
        "يجب أن يشتمل عقد التأسيس بخاصة على البيانات نفسها المقرَّرة لشركة التضامن (المادة 36): "
        "أسماء الشركاء وبياناتهم، واسم الشركة، ومركزها الرئيس، وغرضها، ورأس المال وتوزيعه والحصص "
        "ومواعيد استحقاقها، ومدتها (إن وُجدت)، والإدارة، وقرارات الشركاء والنصاب، وتوزيع الأرباح "
        "والخسائر، وبدء السنة المالية وانتهائها، والانتهاء، وأي أحكام أخرى لا تتعارض مع النظام.",
        "第五十二条（设立协议必备条款）：设立协议尤其须载明与无限公司（普通合伙）相同的事项"
        "（第三十六条）：合伙人姓名及信息、公司名称、总部、经营范围、资本及其分配与各出资及到期日、"
        "公司期限（如有）、管理机制、合伙人决议及法定人数、损益分配、会计年度起止、解散事由，以及"
        "其他不违反本法的条款。",
        "Article 52 — Mandatory Contents of the Deed",
        ["عقد التأسيس", "البيانات الواجبة"],
        ["设立协议", "必备条款"],
        "The deed must contain the same particulars required for a general partnership (Art. 36)."),

    art(53, "partners_decisions",
        "صلاحيات الشريك الموصي",
        "有限合伙人的权限",
        "(1) للشريك الموصي — أو لمن يفوّضه — أن يطّلع مرّتين خلال السنة المالية على سير الأعمال، "
        "ويفحص السجلات والوثائق، ويستخرج بياناً موجزاً عن الحالة المالية. (2) لا يجوز له التدخّل في "
        "أعمال الإدارة الخارجية ولو بموجب توكيل، فإن تدخّل كان مسؤولاً شخصياً وبالتضامن في جميع أمواله "
        "عن ديون الشركة والتزاماتها المترتبة على ما باشره. ومع ذلك يجوز له الاشتراك في أعمال الإدارة "
        "الداخلية وفق ما يخصّه العقد، ولا يرتّب ذلك التزاماً في ذمّته، إلا إذا كانت أعماله تدعو الغير "
        "إلى الاعتقاد بأنه شريك متضامن، فيُعدّ — في مواجهة ذلك الغير — مسؤولاً شخصياً وبالتضامن.",
        "第五十三条（有限合伙人的权限）：1. 有限合伙人或其受托人有权在每个会计年度内两次查阅业务"
        "进展、检查账簿与文件、摘录财务状况简报。2. 有限合伙人不得参与或干预对外管理行为，即使持有"
        "授权委托书；若参与，则须就其行为所致公司债务及义务，以其全部财产承担个人连带责任。但其可依"
        "设立协议参与对内管理行为，此不使其负担义务；除非其行为足以使第三人相信其为普通合伙人——"
        "此时对该第三人承担个人连带责任（表见/表象责任）。",
        "Article 53 — Powers of the Limited Partner",
        ["الشريك الموصي", "الإدارة الخارجية", "الإدارة الداخلية", "المسؤولية الظاهرة"],
        ["有限合伙人", "对外管理", "对内管理", "表见责任"],
        "A limited partner has inspection rights but may not take part in external management "
        "(else personal joint liability); internal management per the deed is allowed unless it "
        "leads third parties to believe he is a general partner (apparent authority).",
        legal_notes=[
            "المعيار موضوعي (المسؤولية الظاهرة / 表见责任): العبرة بالمظهر الذي يدعو الغير للاعتقاد بأن الموصي شريك متضامن، لا بحسن نية الغير بمعناه الذاتي.",
        ],
        terminology=[
            {"ar": "أعمال الإدارة الخارجية", "zh": "对外管理行为"},
            {"ar": "أعمال الإدارة الداخلية", "zh": "对内管理行为"},
            {"ar": "إيهام الغير بصفة التضامن", "zh": "表见普通合伙（表象责任）"},
        ]),

    art(54, "partners_decisions",
        "الجمعية العامة",
        "股东大会",
        "يجوز للشركاء المتضامنين والموصين الاتفاق في عقد التأسيس على أن يكون للشركة جمعية عامة، "
        "وتحديد اختصاصاتها وإجراءات انعقادها.",
        "第五十四条（股东大会）：普通合伙人与有限合伙人可在设立协议中约定设立公司股东大会，并确定"
        "其职权与召开程序。",
        "Article 54 — General Meeting",
        ["الجمعية العامة", "عقد التأسيس"],
        ["股东大会", "设立协议"],
        "Partners may agree in the deed to establish a general meeting and set its powers and "
        "convening procedures."),

    art(55, "partners_decisions",
        "قرارات الشركاء",
        "合伙人决议",
        "ما لم ينص العقد على غير ذلك: (أ) قرارات تعديل عقد التأسيس: بإجماع الشركاء المتضامنين "
        "وموافقة مالكي أغلبية رأس المال الخاص بالشركاء الموصين. (ب) القرارات الأخرى: بموافقة الأغلبية "
        "العددية لآراء الشركاء المتضامنين. ولا يجوز للشريك الموصي طلب حلّ الشركة، ولا الاشتراك في "
        "التصويت على تعيين مديرها أو عزله.",
        "第五十五条（合伙人决议）：设立协议另有约定的除外：（一）修改设立协议的决议：须经全体普通"
        "合伙人一致同意，并经占有限合伙人资本多数的出资人同意；（二）其他决议：以普通合伙人的人数"
        "多数通过。有限合伙人无权请求解散公司，亦无权参与经理任免的表决。",
        "Article 55 — Partners' Resolutions",
        ["قرارات الشركاء", "تعديل العقد", "أغلبية رأس المال"],
        ["合伙人决议", "修改协议", "资本多数"],
        "Amending the deed needs unanimity of general partners plus a capital-majority of limited "
        "partners; other resolutions by numeric majority of general partners; a limited partner "
        "cannot seek dissolution or vote on manager appointment/removal."),

    art(56, "transfer_termination",
        "التنازل عن الحصص",
        "份额转让",
        "(1) للشريك الموصي أن يتنازل عن حصّته كلها أو بعضها لأيٍّ من الشركاء الآخرين. (2) وتنازله "
        "للغير يكون بموافقة جميع المتضامنين ومالكي أغلبية رأس مال الموصين، ما لم ينص العقد على غير "
        "ذلك. (3) وتنازل الشريك المتضامن للموصي أو للغير تسري عليه الفقرة (2). (4) وإذا لم يكن "
        "المتنازِل قد أوفى بحصّته، كان المتنازَل له مسؤولاً عن تقديمها. (5) وإدخال شريك متضامن أو موصٍ "
        "يكون بموافقة جميع المتضامنين دون حاجة لموافقة الموصين، ما لم ينص العقد على غير ذلك.",
        "第五十六条（份额转让）：1. 有限合伙人可将其全部或部分份额转让给其他任何合伙人。2. 有限"
        "合伙人向第三人转让，须经全体普通合伙人及占有限合伙人资本多数者同意，协议另有约定的除外。"
        "3. 普通合伙人向有限合伙人或第三人转让，适用第2款。4. 有限合伙人转让前未实缴出资的，由受让"
        "人承担实缴义务。5. 引入新的普通合伙人或有限合伙人，须经全体普通合伙人同意，无需有限合伙人"
        "同意，协议另有约定的除外。",
        "Article 56 — Transfer of Quotas",
        ["التنازل عن الحصص", "موافقة المتضامنين", "المتنازَل له"],
        ["份额转让", "普通合伙人同意", "受让人"],
        "Quota-transfer rules: limited partner to other partners freely; to third parties needs "
        "all general partners + capital-majority of limited partners; unpaid contributions pass "
        "to the transferee; admitting new partners needs all general partners.",
        terminology=[
            {"ar": "المتنازِل / المتنازَل له", "zh": "转让人 / 受让人"},
        ]),

    art(57, "transfer_termination",
        "حالات الانتهاء",
        "终止事由",
        "لا تنتهي شركة التوصية البسيطة بوفاة أيٍّ من الشركاء الموصين، ولا بالحجر عليه، ولا بإعساره، "
        "ولا بافتتاح أيٍّ من إجراءات التصفية تجاهه وفقاً لنظام الإفلاس، ولا بانسحابه، ما لم ينص عقد "
        "التأسيس على ذلك.",
        "第五十七条（终止事由）：两合公司不因任何有限合伙人的死亡、被宣告禁治产、无力偿债、依"
        "《破产法》对其启动清算程序或退伙而终止，设立协议另有约定的除外。",
        "Article 57 — Grounds of Termination",
        ["الانتهاء", "الإعسار", "الشريك الموصي"],
        ["终止", "无力偿债", "有限合伙人"],
        "The limited partnership does not terminate on a limited partner's death, interdiction, "
        "insolvency, bankruptcy-liquidation, or withdrawal, unless the deed so provides.",
        legal_notes=[
            "«إعسار» تُرجمت 无力偿债 (العجز عن سداد الديون المستحقة)، وليست 民事破产 (لا وجود لنظام إفلاس مدني مستقل في النظام السعودي 1439هـ) ولا 资不抵债 (زيادة الخصوم على الأصول).",
        ]),
]


def main():
    assert len(ARTICLES) == 7, f"expected 7 articles, got {len(ARTICLES)}"
    nums = [a["article_number"] for a in ARTICLES]
    assert nums == list(range(51, 58)), f"article numbers not 51..57: {nums}"

    payload = {
        "book": 3,
        "book_title_ar": "الباب الثالث",
        "book_title_zh": "第三编",
        "scope_ar": "الباب الثالث كاملًا: شركة التوصية البسيطة — المواد 51–57",
        "scope_zh": "第三编（全）：两合公司（有限合伙性质）（第五十一条 至 第五十七条）",
        "articles": ARTICLES,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT} with {len(ARTICLES)} articles")

    rows = []
    for a in ARTICLES:
        n = a["article_number"]
        rows.append({
            "article_number": n,
            "article_title_ar": a["article_title_ar"],
            "article_title_zh": a["article_title_zh"],
            "coverage_status": a["coverage_status"],
            "expression_mode": "concise_summary",
            "note": COVERAGE_NOTES.get(n, ""),
        })
    coverage = {
        "coverage_id": "sa-companies-book3-coverage",
        "book": 3,
        "scope_ar": payload["scope_ar"],
        "scope_zh": payload["scope_zh"],
        "articles_range": "51-57",
        "total_articles": len(rows),
        "expanded_after_review": [],
        "columns": ["article_number", "article_title_ar", "article_title_zh",
                    "coverage_status", "expression_mode", "note"],
        "rows": rows,
    }
    os.makedirs(os.path.dirname(COVERAGE_OUT), exist_ok=True)
    with open(COVERAGE_OUT, "w", encoding="utf-8") as f:
        json.dump(coverage, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {COVERAGE_OUT} with {len(rows)} rows")


if __name__ == "__main__":
    main()
