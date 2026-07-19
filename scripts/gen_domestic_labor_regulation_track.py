#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Domestic Labor Regulation track (لائحة العمالة
المنزلية ومن في حكمهم, Ministerial Decision No. 40676, 17/3/1445H / 2 Oct
2023G, issued by the Minister of Human Resources and Social Development).

VERIFICATION TIER -- see sources/domestic_labor/regulation/official_source/
domestic_labor_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology, but
its live portal was unreachable this pass (connection reset), and Wayback
Machine snapshots of BOE's only page for this topic (lawId
cc46debb-482e-48be-9daf-a9a700f2bfe7), spanning 2019 through the most recent
archived snapshot (6 Sep 2025), show BOE has NOT been updated to reflect the
current regulation -- it still displays only the SUPERSEDED 2013 predecessor
(لائحة عمال الخدمة المنزلية ومن في حكمهم, Council of Ministers Decision 310,
7/9/1434H, 23 articles). This is a confirmed, genuine gap in BOE's own
coverage for this specific instrument, not a retrieval artifact of this pass.

PRIMARY SOURCE: hrsd.gov.sa (the issuing Ministry's own official website),
fetched directly (200 OK), cross-confirmed stable across three independent
Wayback Machine snapshots (18 Mar 2024, 2 Oct 2025) with byte-identical digest
between the two most recent -- i.e. the exact same file, with the same two
defects described below, has been hosted unchanged for at least 18 months:
(1) the PDF's own cover page and ministerial-decision preamble retain an
unfilled DRAFT template (dated 19 May 2022, decree number/date left as blank
parentheses, an internal header literally reading "مسودة" (draft)); (2) the
file is physically truncated at 11 pages (its own footer references "12"),
cutting off mid-sentence within Article 33 -- confirmed via TWO independent
extraction pipelines (poppler pdftotext and PyMuPDF) that agree on the exact
cutoff point, ruling out an extraction-tool artifact.

SECONDARY CROSS-CHECKS: qanoonsa.com (independent Arabic legal aggregator)
confirms the decree number (40676), hijri date (17/3/1445H), Gregorian
equivalent, and the named repeal of Council of Ministers Decision 310
(7/9/1434H); lexismiddleeast.com (independent commercial legal database)
independently confirms the 33-article structure and final "أحكام ختامية"
section; multiple Arabic news outlets (akhbaar24.com, ajel.sa) corroborate.

33 records, all اصلية (this is the founding/only version of this specific
instrument; no per-article amendment has been documented since 17/3/1445H).
0 معدلة, 0 ملغاة, 0 مضافة. Article 33's text is preserved VERBATIM AS FAR AS
THE SOURCE PROVIDES ONLY -- flagged status ORIGINAL_TEXT_INCOMPLETE, its
missing tail is NOT fabricated or reconstructed.

PREDECESSOR: the ministerial decision's own clause (2) explicitly repeals/
replaces لائحة عمال الخدمة المنزلية ومن في حكمهم (Council of Ministers
Decision 310, 7/9/1434H, 23 articles) -- neither exists in this corpus; noted
as historical context only (one-law-per-pass rule).

COMPANION INSTRUMENT NOT INGESTED: ضوابط تحسين العلاقة التعاقدية للعمالة
المنزلية ومن في حكمهم (~28 Mar 2024 / 18 Ramadan 1445H) was identified but
determined to be a separate procedural/administrative initiative (rules for
contract termination due to worker absconding, worker-mobility service), not
a textual amendment to any numbered article of this Regulation -- NOT
ingested this pass.

Two confirmed source-layer (not content) defects were corrected: (1) a
font-embedded ligature-extraction bug mapping the "تر" glyph pair to "بخ"
(reproduced identically by both pdftotext and PyMuPDF, so it is a defect in
the PDF's embedded font/ToUnicode map, not a tool quirk) -- fixed via a
10-word targeted dictionary, each verified against sentence context; (2)
mirrored/reversed parentheses (a common RTL-PDF-extraction artifact) fixed via
a global paren swap. Diacritics (tashkeel) are stripped uniformly across this
track for consistency with the rest of this corpus's BOE-sourced tracks (which
carry none) and because the source PDF's own combining-mark ordering was
unreliable under extraction (e.g. "بناًء" instead of "بناءً"); this is a
presentation-layer normalization only, no letter/word/number/legal-substance
was altered. One likely genuine source-level typo (missing space in "أوبهما"
in Article 29(a), vs. correctly-spaced "أو بهما" in the parallel Article
30(1)) is preserved verbatim, not silently corrected.

No legal text is altered beyond the above disclosed, source-artifact-layer
fixes. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "domestic_labor", "regulation", "official_source",
                   "domestic_labor_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "domestic_labor", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "domestic_labor_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "domestic_labor_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "domestic_labor_arabic_legal_llm",
                        "domestic_labor_regulation_legal_llm_001_033.json")

LAW_ID = "sa-domestic-labor-regulation-40676-1445"
LAW_AR = "لائحة العمالة المنزلية ومن في حكمهم"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_INCOMPLETE = "ORIGINAL_TEXT_INCOMPLETE"
KEY_RE = r"domestic_labor_art_(\d{3})(?:_mukarrar(\d*))?$"
INCOMPLETE_KEYS = {"domestic_labor_art_033"}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم العامل المنزلي صاحب العمل").split())


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
    if key in INCOMPLETE_KEYS:
        return STATUS_INCOMPLETE
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
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "domestic_labor", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "DOMESTIC_LABOR_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source is hrsd.gov.sa (the "
                                              "issuing Ministry's own site) -- laws.boe.gov.sa was "
                                              "checked first per standard methodology but its only "
                                              "page for this topic remains stale (still shows the "
                                              "superseded 2013/1434H predecessor as of the most "
                                              "recent archived snapshot, 6 Sep 2025). Cross-verified "
                                              "against qanoonsa.com (decree number/date/repeal) and "
                                              "lexismiddleeast.com (33-article structure). The "
                                              "source PDF is itself confirmed truncated at Article "
                                              "33 (physically 11 pages though its own footer "
                                              "references 12) -- this article's text_complete=False "
                                              "and its text is preserved only as far as the source "
                                              "provides, with no fabricated completion. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track's text or provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "domestic-labor-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "domestic_labor/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من لائحة العمالة المنزلية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. 40676 "
                                                          "(17/3/1445H) — hrsd.gov.sa (issuing "
                                                          "Ministry's own site), cross-verified "
                                                          "against qanoonsa.com and "
                                                          "lexismiddleeast.com; laws.boe.gov.sa "
                                                          "confirmed stale for this specific topic "
                                                          "(still shows the superseded 2013/1434H "
                                                          "predecessor)"),
                                     "source_authority_ar": "القرار الوزاري رقم 40676 وتاريخ 17/3/1445هـ — الموقع الرسمي لوزارة الموارد البشرية والتنمية الاجتماعية (hrsd.gov.sa)، مطابق مع qanoonsa.com وlexismiddleeast.com؛ بوابة هيئة الخبراء لا تزال تعرض اللائحة السابقة الملغاة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "domestic_labor",
               "layer": "DOMESTIC_LABOR_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-domestic-labor-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (33 مادة، جميعها أصلية؛ المادة 33 غير مكتملة النص في المصدر)",
               "title_en": ("Saudi Arabian Domestic Labor Regulation — Arabic LLM-ready layer "
                            "(33 records, all original; Article 33's text is incomplete in the "
                            "source and flagged accordingly)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 33], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Domestic Labor Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
