#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Premium Residency Law track (نظام الإقامة المميزة, Royal Decree
No. M/106 dated 10/9/1440H / 15 May 2019G) -- a distinct, much newer
investor/talent long-term residency instrument, entirely separate from this
corpus's already-ingested residency_law track (نظام الإقامة, the 1371H
Iqama/Kafala law). See that track's own official_source.json for the explicit
note that this Premium Residency Law (and its لائحة تنفيذية) were identified
as companion instruments "explicitly out of scope" for that earlier pass.

VERIFICATION TIER -- see sources/premium_residency/law/official_source/
premium_residency_law_official_source.json's verification_methodology_note for
the full account. Summary:

laws.boe.gov.sa's LIVE portal was unreachable this pass (connection reset via
direct curl and via the r.jina.ai reader-proxy fallback, both timing out) --
consistent with this corpus's established pattern for this portal. Relied
instead on SIX independent Wayback Machine snapshots of BOE's own dedicated
lawId page (5e9762df-2b15-4e66-8cdc-aa5200f62042) spanning SIX YEARS (22 Nov
2019 through 16 Nov 2025) -- internally consistent with the real amendment
timeline (the 2019 snapshot shows zero amendments; the Feb 2023 snapshot shows
exactly the three amendments enacted by that date and none of the later ones;
the Nov 2025 snapshot shows all five). This multi-snapshot temporal
cross-check is stronger than this corpus's usual single-snapshot practice.

CRITICAL CROSS-VERIFICATION (raises this track to TIER_1): an independent
OFFICIAL government source -- misa.gov.sa (Ministry of Investment), hosting a
PDF titled with "1445H" in its filename -- was directly downloaded (200 OK)
and its extracted text (via pdftotext) already presents the CURRENT,
CONSOLIDATED, POST-AMENDMENT text as its primary body (unlike BOE's own
two-layer original-text-plus-annotations rendering). This MISA text agrees
WORD-FOR-WORD with the text reconstructed here from BOE's own quoted
amendment instructions, at every point checked, with exactly ONE minor
one-word discrepancy (Article 2(e)'s "صك حق انتفاع" vs MISA's "صك انتفاع" --
BOE's fuller, temporally-stable wording is treated as canonical; disclosed,
not silently resolved). Two independent official government sources agreeing
= TIER_1_PRIMARY_MULTI_SOURCE per this corpus's taxonomy.

14 articles, no أبواب/فصول (a genuinely flat structure per BOE's own
rendering; chapter_structure below is an informal thematic grouping for
indexing only). Per BOE's OWN per-article "مادة معدلة"/"مادة ملغية" tagging:
8 معدلة (Articles 1, 2, 3, 4, 5, 6, 10, 11), 1 ملغاة (Article 8, text
preserved not deleted), 5 اصلية (Articles 7, 9, 12, 13, 14 -- though Articles
9 and 13's wording nonetheless reflects a downstream global term-substitution
from Article 1's own amendment; disclosed, not silently normalized), 0
مضافة (no new standalone مكرر articles; the one new paragraph inserted by
M/71 lives inside existing Article 11). Repealed sub-paragraphs/paragraphs
within otherwise-still-amended articles are preserved as an explicit
"(ألغيت)" placeholder (matching the exact convention used by the MISA
official consolidated text), not silently deleted or renumbered.

REPEAL/PREDECESSOR: Article 14 (entry into force) names no repealed
predecessor law at all -- a confirmed negative finding, not a research gap.
This is a wholly new residency category with no prior instrument to repeal,
genuinely distinct in subject matter and target population from this
corpus's already-ingested residency_law (1371H Iqama/Kafala law) -- the two
coexist, mirroring this corpus's social_insurance_law / social_insurance_
legacy_law naming-distinction precedent, not a supersession relationship.

COMPANION INSTRUMENTS IDENTIFIED, NOT INGESTED THIS PASS: (1) اللائحة
التنفيذية لنظام الإقامة المميزة (the Law's own implementing regulation,
originally issued by the Center itself as its Decision No. 4-1440 dated
20/9/1440H, amended by the Center's Board Decision No. 7-5-1444 dated
29/12/1444H) -- confirmed to exist via multiple agreeing secondary sources,
but NOT separately indexed on BOE under its own lawId, and the only source
located with article-level content (aunklaw.com) provides a paraphrased
per-article SUMMARY, not verbatim text -- not ingested, per this corpus's
binding constraint against treating a paraphrase as verified verbatim text;
(2) تنظيم مركز الإقامة المميزة (the Center's own internal organizational
bylaws -- board/CEO/budget structure, CoM Resolution 555, 1443H, BOE lawId
bc27d6e4-560a-4778-9364-aeac00ca7e3b) -- a genuinely distinct administrative
instrument, not the substantive residency regulation, out of scope.

No legal wording is altered beyond whitespace normalization. Arabic governs;
no translation/paraphrase/interpretation performed on the Arabic text. Read-
only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "premium_residency", "law", "official_source",
                   "premium_residency_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "premium_residency", "law", "verified")
RECORDS = os.path.join(OUT_VER, "premium_residency_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "premium_residency_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "premium_residency_arabic_legal_llm",
                        "premium_residency_law_legal_llm_001_014.json")

LAW_ID = "sa-premium-residency-law-royal-decree-m-106-1440"
LAW_AR = "نظام الإقامة المميزة"
TOP_STATUS = ("PREMIUM_RESIDENCY_LAW_BOE_LIVE_UNREACHABLE_WAYBACK_MULTI_SNAPSHOT_2019_2025_"
              "X_MISA_OFFICIAL_CONSOLIDATED_PDF_CROSS_VERIFIED")
KEY_RE = r"premium_residency_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"premium_residency_art_%03d" % n for n in (1, 2, 3, 4, 5, 6, 10, 11)}
REPEALED_KEYS = {"premium_residency_art_008"}
ADDED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الإقامة المميزة حامل غير السعودي "
            "الفقرة هذه ألغيت").split())


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
        ver.append({"law_key": "premium_residency", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PREMIUM_RESIDENCY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; laws.boe.gov.sa's live portal was "
                                              "unreachable this pass -- this track rests on six "
                                              "independent Wayback Machine snapshots of BOE's own "
                                              "dedicated lawId page (2019-2025), cross-verified "
                                              "word-for-word against an independent official "
                                              "government source (misa.gov.sa's own hosted "
                                              "consolidated-text PDF), qualifying as "
                                              "TIER_1_PRIMARY_MULTI_SOURCE. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track for any "
                                              "single article's definitively-current wording."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "premium-residency-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "premium_residency/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الإقامة المميزة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. M/106 (10/9/1440H) — "
                                                          "laws.boe.gov.sa live portal unreachable "
                                                          "this pass; sourced from six Wayback "
                                                          "Machine snapshots of BOE's own lawId "
                                                          "page (2019-2025), cross-verified "
                                                          "word-for-word against misa.gov.sa's "
                                                          "(Ministry of Investment) own hosted "
                                                          "consolidated-text PDF"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/106) وتاريخ 10/9/1440هـ — بوابة هيئة الخبراء الحية غير متاحة هذه الجولة؛ اعتُمد على ست لقطات أرشيف Wayback لصفحة الهيئة نفسها (2019-2025)، مطابقة حرفياً لنسخة وزارة الاستثمار الرسمية الموحَّدة (misa.gov.sa)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "premium_residency",
               "layer": "PREMIUM_RESIDENCY_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-premium-residency-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (14 مادة؛ 5 أصلية و8 معدلة ومادة واحدة ملغاة)",
               "title_en": ("Premium Residency Law — Arabic LLM-ready layer (14 ingested "
                            "records: 5 original, 8 amended, 1 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 14], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Premium Residency Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
