#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the (New) Social Insurance Law
track (اللائحة التنفيذية لنظام التأمينات الاجتماعية, Minister of Finance
Resolution No. 230/تأمينات, 26/12/1445H, in force from 3/7/2024G).

SCOPE NOTE -- this is the implementing regulation of the NEW Social
Insurance Law (Royal Decree M/273, 26/12/1445H, tracked at
sources/social_insurance/) ONLY. It is a SEPARATE track from the
implementing regulation of the OLD/legacy Social Insurance Law (Royal
Decree M/33, 3/9/1421H, tracked at sources/social_insurance_legacy/ and its
own regulation track built independently/in parallel by a different agent).
Do not conflate the two -- see
social_insurance_regulation_base_law_naming_collision_inherited in
known_unresolved_discrepancies for the full family of related-but-distinct
instruments (old law, old law's regulation, SANED unemployment-insurance
law M/18, Civil Pension Law M/41).

CORRECTION OF PRIOR-RESEARCH NOTE -- the task brief that seeded this track
stated the Regulation was "approved by Royal Decree No. (M/273)". That is
imprecise: M/273 is the Royal Decree that issued the base LAW itself. This
Regulation was approved by a DIFFERENT instrument of a different type and
issuing authority: Minister of Finance Resolution No. (230/تأمينات) dated
26/12/1445H (the same date as M/273, but not the same instrument), signed
by Minister of Finance Mohammed Al-Jadaan in his capacity as Chairman of
GOSI's Board, citing M/273 as its legal basis and GOSI Board Resolution No.
1490 (same date) as its administrative basis. Verified directly by fetching
the approval-resolution's own text from uqn.gov.sa (details?p=25236). See
social_insurance_regulation_approving_instrument_not_royal_decree_m273 in
known_unresolved_discrepancies.

VERIFICATION TIER -- see sources/social_insurance_regulation/law/
official_source/social_insurance_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the official Umm al-Qura Gazette portal itself (uqn.gov.sa)
-- the Regulation's full-text page (details?p=25240, ~941 KB) and the
approval-resolution page (details?p=25236, ~789 KB) were both fetched
directly via curl (HTTP 200, direct HTML text, not scanned/OCR). Parsed
programmatically: 107 "المادة (N):" markers, numbered 1-107 with no gap or
duplicate, across 7 أبواب (with أبواب 2/3/4/6 further subdivided into 4/3/
2/2 نested فصول respectively).

SECONDARY SOURCE (cross-verified article-by-article): qanoonsa.com/p/503813
-- fetched directly (HTTP 200). All 107 articles diffed programmatically
against the primary after normalizing digit-style (Eastern/Western) and
diacritics: 44/107 matched byte-for-byte; 39/107 differed ONLY in that
uqn.gov.sa's raw text is missing top-level paragraph-numbering markers
("1-", "2-"...) that qanoonsa.com's copy retains; 24/107 additionally
differed in that uqn.gov.sa is missing lettered sub-paragraph markers
("أ-", "ب-"...) too. In every one of the 107 articles the underlying words/
clauses/figures are otherwise identical -- 0 substantive differences.
Verified directly in the raw HTML that uqn.gov.sa uses NO <ol>/<li>/CSS
counter markup anywhere on the page, confirming the missing markers are a
genuine gap in the fetched primary text (most likely a Word-auto-numbered-
list-to-CMS paste artifact), not a rendering-only illusion. This track
stores the uqn.gov.sa (primary) text VERBATIM, including this gap, rather
than silently inserting qanoonsa.com's numbering -- see
social_insurance_regulation_uqn_paragraph_enumeration_gap in
known_unresolved_discrepancies for the full disclosure and a warning for
anyone needing precise sub-paragraph pinpoint citations.

TERTIARY CORROBORATION: argaam.com (Saudi financial news outlet, article ID
1739061, dated 2024-07-06) independently confirms the approving official
(Minister Al-Jadaan) and quotes regulation text matching this track
verbatim.

laws.boe.gov.sa was checked per this corpus's standard methodology but
returned "Recv failure: Connection reset by peer" on direct curl (TLS
handshake failure after a successful proxy CONNECT); not circumvented.
web.archive.org was reachable in this session for an unrelated general
page, but was not needed/used given the strength of the direct primary +
secondary + tertiary corroboration already obtained.

107 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- no amendment found
since issuance (26/12/1445H) through this research date (2026-07-25). 7
أبواب: الأول (الأحكام العامة, 1-5); الثاني (التسجيل والاشتراكات, 6-35, 4
فصول); الثالث (فرع المعاشات, 36-45, 3 فصول -- الفصل الأول بلا عنوان في
المصدر الأساسي نفسه، أُبقي فارغاً دون تخمين); الرابع (فرع الأخطار المهنية
والتعويضات الإضافية, 46-72, فصلان); الخامس (فرع التأمين ضد التعطل عن العمل,
73-80); السادس (الأحكام المشتركة, 81-97, فصلان); السابع (الأحكام الختامية,
98-107).

Diacritics (tashkeel) present in the uqn.gov.sa source are NOT stripped,
matching the base Law's own track convention (sources/social_insurance/,
which likewise preserves tashkeel) rather than this corpus's tashkeel-
stripping convention used by some other regulation tracks (e.g.
disability_rights_regulation) -- a deliberate choice of consistency with
this Regulation's own parent-Law track. Decorative in-word tatweel
introduced by the source document's justified-text formatting IS stripped
(matching this corpus's established _bad_tatweel convention), while
legitimate tatweel after the letter ه is retained. No Eastern-Arabic-Indic
digits, ZWNJ, NBSP, curly quotes, or double spaces were found in the
extracted text. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance_regulation", "law", "official_source",
                   "social_insurance_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "social_insurance_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "social_insurance_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "social_insurance_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "social_insurance_regulation_arabic_legal_llm",
                        "social_insurance_regulation_legal_llm_001_107.json")

LAW_ID = "sa-social-insurance-regulation-mof-230-1445"
LAW_AR = "اللائحة التنفيذية لنظام التأمينات الاجتماعية"
KEY_RE = r"social_insurance_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي المؤسسة المحافظ صاحب العمل المشترك").split())


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


GOV_NOTE = ("Arabic governs; PRIMARY source is the official Umm al-Qura Gazette portal "
            "(uqn.gov.sa) itself -- the Regulation's dedicated page (details?p=25240) carries "
            "the full text as direct HTML, not a scanned image, fetched directly (HTTP 200). "
            "Cross-checked article-by-article against qanoonsa.com (an independent secondary "
            "aggregator, details?p=503813): 0 substantive differences across all 107 articles, "
            "though ~63/107 show a paragraph/sub-paragraph enumeration-marker gap on the primary "
            "side only (disclosed, not silently corrected). Tertiary corroboration via "
            "argaam.com. This is the NEW Social Insurance Law's (M/273) implementing regulation "
            "-- distinct from the OLD/legacy Social Insurance Law's (M/33) own regulation, a "
            "separate track. laws.boe.gov.sa was unreachable live this pass (connection reset), "
            "not circumvented. See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance, especially for precise sub-paragraph pinpoint "
            "citations.")

SRC_AUTH = ("Minister of Finance Resolution No. (230/تأمينات), dated 26/12/1445H, signed by "
            "Minister of Finance Mohammed Al-Jadaan as Chairman of the Board of Directors of "
            "the General Organization for Social Insurance (GOSI), pursuant to the Social "
            "Insurance Law (Royal Decree M/273, 26/12/1445H) and GOSI Board Resolution No. 1490 "
            "(same date). NOT approved by Royal Decree M/273 itself (that decree issues the "
            "base Law, not this Regulation) -- see known_unresolved_discrepancies. Full text "
            "from uqn.gov.sa (official Umm al-Qura Gazette portal, primary) cross-checked "
            "article-by-article against qanoonsa.com (independent secondary source) and "
            "corroborated by argaam.com (tertiary).")

SRC_AUTH_AR = ("قرار وزير المالية رقم (230/تأمينات) وتاريخ 26/12/1445هـ، عن وزير المالية محمد "
               "بن عبدالله الجدعان بصفته رئيس مجلس إدارة المؤسسة العامة للتأمينات الاجتماعية، "
               "استناداً إلى نظام التأمينات الاجتماعية (المرسوم الملكي م/273، 26/12/1445هـ) "
               "وقرار مجلس إدارة المؤسسة رقم (1490) بذات التاريخ. لم تُعتمد بالمرسوم الملكي "
               "(م/273) ذاته (فذلك مرسوم إصدار النظام الأم لا اعتماد هذه اللائحة). النص الكامل "
               "من uqn.gov.sa (بوابة جريدة أم القرى الرسمية، مصدر أساسي) متقاطع مادة بمادة مع "
               "qanoonsa.com (مصدر ثانوي مستقل) ومؤكَّد عبر argaam.com (مصدر ثالث).")


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
        ver.append({"law_key": "social_insurance_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "SOCIAL_INSURANCE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "social-insurance-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "social_insurance_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام التأمينات الاجتماعية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
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
    json.dump({"law_key": "social_insurance_regulation",
               "layer": "SOCIAL_INSURANCE_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-social-insurance-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (107 مواد أصلية)",
               "title_en": ("Implementing Regulation of the (New) Social Insurance Law -- "
                            "Arabic LLM-ready layer (107 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 107], "text_status": "UNCHANGED",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Social Insurance Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
