#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Travel Documents Implementing Regulation track
(اللائحة التنفيذية لنظام وثائق السفر, Ministerial Resolution No. 4203, 1447H
/ published Umm Al-Qura Gazette No. 5151, 30 March 2026G), the companion
Implementing Regulation to the travel_documents_law track's Article 14
requirement (Royal Decree M/24, 28/5/1421H) -- flagged by that track's own
official_source.json as "NOT ingested this pass" pending this dedicated pass.

VERIFICATION TIER -- see sources/travel_documents/regulation/official_source/
travel_documents_regulation_official_source.json's verification_methodology_note
for the full account. Summary (be conservative -- honest TIER_3, NOT inflated):

ACCESS ATTEMPTS, IN THE ORDER THIS CORPUS'S METHODOLOGY REQUIRES: (1)
laws.boe.gov.sa -- multi-query search found NO dedicated lawId page at all for
this Implementing Regulation, current (4203) or superseded (7/waw-zay,
1422H); direct curl also failed with a TLS connection error (exit 35), the
same recurring pattern documented for this exact portal elsewhere in this
corpus. (2) moi.gov.sa / legacy.moi.gov.sa (the issuing Ministry) -- both
unreachable this pass (TLS connection failure), independently reconfirming
the travel_documents_law track's own finding for the same domain. gdp.gov.sa
(General Directorate of Passports, the regulation's own named issuing
directorate) returned HTTP 503 twice. (3) uqn.gov.sa (Umm Al-Qura Official
Gazette, the publication explicitly named in this Regulation's own Article
53) -- the domain itself IS reachable (200 OK), but it is a JavaScript-heavy
single-page application; the specific gazette-issue-5151 page could not be
located this pass via in-site search or URL-pattern guessing. This is a
genuine unresolved access gap, not a domain-level failure.

PRIMARY TEXT SOURCE ACTUALLY USED: qanoonsa.com (an independent Arabic legal
aggregator, NOT an official portal), fetched via direct raw HTML curl (NOT
WebFetch's own LLM-summarization layer, to avoid any paraphrase risk on the
legal text itself) and parsed structurally from its <h3>/<p> tags. The
page's own body cites the regulation's exact decree number, gazette issue,
and publication date (30 March 2026) as part of the regulation's own closing
articles, not as an external claim. A single available Wayback Machine
snapshot (16 Apr 2026 -- the only one that exists, given the regulation's own
recency) was diffed against the live fetch (19 Jul 2026) and found BYTE-
IDENTICAL for all 53 articles' substantive text (only an unrelated "related
posts" sidebar differed).

SECOND SOURCE (a genuine government archival body, NOT a private aggregator):
ncar.gov.sa (National Center for Archives and Records, established by Royal
Order 1409H/1989, under the Royal Court, overseen by a board that includes
the Bureau of Experts itself) hosts a page titled "the Implementing
Regulation of the Travel Documents Law for 1447H" independently confirming
decree number 4203, the Ministry of Interior as issuer, gazette issue 5151,
publication date 30 March 2026, and the exact repeal of Decision 7/waw-zay
(1422H) -- but this was reached only via WebFetch's own AI-summarization (direct
curl got a TLS reset, likely anti-bot protection), so it corroborates decree
METADATA, not a sentence-level verbatim cross-check of all 53 articles.

THIRD SOURCE (private aggregator): qanoniah.com independently indexes this
Regulation as a document distinct from its own separately-dated "-1422" page
for the superseded predecessor -- corroborating that a current, separate
version exists, though its JavaScript-rendered reader could not be scraped
for full text this pass.

HONEST TIER CALL: TIER_3 (per reports/verification_tiers/
VERIFICATION_TIERS_METHODOLOGY_AR.md's own taxonomy) -- full access to a
primary/official source was NOT achieved this pass despite genuinely
attempting BOE, MOI, GDP, and UQN in that order; the full article text rests
entirely on a private aggregator (qanoonsa.com), cross-checked against two
other secondary sources (ncar.gov.sa, an official archival body, at the
metadata level; qanoniah.com, private, at the indexing level) that agree with
each other and with qanoonsa.com on all decree-identifying facts. This is
NOT inflated to TIER_2 or TIER_1.

53 records, all اصلية (this is the founding/only version of this specific
instrument; issued ~4 months before this pass, no per-article amendment has
been documented since). 0 معدلة, 0 ملغاة, 0 مضافة. 10 formally-numbered
فصول (chapters) -- a genuine numbered chapter structure, unlike the flat
travel_documents_law (no أبواب/فصول at all) or the domestic_labor_regulation
(14 informal, unnumbered thematic sections).

PREDECESSOR: Article 52 states this Regulation replaces IN FULL (not
scoped/partial) the prior Implementing Regulation issued by Ministerial
Decision No. 7/waw-zay, 23/9/1422H (~69 articles across ~12 chapters per
secondary sources only, not independently verified article-by-article) --
neither the predecessor's decree nor its full text is present anywhere in
this corpus; recorded as historical context only, not ingested (one-
instrument-per-pass rule).

One confirmed source-side textual anomaly preserved verbatim, not silently
fixed: Article 37(3)'s "يمنع" appears split with an internal space as "مي
نع" in the sole available source, stable across both the live fetch and the
single Wayback snapshot -- flagged, not corrected, absent a second
independent extraction of the same original document. RLM (U+200F)
directional-control characters preceding list-item dashes (111 occurrences)
were stripped as pure typographic normalization, consistent with this
corpus's existing NBSP/curly-quote precedent (no other track retains RLM in
article text). No legal text is altered beyond this. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "travel_documents", "regulation", "official_source",
                   "travel_documents_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "travel_documents", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "travel_documents_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "travel_documents_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "travel_documents_regulation_arabic_legal_llm",
                        "travel_documents_regulation_legal_llm_001_053.json")

LAW_ID = "sa-travel-documents-regulation-4203-1447"
LAW_AR = "اللائحة التنفيذية لنظام وثائق السفر"
STATUS_UNCHANGED = ("QANOONSA_COM_RAW_HTML_DIRECT_FETCH_MAR2026_PUBLISH_APR2026_WAYBACK_"
                     "JUL2026_LIVE_STABLE_X_NCAR_GOV_SA_OFFICIAL_ARCHIVE_METADATA_CROSSCHECK_X_"
                     "QANONIAH_COM_INDEX_CONFIRM_BOE_NO_DEDICATED_LAWID_MOI_GDP_UNREACHABLE_"
                     "UQN_GOV_SA_REACHABLE_BUT_SPECIFIC_GAZETTE_PAGE_NOT_LOCATED_THIS_PASS")
STATUS_ART37_ANOMALY = STATUS_UNCHANGED + "_PARA3_SOURCE_TYPO_VERBATIM_PRESERVED_NOT_SILENTLY_CORRECTED"
KEY_RE = r"travel_documents_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ANOMALY_KEYS = {"travel_documents_regulation_art_037"}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك التنفيذية وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم").split())


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
    if key in ANOMALY_KEYS:
        return STATUS_ART37_ANOMALY
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
        ver.append({"law_key": "travel_documents", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "TRAVEL_DOCUMENTS_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY text source is qanoonsa.com "
                                              "(private legal aggregator, directly raw-HTML-fetched, "
                                              "not WebFetch-summarized) -- laws.boe.gov.sa has NO "
                                              "dedicated page for this Implementing Regulation at all "
                                              "(current or superseded), and moi.gov.sa/gdp.gov.sa were "
                                              "unreachable this pass; uqn.gov.sa (the gazette named in "
                                              "this Regulation's own Article 53) was domain-reachable "
                                              "but its specific article page could not be located. "
                                              "Cross-checked at the decree-metadata level against "
                                              "ncar.gov.sa (a genuine government archival body) and "
                                              "qanoniah.com (private, indexing-level only). See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track's text or provenance. "
                                              "Overall verification tier is honestly self-assessed as "
                                              "TIER_3 (not inflated to TIER_2 or TIER_1), since no "
                                              "official/primary source's own text was directly reached "
                                              "this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "travel-documents-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "travel_documents/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام وثائق السفر" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Resolution No. 4203 (1447H) — "
                                                          "published Umm Al-Qura Gazette No. 5151, 30 "
                                                          "March 2026G — qanoonsa.com (private "
                                                          "aggregator, direct raw-HTML fetch), "
                                                          "cross-checked at the decree-metadata level "
                                                          "against ncar.gov.sa (National Center for "
                                                          "Archives and Records, a genuine government "
                                                          "archival body) and qanoniah.com; BOE has no "
                                                          "dedicated page for this instrument, MOI/GDP "
                                                          "unreachable, UQN domain-reachable but "
                                                          "specific gazette page not located this pass"),
                                     "source_authority_ar": "القرار الوزاري رقم (٤٢٠٣) — جريدة أم القرى رقم (٥١٥١)، ٣٠ مارس ٢٠٢٦م — qanoonsa.com (جلب HTML خام مباشر)، مطابق مع ncar.gov.sa (جهة أرشيفية حكومية، مستوى البيانات الوصفية) وqanoniah.com؛ لا توجد صفحة مخصصة لهذه اللائحة على هيئة الخبراء، وتعذر الوصول لوزارة الداخلية والمديرية العامة للجوازات، وموقع جريدة أم القرى قابل للوصول لكن لم تُحدَّد صفحته المحدَّدة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "travel_documents",
               "layer": "TRAVEL_DOCUMENTS_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-travel-documents-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (53 مادة، جميعها أصلية، موزعة على 10 فصول رسمية)",
               "title_en": ("Saudi Travel Documents Implementing Regulation — Arabic LLM-ready layer "
                            "(53 records, all original, across 10 formally-numbered chapters)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 53], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Travel Documents Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
