#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Rules for Detecting and Investigating Cybersecurity Violations track
(قواعد ضبط مخالفات الأمن السيبراني والتحقيق فيها), issued by the Board of Directors of
the National Cybersecurity Authority (NCA), Decision No. (ع26/1/1/1ت) dated 22/8/1447H,
implementing Item (سادساً) of this corpus's own cybersecurity_authority_enablers track
(the Authority's Regulatory/Legal Enablers, Royal Decree M/117, 21/6/1446H), and published
in the Umm Al-Qura Official Gazette (uqn.gov.sa/decisions-and-regulations/4001430) with a
dateline of 3/2/1448H = 17/7/2026G -- a VERY recent instrument, gazetted only ~11 days
before this track's own build date (2026-07-28).

VERIFICATION TIER -- see this track's own official_source.json for the full account
(verification_methodology_note / known_unresolved_discrepancies). Summary:

TIER: TIER_1_PRIMARY_MULTI_SOURCE. Two independent, directly-fetched, official/primary
government sources agree word-for-word on the governing Arabic text of all 9 articles:
(1) NCA's own official website -- a prior research pass this session had already
downloaded this instrument's PDF; this pass independently re-fetched the SAME document
live from nca.gov.sa's own CDN (HTTP 200, 7 pages) via a URL surfaced by WebFetch against
nca.gov.sa/ar/laws-and-regulations/. The live copy differs from the earlier-downloaded
copy in exactly three small grammatical corrections (Article 3, Article 4(3), Article
8(2)) -- NCA appears to have silently fixed three typos in its own web-hosted copy of this
very recently issued instrument between the two fetches. (2) The Umm Al-Qura Official
Gazette (uqn.gov.sa/decisions-and-regulations/4001430) -- an entirely separate government
portal from NCA -- whose own page embeds the COMPLETE Arabic text of all 9 articles in a
server-rendered '<article id="article-content">' HTML element (not merely a topical
summary), independently confirming the SAME governing text, INCLUDING the same three
corrections found in the live NCA PDF (i.e. the gazette matches the corrected, live PDF
copy, not the earlier pre-correction copy). No OCR was required for either source: this
instrument's PDF, unlike this corpus's cybersecurity_authority_law/
cybersecurity_authority_enablers tracks' own PDFs, has no letter-transposition corruption
in its text layer (confirmed independently via both pdftotext and PyMuPDF/fitz); every
article was additionally cross-checked by direct visual inspection of 400dpi rendered page
images.

9 articles, all اصلية (first, single edition; no amendment found this pass -- expected,
given the instrument was gazetted only ~11 days before this track's build date). No أبواب
or فصول -- a flat sequence of 9 numbered مواد (chapter_structure carries one flat entry,
articles 1-9).

Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_investigation_rules", "law",
                   "official_source",
                   "nca_cybersecurity_violations_investigation_rules_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_investigation_rules", "law",
                       "verified")
RECORDS = os.path.join(OUT_VER,
                       "nca_cybersecurity_violations_investigation_rules_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER,
                       "nca_cybersecurity_violations_investigation_rules_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "nca_cybersecurity_violations_investigation_rules_arabic_legal_llm",
                        "nca_cybersecurity_violations_investigation_rules_legal_llm_001_009.json")

LAW_ID = "sa-nca-cybersecurity-violations-investigation-rules-1447"
LAW_AR = "قواعد ضبط مخالفات الأمن السيبراني والتحقيق فيها"
STATUS = "NCA_OFFICIAL_LIVE_PDF_X_UQN_GAZETTE_FULLTEXT_DUAL_PRIMARY_CROSS_VERIFIED_TIER1"
KEY_RE = r"nca_cybersecurity_violations_investigation_rules_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة القواعد أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة المفتش").split())


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
        text = a["text"]
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((": " + title) if title else "")
        ver.append({"law_key": "nca_cybersecurity_violations_investigation_rules",
                    "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "NCA_CYBERSECURITY_VIOLATIONS_INVESTIGATION_RULES_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY sources are (1) the "
                                              "National Cybersecurity Authority's own official "
                                              "website PDF (cdn.nca.gov.sa, live-refetched) and "
                                              "(2) the Umm Al-Qura Official Gazette's own full "
                                              "HTML text (uqn.gov.sa/decisions-and-regulations/"
                                              "4001430) -- two independent official/primary "
                                              "government sources agreeing word-for-word, no OCR "
                                              "required for either. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the full account, including three "
                                              "minor typos found corrected between an earlier-"
                                              "downloaded PDF copy and the live-refetched one."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "nca-cybersecurity-violations-investigation-rules-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "nca_cybersecurity_violations_investigation_rules/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من قواعد ضبط مخالفات الأمن السيبراني والتحقيق فيها"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Board of Directors of the National "
                                                          "Cybersecurity Authority (NCA) Decision "
                                                          "No. (ع26/1/1/1ت), 22/8/1447H -- cross-"
                                                          "verified via NCA's own official website "
                                                          "(cdn.nca.gov.sa, live-refetched) and the "
                                                          "Umm Al-Qura Official Gazette (uqn.gov.sa"
                                                          "/decisions-and-regulations/4001430, "
                                                          "dateline 3/2/1448H = 17/7/2026G)"),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة الوطنية للأمن "
                                                            "السيبراني رقم (ع26/1/1/1ت) وتاريخ "
                                                            "22/8/1447هـ -- تم التحقق عبر الموقع "
                                                            "الإلكتروني الرسمي للهيئة "
                                                            "(cdn.nca.gov.sa، بإعادة جلب حية) "
                                                            "وجريدة أم القرى الرسمية (uqn.gov.sa"
                                                            "/decisions-and-regulations/4001430، "
                                                            "بتاريخ نشر مؤكَّد 3/2/1448هـ الموافق "
                                                            "17/7/2026م)"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "nca_cybersecurity_violations_investigation_rules",
               "layer": "NCA_CYBERSECURITY_VIOLATIONS_INVESTIGATION_RULES_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-nca-cybersecurity-violations-investigation-rules-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (9 مواد، "
                           "اصلية جميعها)",
               "title_en": ("Rules for Detecting and Investigating Cybersecurity Violations — "
                            "Arabic LLM-ready layer (9 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 9], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready NCA Cybersecurity Violations Investigation Rules records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
