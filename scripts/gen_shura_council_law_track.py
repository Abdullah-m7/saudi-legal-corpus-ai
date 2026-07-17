#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Shura Council Law track (نظام مجلس الشورى, Royal Order A/91,
27/8/1412H).

MIXED VERIFICATION TIER — laws.boe.gov.sa's exact LawDetails page for this
law was located (GUID b5cf540a-e6ac-426a-b348-a9a700f163de) but was
unreachable by every method tried this research pass (direct fetch HTTP
503; a direct curl attempt returned a TLS/connection reset; r.jina.ai
returned repeated timeout/422; Wayback Machine blocked by sandbox egress
policy). Every article carries its own verification_tier:

  TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE — the 24
  unamended articles, and the pre-2013 amendment history of the 5 other
  amended articles: full text fetched directly (not AI-summarized) from
  THREE independent Arabic sources (ar.wikisource.org, nezams.com, and a
  King Saud University faculty-hosted PDF), all agreeing word-for-word.

  GOVERNMENT_PRIMARY_SPA_ANNOUNCEMENT_VERIFIED — Article 3's CURRENT
  (2013-amended) text specifically: backed by an actual Tier-1 GOVERNMENT
  PRIMARY SOURCE, the Saudi Press Agency's verbatim reproduction of Royal
  Order أ/44 (29/2/1434H, adding the 20% female-representation quota).

See sources/shura_council/law/official_source/
shura_council_law_official_source.json for the full methodology note and
documented unresolved discrepancies (most importantly: Article 3's very
first amendment, by Royal Order أ/78, was never located as a primary or
full-text secondary source — only cited by later sources — and is flagged,
not silently presented as confirmed).

Consolidated amended law: 24 اصلية / 6 معدلة / 0 ملغاة / 0 مضافة (30 total
articles). Article 3 was amended three times (60->120->150 members, then
the 2013 female-quota addition); articles 10, 21, 29 were each amended once
by أ/181 (1428H); articles 17, 23 were each amended once by أ/198 (1424H).
Articles are numbered by ordinal position 1..30, no مكرر, flat structure
with no chapter/section wrapper.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "shura_council", "law", "official_source",
                   "shura_council_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "shura_council", "law", "verified")
RECORDS = os.path.join(OUT_VER, "shura_council_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "shura_council_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "shura_council_arabic_legal_llm",
                        "shura_council_law_legal_llm_001_030.json")

LAW_ID = "sa-shura-council-law-a91-1412"
LAW_AR = "نظام مجلس الشورى"
KEY_RE = r"shura_council_art_(\d{3})$"
AMENDED_KEYS = {"shura_council_art_%03d" % n for n in (3, 10, 17, 21, 23, 29)}
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
        is_amended = ls == "معدلة"
        text = a["text"]
        tier = a["verification_tier"]
        ver.append({"law_key": "shura_council", "law_component": "law", "language": "ar",
                    "record_layer": "SHURA_COUNCIL_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": tier,
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1412h_text": a.get("original_1412h_text"),
                    "official_text_status": tier,
                    "governing_source_note": ("Arabic governs; this track uses a distinct, "
                                              "per-article verification tier because "
                                              "laws.boe.gov.sa was unreachable this research "
                                              "pass — see this article's own verification_tier "
                                              "field and the source artifact's "
                                              "verification_methodology_note for the full "
                                              "caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "shura-council-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "shura_council/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مجلس الشورى" % n],
                    "text_status": tier,
                    "source_trust": {"source_authority": ("Royal Order — triple independent "
                                                          "Arabic secondary sources (BOE page "
                                                          "unreachable this pass)"
                                                          if tier != "GOVERNMENT_PRIMARY_SPA_ANNOUNCEMENT_VERIFIED"
                                                          else "Royal Order — Saudi Press Agency "
                                                          "verbatim reproduction (government "
                                                          "primary source)"),
                                     "source_authority_ar": "أمر ملكي — مصادر عربية ثانوية ثلاثية مستقلة" if tier != "GOVERNMENT_PRIMARY_SPA_ANNOUNCEMENT_VERIFIED" else "أمر ملكي — إعادة نشر حرفية من وكالة الأنباء السعودية",
                                     "source_status": tier.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"],
                                     "verification_tier": tier},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "shura_council",
               "layer": "SHURA_COUNCIL_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "official_text_status": "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-shura-council-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ نص موحّد: 24 أصلية، 6 معدّلة)",
               "title_en": "Saudi Shura Council Law — Arabic LLM-ready layer (30 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30],
               "text_status": "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Shura Council Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
