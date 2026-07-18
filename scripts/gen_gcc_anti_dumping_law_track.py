#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the GCC Unified Anti-Dumping, Countervailing and Safeguard
Measures Law track (القانون (النظام) الموحد لمكافحة الإغراق والتدابير
التعويضية والوقائية لدول مجلس التعاون لدول الخليج العربية, Royal Decree
M/30, 17/5/1427H).

VERIFICATION TIER -- STATUS constant
BOE_WAYBACK_ARCHIVE_PRIMARY_X_QISTAS_PARTIAL_STRUCTURAL_CROSSCHECK_LIVE_BOE_UNREACHABLE_M7_1434H_AMENDED_TEXT_NOT_INCORPORATED
reflects that laws.boe.gov.sa's LIVE portal was unreachable this pass (curl
returned exit code 35 / connection reset over HTTPS, HTTP 503 over plain
HTTP) -- BUT two independent Wayback Machine snapshots of the exact BOE
law-detail page (20231112034551 and 20250619192625, ~20 months apart) WERE
reachable and show an identical, unamended 17-article state. The archived
page was parsed with BeautifulSoup (locating each of 17 'article_item' divs,
its 'h3.center' heading and 'div.HTMLContainer' body) to recover the full
text of all 17 articles, the decree number/date, and BOE's own per-article
class attributes -- all 17 articles carry ONLY the default 'no_alternate'
class, with zero amended/repealed markers anywhere on the page.

This was cross-verified (partially -- articles 1-3 only) against qistas.com,
an independent Gulf-region legal-text aggregator, which matches BOE's
article numbering and content for the articles it surfaced.

CRITICAL, MOST-IMPORTANT DOCUMENTED DISCREPANCY: WIPO Lex (record SA086) and
a wholly separate, currently-in-force Saudi law's own official BOE-hosted
preamble (نظام المعالجات التجارية في التجارة الدولية, Royal Decree M/60,
29/4/1444H/2022) both independently indicate that Royal Decree No. (M/7)
dated 20/3/1434H (2013) approved an AMENDED ('المعدل') version of this
Unified Law that WIPO Lex says supersedes the M/30 text ingested here. The
GCC Secretariat General's own official PDF booklet (gcc-sg.org, fetched live
this pass) contains that amended text and shows it is a DIFFERENT,
restructured 15-article text (vs. this track's 17 articles). BOE's own
primary catalog page for this law -- this track's actual source, checked
across two Wayback snapshots 20 months apart -- lists ONLY M/30 as an
issuing instrument and shows zero per-article amendment markers, with no
on-page reference anywhere to M/7. This pass could NOT independently obtain
the exact Saudi-Gazette-published wording of M/7 itself (Umm Al-Qura Gazette
search and WIPO Lex's own full-text PDF endpoints were both unavailable this
pass). This track therefore ingests BOE's directly-verified 17-article
ORIGINAL text rather than silently substituting the unverified amended text.
See sources/gcc_anti_dumping/law/official_source/
gcc_anti_dumping_law_official_source.json for the full methodology note and
every documented discrepancy, including the un-ingested companion
Implementing Regulation and the correction of this corpus's own
coverage-gap-map article-count estimate (30-40 -> confirmed 17).

17 records, ALL اصلية per BOE's own no-amendment-marker rendering of the
text this track ingests -- this does NOT mean the Law has definitely never
been amended in substance (see the M/7 discrepancy above); it means BOE's
own currently-served text carries no per-article amendment marker.

No legal text is altered beyond whitespace normalization (collapsing
repeated spaces, converting <br> tags to newlines). Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gcc_anti_dumping", "law", "official_source",
                   "gcc_anti_dumping_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "gcc_anti_dumping", "law", "verified")
RECORDS = os.path.join(OUT_VER, "gcc_anti_dumping_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "gcc_anti_dumping_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "gcc_anti_dumping_arabic_legal_llm",
                        "gcc_anti_dumping_law_legal_llm_001_017.json")

LAW_ID = "sa-gcc-anti-dumping-law-m30-1427"
LAW_AR = "القانون (النظام) الموحد لمكافحة الإغراق والتدابير التعويضية والوقائية لدول مجلس التعاون لدول الخليج العربية"
STATUS = ("BOE_WAYBACK_ARCHIVE_PRIMARY_X_QISTAS_PARTIAL_STRUCTURAL_CROSSCHECK_"
          "LIVE_BOE_UNREACHABLE_M7_1434H_AMENDED_TEXT_NOT_INCORPORATED")
KEY_RE = r"gcc_anti_dumping_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك القانون").split())


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
        title = a.get("title_ar") or ""
        display_title = ("%s: %s" % (a["number_label_ar"], title) if title
                          else a["number_label_ar"])
        ver.append({"law_key": "gcc_anti_dumping", "law_component": "law",
                    "language": "ar",
                    "record_layer": "GCC_ANTI_DUMPING_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": title,
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a BOE-via-"
                                              "Wayback-Machine archived snapshot as the PRIMARY "
                                              "source (live BOE unreachable), partially "
                                              "cross-verified against qistas.com (Articles 1-3 "
                                              "only). A credible, multiply-corroborated but "
                                              "UNRESOLVED discrepancy exists regarding a possible "
                                              "2013 amendment (Royal Decree M/7, 20/3/1434H) to a "
                                              "differently-structured 15-article text -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact (key "
                                              "gcc_anti_dumping_m7_1434h_amended_text_not_"
                                              "incorporated) before relying on this track's "
                                              "17-article numbering as necessarily the current "
                                              "text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": display_title,
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "gcc-anti-dumping-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, display_title),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, display_title),
                    "article_path": "gcc_anti_dumping/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من القانون الموحد لمكافحة الإغراق" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/30 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "partially cross-verified against "
                                                          "qistas.com (Arts 1-3); live BOE "
                                                          "unreachable this pass; a candidate 2013 "
                                                          "amendment (M/7) is documented as an "
                                                          "UNRESOLVED discrepancy, not "
                                                          "incorporated into this text"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/30) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة جزئياً مع qistas.com؛ تعديل محتمل عام 1434هـ (م/7) موثق كفجوة غير محسومة",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "gcc_anti_dumping",
               "layer": "GCC_ANTI_DUMPING_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-gcc-anti-dumping-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 مادة؛ جميعها أصلية بحسب النص المعروض حالياً على بوابة هيئة الخبراء)",
               "title_en": "GCC Unified Anti-Dumping, Countervailing and Safeguard Measures Law — Arabic LLM-ready layer (17 records, per BOE's currently-served text)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 17], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready GCC Anti-Dumping Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
