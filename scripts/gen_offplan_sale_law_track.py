#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Off-Plan Sale and Lease of Real Estate Projects Law
track (نظام بيع وتأجير مشروعات عقارية على الخارطة -- "برنامج وافي" / the "WAFI"
program, Royal Decree M/44, 10/3/1445H -- the currently in-force off-plan real
estate law, administered by the General Real Estate Authority (REGA) via its own
Implementing Regulation).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It was
built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام بيع وتأجير مشروعات عقارية على الخارطة
is a single, self-standing, flat (chapter-less) Royal-Decree law of 30 articles.
Unlike several other tracks in this corpus, the PRIMARY official source (Umm
Al-Qura Gazette, uqn.gov.sa) was directly and successfully reached this pass:
uqn.gov.sa/details?p=24326 carries the issuing Royal Decree's own text (title tag
confirms "مرسوم ملكي رقم (م/44) وتاريخ 10 /03 /1445هـ"), and the immediately
adjacent gazette item uqn.gov.sa/details?p=24327 (found by systematic probing
once it became clear p=24326 held only the decree preamble, not the Law's
articles) carries the Law's own title and its full 30 articles verbatim, parsed
directly out of the page's <article id="article-content"> element. Cross-checked
for near-verbatim identity against two independent secondary aggregators:
qanoonsa.com (qanoonsa.com/p/501403/, HTTP 200) and nezams.com (HTTP 200) -- both
carry the same 30 articles with only cosmetic differences (Arabic-Indic vs.
Western digit rendering, one stray aggregator-added footer line, minor tashkeel
variance). laws.boe.gov.sa (this corpus's usual primary source) carries its own
dedicated lawId (99613e6a-6b85-423c-87af-b0ec00b4633e, confirmed via WebSearch)
but the live portal was unreachable this pass (WebFetch HTTP 503; direct curl
"Connection reset by peer") -- same failure class documented in other tracks of
this corpus (e.g. waste_management_law).

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. The primary
official government gazette (Umm Al-Qura, the actual original publishing organ
of Saudi law) was reached directly and used as the governing text for the
preamble and all 30 articles, cross-verified against two independent secondary
aggregators with no substantive divergence. This does not rise to TIER_1 because
a second official source's CONTENT could not be confirmed this pass: BOE's
portal is unreachable, and REGA's own official PDF of the Law
(rega.gov.sa/media/ledpb1jo/, HTTP 200, 14 pages) turned out to be scanned
images with no text layer (pdftotext empty, pdffonts empty, pdfimages confirms
JPEG-per-page); an Arabic OCR pass (tesseract, 300dpi, psm 6) was attempted as an
independent second-official-source check but did not complete in reasonable
time this pass due to heavy shared-resource contention on this build host
(dozens of concurrent tesseract/pdftoppm processes from unrelated sessions were
observed via ps aux). REGA's copy is therefore only identity-confirmed (same
title, same administering authority), not text-verified, this pass.

30 articles, flat structure (no chapters/فصول, no أبواب); all 30 اصلية; 0 معدلة,
0 ملغاة, 0 مضافة (in force, no amendments per nezams.com: "لم يجرى عليه تعديل").
Diacritics (tashkeel) are stripped uniformly for consistency with this corpus's
other BOE-family tracks; uqn.gov.sa itself carried partial/uneven tashkeel on 22
of the 30 articles (e.g. "المبيّنة", "يقتضِ"). The source uses ONLY Western
digits throughout the article bodies (no mixed Arabic-Indic/Western rendering to
disclose).

SUPERSESSION -- unlike waste_management_law (explicit named repeal inside a
numbered article), Article 29 here carries only a GENERAL repeal clause ("يلغي
النظام كل ما يتعارض معه من أحكام") naming no specific predecessor instrument.
The issuing Council of Ministers Resolution's own preamble (sourced from
nezams.com only) references an earlier administrative framework -- CoM
Resolution No. (536), 4/12/1437H, "الضوابط المتعلقة ببيع أو تأجير وحدات عقارية
على الخارطة" -- that this Law appears to supersede in practice, but this is
recorded as interpretive context only (see supersedes_ar), not a confirmed
numbered-article repeal.

IMPLEMENTING REGULATION -- identified AND independently gazetted in its own
right (uqn.gov.sa/details?p=24924, fetched HTTP 200 this pass): General Real
Estate Authority (REGA) Board Resolution No. (Q/M/I/H/8/2024/T) dated
20/10/1445H, 49 articles. NOT built as a track this pass (base-law priority per
task scope); flagged as a follow-up candidate (offplan_sale_law_regulation,
law_component "regulation") with a citation already confirmed directly from a
primary gazette source.

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "offplan_sale_law", "law", "official_source",
                   "offplan_sale_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "offplan_sale_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "offplan_sale_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "offplan_sale_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "offplan_sale_law_arabic_legal_llm",
                        "offplan_sale_law_legal_llm_001_030.json")

LAW_ID = "sa-offplan-sale-law-m44-1445"
LAW_AR = "نظام بيع وتأجير مشروعات عقارية على الخارطة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"offplan_sale_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الجهة المختصة المشروع العقاري المطور").split())


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
        ver.append({"law_key": "offplan_sale_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "OFFPLAN_SALE_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this is the currently in-force "
                                              "Off-Plan Sale and Lease of Real Estate Projects Law "
                                              "(Royal Decree M/44, 10/3/1445H, \"WAFI\" program), a "
                                              "brand-new base-law track built from scratch this pass "
                                              "(not previously in this corpus). Flat structure, no "
                                              "chapters. Full verbatim text of all 30 articles "
                                              "extracted directly from the primary official Umm "
                                              "Al-Qura Gazette (uqn.gov.sa/details?p=24327), "
                                              "cross-checked near-verbatim against two independent "
                                              "secondary aggregators (qanoonsa.com, nezams.com). "
                                              "laws.boe.gov.sa identity confirmed but unreachable "
                                              "this pass; REGA's own official PDF copy is scanned "
                                              "images only, OCR cross-check attempted but did not "
                                              "complete this pass due to shared-resource contention. "
                                              "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "offplan-sale-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "offplan_sale_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام بيع وتأجير مشروعات عقارية على الخارطة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/44), 10/3/1445H "
                                                          "(Council of Ministers Resolution 196, "
                                                          "4/3/1445H; Shura Council Resolutions "
                                                          "306/45, 28/11/1443H and 184/25, "
                                                          "28/8/1444H) — the currently in-force "
                                                          "Off-Plan Sale and Lease of Real Estate "
                                                          "Projects Law (\"WAFI\" program). Verbatim "
                                                          "text from the primary Umm Al-Qura Gazette "
                                                          "(uqn.gov.sa), cross-checked against two "
                                                          "independent secondary aggregators "
                                                          "(qanoonsa.com, nezams.com). "
                                                          "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/44) وتاريخ 10/3/1445هـ (قرار مجلس الوزراء رقم 196 وتاريخ 4/3/1445هـ؛ قرارا مجلس الشورى رقم 306/45 وتاريخ 28/11/1443هـ ورقم 184/25 وتاريخ 28/8/1444هـ) — نظام بيع وتأجير مشروعات عقارية على الخارطة (برنامج وافي) النافذ حالياً. النص الحرفي من جريدة أم القرى الرسمية (uqn.gov.sa)، مدقق مقابل مصدرين ثانويين مستقلين (qanoonsa.com، nezams.com). المستوى TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "offplan_sale_law",
               "layer": "OFFPLAN_SALE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-offplan-sale-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ 30 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Off-Plan Sale and Lease of Real Estate Projects Law (Royal Decree "
                            "M/44, 10/3/1445H, \"WAFI\" program) — Arabic LLM-ready layer (30 records: "
                            "30 original, 0 amended, 0 added, 0 repealed; flat structure, no chapters)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Off-Plan Sale Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
