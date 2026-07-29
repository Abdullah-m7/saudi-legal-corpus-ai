#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Excise Tax Law track (نظام الضريبة الانتقائية, Royal Decree
M/86, 27/8/1438H, as amended by Royal Decree M/113 (2/11/1438H) and Royal
Decree M/52 (28/4/1441H)).

An ENTIRE TAX was absent from this corpus before this track: the corpus already
held vat_law, vat_regulation, income_tax_law, income_tax_regulation, zakat_law,
rett_law, rett_regulation, customs_law, customs_regulation and
einvoicing_regulation, but no excise-tax instrument at all.

VERIFICATION TIER -- TIER_2 (one official source + an independent secondary
cross-check). See excise_tax_law_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: ZATCA's (Zakat, Tax and Customs Authority) own official
consolidated Arabic PDF of the Excise Tax Law, downloaded directly from
zatca.gov.sa this pass (HTTP 200, 10 pages, born-digital). The file prints the
complete enactment/amendment chain on its own cover page (M/86 27/8/1438H,
amended by M/113 2/11/1438H and by M/52 28/4/1441H) and carries two numbered
footnotes attributing those amendments to Articles 25 and 27 respectively.

SECONDARY CROSS-CHECK: nezams.com's independent rendering of the Law (which
publishes the ORIGINAL 1438H text plus amendment notes). All 30 articles were
compared letter-by-letter after stripping tatweel, tashkeel, punctuation and
whitespace: 20 articles matched EXACTLY; the 10 differences are each explained
and recorded in known_unresolved_discrepancies (authority rename, ya/alef-
maqsura orthography, genuine amendments to Articles 25 and 27, and secondary-
source typos). ZATCA's text governs at every divergence; the secondary source
was never used to correct a single Arabic character.

NOT AVAILABLE this pass: laws.boe.gov.sa (server-side TLS rejection),
web.archive.org and r.jina.ai (both blocked), and no extractable Umm al-Qura
gazette text. Hence TIER_2, not TIER_1. ZATCA's English version was never
consulted: Arabic governs.

REAL ARTICLE COUNT: 30 (المادة الأولى .. المادة الثلاثون), 10 chapters
(فصول) -- this matches the corpus census figure. 28 اصلية / 2 معدلة.
No pre-amendment original text is included for Articles 25 or 27: it was not
established from an official source this pass, and this corpus does not
fabricate. Both gaps are documented, not guessed.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "excise_tax_law", "law", "official_source",
                   "excise_tax_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "excise_tax_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "excise_tax_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "excise_tax_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "excise_tax_law_arabic_legal_llm",
                        "excise_tax_law_legal_llm_001_030.json")

LAW_ID = "sa-excise-tax-law-m86-1438"
LAW_AR = "نظام الضريبة الانتقائية"
STATUS = "ZATCA_OFFICIAL_CONSOLIDATED_PDF_X_SECONDARY_CROSS_VERIFIED"
KEY_RE = r"excise_tax_law_art_(\d{3})$"
AMENDED_KEYS = {"excise_tax_law_art_025", "excise_tax_law_art_027"}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها إليه "
            "عليها الهيئة الضريبة الضريبية للضريبة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text.replace("ـ", "")).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


GOV_NOTE = ("Arabic governs. PRIMARY source: ZATCA's own official consolidated "
            "Arabic PDF of the Excise Tax Law (zatca.gov.sa, HTTP 200, "
            "born-digital), whose cover prints the full M/86 -> M/113 -> M/52 "
            "chain and whose numbered footnotes attribute the two amendments to "
            "Articles 25 and 27. CROSS-CHECK: nezams.com (independent secondary), "
            "compared letter-by-letter for all 30 articles -- 20 exact matches, "
            "all 10 divergences documented in known_unresolved_discrepancies with "
            "ZATCA's wording governing. laws.boe.gov.sa, the Wayback Machine and "
            "r.jina.ai were all unreachable/blocked this pass, so this track is "
            "TIER_2 (one official + secondary), not TIER_1. Pre-amendment original "
            "text is NOT included for Articles 25 or 27 -- a documented gap, not a "
            "fabrication. The English ZATCA version was never used.")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        text = a["text"]
        ver.append({"law_key": "excise_tax_law", "law_component": "law", "language": "ar",
                    "record_layer": "EXCISE_TAX_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "verification_tier": src["verification_tier"],
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "excise-tax-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "excise_tax_law/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من نظام الضريبة الانتقائية" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree M/86 (27/8/1438H), as "
                                                          "amended by M/113 (2/11/1438H) and "
                                                          "M/52 (28/4/1441H) — ZATCA official "
                                                          "consolidated PDF, cross-verified "
                                                          "against an independent secondary "
                                                          "source (TIER_2)"),
                                     "source_authority_ar": ("المرسوم الملكي رقم (م/86) وتاريخ "
                                                             "27/8/1438هـ، المعدَّل بالمرسوم "
                                                             "(م/113) 2/11/1438هـ وبالمرسوم "
                                                             "(م/52) 28/4/1441هـ — النسخة "
                                                             "الرسمية الموحّدة لهيئة الزكاة "
                                                             "والضريبة والجمارك، مع تحقّق "
                                                             "متقاطع من مصدر ثانوي مستقل"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "verification_tier": src["verification_tier"],
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "excise_tax_law",
               "layer": "EXCISE_TAX_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "verification_tier": src["verification_tier"],
               "verification_tier_basis": src["verification_tier_basis"],
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "cover_page_verbatim_ar": src["cover_page_verbatim_ar"],
               "amendment_history": src["amendment_history"],
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-excise-tax-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": (LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                            "(30 مادة؛ نص موحّد: 28 أصلية، 2 معدّلة)"),
               "title_en": ("Saudi Excise Tax Law — Arabic LLM-ready layer "
                            "(30 records, consolidated)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS,
               "verification_tier": src["verification_tier"],
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Excise Tax Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
