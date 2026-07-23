#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Environmental Inspection & Audit
track (اللائحة التنفيذية للتفتيش والتدقيق البيئي لنظام البيئة).

This is a COMPANION regulation to an already-ingested base law -- the same
pattern as scripts/gen_food_regulation_track.py (companion to food_law). The
base law here is نظام البيئة (Environmental Law, Royal Decree M/165,
19/11/1441H), already ingested as the environmental_law track. This regulation
is one of ~15 topical Implementing Regulations flagged under that base law in
this corpus's coverage_gap_map (candidate environmental_inspection_audit_reg).

CITATION / VERIFICATION TIER -- see
sources/environmental_inspection_audit/official_source/
environmental_inspection_audit_reg_official_source.json's
verification_methodology_note and known_unresolved_discrepancies for the full
account. Summary:

The Regulation was ORIGINALLY issued by Ministerial Decision No. (393691/1/1442)
dated 13/7/1442H. Its CURRENT in-force text was issued by Decision No.
(15116190) of the Minister of Environment, Water and Agriculture, dated 12
Jumada al-Ula 1446H (14 Nov 2024), published in Umm Al-Qura Gazette issue (5057)
on 22 Nov 2024. Clause (Second) of Decision 15116190 states expressly that it
REPLACES the original Regulation ("تحل هذه اللائحة محل ..."). This is therefore
a wholesale repeal-and-replace, NOT an in-place article amendment: the current
text is ingested as a single unit and all 8 articles are classified اصلية
relative to the current (replacement) instrument, with the supersession
documented in amendment_history and known_unresolved_discrepancies.

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology; it was
unreachable this pass (HTTP 503, matching the environmental_law track's own
experience) and has NO dedicated lawId page for this Regulation (only for the
base Environmental Law, lawId 63831ff6-63d9-4212-8b54-abf800e146bd). Wayback was
NOT attempted (blocked by this session's egress policy). Government primaries
(uqn.gov.sa gazette issue 5057, mewa.gov.sa, spa.gov.sa, the istitlaa/tafaul
consultation portal) were checked but their text content was unreachable this
pass (404/403/JS-challenge). PRIMARY reachable full-text source actually used:
qanoonsa.com (dedicated pages /p/505703 for the text and /p/505702 for the
issuing decision preamble; it reproduces Umm Al-Qura issue 5057 text expressly).
Citation is corroborated by the replacing decision's own recital (most
authoritative), qistas.com, the MEWA/SPA announcement, and this corpus's own
prior gap-map pass. Text cross-check: qistas.com corroborates Articles 2-3
near-verbatim (though it shows the pre-2024 ORIGINAL, whose Article 1
definitions differ -- directly confirming the 2024 amendment rewrote them);
Articles 4-8 + the two annexes were NOT independently cross-checked against a
second full text this pass -- disclosed.

STRUCTURE: 8 articles + Table (1) penalty schedule (referenced by Art 8) +
Appendix (1) environmental-audit-study template (referenced by Art 5) = 10
records. status_counts: 8 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (see the wholesale-
replacement note above). Arabic-Indic numerals (including load-bearing penalty
amounts) are preserved verbatim; tashkeel/decorative-tatweel stripped (Hijri
'هـ' marker kept); one source-rendering artifact ('الش عب'->'الشعب') corrected
and disclosed. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_inspection_audit",
                   "official_source",
                   "environmental_inspection_audit_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_inspection_audit", "verified")
RECORDS = os.path.join(OUT_VER,
                       "environmental_inspection_audit_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER,
                       "environmental_inspection_audit_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_inspection_audit_arabic_legal_llm",
                        "environmental_inspection_audit_reg_legal_llm_001_010.json")

LAW_ID = "sa-environmental-inspection-audit-reg-15116190"
LAW_AR = "اللائحة التنفيذية للتفتيش والتدقيق البيئي لنظام البيئة"
ART_RE = r"environmental_inspection_audit_reg_art_(\d{3})$"
JADWAL_KEY = "environmental_inspection_audit_reg_jadwal_001"
MULHAQ_KEY = "environmental_inspection_audit_reg_mulhaq_001"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها المركز اللوائح النظام البيئي البيئة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(ART_RE, key)
    if m:
        return (0, int(m.group(1)))
    if key == JADWAL_KEY:
        return (1, 0)
    if key == MULHAQ_KEY:
        return (1, 1)
    return (2, 0)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(ART_RE, key)
        art_no = int(m.group(1)) if m else idx
        rec_type = a.get("record_type", "article")
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        note = ("Arabic governs; PRIMARY reachable full-text source is qanoonsa.com "
                "(reproducing Umm Al-Qura Gazette issue 5057, the in-force 2024 "
                "replacement text). laws.boe.gov.sa was checked first per standard "
                "methodology but is unreachable this pass and has no dedicated lawId "
                "page for this Regulation. The current text was issued by Ministerial "
                "Decision (15116190), 12 Jumada al-Ula 1446H (14 Nov 2024), which "
                "wholly replaced the original Decision (393691/1/1442), 13/7/1442H. "
                "See verification_methodology_note and known_unresolved_discrepancies "
                "in the source artifact before relying on this track -- in particular "
                "the single-reachable-full-text-source limitation, the wholesale-"
                "replacement (not article-level) amendment relation, the penalty-table "
                "column-alignment ambiguity, and the preserved appendix-title typo "
                "(التحقيق vs التدقيق).")
        ver.append({"law_key": "environmental_inspection_audit",
                    "law_component": "regulation", "language": "ar",
                    "record_layer": "ENVIRONMENTAL_INSPECTION_AUDIT_REG_ARABIC_VERIFIED_TEXT",
                    "record_type": rec_type,
                    "article_number": art_no, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": a.get("text_complete", True),
                    "amendment_history": a.get("history"),
                    "official_text_status": "UNCHANGED",
                    "governing_source_note": note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation",
                    "record_type_structural": rec_type,
                    "article_number": art_no,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "inline_title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": a.get("text_complete", True),
                    "record_id": "environmental-inspection-audit-reg-llm-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "environmental_inspection_audit/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية للتفتيش والتدقيق البيئي" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. "
                                        "(15116190), 12 Jumada al-Ula 1446H (14 Nov 2024), "
                                        "Umm Al-Qura Gazette issue 5057 -- fully replacing "
                                        "the original Decision (393691/1/1442), 13/7/1442H; "
                                        "issued under Article 48 of the Environmental Law "
                                        "(Royal Decree M/165). PRIMARY reachable full-text "
                                        "source: qanoonsa.com; cross-verified citation "
                                        "against the replacing decision's own recital, "
                                        "qistas.com, and the MEWA/SPA announcement; "
                                        "laws.boe.gov.sa unreachable this pass with no "
                                        "dedicated lawId page for this Regulation"),
                                     "source_authority_ar": ("قرار وزير البيئة والمياه "
                                        "والزراعة رقم (15116190) وتاريخ 12 جمادى الأولى "
                                        "1446هـ (14 نوفمبر 2024م)، جريدة أم القرى العدد "
                                        "(5057)، الحال محل القرار الأصلي (393691/1/1442) "
                                        "وتاريخ 13/7/1442هـ؛ صادرة استنادا إلى المادة (48) "
                                        "من نظام البيئة (م/165). المصدر النصي الأساسي "
                                        "القابل للوصول: qanoonsa.com؛ الاستشهاد مطابق "
                                        "لديباجة قرار الإحلال نفسه وqistas.com وإعلان "
                                        "الوزارة/واس؛ بوابة هيئة الخبراء غير قابلة للوصول "
                                        "هذه الجولة ولا تملك صفحة مخصصة لهذه اللائحة"),
                                     "source_status": "UNCHANGED",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "environmental_inspection_audit",
               "layer": "ENVIRONMENTAL_INSPECTION_AUDIT_REG_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "article_count": src["article_count"],
               "annex_count": src["annex_count"],
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "current_text_decree": src["current_text_decree"],
               "current_text_decree_date_hijri": src["current_text_decree_date_hijri"],
               "current_text_gazette": src["current_text_gazette"],
               "legal_status_ar": src["legal_status_ar"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "base_law": src["base_law"],
               "preamble_ar": src["preamble_ar"],
               "supersession_finding_ar": src["supersession_finding_ar"],
               "amendment_history": src.get("amendment_history", []),
               "annex_structure": src["annex_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-environmental-inspection-audit-reg-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                           "(10 سجلات: 8 مواد + الجدول رقم 1 + الملحق رقم 1؛ جميعها اصلية)",
               "title_en": ("Implementing Regulation for Environmental Inspection and Audit "
                            "— Arabic LLM-ready layer (10 records: 8 articles + Table 1 + "
                            "Appendix 1; all original to the in-force 2024 replacement text)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 8], "annex_count": src["annex_count"],
               "text_status": "UNCHANGED",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Environmental Inspection & Audit records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
