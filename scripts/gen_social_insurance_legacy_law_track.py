#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Social Insurance Law (Old/Legacy System) track (نظام
التأمينات الاجتماعية — القديم، المرسوم الملكي رقم م/33، 3/9/1421هـ).

SCOPE NOTE — this is the OLD social-insurance law only. It governs everyone
already enrolled in Saudi social insurance BEFORE 1 July 2025 and remains
concurrently in force alongside the NEW Social Insurance Law (Royal Decree
M/273, 26/12/1445H, already merged at sources/social_insurance/law/
official_source/social_insurance_law_official_source.json), which governs
only new labor-market entrants from that date onward. The two laws share
the identical Arabic title "نظام التأمينات الاجتماعية" despite being
differently-numbered/dated instruments covering different populations — a
genuine naming collision, documented in known_unresolved_discrepancies (see
the official_source JSON), analogous to the Franchise Law/Anti-Concealment
Law M/22 collision already flagged elsewhere in this corpus.

VERIFICATION TIER — full article text (71 article-entries: 70 numbered +
Article 58 مكرر) was extracted directly from a Wayback Machine archive
snapshot (2026-02-09) of the official BOE portal (laws.boe.gov.sa), fetched
via curl using the "if_" raw-content modifier with a desktop User-Agent
header (laws.boe.gov.sa's live portal itself returned HTTP 503; WebFetch
cannot reach web.archive.org directly — no egress-policy circumvention was
used or needed, curl reached it directly), and parsed from its structured
`<div class="article_item">` / `<h3 class="center">` (فصل/قسم heading)
markup, including each amended/added article's own "تعديلات المادة"
amendment-history popup (decree number, date, and literal substitution
text). Full-text cross-checked (20+ of 71 articles, plus 100% of the nine
changed-article amendment-history popups) word-for-word — verbatim match
modulo optional tashkil/dash-style — against a direct fetch of nezams.com's
"نظام التأمينات الاجتماعية (القديم)" page, whose own article index also
independently confirmed the complete, gap-free 1-70 (+58 مكرر) sequence and
all فصل/قسم attachment points. Two BOE-portal-staleness findings (Articles
10 and 37, where BOE's default rendered main-body text is the ORIGINAL
pre-amendment wording, not the current one) were resolved using BOE's own
amendment-history popups (cross-verified against nezams.com) plus, for
Article 37 specifically, independent Saudi news corroboration (Okaz,
Al-Riyadh) of the current broader 3-part text — the same "BOE portal lag"
pattern already documented in this corpus's Traffic Law and Environmental
Law tracks. See sources/social_insurance_legacy/law/official_source/
social_insurance_legacy_law_official_source.json's verification_methodology_note
for the full methodology and known_unresolved_discrepancies for all
documented gaps/anomalies, including: the dual-law title collision; the
Article 10 board-composition reconciliation and a further unresolved
divergence against GOSI's own website; the Article 37 BOE-staleness
resolution; the Article 38 sub-paragraph deletion (NOT to be confused with
the 2024 retirement-age transitional override, which lives in the NEW
law's own promulgating Royal Decree, not here); the Article 41 instrument-
type citation discrepancy; and a duplicate/glitch amendment-history popup
attached to Article 58 (base).

71 records (70 article-numbered + 1 مكرر): 63 اصلية / 7 معدلة (Articles 2,
10, 37, 38, 41, 43, 62) / 0 ملغاة / 1 مضافة (Article 58 مكرر, Royal Decree
M/16, 24/3/1431H). 7 فصول, with الفصل الخامس split into 4 نested أقسام
(القسم الأول تعويضات فرع الأخطار المهنية 27-37، القسم الثاني تعويضات فرع
المعاشات 38-41، القسم الثالث أحكام خاصة بتطبيق فرع المعاشات على المشتركين
اختيارياً 42-46، القسم الرابع أحكام مشتركة بين فرع الأخطار المهنية وفرع
المعاشات 47-58 بما فيها 58 مكرر).

The Royal Decree's own preamble and the companion Council of Ministers
Resolution 199 text (forming a coordination committee between the civil/
military pension systems and social insurance, and instructing actuarial
studies) are NOT numbered articles of the law and are therefore not part
of `articles`; they are preserved verbatim in the source JSON's
`preamble_ar` / `decree_transitional_provisions_ar` fields.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance_legacy", "law", "official_source",
                   "social_insurance_legacy_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "social_insurance_legacy", "law", "verified")
RECORDS = os.path.join(OUT_VER, "social_insurance_legacy_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "social_insurance_legacy_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "social_insurance_legacy_arabic_legal_llm",
                        "social_insurance_legacy_law_legal_llm_001_071.json")

LAW_ID = "sa-social-insurance-law-legacy-m33-1421"
LAW_AR = "نظام التأمينات الاجتماعية (القديم)"
STATUS = "BOE_WAYBACK_X_NEZAMS_SPOTCHECK_X_OKAZ_ALRIYADH_CORROBORATED"
KEY_RE = r"social_insurance_legacy_art_(\d{3})(_mukarrar)?$"
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
        original = a.get("original_1421h_text")
        suffix = key.replace("social_insurance_legacy_art_", "")
        ver.append({"law_key": "social_insurance_legacy", "law_component": "law", "language": "ar",
                    "record_layer": "SOCIAL_INSURANCE_LEGACY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "original_1421h_text": original,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this is the OLD Social Insurance Law "
                                              "(Royal Decree M/33, 3/9/1421H), distinct from the NEW "
                                              "Social Insurance Law (M/273, 26/12/1445H) which shares "
                                              "the identical Arabic title but is a separate track "
                                              "covering only new labor-market entrants from 1/7/2025. "
                                              "Full text extracted from a Wayback Machine BOE archive "
                                              "snapshot (2026-02-09), cross-verified (20+ of 71 "
                                              "articles, plus 100% of the nine changed-article "
                                              "amendment popups) against nezams.com, with Articles 10 "
                                              "and 37's current reconciled text additionally "
                                              "corroborated (Art. 37 via independent Okaz/Al-Riyadh "
                                              "news coverage) over BOE's stale default rendering — "
                                              "see verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "social-insurance-legacy-law-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "original_1421h_text": original,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "social_insurance_legacy/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام التأمينات الاجتماعية القديم" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("BOE (laws.boe.gov.sa) via Wayback Machine "
                                                          "archive snapshot 2026-02-09, direct primary "
                                                          "fetch; cross-verified (20+ of 71 articles, "
                                                          "plus all nine changed-article amendment "
                                                          "popups) against nezams.com; Article 37's "
                                                          "current reconciled text additionally "
                                                          "corroborated via independent Okaz/Al-Riyadh "
                                                          "news coverage"),
                                     "source_authority_ar": "بوابة هيئة الخبراء BOE عبر أرشيف Wayback Machine (لقطة 2026-02-09)، مع مطابقة موسّعة (20+ من 71 مادة، وكامل نوافذ تعديلات المواد التسع) مقابل nezams.com، وتأكيد إضافي عبر تغطية صحفية (عكاظ/الرياض) للمادة 37",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "social_insurance_legacy",
               "layer": "SOCIAL_INSURANCE_LEGACY_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "preamble_ar": src["preamble_ar"],
               "decree_transitional_provisions_ar": src["decree_transitional_provisions_ar"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-social-insurance-legacy-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                           "(71 سجلاً؛ نص موحّد: 63 أصلية، 7 معدلة، 0 ملغاة، 1 مضافة)",
               "title_en": "Saudi Social Insurance Law (Old/Legacy System) — Arabic LLM-ready layer "
                           "(71 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 70], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Social Insurance Law (Old/Legacy System) records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
