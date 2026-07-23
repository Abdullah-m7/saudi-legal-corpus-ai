#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Universities Law track (نظام الجامعات, Royal Decree M/27,
2/3/1441H -- the fresh higher-education/universities law that replaced the older
نظام مجلس التعليم العالي والجامعات).

IDENTITY / CITATION -- Royal Decree No. (M/27) dated 2/3/1441H, approving Council
of Ministers Resolution No. 183 dated 1/3/1441H (Shura Council Resolution No.
61/239 dated 28/2/1440H). Published in the Official Gazette (Umm al-Qura) on
11/3/1441H; enters into force 180 days after publication (Article 58). 58 articles
across 14 chapters (فصول). Administered by the Council of Universities' Affairs
(cua.gov.sa) and the Ministry of Education (moe.gov.sa). All identity facts
cross-verified: the cover of the administering authority's own official edition
(cua.gov.sa PDF) carries "المرسوم الملكي رقم (م/27) وتاريخ 1441/3/2هـ"; the BOE
portal's search-indexed lawId page, the KSU faculty blog title, and moe.gov.sa all
agree on M/27, 2/3/1441H and on the 58-article / 14-chapter structure.

NAMED REPEAL OF PREDECESSOR -- Article 57 reads verbatim (confirmed in BOTH the
born-digital full-text source AND the government PDF): "يحل هذا النظام محل نظام
مجلس التعليم العالي والجامعات، الصادر بالمرسوم الملكي رقم (م/8) وتاريخ 4/6/1414هـ
ويلغي جميع ما يتعارض معه من أحكام". This is a replace-and-repeal-conflicting-
provisions clause. NOTE the Royal Decree itself (clauses 3 & 4) keeps the OLD law
transitionally in force for universities not yet brought under the new law -- i.e.
the replacement is phased, not instantaneous. The predecessor (M/8, 4/6/1414H) is
not currently a standalone track in this corpus; it is flagged as a real named
repeal/supersession candidate for the repository-level graph (owner decision).

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY source)
was checked FIRST per standard methodology but is unreachable this pass (WebFetch
HTTP 503; direct curl HTTP 000 connection-reset), and web.archive.org egress is
blocked by this session's policy (NOT circumvented) -- matching the pattern this
corpus's water_law / electricity_law / food / health_system tracks documented for
the same domains. The full verbatim text of all 58 articles was extracted from
bibliotdroit.com (a clean born-digital HTML page, HTTP 200 -- NOT a scanned/OCR
PDF) and cross-verified article-by-article (distinctive-phrase matching, after
normalising both sides) against the administering authority's OWN official edition
(cua.gov.sa PDF, HTTP 200), with the 58-article / 14-chapter structure independently
re-confirmed by moe.gov.sa. This is at the strong end of TIER_3 (one corroborating
full-text source is the applying government authority's own published edition), but
remains TIER_3 because the BOE primary text could not be pinned directly this pass.

58 articles across 14 chapters; all 58 اصلية (original/unamended -- no amendments
recorded); 0 معدلة, 0 ملغاة, 0 مضافة. Diacritics (tashkeel) are stripped uniformly
for consistency with this corpus's BOE-family / water_law / electricity_law tracks
(the legitimate Hijri marker "هـ" is preserved; source has no in-word decorative
tatweel). Source digits are Latin (0-9) and preserved as-is. The Royal Decree
preamble is NOT ingested verbatim (the government PDF extraction dropped the
Arabic-Indic digits and carries typeset artifacts, and BOE was unreachable); its
issuing facts are recorded as explicit metadata in preamble_ar. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "universities", "law", "official_source",
                   "universities_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "universities", "law", "verified")
RECORDS = os.path.join(OUT_VER, "universities_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "universities_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "universities_arabic_legal_llm",
                        "universities_law_legal_llm_001_058.json")

LAW_ID = "sa-universities-law-m27-1441"
LAW_AR = "نظام الجامعات"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"universities_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الجامعة الجامعات المجلس مجلس").split())


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
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; this is the Saudi Universities Law (نظام الجامعات, "
                "Royal Decree M/27, 2/3/1441H), which by its own Article 57 replaces "
                "and repeals conflicting provisions of the predecessor نظام مجلس "
                "التعليم العالي والجامعات (M/8, 4/6/1414H) -- a phased replacement, as "
                "the Royal Decree keeps the old law transitionally in force for "
                "universities not yet brought under the new one. laws.boe.gov.sa was "
                "checked FIRST per standard methodology but is unreachable this pass "
                "(HTTP 503 / connection reset) and Wayback is egress-blocked; the "
                "verbatim text of all 58 articles was extracted from bibliotdroit.com "
                "(a clean born-digital HTML page) and cross-verified article-by-article "
                "against the administering authority's own official edition "
                "(cua.gov.sa PDF), with the 58-article/14-chapter structure "
                "re-confirmed by moe.gov.sa. TIER_3. See verification_methodology_note "
                "and known_unresolved_discrepancies in the source artifact before "
                "relying on this track -- in particular the recommended re-verification "
                "of verbatim text against laws.boe.gov.sa, the phased/transitional "
                "nature of the Article-57 repeal, and the preamble not being ingested "
                "verbatim.")
    src_auth = ("Royal Decree No. (M/27), 2/3/1441H (Council of Ministers Resolution "
                "183, 1/3/1441H; Shura Resolution 61/239, 28/2/1440H; Umm al-Qura "
                "11/3/1441H) -- the Saudi Universities Law, which by Article 57 "
                "replaces/repeals-conflicting-provisions of the predecessor Higher "
                "Education Council and Universities Law (M/8, 4/6/1414H), phased in "
                "transitionally. Verbatim text from bibliotdroit.com (born-digital "
                "HTML), cross-verified article-by-article against the administering "
                "authority's own official edition (cua.gov.sa PDF); structure "
                "re-confirmed by moe.gov.sa. laws.boe.gov.sa unreachable this pass, "
                "Wayback egress-blocked. TIER_3.")
    src_auth_ar = ("المرسوم الملكي رقم (م/27) وتاريخ 2/3/1441هـ (قرار مجلس الوزراء 183 "
                   "وتاريخ 1/3/1441هـ؛ قرار مجلس الشورى 61/239 وتاريخ 28/2/1440هـ؛ نشر أم "
                   "القرى 11/3/1441هـ) -- نظام الجامعات، الذي يحل بموجب مادته السابعة "
                   "والخمسين محل نظام مجلس التعليم العالي والجامعات (م/8، 4/6/1414هـ) "
                   "ويلغي ما يتعارض معه، إحلالاً مرحلياً انتقالياً. النص الحرفي من "
                   "bibliotdroit.com (HTML مولود رقمياً)، متحقَّق مادةً بمادة ضد النسخة "
                   "الرسمية لمجلس شؤون الجامعات (cua.gov.sa)، والبنية مؤكدة من وزارة "
                   "التعليم. laws.boe.gov.sa غير متاح هذه الجولة، وWayback محظور. المستوى "
                   "TIER_3.")

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
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "universities", "law_component": "law",
                    "language": "ar",
                    "record_layer": "UNIVERSITIES_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "universities-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "universities/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الجامعات" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": src_auth,
                                     "source_authority_ar": src_auth_ar,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "universities",
               "layer": "UNIVERSITIES_LAW_ARABIC_VERIFIED_TEXT",
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
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-universities-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (58 مادة؛ 58 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("The Saudi Universities Law (Royal Decree M/27, 2/3/1441H) — "
                            "Arabic LLM-ready layer (58 records: 58 original, 0 amended, "
                            "0 added, 0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 58], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Universities Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
