#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Mining Investment Law track
(اللائحة التنفيذية لنظام الاستثمار التعديني, Ministerial Decision No. 1006/1/1442,
dated 9/5/1442H, issued by the Minister of Industry and Mineral Resources;
published Official Gazette 17/5/1442H = 1/1/2021G; amended by Ministerial
Decision No. 3293/1/1444, dated 5/6/1444H). Implementing regulation of the
mining_investment_law base-law track already in this corpus (Royal Decree
M/140, 19/10/1441H, 64 articles) -- NOT touched this pass.

VERIFICATION TIER -- see sources/mining_investment_implementing_regulation/
law/official_source/mining_investment_implementing_regulation_official_
source.json's verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: uqn.gov.sa (Umm Al-Qura Official Gazette)'s own dedicated page
for this regulation (?p=2083). The LIVE page returns only a generic client-
rendered SPA shell on direct fetch (no article content); a confirmed Wayback
Machine snapshot (20251011171315) of the SAME url IS server-rendered and
carries the full Gutenberg-block HTML body inline. Fetched via curl against
the archive's raw ('id_') rendering, parsed with BeautifulSoup walking every
<p>/<table> element in document order (never naive tag-stripping); 166
sequential "المادة ...:" headings recovered across 7 أبواب (with نested فصول
in أبواب 1-5). The ONE in-body <table> (Article 86's rehabilitation-cost
schedule) was merged row-by-row into that article's own text; the 6 numbered
ملاحق appearing after Article 166 are deliberately NOT modeled as additional
article records (see known_unresolved_discrepancies) -- a disclosed scope
boundary, not lost content.

SUBSTANTIVE CROSS-CHECK: argaam.com's own coverage of this regulation
(fetched via WebFetch) paraphrases two specific provisions; both were found
VERBATIM in the extracted text (Article 11.1 mining-reserve-zone designation;
Article 135.3 Category-B mineral export fee/cap) -- independent corroboration
of the extracted text's authenticity, from a source this task itself
designated as a lead.

AMENDMENT: Ministerial Decision No. 3293/1/1444 (5/6/1444H) is CONFIRMED to
exist and to have been approved -- its own decision text (preamble, 3
operative clauses, Minister's signature) was read directly from a Wayback
Machine capture of uqn.gov.sa/?p=21989 (snapshot 20230507072534), which
explicitly names and dates the ORIGINAL decision being amended (1006/1/1442,
9/5/1442H) -- a second independent primary-source citation of that founding
decision. However, the amendment's OWN attached text ("بالصيغة المرافقة لهذا
القرار") is not embedded on that page, and could not be obtained through any
other channel tried this pass (istitlaa.ncc.gov.sa PDF: persistent TLS
connection resets across curl + WebFetch + Docs-viewer proxy attempts, no
Wayback snapshot available; eparticipation.my.gov.sa: HTTP 403; a FAOLEX PDF
lead turned out to be the parent LAW, not this Regulation; nezams.com does
not host this Regulation's text; qanoonsa.com: no dedicated page found). A
WebSearch synthesis surfaced 4 qualitative, non-verbatim, non-article-
attributed themes for the amendment's substance -- NOT used to tag any
article معدلة, since doing so without a directly-verified, citable,
article-level source would be a fabricated/guessed attribution.

TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED -- exactly one official/primary
source (uqn.gov.sa, via Wayback archive of its own live page) reached and
used as this track's governing text for the 166-article body, cross-verified
against independent secondary/press corroboration (argaam.com, substantively,
not merely citation-level); no SECOND independent official source confirmed
the full 166-article body verbatim this pass (istitlaa.ncc.gov.sa's PDF, the
one candidate second primary source, was unreachable throughout this pass).

CONSOLIDATED_AMENDED_LAW = False (the MIRROR IMAGE of the sibling
real_estate_finance_implementing_regulation track): this track's stored text
is the FOUNDING/original 1442H text, not a post-amendment consolidated
re-issuance -- the 1444H amendment's own attached text could not be obtained
this pass (see above), so no article is tagged معدلة/مضافة without direct
textual evidence of what specifically changed. All 166 articles are recorded
اصلية, meaning "verified original text as issued by Decision 1006/1/1442",
NOT "certified unchanged as of today" -- an explicit, disclosed limitation,
not a fabricated or guessed amendment attribution.

166 articles, 7 أبواب (1-12 / 13-68 / 69-106 / 107-135 / 136-153 / 154-161 /
162-166); all 166 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة. Arabic governs; no
translation/paraphrase/interpretation performed on the Arabic text. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mining_investment_implementing_regulation", "law",
                   "official_source", "mining_investment_implementing_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "mining_investment_implementing_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "mining_investment_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "mining_investment_implementing_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "mining_investment_implementing_regulation_arabic_legal_llm",
                        "mining_investment_implementing_regulation_legal_llm_001_166.json")

LAW_ID = "sa-mining-investment-implementing-regulation-1006-1442"
LAW_AR = "اللائحة التنفيذية لنظام الاستثمار التعديني"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير المرخص الرخصة رخصة").split())
KEY_RE = r"mining_investment_implementing_regulation_art_(\d{3})$"


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    governing_source_note = (
        "Arabic governs. PRIMARY: uqn.gov.sa (Umm Al-Qura Official Gazette)'s own page for this "
        "regulation, reached via a Wayback Machine archive of the live page (snapshot 20251011171315; "
        "the live page itself returns only a generic SPA shell this pass). Parsed with BeautifulSoup "
        "walking every <p>/<table> in document order; the ONE in-body table (Article 86) merged "
        "row-by-row into that article's own text; the 6 numbered ملاحق after Article 166 are "
        "deliberately excluded from the article collection (disclosed scope boundary, not lost "
        "content). SUBSTANTIVE cross-check: argaam.com's own coverage paraphrases two provisions "
        "(mining-reserve-zone designation; Category-B export fee/cap) found verbatim in the "
        "extracted text. TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. This is a "
        "consolidated_amended_law=False track: Ministerial Decision 3293/1/1444 (5/6/1444H) is "
        "CONFIRMED to have amended this regulation 'in the form attached to that decision', but the "
        "attachment's own text could not be obtained this pass through any channel tried "
        "(istitlaa.ncc.gov.sa PDF unreachable -- persistent TLS resets; eparticipation.my.gov.sa "
        "HTTP 403; a FAOLEX PDF lead was the parent Law, not this Regulation; nezams.com/qanoonsa.com "
        "do not host it) -- see known_unresolved_discrepancies. No article is tagged معدلة without "
        "direct textual evidence of what changed -- an explicit, disclosed limitation."
    )
    source_authority_ar = (
        "قرار وزير الصناعة والثروة المعدنية رقم (1006/1/1442) وتاريخ 9/5/1442هـ، منشور كاملاً في "
        "الجريدة الرسمية (أم القرى) بتاريخ 17/5/1442هـ الموافق 1/1/2021م، ويُتبع بقرار وزير الصناعة "
        "والثروة المعدنية رقم (3293/1/1444) وتاريخ 5/6/1444هـ بالموافقة على تعديل اللائحة 'بالصيغة "
        "المرافقة' لذلك القرار -- نص المرفق المعدَّل ذاته لم يُتحصَّل عليه هذه الجولة رغم محاولات "
        "متعددة القنوات (istitlaa.ncc.gov.sa، eparticipation.my.gov.sa، FAOLEX، nezams.com، "
        "qanoonsa.com). النص جُلب مباشرة من uqn.gov.sa (عبر أرشيف Wayback Machine للصفحة الحية)، "
        "وقُوطع جوهرياً مع تغطية argaam.com الصحفية. TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. نسخة "
        "غير موحَّدة (consolidated_amended_law=false): النص المخزَّن هو نص الإصدار التأسيسي "
        "1006/1/1442 كما نُشر أصلاً، وليس نصاً يعكس تعديل 1444هـ."
    )

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        section = a.get("section_ar") or ""
        ver.append({"law_key": "mining_investment_implementing_regulation",
                    "law_component": "regulation", "language": "ar",
                    "record_layer": "MINING_INVESTMENT_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "source_tier": a.get("source_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": governing_source_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "mining-investment-implementing-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "mining_investment_implementing_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الاستثمار التعديني"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                                        "Ministerial Decision No. (1006/1/1442), 9/5/1442H, "
                                        "published Official Gazette 17/5/1442H (1/1/2021G), followed "
                                        "by Ministerial Decision No. (3293/1/1444), 5/6/1444H "
                                        "approving an amendment 'in the form attached' -- attachment "
                                        "text not obtained this pass. Primary: uqn.gov.sa (Wayback "
                                        "archive of live page). Secondary substantive cross-check: "
                                        "argaam.com. TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. "
                                        "consolidated_amended_law=false; stored text is the "
                                        "pre-1444-amendment original."),
                                     "source_authority_ar": source_authority_ar,
                                     "source_status": a["status"].lower(),
                                     "source_tier": a.get("source_tier"),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "mining_investment_implementing_regulation",
               "layer": "MINING_INVESTMENT_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "base_law_key": src.get("base_law_key"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "gazette_publication": src.get("gazette_publication"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-mining-investment-implementing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (166 مادة؛ 166 أصلية، "
                                     "0 معدلة، 0 مضافة، 0 ملغاة؛ 7 أبواب)",
               "title_en": ("Implementing Regulation of the Mining Investment Law — Arabic "
                            "LLM-ready layer (166 records: 166 original/founding-text, 0 amended, "
                            "0 added, 0 repealed; 7 أبواب)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 166], "text_status": "FOUNDING_TEXT_1442H_AMENDMENT_UNOBTAINED",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Mining Investment Implementing Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
