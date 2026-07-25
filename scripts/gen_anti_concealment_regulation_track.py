#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Anti-Concealment Law track
(اللائحة التنفيذية لنظام مكافحة التستر). This is the explicitly-flagged
follow-up to this corpus's own anti_concealment (base law) track (see
sources/anti_concealment/law/official_source/
anti_concealment_law_official_source.json, whose verification_methodology_note
already names "a companion Implementing Regulation ... Ministerial Resolution
00479, 20/7/1442H" as a known-to-exist, not-yet-ingested instrument). This
track ingests it. The base law's own Article (الأولى) explicitly defines
"اللائحة: اللائحة التنفيذية للنظام", and about seven of its provisions
(Articles 4, 6, 8, 11, 14, 18, 19) delegate detail to this Regulation.

VERIFICATION TIER -- see sources/anti_concealment_regulation/law/
official_source/anti_concealment_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE (full text): an official Ministry of Commerce PDF
(mc.gov.sa/ar/CC/D/RCC.pdf), fetched directly (HTTP 200, after resolving a
server-side TLS chain gap -- mc.gov.sa serves only its leaf certificate, not
the DigiCert intermediate; fixed by fetching the public intermediate from
cacerts.digicert.com and combining it with the environment's CA bundle, a
client-side chain-completion step, not a policy bypass). pdftotext could not
extract correct Arabic from this file (systematic character-swap corruption,
e.g. "التسرت" for "التستر" -- a known embedded-font/ToUnicode issue); all 9
pages were read via direct vision reading of 200dpi page-image renders
instead. All 18 articles were extracted this way, including the document's
own 9 unnumbered topical section headings (matching its table of contents
exactly -- no "الفصل"/"الباب" labelling exists in the source, unlike the base
law).

CROSS-CHECK: an official Ministry of Commerce NEWS page
(mc.gov.sa/ar/mediacenter/News/Pages/08-03-21-02.aspx, dated 24 Rajab 1442H)
links directly to this same PDF and confirms its subject; a Saudi Press
Agency (SPA, an independent state news wire) article (spa.gov.sa/2198358,
dated 25 Rajab 1442H) independently corroborates the content, the 9 topical
sections, and the coordinating government agencies named in the base law's
own Article 6 -> TIER_2 (single full-text primary + independent official
corroboration, not a second full-text copy for clause-by-clause diffing).

The founding/only ministerial resolution's number (00479) and date
(20/7/1442H) were NOT read verbatim in any primary document this pass (the
PDF itself is a title+cover booklet with no signed decree preamble). They
rest on convergent indirect evidence: an indexed Umm al-Qura gazette page
titled verbatim "الموافقة على اللائحة التنفيذية لنظام مكافحة التستر",
multiple independent aggregated web citations, and -- independently
significant -- this PDF's own embedded file-creation metadata (extracted via
pdfinfo directly from the fetched file, not from any webpage), which shows
Thu Mar 4 2021 09:23:11 UTC = 20/7/1442H exactly. uqn.gov.sa (both candidate
slugs), the Wayback Machine (blocked by this environment's egress policy),
and the r.jina.ai reader proxy (401 Unauthorized) were all attempted and
found unreachable this pass, mirroring the exact fallback-chain failure
pattern already documented in the base law's own official_source.json.

18 records, all اصلية (no amendment found this pass -- an honest "none
found", not "confirmed absent"). No chapters/فصول of the base law's kind
exist in this Regulation's own source; its 9 unnumbered topical section
headings are preserved in chapter_structure/section_ar as-is.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_concealment_regulation", "law", "official_source",
                   "anti_concealment_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_concealment_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_concealment_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_concealment_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_concealment_regulation_arabic_legal_llm",
                        "anti_concealment_regulation_legal_llm_001_018.json")

LAW_ID = "sa-anti-concealment-regulation-mc-res-00479-1442"
LAW_AR = "اللائحة التنفيذية لنظام مكافحة التستر"
STATUS = "PRIMARY_MC_GOVSA_PDF_X_SPA_OFFICIAL_CORROBORATION_TIER2"
KEY_RE = r"anti_concealment_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الوزارة الوزير").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


GOV_NOTE = ("Arabic governs; this track's full text was vision-read from the official "
            "Ministry of Commerce PDF (mc.gov.sa/ar/CC/D/RCC.pdf) -- a single direct "
            "primary source, cross-checked against an independent official Saudi Press "
            "Agency (SPA) article confirming content/structure/date -> TIER_2. The "
            "founding ministerial resolution's number (00479) and date (20/7/1442H) rest "
            "on convergent indirect evidence (indexed gazette page title, aggregated web "
            "citations, and this PDF's own file-creation metadata), NOT on a verbatim "
            "reading of the signed resolution text -- see verification_methodology_note "
            "and known_unresolved_discrepancies in the source artifact before relying on "
            "this track's provenance claims.")

SRC_AUTH = ("Implementing Regulation of the Anti-Concealment Law, issued under Article 19 "
            "of Royal Decree M/4 (1/1/1442H) by ministerial resolution (No. 00479, dated "
            "20/7/1442H per convergent indirect evidence, not verbatim primary reading). "
            "Full text from the official Ministry of Commerce PDF (mc.gov.sa), vision-read "
            "in full; cross-checked against an independent SPA news article -> TIER_2")

SRC_AUTH_AR = ("اللائحة التنفيذية لنظام مكافحة التستر، صادرة عملا بالمادة التاسعة عشرة من "
               "المرسوم الملكي رقم (م/4) وتاريخ 1/1/1442هـ، بقرار وزاري (رقم 00479 وتاريخ "
               "20/7/1442هـ بتقارب أدلة غير مباشرة، لا بقراءة مباشرة لنص القرار). النص "
               "الكامل من ملف وزارة التجارة الرسمي (mc.gov.sa)، مقروء بصريا كاملا، ومقترن "
               "بمقالة إخبارية مستقلة من وكالة الأنباء السعودية (واس) -- TIER_2")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "anti_concealment_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ANTI_CONCEALMENT_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": a.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended,
                    "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "anti-concealment-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_concealment_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام مكافحة التستر"
                                          % n],
                    "text_status": STATUS, "verification_tier": a.get("verification_tier"),
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_concealment_regulation",
               "layer": "ANTI_CONCEALMENT_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "founding_resolution_confirmed": src.get("founding_resolution_confirmed", False),
               "founding_resolution_confirmation_basis":
                   src.get("founding_resolution_confirmation_basis"),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_decree_date_hijri": src.get("base_law_decree_date_hijri"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-concealment-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (18 مادة؛ جميعها أصلية)",
               "title_en": ("Implementing Regulation of the Anti-Concealment Law — Arabic "
                            "LLM-ready layer (18 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 18], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Concealment Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
