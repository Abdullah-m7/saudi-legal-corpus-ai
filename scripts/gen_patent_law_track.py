#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Patent Law track (نظام براءات الاختراع والتصميمات التخطيطية
للدارات المتكاملة والأصناف النباتية والنماذج الصناعية, Royal Decree M/27,
29/5/1425H, approving Council of Ministers Resolution No. 159).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa's own "نص النظام" portal
(captured via two Wayback Machine snapshots, 2024-11-13 and 2025-12-12) gives
clean, non-OCR plain text for all 65 sequentially-numbered articles, but that
text is confirmed STALE: it has not incorporated the 2023 Hague-accession
amendment (Royal Decree M/45) at all (Articles 2, 18, 19), and for the 2018
institutional-terminology amendment (Council of Ministers Resolution 536) its
own displayed body still shows the pre-2018 "المدينة"/"الإدارة" wording even
where BOE's own amendment-annotation UI names and describes the change
(Articles 2, 35, 42, 63) — and, confirmed in this pass, that same staleness
silently extends to ~22 further, unflagged articles. The governing CURRENT
text was recovered by cross-verifying every BOE-sourced article against WIPO
Lex's own hosted PDF explicitly labelled as consolidated through M/45, using
two independent extraction routes (OCR, and pdftotext -layout directly over
the PDF's own native Word-generated text layer). See
sources/patent/law/official_source/patent_law_official_source.json for the
full verification_methodology_note and all documented discrepancies.

66 records: 65 sequentially-numbered articles (المادة الأولى .. الخامسة
والستون) plus one inserted "المادة الستون (مكرر)" — 59 اصلية / 6 معدلة
(Articles 2, 18, 19, 35, 42, 63) / 1 مضافة (60 مكرر) / 0 ملغاة. Six chapters
(فصول): أحكام عامة (1-42), أحكام خاصة ببراءات الاختراع (43-48), أحكام خاصة
بالتصميمات التخطيطية للدارات المتكاملة (49-53), أحكام خاصة بحماية الأصناف
النباتية الجديدة (54-58), أحكام خاصة بالنماذج الصناعية (59-60 + 60 مكرر),
أحكام ختامية (61-65).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation, and no English or Chinese text is produced for this track.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "patent", "law", "official_source",
                   "patent_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "patent", "law", "verified")
RECORDS = os.path.join(OUT_VER, "patent_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "patent_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "patent_arabic_legal_llm",
                        "patent_law_legal_llm_001_066.json")

LAW_ID = "sa-patent-law-m27-1425"
LAW_AR = "نظام براءات الاختراع والتصميمات التخطيطية للدارات المتكاملة والأصناف النباتية والنماذج الصناعية"
STATUS = "WIPOLEX_M45_CONSOLIDATED_X_BOE_PLAINTEXT_STALE_TERMINOLOGY_CROSS_VERIFIED"
KEY_RE = r"patent_art_(\d{3})(_mukarrar)?$"
AMENDED_KEYS = {"patent_art_002", "patent_art_018", "patent_art_019",
                "patent_art_035", "patent_art_042", "patent_art_063"}
ADDED_KEYS = {"patent_art_060_mukarrar"}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك أنه إنه التي الذين اللذين هذه هؤلاء").split())


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
    is_bis = 1 if m.group(2) else 0
    return (n, is_bis)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n, is_bis = _sort_key(key)
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "patent", "law_component": "law", "language": "ar",
                    "record_layer": "PATENT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_1425h_text": a.get("original_1425h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — BOE's own portal text is "
                                              "confirmed stale relative to the 2018 and 2023 "
                                              "amendments, so the governing current wording "
                                              "rests on WIPO Lex's hosted PDF explicitly "
                                              "labelled as consolidated through Royal Decree "
                                              "M/45, cross-verified by two independent "
                                              "extraction routes — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including the "
                                              "terminology-substitution-scope discrepancy and "
                                              "the Art.35-vs-42/63 drafting inconsistency."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "patent-law-llm-art-%03d%s" % (n, "-bis" if is_bis else ""),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "patent/law/articles/%03d%s" % (n, "_mukarrar" if is_bis else ""),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام براءات الاختراع" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — WIPO Lex hosted PDF "
                                                          "consolidated through Royal Decree "
                                                          "M/45, cross-verified against BOE's "
                                                          "own portal text (confirmed stale) "
                                                          "and against SAIP's administering-"
                                                          "authority status"),
                                     "source_authority_ar": "مرسوم ملكي — ملف PDF من قاعدة بيانات WIPO Lex موحّد حتى المرسوم الملكي رقم (م/45)، تمت مقارنته بنص بوابة هيئة الخبراء (BOE) الذي تبين أنه غير محدّث",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "patent",
               "layer": "PATENT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-patent-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (66 مادة؛ نص موحّد: 59 أصلية، 6 معدّلة، 1 مضافة)",
               "title_en": "Saudi Patent Law (M/27) — Arabic LLM-ready layer (66 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 66], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Patent Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
