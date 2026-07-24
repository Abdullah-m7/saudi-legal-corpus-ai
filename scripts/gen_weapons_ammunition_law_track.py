#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Weapons and Ammunition Law track (نظام الأسلحة والذخائر,
Royal Decree M/45, 25/7/1426H / ~2005G; amended by CoM Resolution 217 1439H,
Royal Decree M/17 1437H, Royal Decree M/71 1444H, and CoM Resolution 967 1445H).

VERIFICATION TIER -- see sources/weapons_ammunition/law/official_source/
weapons_ammunition_law_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY BOE PORTAL LIVE ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a
dedicated lawId page for this law (a445af93-671f-496b-818a-a9a700f19150) but
the live portal returned HTTP 503 (WebFetch) / connection-reset errno 35
(direct curl), across several attempts.

UNLIKE some earlier tracks in this corpus that treated web.archive.org as
egress-blocked and never attempted it, this pass confirmed archive.org WAS
reachable via direct curl (after one transient 403 retry) and was used to
retrieve the OFFICIAL BOE portal's own historical page content -- not a
third-party mirror. Three snapshots were fetched and cross-checked: 17 Aug
2019, 18 Jun 2025, and 15 Feb 2026 (of 23 total snapshots enumerated via the
Wayback CDX API, all HTTP 200). The full 63-article text was parsed from the
2026 snapshot and diffed against the 2019 snapshot: byte-for-byte identical
for every article NOT flagged as amended.

SOURCES USED (TIER_2):
  * PRIMARY full text (all 63 articles): the archived laws.boe.gov.sa portal
    page itself (government source, via Wayback, not live).
  * INDEPENDENT cross-check: nezams.com (independent legal aggregator),
    fetched directly (HTTP 200), 63 "subject" elements. Every one of the 63
    articles' BOE-displayed text matched nezams.com's copy verbatim after
    whitespace/harakat normalization.
  * Umm al-Qura official gazette API (uqn.gov.sa) directly confirmed the
    EXISTENCE, TITLE, and PREAMBLE of Royal Decree M/71 (1/6/1444H) and CoM
    Resolution 967 (13/11/1445H) -- but truncated API responses prevented
    retrieval of their full operative/enacting text.

Not TIER_1 because: (a) the live BOE portal itself was never reachable this
pass; (b) five articles (12, 25, 43, 50, 53) show a genuine INTERNAL conflict
in the BOE portal's own data between the main displayed text (unchanged since
2019) and a "changed-article" version-history popup citing a specific Royal
Decree (M/71 for 12/25; M/17 for 43/50/53) with different wording -- resolved
here by a documented INTERPRETIVE judgment (favoring the popup/decree text as
current), not a clean multi-source agreement; (c) Article 31's paragraph (d)
amendment (CoM Res. 967) is confirmed to EXIST via the official gazette API
but its full operative text comes only from nezams.com, and the archived BOE
portal does not yet display it at all (a disclosed, unresolved gap).

63 records: 56 اصلية, 7 معدلة (arts 2, 12, 25, 31, 43, 50, 53), 0 ملغاة,
0 مضافة. The statute is divided into SEVEN topical sections with NO formal
باب/فصل label in the source (التعريفات، أحكام عامة، أحكام الرخص، إصلاح
الأسلحة وصيانتها، أحكام خاصة بالدبلوماسيين والمقيمين والوفود الرسمية،
العقوبات، أحكام انتقالية) -- section_ar stores "<label> (<article range>)"
per the premium_residency_law convention (topical headers without
باب/فصل wording), NOT chapter_structure entries with a fasl/bab label_ar.

NAMED PREDECESSOR REPEAL: Article 62 explicitly states "يحل هذا النظام محل
نظام الأسلحة والذخائر، الصادر بالمرسوم الملكي ذي الرقم (م/8) وتاريخ
19/2/1402هـ، ويلغي كل ما يتعارض معه من أحكام" -- a confirmed, precisely-named
repeal of a predecessor Weapons and Ammunition Law (Royal Decree M/8,
19/2/1402H, ~1982G), plus a general conflict clause. That predecessor is NOT
ingested as a separate track in this corpus.

For each amended article the CURRENT (as-determined) text is stored in
`text`; the pre-amendment/BOE-main-display text is preserved in
history[type=original] and the amended/decree-cited text in
history[type=amendment_current], with a decree_note documenting the specific
interpretive basis (see known_unresolved_discrepancies for full disclosure).

TASHKEEL: none found in either source (checked programmatically across all
63 articles). NBSP stripped from popup-sourced amendment text; curly quotes
straightened (none found). Kashida: only legitimate هـ/جـ enumeration and
Hijri-era markers present, no decorative kashida. Arabic governs; no
translation/paraphrase/interpretation of the legal text itself (the ONE
interpretive act -- choosing which of two BOE-provided texts is "current" for
5 articles -- is fully disclosed, not silent). Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "weapons_ammunition", "law", "official_source",
                   "weapons_ammunition_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "weapons_ammunition", "law", "verified")
RECORDS = os.path.join(OUT_VER, "weapons_ammunition_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "weapons_ammunition_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "weapons_ammunition_arabic_legal_llm",
                        "weapons_ammunition_law_legal_llm_001_063.json")

LAW_ID = "sa-weapons-ammunition-law-m-45-1426"
LAW_AR = "نظام الأسلحة والذخائر"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"weapons_ammunition_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {
    "weapons_ammunition_law_art_002",
    "weapons_ammunition_law_art_012",
    "weapons_ammunition_law_art_025",
    "weapons_ammunition_law_art_031",
    "weapons_ammunition_law_art_043",
    "weapons_ammunition_law_art_050",
    "weapons_ammunition_law_art_053",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزير الوزارة رخصة رخص").split())


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
            "(a445af93-671f-496b-818a-a9a700f19150) but the LIVE portal was unreachable this "
            "pass (HTTP 503 / connection-reset). Three Wayback Machine snapshots of that SAME "
            "official portal page (2019, 2025, 2026) were used instead and cross-checked against "
            "nezams.com for all 63 articles (verbatim match after normalization) -> TIER_2. Five "
            "articles (12, 25, 43, 50, 53) show an internal BOE conflict between the main "
            "displayed text and a 'changed-article' version-history popup citing a specific Royal "
            "Decree; the popup/decree text was adopted as current via a documented interpretive "
            "judgment (see known_unresolved_discrepancies). Article 31's paragraph (d), added by "
            "CoM Resolution 967 (1445H), is confirmed to exist via the Umm al-Qura gazette API but "
            "its full text is sourced from nezams.com only; the archived BOE portal does not yet "
            "display it. Article 62 names and repeals a predecessor Weapons and Ammunition Law "
            "(Royal Decree M/8, 19/2/1402H). See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this track's "
            "text or provenance.")

SRC_AUTH = ("Royal Decree M/45 (25/7/1426H), CoM Resolution 193 (24/7/1426H), published Umm "
            "al-Qura 18/9/1426H; amended by CoM Resolution 217 (29/4/1439H, art.2), Royal Decree "
            "M/17 (1/4/1437H, arts.43/50/53), Royal Decree M/71 (1/6/1444H, arts.12/25), and CoM "
            "Resolution 967 (13/11/1445H, art.31). Full text from the archived laws.boe.gov.sa "
            "portal page (Wayback, 3 snapshots 2019-2026) cross-checked verbatim against "
            "nezams.com; the M/71 and 967 decrees' existence/title/preamble independently "
            "confirmed via the Umm al-Qura gazette API. laws.boe.gov.sa live portal unreachable "
            "this pass (HTTP 503 / connection-reset) -> TIER_2")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/45 وتاريخ 25/7/1426هـ، وقرار مجلس الوزراء رقم 193 وتاريخ "
               "24/7/1426هـ (منشور بأم القرى 18/9/1426هـ)؛ عُدلت المواد 2 و12 و25 و31 و43 و50 و53 "
               "بموجب قرار مجلس الوزراء 217 (1439هـ) والمرسوم الملكي م/17 (1437هـ) والمرسوم الملكي "
               "م/71 (1444هـ) وقرار مجلس الوزراء 967 (1445هـ). النص الكامل من صفحة بوابة هيئة "
               "الخبراء المؤرشفة (Wayback، ثلاث لقطات 2019-2026) متقاطع حرفيا مع nezams.com؛ وجود "
               "مرسومي م/71 وقرار 967 وعنوانهما وديباجتهما مؤكد بشكل مستقل عبر واجهة برمجة تطبيقات "
               "جريدة أم القرى. البوابة الحية (laws.boe.gov.sa) غير قابلة للوصول هذه الجولة "
               "(503/connection-reset) -- TIER_2")


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
        ver.append({"law_key": "weapons_ammunition", "law_component": "law",
                    "language": "ar",
                    "record_layer": "WEAPONS_AMMUNITION_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "weapons-ammunition-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "weapons_ammunition/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الأسلحة والذخائر" % a["number_label_ar"]],
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
    json.dump({"law_key": "weapons_ammunition",
               "layer": "WEAPONS_AMMUNITION_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-weapons-ammunition-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (63 مادة؛ 56 أصلية، 7 معدلة)",
               "title_en": ("Weapons and Ammunition Law — Arabic LLM-ready layer "
                            "(63 records: 56 original, 7 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 63], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Weapons and Ammunition Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
