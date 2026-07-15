#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Executive Working Mechanism for the Law of the Judiciary and
the Law of the Board of Grievances (آلية العمل التنفيذية لنظام القضاء ونظام
ديوان المظالم).

Source: the official MOJ legal-portal text (Royal Decree م/78, 19/09/1428H —
the same decree promulgating the companion Law of the Judiciary and Law of
the Board of Grievances), fetched item-by-item (get-Section-Changes, 0
divergences from statuteStructure) and cross-verified against the official
MOJ PDF. This PDF's text layer exhibits the known RTL/ligature extraction
artifact seen elsewhere in this corpus, which caps automated similarity
scoring below the 0.90 floor for 14 of 15 items (mean 0.5026, min 0.1253)
despite the underlying text being verbatim-correct; those 14 were visually
adjudicated against the rendered PDF pages, and all 15 were visually read in
full. This mechanism is IN FORCE, implementing the transitional/executive
provisions of the two companion laws (formation of the Supreme Judicial
Council and Board of Administrative Judiciary, court conversion, staffing,
budgets, transitional periods).

NOT A FRESH ISSUANCE: 14 of 15 items are اصلية (unmodified since 1428H); item
7 (سابعاً, labor courts) is معدلة with a 2-version amendment history —
originally اصلية (1428H) -> amended by Royal Decree م/6 (02/01/1440H) ->
amended again by Royal Decree م/113 (09/11/1443H, current in-force text).
Item 7 carries its full amendment_history (see source artifact); no items
are repealed or added.

Items are numbered by ordinal position across the whole document (1..15,
no مكرر), grouped into 3 sections (9 + 5 + 1 items) whose Arabic ordinal-word
sequence markers (أولاً/ثانياً/...) repeat per section rather than being
globally unique — section_ar disambiguates. DOCUMENTED SOURCE ANOMALIES
(confirmed identically in both official sources): (1) item 9's heading reads
"شبة القضائية" (taa marbuta) instead of "شبه" (heh); (2) item 10's heading
reads "بمجل القضاء الإداري", missing the final س of مجلس (the item's own
body text correctly uses "مجلس القضاء الإداري"). Both preserved verbatim.
Items 3, 12 have empty portal name fields (bare sequence-marker headings);
item 15 (all of section 3) uses the literal "أحكام عامة" as its own label.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "judiciary_bog", "mechanism", "official_source",
                   "judiciary_bog_mechanism_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "judiciary_bog", "mechanism", "verified")
RECORDS = os.path.join(OUT_VER, "judiciary_bog_mechanism_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "judiciary_bog_mechanism_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "judiciary_bog_arabic_legal_llm",
                        "judiciary_bog_mechanism_legal_llm_001_015.json")

LAW_ID = "sa-judiciary-bog-mechanism-m78-1428"
LAW_AR = "آلية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"judiciary_bog_mechanism_art_(\d{3})$"
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
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        ver.append({"law_key": "judiciary_bog", "law_component": "mechanism", "language": "ar",
                    "record_layer": "JUDICIARY_BOG_MECHANISM_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": hist,
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ portal text "
                                              "(statute/get-Statute-gateway-Detail cross-checked "
                                              "against section/get-Section-Changes, 0 divergences) "
                                              "cross-verified against the official MOJ PDF (verbatim; "
                                              "the PDF text layer's RTL/ligature extraction artifact "
                                              "caps automated similarity scoring below the 0.90 floor "
                                              "for 14 of 15 records, so those were confirmed verbatim "
                                              "by direct visual inspection of the rendered PDF pages, "
                                              "200dpi, all 8 pages; the remaining 1 record scored "
                                              ">=0.90 automatically and was also visually spot-checked)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "mechanism", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "judiciary-bog-mechanism-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "judiciary_bog/mechanism/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["البند %d %s" % (n, LAW_AR),
                                          "%s البند %d" % (LAW_AR, n),
                                          "آلية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم %d" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "judiciary_bog", "layer": "JUDICIARY_BOG_MECHANISM_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-judiciary-bog-mechanism-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "mechanism",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 بنداً؛ 14 أصلية، 1 معدّلة)",
               "title_en": "Saudi Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances — Arabic LLM-ready layer (15 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Judiciary/Board of Grievances Executive Mechanism records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
