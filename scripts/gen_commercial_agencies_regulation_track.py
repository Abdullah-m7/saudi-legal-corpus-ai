#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Commercial Agencies Law track
(اللائحة التنفيذية لنظام الوكالات التجارية).

Source: the official Regulations portal of the Ministry of Commerce (mc.gov.sa),
lawId 6921ddd3-b992-4940-8c23-a84000b1a888, fetched LIVE (single fetch, not
cross-snapshot) via the r.jina.ai reader-proxy after direct curl/WebFetch and a
Wayback Machine snapshot of the same URL both hit CAPTCHA bot-detection / TLS
failures. See sources/commercial_agencies_regulation/law/official_source/
commercial_agencies_regulation_official_source.json for the full provenance,
verification_methodology_note and known_unresolved_discrepancies.

Ministerial Decision (Minister of Commerce) No. 1897, dated 24/5/1401H
(30/3/1981), confirmed independently via the mc.gov.sa portal's own attachment
title ("قرار رقم (1897)") plus four independent secondary sources (nezams.com,
qistas.com, thelawsa.com, corporate-lawyer.org). IN FORCE (ساري).

Structure: 49 articles total -- 22 in the main body (5 sections: الأحكام العامة
1-5, أحكام القيد 6-15, شطب القيد 16-18, المخالفات والعقوبات 19-21, أحكام
انتقالية 22) plus a separately-numbered 27-article annex ("ملحق: أحكام تقديم
الصيانة وتوفير قطع الغيار وضمان جودة الصنع"). 21 اصلية / 1 معدلة (body art 3,
amended by Ministerial Decision No. 817 dated 24/8/1435H, current text +
original in amendment_history) / 27 مضافة (the whole annex, attributed by
strong inference -- not a portal-native label -- to the same 817/1435H decision;
corroborated in detail against an independent June-2014 news article,
almuraba.net) / 0 ملغاة. TIER_2. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_agencies_regulation", "law", "official_source",
                   "commercial_agencies_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "commercial_agencies_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "commercial_agencies_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "commercial_agencies_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "commercial_agencies_regulation_arabic_legal_llm",
                        "commercial_agencies_regulation_legal_llm_001_049.json")

LAW_ID = "sa-commercial-agencies-regulation-mc1897-1401"
LAW_AR = "اللائحة التنفيذية لنظام الوكالات التجارية"
STATUS = "MATCHES_MC_GOV_SA_LIVE_PORTAL"
BODY_KEY_RE = r"commercial_agencies_regulation_art_(\d{3})$"
ANNEX_KEY_RE = r"commercial_agencies_regulation_annex_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الوكيل الموزع").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(BODY_KEY_RE, key)
    if m:
        return (0, int(m.group(1)))
    m = re.match(ANNEX_KEY_RE, key)
    return (1, int(m.group(1)))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for i, key in enumerate(keys, start=1):
        a = arts[key]
        is_annex = a["part"] == "annex"
        n = a["native_article_number"]
        suffix = "-annex" if is_annex else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        label = a["number_label_ar"]
        if is_annex and a.get("article_subtitle_ar"):
            label_full = "%s: %s" % (label, a["article_subtitle_ar"])
        else:
            label_full = label
        ver.append({"law_key": "commercial_agencies_regulation", "law_component": "regulation", "language": "ar",
                    "record_layer": "COMMERCIAL_AGENCIES_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": i, "part": a["part"], "native_article_number": n,
                    "is_annex": is_annex, "article_key": key,
                    "number_label_ar": label_full,
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": hist,
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official Ministry of Commerce (mc.gov.sa) live "
                                              "portal text fetched via reader-proxy (single fetch, TIER_2 -- see "
                                              "source artifact for full methodology); amendment status flagged."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": i,
                    "part": a["part"], "native_article_number": n, "is_annex": is_annex,
                    "article_key": key, "article_title_ar": label_full,
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "commercial-agencies-regulation-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, label_full,
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label_full),
                    "article_path": "commercial_agencies_regulation/law/articles/%s%03d%s" % (
                        "annex/" if is_annex else "", n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام الوكالات التجارية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Commerce (Saudi Arabia) — official Regulations portal",
                                     "source_authority_ar": "وزارة التجارة — البوابة الرسمية للأنظمة واللوائح",
                                     "source_status": "mc_gov_sa_live_portal_single_fetch_tier2",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "commercial_agencies_regulation",
               "layer": "COMMERCIAL_AGENCIES_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "base_law_decree": src["base_law_decree"],
               "base_law_decree_date_hijri": src["base_law_decree_date_hijri"],
               "base_law_key_in_repo": src["base_law_key_in_repo"],
               "consolidated_amended_law": True,
               "verification_tier": src["verification_tier"],
               "primary_source_url": src["primary_source_url"],
               "primary_source_access_method": src["primary_source_access_method"],
               "corpus_text_sha256": src["provenance"]["corpus_text_sha256"],
               "known_unresolved_discrepancies_count": len(src.get("known_unresolved_discrepancies", [])),
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-commercial-agencies-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (49 مادة؛ 22 في المتن + 27 في الملحق؛ 21 أصلية، 1 معدّلة، 27 مضافة)",
               "title_en": "Saudi Implementing Regulation of the Commercial Agencies Law — Arabic LLM-ready layer (49 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 49], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Commercial Agencies Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
