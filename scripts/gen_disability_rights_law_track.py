#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Rights of Persons with Disabilities Law track (نظام حقوق
الأشخاص ذوي الإعاقة, Royal Decree M/27, 11/2/1445H / ~2023G).

VERIFICATION TIER -- see sources/disability_rights/law/official_source/
disability_rights_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law (e52b691a-785c-42a7-8916-b07d00e4fd38, viewer id
e3923599-e921-4891-bed2-b07d00e4fd4b) -- found via WebSearch -- but the live
portal returned HTTP 503 (WebFetch) / connection-reset (direct curl, exit code
000). web.archive.org was CONFIRMED BLOCKED by this session's egress policy: a
direct curl to a real archived snapshot (found via the wayback availability
API) returned the literal string "Blocked by egress policy", and WebFetch
explicitly refused ("Claude Code is unable to fetch from web.archive.org").
Neither was bypassed.

SOURCES USED (TIER_3 -- no official government source reachable this pass for
the primary text itself):
  * nezams.com (independent Arabic legal-text aggregator) -- fetched directly
    via curl (HTTP 200, ~456 KB), parsed programmatically: exactly 33 HTML
    "subject-N" elements (subject-1..subject-33), spelled-ordinal labels
    المادة الأولى..الثالثة والثلاثون, grouped under 5 "الباب" headers embedded
    in the opening article of each chapter (articles 1, 3, 15, 21, 29). The
    page also carries the full Royal Decree (M/27) + CoM Resolution (110)
    preamble text, and og:description metadata explicitly confirming: decree
    date 11/02/1445H, CoM resolution date 06/02/1445H, publication date
    23/02/1445H, status "ساري", and "التعديلات: لم يجرِ عليه تعديل" (no
    amendments made).
  * qanoonsa.com (a second, technically unrelated independent legal
    blog/aggregator; separate pages /p/499702/ for the decree text alone and
    /p/499703/ for the full statute) -- fetched directly via curl (HTTP 200
    for both). Every one of its 33 articles was diffed programmatically
    against the nezams.com text: content matched VERBATIM for all 33 articles;
    the only difference found across the entire statute was numeral-glyph
    style (nezams.com renders enumeration digits as Western 1/2/3; qanoonsa.com
    renders them as Eastern Arabic ١/٢/٣ for the identical items) -- normalized
    to Western digits (nezams.com's original rendering) in the stored text.

NOT TIER_1/TIER_2 because no official BOE/Umm-al-Qura-gazette-issue page could
be retrieved directly this pass for the primary law text; corroboration rests
on two independent non-derivative secondary sources agreeing verbatim, plus
WebSearch snippets independently quoting the same decree number/date.

33 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- nezams.com's own portal
metadata states explicitly no amendment has been made since enactment. 5
chapters (أبواب): Ch.1 تعريفات ومبادئ عامة (1-2); Ch.2 الحقوق والخدمات (3-14);
Ch.3 الدعم الاجتماعي والاقتصادي (15-20); Ch.4 المخالفات والعقوبات (21-28);
Ch.5 أحكام ختامية (29-33).

NAMED-PREDECESSOR REPEAL (rare, and directly relevant to this corpus's
repeal-graph work): Article 32 states verbatim: "يحل النظام محل نظام رعاية
المعوقين الصادر بالمرسوم الملكي رقم (م/37) وتاريخ 23/9/1421هـ، ويلغي كل ما
يتعارض معه من أحكام" -- i.e. this law EXPLICITLY repeals the older نظام رعاية
المعوقين (Royal Decree M/37, 23/9/1421H). This is independently corroborated a
THIRD way: CoM Resolution 110's own recitals (part of the preamble, same text
on both independent sources) separately list "نظام رعاية المعوقين، الصادر
بالمرسوم الملكي رقم (م/37) وتاريخ 23/9/1421هـ" among the documents it
reviewed. This is a genuine named-predecessor repeal, not a vague general
conflict clause.

TASHKEEL stripped uniformly (corpus-majority convention, harakat range
U+064B-U+0652 plus related marks); curly quotes straightened (none were
present); enumeration digits normalized to Western glyphs; double/nbsp spaces
removed -- display-layer only, no legal text altered. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.

FOLLOW-UP CANDIDATES NOT INGESTED (one-instrument-per-pass rule): (1) the
Implementing Regulation mandated by Article 31 (published in Umm al-Qura,
uqn.gov.sa pages p=24966/p=24967 -- existence confirmed via WebSearch only);
(2) the Violations-Committee procedural rules (Resolution No. 27,
22/1/1446H -- uqn.gov.sa p=26539/p=26569).
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "disability_rights", "law", "official_source",
                   "disability_rights_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "disability_rights", "law", "verified")
RECORDS = os.path.join(OUT_VER, "disability_rights_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "disability_rights_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "disability_rights_arabic_legal_llm",
                        "disability_rights_law_legal_llm_001_033.json")

LAW_ID = "sa-disability-rights-law-m-27-1445"
LAW_AR = "نظام حقوق الأشخاص ذوي الإعاقة"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"disability_rights_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة الجهة المعنية الأشخاص ذوي الإعاقة").split())


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
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa HAS a dedicated lawId page for this law "
            "(e52b691a-785c-42a7-8916-b07d00e4fd38) but it was unreachable this pass "
            "(HTTP 503 live / connection reset; web.archive.org CONFIRMED egress-blocked "
            "for this session and NOT bypassed). Full text is from nezams.com "
            "(independent aggregator), cross-checked verbatim article-by-article against "
            "qanoonsa.com (a second, technically unrelated independent aggregator) -> "
            "TIER_3. 33 articles, 5 chapters (أبواب); ALL اصلية (no amendment since "
            "enactment, per nezams.com's own metadata). Article 32 EXPLICITLY repeals a "
            "named predecessor: نظام رعاية المعوقين (Royal Decree M/37, 23/9/1421H) -- "
            "independently corroborated a third way by CoM Resolution 110's own recitals. "
            "See verification_methodology_note and known_unresolved_discrepancies in the "
            "source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/27 (11/2/1445H), CoM Resolution 110 (6/2/1445H), published "
            "Umm al-Qura gazette issue 4997 (8 Sept 2023G). Full text from nezams.com "
            "cross-checked verbatim against qanoonsa.com (independent secondary sources; "
            "laws.boe.gov.sa dedicated lawId page unreachable this pass -- live 503; "
            "Wayback egress-blocked, not bypassed) -> TIER_3. Article 32 explicitly repeals "
            "the predecessor نظام رعاية المعوقين (Royal Decree M/37, 23/9/1421H).")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/27 وتاريخ 11/2/1445هـ، وقرار مجلس الوزراء رقم 110 وتاريخ "
               "6/2/1445هـ، منشور بجريدة أم القرى العدد 4997 (8 سبتمبر 2023م). النص الكامل من "
               "nezams.com متقاطع حرفيا مع qanoonsa.com (مصدران ثانويان مستقلان؛ الصفحة "
               "المخصصة على laws.boe.gov.sa غير قابلة للوصول هذه الجولة -- 503 حيا، وWayback "
               "محظور سياسيا ولم يُتجاوَز) -- TIER_3. المادة (32) تلغي صراحة نظام رعاية "
               "المعوقين السابق (المرسوم الملكي م/37، 23/9/1421هـ).")


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
        ver.append({"law_key": "disability_rights", "law_component": "law",
                    "language": "ar",
                    "record_layer": "DISABILITY_RIGHTS_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "disability-rights-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "disability_rights/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام حقوق الأشخاص ذوي الإعاقة" % a["number_label_ar"]],
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
    json.dump({"law_key": "disability_rights",
               "layer": "DISABILITY_RIGHTS_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-disability-rights-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (33 مادة أصلية)",
               "title_en": ("Rights of Persons with Disabilities Law — Arabic LLM-ready layer "
                            "(33 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 33], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Disability Rights Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
