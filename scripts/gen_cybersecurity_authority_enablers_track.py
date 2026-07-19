#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the "Regulatory (Legal) Enablers" of the National Cybersecurity
Authority track (الممكنات النظامية للهيئة الوطنية للأمن السيبراني, Royal
Decree No. م/117, 21/6/1446H / 22 Dec 2024G, based on Council of Ministers
Resolution No. 409, 16/6/1446H, and Shura Council Resolution No. 16/3,
28/3/1446H; published Umm Al-Qura Gazette No. 5065, 17 Jan 2025G).

This is the follow-up track explicitly flagged (but NOT ingested) by this
corpus's own cybersecurity_authority_law track (Royal Order 6801/7053) --
see that track's own known_unresolved_discrepancies key
cybersecurity_authority_enablers_m117_distinct_not_ingested.

VERIFICATION TIER -- see sources/cybersecurity_authority/enablers/
official_source/cybersecurity_authority_enablers_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa could not be located for this exact instrument this pass
(site:laws.boe.gov.sa WebSearch surfaced only other, unrelated BOE-catalogued
laws; a direct curl to the portal -- both the root domain and a
SearchDetails query -- returned "Connection reset by peer" on both
attempts). The PRIMARY source actually used is the National Cybersecurity
Authority's OWN official website (cdn.nca.gov.sa), an official PDF fetched
live this pass (HTTP 200), independently confirmed to exist via a Wayback
Machine availability check for the exact URL.

A GENUINE TEXT-EXTRACTION ANOMALY, THE SAME ONE ALREADY DOCUMENTED IN THE
PARENT TRACK: the source PDF's embedded text layer has the same confirmed,
systematic character-transposition artifact (both pdftotext and PyMuPDF
independently produce the same corrupted local letter-pair order, e.g.
"السيبراني" extracting as "السيبراين"). Worked around via 300dpi page
renders OCR'd with Tesseract 5's Arabic model, cross-read word-by-word
against the flawed-but-complete pdftotext -layout extraction (for
boundaries/counts) and against qanoonsa.com's independent full structural
summary (three separate pages: the Royal Decree text, the Council of
Ministers Resolution, and the instrument itself).

A GENUINE STRUCTURAL DIFFERENCE FROM EVERY OTHER TRACK: this instrument has
NO "مادة" (article) numbering at all -- it is organized into seven ordinal
"بند" (clause/item) divisions: أولاً, ثانياً, ثالثاً, رابعاً, خامساً,
سادساً, سابعاً, confirmed both from the PDF's own layout and from the
instrument's own internal cross-references (which repeatedly call these
divisions "البند"). Each بند is treated as one record here (number_label_ar
= "البند أولاً" etc.), consistent with this corpus's convention of using
the source's own smallest independently-numbered top-level division as the
atomic unit, but this is flagged explicitly as a structural anomaly, not
silently absorbed into a "مادة" label the source never uses.

7 records: all اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- this is the founding
and, to date, only version of this instrument. Flat structure, no
أبواب/فصول. CONFIRMED NEGATIVE FINDING (independently re-verified, not
merely inherited from the parent track): no source consulted this pass
states that this instrument amends or repeals any مادة of the parent
organizational تنظيم (Royal Order 6801/7053, this corpus's separate
cybersecurity_authority_law track) -- both instruments remain textually and
substantively separate, companion instruments on different subject matter.

No legal text is altered beyond: OCR-based recovery of the correct letter
order where the PDF's own text layer is corrupted (a read-only
transcription correction of a source-side extraction artifact, not a
substantive edit); omission of list-rendering numeral markers per this
corpus's convention (lettered sub-items in بند خامساً's first item are
preserved with their أ-/ب-/ج-/د-/ه- prefixes); exclusion of a repeating
page-footer classification-banner ("التصنيف: عام") that is page furniture,
not legal text; whitespace/line-break normalization. Numeral conventions
(Arabic-Indic digits, spelled-out Arabic words, and Western digits with
period thousand-separators for the 25-million-SAR maximum fine) are
preserved exactly as they appear at each specific point in the source, not
normalized to one convention -- this mixed usage is a verified feature of
the source's own legal drafting. Arabic governs; no translation/paraphrase/
interpretation performed. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cybersecurity_authority", "enablers", "official_source",
                   "cybersecurity_authority_enablers_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cybersecurity_authority", "enablers", "verified")
RECORDS = os.path.join(OUT_VER, "cybersecurity_authority_enablers_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cybersecurity_authority_enablers_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cybersecurity_authority_enablers_arabic_legal_llm",
                        "cybersecurity_authority_enablers_legal_llm_001_007.json")

LAW_ID = "sa-cybersecurity-authority-enablers-m117-1446"
LAW_AR = "الممكنات النظامية للهيئة الوطنية للأمن السيبراني"
TOP_STATUS = ("NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QANOONSA_"
              "STRUCTURAL_FULL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED")
KEY_RE = r"cybersecurity_authority_enablers_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن البند الممكنات الهيئة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الوطنية المخالفة المخالفات المجلس").split())


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
        ver.append({"law_key": "cybersecurity_authority", "law_component": "enablers",
                    "language": "ar",
                    "record_layer": "CYBERSECURITY_AUTHORITY_ENABLERS_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on an official "
                                              "PDF hosted on the National Cybersecurity "
                                              "Authority's own website (cdn.nca.gov.sa) as the "
                                              "PRIMARY source (no laws.boe.gov.sa page for this "
                                              "exact instrument could be located this pass), "
                                              "transcribed via Tesseract OCR to work around the "
                                              "same confirmed text-layer letter-transposition "
                                              "artifact already documented in this corpus's "
                                              "parent cybersecurity_authority_law track, "
                                              "cross-verified against qanoonsa.com's independent "
                                              "full structural summary (three separate pages) and "
                                              "uqn.gov.sa's topical gazette indexing. This "
                                              "instrument is organized into seven ordinal بند "
                                              "divisions, NOT مادة articles -- a genuine "
                                              "structural anomaly relative to every other track "
                                              "in this corpus, see "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact, key "
                                              "cybersecurity_authority_enablers_band_not_madda_"
                                              "structure. All 7 بنود are اصلية (this is the "
                                              "founding and, to date, only version). No source "
                                              "found this pass states this instrument amends or "
                                              "repeals any مادة of the parent organizational "
                                              "تنظيم (Royal Order 6801/7053) -- a confirmed, "
                                              "independently re-verified negative finding. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text or "
                                              "provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "enablers", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "cybersecurity-authority-enablers-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "cybersecurity_authority/enablers/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من الممكنات النظامية للهيئة الوطنية للأمن السيبراني" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/117), 21/6/1446H — "
                                                          "official PDF on the National "
                                                          "Cybersecurity Authority's own website "
                                                          "(cdn.nca.gov.sa), OCR-transcribed to "
                                                          "work around a confirmed text-layer "
                                                          "letter-transposition artifact, "
                                                          "cross-verified against qanoonsa.com "
                                                          "(three separate pages: the Royal "
                                                          "Decree, the Council of Ministers "
                                                          "Resolution, and the instrument itself) "
                                                          "and uqn.gov.sa (topical indexing only); "
                                                          "no laws.boe.gov.sa page for this exact "
                                                          "instrument could be located this pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/117) وتاريخ 21/6/1446هـ — نسخة PDF رسمية من الموقع الرسمي للهيئة الوطنية للأمن السيبراني (cdn.nca.gov.sa)، مفرَّغة بالتعرف الضوئي على الحروف (OCR) لتجاوز خلل في طبقة النص، مطابقة مع qanoonsa.com (ثلاث صفحات مستقلة) وuqn.gov.sa (فهرسة موضوعية فقط)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cybersecurity_authority",
               "layer": "CYBERSECURITY_AUTHORITY_ENABLERS_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cybersecurity-authority-enablers-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "enablers",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (7 بنود أصلية، بلا تقسيم إلى أبواب أو مواد)",
               "title_en": ("Regulatory (Legal) Enablers of the National Cybersecurity Authority "
                            "— Arabic LLM-ready layer (7 records, all original; organized into "
                            "بند clauses, not مادة articles)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 7], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Cybersecurity Authority Enablers records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
