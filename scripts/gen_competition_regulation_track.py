#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Competition Law track
(اللائحة التنفيذية لنظام المنافسة, GAC Board of Directors Decision No. (337),
25/1/1441H (24 Sep 2019), issued pursuant to Article 27 of the Competition Law,
Royal Decree M/75, 29/6/1440H).

This is the companion-regulation follow-up candidate explicitly flagged by this
corpus's own competition_law track (see sources/competition/law/official_source/
competition_law_official_source.json, known_unresolved_discrepancies key
competition_implementing_regulation: "A companion Implementing Regulation exists
per this law's own Article 27, reportedly issued via GAC Board of Directors
Decision 337 (25/1/1441H) ... GAC's own site (gac.gov.sa) was unreachable
throughout that research pass, so the primary document was not independently
confirmed ... candidate for a follow-up companion-track ingestion"). This track
ingests it -- confirming the number/date/article-count/structure independently.

CAPTURED SCOPE -- IMPORTANT. The full Regulation contains 90 articles across 11
chapters (independently confirmed this pass via WIPO Lex record 19749/SA071
metadata, its Arabic and English official PDFs, and qanoniah.com's own index).
This track ingests ONLY Articles 1-5 (Chapters 1 "التعريفات والأهداف", arts 1-2,
and 2 "الاختصاص ونطاق التطبيق", arts 3-5) -- the ONLY articles for which a clean,
independent, correct-digit Arabic full text could be obtained AND cross-verified
this pass. Articles 6-90 are NOT ingested; see the source artifact's
known_unresolved_discrepancies (key competition_regulation_partial_scope_arts_
6_90_pending) for the fully-disclosed reason. This honours this corpus's binding
rule -- nothing untrusted enters -- over completeness: the only fetchable
COMPLETE Arabic source (WIPO Lex sa071ar.pdf) has an unrecoverable lossy digit-
CMap extraction defect (real digits 2,3,5,6,7,8,9 collapse many-to-one: "337"
extracts as "663"; the list 1..7 extracts as 1,5,6,4,2,3,3), and the clean
Arabic source (qanoniah.com) auth-gates articles 6+ (HTTP 401). No fabricated
numerals were introduced for the un-captured articles.

VERIFICATION TIER for the 5 captured articles -- DUAL INDEPENDENT SOURCE:
(1) PRIMARY TEXT: qanoniah.com's backend API (api.qanoniah.com/v1/files/...),
which returns real clean-Unicode Arabic (correct Western-Arabic digits) and
served Articles 1-5 in full without authentication.
(2) INDEPENDENT CORROBORATION: WIPO Lex's official Arabic PDF (sa071ar.pdf, a
born-digital MS-Word-produced file created 25 Sep 2019, fetched via its signed
CloudFront URL) -- its LETTER content matches qanoniah's Articles 1-5 exactly in
substance, providing a second independent confirmation. (WIPO's numerals are not
usable due to the digit-CMap defect, but Articles 1-5 contain only safe digits
{1,2,3,4} plus spelled-out cross-references, all matching qanoniah.)

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology: it is
unreachable this pass (HTTP 503) AND, more fundamentally, has no dedicated lawId
page for this Board-level Implementing Regulation at all (only for the base
Competition Law and, separately, the GAC organisational statute) -- consistent
with BOE's practice. The issuing Authority's own site (gac.gov.sa /
beta.gac.gov.sa) was unreachable this pass (HTTP 503 / DNS failure).

SUPERSESSION (confirmed): this Regulation replaces the 2014 Implementing
Regulation (Competition Council Decision 126, 4/9/1435H, under the repealed
Competition Law M/25) -- WIPO Lex explicitly marks the 2014 record (19750/SA072)
as superseded by the current SA071.

Diacritics (tashkeel), tatweel, and zero-width formatting characters are stripped
uniformly for consistency with this corpus's competition_law track and other
tracks. Arabic governs; no translation/paraphrase/interpretation was performed,
and the English (WIPO) text was NOT used to correct any Arabic character -- it
was used only to cross-check non-governing structural metadata (article count,
11-chapter map, per-chapter article ranges). Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "competition", "regulation", "official_source",
                   "competition_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "competition", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "competition_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "competition_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "competition_regulation_arabic_legal_llm",
                        "competition_regulation_legal_llm_001_005.json")

LAW_ID = "sa-competition-regulation-337-1441"
LAW_AR = "اللائحة التنفيذية لنظام المنافسة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"competition_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة المنشأة النظام المنافسة").split())


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


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


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
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "competition", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "COMPETITION_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs. CAPTURED SCOPE = Articles 1-5 "
                                              "(Chapters 1-2 of 11); the full Regulation has 90 "
                                              "articles -- Articles 6-90 are NOT in this track "
                                              "(see the source artifact's "
                                              "known_unresolved_discrepancies, key "
                                              "competition_regulation_partial_scope_arts_6_90_"
                                              "pending). PRIMARY TEXT source is qanoniah.com's "
                                              "clean-Unicode API (correct digits), independently "
                                              "corroborated for these 5 articles by WIPO Lex's "
                                              "official Arabic PDF (sa071ar.pdf) letter-for-"
                                              "letter. laws.boe.gov.sa was checked first but is "
                                              "unreachable this pass and has no dedicated lawId "
                                              "page for this Board-level Implementing Regulation; "
                                              "gac.gov.sa (issuer) was also unreachable. Decision "
                                              "337 / 25-1-1441H, article count (90), 11-chapter "
                                              "structure, and supersession of the 2014 "
                                              "Regulation (Decision 126, 4/9/1435H) are cross-"
                                              "verified via WIPO Lex, qanoniah metadata, SPA, and "
                                              "secondary legal sources. See "
                                              "verification_methodology_note before relying on "
                                              "provenance -- in particular the disclosed "
                                              "unrecoverable WIPO digit-CMap defect that gates "
                                              "the un-captured articles."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "competition-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "competition/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المنافسة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("GAC Board of Directors Decision No. "
                                                          "(337) (25/1/1441H) — text via "
                                                          "qanoniah.com (clean-Unicode API), "
                                                          "independently corroborated by WIPO Lex "
                                                          "official Arabic PDF (sa071ar.pdf); "
                                                          "laws.boe.gov.sa unreachable this pass "
                                                          "and has no dedicated lawId page for "
                                                          "this Implementing Regulation; "
                                                          "gac.gov.sa (issuer) unreachable. "
                                                          "CAPTURED SCOPE = Articles 1-5 of 90"),
                                     "source_authority_ar": "قرار مجلس إدارة الهيئة العامة للمنافسة رقم (337) وتاريخ 25/1/1441هـ — النص من qanoniah.com (واجهة يونيكود نظيفة)، مؤكَّد مستقلا بملف WIPO Lex العربي الرسمي (sa071ar.pdf)؛ بوابة هيئة الخبراء غير قابلة للوصول هذه الجولة ولا تملك صفحة مخصصة لهذه اللائحة؛ موقع الهيئة (المُصدِر) غير متاح. النطاق المُدرَج = المواد 1-5 من 90",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "competition",
               "layer": "COMPETITION_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "captured_scope_note": src.get("captured_scope_note", ""),
               "full_regulation_article_count": src.get("full_regulation_article_count"),
               "full_regulation_chapter_count": src.get("full_regulation_chapter_count"),
               "full_regulation_chapter_structure": src.get("full_regulation_chapter_structure", []),
               "supersedes": src.get("supersedes", {}),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-competition-regulation-arabic-legal-llm-captured-1-5",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (النطاق المُدرَج: المواد 1-5 من 90؛ جميعها أصلية)",
               "title_en": ("Implementing Regulation of the Competition Law — Arabic LLM-ready "
                            "layer (CAPTURED SCOPE: Articles 1-5 of 90; all original). Articles "
                            "6-90 pending — see known_unresolved_discrepancies."),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 5], "full_regulation_article_count": 90,
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Competition Regulation records "
          "(captured scope: Articles 1-5 of 90)" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
