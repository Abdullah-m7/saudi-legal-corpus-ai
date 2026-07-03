#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Four — Section 2 (مجلس الإدارة والحوكمة / 董事会与治理) provisions generator.

Model 1b: creates PROVISION records ONLY for the articles explicitly rendered in
the source PDF for this section — Articles 67, 68, 71, 72, 75, 77. The source
groups Articles 67 & 68 into one thematic provision (composition & term), so this
section is 5 provisions over 6 explicit articles. The other Section-2 articles
(69, 70, 73, 74, 76, 78–83) are NOT rendered in the source and receive NO record
(they remain needs_official_text_check in the coverage matrix — no invented text).

The reference text is derived from the source PDF's own thematic content (the
Chinese layer extracts cleanly; the Arabic is reconstructed in MSA to the same
provision). Trust posture: internally_reviewed_summary / needs_check.

Writes: data/articles/book4_provisions_067_083.json
Then re-runs the coverage generator so the matrix reflects provision_created.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json")

SECTION = "board_and_governance"
ALLOWED = {67, 68, 71, 72, 75, 77}
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]


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
        [67, 68], "sa-companies-book4-prov005",
        "تكوين مجلس الإدارة ومدته وعزل أعضائه",
        "董事会的组成、任期与解聘",
        "يتكوّن مجلس الإدارة من ثلاثة (3) أعضاء على الأقل من ذوي الصفة الطبيعية. ولا تزيد مدة عضوية "
        "المجلس على أربع (4) سنوات، وتجوز إعادة انتخاب العضو. وللجمعية العامة العادية عزل أعضاء "
        "المجلس ولو نصّ النظام الأساس على غير ذلك.",
        "董事会至少由三（3）名自然人成员组成。董事任期不超过四（4）年，可连选连任。普通股东大会有权解聘"
        "董事，即使公司章程另有约定。",
        "Articles 67–68 — Board Composition and Term",
        ["مجلس الإدارة", "تكوين المجلس", "مدة العضوية", "عزل العضو", "الجمعية العامة العادية"],
        ["董事会", "组成", "任期", "解聘", "普通股东大会"],
        "The board has at least three natural-person members; a member's term is at most four "
        "years and is renewable; the ordinary general assembly may dismiss board members even if "
        "the bylaws provide otherwise.",
        terminology=[
            {"ar": "مجلس الإدارة", "zh": "董事会"},
            {"ar": "الجمعية العامة العادية", "zh": "普通股东大会"},
        ]),

    prov(
        [71], "sa-companies-book4-prov006",
        "الإفصاح عن المصالح وتجنّب التصويت ومسؤولية المجلس",
        "董事利益披露、表决回避与责任",
        "على عضو مجلس الإدارة الإفصاح فور علمه بأي مصلحة مباشرة أو غير مباشرة له في الأعمال والعقود "
        "التي تُبرم لحساب الشركة، ويُثبت ذلك في محضر الاجتماع، ولا يشارك في التصويت عليها في المجلس أو "
        "الجمعية العامة. ويُعفى من المسؤولية العضو الذي أثبت اعتراضه في المحضر، ولا يُعفى الغائب إلا "
        "إذا أثبت عدم علمه بالقرار أو تعذّر اعتراضه عليه بعد علمه به.",
        "董事一旦知悉其在为公司利益进行的业务或合同中拥有任何直接或间接利益，须即时披露并记入会议纪要，"
        "且不得在董事会或股东大会就该事项表决。在会议纪要中明确记录反对的董事免除责任；缺席的董事仅在"
        "证明其不知情、或知情后无法提出反对时方免除责任。",
        "Article 71 — Directors' Interest Disclosure and Abstention",
        ["الإفصاح", "تعارض المصالح", "محضر الاجتماع", "الامتناع عن التصويت", "المسؤولية"],
        ["利益披露", "利益冲突", "会议纪要", "表决回避", "责任"],
        "A director must immediately disclose any direct or indirect interest, record it in the "
        "minutes, and abstain from voting on it in the board or the general assembly; a director "
        "who records dissent is exempt from liability, and an absent director only if unaware or "
        "unable to object.",
        terminology=[
            {"ar": "الإفصاح", "zh": "披露"},
            {"ar": "محضر الاجتماع", "zh": "会议纪要"},
        ]),

    prov(
        [72], "sa-companies-book4-prov007",
        "حظر تمويل أعضاء مجلس الإدارة",
        "禁止向董事提供贷款或担保",
        "لا يجوز للشركة أن تقدّم قرضاً لأيٍّ من أعضاء مجلس إدارتها، ولا أن تضمن أو تكفل قرضاً يعقده "
        "العضو مع الغير. ويمتدّ الحظر إلى أقارب العضو (الآباء والأمهات والأجداد وإن علوا، والأولاد وإن "
        "نزلوا، والأزواج)، وكل عقد يخالف ذلك باطل. ويُستثنى من الحظر البنوك وشركات التمويل وفق شروط "
        "تعاملها العامة، وبرامج تحفيز العاملين المعتمدة.",
        "公司不得向其任何董事提供贷款，亦不得为该董事向第三方的借款作保或提供担保；该禁止延伸至其亲属"
        "（父母及以上尊亲属、子女及以下卑亲属、配偶）；违反该禁止的合同无效。例外：银行及融资公司按其"
        "对公众适用的一般条件办理的交易，以及经批准的员工激励计划。",
        "Article 72 — Prohibition on Financing Directors",
        ["حظر القروض", "أعضاء المجلس", "الكفالة", "الأقارب", "بطلان العقد"],
        ["禁止贷款", "董事", "担保", "亲属", "合同无效"],
        "The company may not lend to, or guarantee third-party borrowing by, any of its "
        "directors; the prohibition extends to a director's relatives (ascendants, descendants, "
        "spouses) and a contract breaching it is void; banks/finance companies on general public "
        "terms and approved employee incentive programs are excepted.",
        terminology=[
            {"ar": "حظر القروض", "zh": "禁止贷款"},
            {"ar": "الأقارب", "zh": "亲属"},
        ],
        risk_flags=["related_party_financing_prohibition"]),

    prov(
        [75], "sa-companies-book4-prov008",
        "بيع الأصول الجوهرية وموافقة الجمعية العامة",
        "重大资产出售与股东大会批准",
        "يجب موافقة الجمعية العامة على بيع أصول تزيد قيمتها على خمسين بالمئة (50%) من إجمالي أصول "
        "الشركة، سواء تمّ ذلك بصفقة واحدة أو بعدّة صفقات. وتُحتسب هذه النسبة تراكمياً اعتباراً من أول "
        "صفقة خلال الاثني عشر (12) شهراً السابقة.",
        "出售价值超过公司总资产百分之五十（50%）的资产，无论通过一次或多次交易进行，均须经股东大会批准；"
        "该比例自此前十二（12）个月内的首笔交易起累计计算。",
        "Article 75 — Sale of Material Assets",
        ["بيع الأصول", "الأصول الجوهرية", "موافقة الجمعية العامة", "50%", "الاحتساب التراكمي"],
        ["资产出售", "重大资产", "股东大会批准", "50%", "累计计算"],
        "Selling assets worth more than 50% of the company's total assets — whether in one or "
        "several transactions — requires general-assembly approval; the ratio is computed "
        "cumulatively from the first transaction within the preceding twelve months.",
        terminology=[
            {"ar": "بيع الأصول الجوهرية", "zh": "重大资产出售"},
        ],
        risk_flags=["material_asset_disposal_threshold"]),

    prov(
        [77], "sa-companies-book4-prov009",
        "صلاحيات مجلس الإدارة تجاه الغير",
        "董事会对第三人的权限",
        "فيما عدا ما يدخل في اختصاص الجمعية العامة على وجه الحصر، يملك مجلس الإدارة أوسع الصلاحيات "
        "اللازمة لتحقيق أغراض الشركة. وتلتزم الشركة بما يجريه المجلس من تصرّفات باسمها ولو تجاوزت حدود "
        "صلاحياته، إلا إذا كان من تعامل معه سيّئ النية أو كان يعلم بتجاوز التصرّف لتلك الحدود.",
        "除专属于股东大会的事项外，董事会享有为实现公司宗旨所需的最广泛权限。公司受董事会以公司名义所为"
        "行为的约束，即使该行为超出其权限；但交易相对人为恶意、或明知该行为越权的除外。",
        "Article 77 — Board Powers Toward Third Parties",
        ["صلاحيات المجلس", "اختصاص الجمعية العامة", "التزام الشركة", "سوء النية", "تجاوز الصلاحيات"],
        ["董事会权限", "股东大会专属", "公司约束", "恶意", "越权"],
        "Except for matters reserved exclusively to the general assembly, the board holds the "
        "widest powers to achieve the company's objectives; the company is bound by acts done in "
        "its name even beyond the board's powers, unless the counterparty acted in bad faith or "
        "knew of the excess.",
        terminology=[
            {"ar": "اختصاص الجمعية العامة", "zh": "股东大会专属职权"},
        ]),
]


def main():
    # Guardrails: no provision may map outside the explicit Section 2 set, and
    # never onto an uncovered article (69,70,73,74,76,78–83) or another section.
    covered = set()
    for p in PROVISIONS:
        nums = set(p["source_article_numbers"])
        assert nums <= ALLOWED, "%s maps outside explicit set: %s" % (p["provision_id"], nums)
        assert not (nums & set(UNCOVERED)), "%s maps to an uncovered article" % p["provision_id"]
        assert all(67 <= n <= 83 for n in nums), "%s maps outside 67-83" % p["provision_id"]
        covered |= nums
    assert covered == ALLOWED, "provisions cover %s != explicit %s" % (sorted(covered), sorted(ALLOWED))

    payload = {
        "book": 4,
        "book_title_ar": "الباب الرابع",
        "book_title_zh": "第四编",
        "section_key": SECTION,
        "section_title_ar": "مجلس الإدارة والحوكمة",
        "section_title_zh": "董事会与治理",
        "article_range": "67-83",
        "model": "model_1b_thematic_provisions",
        "scope_note_ar": "أحكام مختارة من الباب الرابع (شركة المساهمة) للمواد المغطاة صراحةً في المصدر ضمن قسم مجلس الإدارة والحوكمة: 67، 68، 71، 72، 75، 77 — وليست ترجمة كاملة للقسم.",
        "scope_note_zh": "第四编（股份公司）董事会与治理一节中，源文件明确涵盖的条款（第67、68、71、72、75、77条）择要；并非本节全文翻译。",
        "explicit_articles": [67, 68, 71, 72, 75, 77],
        "uncovered_articles": UNCOVERED,
        "provisions": PROVISIONS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s with %d provisions (articles 67,68,71,72,75,77)" % (OUT, len(PROVISIONS)))

    # Refresh the coverage matrix so 67,68,71,72,75,77 -> provision_created.
    subprocess.run([sys.executable, os.path.join(HERE, "gen_book4_coverage.py")], check=True)


if __name__ == "__main__":
    main()
