#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Electricity Law IMPLEMENTING REGULATION(S) track
(اللائحتان التنفيذيتان لنظام الكهرباء), covering BOTH instruments issued under Article 22
of the Electricity Law (Royal Decree M/44, 16/5/1442H):

  (1) the AUTHORITY'S part -- "اللائحة التنفيذية لنظام الكهرباء فيما يتعلق بمهمات هيئة
      تنظيم المياه والكهرباء" -- Water & Electricity Regulatory Authority Board Decision
      No. (43/02), dated 13/04/1443H (19 Nov 2021G as stated in-source), published Umm
      Al-Qura Gazette No. 4911 (3 Dec 2021G as stated in-source). 56 articles, 10 chapters.

  (2) the MINISTRY'S part -- "اللائحة التنفيذية لنظام الكهرباء الخاصة بمهمات الوزارة" --
      Minister of Energy Decision No. (1443/1728/01), dated 08/03/1443H (15 Oct 2021G as
      stated in-source), published Umm Al-Qura Gazette No. 4912 (10 Dec 2021G as stated
      in-source). 36 articles, 14 chapters.

STRUCTURE DECISION -- ONE combined track (electricity_regulation) with clear internal
sectioning, NOT two separate tracks. Both instruments issue from the SAME enabling clause
(Electricity Law Article 22, paragraphs 1 and 2) as a single co-designed regulatory
package implementing the same parent law, published one week apart in adjoining Umm
Al-Qura issues (4911/4912). They remain fully distinguishable within this one track: every
article record carries `instrument_part` ("authority"/"ministry"), `part_article_number`,
and `part_number_label_ar` alongside the combined track's own sequential `article_key`
(electricity_regulation_art_001..092, authority-part first [001-056], ministry-part second
[057-092] -- matching Umm Al-Qura publication order 4911 before 4912). See the source
artifact's `structure_decision_rationale_ar` for the full reasoning, including the
disclosed counter-consideration (two fully independent issuing authorities, decision
numbers, dates, and native per-instrument article numbering starting at 1 in each).

VERIFICATION TIER -- TIER_3 for both parts. laws.boe.gov.sa and sera.gov.sa were checked
FIRST per standard methodology but both reset the TCP/TLS connection this pass (matching
the pattern the base electricity_law track documented for the same period). uqn.gov.sa's
legacy `?p=NNNN` permalinks (cited by web search results) now resolve to the site's
redesigned homepage shell, not the original gazette content (confirmed by direct fetch and
independently via the r.jina.ai reader proxy -- both returned the same generic homepage,
containing no occurrence of "كهرباء"). Wayback Machine was blocked at the egress-policy
level for BOTH the content-serving path (web.archive.org) and the CDX metadata API
(web.archive.org/cdx/search/cdx -> HTTP 403 "Blocked by egress policy") this pass; neither
was circumvented. The full verbatim text of both instruments (56 + 36 = 92 articles) was
therefore extracted from qanoonsa.com, a clean born-digital HTML aggregator (NOT a
scanned/OCR document): qanoonsa.com/p/491109 (Authority-part full text) and
qanoonsa.com/p/491218 (Ministry-part full text). The official approval DECISIONS themselves
(qanoonsa.com/p/491108 and qanoonsa.com/p/491217) were also fetched directly -- these carry
the signing officials' names, Hijri+Gregorian signing dates, and Umm Al-Qura issue
numbers/dates in their own text, corroborating the governing metadata beyond a single
aggregator's say-so. The regulator's 2024 rename to the Saudi Electricity Regulatory
Authority (SERA) is independently confirmed this pass from ITS OWN ENABLING INSTRUMENT --
Council of Ministers Decision No. (918), dated 28 Shawwal 1445H, published Umm Al-Qura
issue 5032 -- fetched directly from qanoonsa.com/p/503201, stronger primary grounding than
the base law track had for the same fact. See the source artifact's
`verification_methodology_note`, `verbatim_normalization_note`, and
`known_unresolved_discrepancies` for the complete account, including an explicitly
UNCONFIRMED WebSearch claim of two later 1444H amendment decisions to the Authority's part
that could NOT be corroborated via qanoonsa.com's own site search or its Authority-tag
listing this pass -- NOT adopted; all 92 articles are treated as اصلية (original/
unamended) pending independent confirmation.

92 articles total (56 Authority-part + 36 Ministry-part); all 92 اصلية (no confirmed
amendments this pass); 0 معدلة, 0 ملغاة, 0 مضافة. Diacritics/tashkeel and decorative
kashida are stripped uniformly for consistency with this corpus's other BOE-family
tracks -- built from explicit Unicode codepoints (U+064B-065F, U+0670) rather than a naive
contiguous character-class range, specifically because a naive range would wrongly eat the
Arabic-Indic digits (U+0660-0669) this source uses natively for enumeration (unlike the
base law's ASCII-digit source). Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electricity_regulation", "law", "official_source",
                   "electricity_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "electricity_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "electricity_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "electricity_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "electricity_regulation_arabic_legal_llm",
                        "electricity_regulation_legal_llm_001_092.json")

LAW_ID = "sa-electricity-regulation-implementing-m44-1442"
DOC_AR = "اللائحتان التنفيذيتان لنظام الكهرباء"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"electricity_regulation_art_(\d{3})$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة الوزارة النظام المرخص الكهرباء الكهربائية الوزير المجلس").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [DOC_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    return int(m.group(1))


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


GOVERNING_NOTE = (
    "Arabic governs; this record belongs to ONE of the two implementing-regulation "
    "instruments issued under Article 22 of the Electricity Law (Royal Decree M/44, "
    "16/5/1442H) -- see this record's instrument_part field for which one. Both parts were "
    "checked against laws.boe.gov.sa and sera.gov.sa FIRST per standard methodology, but "
    "both reset the connection this pass; uqn.gov.sa's legacy permalinks now resolve to a "
    "redesigned homepage shell, not the original content; Wayback (content path AND CDX "
    "API) was egress-blocked and NOT circumvented. Full verbatim text extracted from "
    "qanoonsa.com (a single clean born-digital HTML aggregator per part, no scan/OCR/ "
    "ligature defects); the official approval decisions themselves were fetched directly "
    "and corroborate signing dates and gazette issue numbers. TIER_3. See "
    "verification_methodology_note, verbatim_normalization_note, and "
    "known_unresolved_discrepancies in the source artifact before relying on this track -- "
    "in particular the single-track-with-two-parts structure rationale, and the disclosed, "
    "NOT-adopted WebSearch claim of later amendments to the Authority's part."
)

SOURCE_AUTHORITY_AR = (
    "اللائحتان التنفيذيتان لنظام الكهرباء (م/44، 16/5/1442هـ، المادة 22): لائحة الهيئة "
    "بقرار مجلس إدارة هيئة تنظيم المياه والكهرباء رقم (43/02) وتاريخ 13/04/1443هـ (56 مادة، "
    "10 فصول)، ولائحة الوزارة بقرار وزير الطاقة رقم (1443/1728/01) وتاريخ 08/03/1443هـ (36 "
    "مادة، 14 فصلا). النص الحرفي من qanoonsa.com (مصدر نص كامل واحد لكل صك)؛ "
    "laws.boe.gov.sa وsera.gov.sa وuqn.gov.sa (الحي) غير قابلة للوصول هذه الجولة، وWayback "
    "محظور. جميع البيانات الوصفية متقاطعة عبر نصي قراري الاعتماد الرسميين المسحوبين مباشرة. "
    "المستوى TIER_3."
)

SOURCE_AUTHORITY_EN = (
    "The two Electricity Law implementing regulations (M/44, 16/5/1442H, Article 22): the "
    "Authority's part by Water & Electricity Regulatory Authority Board Decision No. "
    "(43/02) dated 13/04/1443H (56 articles, 10 chapters), and the Ministry's part by "
    "Minister of Energy Decision No. (1443/1728/01) dated 08/03/1443H (36 articles, 14 "
    "chapters). Verbatim text from qanoonsa.com (one full-text aggregator per part); "
    "laws.boe.gov.sa, sera.gov.sa, and uqn.gov.sa (live) unreachable this pass, Wayback "
    "egress-blocked. All governing metadata cross-verified via the official approval "
    "decisions' own text, fetched directly. TIER_3."
)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = _sort_key(key)
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        part = a["instrument_part"]
        ver.append({"law_key": "electricity_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ELECTRICITY_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "instrument_part": part,
                    "part_article_number": a["part_article_number"],
                    "part_number_label_ar": a["part_number_label_ar"],
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": GOVERNING_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        part_label_ar = next(p["part_label_ar"] for p in src["parts"] if p["part_key"] == part)
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "instrument_part": part,
                    "part_article_number": a["part_article_number"],
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "electricity-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s (%s) — %s" % (DOC_AR, part_label_ar, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (part_label_ar, a["number_label_ar"]),
                    "article_path": "electricity_regulation/law/%s/articles/%s" % (part, key),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": [
                        "%s %s" % (a["part_number_label_ar"], part_label_ar),
                        "%s %s" % (part_label_ar, a["part_number_label_ar"]),
                        "%s من اللائحة التنفيذية لنظام الكهرباء" % a["part_number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SOURCE_AUTHORITY_EN,
                                     "source_authority_ar": SOURCE_AUTHORITY_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": part_label_ar,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "electricity_regulation",
               "layer": "ELECTRICITY_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "legal_status_ar": src.get("legal_status_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "parts": src["parts"],
               "amendment_history": src.get("amendment_history", []),
               "track_structure_note_ar": src.get("track_structure_note_ar"),
               "structure_decision_rationale_ar": src.get("structure_decision_rationale_ar"),
               "verification_methodology_note": src["verification_methodology_note"],
               "verbatim_normalization_note": src.get("verbatim_normalization_note"),
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-electricity-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": (DOC_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (92 مادة: "
                            "56 لائحة الهيئة + 36 لائحة الوزارة؛ 92 أصلية، 0 معدلة، 0 مضافة، "
                            "0 ملغاة)"),
               "title_en": ("The Saudi Arabian Electricity Law Implementing Regulations "
                            "(Authority's part + Ministry's part) — Arabic LLM-ready layer "
                            "(92 records: 92 original, 0 amended, 0 added, 0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 92], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Electricity Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
