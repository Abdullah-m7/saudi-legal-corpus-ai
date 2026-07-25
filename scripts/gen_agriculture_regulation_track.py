#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Agriculture Law track (اللائحة التنفيذية لنظام
الزراعة -- issued by Ministerial Decision No. 14967/1/1444, 15/1/1444H, pursuant to Article 36
of the Agriculture Law, Royal Decree M/64, 10/8/1442H).

STANDALONE COMPANION TRACK -- built independently in this worktree, mirroring the structural
conventions of scripts/gen_agriculture_law_track.py (the already-ingested base-law track at
sources/agriculture/) but NOT touching any shared pipeline file. Reads only from this track's
own sources/agriculture_regulation/law/official_source/ artifact and writes only to this
track's own sources/agriculture_regulation/law/verified/ and
data/agriculture_regulation_arabic_legal_llm/ paths.

STRUCTURE -- 271 articles across NINE أبواب (Parts): الأول (التعريفات، دون فصول)؛ الثاني (أعمال
ونشاط القطاع الزراعي، 4 فصول)؛ الثالث (الثروة النباتية، 4 فصول)؛ الرابع (الجمعيات التعاونية
الزراعية والجمعيات الأهلية الزراعية، دون فصول)؛ الخامس (الأبحاث والإرشاد الزراعي، دون فصول)؛
السادس (الثروة الحيوانية، 11 فصلاً بما فيها فصل تربية النحل)؛ السابع (الثروة المائية الحية، 3
فصول)؛ الثامن (الرقابة والتفتيش وضبط المخالفات، 5 فصول)؛ التاسع (أحكام عامة، دون فصول). No مكرر
articles.

FULL-TEXT SOURCE -- Umm Al-Qura Official Gazette itself (uqn.gov.sa/details?p=20060), NOT a
private aggregator: this is a materially stronger primary source than the base law's own
(nezams.com). laws.boe.gov.sa was checked first but is unreachable this pass (HTTP 503) and does
not appear to separately index this Implementing Regulation at all in the search results
available. Cross-verified structurally and substantively (spot-checked) against the Ministry's
own official PDF (mewa.gov.sa, 86pp -- table of contents matches exactly, incl. the easy-to-miss
11th فصل "تربية النحل"), though that PDF has known text-extraction font-corruption artifacts
(justification/kashida-related letter duplication) and was therefore NOT used as a verbatim
source. Also cross-checked against qanoonsa.com for the amendment decisions.

AMENDMENTS -- TWO independently confirmed: (1) Ministerial Decision No. 15065837, 15/3/1446H
(Umm Al-Qura issue 5060, 13 Dec 2024G), added the "المخالفة الجسيمة" (gross violation)
definition to Article 1 -- text confirmed via qanoonsa.com's verbatim quotation and
cross-matched substantively against the current mewa.gov.sa PDF; INCORPORATED into Article 1's
stored text (consolidated_amended_law=True). (2) Ministerial Decision No. 15227269, 15/12/1447H
(published 11/1/1448H / 26 June 2026G), approved amendments to Articles 45, 98, 208, and
paragraph 5 of Article 248 -- but the actual attached amended wording ("الصيغة المرفقة") could
NOT be retrieved from any source reachable this pass (confirmed the current mewa.gov.sa PDF has
NOT yet been updated to reflect it: Article 45's text there is byte-identical to the 2022
original). Per this corpus's binding trust rule, the ORIGINAL (pre-2026-amendment) text is kept
for these four articles, honestly flagged legal_status_ar="معدلة" / status=
"AMENDED_TEXT_UNCONFIRMED" / text_complete=False -- NOT fabricated, NOT silently left as
"اصلية". A third possible amendment (a public consultation draft for Article 245 on
istitlaa.ncc.gov.sa) was found via WebSearch but that page was completely unreachable this pass
(repeated connection resets); its status (draft vs. adopted) could not be determined, so it is
NOT incorporated.

VERIFICATION TIER -- documented per-article variation (has_per_article_variation=True in the
source artifact): 267 of 271 articles are effectively TIER_2-equivalent (one official/primary
source -- Umm Al-Qura -- whose text was adopted, cross-audited structurally/substantively
against a second official source and a private aggregator); the 4 articles above carry
unconfirmed post-amendment text. Following this corpus's convention of grading a track by its
WEAKEST verified part, the track-level tier is TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE. See
verification_methodology_note and known_unresolved_discrepancies in the source artifact.

Diacritics (tashkeel) and decorative kashida are stripped uniformly (only when kashida is
genuinely decorative, i.e. sits between two Arabic letters and is not part of a legitimate
"هـ" marker); a Farsi yeh in Article 1 is normalized to Arabic yeh. Legitimate embedded Latin
text (scientific species names, standard/document-type codes, org acronyms like OIE/GPS/CI/BOL)
is preserved verbatim -- this track's validator does not treat ALL Latin characters as leftover
artifacts (unlike the base law's flat statute, this regulation's technical annexed-style
provisions genuinely contain such tokens in the primary source). Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "agriculture_regulation", "law", "official_source",
                   "agriculture_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "agriculture_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "agriculture_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "agriculture_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "agriculture_regulation_arabic_legal_llm",
                        "agriculture_regulation_legal_llm_001_271.json")

LAW_ID = "sa-agriculture-regulation-mewa-1444"
LAW_AR = "اللائحة التنفيذية لنظام الزراعة"
KEY_RE = r"agriculture_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير الهيئة القطاع الزراعي الزراعية").split())


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
        top_status = a["status"]
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "agriculture_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "AGRICULTURE_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this is the Implementing "
                                              "Regulation of the Agriculture Law (Ministerial "
                                              "Decision 14967/1/1444, 15/1/1444H; base law: "
                                              "Royal Decree M/64, 10/8/1442H), a standalone "
                                              "companion track built this pass. Full text "
                                              "sourced from the Umm Al-Qura Official Gazette "
                                              "(uqn.gov.sa) -- a primary government source, not "
                                              "a private aggregator -- structurally/"
                                              "substantively cross-verified against MEWA's own "
                                              "PDF and qanoonsa.com. TWO confirmed amendments: "
                                              "2024 decision 15065837 (Art.1 'المخالفة الجسيمة' "
                                              "definition, INCORPORATED) and 2026 decision "
                                              "15227269 (Arts. 45/98/208/248(5), touched but "
                                              "new wording UNCONFIRMED -- pre-amendment text "
                                              "kept, honestly flagged). Track-level tier: "
                                              "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE "
                                              "(documented per-article variation; see "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on Arts. 45/98/208/248)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "agriculture-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "agriculture_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الزراعة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. "
                                                          "(14967/1/1444), 15/1/1444H (MEWA), "
                                                          "issued under Article 36 of the "
                                                          "Agriculture Law (Royal Decree M/64, "
                                                          "10/8/1442H). Verbatim text from the "
                                                          "Umm Al-Qura Official Gazette "
                                                          "(uqn.gov.sa) -- a primary government "
                                                          "source. Structurally/substantively "
                                                          "cross-verified against mewa.gov.sa's "
                                                          "own PDF and qanoonsa.com. Track tier "
                                                          "TIER_4_SINGLE_SOURCE_OR_MIXED_"
                                                          "CONFIDENCE (documented per-article "
                                                          "variation on Arts. 45/98/208/248 -- "
                                                          "confirmed amended but new wording "
                                                          "unconfirmed this pass)."),
                                     "source_authority_ar": ("صادرة بالقرار الوزاري رقم "
                                                            "(14967/1/1444) وتاريخ 15/1/1444هـ "
                                                            "(وزارة البيئة والمياه والزراعة)، "
                                                            "إعمالاً للمادة (36) من نظام "
                                                            "الزراعة (م/64). النص الحرفي من "
                                                            "جريدة أم القرى الرسمية "
                                                            "(uqn.gov.sa) -- مصدر حكومي أساسي "
                                                            "-- مع تدقيق بنيوي/مضموني مقابل "
                                                            "ملف mewa.gov.sa الرسمي وqanoonsa."
                                                            "com. تصنيف المسار: TIER_4 (ثقة "
                                                            "متفاوتة موثَّقة على المواد 45/98/"
                                                            "208/248: تعديلها مؤكَّد لكن نصها "
                                                            "الجديد غير مؤكَّد هذه الجولة)."),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "agriculture_regulation",
               "layer": "AGRICULTURE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "base_law_key": src.get("base_law_key"),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_decree_date_hijri": src.get("base_law_decree_date_hijri"),
               "issuing_decision": src["issuing_decision"],
               "issuing_decision_date_hijri": src["issuing_decision_date_hijri"],
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_tier": src.get("verification_tier"),
               "has_per_article_variation": src.get("has_per_article_variation"),
               "per_article_variation_note": src.get("per_article_variation_note"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "amended_article_keys": src.get("amended_article_keys", []),
               "amended_text_unconfirmed_article_keys":
                   src.get("amended_text_unconfirmed_article_keys", []),
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-agriculture-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (271 مادة؛ "
                           "266 أصلية، 5 معدلة، 0 مضافة، 0 ملغاة؛ تسعة أبواب)",
               "title_en": ("The Implementing Regulation of the Agriculture Law "
                            "(Ministerial Decision 14967/1/1444, 15/1/1444H) — Arabic LLM-ready "
                            "layer (271 records: 266 original, 5 amended [1 fully confirmed, 4 "
                            "with unconfirmed post-amendment wording], 0 added, 0 repealed; "
                            "nine Parts)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 271],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "verification_tier": src.get("verification_tier"),
               "has_per_article_variation": src.get("has_per_article_variation"),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Agriculture Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
