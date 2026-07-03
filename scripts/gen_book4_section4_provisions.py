#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Four — Section 4 (الأسهم وأدوات الدين والصكوك / 股份、债务工具与融资凭证) provisions.

Owner scope reconciliation (Option 1, see BOOK4_SECTION4_SCOPE_DECISION.md): the
explicit source-covered set is the articles the source PDF actually renders as distinct
provisions — 108, 113, 115, 117. Article 110 ("Amendment of Share-Associated Rights and
Obligations") is reclassified to not_explicit_in_source: the source only cross-references
it as （第110、89条）under Article 108's types/classes rule and renders no distinct block.

Model 1b: provision records only for the explicit set, as single-article blocks:
[108], [113], [115], [117]. No records for uncovered Section-4 articles
(103,104,105,106,107,109,110,111,112,114,116,118,119,120). No invented content; the
Arabic/Chinese below reconstruct the source's own (garbled-Arabic / clean-Chinese)
thematic blocks — the official English is NOT used as the basis for content.

Writes: data/articles/book4_provisions_103_120.json
Then re-runs the coverage generator so the matrix reflects the reconciliation and
provision_created for 108,113,115,117 (and 110 as not_explicit_in_source).
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json")

SECTION = "shares_debt_instruments_sukuk"
ALLOWED = {108, 113, 115, 117}
UNCOVERED = [103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120]
GROUPS = [[108], [113], [115], [117]]


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
        [108], "sa-companies-book4-prov015",
        "أنواع الأسهم وفئاتها",
        "股份的种类与类别",
        "للأسهم ثلاثة أنواع: عادية، وممتازة، وقابلة للاسترداد؛ ويجوز أن تُنشأ داخل كل نوع فئات "
        "بحقوق أو امتيازات أو قيود مختلفة. والأسهم من النوع أو الفئة ذاتها متساوية في الحقوق "
        "والالتزامات، ويتطلب تعديل حقوق فئة معينة — إضافةً إلى الجمعية غير العادية — موافقة جمعية "
        "خاصة بحملة تلك الفئة.",
        "股份分为三大种类：普通股、优先股、可赎回股；每一种类下可设立权利、特权或限制各不相同的类别。"
        "同一种类或类别的股份，其权利与义务相等；变更某一类别的权利，除经非常大会（EGM）外，还须经"
        "该类别持有人组成的专门大会批准。",
        "Article 108 — Types and Classes of Shares",
        ["أنواع الأسهم", "فئات الأسهم", "الأسهم الممتازة", "القابلة للاسترداد", "الجمعية الخاصة"],
        ["股份种类", "股份类别", "优先股", "可赎回股", "专门大会"],
        "Shares are of three types (ordinary, preferred, redeemable); classes with differing "
        "rights, privileges or restrictions may be created within each type. Shares of the same "
        "type/class carry equal rights and obligations; amending a class's rights requires — in "
        "addition to the EGM — approval of a special assembly of that class's holders.",
        terminology=[
            {"ar": "نوع", "zh": "种类"},
            {"ar": "فئة", "zh": "类别"},
        ],
        risk_flags=["share_type_vs_class_distinction"]),

    prov(
        [113], "sa-companies-book4-prov016",
        "البيع الإجباري: حق السحب وحق الإلحاق",
        "强制出售：拖售权与随售权",
        "دون إخلال بأحكام نظام السوق المالية، يجوز أن ينصّ النظام الأساس — بموافقة مساهمين يمثلون "
        "تسعين بالمئة (90%) على الأقل من حقوق التصويت — على: (أ) حق الأكثرية في إلزام الأقلية بقبول "
        "عرضٍ من مشترٍ حسن النية لشراء جميع الأسهم بالسعر والشروط نفسها (حق السحب Drag-along)؛ "
        "(ب) حق الأقلية في إلزام الأكثرية بأن تضمن بيع أسهم الأقلية بالشروط نفسها عند بيع الأكثرية "
        "(حق الإلحاق Tag-along).",
        "在不违反《资本市场法》的前提下，经代表至少百分之九十（90%）表决权的股东同意，公司章程可规定："
        "1. 多数股东有权强制少数股东接受善意买方按同一价格与条件收购全部股份（拖售权 Drag-along）；"
        "2. 少数股东有权在多数股东出售时，要求其保证按同一条件一并售出少数股东的股份（随售权 Tag-along）。",
        "Article 113 — Drag-along and Tag-along Rights",
        ["حق السحب", "حق الإلحاق", "90%", "نظام السوق المالية", "الأقلية"],
        ["拖售权", "随售权", "90%", "资本市场法", "少数股东"],
        "Without prejudice to the Capital Market Law, the bylaws may provide — with the consent of "
        "shareholders representing at least 90% of voting rights — for (a) the majority's right to "
        "compel the minority to accept a good-faith buyer's offer for all shares at the same price "
        "and terms (drag-along); and (b) the minority's right to require the majority to guarantee "
        "the sale of the minority's shares on the same terms when the majority sells (tag-along).",
        terminology=[
            {"ar": "حق السحب", "zh": "拖售权"},
            {"ar": "حق الإلحاق", "zh": "随售权"},
        ],
        legal_notes=[
            "يرتبط الحكم بنظام السوق المالية (CMA)؛ يُراجَع النص الرسمي عند التطبيق.",
        ],
        risk_flags=["drag_along_tag_along_90pct"]),

    prov(
        [115], "sa-companies-book4-prov017",
        "التخلف عن سداد قيمة الأسهم",
        "违约未缴款",
        "إذا تخلّف المساهم عن سداد قيمة سهمه في موعدها، جاز لمجلس الإدارة — بعد إبلاغه — بيع السهم في "
        "مزادٍ علني أو في السوق المالية، واستيفاء المستحق من حصيلة البيع مع ردّ الفائض إلى صاحبه "
        "(فإن لم تفِ الحصيلة رجعت الشركة عليه في سائر أمواله). وتُوقَف الحقوق المتصلة بالسهم — كالأرباح "
        "والتصويت — إلى حين تمام البيع أو السداد.",
        "股东逾期未缴清其股款的，董事会经通知后，可在公开拍卖或资本市场出售该违约股份，从出售所得中"
        "受偿并将余额返还股东（所得不足的，公司可就其其余财产追偿）；在出售或缴清之前，暂停该股份"
        "相关的权利（如分红权与表决权）。",
        "Article 115 — Non-Payment (Default on Share Calls)",
        ["التخلف عن الدفع", "بيع السهم", "المزاد", "إيقاف الحقوق", "استيفاء المستحق"],
        ["违约未缴款", "出售股份", "拍卖", "暂停权利", "受偿"],
        "If a shareholder defaults on paying the value of his share when due, the board — after "
        "notice — may sell the share by public auction or on the capital market, satisfy the amount "
        "owed from the proceeds and return the surplus (if proceeds fall short the company recovers "
        "from his other assets); the share's rights (dividends and voting) are suspended until the "
        "sale or payment is complete.",
        terminology=[
            {"ar": "التخلف عن الدفع", "zh": "违约未缴款"},
        ],
        risk_flags=["default_share_sale_rights_suspension"]),

    prov(
        [117], "sa-companies-book4-prov018",
        "إصدار أدوات الدين والصكوك التمويلية",
        "债务工具与融资凭证（Sukuk）的发行",
        "يجوز لشركة المساهمة أن تُصدر أدوات دينٍ أو صكوكاً تمويلية قابلة للتداول وفق أحكام نظام السوق "
        "المالية. ويُشترط لإصدار الأدوات أو الصكوك القابلة للتحويل إلى أسهم صدور قرارٍ من الجمعية "
        "العامة غير العادية (EGM) يحدّد الحد الأقصى للأسهم التي يجوز إصدارها مقابلها.",
        "股份公司可依《资本市场法》的规定，发行可交易的债务工具或融资凭证（Sukuk）。发行可转换为股份的"
        "债务工具或凭证的，须经非常大会（EGM）决议，并在决议中列明可据以发行的股份上限。",
        "Article 117 — Issuance of Debt Instruments and Financing Sukuk",
        ["أدوات الدين", "الصكوك التمويلية", "قابلة للتحويل", "الجمعية غير العادية", "نظام السوق المالية"],
        ["债务工具", "融资凭证", "可转股", "非常大会", "资本市场法"],
        "A joint-stock company may issue tradable debt instruments or financing sukuk under the "
        "Capital Market Law; issuing instruments/sukuk convertible into shares requires an EGM "
        "decision specifying the maximum number of shares that may be issued against them.",
        terminology=[
            {"ar": "الصكوك", "zh": "融资凭证"},
            {"ar": "أدوات الدين", "zh": "债务工具"},
        ],
        legal_notes=[
            "يرتبط الحكم بنظام السوق المالية (CMA)؛ يُراجَع النص الرسمي عند التطبيق.",
        ],
        risk_flags=["convertible_sukuk_egm_cap"]),
]


def main():
    # Guardrails: provisions map only to the reconciled explicit set {108,113,115,117},
    # never to an uncovered article, and never outside the section range 103-120.
    covered = set()
    for p in PROVISIONS:
        nums = set(p["source_article_numbers"])
        assert nums <= ALLOWED, "%s maps outside explicit set: %s" % (p["provision_id"], nums)
        assert not (nums & set(UNCOVERED)), "%s maps to an uncovered article" % p["provision_id"]
        assert all(103 <= n <= 120 for n in nums), "%s maps outside 103-120" % p["provision_id"]
        covered |= nums
    assert covered == ALLOWED, "provisions cover %s != explicit %s" % (sorted(covered), sorted(ALLOWED))
    assert [p["source_article_numbers"] for p in PROVISIONS] == GROUPS
    assert 110 not in covered, "Article 110 must NOT get a provision (reclassified uncovered)"

    payload = {
        "book": 4,
        "book_title_ar": "الباب الرابع",
        "book_title_zh": "第四编",
        "section_key": SECTION,
        "section_title_ar": "الأسهم وأدوات الدين والصكوك",
        "section_title_zh": "股份、债务工具与融资凭证",
        "article_range": "103-120",
        "model": "model_1b_thematic_provisions",
        "scope_note_ar": "أحكام مختارة من الباب الرابع (شركة المساهمة) للمواد المغطاة صراحةً في المصدر ضمن قسم الأسهم وأدوات الدين والصكوك بعد المطابقة مع المصدر: 108، 113، 115، 117 — وليست ترجمة كاملة للقسم. (المادة 110 وبقية مواد القسم غير مغطاة في المصدر).",
        "scope_note_zh": "第四编（股份公司）股份、债务工具与融资凭证一节中，经与源文件核对后明确涵盖的条款（第108、113、115、117条）择要；并非本节全文翻译。（第110条及本节其余条款在源文件中未涵盖）。",
        "explicit_articles": [108, 113, 115, 117],
        "uncovered_articles": UNCOVERED,
        "reconciliation_note": "Owner Option 1 (BOOK4_SECTION4_SCOPE_DECISION.md): reconciled to the source; Article 110 reclassified not_explicit_in_source (only cross-referenced （第110、89条）under Art. 108; no distinct block).",
        "provisions": PROVISIONS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s with %d provisions (articles 108,113,115,117)" % (OUT, len(PROVISIONS)))

    # Refresh the coverage matrix (reflects reconciliation + provision_created).
    subprocess.run([sys.executable, os.path.join(HERE, "gen_book4_coverage.py")], check=True)


if __name__ == "__main__":
    main()
