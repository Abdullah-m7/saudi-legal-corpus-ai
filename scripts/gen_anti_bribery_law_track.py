#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Anti-Bribery Law track (نظام مكافحة الرشوة, Royal Decree M/36,
29/12/1412H).

DISTINCT, LOWER-CONFIDENCE VERIFICATION TIER — read this before trusting this
track at the same level as the rest of this corpus. This law is not a
MOJ-issued instrument (not on the MOJ legal portal) and laws.boe.gov.sa /
web.archive.org were both confirmed unreachable from the build environment
across three separate research passes this session (BOE fails at the TLS
handshake stage on every path tried; archive.org is blocked by the sandbox's
network egress policy outright). So neither of this corpus's two established
verification methods (MOJ portal DB x official PDF, or BOE-portal-via-Wayback
byte-identical cross-snapshot) was available. Two ad hoc tiers were used
instead, and every article carries its own tier tag in the official source:

  SINGLE_PRIMARY_SOURCE_TOPICAL_CORROBORATION — the 16 articles unchanged
  since 1412H: full verbatim text from ONE official source (a scanned
  Bureau-of-Experts-letterhead booklet at faculty.ksu.edu.sa, committed at
  inputs/anti_bribery_official_pdfs/anti_bribery_law_1412h_original_ksu.pdf),
  topically (not verbatim) corroborated by a second, independently-hosted
  summary table. This is weaker than this corpus's usual article-by-article
  byte/text-similarity cross-verification.

  SECONDARY_SOURCE_CONVERGENCE_UNVERIFIED_PRIMARY — the 7 amended articles
  (5, 8, 9, 14, 15, 17, 21) and 2 newly-added مكرر articles: current text
  rests entirely on convergence between two Saudi legal-publishing sites
  (nezams.com, manielaw-sa.com — committed at inputs/anti_bribery_official_pdfs/
  anti_bribery_law_consolidated_manielaw.pdf) that are themselves suspected
  to share a common upstream source, NOT confirmed against any primary
  official gazette scan. This is the WEAKEST verification tier used anywhere
  in this corpus. The repository owner explicitly reviewed and approved
  ingestion under this distinct, clearly-flagged tier after two dedicated
  research passes confirmed the primary channels were unreachable.

See sources/anti_bribery/law/official_source/anti_bribery_law_official_source.json
for the full methodology note and documented unresolved discrepancies
(article 17's exact current wording, article 14's 2024-rename inference, and
a punctuation artifact in article 9 مكرر (1)).

Consolidated amended law: 16 اصلية / 7 معدلة / 2 مضافة / 0 ملغاة (25 total
provisions). Articles are numbered by ordinal position 1..23 plus two
مكرر articles inserted between 9 and 10 (9 مكرر (1), 9 مكرر (2) — confirmed
non-renumbering of articles 10-23), flat structure with no chapter/section
wrapper (section_ar empty for every article).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_bribery", "law", "official_source",
                   "anti_bribery_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_bribery", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_bribery_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_bribery_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_bribery_arabic_legal_llm",
                        "anti_bribery_law_legal_llm_001_023.json")

LAW_ID = "sa-anti-bribery-law-m36-1412"
LAW_AR = "نظام مكافحة الرشوة"
KEY_RE = r"anti_bribery_art_(\d{3})(_mukarrar_(\d))?$"
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
    return (int(m.group(1)), int(m.group(3)) if m.group(3) else 0)


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
        n, is_muk = int(m.group(1)), bool(m.group(3))
        suffix = ("-mukarrar-%s" % m.group(3)) if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        tier = a["verification_tier"]
        ver.append({"law_key": "anti_bribery", "law_component": "law", "language": "ar",
                    "record_layer": "ANTI_BRIBERY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": tier,
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": tier,
                    "governing_source_note": ("Arabic governs; this track uses a distinct, "
                                              "LOWER-CONFIDENCE verification tier than the rest of "
                                              "this corpus (not MOJ-portal-verified, not "
                                              "BOE-Wayback-byte-identical-verified) because the "
                                              "primary channels were confirmed unreachable from the "
                                              "build environment — see this article's own "
                                              "verification_tier field and the source artifact's "
                                              "verification_methodology_note for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "anti-bribery-law-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_bribery/law/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة الرشوة" % n],
                    "text_status": tier,
                    "source_trust": {"source_authority": ("Royal Decree — secondary-source "
                                                          "convergence (see verification_tier); "
                                                          "NOT MOJ-portal-verified"),
                                     "source_authority_ar": "مرسوم ملكي — تحقق من مصادر ثانوية متقاربة (انظر verification_tier)",
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
    json.dump({"law_key": "anti_bribery", "layer": "ANTI_BRIBERY_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "official_text_status": "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-bribery-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة؛ نص موحّد: 16 أصلية، 7 معدّلة، 2 مضافة؛ درجة توثيق أقل من المعتاد)",
               "title_en": "Saudi Anti-Bribery Law — Arabic LLM-ready layer (25 records, consolidated, lower-confidence verification tier)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 23], "text_status": "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Bribery Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
