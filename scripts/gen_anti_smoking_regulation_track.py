#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Anti-Smoking Law track
(اللائحة التنفيذية لنظام مكافحة التدخين), the follow-up candidate explicitly
flagged by this corpus's own anti_smoking (base law) track (see sources/
anti_smoking/law/official_source/anti_smoking_law_official_source.json,
known_unresolved_discrepancies key
anti_smoking_implementing_regulation_out_of_scope). This track ingests it.

VERIFICATION TIER -- see sources/anti_smoking_regulation/law/official_source/
anti_smoking_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

FOUNDING RESOLUTION NOT CONFIRMED: Article 19 of the base Law (Royal Decree
M/56, 28/7/1436H) requires the Minister of Health to issue this Implementing
Regulation within six months of the Law's publication (~early 1437H). The
founding ministerial resolution's own number and date were NOT located this
pass despite repeated search -- this is flagged explicitly rather than
assumed. This directly corrects a prior research pass's framing, which
described Ministerial Resolution No. 797557 (1/5/1441H) as if it were the
issuing resolution. Independent verification this pass shows 797557/1441H is
instead a later AMENDMENT resolution (confirmed by multiple independent web
sources, including an argaam.com news article dated 25 Jan 2020 describing
"Minister of Health approves amendments to a number of articles of the
Implementing Regulation") -- not the founding instrument. No source found
this pass describes 797557 as a founding/issuing resolution.

PRIMARY SOURCE (full text, current edition): an official Ministry of Health
PDF (moh.gov.sa/Ministry/Rules/Documents/22.pdf; the SAME file used as the
base law's own primary source), titled "...Implementing Regulation... 3rd
edition, 2019", issued jointly with the National Committee for Tobacco
Control. pdftotext could not extract Arabic from this file (same embedded-
font issue documented in the base law track); all 14 pages were read via
direct vision reading of page-image renders (more reliable than OCR for
Arabic).

CROSS-CHECK / AMENDMENT DETECTION: a second, independently-hosted copy of
the regulation -- a WHO/EMRO-hosted PDF (emro.who.int/images/stories/tfi/
documents/reg_saa_2017.pdf, file-dated 18 Oct 2017) -- was fetched and read
(pdftotext -layout partially succeeded; cross-checked via vision reading).
Comparing this 2017 text against the 2019 MOH text, clause by clause, for
all 17 regulation-bearing articles: 11 articles (1, 4, 9, 10, 11, 12, 13, 16,
18, 19, 20) match VERBATIM between the two editions. 6 articles differ:
  * Article 2 (clause 1-2): separate "e-cigarette"/"e-muassel" mentions in
    2017 are consolidated into one term "الأنظمة الإلكترونية للتدخين" in 2019.
  * Article 3 (clause 3-3 only): the competent authority phrase changes from
    "الجهات المشرفة على شؤون الزراعة والصناعة" (2017) to "الجهات الرقابية ذات
    العلاقة" (2019).
  * Article 5 (clauses 1-5, 2-5): detailed GSO-246-based packaging
    requirements (2017) are replaced by a general reference to Saudi Food &
    Drug Authority (SFDA) published standards, plus a wholly new clause 2-5.
  * Article 6 (clauses 1-6, 2-6): competent testing authority shifts from
    SASO (Saudi Standards, Metrology and Quality Org) to SFDA, plus a new
    importer-bears-testing-cost clause added to 2-6.
  * Article 7 (clauses 1-7, 2-7): mosques added as item 1 of the banned-place
    list (12 -> 13 items); the buffer distance around gatherings increases
    from 8 to 10 meters. This SPECIFIC change matches an argaam.com news
    article (id 1343780, published 25 Jan 2020) describing Ministerial
    Resolution 797557 (1/5/1441H) almost exactly (13 place categories, a
    10-meter buffer) -- the only one of the six changes independently
    corroborated by name to that resolution.
  * Article 8 (clause 1-8 only): minimum-quantity/weight packaging rules
    change (the "or 10 cigars" alternative is dropped; the flat 500g minimum
    for other tobacco products becomes a 250-500g range).
Only Article 7's change is independently attributed BY NAME to Resolution
797557 in a secondary source; the other five changes are confirmed by direct
2017-vs-2019 text comparison but not attributed by name to any specific
resolution in a source found this pass.

Articles 14, 15, 17 of the base Law have NO corresponding regulation content
in EITHER the 2017 or 2019 edition (no "اللائحة:" subsection at all) -- this
track deliberately has NO records for these three law articles; 17 records
total (not 20).

laws.boe.gov.sa has NO dedicated lawId page for this Implementing Regulation
(only for the base Law) -- consistent with the pattern documented in this
corpus's traffic_regulation track (BOE does not catalogue ministerial-level
executive regulations as standalone lawId records). uqn.gov.sa (Umm al-Qura
Gazette), nctc.gov.sa (National Committee for Tobacco Control), and
qanoniah.com were all attempted and found inaccessible this pass (404, DNS
failure, and JS/login-gated content respectively) -- see
known_unresolved_discrepancies for details, none of these blocks were
bypassed.

17 records: 11 اصلية, 6 معدلة (2, 3, 5, 6, 7, 8), 0 ملغاة, 0 مضافة. The
regulation is FLAT relative to the base law's own numbering (no separate
chapter/باب structure of its own); section_ar is empty for every record.
Article keys follow the corresponding BASE LAW article number (anti_smoking_
regulation_art_001 .. _020, with 014/015/017 intentionally absent) --
matching the primary source's own "N-M" convention where M is the base law
article number.

Diacritics (tashkeel) stripped uniformly for consistency with this corpus's
other tracks. A verbatim editing-artifact trailing fragment in Article 8's
clause 1-8 of the primary MOH source itself ("من تبغ الجراك أو المعسل أو
الغليون.") is preserved as-is, never silently deleted or "fixed" -- see
known_unresolved_discrepancies. Arabic governs; no translation / paraphrase /
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_smoking_regulation", "law", "official_source",
                   "anti_smoking_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_smoking_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_smoking_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_smoking_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_smoking_regulation_arabic_legal_llm",
                        "anti_smoking_regulation_legal_llm_001_020.json")

LAW_ID = "sa-anti-smoking-regulation-2019-3rd-ed"
LAW_AR = "اللائحة التنفيذية لنظام مكافحة التدخين"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
KEY_RE = r"anti_smoking_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"anti_smoking_regulation_art_002", "anti_smoking_regulation_art_003",
                "anti_smoking_regulation_art_005", "anti_smoking_regulation_art_006",
                "anti_smoking_regulation_art_007", "anti_smoking_regulation_art_008"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات").split())


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
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa has NO dedicated lawId page for this "
            "Implementing Regulation (only for the base Anti-Smoking Law). The founding "
            "ministerial resolution's own number/date were NOT confirmed this pass -- this "
            "corrects a prior pass's framing that treated Ministerial Resolution No. 797557 "
            "(1/5/1441H) as the issuing resolution; independent verification shows 797557 "
            "is instead a later AMENDMENT resolution (multiple independent sources describe "
            "it as approving amendments, not an original issuance). PRIMARY full-text source: "
            "an official Ministry of Health PDF (moh.gov.sa, joint MOH/National Committee for "
            "Tobacco Control publication, \"3rd edition, 2019\"), vision-read in full. "
            "CROSS-CHECK: a WHO/EMRO-hosted 2017 edition of the same regulation, diffed "
            "clause-by-clause against the 2019 text to detect amendments -> TIER_2. 17 "
            "records (base-law Articles 14/15/17 have no regulation content in either "
            "edition and are intentionally absent); 11 اصلية, 6 معدلة (Articles 2, 3, 5, 6, "
            "7, 8) -- only Article 7's change is independently attributed by name to "
            "Resolution 797557 in a secondary news source. See verification_methodology_note "
            "and known_unresolved_discrepancies in the source artifact before relying on "
            "this track's text or provenance.")

SRC_AUTH = ("Ministry of Health Implementing Regulation of the Anti-Smoking Law, issued "
            "under Article 19 of Royal Decree M/56 (28/7/1436H). Founding resolution "
            "number/date NOT confirmed this pass. Full text from the official MOH PDF "
            "(\"3rd edition, 2019\"), cross-checked against a 2017 WHO/EMRO-hosted edition "
            "to detect amendments. Latest confirmed amendment: Ministerial Resolution No. "
            "797557 (1/5/1441H) -> TIER_2")

SRC_AUTH_AR = ("اللائحة التنفيذية لنظام مكافحة التدخين، صادرة عن وزارة الصحة عملا بالمادة "
               "التاسعة عشرة من المرسوم الملكي رقم م/56 وتاريخ 28/7/1436هـ. رقم/تاريخ القرار "
               "التأسيسي غير مؤكد هذه الجولة. النص الكامل من ملف وزارة الصحة الرسمي (الإصدار "
               "الثالث، 2019)، متقاطع مع نسخة 2017 المستضافة على موقع منظمة الصحة العالمية "
               "لرصد التعديلات. آخر تعديل مؤكد: قرار معالي وزير الصحة رقم (797557) وتاريخ "
               "1/5/1441هـ -- TIER_2")


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
        ver.append({"law_key": "anti_smoking_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ANTI_SMOKING_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": a.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "anti-smoking-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_smoking_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مكافحة التدخين"
                                          % a["number_label_ar"]],
                    "text_status": a["status"], "verification_tier": a.get("verification_tier"),
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_smoking_regulation",
               "layer": "ANTI_SMOKING_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "founding_resolution_confirmed": src.get("founding_resolution_confirmed", False),
               "latest_confirmed_amendment_resolution_ar":
                   src.get("latest_confirmed_amendment_resolution_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-smoking-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 سجلا؛ 11 أصلية، 6 معدلة، 0 ملغاة، 0 مضافة)",
               "title_en": ("Implementing Regulation of the Anti-Smoking Law — Arabic "
                            "LLM-ready layer (17 records: 11 original, 6 amended, 0 "
                            "repealed, 0 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20],
               "note": ("Base-law Articles 14, 15, and 17 have no corresponding regulation "
                        "content in either edition examined; only 17 of 20 possible "
                        "article-keyed records exist by design."),
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Smoking Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
