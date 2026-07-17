#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Civil Aviation Law track (نظام الطيران المدني, Royal Decree
M/44, 18/7/1426H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa's live portal was unreachable
this research pass (HTTP 503 via WebFetch on both discovered law-detail
URLs, connection-reset via direct curl, and HTTP 401 "bad IP reputation"
via the r.jina.ai proxy). Wayback Machine was not attempted this pass. Full
text instead rests on a direct fetch of nezams.com (a secondary Arabic
legal-reference site, fetched successfully via curl, 2.1MB HTML parsed
against its structured `<li class="subject" id="subject-N">` per-article
markup for all 180 articles), spot-checked — not fully cross-verified
article-by-article — against a second independent source
(rakadvocate.blogspot.com), which matched verbatim for Article 1 and
Article 180 (the only two spot-checked).

See sources/civil_aviation/law/official_source/
civil_aviation_law_official_source.json for the full methodology note and
all documented unresolved discrepancies, including: an apparent stray/
mislabeled "الفصل الثاني: صلاحيات وواجبات السلطات" sub-chapter heading
found in the raw source immediately before Article 149 (content-wise a
continuation of the preceding sub-chapter, not a new one — transcribed
verbatim as encountered, not silently relabeled); Council of Ministers
Resolution 158/1445H (the "المكتب"→"المركز" institutional rename across
Articles 108/109/112/114-116/118/119, and the full re-issuance of Article
107) confirmed via only one primary source; and the multi-instrument
Civil Aviation Regulations (CARs) issued under Article 179 with no single
consolidating "اللائحة التنفيذية" date.

180 records, all article-numbered (no مكرر articles found): 168 اصلية /
12 معدلة (Articles 1 §6, 32 §1, 46, 107, 108, 109, 112, 114, 115, 116,
118, 119) / 0 ملغاة / 0 مضافة. 14 أبواب, several with sub-فصول. For
amended articles, `text` holds the CURRENT (post-amendment, in-force)
integrated wording; each carries a full `history` entry, and where the
source actually captured verbatim pre-amendment wording (not merely noted
that an amendment "occurred"), an `original_1426h_text` field is also
present — never fabricated or reconstructed where the original text was
not actually captured.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_aviation", "law", "official_source",
                   "civil_aviation_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "civil_aviation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "civil_aviation_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "civil_aviation_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "civil_aviation_arabic_legal_llm",
                        "civil_aviation_law_legal_llm_001_180.json")

LAW_ID = "sa-civil-aviation-law-m44-1426"
LAW_AR = "نظام الطيران المدني"
STATUS = "NEZAMS_PRIMARY_X_RAKADVOCATE_SPOT_CHECKED"
KEY_RE = r"civil_aviation_art_(\d{3})(_mukarrar)?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


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
    mk = 1 if m.group(2) else 0
    return (n, mk)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(m.group(2))
        ls = a.get("legal_status_ar")
        text = a["text"]
        suffix = key.replace("civil_aviation_art_", "")
        ver.append({"law_key": "civil_aviation", "law_component": "law", "language": "ar",
                    "record_layer": "CIVIL_AVIATION_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — nezams.com fetched directly "
                                              "as the primary full-text source, spot-checked "
                                              "(Articles 1 and 180 only, not the full 180) "
                                              "against rakadvocate.blogspot.com, because "
                                              "laws.boe.gov.sa's live portal was unreachable "
                                              "this research pass (503/connection-reset/401 "
                                              "across every access method tried, Wayback Machine "
                                              "not attempted) — see verification_methodology_note "
                                              "in the source artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "civil-aviation-law-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "civil_aviation/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الطيران المدني" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("nezams.com (secondary Arabic legal "
                                                          "reference site, fetched directly), "
                                                          "spot-checked against "
                                                          "rakadvocate.blogspot.com — BOE portal "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "nezams.com (موقع مرجعي قانوني ثانوي، جلب مباشر) مع مطابقة نقطية مقابل rakadvocate.blogspot.com — تعذر الوصول لبوابة هيئة الخبراء BOE",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "civil_aviation",
               "layer": "CIVIL_AVIATION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-civil-aviation-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (180 سجلاً؛ نص موحّد: 168 أصلية، 12 معدلة)",
               "title_en": "Saudi Civil Aviation Law — Arabic LLM-ready layer (180 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 180], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Civil Aviation Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
