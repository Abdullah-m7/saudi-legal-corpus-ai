#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Recording Violations and Imposing
Penalties under the (General) Environmental Law track
(اللائحة التنفيذية لضبط المخالفات وإيقاع العقوبات لنظام البيئة).

This is a companion-regulation follow-up candidate flagged by this corpus's own
coverage-gap map (reports/coverage_gap_map/coverage_gap_map.json, gap entry
"Implementing Regulations of the General Environmental Law -- CORRECTED SCOPE",
sub_candidate environmental_violations_penalties_reg). It is a companion to the
already-ingested base Environmental Law track (corpus key `environmental`,
Royal Decree M/165, 19/11/1441H) -- the same "companion regulation to an
already-ingested base law" pattern as food_regulation is to food_law.

CITATION (independently verified this pass):
  Founding: Decision of the Minister of Environment, Water and Agriculture No.
  (312186/1/1442) (٣١٢١٨٦/١/١٤٤٢), dated 4/6/1442H, issued under Article 48
  (المادة الثامنة والأربعون) of the Environmental Law and Council of Ministers
  Decision No. (729), 16/11/1441H.
  Amendment / wholesale re-issuance: Ministerial Decision No. (15101619)
  (١٥١٠١٦١٩), dated 26/4/1446H (30 October 2024), published in Umm Al-Qura
  Gazette issue No. (5055) on 8 November 2024. Its clause (ثانيا) states the
  re-issued regulation "تحل محل" (replaces) the original 312186/1/1442 version.

VERIFICATION TIER -- see the official_source JSON's verification_methodology_note
for the full account. Summary: laws.boe.gov.sa was checked FIRST per this
corpus's standard methodology; there is NO dedicated lawId page for this
Implementing Regulation specifically (BOE catalogues the base Environmental Law
and the Waste Management Law as lawId records, but not this ministerial
executive regulation -- consistent with BOE's practice of not indexing
standalone ministerial implementing regulations). The PRIMARY full text used is
qanoonsa.com/p/505504 (the consolidated in-force text as re-issued by
15101619, server-rendered), with the appendix (محضر ضبط form) independently
corroborated on qistas.com, and the amending decision text (number 15101619,
date 26/4/1446H, the "تحل محل" clause and the original decision number)
corroborated on qanoonsa.com/p/505503. The citation itself is corroborated
across mewa.gov.sa, uqn.gov.sa (Umm Al-Qura), istitlaa.ncc.gov.sa and
qanoonsa.com.

STRUCTURE: 8 numbered articles (المادة الأولى .. المادة الثامنة) + 2 appendices
(الملحق (١) نموذج محضر ضبط مخالفة، الملحق (٢) نموذج محضر تحقيق). The 2 appendices
are official, integral form templates referenced by Article 3; they are ingested
as 2 distinct records flagged is_appendix=true so that nothing is dropped, but
they are NOT counted as numbered articles (article_count = 8, appendix_count = 2,
record_count = 10).

LEGAL STATUS: all 10 records are اصلية. The amending decision (15101619) re-issued
the regulation WHOLESALE ("تحل محل") and did NOT designate any specific article as
معدلة / مضافة / ملغاة; therefore article-level status is اصلية (each is an original
component of the currently-in-force re-issued instrument), while the track-level
status carries consolidated_amended_law=true with the full amendment_history and
the self-supersession of the 1442H version documented. This is NOT a claim that
the text is byte-identical to the 1442H original -- a precise per-article diff
against the original could not be performed (see
known_unresolved_discrepancies key
environmental_violations_penalties_reg_original_1442_text_not_diffable); positive
evidence shows at least Article 1's definitions changed (they now reference the
General Authority for the Preservation of Coral Reefs and Turtles in the Red Sea,
created by Council of Ministers Decision 406, 14/5/1445H -- post-dating the 1442H
original).

TEXT HANDLING: verbatim Arabic from the primary source. One disclosed
extraction-spacing artifact fixed ("الش عب" -> "الشعب"); zero-width / non-breaking
spaces stripped; repeated spaces collapsed; tashkeel (diacritics) stripped
uniformly for consistency with this corpus's other BOE-family tracks. No legal
text altered beyond these disclosed source-artifact-layer fixes. Arabic governs;
no translation / paraphrase / interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_violations_penalties",
                   "official_source",
                   "environmental_violations_penalties_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_violations_penalties",
                       "verified")
RECORDS = os.path.join(OUT_VER,
                       "environmental_violations_penalties_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER,
                       "environmental_violations_penalties_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data",
                        "environmental_violations_penalties_arabic_legal_llm",
                        "environmental_violations_penalties_reg_legal_llm_001_010.json")

LAW_ID = "sa-environmental-violations-penalties-reg-312186-1-1442"
LAW_AR = "اللائحة التنفيذية لضبط المخالفات وإيقاع العقوبات لنظام البيئة"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"environmental_violations_penalties_reg_art_(\d{3})$"
APP_RE = r"environmental_violations_penalties_reg_appendix_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام اللوائح الجهة المختصة").split())


def _sort_key(key):
    m = re.match(ART_RE, key)
    if m:
        return (0, int(m.group(1)))
    m = re.match(APP_RE, key)
    return (1, int(m.group(1)))


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; PRIMARY full text is qanoonsa.com/p/505504 (the "
                "consolidated in-force regulation as re-issued by Ministerial "
                "Decision 15101619, server-rendered), appendix corroborated on "
                "qistas.com and the amending decision on qanoonsa.com/p/505503. "
                "laws.boe.gov.sa was checked first per standard methodology but has "
                "NO dedicated lawId page for this Implementing Regulation (only the "
                "base Environmental Law and the Waste Management Law). Citation "
                "cross-verified across mewa.gov.sa, uqn.gov.sa (Umm Al-Qura issue "
                "5055) and istitlaa.ncc.gov.sa. The 1446H amendment re-issued the "
                "regulation WHOLESALE (\"تحل محل\") without itemising per-article "
                "changes; article-level status is اصلية while the track carries "
                "consolidated_amended_law=true. See verification_methodology_note "
                "and known_unresolved_discrepancies in the source artifact before "
                "relying on this track.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        is_app = bool(a.get("is_appendix"))
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        component = "appendix" if is_app else "regulation"
        ver.append({
            "law_key": "environmental_violations_penalties",
            "law_component": component,
            "language": "ar",
            "record_layer": "ENVIRONMENTAL_VIOLATIONS_PENALTIES_REG_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "is_appendix": is_app,
            "is_mukarrar": bool(a.get("is_mukarrar")),
            "article_key": key,
            "number_label_ar": a["number_label_ar"],
            "title_ar": a.get("title_ar") or "",
            "section_ar": a.get("section_ar") or "",
            "article_text_verified": text,
            "verification_status": a["status"],
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_amended": ls == "معدلة",
            "is_added": ls == "مضافة",
            "text_complete": a.get("text_complete", True),
            "amendment_history": a.get("history"),
            "official_text_status": STATUS_UNCHANGED,
            "governing_source_note": gov_note,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        })
        unit_ar = a["number_label_ar"] + ((" - " + a["title_ar"]) if a.get("title_ar") else "")
        llm.append({
            "law_id": LAW_ID,
            "law_component": component,
            "article_number": n,
            "is_appendix": is_app,
            "is_mukarrar": bool(a.get("is_mukarrar")),
            "article_key": key,
            "article_title_ar": unit_ar,
            "title_ar": a.get("title_ar") or "",
            "section_ar": a.get("section_ar") or "",
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_added": ls == "مضافة",
            "is_amended": ls == "معدلة",
            "text_complete": a.get("text_complete", True),
            "record_id": "environmental-violations-penalties-reg-llm-%03d" % idx,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, unit_ar),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, unit_ar),
            "article_path": "environmental_violations_penalties/%s/%s" % (component, key),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "%s %s" % (a["number_label_ar"], LAW_AR),
                "%s %s" % (LAW_AR, a["number_label_ar"]),
                "%s من اللائحة التنفيذية لضبط المخالفات وإيقاع العقوبات لنظام البيئة" % a["number_label_ar"],
            ],
            "text_status": a["status"],
            "source_trust": {
                "source_authority": ("Ministerial Decision (Minister of Environment, "
                                     "Water and Agriculture) No. (312186/1/1442) "
                                     "(4/6/1442H), wholly re-issued by Ministerial "
                                     "Decision No. (15101619) (26/4/1446H, Umm Al-Qura "
                                     "5055) which replaces the original — full text "
                                     "from qanoonsa.com/p/505504, appendix corroborated "
                                     "on qistas.com; laws.boe.gov.sa has no dedicated "
                                     "lawId page for this Implementing Regulation"),
                "source_authority_ar": ("قرار وزير البيئة والمياه والزراعة رقم "
                                        "(312186/1/1442) وتاريخ 4/6/1442هـ، أعيد إصداره "
                                        "بالكامل بالقرار رقم (15101619) وتاريخ "
                                        "26/4/1446هـ (أم القرى 5055) الذي يحل محل الأصلي "
                                        "— النص الكامل من qanoonsa.com/p/505504، والملحق "
                                        "مؤكد من qistas.com؛ بوابة هيئة الخبراء لا تملك "
                                        "صفحة lawId مخصصة لهذه اللائحة التنفيذية"),
                "source_status": a["status"].lower(),
                "source_document_ar": LAW_AR,
                "legal_status_ar": ls,
                "verification_status": a["status"],
            },
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "english_used_for_correction": False,
            "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({
        "law_key": "environmental_violations_penalties",
        "layer": "ENVIRONMENTAL_VIOLATIONS_PENALTIES_REG_ARABIC_VERIFIED_TEXT",
        "record_count": len(ver),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "status_counts": src["status_counts"],
        "decree": src["decree"],
        "decree_date_hijri": src["decree_date_hijri"],
        "amending_decree": src["amending_decree"],
        "amending_decree_date_hijri": src["amending_decree_date_hijri"],
        "gazette_ar": src["gazette_ar"],
        "legal_basis_ar": src["legal_basis_ar"],
        "base_law_track": src["base_law_track"],
        "legal_status_ar": src["legal_status_ar"],
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "amendment_history": src.get("amendment_history", []),
        "supersession": src.get("supersession", {}),
        "chapter_structure": src["chapter_structure"],
        "verification_methodology_note": src["verification_methodology_note"],
        "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
        "source_artifact": os.path.relpath(SRC, ROOT),
    }, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({
        "layer_id": "sa-environmental-violations-penalties-reg-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (10 سجلات: 8 مواد + ملحقان؛ جميعها أصلية)",
        "title_en": ("Implementing Regulation for Recording Violations and Imposing "
                     "Penalties under the Environmental Law — Arabic LLM-ready layer "
                     "(10 records: 8 articles + 2 appendices; all original)"),
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(llm),
        "article_count": src["article_count"],
        "appendix_count": src["appendix_count"],
        "article_range": [1, 8],
        "text_status": STATUS_UNCHANGED,
        "consolidated_amended_law": src.get("consolidated_amended_law", False),
        "status_counts": src["status_counts"],
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Environmental Violations & Penalties "
          "Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
