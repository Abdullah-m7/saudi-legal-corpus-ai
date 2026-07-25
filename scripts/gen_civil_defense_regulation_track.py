#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Civil Defense Law's subordinate IMPLEMENTING REGULATIONS
track (لوائح نظام الدفاع المدني الفرعية). Base law: نظام الدفاع المدني, Royal
Decree M/10, 10/5/1406H, tracked separately at sources/civil_defense/.

STRUCTURE DECISION (single combined track, two labeled components) and the
full account of what was independently verified this pass -- sources fetched,
Wayback-vs-live reachability, the third candidate instrument found but NOT
included, and the broader out-of-scope universe of sector safety codes -- are
recorded in structure_decision_note and verification_methodology_note inside
sources/civil_defense_regulation/law/official_source/
civil_defense_regulation_official_source.json. Summary:

COMPONENT 1 -- rights_duties: لائحة حقوق وواجبات من يستعان بهم في أعمال الدفاع
المدني وعلاقتهم بجهاتهم. CoM Resolution (10), 6/1/1442H (25/8/2020G). 12 flat
articles (1-12). Fetched from the Bureau of Experts portal (laws.boe.gov.sa,
lawId 90f66860-d28b-40ed-b49d-ac3700baf50e) via FIVE independent Wayback
Machine snapshots spanning 2020-10-22 to 2025-06-22 -- the live portal itself
resets the connection for direct curl/WebFetch in this environment (consistent
with this corpus's prior findings for this same domain). All 5 snapshots show
byte-identical article text and zero articles flagged "modified"/"repealed" ->
this component has NEVER been amended since enactment.

COMPONENT 2 -- firefighting_rescue: لائحة تنظيم أعمال الإطفاء والإنقاذ
بالمديرية العامة للدفاع المدني. Approved by Resolution No. (1) of the Mandated
Civil Defense Committee (لجنة الدفاع المدني المكلفة), 6/3/1443H, signed by the
Minister of Interior. An unnumbered intro (مقدمة) plus 9 flat articles (1-9).
Fetched from the Umm al-Qura Gazette (uqn.gov.sa, ?p=8545 full text / ?p=8543
approving resolution) via 2022 Wayback Machine snapshots -- the live uqn.gov.sa
site was redesigned into a client-rendered SPA where these old numeric routes
no longer resolve to their original content (HTTP 200 but homepage shell only).

NOT INCLUDED (disclosed, not fabricated): a THIRD candidate instrument, لائحة
النظر في مخالفات نظام ولوائح الدفاع المدني (Ministerial Decision 12/1/و/5/دف,
18/4/1428H) -- confirmed to EXIST via multiple independent secondary sources
and directly cross-referenced by Article 7 of component 2, but its only
locatable primary copy is a 20-page SCANNED (no text layer) 2012 PDF; a quick
tesseract OCR test on its cover page produced garbled, unreliable output, so no
verbatim text is stored for it here. A CDX listing of 998.gov.sa's
CivilDefenseLists/Documents/ folder also surfaced ~30 additional sector-
specific "لائحة شروط السلامة ..." circulars -- out of scope for this pass; see
known_unresolved_discrepancies for the full disclosure.

21 verified records total: 12 (rights_duties) + 9 (firefighting_rescue),
all اصلية (original, unamended), 0 معدلة, 0 ملغاة, 0 مضافة. BOTH regulations are
flat (no chapters/فصول); section_ar is empty for every article by design.

TASHKEEL and justification-tatweel stripped uniformly (this corpus's majority
convention); curly quotes straightened; double spaces and space-before-
punctuation removed -- display-layer only, no legal text altered. Trailing/
standalone tatweel forming a genuine "هـ" (hijri-date abbreviation) or "جـ"
bullet-letter is preserved. Arabic governs; no translation/paraphrase/
interpretation performed. Read-only over input; deterministic over output.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_defense_regulation", "law", "official_source",
                   "civil_defense_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "civil_defense_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "civil_defense_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "civil_defense_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "civil_defense_regulation_arabic_legal_llm",
                        "civil_defense_regulation_legal_llm_001_021.json")

LAW_ID = "sa-civil-defense-regulation-combined-track"
KEY_RE = r"civil_defense_regulation_(rights_duties|firefighting_rescue)_art_(\d{3})$"

COMPONENT_ORDER = ["rights_duties", "firefighting_rescue"]

COMPONENT_NAME_AR = {
    "rights_duties": "لائحة حقوق وواجبات من يستعان بهم في أعمال الدفاع المدني وعلاقتهم بجهاتهم",
    "firefighting_rescue": "لائحة تنظيم أعمال الإطفاء والإنقاذ بالمديرية العامة للدفاع المدني",
}
COMPONENT_DECREE = {
    "rights_duties": "قرار مجلس الوزراء رقم (10) وتاريخ 6/1/1442هـ",
    "firefighting_rescue": "قرار لجنة الدفاع المدني المكلفة رقم (1) وتاريخ 6/3/1443هـ",
}

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم مجلس الدفاع المدني وزير الداخلية").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or ["الدفاع المدني"]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    component, n = m.group(1), int(m.group(2))
    return (COMPONENT_ORDER.index(component), n)


GOV_NOTE = ("Arabic governs; English is reference-only. This track stores BOTH subordinate "
            "implementing regulations of the Civil Defense Law (Royal Decree M/10, "
            "10/5/1406H; tracked separately at sources/civil_defense/) whose full verbatim "
            "text could be independently confirmed this pass, each via Wayback Machine "
            "snapshots of its own live government portal (laws.boe.gov.sa for "
            "rights_duties, uqn.gov.sa for firefighting_rescue) after the live portals "
            "themselves proved unreachable/redesigned in this environment -> TIER_2 for "
            "both components. A third candidate instrument (لائحة النظر في مخالفات نظام "
            "ولوائح الدفاع المدني) and a broader universe of ~30 sector-specific safety "
            "circulars were confirmed to EXIST but are deliberately NOT included -- see "
            "known_unresolved_discrepancies in the source artifact for the full, honest "
            "account before relying on this track's scope or provenance.")

SRC_AUTH = ("rights_duties: CoM Resolution (10), 6/1/1442H, via Bureau of Experts portal "
            "(laws.boe.gov.sa) Wayback snapshots 2020-2025 (byte-identical, unamended). "
            "firefighting_rescue: Mandated Civil Defense Committee Resolution (1), "
            "6/3/1443H, via Umm al-Qura Gazette (uqn.gov.sa) Wayback snapshots (2022). "
            "Both TIER_2 (archived official-portal capture; live portals unreachable/"
            "redesigned this pass).")

SRC_AUTH_AR = ("لائحة حقوق وواجبات: قرار مجلس الوزراء رقم (10) وتاريخ 6/1/1442هـ، عبر نسخ "
               "أرشيفية (Wayback) من بوابة هيئة الخبراء (laws.boe.gov.sa) بين 2020 و2025 "
               "(مطابقة حرفيا، غير معدلة). لائحة تنظيم أعمال الإطفاء والإنقاذ: قرار لجنة "
               "الدفاع المدني المكلفة رقم (1) وتاريخ 6/3/1443هـ، عبر نسخ أرشيفية من جريدة "
               "أم القرى (uqn.gov.sa) لعام 2022. كلاهما TIER_2 (نسخة أرشيفية لبوابة رسمية؛ "
               "تعذر الوصول الحي/أعيد تصميم الموقع الحي هذه الجولة).")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        component = a["component"]
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({"law_key": "civil_defense_regulation", "law_component": "regulation",
                    "component": component,
                    "language": "ar",
                    "record_layer": "CIVIL_DEFENSE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": "UNCHANGED",
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        component_ar = COMPONENT_NAME_AR[component]
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "component": component,
                    "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_added": ls == "مضافة", "is_amended": ls == "معدلة",
                    "record_id": "civil-defense-regulation-llm-%s-art-%03d" % (
                        component.replace("_", "-"), n),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (component_ar, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (component_ar, a["number_label_ar"]),
                    "article_path": "civil_defense_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], component_ar),
                                          "%s %s" % (component_ar, a["number_label_ar"]),
                                          "%s من %s" % (a["number_label_ar"], component_ar)],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": component_ar,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    combined_status_counts = {"اصلية": 0, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
    for c in src["components"]:
        for k, v in c["status_counts"].items():
            combined_status_counts[k] += v

    json.dump({"law_key": "civil_defense_regulation",
               "layer": "CIVIL_DEFENSE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": combined_status_counts,
               "components": [{"component_key": c["component_key"],
                                "document_ar": c["document_ar"],
                                "decree": c["decree"],
                                "decree_date_hijri": c["decree_date_hijri"],
                                "article_count": c["article_count"],
                                "status_counts": c["status_counts"]}
                               for c in src["components"]],
               "structure_decision_note": src["structure_decision_note"],
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    json.dump({"layer_id": "sa-civil-defense-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": "لوائح نظام الدفاع المدني الفرعية — الطبقة العربية الجاهزة "
                           "للنماذج اللغوية (21 مادة عبر لائحتين؛ الكل أصلية غير معدلة)",
               "title_en": ("Civil Defense Law Subordinate Regulations — Arabic LLM-ready "
                            "layer (21 records across 2 instruments, all original/unamended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "components": [{"component_key": c["component_key"],
                                "article_count": c["article_count"]}
                               for c in src["components"]],
               "text_status": "UNCHANGED",
               "status_counts": combined_status_counts,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Civil Defense Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
