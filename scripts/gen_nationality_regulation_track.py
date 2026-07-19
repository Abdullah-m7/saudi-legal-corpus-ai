#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Implementing Regulation of the Nationality Law
track (اللائحة التنفيذية لنظام الجنسية العربية السعودية, Ministerial Decision
No. 74/زو, 9/3/1426H / 22 Apr 2005G, issued by the Minister of Interior).

This is the companion regulation flagged (but not ingested) in the
nationality_law track's own known_unresolved_discrepancies, key
"nationality_implementing_regulation_not_ingested" -- that entry estimated
"~25 articles" from an earlier light-verification pass. This pass confirms
the TRUE article count is 35, not 25 -- see
sources/nationality/regulation/official_source/
nationality_regulation_official_source.json's verification_methodology_note
and known_unresolved_discrepancies for the full account of that correction.

VERIFICATION TIER -- summary (full account in the official_source file):

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology.
Confirmed (web search + Wayback CDX scan of the whole laws.boe.gov.sa domain)
that BOE hosts NO dedicated lawId page for this Implementing Regulation at
all -- only the parent Law's own page appears in any search. BOE's live
portal was also unreachable this pass (connection reset), consistent with
this corpus's established recurring pattern for this portal.

PRIMARY SOURCE: moi.gov.sa (the Ministry of Interior's own official site),
the Implementing Regulation's own issuing authority. Its live portal was
also unreachable this pass (connection reset via curl, HTTP 503 via
WebFetch) -- so the PDF was fetched via THREE independent Wayback Machine
snapshots (4 Mar 2011, 29 Sep 2022, 15 Mar 2024) which are BYTE-IDENTICAL
(sha256 5b48f12d...61538ad2f7) across all 13 years, extracted via two
independent tools (poppler pdftotext, PyMuPDF), both agreeing on 35 articles.

SECOND SOURCE: nezams.com (independent legal aggregator) confirms the
founding decree number/date (74/زو, 9/3/1426H) as an appendix to its own
nationality-law page.

THIRD SOURCE: alriyadh.com's own contemporaneous news article (published
Saturday 14 Rabi' al-Awwal 1426H / 23 Apr 2005G, the day after Umm Al-Qura
publication) reproduces the Regulation's FULL 35-article text verbatim.
Automated normalized diffing against moi.gov.sa's PDF found word-for-word
equivalence across all 35 articles (18+ years apart), with only: (a) a font
ligature-drop bug in moi.gov.sa's own PDF (loses "مخ" from
المختص/المختصة in 5 places) and an RTL line-reordering artifact in 2 short
paragraphs -- both absent from alriyadh's text and confirmed via the clean
cross-match, not guessed; (b) two single-letter transcription typos in
alriyadh's own text (Art. 5, Art. 25) fixed against moi.gov.sa's spelling;
(c) an informal hamza-orthography convention in alriyadh's text, disclosed
not individually corrected. alriyadh's text (thus corrected) is used as the
base "text" field for all 35 articles since it is free of the PDF's
extraction artifacts and fully cross-verified against the primary source.

ARTICLE-COUNT DISCREPANCY RESOLVED (25 -> 35): the alriyadh 2005 article's
own PROSE erroneously states "25 مادة" even though its own reproduced full
text (below that same sentence) runs to Article 35 -- an internal
self-contradiction in that single source, almost certainly the origin of
this corpus's own prior "~25 articles" gap-map estimate. Resolved definitively
in favor of 35, independently confirmed by the byte-stable government PDF.

REPEAL FINDING: Article 28 (originally: "يصدر وزير الداخلية القرارات اللازمة
لمنح الجنسية بموجب المادة (8) من النظام") was DELETED by a Minister of
Interior decision (Prince Abdulaziz bin Saud bin Nayef), published in Umm
Al-Qura (per uqn.gov.sa's own headline) around Friday 17 Mar 2023G, following
Royal Decree M/88 (11/6/1444H) which transferred nationality-grant authority
under the parent Law's Article 8 from the Minister of Interior to the Prime
Minister -- confirmed by 5+ independent Saudi news outlets, all quoting the
SAME deleted article text verbatim. moi.gov.sa's own PDF is confirmed STALE:
it still shows Article 28's pre-deletion text as of its most recent Wayback
snapshot (15 Mar 2024, over a year after the deletion). Per this corpus's
binding rule, Article 28 is preserved here with its original text,
legal_status_ar=ملغاة -- never deleted or silently merged away.

No other article's text has changed since 1426H. 34 اصلية, 0 معدلة, 1 ملغاة
(Article 28), 0 مضافة. This Regulation names no repealed predecessor
instrument of its own (confirmed negative finding -- it is the first and
only Implementing Regulation for this Law since 1374H).

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nationality", "regulation", "official_source",
                   "nationality_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "nationality", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "nationality_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "nationality_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "nationality_regulation_arabic_legal_llm",
                        "nationality_regulation_legal_llm_001_035.json")

LAW_ID = "sa-nationality-regulation-74zw-1426"
LAW_AR = "اللائحة التنفيذية لنظام الجنسية العربية السعودية"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"nationality_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
REPEALED_KEYS = {"nationality_regulation_art_028"}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم صاحب الطلب الجنسية").split())


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
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "nationality", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "NATIONALITY_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": ("Arabic governs; PRIMARY source is moi.gov.sa (the "
                                              "issuing Ministry's own site) -- laws.boe.gov.sa was "
                                              "checked first per standard methodology but confirmed "
                                              "to host NO dedicated page at all for this Implementing "
                                              "Regulation. Cross-verified against nezams.com (decree "
                                              "number/date) and alriyadh.com's 2005G contemporaneous "
                                              "full-text reproduction (35 articles, matching "
                                              "moi.gov.sa's byte-stable PDF word-for-word). Article 28 "
                                              "was deleted circa March 2023 by Minister of Interior "
                                              "decision (independently confirmed by 5+ news outlets) "
                                              "but moi.gov.sa's own PDF remains stale and still shows "
                                              "its pre-deletion text as of the most recent Wayback "
                                              "snapshot checked (15 Mar 2024) -- preserved here "
                                              "verbatim with legal_status_ar=ملغاة, not deleted. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track's text or provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "nationality-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "nationality/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الجنسية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. 74/زو "
                                                          "(9/3/1426H) — moi.gov.sa (issuing "
                                                          "Ministry's own site), cross-verified "
                                                          "against nezams.com and alriyadh.com's "
                                                          "2005G contemporaneous full-text "
                                                          "reproduction; laws.boe.gov.sa confirmed "
                                                          "to host no dedicated page for this topic"),
                                     "source_authority_ar": "القرار الوزاري رقم 74/زو وتاريخ 9/3/1426هـ — الموقع الرسمي لوزارة الداخلية (moi.gov.sa)، مطابق مع nezams.com ونص جريدة الرياض المعاصر (2005م)؛ بوابة هيئة الخبراء لا تستضيف صفحة مستقلة لهذا الموضوع",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "nationality",
               "layer": "NATIONALITY_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-nationality-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (35 مادة؛ 34 أصلية و1 ملغاة [المادة 28])",
               "title_en": ("Implementing Regulation of the Saudi Arabian Nationality Law — Arabic "
                            "LLM-ready layer (35 records; 34 original, 1 repealed [Article 28])"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 35], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Nationality Implementing Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
