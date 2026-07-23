#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Environmental Permits for Establishing
and Operating Activities track (اللائحة التنفيذية للتصاريح البيئية لإنشاء وتشغيل
الأنشطة, Minister of Environment, Water and Agriculture Decision No. 43615/3/1/1442,
09/08/1442H, issued under Article 48 of the Environmental Law, Royal Decree M/165,
19/11/1441H).

This is a COMPANION-REGULATION track to the base Environmental Law already ingested
in this corpus (track `environmental_law`, corpus key `environmental`, Royal Decree
M/165) -- the same pattern as this corpus's food_regulation track (companion to
food_law). It is one of ~15 genuinely distinct topical Implementing Regulations
under the base Environmental Law (see reports/coverage_gap_map/coverage_gap_map.json,
gap "Implementing Regulations of the General Environmental Law -- CORRECTED SCOPE",
sub_candidate environmental_permits_reg, which flagged this instrument with the
highest confidence of the family). This track ingests it.

VERIFICATION TIER -- TIER_2. See the source artifact's verification_methodology_note
for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. The live
portal was unreachable this pass (HTTP 503 Service Unavailable on the LawDetails
path). More fundamentally, exhaustive search found NO dedicated BOE lawId page for
this Implementing Regulation at all -- BOE's only page for this subject is the BASE
Environmental Law's own lawId (63831ff6-63d9-4212-8b54-abf800e146bd) -- consistent
with BOE's practice of not cataloguing ministerial-decision-level executive
regulations as standalone lawId records (identical to what food_regulation
documented). web.archive.org is blocked in this session but was not needed: the live
official gazette (uqn.gov.sa) was directly reachable.

PRIMARY SOURCE: the official text as published in the Official Gazette (Umm Al-Qura /
جريدة أم القرى -- the Kingdom's gazette of record), issue 4888, year 99, dated 15 Dhu
al-Qi'dah 1442H (25 June 2021G). TWO independent renderings of this single official
source were used and cross-verified against each other:
  (1) the uqn.gov.sa HTML page (uqn.gov.sa/details?p=17831, datePublished 2021-06-25)
      -- correct linear DOM reading order, clean Arabic glyphs with no ligature
      corruption; this is the rendering the ingested article text was extracted from;
  (2) the official born-digital PDF of the same gazette issue (downloaded directly
      from uqn.gov.sa, HTTP 200, 16 pages, Adobe InDesign CS5.5, CreationDate 24 Jun
      2021) -- the authoritative facsimile of the gazette as published, against which
      the HTML text was verified.
Word-level fidelity between HTML and PDF was measured programmatically using an
ANAGRAM SIGNATURE (each word's characters sorted alphabetically -- invariant to the
adjacent-letter ligature-reversal defect known to affect Arabic PDF text extraction)
after uniform normalization (strip tashkeel/tatweel; unify alef/ya/hamza forms):
2366 of 2374 HTML content words have a match in the PDF (99.66%); the 8 non-matching
words are all either tanween-final adverbials (مخولة/أخذا/مقابلا/جديدا/مسؤولا/كتابة
-- a tanween-normalization edge case, not a content difference) or two words from the
web page's JavaScript template footer (الموافق/الساعة, already excluded from article
text). This near-total match confirms the ingested HTML text faithfully represents
the Official Gazette (PDF).

WHY HTML (not PDF) for the ingested text: the gazette PDF uses a dense two-column
magazine layout with heavy justification kashida and the systematic ligature-reversal
extraction defect (e.g. المادة extracted as املادة -- the same defect family
documented in food_regulation), making clean linear extraction from it error-prone;
the official-source HTML renders the same text in correct linear order with clean
glyphs. No character/word-level corrective edits were applied to the HTML text (it
had no ligature defects to fix). The only normalization applied is stripping tashkeel
(only ~10 words in the source carry any) and justification tatweel -- a display-layer
normalization that changes no letter, word, number, or legal ruling, consistent with
this corpus's other tracks.

11 articles, each with a descriptive title (this regulation has NO chapter/باب
division). All 11 are اصلية -- no article-level amendment to THIS regulation was
found. Other environmental implementing regulations surfaced in research (تقييم الأثر
البيئي، المقابل المالي، التفتيش والتدقيق البيئي، ضبط المخالفات، إعادة التأهيل البيئي،
مقدمي الخدمات البيئية) are SEPARATE sibling regulations in the Environmental Law
family (this regulation's own text cross-references several of them -- Articles 6 and
11), not amendments to this one.

REPEAL/SUPERSESSION: confirmed NEGATIVE finding -- the issuing decision contains only
a generic conflict-repeal clause ("ويلغي كل ما يتعارض معه من قرارات سابقة") with no
named predecessor, consistent with this being the first environmental-permits
regulation under the 2020 Environmental Law.

A genuine SOURCE anomaly is preserved, not silently corrected: Article 1's preamble
prints "أينما وردت في هذ اللائحة" (هذ, dropping the ة of هذه) -- confirmed identical
in BOTH the HTML and PDF renderings (a genuine source typo, not an extraction
artifact), preserved verbatim. The 4 form/table annexes (ملاحق 1-4) and the penalty
table (جدول 2) that appear in the gazette (PDF pages 5-16) are tabular/form templates,
not numbered normative articles; they are disclosed but NOT ingested (Table 1 is
embedded within Article 6's own text and is kept there). See the source artifact's
known_unresolved_discrepancies for all disclosures.

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_permits", "official_source",
                   "environmental_permits_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_permits", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_permits_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_permits_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_permits_reg_arabic_legal_llm",
                        "environmental_permits_reg_legal_llm_001_011.json")

LAW_ID = "sa-environmental-permits-regulation-43615-3-1-1442"
LAW_AR = "اللائحة التنفيذية للتصاريح البيئية لإنشاء وتشغيل الأنشطة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"environmental_permits_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها المركز النشاط البيئي البيئية التصريح").split())


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

    gov_note = ("Arabic governs; PRIMARY source is the Official Gazette (Umm Al-Qura / "
                "uqn.gov.sa), gazette issue 4888 (25 June 2021), used in two "
                "cross-verified renderings (clean official HTML for the ingested text; "
                "the official born-digital gazette PDF as the authoritative facsimile, "
                "matched at 99.66% word-level via anagram-signature comparison). "
                "laws.boe.gov.sa was checked first per standard methodology but is "
                "unreachable this pass (HTTP 503) and has no dedicated lawId page for "
                "this Implementing Regulation at all. Issued by Minister of Environment "
                "Decision No. (43615/3/1/1442) dated 09/08/1442H under Article 48 of the "
                "Environmental Law (Royal Decree M/165). See verification_methodology_note "
                "and known_unresolved_discrepancies in the source artifact before relying "
                "on this track's text or provenance -- in particular the preserved source "
                "typo in Article 1 ('هذ' for 'هذه'), the bidi digit-grouping note on the "
                "decision number, and the four form/table annexes disclosed as out of "
                "scope.")

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
        ver.append({"law_key": "environmental_permits", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ENVIRONMENTAL_PERMITS_REG_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or a.get("title_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": "%s: %s" % (a["number_label_ar"], a.get("title_ar") or ""),
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or a.get("title_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "environmental-permits-reg-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s: %s" % (LAW_AR, a["number_label_ar"], a.get("title_ar") or ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "environmental_permits/regulation/articles/%s" % key,
                    "keywords_ar": _kw((a.get("title_ar") or "") + " " + text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (a.get("title_ar") or "", LAW_AR),
                                          "%s من اللائحة التنفيذية للتصاريح البيئية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Minister of Environment, Water and "
                                                          "Agriculture Decision No. (43615/3/1/1442) "
                                                          "(09/08/1442H), under Article 48 of the "
                                                          "Environmental Law (Royal Decree M/165) — "
                                                          "Official Gazette (Umm Al-Qura, uqn.gov.sa), "
                                                          "issue 4888 (25 June 2021); HTML + "
                                                          "born-digital gazette PDF cross-verified; "
                                                          "laws.boe.gov.sa unreachable this pass and "
                                                          "has no dedicated lawId page for this "
                                                          "Implementing Regulation"),
                                     "source_authority_ar": "قرار وزير البيئة والمياه والزراعة رقم (43615/3/1/1442) وتاريخ 09/08/1442هـ، استنادا إلى المادة (الثامنة والأربعين) من نظام البيئة (المرسوم الملكي م/165) — الجريدة الرسمية (جريدة أم القرى، uqn.gov.sa) العدد 4888 (25 يونيو 2021م)؛ تم التحقق المتبادل بين نص HTML وملف PDF الرسمي للجريدة؛ بوابة هيئة الخبراء غير قابلة للوصول هذه الجولة ولا تملك صفحة مخصصة لهذه اللائحة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "environmental_permits",
               "layer": "ENVIRONMENTAL_PERMITS_REG_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "base_law_document": src.get("base_law_document"),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_track_key": src.get("base_law_track_key"),
               "delegation_basis": src.get("delegation_basis"),
               "gazette_reference": src.get("gazette_reference"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "structure_note": src.get("structure_note"),
               "preamble_ar": src.get("preamble_ar"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-environmental-permits-reg-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (11 مادة؛ 11 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation for Environmental Permits for Establishing and "
                            "Operating Activities — Arabic LLM-ready layer (11 records: 11 original, "
                            "0 amended, 0 added, 0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 11], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "base_law_track_key": src.get("base_law_track_key"),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Environmental Permits Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
