#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the "Organizational Arrangements of the Saudi Data and AI
Authority" track (الترتيبات التنظيمية للهيئة السعودية للبيانات والذكاء
الاصطناعي, Council of Ministers Resolution No. 292, 27/4/1441H, amended by
Council of Ministers Resolution No. 195, 15/3/1444H).

VERIFICATION TIER -- see sources/sdaia_organizational_arrangements/law/
official_source/sdaia_organizational_arrangements_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa could not be located for this exact instrument this pass
(site:laws.boe.gov.sa WebSearch surfaced only other, unrelated BOE-catalogued
laws that merely reference SDAIA in passing; direct curl attempts to the
portal failed outright). The PRIMARY source actually used is SDAIA's OWN
official website (sdaia.gov.sa/ar/SDAIA/about/Documents/
organizationalArrangementsAr.pdf). Direct curl/WebFetch to sdaia.gov.sa fail
domain-wide in this sandbox ("Connection reset by peer" / WAF rejection); the
PDF was instead fetched via the r.jina.ai reader-proxy, HTTP 200,
reproducibly identical across two independent fetches.

A GENUINE TEXT-EXTRACTION ARTIFACT, DISCLOSED, RECONSTRUCTED WITHOUT
PIXEL-LEVEL OCR (a genuine methodological limitation relative to this
corpus's cybersecurity_authority_enablers precedent): the r.jina.ai
extraction systematically reverses any lam (ل) immediately followed -- within
the same word -- by an alif-form (ا/أ/إ/آ), e.g. "الاعتبارية" extracts as
"االعتبارية". Independently confirmed via qistas.com's own clean preview of
بنود أولاً-ثالثاً (which renders these exact phrases correctly) and via
internal cross-check against the same correct spelling appearing elsewhere
in this document unaffected by the artifact. This pass could not obtain the
PDF's raw bytes for pixel-level OCR (direct fetch, Wayback replay [HTTP 403],
and a CORS proxy [HTTP 522] all failed) -- text was instead reconstructed via
disclosed, cross-validated, word-level correction of this confirmed
mechanical pattern. One specific clause (بند ثالث عشر's transitional first
fiscal year) required a lower-confidence reconstruction, flagged separately.

A GENUINE STRUCTURAL DIFFERENCE FROM MOST TRACKS (SHARED WITH
cybersecurity_authority_enablers): this instrument has NO "مادة" numbering --
it is organized into sixteen ordinal "بند" divisions: أولاً through سادس
عشر. Each بند is treated as one record here (number_label_ar = "البند أولاً"
etc.), consistent with this corpus's convention of using the source's own
smallest independently-numbered top-level division as the atomic unit.

16 records: 15 اصلية, 1 معدلة (بند خامساً, board formation -- per
lexismiddleeast.com's own "الأحكام المعدلة" index entry "المادة 5 - مجلس
إدارة الهيئة"; the pre-1444H-amendment wording could not be independently
retrieved this pass, see known_unresolved_discrepancies). Flat structure, no
أبواب/فصول. NO repeal clause anywhere (unlike cybersecurity_authority_
enablers' generic conflict-repeal at its final بند) and NO violations/
penalties clause -- this organizational/founding-mandate instrument
establishes SDAIA's structure, governance, and rule-making mandate but does
not itself create sanctions. CONFIRMED NEGATIVE FINDING: the founding Royal
Order A/471 (29/12/1440H, independently confirmed this pass via the Saudi
Press Agency's own verbatim republication) organizationally links the
pre-existing National Information Center (established under Royal Order
A/293/1438H and Council of Ministers Resolution 495/1439H) to SDAIA without
any source consulted this pass explicitly repealing either predecessor
instrument.

No legal text is altered beyond: disclosed, cross-validated correction of
the lam-alif-ligature-reversal extraction artifact (a read-only transcription
correction of a source-side artifact, not a substantive edit); omission of
list-rendering Western-numeral-plus-hyphen markers per this corpus's
convention (lettered أ-/ب-/ج-/د- sub-items in بند ثاني عشر are preserved);
whitespace/justification-spacing normalization. Arabic governs; no
translation/paraphrase/interpretation performed. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sdaia_organizational_arrangements", "law", "official_source",
                   "sdaia_organizational_arrangements_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "sdaia_organizational_arrangements", "law", "verified")
RECORDS = os.path.join(OUT_VER, "sdaia_organizational_arrangements_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "sdaia_organizational_arrangements_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "sdaia_organizational_arrangements_arabic_legal_llm",
                        "sdaia_organizational_arrangements_legal_llm_001_016.json")

LAW_ID = "sa-sdaia-organizational-arrangements-292-1441"
LAW_AR = "الترتيبات التنظيمية للهيئة السعودية للبيانات والذكاء الاصطناعي"
TOP_STATUS = ("SDAIA_OFFICIAL_SITE_PDF_PRIMARY_JINA_READER_PROXY_LIGATURE_ARTIFACT_RECONSTRUCTED_"
              "X_QISTAS_LEXISMIDDLEEAST_SPA_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED")
KEY_RE = r"sdaia_organizational_arrangements_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"sdaia_organizational_arrangements_art_005"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن البند الترتيبات الهيئة أحكام يجب يجوز عليه "
            "دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الوطنية المجلس").split())


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
        ver.append({"law_key": "sdaia_organizational_arrangements", "law_component": "law",
                    "language": "ar",
                    "record_layer": "SDAIA_ORGANIZATIONAL_ARRANGEMENTS_ARABIC_VERIFIED_TEXT",
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
                                              "PDF hosted on SDAIA's own website (sdaia.gov.sa) as "
                                              "the PRIMARY source (no laws.boe.gov.sa page for this "
                                              "exact instrument could be located this pass), "
                                              "reached via the r.jina.ai reader-proxy since direct "
                                              "curl/WebFetch to sdaia.gov.sa fail domain-wide in "
                                              "this sandbox. A confirmed lam-alif-ligature-reversal "
                                              "extraction artifact was corrected via disclosed, "
                                              "cross-validated word-level reconstruction (NOT pixel "
                                              "OCR -- the PDF's raw bytes could not be obtained this "
                                              "pass), cross-checked against qistas.com's clean "
                                              "excerpt (بنود أولاً-ثالثاً), lexismiddleeast.com's "
                                              "clean Resolution 292 preamble, and the Saudi Press "
                                              "Agency's (spa.gov.sa) independently-fetched primary "
                                              "text of the founding Royal Order A/471. This "
                                              "instrument is organized into sixteen ordinal بند "
                                              "divisions, NOT مادة articles -- see "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact, key "
                                              "sdaia_organizational_arrangements_band_not_madda_"
                                              "structure. بند خامساً (board formation) is marked "
                                              "معدلة per lexismiddleeast.com's own amendment index "
                                              "only (pre-amendment text not independently "
                                              "retrieved this pass) -- see "
                                              "sdaia_organizational_arrangements_amended_clause_"
                                              "attribution_limited_confidence. No repeal clause and "
                                              "no violations/penalties clause anywhere in this "
                                              "instrument -- a confirmed structural difference from "
                                              "the sibling cybersecurity_authority_enablers track. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text or "
                                              "provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "sdaia-organizational-arrangements-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "sdaia_organizational_arrangements/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من الترتيبات التنظيمية للهيئة السعودية للبيانات والذكاء الاصطناعي" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(292), 27/4/1441H, amended by Resolution "
                                                          "No. (195), 15/3/1444H — official PDF on "
                                                          "SDAIA's own website (sdaia.gov.sa), "
                                                          "fetched via r.jina.ai reader-proxy "
                                                          "(direct fetch fails domain-wide in this "
                                                          "sandbox), reconstructed via disclosed "
                                                          "correction of a confirmed extraction "
                                                          "artifact, cross-verified against "
                                                          "qistas.com, lexismiddleeast.com, and the "
                                                          "Saudi Press Agency (for the founding "
                                                          "Royal Order A/471); no laws.boe.gov.sa "
                                                          "page for this exact instrument could be "
                                                          "located this pass"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (292) وتاريخ 27/4/1441هـ، المعدل بقرار مجلس الوزراء رقم (195) وتاريخ 15/3/1444هـ — نسخة PDF رسمية من الموقع الرسمي لهيئة سدايا (sdaia.gov.sa)، عبر وسيط قراءة (r.jina.ai) نظرًا لتعذر الوصول المباشر، مع تصحيح مفصح عنه لخلل استخراج نصي مؤكَّد، ومطابقة مع qistas.com وlexismiddleeast.com وواس (للأمر الملكي التأسيسي أ/471)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "sdaia_organizational_arrangements",
               "layer": "SDAIA_ORGANIZATIONAL_ARRANGEMENTS_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-sdaia-organizational-arrangements-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 بندًا، 15 أصلية و1 معدلة، بلا تقسيم إلى أبواب أو مواد)",
               "title_en": ("Organizational Arrangements of the Saudi Data and AI Authority "
                            "(SDAIA) — Arabic LLM-ready layer (16 records, 15 original + 1 "
                            "amended; organized into بند clauses, not مادة articles)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 16], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready SDAIA Organizational Arrangements records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
