#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Health System Law track (النظام الصحي,
Royal Decree M/11, 23/3/1423H / 2002G).

VERIFICATION TIER -- see sources/health_system/law/official_source/
health_system_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY SOURCE ACCESS FAILED THIS PASS: laws.boe.gov.sa's live portal
returned HTTP 503 (WebFetch) / HTTP 000 connection-reset (direct curl) on
repeated attempts. The usual fallback in this corpus (Wayback Machine
snapshots) was also unavailable: the WebFetch tool refuses any
web.archive.org request outright, and a direct curl to a snapshot confirmed
to exist via the availability API returned HTTP 403 (an organization egress
policy block on that host for this session, not to be routed around).
istitlaa.ncc.gov.sa (hosting the Implementing Regulation) also failed via
TLS connection reset.

SECONDARY SOURCES (both fetched directly via curl, HTTP 200): nezams.com (an
independent Arabic legal-text aggregator, NOT a BOE mirror) supplied the full
verbatim text of all 19 articles plus inline amendment notes, extracted
programmatically from its raw "subject" HTML elements (19 elements confirmed,
subject-1 through subject-19). qanoonsa.com supplied the full text of Council
of Ministers Resolution No. 151 (24/2/1444H) -- itself a reproduction of the
Umm Al-Qura Gazette publication, not an aggregation of nezams.com -- whose own
preamble independently confirms the founding decree (M/11, 23/3/1423H) and
references four of the five Article-16 amendment resolutions nezams.com
documents in detail (418, 283, 442, 185), plus a fifth (475, 9/11/1436H) that
neither source explains in substance (flagged, not fabricated).

19 records: 15 اصلية (Articles 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
18, 19), 4 معدلة (Articles 4, 5, 16, 17), 0 ملغاة, 0 مضافة. Flat structure,
no أبواب/فصول. No inline per-article titles beyond spelled-ordinal "المادة
..." labels -- no title_ar field is used.

AMENDMENT INCORPORATION: Articles 4 and 5 are a CLEAN case (Royal Decree
M/52, 4/8/1437H, adds one explicitly-numbered sub-paragraph to each -- "1
مكرر" and "12 مكرر" respectively). Article 17 is also clean (CoM Resolution
418, 1435H, adds six explicitly-lettered paragraphs و-ل). Article 16 is the
most complex in this track: five dated CoM/royal amendments are
reconstructable with confidence (418/1435H, 283/1440H, 442/1440H, 185/1443H
for paragraph أ's successive replacements/additions), but the LATEST
confirmed amendment (CoM Resolution 151, 24/2/1444H) is recorded in history[]
without being merged into the article's current text, because neither source
supplies an explicitly-numbered replacement sub-paragraph for it (unlike
283/442's explicit numbering) -- fabricating an insertion point would violate
this corpus's no-fabrication rule. A sixth citation (CoM Resolution 475,
9/11/1436H) is referenced by Resolution 151's own preamble but its substance
is undocumented in either source -- flagged, not incorporated.

PREDECESSOR REPEAL: Article 19 repeals only generically ("يلغي كل ما
يتعارض معه من أحكام") -- NO named predecessor law is repealed. This is a
confirmed negative finding, not a research gap.

No legal text is altered beyond whitespace/HTML-entity normalization needed
to convert nezams.com's raw HTML into plain text, and the amendment
incorporation described above. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "health_system", "law", "official_source",
                   "health_system_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "health_system", "law", "verified")
RECORDS = os.path.join(OUT_VER, "health_system_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "health_system_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "health_system_arabic_legal_llm",
                        "health_system_law_legal_llm_001_019.json")

LAW_ID = "sa-health-system-law-m-11-1423"
LAW_AR = "النظام الصحي"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"health_system_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_NUMS = (4, 5, 16, 17)
AMENDED_KEYS = {"health_system_art_%03d" % n for n in AMENDED_NUMS}
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الصحة الصحية الوزارة الوزير").split())


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
        ver.append({"law_key": "health_system", "law_component": "law",
                    "language": "ar",
                    "record_layer": "HEALTH_SYSTEM_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on TWO "
                                              "independently-fetched secondary legal sources "
                                              "(nezams.com and qanoonsa.com, neither a BOE mirror "
                                              "nor a mirror of each other) because laws.boe.gov.sa "
                                              "(live and via Wayback Machine) and "
                                              "istitlaa.ncc.gov.sa were all unreachable this pass. "
                                              "4 of 19 articles are معدلة (4, 5, 16, 17). Article "
                                              "16's most recent confirmed amendment (CoM Resolution "
                                              "151, 1444H) is recorded in amendment_history but NOT "
                                              "merged into this article's current text, because "
                                              "neither source gives an explicitly-numbered "
                                              "replacement sub-paragraph for it -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on Article 16's text or "
                                              "its full amendment provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "health-system-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "health_system/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من النظام الصحي" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/11 (23/3/1423H) — "
                                                          "reconstructed from nezams.com and "
                                                          "qanoonsa.com, two independent "
                                                          "secondary sources; laws.boe.gov.sa "
                                                          "(live and via Wayback Machine) and "
                                                          "istitlaa.ncc.gov.sa were unreachable "
                                                          "this pass"),
                                     "source_authority_ar": "المرسوم الملكي رقم م/11 وتاريخ 23/3/1423هـ — أُعيد بناؤه من nezams.com وqanoonsa.com (مصدران ثانويان مستقلان)؛ تعذّر الوصول إلى بوابة هيئة الخبراء (حياً ومؤرشفاً) وإلى istitlaa.ncc.gov.sa هذه الجولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "health_system",
               "layer": "HEALTH_SYSTEM_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-health-system-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة؛ 15 أصلية و4 معدلة)",
               "title_en": "Saudi Arabian Health System Law — Arabic LLM-ready layer (19 records: 15 original, 4 amended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Health System Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
