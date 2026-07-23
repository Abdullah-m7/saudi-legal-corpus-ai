#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian Franchise Law track
(اللائحة التنفيذية لنظام الامتياز التجاري, Ministerial (Minister of Commerce)
Resolution No. (591) [also rendered (00591)], 18/9/1441H, issued under Article
(26) of the Franchise Law, Royal Decree M/22, 9/2/1441H).

This is the companion-regulation follow-up candidate explicitly flagged by this
corpus's own franchise_law track (see sources/franchise/law/official_source/
franchise_law_official_source.json, verification_methodology_note: "a companion
Implementing Regulation is confirmed to exist -- Ministerial Decision No. 591
(00591), issued by the Minister of Commerce and Investment, dated 18/9/1441H,
based on Article 26 of this Law, containing 16 articles ... flagged here as a
candidate for a follow-up companion-track ingestion"). This track ingests it.

VERIFICATION TIER -- see franchise_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. The
Bureau of Experts portal HAS a dedicated lawId page for the base Franchise LAW
(af2a6b93-51dd-4f16-b781-aafd00d9fbbc, fetched this pass via the r.jina.ai
proxy after a direct query returned HTTP 503), but has NO dedicated lawId page
for this Implementing Regulation specifically -- consistent with BOE not
cataloguing Ministerial-level executive regulations as standalone lawId
records (the same pattern documented by this corpus's food_regulation track).
Direct downloads from government hosts (monshaat.gov.sa, mc.gov.sa,
franchisecenter.sa) reset the TLS connection from the destination this pass
(likely geoblocking) and were not bypassed.

PRIMARY SOURCE for the article text: franchising.sa -- a clean reproduction of
the Umm Al-Qura gazette text that itself links the official uqn.gov.sa PDF.
CROSS-VERIFICATION #1 (full text, verbatim): aunklaw.com (an independent law
firm, 2024) -- all 16 articles matched franchising.sa consonant-for-consonant
(only trivial diacritic / Eastern-vs-Western digit-glyph / zero-width /
dash-spacing presentation differed), confirmed programmatically by normalizing
both and comparing article by article (exact match on all 16).
CROSS-VERIFICATION #2 (instrument metadata + structure): lexismiddleeast.com
(Sader Publishers / LexisNexis) independently confirmed the resolution number
(00591/1441H), issuance date (18/9/1441H = 11 May 2020), enabling authority
(Article 26 of Council of Ministers Resolution 122/1441H re the Franchise Law,
Royal Decree M/22), the issuing Minister (Dr. Majid bin Abdullah Al-Qasabi),
gazette publication (Umm Al-Qura issue 4832, 22 May 2020, p.12), and the exact
six-chapter structure with article ranges.

16 articles across 6 chapters; all 16 اصلية (0 معدلة, 0 ملغاة, 0 مضافة). The
articles themselves have NOT been amended. A confirmed amendment affects ONLY
the separate "Disclosure Document Requirements" annex (متطلبات وثيقة الإفصاح):
element (13) "معلومات الوضع المالي لمانح الامتياز" was later deleted (per an
Umm Al-Qura headline at uqn.gov.sa/?p=22360, attributed by a search summary to
Ministerial Resolution No. 339, 14/8/1444H) -- independently corroborated by
the structural divergence between the 2020 franchising.sa annex (17 elements,
element 13 present) and the 2024 aunklaw.com annex (16 elements, element 13
deleted, subsequent elements renumbered down). The annex is preserved verbatim
in its ORIGINAL as-gazetted form (17 elements, element 13 retained not deleted)
in the source artifact's annex_ar field, per this corpus's flag-don't-delete
rule; it is NOT split into per-article records (it is a non-numbered appendix).

This Regulation names NO predecessor it repeals (Article 16 merely publishes it
and sets its effective date); the base Franchise Law's Article 27 carries only
a general repeal of conflicting provisions, naming no specific predecessor.

Text normalization: only tatweel and zero-width/bidi control characters were
removed and whitespace collapsed; diacritics and source quotation marks («» and
typographic quotes) are preserved as they appear in franchising.sa, consistent
with this corpus's sibling franchise_law track (which preserves source
diacritics). Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "franchise", "regulation", "official_source",
                   "franchise_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "franchise", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "franchise_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "franchise_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "franchise_regulation_arabic_legal_llm",
                        "franchise_regulation_legal_llm_001_016.json")

LAW_ID = "sa-franchise-regulation-591-1441"
LAW_AR = "اللائحة التنفيذية لنظام الامتياز التجاري"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"franchise_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الامتياز مانح صاحب اتفاقية").split())


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
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
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
        ver.append({"law_key": "franchise", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "FRANCHISE_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source for the article "
                                              "text is franchising.sa (a clean reproduction of the "
                                              "Umm Al-Qura gazette text that links the official "
                                              "uqn.gov.sa PDF) -- laws.boe.gov.sa was checked "
                                              "first per standard methodology but has no dedicated "
                                              "lawId page for this Implementing Regulation (only "
                                              "for the base Franchise Law) and its direct query "
                                              "returned HTTP 503 this pass. All 16 articles were "
                                              "cross-verified VERBATIM against an independent "
                                              "full-text source (aunklaw.com), and the instrument "
                                              "metadata + six-chapter structure were "
                                              "cross-verified against lexismiddleeast.com "
                                              "(Sader/LexisNexis). See verification_methodology_"
                                              "note and known_unresolved_discrepancies in the "
                                              "source artifact before relying on this track -- in "
                                              "particular the confirmed deletion of annex element "
                                              "(13) 'معلومات الوضع المالي لمانح الامتياز' (which "
                                              "affects the Disclosure-Document annex only, NOT any "
                                              "of the 16 numbered articles), and the fact the "
                                              "official government-hosted PDF was not directly "
                                              "fetchable this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "franchise-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "franchise/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الامتياز التجاري" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Minister of Commerce Resolution No. "
                                                          "(591) [also (00591)] (18/9/1441H), "
                                                          "issued under Article 26 of the Franchise "
                                                          "Law (Royal Decree M/22, 9/2/1441H) — "
                                                          "franchising.sa (Umm Al-Qura gazette "
                                                          "reproduction), cross-verified verbatim "
                                                          "against aunklaw.com and (metadata/"
                                                          "structure) lexismiddleeast.com; "
                                                          "laws.boe.gov.sa has no dedicated lawId "
                                                          "page for this Implementing Regulation"),
                                     "source_authority_ar": "قرار وزير التجارة رقم (591) [ويظهر أيضا بصيغة (00591)] وتاريخ 18/9/1441هـ، الصادر استنادا إلى المادة (السادسة والعشرين) من نظام الامتياز التجاري (المرسوم الملكي رقم م/22، 9/2/1441هـ) — franchising.sa (استنساخ جريدة أم القرى)، مطابق حرفيا مع aunklaw.com ومع lexismiddleeast.com (بيانات الإصدار والبنية)؛ بوابة هيئة الخبراء لا تملك صفحة مخصصة لهذه اللائحة التنفيذية",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "franchise",
               "layer": "FRANCHISE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "annex_ar": src.get("annex_ar"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-franchise-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 مادة؛ 16 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation of the Saudi Arabian Franchise Law — Arabic "
                            "LLM-ready layer (16 records: 16 original, 0 amended, 0 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 16], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Franchise Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
