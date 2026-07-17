#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Social Insurance Law (New System) track (نظام التأمينات
الاجتماعية — الجديد، المرسوم الملكي رقم م/273، 26/12/1445هـ).

SCOPE NOTE — this is the NEW social-insurance law only, in force since
1 Jul 2025 for new labor-market entrants with no prior contribution history
under the old Social Insurance Law (Royal Decree M/33, 3/9/1421H) or the
Civil Pension Law (Royal Decree M/41, 29/7/1393H). The OLD M/33 law governs
everyone already enrolled before that date and is a SEPARATE track, out of
scope here. The two laws share the identical Arabic title "نظام التأمينات
الاجتماعية" despite being differently-numbered/dated instruments covering
different populations — a genuine naming collision, documented in
known_unresolved_discrepancies (see the official_source JSON), analogous to
the Franchise Law/Anti-Concealment Law M/22 collision already flagged
elsewhere in this corpus.

VERIFICATION TIER — full article text (all 63 articles) was extracted
directly from a Wayback Machine archive snapshot (2025-12-12) of the
official BOE portal (laws.boe.gov.sa), fetched via curl using the "if_"
raw-content modifier with a desktop User-Agent header, and parsed from its
structured `<div class="article_item">` / `<h3 class="center">` (باب/فصل
heading) markup. Full-text spot-checked (5 of 63 articles: 1, 16, 30, 44,
63) word-for-word — verbatim match modulo optional tashkil — against a
direct fetch of nezams.com, whose own article index also independently
confirmed the complete, gap-free 1-63 article sequence and all باب/فصل
attachment points. See sources/social_insurance/law/official_source/
social_insurance_law_official_source.json's verification_methodology_note
for the full methodology and known_unresolved_discrepancies for all
documented gaps/anomalies, including: the dual-law title collision; the
Article 44 statutory-vs-administrative unemployment-rate figures (2%
statutory ceiling vs 1.5% administrative starting rate per Cabinet
Resolution 1022); the Article 16 qualifying-period gap-fill (Resolution
1022 fixes 180 months where the law itself defers to a future Cabinet
decision); a BOE-vs-nezams wording variance at Article 21(1)(a); and the
unextracted-but-referenced SANED (M/18) and Civil Pension (M/41) laws.

63 records, all article-numbered (no مكرر articles), all اصلية (no
amendments found or expected — the law is under 2 years old): 0 معدلة /
0 ملغاة / 0 مضافة. 6 أبواب, with الباب الثالث split into 2 نested فصول
(الفصل الأول تعويضات الأخطار المهنية 30-40، الفصل الثاني تعويض الأمومة
41-42؛ المادتان 28-29 تقعان مباشرة تحت الباب الثالث قبل انقسامه إلى فصلين).

The Royal Decree's own transitional provisions (بند أولاً - حادي عشر) are
NOT numbered articles of the law and are therefore not part of `articles`;
they are preserved verbatim in the source JSON's
`decree_transitional_provisions_ar` field and summarized in
`verification_methodology_note`.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance", "law", "official_source",
                   "social_insurance_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "social_insurance", "law", "verified")
RECORDS = os.path.join(OUT_VER, "social_insurance_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "social_insurance_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "social_insurance_arabic_legal_llm",
                        "social_insurance_law_legal_llm_001_063.json")

LAW_ID = "sa-social-insurance-law-new-m273-1445"
LAW_AR = "نظام التأمينات الاجتماعية (الجديد)"
STATUS = "BOE_WAYBACK_PRIMARY_X_NEZAMS_SPOTCHECK_X_QANOONSA_STRUCTURE_VERIFIED"
KEY_RE = r"social_insurance_art_(\d{3})(_mukarrar)?$"
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
        suffix = key.replace("social_insurance_art_", "")
        ver.append({"law_key": "social_insurance", "law_component": "law", "language": "ar",
                    "record_layer": "SOCIAL_INSURANCE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this is the NEW Social Insurance Law "
                                              "(Royal Decree M/273, 26/12/1445H), distinct from the OLD "
                                              "Social Insurance Law (M/33, 3/9/1421H) which shares the "
                                              "identical Arabic title but is a separate track. Full text "
                                              "extracted from a Wayback Machine BOE archive snapshot "
                                              "(2025-12-12), spot-checked (5 of 63 articles) against "
                                              "nezams.com — see verification_methodology_note in the "
                                              "source artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "social-insurance-law-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "social_insurance/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام التأمينات الاجتماعية الجديد" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("BOE (laws.boe.gov.sa) via Wayback Machine "
                                                          "archive snapshot 2025-12-12, direct primary "
                                                          "fetch; spot-checked (5 of 63 articles) against "
                                                          "nezams.com (secondary Arabic legal-reference "
                                                          "site, fetched directly)"),
                                     "source_authority_ar": "بوابة هيئة الخبراء BOE عبر أرشيف Wayback Machine (لقطة 2025-12-12، جلب مباشر أساسي)، مع مطابقة نقطية حرفية (5 من 63 مادة) مقابل nezams.com",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "social_insurance",
               "layer": "SOCIAL_INSURANCE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "decree_transitional_provisions_ar": src["decree_transitional_provisions_ar"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-social-insurance-law-new-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (63 سجلاً، كلها أصلية)",
               "title_en": "Saudi Social Insurance Law (New System) — Arabic LLM-ready layer "
                           "(63 records, all اصلية)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 63], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Social Insurance Law (New System) records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
