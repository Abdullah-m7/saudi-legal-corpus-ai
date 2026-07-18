#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Cooperative Health Insurance Law track (نظام الضمان الصحي
التعاوني, Royal Decree M/10, 1/5/1420H).

VERIFICATION TIER -- STATUS constant
BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503
reflects that laws.boe.gov.sa's LIVE portal was unreachable this pass
(direct HTTPS connection reset) -- BUT a Wayback Machine snapshot of this
exact BOE law page WAS reachable via direct curl over https://web.archive.org/
(note: the plain http:// scheme for web.archive.org was blocked by this
environment's egress policy; https:// succeeded), and is treated as this
track's PRIMARY source. It was parsed with BeautifulSoup (naive regex/tag-
stripping was found to truncate Article 14's nested list) to recover the
full text of all 19 articles, the decree number/date, and BOE's own tracked
amendment annotations. This was cross-verified against nezams.com's HTML
transcription (fetched directly with a browser User-Agent header, after a
bare curl request and the r.jina.ai proxy both failed) -- ZERO substantive
discrepancies across all 17 unamended articles and across the 1420H/1425H
states of the two amended articles (4 and 14).

19 records: 17 اصلية / 2 معدلة across TWO amendment waves -- Council of
Ministers Resolution 246 (4/9/1425H, renamed a ministry in Articles 4 and
14) and Resolution 472 (18/8/1440H, restructured Article 4's council
membership only). BOE's own page does not reproduce the 472/1440H
replacement text (citation only); nezams.com is the sole source for that
specific text, and its raw HTML contained evident single-character
transcription artifacts that are normalized and fully disclosed -- see
sources/cooperative_health_insurance/law/official_source/
cooperative_health_insurance_law_official_source.json for the full
methodology note and every documented discrepancy, including the
un-ingested companion Implementing Regulation and the out-of-scope
Umrah/Hajj-coverage-expansion circulars.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cooperative_health_insurance", "law", "official_source",
                   "cooperative_health_insurance_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cooperative_health_insurance", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cooperative_health_insurance_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cooperative_health_insurance_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cooperative_health_insurance_arabic_legal_llm",
                        "cooperative_health_insurance_law_legal_llm_001_019.json")

LAW_ID = "sa-cooperative-health-insurance-law-m10-1420"
LAW_AR = "نظام الضمان الصحي التعاوني"
STATUS = "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503"
KEY_RE = r"cooperative_health_insurance_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الضمان الصحي التعاوني").split())


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


def _original_text(a):
    for k in ("original_1420h_text", "original_1425h_text", "original_1440h_text"):
        if a.get(k):
            return a[k]
    return None


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
        text = a["text"]
        original_text = _original_text(a)
        ver.append({"law_key": "cooperative_health_insurance", "law_component": "law",
                    "language": "ar",
                    "record_layer": "COOPERATIVE_HEALTH_INSURANCE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_text": original_text,
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a BOE-via-"
                                              "Wayback-Machine archived snapshot as the PRIMARY "
                                              "source (live BOE unreachable), cross-verified "
                                              "against nezams.com's HTML transcription (zero "
                                              "substantive discrepancies across all 17 "
                                              "unamended articles and the 1420H/1425H states of "
                                              "the 2 amended articles). Article 4's second "
                                              "(1440H) amendment text rests on nezams.com alone "
                                              "-- BOE cites the amending resolution but does not "
                                              "reproduce its text -- and had evident single-"
                                              "character transcription artifacts normalized and "
                                              "disclosed. See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for full caveats, including the "
                                              "un-ingested companion Implementing Regulation."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "cooperative-health-insurance-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "cooperative_health_insurance/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الضمان الصحي التعاوني" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/10 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "cross-verified against nezams.com; "
                                                          "live BOE unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/10) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع نزامز.كوم",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cooperative_health_insurance",
               "layer": "COOPERATIVE_HEALTH_INSURANCE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cooperative-health-insurance-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة؛ 17 أصلية، 2 معدّلة)",
               "title_en": "Saudi Cooperative Health Insurance Law — Arabic LLM-ready layer (19 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Cooperative Health Insurance Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
