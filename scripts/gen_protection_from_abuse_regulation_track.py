#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Implementing Regulation of the Protection from Abuse Law
track (اللائحة التنفيذية لنظام الحماية من الإيذاء) -- the CURRENT (2024G)
version published by the Ministry of Human Resources and Social Development
(HRSD), NOT the original ~1435H version.

VERSION SELECTED AND WHY -- see sources/protection_from_abuse_regulation/law/
official_source/protection_from_abuse_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

Three versions of this Implementing Regulation are known to exist:
  1. ORIGINAL: Ministerial Resolution No. 43047, 8/5/1435H (uses "Ministry of
     Social Affairs" wording). Still the ONLY version hosted by adlm.moj.gov.sa
     (مجلة العدل، عدد 70) -- confirmed stale this pass by direct fetch.
  2. INTERMEDIATE: Ministerial Resolution No. 76048, 20/4/1440H (27/12/2018G).
     Documented via a distinctly-titled "-1440" file on qanoniah.com (title
     only; the site is a JS-rendered SPA so full text was not retrievable) and
     via the CURRENT regulation's own Article 13, which names it as the
     instrument being replaced.
  3. CURRENT (THIS TRACK): published on hrsd.gov.sa, Arabic PDF file-creation
     timestamp 2024-09-24T09:52:46Z, English translation file-creation
     timestamp 2024-10-03T11:01:34Z. Uses the modern Ministry name (Human
     Resources and Social Development) and explicitly states (Article 13) that
     it replaces version 2 (Resolution 76048, 20/4/1440H). This is the version
     built here because it is the one currently live on the issuing Ministry's
     own site and is the most recent in the chain.

NO DECREE NUMBER SELF-STATED FOR THE CURRENT VERSION: neither the Arabic nor
the English official PDF states a ministerial resolution number or issuance
date for ITSELF anywhere in the document -- a genuine gap in the Ministry's
own publication, not fabricated or guessed here. `decree` /
`decree_date_hijri` record this honestly; the only concrete dates available
are the PDF file-generation timestamps above.

VERIFICATION TIER: TIER_2. Primary source fetched directly (HTTP 200, both
Arabic and English official PDFs from hrsd.gov.sa). Cross-internal-consistency
confirmed between the two official-language versions (same predecessor
citation, same 14-article count). BOE (laws.boe.gov.sa) returned no dedicated
lawId page for this specific Implementing Regulation this pass (only the base
law's page was found). Wayback Machine's CDX metadata API worked but its
content-serving path (web.archive.org) was refused both by direct curl (HTTP
403) and explicitly by the WebFetch tool -- not bypassed. r.jina.ai reader
fallback returned HTTP 401 (blocked, bad IP reputation) -- unusable this pass.
qanoniah.com was fetched (HTTP 200) but is a fully JS-rendered Nuxt SPA with no
article text in static HTML -- used only to corroborate that a distinct
"1440" file exists (title-level corroboration, not full-text).

14 articles, flat structure (no chapters/فصول), all 14 اصلية within this
instrument (it is a full replacement of its predecessor, not a per-article
amendment of standing text, so consolidated_amended_law = False). Article 13
is the sole repeal/replacement clause (targets Ministerial Resolution 76048,
20/4/1440H); Article 14 delegates further detailed rules to the Minister.

PDF EXTRACTION DEFECT (tool artifact, corrected): poppler's pdftotext drops
the lam of the definite article "ال" whenever immediately followed by a
hamza-initial word (الإيذاء -> اإيذاء) and transposes lam/hamza for a bare
"لـ" + hamza-initial word (للإيذاء -> لإليذاء). Re-extracted with a wholly
different engine (PyMuPDF/fitz), which produced every affected word correctly
with no exceptions -- confirmed as a poppler ToUnicode/ligature bug, not a
source defect, via side-by-side comparison and direct visual inspection of
the rendered PDF pages. PyMuPDF's extraction is the base text used here.

GENUINE SOURCE-LEVEL DEFECTS (preserved verbatim, NOT silently corrected):
(1) Article 1's definition of "الإساءة النفسية" reads "الما نفسيا" (missing
the expected hamza of "ألما") -- confirmed via 300dpi visual inspection of the
official PDF itself, not an extraction artifact. (2) Article 1's definition of
"فريق متعدد التخصصات" repeats the term itself twice before the definition,
confirmed visually as a genuine drafting duplication in the published PDF.
(3) Article 7(3) spells "الارشاد الاسري" without hamza, while Article 12(1) of
the SAME document spells "الإرشاد الأسري" correctly -- an unresolved internal
spelling inconsistency, preserved as extracted.

TASHKEEL stripped uniformly (corpus-majority convention); reversed
bidi-mirrored parenthesis pairs corrected to standard (open...close) order;
lettered sub-item separators (أ/ب/ج) normalized to a uniform "letter- text"
style (display-layer only). Arabic governs; no translation/paraphrase/
interpretation performed on the Arabic text (the English official PDF was
used only for cross-checking numbers/dates/structure, never to alter Arabic
wording). Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "protection_from_abuse_regulation", "law", "official_source",
                    "protection_from_abuse_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "protection_from_abuse_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "protection_from_abuse_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "protection_from_abuse_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "protection_from_abuse_regulation_arabic_legal_llm",
                         "protection_from_abuse_regulation_legal_llm_001_014.json")

LAW_ID = "sa-protection-from-abuse-regulation-current-2024"
LAW_AR = "اللائحة التنفيذية لنظام الحماية من الإيذاء"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"protection_from_abuse_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات مركز الحماية").split())


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
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; this track builds the CURRENT (2024G) Implementing Regulation "
            "published directly on hrsd.gov.sa (Arabic PDF file-creation 2024-09-24T09:52:46Z; "
            "English translation file-creation 2024-10-03T11:01:34Z), NOT the original ~1435H "
            "version still hosted (stale) at adlm.moj.gov.sa. Neither official version "
            "self-states a ministerial resolution number or date for ITSELF; Article 13 names "
            "only the predecessor it replaces (Ministerial Resolution 76048, 20/4/1440H). "
            "laws.boe.gov.sa returned no dedicated lawId page for this Regulation this pass "
            "(only the base law's page was found); Wayback Machine's content-serving path and "
            "r.jina.ai were both blocked/refused this pass (CDX metadata API worked). "
            "qanoniah.com is a JS-rendered SPA (title-level corroboration of a distinct 1440 "
            "file only, no full text retrievable) -> TIER_2. 14 articles, flat (no chapters); "
            "all 14 اصلية within this instrument (full replacement of predecessor, not a "
            "per-article amendment). See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance.")

SRC_AUTH = ("CURRENT (2024G) Implementing Regulation of the Law of Protection from Abuse, "
            "published by the Ministry of Human Resources and Social Development on its "
            "official site hrsd.gov.sa (Arabic + English official PDFs, both fetched directly "
            "HTTP 200; Arabic file-creation 2024-09-24, English file-creation 2024-10-03). "
            "Replaces (Article 13) the prior regulation issued by Ministerial Resolution 76048 "
            "dated 20/4/1440H. No self-citing decree number/date found in either official "
            "version. laws.boe.gov.sa has no dedicated page found for this Regulation this "
            "pass; Wayback content path and r.jina.ai both blocked -> TIER_2")

SRC_AUTH_AR = ("اللائحة التنفيذية الحالية (2024م) لنظام الحماية من الإيذاء، منشورة من وزارة "
               "الموارد البشرية والتنمية الاجتماعية على موقعها الرسمي hrsd.gov.sa (نسختان "
               "رسميتان عربية وإنجليزية، جُلبتا مباشرة HTTP 200؛ تاريخ إنشاء ملف النسخة العربية "
               "24/9/2024م، والإنجليزية 3/10/2024م). تحل (المادة 13) محل اللائحة السابقة "
               "الصادرة بالقرار الوزاري رقم 76048 وتاريخ 20/4/1440هـ. لا رقم قرار وزاري ذاتي "
               "مذكور في أي من النسختين الرسميتين. لم يُعثر على صفحة مخصصة لهذه اللائحة على "
               "laws.boe.gov.sa هذه الجولة؛ مسار عرض محتوى أرشيف الويب وr.jina.ai كلاهما محظوران "
               "-- TIER_2")


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
        ver.append({"law_key": "protection_from_abuse_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PROTECTION_FROM_ABUSE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
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
                    "record_id": "protection-from-abuse-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "protection_from_abuse_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الحماية من الإيذاء"
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
    json.dump({"law_key": "protection_from_abuse_regulation",
               "layer": "PROTECTION_FROM_ABUSE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "self_citation_status": src.get("self_citation_status"),
               "document_file_metadata": src.get("document_file_metadata"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-protection-from-abuse-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " (النسخة الحالية 2024م) — الطبقة العربية الجاهزة للنماذج "
                                     "اللغوية (14 مادة، كلها أصلية ضمن هذا الإصدار)",
               "title_en": ("Implementing Regulation of the Law of Protection from Abuse "
                            "(CURRENT 2024G version) — Arabic LLM-ready layer "
                            "(14 records, all original within this instrument)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 14], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Protection from Abuse Regulation (current, 2024G) "
          "records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
