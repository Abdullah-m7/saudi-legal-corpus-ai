#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law of the Accounting and Auditing Profession track
(نظام مهنة المحاسبة والمراجعة, Royal Decree M/59, 27/7/1442H).

VERIFICATION TIER -- see sources/accounting_auditing/law/official_source/
accounting_auditing_law_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via a single reachable Wayback
Machine snapshot (20251015113239, 15 Oct 2025) because the live BOE portal
was unreachable this pass (curl exit 000 over HTTPS, HTTP 503 over HTTP).
The archived page was parsed with BeautifulSoup: 22 'article_item' divs,
none carrying an inline title (unlike gcc_anti_dumping_law's source page),
5 of them (Articles 1, 4, 5, 19, 20) additionally flagged 'changed-article'
with a nested changelog popup quoting Royal Decree M/169's (10/8/1446H)
amended wording verbatim.

CRITICAL VERIFIED ANOMALY: for those same 5 articles, BOE's own *main*
displayed article body text (as archived) still shows the OLDER,
pre-M/169 wording -- confirmed stale by diffing three snapshots spanning
Jan-Oct 2025. This track ingests the AMENDED wording (BOE's own
changelog-popup text, independently corroborated word-for-word by SOCPA's
own official PDF of the law and by two qanoonsa.com pages) as each
amended article's current text, NOT the stale main body. See
known_unresolved_discrepancies (key
accounting_auditing_boe_main_body_stale_vs_changelog_popup).

A SECOND, more recent amendment -- Council of Ministers Resolution 283
(22/4/1447H / 14 Oct 2025G, gazetted 31/10/2025G) -- further amended
Article 1's "الوزير" definition. It postdates this track's only available
BOE snapshot, so BOE shows no trace of it; this track incorporates it from
SOCPA's own currently-published PDF, cross-checked against qanoonsa.com
(see known_unresolved_discrepancies, key
accounting_auditing_cr283_not_yet_reflected_on_boe).

PREDECESSOR: this law's own Article 21 states it replaces (يحل محل) the
Law of Certified Public Accountants (Royal Decree M/12, 13/5/1412H) --
independently confirmed via BOE's own separate page for that law, whose
status field reads "لاغي" (repealed). Not ingested (historical context
only).

22 records: 17 اصلية, 5 معدلة (Articles 1, 4, 5, 19, 20), 0 ملغاة,
0 مضافة. No أبواب/فصول structure (flat 1-22). No inline per-article
titles in the BOE source (consistent with this corpus's finance_lease_law
precedent) -- no title_ar field is used.

No legal text is altered beyond whitespace normalization and (for the 5
amended articles only) reconstructing clean Unicode Arabic from BOE's own
changelog-popup wording, cross-checked against SOCPA's PDF. Arabic
governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "accounting_auditing", "law", "official_source",
                   "accounting_auditing_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "accounting_auditing", "law", "verified")
RECORDS = os.path.join(OUT_VER, "accounting_auditing_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "accounting_auditing_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "accounting_auditing_arabic_legal_llm",
                        "accounting_auditing_law_legal_llm_001_022.json")

LAW_ID = "sa-accounting-auditing-law-m59-1442"
LAW_AR = "نظام مهنة المحاسبة والمراجعة"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_BOE_WAYBACK_PRIMARY_X_SOCPA_"
              "OFFICIAL_PDF_X_QANOONSA_CROSSCHECK_LIVE_BOE_UNREACHABLE")
KEY_RE = r"accounting_auditing_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"accounting_auditing_art_001", "accounting_auditing_art_004",
                "accounting_auditing_art_005", "accounting_auditing_art_019",
                "accounting_auditing_art_020"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المحاسب القانوني الترخيص").split())


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
        ver.append({"law_key": "accounting_auditing", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ACCOUNTING_AUDITING_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on a single "
                                              "BOE-via-Wayback-Machine archived snapshot "
                                              "(20251015113239) as the PRIMARY source (live BOE "
                                              "unreachable this pass). Five articles (1, 4, 5, "
                                              "19, 20) are معدلة: BOE's own main body text for "
                                              "these is STALE (pre-M/169); this record instead "
                                              "carries BOE's own changelog-popup wording "
                                              "(quoting Royal Decree M/169, 10/8/1446H), "
                                              "cross-verified against SOCPA's official PDF and "
                                              "qanoonsa.com. Article 1 carries a further, more "
                                              "recent amendment (Council of Ministers "
                                              "Resolution 283, 22/4/1447H) sourced from SOCPA's "
                                              "PDF only (postdates this track's only available "
                                              "BOE snapshot) -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text as "
                                              "necessarily reflecting BOE's own live rendering."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "accounting-auditing-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "accounting_auditing/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام مهنة المحاسبة والمراجعة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/59 — laws.boe.gov.sa "
                                                          "via Wayback Machine archive (primary), "
                                                          "cross-verified against SOCPA's own "
                                                          "official PDF and qanoonsa.com; live "
                                                          "BOE unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/59) — نسخة أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine، مطابقة مع نسخة الهيئة السعودية للمراجعين والمحاسبين الرسمية (PDF) وقانونسا",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "accounting_auditing",
               "layer": "ACCOUNTING_AUDITING_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-accounting-auditing-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (22 مادة؛ 17 أصلية و5 معدلة)",
               "title_en": "Law of the Accounting and Auditing Profession — Arabic LLM-ready layer (22 records: 17 original, 5 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 22], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Accounting and Auditing Profession Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
