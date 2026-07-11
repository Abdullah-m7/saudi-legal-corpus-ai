#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the three Evidence Law companion tracks.

ضوابط إجراءات الإثبات إلكترونياً (24), الأدلة الإجرائية لنظام الإثبات (135),
القواعد الخاصة بتنظيم شؤون الخبرة أمام المحاكم (34) — all issued by Minister
of Justice decision (921) dated 16/03/1444H, all in force and unamended. Each
was fetched article-by-article from the official MOJ legal-portal database
and cross-verified against the official MOJ PDF from the same portal (zero
unexplained differences; see the source artifacts). Arabic governs; no
translation, paraphrase, or legal interpretation. Read-only over inputs;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())

TRACKS = [
    {"key": "dawabit", "dir": "electronic_rules",
     "law_id": "sa-evidence-electronic-procedures-rules",
     "doc_ar": "ضوابط إجراءات الإثبات إلكترونياً",
     "doc_en": "Controls of the Electronic Evidentiary Procedures",
     "component": "electronic_procedures_rules", "n": 24,
     "rid": "evidence-elec-llm-art", "query_doc": "ضوابط الإثبات الإلكتروني"},
    {"key": "adillah", "dir": "procedural_manuals",
     "law_id": "sa-evidence-procedural-manuals",
     "doc_ar": "الأدلة الإجرائية لنظام الإثبات",
     "doc_en": "Procedural Manuals for the Evidence Law",
     "component": "procedural_manuals", "n": 135,
     "rid": "evidence-manuals-llm-art", "query_doc": "الأدلة الإجرائية لنظام الإثبات"},
    {"key": "khibrah", "dir": "expertise_rules",
     "law_id": "sa-evidence-expertise-rules",
     "doc_ar": "القواعد الخاصة بتنظيم شؤون الخبرة أمام المحاكم",
     "doc_en": "Rules Regulating Expert Affairs Before the Courts",
     "component": "expertise_rules", "n": 34,
     "rid": "evidence-expertise-llm-art", "query_doc": "قواعد شؤون الخبرة أمام المحاكم"},
]


def _kw(text, k=6, fallback="الإثبات"):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [fallback]


def build(t):
    src_p = os.path.join(ROOT, "sources", "evidence", t["dir"], "official_source",
                         "evidence_%s_official_source.json" % t["dir"])
    out_ver = os.path.join(ROOT, "sources", "evidence", t["dir"], "verified")
    rec_p = os.path.join(out_ver, "evidence_%s_verified_records.jsonl" % t["dir"])
    sum_p = os.path.join(out_ver, "evidence_%s_verified_summary.json" % t["dir"])
    llm_p = os.path.join(ROOT, "data", "evidence_arabic_legal_llm",
                         "evidence_%s_legal_llm_001_%03d.json" % (t["dir"], t["n"]))

    src = json.load(open(src_p, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=lambda k: int(re.search(r"_art_(\d{3})$", k).group(1)))
    os.makedirs(out_ver, exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.search(r"_art_(\d{3})$", key).group(1))
        text = a["text"]
        ver.append({"law_key": "evidence", "law_component": t["component"],
                    "language": "ar",
                    "record_layer": "EVIDENCE_%s_ARABIC_VERIFIED_TEXT" % t["dir"].upper(),
                    "article_number": n, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": a.get("legal_status_ar"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ legal-portal database "
                                              "text cross-verified against the official MOJ PDF "
                                              "(see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": t["law_id"], "law_component": t["component"],
                    "article_number": n, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "record_id": "%s-%03d" % (t["rid"], n),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (t["doc_ar"], a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (t["doc_ar"], a["number_label_ar"]),
                    "article_path": "evidence/%s/articles/%03d" % (t["dir"], n),
                    "keywords_ar": _kw(text, fallback=t["query_doc"]),
                    "search_queries_ar": ["المادة %d %s" % (n, t["query_doc"]),
                                          "%s المادة %d" % (t["query_doc"], n),
                                          "المادة %d من %s" % (n, t["doc_ar"])],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": t["doc_ar"],
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(rec_p, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "evidence",
               "layer": "EVIDENCE_%s_ARABIC_VERIFIED_TEXT" % t["dir"].upper(),
               "record_count": len(ver), "official_text_status": STATUS,
               "issued_by_ar": src["issued_by_ar"],
               "source_artifact": os.path.relpath(src_p, ROOT)},
              open(sum_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-evidence-%s-arabic-legal-llm-full" % t["dir"].replace("_", "-"),
               "law_id": t["law_id"], "law_component": t["component"],
               "title_ar": t["doc_ar"] + " — الطبقة العربية الجاهزة للنماذج اللغوية (%d مادة)" % len(llm),
               "title_en": t["doc_en"] + " — Arabic LLM-ready layer (%d records)" % len(llm),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, t["n"]], "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(llm_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %s: %d verified + %d LLM-ready records" % (t["dir"], len(ver), len(llm)))


def main():
    for t in TRACKS:
        build(t)


if __name__ == "__main__":
    main()
