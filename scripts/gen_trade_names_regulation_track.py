#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Trade Names Law track
(اللائحة التنفيذية لنظام الأسماء التجارية), issued under clause "ثانيا" (Second)
of Ministry of Commerce Decision No. (288), dated 20 Ramadan 1446H (20 March
2025G), published in Umm al-Qura Gazette Issue No. 5079 (30 March 2025G / 1
Shawwal 1446H).

JOINT-DECISION DISAMBIGUATION (see the source artifact's disambiguation_note_ar
for the full account): Decision 288 is a single OMNIBUS decision that approves
FOUR distinct instruments in one document:
  اولا   - Implementing Regulation of the Commercial Register Law (separate
           track: commercial_register_regulation -- built independently by
           another worker; NOT ingested here)
  ثانيا  - Implementing Regulation of the Trade Names Law -- THIS track (18
           articles + Annex 1, the fee schedule)
  ثالثا  - Mechanism for correcting subsidiary/branch commercial-register
           status -- a Commercial-Register-side transitional instrument; out
           of scope for both tracks; NOT ingested here
  رابعا  - Controls for trade names registered before the Trade Names Law's
           effectiveness -- a DISTINCT, separately-titled trade-names-adjacent
           transitional instrument; NOT itself "the Implementing Regulation";
           disclosed as out-of-scope but its own text was NOT fetched/verified
           this pass
Disambiguation method: read the decision's own operative text (منطوق) verbatim
from qanoonsa.com/p/507901/, which names all four instruments explicitly by
title, and confirmed that qanoonsa.com itself indexes each of the four as a
separate page (507902 = Commercial Register regulation, 507903 = this track)
with explicit prev/next navigation links confirming they are treated as
distinct documents, not sections of one document.

VERIFICATION TIER: TIER_3. No direct .gov.sa-hosted copy of THIS REGULATION's
text was reachable this pass: uqn.gov.sa (issue 5079) is a Vue.js SPA that
returns only unrendered template markup; laws.boe.gov.sa has no dedicated
LawDetails page for this 2025 ministerial regulation; a direct curl fetch of
mc.gov.sa's own Regulations page failed at the connection level (HTTP 000).
PRIMARY TEXT SOURCE: qanoonsa.com/p/507903/ (fetched directly, HTTP 200) -- a
private Saudi legal database that explicitly disclaims being an official
source in its own footer. Cross-checked via: (1) a Wayback Machine snapshot of
the SAME page (2026-05-21), byte-identical for the full article-body zone; (2)
an independent secondary source (ndmlaw.sa, a law-firm commentary) quoting
Articles 6, 8, and 10 verbatim-matching; (3) mc.gov.sa's own news release
(fetched via WebFetch) confirming Decision 288, Royal Decree M/83, and the
joint effective date -- metadata only, not full text.

18 articles, ALL اصلية, plus one non-article annex (مرفق ١، fee schedule),
ALSO اصلية. Flat regulation (no chapters/فصول). No repeal of any predecessor
instrument confirmed in the text (Article 18 ties entry into force to the
underlying Trade Names Law's own effective date; the predecessor 1420H
implementing regulation, per WIPO Lex, is superseded only implicitly via the
new LAW's own Article 23 repeal of the predecessor LAW -- see
known_unresolved_discrepancies).

A Hijri-date error in the prior research lead that pointed to this track
("30 Rabi' II 1446H") is corrected here via independent Hijri<->Gregorian
conversion plus direct reading of the decision's own operative text: the
decision was SIGNED 20 Ramadan 1446H (20 March 2025G) and PUBLISHED in Umm
al-Qura Gazette No. 5079 on 1 Shawwal 1446H (30 March 2025G).

Arabic governs; no translation/paraphrase/interpretation performed on the
Arabic text. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "trade_names_regulation", "law", "official_source",
                   "trade_names_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "trade_names_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "trade_names_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "trade_names_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "trade_names_regulation_arabic_legal_llm",
                        "trade_names_regulation_legal_llm_001_019.json")

LAW_ID = "sa-trade-names-regulation-moc-288-1446h"
LAW_AR = "اللائحة التنفيذية لنظام الأسماء التجارية"
N_RECORDS = 19
KEY_RE = r"trade_names_regulation_(art|annex)_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك المسجل التاجر الوزارة").split())


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
    kind, n = m.group(1), int(m.group(2))
    return (1 if kind == "annex" else 0, n)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    # deterministic order: 18 articles (001..018) first, then the annex
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        is_annex = bool(a.get("is_annex"))
        n = int(re.match(KEY_RE, key).group(2))
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        ver.append({"law_key": "trade_names_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "TRADE_NAMES_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_annex": is_annex, "is_mukarrar": False,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": a.get("article_title_ar", ""),
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": a.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": "UNCHANGED",
                    "governing_source_note": (
                        "Arabic governs; primary text from qanoonsa.com (fetched directly, HTTP "
                        "200), which explicitly disclaims being an official source. Cross-checked "
                        "via a byte-identical Wayback Machine snapshot of the same page, an "
                        "independent secondary source (ndmlaw.sa) with verbatim-matching quotes, "
                        "and mc.gov.sa's own news release confirming Decision 288 and Royal "
                        "Decree M/83 -> TIER_3. laws.boe.gov.sa has no dedicated page for this "
                        "2025 ministerial regulation; uqn.gov.sa (Gazette 5079) is an unrenderable "
                        "SPA; direct mc.gov.sa fetch failed at the connection level. This is a "
                        "JOINT decision covering four instruments; ONLY clause \"ثانيا\" (this "
                        "regulation) is ingested here -- see disambiguation_note_ar in the source "
                        "artifact."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_annex": is_annex, "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"] + (
                        " - " + a["article_title_ar"] if a.get("article_title_ar") else ""),
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "trade-names-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_annex" if is_annex else "verified_arabic_article",
                    "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "trade_names_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الأسماء التجارية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"], "verification_tier": a.get("verification_tier"),
                    "source_trust": {"source_authority": ("Ministry of Commerce Decision No. 288 "
                                                          "(20 Ramadan 1446H / 20 March 2025G), "
                                                          "clause 'ثانيا'; text from qanoonsa.com, "
                                                          "cross-checked -> TIER_3"),
                                     "source_authority_ar": ("قرار وزير التجارة رقم (٢٨٨)، البند "
                                                             "(ثانيا)؛ النص من qanoonsa.com، "
                                                             "مُحقَّق تقاطعيا -> TIER_3"),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "trade_names_regulation",
               "layer": "TRADE_NAMES_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "gazette_issue": src.get("gazette_issue"),
               "gazette_publication_gregorian": src.get("gazette_publication_gregorian"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "disambiguation_note_ar": src["disambiguation_note_ar"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "provenance": src["provenance"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-trade-names-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                                    "(18 مادة + مرفق واحد؛ 19 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation of the Trade Names Law — Arabic LLM-ready "
                            "layer (18 articles + 1 annex = 19 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 18], "annex_count": 1, "text_status": "UNCHANGED",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Trade Names Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
