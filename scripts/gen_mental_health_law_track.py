#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Mental Health Care Law track (نظام الرعاية الصحية
النفسية, Royal Decree M/56, 20/9/1435H -- the currently in-force Mental Health
Care Law, administered by the Ministry of Health (MOH) through the General and
Local Mental Health Care Monitoring Councils).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass. This corpus already separately tracks
health_system_law/healthcare_professions_law -- neither of those was touched.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام الرعاية الصحية النفسية is a single,
self-standing Royal-Decree law (M/56, 20/9/1435H / 17 July 2014G, 30 articles,
no formal division into أبواب/فصول), confirmed via cross-checked independent
signals: (1) laws.boe.gov.sa carries it under its own dedicated lawId
107f22b5-81a2-47ee-84bc-a9a700f2907a (seen via WebSearch, the same URL supplied
in this pass's task); (2) saudipedia.com (an independent Saudi encyclopedia,
fetched HTTP 200 after following its redirect) independently confirms the
decree number/date, the 30-article count, and reproduces Article 4's
competency list in near-identical wording (misattributed there to "Article 3",
apparently an editorial numbering slip on saudipedia's part, not a wording
discrepancy); (3) moh.gov.sa (the administering ministry) hosts the
Implementing Regulation (3rd edition, 1442H/2021G, fetched directly, HTTP 200,
52 pages) whose cover page independently reproduces the same decree number and
date.

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY
source) was checked FIRST per standard methodology but is unreachable this
pass: a direct curl attempt (full browser headers, --cacert pointed at this
session's proxy CA bundle) returned "Connection reset by peer". A
web.archive.org attempt (a legitimate workaround, unlike sessions that skip it
entirely) returned a direct HTTP 403 (not retried, per this session's proxy
policy of not retrying 403/407). The full verbatim Arabic text of all 30
articles, plus the Royal Decree preamble and the Council of Ministers
Resolution No. (366) text, was extracted from ONE full-text aggregator,
nezams.com (a clean born-digital HTML page, HTTP 200 -- no scan/OCR/ligature
defects). Every governing metadata fact, the 30-article count, and -- critically
-- the verbatim wording of Article 4 are independently cross-checked against a
SECOND secondary source (saudipedia.com) and a THIRD official source
(moh.gov.sa, for the decree identity, though that PDF covers the Regulation,
not the Law's own articles). A follow-up re-verification of the verbatim text
against laws.boe.gov.sa is recommended once reachable.

UNRESOLVED AMENDMENT (Al-Riyadh newspaper) -- Al-Riyadh (alriyadh.com/1821370,
headline confirmed verbatim across multiple independent WebSearch hits:
"مجلس الوزراء يعدل نظام الرعاية الصحية النفسية.. و«الرياض» تكشف التفاصيل")
reports that the Council of Ministers approved an amendment to this Law,
apparently touching Article 4 (the General Monitoring Council's competencies).
The actual article text of that report could NOT be reached this pass by any
available method: direct curl (with the correct proxy CA bundle) shows a real
TLS handshake reaching alriyadh.com's own server (i.e. NOT proxy-intercepted)
that fails with "unable to get local issuer certificate" -- a broken/
incomplete certificate chain served by alriyadh.com itself, not a proxy block;
WebFetch returned HTTP 503 both directly and via a Wayback Machine mirror
attempt; and the r.jina.ai text-extraction proxy returned HTTP 403. Because no
verbatim replacement text could be obtained, Article 4 is NOT marked "معدلة"
and NOT rewritten -- it is retained with its original wording as confirmed
identically by nezams.com and saudipedia.com (both apparently predating the
reported amendment), per this corpus's policy that an honest "could not
confirm" beats a fabricated or guessed diff. See
known_unresolved_discrepancies: mental_health_law_alriyadh_com_amendment_
unconfirmed for full detail and a recommended follow-up.

30 articles, no أبواب/فصول (chapter_structure carries one entry, "بدون تقسيم
إلى أبواب أو فصول", mirroring this corpus's existing health_system_law
convention for a law of a similar style); all 30 اصلية; 0 معدلة, 0 ملغاة, 0
مضافة (nezams.com's own metadata states "لم يجرى عليه تعديل" -- consistent
with the fact that no verified amended text could be obtained this pass).
Diacritics (tashkeel, incl. tanwin) are stripped uniformly from the 30 numbered
articles for consistency with this corpus's other BOE-family/nezams.com-based
tracks; curly quotes in Article 3 are normalized to Arabic guillemets «»,
matching corpus convention. The Royal Decree preamble and Council of Ministers
Resolution text (preamble_ar / com_resolution_ar) are preserved EXACTLY as
rendered by nezams.com, including their partial tashkeel and their use of
Arabic-Indic digits for royal-order/resolution citations (disclosed, not
normalized -- see known_unresolved_discrepancies).

IMPLEMENTING REGULATION -- identified and directly fetched this pass
(moh.gov.sa, 3rd edition, 1442H/2021G, 52 pages) but NOT built as its own track:
pdftotext extraction showed the expected reversed-character-order artifact
common to RTL text embedded in PDFs not authored for text extraction, which
would require careful, page-by-page directional correction before any
article/clause-level text could be trusted. Given the base law's priority this
pass and the risk of introducing undetected corruption into a 24-section
regulatory text, it was NOT ingested. Flagged as a follow-up candidate track
(mental_health_regulation, law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation of the Arabic text.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mental_health_law", "law", "official_source",
                   "mental_health_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "mental_health_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "mental_health_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "mental_health_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "mental_health_law_arabic_legal_llm",
                        "mental_health_law_legal_llm_001_030.json")

LAW_ID = "sa-mental-health-law-m56-1435"
LAW_AR = "نظام الرعاية الصحية النفسية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"mental_health_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير المريض النفسي النفسية الرعاية الصحية").split())


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
        ver.append({"law_key": "mental_health_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "MENTAL_HEALTH_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Mental Health Care Law (Royal Decree M/56, "
                                              "20/9/1435H), a brand-new base-law track built from "
                                              "scratch this pass (not previously in this corpus). "
                                              "laws.boe.gov.sa was checked FIRST per standard "
                                              "methodology but unreachable this pass (connection "
                                              "reset); web.archive.org was also explicitly "
                                              "attempted and returned HTTP 403 (not retried). The "
                                              "verbatim text of all 30 articles was extracted from "
                                              "nezams.com (a single clean born-digital HTML "
                                              "aggregator, no scan/OCR/ligature defects), with "
                                              "governing metadata and Article 4's wording "
                                              "specifically cross-checked against saudipedia.com. "
                                              "TIER_3. Al-Riyadh newspaper reports an UNCONFIRMED "
                                              "Council of Ministers amendment to Article 4 that "
                                              "could not be reached this pass by any available "
                                              "method -- see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact (mental_health_law_alriyadh_com_amendment_"
                                              "unconfirmed) before relying on Article 4 of this "
                                              "track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "mental-health-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "mental_health_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الرعاية الصحية النفسية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/56), 20/9/1435H "
                                                          "(Council of Ministers Resolution 366, "
                                                          "10/9/1435H; Shura Council Resolutions "
                                                          "75/61 and 34/18) — the currently "
                                                          "in-force Mental Health Care Law. "
                                                          "Verbatim text from nezams.com (single "
                                                          "full-text aggregator; laws.boe.gov.sa "
                                                          "unreachable this pass, web.archive.org "
                                                          "returned HTTP 403); metadata and Article "
                                                          "4 wording cross-verified against "
                                                          "saudipedia.com. TIER_3. An UNCONFIRMED "
                                                          "Council of Ministers amendment to "
                                                          "Article 4 was reported by Al-Riyadh "
                                                          "newspaper but could not be verified this "
                                                          "pass -- see known_unresolved_"
                                                          "discrepancies."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/56) وتاريخ 20/9/1435هـ (قرار مجلس الوزراء رقم (366) وتاريخ 10/9/1435هـ؛ قرارا مجلس الشورى رقم (75/61) ورقم (34/18)) — نظام الرعاية الصحية النفسية النافذ حالياً. النص الحرفي من nezams.com (مصدر نص كامل واحد؛ laws.boe.gov.sa غير قابل للوصول هذه الجولة، وweb.archive.org أعاد HTTP 403)؛ البيانات الوصفية ونص المادة الرابعة متقاطعة مع saudipedia.com. المستوى TIER_3. أفادت صحيفة الرياض بتعديل غير مؤكَّد من مجلس الوزراء للمادة الرابعة تعذّر التحقق منه هذه الجولة -- انظر known_unresolved_discrepancies.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "mental_health_law",
               "layer": "MENTAL_HEALTH_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-mental-health-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ 30 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بدون تقسيم إلى أبواب أو فصول)",
               "title_en": ("The Saudi Arabian Mental Health Care Law (Royal Decree M/56, "
                            "20/9/1435H) — Arabic LLM-ready layer (30 records: 30 original, 0 "
                            "amended, 0 added, 0 repealed; no formal chapter/part division)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Mental Health Care Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
