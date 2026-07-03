#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Four — Section 5 (المالية والأرباح وتغيير رأس المال / 财务、利润与资本变更) provisions.

The source PDF and the coverage matrix AGREE on the Section 5 explicit set — the
articles the source distinctly renders as thematic provision blocks:
  123, 124, 126, 127, 128, 129, 130, 132, 133.

Model 1b: provision records only for that explicit set, grouped exactly as the source
renders them:
  [123, 124]         储备金 / الاحتياطيات (reserves)
  [126, 127]         增资 / زيادة رأس المال (capital increase)
  [128, 129, 130]    优先认购权及其转让 / حق الأولوية (pre-emption rights & transfer)
  [132]              重大亏损 / الخسائر الفادحة (major losses)
  [133]              减资 / تخفيض رأس المال (capital reduction)

No records for the uncovered Section-5 articles (121, 122, 125, 131, 134, 135, 136,
137). Articles 134 & 135 appear ONLY as a cross-reference in the capital-reduction
block ("债权人保护与异议细则见第134–135条"); they are not distinctly rendered and get
no record. No invented content — the Arabic/Chinese reconstruct the source's own
(garbled-Arabic / clean-Chinese) thematic blocks.

Writes: data/articles/book4_provisions_121_137.json
Then re-runs the coverage generator so the matrix marks 123,124,126,127,128,129,130,
132,133 as provision_created (all prior owner decisions — 84/89/100/110 uncovered —
are preserved).
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")

SECTION = "finance_profits_and_capital_changes"
ALLOWED = {123, 124, 126, 127, 128, 129, 130, 132, 133}
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]
GROUPS = [[123, 124], [126, 127], [128, 129, 130], [132], [133]]


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
        [123, 124], "sa-companies-book4-prov019",
        "الاحتياطيات: تكوينها واستخدامها",
        "储备金的提取与动用",
        "للنظام الأساس أن يقتطع نسبةً من صافي الأرباح لتكوين احتياطي مخصّص لأغراضٍ محددة، ولا "
        "يُستخدم الاحتياطي المخصّص إلا بقرارٍ من الجمعية العامة غير العادية؛ أما الاحتياطي غير "
        "المخصّص فتقرّر الجمعية العامة العادية استخدامه بناءً على اقتراح مجلس الإدارة.",
        "公司章程可提取净利润的一定比例，作为用于特定用途的专项储备；专项储备的使用须经非常大会"
        "（EGM）决议。非专项储备则由普通大会（OGM）依董事会的提议动用。",
        "Articles 123 & 124 — Formation and Use of Reserves",
        ["الاحتياطي المخصّص", "الاحتياطي غير المخصّص", "صافي الأرباح", "الجمعية غير العادية"],
        ["专项储备", "非专项储备", "净利润", "EGM"],
        "The bylaws may set aside a percentage of net profits to form a reserve for specific "
        "purposes; the earmarked reserve may be used only by an EGM decision, while the "
        "non-earmarked reserve is used by an OGM decision on the board's proposal.",
        terminology=[
            {"ar": "الاحتياطي المخصّص", "zh": "专项储备"},
            {"ar": "الاحتياطي غير المخصّص", "zh": "非专项储备"},
        ]),

    prov(
        [126, 127], "sa-companies-book4-prov020",
        "زيادة رأس المال: شروطها وطرقها",
        "增资的条件与方式",
        "تكون زيادة رأس المال بقرارٍ من الجمعية العامة غير العادية وبشرط أن يكون رأس المال المصدر "
        "قد دُفع بالكامل. وطرق الزيادة: إصدار أسهمٍ جديدة نقدية أو عينية، أو مقابل ديونٍ (تحويل "
        "الديون إلى أسهم)، أو رسملة الاحتياطي (أسهم منحة)، أو مقابل أدوات دينٍ أو صكوك.",
        "增资须经非常大会（EGM）决议，且已发行资本须已全额缴清；方式包括：发行新股（现金或实物）、"
        "以债权抵充（债转股）、资本化储备（红股），或对应债务工具/融资凭证发行。",
        "Articles 126 & 127 — Capital Increase: Conditions and Methods",
        ["زيادة رأس المال", "الجمعية غير العادية", "رسملة الاحتياطي", "أسهم منحة", "تحويل الديون"],
        ["增资", "EGM", "资本化储备", "红股", "债转股"],
        "A capital increase requires an EGM decision and full payment of the issued capital; "
        "methods include issuing new (cash or in-kind) shares, converting debt into shares, "
        "capitalising reserves (bonus shares), or against debt instruments/sukuk.",
        terminology=[
            {"ar": "رسملة الاحتياطي", "zh": "资本化储备"},
            {"ar": "أسهم منحة", "zh": "红股"},
        ],
        risk_flags=["capital_increase_egm_paid_up"]),

    prov(
        [128, 129, 130], "sa-companies-book4-prov021",
        "حق الأولوية في الاكتتاب والتنازل عنه وإلغاؤه",
        "优先认购权及其转让与取消",
        "للمساهمين وقت صدور قرار الزيادة حقُّ الأولوية في الاكتتاب بالأسهم النقدية الجديدة، ولهم بيع "
        "هذا الحق أو التنازل عنه. ويجوز للجمعية العامة غير العادية — إذا نصّ النظام الأساس على ذلك "
        "وبما يحقّق مصلحة الشركة — إلغاء حق الأولوية أو منحه لغير المساهمين.",
        "在增资决议作出时的股东，对新发行的现金股份享有优先认购权，并可出售或转让该权利。若公司章程"
        "有规定，非常大会（EGM）可为公司利益取消优先认购权，或将其授予非股东。",
        "Articles 128, 129 & 130 — Pre-emption Right, its Transfer and Cancellation",
        ["حق الأولوية", "الاكتتاب", "التنازل عن الحق", "إلغاء الأولوية", "الجمعية غير العادية"],
        ["优先认购权", "认购", "权利转让", "取消优先权", "EGM"],
        "Shareholders at the time of the increase decision have a pre-emption right over new cash "
        "shares and may sell or assign it; the EGM may — if the bylaws so provide and for the "
        "company's interest — cancel the pre-emption right or grant it to non-shareholders.",
        terminology=[
            {"ar": "حق الأولوية", "zh": "优先认购权"},
        ],
        risk_flags=["preemption_cancellation_minority_dilution"]),

    prov(
        [132], "sa-companies-book4-prov022",
        "الخسائر الفادحة (بلوغ الخسائر نصف رأس المال)",
        "重大亏损",
        "إذا بلغت الخسائر نصف رأس المال المصدر، وجب على مجلس الإدارة الإفصاح عنها خلال ستين (60) "
        "يوماً من علمه بها، ودعوة الجمعية العامة غير العادية للانعقاد خلال مئة وثمانين (180) يوماً "
        "للنظر في استمرار الشركة، أو معالجة الخسائر، أو حلّها.",
        "当亏损达到已发行资本的二分之一时，董事会须自知悉之日起六十（60）日内予以披露，并在一百八十"
        "（180）日内召集非常大会（EGM），审议公司存续、亏损处置或解散。",
        "Article 132 — Grave Losses (losses reaching half the capital)",
        ["الخسائر الفادحة", "نصف رأس المال", "60 يوماً", "180 يوماً", "استمرار الشركة"],
        ["重大亏损", "资本二分之一", "60日", "180日", "公司存续"],
        "If losses reach half the issued capital, the board must disclose within sixty (60) days "
        "of becoming aware and call an EGM within one hundred eighty (180) days to consider the "
        "company's continuation, remedying the losses, or dissolution.",
        terminology=[
            {"ar": "الخسائر الفادحة", "zh": "重大亏损"},
        ],
        risk_flags=["grave_losses_60_180_day_egm"]),

    prov(
        [133], "sa-companies-book4-prov023",
        "تخفيض رأس المال: طرقه",
        "减资的方式",
        "يكون تخفيض رأس المال بإحدى الطرق: إلغاء أسهم؛ أو تخفيض القيمة الاسمية (بإلغاء جزءٍ يعادل "
        "الخسائر، أو بردّ جزءٍ للمساهم، أو بإبراء الجزء غير المدفوع)؛ أو شراء الشركة أسهمها "
        "وإلغائها. وتفصيل حماية الدائنين وحقّ الاعتراض ورد في المادتين 134 و135 (غير مغطاتين في "
        "هذا المصدر).",
        "减资的方式包括：注销股份；下调面值（注销相当于亏损的部分、向股东返还一部分，或豁免未缴部"
        "分）；或由公司回购并注销股份。债权人保护与异议的细则见第134–135条（在本源文件中未涵盖）。",
        "Article 133 — Capital Reduction: Methods",
        ["تخفيض رأس المال", "إلغاء الأسهم", "القيمة الاسمية", "شراء الأسهم", "حماية الدائنين"],
        ["减资", "注销股份", "面值", "回购股份", "债权人保护"],
        "Capital reduction is by one of: cancelling shares; reducing the nominal value (cancelling "
        "a part equal to losses, refunding a part to shareholders, or waiving the unpaid part); or "
        "the company buying back and cancelling shares. Creditor-protection and objection detail "
        "is in Articles 134-135 (not covered in this source).",
        terminology=[
            {"ar": "تخفيض رأس المال", "zh": "减资"},
        ],
        legal_notes=[
            "المصدر يحيل تفاصيل حماية الدائنين والاعتراض إلى المادتين 134 و135 — وهما غير مغطاتين "
            "في هذا المصدر (تظهران كإحالةٍ فقط).",
        ],
        risk_flags=["capital_reduction_creditor_protection"]),
]


def main():
    # Guardrails: provisions map only to the explicit set, never to an uncovered
    # article (121,122,125,131,134,135,136,137) or outside 121-137.
    covered = set()
    for p in PROVISIONS:
        nums = set(p["source_article_numbers"])
        assert nums <= ALLOWED, "%s maps outside explicit set: %s" % (p["provision_id"], nums)
        assert not (nums & set(UNCOVERED)), "%s maps to an uncovered article" % p["provision_id"]
        assert all(121 <= n <= 137 for n in nums), "%s maps outside 121-137" % p["provision_id"]
        covered |= nums
    assert covered == ALLOWED, "provisions cover %s != explicit %s" % (sorted(covered), sorted(ALLOWED))
    assert [p["source_article_numbers"] for p in PROVISIONS] == GROUPS

    payload = {
        "book": 4,
        "book_title_ar": "الباب الرابع",
        "book_title_zh": "第四编",
        "section_key": SECTION,
        "section_title_ar": "المالية والأرباح وتغيير رأس المال",
        "section_title_zh": "财务、利润与资本变更",
        "article_range": "121-137",
        "model": "model_1b_thematic_provisions",
        "scope_note_ar": "أحكام مختارة من الباب الرابع (شركة المساهمة) للمواد المغطاة صراحةً في المصدر ضمن قسم المالية والأرباح وتغيير رأس المال: 123، 124، 126، 127، 128، 129، 130، 132، 133 — وليست ترجمة كاملة للقسم. (المواد 121، 122، 125، 131، 134، 135، 136، 137 غير مغطاة في المصدر).",
        "scope_note_zh": "第四编（股份公司）财务、利润与资本变更一节中，源文件明确涵盖的条款（第123、124、126、127、128、129、130、132、133条）择要；并非本节全文翻译。（第121、122、125、131、134、135、136、137条在源文件中未涵盖）。",
        "explicit_articles": sorted(ALLOWED),
        "uncovered_articles": UNCOVERED,
        "reconciliation_note": "Coverage matrix and source PDF agree on the Section 5 explicit set; no reclassification needed. Articles 134 & 135 appear only as a cross-reference in the capital-reduction block and remain not_explicit_in_source.",
        "provisions": PROVISIONS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s with %d provisions (articles 123,124,126,127,128,129,130,132,133)" % (OUT, len(PROVISIONS)))

    # Refresh the coverage matrix (marks the explicit set provision_created).
    subprocess.run([sys.executable, os.path.join(HERE, "gen_book4_coverage.py")], check=True)


if __name__ == "__main__":
    main()
