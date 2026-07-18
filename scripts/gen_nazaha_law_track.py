#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law (Statute) of the Control and Anti-Corruption Authority
track (نظام هيئة الرقابة ومكافحة الفساد, Royal Decree M/25, 23/1/1446H).

VERIFICATION TIER -- see sources/nazaha/law/official_source/
nazaha_law_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via TWO Wayback Machine snapshots
(20241101220240, 1 Nov 2024; 20260215014056, 15 Feb 2026 -- roughly 15.5
months apart) because the live BOE portal was unreachable this pass. Both
snapshots were parsed with BeautifulSoup: 24 'article_item' divs (all class
'no_alternate' -- zero amendment markers), interleaved in document order
with four باب (chapter) h3 headings. A byte-for-byte diff of the two
snapshots' extracted article text found ZERO differences -- strong evidence
the law remains wholly unamended.

A THIRD, independent time-point: a FAOLEX-hosted PDF (faolex.fao.org)
turned out to be a saved browser printout of this exact same BOE URL, dated
16/06/2025 -- its text (spot-checked) matches both Wayback snapshots
verbatim, giving three independent time-points spanning ~15.5 months with
byte/word-identical text.

SECONDARY CROSS-VERIFICATION: nezams.com independently confirms the decree
number/dates, status, and "لم يجرِ عليه تعديل" (no amendment made), with
Articles 1-14 matching in substance (partial full-text check).
qanoonsa.com independently confirms the same four-باب structure and
article ranges, and the same 24-article total.

24 records: all اصلية (0 معدلة, 0 ملغاة, 0 مضافة). Four أبواب: تعريفات
(1-2), جهاز الهيئة ومهماته واختصاصاته (3-17), أحكام متصلة بمكافحة جرائم
الفساد (18-22), أحكام ختامية (23-24). No inline per-article titles in the
BOE source -- no title_ar field is used; section_ar carries each article's
باب title.

CRITICAL CROSS-TRACK FINDING: this law's own enacting Royal Decree (clause
سابعاً) amends this corpus's already-ingested anti_bribery_law track by
substituting "هيئة الرقابة ومكافحة الفساد" for "رئاسة أمن الدولة" wherever
the latter appears in the Anti-Bribery Law -- but that track's own
discrepancy notes show its Articles 17 and 21 still carry the OLD phrase
per its own secondary sources. See known_unresolved_discrepancies (key
nazaha_anti_bribery_crossref_articles_17_21_stale) -- flagged for a
dedicated follow-up pass, not resolved here (out of scope for this track).

No legal text is altered beyond whitespace/line-break normalization
(<br> -> newline; inline <strong>/<span> runs within one <li>/<p> joined
without an inserted separator). Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nazaha", "law", "official_source",
                   "nazaha_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "nazaha", "law", "verified")
RECORDS = os.path.join(OUT_VER, "nazaha_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "nazaha_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "nazaha_arabic_legal_llm",
                        "nazaha_law_legal_llm_001_024.json")

LAW_ID = "sa-nazaha-law-m25-1446"
LAW_AR = "نظام هيئة الرقابة ومكافحة الفساد"
TOP_STATUS = ("UNAMENDED_TRIPLE_TIMEPOINT_BOE_WAYBACK_X_FAOLEX_PDF_MIRROR_X_NEZAMS_"
              "PARTIAL_X_QANOONSA_STRUCTURAL_CROSSCHECK_LIVE_BOE_UNREACHABLE")
KEY_RE = r"nazaha_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة الرئيس الوحدة").split())


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
        ver.append({"law_key": "nazaha", "law_component": "law",
                    "language": "ar",
                    "record_layer": "NAZAHA_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on two "
                                              "BOE-via-Wayback-Machine archived snapshots "
                                              "(20241101220240 and 20260215014056, ~15.5 "
                                              "months apart, byte-identical article text) "
                                              "plus a third independent time-point (a FAOLEX-"
                                              "hosted PDF mirror of the same BOE page, dated "
                                              "16/06/2025) as PRIMARY sources (live BOE "
                                              "unreachable this pass), cross-verified against "
                                              "nezams.com (partial, Arts. 1-14) and "
                                              "qanoonsa.com (structural, all 24 articles' "
                                              "chapter/range breakdown). All 24 articles are "
                                              "اصلية (unamended) -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact, in particular a critical cross-track "
                                              "finding regarding this corpus's already-"
                                              "ingested anti_bribery_law track's Articles 17 "
                                              "and 21, before relying on this track's text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "nazaha-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "nazaha/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام هيئة الرقابة ومكافحة الفساد" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/25 — laws.boe.gov.sa "
                                                          "via two Wayback Machine snapshots "
                                                          "(byte-identical) plus a FAOLEX PDF "
                                                          "mirror of the same BOE page, "
                                                          "cross-verified against nezams.com "
                                                          "and qanoonsa.com; live BOE "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/25) — نسختان أرشيفيتان من بوابة هيئة الخبراء عبر Wayback Machine (متطابقتان)، إضافة إلى نسخة PDF من FAOLEX لنفس صفحة الهيئة، مطابقة مع nezams.com وqanoonsa.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "nazaha",
               "layer": "NAZAHA_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-nazaha-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (24 مادة أصلية، أربعة أبواب)",
               "title_en": "Law (Statute) of the Control and Anti-Corruption Authority — Arabic LLM-ready layer (24 records, all original, unamended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 24], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Nazaha Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
