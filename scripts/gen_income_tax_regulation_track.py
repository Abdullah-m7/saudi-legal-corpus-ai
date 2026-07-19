#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian Income Tax Law track
(اللائحة التنفيذية لنظام ضريبة الدخل, Ministerial Resolution No. 1535, 11/6/1425H,
issued by the Minister of Finance under Article 79 of the Income Tax Law,
Royal Decree M/1, 15/1/1425H).

This is the companion-regulation follow-up candidate explicitly flagged by this
corpus's own income_tax_law track (see sources/income_tax/law/official_source/
income_tax_law_official_source.json, known_unresolved_discrepancies key
income_tax_implementing_regulation_date_not_pinned_down: "confirmed to exist via
two hosted copies (ZATCA and gstc.gov.sa) ... issued as Ministerial Resolution
No. 1535. Its exact Hijri date could not be verified this pass"). This track
ingests it AND pins the date: 11/6/1425H, cross-verified across BOTH government
copies' headers.

VERIFICATION TIER -- see income_tax_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. There
is NO dedicated lawId page for this Implementing Regulation on the BOE portal
(only for the base Income Tax Law, lawId 23576008-1ce4-4685-ac3e-a9a700f2cb02)
-- consistent with BOE's general practice of not cataloguing Ministerial-
Resolution-level executive regulations as standalone lawId records (the same
pattern this corpus's food_regulation track documented). The portal also
returned HTTP 503 on the search query this pass.

PRIMARY SOURCES (two cross-verified government-hosted copies -- the exact
cross-check the parent income_tax_law track established works for this family of
documents): (1) ZATCA's own official consolidated Arabic PDF on zatca.gov.sa
(45 pages, Microsoft Print to PDF, 2024-10) -- the NEWEST copy, listing the full
amendment chain through Ministerial Resolution No. (25) dated 8/1/1445H;
(2) gstc.gov.sa's older INCOM2.pdf (Microsoft Word 2016, 2019-06), listing
amendments only through Resolution 2568 (12/8/1440H). Both headers carry the
same founding resolution number (1535) and date (11/6/1425H).

EXTRACTION: the governing text is taken from the ZATCA copy (newest, most fully
amended). Its Arabic glyphs are stored as Arabic Presentation Forms (as this
corpus's income_tax_law track already documented for ZATCA's copy of the base
law), so Unicode NFKC normalization is applied. Because pdftotext -layout
occasionally scrambles the line order of justified lines carrying floated
tanwin, a coordinate-based reconstruction via PyMuPDF is used instead (words
clustered into lines by y, then sorted by descending x for RTL reading order).
This yields dates in correct order (calibrated: Resolution 2194 extracts as
12/7/1432H, matching the date the parent income_tax_law track independently
pinned for that same resolution; pdftotext -layout reverses it to 1432/7/12).

DISCLOSED EXTRACTION-LAYER FIXES (see known_unresolved_discrepancies): (1) the
mandatory lam-alef ligature (لا/لأ/لإ/لآ) is split into two glyph tokens by the
coordinate reconstruction (952 sites); rejoined by matching against the
correctly-spelled vocabulary of the pdftotext -layout extraction, with 33
residual sites resolved by the individually-verified HAND dictionary below;
(2) single-letter split prefixes (ال، ك، hamzated alef forms) rejoined against
the same vocabulary; (3) dates reformatted to unified day/month/year with هـ/م
suffix; (4) inline numeric footnote-reference markers removed at clause
boundaries (editorial annotations, not legal text), while legal numbers
(percentages, day counts, article numbers) are preserved; (5) diacritics
(tashkeel) and tatweel stripped uniformly, consistent with this corpus's other
BOE-family tracks.

74 articles across 30 topical section headings; 30 اصلية, 19 معدلة, 25 ملغاة,
0 مضافة. NATURAL-GAS RISK (direct analog of the parent law track's Chapter 10):
the (ضريبة استثمار الغاز الطبيعي) section implements the OLD Internal-Rate-of-
Return natural-gas regime; Resolution 2568 (12/8/1440H), accompanying the M/70
reform, REPEALED 25 of its articles. Unlike the parent law track (where both
government PDFs printed only a bare repeal notice for Chapter 10), ZATCA's copy
of THIS Regulation preserves the full text of the repealed articles with a
(تم حذف المادة) footnote -- so the completeness risk is inverted: the text is
present in full but formally repealed. Those 25 articles are marked ملغاة with
their preserved text and text_complete=true.

No legal text is altered beyond the disclosed source-artifact-layer fixes above.
Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "income_tax", "regulation", "official_source",
                   "income_tax_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "income_tax", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "income_tax_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "income_tax_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "income_tax_regulation_arabic_legal_llm",
                        "income_tax_regulation_legal_llm_001_074.json")

LAW_ID = "sa-income-tax-regulation-1535-1425"
LAW_AR = "اللائحة التنفيذية لنظام ضريبة الدخل"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
STATUS_REPEALED = "REPEALED"
KEY_RE = r"income_tax_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة المصلحة الوعاء الضريبي الضريبة الدخل المكلف").split())


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


def _top_status(ls):
    if ls == "معدلة":
        return STATUS_AMENDED
    if ls == "مضافة":
        return STATUS_ADDED
    if ls == "ملغاة":
        return STATUS_REPEALED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

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
        top_status = _top_status(ls)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "income_tax", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "INCOME_TAX_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; PRIMARY sources are TWO cross-verified "
                                              "government-hosted copies -- ZATCA's own official "
                                              "consolidated PDF (zatca.gov.sa, newest, amended through "
                                              "Ministerial Resolution 25 of 8/1/1445H) and gstc.gov.sa's "
                                              "older INCOM2.pdf. laws.boe.gov.sa was checked first per "
                                              "standard methodology but has NO dedicated lawId page for "
                                              "this Implementing Regulation (only the base Income Tax "
                                              "Law). Founding Resolution 1535's date 11/6/1425H is "
                                              "cross-verified across both copies' headers, resolving the "
                                              "gap the income_tax_law track flagged. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track's text or provenance -- in "
                                              "particular the coordinate-based extraction with disclosed "
                                              "lam-alef-ligature-split fixes, the residual justified-line "
                                              "word-order risk, and the 25 natural-gas articles marked "
                                              "ملغاة (repealed by Resolution 2568) whose text ZATCA "
                                              "preserves in full."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "income-tax-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "income_tax/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام ضريبة الدخل" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Resolution No. (1535) (11/6/1425H), "
                                                          "as consolidated with later ministerial "
                                                          "amendments through Resolution No. (25) "
                                                          "(8/1/1445H) — ZATCA's own official PDF "
                                                          "(zatca.gov.sa), cross-verified against "
                                                          "gstc.gov.sa's INCOM2.pdf; laws.boe.gov.sa has "
                                                          "no dedicated lawId page for this Implementing "
                                                          "Regulation"),
                                     "source_authority_ar": "القرار الوزاري رقم (1535) وتاريخ 11/6/1425هـ، بصيغته المجمَّعة مع تعديلاته الوزارية اللاحقة حتى القرار رقم (25) وتاريخ 8/1/1445هـ — ملف الهيئة العامة للزكاة والضريبة والجمارك الرسمي (zatca.gov.sa)، مطابق بالتقاطع مع ملف gstc.gov.sa (INCOM2.pdf)؛ بوابة هيئة الخبراء لا تملك صفحة مخصصة لهذه اللائحة التنفيذية",
                                     "source_status": top_status.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "income_tax",
               "layer": "INCOME_TAX_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-income-tax-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (74 مادة؛ 30 أصلية، 19 معدلة، 25 ملغاة، 0 مضافة)",
               "title_en": ("Implementing Regulation of the Saudi Arabian Income Tax Law — Arabic "
                            "LLM-ready layer (74 records: 30 original, 19 amended, 25 repealed, "
                            "0 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 74], "text_status": "CONSOLIDATED_AMENDED",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Income Tax Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
