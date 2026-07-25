#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Weapons and Ammunition Law track
(اللائحة التنفيذية لنظام الأسلحة والذخائر, Ministerial Resolution No. 23,
19/1/1428H; published Umm al-Qura issue 4159, 13/7/1428H).

STRUCTURAL NOTE -- this Regulation carries NO independent article numbering of
its own. It is organized entirely as implementing provisions cross-referenced
to the PARENT LAW's own article numbers (the source's own convention: "(5ل)"
means "the Implementing Regulation for [Law] Article Five"). Of the parent
Law's 63 articles, only 19 carry attached regulation text in this source
(1, 5, 8, 9, 10, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 32).
Article 3's regulation content was moved in full to Article 9's regulation by
Ministerial Resolution 5656 (1442H) and is therefore NOT a separate record.

VERIFICATION TIER -- see sources/weapons_ammunition_regulation/law/
official_source/weapons_ammunition_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: a 63-page compiled PDF from qadha.org.sa (Saudi Judicial
Scientific Society) titled "نظام الأسلحة والذخائر ولائحته التنفيذية", fetched
directly (HTTP 200). This PDF's embedded digital text layer is SYSTEMICALLY
CORRUPTED (a font/ToUnicode-CMap bug that transposes/drops specific Arabic
letters around the definite article and several common function words --
e.g. "المادة" extracts as "املادة", "في" as "يف", "على" as "عى" -- verified
empirically by diffing PyMuPDF's raw extraction against Tesseract OCR of the
same rasterized pages across all 63 pages). Digits are NOT affected by this
bug (verified by direct visual inspection of cropped page images for every
resolution number/date cited below).

RECOVERY METHOD: each page was rasterized (300dpi) and OCR'd (Tesseract,
Arabic), and the OCR text (which reads the actual drawn glyph shapes, not the
broken codepoint map) was used as the base text for every article, with all
digits cross-verified against PyMuPDF's raw digit extraction (unaffected by
the bug) and, for administrative facts, against direct visual crops of the
source PDF.

CROSS-CHECKS: qanoonsa.com (independent legal aggregator, clean non-OCR HTML)
supplied a verbatim match for Articles 3 and 5's regulation text, corroborating
the OCR-recovery methodology. uqn.gov.sa (the official Umm al-Qura gazette API)
directly confirmed the Regulation's own issuance facts (issue 4159, date
13/7/1428H, appearing independently within the source's own back-matter too)
and -- critically -- surfaced a FIFTH amendment (Minister of Interior
Resolution No. 1938, 10/4/1446H, published 29/4/1446H / ~1 Nov 2024) that is
NOT present in the qadha.org.sa compiled PDF (whose cover states a 4/1/1446H
update, predating this resolution) and was NOT part of the four amendments
known from prior research. This 5th amendment is disclosed in full and its
text (a new medical/toxicology exam requirement under Article 9's licensing
conditions) is incorporated into Article 9's current text.

NOT TIER_2 (unlike the sibling weapons_ammunition law track) because: (a) the
primary source's digital text layer required OCR reconstruction rather than
being cleanly machine-readable; (b) full independent full-text cross-checks
were available for only 2 of 19 articles; (c) the source itself carries an
internal conflict on the founding resolution's own number (23 vs 33, both
appearing in different parts of the SAME compiled document -- resolved in
favor of 23, the preamble's own text, appearing in two of three internal
citations); (d) most regulation-level amendments in this source are described
only as "amended by adding a number of clauses" WITHOUT the pre-amendment
wording being preserved, so most history[] entries carry amendment_current
only, not a paired original; (e) Ministerial Resolution 549 (1446H) is
explicitly marked "غير سارية" (not yet in force) in the source's own registry
AND its added Article-23 clause is explicitly captioned "لمّا تسرِ بعد" (has
not yet taken effect) -- disclosed rather than silently treated as settled
law. TIER_3.

19 records: 7 اصلية (arts 1, 13, 15, 20, 21, 22, 27), 12 معدلة (arts 5, 8, 9,
10, 12, 18, 19, 23, 24, 25, 28, 32), 0 ملغاة, 0 مضافة.

TASHKEEL: OCR-introduced diacritics/tatweel stripped programmatically. No
translation/paraphrase/interpretation of the governing Arabic text (the one
interpretive act -- adopting OCR-recovered readings over the corrupted PDF
text layer -- is a technical recovery method, not a legal interpretation, and
is fully disclosed). Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "weapons_ammunition_regulation", "law", "official_source",
                   "weapons_ammunition_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "weapons_ammunition_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "weapons_ammunition_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "weapons_ammunition_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "weapons_ammunition_regulation_arabic_legal_llm",
                        "weapons_ammunition_regulation_legal_llm_001_019.json")

LAW_ID = "sa-weapons-ammunition-regulation-res-23-1428"
LAW_AR = "اللائحة التنفيذية لنظام الأسلحة والذخائر"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_AMENDED_PENDING = "AMENDED_PENDING_NOT_YET_EFFECTIVE"
KEY_RE = r"weapons_ammunition_regulation_art_(\d{3})$"

AMENDED_KEYS = {
    "weapons_ammunition_regulation_art_005",
    "weapons_ammunition_regulation_art_008",
    "weapons_ammunition_regulation_art_009",
    "weapons_ammunition_regulation_art_010",
    "weapons_ammunition_regulation_art_012",
    "weapons_ammunition_regulation_art_018",
    "weapons_ammunition_regulation_art_019",
    "weapons_ammunition_regulation_art_023",
    "weapons_ammunition_regulation_art_024",
    "weapons_ammunition_regulation_art_025",
    "weapons_ammunition_regulation_art_028",
    "weapons_ammunition_regulation_art_032",
}
PENDING_KEYS = {"weapons_ammunition_regulation_art_023"}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزير الوزارة رخصة رخص إنفاذاً للمادة").split())


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


def _top_status(key):
    if key in PENDING_KEYS:
        return STATUS_AMENDED_PENDING
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs. Primary source: a 63-page compiled PDF from qadha.org.sa whose embedded "
            "digital text layer is systemically corrupted (font/CMap bug transposing/dropping specific "
            "Arabic letters); text was recovered via Tesseract OCR of rasterized pages (verified against "
            "PyMuPDF's raw digit extraction, which is unaffected by the bug, and against direct visual "
            "crops for every cited resolution number/date). Cross-checked against qanoonsa.com (clean "
            "HTML, arts 3 & 5 verbatim match) and uqn.gov.sa (official gazette API, issuance facts + a "
            "5th amendment -- Ministerial Resolution 1938, 10/4/1446H -- not present in the qadha.org.sa "
            "PDF and not part of the four amendments known from prior research) -> TIER_3. Ministerial "
            "Resolution 549 (1446H) is marked 'غير سارية' (not in force) in the source's own registry and "
            "its Article-23 addition is explicitly captioned 'has not yet taken effect'. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source artifact "
            "before relying on this track's text or provenance.")

SRC_AUTH = ("Ministerial Resolution No. 23 (19/1/1428H), published Umm al-Qura gazette issue 4159 "
            "(13/7/1428H); amended by Ministerial Resolutions 3499 (14/4/1434H, superseded), 274833 "
            "(1/11/1437H), 5656 (6/5/1442H, broad), 549 (4/2/1446H, marked not-yet-effective in the "
            "source's own registry), and Minister of Interior Resolution 1938 (10/4/1446H, independently "
            "discovered via uqn.gov.sa, not in the primary compiled PDF). Full text recovered via OCR of "
            "the qadha.org.sa compiled PDF (corrupted digital text layer) cross-checked against "
            "qanoonsa.com and uqn.gov.sa -> TIER_3")

SRC_AUTH_AR = ("القرار الوزاري رقم 23 وتاريخ 19/1/1428هـ، منشور بجريدة أم القرى العدد 4159 وتاريخ "
               "13/7/1428هـ؛ عُدّلت اللائحة بالقرارات الوزارية 3499 (1434هـ، مستبدل لاحقاً) و274833 "
               "(1437هـ) و5656 (1442هـ، واسع النطاق) و549 (1446هـ، مُصنَّف غير سارٍ في سجل المصدر نفسه) "
               "وقرار وزير الداخلية 1938 (1446هـ، اكتُشف بتحقق مستقل من uqn.gov.sa، غير مذكور في PDF "
               "المصدر الأساسي). النص الكامل استُرجع بتقنية OCR من ملف qadha.org.sa المُجمَّع (طبقة نص "
               "رقمي معطوبة) وقُوطع مع qanoonsa.com وuqn.gov.sa -- TIER_3")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        law_n = int(a["law_article_number"])
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        ver.append({"law_key": "weapons_ammunition_regulation", "law_component": "regulation",
                    "parent_law_key": "weapons_ammunition",
                    "language": "ar",
                    "record_layer": "WEAPONS_AMMUNITION_REGULATION_ARABIC_VERIFIED_TEXT",
                    "sequence_number": idx, "law_article_number": law_n, "is_mukarrar": False,
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
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "parent_law_key": "weapons_ammunition",
                    "article_number": idx, "sequence_number": idx, "law_article_number": law_n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "weapons-ammunition-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "weapons_ammunition_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "لائحة المادة %d من نظام الأسلحة والذخائر" % law_n],
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
    json.dump({"law_key": "weapons_ammunition_regulation",
               "layer": "WEAPONS_AMMUNITION_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "law_article_keys_with_regulation_text": src["law_article_keys_with_regulation_text"],
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-weapons-ammunition-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation", "parent_law_key": "weapons_ammunition",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 سجلاً؛ 7 أصلية، 12 معدلة)",
               "title_en": ("Implementing Regulation of the Weapons and Ammunition Law — Arabic LLM-ready "
                            "layer (19 records: 7 original, 12 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "law_article_keys_with_regulation_text": src["law_article_keys_with_regulation_text"],
               "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Weapons and Ammunition Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
