#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Law of Service Providers for External Hajj
Pilgrims track (نظام مقدمي خدمة حجاج الخارج, Royal Decree M/111, 17/9/1440H --
the currently in-force law restructuring the historical Mutawwif/Agent/
Zamzami/Guide "أرباب الطوائف" trades into regulated joint-stock "شركات ضيافة
الحجاج" and licensed "شركات تقديم الخدمة" companies serving pilgrims arriving
from outside the Kingdom, administered by the Ministry of Hajj and Umrah).

BRAND-NEW BASE-LAW TRACK -- this statute was not previously in this corpus.
NOTE ON TITLE: the Royal Decree and every external source (nezams.com,
qanoonsa.com, uqn.gov.sa) call it "نظام مقدمي خدمة حجاج الخارج", the title used
throughout this track. The Law's OWN Article 1 §3 internally defines "النظام"
using a longer descriptive name, "نظام شركات أرباب الطوائف وشركات تقديم الخدمة
لحجاج الخارج" -- left untouched by the 2025 amendment despite the parallel
terminology ("أرباب الطوائف") being replaced everywhere else the amendment
touched. Both facts are disclosed in known_unresolved_discrepancies.

WHICH INSTRUMENT, AND HOW CONFIRMED -- confirmed via: (1) laws.boe.gov.sa
carries a dedicated lawId (962235c2-9fa8-4c1a-b835-aa6400dd851e) seen via
WebSearch, but unreachable this pass on every channel (WebFetch 503 x2, curl
reset x2, and web.archive.org snapshots that DO exist per the Wayback
Availability API but were blocked outright by this session's egress policy);
(2) nezams.com and tanseiqiah.sa (a Ministry-of-Hajj-and-Umrah-supervised
industry coordination council's own PDF hosting, distinct from a .gov.sa
portal) independently agree word-for-word on the full 23-article 1440H text;
(3) uqn.gov.sa (the official Umm Al-Qura Gazette, a genuine .gov.sa primary
source) was reached directly (HTTP 200 via curl) and carries the FULL verbatim
text of the 2025 amendment, cross-checked word-for-word (only Eastern vs.
Western digit rendering differs) against qanoonsa.com.

SUPERSESSION -- confirmed verbatim INSIDE the Royal Decree M/111's own
enacting clause (Second) and the accompanying Council of Ministers
Resolution's identical clause (NOT inside any of the Law's own 23 numbered
articles): repeals four prior instruments -- the General Mutawwif System
(1367H), the Mutawwif Agents and Java Sheikhs System (1365H), the Madinah
Guides Authority System (1356H), and the Disciplinary Rules for Mutawwifeen/
Agents/Guides/Zamazemah (Council of Ministers Resolution 79, 1400H -- this
fourth instrument was not part of the original task brief and was discovered
independently this pass).

VERIFICATION TIER -- TIER_3 overall (weakest meaningfully-sized portion
governs, per this corpus's own convention for per-article-varying confidence
tracks). The original 1440H text of the 9 UNAMENDED articles (7, 10, 12, 15,
16, 19, 20, 22, 23) rests on two independent secondary/quasi-official sources
(nezams.com, tanseiqiah.sa) with zero primary-source confirmation (BOE fully
unreachable, live and archived). The 2025 amendment governing the CURRENT text
of the other 14 articles (1,2,3,4,5,6,8,9,11,13,14,17,18,21) plus the newly
added Article 19 bis rests on a genuine primary government source (uqn.gov.sa,
directly fetched) cross-verified against a secondary aggregator -- a stronger
TIER_2-grade confirmation for that portion specifically. See the source
artifact's verification_methodology_note for the full, heavily-disclosed
account, including an internal 454-vs-545 Council of Ministers resolution
number conflict inside nezams.com itself, a one-day gazette-date discrepancy,
and a corrected 21-vs-14 amended-article-count claim (the task brief's "21
articles" figure could not be confirmed against any directly-fetched verbatim
text; the programmatically-counted figure from the verbatim amendment text is
14 amended + 1 added = 15 total change-events).

24 records (23 original numbered articles + 1 "مكرر" addition); 9 اصلية, 14
معدلة (Articles 1,2,3,4,5,6,8,9,11,13,14,17,18,21), 0 ملغاة, 1 مضافة (Article
19 bis). No chapter/فصل or باب structure (confirmed via a full programmatic
scan of the source page finding zero occurrences of either word; the
combined-with-implementing-regulation tanseiqiah.sa PDF DOES have باب/فصل
headings, but only inside the separately-numbered Implementing Regulation
section, which is excluded entirely from this track per the task's explicit
scope).

Implementing Regulation (Minister of Hajj and Umrah Decision No. 410105143,
5/1/1441H, confirmed via the tanseiqiah.sa combined PDF) exists and is enacted
(not a draft) but was NOT built as a separate track this pass -- explicitly
out of scope per the task brief, which also directed exclusion of any draft
amendment to it under public consultation on istitlaa.ncc.gov.sa.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "hajj_umrah_external_pilgrims_law", "law", "official_source",
                   "hajj_umrah_external_pilgrims_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "hajj_umrah_external_pilgrims_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "hajj_umrah_external_pilgrims_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "hajj_umrah_external_pilgrims_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "hajj_umrah_external_pilgrims_law_arabic_legal_llm",
                        "hajj_umrah_external_pilgrims_law_legal_llm_001_024.json")

LAW_ID = "sa-hajj-umrah-external-pilgrims-law-m111-1440"
LAW_AR = "نظام مقدمي خدمة حجاج الخارج"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"hajj_umrah_external_pilgrims_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {
    "hajj_umrah_external_pilgrims_law_art_001",
    "hajj_umrah_external_pilgrims_law_art_002",
    "hajj_umrah_external_pilgrims_law_art_003",
    "hajj_umrah_external_pilgrims_law_art_004",
    "hajj_umrah_external_pilgrims_law_art_005",
    "hajj_umrah_external_pilgrims_law_art_006",
    "hajj_umrah_external_pilgrims_law_art_008",
    "hajj_umrah_external_pilgrims_law_art_009",
    "hajj_umrah_external_pilgrims_law_art_011",
    "hajj_umrah_external_pilgrims_law_art_013",
    "hajj_umrah_external_pilgrims_law_art_014",
    "hajj_umrah_external_pilgrims_law_art_017",
    "hajj_umrah_external_pilgrims_law_art_018",
    "hajj_umrah_external_pilgrims_law_art_021",
}
ADDED_KEYS = {"hajj_umrah_external_pilgrims_law_art_019_mukarrar"}
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير").split())


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
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
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
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "hajj_umrah_external_pilgrims_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "HAJJ_UMRAH_EXTERNAL_PILGRIMS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this is the currently in-force Law "
                                              "of Service Providers for External Hajj Pilgrims "
                                              "(Royal Decree M/111, 17/9/1440H), as amended by "
                                              "Royal Decree M/89, 12/5/1447H (3 Nov 2025G). "
                                              "Brand-new base-law track built from scratch this "
                                              "pass. The Royal Decree's own enacting clause "
                                              "(Second) -- not any article inside the Law's 23 "
                                              "numbered articles -- repeals four prior instruments, "
                                              "including one (CoM Resolution 79, 1400H) discovered "
                                              "independently this pass beyond the original task "
                                              "brief. laws.boe.gov.sa was checked first per standard "
                                              "methodology but was unreachable on every channel this "
                                              "pass (live 503/reset; archived snapshots exist per "
                                              "Wayback's own Availability API but web.archive.org "
                                              "was blocked outright by this session's egress "
                                              "policy). The original 1440H text of the 9 unamended "
                                              "articles rests on two independent secondary/"
                                              "quasi-official sources (nezams.com, "
                                              "tanseiqiah.sa) with zero primary confirmation; the "
                                              "2025 amendment governing 14 articles plus the new "
                                              "Article 19 bis rests on the official Umm Al-Qura "
                                              "Gazette (uqn.gov.sa, reached directly) cross-checked "
                                              "against qanoonsa.com. Overall TIER_3 (weakest portion "
                                              "governs per this corpus's convention). See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably the "
                                              "corrected 21-vs-14 amended-article count and the "
                                              "internal 454-vs-545 CoM resolution number conflict."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "hajj-umrah-external-pilgrims-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "hajj_umrah_external_pilgrims_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام مقدمي خدمة حجاج الخارج" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/111), 17/9/1440H "
                                                          "(Council of Ministers Resolution 545, "
                                                          "16/9/1440H; Shura Council Resolution "
                                                          "48/13, 2/5/1440H), as amended by Royal "
                                                          "Decree No. (M/89), 12/5/1447H (3 Nov "
                                                          "2025G; CoM Resolution 322, 6/5/1447H) -- "
                                                          "the currently in-force Law of Service "
                                                          "Providers for External Hajj Pilgrims. "
                                                          "Original 1440H text from nezams.com and "
                                                          "tanseiqiah.sa (laws.boe.gov.sa unreachable "
                                                          "live and archived this pass); the 2025 "
                                                          "amendment's governing text from the "
                                                          "official Umm Al-Qura Gazette (uqn.gov.sa, "
                                                          "reached directly), cross-checked against "
                                                          "qanoonsa.com. Overall TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/111) وتاريخ 17/9/1440هـ (قرار مجلس الوزراء رقم 545 وتاريخ 16/9/1440هـ؛ قرار مجلس الشورى رقم 48/13 وتاريخ 2/5/1440هـ)، كما عُدِّل بالمرسوم الملكي رقم (م/89) وتاريخ 12/5/1447هـ (3 نوفمبر 2025م؛ قرار مجلس الوزراء رقم 322 وتاريخ 6/5/1447هـ) — نظام مقدمي خدمة حجاج الخارج النافذ حاليا. النص الأصلي لعام 1440هـ من nezams.com وtanseiqiah.sa (BOE غير قابل للوصول حيا وأرشيفيا هذه الجولة)؛ نص التعديل النافذ من جريدة أم القرى الرسمية (uqn.gov.sa، مجلوبة مباشرة)، مدقَّق بـqanoonsa.com. المستوى الكلي TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "hajj_umrah_external_pilgrims_law",
               "layer": "HAJJ_UMRAH_EXTERNAL_PILGRIMS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-hajj-umrah-external-pilgrims-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (24 سجلا؛ 9 أصلية، 14 معدلة، 1 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Saudi Arabian Law of Service Providers for External Hajj "
                            "Pilgrims (Royal Decree M/111, 17/9/1440H, as amended by Royal Decree "
                            "M/89, 12/5/1447H/3 Nov 2025G) — Arabic LLM-ready layer (24 records: 9 "
                            "original, 14 amended [Articles 1,2,3,4,5,6,8,9,11,13,14,17,18,21], 1 "
                            "added [Article 19 bis], 0 repealed; no chapter structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 23], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Hajj/Umrah External Pilgrims Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
