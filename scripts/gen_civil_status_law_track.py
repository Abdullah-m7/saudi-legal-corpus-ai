#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Civil Status Law track (نظام الأحوال المدنية,
Royal Decree M/7, 20/4/1407H / 1987G).

VERIFICATION TIER -- see sources/civil_status/law/official_source/
civil_status_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa, fetched via SEVEN independent Wayback
Machine snapshots spanning 13 Nov 2019 - 15 Feb 2026 (live BOE portal
unreachable this pass, connection reset via direct curl). All 96
"article_item" divs are present in every snapshot, in the same order, no
أبواب/فصول grouping. All 96 articles' main-body text is byte-identical across
all seven time-points; the only differences across snapshots are in the
per-article "تعديلات المادة" changelog popups themselves: Articles 2, 16, and
67 each gained an additional changelog popup (their M/198, 1445H amendment)
between the 21 Feb 2024 and 14 Jan 2025 snapshots -- consistent with (not
contradicting) that amendment's real-world date (22 Ramadan 1445H ~ early
Apr 2024G).

SECOND SOURCE: Council of Ministers Resolution No. 805 (16/9/1445H,
published Umm Al-Qura Gazette issue 5028, 22 Apr 2024G), independently
reported by qanoonsa.com (an independent Arabic legal aggregator, not a BOE
mirror) -- confirms the SAME three articles (2, 16, 67) were amended at the
same time, with substance matching BOE's own changelog text almost word for
word. THIRD SOURCE: nezams.com independently reproduces the founding decree
identity (M/7, 20/4/1407H; Council of Ministers Resolution 1, 11/1/1407H),
preamble content, 96-article total, and both M/25 (1422H) and M/198 (1445H)
amendment decrees.

AMENDMENT INCORPORATION -- a CLEAN case: every one of the 24 amended
articles' changelog popups supplies a complete, self-contained replacement
text (no partial "before/after" phrase substitution requiring positional
disambiguation anywhere in this track). Article 2's second popup (M/198) is
the sole exception to "full replacement" -- it explicitly ADDS a new
paragraph (ك) to the already-amended (M/25) text rather than replacing it.
Five articles (30, 33, 47, 50, 53) have a changelog popup with NO decree
number or date cited anywhere in BOE's own source (confirmed absent across
all seven snapshots; their "Viewer" attachment pages are also unarchived and
unreachable) -- flagged, not fabricated; their history[] decree field reads
"غير مذكور في مصدر هيئة الخبراء" and their status is tagged AMENDED_UNDATED.

96 records: 72 اصلية, 24 معدلة (Articles 2, 15, 16, 19, 20, 22, 25, 26, 30,
33, 34, 38, 40, 47, 50, 53, 67, 74, 76, 82, 83, 85, 87, 91), 0 ملغاة,
0 مضافة. Flat structure, no أبواب/فصول. No inline per-article titles in the
BOE source (spelled-ordinal "المادة ..." labels, e.g. "المادة الحادية
والتسعون") -- no title_ar field is used.

PREDECESSOR: Article 95 explicitly repeals TWO named predecessors -- نظام
دائرة النفوس (Population Department System, Supreme Order 8172, 15/7/1358H)
and نظام المواليد والوفيات (Births and Deaths System, Royal Decree 2,
11/1/1382H) -- neither exists anywhere in this corpus; recorded as
historical context only, not ingested (one-law-per-pass rule).

COMPANION INSTRUMENT NOT INGESTED: اللائحة التنفيذية لنظام الأحوال المدنية
(Ministerial Decision No. 81, 19/5/1426H per aggregated web search, itself
later amended) was identified but NOT ingested this pass (one-law-per-pass
precedent, as with nationality_law) -- see known_unresolved_discrepancies.

No legal text is altered beyond whitespace normalization, stripping BOE's own
"عدلت هذه المادة بموجب المرسوم ... لتكون بالنص الآتي/التالي:" changelog
provenance sentence (metadata about the amendment, not part of the article's
own text) and its wrapping quotation marks, and the clean amendment
incorporation described above. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_status", "law", "official_source",
                   "civil_status_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "civil_status", "law", "verified")
RECORDS = os.path.join(OUT_VER, "civil_status_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "civil_status_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "civil_status_arabic_legal_llm",
                        "civil_status_law_legal_llm_001_096.json")

LAW_ID = "sa-civil-status-law-m-7-1407"
LAW_AR = "نظام الأحوال المدنية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_AMENDED_UNDATED = "AMENDED_UNDATED"
KEY_RE = r"civil_status_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_NUMS_DATED = (2, 15, 16, 19, 20, 22, 25, 26, 34, 38, 40, 67, 74, 76, 82, 83, 85, 87, 91)
AMENDED_NUMS_UNDATED = (30, 33, 47, 50, 53)
AMENDED_KEYS = {"civil_status_art_%03d" % n for n in (AMENDED_NUMS_DATED + AMENDED_NUMS_UNDATED)}
UNDATED_KEYS = {"civil_status_art_%03d" % n for n in AMENDED_NUMS_UNDATED}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الأحوال المدنية الأحوال المدنية").split())


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


def _top_status(key):
    if key in UNDATED_KEYS:
        return STATUS_AMENDED_UNDATED
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


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
        top_status = _top_status(key)
        ver.append({"law_key": "civil_status", "law_component": "law",
                    "language": "ar",
                    "record_layer": "CIVIL_STATUS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this track rests on SEVEN "
                                              "independently-fetched BOE-via-Wayback-Machine "
                                              "archived snapshots spanning 13 Nov 2019 - 15 Feb "
                                              "2026 as the PRIMARY source (live BOE unreachable "
                                              "this pass, connection reset), cross-verified "
                                              "against Council of Ministers Resolution 805 (via "
                                              "qanoonsa.com) for the most recent amendment "
                                              "(Articles 2, 16, 67; M/198, 1445H) and against "
                                              "nezams.com's independent reproduction of the "
                                              "founding decree identity and earlier amendments. "
                                              "24 of 96 articles are معدلة; 5 of those (30, 33, "
                                              "47, 50, 53) have a changelog popup with NO decree "
                                              "number or date cited anywhere in BOE's own source "
                                              "(confirmed absent across all seven snapshots) -- "
                                              "see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's amended-"
                                              "article text or its decree attribution."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "civil-status-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "civil_status/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الأحوال المدنية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/7 (20/4/1407H) — "
                                                          "laws.boe.gov.sa via seven Wayback "
                                                          "Machine snapshots (2019-2026), "
                                                          "cross-verified against Council of "
                                                          "Ministers Resolution 805 (via "
                                                          "qanoonsa.com) and nezams.com; live "
                                                          "BOE unreachable this pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم م/7 وتاريخ 20/4/1407هـ — سبع لقطات أرشيفية من بوابة هيئة الخبراء عبر Wayback Machine (2019-2026)، مطابقة مع قرار مجلس الوزراء رقم 805 (عبر qanoonsa.com) ومع nezams.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "civil_status",
               "layer": "CIVIL_STATUS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-civil-status-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (96 مادة؛ 72 أصلية و24 معدلة)",
               "title_en": "Saudi Arabian Civil Status Law — Arabic LLM-ready layer (96 records: 72 original, 24 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 96], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Civil Status Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
