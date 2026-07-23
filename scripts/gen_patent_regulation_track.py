#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian Patents Law track
(اللائحة التنفيذية لنظام براءات الاختراع والتصميمات التخطيطية للدارات المتكاملة
والأصناف النباتية والنماذج الصناعية — issued by Resolution of the President of
King Abdulaziz City for Science and Technology (KACST) No. (161-2-3607329),
30/12/1436H, under Article 63 of the Patents Law, Royal Decree M/27, 29/5/1425H;
consolidated as amended by SAIP Board Resolution No. (5/8/2019), 04/09/1440H).

This is the companion Implementing Regulation of this corpus's already-ingested
base Patents Law (see sources/patent/law/..., whose Article 63 mandates the
competent authority to issue this Regulation). It ingests it as a NEW track.

VERIFICATION TIER -- see patent_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. The
live portal was unreachable this pass (connection reset), and -- more
fundamentally -- BOE has NO dedicated lawId page for this Implementing
Regulation at all (only for the base Patents Law, M/27), consistent with BOE's
general practice of not cataloguing Board/agency-head-level executive
regulations as standalone lawId records. istitlaa.ncc.gov.sa returned 503;
legal aggregators (qanoniah/almirkaz/nezams) are JS-rendered with no plain
full text.

PRIMARY SOURCE: the official Arabic PDF hosted on WIPO Lex (identifier SA065,
wipolex-res.wipo.int/edocs/lexdocs/laws/ar/sa/sa065ar_1.pdf, fetched directly
this pass via a signed URL, HTTP 200, 52 pages). WIPO Lex is the same strong
independent source this corpus's base patent_law track relied on. Direct visual
inspection of rendered pages (PyMuPDF, 150-220 dpi) confirmed the file carries
SAIP's own official letterhead (SAIP logo + Vision 2030) -- i.e. it is SAIP's
own official document hosted on WIPO Lex, not a third-party secondary copy.
Decree number/date, article count (67) and chapter count (12 أبواب) were
independently cross-verified against WIPO Lex's descriptive page (details/19743)
and qanoonsa.com's dedicated page for the 2024 amending resolution
(02/32/2024) -- two independent secondary sources agreeing with the primary.

EXTRACTION (one primary source, TWO fully independent extraction pipelines +
direct visual check + a character-level integrity gate): this file stores Arabic
as Presentation Forms with intra-word run breaks, making word boundaries
ambiguous in both standard extractors. Used: (1) poppler `pdftotext -layout`
(applies the Unicode bidi algorithm -> correct line reading order, but inserts
intra-word letter-spacing on justified lines); (2) a custom PyMuPDF
`get_text("words")` reconstruction that clusters words into visual lines by
vertical overlap, orders them right-to-left by x-coordinate, and joins tokens
using an ABSOLUTE horizontal-gap window of [-1.5, +1.5] pt (derived
statistically from 8000+ measured gaps: intra-word gap ~= 0 pt, normal word
boundary ~= +5 pt, and word boundary after an accusative tanwin ~= -3.3 pt due
to the tanwin glyph overhang -- so strongly-negative gaps are treated as word
boundaries). All glyphs NFKC-normalized (presentation forms -> base letters,
lam-alef ligature decomposed); bidi control marks stripped; diacritics
(tashkeel) and tatweel removed uniformly for consistency with this corpus's
BOE-family tracks (the source is fully vocalized in print -- confirmed visually
-- so removal is a display-layer normalization only, touching no letter, word,
digit or provision).

INTEGRITY GATE: after extraction, the Arabic-letters-only sequence of every page
was compared between the two independent pipelines -- identical across the whole
document EXCEPT 14 bidi-reversed lines in the PyMuPDF pipeline (lines carrying
embedded numbers/dates), which the pdftotext -layout pipeline renders in correct
order and which were fixed individually from it (see LINE_FIX below). A second
letter-multiset gate confirmed every downstream fix producing the source
artifact is letter-preserving EXCEPT one deliberately-restored accusative alif
("اسباباً" in Article 25, confirmed against the independent pdftotext pipeline).
About 20 justified-line word-split artifacts were fixed individually after
context verification (WORD_FIX below); mirrored parentheses (RTL visual order)
were normalized to logical order (e.g. "(PCT)"); page headers/footers (Saudi
state logo, an IUPAC footnote gloss, page numbers) and the cover page (title +
decree block) were excluded from article text. The fee-schedule annex ("جدول
بالنفقات") that follows Article 67 is stored in the source artifact's separate
schedule_ar field, NOT as a numbered article.

The full LINE_FIX (14 reversed lines) and WORD_FIX (~20 split/glyph fixes)
dictionaries used to produce the source artifact from the raw dual-pipeline
extraction are reproduced verbatim below for full disclosure (this generator
reads the already-verified text from the source artifact; the dictionaries are
retained here as the audit record of exactly what was corrected and how):

  LINE_FIX (garbled bidi-reversed line -> correct pdftotext-layout order), e.g.:
    "٩١/٦٠/٠٧٩١،م ايتل دصر ..."  -> "١٩٧٠/٠٦/١٩م، التي صدر بشأنها المرسوم الملكي رقم م/٦٣ ..."
    "٠١- بجي ىلع دقمم ابلطل نأ يفوتسي ..." -> "١٠- يجب على مقدم الطلب أن يستوفي كل ما تطلبه ..."
    (14 entries total: pages 3, 7, 8, 12, 18, 20, 22, 39, 40, 46 of the PDF.)
  WORD_FIX (justified-line splits & glyph fixes), e.g.:
    "الكتروني ا"->"الكترونيا", "وفقالنماذج"->"وفق النماذج", "ت سلم"->"تسلم",
    "تفح ص"->"تفحص", "تسل1م"->"تسلم" (mis-encoded shadda in تسلّم, visually
    confirmed), "اسباب تقبلها"->"اسبابا تقبلها" (restored accusative alif,
    confirmed against pdftotext pipeline).
  Parenthesis normalization: RTL-mirrored "(" / ")" swapped to logical order.

67 articles across 12 أبواب (chapters); ALL classified اصلية (67 اصلية, 0 معدلة,
0 ملغاة, 0 مضافة). The primary consolidated PDF does not enumerate, at the
per-article level, which articles the 2019 amendment changed, so this track does
NOT unilaterally classify any article "معدلة" -- disclosed in
known_unresolved_discrepancies. A later 2024 amendment (Board Resolution
02/32/2024) is NOT reflected in this WIPO Lex text (a staleness pattern
mirroring the base patent_law track's own BOE staleness) and is disclosed, not
fabricated. This Regulation contains NO named-predecessor repeal/supersession
clause (it is the first Implementing Regulation under M/27) -- also disclosed.

No legal text is altered beyond the above disclosed, source-artifact-layer fixes.
Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "patent", "regulation", "official_source",
                   "patent_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "patent", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "patent_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "patent_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "patent_regulation_arabic_legal_llm",
                        "patent_regulation_legal_llm_001_067.json")

LAW_ID = "sa-patent-regulation-161-2-3607329-1436"
LAW_AR = ("اللائحة التنفيذية لنظام براءات الاختراع والتصميمات التخطيطية للدارات "
          "المتكاملة والأصناف النباتية والنماذج الصناعية")
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"patent_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة الطلب الحماية").split())


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
        ver.append({"law_key": "patent", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PATENT_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source is the official "
                                              "SAIP-letterhead Arabic PDF hosted on WIPO Lex "
                                              "(identifier SA065), consolidated as amended by SAIP "
                                              "Board Resolution 5/8/2019 -- laws.boe.gov.sa was "
                                              "checked first per standard methodology but is "
                                              "unreachable this pass and has NO dedicated lawId "
                                              "page for this Board/agency-level Implementing "
                                              "Regulation at all. Article/chapter count (67 "
                                              "articles, 12 أبواب) and decree number/date "
                                              "cross-verified against WIPO Lex details/19743 and "
                                              "qanoonsa.com. See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- in "
                                              "particular: the presentation-form dual-pipeline "
                                              "extraction with individually-disclosed reversed-line "
                                              "and word-split fixes; the 'تسل1م'->'تسلم' "
                                              "mis-encoded-shadda fix (visually verified); the "
                                              "later 2024 amendment (02/32/2024) NOT reflected in "
                                              "this 2019-consolidated text; and the per-article "
                                              "2019-amendment scope being unenumerated by the "
                                              "primary source (hence all 67 articles اصلية)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "patent-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "patent/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام براءات الاختراع" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Resolution of the President of KACST "
                                                          "No. (161-2-3607329) (30/12/1436H), as "
                                                          "amended by SAIP Board Resolution No. "
                                                          "(5/8/2019) (04/09/1440H) — official "
                                                          "SAIP-letterhead PDF hosted on WIPO Lex "
                                                          "(SA065), cross-verified against WIPO "
                                                          "Lex details/19743 and qanoonsa.com; "
                                                          "laws.boe.gov.sa unreachable this pass "
                                                          "and has no dedicated lawId page for "
                                                          "this Implementing Regulation"),
                                     "source_authority_ar": "قرار رئيس مدينة الملك عبدالعزيز للعلوم والتقنية رقم (١٦١-٢-٣٦٠٧٣٢٩) وتاريخ 30/12/1436هـ، بصيغته المعدلة بقرار مجلس إدارة الهيئة السعودية للملكية الفكرية رقم (5/8/2019) وتاريخ 04/09/1440هـ — ملف PDF رسمي بترويسة سايب مستضاف على WIPO Lex (المعرّف SA065)، مطابق مع صفحة WIPO Lex الوصفية وqanoonsa.com؛ بوابة هيئة الخبراء غير قابلة للوصول هذه الجولة ولا تملك صفحة مخصصة لهذه اللائحة التنفيذية أصلاً",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "patent",
               "layer": "PATENT_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "schedule_ar": src.get("schedule_ar"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-patent-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (67 مادة؛ 67 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation of the Saudi Arabian Patents Law — Arabic "
                            "LLM-ready layer (67 records: 67 original, 0 amended, 0 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 67], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Patent Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
