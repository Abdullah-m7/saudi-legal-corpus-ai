#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Maritime Commercial Regulation track -- specifically
لائحة تسجيل السفن وقيد الوحدات البحرية (the Ship Registration and Maritime
Unit Registration Regulation), issued by the General Authority for Transport
(TGA) implementing Article 7 of the Maritime Commercial Law (Royal Decree
M/33, 5/4/1440H, already tracked at sources/maritime_commercial/).

SCOPING NOTE -- this is ONE regulation out of a FAMILY
Article 390 of the base Law requires the TGA president to issue 'اللوائح
اللازمة' (the regulations -- PLURAL -- necessary for the Law) within 180
days. This Law has in fact spawned a large family of separate TGA
regulations (ship registration, maritime transport business licensing,
maritime accident investigation, classification-society authorization,
maritime service records, ticket sales, etc.) plus a further cluster of
TGA-administered regulations implementing ratified international maritime
conventions (SOLAS, MARPOL, COLREG, STCW, etc.). This track deliberately
ingests ONLY the ship-registration regulation (the most solidly
cross-checkable single instrument found this pass) rather than forcing
several structurally distinct regulations into one track. See
known_unresolved_discrepancies in the official_source.json (entry
'maritime_commercial_regulation_full_family_scope_not_ingested') for the
full enumerated family scope and every other candidate's TGA regulation id.

VERIFICATION TIER -- STATUS constant
TGA_WAYBACK_DOUBLE_SNAPSHOT_X_QISTAS_PARTIAL_CROSSCHECK_LIVE_TGA_UNREACHABLE
reflects: tga.gov.sa's LIVE portal was unreachable this pass (direct HTTPS
curl returned 'Recv failure: Connection reset by peer'; old.tga.gov.sa no
longer resolves via DNS at all; r.jina.ai's reader-proxy fallback refused
anonymous queries). TWO INDEPENDENT Wayback Machine historical snapshots of
TGA's own regulation page (2022-06-21 and 2025-01-17, 2 years 7 months
apart) WERE reachable via https:// and were parsed with BeautifulSoup
(locating each of 49 'regulation-title-Article' accordion headers and its
sibling '.regulation-content' div, plus the 4 interleaved 'فصل' chapter
headers, plus ONE further sibling of a distinct 'regulation-title-Other'
class holding the 22-row جدول العقوبات penalty table). A full programmatic
diff of both snapshots' extracted article text and penalty table found
ZERO differences -- byte-for-byte identical 2.5+ years apart. qistas.com's
gated legislation-viewer preview independently corroborates Articles 1-3
(word-for-word identical substance; qistas.com renders enumerated
definitions with explicit digit-dot prefixes that TGA's own HTML does not
embed as literal text, a presentational difference only -- see
known_unresolved_discrepancies). Articles 4-49 and the penalty table rest
on the TGA-via-Wayback source alone (two identical historical crawls, not
independently cross-site verified) -- a materially weaker tier than the
base law's BOE x nezams.com x BOE-English-PDF triple cross-check, and this
is disclosed rather than overstated. See sources/maritime_commercial_regulation/
law/official_source/maritime_commercial_regulation_official_source.json for
the full methodology note and every documented discrepancy, including the
unconfirmed original decision number/date and the unconfirmed claimed
Article-46-مكرر amendment (absent from TGA's own page in every snapshot
checked, 2022-2025).

49 records, ALL اصلية (this pass found no amendment reflected in the
primary TGA text). No legal text is translated, paraphrased, or
interpreted; no digit prefixes were synthesized for enumerated sub-clauses
that TGA's own HTML renders via CSS numbering only (see
known_unresolved_discrepancies). Arabic governs. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "maritime_commercial_regulation", "law", "official_source",
                   "maritime_commercial_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "maritime_commercial_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "maritime_commercial_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "maritime_commercial_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "maritime_commercial_regulation_arabic_legal_llm",
                        "maritime_commercial_regulation_legal_llm_001_049.json")

LAW_ID = "sa-maritime-commercial-regulation-ship-registration-tga-1441"
LAW_AR = "لائحة تسجيل السفن وقيد الوحدات البحرية"
STATUS = "TGA_WAYBACK_DOUBLE_SNAPSHOT_X_QISTAS_PARTIAL_CROSSCHECK_LIVE_TGA_UNREACHABLE"
KEY_RE = r"maritime_commercial_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك السفينة الوحدة البحرية").split())


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
        text = a["text"]
        title = a.get("article_title_ar") or ""
        label_full = a["number_label_ar"] + ((": " + title) if title else "")
        ver.append({"law_key": "maritime_commercial_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "MARITIME_COMMERCIAL_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_text": a.get("original_1440h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on TWO "
                                              "independent Wayback-Machine historical "
                                              "snapshots of TGA's own regulation page "
                                              "(2022-06-21 and 2025-01-17), byte-for-byte "
                                              "identical, as the PRIMARY source (live TGA "
                                              "unreachable), partially cross-verified "
                                              "against qistas.com's gated preview for "
                                              "Articles 1-3 only. Implements Article 7 of "
                                              "the Maritime Commercial Law (Royal Decree "
                                              "M/33, 5/4/1440H). See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact for full caveats, "
                                              "including the unconfirmed original "
                                              "decision number/date, the unconfirmed "
                                              "claimed Article-46-مكرر amendment, and "
                                              "the full un-ingested regulation-family "
                                              "scope."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": label_full,
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "maritime-commercial-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label_full),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label_full),
                    "article_path": "maritime_commercial_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من لائحة تسجيل السفن" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("TGA (الهيئة العامة للنقل) "
                                                          "regulation page via Wayback "
                                                          "Machine archive (primary, two "
                                                          "independent identical "
                                                          "snapshots), partially "
                                                          "cross-verified against "
                                                          "qistas.com (Articles 1-3 "
                                                          "only); live TGA unreachable "
                                                          "this pass"),
                                     "source_authority_ar": "الهيئة العامة للنقل — نسخة أرشيفية عبر Wayback Machine (لقطتان مستقلتان متطابقتان)، مطابقة جزئية مع قِسطاس للمواد 1-3 فقط",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "maritime_commercial_regulation",
               "layer": "MARITIME_COMMERCIAL_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "implements_law_key": src.get("implements_law_key"),
               "implements_law_ar": src.get("implements_law_ar"),
               "implements_article_ar": src.get("implements_article_ar"),
               "decree": src.get("decree"), "decree_date_hijri": src.get("decree_date_hijri"),
               "issuing_authority_ar": src.get("issuing_authority_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "penalty_table_ar": src.get("penalty_table_ar", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-maritime-commercial-regulation-ship-registration-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (49 مادة؛ جميعها أصلية)",
               "title_en": "Ship Registration and Maritime Unit Registration Regulation (TGA) — Arabic LLM-ready layer (49 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 49], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Maritime Commercial Regulation "
          "(Ship Registration) records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
