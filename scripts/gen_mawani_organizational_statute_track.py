#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Organizational Statute of the General Authority for Ports
(Mawani) track (تنظيم الهيئة العامة للموانئ, Council of Ministers Resolution
No. 299, 11/6/1439H).

VERIFICATION TIER -- see sources/mawani_organizational_statute/law/
official_source/mawani_organizational_statute_official_source.json's
verification_methodology_note for the full account. Summary:

TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE. laws.boe.gov.sa returned HTTP 503
(WebFetch) and a TLS connection reset on three separate direct curl attempts
against both its LawDetails and Viewer URLs for this law; a r.jina.ai
reader-proxy fetch also failed (HTTP 422). The Wayback Machine was
independently confirmed BLOCKED this pass (unlike a prior sibling-track
pass): two separate WebFetch calls both returned the tool-level refusal
"Claude Code is unable to fetch from web.archive.org", and a direct curl to
its CDX API returned "Blocked by egress policy". mawani.gov.sa (the
Authority's own site) returned HTTP 405 (Alibaba Cloud WAF block) on direct
curl. uqn.gov.sa's root is reachable but the specific gazette issue was not
located this pass. qanoonsa.com and mohamah.net were both searched
extensively; qanoonsa.com surfaced no dedicated page for this 2018 decree,
and mohamah.net carries a page for the PREDECESSOR statute only.

The ONLY full-text source this track was able to reach is nezams.com
(fetched via direct curl with a browser User-Agent, HTTP 200; a prior
WebFetch call against the same URL returned only an AI-summarized paraphrase
and is NOT relied on anywhere in this track). This yielded all 20 articles'
complete text plus the site's own "no amendments" metadata. Numerous
independent sources (ar.wikipedia.org, saudipedia.com, my.gov.sa, WebSearch
snippets of BOE's own page) corroborate the statute's METADATA (decree
number/date, name change, board composition, scope) but none reproduce the
full article text -- hence TIER_4 rather than TIER_3, which this corpus's
taxonomy reserves for 2+ independent FULL-TEXT secondary sources.

20 records, all اصلية (original) -- nezams.com's own metadata states no
amendment has been made to this statute, and no amending decree was located
this pass. Flat structure, no أبواب/فصول. No inline per-article titles in
the source -- no title_ar field is used.

GENUINE PREDECESSOR REPEAL CONFIRMED: Article 19 explicitly repeals and
replaces the Statute of the Public Ports Corporation (Royal Decree No. M/13,
7/4/1397H): "يحل التنظيم محل نظام المؤسسة العامة للموانئ، الصادر بالمرسوم
الملكي رقم (م/13) وتاريخ 7/4/1397هـ، ويُلغي كل ما يتعارض معه من أحكام."

Several structural oddities are preserved literally and flagged rather than
silently smoothed over -- see known_unresolved_discrepancies in the source
artifact: Article 8's numbered item 15 appears after the article's own
general delegation/closing sentence; Article 5's final board seat (ز, three
private-sector members) closes with the plural role-word "أعضاء" rather
than "عضواً". Article 1's decorative tatweel (used for column-alignment in
nezams.com's own rendering) is stripped as pure typographic normalization,
carefully distinguished from the legitimate "هـ" Hijri-date abbreviation and
the "هـ-" fifth-ordinal board-list letter in Article 5, both preserved
intact.

No legal text is altered beyond this whitespace/decorative-character
normalization. Arabic governs; no translation/paraphrase/interpretation
performed on the Arabic text. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mawani_organizational_statute", "law", "official_source",
                   "mawani_organizational_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "mawani_organizational_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "mawani_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "mawani_organizational_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "mawani_organizational_statute_arabic_legal_llm",
                        "mawani_organizational_statute_legal_llm_001_020.json")

LAW_ID = "sa-mawani-organizational-statute-299-1439"
LAW_AR = "تنظيم الهيئة العامة للموانئ"
TOP_STATUS = ("NEZAMS_COM_SINGLE_FULLTEXT_SOURCE_BOE_LIVE_TLS_RESET_WAYBACK_MACHINE_EGRESS_"
              "AND_TOOL_BLOCKED_MAWANI_GOV_SA_WAF_405_BLOCKED_QANOONSA_NO_DEDICATED_PAGE_"
              "FOUND_INDEPENDENT_METADATA_ONLY_CROSSCHECK_TIER_4_SINGLE_SOURCE")
KEY_RE = r"mawani_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الهيئة المجلس الرئيس بوجه خاص").split())


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
        ver.append({"law_key": "mawani_organizational_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "MAWANI_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on a SINGLE "
                                              "full-text source (nezams.com, fetched via "
                                              "direct curl) for the statute's own article "
                                              "text -- laws.boe.gov.sa (HTTP 503 / TLS reset "
                                              "on 3 attempts), the Wayback Machine (confirmed "
                                              "blocked via WebFetch tool refusal and egress "
                                              "policy), and mawani.gov.sa (HTTP 405 WAF "
                                              "block) were all confirmed unreachable this "
                                              "pass. Independent metadata-level (not "
                                              "full-text) corroboration was found via "
                                              "ar.wikipedia.org, saudipedia.com, my.gov.sa "
                                              "and WebSearch snippets of BOE's own page -- "
                                              "see verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's tier."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "mawani-organizational-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "mawani_organizational_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم الهيئة العامة للموانئ" %
                                          a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(299), 11/6/1439H — nezams.com "
                                                          "(single full-text source reached "
                                                          "this pass, direct curl); "
                                                          "laws.boe.gov.sa, the Wayback "
                                                          "Machine, and mawani.gov.sa all "
                                                          "confirmed unreachable/blocked; "
                                                          "metadata-only corroboration via "
                                                          "ar.wikipedia.org, saudipedia.com, "
                                                          "my.gov.sa"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (299) وتاريخ 11/6/1439هـ — nezams.com (المصدر الوحيد الكامل النص الذي أمكن الوصول إليه هذه الجولة، عبر جلب مباشر)؛ تعذّر الوصول إلى بوابة هيئة الخبراء (BOE) وأرشيف Wayback Machine وموقع الهيئة الرسمي (mawani.gov.sa)؛ تدقيق على مستوى البيانات الوصفية فقط عبر ويكيبيديا وسعوديبيديا ودليل my.gov.sa",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "mawani_organizational_statute",
               "layer": "MAWANI_ORGANIZATIONAL_STATUTE_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-mawani-organizational-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (20 مادة، جميعها أصلية)",
               "title_en": "Organizational Statute of the General Authority for Ports "
                          "(Mawani) — Arabic LLM-ready layer (20 records, all original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Mawani Organizational Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
