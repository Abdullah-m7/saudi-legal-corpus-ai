#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chinese all-Babs (1-14) source coverage inventory (source-inventory / review stage only).

Preserves the original Chinese PDFs for Babs 2-14 (Bab 1 already in repo), extracts their Chinese
text, segments by article where possible, and builds a complete Articles 1-281 coverage inventory
by combining the already-merged Bab 1 artifacts with newly extracted Babs 2-14. This does NOT
create Chinese LLM-ready records, does NOT rewrite any PDF, and does NOT produce a corrected
translation. Chinese is an internal working/reference translation only — NOT official, NOT binding;
Arabic is governing. Not legal advice.

Babs 1-3 carry per-article `第N条（Title）` headings. Babs 4-14 are thematic-table / summary-style
(the PDFs state "以专题表格呈现" / summary of core provisions); per-article text is only partially
isolable via inline `(N)` markers — recorded honestly (extraction_confidence, coverage_posture),
never fabricated.

Reads : inputs/chinese_translation_source_pdfs/saudi_companies_law_ar_zh_bab{1..14}*.pdf
        data/chinese_translation_sources/bab1_zh_source_extracted_articles_001_034.json (reuse)
        reports/chinese_translation_review/bab1_original_pdf_translation_review.json (reuse)
        data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json
Writes: data/chinese_translation_sources/bab{2..14}_zh_source_extracted_articles_*.json
        reports/chinese_translation_review/chinese_all_babs_source_inventory.json
        reports/chinese_translation_review/chinese_article_coverage_index_001_281.json
        reports/chinese_translation_review/CHINESE_ALL_BABS_SOURCE_INVENTORY_AR.md
"""

from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT, "inputs", "chinese_translation_source_pdfs")
SRC_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
RV_DIR = os.path.join(ROOT, "reports", "chinese_translation_review")
BAB1_EX = os.path.join(SRC_DIR, "bab1_zh_source_extracted_articles_001_034.json")
BAB1_REVIEW = os.path.join(RV_DIR, "bab1_original_pdf_translation_review.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
INV_JSON = os.path.join(RV_DIR, "chinese_all_babs_source_inventory.json")
IDX_JSON = os.path.join(RV_DIR, "chinese_article_coverage_index_001_281.json")
MD = os.path.join(RV_DIR, "CHINESE_ALL_BABS_SOURCE_INVENTORY_AR.md")

STAGE = "CHINESE_ALL_BABS_SOURCE_INVENTORY"
TARGET = 281

# bab_number: (lo, hi, pdf_basename, mode, extracted_basename)
BABS = {
    1: (1, 34, "saudi_companies_law_ar_zh_bab1_full.pdf", "reuse",
        "bab1_zh_source_extracted_articles_001_034.json"),
    2: (35, 50, "saudi_companies_law_ar_zh_bab2_full.pdf", "per_article",
        "bab2_zh_source_extracted_articles_035_050.json"),
    3: (51, 57, "saudi_companies_law_ar_zh_bab3.pdf", "per_article",
        "bab3_zh_source_extracted_articles_051_057.json"),
    4: (58, 137, "saudi_companies_law_ar_zh_bab4.pdf", "thematic",
        "bab4_zh_source_extracted_articles_058_137.json"),
    5: (138, 155, "saudi_companies_law_ar_zh_bab5.pdf", "thematic",
        "bab5_zh_source_extracted_articles_138_155.json"),
    6: (156, 184, "saudi_companies_law_ar_zh_bab6.pdf", "thematic",
        "bab6_zh_source_extracted_articles_156_184.json"),
    7: (185, 196, "saudi_companies_law_ar_zh_bab7.pdf", "thematic",
        "bab7_zh_source_extracted_articles_185_196.json"),
    8: (197, 215, "saudi_companies_law_ar_zh_bab8.pdf", "thematic",
        "bab8_zh_source_extracted_articles_197_215.json"),
    9: (216, 219, "saudi_companies_law_ar_zh_bab9.pdf", "thematic",
        "bab9_zh_source_extracted_articles_216_219.json"),
    10: (220, 234, "saudi_companies_law_ar_zh_bab10.pdf", "thematic",
         "bab10_zh_source_extracted_articles_220_234.json"),
    11: (235, 241, "saudi_companies_law_ar_zh_bab11.pdf", "thematic",
         "bab11_zh_source_extracted_articles_235_241.json"),
    12: (242, 259, "saudi_companies_law_ar_zh_bab12.pdf", "thematic",
         "bab12_zh_source_extracted_articles_242_259.json"),
    13: (260, 271, "saudi_companies_law_ar_zh_bab13.pdf", "thematic",
         "bab13_zh_source_extracted_articles_260_271.json"),
    14: (272, 281, "saudi_companies_law_ar_zh_bab14.pdf", "thematic",
         "bab14_zh_source_extracted_articles_272_281.json"),
}

# genuinely-trailing sections only (NOT the top disclaimer 译者声明, and not bare 术语/注释)
_CUT = ("译者战略性注释", "战略性注释", "公司法术语表", "公司治理与责任术语表", "译文审校记录",
        "术语表")
_U = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def _sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def _int2cjk(n):
    if n < 10:
        return list(_U.keys())[n - 1]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + list(_U.keys())[n - 11]
    if n < 100:
        t, u = divmod(n, 10)
        return list(_U.keys())[t - 1] + "十" + (list(_U.keys())[u - 1] if u else "")
    h, rem = divmod(n, 100)
    s = list(_U.keys())[h - 1] + "百"
    if rem == 0:
        return s
    if rem < 10:
        return s + "零" + list(_U.keys())[rem - 1]
    t, u = divmod(rem, 10)
    return s + (list(_U.keys())[t - 1] if t else "") + "十" + (list(_U.keys())[u - 1] if u else "")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _pdf_text(path):
    from pypdf import PdfReader
    reader = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in reader.pages), len(reader.pages)


def _cjk_body(text):
    """Keep CJK-dominant lines; drop the garbled Arabic column, page headers, trailing notes."""
    for mk in _CUT:
        # keep the disclaimer (译者声明) intro out of article bodies later; cut trailing sections
        pass
    lines = []
    for line in text.split("\n"):
        cjk = len(re.findall(r"[一-鿿]", line))
        ar = len(re.findall(r"[؀-ۿ]", line))
        if cjk >= ar:
            lines.append(line)
    s = "\n".join(lines)
    s = re.sub(r"·?\s*沙特公司法[^\n]*", " ", s)
    s = re.sub(r"Saudi Companies Law", " ", s)
    s = re.sub(r"\d+\s*/\s*\d+", " ", s)
    return s


def _clean(seg):
    for mk in _CUT:
        i = seg.find(mk)
        if i != -1:
            seg = seg[:i]
    s = re.sub(r"\s*\n\s*", "", seg)
    s = re.sub(r"[ \t]+", " ", s).strip().lstrip("：:").strip()
    return s


def _extract_per_article(text, lo, hi):
    """Babs 1-3: segment by 第N条（Title） headings (+ clause-form fallback e.g. Art 50)."""
    anchors = []  # (pos, n, heading_title)
    for n in range(lo, hi + 1):
        cjk = _int2cjk(n)
        m = re.search(r"第" + cjk + r"条（([^）]*)）", text)
        if m:
            anchors.append((m.start(), n, m.group(1).strip()))
            continue
        # clause-form heading, e.g. 第五十条 — 第（1）款（存续原则）
        m = re.search(r"第" + cjk + r"条\s*[—-]", text)
        if m:
            t = re.search(r"（([^）]*)）", text[m.start():m.start() + 40])
            anchors.append((m.start(), n, (t.group(1).strip() if t else "")))
    anchors.sort()
    recs = {}
    for i, (pos, n, title) in enumerate(anchors):
        nxt = anchors[i + 1][0] if i + 1 < len(anchors) else len(text)
        # body starts after the heading line
        seg = text[pos:nxt]
        seg = re.sub(r"^第[^\n]*", "", seg, count=1)
        recs[n] = {"heading": title, "text": _clean(seg), "confidence": "high"}
    return recs


def _extract_thematic(text, lo, hi):
    """Babs 4-14: thematic-table summary; isolate per-article chunks via inline (N)/(N/k) markers.

    Articles without a distinct marker are covered only within a thematic group summary — recorded
    with empty text + a note (never fabricated)."""
    body = _cjk_body(text)
    # cut trailing translator-note / glossary / revision-log sections
    for mk in _CUT:
        j = body.find(mk)
        if j != -1:
            body = body[:j]
    # Chinese has no inter-character spaces: join wrapped lines so markers split across a line
    # break (e.g. "(218/\n1)") stay intact for detection.
    body = re.sub(r"\s*\n\s*", "", body)
    marks = []
    for m in re.finditer(r"[（(](\d{1,3})(?:\s*/\s*\d+)?[）)]", body):
        n = int(m.group(1))
        if lo <= n <= hi:
            marks.append((m.start(), n))
    # chunk text between consecutive in-range markers; group repeats of same n
    recs = {}
    for i, (pos, n) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        seg = body[pos:nxt].strip()
        recs.setdefault(n, []).append(seg)
    out = {}
    for n in range(lo, hi + 1):
        if n in recs:
            out[n] = {"heading": "", "text": " ".join(recs[n]).strip(), "confidence": "medium"}
        else:
            out[n] = {"heading": "", "text": "", "confidence": "low"}
    return out


def _bab_extraction(bnum):
    lo, hi, pdf, mode, exbase = BABS[bnum]
    path = os.path.join(PDF_DIR, pdf)
    text, pages = _pdf_text(path)
    if mode == "per_article":
        seg = _extract_per_article(text, lo, hi)
    else:
        seg = _extract_thematic(text, lo, hi)
    records = []
    for n in range(lo, hi + 1):
        s = seg.get(n, {"heading": "", "text": "", "confidence": "low"})
        note = ("clean 第N条 per-article heading segmentation" if mode == "per_article"
                else ("thematic-table summary; isolated via inline (N) marker" if s["text"]
                      else "no distinct per-article segment; covered within the Bab's thematic-"
                           "table summary group (not fabricated)"))
        records.append({
            "article_number": n,
            "chinese_heading": s["heading"],
            "chinese_text": s["text"],
            "extraction_method": ("pypdf_text_layer + 第N条 heading segmentation"
                                  if mode == "per_article"
                                  else "pypdf_text_layer + thematic-table inline (N) marker"),
            "extraction_confidence": s["confidence"] if s["text"] else "low",
            "extraction_notes": note,
        })
    return records, pages, path, mode


def _write_extracted(bnum, records, pages, path):
    lo, hi, pdf, mode, exbase = BABS[bnum]
    payload = {
        "source_file": "inputs/chinese_translation_source_pdfs/%s" % pdf,
        "source_language": "zh",
        "source_status": "internal_working_translation_source",
        "governing_text_language": "ar",
        "official_translation": False,
        "not_binding": True,
        "not_full_legal_translation_claimed": True,
        "bab_number": bnum,
        "expected_article_range": [lo, hi],
        "source_pdf_sha256": _sha256_file(path),
        "source_pdf_page_count": pages,
        "article_count": len(records),
        "records": records,
    }
    with open(os.path.join(SRC_DIR, exbase), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def build():
    os.makedirs(SRC_DIR, exist_ok=True)
    os.makedirs(RV_DIR, exist_ok=True)

    # -- per-Bab extraction (Bab 1 reused) --
    bab_records = {}
    bab_pages = {}
    bab_sha = {}
    for bnum in range(2, 15):
        recs, pages, path, mode = _bab_extraction(bnum)
        _write_extracted(bnum, recs, pages, path)
        bab_records[bnum] = recs
        bab_pages[bnum] = pages
        bab_sha[bnum] = _sha256_file(path)
    # Bab 1: reuse existing extracted file + review
    bab1 = _read(BAB1_EX)
    bab_records[1] = bab1["records"]
    bab_pages[1] = bab1.get("source_pdf_page_count")
    bab_sha[1] = bab1.get("source_pdf_sha256") or _sha256_file(
        os.path.join(PDF_DIR, BABS[1][2]))
    bab1_review = {r["article_number"]: r for r in _read(BAB1_REVIEW)["records"]}

    style_by_mode = {"reuse": "mixed_full_and_summary",
                     "per_article": "mostly_aligned_but_condensed",
                     "thematic": "summary_or_core_terms"}

    # -- master inventory (per Bab) --
    babs_out = []
    coverage = []
    for bnum in range(1, 15):
        lo, hi, pdf, mode, exbase = BABS[bnum]
        recs = bab_records[bnum]
        nums = [r["article_number"] for r in recs]
        exp = list(range(lo, hi + 1))
        nonempty = [r["article_number"] for r in recs if (r.get("chinese_text") or "").strip()]
        missing = [n for n in exp if n not in nums]
        dups = sorted({n for n in nums if nums.count(n) > 1})
        if mode == "thematic":
            status = "extraction_unclear_needs_manual_review"
        elif missing:
            status = "extracted_with_missing_articles"
        else:
            status = "extracted_exact_range"
        style = style_by_mode[mode]
        posture = ("per_article_mixed_full_and_summary" if bnum == 1 else
                   "per_article_condensed" if mode == "per_article" else
                   "thematic_table_summary_partial_per_article")
        action = ("semantic_review_then_expand_condensed_before_llm_ready" if mode != "thematic"
                  else "expand_from_arabic_official_text_before_llm_ready_(thematic_summary)")
        babs_out.append({
            "bab_number": bnum,
            "source_pdf": "inputs/chinese_translation_source_pdfs/%s" % pdf,
            "source_pdf_sha256": bab_sha[bnum],
            "expected_article_range": [lo, hi],
            "extracted_article_count": len(nums),
            "extracted_article_numbers": nums,
            "missing_article_numbers": missing,
            "duplicate_article_numbers": dups,
            "articles_with_nonempty_chinese_text": len(nonempty),
            "extraction_status": status,
            "coverage_posture": posture,
            "likely_translation_style": style,
            "ready_for_chinese_llm_ready": False,
            "recommended_next_action": action,
        })
        # coverage index rows
        for r in recs:
            n = r["article_number"]
            nonemp = bool((r.get("chinese_text") or "").strip())
            if bnum == 1 and n in bab1_review:
                conf = "high"
                style_a = "mixed_full_and_summary"
                posture_a = bab1_review[n]["coverage_status"]
                usable = bab1_review[n]["usable_as_internal_reference"]
            else:
                conf = r.get("extraction_confidence", "low")
                style_a = style
                posture_a = posture
                usable = nonemp
            coverage.append({
                "article_number": n,
                "expected_bab_number": bnum,
                "source_pdf": "inputs/chinese_translation_source_pdfs/%s" % pdf,
                "source_extracted_file": "data/chinese_translation_sources/%s" % exbase,
                "chinese_source_present": True,
                "chinese_text_nonempty": nonemp,
                "extraction_confidence": conf,
                "coverage_posture": posture_a,
                "likely_translation_style": style_a,
                "llm_ready_as_full_translation": False,
                "usable_as_internal_reference": bool(usable),
                "recommended_next_action": action,
            })
    coverage.sort(key=lambda r: r["article_number"])

    extracted_total = sum(b["extracted_article_count"] for b in babs_out)
    nonempty_total = sum(1 for r in coverage if r["chinese_text_nonempty"])
    unclear = [b["bab_number"] for b in babs_out
               if b["extraction_status"] == "extraction_unclear_needs_manual_review"]
    review_summary = {
        "expected_article_total": TARGET,
        "extracted_article_total": extracted_total,
        "articles_with_nonempty_chinese_text": nonempty_total,
        "articles_missing_chinese_text": TARGET - nonempty_total,
        "babs_extracted_exact_range": [b["bab_number"] for b in babs_out
                                       if b["extraction_status"] == "extracted_exact_range"],
        "babs_extraction_unclear": unclear,
        "articles_llm_ready_as_full_translation": 0,
        "overall_note_ar": "أُنجز جرد مصادر الأبواب الصينية 1–14 لكامل نطاق 1–281. الأبواب 1–3 "
                           "مقسّمة مادةً بمادة؛ الأبواب 4–14 بأسلوب جداول موضوعية/تلخيصية "
                           "(تغطية جزئية على مستوى المادة). لا يصلح لإنشاء طبقة Chinese LLM-ready "
                           "كاملة الآن؛ يلزم مراجعة دلالية/توسعة من النص العربي الرسمي أولًا.",
    }

    inv = {
        "stage": STAGE,
        "not_legal_advice": True,
        "source_pdf_count": 14,
        "expected_bab_count": 14,
        "expected_article_total": TARGET,
        "extracted_article_total": extracted_total,
        "full_article_range": [1, TARGET],
        "governing_language": "ar",
        "chinese_source_status": "internal_working_translation_source",
        "official_chinese_translation_claimed": False,
        "chinese_binding_claimed": False,
        "full_translation_claimed": False,
        "chinese_llm_ready_created": False,
        "babs": babs_out,
        "article_coverage_index": "reports/chinese_translation_review/"
                                  "chinese_article_coverage_index_001_281.json",
        "review_summary": review_summary,
    }
    with open(INV_JSON, "w", encoding="utf-8") as fh:
        json.dump(inv, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    idx = {
        "stage": STAGE,
        "not_legal_advice": True,
        "governing_language": "ar",
        "chinese_source_status": "internal_working_translation_source",
        "official_chinese_translation_claimed": False,
        "chinese_binding_claimed": False,
        "full_translation_claimed": False,
        "chinese_llm_ready_created": False,
        "article_count": len(coverage),
        "article_range": [1, TARGET],
        "records": coverage,
    }
    with open(IDX_JSON, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    _write_md(inv, babs_out, review_summary)
    print("wrote Chinese all-Babs inventory: 14 Babs, %d extracted articles, %d with text; "
          "unclear Babs=%s" % (extracted_total, nonempty_total, unclear))


def _write_md(inv, babs_out, summary):
    L = []
    L.append("# جرد مصادر الأبواب الصينية 1–14")
    L.append("# Chinese all-Babs (1–14) source inventory")
    L.append("")
    L.append("> **هذا جرد مصدر/مراجعة تغطية فقط، وليس ترجمة رسمية ولا استشارة قانونية.** لم يُنشأ "
             "أي سجل Chinese LLM-ready، ولم تُصحَّح ترجمة، ولم يُعدَّل أي ملف PDF.")
    L.append("")
    L.append("## ملخص / Summary")
    L.append("")
    L.append("- تم جرد **ملفات الأبواب الصينية 1–14** (عدد ملفات PDF: **%d**)."
             % inv["source_pdf_count"])
    L.append("- **نطاق المواد المتوقع:** 1–281.")
    L.append("- **هل كل المواد لها مصدر صيني مستخرج؟** كل مادة ضمن باب PDF محفوظ يغطي نطاقها؛ "
             "**نص صيني على مستوى المادة متوفر لـ %d/281**، والباقي مُغطّى ضمن ملخصات جداول "
             "موضوعية (تغطية جزئية)." % summary["articles_with_nonempty_chinese_text"])
    L.append("- **الصينية ليست رسمية** (`official_translation = false`).")
    L.append("- **الصينية ليست حاكمة؛ العربية هي النص الحاكم** (`governing = ar`).")
    L.append("- **لم يتم إنشاء Chinese LLM-ready في هذه المرحلة** "
             "(`chinese_llm_ready_created = false`؛ `llm_ready_as_full_translation = false` "
             "لكل 281).")
    L.append("")
    L.append("## جدول الأبواب / Per-Bab table")
    L.append("")
    L.append("| الباب | نطاق المواد | مستخرَجة | نص صيني | حالة الاستخراج | نمط الترجمة | الإجراء التالي |")
    L.append("|---|---|---|---|---|---|---|")
    for b in babs_out:
        L.append("| %d | %d–%d | %d | %d | `%s` | `%s` | `%s` |" % (
            b["bab_number"], b["expected_article_range"][0], b["expected_article_range"][1],
            b["extracted_article_count"], b["articles_with_nonempty_chinese_text"],
            b["extraction_status"], b["likely_translation_style"],
            b["recommended_next_action"]))
    L.append("")
    L.append("## تغطية عامة / Overall coverage")
    L.append("")
    L.append("- **مواد ذات نص صيني مستخرج / articles with extracted Chinese text:** %d/281"
             % summary["articles_with_nonempty_chinese_text"])
    L.append("- **مواد بلا نص صيني على مستوى المادة (ضمن ملخص موضوعي) / without per-article text:** "
             "%d" % summary["articles_missing_chinese_text"])
    L.append("- **أبواب باستخراج غير واضح (جداول موضوعية) / extraction-unclear Babs:** %s"
             % ", ".join(str(x) for x in summary["babs_extraction_unclear"]))
    L.append("- **مواد مرشحة للمراجعة/التوسعة قبل LLM-ready / candidates before LLM-ready:** 281 "
             "(جميعها؛ `llm_ready_as_full_translation = false`).")
    L.append("")
    L.append("## التوصية للمرحلة التالية / Recommendation")
    L.append("")
    L.append("لا يُنصح بإنشاء طبقة Chinese LLM-ready كاملة قبل تثبيت خريطة التغطية والتفريق بين "
             "النصوص الكاملة والنصوص المختصرة/الملخصة. المرحلة التالية يجب أن تكون إما مراجعة "
             "دلالية للمواد ذات التغطية الكاملة أو توسعة المواد المختصرة من النص العربي الرسمي.")
    L.append("")
    L.append("**العربية هي اللغة الحاكمة. الصينية ترجمة داخلية غير رسمية وغير مُلزِمة. "
             "ليست استشارة قانونية.**")
    L.append("Arabic is governing. Chinese is an internal, non-official, non-binding working "
             "translation. Not legal advice.")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    build()


if __name__ == "__main__":
    main()
