#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Finance Lease Law track
(اللائحة التنفيذية لنظام الإيجار التمويلي, Administrative Decision No.
1/م ش ت, dated 14/4/1434H = 24/2/2013G, issued by the Governor of SAMA
pursuant to Article 27 of the base Finance Lease Law, Royal Decree M/48,
13/8/1433H).

This is the companion-regulation track for this corpus's own finance_lease
base-Law track (see sources/finance_lease/law/official_source/
finance_lease_law_official_source.json, which documents that this companion
Implementing Regulation exists, has itself been separately amended, and was
deliberately NOT ingested in that base-Law pass). This track ingests that
companion Implementing Regulation.

VERIFICATION TIER -- see finance_lease_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: rulebook.sama.gov.sa (SAMA's own official Rulebook portal,
the issuing/administering authority's own site), Arabic full-text
'entiresection' view (https://rulebook.sama.gov.sa/ar/entiresection/123,
HTTP 200, live, born-digital structured HTML -- no OCR needed), which
renders all 32 articles across 3 أبواب (Parts) on a single page. Arabic
governs; the equivalent English entiresection view was fetched and used
ONLY for structural cross-verification (article count, Part boundaries,
and confirming the location/scope of the amendment footnotes), never as a
source of Arabic wording.

32 articles, 3 Parts (الباب الأول: 1-2 | الباب الثاني: 3-11 | الباب الثالث:
12-32) -- matching this track's commissioning brief exactly. THREE articles
carry a confirmed amendment by the SAME Governor's Decision No. 93/م ش ت,
dated 18/10/1441H: Article 10 paragraph (3), Article 17 in full, and
Article 25 paragraph (2). IMPORTANT: this track's commissioning brief named
only Article 10(3) and Article 17; independent re-verification this pass
(via SAMA Rulebook's own dedicated amendment-decision page, node 3243,
cross-corroborated by both the Arabic and English entiresection views)
found the SAME decision also amended Article 25(2) -- see
known_unresolved_discrepancies in the source artifact for the full
correction and chronology. The pre-amendment wording of all three
provisions was NOT recoverable this pass (the decision page states only
the new text; no usable Wayback snapshot predating the 2020G/1441H
amendment was found for this URL) -- this is disclosed, not guessed at.

No legal text is altered. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_lease_regulation", "law", "official_source",
                   "finance_lease_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "finance_lease_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "finance_lease_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "finance_lease_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "finance_lease_regulation_arabic_legal_llm",
                        "finance_lease_regulation_legal_llm_001_032.json")

LAW_ID = "sa-finance-lease-regulation-1-m-sh-t-1434"
LAW_AR = "اللائحة التنفيذية لنظام الإيجار التمويلي"
STATUS = "SAMA_RULEBOOK_PRIMARY_AR_EN_BILINGUAL_X_AMENDMENT_DECISION_NODE_CROSS_VERIFIED"
KEY_RE = r"finance_lease_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم المؤجر المستأجر العقد").split())


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

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        text = a["text"]
        section = a.get("section_ar", "")
        label = a["number_label_ar"] + ((" — " + section) if section else "")
        ver.append({"law_key": "finance_lease_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "FINANCE_LEASE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is "
                                              "rulebook.sama.gov.sa (SAMA's own official "
                                              "Rulebook portal, the issuing/administering "
                                              "authority's own site), Arabic 'entiresection' "
                                              "full-text view, HTTP 200, born-digital "
                                              "structured HTML (no OCR). Cross-checked "
                                              "structurally (article count, Part boundaries, "
                                              "amendment-footnote scope) against the "
                                              "equivalent English entiresection view -- "
                                              "English was NEVER used as a source of Arabic "
                                              "wording. See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text -- "
                                              "in particular the correction of this track's "
                                              "own commissioning brief, which named only "
                                              "Article 10(3) and Article 17 as amended by "
                                              "Governor's Decision No. 93/م ش ت "
                                              "(18/10/1441H); independent re-verification "
                                              "this pass found the SAME decision also amended "
                                              "Article 25(2), and that the pre-amendment "
                                              "wording of all three provisions could not be "
                                              "recovered from any source consulted this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "finance-lease-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "finance_lease_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنفيذية لنظام الإيجار التمويلي" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Administrative Decision No. 1/م ش ت "
                                                          "(14/4/1434H = 24/2/2013G), issued by "
                                                          "the Governor of SAMA pursuant to "
                                                          "Article 27 of the Finance Lease Law "
                                                          "(Royal Decree M/48, 13/8/1433H) -- "
                                                          "rulebook.sama.gov.sa (issuing "
                                                          "Authority's own site); Articles "
                                                          "10(3), 17 and 25(2) further amended "
                                                          "by Governor's Decision No. 93/م ش ت "
                                                          "(18/10/1441H)"),
                                     "source_authority_ar": ("قرار إداري رقم 1/م ش ت وتاريخ "
                                                            "14/4/1434هـ (الموافق 24/2/2013م)، "
                                                            "صادر عن محافظ مؤسسة النقد العربي "
                                                            "السعودي (البنك المركزي السعودي "
                                                            "حالياً) استناداً إلى المادة "
                                                            "السابعة والعشرين من نظام الإيجار "
                                                            "التمويلي (المرسوم الملكي م/48 "
                                                            "وتاريخ 13/8/1433هـ) — الموقع "
                                                            "الرسمي لبوابة SAMA Rulebook "
                                                            "(rulebook.sama.gov.sa)؛ عُدلت "
                                                            "المواد (العاشرة/الفقرة 3، "
                                                            "والسابعة عشرة، والخامسة "
                                                            "والعشرون/الفقرة 2) بموجب قرار "
                                                            "معالي المحافظ رقم 93/م ش ت وتاريخ "
                                                            "18/10/1441هـ"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "finance_lease_regulation",
               "layer": "FINANCE_LEASE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "parent_law": src.get("parent_law"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-finance-lease-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (32 مادة؛ 29 أصلية، 3 معدلة)",
               "title_en": ("Implementing Regulation of the Finance Lease Law — Arabic "
                            "LLM-ready layer (32 records; 29 original, 3 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 32], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Finance Lease Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
