#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Antiquities, Museums and Urban Heritage Law track
(نظام الآثار والمتاحف والتراث العمراني, Royal Decree M/3, 9/1/1436H, as amended).

WHAT THIS LAW IS -- the currently in-force statute governing antiquities, museums
and urban/architectural heritage in Saudi Arabia. Issued by Royal Decree No. (M/3)
dated 9/1/1436H (Council of Ministers Resolution No. 348 dated 25/8/1435H; Shura
Council Resolutions 194/78 dated 18/2/1434H and 67/38 dated 14/7/1435H). By its own
Article 92 it EXPLICITLY replaces, BY NAME, the older Antiquities Law (نظام الآثار,
Royal Decree M/26, 23/6/1392H) and repeals all conflicting provisions -- a named
repeal-and-replace clause, not a generic conflict-only clause.

94 articles, with NO division into أبواب/فصول (a genuinely flat structure --
confirmed from two sources: nezams.com and a BOE-content print PDF, neither of which
shows any chapter headers). Hence chapter_structure is [] and section_ar is empty
for every article.

AMENDMENT HISTORY (never silently merged -- 16 معدلة articles across 6 instruments):
  - Royal Decree M/16, 21/1/1439H        -> Art 85 (added paragraph (ب))
  - CoM Resolution 693, 2/11/1441H        -> Arts 12, 29, 54 (ministry-name substitution)
  - Royal Decree M/67, 12/8/1442H         -> Arts 71-77 + Art 90(1) (penalties toughened)
    (paired with CoM Resolution 453, 10/8/1442H; scope independently confirmed by the
     Umm Al-Qura Gazette)
  - Royal Decree M/103, 21/11/1442H       -> Art 3 (expropriation; added paragraph 2)
  - CoM Resolution 1012, 27/11/1445H      -> Arts 1, 65, 93 (transfer of competence to
    the Ministry of Culture / Heritage Commission / Museums Commission)
For full-text-replacement amendments (Arts 3, 65, 71-77, 93) the CURRENT in-force text
sits on top and the pre-amendment text is preserved verbatim in history[]. For partial,
term-substitution and paragraph-addition amendments (Arts 1, 12, 29, 54, 85, 90) the
source does not supply a complete consolidated body verbatim, so the enacted body sits
on top and the full amendment annotation (with the new fragment) is preserved in
history[] -- no consolidated text is fabricated. See the source artifact's
verification_methodology_note and known_unresolved_discrepancies for the full account.

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY source) was
checked FIRST per standard methodology: the law HAS a dedicated lawId page
(a7d4493b-7c03-4c2d-b3c6-a9a700f275cd), confirmed via search-engine indexing, but the
live portal was unreachable this pass (HTTP 503 / connection reset). Wayback Machine
is egress-policy-blocked in this environment and was NOT circumvented. The full verbatim
Arabic text of all 94 articles (and all amendment annotations) was therefore extracted
from nezams.com (an independent born-digital HTML aggregator, HTTP 200 -- no scan/OCR
ligature defects). Confidence was reinforced by THREE independent sources: (1) a
BOE-content print PDF of this very law (hosted on media.unesco.org, HTTP 200, generated
27/11/2025) which matched the decree identity, the verbatim preamble, the named repeal
of M/26, and the original article text; (2) the Umm Al-Qura Gazette (uqn.gov.sa), which
independently confirmed the scope of the M/67 amendment (Arts 71-77 + Art 90(1)); and
(3) Arabic Wikipedia, confirming the decree (M/3, 9/1/1436H) and predecessor (M/26,
23/6/1392H).

Diacritics (tashkeel) and decorative kashida are stripped uniformly (the Hijri marker
"هـ" is preserved), Arabic-Indic numerals normalized to Western, and curly double
quotes to straight -- for consistency with this corpus's sibling BOE-family tracks
(water/electricity/agriculture). One disclosed source-rendering quirk is preserved
verbatim, not silently corrected: Article 3's M/103 amendment text renders "مبنی
تاریخي" with a Farsi yeh (ی) in nezams (the pre-amendment text in history uses the
correct Arabic yeh) -- see known_unresolved_discrepancies. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "antiquities_heritage", "law", "official_source",
                   "antiquities_heritage_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "antiquities_heritage", "law", "verified")
RECORDS = os.path.join(OUT_VER, "antiquities_heritage_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "antiquities_heritage_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "antiquities_heritage_arabic_legal_llm",
                        "antiquities_heritage_law_legal_llm_001_094.json")

LAW_ID = "sa-antiquities-heritage-law-m3-1436"
LAW_AR = "نظام الآثار والمتاحف والتراث العمراني"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"antiquities_heritage_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة النظام الآثار التراث العمراني الوزارة").split())


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


def _top_status(ls):
    if ls == "معدلة":
        return STATUS_AMENDED
    if ls == "مضافة":
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
        top_status = _top_status(ls)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "antiquities_heritage", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ANTIQUITIES_HERITAGE_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; نظام الآثار والمتاحف والتراث العمراني "
                                              "(Royal Decree M/3, 9/1/1436H, as amended), which by "
                                              "its own Article 92 repealed/replaced BY NAME the older "
                                              "Antiquities Law (M/26, 23/6/1392H). laws.boe.gov.sa "
                                              "HAS a dedicated lawId page "
                                              "(a7d4493b-7c03-4c2d-b3c6-a9a700f275cd) but was "
                                              "unreachable this pass (HTTP 503 / connection reset), "
                                              "and Wayback is egress-blocked (not circumvented); the "
                                              "verbatim text of all 94 articles was extracted from "
                                              "nezams.com (independent born-digital HTML aggregator), "
                                              "with the decree identity/preamble/named-repeal/original "
                                              "text corroborated by a BOE-content print PDF "
                                              "(unesco.org) and the M/67 amendment scope corroborated "
                                              "by the Umm Al-Qura Gazette. 16 articles are معدلة "
                                              "(amendments never silently merged -- pre-amendment "
                                              "text preserved in amendment_history). TIER_3. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track's text or provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "antiquities-heritage-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "antiquities_heritage/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الآثار والمتاحف والتراث العمراني"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/3), 9/1/1436H "
                                                          "(Council of Ministers Resolution 348, "
                                                          "25/8/1435H; Shura Resolutions 194/78 and "
                                                          "67/38), as amended (M/16 1439H; CoM 693 "
                                                          "1441H; M/67 1442H = CoM 453; M/103 1442H; "
                                                          "CoM 1012 1445H) — the in-force Antiquities, "
                                                          "Museums and Urban Heritage Law, which by "
                                                          "Article 92 repealed/replaced the older M/26 "
                                                          "(23/6/1392H) Antiquities Law by name. "
                                                          "Verbatim text from nezams.com; "
                                                          "laws.boe.gov.sa dedicated lawId page "
                                                          "(a7d4493b-7c03-4c2d-b3c6-a9a700f275cd) "
                                                          "unreachable this pass, Wayback egress- "
                                                          "blocked; corroborated by a BOE-content "
                                                          "print PDF (unesco.org) and the Umm Al-Qura "
                                                          "Gazette (M/67 scope). TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/3) وتاريخ 9/1/1436هـ (قرار مجلس الوزراء 348 وتاريخ 25/8/1435هـ؛ قرارا مجلس الشورى 194/78 و67/38)، وتعديلاته (م/16 1439هـ؛ قرار مجلس الوزراء 693 1441هـ؛ م/67 1442هـ المقترن بقرار مجلس الوزراء 453؛ م/103 1442هـ؛ قرار مجلس الوزراء 1012 1445هـ) — نظام الآثار والمتاحف والتراث العمراني النافذ، الذي حلّ بموجب مادته الثانية والتسعين محل نظام الآثار الأقدم (م/26، 23/6/1392هـ) بالاسم. النص الحرفي من nezams.com؛ صفحة laws.boe.gov.sa المخصصة (lawId a7d4493b-7c03-4c2d-b3c6-a9a700f275cd) غير قابلة للوصول هذه الجولة، وWayback محظور؛ معزّز بملف PDF مطبوع من محتوى هيئة الخبراء (unesco.org) وبجريدة أم القرى (نطاق تعديل م/67). المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "antiquities_heritage",
               "layer": "ANTIQUITIES_HERITAGE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_tier": src.get("verification_tier"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sc = src["status_counts"]
    json.dump({"layer_id": "sa-antiquities-heritage-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (94 مادة؛ %d أصلية، %d معدلة، %d مضافة، %d ملغاة)"
                           % (sc["اصلية"], sc["معدلة"], sc["مضافة"], sc["ملغاة"]),
               "title_en": ("The Saudi Arabian Antiquities, Museums and Urban Heritage Law "
                            "(Royal Decree M/3, 9/1/1436H, as amended) — Arabic LLM-ready layer "
                            "(94 records: %d original, %d amended, %d added, %d repealed)"
                            % (sc["اصلية"], sc["معدلة"], sc["مضافة"], sc["ملغاة"])),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 94], "text_status": STATUS_AMENDED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Antiquities/Heritage Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
