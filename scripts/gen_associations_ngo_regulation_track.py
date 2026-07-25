#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law of Associations and Civil
Institutions track (اللائحة التنفيذية لنظام الجمعيات والمؤسسات الأهلية,
"محدثة 2025", NCNP Board Resolution No. Q/2/1/2022, 22/3/1444H, amended four
times through 26/7/1447H).

VERIFICATION TIER -- see sources/associations_ngo_regulation/law/
official_source/associations_ngo_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the official PDF (56 pages) hosted directly by the issuing
body itself -- the National Center for the Non-Profit Sector (NCNP,
ncnp.gov.sa) -- fetched directly this pass (HTTP 200) from the page titled
"اللائحة التنفيذية لنظام الجمعيات والمؤسسات الأهلية 'محدثة 2025'".

FONT/CMAP DEFECT DISCOVERED: this PDF's embedded text layer (ToUnicode CMap
for some embedded font subsets) corrupts SOME (not all) Arabic letter runs
under automated extraction (pdftotext, PyMuPDF) -- an inconsistent
letter-substitution defect (e.g. ع<->ل, ث<->ل/ن, ص<->ذ, ي<->و in some but not
all occurrences), the same category of defect documented for a different PDF
in this corpus's zakat track. Digits, page/article structural markers, and
some boilerplate runs (Article 1's definitions) are NOT affected. Because no
single global substitution cipher could safely repair this, verification
instead relied on DIRECT VISUAL READING of 300dpi page-image renders of the
SAME official PDF (by this track's builder agent for the cover page and
Articles 1-29, and by four independent sub-agents for the remaining page
ranges 11-23, 24-37, 38-50 and 51-56, with overlapping boundary articles
cross-checked and one transcription slip caught and corrected via a targeted
re-read of the source page). This exact pattern -- one official PDF verified
via an independent OCR/page-image pass of the SAME document -- is the
TIER_1-qualifying pattern documented in this corpus's own
reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md (section 4,
citing the HRSD precedent). Independent secondary corroboration: qanoonsa.com
confirms the founding decision's number/date/gazette citation; this
regulation's own Article 127 names the exact predecessor decree (Ministerial
Resolution 73739, 11/6/1437H) independently documented in this corpus's
associations_ngo (base law) track.

129 articles, ALL classified اصلية: the source publishes only a fully
consolidated current text with cover-page-level (not article-level) citation
of the 5 instruments (1 founding + 4 amending resolutions) -- no article can
be honestly marked "معدلة" without fabricating that attribution, per this
corpus's no-fabrication rule. consolidated_amended_law = true; the 5
instruments are recorded in amendment_history at the document level.

STRUCTURE: 129 articles across 5 "أبواب" (chapters) -- confirmed a GENUINE
source-level anomaly via direct visual reading (not a corrupted-extraction
artifact): the chapter number "الباب الثاني" is used TWICE in the official
PDF itself (once for "الجمعيات الأهلية" arts 3-40, again for "المؤسسات
الأهلية" arts 41-70) before the numbering continues to "الباب الثالث" (arts
71-87, no فصول), "الباب الرابع" (arts 88-112, 2 فصول) and "الباب الخامس"
(arts 113-129, no فصول). chapter_structure preserves this duplicate labeling
verbatim -- not silently renumbered.

Article 73 and Article 114 each carry a genuine numbering gap in the
official source (73's list starts at item 4 with no items 1-3 anywhere;
114's lettered list jumps from the lead-in straight to item "ب" with no item
"أ") -- confirmed by close re-inspection and, for Article 73, by comparison
against its near-verbatim mirror Article 90. Transcribed exactly as printed,
not silently completed.

Article 127 EXPLICITLY repeals the prior Implementing Regulation (Ministerial
Resolution No. 73739, 11/6/1437H) -- a genuine named repeal link, flagged for
the corpus-wide supersession/repeal graph (the repealed predecessor is not
itself ingested as a separate track). Article 129 (the final article) is the
publication/90-day effective-date clause.

TASHKEEL stripped uniformly (corpus-majority convention); the Hijri-era
marker "هـ" is preserved (not stripped) as it is a meaningful marker, not
decorative tatweel. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "associations_ngo_regulation", "law", "official_source",
                   "associations_ngo_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "associations_ngo_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "associations_ngo_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "associations_ngo_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "associations_ngo_regulation_arabic_legal_llm",
                        "associations_ngo_regulation_legal_llm_001_129.json")

LAW_ID = "sa-associations-ngo-regulation-ncnp-q212022-1444"
LAW_AR = "اللائحة التنفيذية لنظام الجمعيات والمؤسسات الأهلية"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"associations_ngo_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم المركز المجلس حالة حالات الجمعية المؤسسة").split())


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


GOV_NOTE = ("Arabic governs; this track's primary source is the official PDF hosted directly "
            "by the issuing body (NCNP, ncnp.gov.sa) -- fetched directly (HTTP 200). That PDF's "
            "embedded text layer carries a font/ToUnicode-CMap defect that corrupts some (not "
            "all) Arabic letter runs under automated extraction, so verification instead relied "
            "on direct visual reading of 300dpi page-image renders of the SAME official "
            "document (self + four independent sub-agents covering non-overlapping page ranges, "
            "with boundary articles cross-checked and one transcription slip caught and "
            "corrected) -> TIER_1 per this corpus's own documented pattern (official PDF + "
            "independent OCR/page-image verification pass of the same document). 129 articles "
            "across 5 chapters; the source itself reuses the chapter number 'الباب الثاني' "
            "twice (Associations, then Institutions) before continuing to 'الباب الثالث' -- a "
            "genuine source-level numbering anomaly, preserved verbatim. All 129 articles are "
            "classified اصلية: the source publishes only a fully consolidated current text with "
            "cover-page-level (not article-level) citation of 5 instruments (1 founding + 4 "
            "amending resolutions), so no article can be honestly marked معدلة without "
            "fabricating that attribution. Article 127 EXPLICITLY repeals the prior Implementing "
            "Regulation (Ministerial Resolution 73739, 11/6/1437H) -- flagged for the "
            "corpus-wide supersession graph. Articles 73 and 114 each carry a genuine numbering "
            "gap in the official source (confirmed, not a transcription artifact). See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance.")

SRC_AUTH = ("NCNP Board Resolution No. (Q/2/1/2022), 22/3/1444H (18/10/2022G; Umm al-Qura "
            "Gazette No. 4968, 3 Feb 2023G), amended by four further NCNP Board resolutions "
            "dated 10/6/1444H, 19/3/1445H, 19/6/1447H and 26/7/1447H (the 'محدثة 2025' "
            "consolidated text). Full text from the official ncnp.gov.sa PDF, verified via "
            "direct visual reading of the same document's page images (font/CMap extraction "
            "defect documented) plus independent corroboration from qanoonsa.com for the "
            "founding decision's identity/date/gazette citation -> TIER_1")

SRC_AUTH_AR = ("قرار مجلس إدارة المركز الوطني لتنمية القطاع غير الربحي رقم (ق/2/1/2022) وتاريخ "
               "22/3/1444هـ (الموافق 18/10/2022م؛ جريدة أم القرى العدد 4968، 3 فبراير 2023م)، "
               "المعدل بأربعة قرارات لاحقة بتواريخ 10/6/1444هـ و19/3/1445هـ و19/6/1447هـ "
               "و26/7/1447هـ (النسخة المدمجة 'محدثة 2025'). النص الكامل من ملف PDF الرسمي على "
               "ncnp.gov.sa، متحقق منه بالقراءة البصرية المباشرة لصور صفحات المستند نفسه (مع "
               "توثيق عيب في طبقة النص الرقمية)، وتحقق مستقل إضافي عبر qanoonsa.com لهوية "
               "القرار المؤسس وتاريخه ونشره -- TIER_1")


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
        ver.append({"law_key": "associations_ngo_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ASSOCIATIONS_NGO_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "associations-ngo-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "associations_ngo_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الجمعيات والمؤسسات "
                                          "الأهلية" % a["number_label_ar"]],
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
    json.dump({"law_key": "associations_ngo_regulation",
               "layer": "ASSOCIATIONS_NGO_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-associations-ngo-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " (محدثة 2025) — الطبقة العربية الجاهزة للنماذج اللغوية "
                            "(129 مادة، جميعها أصلية)",
               "title_en": ("Implementing Regulation of the Law of Associations and Civil "
                            "Institutions ('updated 2025') — Arabic LLM-ready layer (129 "
                            "records, all اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 129], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Associations/NGO Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
