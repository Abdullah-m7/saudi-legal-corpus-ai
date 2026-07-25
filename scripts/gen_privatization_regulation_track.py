#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Privatization Law track
(اللائحة التنفيذية لنظام التخصيص), issued under Article 44 of the Privatization
Law (Royal Decree M/63, 5/8/1442H) by the National Center for Privatization
(NCP) Board of Directors.

VERIFICATION TIER -- see sources/privatization_regulation/law/official_source/
privatization_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE (governing text): fetched DIRECTLY and LIVE from the Official
Gazette itself, https://uqn.gov.sa/details?p=24451 (HTTP 200, via curl with a
standard browser User-Agent header -- the bare request without one returned
HTTP 503/301). This is the CURRENT, AMENDED, consolidated text: 169 articles
across 8 books (أبواب), published 21/7/1445H = 2 February 2024G (precise
publish timestamp 2024-02-02T14:52:50+03:00 per the page's own metadata),
reflecting NCP Board Decision No. (1/4/2023) dated 18/6/1445H = 31 December
2023G. Text was extracted programmatically from the page's own HTML structure
(each article/clause is one <div><span><span> unit) -- NOT OCR, NOT a
secondary aggregator -- so no letter-transposition risk of the kind documented
for this corpus's misa.gov.sa / argaam PDF sources.

laws.boe.gov.sa: checked first per this corpus's standard methodology;
unreachable this pass (HTTP 000 connection-reset), consistent with the pattern
documented across this session's other tracks. No dedicated lawId page is
known for NCP board-level decisions. web.archive.org is org-policy-blocked
this session and was NOT bypassed. r.jina.ai reader-proxy was tried as an
explicit fallback and returned HTTP 401 ("blocked ... bad IP reputation") for
both uqn.gov.sa URLs -- an infrastructure-level block, not content-related,
and moot since the direct fetch (with a browser UA) succeeded.

ORIGINAL (2021) VERSION FOR AMENDMENT-DIFFING ONLY: NCP Board Decision No.
(Q-9/2021) dated 23/4/1443H, 159 articles / 8 books, fetched as an official PDF
hosted by argaam.com (argaamplus.s3.amazonaws.com, HTTP 200, 59 pages). Like
this corpus's misa.gov.sa PDF for the base Privatization Law, pdftotext
reverses some in-word letter-groups in this particular PDF -- so it was used
ONLY for structural comparison (confirmed: 159 articles, 8 books, matching book
count) and targeted content comparison to locate the 2023 amendment's scope; it
was NEVER adopted as governing text for any article.

INDEPENDENT CORROBORATION: argaam.com (news ids 1526053 or the 2021/2022
approval, 1702284 for the 2023/2024 amendment), ajel.sa (3 Feb 2024, states
"تتضمن 169 مادة" -- an independent confirmation of the exact article count),
alarabiya.net, snadlaw.sa, qanoonsa.com.

VERIFICATION TIER: TIER_1 for the governing text (direct live fetch of the
primary Official Gazette page itself, HTTP 200, no secondary aggregator, no
OCR) -- stronger than this corpus's base Privatization Law track (TIER_2,
which took its full text from a secondary aggregator). See the disclosed,
SEPARATE and more important reservation about amendment-diff completeness
below and in known_unresolved_discrepancies
(privatization_regulation_amendment_diff_partial) -- TIER_1 describes the
strength of the CURRENT text's source, not exhaustive certainty about which
individual articles among the 140 "اصلية"-labelled ones might carry an
undetected wording tweak from the 2023 amendment.

169 records: 140 اصلية, 19 معدلة, 10 مضافة, 0 ملغاة. Structural comparison of
the 2021 (159-article) vs 2024 (169-article) texts precisely located ALL 10
net-new articles (66, 72, 80, 81, 82, 89, 104, 141, 155, 158) via book/chapter
article-count deltas cross-checked with direct content comparison (not count
alone). 19 further articles (15, 23, 30, 32, 33, 34, 49, 64, 67, 71, 75, 76,
79, 84, 85, 86, 87, 88, 135) were confirmed AMENDED via direct old-vs-new
content comparison (numeric period changes, terminology harmonisation,
added/reorganised clauses) -- see each article's "history" entry for specifics
and article_key
privatization_regulation_amendment_diff_partial for the honest disclosure that
a full exhaustive word-for-word diff of all 169 articles was NOT completed
(the only available pre-amendment full text is the letter-transposition-
corrupted argaam PDF, and the scale made exhaustive reconciliation
impractical this pass): "اصلية" on the remaining 140 articles means "not
identified as changed in the checks performed" (full structural check + a
representative direct-comparison sample spanning all 8 books), not an
exhaustive confirmed-unchanged guarantee.

STRUCTURE: 8 أبواب (books), 7 of which are further divided into فصول
(chapters); Book 7 (العروض التلقائية, arts. 142-148) has NO فصول -- its
articles are direct children of the book. No مكرر (repeated) article numbers.
Article (165)'s header is missing the colon present on all 168 other headers
in the official source itself -- preserved as published, not corrected.

DISAMBIGUATION (binding, see task caveat): this Regulation is DISTINCT from
(1) the Privatization Law itself (Royal Decree M/63 -- sources/privatization,
a separate track), (2) the "Organizing Rules" (القواعد المنظمة للتخصيص,
Council of Ministers Resolution 114, 14/2/1443H -- a separate Article-2
instrument defining the competent/executing authorities, NOT built here), and
(3) the NCP's own organizational statute (تنظيم المركز الوطني للتخصيص). This
Regulation's own Article 1 defines "الجهة المختصة"/"الجهة التنفيذية" by
cross-reference to "القواعد المنظمة" (not to itself) -- internal textual
confirmation the two instruments are independent.

TASHKEEL: partial harakat (145 of 169 articles) and decorative in-word tatweel
were present in the source HTML; both are stripped/normalised uniformly for
consistency with this corpus's majority (tatweel is preserved only in the
"هـ" list-marker/Hijri-marker sequence). Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "privatization_regulation", "law", "official_source",
                   "privatization_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "privatization_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "privatization_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "privatization_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "privatization_regulation_arabic_legal_llm",
                        "privatization_regulation_legal_llm_001_169.json")

LAW_ID = "sa-privatization-regulation-ncp-1-4-2023"
LAW_AR = "اللائحة التنفيذية لنظام التخصيص"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_ADDED_DATED = "ADDED_DATED"
KEY_RE = r"privatization_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم التخصيص المركز الجهة الجهاز").split())


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


def _top_status(ls):
    if ls == "معدلة":
        return STATUS_AMENDED_DATED
    if ls == "مضافة":
        return STATUS_ADDED_DATED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; governing text fetched DIRECTLY and LIVE from the Official "
                "Gazette (uqn.gov.sa/details?p=24451, HTTP 200, browser User-Agent required) -- "
                "the current, amended, consolidated 169-article text (NCP Board Decision "
                "1/4/2023, 18/6/1445H = 31 Dec 2023G; gazette-published 21/7/1445H = 2 Feb "
                "2024G). No secondary aggregator, no OCR. The pre-amendment 159-article text "
                "(NCP Board Decision Q-9/2021) was used ONLY for structural/content comparison "
                "via an argaam.com-hosted official PDF that exhibits the same pdftotext "
                "letter-transposition artifact documented for this corpus's base Privatization "
                "Law PDF source -- never adopted as governing text. 10 articles are confirmed "
                "ADDED (66,72,80,81,82,89,104,141,155,158) and 19 further articles confirmed "
                "AMENDED via direct old-vs-new comparison; the remaining 140 are اصلية in the "
                "sense of 'not identified as changed in the checks performed' -- NOT an "
                "exhaustive word-for-word guarantee (see "
                "privatization_regulation_amendment_diff_partial in "
                "known_unresolved_discrepancies). This Regulation is DISTINCT from the "
                "Privatization Law itself, from the separate 'Organizing Rules' (القواعد "
                "المنظمة للتخصيص, CoM Resolution 114), and from the NCP's own organizational "
                "statute -- see known_unresolved_discrepancies for full disambiguation.")
    gov_note_ar = ("العربية هي اللغة الحاكمة؛ جُلب النص الحاكم مباشرة وحيا من الجريدة الرسمية "
                   "(uqn.gov.sa/details?p=24451، HTTP 200) -- النص المعدّل الحالي (169 مادة، "
                   "قرار مجلس إدارة المركز 1/4/2023 وتاريخ 18/6/1445هـ، نُشر 21/7/1445هـ) دون "
                   "أي مجمّع ثانوي أو OCR. اعتُمد نص اللائحة الأصلية (159 مادة، قرار ق-9/2021) "
                   "للمقارنة الهيكلية/المحتوى فقط عبر ملف PDF من argaam.com يحمل عيب انقلاب "
                   "الحروف ذاته الموثق لملف نظام التخصيص الأساسي، ولم يُعتمد كنص حاكم إطلاقا. "
                   "10 مواد مؤكدة الإضافة، و19 مادة أخرى مؤكدة التعديل بمقارنة مباشرة؛ الباقي "
                   "(140 مادة) اصلية في حدود ما فُحص فقط -- انظر التحفظ المفصل في "
                   "known_unresolved_discrepancies. هذه اللائحة مستقلة عن نظام التخصيص ذاته "
                   "وعن القواعد المنظمة للتخصيص وعن تنظيم المركز الوطني للتخصيص.")

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
        top_status = _top_status(ls)
        ver.append({"law_key": "privatization_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PRIVATIZATION_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "book_label_ar": a.get("book_label_ar"),
                    "book_title_ar": a.get("book_title_ar"),
                    "chapter_label_ar": a.get("chapter_label_ar"),
                    "chapter_title_ar": a.get("chapter_title_ar"),
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "renumbered_from_2021_article": a.get("renumbered_from_2021_article"),
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "book_title_ar": a.get("book_title_ar"),
                    "chapter_title_ar": a.get("chapter_title_ar"),
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "renumbered_from_2021_article": a.get("renumbered_from_2021_article"),
                    "record_id": "privatization-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "privatization_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام التخصيص" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("NCP Board Decision 1/4/2023 (18/6/1445H "
                                                          "= 31 Dec 2023G), gazette-published "
                                                          "21/7/1445H = 2 Feb 2024G -- full text "
                                                          "fetched directly and live from "
                                                          "uqn.gov.sa (Official Gazette itself, "
                                                          "HTTP 200), no secondary aggregator, no "
                                                          "OCR; independently corroborated by "
                                                          "ajel.sa's article-count confirmation "
                                                          "(169 مادة) and argaam.com/alarabiya.net "
                                                          "coverage; laws.boe.gov.sa unreachable "
                                                          "this pass (connection reset), no known "
                                                          "dedicated lawId page for NCP board "
                                                          "decisions; web.archive.org org-policy "
                                                          "blocked, not bypassed"),
                                     "source_authority_ar": gov_note_ar,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "privatization_regulation",
               "layer": "PRIVATIZATION_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-privatization-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (169 مادة؛ 140 أصلية، 19 معدلة، 10 مضافة)",
               "title_en": "Implementing Regulation of the Privatization Law -- Arabic LLM-ready layer "
                           "(169 records: 140 original, 19 amended, 10 added)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 169], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Privatization Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
