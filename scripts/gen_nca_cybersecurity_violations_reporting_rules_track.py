#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the NCA "Rules Organizing the Reporting of Cybersecurity Violations"
track (قواعد تنظيم الإبلاغ عن مخالفات الأمن السيبراني) -- the whistleblower/
reward rules mandated by paragraph (1) of Item (سادساً/Sixth) of the
Regulatory (Legal) Enablers of the National Cybersecurity Authority (Royal
Decree No. M/117, 21/6/1446H; this corpus's own cybersecurity_authority
enablers track).

VERIFICATION TIER -- see this track's own official_source.json for the full
account (verification_methodology_note / known_unresolved_discrepancies).
Summary:

TIER_2 (single official/primary source reached and internally cross-checked
by two independent methods, plus topical-only secondary news corroboration --
NOT TIER_1, since no second independent OFFICIAL source with this specific
instrument's full text was reached, and the exact NCA Board of Directors
decision number/date approving THIS instrument could not be independently
confirmed this pass).

PRIMARY SOURCE: an official PDF hosted on the National Cybersecurity
Authority's own site (cdn.nca.gov.sa), already downloaded to this session's
scratchpad by a prior research pass (reporting_rules.pdf, 407852 bytes, 7
pages, PDF 1.7; embedded metadata: Title="Microsoft Word - قواعد تنظيم
الإبلاغ عن مخالفات الأمن السيبراني.docx", Producer="Microsoft: Print To
PDF", creation/mod timestamps both 2026-07-09T09:56:20Z). Unlike this
corpus's cybersecurity_authority_enablers track (whose PDF has a confirmed,
systematic 'لا'-ligature/letter-transposition text-layer bug), THIS PDF's
pdftotext -layout text layer was checked and found clean (e.g. "السيبراني"
appears 11 times, always correctly spelled; the corrupted variant
"السيبراين" appears zero times) -- nonetheless, every page was additionally
rendered to a 200-400dpi PNG and read directly (multimodal visual read of
the actual glyphs, not just the text layer), word-for-word matching the
text-layer extraction across all 7 pages with zero discrepancy, satisfying
this corpus's "independent OCR/rendered-page-image pass of the same
official document" standard.

CITATION FINDING -- A CONFIRMED, INDEPENDENTLY-VERIFIED NEGATIVE RESULT:
this track's own commissioning brief flagged, but did not confirm, that this
instrument might share the same NCA Board of Directors decision number/date
as its companion "قواعد ضبط مخالفات الأمن السيبراني والتحقيق فيها"
(investigation rules) instrument (ع26/1/1/1ت, 22/08/1447H). This pass
independently fetched the companion instrument's OWN dedicated Umm Al-Qura
Gazette page (uqn.gov.sa/decisions-and-regulations/4001430) and confirmed
that decision number/date is stated there EXCLUSIVELY as the citation for
the companion investigation-rules instrument, not for this reporting-rules
instrument. No dedicated uqn.gov.sa gazette page, and no independent
decision number, could be located for THIS specific instrument despite
multiple search strategies (direct WebSearch, site:uqn.gov.sa,
site:qanoonsa.com, site:qistas.com) and one further government portal
(istitlaa.ncc.gov.sa) that hosts a public-consultation page for this exact
instrument but returned HTTP 503 (via WebFetch, twice) and a TLS/SSL error
(via direct curl) both times this pass, so its content could not be read.
Consequently, THIS track's decree/decree_date_hijri fields explicitly
disclose "غير مؤكد لهذا الصك تحديداً" (unconfirmed for this specific
instrument) rather than silently copying the companion's citation -- and
this is the reason this track sits at TIER_2, not any higher tier, per this
track's own commissioning instructions.

8 records, all اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- the founding and, to
date, only known version. Flat structure: 8 numbered مادة articles, NO
أبواب/فصول grouping at all (confirmed via the PDF's own index/فهرس page and
full visual read of all 7 pages).

No legal text is altered beyond: stripping of invisible bidi control
characters inserted by pdftotext when extracting RTL text (a display-only
artifact, no textual content); whitespace/line-break normalization; and
exclusion of cover-page/TLP-protocol/index-page furniture (not legal text).
Numeral conventions (Eastern Arabic-Indic digits with a trailing period for
numbered list items; hyphen-suffixed Arabic letters for lettered sub-items,
matching the source's own "ه-" with no tatweel; Arabic thousands separator
and percent sign in Article 6) are preserved exactly as they appear in the
source PDF, verified via a direct 400dpi zoomed crop of the relevant lines.
Arabic governs; no translation/paraphrase/interpretation performed. Read-
only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_reporting_rules", "law",
                   "official_source",
                   "nca_cybersecurity_violations_reporting_rules_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_reporting_rules", "law",
                       "verified")
RECORDS = os.path.join(OUT_VER, "nca_cybersecurity_violations_reporting_rules_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "nca_cybersecurity_violations_reporting_rules_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "nca_cybersecurity_violations_reporting_rules_arabic_legal_llm",
                        "nca_cybersecurity_violations_reporting_rules_legal_llm_001_008.json")

LAW_ID = "sa-nca-cybersecurity-violations-reporting-rules"
LAW_AR = "قواعد تنظيم الإبلاغ عن مخالفات الأمن السيبراني"
KEY_RE = r"nca_cybersecurity_violations_reporting_rules_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة القواعد أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((": " + title) if title else "")
        status = a["status"]
        ver.append({"law_key": "nca_cybersecurity_violations_reporting_rules",
                    "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "NCA_CYBERSECURITY_VIOLATIONS_REPORTING_RULES_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": status,
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": status,
                    "governing_source_note": ("Arabic governs; PRIMARY source is an official "
                                              "PDF on the National Cybersecurity Authority's "
                                              "own site (cdn.nca.gov.sa), already downloaded "
                                              "this session, cross-checked internally via a "
                                              "clean pdftotext -layout extraction AND an "
                                              "independent direct visual read of 200-400dpi "
                                              "rendered page images -- full word-for-word "
                                              "agreement across all 7 pages. The NCA Board of "
                                              "Directors decision number/date approving this "
                                              "SPECIFIC instrument could NOT be independently "
                                              "confirmed this pass -- a direct fetch of the "
                                              "companion investigation-rules instrument's own "
                                              "uqn.gov.sa gazette page confirmed the number "
                                              "suggested in this track's commissioning brief "
                                              "(ع26/1/1/1ت, 22/08/1447H) belongs to that "
                                              "DIFFERENT companion instrument, not this one -- "
                                              "see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's "
                                              "citation/provenance. TIER_2, not TIER_1."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "nca-cybersecurity-violations-reporting-rules-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "nca_cybersecurity_violations_reporting_rules/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من قواعد تنظيم الإبلاغ عن مخالفات الأمن السيبراني"
                                          % a["number_label_ar"]],
                    "text_status": status,
                    "source_trust": {"source_authority": ("NCA Board of Directors decision -- "
                                                          "exact decision number/date "
                                                          "unconfirmed for this specific "
                                                          "instrument this pass (see "
                                                          "known_unresolved_discrepancies); "
                                                          "text cross-verified via the "
                                                          "official cdn.nca.gov.sa PDF's clean "
                                                          "text layer AND an independent "
                                                          "direct visual read of rendered "
                                                          "page images, plus topical secondary "
                                                          "corroboration from arabi21.com and "
                                                          "akhbaar24.com"),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة الوطنية "
                                                            "للأمن السيبراني -- رقم القرار "
                                                            "وتاريخه غير مؤكَّدين بشكل مستقل "
                                                            "لهذا الصك تحديداً هذه الجولة؛ "
                                                            "النص مطابَق داخلياً عبر طبقة نص "
                                                            "PDF نظيفة من cdn.nca.gov.sa "
                                                            "وقراءة بصرية مباشرة مستقلة لصور "
                                                            "الصفحات، مع تدقيق ثانوي موضوعي "
                                                            "من arabi21.com وakhbaar24.com"),
                                     "source_status": status.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": status},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "nca_cybersecurity_violations_reporting_rules",
               "layer": "NCA_CYBERSECURITY_VIOLATIONS_REPORTING_RULES_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "official_text_status": arts[keys[0]]["status"],
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-nca-cybersecurity-violations-reporting-rules-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (8 مواد، "
                           "اصلية جميعها)",
               "title_en": ("Rules Organizing the Reporting of Cybersecurity Violations — "
                            "Arabic LLM-ready layer (8 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 8], "text_status": arts[keys[0]]["status"],
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready NCA Cybersecurity Violations Reporting Rules records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
