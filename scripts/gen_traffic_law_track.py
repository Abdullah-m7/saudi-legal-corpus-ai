#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Traffic Law track (نظام المرور, Royal Decree M/85, 26/10/1428H).

DISTINCT VERIFICATION TIER — this track required TWO independent research
passes because of a genuine, unresolved discrepancy between the official
BOE portal (laws.boe.gov.sa) and the secondary reference site nezams.com
for roughly a third of this law's articles. BOE's live portal was
confirmed (across both passes) to be genuinely stale for this law — not a
proxy/rendering artifact — via four independently-verified data points
(Article 71's repeal, Article 74's 2025 rewrite, Article 2's added
definition #44, and the Table 2 item-16 wording). nezams.com's "current
text" is therefore used as the governing text for amended articles where
it differs from BOE's stale text, but this is PATTERN-BASED confidence,
not per-article gazette proof: each article carries a per-article
`verification_tier` field (PRIMARY_INDEPENDENTLY_CONFIRMED vs
SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE) carrying the real granularity that
the overall STATUS constant deliberately does not smooth over.

See sources/traffic/law/official_source/traffic_law_official_source.json
for the full methodology note and all documented unresolved discrepancies.

86 records (85 numbered + 1 مكرر): 52 اصلية / 32 معدلة / 1 ملغاة / 1 مضافة.
8 chapters (أبواب). Article 71 repealed (text preserved per corpus policy
of never deleting repealed articles); Article 50 مكرر added by Royal
Decree M/115 (5/12/1439H).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "traffic", "law", "official_source",
                   "traffic_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "traffic", "law", "verified")
RECORDS = os.path.join(OUT_VER, "traffic_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "traffic_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "traffic_arabic_legal_llm",
                        "traffic_law_legal_llm_001_086.json")

LAW_ID = "sa-traffic-law-m85-1428"
LAW_AR = "نظام المرور"
STATUS = "BOE_PROXY_X_NEZAMS_PATTERN_VERIFIED_MIXED_CONFIDENCE"
KEY_RE = r"traffic_art_(\d{3})(_mukarrar)?$"
ALLOWED_TIERS = {"PRIMARY_INDEPENDENTLY_CONFIRMED", "SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE"}
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
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    mk = 1 if m.group(2) else 0
    return (n, mk)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(m.group(2))
        ls = a.get("legal_status_ar")
        text = a["text"]
        tier = a.get("verification_tier")
        original = a.get("original_1428h_text")
        suffix = key.replace("traffic_art_", "")
        ver.append({"law_key": "traffic", "law_component": "law", "language": "ar",
                    "record_layer": "TRAFFIC_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "original_1428h_text": original,
                    "verification_status": a["status"],
                    "verification_tier": tier,
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a distinct, "
                                              "MIXED-CONFIDENCE verification tier — nezams.com's "
                                              "current text is preferred over BOE's confirmed-stale "
                                              "portal text for amended articles, but only "
                                              "%s of this article's status is per-article "
                                              "gazette/press-confirmed rather than pattern-based — "
                                              "see verification_tier and "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat." % tier),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "verification_tier": tier,
                    "record_id": "traffic-law-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "original_1428h_text": original,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "traffic/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام المرور" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/85 — BOE portal "
                                                          "(confirmed stale for several "
                                                          "amended-era articles) cross-checked "
                                                          "against nezams.com, per-article "
                                                          "verification_tier applied"),
                                     "source_authority_ar": "مرسوم ملكي رقم (م/85) — بوابة هيئة الخبراء (مؤكدة التقادم لعدد من المواد المعدلة) مقارنة بموقع نزامز.كوم، مع تصنيف ثقة لكل مادة على حدة",
                                     "source_status": STATUS.lower(),
                                     "verification_tier": tier,
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "traffic",
               "layer": "TRAFFIC_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-traffic-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (86 سجلاً؛ نص موحّد: 52 أصلية، 32 معدلة، 1 ملغاة، 1 مضافة)",
               "title_en": "Saudi Traffic Law — Arabic LLM-ready layer (86 records, consolidated, mixed-confidence)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 85], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Traffic Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
