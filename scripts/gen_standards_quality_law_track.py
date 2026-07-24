#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Standards and Quality Law track (نظام المواصفات والجودة,
Royal Decree M/36, 29/1/1446H / 5 August 2024G; published Umm al-Qura
Issue 5043, 16/8/2024G).

CRITICAL DECREE-NUMBER CORRECTION -- the coverage-gap-map that flagged this
law cited Royal Decree "M/148, 2024" for BOTH this law and its sibling, the
Product Safety Law. That number could not be confirmed anywhere (direct web
search, laws.boe.gov.sa, nezams.com, qanoonsa.com, decreesa.com, or
secondary legal commentary). Every independent source -- including an
OFFICIAL government source (Umm al-Qura Gazette, uqn.gov.sa) -- converges
instead on Royal Decree M/36, dated 29/1/1446H, approving Council of
Ministers Resolution No. 93 (24/1/1446H). "M/148" is NOT used in this track.

RELATIONSHIP TO THE PRODUCT SAFETY LAW -- the SAME Royal Decree M/36
contains TWO separate clauses: Clause One (البند أولا) approves the Product
Safety Law (نظام سلامة المنتجات, 37 articles / 9 أبواب, track_id:
product_safety); Clause Two (البند ثانيا) approves THIS law (نظام
المواصفات والجودة, 24 articles / 7 أبواب) -- a wholly distinct statute on a
different subject, jointly promulgated in the same decree instrument. This
is NOT a decree-number collision across different Hijri years and NOT one
law under two names; it is two genuinely separate laws sharing one joint
enacting decree (a normal, documented Saudi legislative practice). This law
is ALSO distinct from SASO's own founding statute (Royal Decree M/10,
3/3/1392H, establishing the Saudi Standards, Metrology and Quality
Organization as a government body) -- no relationship, no repeal, between
the two. See
sources/standards_quality/law/official_source/standards_quality_law_official_source.json's
verification_methodology_note for the full account, including the two
official Umm al-Qura Gazette citations (uqn.gov.sa/details?p=26778 for this
law's "البند ثانيا"; uqn.gov.sa/details?p=26780 for the sibling's "البند
أولا") that literally quote the decree and, in passing, this law's own
Article 23 text verbatim.

VERIFICATION TIER: TIER_2. An official government source (Umm al-Qura
Gazette notices for both laws' later Executive Regulations) confirms the
decree/resolution identity and quotes Article 23's text verbatim (matching
this track exactly); a dedicated laws.boe.gov.sa index entry for this law's
NAME was independently found via web search (Id
c487b0ff-8e52-442d-bf62-b1cd009fdc57), though the live portal itself could
not be fetched this pass. The full 24-article text is primarily from
qanoonsa.com, cross-checked word-for-word against nezams.com (independent,
non-derivative), with only two single-word discrepancies found in Article 1
-- both resolved toward qanoonsa.com's reading (see discrepancies below).
web.archive.org was NOT attempted (org egress-policy block, not bypassed).

24 records, ALL اصلية (no confirmed amendments as of 2026-07-24), 0 ملغاة,
0 مضافة. 7 أبواب (chapters): التعريفات (1) -- أحكام عامة (2-6) -- إعداد
واعتماد وتبني المواصفة والوثيقة ذات الصلة (7-11) -- مراجعة وتطبيق المواصفة
السعودية والوثيقة ذات الصلة (12-13) -- الجودة (14-17) -- ضبط مخالفات النظام
وإيقاع العقوبات (18-22) -- أحكام ختامية (23-24).

ARTICLE 1 -- TWO SINGLE-WORD DISCREPANCIES RESOLVED: nezams.com reads "ما لم
يقض السياق" (missing a ت) where qanoonsa.com reads "ما لم يقتض السياق" (the
standard formula, identical to the Product Safety Law's own Article 1 and
dozens of other tracks in this corpus); and nezams.com spells a tanween
fatha directly on ق with no alif carrier ("وفقً", non-standard Arabic
orthography) where qanoonsa.com spells it fully ("وفقا"). Both resolved
toward qanoonsa.com's reading.

ARTICLE 10 -- VERBATIM ENGLISH ACRONYM: Article 10 legitimately states that
the Saudi Standard begins with the identifying symbol "(م ق س)" in Arabic
and "(SASO)" in English -- the Latin letters "SASO" are an authentic part of
this law's own Arabic text at this one point, not a scraping artifact.

NO NAMED PREDECESSOR REPEAL: Article 24 (closing article) carries only a
generic conflict clause ("ويلغي ما يتعارض معه من أحكام") -- no specific
prior law/regulation is named.

Implementing Regulation (Minister of Commerce Decision No. 098, 18/5/1446H,
per SASO Board adoption) is OUT OF SCOPE this pass (one-instrument-per-pass
rule) -- flagged as a documented follow-up candidate.

TASHKEEL: Article 1 carried partial tashkeel in nezams.com (stripped
uniformly here; qanoonsa.com's version -- used for the rest of the law --
was already clean). Stray curly-quotes/nbsp/double-spaces normalized
(display layer only, no legal text altered). Arabic governs; no
translation, paraphrase or interpretation performed; read-only over input,
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "standards_quality", "law", "official_source",
                   "standards_quality_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "standards_quality", "law", "verified")
RECORDS = os.path.join(OUT_VER, "standards_quality_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "standards_quality_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "standards_quality_arabic_legal_llm",
                        "standards_quality_law_legal_llm_001_024.json")

LAW_ID = "sa-standards-quality-law-m-36-1446"
LAW_AR = "نظام المواصفات والجودة"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"standards_quality_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة المجلس ذات الصلة").split())


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


STATUS_MAIN = ("UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_QANOONSA_PRIMARY_TEXT_"
               "X_NEZAMS_CROSS_VERIFIED_2_WORDS_CORRECTED_BOE_LAWID_UNCONFIRMED_LIVE_UNREACHABLE")

GOV_NOTE = ("Arabic governs. Decree-number CORRECTED from the coverage-gap-map's unconfirmable "
            "M/148 to the multi-source-confirmed Royal Decree M/36 (29/1/1446H / 5 Aug 2024G), "
            "approving CoM Resolution 93 (24/1/1446H), published Umm al-Qura Issue 5043 "
            "(16/8/2024G). This same decree's Clause One (البند أولا) separately approved the "
            "wholly distinct Product Safety Law (track_id: product_safety) -- two different "
            "statutes jointly promulgated in one decree, not a numbering collision and not one "
            "law under two names. This law is ALSO distinct from SASO's own founding statute "
            "(Royal Decree M/10, 3/3/1392H). laws.boe.gov.sa has an indexed entry for this law's "
            "name (Id c487b0ff-8e52-442d-bf62-b1cd009fdc57, confirmed via web search) but the "
            "live portal was unreachable this pass (connection reset / HTTP 503; Wayback "
            "egress-blocked, NOT bypassed). An official Umm al-Qura Gazette notice "
            "(uqn.gov.sa/details?p=26778) quotes the decree AND this law's Article 23 verbatim, "
            "matching this track exactly -> TIER_2. Full text primarily from qanoonsa.com, "
            "cross-checked against nezams.com; two single-word discrepancies in Article 1 "
            "resolved toward qanoonsa.com. Article 10 legitimately contains the Latin acronym "
            "'SASO' as part of the official Arabic text (not a scraping artifact). 24 articles, "
            "ALL اصلية, 7 أبواب, no confirmed amendments (checked 2026-07-24), no "
            "named-predecessor repeal (Art 24 is a generic conflict clause only). See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/36 (29/1/1446H / 5 Aug 2024G), CoM Resolution 93 (24/1/1446H), "
            "published Umm al-Qura Issue 5043 (16/8/2024G). Decree number CORRECTED from the "
            "coverage-gap-map's unconfirmable M/148. Full text from qanoonsa.com, cross-checked "
            "against nezams.com (two single-word discrepancies in Article 1 resolved toward "
            "qanoonsa.com). An official Umm al-Qura Gazette notice "
            "(uqn.gov.sa/details?p=26778) independently confirms the decree and quotes Article "
            "23 verbatim. laws.boe.gov.sa has a confirmed index entry for this law's name but "
            "was unreachable live this pass (503 / connection reset; Wayback egress-blocked, "
            "not bypassed) -> TIER_2")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/36 وتاريخ 29/1/1446هـ (الموافق 5 أغسطس 2024م)، وقرار مجلس "
               "الوزراء رقم 93 وتاريخ 24/1/1446هـ (منشور بأم القرى العدد 5043 بتاريخ 16/8/2024م). "
               "رقم المرسوم مصحح من (م/148) غير المؤكد في خريطة الفجوات الأولية. النص الكامل من "
               "qanoonsa.com، متقاطع مع nezams.com (خلافان كلاميان طفيفان في المادة الأولى، محسومان "
               "لصالح qanoonsa.com). إشعار جريدة أم القرى الرسمية (uqn.gov.sa/details?p=26778) يؤكد "
               "المرسوم ويقتبس نص المادة 23 حرفيا. لـlaws.boe.gov.sa سجل مفهرس مؤكد لاسم هذا النظام "
               "لكن تعذر الوصول الحي إليه هذه الجولة (503 / connection reset؛ Wayback محظور، لم "
               "يُتجاوَز) -- TIER_2")


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
        top_status = STATUS_UNCHANGED
        ver.append({"law_key": "standards_quality", "law_component": "law",
                    "language": "ar",
                    "record_layer": "STANDARDS_QUALITY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "standards-quality-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "standards_quality/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المواصفات والجودة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "standards_quality",
               "layer": "STANDARDS_QUALITY_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-standards-quality-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (24 مادة؛ جميعها أصلية)",
               "title_en": ("Standards and Quality Law — Arabic LLM-ready layer "
                            "(24 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 24], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Standards and Quality Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
