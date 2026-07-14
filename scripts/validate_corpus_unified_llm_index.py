#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the unified Arabic LLM retrieval index.

Checks the index is complete and consistent with the source enrichment layers,
that records are well-formed and unique, and that a set of built-in sanity
queries route to the expected law.  Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
SUMMARY = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index_summary.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from search_corpus_unified import search  # noqa: E402

EXPECTED_TOTAL = 6537
EXPECTED_PER_CORPUS = {"companies_law": 281, "pdpl": 81, "investment": 53, "civil": 721, "gtpl": 256, "labor": 571, "evidence": 322, "personal_status": 293, "sharia_procedure": 880, "criminal_procedure": 403, "enforcement": 371, "judiciary": 85, "board_of_grievances": 26, "law_practice": 146, "commercial_courts": 377, "bankruptcy": 353, "judicial_costs": 40, "arbitration": 77, "commercial_papers": 121, "commercial_register": 29, "trade_names": 23, "commercial_agencies": 6, "chambers_of_commerce": 66, "commercial_books": 16, "aml": 52, "tawtheeq": 88, "real_estate_registration": 91, "real_estate_mortgage": 46, "real_estate_finance": 15, "real_estate_units": 74, "foreign_ownership": 15, "municipal_realestate": 41, "gcc_ownership": 6, "terrorism": 127, "juveniles": 37, "whistleblower": 37, "judicial_inspection": 68, "qismah": 48, "sulook": 47, "aawan": 35, "muslaha": 29, "iflas_hudud": 23, "judicial_documents": 23, "bankruptcy_fees": 20, "enforcement_providers": 18}
REQUIRED = ["record_id", "corpus", "law_id", "law_component", "law_title_ar",
            "article_number", "llm_title_ar", "retrieval_title_ar", "article_path",
            "keywords_ar", "search_queries_ar", "text_ar", "text_status", "source_layer"]

# (query, expected corpus of the top hit, expected article_number of the top hit)
SANITY = [
    ("تسرب البيانات الشخصية", "pdpl", 24),
    ("المصادرة غير المباشرة", "investment", 5),
    ("انتخاب أعضاء مجلس الإدارة", "companies_law", 68),
    ("عقد المقايضة", "civil", 361),
    ("المزايدة العكسية", "gtpl", None),
    ("ساعات العمل الإضافية", "labor", None),
    ("تحويل عقد العمل المؤقت تسعين يوما", "labor", 1),
    ("جدول المخالفات والجزاءات", "labor", None),
    ("ترخيص التوسط في توظيف السعوديين", "labor", None),
    ("استقبال وإيواء العمالة المستقدمة", "labor", 52),
    ("الترتيبات التيسيرية للإعاقات البصرية", "labor", 4),
    ("نموذج عقد عمل موسمي", "labor", None),
    ("حجية الدليل الرقمي في الإثبات", "evidence", 55),
    ("التوقيع الرقمي في إجراءات الإثبات", "evidence", 2),
    ("قيد الخبراء أمام المحاكم", "evidence", 2),
    ("الخطبة والوعد بالزواج", "personal_status", 1),
    ("المهر ملك للمرأة", "personal_status", 38),
    ("انتفاء الخلوة بين الزوجين", "personal_status", 1),
    ("طرق الاعتراض على الأحكام الاستئناف والنقض", "sharia_procedure", 176),
    ("يجوز رد القاضي لأحد الأسباب دعوى مماثلة أو خصومة مع أحد الخصوم", "sharia_procedure", 96),
    ("تكون المرافعة علنية ما لم ترَ المحكمة إجراءها سرا", "sharia_procedure", 64),
    ("يجوز للمحكمة أن تأمر بوقف التنفيذ المعجل إذا رأت أن أسباب الاعتراض على الحكم قد تقضي بنقضه", "sharia_procedure", 170),
    ("يكتب التاريخ الهجري أولا بحسب تقويم أم القرى", "sharia_procedure", 16),
    ("لا يجوز القبض على أي إنسان أو توقيفه إلا بأمر من السلطة المختصة", "criminal_procedure", 35),
    ("الأحكام النهائية هي الأحكام المكتسبة للقطعية", "criminal_procedure", 210),
    ("يباشر المحقق معاينة مكان وقوع الجريمة بنفسه وله ندب أحد رجال الضبط الجنائي", "criminal_procedure", 54),
    ("ضبط الأموال والأرصدة لدى البنوك في مرحلة التحقيق", "criminal_procedure", 58),
    ("التنفيذ الجبري لا يكون إلا بسند تنفيذي لحق محقق الوجود حال الأداء", "enforcement", 9),
    ("يختص قاضي التنفيذ بالفصل في منازعات التنفيذ", "enforcement", 3),
    ("يكون توقيع المحضر في مكان المال المحجوز إن أمكن وعلى كل صفحة من صفحاته", "enforcement", 134),
    ("الحجز على العقار حجز على غلته ويبلغ المستأجر بالحجز التنفيذي", "enforcement", 143),
    ("القضاة مستقلون لا سلطان عليهم في قضائهم لغير أحكام الشريعة الإسلامية", "judiciary", 1),
    ("لا يجوز نقل أعضاء السلك القضائي أو ندبهم داخل السلك القضائي إلا بقرار من المجلس الأعلى للقضاء", "judiciary", 49),
    ("ديوان المظالم هيئة قضاء إداري مستقلة يرتبط مباشرة بالملك", "board_of_grievances", 1),
    ("تختص المحاكم الإدارية بالفصل في دعاوى إلغاء القرارات الإدارية النهائية وإساءة استعمال السلطة", "board_of_grievances", 13),
    ("يُنشأ في الديوان مجلس يسمى مجلس القضاء الإداري ويتكون من رئيس ديوان المظالم واثنين من ذوي الخبرة والاختصاص", "board_of_grievances", 4),
    ("يقصد بمهنة المحاماة الترافع عن الغير أمام المحاكم واللجان ومزاولة الاستشارات الشرعية والنظامية", "law_practice", 1),
    ("يقصد بمكتب المحاماة الأجنبي المنشأة غير السعودية التي تزاول أعمال مهنة المحاماة والترخيص له في المملكة", "law_practice", 44),
    ("يلتزم المحامي عند تقديم أعمال المهنة عبر منصة إلكترونية وسيطة بالمحافظة على خصوصية عملائه وسرية البيانات", "law_practice", 19),
    ("يقتصر منح الترخيص المؤقت لمكتب المحاماة الأجنبي على الاستشارات لمشروعات نوعية أو متخصصة تحتاج إليها المملكة", "law_practice", 62),
    ("تختص المحكمة التجارية بالنظر في المنازعات التي تنشأ بين التجار بسبب أعمالهم التجارية الأصلية أو التبعية", "commercial_courts", 16),
    ("يجوز للمدين التظلم من أمر الأداء الصادر بحقه أمام المحكمة المختصة خلال خمسة عشر يوماً", "commercial_courts", 71),
    ("يشترط لرفع الدعوى الجماعية اتحاد موضوع المطالبة والسبب والمدعى عليه وألا يقل عدد المدعين عن عشرة", "commercial_courts", 252),
    ("تراعي المحكمة عند تقريرها الاعتماد على خبير واحد مشترك من عدمه", "commercial_courts", 144),
    ("يهدف النظام إلى تنظيم إجراءات الإفلاس وهي التسوية الوقائية وإعادة التنظيم المالي والتصفية", "bankruptcy", 2),
    ("تكون أولوية الديون في إجراء التصفية الديون المضمونة ضمانا عينيا ثم التمويل المضمون", "bankruptcy", 196),
    ("تكون حصيلة بيع أصول التفليسة غير مجدية إذا كانت التكلفة المقدرة للبيع تساوي أو تزيد على القيمة المقدرة لبيعه", "bankruptcy", 70),
    ("تتولى الوحدة المختصة في المحكمة إدارة قضايا الإفلاس وقيد الطلبات والاعتراضات والمذكرات", "bankruptcy", 8),
    ("تفرض تكاليف قضائية على الدعوى بمبلغ لا يزيد على نسبة خمسة بالمئة من قيمة المطالبة وبحد أعلى مليون ريال", "judicial_costs", 3),
    ("لا تفرض التكاليف القضائية على المسجونين والموقوفين والعمال المشمولين بنظام العمل والوزارات والأجهزة الحكومية", "judicial_costs", 17),
    ("لا تقبل دعوى بطلان حكم التحكيم إلا إذا لم يوجد اتفاق تحكيم أو كان باطلاً أو خالف حكم التحكيم النظام العام", "arbitration", 50),
    ("إذا كانت هيئة التحكيم مشكلة من محكم واحد ولم يتفق طرفا التحكيم على اختياره تولت المحكمة المختصة اختياره", "arbitration", 10),
    ("تشتمل الكمبيالة على البيانات الآتية كلمة كمبيالة مكتوبة في متن الصك وأمر غير معلق على شرط بوفاء مبلغ معين", "commercial_papers", 1),
    ("يعاقب بالحبس وبغرامة كل من سحب بسوء نية شيكا لا يكون له مقابل وفاء قائم وقابل للسحب", "commercial_papers", 118),
    ("تنشئ الوزارة السجل التجاري وتقيد فيه البيانات التي يحددها النظام واللائحة وكل تحديث يطرأ عليها", "commercial_register", 3),
    ("يجب على كل تاجر اتخاذ اسم تجاري وقيده في السجل التجاري ويجوز حجز الاسم التجاري لمدة مؤقتة لدى المسجل", "trade_names", 3),
    ("لا يجوز لغير السعوديين أشخاصا طبيعيين أو معنويين أن يكونوا وكلاء تجاريين في المملكة", "commercial_agencies", 1),
    ("تحدد رسوم القيد في سجل الوكالات بخمسمائة ريال للتاجر الفرد والشركة وتدفع لمرة واحدة", "commercial_agencies", 5),
    ("تنشأ الغرفة بقرار من الوزير ويكون في كل منطقة إدارية غرفة واحدة ويحدد القرار مقرها ونطاق اختصاصها", "chambers_of_commerce", 3),
    ("تتكون الجمعية العمومية للغرفة من جميع المشتركين فيها", "chambers_of_commerce", 8),
    ("يجب على كل تاجر أن يمسك الدفاتر التجارية التي تستلزمها طبيعة تجارته بطريقة تكفل بيان مركزه المالي", "commercial_books", 1),
    ("تقيد في دفتر اليومية الأصلي جميع العمليات المالية التي يقوم بها التاجر وكذلك مسحوباته الشخصية", "commercial_books", 3),
    ("يعد مرتكباً جريمة غسل الأموال كل من قام بأي من الأفعال الآتية", "aml", 2),
    ("يُعد الشخص الاعتباري مرتكباً جريمة غسل الأموال إذا ارتكب باسمه أو لحسابه", "aml", 3),
    ("يطبق كاتب العدل والمرخص له أحكام الشريعة الإسلامية والأنظمة عند إجراء أعمال التوثيق", "tawtheeq", 2),
    ("يكون إنشاء كتابات العدل وتحديد دوائر اختصاصها النوعي والمكاني بقرار يصدره الوزير", "tawtheeq", 3),
    ("يصدر وكيل الوزارة للتوثيق والتسجيل العيني للعقار بعد موافقة الوزير قواعد السلوك المهني والأدلة الإجرائية", "tawtheeq", 29),
    ("يسري النظام على جميع العقارات الواقعة في إقليم المملكة", "real_estate_registration", 2),
    ("تحدد المنطقة العقارية بقرار يصدر عن الجهة المختصة ويتضمن القرار المدة المحددة لاستقبال طلبات التسجيل العيني", "real_estate_registration", 7),
    ("يشكل في الهيئة لجنة عليا للتسجيل العيني للعقار برئاسة الرئيس التنفيذي للهيئة أو من ينيبه وستة أعضاء من ذوي الخبرة", "real_estate_registration", 2),
    ("يصدر المسؤول الأول الدليل الإجرائي لتوثيق التصرفات اللاحقة للتسجيل العيني الأول للعقار", "real_estate_registration", 50),
    ("الرهن العقاري المسجل عقد يسجل يكسب به المرتهن الدائن حقا عينيا على عقار معين له سجل", "real_estate_mortgage", 1),
    ("إذا كان الراهن غير مالك للعقار المرهون كان رهنه موقوفا على إجازة موثقة من المالك", "real_estate_mortgage", 3),
    ("عقد التمويل العقاري: عقد الدفع الآجل لتملك المستفيد للسكن", "real_estate_finance", 1),
    ("يزاول الممول العقاري أعمال التمويل العقاري بما لا يتعارض مع أحكام الشريعة الإسلامية", "real_estate_finance", 3),
    ("لكل مالك أرض بصك مستوف للمتطلبات الشرعية والنظامية أن يبني عليها بناء ويفرزه إلى وحدات مستقلة", "real_estate_units", 2),
    ("يجوز إعادة فرز العقار المشترك أو جزء منه أو تغير استعمالاته بعد موافقة الجمعية العامة وموافقة المرتهن إن وجد", "real_estate_units", 3),
    ("تفتح الجمعية حساباً مصرفياً باسمها في أحد البنوك المرخص لها بالعمل داخل المملكة وتودع جميع أموال الجمعية فيه", "real_estate_units", 31),
    ("يجوز على أساس المعاملة بالمثل للممثليات الدبلوماسية المعتمدة بالمملكة تملك المقر الرسمي لها ومقر السكن لرئيسها وأعضائها", "foreign_ownership", 7),
    ("لغير السعودي تملك العقار أو اكتساب الحقوق العينية الأخرى على العقار في المملكة في النطاق الجغرافي الذي يحدده مجلس الوزراء", "foreign_ownership", 2),
    ("الأموال العامة التابعة للبلديات غير قابلة للتصرف ولكن يجوز في حدود ما تقر الأنظمة واللوائح الترخيص بالانتفاع بها", "municipal_realestate", 1),
    ("تتولى الوزارة إعداد عقود استثمار موحدة نماذج تعتمد بقرار من الوزير ليتم التقيد بها عند إبرام عقود الاستثمار في جميع العقارات البلدية", "municipal_realestate", 31),
    ("يسمح لمواطني دول مجلس التعاون من الأشخاص الطبيعيين أو الاعتباريين باستئجار وتملك العقارات المبنية والأراضي لغرض السكن أو الاستثمار", "gcc_ownership", 1),
    ("تعد الجرائم المنصوص عليها في النظام من الجرائم الكبيرة الموجبة للتوقيف", "terrorism", 2),
    ("كل من هرب أو صنعها أو طورها أو جمعها أو حضرها أو جهزها أو استوردها أو حازها أو أحرزها من الأسلحة والذخائر والمتفجرات بقصد استخدامها في ارتكاب الجرائم", "terrorism", 39),
    ("لأغراض تطبيق المادة الخامسة من النظام عند القبض على المشتبه بارتكابه إحدى الجرائم المنصوص عليها في النظام يتم إشعار النيابة العامة فور القبض عليه وبشكل مباشر", "terrorism", 5),
    ("لا يساءل جزائيا من لم يتم السابعة من عمره وقت ارتكاب الفعل المعاقب عليه", "juveniles", 2),
    ("تقوم الدار فور إيداع الحدث لديها بإعداد تقرير اجتماعي عن حالته يشتمل على كل ما يفيد القاضي في إصدار حكمه", "juveniles", 9),
    ("يعاقب بالسجن مدة لا تتجاوز سنتين وبغرامة لا تزيد على ثلاثمئة ألف ريال كل من هدد المشمول بالحماية أو ابتزه", "whistleblower", 26),
    ("التعاون مع المحكمة بما يكفل أداء الشهود لشهادتهم دون تأثير أو تأخير على جهات الرقابة والضبط والتحقيق في الجرائم المشمولة بأحكام النظام", "whistleblower", 2),
    ("تحل هذه اللائحة محل لائحة التفتيش القضائي الصادرة بقرار المجلس الأعلى للقضاء ويعمل بها من تاريخ صدورها", "judicial_inspection", 68),
    ("تؤلف الإدارة من رئيس ومساعد لا تقل درجة كل منهما عن قاضي استئناف وعدد كاف من الأعضاء المتفرغين يختارهم المجلس", "judicial_inspection", 9),
    ("يراعى في قسمة المال المشترك المتضمن لنصيب قاصر أو غائب أو مفقود أو وقف أو وصية في جميع مراحل القسمة أو التصفية الأحكام الخاصة", "qismah", 2),
    ("على الدائرة أن تتخذ عند الاقتضاء جميع ما يجب بصفة مستعجلة للمحافظة على الأموال المشتركة وحراستها ولها أن تعهد إلى الهيئة العامة للولاية على أموال القاصرين", "qismah", 20),
    ("يستثنى من الأحكام المنصوص عليها في الفقرة الأولى من هذه القاعدة الدعاوى والوقائع التي يكون من سبق له العمل في السلك القضائي ومن في حكمه طرفا فيها أو وليا أو وصيا أو ناظرا للوقف", "sulook", 9),
    ("عند إعلان المحامي عن نفسه بطريق مباشر أو غير مباشر فعليه مراعاة الآتي ألا يكون الإعلان مضللا أو كاذبا أو مخادعا كالتضليل في الإشارة لتأهيل المحامي وخبراته", "sulook", 38),
    ("يقصد بأعوان القضاء من يعين الدائرة في عملها المنصوص عليه نظاما", "aawan", 1),
    ("تسلم صحائف الدعاوى والطلبات وكافة الأوراق المطلوب إعلانها من المختص وقيدها في السجل الخاص بذلك ويجب أن يشمل السجل اسم الجهة المعلنة", "aawan", 14),
    ("يشترط لتسجيل المصلح الشروط الآتية أن يكون كامل الأهلية أن يكون حسن السيرة والسلوك غير محكوم عليه بحكم مخل بالأمانة والشرف", "muslaha", 7),
    ("دعوى مالية بعشرين ألف ريال فما دون الحد الأعلى لموعد الجلسة الأولى من حين قيد الطلب واحد وعشرون يوما", "muslaha", 27),
    ("دون الإخلال بأنظمة الدولة الأجنبية للأمين المعين في إجراء الإفلاس بموجب أحكام النظام ممارسة صلاحياته ومهماته ذات الصلة في الدولة الأجنبية", "iflas_hudud", 5),
    ("للأمين الأجنبي خلال المدة من تقديم طلب الاعتراف بإجراء الإفلاس الأجنبي إلى حين البت فيه أن يتقدم إلى المحكمة بطلب مساعدة قضائية عند الاقتضاء لحماية أصول المدين", "iflas_hudud", 10),
    ("مع مراعاة المتطلبات النظامية التي من شأنها إضفاء الموثوقية والسلامة في البيانات تدون الوثائق القضائية الكترونيا ويكون لها حكم المحررات المكتوبة", "judicial_documents", 5),
    ("لا يجوز تعديل الضبط بعد اعتماده فإن رأت الدائرة حاجة لذلك فيكون في محضر لاحق يذكر فيه ما يراد إضافته أو تعديله", "judicial_documents", 10),
    ("تهدف هذه القواعد إلى حوكمة تقدير أتعاب الأمناء والخبراء وتعزيز الثقة والشفافية في إجراءات الإفلاس", "bankruptcy_fees", 2),
    ("تغطي أتعاب الأمين المعين في إجراء الإفلاس جميع الأعمال المنصوص عليها في النظام واللوائح والقواعد ذات الصلة بأداء المهمة", "bankruptcy_fees", 4),
    ("تسري أحكام اللائحة على جميع مقدمي خدمات التنفيذ المذكورين في الفقرة الأولى من المادة الثالثة والتسعين من النظام", "enforcement_providers", 2),
]


def main():
    errors = []
    for p in (INDEX, SUMMARY):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    records = [json.loads(l) for l in open(INDEX, encoding="utf-8") if l.strip()]

    if len(records) != EXPECTED_TOTAL:
        errors.append("[1] expected %d records, found %d" % (EXPECTED_TOTAL, len(records)))

    per = {}
    ids = set()
    for r in records:
        per[r["corpus"]] = per.get(r["corpus"], 0) + 1
        for k in REQUIRED:
            if k not in r:
                errors.append("[2] %s: missing field %r" % (r.get("record_id"), k))
        if not str(r.get("text_ar", "")).strip():
            errors.append("[2] %s: empty text_ar" % r.get("record_id"))
        if r["record_id"] in ids:
            errors.append("[3] duplicate record_id %s" % r["record_id"])
        ids.add(r["record_id"])

    for corpus, n in EXPECTED_PER_CORPUS.items():
        if per.get(corpus) != n:
            errors.append("[4] corpus %s: expected %d, found %d" % (corpus, n, per.get(corpus)))

    # [5] index text matches the source enrichment layers verbatim
    src_text = {}
    for rel in (
        "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
        "data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json",
        "data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
        "data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json",
        "data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json",
        "data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
        "data/gtpl_arabic_legal_llm/gtpl_law_legal_llm_001_099.json",
        "data/gtpl_arabic_legal_llm/gtpl_regulation_legal_llm_001_157.json",
        "data/labor_arabic_legal_llm/labor_law_legal_llm_001_245.json",
        "data/labor_arabic_legal_llm/labor_regulation_legal_llm_001_040.json",
        "data/labor_arabic_legal_llm/labor_annex1_legal_llm_001_072.json",
        "data/labor_arabic_legal_llm/labor_annex1_violation_tables_llm.json",
        "data/labor_arabic_legal_llm/labor_annex3_legal_llm_001_020.json",
        "data/labor_arabic_legal_llm/labor_annex4_legal_llm_001_072.json",
        "data/labor_arabic_legal_llm/labor_annex2_accessibility_tables_llm.json",
        "data/labor_arabic_legal_llm/labor_annex5_contract_forms_llm.json",
        "data/evidence_arabic_legal_llm/evidence_law_legal_llm_001_129.json",
        "data/evidence_arabic_legal_llm/evidence_electronic_rules_legal_llm_001_024.json",
        "data/evidence_arabic_legal_llm/evidence_procedural_manuals_legal_llm_001_135.json",
        "data/evidence_arabic_legal_llm/evidence_expertise_rules_legal_llm_001_034.json",
        "data/personal_status_arabic_legal_llm/personal_status_law_legal_llm_001_252.json",
        "data/personal_status_arabic_legal_llm/personal_status_regulation_legal_llm_001_041.json",
        "data/sharia_procedure_arabic_legal_llm/sharia_procedure_law_legal_llm_001_243.json",
        "data/sharia_procedure_arabic_legal_llm/sharia_procedure_regulation_legal_llm_001_637.json",
        "data/criminal_procedure_arabic_legal_llm/criminal_procedure_law_legal_llm_001_222.json",
        "data/criminal_procedure_arabic_legal_llm/criminal_procedure_regulation_legal_llm_001_181.json",
        "data/enforcement_arabic_legal_llm/enforcement_law_legal_llm_001_098.json",
        "data/enforcement_arabic_legal_llm/enforcement_regulation_legal_llm_001_273.json",
        "data/judiciary_arabic_legal_llm/judiciary_law_legal_llm_001_085.json",
        "data/board_of_grievances_arabic_legal_llm/board_of_grievances_law_legal_llm_001_026.json",
        "data/law_practice_arabic_legal_llm/law_practice_law_legal_llm_001_056.json",
        "data/law_practice_arabic_legal_llm/law_practice_regulation_legal_llm_001_090.json",
        "data/commercial_courts_arabic_legal_llm/commercial_courts_law_legal_llm_001_096.json",
        "data/commercial_courts_arabic_legal_llm/commercial_courts_regulation_legal_llm_001_281.json",
        "data/bankruptcy_arabic_legal_llm/bankruptcy_law_legal_llm_001_231.json",
        "data/bankruptcy_arabic_legal_llm/bankruptcy_regulation_legal_llm_001_098.json",
        "data/bankruptcy_arabic_legal_llm/bankruptcy_case_rules_legal_llm_001_024.json",
        "data/judicial_costs_arabic_legal_llm/judicial_costs_law_legal_llm_001_023.json",
        "data/judicial_costs_arabic_legal_llm/judicial_costs_regulation_legal_llm_001_017.json",
        "data/arbitration_arabic_legal_llm/arbitration_law_legal_llm_001_058.json",
        "data/arbitration_arabic_legal_llm/arbitration_regulation_legal_llm_001_019.json",
        "data/commercial_papers_arabic_legal_llm/commercial_papers_law_legal_llm_001_121.json",
        "data/commercial_register_arabic_legal_llm/commercial_register_law_legal_llm_001_029.json",
        "data/trade_names_arabic_legal_llm/trade_names_law_legal_llm_001_023.json",
        "data/commercial_agencies_arabic_legal_llm/commercial_agencies_law_legal_llm_001_006.json",
        "data/chambers_of_commerce_arabic_legal_llm/chambers_of_commerce_law_legal_llm_001_066.json",
        "data/commercial_books_arabic_legal_llm/commercial_books_law_legal_llm_001_016.json",
        "data/aml_arabic_legal_llm/aml_law_legal_llm_001_052.json",
        "data/tawtheeq_arabic_legal_llm/tawtheeq_law_legal_llm_001_057.json",
        "data/tawtheeq_arabic_legal_llm/tawtheeq_regulation_legal_llm_001_031.json",
        "data/real_estate_registration_arabic_legal_llm/real_estate_registration_law_legal_llm_001_040.json",
        "data/real_estate_registration_arabic_legal_llm/real_estate_registration_regulation_legal_llm_001_051.json",
        "data/real_estate_mortgage_arabic_legal_llm/real_estate_mortgage_law_legal_llm_001_046.json",
        "data/real_estate_finance_arabic_legal_llm/real_estate_finance_law_legal_llm_001_015.json",
        "data/real_estate_units_arabic_legal_llm/real_estate_units_law_legal_llm_001_033.json",
        "data/real_estate_units_arabic_legal_llm/real_estate_units_regulation_legal_llm_001_041.json",
        "data/foreign_ownership_arabic_legal_llm/foreign_ownership_law_legal_llm_001_015.json",
        "data/municipal_realestate_arabic_legal_llm/municipal_realestate_law_legal_llm_001_006.json",
        "data/municipal_realestate_arabic_legal_llm/municipal_realestate_regulation_legal_llm_001_035.json",
        "data/gcc_ownership_arabic_legal_llm/gcc_ownership_law_legal_llm_001_006.json",
        "data/terrorism_arabic_legal_llm/terrorism_law_legal_llm_001_099.json",
        "data/terrorism_arabic_legal_llm/terrorism_regulation_legal_llm_001_028.json",
        "data/juveniles_arabic_legal_llm/juveniles_law_legal_llm_001_024.json",
        "data/juveniles_arabic_legal_llm/juveniles_regulation_legal_llm_001_013.json",
        "data/whistleblower_arabic_legal_llm/whistleblower_law_legal_llm_001_037.json",
        "data/judicial_inspection_arabic_legal_llm/judicial_inspection_regulation_legal_llm_001_068.json",
        "data/qismah_arabic_legal_llm/qismah_regulation_legal_llm_001_048.json",
        "data/sulook_arabic_legal_llm/sulook_regulation_legal_llm_001_047.json",
        "data/aawan_arabic_legal_llm/aawan_regulation_legal_llm_001_035.json",
        "data/muslaha_arabic_legal_llm/muslaha_regulation_legal_llm_001_029.json",
        "data/iflas_hudud_arabic_legal_llm/iflas_hudud_regulation_legal_llm_001_023.json",
        "data/judicial_documents_arabic_legal_llm/judicial_documents_regulation_legal_llm_001_023.json",
        "data/bankruptcy_fees_arabic_legal_llm/bankruptcy_fees_regulation_legal_llm_001_020.json",
        "data/enforcement_providers_arabic_legal_llm/enforcement_providers_regulation_legal_llm_001_018.json",
    ):
        env = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        for r in env["records"]:
            src_text[r["record_id"]] = r.get("article_text_ar") or r.get("official_text_ar")
    for r in records:
        if r["text_ar"] != src_text.get(r["record_id"]):
            errors.append("[5] %s: text_ar differs from source layer" % r["record_id"])

    # [6] summary consistency
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("total_records") != len(records):
        errors.append("[6] summary total_records mismatch")

    # [7] sanity queries route to the expected law/article
    for q, corpus, art in SANITY:
        hits = search(q, top=1, index=records)
        if not hits:
            errors.append("[7] query %r returned no hits" % q)
            continue
        top = hits[0]
        rid = top["record_id"]
        rec = next((x for x in records if x["record_id"] == rid), {})
        if rec.get("corpus") != corpus or (art is not None and top["article_number"] != art):
            errors.append("[7] query %r -> top %s/art %s (expected %s/art %s)"
                          % (q, rec.get("corpus"), top["article_number"], corpus, art))

    if errors:
        print("FAIL: %d error(s) in unified LLM index:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    print("PASS: unified LLM retrieval index over %d records" % len(records))
    print("  - companies_law 281 + pdpl 81 + investment 53 + civil 721 + gtpl 256 + labor 571 + evidence 322 + personal_status 293 + sharia_procedure 880 + criminal_procedure 403 + enforcement 371 + judiciary 85 + board_of_grievances 26 + law_practice 146 + commercial_courts 377 + bankruptcy 353 + judicial_costs 40 + arbitration 77 + commercial_papers 121 + commercial_register 29 + trade_names 23 + commercial_agencies 6 + chambers_of_commerce 66 + commercial_books 16 + aml 52 + tawtheeq 88 + real_estate_registration 91 + real_estate_mortgage 46 + real_estate_finance 15 + real_estate_units 74 + foreign_ownership 15 + municipal_realestate 41 + gcc_ownership 6 + terrorism 127 + juveniles 37 + whistleblower 37 + judicial_inspection 68 + qismah 48 + sulook 47 + aawan 35 + muslaha 29 + iflas_hudud 23 + judicial_documents 23 + bankruptcy_fees 20 + enforcement_providers 18; unique ids; text verbatim from source layers")
    print("  - %d sanity queries each route to the expected law/article" % len(SANITY))
    return 0


if __name__ == "__main__":
    sys.exit(main())
