#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Building Code Application Law track (نظام تطبيق كود البناء
السعودي, Royal Decree M/43, 26/4/1438H / 24/01/2017G; amended by Royal Decree
M/15, 19/1/1441H; Royal Decree M/88, 10/4/1446H; and Royal Decree M/204,
12/9/1446H).

VERIFICATION TIER -- see sources/building_code/law/official_source/
building_code_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY BOE PORTAL: laws.boe.gov.sa's dedicated law page (lawId
cfc97985-4a9f-4012-832b-a9a700f21ed2) returned HTTP 503 on live direct access
(both WebFetch and curl) this pass. Per this corpus's methodology, web.archive.org
was tried next -- it was NOT blocked in this session (root fetch returned HTTP
200; CDX/available API worked normally) -- and a very recent archived snapshot
(timestamp 20260114015823) of the live BOE page was retrieved directly (HTTP
200, real HTML with full 16-article text and per-article "تعديلات المادة"
amendment-history popups, not an empty JS shell). This IS the official BOE
portal's own content, retrieved via a legitimate archived copy of the live site
-- not a substitute source.

IMPORTANT FINDING: the BOE page's MAIN body for Article 1 and Article 9 (in
this snapshot) still displays PRE-amendment wording, even though the SAME
page's own "تعديلات المادة" popups cite later dated amending decrees for both
articles. The BOE portal's main display had not caught up with its own amendment
log as of this snapshot. This track uses the fully-amended current text
(original + all dated amendments applied, cross-verified independently for each
amendment) in `text`, and preserves the original AND every intermediate
amendment stage in `history`. This BOE-side display lag is disclosed in
known_unresolved_discrepancies -- NOT silently "fixed" in the portal's own
main-body text, only accounted for in what this track stores.

SOURCES USED (TIER_1_PRIMARY_MULTI_SOURCE):
  * ORIGINAL full text (all 16 articles) + Royal Decree M/15 (19/1/1441H)
    amendment (arts 1, 8, 9): BOE portal cross-checked verbatim against an
    independent PDF published by the Saudi Council of Engineers (saudieng.sa,
    retrieved via archive.org after the live file was unreachable), which
    explicitly reproduces the M/15 amendment text in its own dedicated section.
  * Royal Decree M/88 (10/4/1446H) amendment (art 9, final "التيار الكهربائي"
    clause): BOE portal cross-checked against the Umm al-Qura OFFICIAL GAZETTE
    itself (uqn.gov.sa/details?p=26627, HTTP 200, live fetch), which quotes
    Council of Ministers Resolution 286 (5/4/1446H) verbatim, including its
    citation of the prior M/15 amendment to the same article.
  * Royal Decree M/204 (12/9/1446H) amendment (arts 1, 15: اللجنة الوطنية ->
    المركز): BOE portal cross-checked against qanoonsa.com (independent legal
    aggregator), which separately confirms both the decree text and its
    underlying Council of Ministers Resolution 656 (4/9/1446H).

16 records: 12 اصلية, 4 معدلة (arts 1, 8, 9, 15), 0 ملغاة, 0 مضافة. The statute
has NO chapter/باب/فصل divisions (flat 1-16); section_ar is empty for every
article by design. Articles 1 and 9 each carry a TWO-stage amendment chain
(original -> intermediate -> current); Articles 8 and 15 each carry a
single-stage amendment (original -> current). For every amended article the
CURRENT (fully-amended) text is stored in `text`; every earlier stage is
preserved in `history` (types: "original", "amendment_intermediate_m15",
"amendment_current").

NO PREDECESSOR REPEAL: Article 16 contains only a generic conflict clause
("ويلغي كل ما يتعارض معه من أحكام") with no named predecessor law -- it is a
founding statute, not a repeal of a specifically identified prior instrument.

KNOWN INTERNAL INCONSISTENCY (disclosed, not resolved): Articles 4 and 5 still
literally read "اللجنة الوطنية" and "وزير التجارة والاستثمار رئيس مجلس إدارة
الهيئة السعودية للمواصفات والمقاييس والجودة" -- the SAME titles that Royal
Decree M/204 replaced in Articles 1 and 15 -- because BOE records no official
textual amendment to Articles 4 or 5 themselves. This track does NOT silently
harmonize this; it is flagged in known_unresolved_discrepancies.

TASHKEEL stripped uniformly (corpus-majority convention); curly/guillemet
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
SRC = os.path.join(ROOT, "sources", "building_code", "law", "official_source",
                   "building_code_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "building_code", "law", "verified")
RECORDS = os.path.join(OUT_VER, "building_code_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "building_code_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "building_code_arabic_legal_llm",
                        "building_code_law_legal_llm_001_016.json")

LAW_ID = "sa-building-code-law-m-43-1438"
LAW_AR = "نظام تطبيق كود البناء السعودي"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"building_code_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {
    "building_code_law_art_001",
    "building_code_law_art_008",
    "building_code_law_art_009",
    "building_code_law_art_015",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الكود الجهات ذات العلاقة").split())


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


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa's dedicated lawId page for this law "
            "(cfc97985-4a9f-4012-832b-a9a700f21ed2) returned HTTP 503 on live direct "
            "access this pass; a very recent (2026-01-14) web.archive.org snapshot of "
            "the live BOE page was retrieved instead (web.archive.org was NOT blocked "
            "in this session) and contains the full 16-article text plus per-article "
            "amendment-history popups -> this IS the official portal's own content. "
            "The BOE page's main body for Articles 1 and 9 lags behind its own cited "
            "amendments (disclosed, not silently corrected); this track stores the "
            "fully-amended current text, cross-verified per amendment: original text + "
            "Royal Decree M/15 (19/1/1441H) via an independent Saudi Council of "
            "Engineers PDF; Royal Decree M/88 (10/4/1446H) via the Umm al-Qura OFFICIAL "
            "GAZETTE itself; Royal Decree M/204 (12/9/1446H) via qanoonsa.com -> "
            "TIER_1_PRIMARY_MULTI_SOURCE. 16 articles, flat (no chapters); arts 1/8/9/15 "
            "معدلة, all others اصلية; no repeal of any named predecessor (Art 16 is only "
            "a generic conflict clause). Articles 4/5 still literally read the "
            "pre-M/204 institutional titles even though the same titles were replaced "
            "elsewhere (M/204 did not textually touch arts 4/5) -- a genuine internal "
            "inconsistency in the current law, disclosed not resolved. See "
            "verification_methodology_note and known_unresolved_discrepancies in the "
            "source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/43 (26/4/1438H), CoM Resolution 241 (25/4/1438H); amended by "
            "Royal Decree M/15 (19/1/1441H) for arts 1/8/9; Royal Decree M/88 "
            "(10/4/1446H, CoM Resolution 286) for art 9; Royal Decree M/204 (12/9/1446H, "
            "CoM Resolution 656) for arts 1/15. Original text + M/15 from the BOE portal "
            "(archived live snapshot) cross-checked against an independent Saudi Council "
            "of Engineers PDF; M/88 cross-checked against the Umm al-Qura official "
            "gazette itself (uqn.gov.sa); M/204 cross-checked against qanoonsa.com -> "
            "TIER_1_PRIMARY_MULTI_SOURCE")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/43 وتاريخ 26/4/1438هـ، وقرار مجلس الوزراء رقم 241 وتاريخ "
               "25/4/1438هـ؛ عدلت المواد 1 و8 و9 بالمرسوم الملكي رقم م/15 وتاريخ 19/1/1441هـ؛ "
               "وعدلت المادة 9 بالمرسوم الملكي رقم م/88 وتاريخ 1446/4/10هـ (قرار مجلس الوزراء "
               "286)؛ وعدلت المادتان 1 و15 بالمرسوم الملكي رقم م/204 وتاريخ 1446/9/12هـ (قرار "
               "مجلس الوزراء 656). النص الأصلي وتعديل م/15 من بوابة هيئة الخبراء (لقطة أرشيفية "
               "حية) متقاطعان مع ملف مستقل للهيئة السعودية للمهندسين؛ تعديل م/88 متقاطع مع نص "
               "جريدة أم القرى الرسمية ذاتها؛ تعديل م/204 متقاطع مع qanoonsa.com -- "
               "TIER_1_PRIMARY_MULTI_SOURCE")


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
        ver.append({"law_key": "building_code", "law_component": "law",
                    "language": "ar",
                    "record_layer": "BUILDING_CODE_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "building-code-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "building_code/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام تطبيق كود البناء السعودي" % a["number_label_ar"]],
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
    json.dump({"law_key": "building_code",
               "layer": "BUILDING_CODE_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-building-code-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 مادة؛ 12 أصلية، 4 معدلة)",
               "title_en": ("Law on Implementation of the Saudi Building Code — Arabic "
                            "LLM-ready layer (16 records: 12 original, 4 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 16], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Building Code Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
