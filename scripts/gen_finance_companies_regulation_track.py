#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the track for the Implementing Regulation of the Finance
Companies Control Law (اللائحة التنفيذية لنظام مراقبة شركات التمويل).

VERIFICATION TIER -- see sources/finance_companies_regulation/law/
official_source/finance_companies_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE, DIRECT FETCH SUCCEEDED THIS PASS: fetched directly via curl
(HTTP 200, 17,522,441 bytes, 38 pages) from bfc.gov.sa's own RulesandRegulations1
document path -- the same host already confirmed reachable and used as primary
source by the sibling finance_companies_law track's own disclosure of this
Regulation as an out-of-scope candidate.

CRITICAL DATING DISCOVERY: the PDF's own creation-date metadata (pdfinfo) reads
"Mon Dec 22 17:14:22 2025 UTC". Page 1 of the file is not a regulation cover
page but a SAMA circular (تعميم رقم 472038006، تاريخ 1447/07/02هـ = 22/12/2025G)
transmitting Governor's Decision No. (179/م ش ت) approving substantial
amendments to this Regulation and repealing two companion rule-sets (microfinance
practice rules 80/م ش ت 1441H, and micro consumer finance company rules
82/م ش ت 1441H). This independently confirms -- via the primary document itself,
not merely secondary reporting -- the ~Dec-2025 SAMA update flagged in this
pass's brief. Decision No. 179/م ش ت itself was cross-verified via multiple
independent secondary sources (qanoonsa.com, spa.gov.sa official news agency,
argaam.com, aawsat.com, cnbcarabia.com), all describing the same 22/12/2025
update with matching substantive scope (activity-practice requirements,
aggregate financing caps, licensing bank-guarantee amounts, related-party
provisions, license-termination clarifications).

TEXT EXTRACTION METHOD: pure image-scanned PDF, NO extractable text layer
(confirmed: pdftotext output ~38 near-empty lines for the whole file). All 38
pages rendered at 200dpi (pdftoppm) and read visually, page by page, by the
auditing agent -- no OCR, no guessed character correction.

106 records, ALL اصلية (as CURRENTLY governing text) across 22 أبواب (Parts),
one of which -- الباب الحادي عشر (سياسات التمويل وإجراءاته, arts 56-68) -- is
itself subdivided into 3 فصول (Chapters). consolidated_amended_law=True: this
is a post-amendment consolidated re-issuance with NO per-article amendment
markers in the source itself, and no prior (pre-Dec-2025) version of this
Regulation's text was available this pass for an article-level diff -- so no
individual article is tagged معدلة/مضافة; this constraint is disclosed, not
silently assumed away. See known_unresolved_discrepancies for this and other
limitations (decision-number sourced from secondary confirmation rather than
the circular's own text; sama.gov.sa's own PDF and rulebook.sama.gov.sa's
JS-rendered page were not usable as direct textual cross-checks this pass;
the Article 85 APR formula is a best-effort text rendering of a printed
mathematical expression).

Read-only over input; deterministic over outputs. Arabic governs; no
translation/paraphrase/interpretation performed on the Arabic text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_companies_regulation", "law", "official_source",
                   "finance_companies_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "finance_companies_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "finance_companies_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "finance_companies_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "finance_companies_regulation_arabic_legal_llm",
                        "finance_companies_regulation_legal_llm_001_106.json")

LAW_ID = "sa-finance-companies-regulation-2-m-sh-t-1434"
LAW_AR = "اللائحة التنفيذية لنظام مراقبة شركات التمويل"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"finance_companies_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم البنك شركة التمويل الشركة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    governing_source_note = (
        "Arabic governs; full text fetched directly via curl (HTTP 200) from bfc.gov.sa's own "
        "RulesandRegulations1 document path (not a mirror/aggregator; the same host already "
        "confirmed reachable for this exact document by the sibling finance_companies_law track). "
        "The PDF is a pure image scan with NO extractable text layer; every article was transcribed "
        "by directly reading the rendered page images (200dpi), not OCR or guessed reconstruction. "
        "The PDF's own creation-date metadata (22 Dec 2025 UTC) and its first page (a SAMA circular, "
        "No. 472038006, dated 2/7/1447H) independently confirm this is the Dec-2025 consolidated "
        "re-issuance (Governor's Decision 179/M SH T) -- cross-verified against five independent "
        "secondary sources (qanoonsa.com, spa.gov.sa, argaam.com, aawsat.com, cnbcarabia.com). This "
        "is a consolidated_amended_law=True track: no prior (pre-Dec-2025) text was available this "
        "pass for an article-level amendment diff, so no individual article carries a معدلة/مضافة "
        "tag; see known_unresolved_discrepancies in the source artifact before relying on this "
        "track's provenance for article-level amendment attribution."
    )
    source_authority_ar = (
        "قرار محافظ البنك المركزي السعودي رقم (179/م ش ت) عبر التعميم رقم (472038006) وتاريخ "
        "2/7/1447هـ (الموافق 22/12/2025م)، بموجب الصلاحيات المخولة بنظام مراقبة شركات التمويل "
        "(المرسوم الملكي رقم م/51 وتاريخ 13/8/1433هـ) -- النص الكامل جُلب مباشرة (HTTP 200) من "
        "bfc.gov.sa؛ الملف صورة ممسوحة ضوئياً بالكامل، وكل مادة قُرئت مباشرة من صور الصفحات "
        "المصورة (200dpi) تفادياً لأي تخمين. هذه نسخة موحّدة بعد تعديل جوهري مؤكد "
        "(consolidated_amended_law=true)؛ لم يتوفر نص سابق للمقارنة على مستوى المادة المفردة."
    )

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        ver.append({"law_key": "finance_companies_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "FINANCE_COMPANIES_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": governing_source_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "finance-companies-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "finance_companies_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مراقبة شركات التمويل" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                                        "Governor's Decision No. (179/M SH T) via Circular No. "
                                        "(472038006) dated 2/7/1447H (22/12/2025G), under the "
                                        "Finance Companies Control Law (Royal Decree M/51, "
                                        "13/8/1433H) -- full text fetched directly (HTTP 200) from "
                                        "bfc.gov.sa; the PDF is a pure image scan, every article "
                                        "read directly from rendered page images; consolidated "
                                        "post-amendment re-issuance, no prior text available this "
                                        "pass for article-level diff"),
                                     "source_authority_ar": source_authority_ar,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "finance_companies_regulation",
               "layer": "FINANCE_COMPANIES_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-finance-companies-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (106 مواد؛ 106 أصلية)",
               "title_en": ("Implementing Regulation of the Finance Companies Control Law — Arabic "
                            "LLM-ready layer (106 records: 106 original/currently-governing)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 106], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Finance Companies Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
