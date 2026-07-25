#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law on Protection of Whistleblowers,
Witnesses, Experts and Victims (اللائحة التنفيذية لنظام حماية المبلغين والشهود
والخبراء والضحايا).

Source: sources/whistleblower_regulation/law/official_source/
whistleblower_regulation_official_source.json — independently built from the Umm
Al-Qura official gazette (issue 5163, 12 June 2026), the CORRECTED/final printing
of the regulation approved by Council of Ministers decision (892) of 19 May 2026
(2/12/1447H). Article count is 12 (NOT 11 — the number reported in earlier/secondary
coverage, which reflects the SUPERSEDED draft printed a week earlier in issue 5162
under the label "مشروع اللائحة التنفيذية"; that printing was corrected by an
official gazette errata one week later). See the official_source's
`known_unresolved_discrepancies` and `gazette_publications` for the full
provenance/discrepancy trail, including the corrected decision number (892, not the
893 reported by several secondary sources) and the exclusion of the unrelated 2024
public-consultation draft.

This is a VERY RECENT, thinly-corroborated instrument: no independent secondary
legal commentary on the final 12-article text was found during verification (all
secondary coverage located reflects the superseded 11-article draft). Confidence
here rests on two independently hash-recorded primary-source gazette PDFs, not on
secondary cross-corroboration — hence TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE (see
sources/whistleblower_regulation/law/verified/whistleblower_regulation_verified_summary.json).

Articles are numbered by their ordinal position in the corrected gazette printing
(1..12; no مكرر). number_label_ar preserves each article's official label verbatim.
No legal text is altered beyond the three documented HTML-mirror-defect fixes
recorded in official_source (all cross-verified against the committed gazette
PDFs). Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs. Standalone track: this script does not modify
any shared pipeline file.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "whistleblower_regulation", "law", "official_source",
                   "whistleblower_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "whistleblower_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "whistleblower_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "whistleblower_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "whistleblower_regulation_arabic_legal_llm",
                        "whistleblower_regulation_legal_llm_001_012.json")

LAW_ID = "sa-whistleblower-regulation-com892-1447"
LAW_AR = "اللائحة التنفيذية لنظام حماية المبلغين والشهود والخبراء والضحايا"
STATUS = "UQN_GAZETTE_PDF_CROSS_VERIFIED_HTML_MIRROR"
KEY_RE = r"whistleblower_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


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
        text = a["text"]
        ver.append({"law_key": "whistleblower_regulation", "law_component": "regulation", "language": "ar",
                    "record_layer": "WHISTLEBLOWER_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "draft_correspondence_note": a.get("draft_correspondence_note"),
                    "html_mirror_defect_fixed": a.get("html_mirror_defect_fixed"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official Umm Al-Qura gazette text (issue "
                                              "5163, corrected/final printing) cross-verified against a "
                                              "directly-downloaded, hash-recorded gazette PDF and an "
                                              "independent HTML mirror; three documented HTML-mirror "
                                              "transcription defects were fixed by cross-reference to the "
                                              "PDF and the superseded draft printing (see official_source)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "whistleblower-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "whistleblower_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام حماية المبلغين والشهود "
                                          "والخبراء والضحايا" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Umm Al-Qura Official Gazette (uqn.gov.sa) — "
                                                          "issue 5163, corrected/final printing",
                                     "source_authority_ar": "جريدة أم القرى الرسمية — العدد 5163 "
                                                            "(النص المصوَّب والنهائي)",
                                     "source_status": "uqn_gazette_pdf_cross_verified_html_mirror",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "whistleblower_regulation",
               "layer": "WHISTLEBLOWER_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "council_of_ministers_decision": src["council_of_ministers_decision"],
               "gazette_publications": src["gazette_publications"],
               "consolidated_amended_regulation": False,
               "tier": "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE",
               "tier_rationale": ("Extremely recent instrument (finalized ~7 weeks, corrected ~6 weeks, "
                                 "before this corpus's current date) verified directly against two "
                                 "independently hash-recorded primary-source gazette PDFs (issue 5162 "
                                 "draft + issue 5163 correction), which is a strong primary basis; "
                                 "however no secondary legal commentary on the FINAL 12-article/decision-"
                                 "892 text was located, and several secondary sources actively conflict "
                                 "with the primary-source-confirmed facts (article count 11 vs. 12, "
                                 "decision number 893 vs. 892) because they reflect the superseded draft. "
                                 "Given single-channel-of-record verification plus a documented conflict "
                                 "with existing secondary coverage, TIER_4 is the honest classification, "
                                 "not TIER_2."),
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-whistleblower-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 مادة؛ النص المصوَّب "
                                    "والنهائي الصادر في جريدة أم القرى العدد 5163)",
               "title_en": "Saudi Whistleblower/Witness/Expert/Victim Protection Law Implementing "
                          "Regulation — Arabic LLM-ready layer (12 records, corrected/final text)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 12], "text_status": STATUS,
               "consolidated_amended_regulation": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Whistleblower Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
