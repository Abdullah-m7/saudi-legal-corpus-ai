#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Elderly Rights and Care Law track (نظام حقوق
كبير السن ورعايته, Royal Decree M/47, 3/6/1443H / ~14 January 2022G),
following Council of Ministers Resolution No. 292 (1/6/1443H).

VERIFICATION TIER -- see sources/elderly_care_law/law/official_source/
elderly_care_law_official_source.json's verification_methodology_note for the
full account. Summary:

TIER_1. laws.boe.gov.sa's live portal was unreachable this pass (Connection
reset by peer via direct curl, repeated attempts), but -- unlike the documented
egress-policy block on web.archive.org noted in other tracks of this corpus --
Wayback Machine access was tested directly this pass and found reachable
(HTTP 200). An archived snapshot (dated 2025-02-11) of the law's own dedicated
BOE lawId page (3c63e654-4046-468d-93fd-ae1a00de13be) was fetched directly and
contains the OFFICIAL PORTAL'S OWN full verbatim text of all 23 articles (each
article_item element carries only the "no_alternate" CSS class, with none
marked "modified" or "canceled" -- confirming no article is amended or
repealed as of that snapshot), plus the full preamble (Royal Decree + Council
of Ministers Resolution 292) and the "ساري" (in force) status tag.

This BOE-portal text was cross-checked and found byte-for-byte identical
(after HTML-tag stripping) against nezams.com (independent legal aggregator,
fetched directly via curl, HTTP 200; exactly 23 "subject" elements). Decree
identity, article count (23), and publication date (Umm al-Qura Gazette,
11 Jumada al-Akhirah 1443H / 14 January 2022G, Issue 4917) were independently
confirmed a third time via a National Society for Human Rights (nshr.org.sa,
a quasi-official Saudi human-rights body) printed pamphlet PDF (fetched
directly, HTTP 200) -- used for identity/count/date confirmation only (its own
PDF text extraction carries bidi/font-shaping artifacts), not verbatim text.

23 records, all اصلية (original/unamended), 0 معدلة, 0 ملغاة, 0 مضافة. Flat
structure -- no أبواب/فصول division (chapter_structure is empty by design).
No amendment found in any source checked as of this pass (2026-07-26).

The Implementing Regulation (اللائحة التنفيذية) is tracked separately in this
corpus as elderly_care_regulation (shared internal law_key: elderly_care),
ingested in the same pass -- see that track for a documented, IMPORTANT
correction regarding CoM Resolution 292's actual role (it approved this LAW,
it did NOT itself issue the Implementing Regulation).

TASHKEEL stripped uniformly (corpus-majority convention, applied at the
official_source-build stage, not by this generator); curly quotes
straightened; double/nbsp spaces removed -- display-layer only, no legal text
altered. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "elderly_care_law", "law", "official_source",
                   "elderly_care_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "elderly_care_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "elderly_care_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "elderly_care_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "elderly_care_law_arabic_legal_llm",
                        "elderly_care_law_legal_llm_001_023.json")

LAW_KEY = "elderly_care"
LAW_ID = "sa-elderly-care-law-m-47-1443"
LAW_AR = "نظام حقوق كبير السن ورعايته"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"elderly_care_law_art_(\d{3})$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير كبير السن").split())


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
    if key in AMENDED_KEYS:
        return "AMENDED_DATED"
    if key in ADDED_KEYS:
        return "ADDED_DATED"
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa's live portal was unreachable this pass "
            "(connection reset), but a Wayback Machine snapshot (2025-02-11) of this law's "
            "own dedicated BOE lawId page (3c63e654-4046-468d-93fd-ae1a00de13be) WAS "
            "reachable this pass (HTTP 200 direct) and carries the official portal's own full "
            "verbatim text of all 23 articles, none flagged modified/canceled. Cross-checked "
            "byte-for-byte (post-HTML-stripping) against nezams.com; decree identity, article "
            "count and publication date independently confirmed a third time via a National "
            "Society for Human Rights (nshr.org.sa) pamphlet PDF -> TIER_1. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance -- including an "
            "important clarification of Council of Ministers Resolution 292's role (it "
            "approved this Law; the separate elderly_care_regulation track documents why it "
            "is not itself the Implementing Regulation's issuing instrument).")

SRC_AUTH = ("Royal Decree M/47 (3/6/1443H), Council of Ministers Resolution 292 (1/6/1443H), "
            "published Umm al-Qura Gazette 11 Jumada al-Akhirah 1443H / 14 January 2022G "
            "(Issue 4917). Full verbatim text from a Wayback-archived snapshot of the official "
            "laws.boe.gov.sa portal page itself (2025-02-11, HTTP 200 direct), cross-checked "
            "byte-for-byte against nezams.com; identity/count/date independently confirmed a "
            "third time via a National Society for Human Rights (nshr.org.sa) pamphlet PDF -> "
            "TIER_1.")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/47 وتاريخ 3/6/1443هـ، وقرار مجلس الوزراء رقم 292 وتاريخ "
               "1/6/1443هـ، منشور بجريدة أم القرى بتاريخ 11 جمادى الآخرة 1443هـ الموافق 14 "
               "يناير 2022م (العدد 4917). النص الحرفي الكامل من لقطة أرشيفية (Wayback، "
               "2025-02-11) لصفحة بوابة هيئة الخبراء الرسمية نفسها (HTTP 200 مباشر)، متطابق "
               "حرفياً مع nezams.com؛ الهوية والعدد وتاريخ النشر مؤكدة مستقلاً ثالثاً عبر كتيب "
               "الجمعية الوطنية لحقوق الإنسان (nshr.org.sa) -- TIER_1.")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = a["article_number"]
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        ver.append({"law_key": LAW_KEY, "law_component": "law", "language": "ar",
                    "record_layer": "ELDERLY_CARE_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "elderly-care-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "elderly_care_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام حقوق كبير السن ورعايته" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": top_status.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": LAW_KEY,
               "layer": "ELDERLY_CARE_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-elderly-care-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (23 مادة، جميعها أصلية)",
               "title_en": ("Saudi Arabian Elderly Rights and Care Law — Arabic LLM-ready "
                            "layer (23 records, all original/unamended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 23], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Elderly Care Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
