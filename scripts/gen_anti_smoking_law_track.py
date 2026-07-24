#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Anti-Smoking Law track (نظام مكافحة التدخين,
Royal Decree M/56, 28/7/1436H / ~2015G).

VERIFICATION TIER -- see sources/anti_smoking/law/official_source/
anti_smoking_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law (93b6f7f3-1083-46e7-b30e-a9a700f291b0) but the live
portal returned HTTP 503 (WebFetch) / connection-reset exit 35 (direct curl),
for both the exact law-detail URL and the bare root domain, repeated attempts.
archive.org/wayback/available (a DIFFERENT host than web.archive.org) confirmed
a real Wayback snapshot of this exact BOE page (timestamp 20251015113738, HTTP
200 from the availability API), but fetching that snapshot's actual content
over the web.archive.org domain itself -- via WebFetch AND via direct curl --
returned "Blocked by egress policy" both times; this block was NOT bypassed.

SOURCES USED (TIER_2):
  * ORIGINAL full text (all 20 articles): an OFFICIAL Saudi GOVERNMENT PDF
    hosted by the Ministry of Health (moh.gov.sa/Ministry/Rules/Documents/
    22.pdf), titled "Anti-Smoking Law ... Implementing Regulation, 3rd
    edition, 2019", issued jointly with the National Committee for Tobacco
    Control. Fetched directly via curl (HTTP 200, 14 pages, 2.3MB). pdftotext
    could not extract Arabic glyphs from this specific PDF's embedded font
    encoding (numbers/whitespace only, no Arabic characters at all) -- so all
    14 pages were read visually (page-image reading), a reliable method since
    Arabic script is read directly rather than OCR'd. Only the Law's own
    numbered "المادة (N)" articles were extracted; the interleaved
    Implementing-Regulation sub-clauses (e.g. 1-1, 2-1, ... 4-7) appearing in
    the same PDF were excluded from this track's article text (one-instrument-
    per-pass rule).
  * CROSS-CHECK 1: nezams.com (independent legal aggregator). Fetched directly
    via curl with a standard browser User-Agent (HTTP 200, 218592 bytes) and
    parsed with BeautifulSoup on the RAW HTML (not merely an AI-mediated
    fetch-tool summary) -- confirming the decree metadata (تاريخ النظام
    1436/07/28هـ; الاعتماد: المرسوم الملكي م/56 + قرار مجلس الوزراء 90 بتاريخ
    23/3/1434هـ; تاريخ النشر 1436/09/02هـ; التعديلات: "لم يجرى عليه تعديل" --
    an explicit page string, not an inference), the full Royal Decree preamble
    and Council of Ministers Resolution 90 text verbatim, and all 20 numbered
    "subject" article elements, matching the MOH PDF text verbatim (only minor
    spelling/tashkeel variants, e.g. مخالفا/مخالفاً، مئتا/مائتا).
  * CROSS-CHECK 2: a bilingual (Arabic/English) PDF hosted at
    d3vqfzrrx1ccvd.cloudfront.net (an international legislation-tracking
    aggregator), fetched directly via curl (HTTP 200) and machine-extracted
    via pdftotext -layout (Arabic extraction succeeded for this file).
    Independently matched the MOH PDF and nezams.com verbatim for all 20
    articles, including Article 7's nine prohibited-place items, Article 8's
    eight sale-restriction items, and the exact penalty figures in Articles
    13-15 (20,000 / 200 / 5,000 SAR).

Not TIER_1 because the canonical BOE portal page itself could not be
retrieved live or via an archived snapshot (web.archive.org egress-blocked)
this pass, despite confirming the snapshot exists.

20 records, all اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- nezams.com's own page
explicitly states no amendment has been made to the Law itself ("لم يجرى عليه
تعديل"); only its Implementing Regulation has been amended since (e.g.
Ministerial Resolution 797557, 1/5/1441H) -- out of scope for this track. The
statute has NO chapter/باب/فصل divisions (flat 1-20); section_ar is empty for
every article by design.

NO NAMED-PREDECESSOR REPEAL, BUT A TRANSITIONAL CONTINUATION CLAUSE: neither
the 20 articles, the Royal Decree preamble, nor the CoM Resolution 90 preamble
contain an explicit repeal clause naming a prior law/regulation. However, both
the Royal Decree's own enacting clause (ثانيا) and CoM Resolution 90's own
clause 2 state: government entities that already have competent-authority-
approved anti-smoking regulations shall CONTINUE applying them and collecting
fines until this Law's own Implementing Regulation is issued. This proves
unnamed prior agency-level anti-smoking regulations existed and were phased
out only once the new Implementing Regulation took effect -- a TRANSITIONAL
clause, not a REPEAL clause -- so this track does NOT record a confirmed
named-predecessor repeal (see known_unresolved_discrepancies).

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; double/nbsp spaces and in-word decorative kashida removed
(هـ/جـ preserved) -- display-layer only, no legal text altered. Arabic
governs; no translation/paraphrase/interpretation (the cloudfront.net
bilingual PDF's English column was used only to help locate the matching
Arabic text, never to correct or interpret it). Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_smoking", "law", "official_source",
                   "anti_smoking_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_smoking", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_smoking_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_smoking_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_smoking_arabic_legal_llm",
                        "anti_smoking_law_legal_llm_001_020.json")

LAW_ID = "sa-anti-smoking-law-m-56-1436"
LAW_AR = "نظام مكافحة التدخين"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"anti_smoking_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات").split())


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
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa HAS a dedicated lawId page for this law "
            "(93b6f7f3-1083-46e7-b30e-a9a700f291b0) but it was unreachable this pass (HTTP "
            "503 live / connection-reset via curl; a Wayback snapshot of this exact page was "
            "confirmed to exist via archive.org/wayback/available, but fetching its content "
            "over web.archive.org itself returned \"Blocked by egress policy\" and was NOT "
            "bypassed). ORIGINAL full text is from an OFFICIAL Ministry of Health PDF "
            "(moh.gov.sa, joint MOH/National Committee for Tobacco Control publication), "
            "cross-checked verbatim against nezams.com (raw HTML, BeautifulSoup-parsed) and a "
            "bilingual cloudfront.net legislation-aggregator PDF -> TIER_2. 20 articles, flat "
            "(no chapters); ALL 20 اصلية -- no amendment to the Law itself has occurred "
            "(nezams.com states this explicitly); only the Implementing Regulation has been "
            "amended (out of scope). NO named-predecessor repeal clause exists, but the Royal "
            "Decree/CoM Resolution 90 preambles contain a TRANSITIONAL clause permitting "
            "unnamed prior agency-level anti-smoking regulations to continue temporarily until "
            "this Law's own Implementing Regulation issues -- not a repeal. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/56 (28/7/1436H), CoM Resolution 90 (23/3/1434H), published Umm "
            "al-Qura 2/9/1436H. Full text from an official Ministry of Health PDF (moh.gov.sa, "
            "joint MOH/National Committee for Tobacco Control publication), independently "
            "cross-checked verbatim against nezams.com (raw HTML) and a bilingual "
            "cloudfront.net legislation PDF. laws.boe.gov.sa dedicated lawId page "
            "(93b6f7f3-1083-46e7-b30e-a9a700f291b0) unreachable live this pass; a confirmed "
            "Wayback snapshot's content could not be fetched (web.archive.org egress-blocked, "
            "not bypassed) -> TIER_2")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/56 وتاريخ 28/7/1436هـ، وقرار مجلس الوزراء رقم 90 وتاريخ "
               "23/3/1434هـ (منشور بأم القرى 2/9/1436هـ). النص الكامل من PDF رسمي لوزارة الصحة "
               "(بالاشتراك مع اللجنة الوطنية لمكافحة التبغ)، متقاطع حرفيا مع nezams.com (HTML خام) "
               "وملف PDF ثنائي اللغة لمجمّع تشريعات cloudfront.net. صفحة laws.boe.gov.sa المخصصة "
               "(lawId 93b6f7f3-1083-46e7-b30e-a9a700f291b0) غير قابلة للوصول حيا هذه الجولة؛ "
               "ولقطة Wayback المؤكدة تعذر جلب محتواها (حظر على مستوى سياسة خروج الشبكة، لم "
               "يُتجاوَز) -- TIER_2")


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
        ver.append({"law_key": "anti_smoking", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ANTI_SMOKING_LAW_ARABIC_VERIFIED_TEXT",
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
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "anti-smoking-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_smoking/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام مكافحة التدخين" % a["number_label_ar"]],
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
    json.dump({"law_key": "anti_smoking",
               "layer": "ANTI_SMOKING_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-anti-smoking-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (20 مادة؛ كلها أصلية)",
               "title_en": ("Anti-Smoking Law — Arabic LLM-ready layer (20 records: all "
                            "original, no amendments)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Smoking Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
