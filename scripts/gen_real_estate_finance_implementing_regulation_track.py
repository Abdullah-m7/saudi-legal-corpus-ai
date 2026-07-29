#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Real Estate Finance Law track
(اللائحة التنفيذية لنظام التمويل العقاري, Minister of Finance Decision No.
1229, dated 10/4/1434H = 20/2/2013G; published Official Gazette 7/7/1434H =
17/5/2013G; amended by Minister of Finance Decision No. 1144, dated
2/6/1443H). Implementing regulation of the real_estate_finance base-law track
already in this corpus (Royal Decree M/50, 13/8/1433H) -- NOT touched this
pass.

VERIFICATION TIER -- see sources/real_estate_finance_implementing_regulation/
law/official_source/real_estate_finance_implementing_regulation_official_
source.json's verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: rulebook.sama.gov.sa (SAMA's own official live "Rulebook"
portal), the Arabic page dedicated to this Regulation (node 190) -- fetched
directly via curl (HTTP 200, born-digital Drupal-10 HTML, no OCR needed). The
page lays out the regulation's cover metadata, all 4 أبواب, and all 31
مواد on one connected page as a sequence of <h2 class='page-title'> / <div
class='field--name-body'> pairs; table markup (used for several numbered/
lettered sub-items) was converted row-by-row into prose, never naive
tag-stripped.

SECONDARY SOURCE (independent GOVERNMENT domain, different administering
body): bfc.gov.sa (Financial Sector Development Program / برنامج تطوير
القطاع المالي, a Vision 2030 program under the Council of Economic and
Development Affairs -- NOT SAMA) hosts a born-digital PDF mirror of the same
official gazetted document (identical decision number/dates/gazette date/
amendment note on its own cover page). The original task-designated SAMA URL
(www.sama.gov.sa/.../Implementing_Regulation_of_the_Real_Estate_Finance_Law_
Ar.pdf) itself returned a connection-reset via curl and an internal SAMA
error page via WebFetch this pass; bfc.gov.sa's mirror was fetched via
WebFetch and read directly (9 pages, Sakkal Majalla font, real text layer --
cross-checked additionally via pdftotext). Full-document comparison (31/31
articles, 4/4 أبواب) found the core substantive content identical, with three
explicitly-disclosed non-substantive divergences (a terminology update
المؤسسة->البنك المركزي with its own documented provenance, and two isolated
transcription typos on the live Rulebook page) -- see
known_unresolved_discrepancies in the source artifact.

Additional corroboration on the amendment itself: argaam.com's own article
(fetched directly via curl) quotes SAMA's official statement verbatim that
Decision 1144 repealed the ORIGINAL Article Four (which had barred combining
real estate finance with other financing activities); a second, independent
WebFetch read of SAMA's own news page (news-755.aspx, unreachable via direct
curl) confirms the same account.

TIER: TIER_1_PRIMARY_MULTI_SOURCE -- two independently-hosted, independently
produced/maintained OFFICIAL government sources (SAMA's own live Rulebook +
a different government body's official PDF mirror of the same gazetted
document) agree word-for-word across the full 31-article/4-chapter document,
with no unresolved reachability gap (both reached successfully this pass).

CONSOLIDATED_AMENDED_LAW = True: the text is a post-1144-amendment
consolidated re-issuance. Decision 1144 repealed the regulation's ORIGINAL
Article Four (restricting combined financing activities), which produced an
automatic downward renumbering of subsequent articles; neither source used
this pass marks any per-article amendment/renumbering boundary, and no
reliable pre-2022 archived copy was found this pass for an article-level
diff. Following this corpus's own precedent for the sibling
finance_companies_regulation track (and healthcare_professions_regulation),
all 31 articles are recorded اصلية (= currently-governing text, not "unchanged
since 2013"); no article is tagged معدلة/مضافة without direct textual
evidence of what specifically changed -- an explicit, disclosed limitation,
not a fabricated or guessed amendment attribution.

31 articles, 4 أبواب (1-7 / 8-15 / 16-27 / 28-31); all 31 اصلية; 0 معدلة, 0
ملغاة, 0 مضافة. Arabic governs; no translation/paraphrase/interpretation
performed on the Arabic text. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_finance_implementing_regulation", "law",
                   "official_source", "real_estate_finance_implementing_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_finance_implementing_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_finance_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_finance_implementing_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_finance_implementing_regulation_arabic_legal_llm",
                        "real_estate_finance_implementing_regulation_legal_llm_001_031.json")

LAW_ID = "sa-real-estate-finance-implementing-regulation-1229-1434"
LAW_AR = "اللائحة التنفيذية لنظام التمويل العقاري"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"real_estate_finance_implementing_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم البنك المركزي العقاري التمويل الممول").split())


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
        "Arabic governs. PRIMARY: rulebook.sama.gov.sa (SAMA's own live official Rulebook "
        "portal, node 190) -- fetched directly via curl (HTTP 200, born-digital HTML). "
        "SECONDARY (independent government mirror, a different administering body -- "
        "Financial Sector Development Program / bfc.gov.sa): a born-digital PDF mirror of "
        "the same official gazetted document, fetched via WebFetch and cross-checked via "
        "pdftotext; full-document comparison found the substantive content identical across "
        "all 31 articles / 4 أبواب, net of one disclosed terminology update (المؤسسة -> "
        "البنك المركزي, per SAMA's own Article-1 footnote citing Royal Decree M/36, "
        "11/4/1442H) and two isolated live-page transcription typos (Article 6(ب), Article "
        "7 item 2 / Article 22 item 2 numbering) -- see known_unresolved_discrepancies in "
        "the source artifact. TIER_1_PRIMARY_MULTI_SOURCE. This is a "
        "consolidated_amended_law=True track: Decision 1144 (2/6/1443H) repealed the "
        "regulation's ORIGINAL Article Four (per SAMA's own official statement, quoted "
        "verbatim by argaam.com and independently confirmed via a direct WebFetch read of "
        "SAMA's own news page), producing an automatic renumbering of subsequent articles "
        "that neither source marks explicitly; no reliable pre-2022 archived text was found "
        "this pass for an article-level diff, so no individual article is tagged معدلة -- "
        "an explicit, disclosed limitation. See verification_methodology_note and "
        "known_unresolved_discrepancies before relying on this track's per-article "
        "amendment attribution."
    )
    source_authority_ar = (
        "قرار معالي وزير المالية رقم (1229) وتاريخ 10/4/1434هـ الموافق 20/2/2013م، منشور "
        "كاملاً في الجريدة الرسمية بتاريخ 7/7/1434هـ الموافق 17/5/2013م، بصيغته المعدَّلة "
        "بقرار معالي وزير المالية رقم (1144) وتاريخ 2/6/1443هـ (الذي ألغى المادة الرابعة "
        "الأصلية وأنتج إعادة ترقيم تلقائية للمواد اللاحقة، بحسب بيان رسمي للبنك المركزي "
        "السعودي منقول حرفياً في argaam.com ومؤكَّد عبر قراءة مباشرة لصفحة خبر ساما "
        "الرسمية). النص جُلب مباشرة من rulebook.sama.gov.sa (المصدر الأساسي)، وقُوطع مع "
        "نسخة PDF رسمية مطابقة مستضافة على bfc.gov.sa (مصدر حكومي ثانٍ مستقل). "
        "TIER_1_PRIMARY_MULTI_SOURCE. نسخة موحّدة بعد تعديل جوهري مؤكد "
        "(consolidated_amended_law=true)؛ لم يتوفر نص سابق لتعديل 1443هـ للمقارنة على "
        "مستوى المادة المفردة."
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
        ver.append({"law_key": "real_estate_finance_implementing_regulation",
                    "law_component": "regulation", "language": "ar",
                    "record_layer": "REAL_ESTATE_FINANCE_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": governing_source_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "real-estate-finance-implementing-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "real_estate_finance_implementing_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام التمويل العقاري"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                                        "Minister of Finance Decision No. (1229), 10/4/1434H "
                                        "(20/2/2013G), published Official Gazette 7/7/1434H "
                                        "(17/5/2013G), as amended by Decision No. (1144), "
                                        "2/6/1443H. Primary: rulebook.sama.gov.sa (live, "
                                        "direct curl fetch). Secondary: bfc.gov.sa official "
                                        "PDF mirror (WebFetch + pdftotext cross-check). "
                                        "TIER_1_PRIMARY_MULTI_SOURCE. consolidated_amended_"
                                        "law=true; no prior text available this pass for an "
                                        "article-level diff of the 1144 amendment."),
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
    json.dump({"law_key": "real_estate_finance_implementing_regulation",
               "layer": "REAL_ESTATE_FINANCE_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-real-estate-finance-implementing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (31 مادة؛ 31 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ 4 أبواب)",
               "title_en": ("Implementing Regulation of the Real Estate Finance Law — Arabic "
                            "LLM-ready layer (31 records: 31 original/currently-governing, 0 "
                            "amended, 0 added, 0 repealed; 4 أبواب)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 31], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Finance Implementing Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
