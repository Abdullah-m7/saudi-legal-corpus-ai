#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the track for the Implementing Regulation of the Cooperative
Societies Law (اللائحة التنفيذية لنظام الجمعيات التعاونية).

VERIFICATION TIER -- see sources/cooperative_societies_regulation/law/
official_source/cooperative_societies_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

Ministerial Decision No. 52068 of the Minister of Social Affairs, issued
under Article 42 of the Cooperative Societies Law (Royal Decree M/14,
10/3/1429H; Council of Ministers Resolution 73, 9/3/1429H). 55 articles
across nine parts. Full text fetched directly (HTTP 200) as a 32-page
image-scanned PDF from two independent official bodies -- the National
Center for the Development of the Non-Profit Sector (ncnp.gov.sa, the
current publisher of the base law's own text) and the Cooperative
Societies Council (cscs.org.sa, the body established by this very
regulation's own Article 54) -- a genuine cross-corroboration between two
independent primary sources, not a mirror of the same file. The PDF has no
extractable text layer at all (pure scan); every article was transcribed
by direct visual reading of 200dpi page renders, including zoomed crops to
resolve the handwritten ministerial-decision number/date on the cover.

55 records, ALL اصلية (55 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة) across 9 أبواب.
No amendment found this pass -- disclosed as absence-of-evidence, not proof
of none existing. The decree's exact day/month is obscured by a cover-page
ink stamp (year 1429H is legible) and is NOT fabricated here -- see
known_unresolved_discrepancies.

Read-only over input; deterministic over outputs. Arabic governs; no
translation/paraphrase/interpretation performed on the Arabic text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cooperative_societies_regulation", "law", "official_source",
                   "cooperative_societies_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cooperative_societies_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cooperative_societies_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cooperative_societies_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cooperative_societies_regulation_arabic_legal_llm",
                        "cooperative_societies_regulation_legal_llm_001_055.json")

LAW_ID = "sa-cooperative-societies-regulation-m14-1429"
LAW_AR = "اللائحة التنفيذية لنظام الجمعيات التعاونية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"cooperative_societies_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الجمعية الوزارة الوزير").split())


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
        ver.append({"law_key": "cooperative_societies_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "COOPERATIVE_SOCIETIES_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; full text fetched directly (HTTP 200) as "
                                              "a 32-page image-scanned PDF, cross-corroborated between "
                                              "two independent official bodies (ncnp.gov.sa and "
                                              "cscs.org.sa). No extractable text layer -- every article "
                                              "was transcribed by directly reading rendered page images "
                                              "(200dpi), not a lossy extraction pipeline. The decree's "
                                              "exact day/month is obscured by a cover-page ink stamp and "
                                              "is not fabricated -- see known_unresolved_discrepancies."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "cooperative-societies-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "cooperative_societies_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الجمعيات التعاونية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. 52068 under Cooperative "
                                                          "Societies Law Article 42 (Royal Decree M/14, "
                                                          "10/3/1429H) -- full text fetched directly (HTTP "
                                                          "200) as an image-scanned PDF, cross-corroborated "
                                                          "between ncnp.gov.sa and cscs.org.sa (two "
                                                          "independent official bodies); every article read "
                                                          "directly from rendered page images (no text "
                                                          "layer exists in the source)"),
                                     "source_authority_ar": "قرار وزاري رقم (52068) استناداً للمادة (42) من نظام الجمعيات التعاونية (المرسوم الملكي رقم م/14 وتاريخ 10/3/1429هـ) — النص الكامل جُلب مباشرة (HTTP 200) كملف PDF ممسوح ضوئياً، وتم التحقق التقاطعي بين جهتين رسميتين مستقلتين (ncnp.gov.sa وcscs.org.sa)؛ كل مادة قُرئت مباشرة من صور الصفحات المصورة (لا توجد طبقة نص في المصدر)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cooperative_societies_regulation",
               "layer": "COOPERATIVE_SOCIETIES_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-cooperative-societies-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (55 مادة؛ 55 أصلية)",
               "title_en": ("Implementing Regulation of the Cooperative Societies Law — Arabic "
                            "LLM-ready layer (55 records: 55 original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 55], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Cooperative Societies Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
