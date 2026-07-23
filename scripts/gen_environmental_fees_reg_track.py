#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for the Controls and Procedures Related to
the Financial Consideration (Fees) for Environmental Licenses, Permits and Services
track (اللائحة التنفيذية للضوابط والإجراءات المتعلقة بالمقابل المالي للتراخيص
والتصاريح والخدمات البيئية, Minister of Environment, Water and Agriculture Decision
No. 618660/1/1442, 05/12/1442H, under the Environmental Law, Royal Decree M/165,
19/11/1441H).

COMPANION-REGULATION track to the base Environmental Law already ingested in this
corpus (track `environmental`, corpus key `environmental`, Royal Decree M/165) --
the same pattern as this corpus's food_regulation track and the sibling
environmental_permits / environmental_inspection_audit / environmental_violations_penalties
/ environmental_air_quality tracks. It is one of ~15 genuinely distinct topical
Implementing Regulations under the base Environmental Law (see
reports/coverage_gap_map/coverage_gap_map.json, sub_candidate environmental_fees_reg).

VERIFICATION TIER -- TIER_2 (at the lower end of it -- identical confidence layer to
the qanoonsa.com / food_regulation based sibling tracks: a single accessible
full-text source, with strong multi-source citation cross-check and independent
PARTIAL text cross-check). See the source artifact's verification_methodology_note
for the full account. Summary:

- laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. No
  dedicated BOE lawId page exists for this ministerial-decision-level Implementing
  Regulation (consistent with the sibling tracks and BOE practice). web.archive.org
  is blocked in this session and was not accessed.
- The government primary source (Umm Al-Qura gazette) has two pages for this
  regulation (uqn.gov.sa/?p=6782 the approving decision, ?p=6784 the regulation
  text), but the gazette portal is now a SPA serving articles via an internal cms-id
  API; the legacy permalink could not be mapped to a cms-id to extract the article
  text / issue PDF / issue number this pass. The gazette issue number is therefore
  NOT confirmed and was NOT fabricated.
- PRIMARY TEXT SOURCE actually used: qanoniah.com (a non-government legal database
  that republishes officially-published laws/regulations), via its API
  api.qanoniah.com/v1/files/ZAgjkrdaJVnNZDRnz8wW1mQ4E, which returns the regulation
  structured article-by-article with clean linear HTML. qanoniah's own metadata
  corroborates the citation (name; issue date 1442-12-05; instrument "قرار وزاري"
  no. 1442/1/618660; status ساري; linked base law نظام البيئة). Same source layer as
  the qanoonsa.com sibling tracks.
- Citation cross-verified across many independent sources (uqn gazette page titles;
  ajel.sa verbatim on the decision number/date and Article 3; the coverage gap map;
  multiple news outlets). Text cross-verified PARTIALLY and independently: ajel.sa on
  Article 3, and search-engine summaries of maaal.com / aleqt.com / mewa.gov.sa
  reproducing Article 4's opening clause + fee factors and Article 1 definitions,
  all matching the ingested qanoniah text.

STRUCTURE: 4 titled normative articles (no chapter/باب division):
  (1) التعريفات; (2) نطاق عمل المركز المختص بشأن المقابل المالي;
  (3) المقابل المالي للتصاريح أو التراخيص أو الخدمات البيئية;
  (4) المقابل المالي للتصريح البيئي للتشغيل (contains the annual-fee formula).
Followed by Annex (1) "الحدود القصوى للمقابل المالي..." -- a fee/ceiling TABLE, whose
tabular content is not available as text in the source (title only); it is DISCLOSED
but NOT ingested and NOT fabricated (annex_structure + known_unresolved_discrepancies),
consistent with food_regulation and the sibling environmental tracks.

All 4 articles are اصلية. REPEAL/SUPERSESSION: negative finding -- generic
conflict-repeal clause only, no named predecessor; no later decision replacing/amending
this regulation was found (unlike some siblings reissued in 2024-2025). A residual
possibility of administrative updates to the Annex-1 ceilings (which Articles 3 and 4
provide for every 3 years) is disclosed; that is distinct from amending the regulation.

Source digit glyphs are preserved as rendered by qanoniah (Western digits, e.g.
"(0,8)", "(1.2)", "(3)"); no numeric value or ruling was changed. Article 2's ASCII
comma and Article 4's mixed decimal separators are genuine source renderings,
preserved verbatim and disclosed. No verbatim issuing-decision preamble was recovered
this pass, so preamble_ar is deliberately NOT included (no fabrication).

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_fees", "official_source",
                   "environmental_fees_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_fees", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_fees_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_fees_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_fees_reg_arabic_legal_llm",
                        "environmental_fees_reg_legal_llm_001_004.json")

LAW_ID = "sa-environmental-fees-regulation-618660-1-1442"
LAW_AR = "اللائحة التنفيذية للضوابط والإجراءات المتعلقة بالمقابل المالي للتراخيص والتصاريح والخدمات البيئية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"environmental_fees_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها المركز النشاط البيئي البيئية المقابل المالي").split())


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
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; PRIMARY TEXT source is qanoniah.com (non-government "
                "legal database republishing officially-published laws/regulations), via "
                "api.qanoniah.com/v1/files/ZAgjkrdaJVnNZDRnz8wW1mQ4E (structured "
                "article-by-article, clean HTML), whose metadata corroborates the "
                "citation (issue date 1442-12-05; ministerial decision 1442/1/618660; "
                "status ساري; base law نظام البيئة). laws.boe.gov.sa was checked FIRST "
                "per standard methodology and has no dedicated lawId page for this "
                "Implementing Regulation. The Umm Al-Qura gazette (government primary) has "
                "pages for this regulation but its portal is now a SPA whose article text "
                "/ issue PDF / issue number could not be extracted this pass (issue number "
                "NOT confirmed, not fabricated). Citation cross-verified across many "
                "independent sources; text cross-verified PARTIALLY and independently "
                "(ajel.sa on Art 3; maaal/aleqt/mewa summaries on Arts 1 and 4). Issued by "
                "Minister of Environment Decision No. (618660/1/1442) dated 05/12/1442H, "
                "companion to the Environmental Law (Royal Decree M/165). See "
                "verification_methodology_note and known_unresolved_discrepancies in the "
                "source artifact before relying on this track's text or provenance -- in "
                "particular the single-full-text-source limitation, the unconfirmed gazette "
                "issue number, the excluded Annex-1 fee-ceiling table, the preserved source "
                "digit glyphs / punctuation, and the deliberately-omitted verbatim preamble.")

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
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "environmental_fees", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ENVIRONMENTAL_FEES_REG_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or a.get("title_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": "%s: %s" % (a["number_label_ar"], a.get("title_ar") or ""),
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or a.get("title_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "environmental-fees-reg-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s: %s" % (LAW_AR, a["number_label_ar"], a.get("title_ar") or ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "environmental_fees/regulation/articles/%s" % key,
                    "keywords_ar": _kw((a.get("title_ar") or "") + " " + text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (a.get("title_ar") or "", LAW_AR),
                                          "%s من اللائحة التنفيذية للمقابل المالي للتراخيص والتصاريح والخدمات البيئية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Minister of Environment, Water and "
                                                          "Agriculture Decision No. (618660/1/1442) "
                                                          "(05/12/1442H), under the Environmental Law "
                                                          "(Royal Decree M/165) — primary TEXT source "
                                                          "qanoniah.com (api.qanoniah.com/v1/files/"
                                                          "ZAgjkrdaJVnNZDRnz8wW1mQ4E), a non-government "
                                                          "legal database republishing the officially-"
                                                          "published regulation; citation cross-verified "
                                                          "across many sources (uqn gazette pages, ajel.sa "
                                                          "verbatim, coverage gap map); text partially "
                                                          "cross-verified; laws.boe.gov.sa has no "
                                                          "dedicated lawId page; gazette issue number not "
                                                          "confirmed this pass"),
                                     "source_authority_ar": "قرار وزير البيئة والمياه والزراعة رقم (618660/1/1442) وتاريخ 05/12/1442هـ، استنادا إلى نظام البيئة (المرسوم الملكي م/165) — مصدر النص الأساسي qanoniah.com (api.qanoniah.com/v1/files/ZAgjkrdaJVnNZDRnz8wW1mQ4E)، قاعدة قانونية غير حكومية تعيد نشر اللائحة المنشورة رسميا؛ الاستشهاد مؤكَّد بتقاطع عدة مصادر (صفحتا جريدة أم القرى، وموقع أجل حرفيا، وخريطة فجوات التغطية)؛ والنص مؤكَّد جزئيا بتقاطع مستقل؛ بوابة هيئة الخبراء لا تملك صفحة مخصصة؛ رقم عدد الجريدة غير مؤكَّد هذه الجولة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "environmental_fees",
               "layer": "ENVIRONMENTAL_FEES_REG_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "base_law_document": src.get("base_law_document"),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_track_key": src.get("base_law_track_key"),
               "delegation_basis": src.get("delegation_basis"),
               "gazette_reference_note": src.get("gazette_reference_note"),
               "application_date_press": src.get("application_date_press"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "supersession_finding_ar": src.get("supersession_finding_ar"),
               "annex_structure": src.get("annex_structure", []),
               "annex_count": src.get("annex_count", 0),
               "structure_note": src.get("structure_note"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-environmental-fees-reg-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (4 مواد؛ 4 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ الملحق (1) جدول الحدود القصوى غير مُدرَج)",
               "title_en": ("Implementing Regulation for the Financial Consideration (Fees) for "
                            "Environmental Licenses, Permits and Services — Arabic LLM-ready layer "
                            "(4 records: 4 original, 0 amended, 0 added, 0 repealed; Annex (1) "
                            "fee-ceiling table not ingested)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 4], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "base_law_track_key": src.get("base_law_track_key"),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Environmental Fees Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
