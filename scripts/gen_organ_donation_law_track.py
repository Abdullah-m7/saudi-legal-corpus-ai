#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Human Organ Donation Law track (نظام التبرع بالأعضاء
البشرية, Royal Decree M/70, 19/8/1442H -- the currently in-force Human Organ
Donation Law, administered by the Saudi Center for Organ Transplantation (SCOT,
scot.gov.sa), a center affiliated with the Saudi Health Council).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It was
built from scratch this pass. This corpus already tracks health_system_law /
healthcare_professions_law; those were NOT touched by this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام التبرع بالأعضاء البشرية is a single,
self-standing Royal-Decree law (M/70, 19/8/1442H, approving Council of Ministers
Resolution No. 468 dated 17/8/1442H / 30 March 2021G), confirmed via cross-checked
independent signals: (1) laws.boe.gov.sa carries it under its own dedicated lawId
4a16fbc8-7f1d-4647-8acc-ad0900d849c2 (seen repeatedly via WebSearch); (2)
saudipedia.com (an independent secondary encyclopedia, fetched HTTP 200 directly)
independently confirms the same decree date (19 Shaban 1442H / 1 April 2021G), the
same CoM resolution date (17 Shaban 1442H / 30 March 2021G -- matching the task
brief given BEFORE this research pass began), the 27-article count, and the same
topic list; (3) ar.wikipedia.org (fetched HTTP 200 directly) confirms SCOT is a
center affiliated with the Saudi Health Council, founded 1404H/1984 as the
National Kidney Center and renamed 1413H/1993 by CoM Resolution 80 -- consistent
with the Law's own Article 1 definitions of "the Council" / "the Chairman" / "the
Center" / "the Director-General".

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY source)
was checked FIRST per standard methodology but is unreachable this pass: repeated
direct curl attempts (full browser headers, HTTP/1.1 explicit, including a probe
of the bare portal homepage, not just this law's page) all returned "Connection
reset by peer" at the TLS handshake stage. web.archive.org was ALSO explicitly
attempted this pass via TWO different tools: a direct curl to a confirmed-existing
Wayback snapshot (per the archive.org "available" API) returned "Blocked by egress
policy" verbatim, and the WebFetch tool independently returned "Claude Code is
unable to fetch from web.archive.org" for the same snapshot -- a double
confirmation (two different tools) that the archive is blocked this session, not
circumvented further. The full verbatim Arabic text of all 27 articles was
extracted from ONE full-text aggregator, nezams.com (a clean born-digital HTML
page, HTTP 200 -- no scan/OCR/ligature defects; this is the SAME aggregator this
corpus already used, and disclosed as TIER_3, for the waste_management_law
track). Every governing metadata fact and the 27-article count are self-consistent
within that one source and independently cross-checked for identity against
saudipedia.com (which reproduces near-verbatim wording for at least Article 3 and
the Article 21 penalty amounts -- a textual cross-check, not merely a metadata
match) and ar.wikipedia.org (SCOT identity). A follow-up re-verification of the
verbatim text against laws.boe.gov.sa is recommended once reachable.

27 articles, NO chapters/فصول (a self-check search for the word "الفصل" across the
entire source page returned zero hits -- the Law is a single flat sequence of
Articles 1-27); all 27 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no
amendments per nezams.com: "لم يجرى عليه تعديل"). Diacritics (tashkeel) are
stripped uniformly for consistency with this corpus's other nezams.com-sourced
tracks; partial tashkeel was present in 20 of the 27 raw articles (plus the Royal
Decree preamble and CoM Resolution text) before normalization. The source's own
preamble contains an evident typo ("1441هأ" instead of "1441هـ") which is
preserved VERBATIM in preamble_ar (not silently corrected) -- see
known_unresolved_discrepancies.

SUPERSESSION -- UNLIKE waste_management_law (which replaces a specifically-named
predecessor law inside its own Article 37), this Law's final Article
(27, paragraph 2) carries only a GENERIC, unnamed repeal clause: "يلغي النظام كل
ما يتعارض معه من أحكام." No specific predecessor law is named anywhere in the
text, and no independent evidence of a prior dedicated Saudi organ-donation
statute was found via WebSearch this pass (an absence-of-evidence finding, not
proof of absence -- disclosed, not asserted as fact).

IMPLEMENTING REGULATION -- its EXISTENCE is confirmed via multiple independent
secondary references this pass (lexismiddleeast.com's ministerial-decision page
title referencing decision "4-29425"/1443H; a matching uqn.gov.sa Umm Al-Qura
gazette listing; qanoniah.com's file listing; MOH/istitlaa e-participation
project pages for its draft), but its full verbatim text was NOT retrieved this
pass: uqn.gov.sa's specific article page is a single-page-application that serves
only the site shell on direct fetch (no article content in the raw HTML) and
returned HTTP 503 via WebFetch; lexismiddleeast.com returned HTTP 404 on direct
fetch via both curl and WebFetch; qanoniah.com's viewer is a subscription-gated
Nuxt.js SPA requiring an API call whose endpoint could not be determined within
reasonable effort this pass. Flagged as a follow-up candidate track
(organ_donation_law_regulation, law_component "regulation"); the task-brief date
of 21/2/1443H for this Regulation was NOT independently confirmed this pass and is
NOT asserted as fact here -- see known_unresolved_discrepancies.

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "organ_donation_law", "law", "official_source",
                   "organ_donation_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "organ_donation_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "organ_donation_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "organ_donation_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "organ_donation_law_arabic_legal_llm",
                        "organ_donation_law_legal_llm_001_027.json")

LAW_ID = "sa-organ-donation-law-m70-1442"
LAW_AR = "نظام التبرع بالأعضاء البشرية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"organ_donation_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير المركز الجهة المتبرع المتبرعة").split())


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
        ver.append({"law_key": "organ_donation_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ORGAN_DONATION_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Human Organ Donation Law (Royal Decree M/70, "
                                              "19/8/1442H), a brand-new base-law track built "
                                              "from scratch this pass (not previously in this "
                                              "corpus). The Law has NO chapter/فصل structure "
                                              "(self-checked: zero hits for 'الفصل' across the "
                                              "source page) -- a flat sequence of 27 articles. "
                                              "Article 27(2) carries only a GENERIC unnamed "
                                              "repeal clause (no specific predecessor law is "
                                              "named, unlike waste_management_law's Article "
                                              "37). laws.boe.gov.sa was checked FIRST per "
                                              "standard methodology but unreachable this pass "
                                              "(TLS connection reset on repeated attempts, "
                                              "including the bare portal homepage); "
                                              "web.archive.org was also explicitly attempted "
                                              "via TWO different tools (direct curl and "
                                              "WebFetch) and BOTH independently confirmed the "
                                              "archive is blocked this session. The verbatim "
                                              "text of all 27 articles was extracted from "
                                              "nezams.com (a single clean born-digital HTML "
                                              "aggregator, no scan/OCR/ligature defects). "
                                              "Governing metadata and content are cross-checked "
                                              "for identity -- including near-verbatim textual "
                                              "overlap for Article 3 and the Article 21 penalty "
                                              "amounts, not merely metadata -- against "
                                              "saudipedia.com and ar.wikipedia.org (SCOT "
                                              "identity). TIER_3. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- "
                                              "notably that the Implementing Regulation's full "
                                              "text (Article 26 mandate) was NOT retrieved this "
                                              "pass despite its existence being confirmed via "
                                              "multiple independent secondary references."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "organ-donation-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "organ_donation_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام التبرع بالأعضاء البشرية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/70), 19/8/1442H "
                                                          "(Council of Ministers Resolution 468, "
                                                          "17/8/1442H / 30 March 2021G; Shura "
                                                          "Resolutions 215/54 (17/1/1441H) and "
                                                          "24/4 (15/4/1442H)) — the currently "
                                                          "in-force Human Organ Donation Law, "
                                                          "with NO chapter structure and NO "
                                                          "named predecessor law (Article 27(2) "
                                                          "is a generic unnamed repeal clause "
                                                          "only). Verbatim text from nezams.com "
                                                          "(single full-text aggregator; "
                                                          "laws.boe.gov.sa and web.archive.org "
                                                          "both confirmed unreachable this pass "
                                                          "via two different tools); all "
                                                          "metadata and the 27-article count "
                                                          "cross-verified for identity, "
                                                          "including near-verbatim textual "
                                                          "overlap, against saudipedia.com and "
                                                          "ar.wikipedia.org. TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/70) وتاريخ 19/8/1442هـ (قرار مجلس الوزراء رقم (468) وتاريخ 17/8/1442هـ، الموافق 30 مارس 2021م؛ قرارا مجلس الشورى رقم (215/54) وتاريخ 17/1/1441هـ ورقم (24/4) وتاريخ 15/4/1442هـ) — نظام التبرع بالأعضاء البشرية النافذ حالياً، بلا فصول وبلا نظام سابق مسمى (الفقرة 2 من المادة السابعة والعشرين حكم إلغاء عام غير مسمى فقط). النص الحرفي من nezams.com (مصدر نص كامل واحد؛ laws.boe.gov.sa وweb.archive.org كلاهما مؤكَّد تعذر الوصول إليهما هذه الجولة عبر أداتين مختلفتين)؛ وجميع البيانات الوصفية وعدد المواد (27) متقاطعة هوياتياً، بما في ذلك تطابق نصي شبه حرفي، عبر saudipedia.com وar.wikipedia.org. المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "organ_donation_law",
               "layer": "ORGAN_DONATION_LAW_ARABIC_VERIFIED_TEXT",
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
               "chapter_structure": src.get("chapter_structure", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-organ-donation-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (27 مادة؛ 27 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Saudi Arabian Human Organ Donation Law (Royal Decree M/70, "
                            "19/8/1442H) — Arabic LLM-ready layer (27 records: 27 original, 0 "
                            "amended, 0 added, 0 repealed; no chapters)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 27], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Human Organ Donation Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
