#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulations (family) track for the OLD/LEGACY
Social Insurance Law (اللوائح التنفيذية لنظام التأمينات الاجتماعية القديم،
م/33، 1421هـ).

SCOPE NOTE -- this track is the historical companion regulation FAMILY for
the OLD social-insurance law (sources/social_insurance_legacy/), and is
entirely distinct from the NEW Social Insurance Law's own 1445H implementing
regulation (a separate track, social_insurance_regulation, built in
parallel by a different pass over this corpus). Do not confuse the two.

TRUE STRUCTURE -- this is NOT a single consolidated regulation. It is a
genuine family of FOUR distinct لوائح issued together under ONE umbrella
ministerial decision:

    Decision of the Minister of Labor and Social Affairs No. (128/تأمينات),
    25/10/1421H, based on GOSI Board of Directors Resolution No. (735) of
    the same date, which approved and issued (per the decision's own
    Article 1):
        1. لائحة التسجيل والاشتراكات           (Registration & Contributions)
        2. لائحة تعويضات فرع المعاشات           (Pensions Branch Benefits)
        3. لائحة تعويضات فرع الأخطار المهنية    (Occupational Hazards Branch Benefits)
        4. لائحة اللجان الطبية                  (Medical Committees)

170 article-records total: the umbrella decision itself (6 articles) +
Registration & Contributions (65 articles, 9 أبواب) + Pensions Branch
Benefits (42 articles, 7 فصول) + Occupational Hazards Branch Benefits (40
articles, 7 فصول) + Medical Committees (17 articles, 5 فصول). 165 اصلية / 5
معدلة / 0 ملغاة / 0 مضافة.

VERIFICATION TIER -- KSU_MIRROR_X_QISTAS_PARTIAL_VERBATIM_X_MULTISOURCE_
STRUCTURAL_CORROBORATION. Full text was extracted from a King Saud
University faculty-hosted .doc mirror (faculty.ksu.edu.sa), an academic
reproduction (NOT a direct government-portal fetch), because BOE
(laws.boe.gov.sa) does not list this regulation family as a searchable
instrument at all, gosi.gov.sa serves this content exclusively through a
client-side-rendered Angular SPA with no accessible static/API content in
this environment, qanoniah.com/qistas.com are paywalled with only a 2-3
sentence free preview, and neither the Wayback Machine (404 for the
relevant qanoniah.com URL) nor its CDX API (blocked in this session) nor
Umm al-Qura's own portal (connection reset) were reachable. The source
.doc's own internal colophon states it reproduces the official "6th
edition" (1429H/2008G) as published in Umm al-Qura Gazette issue 3833
(7/12/1421H) plus six listed amending ministerial decisions -- this is a
single, unconfirmed self-citation. Only two of the 170 articles (the
umbrella decision's own Articles 1-2) received a genuine verbatim
cross-check against a second independent source (qistas.com's free
preview), which matched word-for-word. The 4-part family's existence,
titles, and issuing-decision citation were independently corroborated
(structurally, not verbatim) via GOSI's own website (dedicated URL per
lawiha, matching titles), Saudi Press Agency, Argaam, Al-Madina, and Maaal
news coverage, and qistas.com. See the official_source
verification_methodology_note and known_unresolved_discrepancies for the
full, honest accounting of every gap, including: the single-mirror source
tier; the text reflecting only the 1429H/2008G "6th edition" with later
(2022+) amendments confirmed to exist but NOT merged in; a missing "الباب
الثاني" heading in the Registration & Contributions lawiha (all article
text 1-65 is intact and sequential; only that one divider's label is
unconfirmed); an internal date inconsistency in the source's own colophon
(25/01/1421H) versus the decision's own preamble/signature and every
external source (25/10/1421H, adopted here); and an occupational-diseases
reference table (جدول الأمراض المهنية) that is referenced twice in the
Occupational Hazards lawiha's text but whose own tabular content was not
found appended anywhere in the extracted source.

No legal text is altered, translated, or paraphrased. Arabic governs.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance_legacy_regulation", "law", "official_source",
                   "social_insurance_legacy_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "social_insurance_legacy_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "social_insurance_legacy_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "social_insurance_legacy_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "social_insurance_legacy_regulation_arabic_legal_llm",
                        "social_insurance_legacy_regulation_legal_llm_001_170.json")

LAW_ID = "sa-social-insurance-legacy-regulation-family-m33-1421"
LAW_AR = "اللوائح التنفيذية لنظام التأمينات الاجتماعية (القديم)"
STATUS = "KSU_MIRROR_X_QISTAS_PARTIAL_VERBATIM_X_MULTISOURCE_STRUCTURAL_CORROBORATION"
KEY_RE = r"social_insurance_legacy_regulation_(decision|registration|annuities|occupational_hazards|medical_committees)_art_(\d{3})$"
INSTRUMENT_TITLES_AR = {
    "decision": "قرار وزير العمل والشؤون الاجتماعية رقم (128/تأمينات) وتاريخ 25/10/1421هـ",
    "registration": "لائحة التسجيل والاشتراكات",
    "annuities": "لائحة تعويضات فرع المعاشات",
    "occupational_hazards": "لائحة تعويضات فرع الأخطار المهنية",
    "medical_committees": "لائحة اللجان الطبية",
}
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
    instrument, n = m.group(1), int(m.group(2))
    order = {"decision": 0, "registration": 1, "annuities": 2,
             "occupational_hazards": 3, "medical_committees": 4}
    return (order[instrument], n)


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
        instrument, n = m.group(1), int(m.group(2))
        ls = a.get("legal_status_ar")
        text = a["text"]
        suffix = "%s_%03d" % (instrument, n)
        ver.append({"law_key": "social_insurance_legacy_regulation", "law_component": "regulation",
                    "language": "ar", "record_layer": "SOCIAL_INSURANCE_LEGACY_REGULATION_ARABIC_VERIFIED_TEXT",
                    "instrument": instrument, "instrument_title_ar": INSTRUMENT_TITLES_AR[instrument],
                    "article_number": n, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": STATUS,
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history") or [],
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this is the historical implementing "
                                              "REGULATION FAMILY (4 لوائح + issuing ministerial decision "
                                              "128/تأمينات, 25/10/1421H) for the OLD Social Insurance Law "
                                              "(M/33, 3/9/1421H) -- a separate track from that law itself "
                                              "and from the NEW Social Insurance Law's (M/273) own 1445H "
                                              "implementing regulation. Full text sourced from a KSU "
                                              "academic .doc mirror (not a direct government-portal "
                                              "fetch); only 2 of 170 articles received a verbatim "
                                              "second-source cross-check (qistas.com). Text reflects the "
                                              "source's self-described 6th edition (1429H/2008G); later "
                                              "(2022+) amendments are confirmed to exist via web search "
                                              "but are NOT merged into this text -- see "
                                              "verification_methodology_note / "
                                              "known_unresolved_discrepancies in the source artifact."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "instrument": instrument,
                    "instrument_title_ar": INSTRUMENT_TITLES_AR[instrument],
                    "article_number": n, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "social-insurance-legacy-regulation-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s — %s" % (LAW_AR, INSTRUMENT_TITLES_AR[instrument], a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s - %s" % (LAW_AR, INSTRUMENT_TITLES_AR[instrument], a["number_label_ar"]),
                    "article_path": "social_insurance_legacy_regulation/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], INSTRUMENT_TITLES_AR[instrument]),
                                          "%s %s" % (INSTRUMENT_TITLES_AR[instrument], a["number_label_ar"]),
                                          "اللوائح التنفيذية لنظام التأمينات الاجتماعية القديم %s" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("KSU faculty-hosted .doc academic mirror "
                                                          "(faculty.ksu.edu.sa), self-described as the "
                                                          "official 6th edition (1429H/2008G, Umm al-Qura "
                                                          "issue 3833); only the umbrella decision's "
                                                          "Articles 1-2 verbatim cross-checked against a "
                                                          "second independent source (qistas.com free "
                                                          "preview); the 4-part family's existence and "
                                                          "issuing-decision citation structurally "
                                                          "corroborated via GOSI's own website and "
                                                          "multiple independent Saudi news outlets"),
                                     "source_authority_ar": "نسخة KSU الأكاديمية (.doc)، طبعة سادسة 1429هـ/2008م بحسب كولوفونها الداخلي (أم القرى 3833)؛ تحقق حرفي جزئي (مادتان فقط) عبر qistas.com، وتحقق هيكلي واسع عبر GOSI ومصادر إخبارية سعودية مستقلة",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": "%s — %s" % (LAW_AR, INSTRUMENT_TITLES_AR[instrument]),
                                     "legal_status_ar": ls,
                                     "verification_status": STATUS},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "social_insurance_legacy_regulation",
               "layer": "SOCIAL_INSURANCE_LEGACY_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "is_regulation_family": True, "instruments": src["instruments"],
               "decision_preamble_ar": src["decision_preamble_ar"],
               "edition_colophon_ar": src["edition_colophon_ar"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-social-insurance-legacy-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                           "(170 سجلاً عبر خمسة صكوك: القرار الجامع + 4 لوائح؛ 165 أصلية، 5 معدلة، 0 ملغاة، 0 مضافة)",
               "title_en": "Old/Legacy Social Insurance Law -- Implementing Regulations family, Arabic "
                           "LLM-ready layer (170 records across 5 instruments)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "text_status": STATUS,
               "is_regulation_family": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Social Insurance Legacy Regulation (family) records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
