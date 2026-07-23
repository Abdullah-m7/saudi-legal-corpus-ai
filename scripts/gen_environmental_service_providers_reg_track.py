#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation for Environmental Service Providers under the
Environmental Law track (اللائحة التنفيذية لمقدمي الخدمات البيئية لنظام البيئة). The
in-force version is the Minister of Environment, Water and Agriculture Decision No.
(1515009/1), dated 3/7/1446H, issued under Article 48 of the Environmental Law (Royal
Decree M/165, 19/11/1441H), which WHOLLY REPLACES the founding Decision No.
(582979/1/1442) dated 14/11/1442H.

This is a COMPANION-REGULATION track to the base Environmental Law already ingested in
this corpus (track `environmental_law`, corpus key `environmental`, Royal Decree M/165)
-- the same pattern as food_regulation and the four sibling environmental implementing
regulations built in this session (environmental_permits, environmental_inspection_audit,
environmental_violations_penalties, environmental_air_quality). It is one of ~15
genuinely distinct topical Implementing Regulations under the base Environmental Law
(see reports/coverage_gap_map/coverage_gap_map.json, gap "Implementing Regulations of
the General Environmental Law -- CORRECTED SCOPE", sub_candidate
environmental_service_providers_reg, which flagged the 582979-vs-1515009 citation
disagreement for resolution before build). This track resolves it and ingests the
in-force version.

CITATION RESOLUTION (the gap-map's open question, now settled with a positive finding):
Decision 1515009/1 (Rajab 1446H / Jan 2025) is a genuine LATER WHOLE-REPLACEMENT of the
original Decision 582979/1/1442 (14/11/1442H) -- not a partial amendment. The issuing
decision states verbatim: "ثانيا: تحل هذه اللائحة محل اللائحة التنفيذية لمقدمي الخدمات
البيئية لنظام البيئة، الصادرة بالقرار الوزاري رقم (582979/1/1442) بتاريخ 14/11/1442هـ."
This is the identical self-supersession pattern as the two sibling re-issuances
(environmental_inspection_audit: 15116190 replaced 393691/1/1442;
environmental_violations_penalties: 15101619 replaced 312186/1/1442), issued in the same
regulatory context (Royal Order 32043 of 5/5/1444H reviewing violation/penalty
instruments; Council of Ministers Decision 406 of 14/5/1445H). The original 582979 text
is superseded and NOT ingested; its original article count was not independently fixed.

VERIFICATION TIER -- TIER_2. See the source artifact's verification_methodology_note for
the full account. Summary: laws.boe.gov.sa was checked FIRST per standard methodology and
has NO dedicated lawId page for this regulation (only the base Environmental Law's own
lawId 63831ff6-...). web.archive.org is blocked in this session and was not used. The
GOVERNMENT-PRIMARY source used for verification is the issuing ministry's own official
PDF in MEWA's RulesLibrary (mewa.gov.sa/.../RulesLibrary/Documents/اللائحة التنفيذية
لمقدمي الخدمات البيئية لنظام البيئة.pdf, HTTP 200, 15 pages) -- a SCANNED copy (no
extractable text layer) read visually page-by-page, confirming the decision image and
number (١٥١٥٠٠٩١ in the ministry stamp), the three operative clauses including the whole-
replacement clause and the Minister's signature (Al-Fadley), the table of contents (12
titled articles + Table (1) violations/penalties), and the article + table text. The
ingested article text was taken from a SECOND independent rendering -- the clean linear
HTML on qanoonsa.com/p/506302 (complete: 12 articles + Table + footnote; states the
decision number and gazette placement "Umm Al-Qura issue 5063, 5 Jan 2025") -- and
cross-verified visually against the official MEWA scan (structure, article/item counts,
titles, and table rows match). An automated anagram-signature match (as used by the
sibling tracks against born-digital gazette PDFs) was NOT possible here because the
official MEWA copy is an image-only scan and the uqn gazette PDF was behind an image-only
CDN in this environment; verification was therefore by structure + full visual reading.
Additional corroboration: sra7h.com and ajel.sa (full decision preamble + whole-
replacement clause verbatim; the ingested preamble_ar comes from these); uqn.gov.sa
(gazette existence/date); qistas.com (issue 5063 / structure).

12 articles, each with a descriptive title (NO chapter/باب division), plus Table (1)
"المخالفات والعقوبات" (13 rows) ingested as a distinct structural entry (is_table=true)
referenced by Articles 11 and 12 -- kept whole, neither dropped nor silently merged. All
13 entries are اصلية within the in-force version -- no article-level amendment to THIS
version was found. Text normalization is display-layer only (strip bidi marks/tashkeel/
tatweel; the single qanoonsa spacing artifact "الش عب" corrected to "الشعب" per the
official MEWA scan) -- no letter/number/ruling changed. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_service_providers", "official_source",
                   "environmental_service_providers_reg_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "environmental_service_providers", "verified")
RECORDS = os.path.join(OUT_VER, "environmental_service_providers_reg_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "environmental_service_providers_reg_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "environmental_service_providers_reg_arabic_legal_llm",
                        "environmental_service_providers_reg_legal_llm_001_012.json")

LAW_ID = "sa-environmental-service-providers-regulation-1515009-1"
LAW_AR = "اللائحة التنفيذية لمقدمي الخدمات البيئية لنظام البيئة"
STATUS_UNCHANGED = "UNCHANGED"
ART_RE = r"environmental_service_providers_reg_art_(\d{3})$"
TABLE_RE = r"environmental_service_providers_reg_table_(\d{3})$"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها الجهة المختصة مقدمي الخدمات مقدم البيئية الترخيص").split())


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
    m = re.match(TABLE_RE, key)
    return (1, int(m.group(1)))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; the GOVERNMENT-PRIMARY source is the issuing ministry's own "
                "official PDF in MEWA's RulesLibrary (mewa.gov.sa), a scanned copy of the "
                "in-force regulation read visually page-by-page; the ingested article text is "
                "the clean linear rendering on qanoonsa.com/p/506302, cross-verified against "
                "that official scan (structure, article/item counts, titles, and Table (1) "
                "rows). laws.boe.gov.sa was checked first per standard methodology but has no "
                "dedicated lawId page for this Implementing Regulation. In-force version: "
                "Minister of Environment Decision No. (1515009/1), 3/7/1446H, Umm Al-Qura issue "
                "5063 (5 Jan 2025), under Article 48 of the Environmental Law (Royal Decree "
                "M/165); it WHOLLY REPLACES the founding Decision No. (582979/1/1442), "
                "14/11/1442H. See verification_methodology_note and "
                "known_unresolved_discrepancies in the source artifact before relying on this "
                "track's text or provenance -- in particular the 1515009-vs-582979 whole-"
                "replacement resolution, the decision-number slash-grouping note, the "
                "issue/date cluster, the text-source/cross-verification note, and Table (1) "
                "ingested as a distinct entry.")

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        is_table = bool(a.get("is_table"))
        component = "table" if is_table else "regulation"
        n = a["article_number"]
        ls = a.get("legal_status_ar")
        text = a["text"]
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "environmental_service_providers", "law_component": component,
                    "language": "ar",
                    "record_layer": "ENVIRONMENTAL_SERVICE_PROVIDERS_REG_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_table": is_table, "is_mukarrar": False,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or a.get("title_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": component, "article_number": n,
                    "is_table": is_table, "is_mukarrar": False, "article_key": key,
                    "article_title_ar": "%s: %s" % (a["number_label_ar"], a.get("title_ar") or ""),
                    "title_ar": a.get("title_ar") or "",
                    "section_ar": a.get("section_ar") or a.get("title_ar") or "",
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_added": ls == "مضافة", "is_amended": ls == "معدلة",
                    "text_complete": text_complete,
                    "record_id": "environmental-service-providers-reg-llm-%s-%03d"
                                 % ("table" if is_table else "art", idx),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s: %s" % (LAW_AR, a["number_label_ar"], a.get("title_ar") or ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "environmental_service_providers/regulation/articles/%s" % key,
                    "keywords_ar": _kw((a.get("title_ar") or "") + " " + text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (a.get("title_ar") or "", LAW_AR),
                                          "%s من اللائحة التنفيذية لمقدمي الخدمات البيئية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Minister of Environment, Water and "
                                                          "Agriculture Decision No. (1515009/1) "
                                                          "(3/7/1446H), under Article 48 of the "
                                                          "Environmental Law (Royal Decree M/165) — "
                                                          "official MEWA RulesLibrary PDF (scanned, "
                                                          "read page-by-page) cross-verified against "
                                                          "qanoonsa.com/p/506302 clean HTML; Umm "
                                                          "Al-Qura issue 5063 (5 Jan 2025); WHOLLY "
                                                          "REPLACES Decision No. (582979/1/1442), "
                                                          "14/11/1442H; laws.boe.gov.sa has no "
                                                          "dedicated lawId page for this regulation"),
                                     "source_authority_ar": "قرار وزير البيئة والمياه والزراعة رقم (1515009/1) وتاريخ 3/7/1446هـ، استنادا إلى المادة (الثامنة والأربعين) من نظام البيئة (المرسوم الملكي م/165) — الملف الرسمي لمكتبة أنظمة ولوائح وزارة البيئة (مصدر حكومي أساسي، نسخة ممسوحة قُرئت صفحةً صفحةً) متحقَّق منه مقابل نص qanoonsa.com/p/506302؛ جريدة أم القرى العدد 5063 (5 يناير 2025م)؛ يحل محل القرار رقم (582979/1/1442) وتاريخ 14/11/1442هـ كليا؛ بوابة هيئة الخبراء لا تملك صفحة مخصصة لهذه اللائحة",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "environmental_service_providers",
               "layer": "ENVIRONMENTAL_SERVICE_PROVIDERS_REG_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "article_count": src["article_count"],
               "table_count": src.get("table_count", 0),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "predecessor_decree": src.get("predecessor_decree"),
               "base_law_document": src.get("base_law_document"),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_track_key": src.get("base_law_track_key"),
               "delegation_basis": src.get("delegation_basis"),
               "gazette_reference": src.get("gazette_reference"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src.get("chapter_structure"),
               "structure_note": src.get("structure_note"),
               "preamble_ar": src.get("preamble_ar"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-environmental-service-providers-reg-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 مادة + الجدول 1؛ 13 سجلا، جميعها أصلية ضمن الصيغة النافذة بالقرار 1515009/1)",
               "title_en": ("Implementing Regulation for Environmental Service Providers under the "
                            "Environmental Law — Arabic LLM-ready layer (13 records: 12 articles + "
                            "Table 1; all original within the in-force version, Decision 1515009/1, "
                            "which wholly replaces Decision 582979/1/1442)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 12], "table_count": src.get("table_count", 0),
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "base_law_track_key": src.get("base_law_track_key"),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Environmental Service Providers Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
