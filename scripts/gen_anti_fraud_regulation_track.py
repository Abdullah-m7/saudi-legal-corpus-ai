#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Anti-Commercial Fraud Law
track (اللائحة التنفيذية لنظام مكافحة الغش التجاري). Companion instrument to
the base law tracked at sources/anti_fraud/ (Royal Decree M/19, 23/4/1429H).

ISSUING INSTRUMENT -- DISPUTED, NOT SILENTLY RESOLVED: nezams.com's metadata
table states "القرار الوزاري رقم 155 وتاريخ 6/1/1431هـ" (published
29/1/1431هـ), matching the prior research pass. mrksa.net's own page instead
shows an internally-coherent preamble reading "قرار وزاري رقم (55) وتاريخ
20/10/1431هـ". Neither is first-party-confirmed this pass (BOE, mc.gov.sa,
ncar.gov.sa, and Wayback content-fetch all confirmed unreachable; almoaqeb.com
unreachable; qanoniah.com is an unreadable client-rendered SPA). Both
candidate citations are recorded in
sources/anti_fraud_regulation/law/official_source/anti_fraud_regulation_official_source.json's
known_unresolved_discrepancies rather than silently picking one.

SOURCING TIER -- TIER 3, SECONDARY_SINGLE_SOURCE_VERBATIM_PARTIAL_CROSS_CHECK_
BOE_UNREACHABLE: nezams.com (fetched directly via curl, HTML, no AI-generation
fingerprints) is the GOVERNING VERBATIM SOURCE for all 19 articles. mrksa.net
(also fetched directly) was used ONLY for structural cross-check (19-article
count; Article 19's own number-label, which nezams.com's page left blank) --
NOT for verbatim text, because its article-body HTML carries a DeepSeek
AI-markdown-rendering fingerprint (<p class="ds-markdown-paragraph">, 133
occurrences, 0 on nezams.com) and two concrete substantive divergences were
found: Article 10 (mrksa.net's version omits nezams.com's 7-day trader-
notification procedure and foreign-lab-testing allowance) and Article 17
(mrksa.net states a 50% informant-reward cap vs. nezams.com's 25%, and 25% is
the figure consistent with this corpus's own already-verified base law
Article 11 that this regulation article implements). See the official_source
artifact's verification_methodology_note and known_unresolved_discrepancies
for the full caveat, including mc.gov.sa/ncar.gov.sa/almoaqeb.com/qanoniah.com
unreachability and the two corrected HTML-transcription artifacts (Article 1's
run-together definitions; Article 12's run-together clauses ب/ج).

19 articles, 11 heading groups (8 numbered فصول + 3 unnumbered topical
subheadings): أحكام عامة (1-4); ضبط المخالفات (5-9); فحص وتحليل المنتجات
والمدة اللازمة لذلك (10); إجراءات سحب المنتج المغشوش (11); المطالبة بالتعويض
وشروط إعادة القيمة (12); الحجز التحفظي على المنتج المشتبه به (13); إحالة
المخالفات والتحقيق ورفع الدعوى (14); التصرف في المنتج المغشوش (15-16); مكافأة
التبليغ عن المخالفات (17); التخفيضات التجارية (18); المسابقات التجارية (19).
All 19 اصلية (nezams.com's own metadata states "لم يجرى عليه تعديل" -- no
amendments recorded against this regulation by any source found this pass).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation, and no English or Chinese text is produced for this track.
Read-only over input; deterministic over outputs. Standalone construction --
does not modify any shared pipeline file.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_fraud_regulation", "law", "official_source",
                   "anti_fraud_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_fraud_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_fraud_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_fraud_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_fraud_regulation_arabic_legal_llm",
                        "anti_fraud_regulation_legal_llm_001_019.json")

LAW_ID = "sa-anti-fraud-regulation-mr155-1431"
LAW_AR = "اللائحة التنفيذية لنظام مكافحة الغش التجاري"
STATUS = "SECONDARY_SINGLE_SOURCE_VERBATIM_PARTIAL_CROSS_CHECK_BOE_UNREACHABLE"
KEY_RE = r"anti_fraud_reg_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك أنه إنه التي الذين اللذين هذه هؤلاء").split())


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
    return int(m.group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = _sort_key(key)
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "anti_fraud_regulation", "law_component": "regulation", "language": "ar",
                    "record_layer": "ANTI_FRAUD_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_1429h_text": a.get("original_1429h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track's governing current "
                                              "text rests on ONE verbatim-reliable secondary "
                                              "source (nezams.com), with mrksa.net providing "
                                              "structural (not textual) cross-check only, since "
                                              "laws.boe.gov.sa/mc.gov.sa/ncar.gov.sa are "
                                              "confirmed unreachable this pass and mrksa.net's "
                                              "article text shows AI-regeneration fingerprints "
                                              "with two confirmed substantive divergences -- see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including the "
                                              "disputed issuing-instrument citation (Resolution "
                                              "155/6-1-1431H vs 55/20-10-1431H)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "anti-fraud-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_fraud_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام مكافحة الغش التجاري" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Ministerial Resolution -- single "
                                                          "verbatim-reliable secondary source "
                                                          "(nezams.com), structural cross-check "
                                                          "only from mrksa.net; laws.boe.gov.sa, "
                                                          "mc.gov.sa, ncar.gov.sa confirmed "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "قرار وزاري — مصدر ثانوي واحد موثوق للنص الحرفي (نزامز)، مع تحقق بنيوي فقط من المسوق السعودي، وتعذر الوصول المؤكد لبوابة هيئة الخبراء ووزارة التجارة ومركز الوثائق والمحفوظات",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_fraud_regulation",
               "layer": "ANTI_FRAUD_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-fraud-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة؛ 19 أصلية)",
               "title_en": ("Implementing Regulation of the Saudi Anti-Commercial Fraud Law "
                           "(Ministerial Resolution) — Arabic LLM-ready layer (19 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Commercial Fraud Regulation records" %
          (len(ver), len(llm)))


if __name__ == "__main__":
    main()
