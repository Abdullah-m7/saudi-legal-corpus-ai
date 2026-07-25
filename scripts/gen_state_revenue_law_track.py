#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the State Revenue Law track (نظام إيرادات الدولة, Royal Decree
M/68, 18/11/1431H, approving Council of Ministers Resolution 359 dated
17/11/1431H — one day EARLIER than the decree, not the same date as an
earlier unverified research lead had claimed).

DISTINCT VERIFICATION TIER — this track's 32 records (31 numbered articles
plus Article 28-bis / المادة الثامنة والعشرون مكرر) rest on THREE
independent sources: (1) laws.boe.gov.sa (Bureau of Experts / BOE portal),
lawId 8b100aee-54a5-48c1-9866-a9a700f2d539, reached via the Internet
Archive Wayback Machine after the live portal returned HTTP 503 on direct
fetch; (2) nezams.com, fetched directly; (3) qanoonsa.com, corroborating
the decree citation via indexed search snippets. All 32 records are cross-
verified from at least two of these three sources in full agreement on
substantive text.

CONFIRMED FINDINGS THIS PASS:
  - Article 25 (معدلة): BOE's own per-article changelog carries the CURRENT
    post-amendment text (Royal Decree M/5, 2/1/1440H, deleting "أو تقسيط"),
    while BOE's default main-body rendering for the SAME article is STALE
    pre-amendment text -- a confirmed instance of this corpus's known BOE
    staleness pattern. nezams.com shows the identical split. Because both
    the original and current wording are independently confirmed, this
    track populates original_1431h_text for Article 25 -- a rare case
    where the pre-amendment text is NOT a documented gap.
  - Article 28-bis (مضافة): genuinely exists; its substantive text is
    identical across BOE and nezams.com. The two sources DISAGREE on the
    adding instrument: BOE cites Royal Decree M/93 (1/10/1443H); nezams.com
    cites Council of Ministers Resolution 198 (4/4/1443H). This track uses
    BOE's attribution as primary and records nezams.com's conflicting one
    in the same article's amendment_history, unresolved.
  - No formal فصل (chapter) structure exists for this law per BOE's own
    markup -- unlike this corpus's other fiscal-law tracks.
  - Article 30 confirms this law repeals its predecessor, نظام جباية أموال
    الدولة (Royal Will 41/3/2, 12/4/1359H).

SCOPE EXCLUSION -- a July 2026 Council of Ministers approval of an
"updated" version of this law is deliberately NOT represented here: no
promulgating Royal Decree / Resolution number for that update was found in
this research pass (aawsat.com and sabq.org both report only the Cabinet's
14 July 2026 approval, with no instrument number). This track is Royal
Decree M/68 (1431H) as amended by M/5 (1440H) and M/93 (1443H) only -- the
pre-2026-update, currently-in-force consolidated text.

See sources/state_revenue/law/official_source/
state_revenue_law_official_source.json for the full methodology note and
all documented discrepancies. No legal text is altered. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "state_revenue", "law", "official_source",
                   "state_revenue_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "state_revenue", "law", "verified")
RECORDS = os.path.join(OUT_VER, "state_revenue_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "state_revenue_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "state_revenue_arabic_legal_llm",
                        "state_revenue_law_legal_llm_001_032.json")

LAW_ID = "sa-state-revenue-law-m-68-1431"
LAW_AR = "نظام إيرادات الدولة"
STATUS = "BOE_WAYBACK_X_NEZAMS_X_QANOONSA_CROSS_VERIFIED"
KEY_RE = r"state_revenue_art_(\d{3})(_mukarrar)?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات المجلس تضع تعمل تتولى للوزارة").split())

GOV_NOTE = ("Arabic governs; this track's text rests on THREE independent sources -- "
            "laws.boe.gov.sa (via the Wayback Machine, after the live portal returned HTTP 503) "
            "x nezams.com x qanoonsa.com -- with full agreement for all 32 records. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact for the full caveats, including the confirmed BOE stale-main-body-vs-"
            "changelog split on Article 25, the unresolved two-source conflict over which "
            "instrument added Article 28-bis, and the explicit exclusion of an unconfirmed "
            "July-2026 'updated' version of this law.")


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
    return (int(m.group(1)), 1 if m.group(2) else 0)


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
        n, is_muk = int(m.group(1)), bool(m.group(2))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({
            "law_key": "state_revenue", "law_component": "law", "language": "ar",
            "record_layer": "STATE_REVENUE_LAW_ARABIC_VERIFIED_TEXT",
            "article_number": n, "is_mukarrar": is_muk, "article_key": key,
            "number_label_ar": a["number_label_ar"],
            "section_ar": a.get("section_ar", ""),
            "article_text_verified": text,
            "verification_status": a["status"],
            "legal_status_ar": ls,
            "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
            "amendment_history": a.get("history"),
            "original_1431h_text": a.get("original_1431h_text"),
            "official_text_status": STATUS,
            "governing_source_note": GOV_NOTE,
            "translation_performed": False, "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False, "english_used_for_correction": False,
        })
        llm.append({
            "law_id": LAW_ID, "law_component": "law", "article_number": n,
            "is_mukarrar": is_muk, "article_key": key,
            "article_title_ar": a["number_label_ar"],
            "section_ar": a.get("section_ar") or "",
            "legal_status_ar": ls, "is_repealed": is_repealed,
            "is_added": is_added, "is_amended": is_amended,
            "record_id": "state-revenue-law-llm-art-%03d" % idx,
            "record_type": "verified_arabic_article", "language": "ar",
            "governing_text_language": "ar", "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
            "article_path": "state_revenue/law/articles/%s" % key,
            "keywords_ar": _kw(text),
            "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                  "%s %s" % (LAW_AR, a["number_label_ar"]),
                                  "%s من نظام إيرادات الدولة" % a["number_label_ar"]],
            "text_status": a["status"],
            "source_trust": {"source_authority": GOV_NOTE,
                             "source_status": a["status"].lower(),
                             "source_document_ar": LAW_AR,
                             "legal_status_ar": ls,
                             "verification_status": a["status"]},
            "translation_performed": False, "legal_interpretation_performed": False,
            "english_used_for_correction": False, "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    json.dump({
        "law_key": "state_revenue",
        "layer": "STATE_REVENUE_LAW_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver), "official_text_status": STATUS,
        "status_counts": src["status_counts"],
        "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
        "council_resolution": src["council_resolution"],
        "council_resolution_date_hijri": src["council_resolution_date_hijri"],
        "consolidated_amended_law": True,
        "numbered_articles_max": src["numbered_articles_max"],
        "mukarrar_article_keys": src["mukarrar_article_keys"],
        "chapter_structure": src["chapter_structure"],
        "repealed_predecessor": src["repealed_predecessor"],
        "verification_methodology_note": src["verification_methodology_note"],
        "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
        "source_artifact": os.path.relpath(SRC, ROOT),
    }, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    json.dump({"layer_id": "sa-state-revenue-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (32 مادة)",
               "title_en": "State Revenue Law — Arabic LLM-ready layer (32 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 32], "text_status": STATUS,
               "consolidated_amended_law": True,
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("Wrote %d verified + %d LLM-ready State Revenue Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
