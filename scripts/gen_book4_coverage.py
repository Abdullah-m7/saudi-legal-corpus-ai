#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Book Four coverage matrix (model 1b) over ALL 80 articles 58–137.

This is INFRASTRUCTURE, not content: it enumerates every article number and marks
whether the source PDF explicitly covers it. It does NOT create provision records
and does NOT invent article titles or legal text for uncovered articles.

Writes: data/coverage/book4_coverage_matrix.json
"""

import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")

FIRST, LAST = 58, 137


def _articles_with_provision_records():
    """Scan any committed Book Four provision datasets and return the set of
    article numbers that already have a provision record. This keeps the coverage
    matrix's content_record_status a reproducible function of what exists."""
    covered = set()
    pattern = os.path.join(ROOT, "data", "articles", "book4_provisions_*.json")
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        for prov in doc.get("provisions", []):
            for n in prov.get("source_article_numbers", []):
                covered.add(n)
    return covered

# Articles explicitly rendered in inputs/bab4_source.pdf (from preflight inspection).
# Articles 134–135 are only REFERENCED (creditor-protection detail), not rendered,
# so they are treated as not_explicit_in_source.
# Section 3 reconciliation (owner Option 1, see BOOK4_SECTION3_SCOPE_DECISION.md):
# Articles 84 and 89 were over-listed at preflight but are NOT distinctly rendered in
# the source (89 absent entirely; 84 has no separate block — the powers block is
# tagged 85、87), so they are reclassified to not_explicit_in_source. Article 100
# also stays not_explicit_in_source (the source tags circulation as 101 only).
EXPLICIT = {
    58, 59, 60, 66, 67, 68, 71, 72, 75, 77, 85, 87, 92, 93, 99, 101, 102,
    108, 110, 113, 115, 117, 123, 124, 126, 127, 128, 129, 130, 132, 133,
}

# Short, non-inventive topic labels for explicitly covered articles (what the PDF
# addresses — NOT a legal rule statement). Absent => generic label.
EXPLICIT_NOTES = {
    58: "定义与责任 / التعريف والمسؤولية",
    59: "最低资本 / الحد الأدنى لرأس المال",
    60: "已发行/授权资本 / المصدر والمصرح به",
    66: "实物出资评估 / الحصص العينية",
    67: "董事会组成 / تكوين المجلس",
    68: "董事任期与解聘 / المدة والعزل",
    71: "董事披露与表决回避 / الإفصاح",
    72: "禁止向董事提供贷款 / حظر التمويل",
    75: "重大资产出售 / بيع الأصول الجوهرية",
    77: "董事会对第三人的权限 / صلاحيات المجلس تجاه الغير",
    85: "大会职权（OGM/EGM） / اختصاصات الجمعيتين",
    87: "普通大会职权 / اختصاصات الجمعية العادية",
    92: "法定人数与多数决 / النصاب والأغلبية",
    93: "EGM 法定人数/多数 / نصاب وأغلبية غير العادية",
    99: "决议撤销 / إبطال القرار",
    101: "传阅决议 / القرار بالتمرير",
    102: "公司检查（5%） / التفتيش على الشركة",
    108: "股份种类与类别 / أنواع وفئات الأسهم",
    110: "类别权利变更 / حقوق الفئة",
    113: "拖售权/随售权 / حق السحب والإلحاق",
    115: "违约未缴款 / التخلف عن الدفع",
    117: "债务工具与融资凭证（Sukuk） / أدوات الدين والصكوك",
    123: "储备金 / الاحتياطيات",
    124: "储备金动用 / استخدام الاحتياطي",
    126: "增资 / زيادة رأس المال",
    127: "增资方式 / طرق الزيادة",
    128: "优先认购权 / حق الأولوية في الاكتتاب",
    129: "取消优先认购权（EGM） / إلغاء الأولوية",
    130: "优先认购权转让 / التنازل عن حق الأولوية",
    132: "重大亏损 / الخسائر الفادحة",
    133: "减资 / تخفيض رأس المال",
}

SECTIONS = [
    (58, 66, "formation_and_capital", "التأسيس ورأس المال", "设立与资本"),
    (67, 83, "board_and_governance", "مجلس الإدارة والحوكمة", "董事会与治理"),
    (84, 102, "general_assemblies", "الجمعية العامة", "股东大会"),
    (103, 120, "shares_debt_and_financing", "الأسهم وأدوات الدين والصكوك", "股份、债务工具与融资凭证"),
    (121, 137, "finance_profits_and_capital_changes", "المالية والأرباح وتغيير رأس المال", "财务、利润与资本变更"),
]


def section_of(n):
    for lo, hi, key, ar, zh in SECTIONS:
        if lo <= n <= hi:
            return key, ar, zh
    return None, None, None


def main():
    provisioned = _articles_with_provision_records()
    rows = []
    for n in range(FIRST, LAST + 1):
        key, sec_ar, sec_zh = section_of(n)
        explicit = n in EXPLICIT
        if explicit:
            record_status = "provision_created" if n in provisioned else "pending"
        else:
            record_status = "no_record_until_source_available"
        rows.append({
            "book": 4,
            "article_number": n,
            "thematic_section": key,
            "thematic_section_ar": sec_ar,
            "thematic_section_zh": sec_zh,
            # Titles are NOT invented for uncovered articles (null unless explicit
            # in the source; even explicit rows keep title null here — provision
            # titles live on provision records, not the coverage matrix).
            "article_title_ar": None,
            "article_title_zh": None,
            "source_coverage_status": "explicit_in_source" if explicit else "not_explicit_in_source",
            "official_text_check": "needs_check" if explicit else "needs_official_text_check",
            "content_record_status": record_status,
            "note": EXPLICIT_NOTES.get(n, "" if explicit else "not rendered in source PDF; no invented content"),
        })

    explicit_nums = sorted(EXPLICIT)
    payload = {
        "coverage_id": "sa-companies-book4-coverage",
        "book": 4,
        "model": "model_1b_thematic_provisions",
        "scope_ar": "الباب الرابع: شركة المساهمة — أهم الأحكام — المواد 58–137",
        "scope_zh": "第四编：股份公司（JSC）— 核心条款（第五十八条 至 第一百三十七条）",
        "articles_range": "58-137",
        "total_articles": len(rows),
        "explicit_in_source_count": len(explicit_nums),
        "explicit_in_source": explicit_nums,
        "not_explicit_in_source_count": len(rows) - len(explicit_nums),
        "columns": ["book", "article_number", "thematic_section",
                    "source_coverage_status", "official_text_check",
                    "content_record_status", "note"],
        "rows": rows,
    }

    assert len(rows) == 80, len(rows)
    assert [r["article_number"] for r in rows] == list(range(58, 138))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT}: {len(rows)} rows, {len(explicit_nums)} explicit_in_source")


if __name__ == "__main__":
    main()
