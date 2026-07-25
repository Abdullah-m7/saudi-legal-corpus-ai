#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law on Application of the Saudi
Building Code track (اللائحة التنفيذية لنظام تطبيق كود البناء السعودي, Ministerial
Decision No. (1213/Q/A/39), 14/10/1439H; amended by Ministerial Decision (56),
3/3/1441H; Ministerial Decision (00004), 8/1/1443H; and Ministerial Decision
(304), 8/7/1444H). Base law: building_code (sources/building_code/), already
tracked independently in this corpus.

VERIFICATION TIER -- see sources/building_code_regulation/law/official_source/
building_code_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE: momah.gov.sa -- the Ministry of Municipal, Rural Affairs and
Housing's OWN site (the entity administering the Code) -- hosts FOUR directly
fetchable PDFs of this Regulation (2021-06; 2022-03 filename-labeled "1443";
2024-09 filename-labeled "1444h"; 2025-10, current). Direct comparison of all
four covers and lead pages established they carry the SAME substantive decree
chain (founding decision + 56 + 00004 + 304) merely re-hosted under different
ministry branding (old SASO-era vs. post-merger "Ministry of Municipalities and
Housing" branding) and, for the 2025-10 file only, a richer inline per-article
amendment-tracking presentation (original text + every dated amendment box) --
NOT a fifth substantive amendment. This resolves the "two PDF versions" question
explicitly: same governing text, re-hosted/re-branded, reconciled rather than
assumed identical or different.

NUMBERING POLICY (important, disclosed at length in the source artifact and in
known_unresolved_discrepancies): Ministerial Decision (00004), 8/1/1443H,
comprehensively restructured the Regulation's Chapter 3-5 article numbering
(repealing two founding articles with no successor number, inserting one new
article on the Standards Authority's duties, net zero change to the total
count). This track uses the CURRENT (post-00004) sequential numbering 1-30 as
its stable key -- independently corroborated article-by-article against
qanoonsa.com's current-text rendition -- because this renumbering was done BY
THE ISSUING MINISTRY ITSELF, unlike this corpus's usual "never silently
renumber" precedent (which applies where no official renumbering occurred,
e.g. enforcement/law, sharia_procedure/law). The precise founding-1439H-to-
current article-by-article mapping for the affected range (current arts 8-23)
could not be fully and confidently reconstructed from the source's own
internal cross-reference boxes alone -- disclosed, not guessed.

30 articles across 7 chapters + an implementation-phases appendix: 15 اصلية,
13 معدلة, 0 ملغاة (two founding articles were repealed with no surviving
numbered slot in the current sequence -- their repealed text is preserved
verbatim in known_unresolved_discrepancies per this corpus's never-delete
policy, but they do not occupy one of the 30 current keys), 2 مضافة (the
Standards-Authority-duties article inserted by decision 00004, and the
ten-year joint-liability article added by decision 56).

DISCLOSED, NOT SILENTLY RESOLVED: a likely FIFTH amendment (replacing "National
Committee"/"Minister of Commerce" with "Saudi Building Code Center"/"Minister
of Municipalities and Housing" in the code-update articles, paralleling the
parent law's own Royal Decree M/204 amendment) is indicated by secondary
evidence (an aggregator site's current wording, 2026 news coverage of a
Center-board-approved amendment) but could NOT be independently confirmed from
a primary Umm al-Qura Gazette source this pass (uqn.gov.sa's detail pages, and
the web.archive.org content-serving path, were both inaccessible this
session). This track does NOT incorporate that unverified amendment; Articles
24/25 store the last text independently confirmed from momah.gov.sa itself.

Tashkeel stripped uniformly (corpus-majority convention); curly/guillemet
quotes straightened; double/nbsp spaces removed -- display-layer only, no legal
text altered. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "building_code_regulation", "law", "official_source",
                   "building_code_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "building_code_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "building_code_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "building_code_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "building_code_regulation_arabic_legal_llm",
                        "building_code_regulation_legal_llm_001_030.json")

LAW_ID = "sa-building-code-regulation-1213-1439"
LAW_AR = "اللائحة التنفيذية لنظام تطبيق كود البناء السعودي"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"building_code_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون فيما منه منها "
            "وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها إليه عليها "
            "منهم بينهم الكود الجهات ذات العلاقة الوزارة الجهاز البلدي").split())


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


def _top_status(a):
    ls = a.get("legal_status_ar")
    if ls == "معدلة":
        return STATUS_AMENDED
    if ls == "مضافة":
        return STATUS_ADDED
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; PRIMARY source is momah.gov.sa (the Ministry of Municipal, Rural "
            "Affairs and Housing's own site -- the entity administering the Code), which hosts "
            "FOUR directly-fetchable PDFs of this Regulation (2021-06; 2022-03 'v1443'; 2024-09 "
            "'v1444h'; 2025-10 current). All four were directly compared and found to carry the "
            "SAME decree chain (founding Ministerial Decision 1213/Q/A/39 [14/10/1439H] + Decision "
            "56 [3/3/1441H] + Decision 00004 [8/1/1443H] + Decision 304 [8/7/1444H]) merely "
            "re-hosted under evolving ministry branding, with the 2025-10 file additionally adding "
            "a richer inline per-article amendment-tracking presentation -- NOT a fifth amendment. "
            "This track uses the CURRENT (post-Decision-00004) sequential numbering 1-30 as its "
            "stable key, independently corroborated article-by-article against qanoonsa.com's "
            "current-text rendition, because the ISSUING MINISTRY ITSELF renumbered the Regulation "
            "via Decision 00004 (a comprehensive Chapter 3-5 restructuring: two founding articles "
            "repealed with no surviving numbered slot, one new article on Standards Authority "
            "duties inserted). The precise founding-1439H-to-current mapping for the heavily "
            "cross-referenced range (current articles 8-23) could not be fully reconstructed with "
            "confidence from the source's own internal renumbering boxes alone -- disclosed, not "
            "guessed. A likely FIFTH amendment (paralleling the parent law's own Royal Decree "
            "M/204: 'National Committee'/'Minister of Commerce' -> 'Saudi Building Code Center'/"
            "'Minister of Municipalities and Housing') is indicated by secondary evidence but was "
            "NOT independently confirmed from a primary Umm al-Qura Gazette source this pass "
            "(uqn.gov.sa detail pages and the web.archive.org content-serving path were both "
            "inaccessible this session) and is therefore NOT incorporated -- Articles 24/25 store "
            "the last text confirmed directly from momah.gov.sa. See verification_methodology_note "
            "and known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance, including the verbatim preserved text of the two repealed "
            "founding articles that no longer occupy a current numbered slot.")

SRC_AUTH_AR = ("القرار الوزاري رقم (1213/ق/أع/39) وتاريخ 14/10/1439هـ، عن وزير التجارة والاستثمار "
               "رئيس مجلس إدارة الهيئة السعودية للمواصفات والمقاييس والجودة؛ عدل بالقرار الوزاري رقم "
               "(56) وتاريخ 3/3/1441هـ، والقرار الوزاري رقم (00004) وتاريخ 8/1/1443هـ (إعادة هيكلة "
               "شاملة للترقيم)، والقرار الوزاري رقم (304) وتاريخ 8/7/1444هـ. أربع نسخ PDF مستضافة "
               "مباشرة على momah.gov.sa (2021-06؛ 2022-03؛ 2024-09؛ 2025-10) متطابقة المضمون "
               "القانوني؛ الترقيم النهائي (1-30) مؤكد بمطابقة مستقلة من qanoonsa.com مادة بمادة.")
SRC_AUTH_EN = ("Ministerial Decision No. (1213/Q/A/39) dated 14/10/1439H, by the Minister of "
               "Commerce and Investment, Chairman of the Board of the Saudi Standards, Metrology "
               "and Quality Organization; amended by Ministerial Decision (56) [3/3/1441H], "
               "Ministerial Decision (00004) [8/1/1443H, comprehensive renumbering], and "
               "Ministerial Decision (304) [8/7/1444H]. Four PDFs hosted directly on momah.gov.sa "
               "(2021-06; 2022-03; 2024-09; 2025-10) carry identical substantive text; the final "
               "numbering (1-30) is independently corroborated article-by-article via qanoonsa.com.")


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
        top_status = _top_status(a)
        ver.append({"law_key": "building_code_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "BUILDING_CODE_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "building-code-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "building_code_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام تطبيق كود البناء السعودي" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH_EN,
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
    json.dump({"law_key": "building_code_regulation",
               "layer": "BUILDING_CODE_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-building-code-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ 15 أصلية، 13 معدلة، 2 مضافة)",
               "title_en": ("Implementing Regulation of the Law on Application of the Saudi "
                            "Building Code — Arabic LLM-ready layer (30 records: 15 original, "
                            "13 amended, 2 added, 0 repealed-with-current-slot)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS_AMENDED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Building Code Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
