#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chinese internal LLM-ready candidate layer — isolable-source articles only.

Builds an internal, non-official Chinese LLM/RAG candidate layer from ONLY the articles that have
isolable per-article Chinese source text (chinese_text_nonempty = true in the coverage index). Each
record carries the VERBATIM Chinese source text (copied exactly from the extracted Chinese source
JSON) plus mechanical retrieval metadata. It does NOT translate, expand, correct, summarize, or
improve the Chinese, and it does NOT generate Chinese from Arabic or English. The 92 thematic-
summary-group articles (no isolable per-article text) are EXCLUDED — never fabricated.

Chinese is an internal working/reference translation only — NOT official, NOT binding, NOT
governing; the Arabic text is governing. This is NOT a full verified Chinese translation. Not
legal advice.

Reads : reports/chinese_translation_review/chinese_article_coverage_index_001_281.json
        data/chinese_translation_sources/bab*_zh_source_extracted_articles_*.json
Writes: data/chinese_internal_legal_llm/
          companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json
        reports/chinese_translation_review/CHINESE_INTERNAL_LLM_READY_ISOLABLE_189_AR.md
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
INV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_all_babs_source_inventory.json")
SRC_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
OUT_DIR = os.path.join(ROOT, "data", "chinese_internal_legal_llm")
OUT = os.path.join(OUT_DIR,
                   "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_INTERNAL_LLM_READY_ISOLABLE_189_AR.md")

LAW_ID = "sa-companies-law-m132-1443"
EXPECTED = 189
EXCLUDED_REASON = "thematic_summary_group_covered_no_isolable_article_text"
_TRUST_NOTE = ("Chinese text is an internal working/reference translation candidate copied from "
               "the owner-provided Chinese source PDFs. It is not official, not binding, not "
               "governing, and not claimed as full verified legal translation.")
# conservative Chinese stopwords for heading-derived keywords
_STOP = {"的", "与", "及", "和", "或", "第", "条", "公司", "之"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _source_maps():
    """article_number -> (chinese_text, chinese_heading) from extracted source files."""
    out = {}
    for f in glob.glob(os.path.join(SRC_DIR, "bab*_zh_source_extracted_articles_*.json")):
        d = _read(f)
        for r in d["records"]:
            out[r["article_number"]] = (r.get("chinese_text") or "",
                                        r.get("chinese_heading") or "")
    return out


def _keywords(heading):
    """Conservative heading-derived keywords (may be empty). No invented legal conclusions."""
    if not heading:
        return []
    toks = re.split(r"[、，,；;（）()\s/]+", heading)
    out = []
    for t in toks:
        t = t.strip()
        if len(t) >= 2 and t not in _STOP and t not in out:
            out.append(t)
    return out


def _search_queries(n, heading):
    q = ["沙特公司法 第%d条" % n, "公司法 第%d条" % n]
    h = (heading or "").strip()
    if h:
        q.append("公司法 第%d条 %s" % (n, h))
    seen, out = set(), []
    for x in q:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def build():
    idx = _read(IDX)
    src = _source_maps()

    records = []
    excluded = []
    for cov in idx["records"]:
        n = cov["article_number"]
        zh_text, heading = src.get(n, ("", ""))
        include = cov.get("chinese_text_nonempty") and zh_text.strip()
        if not include:
            excluded.append(n)
            continue
        title = "公司法 第%d条" % n + (" — %s" % heading if heading else "")
        records.append({
            "law_id": LAW_ID,
            "article_number": n,
            "expected_bab_number": cov["expected_bab_number"],
            "record_id": "zh-int-companies-art-%03d" % n,
            "record_type": "chinese_internal_reference_article",
            "language": "zh",
            "governing_text_language": "ar",
            "chinese_text": zh_text,
            "chinese_text_hash_sha256": _sha256(zh_text),
            "llm_title_zh": title,
            "retrieval_title_zh": "沙特公司法 - 第%d条" % n + (" - %s" % heading if heading else ""),
            "article_path": "companies_law/articles/%03d/zh/internal" % n,
            "keywords_zh": _keywords(heading),
            "search_queries_zh": _search_queries(n, heading),
            "source_coverage": {
                "source_pdf": cov["source_pdf"],
                "source_extracted_file": cov["source_extracted_file"],
                "chinese_text_nonempty": True,
                "extraction_confidence": cov["extraction_confidence"],
                "coverage_posture": cov["coverage_posture"],
                "likely_translation_style": cov["likely_translation_style"],
                "llm_ready_as_full_translation": False,
                "usable_as_internal_reference": bool(cov.get("usable_as_internal_reference")),
                "recommended_next_action": cov["recommended_next_action"],
            },
            "source_trust": {
                "chinese_source_status": "internal_working_translation_source",
                "official_translation": False,
                "not_binding": True,
                "governing_text_language": "ar",
                "full_translation_claimed": False,
                "internal_reference_only": True,
                "arabic_governs": True,
                "notes": _TRUST_NOTE,
            },
        })

    payload = {
        "layer_id": "sa-companies-chinese-internal-legal-llm-isolable",
        "law_id": LAW_ID,
        "language": "zh",
        "governing_text_language": "ar",
        "title_en": "Companies Law — Chinese internal LLM-ready candidate layer (isolable-source "
                    "articles only)",
        "source_layer": "data/chinese_translation_sources/ (owner-provided Chinese Bab PDFs, "
                        "extracted)",
        "source_inventory_file": "reports/chinese_translation_review/"
                                 "chinese_all_babs_source_inventory.json",
        "article_coverage_index_file": "reports/chinese_translation_review/"
                                       "chinese_article_coverage_index_001_281.json",
        "candidate_record_count": len(records),
        "expected_candidate_record_count": EXPECTED,
        "excluded_article_count": len(excluded),
        "excluded_articles": excluded,
        "excluded_reason_summary": EXCLUDED_REASON,
        "full_chinese_translation_claimed": False,
        "official_chinese_translation_claimed": False,
        "chinese_binding_claimed": False,
        "chinese_governing_claimed": False,
        "not_legal_advice": True,
        "disclaimer_en": "Internal Chinese LLM-ready candidate layer for isolable-source articles "
                         "only. Chinese is an internal working/reference translation — not "
                         "official, not binding, not governing. chinese_text is copied verbatim "
                         "from the extracted Chinese source; nothing is translated, expanded, or "
                         "corrected. The Arabic text is governing. NOT a complete, verified "
                         "Chinese translation of the law. Not legal advice.",
        "records": records,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    _write_md(payload)
    print("wrote Chinese internal LLM-ready candidate layer: %d records, %d excluded"
          % (len(records), len(excluded)))
    return len(records), len(excluded)


def _write_md(p):
    L = []
    L.append("# طبقة صينية داخلية مرشحة — المواد ذات المصدر المستقل (189)")
    L.append("# Chinese internal LLM-ready candidate layer — isolable-source articles (189)")
    L.append("")
    L.append("> **هذه طبقة مرشحة داخلية فقط، وليست ترجمة رسمية ولا استشارة قانونية.** لم تُترجَم "
             "ولم تُوسَّع ولم تُصحَّح أي مادة؛ النص الصيني منسوخ حرفيًا من المصدر المستخرج.")
    L.append("")
    L.append("- **تم إنشاء طبقة مرشحة داخلية فقط** (`internal_reference_only = true`).")
    L.append("- **عدد المواد المرشحة:** %d." % p["candidate_record_count"])
    L.append("- **عدد المواد المستبعدة:** %d." % p["excluded_article_count"])
    L.append("- **سبب الاستبعاد:** لا يوجد نص صيني مستقل لكل مادة، بل تغطية ضمن جداول/ملخصات "
             "موضوعية (`%s`)." % p["excluded_reason_summary"])
    L.append("- **الصينية ليست رسمية ولا حاكمة** (`official_translation = false`، "
             "`chinese_governing_claimed = false`).")
    L.append("- **العربية هي النص الحاكم** (`governing_text_language = ar`).")
    L.append("- **لا يجوز اعتبار الطبقة ترجمة صينية كاملة للنظام** "
             "(`full_chinese_translation_claimed = false`؛ `llm_ready_as_full_translation = "
             "false` لكل السجلات).")
    L.append("")
    L.append("## المواد المستبعدة / Excluded articles (%d)" % p["excluded_article_count"])
    L.append("")
    L.append("المواد التالية مستبعدة لعدم وجود نص صيني مستقل على مستوى المادة "
             "(مُغطّاة ضمن ملخصات جداول موضوعية):")
    L.append("")
    L.append("`%s`" % ", ".join(str(x) for x in p["excluded_articles"]))
    L.append("")
    L.append("## المرحلة التالية / Next stage")
    L.append("")
    L.append("توسعة/إعادة ترجمة المواد المستبعدة أو المختصرة من النص العربي الرسمي قبل بناء طبقة "
             "281 صينية كاملة. لا تُبنى المحاذاة متعددة اللغات قبل تحديد نطاق الطبقة الصينية.")
    L.append("")
    L.append("**العربية هي اللغة الحاكمة. الصينية ترجمة داخلية غير رسمية وغير مُلزِمة. "
             "ليست ترجمة كاملة موثّقة. ليست استشارة قانونية.**")
    L.append("Arabic is governing. Chinese is an internal, non-official, non-binding working "
             "translation. Not a full verified translation. Not legal advice.")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    n, ex = build()
    if n != EXPECTED:
        raise SystemExit("BLOCKED_COUNT_MISMATCH: candidate_record_count=%d (expected %d); "
                         "excluded=%d" % (n, EXPECTED, ex))


if __name__ == "__main__":
    main()
