#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the "Regulation on Transfer of Personal Data Outside the Kingdom"
track (لائحة نقل البيانات الشخصية إلى خارج المملكة), issued by decision of the
President of the Saudi Data and AI Authority (SDAIA) No. (1840), dated
27/2/1446H (published in the Umm al-Qura Official Gazette 28/2/1446H, 1
September 2024), pursuant to Article (29) of the Personal Data Protection Law
(PDPL, Royal Decree M/19, 9/2/1443H) -- specifically subparagraph (d) of
paragraph (1), subparagraphs (b) and (c) of paragraph (2), and the general
delegation in paragraph (4).

This is a NEW, DISTINCT PDPL-family track, separate from both:
  - pdpl_law (the PDPL itself, 43 articles, Royal Decree M/19) and
  - pdpl_implementing_regulation (the PDPL's general Implementing Regulation,
    38 articles),
already present in this corpus. The only overlap is a cross-reference: this
Regulation's Article 5 explicitly cites "Article (17) of the Implementing
Regulation of the Law" for subsequent-transfer rules -- confirming these are
complementary, non-duplicate instruments.

CAPTURED SCOPE: FULL -- all 9 articles of the current (Version 2.0, August
2024, per SDAIA's own official English-language PDF cover page) regulation are
ingested. The regulation has NO chapter/section subdivisions (a flat
9-article structure), unlike its 2023 predecessor (see below).

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE (dual independent OFFICIAL
source, no unresolved reachability gap):
  (1) dgp.sdaia.gov.sa -- SDAIA's own live regulatory portal (the issuing
      authority's site), fetched directly this pass (HTTP 200), containing
      the full Arabic text of all 9 articles.
  (2) uqn.gov.sa -- the Umm al-Qura Official Gazette (a separate government
      publishing authority), fetched directly this pass (HTTP 200, both the
      rendered page and its own /api/article/19307/json endpoint), containing
      the identical full Arabic text PLUS the decree number (1840) and date
      (27/2/1446H) that the live SDAIA portal page itself does not display.
  Both official sources agree WORD FOR WORD on the substantive text (an
  initial HTML-stripping artifact made the SDAIA portal capture look
  unnumbered where the gazette capture showed explicit "1-/2-/.../أ-/ب-"
  paragraph numbering; this was a lossy extraction defect in that one
  scrape -- not a real difference between the sources -- resolved by using
  the fully-numbered Umm al-Qura Gazette text as the governing capture).
  Structural (non-governing) corroboration: SDAIA's own official English PDF
  (dgp.sdaia.gov.sa, 8 pages) explicitly labels the document "Version 2.0,
  August 2024" and lists all 9 articles matching topic-for-topic -- used only
  to confirm the version label and article count, never to correct Arabic
  text. Independent secondary corroboration: aunklaw.com (a Saudi law firm)
  reproduces the identical Arabic text verbatim, including decree 1840 /
  27-2-1446H.
laws.boe.gov.sa was checked FIRST per this corpus's standard methodology but
was unreachable this pass (TCP connection reset); whether it carries a
dedicated lawId page for this authority-level (not royal-decree) regulation
was not independently confirmed either way.

V1.0 PREDECESSOR (2023) -- FOUND, PARTIALLY CONFIRMED. A structurally very
different predecessor, "لائحة نقل البيانات الشخصية خارج المملكة" (note: no
"إلى"), 10 articles across 4 chapters, was independently confirmed via direct
fetch of its own Umm al-Qura Gazette record (uqn.gov.sa/details?p=23597,
published 1445-2-22H / 7 Sept 2023, gazette sub-section "Council of
Ministers"). ITS OWN decree number/date could NOT be independently confirmed
this pass: a single AI-synthesized web-search answer once surfaced "Decision
No. 1517/1445, 20/2/1445H", but a follow-up search could not corroborate that
figure from any retrievable document, and neither directly-fetched gazette
capture (2023 or 2024) contains it -- so it is NOT asserted as fact (see
known_unresolved_discrepancies). No directly-read repeal/supersession clause
was found in either gazette capture (both start directly at the substantive
articles, with no preamble/diba visible in the captured page this pass); the
conclusion that v2.0 supersedes v1.0 rests on strong circumstantial evidence
(same subject and issuer, structurally incompatible provisions, universal
secondary-source description as an "update/amendment", and SDAIA's own
English PDF calling itself "Version 2.0") rather than an explicit repeal
clause -- this is disclosed as an inference, not asserted as directly
confirmed. The 2023 predecessor's text is NOT ingested in this track (out of
scope; recorded only as a disclosed supersession candidate).

Diacritics (tashkeel), tatweel, and zero-width formatting characters
(ZWNJ/ZWJ/RLM/LRM) are stripped uniformly for consistency with this corpus's
other PDPL-family tracks. Arabic governs; no translation, paraphrase, or
interpretation was performed on the Arabic text, and the English (SDAIA's own
PDF) text was NOT used to correct any Arabic character -- only to confirm the
non-governing version label and article count. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "pdpl_cross_border_transfer_regulation", "law",
                    "official_source", "pdpl_cross_border_transfer_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "pdpl_cross_border_transfer_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "pdpl_cross_border_transfer_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "pdpl_cross_border_transfer_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "pdpl_cross_border_transfer_regulation_arabic_legal_llm",
                        "pdpl_cross_border_transfer_regulation_legal_llm_001_009.json")

LAW_ID = "sa-pdpl-cross-border-transfer-regulation-1840-1446"
LAW_AR = "لائحة نقل البيانات الشخصية إلى خارج المملكة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"pdpl_cross_border_transfer_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الجهة المختصة النظام البيانات الشخصية نقل خارج المملكة").split())


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

    governing_note = (
        "Arabic governs. FULL SCOPE: all 9 articles of the current (Version 2.0, "
        "August 2024) regulation. PRIMARY TEXT source is the Umm al-Qura Official "
        "Gazette (uqn.gov.sa/details?p=25412), independently corroborated word-for-"
        "word by SDAIA's own live regulatory portal (dgp.sdaia.gov.sa) -- two "
        "separate government sources in full agreement, no reachability gap "
        "(TIER_1_PRIMARY_MULTI_SOURCE). Structurally cross-checked (article count "
        "and version label only, never used to correct Arabic wording) against "
        "SDAIA's own official English PDF, which labels the document 'Version 2.0, "
        "August 2024'. laws.boe.gov.sa was checked first but was unreachable this "
        "pass (TCP connection reset). A 2023 predecessor with a materially "
        "different 10-article/4-chapter structure was found and is disclosed as a "
        "strongly-inferred (not directly-read) supersession candidate -- see the "
        "source artifact's supersedes_predecessor_v1 and "
        "known_unresolved_discrepancies for full disclosure, including an "
        "unconfirmed candidate decree number for that predecessor that is NOT "
        "asserted as fact.")

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
        ver.append({"law_key": "pdpl_cross_border_transfer_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PDPL_CROSS_BORDER_TRANSFER_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": a.get("article_title_ar") or "",
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": governing_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"] + (": " + a["article_title_ar"]
                                                                 if a.get("article_title_ar") else ""),
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "pdpl-cross-border-transfer-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s: %s" % (LAW_AR, a["number_label_ar"],
                                                      a.get("article_title_ar") or ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "pdpl_cross_border_transfer_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من لائحة نقل البيانات الشخصية إلى خارج المملكة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                                         "SDAIA President Decision No. (1840) (27/2/1446H) -- text via "
                                         "the Umm al-Qura Official Gazette (uqn.gov.sa), independently "
                                         "corroborated word-for-word by SDAIA's own live regulatory "
                                         "portal (dgp.sdaia.gov.sa); laws.boe.gov.sa unreachable this "
                                         "pass. FULL SCOPE = all 9 articles of Version 2.0 (August "
                                         "2024)."),
                                     "source_authority_ar": ("قرار رئيس الهيئة السعودية للبيانات "
                                                             "والذكاء الاصطناعي رقم (1840) وتاريخ "
                                                             "27/2/1446هـ — النص من جريدة أم القرى "
                                                             "الرسمية، مؤكَّد حرفيا من بوابة سدايا "
                                                             "الحية؛ بوابة هيئة الخبراء غير قابلة "
                                                             "للوصول هذه الجولة. النطاق المُدرَج = جميع "
                                                             "المواد التسع (الإصدار 2.0، أغسطس 2024)."),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "pdpl_cross_border_transfer_regulation",
               "layer": "PDPL_CROSS_BORDER_TRANSFER_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "version_label": src.get("version_label", ""),
               "version_label_source_note": src.get("version_label_source_note", ""),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "publication": src.get("publication", {}),
               "pdpl_delegation_basis": src.get("pdpl_delegation_basis", {}),
               "supersedes_predecessor_v1": src.get("supersedes_predecessor_v1", {}),
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-pdpl-cross-border-transfer-regulation-arabic-legal-llm-full-1-9",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (النطاق الكامل: المواد 1-9، جميعها أصلية)",
               "title_en": ("Regulation on Transfer of Personal Data Outside the Kingdom — Arabic "
                            "LLM-ready layer (FULL SCOPE: all 9 articles, all original/current)."),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 9], "full_regulation_article_count": 9,
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Regulation on Transfer of Personal Data "
          "Outside the Kingdom records (full scope: Articles 1-9)" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
