#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Organizational Statute of the Communications, Space and
Technology Commission (CST) track (تنظيم هيئة الاتصالات والفضاء والتقنية,
Council of Ministers Resolution No. 74, 5/3/1422H, amended by Resolutions
133/1424H, 120/1440H, 253/1444H and 430/1446H).

VERIFICATION TIER -- see sources/cst_organizational_statute/law/
official_source/cst_organizational_statute_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa itself, reached via TWO Wayback Machine
snapshots of its own 'LawDetails' page (Id f327464b-2f5a-475d-aa94-
a9a700f2e817) -- one from 11 Feb 2025 (pre-dating BOE's own database catching
up with the 2022/2024 amendments) and one from 27 Feb 2026 (BOE's own
database, by then, DOES carry the current CST name and Resolution 430's own
quoted replacement text for Articles 3 and 4 specifically, via its own
'تعديلات المادة' popups). laws.boe.gov.sa's LIVE portal and cst.gov.sa both
returned a TLS connection reset on every direct attempt this pass (confirmed
via curl -v, not a mere timeout) -- but the Wayback Machine itself was fully
reachable this pass (unlike a prior REGA-track pass), which is what makes
this track's primary-source grounding possible.

CONFIRMED GAP: BOE's own page does NOT yet carry per-article amendment
popups for Articles 1, 5, 8, or 10, despite qanoonsa.com's full gazette
reproduction of Resolution 430 stating all four were also amended by it.
This track's text for those four articles' 2024-amendment layer therefore
rests on qanoonsa.com's Umm Al-Qura Gazette reproduction (issue 5065, 17 Jan
2025G) ALONE -- honestly flagged as a single-secondary-source reliance for
that specific layer, not silently upgraded to match Articles 3/4's stronger
dual-source (BOE + qanoonsa, word-for-word match) grounding.

nezams.com independently triple-confirms the base (2001) 19-article text and
fills a decree-number gap BOE's own popup leaves blank ('()') for Resolution
120 -- but nezams.com has NOT been updated past Resolution 120 and must not
be read as corroborating (or contradicting) Resolutions 253 or 430.

SIX ARTICLES CARRY CONFIRMED, SAFELY-RECONSTRUCTABLE AMENDMENTS (all cleanly
specified -- exact paragraph letter/number, or a complete 'لتكون بالنص
الآتي' substitution; none required inventing an unstated insertion point,
except Article 1's new definition whose list position is unspecified and
flagged):
  - Article 1: one definition deleted ('النظام'), one added ('القطاعات ذات
    الصلة بالهيئة') -- Resolution 430.
  - Article 3: complete substitution, 26 functions -- Resolution 430,
    chained after a since-fully-superseded Resolution 133 (renaming/IT-tasks
    addition, recorded as a superseded intermediate step only).
  - Article 4: complete substitution, 7-member board -- Resolution 430,
    chained after a since-fully-superseded Resolution 120 (partial
    paragraph-1-only substitution, recorded as a superseded intermediate
    step only).
  - Article 5: two paragraphs replaced (ب, ج), one paragraph deleted (ط,
    with the resulting letter gap preserved literally, not relettered), one
    closing paragraph added -- Resolution 430.
  - Article 8: three new paragraphs appended (ي, ك, ل) -- Resolution 430.
  - Article 10: complete substitution, 8 financial-resource items --
    Resolution 430.

19 records: 13 اصلية, 6 معدلة, 0 ملغاة, 0 مضافة. Flat structure, no
أبواب/فصول. No inline per-article titles in the source -- no title_ar field
is used.

A CONFIRMED, UNRESOLVED TEXTUAL INCONSISTENCY is carried forward honestly:
Article 1's own definitions of 'التنظيم'/'الهيئة'/'المجلس'/'المحافظ'/
'العضو' still read the Authority's ORIGINAL 2001 name ('هيئة الاتصالات
السعودية'), never textually updated by either of the Authority's two
renaming decisions (Resolution 133/1424H or Resolution 253/1444H) even
though Resolution 430 explicitly touched Article 1 to delete/add OTHER
definitions. See known_unresolved_discrepancies, key
cst_article1_entity_name_not_updated_despite_two_renames.

No legal text is altered beyond whitespace/hyphen-style normalization, and
splicing each amendment decree's own quoted replacement/addition text into
the position its own operative clause specifies. Arabic governs; no
translation/paraphrase/interpretation performed on the Arabic text.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cst_organizational_statute", "law", "official_source",
                   "cst_organizational_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cst_organizational_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cst_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cst_organizational_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cst_organizational_statute_arabic_legal_llm",
                        "cst_organizational_statute_legal_llm_001_019.json")

LAW_ID = "sa-cst-organizational-statute-74-1422"
LAW_AR = "تنظيم هيئة الاتصالات والفضاء والتقنية"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_BOE_WAYBACK_DUAL_SNAPSHOT_BASE_TEXT_X_"
              "NEZAMS_TRIPLE_CROSS_CHECK_X_QANOONSA_UMM_AL_QURA_5065_FOR_RESOLUTION_430_"
              "ARTS_3_4_BOE_POPUP_VERBATIM_MATCH_ARTS_1_5_8_10_QANOONSA_ONLY_LIVE_BOE_AND_"
              "CST_GOV_SA_BOTH_TLS_RESET_THIS_PASS")
KEY_RE = r"cst_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {
    "cst_organizational_statute_art_001",
    "cst_organizational_statute_art_003",
    "cst_organizational_statute_art_004",
    "cst_organizational_statute_art_005",
    "cst_organizational_statute_art_008",
    "cst_organizational_statute_art_010",
}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الهيئة المجلس الرئيس بوجه خاص").split())


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
        ver.append({"law_key": "cst_organizational_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "CST_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on TWO Wayback "
                                              "Machine captures of laws.boe.gov.sa's own "
                                              "LawDetails page (11 Feb 2025 and 27 Feb 2026), "
                                              "cross-checked against nezams.com (base text + "
                                              "Resolution 120 only) and qanoonsa.com (full "
                                              "Umm Al-Qura Gazette reproduction of Resolutions "
                                              "253 and 430). BOE's own page carries Resolution "
                                              "430's popup text verbatim for Articles 3 and 4 "
                                              "only (word-for-word match with qanoonsa); "
                                              "Articles 1, 5, 8 and 10's 2024-amendment text "
                                              "rests on qanoonsa.com alone -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's tier as "
                                              "uniform across all six amended articles. "
                                              "laws.boe.gov.sa's live portal and cst.gov.sa "
                                              "both returned a TLS reset on every direct "
                                              "attempt this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "cst-organizational-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "cst_organizational_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم هيئة الاتصالات والفضاء والتقنية" %
                                          a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(74), 5/3/1422H — laws.boe.gov.sa "
                                                          "via two Wayback Machine snapshots "
                                                          "(11 Feb 2025, 27 Feb 2026); "
                                                          "nezams.com triple-cross-check of "
                                                          "base text + Resolution 120; "
                                                          "qanoonsa.com full Umm Al-Qura "
                                                          "Gazette (issue 5065) reproduction "
                                                          "of Resolutions 253 and 430 -- "
                                                          "BOE's own popups verbatim-match "
                                                          "qanoonsa for Articles 3/4 only; "
                                                          "live BOE and cst.gov.sa both TLS "
                                                          "reset this pass"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (74) وتاريخ 5/3/1422هـ — عبر نسختين مؤرشفتين لدى Wayback Machine من صفحة هيئة الخبراء بمجلس الوزراء ذاتها (11 فبراير 2025، 27 فبراير 2026)؛ مطابقة ثلاثية مع nezams.com للنص الأصلي والقرار 120؛ ومطابقة مع qanoonsa.com (إعادة نشر كاملة لعدد جريدة أم القرى رقم 5065) للقرارين 253 و430 -- شعبة تعديلات المادة في موقع هيئة الخبراء تطابق نص qanoonsa حرفياً للمادتين الثالثة والرابعة فقط؛ تعذّر الوصول المباشر لموقعي هيئة الخبراء وهيئة الاتصالات والفضاء والتقنية (إعادة ضبط TLS) هذه الجولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cst_organizational_statute",
               "layer": "CST_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cst-organizational-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة؛ 13 أصلية و6 معدلة)",
               "title_en": "Organizational Statute of the Communications, Space and Technology "
                          "Commission (CST) — Arabic LLM-ready layer (19 records: 13 original, "
                          "6 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready CST Organizational Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
