#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law of Practicing Healthcare
Professions track (اللائحة التنفيذية لنظام مزاولة المهن الصحية), the
follow-up candidate explicitly flagged by this corpus's own
healthcare_professions (base law) track (see sources/healthcare_professions/
law/official_source/healthcare_professions_law_official_source.json,
known_unresolved_discrepancies key
healthcare_professions_implementing_regulation_not_ingested_this_pass). This
track ingests it.

VERIFICATION TIER -- see sources/healthcare_professions_regulation/law/
official_source/healthcare_professions_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

FOUNDING RESOLUTION UNCERTAIN: this track's decree field records Ministerial
Resolution No. (4080489) dated 2/1/1439H, per the primary MOH PDF's own
cover page. However, an independently-located EARLIER edition of this same
consolidated booklet (nshr.org.sa, dated 1432H/2011, using a different
paragraph-numbering convention) already contains a full Implementing
Regulation -- meaning 4080489/1439H is very likely a re-issuance/
consolidation of an already-existing regulation into its current (3rd,
1440H/2019) form, not the absolute founding resolution. The true founding
resolution was NOT located this pass -- flagged explicitly, not assumed.

PRIMARY SOURCE (full text, current edition): an official Ministry of Health
PDF (moh.gov.sa/Ministry/Rules/Documents/Executive-Regulations-Health-
Profession-1.pdf), fetched directly (HTTP 200) and independently confirmed
BYTE-IDENTICAL via a Wayback Machine snapshot and a third-party mirror
(docdroid.net). A SECOND, independently-produced MOH export of the same
regulation (different producer software, different pagination) explicitly
labels itself "الإصدار الثالث 1440هـ - 2019م" on its own cover page and was
used as a structural/content cross-check.

EXTRACTION: pdftotext corrupted numerous justified/kashida-stretched words
by inserting stray mid-word spaces (a known issue with this MOH PDF family,
already documented in this corpus's anti_smoking_regulation and base
healthcare_professions_law tracks). This track instead used PyMuPDF word-box
extraction with explicit RTL line reordering, which preserved intact words
but surfaced a distinct, fully mechanical bidi/CMap defect in the source
PDF's own embedded font: the mandatory lam-alef ligature (ل immediately
followed by ا) is either character-order-swapped (for the isolated negation
particle "لا" -> "ال") or dropped outright when mid-word (e.g. "علاقة" ->
"عاقة", "اللائحة" -> "الائحة") -- confirmed present identically in BOTH
independent MOH exports, hence a source-file defect, not a tool artifact.
Corrected via a small, individually context-verified word list (see
_LAM_ALEF_FIXES below); every fix restores exactly one dropped/reordered
ligature letter and changes no other letter or word choice. Two page-layout
scrape-boundary artifacts (an editorial footnote spliced into Article 35's
third clause at a page break, and trailing فصل/فرع heading text on the last
regulation paragraph of Articles 4, 14, 23, 25 and 41) were identified and
excised at the SOURCE-ARTIFACT level (official_source.json already holds the
corrected text); this generator does not re-derive that extraction, it only
reads the vetted official_source.json.

30 of the base Law's 44 articles carry regulation content in this edition;
14 do not (6, 13, 21, 24, 26-32, 34, 42, 43 -- concentrated in the civil/
penal/disciplinary-liability chapter and the closing provisions) -- this is
a structural fact of the primary source (confirmed identically in both MOH
exports), not an extraction gap. This track therefore has 30 records, not
44. Article keys and law_article_number follow the corresponding BASE LAW
article number (matching this corpus's anti_smoking_regulation precedent),
not a resequenced 1..30 count.

All 30 records are اصلية (no per-paragraph amendment history could be
attributed to a specific resolution this pass; edition-to-edition diffing
against the 2011 nshr.org.sa copy was only partial -- see
known_unresolved_discrepancies) -> TIER_2.

Diacritics (tashkeel) stripped uniformly for consistency with this corpus's
majority convention (this source PDF's own tanween encoding is demonstrably
unreliable: ~94% of raw tanween-fatha occurrences were missing their
required carrying alef). Arabic governs; no translation / paraphrase /
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "healthcare_professions_regulation", "law", "official_source",
                   "healthcare_professions_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "healthcare_professions_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "healthcare_professions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "healthcare_professions_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "healthcare_professions_regulation_arabic_legal_llm",
                        "healthcare_professions_regulation_legal_llm_001_030.json")

LAW_ID = "sa-healthcare-professions-regulation-4080489-1439h-3rd-ed"
LAW_AR = "اللائحة التنفيذية لنظام مزاولة المهن الصحية"
KEY_RE = r"healthcare_professions_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات الصحي الصحية الممارس").split())


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


GOV_NOTE = ("Arabic governs. This track ingests only the اللائحة (regulation) paragraphs of "
            "the Ministry of Health's consolidated Law+Regulation booklet; the base Law's own "
            "44 articles are already tracked separately at sources/healthcare_professions/. "
            "PRIMARY: official MOH PDF (Executive-Regulations-Health-Profession-1.pdf), byte-"
            "verified via Wayback Machine and a third-party mirror. SECONDARY: a second, "
            "independently-produced MOH export explicitly labelled 'الإصدار الثالث 1440هـ-"
            "2019م'. Founding resolution NOT confirmed (an older 2011/1432H edition predates "
            "the 4080489/1439H resolution printed on this track's primary source, implying "
            "4080489 is a re-issuance, not the founding instrument). laws.boe.gov.sa and "
            "ncar.gov.sa were both unreachable this pass for a live first-party confirmation "
            "-> TIER_2. 30 of 44 base-law articles carry regulation content; the other 14 do "
            "not, confirmed structurally in both MOH exports. See verification_methodology_note "
            "and known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance.")

SRC_AUTH = ("Implementing Regulation of the Law of Practicing Healthcare Professions, Ministry "
            "of Health, printed decree number (4080489) dated 2/1/1439H (founding status "
            "unconfirmed -- see known_unresolved_discrepancies), 3rd edition 1440H/2019. Full "
            "text from the official MOH PDF, byte-verified via Wayback Machine and a mirror, "
            "cross-checked against a second independent MOH export -> TIER_2")

SRC_AUTH_AR = ("اللائحة التنفيذية لنظام مزاولة المهن الصحية، وزارة الصحة، القرار الوزاري رقم "
               "(4080489) وتاريخ 2/1/1439هـ (حالة كونه القرار التأسيسي غير مؤكدة -- انظر "
               "known_unresolved_discrepancies)، الإصدار الثالث 1440هـ-2019م. النص الكامل من "
               "ملف وزارة الصحة الرسمي، مطابق بصريا عبر Wayback Machine ونسخة مرآة، ومقارن مع "
               "نسخة ثانية مستقلة من وزارة الصحة نفسها -- TIER_2")


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
        ver.append({"law_key": "healthcare_professions_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "HEALTHCARE_PROFESSIONS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "law_article_number": a.get("law_article_number", n),
                    "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": src.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "law_article_number": a.get("law_article_number", n),
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "healthcare-professions-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "healthcare_professions_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مزاولة المهن الصحية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"], "verification_tier": src.get("verification_tier"),
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
    json.dump({"law_key": "healthcare_professions_regulation",
               "layer": "HEALTHCARE_PROFESSIONS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "founding_resolution_confirmed": src.get("founding_resolution_confirmed", False),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_decree_date_hijri": src.get("base_law_decree_date_hijri"),
               "base_law_track": src.get("base_law_track"),
               "ingested_edition_ar": src.get("ingested_edition_ar"),
               "ingested_edition_en": src.get("ingested_edition_en"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "verification_tier": src.get("verification_tier"),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "no_regulation_content_law_articles": src.get("no_regulation_content_law_articles", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-healthcare-professions-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                                     "(30 سجلا؛ جميعها أصلية؛ 14 مادة من النظام الأساسي بلا لائحة)",
               "title_en": ("Implementing Regulation of the Law of Practicing Healthcare "
                            "Professions — Arabic LLM-ready layer (30 records, all original; "
                            "14 base-law articles carry no regulation content)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 44],
               "note": ("Base-law articles 6, 13, 21, 24, 26-32, 34, 42 and 43 have no "
                        "corresponding regulation content in this (3rd) edition; only 30 of "
                        "44 possible article-keyed records exist by design."),
               "text_status": "MOH_PDF_PRIMARY_X_SECOND_MOH_EXPORT_VERIFIED_WAYBACK_IDENTICAL_"
                              "BOE_NCAR_UNREACHABLE",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Healthcare Professions Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
