#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authoring generator for the Book Two canonical article dataset.

Book Two / الباب الثاني — شركة التضامن / 无限公司（普通合伙性质）— Articles 35–50.
Writes the canonical JSON and the coverage matrix:

    data/articles/book2_articles_035_050.json
    data/coverage/book2_coverage_matrix.json

The JSONL derivative is produced by ``scripts/build_book2_jsonl.py``.

Editorial policy (identical trust posture to Book One)
-----------------------------------------------------
* Chinese text is taken from the attached reference PDF (clean layer), with
  minor QA harmonisation (e.g. 无限连带责任 in the definition article).
* Arabic reference summaries are manually reconstructed Modern Standard Arabic
  (the PDF Arabic layer extracts garbled). They are concise reference summaries,
  NOT the official statutory text.
* Nothing here is an official translation. translation_mode is
  "internally_reviewed_summary" and every article is flagged needs_check.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "articles", "book2_articles_035_050.json")
COVERAGE_OUT = os.path.join(ROOT, "data", "coverage", "book2_coverage_matrix.json")

SECTIONS = {
    "def_setup": ("الفصلان الأول والثاني: التعريف والتأسيس", "第一、二节 定义与设立"),
    "management": ("الفصل الثالث: إدارة شركة التضامن", "第三节 无限公司的管理"),
    "shares_partners": ("الفصل الرابع: الحصص والشركاء", "第四节 无限公司的份额与合伙人"),
    "termination": ("الفصل الخامس: انتهاء شركة التضامن", "第五节 无限公司的终止与解散"),
}

COVERAGE_NOTES = {
    35: "无限公司定义：全部个人财产、无限连带责任、商人资格",
    36: "设立协议必备条款",
    37: "管理权限；恶意相对人例外",
    38: "合伙人决议；修改设立协议须全体一致",
    39: "对经理的禁止行为（担保、借款、处分不动产等）",
    40: "竞业禁止",
    41: "非执行合伙人的知情权（每年两次查阅）",
    42: "解聘经理（三种情形）",
    43: "经理辞任（60日通知）",
    44: "份额不得证券化；转让限制与登记公示",
    45: "加入、退伙、除名与转让的责任（30日债权人异议）",
    46: "退伙与除名程序（60日通知；司法除名/解散）",
    47: "损益份额；亏损由以后年度利润补足",
    48: "对合伙人财产的执行；先诉抗辩权；向其他合伙人追偿",
    49: "份额估值；认证评估师；公允价值",
    50: "存续原则；未成年/禁业继承人转两合公司；仅余一人90日宽限",
}


def art(number, sec, title_ar, title_zh, ar_summary, zh, retrieval_title,
        kw_ar, kw_zh, summary_en, legal_notes=None, terminology=None,
        risk_flags=None):
    section_ar, section_zh = SECTIONS[sec]
    return {
        "book": 2,
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
            "input_pdf": "inputs/bab2_source.pdf",
            "page_hint": None,
            "official_text_check": "needs_check",
        },
        "llm": {
            "chunk_id": f"sa-companies-book2-art{number:03d}",
            "retrieval_title": retrieval_title,
            "keywords_ar": kw_ar,
            "keywords_zh": kw_zh,
            "summary_en": summary_en,
        },
    }


ARTICLES = [
    art(35, "def_setup",
        "تعريف شركة التضامن",
        "无限公司的定义",
        "شركة التضامن شركة يؤسّسها شخصان أو أكثر من ذوي الصفة الطبيعية أو الاعتبارية، يكونون فيها "
        "مسؤولين شخصياً وبالتضامن في جميع أموالهم عن ديون الشركة والتزاماتها، ويكتسب الشريك فيها صفة "
        "التاجر.",
        "第三十五条（无限公司的定义）：由两名或两名以上自然人或法人设立的公司，其合伙人以其全部"
        "个人财产对公司债务及义务承担无限连带责任；合伙人因此取得商人资格（商事主体地位）。",
        "Article 35 — Definition of a General Partnership",
        ["شركة التضامن", "المسؤولية التضامنية", "صفة التاجر"],
        ["无限公司", "无限连带责任", "商人资格"],
        "A general partnership (شركة التضامن) is formed by two or more persons who are "
        "personally and jointly liable with all their assets for the company's debts; each "
        "partner acquires merchant status.",
        legal_notes=[
            "شركة التضامن كيان ذو شخصية اعتبارية مستقلة في النظام السعودي؛ الترجمة الوظيفية 无限公司（普通合伙性质）لا تعني تطابقها مع الشراكة العامة (普通合伙企业) في القانون الصيني.",
        ],
        terminology=[
            {"ar": "شركة التضامن", "zh": "无限公司（普通合伙性质）"},
            {"ar": "المسؤولية التضامنية غير المحدودة", "zh": "无限连带责任"},
            {"ar": "صفة التاجر", "zh": "商人资格"},
        ],
        risk_flags=["unlimited_personal_liability"]),

    art(36, "def_setup",
        "بيانات عقد التأسيس",
        "设立协议必备条款",
        "يجب أن يشتمل عقد التأسيس بخاصة على: أسماء الشركاء وبياناتهم، واسم الشركة، ومركزها الرئيس، "
        "وغرضها، ورأس المال وتوزيعه على الشركاء وتعريفاً كافياً بالحصص ومواعيد استحقاقها، ومدة الشركة "
        "(إن وُجدت)، والإدارة، وقرارات الشركاء والنصاب اللازم لها، وكيفية توزيع الأرباح والخسائر، وبدء "
        "السنة المالية وانتهائها، وانتهاء الشركة، وأي أحكام أخرى لا تتعارض مع النظام.",
        "第三十六条（设立协议必备条款）：设立协议尤其须载明：合伙人姓名及信息、公司名称、总部、"
        "经营范围、资本及其在合伙人间的分配与各出资的充分说明及到期日、公司期限（如有）、管理机制、"
        "合伙人决议及其法定人数、损益分配方式、会计年度的起止、公司解散事由，以及其他不违反本法的"
        "条款。",
        "Article 36 — Mandatory Contents of the Deed",
        ["عقد التأسيس", "رأس المال", "مدة الشركة"],
        ["设立协议", "资本", "公司期限"],
        "Mandatory contents of the deed of incorporation: partners, name, head office, purpose, "
        "capital and quotas, term, management, quorum, profit/loss allocation, financial year, "
        "and dissolution."),

    art(37, "management",
        "صلاحيات الإدارة",
        "管理权限",
        "يتولّى الإدارة الشركاء، ويجوز الاتفاق على تعيين مدير أو أكثر من الشركاء أو من غيرهم. وإذا "
        "تعدّد المديرون دون تحديد اختصاص كلٍّ منهم ودون منع الانفراد، جاز لكلٍّ منهم الانفراد بأعمال "
        "الإدارة، ولباقي المديرين الاعتراض قبل أن يُبرم العمل ملزِماً في مواجهة الغير، وحينئذٍ تكون "
        "العبرة بأغلبية المديرين، فإن تساوت الآراء رُفع الأمر إلى الشركاء. وتلتزم الشركة بكل عمل يجريه "
        "المدير باسمها وفي حدود غرضها، إلا إذا كان من تعامل معه سيّئ النية.",
        "第三十七条（管理权限）：公司由合伙人管理，亦可约定从合伙人或外部人员中任命一名或多名经理。"
        "若经理为多人且未划分各自权限、亦未禁止单独行事，则每名经理均可单独执行管理事务；其余经理"
        "有权在该行为对第三人生效之前提出异议，此时以经理的多数意见为准，意见相等时提交合伙人决定。"
        "公司在其经营范围内受经理以公司名义所作行为的约束，除非交易相对人为恶意。",
        "Article 37 — Management Powers",
        ["الإدارة", "المدير", "سوء النية"],
        ["管理", "经理", "恶意"],
        "Management by partners or appointed managers; multiple managers may act individually "
        "subject to objection and majority; the company is bound by acts within its purpose "
        "unless the counterparty acted in bad faith."),

    art(38, "management",
        "قرارات الشركاء",
        "合伙人决议",
        "تصدر قرارات الشركاء بالأغلبية العددية، إلا إذا كان القرار متعلقاً بتعديل عقد التأسيس فيجب أن "
        "يصدر بإجماع الشركاء، ما لم ينص العقد على غير ذلك.",
        "第三十八条（合伙人决议）：以人数多数通过；但涉及修改设立协议的决议须经全体合伙人一致同意，"
        "协议另有约定的除外。",
        "Article 38 — Partners' Resolutions",
        ["قرارات الشركاء", "الإجماع", "تعديل العقد"],
        ["合伙人决议", "一致同意", "修改协议"],
        "Partners' resolutions pass by numeric majority; amending the deed requires unanimity "
        "unless the deed provides otherwise."),

    art(39, "management",
        "الأعمال المحظورة على المدير",
        "对经理的禁止行为",
        "يُحظر على المدير مباشرة ما يتجاوز غرض الشركة إلا بقرار من الشركاء أو نص صريح، وبخاصة: إنشاء "
        "الفروع أو إغلاقها، التبرّعات (عدا العينية المعتادة اليسيرة)، كفالة الشركة للغير، الصلح على "
        "حقوق الشركة، بيع عقارات الشركة أو رهنها (إلا إذا كان البيع من غرضها)، بيع المحل التجاري "
        "(المتجر) أو رهنه، والاقتراض نيابةً عن الشركة.",
        "第三十九条（对经理的禁止行为）：非经合伙人决议或协议明文授权，经理不得从事超出公司经营"
        "范围的行为，尤其：设立或关闭分公司、捐赠（惯常小额捐赠除外）、以公司为他人提供担保、就"
        "公司权利进行和解、出售或抵押公司不动产（属经营范围内的出售除外）、出售或抵押营业场所"
        "（商号），以及代表公司借款。",
        "Article 39 — Acts Prohibited to the Manager",
        ["الأعمال المحظورة", "الكفالة", "الاقتراض"],
        ["禁止行为", "担保", "借款"],
        "Without a partners' resolution or express authority, the manager may not act beyond "
        "the company's purpose: branches, donations, guaranteeing third parties, settlement, "
        "sale/mortgage of real estate or the business, or borrowing."),

    art(40, "management",
        "منافسة الشركة",
        "竞业禁止",
        "لا يجوز للشريك — دون موافقة باقي الشركاء — أن يمارس لحسابه أو لحساب الغير نشاطاً من نوع نشاط "
        "الشركة، ولا أن يكون شريكاً أو مديراً أو عضو مجلس إدارة في شركة منافِسة، ولا مالكاً لنسبة "
        "مؤثِّرة في شركة تمارس النشاط ذاته. وإذا أخلّ بذلك، جاز للشركة أن تطلب عدّ تصرّفاته لحسابها، "
        "فضلاً عن التعويض.",
        "第四十条（竞业禁止）：未经其余合伙人同意，合伙人不得为自己或他人从事与公司同类的业务，"
        "不得在竞争公司中担任合伙人、经理或董事，亦不得持有从事同类业务公司的重大比例份额。违反的，"
        "公司可请求将其相关行为视为为公司所为，并另行请求赔偿。",
        "Article 40 — Non-competition",
        ["منافسة الشركة", "حظر المنافسة", "التعويض"],
        ["竞业禁止", "同类业务", "赔偿"],
        "Without the other partners' consent, a partner may not compete with the company; the "
        "company may treat the partner's competing acts as its own and claim damages."),

    art(41, "management",
        "صلاحيات الشريك غير المدير",
        "非执行合伙人的权利",
        "لا يجوز له التدخّل في الإدارة، وله — أو لمن يفوّضه — أن يطّلع مرّتين خلال السنة المالية على "
        "سير الأعمال، ويفحص السجلات والوثائق، ويستخرج بياناً موجزاً عن الحالة المالية، ويقدّم الآراء. "
        "وكل اتفاق على غير ذلك يُعدّ كأن لم يكن.",
        "第四十一条（非执行合伙人的权利）：不得干预管理；但其本人或受托人有权在每个会计年度内两次"
        "查阅业务进展、检查账簿与文件、摘录财务状况简报并提出意见。任何相反约定视为不存在。",
        "Article 41 — Rights of a Non-managing Partner",
        ["الشريك غير المدير", "الاطلاع", "السنة المالية"],
        ["非执行合伙人", "查阅权", "会计年度"],
        "A non-managing partner may not interfere in management but has an inalienable right to "
        "inspect the books and financial position twice per financial year."),

    art(42, "management",
        "عزل المدير",
        "解聘经理",
        "إذا كان المدير شريكاً معيّناً في عقد التأسيس فلا يُعزل إلا بإجماع باقي الشركاء؛ وإذا كان "
        "معيّناً في عقد مستقل فيُعزل بالأغلبية العددية. وإذا كان من غير الشركاء (في العقد أو منفصلاً) "
        "فيُعزل بالأغلبية العددية. ويجوز عزله بحكم قضائي نهائي. ولا يترتّب على العزل حلُّ الشركة ما لم "
        "ينص العقد على ذلك.",
        "第四十二条（解聘经理）：经理为设立协议指定的合伙人的，非经其余合伙人一致同意不得解聘；"
        "经理由独立合同指定的，以人数多数解聘；经理为非合伙人的（无论在协议或独立合同中指定），"
        "亦以人数多数解聘。经法院终审判决可强制解聘。解聘不导致公司解散，协议另有约定的除外。",
        "Article 42 — Dismissal of the Manager",
        ["عزل المدير", "الإجماع", "الأغلبية العددية"],
        ["解聘经理", "一致同意", "人数多数"],
        "Dismissal thresholds by how the manager was appointed (deed-partner: unanimity; "
        "otherwise majority); court may compel dismissal; dismissal does not dissolve the "
        "company by default."),

    art(43, "management",
        "اعتزال المدير",
        "经理辞任",
        "للمدير — شريكاً كان أو غير شريك — أن يعتزل بإبلاغ الشركاء كتابةً قبل نفاذه بـ (60) يوماً على "
        "الأقل، ما لم ينص العقد على غير ذلك، وإلا كان مسؤولاً عن تعويض الأضرار المترتبة على الاعتزال. "
        "ولا يترتّب على الاعتزال حلُّ الشركة ما لم ينص العقد على ذلك.",
        "第四十三条（经理辞任）：经理（无论是否为合伙人）可辞任，但须在生效前至少六十（60）日"
        "书面通知合伙人，协议另有约定的除外；否则须就其辞任所致损害承担赔偿。辞任不导致公司解散，"
        "协议另有约定的除外。",
        "Article 43 — Resignation of the Manager",
        ["اعتزال المدير", "الإخطار", "التعويض"],
        ["辞任", "60日通知", "赔偿"],
        "A manager may resign on at least 60 days' written notice; otherwise liable for "
        "resulting damages; resignation does not dissolve the company by default."),

    art(44, "shares_partners",
        "حصص الشركاء والتنازل عنها",
        "合伙份额及其转让",
        "لا يجوز أن تكون الحصص ممثَّلة في صكوك قابلة للتداول. ولا يجوز للشريك التنازل عن حصّته كلها أو "
        "بعضها إلا بمراعاة قيود العقد أو بموافقة باقي الشركاء، ويُعدّ باطلاً كل اتفاق على التنازل دون "
        "ذلك، ويجب قيد التنازل وشهره لدى السجل التجاري. ويجوز للشريك التنازل للغير عن الحقوق المالية "
        "المتّصلة بحصّته، ولا يكون لهذا التنازل أثر إلا بين طرفيه.",
        "第四十四条（合伙份额及其转让）：份额不得以可流通证券形式表现。合伙人转让其全部或部分份额，"
        "须遵守协议限制或经其余合伙人同意；违反的转让约定无效。转让须在商业登记（CR）登记并公示。"
        "合伙人可向第三人转让其份额所附的财产性权利，但该转让仅在转让双方之间发生效力。",
        "Article 44 — Quotas and Their Transfer",
        ["الحصص", "التنازل عن الحصة", "القيد والشهر"],
        ["份额", "份额转让", "登记公示"],
        "Quotas cannot be represented by negotiable instruments; transfer requires deed "
        "compliance or partners' consent and CR registration; financial rights may be assigned "
        "but only between the parties.",
        terminology=[
            {"ar": "التنازل عن الحصة", "zh": "份额转让"},
        ]),

    art(45, "shares_partners",
        "الانضمام والانسحاب والإخراج والتنازل",
        "加入、退伙、除名与转让",
        "(1) الشريك المنضمّ بحصة جديدة يكون مسؤولاً شخصياً وبالتضامن عن ديون الشركة السابقة واللاحقة "
        "لانضمامه، ويجوز إعفاؤه من السابقة بإجماع الشركاء، ويسري الإعفاء في مواجهة الدائنين من تاريخ "
        "قيده وشهره. (2) الشريك المنسحب أو المُخرَج لا يُسأل عن الديون اللاحقة لقيد وشهر انسحابه، "
        "ويظلّ مسؤولاً عن السابقة ما لم يُعفَ بموافقة باقي الشركاء والدائنين. (3) عند التنازل يكون "
        "المتنازَل له مسؤولاً قِبَل الدائنين عن الديون السابقة واللاحقة، ولا يُعفى المتنازِل إلا إذا لم "
        "يعترض الدائنون على الإعفاء خلال (30) يوماً من إبلاغهم؛ وفي حال الاعتراض يظلّ المتنازِل "
        "مسؤولاً بالتضامن عن الديون السابقة للتنازل.",
        "第四十五条（加入、退伙、除名与转让）：1. 以新出资加入的新合伙人，对其加入之前及之后的"
        "公司债务承担个人连带责任；经全体合伙人一致同意可免除其对加入前债务的责任，该免除自登记"
        "公示之日起对债权人生效。2. 退伙或被除名的合伙人，对其退伙登记公示之后产生的债务不负责任，"
        "但对此前债务仍负责任，经其余合伙人及债权人同意免除的除外。3. 转让份额时，受让人对债权人就"
        "转让前后的债务负责；转让人仅在债权人自被通知之日起三十（30）日内未对免除其责任提出异议时"
        "方获免除；债权人提出异议的，转让人对其转让前的债务仍负连带责任。",
        "Article 45 — Admission, Withdrawal, Expulsion, Transfer",
        ["الانضمام", "الانسحاب", "الإخراج", "المسؤولية عن الديون"],
        ["加入", "退伙", "除名", "债务责任"],
        "Liability rules for incoming partners (pre/post debts), withdrawing/expelled partners, "
        "and transfers, including the 30-day creditor-objection window for releasing the "
        "transferor.",
        terminology=[
            {"ar": "المتنازِل / المتنازَل له", "zh": "转让人 / 受让人"},
        ]),

    art(46, "shares_partners",
        "إجراءات الانسحاب والإخراج",
        "退伙与除名程序",
        "ما لم ينص العقد على غير ذلك، للشريك الانسحاب بإرادته المنفردة بإبلاغ باقي الشركاء قبل (60) "
        "يوماً على الأقل. ويجوز الاتفاق على إجراءات الإخراج، وإلا جاز للأغلبية العددية طلب إخراج شريك "
        "من الجهة القضائية لأسباب مشروعة، وتبقى الشركة قائمة بين الباقين. ويجب قيد وشهر الانسحاب أو "
        "الإخراج، ولا يسري في مواجهة الغير إلا بعد ذلك. وللجهة القضائية — بطلب شريك — حلّ الشركة إذا "
        "تعذّر استمرارها.",
        "第四十六条（退伙与除名程序）：协议另有约定外，合伙人可依单方意愿退伙，但须至少提前六十"
        "（60）日通知其余合伙人。可约定除名程序；未约定的，人数多数可因正当理由向主管司法机关申请"
        "将某合伙人除名，公司在其余合伙人之间存续。退伙或除名须登记公示，非经登记公示不得对抗第三人。"
        "经合伙人申请，主管司法机关在公司无法继续存续时可裁定解散。",
        "Article 46 — Withdrawal and Expulsion Procedure",
        ["الانسحاب", "الإخراج", "القيد والشهر"],
        ["退伙", "除名", "登记公示"],
        "Withdrawal on 60 days' notice; expulsion by agreement or by the court for lawful cause; "
        "registration/publication is required to bind third parties; court may dissolve if the "
        "company cannot continue."),

    art(47, "shares_partners",
        "نصيب الشريك في الأرباح والخسائر",
        "合伙人的损益份额",
        "تُحدّد الأرباح والخسائر ونصيب كل شريك عند نهاية السنة المالية من واقع قوائم مالية معتمدة، "
        "ويصير الشريك دائناً للشركة بنصيبه في الأرباح بمجرّد تحديده. ويُكمَّل ما نقص من رأس المال بسبب "
        "الخسائر من أرباح السنوات التالية، وفيما عدا ذلك لا يُلزَم الشريك بتكملة النقص في حصّته إلا "
        "بموافقته.",
        "第四十七条（合伙人的损益份额）：利润、亏损及各合伙人的份额于会计年度末依经认可的财务报表"
        "确定；份额一经确定，合伙人即就其利润份额成为公司的债权人。因亏损而减少的资本，由以后年度"
        "的利润予以补足；除此之外，非经合伙人同意，不得强制其补足因亏损而减少的出资份额。",
        "Article 47 — Share in Profits and Losses",
        ["الأرباح والخسائر", "تكملة رأس المال", "قوائم مالية"],
        ["损益份额", "补足资本", "财务报表"],
        "Profits/losses fixed at year-end from approved statements; capital reduced by losses is "
        "replenished from future profits; a partner is not otherwise forced to top up without "
        "consent."),

    art(48, "shares_partners",
        "التنفيذ على أموال الشريك",
        "对合伙人财产的执行",
        "لا يجوز مطالبة الشريك بأداء دين الشركة من ماله إلا بعد ثبوت الدين في ذمّتها بحكم نهائي أو سند "
        "تنفيذي، وإعذارها بالوفاء، وتعذّر استيفاء الحق منها (الدفع بالتجريد / حق المناقشة). وللشريك — "
        "بعد وفائه بدين الشركة — الرجوع على باقي الشركاء بنسبة حصّة كلٍّ منهم.",
        "第四十八条（对合伙人财产的执行）：非经以下步骤，不得要求合伙人以其个人财产清偿公司债务："
        "该债务已凭终审判决或执行依据确定归属于公司、已催告公司清偿、且无法从公司处获得清偿（先诉"
        "抗辩权）。合伙人清偿公司债务后，有权按各合伙人的份额比例向其余合伙人追偿。",
        "Article 48 — Execution against a Partner's Assets",
        ["الدفع بالتجريد", "الإعذار بالوفاء", "حق الرجوع"],
        ["先诉抗辩权", "催告清偿", "追偿"],
        "A partner's personal assets may be reached only after the debt is established against "
        "the company, demand is made, and recovery from the company fails (benefit of "
        "excussion); the paying partner may recover pro rata from the others.",
        terminology=[
            {"ar": "الدفع بالتجريد (حق المناقشة)", "zh": "先诉抗辩权"},
            {"ar": "حق الرجوع على الشركاء", "zh": "向其他合伙人追偿"},
        ]),

    art(49, "shares_partners",
        "تقدير قيمة حصة الشريك",
        "合伙人份额的估值",
        "ما لم يُتّفق على القيمة أو ينص العقد على طريقة التقييم، تُقدَّر قيمة الحصة عند الانسحاب أو "
        "الإخراج أو افتتاح إجراءات التصفية بحق الشريك وفق نظام الإفلاس أو الوفاة (وعدم دخول الورثة)؛ "
        "وذلك بتقرير من مقيّم معتمد يبيّن القيمة العادلة للنصيب في تاريخ الواقعة، ولا يكون له أو لورثته "
        "نصيب فيما يُستجدّ بعدها إلا بقدر ما ينتج من عمليات سابقة. وعند التنازل تُقدَّر الحصة بالقيمة "
        "المتّفق عليها مع المتنازَل له.",
        "第四十九条（合伙人份额的估值）：未约定价值或协议未规定估值方法的，于退伙、除名、依破产法"
        "对合伙人启动清算程序或其死亡（且继承人不加入）时，由认证评估师出具报告，列明其份额在事件"
        "发生日的公允价值；此后新增部分，除源于此前已进行的交易外，合伙人或其继承人不享有份额。转让"
        "情形下，份额按与受让人约定的价值估定。",
        "Article 49 — Valuation of a Partner's Quota",
        ["تقدير قيمة الحصة", "المقيّم المعتمد", "القيمة العادلة", "نظام الإفلاس"],
        ["份额估值", "认证评估师", "公允价值", "破产法"],
        "Absent agreement, a certified appraiser sets the fair value of the quota at the event "
        "date (withdrawal, expulsion, bankruptcy-liquidation, or death); later gains accrue only "
        "from prior operations.",
        terminology=[
            {"ar": "مقيّم معتمد", "zh": "认证评估师"},
            {"ar": "القيمة العادلة", "zh": "公允价值"},
        ]),

    art(50, "termination",
        "انتهاء شركة التضامن",
        "无限公司的终止与解散",
        "(1) لا تنتهي شركة التضامن بوفاة أيٍّ من الشركاء، ولا بالحجر عليه، ولا بافتتاح أيٍّ من إجراءات "
        "التصفية تجاهه وفقاً لنظام الإفلاس، ولا بإخراجه، ولا بانسحابه، ما لم ينص عقد التأسيس على ذلك؛ "
        "وتستمر الشركة بين باقي الشركاء، ولا يكون لهذا الشريك أو ورثته إلا نصيب في أموال الشركة يُقدَّر "
        "وفق المادة (49). (2) يجوز النص في العقد على أن تستمر الشركة عند وفاة أحد الشركاء مع من يرغب من "
        "الورثة ولو كانوا قُصَّراً أو ممنوعين نظاماً من التجارة، ولا يُسألون عن ديون الشركة إلا في حدود "
        "نصيب كلٍّ منهم في حصة المورّث؛ ويجب تحويل الشركة خلال مدة لا تتجاوز (سنة) من تاريخ الوفاة إلى "
        "شركة توصية بسيطة يكون فيها القاصر أو الممنوع شريكاً موصياً؛ وإلا انتهت الشركة بقوة النظام. "
        "(3) إذا لم يتبقَّ في الشركة — عند وفاة شريك أو الحجر عليه أو افتتاح إجراءات التصفية تجاهه أو "
        "انسحابه أو إخراجه — غير شريك واحد، مُنح مهلة (90) يوماً لتصحيح الوضع، وإلا انتهت الشركة بقوة "
        "النظام بمُضيّ المهلة.",
        "第五十条（无限公司的终止与解散）：（1）存续原则：无限公司不因任何合伙人的死亡、被宣告"
        "禁治产、依《破产法》对其启动清算程序、被除名或退伙而终止，设立协议另有约定的除外；公司在"
        "其余合伙人之间继续存续，该合伙人或其继承人仅有权取得其在公司资产中的份额，并依第四十九条"
        "估定。（2）未成年人与禁业者保护：设立协议可约定合伙人死亡时公司与愿意加入的继承人继续存续，"
        "即使继承人为未成年人或依法被禁止从事商业活动者；该等继承人仅以其在被继承人资本份额中所占"
        "部分为限对公司债务负责。此时须自死亡之日起不超过一（1）年内将公司转为两合公司，使其成为"
        "有限合伙人；否则期限届满时公司依法当然终止。（3）仅余一名合伙人及纠正宽限期：若致公司仅余"
        "一名合伙人，则给予九十（90）日宽限期以纠正状况（引入新合伙人或转为本法其他公司形式）；否则"
        "期限届满时公司依法终止。",
        "Article 50 — Termination and Dissolution",
        ["انتهاء الشركة", "استمرار الشركة", "شركة توصية بسيطة", "بقوة النظام"],
        ["公司终止", "存续原则", "两合公司", "依法当然终止"],
        "The partnership survives a partner's death, interdiction, bankruptcy-liquidation, "
        "expulsion or withdrawal unless the deed says otherwise; minor/interdicted heirs trigger "
        "conversion to a limited partnership within one year; a sole remaining partner has a "
        "90-day cure period.",
        terminology=[
            {"ar": "شركة التوصية البسيطة", "zh": "两合公司"},
            {"ar": "بقوة النظام", "zh": "依法当然（自动）"},
        ]),
]


def main():
    assert len(ARTICLES) == 16, f"expected 16 articles, got {len(ARTICLES)}"
    nums = [a["article_number"] for a in ARTICLES]
    assert nums == list(range(35, 51)), f"article numbers not 35..50: {nums}"

    payload = {
        "book": 2,
        "book_title_ar": "الباب الثاني",
        "book_title_zh": "第二编",
        "scope_ar": "الباب الثاني كاملًا: شركة التضامن — من التأسيس إلى الانتهاء — المواد 35–50",
        "scope_zh": "第二编（全）：无限公司 — 从设立到终止（第三十五条 至 第五十条）",
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
        "coverage_id": "sa-companies-book2-coverage",
        "book": 2,
        "scope_ar": payload["scope_ar"],
        "scope_zh": payload["scope_zh"],
        "articles_range": "35-50",
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
