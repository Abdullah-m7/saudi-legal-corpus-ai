#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Press and Publications Law track
(نظام المطبوعات والنشر, Royal Decree M/32, 3/9/1421H).

CURRENCY CHECK -- performed before any build work, since this corpus's
coverage-gap-map flagged this law as needing one. CONFIRMED: M/32 is STILL
the current, in-force organising statute for print media/publishing as of
this build (18 Jul 2026). A draft comprehensive "نظام الإعلام" (Media Law),
intended to eventually replace both M/32 and the Audiovisual Media Law
(M/33, 1439H), has been in public consultation since Nov 2023 but had NOT
been enacted as of this pass -- see
sources/press/law/official_source/press_law_official_source.json's
verification_methodology_note and known_unresolved_discrepancies for the
full account (including a note ruling out an unrelated, confusingly
similarly-named JORDANIAN law found during initial searches).

VERIFICATION TIER -- summary (full account in the official_source.json):
TIER_1: BOE (laws.boe.gov.sa), reached via a near-live Wayback Machine
  snapshot dated 26 Feb 2026 (live portal returned 503/connection-reset on
  every direct attempt this pass) with fully legible, cleanly-parsed
  article text, cross-checked against the Ministry of Media's OWN official
  PDF of this exact law (media.gov.sa -- a genuinely separate primary
  source, this law's own subject-matter regulator, not a re-hosted BOE
  mirror; its body text extracts with character-scrambling so it was used
  only for structural/decree-number cross-check), further corroborated
  structurally by WIPO Lex (exact decree-number/date match) and by
  nezams.com / qanoonsa.com.

49 articles: 43 اصلية (original), 6 معدلة (amended: Articles 5, 9, 36, 37,
38, 40), 0 ملغاة, 0 مضافة. No أبواب/فصول labels used in the source itself;
Articles 1-12 carry no section heading at all in BOE's own HTML, unlike the
other five groups (المطبوعات الداخلية 13-17; المطبوعات الخارجية 18-23;
الصحافة المحلية 24-34; الجزاءات 35-41; أحكام عامة 42-49).

BOE MAIN-BODY-STALE-VS-CHANGELOG PATTERN: for all 6 amended articles, BOE's
own live main-body text still shows the OLDER, pre-amendment wording even
though BOE's own changelog popup logs the newer decree(s) -- this corpus's
established recurring pattern (cf. accounting_auditing_law, awqaf_law).
Following the accounting_auditing_law precedent for a clean, self-contained
changelog quote, this track ingests the AMENDED wording as each article's
current "text", preserving BOE's stale wording verbatim in an
"original_2000_text" field.

REPEAL/PREDECESSOR: this law's own Article 48 EXPLICITLY and fully repeals
the prior 1982 Press and Publications Law (نظام المطبوعات والنشر, Royal
Decree M/17, 13/4/1402H). That predecessor is not ingested in this corpus
and its text is not independently fetched here (historical/cross-reference
context only), consistent with this corpus's one-law-per-pass practice.

No legal text is altered beyond whitespace normalisation (collapsing extra
inline-span spacing artifacts in BOE's own HTML). Arabic governs; no
translation/paraphrase/interpretation performed. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "press", "law", "official_source",
                   "press_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "press", "law", "verified")
RECORDS = os.path.join(OUT_VER, "press_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "press_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "press_arabic_legal_llm",
                        "press_law_legal_llm_001_049.json")

LAW_ID = "sa-press-law-m32-1421"
LAW_AR = "نظام المطبوعات والنشر"
TOP_STATUS_ORIGINAL = ("TIER_1_BOE_WAYBACK_FEB2026_NEARLIVE_CLEAN_TEXT_X_MEDIA_GOV_SA_"
                       "OFFICIAL_PDF_STRUCTURAL_SCRAMBLED_EXTRACTION_X_WIPOLEX_NEZAMS_"
                       "QANOONIAH_CROSSCHECK_LIVE_BOE_UNREACHABLE_DIRECT")
TOP_STATUS_AMENDED = ("TIER_1_BOE_WAYBACK_FEB2026_NEARLIVE_CLEAN_CHANGELOG_POPUP_TEXT_"
                      "INCORPORATED_MAIN_BODY_STALE_X_MEDIA_GOV_SA_OFFICIAL_PDF_STRUCTURAL_"
                      "SCRAMBLED_EXTRACTION_X_WIPOLEX_NEZAMS_QANOONIAH_CROSSCHECK_"
                      "LIVE_BOE_UNREACHABLE_DIRECT")
KEY_RE = r"press_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"press_art_005", "press_art_009", "press_art_036",
                "press_art_037", "press_art_038", "press_art_040"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الوزارة الوزير").split())


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
        top_status = TOP_STATUS_AMENDED if key in AMENDED_KEYS else TOP_STATUS_ORIGINAL
        ver.append({"law_key": "press", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PRESS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_2000_text": a.get("original_2000_text"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this track rests on a near-live "
                                              "BOE-via-Wayback-Machine snapshot (26 Feb 2026), "
                                              "cross-verified structurally against the Ministry "
                                              "of Media's own official PDF of this law "
                                              "(media.gov.sa, a genuinely separate primary "
                                              "source, scrambled-extraction limited to "
                                              "structural/decree-number use), WIPO Lex, and "
                                              "nezams.com/qanoonsa.com. Live BOE was unreachable "
                                              "this pass (HTTP 503/connection-reset). Articles 5, "
                                              "9, 36, 37, 38 and 40 carry BOE-logged amendments "
                                              "that BOE's own live main body does not yet "
                                              "reflect; this track ingests the amended wording "
                                              "as current text with the stale BOE wording "
                                              "preserved in original_2000_text. See "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the currency-check finding (a draft "
                                              "comprehensive نظام الإعلام remains unenacted), the "
                                              "confirmed full repeal of the predecessor 1982 "
                                              "Press Law (M/17) by this law's own Article 48, "
                                              "and the untitled first structural group "
                                              "(Articles 1-12)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "press-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "press/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المطبوعات والنشر" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/32 — laws.boe.gov.sa "
                                                          "via a near-live Wayback Machine "
                                                          "snapshot (26 Feb 2026), cross-verified "
                                                          "against media.gov.sa's own official "
                                                          "PDF (structural use only), WIPO Lex, "
                                                          "and nezams.com/qanoonsa.com; live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/32) — لقطة أرشيفية شبه حية من بوابة هيئة الخبراء عبر Wayback Machine (26 فبراير 2026)، مطابقة هيكليًا مع نسخة وزارة الإعلام الرسمية ومع WIPO Lex وnezams.com/qanoonsa.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "press",
               "layer": "PRESS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-press-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (49 مادة، 43 أصلية و6 معدلة)",
               "title_en": "Press and Publications Law — Arabic LLM-ready layer (49 records, 43 original, 6 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 49], "text_status": TOP_STATUS_ORIGINAL,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Press Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
