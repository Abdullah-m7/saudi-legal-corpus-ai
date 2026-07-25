#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Human Resources in the Civil
Service track (اللائحة التنفيذية للموارد البشرية في الخدمة المدنية, First
Edition 1440H/2019G, Ministry of Human Resources and Social Development).

CURRENCY DETERMINATION (the central question this track was built to
answer): is the 1397H "اللوائح التنفيذية لنظام الخدمة المدنية" (Civil
Service Council Resolution No. 1, 27/7/1397H) still the governing
implementing regulation of the Civil Service Law, or has this newer
instrument superseded it in practice? This track concludes the LATTER, on
the strength of: (1) the 1397H document is not a coherent standalone
regulation but a historical index quoting the base Law article-by-article
with footnotes pointing to whichever separate sub-regulation (لائحة
الترقيات 1421H, لائحة النقل 1424H, لائحة التعيين 1425H, etc.) later
implemented it -- most of that scattered patchwork frozen since 1438H; (2)
this Regulation consolidates/replaces exactly those scattered sub-regulation
domains in one coherent 261-article, 11-chapter instrument; (3) Article 31
of this Regulation names the very reform committee (Council of Ministers
Resolution No. 75, 29/1/1440H) tasked with overhauling the Civil Service
Law's implementing regulations; (4) this Regulation is a living instrument
actively amended through 1444H, while the 1397H document has had no
disclosed update since 1438H, predating that reform committee. No single
explicit repeal clause for the 1397H document was found, and this is
disclosed rather than silently assumed away -- see
know_unresolved_discrepancies key
civil_service_regulation_currency_determination_1397h_vs_1440h in the source
artifact for the full account.

VERIFICATION TIER -- see sources/civil_service_regulation/law/
official_source/civil_service_regulation_official_source.json's
verification_methodology_note for the complete methodology. Summary:

PRIMARY TEXT SOURCE for 245/261 articles (status =
KSU_1440H_SINGLE_SOURCE_STRUCTURALLY_CROSS_CHECKED_VS_HRSD): a clean,
uncorrupted PDF text layer of the Regulation's First Edition (1440H/2019G,
Adobe InDesign-produced) hosted at King Saud University
(projects.ksu.edu.sa) -- independently fetched, 48 pages, verified to
contain all 261 articles with no gaps, and structurally cross-checked
(article count, 11-chapter/فصل structure, chapter titles) against HRSD's own
current portal listing and PDF table of contents. This baseline text is
final for the 245 articles with no evidence of subsequent amendment.

WHY NOT HRSD's OWN CURRENT PDF FOR EVERYTHING: HRSD's own hosted current
edition (hrsd.gov.sa, 2023-03 folder; a near-identical copy is also hosted
at moe.gov.sa) exhibits a systematic, confirmed text-layer corruption
(verified with two independent extraction engines, pdftotext and PyMuPDF,
ruling out a tool-specific bug): certain whole words consistently extract
with internally transposed letters (e.g. "التي" -> "اليت", "الترقية" ->
"الرتقية", "يتم" -> "يمت", "الخبرات" -> "الخربات", with zero counter-examples
found for "التي" across the full document). This is NOT a simple, safely-
reversible per-letter-pair rule (some genuinely-correct words, e.g.
"المرتبتين", contain the exact same letter sequences that are corrupted
elsewhere), so no automated "fix" was attempted -- per this corpus's rule
against reconstructing/inferring legal text. OCR was attempted as a
workaround and found infeasible in this environment (a single page at 150
DPI did not finish within 60 seconds; at 300 DPI a run exceeded 5 minutes
before being manually terminated -- this sandbox was heavily contended by
unrelated concurrent OCR jobs from other sessions this pass).

16 ARTICLES CARRY A LOWER-CONFIDENCE TIER (status =
HRSD_SINGLE_SOURCE_TEXT_LAYER_ARTIFACTS_MANUALLY_REVIEWED_LOWER_CONFIDENCE):
articles 1, 9, 15, 26, 39, 94, 105, 127, 159, 160, 189, 198, 208, 212, 219,
224 carry a confirmed Ministerial Resolution amendment footnote on HRSD's
current PDF. Their CURRENT (post-amendment) text was extracted by manually
locating each footnote's true INLINE marker position (a naive "nearest
preceding مادة heading before the footnote text at the page bottom"
heuristic was tried first and found to mis-attribute six of these footnotes
to the wrong article entirely -- corrected only after re-checking each
marker's actual in-body position; see
civil_service_regulation_footnote_attribution_corrections in the source
artifact) and manually reviewing every changed word for the known corruption
signature (none was found in the actual amendment deltas). This text is
still single-source (no independent second source was reachable for this
Regulation specifically this pass) and is stored at a distinctly lower
confidence tier than the 245-article baseline; the original 1440H text for
all 16 is preserved verbatim in original_1440h_text, never deleted.

Additionally, 10 scrambled cross-line-wrap numeral references (e.g. a
citation to "المادة (93)" that PDF text extraction had split and reordered
across a justified line-wrap into unreadable fragments) were identified and
manually reconstructed by reading the source page directly and, where
needed, cross-checking the referenced article number topically against the
base Civil Service Law or this Regulation's own neighboring articles --
documented in the generator's own history, not silently smoothed over.

261 records: 245 اصلية (unamended since the 1440H First Edition) / 16 معدلة
(amended 1441H-1444H, per 7 distinct Ministerial Resolutions) / 0 ملغاة / 0
مضافة. 11 أبواب, with الباب الثاني (2 فصول), الباب الرابع (6 فصول), and
الباب السابع (4 فصول) further subdivided.

No legal text is altered beyond decorative-tatweel/tashkeel stripping and
digit-glyph normalization (Eastern Arabic-Indic -> Western), matching this
corpus's established convention. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_service_regulation", "law", "official_source",
                   "civil_service_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "civil_service_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "civil_service_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "civil_service_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "civil_service_regulation_arabic_legal_llm",
                        "civil_service_regulation_legal_llm_001_261.json")

LAW_ID = "sa-civil-service-regulation-hr-1440"
LAW_AR = "اللائحة التنفيذية للموارد البشرية في الخدمة المدنية"
KEY_RE = r"civil_service_regulation_art_(\d{3})$"
TIER_BASELINE = "KSU_1440H_SINGLE_SOURCE_STRUCTURALLY_CROSS_CHECKED_VS_HRSD"
TIER_AMENDED = "HRSD_SINGLE_SOURCE_TEXT_LAYER_ARTIFACTS_MANUALLY_REVIEWED_LOWER_CONFIDENCE"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الجهة الحكومية الموظف الوزير المختص").split())


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
    return int(m.group(1))


GOV_NOTE = ("Arabic governs. 245/261 articles rest on a clean, uncorrupted single primary source "
            "(the Regulation's First Edition 1440H/2019G PDF, Adobe InDesign-produced, hosted at "
            "projects.ksu.edu.sa), structurally cross-checked (article count, chapter/فصل "
            "structure) against HRSD's own current portal -- no evidence of amendment. 16 articles "
            "(1, 9, 15, 26, 39, 94, 105, 127, 159, 160, 189, 198, 208, 212, 219, 224) carry a "
            "confirmed Ministerial Resolution amendment; their current text was manually extracted "
            "from HRSD's current PDF (which has a confirmed, non-reversible text-layer word-"
            "scrambling defect elsewhere in the document -- none was found in these specific "
            "amendment deltas after manual review) and is flagged at a distinctly lower confidence "
            "tier, single-source, with the pre-amendment 1440H text preserved in "
            "original_1440h_text. See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact -- especially the currency "
            "question of whether this Regulation (rather than the older 1397H implementing "
            "regulation) is truly the governing instrument -- before relying on this track.")

SRC_AUTH = ("Implementing Regulation for Human Resources in the Civil Service, First Edition "
            "1440H/2019G, Ministry of Human Resources and Social Development, issued under "
            "Article 39 of the Civil Service Law (Royal Decree M/49, 10/7/1397H) via the "
            "committee formed by Council of Ministers Resolution No. 75 (29/1/1440H). Baseline "
            "text: projects.ksu.edu.sa (clean single primary source, structurally cross-checked "
            "against HRSD). Amended-article current text: hrsd.gov.sa (single source, manually "
            "reviewed, lower confidence).")
SRC_AUTH_AR = ("اللائحة التنفيذية للموارد البشرية في الخدمة المدنية، الإصدار الأول 1440هـ/2019م، "
               "وزارة الموارد البشرية والتنمية الاجتماعية، صادرة استناداً إلى المادة (39) من نظام "
               "الخدمة المدنية عبر اللجنة المشكلة بقرار مجلس الوزراء رقم (75) وتاريخ 29/1/1440هـ. "
               "النص الأساسي: projects.ksu.edu.sa (مصدر أساسي منفرد نظيف، تحقق بنيوي مقابل "
               "hrsd.gov.sa). نص المواد المعدَّلة الحالي: hrsd.gov.sa (مصدر منفرد، مراجعة يدوية، "
               "ثقة أدنى).")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = _sort_key(key)
        ls = a.get("legal_status_ar")
        text = a["text"]
        original = a.get("original_1440h_text")
        suffix = key.replace("civil_service_regulation_art_", "")
        ver.append({"law_key": "civil_service_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "CIVIL_SERVICE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "original_1440h_text": original,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "civil-service-regulation-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "original_1440h_text": original,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "civil_service_regulation/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية للموارد البشرية في الخدمة المدنية"
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
    json.dump({"law_key": "civil_service_regulation",
               "layer": "CIVIL_SERVICE_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-civil-service-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (261 مادة؛ 245 أصلية، 16 معدلة)",
               "title_en": ("Implementing Regulation for Human Resources in the Civil Service — "
                            "Arabic LLM-ready layer (261 records: 245 original, 16 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 261], "text_status": "MIXED_TIER_SEE_PER_RECORD_STATUS",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Civil Service HR Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
