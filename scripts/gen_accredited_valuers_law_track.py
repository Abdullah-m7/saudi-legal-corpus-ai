#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Certified/Accredited Valuers Law track (نظام المقيّمين
المعتمدين, Royal Decree M/43, 9/7/1433H -- the currently in-force Law, as substantially
amended by Royal Decree M/190, 22/11/1444H, establishing/governing the Saudi Authority
for Accredited Valuers, "Taqeem").

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It was built
from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام المقيّمين المعتمدين is a single Royal-Decree
law (M/43, 9/7/1433H), substantially amended by Royal Decree M/190 (22/11/1444H, ratifying
Council of Ministers Resolution 795/17/11/1444H), with two earlier narrower amendments
(CoM 57/1442H; CoM 123/1443H, limited to Article 27). Confirmed via FOUR independent
sources, two of them official/primary: (1) taqeem.gov.sa -- the Authority's OWN official
site -- serves a consolidated current-text PDF ("...وتعديلاته") directly from its
portal.rules attachment endpoint; (2) uqn.gov.sa -- the Official Umm Al-Qura Gazette --
reproduces the full verbatim text of Royal Decree M/190 and the CoM 795 resolution it
ratifies; (3) nezams.com (independent secondary aggregator) carries the full original
1433H text plus per-article amendment annotations; (4) qanoonsa.com (a second independent
secondary aggregator) reproduces the CoM 795 resolution's full 17-clause text, matching
uqn.gov.sa and nezams.com verbatim.

VERIFICATION TIER -- TIER_2. laws.boe.gov.sa (this corpus's usual PRIMARY source) was
checked first per standard methodology but is unreachable this pass (connection reset).
The consolidated current text was extracted from a taqeem.gov.sa official PDF that
suffers from a known Arabic-PDF font/ligature bug (lam+alef ligature glyph order reversed
in the content stream), corrected by careful manual reading and cross-checked article by
article against nezams.com (original text + quoted amendment substitutions), qanoonsa.com,
and uqn.gov.sa (both giving the CoM 795/M-190 amendment delta verbatim). A handful of
articles/clauses (5 of 45) rest on the manually-corrected taqeem.gov.sa PDF alone without
a second source confirming the exact wording -- individually flagged in
known_unresolved_discrepancies. See the source artifact's verification_methodology_note
for the full account.

45 articles, NO formal chapter/باب division (the Law never uses "الفصل" or "الباب"); 25
معدلة (amended), 20 اصلية (unchanged), 0 ملغاة, 0 مضافة. Diacritics are not stripped here
(the sources are essentially undiacritized already, aside from decorative shadda on
"المقيّم"/"المقيّمين", kept as-is per the official spelling of the Authority's own name).

IMPLEMENTING REGULATION -- identified (Minister of Finance Decision No. 107, ~1445H,
72 articles, replacing the 1441H regulation) but NOT built this pass: a small date
discrepancy across sources (22/1/1445H per qanoonsa.com's own decision text vs 28/1/1445H
per this task's citation vs a 23/2/1445H gazette-portal date field) was not resolved by
guessing. Flagged as a follow-up candidate track (accredited_valuers_regulation,
law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation beyond the disclosed manual
ligature-bug correction of the primary PDF. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "accredited_valuers_law", "law", "official_source",
                   "accredited_valuers_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "accredited_valuers_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "accredited_valuers_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "accredited_valuers_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "accredited_valuers_law_arabic_legal_llm",
                        "accredited_valuers_law_legal_llm_001_045.json")

LAW_ID = "sa-accredited-valuers-law-m43-1433"
LAW_AR = "نظام المقيّمين المعتمدين"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"accredited_valuers_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {"accredited_valuers_law_art_%03d" % n for n in (
    1, 4, 6, 7, 8, 10, 13, 21, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 41,
    42, 44)}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير الهيئة المجلس المقيم المعتمد").split())


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
        ver.append({"law_key": "accredited_valuers_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ACCREDITED_VALUERS_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Certified/Accredited Valuers Law (Royal Decree "
                                              "M/43, 9/7/1433H, as substantially amended by "
                                              "Royal Decree M/190, 22/11/1444H), a brand-new "
                                              "base-law track built from scratch this pass (not "
                                              "previously in this corpus). laws.boe.gov.sa was "
                                              "checked FIRST per standard methodology but "
                                              "unreachable this pass (connection reset). The "
                                              "consolidated current text was extracted from a "
                                              "taqeem.gov.sa (the Authority's own official site) "
                                              "PDF suffering from a known Arabic-PDF lam+alef "
                                              "ligature-order bug, corrected by careful manual "
                                              "reading and cross-checked article by article "
                                              "against nezams.com, qanoonsa.com, and the "
                                              "Official Umm Al-Qura Gazette (uqn.gov.sa), the "
                                              "latter two independently reproducing the CoM 795/ "
                                              "M-190 amendment text verbatim. A handful of "
                                              "articles/clauses (5 of 45) rest on the manually- "
                                              "corrected PDF alone -- individually flagged in "
                                              "known_unresolved_discrepancies. TIER_2. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "accredited-valuers-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "accredited_valuers_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المقيّمين المعتمدين" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/43), 9/7/1433H, "
                                                          "as substantially amended by Royal "
                                                          "Decree No. (M/190), 22/11/1444H "
                                                          "(ratifying CoM Resolution 795, "
                                                          "17/11/1444H) -- the currently "
                                                          "in-force Certified/Accredited "
                                                          "Valuers Law establishing/governing "
                                                          "the Saudi Authority for Accredited "
                                                          "Valuers (Taqeem). Verbatim text from "
                                                          "a taqeem.gov.sa official PDF (manually "
                                                          "corrected for a known ligature-order "
                                                          "bug), cross-checked against nezams.com, "
                                                          "qanoonsa.com, and the Official Umm "
                                                          "Al-Qura Gazette (uqn.gov.sa); "
                                                          "laws.boe.gov.sa unreachable this pass. "
                                                          "TIER_2."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/43) وتاريخ 9/7/1433هـ، بصيغته المعدلة تعديلاً جوهرياً بالمرسوم الملكي رقم (م/190) وتاريخ 22/11/1444هـ (المصادق على قرار مجلس الوزراء رقم 795 وتاريخ 17/11/1444هـ) -- نظام المقيّمين المعتمدين النافذ حالياً، المُنشئ للهيئة السعودية للمقيّمين المعتمدين (تقييم) والحاكم لعملها. النص الحرفي من ملف PDF رسمي من taqeem.gov.sa (مصحح يدوياً من عطل معروف في ترتيب الرباط الخطي)، متقاطع مع nezams.com وqanoonsa.com وبوابة أم القرى الرسمية (uqn.gov.sa)؛ laws.boe.gov.sa غير قابل للوصول هذه الجولة. المستوى TIER_2.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "accredited_valuers_law",
               "layer": "ACCREDITED_VALUERS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-accredited-valuers-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (45 مادة؛ 20 أصلية، 25 معدلة، 0 مضافة، 0 ملغاة؛ دون تقسيم إلى أبواب أو فصول رسمية)",
               "title_en": ("The Saudi Arabian Certified/Accredited Valuers Law (Royal Decree "
                            "M/43, 9/7/1433H, as amended by M/190, 22/11/1444H) — Arabic "
                            "LLM-ready layer (45 records: 20 original, 25 amended, 0 added, "
                            "0 repealed; no formal chapter/باب division)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 45], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Accredited Valuers Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
