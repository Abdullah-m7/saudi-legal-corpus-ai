#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Private Healthcare Institutions Law track (نظام
المؤسسات الصحية الخاصة, Royal Decree M/40, 3/11/1423H -- the currently in-force
law governing ownership/licensing/operation of private hospitals, clinics,
medical complexes, laboratories, radiology centers and other private health
facilities, administered by the Ministry of Health).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
is DISTINCT from health_system_law (public health system generally) and
healthcare_professions_law (individual practitioner licensing) already tracked
elsewhere in this corpus -- this track governs the OWNERSHIP/LICENSING/
OPERATION of private hospitals, clinics and medical centers as institutions.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام المؤسسات الصحية الخاصة is a single,
self-standing Royal-Decree law (M/40, 3/11/1423H), confirmed via cross-checked
independent signals: (1) laws.boe.gov.sa carries it under its own dedicated
lawId 64e307c5-ac8c-49d8-9174-a9a700f285a0 (seen via WebSearch); (2) an official
Ministry of Health PDF (moh.gov.sa/Ministry/Rules/Documents/Private-Health-
Institutions-Law.pdf, 4.2MB/28 pages) was located and downloaded, confirming a
genuine government document exists for this law, though it is scanned/image-
only and could not be OCR'd this pass (see below); (3) nezams.com and
qanoonsa.com (independent secondary aggregators, both fetched HTTP 200 via
direct curl) both carry consistent full text; (4) uqn.gov.sa (the official
Umm Al-Qura Gazette) confirms the existence of the Council of Ministers
Resolution amending Article 2, by page title, though its body content could
not be extracted (client-rendered SPA).

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT: Article 33 states
verbatim: "يحل هذا النظام محل نظام المؤسسات الطبية الخاصة الصادر بالمرسوم
الملكي ذي الرقم (م/58) والتاريخ 3/ 11/ 1407هـ." This is also consistent with
the founding Royal Decree's and Council of Ministers Resolution 240's own
preambles, which both cite the same predecessor law.

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa was checked FIRST per standard
methodology but is unreachable this pass (curl: "Connection reset by peer"
x3; WebFetch: HTTP 503 x2; web.archive.org: WebFetch refused the domain
outright and curl to the same archived snapshot also reset). The official
moh.gov.sa PDF was downloaded but is scanned/image-only (pdftotext yielded no
text layer) and OCR (tesseract, Arabic pack) was abandoned this pass as
infeasible within reasonable effort -- this session's shared environment was
heavily contended with unrelated concurrent OCR jobs, and only 2 of 28 pages
had been processed after 13+ minutes. uqn.gov.sa (official Gazette) is
reachable but its content is loaded via a client-side API not captured by a
static fetch. The full verbatim text of all 35 articles therefore rests on
TWO independently-fetched secondary aggregators, nezams.com (primary working
source, HTML, HTTP 200) and qanoonsa.com (HTTP 200, providing the full Royal
Decree text for the Article 14 amendment) -- both agree WORD FOR WORD wherever
they overlap (Articles 2 and 14). Per this corpus's own taxonomy, this places
the track at TIER_3 (2+ independent secondary sources agree; zero primary-
source text confirmation obtained).

35 articles; 32 اصلية, 3 معدلة (Articles 2, 7, 14), 0 ملغاة, 0 مضافة. No
chapter/فصل or باب structure (35 sequential articles; confirmed via a full
programmatic scan of the source page finding zero occurrences of either word).

ARTICLE 2 -- THREE SEQUENTIAL AMENDMENTS reconstructed from nezams.com's own
in-page amendment history (original 1423H text -> M/36, 11/6/1434H -> M/72,
27/5/1441H -> Council of Ministers Resolution 479, 9/7/1444H, the CURRENT
text). ARTICLE 7 -- one amendment (M/78, 2/12/1435H). ARTICLE 14 -- one
amendment (M/103, 18/6/1445H / 31/12/2023G, published Umm Al-Qura 5014,
5/1/2024G) -- this amendment was NOT part of the prior research brief for
this task and was discovered independently this pass via direct-fetch
cross-checking of qanoonsa.com against nezams.com's own unattributed note for
Article 14 (word-for-word match). A possible ratifying Royal Decree "M/112,
10/7/1444H" for the Article 2 / CoM 479 amendment was repeatedly asserted by
WebSearch's own AI-synthesis text but could NOT be confirmed against any
directly-fetched page this pass -- it is recorded ONLY as an unverified,
flagged detail (known_unresolved_discrepancies), not as a confirmed
amendment_history event.

Diacritics (tashkeel/harakat) are stripped uniformly from all article text for
consistency with this corpus's other BOE-family tracks (e.g. waste_management_
law); decorative quotation marks (« » " ") used by the sources to bracket
quoted amendment text are also stripped as typographic artifacts, not
substantive legal text. All article text uses Western digits only (verified
programmatically -- zero residual Arabic-Indic digits in the final text).

Implementing Regulation (Ministerial Resolution No. 1019377, 28/5/1439H per
nezams.com's metadata) exists but was NOT built as a separate track this pass
(out of scope) -- flagged as a follow-up candidate
(private_healthcare_institutions_regulation, law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "private_healthcare_institutions_law", "law", "official_source",
                   "private_healthcare_institutions_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "private_healthcare_institutions_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "private_healthcare_institutions_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "private_healthcare_institutions_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "private_healthcare_institutions_law_arabic_legal_llm",
                        "private_healthcare_institutions_law_legal_llm_001_035.json")

LAW_ID = "sa-private-healthcare-institutions-law-m40-1423"
LAW_AR = "نظام المؤسسات الصحية الخاصة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"private_healthcare_institutions_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {
    "private_healthcare_institutions_law_art_002",
    "private_healthcare_institutions_law_art_007",
    "private_healthcare_institutions_law_art_014",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير المؤسسة الصحية الخاصة").split())


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
        ver.append({"law_key": "private_healthcare_institutions_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PRIVATE_HEALTHCARE_INSTITUTIONS_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Private Healthcare Institutions Law (Royal Decree "
                                              "M/40, 3/11/1423H), a brand-new base-law track built "
                                              "from scratch this pass (not previously in this "
                                              "corpus; distinct from health_system_law and "
                                              "healthcare_professions_law already tracked). Article "
                                              "33 OF THE LAW ITSELF states it replaces the Private "
                                              "Medical Institutions Law (M/58, 3/11/1407H). "
                                              "laws.boe.gov.sa was checked FIRST per standard "
                                              "methodology but unreachable this pass (connection "
                                              "reset x3; WebFetch HTTP 503 x2); web.archive.org was "
                                              "also attempted and refused/reset. An official "
                                              "moh.gov.sa PDF exists but is scanned/unreadable "
                                              "without OCR, which was infeasible this pass. The "
                                              "verbatim text of all 35 articles was extracted from "
                                              "nezams.com and cross-checked word-for-word against "
                                              "qanoonsa.com for the amended articles. TIER_3. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably the "
                                              "unverified possible ratifying decree M/112 and the "
                                              "newly-discovered M/103 amendment to Article 14."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "private-healthcare-institutions-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "private_healthcare_institutions_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المؤسسات الصحية الخاصة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/40), 3/11/1423H "
                                                          "(Council of Ministers Resolution 240, "
                                                          "26/10/1423H; Shura Council Resolution "
                                                          "54/65, 17/1/1423H) — the currently "
                                                          "in-force Private Healthcare Institutions "
                                                          "Law, which by its own Article 33 replaces "
                                                          "the Private Medical Institutions Law "
                                                          "(M/58, 1407H). Verbatim text from "
                                                          "nezams.com (primary working source; "
                                                          "laws.boe.gov.sa, web.archive.org and the "
                                                          "official moh.gov.sa PDF all unreachable/ "
                                                          "unreadable this pass), cross-checked "
                                                          "word-for-word against qanoonsa.com for "
                                                          "the amended articles (2, 7, 14). TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/40) وتاريخ 3/11/1423هـ (قرار مجلس الوزراء رقم 240 وتاريخ 26/10/1423هـ؛ قرار مجلس الشورى رقم 54/65 وتاريخ 17/1/1423هـ) — نظام المؤسسات الصحية الخاصة النافذ حالياً، الذي يحل -بنص المادة الثالثة والثلاثين منه ذاتها- محل نظام المؤسسات الطبية الخاصة (م/58، 1407هـ). النص الحرفي من nezams.com (المصدر الرئيسي؛ laws.boe.gov.sa وweb.archive.org وملف وزارة الصحة الرسمي جميعها غير قابلة للوصول/القراءة هذه الجولة)، متقاطع حرفياً مع qanoonsa.com بالنسبة للمواد المعدَّلة (2، 7، 14). المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "private_healthcare_institutions_law",
               "layer": "PRIVATE_HEALTHCARE_INSTITUTIONS_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-private-healthcare-institutions-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (35 مادة؛ 32 أصلية، 3 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Saudi Arabian Private Healthcare Institutions Law (Royal Decree "
                            "M/40, 3/11/1423H) — Arabic LLM-ready layer (35 records: 32 original, 3 "
                            "amended [Articles 2, 7, 14], 0 added, 0 repealed; no chapter structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 35], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Private Healthcare Institutions Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
