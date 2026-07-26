#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Waste Management Law track (نظام إدارة النفايات,
Royal Decree M/3, 5/1/1443H -- the currently in-force Waste Management Law,
administered by the National Center for Waste Management (mwan.gov.sa) under the
Ministry of Environment, Water and Agriculture (MEWA)).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It was
built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام إدارة النفايات is a single,
self-standing Royal-Decree law (M/3, 5/1/1443H), confirmed via cross-checked
independent signals: (1) laws.boe.gov.sa carries it under its own dedicated lawId
4d5bda56-cc0d-4b16-a025-ad9d00b281ab (seen via WebSearch), with the PREDECESSOR
law's lawId (de0a2f61-27e3-47fa-a710-a9a700f21a67, نظام إدارة النفايات البلدية
الصلبة) also independently located and confirmed still archived on the same
portal; (2) qanoonsa.com (an independent secondary aggregator, fetched HTTP 200)
confirms both this Law and its Implementing Regulation exist, and lists several
later ministerial decisions approving technical controls/guides under it; (3) a
direct mwan.gov.sa (the National Center for Waste Management -- the administering
authority) link located via WebSearch confirms the existence and approximate
138-page length of the Implementing Regulation.

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT (a stronger anchor than the
decree-only repeal seen in some other tracks in this corpus, e.g. agriculture):
Article 37 states verbatim: "يحل هذا النظام محل نظام إدارة النفايات البلدية
الصلبة، الصادر بالمرسوم الملكي رقم (م/48) وتاريخ 17 /9/ 1434هـ." This is also
consistent with the issuing Council of Ministers Resolution's preamble, which
references the same predecessor law. Recorded in supersedes_ar and
amendment_history; needed later for the corpus-wide supersession graph (not
touched here).

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY source)
was checked FIRST per standard methodology but is unreachable this pass: repeated
direct curl attempts (full browser headers, HTTP/1.1 explicit) all returned
"Connection reset by peer" (a deeper connection-level failure than the HTTP 503
documented for other tracks in this corpus, but the same class of "not actually
reachable this pass"). Unlike several other tracks in this corpus that left
Wayback untried per session egress policy, THIS pass explicitly attempted
web.archive.org and got the identical "Connection reset by peer" -- confirming
the block extends to the archive this session, and NOT circumventing it further.
The full verbatim Arabic text of all 38 articles was extracted from ONE full-text
aggregator, nezams.com (a clean born-digital HTML page, HTTP 200 -- no scan/OCR/
ligature defects). Every governing metadata fact, the 38-article count, the
11-chapter structure, and the Article-37 supersession text are self-consistent
within that one source and independently cross-checked for identity/existence
(not char-level text) via BOE lawIds (current + repealed), qanoonsa.com, and the
mwan.gov.sa Implementing-Regulation link. A follow-up re-verification of the
verbatim text against laws.boe.gov.sa is recommended once reachable.

38 articles, 11 chapters (فصول); all 38 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة (the Law
has had no amendments per nezams.com: "لم يجرى عليه تعديل"). Diacritics
(tashkeel) are stripped uniformly for consistency with this corpus's other
BOE-family tracks; the source itself uses ONLY Western digits throughout the
article bodies (no mixed Arabic-Indic/Western rendering to disclose, unlike
agriculture). The Council of Ministers Resolution No. (11) date is disclosed as
CONFLICTING across three renderings on the same source page (2/1/1443H in the
metadata table, 3/1/1443H in both h4 section headers, and an evident decade-off
typo of 2/1/1433H inside the Royal Decree's own body text) -- see
known_unresolved_discrepancies; NOT silently resolved.

IMPLEMENTING REGULATION -- identified (via mwan.gov.sa link, ~138 pages) but NOT
built this pass: mwan.gov.sa itself was unreachable this session (same
connection-reset pattern), so its full text could not be verified within
reasonable effort. Flagged as a follow-up candidate track (waste_management_
regulation, law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "waste_management_law", "law", "official_source",
                   "waste_management_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "waste_management_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "waste_management_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "waste_management_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "waste_management_law_arabic_legal_llm",
                        "waste_management_law_legal_llm_001_038.json")

LAW_ID = "sa-waste-management-law-m3-1443"
LAW_AR = "نظام إدارة النفايات"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"waste_management_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير المركز الجهة النفايات إدارة").split())


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
        ver.append({"law_key": "waste_management_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "WASTE_MANAGEMENT_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Waste Management Law (Royal Decree M/3, 5/1/1443H), "
                                              "a brand-new base-law track built from scratch this "
                                              "pass (not previously in this corpus). Article 37 "
                                              "OF THE LAW ITSELF states it replaces the Municipal "
                                              "Solid Waste Management Law (M/48, 17/9/1434H). "
                                              "laws.boe.gov.sa was checked FIRST per standard "
                                              "methodology but unreachable this pass (connection "
                                              "reset on repeated attempts); web.archive.org was "
                                              "also explicitly attempted and returned the same "
                                              "connection-reset failure (not circumvented further). "
                                              "The verbatim text of all 38 articles was extracted "
                                              "from nezams.com (a single clean born-digital HTML "
                                              "aggregator, no scan/OCR/ligature defects). Governing "
                                              "metadata and the 11-chapter/38-article structure are "
                                              "cross-checked for identity against BOE lawIds "
                                              "(current + repealed), qanoonsa.com, and an "
                                              "mwan.gov.sa Implementing-Regulation link. TIER_3. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably the "
                                              "disclosed 3-way CoM Resolution 11 date conflict."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "waste-management-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "waste_management_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام إدارة النفايات" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/3), 5/1/1443H "
                                                          "(Council of Ministers Resolution 11 -- "
                                                          "date conflicting across the same "
                                                          "secondary source, see known_unresolved_ "
                                                          "discrepancies; Shura Resolution 140/26, "
                                                          "14/9/1442H) — the currently in-force "
                                                          "Waste Management Law, which by its own "
                                                          "Article 37 replaces the Municipal Solid "
                                                          "Waste Management Law (M/48, 1434H). "
                                                          "Verbatim text from nezams.com (single "
                                                          "full-text aggregator; laws.boe.gov.sa and "
                                                          "web.archive.org both unreachable this "
                                                          "pass); all metadata and the 38-article/ "
                                                          "11-chapter structure cross-verified for "
                                                          "identity against multiple independent "
                                                          "sources. TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/3) وتاريخ 5/1/1443هـ (قرار مجلس الوزراء رقم (11) -- تاريخه متعارض بين مصادر المصدر الثانوي نفسه، انظر known_unresolved_discrepancies؛ قرار مجلس الشورى رقم (140/26) وتاريخ 14/9/1442هـ) — نظام إدارة النفايات النافذ حالياً، الذي يحل -بنص المادة السابعة والثلاثين منه ذاتها- محل نظام إدارة النفايات البلدية الصلبة (م/48، 1434هـ). النص الحرفي من nezams.com (مصدر نص كامل واحد؛ laws.boe.gov.sa وweb.archive.org كلاهما غير قابلين للوصول هذه الجولة)؛ وجميع البيانات الوصفية والبنية (38 مادة، 11 فصلاً) متقاطعة هوياتياً عبر مصادر مستقلة متعددة. المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "waste_management_law",
               "layer": "WASTE_MANAGEMENT_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-waste-management-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (38 مادة؛ 38 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ 11 فصلاً)",
               "title_en": ("The Saudi Arabian Waste Management Law (Royal Decree M/3, 5/1/1443H) "
                            "— Arabic LLM-ready layer (38 records: 38 original, 0 amended, 0 added, "
                            "0 repealed; 11 chapters)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 38], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Waste Management Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
