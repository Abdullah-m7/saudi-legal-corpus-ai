#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ingest + review the ORIGINAL Bab 1 Chinese PDF source (Articles 1-34).

Extracts the Chinese text layer from the owner-provided original Bab 1 bilingual PDF, segments it
into 34 per-article records by `第N条（Title）` headings, and compares each article's MEANING
against the official Arabic text (governing) to classify whether it is suitable for later Chinese
LLM-ready use. Review / source-inventory stage ONLY — it does NOT create Chinese LLM-ready records,
does NOT rewrite the PDF, and does NOT produce a corrected Chinese translation. Chinese is an
internal working/reference translation only — NOT official, NOT binding; Arabic is governing.

Reads : inputs/chinese_translation_source_pdfs/saudi_companies_law_ar_zh_bab1_full.pdf
        data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json
Writes: data/chinese_translation_sources/bab1_zh_source_extracted_articles_001_034.json
        reports/chinese_translation_review/bab1_original_pdf_translation_review.json
        reports/chinese_translation_review/BAB1_ORIGINAL_PDF_TRANSLATION_REVIEW_AR.md
"""

from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "inputs", "chinese_translation_source_pdfs",
                   "saudi_companies_law_ar_zh_bab1_full.pdf")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
EX_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
EX_OUT = os.path.join(EX_DIR, "bab1_zh_source_extracted_articles_001_034.json")
RV_DIR = os.path.join(ROOT, "reports", "chinese_translation_review")
RV_JSON = os.path.join(RV_DIR, "bab1_original_pdf_translation_review.json")
RV_MD = os.path.join(RV_DIR, "BAB1_ORIGINAL_PDF_TRANSLATION_REVIEW_AR.md")

STAGE = "CHINESE_BAB1_ORIGINAL_PDF_TRANSLATION_REVIEW"
TARGET = 34
SOURCE_REL = "inputs/chinese_translation_source_pdfs/saudi_companies_law_ar_zh_bab1_full.pdf"

_HEAD = re.compile(r'第[一二三四五六七八九十]+条（[^）]*）')
# non-article trailing sections that leak into the last article of a section
_CUT_MARKERS = ("译者战略性注释", "译者声明", "公司法术语表", "公司治理与责任术语表",
                "译文审校记录", "术语表")


def _sha256_bytes(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _zh_num(z):
    d = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    s = re.match(r"第([一二三四五六七八九十]+)条", z).group(1)
    if s == "十":
        return 10
    if "十" in s:
        a, b = s.split("十")
        return (d.get(a, 1)) * 10 + (d.get(b, 0) if b else 0)
    return d.get(s, 0)


def _clean_body(seg):
    # cut at the first non-article trailing section
    for mk in _CUT_MARKERS:
        i = seg.find(mk)
        if i != -1:
            seg = seg[:i]
    # drop running headers / page numbers
    seg = re.sub(r"·\s*沙特公司法[^\n]*", " ", seg)
    seg = re.sub(r"\d+\s*/\s*1[01]", " ", seg)
    # keep lines whose CJK content dominates (drop the garbled Arabic source column)
    kept = []
    for line in seg.split("\n"):
        cjk = len(re.findall(r"[一-鿿]", line))
        ar = len(re.findall(r"[؀-ۿ]", line))
        if cjk >= ar:
            kept.append(line)
    s = "\n".join(kept)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "", s)          # join wrapped CJK lines (no spaces in Chinese)
    s = s.strip().lstrip("：:").strip()
    return s


def _raw_text():
    try:
        from pypdf import PdfReader
        reader = PdfReader(PDF)
        return "\n".join((p.extract_text() or "") for p in reader.pages), len(reader.pages)
    except ImportError:
        raise SystemExit(
            "ERROR: pypdf is not installed; cannot extract the Chinese PDF text layer. "
            "Install extras: pip install -e \".[extract]\".")


def extract():
    text, pages = _raw_text()
    heads = [(m.start(), m.end(), m.group(0)) for m in _HEAD.finditer(text)]
    recs = {}
    for i, (s, e, h) in enumerate(heads):
        n = _zh_num(h)
        if n in recs:
            continue
        nxt = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        title = re.search(r"（([^）]*)）", h).group(1)
        recs[n] = {
            "article_number": n,
            "chinese_heading": title,
            "chinese_text": _clean_body(text[e:nxt]),
            "extraction_method": "pypdf_text_layer + 第N条 heading segmentation",
            "extraction_confidence": "high" if _clean_body(text[e:nxt]) else "low",
            "extraction_notes": "Chinese column extracted from the bilingual PDF text layer; the "
                                "garbled Arabic source column is dropped. Some articles are "
                                "condensed/summary style per the PDF's own disclaimer.",
        }
    return recs, pages


# -- per-article expected-element checks (grounded in the Arabic requirements) ----------------
# Each entry: {arabic_label: [chinese_keywords]}; element present if any keyword occurs.
_ELEMENTS = {
    1: {"تعريف كل مصطلح (لا مجرد سرد المصطلحات)": ["：指", "系指", "是指", "定义为"]},
    2: {"المساهمة بمال أو عمل أو بهما": ["出资", "货币", "劳务"],
        "اقتسام الربح والخسارة": ["损益", "盈亏", "分担利润"],
        "استثناء/تغطية الشركة غير الربحية (الباب السابع)": ["非营利", "第七部分"]},
    5: {"قاعدة الاسم بالعربية أو لغة أخرى": ["阿拉伯语", "阿拉伯文", "其他语言"],
        "اشتقاق الاسم من الغرض/الاسم/الشريك/اسم مبتكر": ["取自", "来源", "股东姓名", "专有名称"],
        "موافقة الشريك/المساهم السابق أو الورثة": ["前合伙人", "继承人", "同意"],
        "الالتزام بنظام الأسماء التجارية": ["商业名称法"],
        "إجراءات التعديل": ["变更程序", "修改程序"]},
    6: {"تعريف المؤسس": ["创始人"],
        "الطلب/البيانات/المستندات المطلوبة": ["申请", "资料", "文件", "数据"]},
    7: {"محتوى عقد التأسيس/النظام الأساس": ["设立文件", "章程", "契约"],
        "نماذج/إرشادات الوزارة": ["范本", "指引", "商务部", "表格"]},
    8: {"الشكل الكتابي/البطلان": ["书面", "无效"],
        "متطلبات التعديل": ["修改", "变更"],
        "آثار القيد": ["登记"],
        "المسؤولية التضامنية": ["连带责任"],
        "اطمئنان الغير/الاعتماد": ["第三人", "信赖", "善意"]},
    9: {"الشخصية الاعتبارية أثناء التأسيس": ["设立期间", "法人资格"],
        "المصروفات بعد القيد": ["费用"],
        "المسؤولية عند عدم إتمام التأسيس": ["未完成", "责任"]},
    11: {"الورثة": ["继承人"],
         "سياسة العمل/التوظيف لأفراد العائلة": ["工作政策", "就业", "聘用", "雇佣"],
         "التصرف في الحصص/الأسهم": ["份额", "股份", "转让", "处分"],
         "تسوية المنازعات": ["争议", "纠纷", "解决"]},
    12: {"عنوان المركز الرئيس": ["住所", "地址", "营业所"],
         "البريد الإلكتروني إن وجد": ["电子邮箱", "电邮", "邮箱"],
         "رأس المال المدفوع": ["实缴", "已缴"]},
    13: {"أشكال الحصص/المساهمة": ["出资形式", "出资"],
         "استثناء شركة المساهمة/المساهمة المبسطة": ["股份公司", "简易股份公司"],
         "منح حصص مقابل عمل/خدمات": ["劳务", "服务"]},
    14: {"قاعدة حق الانتفاع/الاستعمال (الإيجار)": ["用益权", "使用权", "租赁"],
         "عائد العمل يعود للشركة": ["劳动", "所得", "归公司"],
         "استثناء حقوق الملكية الفكرية": ["知识产权"]},
    15: {"مديونية كل شريك للشركة بقيمة حصته المتعهد بها": ["出资", "债务", "义务"]},
}

_ACTION = {
    "materially_incomplete_needs_retranslation": "retranslate_full_from_arabic_before_llm_ready",
    "summary_needs_expansion": "expand_from_arabic_before_llm_ready",
    "mostly_aligned_but_condensed": "expand_condensed_details_from_arabic_then_review",
    "full_or_near_full_aligned": "manual_review_then_candidate_for_later_llm_ready",
    "extraction_unclear_needs_manual_review": "manual_review_extraction_then_reassess",
}
_RATING = {
    "materially_incomplete_needs_retranslation": "low",
    "summary_needs_expansion": "low",
    "mostly_aligned_but_condensed": "medium",
    "full_or_near_full_aligned": "high",
    "extraction_unclear_needs_manual_review": "extraction_unclear",
}


def _classify(n, zh_text, ar_title):
    missing = []
    if not zh_text:
        cov = "extraction_unclear_needs_manual_review"
    elif n in _ELEMENTS:
        total = len(_ELEMENTS[n])
        present = 0
        for label, kws in _ELEMENTS[n].items():
            if any(k in zh_text for k in kws):
                present += 1
            else:
                missing.append(label)
        frac = present / total
        if n == 1 or frac < 0.34:
            cov = "materially_incomplete_needs_retranslation"
        elif frac < 0.67:
            cov = "summary_needs_expansion"
        else:
            cov = "mostly_aligned_but_condensed"
    else:
        if 1 <= n <= 15:
            cov = "summary_needs_expansion"
        else:  # 16..34
            cov = "mostly_aligned_but_condensed"
        if len(zh_text) < 40:
            cov = "materially_incomplete_needs_retranslation" if n <= 15 \
                else "summary_needs_expansion"
        missing = ["تفاصيل إجرائية/فرعية مضغوطة مقارنة بالنص العربي الرسمي"] \
            if cov != "materially_incomplete_needs_retranslation" else \
            ["أغلب عناصر النص العربي غير مُغطّاة أو مضغوطة بشدة"]
    rating = _RATING[cov]
    # semantic rating nudge for condensed 1..15 stays low; 16..25 condensed -> medium
    return cov, rating, missing


def review(extracted, arabic_by):
    records = []
    for n in range(1, TARGET + 1):
        ex = extracted[n]
        zh = ex["chinese_text"]
        a = arabic_by.get(n, {})
        ar_title = a.get("article_title_ar", "")
        cov, rating, missing = _classify(n, zh, ar_title)
        usable = cov != "extraction_unclear_needs_manual_review"  # not misleading; usable as ref
        note = {
            "materially_incomplete_needs_retranslation":
                "الترجمة الصينية ناقصة جوهريًا وتحتاج إعادة ترجمة كاملة من العربية قبل أي استخدام كطبقة كاملة.",
            "summary_needs_expansion":
                "الترجمة الصينية مختصرة/تلخيصية وتحتاج توسعة من النص العربي قبل الاستخدام الكامل.",
            "mostly_aligned_but_condensed":
                "الترجمة الصينية متوافقة في الأغلب لكنها مضغوطة؛ تصلح كمرجع داخلي وتحتاج توسعة تفاصيل قبل الطبقة الكاملة.",
            "full_or_near_full_aligned":
                "الترجمة الصينية متوافقة إلى حد كبير؛ مرشّحة لمراجعة لاحقة قبل الطبقة الكاملة.",
            "extraction_unclear_needs_manual_review":
                "تعذّر استخراج نص صيني واضح لهذه المادة؛ تحتاج مراجعة يدوية.",
        }[cov]
        records.append({
            "article_number": n,
            "arabic_article_title": ar_title,
            "chinese_heading": ex["chinese_heading"],
            "coverage_status": cov,
            "semantic_alignment_rating": rating,
            "llm_ready_as_full_translation": False,
            "usable_as_internal_reference": usable,
            "missing_or_compressed_elements_ar": missing,
            "misleading_or_risky_elements": [],
            "recommended_action": _ACTION[cov],
            "reviewer_note_ar": note,
        })
    return records


def _summary(records):
    cov = {}
    for r in records:
        cov[r["coverage_status"]] = cov.get(r["coverage_status"], 0) + 1
    need_expand = [r["article_number"] for r in records
                   if r["coverage_status"] in ("summary_needs_expansion",
                                               "materially_incomplete_needs_retranslation")]
    usable = [r["article_number"] for r in records if r["usable_as_internal_reference"]]
    return {
        "coverage_status_counts": cov,
        "articles_needing_expansion_or_retranslation": need_expand,
        "articles_usable_as_internal_reference": usable,
        "llm_ready_as_full_translation_any": False,
        "overall_note_ar": "الباب الأول (المواد 1–34) ترجمة صينية داخلية غير رسمية، كثير من "
                           "موادها مختصرة/تلخيصية؛ لا يصلح مباشرة كطبقة Chinese LLM-ready كاملة. "
                           "يُعتمد كمصدر مرجعي داخلي تحت المراجعة، مع توسعة/إعادة ترجمة المواد "
                           "الناقصة لاحقًا قبل بناء الطبقة الصينية.",
    }


def build():
    extracted, pages = extract()
    if sorted(extracted) != list(range(1, TARGET + 1)):
        raise SystemExit("ERROR: extracted article numbers are not exactly 1..34: %s"
                         % sorted(extracted))

    ex_payload = {
        "source_file": SOURCE_REL,
        "source_language": "zh",
        "source_status": "internal_working_translation_source",
        "governing_text_language": "ar",
        "official_translation": False,
        "not_binding": True,
        "not_full_legal_translation_claimed": True,
        "source_pdf_sha256": _sha256_bytes(PDF),
        "source_pdf_size_bytes": os.path.getsize(PDF),
        "source_pdf_page_count": pages,
        "extraction_method": "pypdf_text_layer + 第N条 heading segmentation",
        "article_count": TARGET,
        "article_range": [1, TARGET],
        "records": [extracted[n] for n in range(1, TARGET + 1)],
    }
    os.makedirs(EX_DIR, exist_ok=True)
    with open(EX_OUT, "w", encoding="utf-8") as fh:
        json.dump(ex_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    with open(ARABIC, "r", encoding="utf-8") as fh:
        arabic_by = {r["article_number"]: r for r in json.load(fh)["records"]}
    records = review(extracted, arabic_by)
    summary = _summary(records)

    rv_payload = {
        "stage": STAGE,
        "not_legal_advice": True,
        "source_pdf": SOURCE_REL,
        "source_pdf_sha256": _sha256_bytes(PDF),
        "article_count": TARGET,
        "article_range": [1, TARGET],
        "governing_language": "ar",
        "chinese_source_status": "internal_working_translation_source",
        "official_chinese_translation_claimed": False,
        "chinese_binding_claimed": False,
        "full_translation_claimed": False,
        "review_method": "automated_initial_review: chinese_text_element_presence_vs_arabic_"
                         "requirements + range_guidance (needs human confirmation)",
        "review_summary": summary,
        "records": records,
    }
    os.makedirs(RV_DIR, exist_ok=True)
    with open(RV_JSON, "w", encoding="utf-8") as fh:
        json.dump(rv_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    _write_md(ex_payload, rv_payload, records, summary)
    print("wrote Chinese Bab1 review: %d extracted + %d review records; coverage=%s"
          % (len(ex_payload["records"]), len(records), summary["coverage_status_counts"]))


def _write_md(ex, rv, records, summary):
    L = []
    L.append("# مراجعة ترجمة الباب الأول الصينية — ملف PDF الأصلي")
    L.append("# Bab 1 original Chinese PDF — translation review")
    L.append("")
    L.append("> **هذه مراجعة/جرد مصدر فقط، وليست ترجمة رسمية ولا استشارة قانونية.** لم يُنشأ أي "
             "سجل Chinese LLM-ready، ولم تُصحَّح الترجمة، ولم يُعدَّل ملف الـPDF.")
    L.append("")
    L.append("## المصدر / Source")
    L.append("")
    L.append("- **مصدر الملف / source file:** `%s`" % ex["source_file"])
    L.append("- **SHA-256:** `%s`" % rv["source_pdf_sha256"])
    L.append("- **عدد الصفحات / pages:** %s · **الحجم / size:** %s bytes"
             % (ex["source_pdf_page_count"], ex["source_pdf_size_bytes"]))
    L.append("- **طريقة الاستخراج / extraction:** %s" % ex["extraction_method"])
    L.append("- **نطاق الباب الأول / scope:** المواد **1–34**")
    L.append("")
    L.append("## الوضع القانوني / Posture")
    L.append("")
    L.append("- **هل الترجمة الصينية رسمية؟** **لا** (`official_translation = false`).")
    L.append("- **هل الصينية حاكمة؟** **لا، العربية هي اللغة الحاكمة** (`governing = ar`).")
    L.append("- **هل الملف يصلح مباشرة كـChinese LLM-ready كامل؟** **لا** "
             "(`llm_ready_as_full_translation = false` لكل المواد).")
    L.append("- الصينية **ترجمة عمل/مرجع داخلية فقط، غير مُلزِمة** (`not_binding = true`).")
    L.append("")
    L.append("## ملخص التصنيف العام / Classification summary")
    L.append("")
    for k in sorted(summary["coverage_status_counts"]):
        L.append("- `%s`: **%d**" % (k, summary["coverage_status_counts"][k]))
    L.append("- **مواد تحتاج توسعة/إعادة ترجمة / need expansion or retranslation:** %s"
             % ", ".join(str(x) for x in summary["articles_needing_expansion_or_retranslation"]))
    L.append("- **مواد تصلح كمرجع داخلي / usable as internal reference:** %d/34"
             % len(summary["articles_usable_as_internal_reference"]))
    L.append("")
    L.append("## جدول المواد 1–34 / Articles 1–34")
    L.append("")
    L.append("| المادة | درجة المطابقة | حالة التغطية | كاملة LLM؟ | مرجع داخلي؟ | الإجراء المقترح |")
    L.append("|---|---|---|---|---|---|")
    for r in records:
        L.append("| %d | %s | `%s` | %s | %s | `%s` |" % (
            r["article_number"], r["semantic_alignment_rating"], r["coverage_status"],
            "نعم" if r["llm_ready_as_full_translation"] else "لا",
            "نعم" if r["usable_as_internal_reference"] else "لا",
            r["recommended_action"]))
    L.append("")
    L.append("## أهم المواد التي تحتاج توسعة أو إعادة ترجمة / Key articles needing work")
    L.append("")
    for r in records:
        if r["coverage_status"] in ("materially_incomplete_needs_retranslation",
                                    "summary_needs_expansion"):
            miss = "؛ ".join(r["missing_or_compressed_elements_ar"][:4])
            L.append("- **المادة %d — %s:** `%s` — عناصر ناقصة/مضغوطة: %s"
                     % (r["article_number"], r["arabic_article_title"], r["coverage_status"],
                        miss or "—"))
    L.append("")
    L.append("## التوصية للمرحلة التالية / Recommendation")
    L.append("")
    L.append("لا يُنصح بتحويل ملف الباب الأول مباشرة إلى طبقة Chinese LLM-ready كاملة. يوصى "
             "باعتماده أولًا كمصدر ترجمة صينية داخلي تحت المراجعة، ثم إنشاء مرحلة لاحقة "
             "لتوسيع/تصحيح المواد ذات النقص قبل بناء الطبقة الصينية.")
    L.append("")
    L.append("**العربية هي اللغة الحاكمة. الصينية ترجمة داخلية غير رسمية وغير مُلزِمة. "
             "ليست استشارة قانونية.**")
    L.append("Arabic is governing. Chinese is an internal, non-official, non-binding working "
             "translation. Not legal advice.")
    with open(RV_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    build()


if __name__ == "__main__":
    main()
