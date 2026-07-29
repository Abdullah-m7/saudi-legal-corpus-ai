#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Pharmaceutical and Herbal Establishments Law track
(نظام المنشآت والمستحضرات الصيدلانية والعشبية, Royal Decree M/108, 22/8/1441H --
the currently in-force law governing licensing/operation of pharmacies, herbal-
preparation sale establishments, pharmaceutical/herbal manufacturing plants,
trading warehouses, scientific offices, and drug-consultation/analysis centers,
administered by the Saudi Food and Drug Authority (SFDA / الهيئة العامة للغذاء
والدواء)).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام المنشآت والمستحضرات الصيدلانية
والعشبية is a single, self-standing Royal-Decree law (M/108, 22/8/1441H, on
Council of Ministers Resolution 534, 21/8/1441H; Shura Council Resolution
99/24, 18/6/1441H). Confirmed via cross-checked independent sources: (1)
laws.boe.gov.sa carries it under its own dedicated lawId
3d191772-e60b-4925-b5e7-aba50097641f (per the task brief and WebSearch), but
was unreachable this pass (see TIER note below); (2) WIPO Lex
(wipo.int/wipolex/ar/legislation/details/20289) hosts an official Arabic PDF
of the Royal Decree/CoM Resolution/Law submitted directly by the Saudi
government (Bureau-of-Experts-at-the-Council-of-Ministers letterhead, King's
signature, official seals, National Center for Archives and Records
watermark, 13 pages) -- this PDF is the primary source used for this track;
(3) nezams.com (an independent secondary aggregator) confirms the 42-article
structure and full text; (4) WIPO Lex also independently hosts the repealed
predecessor law's own dedicated page
(wipo.int/wipolex/ar/legislation/details/8514: "نظام المنشآت والمستحضرات
الصيدلانية"، Royal Decree M/31, 1/6/1425H, 18 June 2004), corroborating the
identity/date of the instrument this Law repeals.

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT: Article 41 states
verbatim: "يحل هذا النظام محل نظام المنشآت والمستحضرات الصيدلانية، الصادر
بالمرسوم الملكي رقم (م/31) والتاريخ 1/ 6/ 1425هـ. ويلغي كل ما يتعارض معه من
أحكام." This is also confirmed by the Royal Decree's own preamble (clause 3),
which carves out an explicit TRANSITIONAL EXCEPTION to that general
supersession: the old Law's provisions specifically covering pharmacies
(الصيدلية) and herbal-preparation-sale establishments (منشأة بيع المستحضرات
العشبية) remain in force until dedicated provisions for those two facility
types are issued under the new Law.

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. laws.boe.gov.sa
was checked FIRST per standard methodology but is unreachable this pass
(direct curl: "Connection reset by peer"; WebFetch: "HTTP 503 Service
Unavailable"). ONE primary/official source was reached instead and used as
the governing text: WIPO Lex's officially-hosted PDF of the Royal Decree (see
above) -- all 13 pages were read visually, page-by-page, directly by the
assistant (a multimodal read of the rendered page images, since the PDF is
scanned/image-only with no extractable text layer and a tesseract-OCR
feasibility test on one page produced very poor-quality output full of
character/digit errors and was abandoned in favor of direct visual reading).
This full visual read was cross-verified word-for-word against nezams.com
(independent secondary aggregator): all 42 articles, the Royal Decree
preamble, and the CoM Resolution text matched, except SIX minor secondary-
source typos found in nezams.com only (Articles 9, 15, 31, 32, 33, 34, 39),
each corrected using the official PDF as the governing text -- see
verification_methodology_note and known_unresolved_discrepancies in the
source artifact for the full itemized list. No second independent OFFICIAL
source confirms the wording (the live BOE portal, which does have a
dedicated lawId for this Law, could not be reached this pass), so this track
is classified TIER_2, not TIER_1; re-checking laws.boe.gov.sa (live or via
web.archive.org) in a later pass could raise this to TIER_1.

42 articles; all 42 اصلية; 0 معدلة, 0 مضافة, 0 ملغاة (no chapter/فصل or باب
structure -- confirmed via a direct page-by-page visual review of the
official document finding no chapter/part headings anywhere). Per
nezams.com's own metadata ("لم يجرى عليه تعديل" -- no amendment has been
made to it) and an independent full-text programmatic scan (searching for
every occurrence of "المرسوم الملكي رقم" / "قرار مجلس الوزراء رقم" inside
each article body, which found a hit ONLY inside Article 41's own
supersession clause), no amendment has been enacted to date. A separate,
NOT-confirmed-enacted public consultation (istitlaa.ncc.gov.sa /
eparticipation.my.gov.sa) proposes amending the violations/penalties
articles (adding a "serious violation" concept and a warning/correction-
period mechanism) -- this is flagged as an unresolved, unenacted proposal in
known_unresolved_discrepancies and is NOT reflected anywhere in the operative
text stored here.

Diacritics (tashkeel/harakat) are stripped uniformly from all article text
for consistency with this corpus's other BOE-family law tracks. All Arabic-
Indic digits (٠-٩) inside sub-paragraph numbering and the two in-article
tables (Article 8's fee schedule; Article 12's profit-margin schedule) are
converted to Western digits, also for corpus-wide consistency; numbers
spelled out as words in parentheses (e.g. "(مائة وعشرين)") are left as-is
since they are not numerals.

Implementing Regulation (an official SFDA PDF dated 2020-12-28 was located at
sfda.gov.sa/sites/default/files/2025-05/SFDA28122020ee1.pdf) exists but was
NOT built as a separate track this pass (out of scope) -- flagged as a
follow-up candidate track (pharmaceutical_establishments_law_regulation,
law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "pharmaceutical_establishments_law", "law", "official_source",
                   "pharmaceutical_establishments_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "pharmaceutical_establishments_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "pharmaceutical_establishments_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "pharmaceutical_establishments_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "pharmaceutical_establishments_law_arabic_legal_llm",
                        "pharmaceutical_establishments_law_legal_llm_001_042.json")

LAW_ID = "sa-pharmaceutical-establishments-law-m108-1441"
LAW_AR = "نظام المنشآت والمستحضرات الصيدلانية والعشبية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"pharmaceutical_establishments_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس الرئيس الصيدلانية العشبية المستحضرات "
            "المنشأة المنشآت").split())


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
        ver.append({"law_key": "pharmaceutical_establishments_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PHARMACEUTICAL_ESTABLISHMENTS_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Pharmaceutical and Herbal Establishments Law "
                                              "(Royal Decree M/108, 22/8/1441H), a brand-new "
                                              "base-law track built from scratch this pass (not "
                                              "previously in this corpus). Article 41 OF THE LAW "
                                              "ITSELF states it replaces the System of "
                                              "Pharmaceutical Establishments and Preparations "
                                              "(M/31, 1/6/1425H), with a transitional carve-out "
                                              "(Royal Decree preamble, clause 3) keeping that old "
                                              "law's pharmacy/herbal-sales provisions temporarily "
                                              "in force. laws.boe.gov.sa was checked FIRST per "
                                              "standard methodology but unreachable this pass "
                                              "(connection reset; WebFetch HTTP 503). ONE primary "
                                              "source was reached instead and used as the "
                                              "governing text: WIPO Lex's officially-hosted PDF "
                                              "of the Royal Decree (Bureau of Experts letterhead, "
                                              "official seals, National Archives watermark, all "
                                              "13 pages read visually page-by-page by the "
                                              "assistant since the scan has no text layer and "
                                              "tesseract OCR quality was too poor to rely on), "
                                              "cross-verified word-for-word against nezams.com, "
                                              "which had six minor typos (Articles 9, 15, 31, 32, "
                                              "33, 34, 39) corrected here using the official PDF. "
                                              "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably "
                                              "an unconfirmed, not-yet-enacted public-consultation "
                                              "proposal to amend the violations/penalties "
                                              "articles, and the Implementing Regulation not "
                                              "being ingested this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "pharmaceutical-establishments-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "pharmaceutical_establishments_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المنشآت والمستحضرات الصيدلانية والعشبية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/108), 22/8/1441H "
                                                          "(Council of Ministers Resolution 534, "
                                                          "21/8/1441H; Shura Council Resolution "
                                                          "99/24, 18/6/1441H) — the currently "
                                                          "in-force Pharmaceutical and Herbal "
                                                          "Establishments Law, which by its own "
                                                          "Article 41 replaces the System of "
                                                          "Pharmaceutical Establishments and "
                                                          "Preparations (M/31, 1425H), subject to "
                                                          "a transitional carve-out for pharmacies "
                                                          "and herbal-sales establishments. "
                                                          "Verbatim text from a direct visual, "
                                                          "page-by-page read of WIPO Lex's "
                                                          "officially-hosted Royal Decree PDF "
                                                          "(Bureau of Experts letterhead, official "
                                                          "seals), cross-checked word-for-word "
                                                          "against nezams.com (six minor "
                                                          "secondary-source typos found and "
                                                          "corrected). laws.boe.gov.sa itself "
                                                          "unreachable this pass. "
                                                          "TIER_2_PRIMARY_SECONDARY_CROSS_"
                                                          "VERIFIED."),
                                     "source_authority_ar": ("المرسوم الملكي رقم (م/108) وتاريخ "
                                                             "22/8/1441هـ (قرار مجلس الوزراء رقم "
                                                             "534 وتاريخ 21/8/1441هـ؛ قرار مجلس "
                                                             "الشورى رقم 99/24 وتاريخ 18/6/1441هـ) "
                                                             "— نظام المنشآت والمستحضرات "
                                                             "الصيدلانية والعشبية النافذ حالياً، "
                                                             "الذي يحل -بنص المادة الحادية "
                                                             "والأربعين منه ذاتها- محل نظام "
                                                             "المنشآت والمستحضرات الصيدلانية "
                                                             "(م/31، 1425هـ)، مع استثناء انتقالي "
                                                             "للصيدلية ومنشأة بيع المستحضرات "
                                                             "العشبية. النص الحرفي من قراءة بصرية "
                                                             "مباشرة صفحة بصفحة لملف المرسوم "
                                                             "الملكي المستضاف رسمياً على WIPO Lex "
                                                             "(بترويسة هيئة الخبراء وأختامها "
                                                             "الرسمية)، متقاطع حرفياً مع "
                                                             "nezams.com (عُثر على ست هفوات "
                                                             "طباعية صغيرة صُححت). laws.boe.gov.sa "
                                                             "نفسه غير قابل للوصول هذه الجولة. "
                                                             "المستوى "
                                                             "TIER_2_PRIMARY_SECONDARY_CROSS_"
                                                             "VERIFIED."),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "pharmaceutical_establishments_law",
               "layer": "PHARMACEUTICAL_ESTABLISHMENTS_LAW_ARABIC_VERIFIED_TEXT",
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
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-pharmaceutical-establishments-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (42 مادة؛ 42 أصلية، "
                           "0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Saudi Arabian Pharmaceutical and Herbal Establishments Law "
                            "(Royal Decree M/108, 22/8/1441H) — Arabic LLM-ready layer (42 "
                            "records: 42 original, 0 amended, 0 added, 0 repealed; no chapter "
                            "structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 42], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Pharmaceutical and Herbal Establishments Law records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
