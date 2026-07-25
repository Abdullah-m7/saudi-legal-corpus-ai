#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Commercial Register Law track
(اللائحة التنفيذية لنظام السجل التجاري, Ministry of Commerce Decision No. (288),
20 Ramadan 1446H / 20 March 2025G, issued under Article (28) of the Commercial
Register Law, Royal Decree M/83, 19/3/1446H).

DISAMBIGUATION FROM THE JOINT MINISTERIAL DECISION -- see this track's source
artifact (sources/commercial_register_regulation/law/official_source/
commercial_register_regulation_official_source.json, verification_methodology_note
and known_unresolved_discrepancies) for the full account. Summary: MoC Decision
288 is a single ministerial signature that simultaneously approves FOUR entirely
separate, independently-titled, independently-numbered instruments: (1) this
Regulation (21 articles + Annex 1) -- the sole scope of this track; (2) the
Implementing Regulation of the Trade Names Law (a fully separate document, built
in a fully separate track by another agent); (3) the Mechanism for Correcting
Subsidiary Commercial Register Status (a distinct transitional instrument, 7
numbered points, itself commercial-register-specific but NOT part of this
Regulation's own 21 articles -- deliberately left OUT of scope, flagged as a
candidate for a possible future companion track); (4) Controls for Trade Names
Registered Before the Trade Names Law's Effective Date (trade-names-specific,
out of scope). The disambiguation is clean and verified directly from the full
text of the Decision itself (qanoonsa.com/p/507901/), not inferred or guessed.

VERIFICATION TIER: TIER_2. PRIMARY-ish source: qanoonsa.com/p/507902/ (a legal
aggregator that reproduces the Umm al-Qura Gazette text and states the Decision
number and gazette issue/date explicitly within the page), fetched directly via
curl (HTTP 200, clean static HTML -- not a dynamic SPA like qanoniah.com, which
was also checked but its article body could not be extracted from static HTML).
laws.boe.gov.sa was checked FIRST per this corpus's standard methodology: a
lawId page surfaced by web search (98ee4b51-d398-4323-ae69-b2b8009f3156) was
fetched via two independent-date Wayback Machine snapshots (2025-04-08,
2025-08-07) and found to actually be the BASE LAW's page (29 articles, "نظام
السجل التجاري"), not a dedicated page for this Implementing Regulation -- no
dedicated BOE lawId page exists for this Regulation, consistent with the
corpus-wide pattern of BOE not indexing ministerial-level regulations as
standalone lawId records. Direct queries to mc.gov.sa and uqn.gov.sa failed
completely this pass (connection failure, HTTP 000); a Wayback snapshot of the
MoC's own news release (mc.gov.sa/ar/mediacenter/News/Pages/03-04-25-01.aspx,
snapshot 2025-04-06) was fetched instead and corroborates the effective date
and general reform description (but does not carry the Regulation's article
text). CROSS-VERIFICATION: aleqt.com (Al-Eqtisadiah, a well-known Saudi
financial daily) independently confirms the 21-article count and multiple
verbatim phrases matching qanoonsa.com's text exactly (Article 6's full
sentence, Article 7's 15-day period, Article 11's 90-day period, Article 13's
60/180-day periods, and the 5-year subsidiary-correction period).

21 sequential articles, NO chapters (flat structure -- confirmed by direct
inspection of the raw HTML, which contains no "الفصل" heading at all, unlike
the base Law's 6 chapters). Plus Annex (1) "المقابل المالي للخدمات المتعلقة
بالسجل التجاري" (a 3-column fee table referenced by Article 18), preserved
verbatim in the source artifact's annex_ar field and NOT split into
per-article records (consistent with this corpus's franchise_regulation and
disability_rights_regulation precedents for non-numbered annexes).

ALL 21 articles are اصلية (fresh full issuance; 0 معدلة, 0 ملغاة, 0 مضافة) --
this is the founding Implementing Regulation for the new base Law, replacing
the prior 1416H/1996H Implementing Regulation in its entirety.

DOCUMENTED SOURCE ANOMALIES, preserved verbatim (not silently corrected): (1)
Article 19's violation-classification table shows mismatched/reversed
parentheses in the fine amounts for rows 2-4 (")500)" / ")1000)" instead of
"(500)" / "(1000)"), confirmed from the raw HTML <table> structure itself (not
an extraction artifact of this track); (2) Annex 1's last service row reads
"السجل تجاري" (missing the definite article "ال" before "تجاري").

Text normalization: only the invisible RIGHT-TO-LEFT MARK (U+200F) inserted by
the source page's WordPress editor around Arabic-Indic digits/dashes was
stripped (72 occurrences; confirmed not part of the legal text itself). No
visible spacing, digits, or punctuation actually present in the raw HTML was
altered (e.g. the space before the enumerator dash after "هـ" in Articles 15
and 17 is genuinely present in the raw HTML and is preserved, not introduced by
this track). Arabic-Indic digits are preserved verbatim as sourced (consistent
with the majority convention across this corpus). Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_register_regulation", "law", "official_source",
                   "commercial_register_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "commercial_register_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "commercial_register_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "commercial_register_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "commercial_register_regulation_arabic_legal_llm",
                        "commercial_register_regulation_legal_llm_001_021.json")

LAW_ID = "sa-commercial-register-regulation-288-1446"
LAW_AR = "اللائحة التنفيذية لنظام السجل التجاري"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"commercial_register_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
N_ARTICLES = 21
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم التاجر المسجل").split())


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


GOV_NOTE = ("Arabic governs; PRIMARY-ish source is qanoonsa.com/p/507902/ (a legal aggregator "
            "reproducing the Umm al-Qura Gazette text, stating Decision No. (288) and gazette "
            "issue (5079, 30 March 2025G) explicitly within the page) -- fetched directly (HTTP "
            "200, clean static HTML). laws.boe.gov.sa was checked first per this corpus's "
            "standard methodology but has NO dedicated lawId page for this Implementing "
            "Regulation (the lawId surfaced by web search is actually the BASE LAW's page, "
            "confirmed by direct inspection of its Wayback Machine snapshots). Cross-verified "
            "against aleqt.com (Al-Eqtisadiah, independent Saudi financial daily) for article "
            "count and multiple verbatim phrases -> TIER_2. 21 sequential articles, NO chapters; "
            "ALL اصلية (fresh full issuance). MoC Decision 288 jointly approves THREE further "
            "entirely separate instruments (Trade Names Regulation, a subsidiary-register "
            "correction mechanism, and pre-existing trade-name controls) -- cleanly disambiguated "
            "and confirmed from the Decision's own text; NONE of their content is included here. "
            "See verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Ministry of Commerce Decision No. (288) (20 Ramadan 1446H / 20 March 2025G), issued "
            "under Article (28) of the Commercial Register Law (Royal Decree M/83, 19/3/1446H). "
            "Full text from qanoonsa.com (legal aggregator reproducing the Umm al-Qura Gazette "
            "text, issue 5079) cross-checked against aleqt.com (Al-Eqtisadiah, independent "
            "secondary source) -> TIER_2. laws.boe.gov.sa has no dedicated lawId page for this "
            "Implementing Regulation (only for the base Law).")

SRC_AUTH_AR = ("قرار وزير التجارة رقم (288) وتاريخ 20 رمضان 1446هـ (20 مارس 2025م)، صادر استنادا "
               "إلى المادة (الثامنة والعشرين) من نظام السجل التجاري (المرسوم الملكي رقم م/83، "
               "19/3/1446هـ). النص الكامل من qanoonsa.com (مجمّع قانوني يستنسخ نص جريدة أم القرى، "
               "العدد 5079) متقاطع مع aleqt.com (الاقتصادية، مصدر ثانوي مستقل) -- TIER_2. بوابة "
               "هيئة الخبراء (laws.boe.gov.sa) لا تملك صفحة lawId مخصصة لهذه اللائحة التنفيذية "
               "(فقط للنظام الأساسي).")


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
        ver.append({"law_key": "commercial_register_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "COMMERCIAL_REGISTER_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": a.get("article_title_ar", ""),
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "commercial-register-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "commercial_register_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام السجل التجاري"
                                          % a["number_label_ar"]],
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
    json.dump({"law_key": "commercial_register_regulation",
               "layer": "COMMERCIAL_REGISTER_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "annex_ar": src.get("annex_ar"),
               "gazette_publication": src.get("gazette_publication"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-commercial-register-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (21 مادة؛ إصدار كامل: 21 أصلية)",
               "title_en": ("Implementing Regulation of the Commercial Register Law — Arabic "
                            "LLM-ready layer (21 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, N_ARTICLES], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Commercial Register Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
