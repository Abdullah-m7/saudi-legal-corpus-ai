#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Four — Section 1 (التأسيس ورأس المال / 设立与资本) provisions generator.

Model 1b: creates PROVISION records ONLY for the articles explicitly rendered in
the source PDF for this section — Articles 58, 59, 60, 66. Articles 61–65 are NOT
covered by the source and receive NO record (they remain needs_official_text_check
in the coverage matrix — no invented content).

Writes: data/articles/book4_provisions_058_066.json
Then re-runs the coverage generator so the matrix reflects provision_created.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json")

SECTION = "formation_and_capital"


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
        [58], "sa-companies-book4-prov001",
        "تعريف شركة المساهمة والمسؤولية",
        "股份公司的定义与责任",
        "شركة المساهمة شركة يؤسّسها شخص واحد أو أكثر، ينقسم رأس مالها إلى أسهم قابلة للتداول. "
        "والشركة وحدها مسؤولة عن ديونها والتزاماتها، وتقتصر مسؤولية المساهم على أداء قيمة الأسهم "
        "التي اكتتب فيها.",
        "股份公司（JSC）由一人或多人设立，其资本划分为可交易的股份。公司独立对其债务与义务负责，"
        "股东的责任仅限于缴付其所认购股份的价值。",
        "Article 58 — Definition and Liability of a Joint-Stock Company",
        ["شركة المساهمة", "المساهم", "السهم", "المسؤولية المحدودة"],
        ["股份公司", "股东", "股份", "有限责任"],
        "A JSC is formed by one or more persons; capital is divided into tradable shares; the "
        "company alone is liable for its debts and a shareholder's liability is limited to the "
        "value of the shares subscribed.",
        terminology=[
            {"ar": "شركة المساهمة", "zh": "股份公司"},
            {"ar": "المساهم", "zh": "股东"},
            {"ar": "السهم", "zh": "股份"},
        ],
        legal_notes=[
            "«السهم» تُترجم 股份 (وحدة رأس المال)؛ ويُستخدم 股票 عند قصد صك/شهادة السهم — والافتراض هنا 股份.",
            "股份公司（JSC）ترجمة وظيفية لشركة المساهمة السعودية؛ ليست تطابقاً مع 股份有限公司 في قانون الشركات الصيني.",
        ]),

    prov(
        [59], "sa-companies-book4-prov002",
        "الحد الأدنى لرأس المال",
        "最低资本",
        "يجب ألّا يقلّ رأس المال المصدر عن خمسمائة ألف (500,000) ريال، وألّا يقلّ المدفوع منه عند "
        "التأسيس عن ربعه.",
        "已发行资本不得低于五十万（500,000）里亚尔；设立时实缴部分不得低于已发行资本的四分之一。",
        "Article 59 — Minimum Capital",
        ["رأس المال المصدر", "الحد الأدنى", "المدفوع"],
        ["已发行资本", "最低资本", "实缴"],
        "Issued capital must be at least SAR 500,000, and the amount paid at incorporation at "
        "least one quarter of it.",
        terminology=[
            {"ar": "رأس المال المصدر", "zh": "已发行资本"},
        ],
        risk_flags=["minimum_capital_rule"]),

    prov(
        [60], "sa-companies-book4-prov003",
        "رأس المال المصدر والمصرح به",
        "已发行资本与授权资本",
        "يمثّل رأس المال المصدر الأسهم المكتتب بها. ويجوز أن يحدّد النظام الأساس رأس مال مصرَّحاً به. "
        "ولمجلس الإدارة زيادة رأس المال المصدر في حدود المصرَّح به، بشرط أن يكون رأس المال المصدر قد "
        "دُفع بالكامل.",
        "已发行资本代表已认购的股份。公司章程可规定授权资本。董事会可在授权资本限度内增加已发行资本，"
        "但以已发行资本已全额缴清为前提。",
        "Article 60 — Issued vs Authorized Capital",
        ["رأس المال المصدر", "رأس المال المصرح به", "مجلس الإدارة"],
        ["已发行资本", "授权资本", "董事会"],
        "Issued capital represents subscribed shares; the bylaws may set an authorized capital; "
        "the board may raise issued capital within the authorized limit only once issued capital "
        "is fully paid.",
        terminology=[
            {"ar": "رأس المال المصدر", "zh": "已发行资本"},
            {"ar": "رأس المال المصرح به", "zh": "授权资本"},
        ],
        risk_flags=["distinguish_issued_vs_authorized_capital"]),

    prov(
        [66], "sa-companies-book4-prov004",
        "تقييم الحصص العينية",
        "实物出资的评估",
        "تُقيَّم الحصص العينية بمعرفة مقيّم معتمد يبيّن قيمتها العادلة. ولا يشارك مقدّمو الحصص العينية "
        "في التصويت على قرار تقييمها. وإذا تقرّر تخفيض المقابل الممنوح لقاء الحصة العينية وجبت موافقة "
        "مقدّمها على التخفيض.",
        "实物出资须由认证评估师评估其公允价值。实物出资人不得参与对其评估决议的表决。若决定下调其"
        "实物出资的对价，须经该出资人同意。",
        "Article 66 — Valuation of In-kind Contributions",
        ["الحصص العينية", "مقيّم معتمد", "التقييم", "القيمة العادلة"],
        ["实物出资", "认证评估师", "评估", "公允价值"],
        "In-kind contributions are valued by a certified appraiser at fair value; the "
        "contributor may not vote on the valuation resolution; reducing the consideration "
        "requires the contributor's consent.",
        terminology=[
            {"ar": "الحصص العينية", "zh": "实物出资"},
            {"ar": "تقييم الحصص العينية", "zh": "实物出资评估"},
            {"ar": "مقيّم معتمد", "zh": "认证评估师"},
        ]),
]

ALLOWED = {58, 59, 60, 66}


def main():
    # Guardrails: no provision may map outside the explicit Section 1 set.
    for p in PROVISIONS:
        assert set(p["source_article_numbers"]) <= ALLOWED, p["provision_id"]
        assert not (set(p["source_article_numbers"]) & {61, 62, 63, 64, 65}), \
            f"{p['provision_id']} maps to an uncovered article"

    payload = {
        "book": 4,
        "book_title_ar": "الباب الرابع",
        "book_title_zh": "第四编",
        "section_key": SECTION,
        "section_title_ar": "التأسيس ورأس المال",
        "section_title_zh": "设立与资本",
        "article_range": "58-66",
        "model": "model_1b_thematic_provisions",
        "scope_note_ar": "أحكام مختارة من الباب الرابع (شركة المساهمة) للمواد المغطاة صراحةً في المصدر: 58، 59، 60، 66 — وليست ترجمة كاملة للقسم.",
        "scope_note_zh": "第四编（股份公司）设立与资本一节中，源文件明确涵盖的条款（第58、59、60、66条）择要；并非本节全文翻译。",
        "explicit_articles": [58, 59, 60, 66],
        "uncovered_articles": [61, 62, 63, 64, 65],
        "provisions": PROVISIONS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT} with {len(PROVISIONS)} provisions (articles 58,59,60,66)")

    # Refresh the coverage matrix so 58/59/60/66 -> provision_created.
    subprocess.run([sys.executable, os.path.join(HERE, "gen_book4_coverage.py")], check=True)


if __name__ == "__main__":
    main()
