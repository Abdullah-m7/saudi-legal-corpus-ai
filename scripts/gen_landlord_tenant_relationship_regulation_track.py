#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Statutory Provisions Regulating the Landlord-Tenant Relationship
track (الأحكام النظامية الخاصة بضبط العلاقة بين المؤجر والمستأجر).

Issued by Royal Decree No. (M/73) dated 2/4/1447H, following Council of
Ministers Resolution No. 226 dated 24/3/1447H and Shura Council Resolution
No. 8/1 dated 22/3/1447H. Published in Umm Al-Qura Gazette, Issue No. 5120,
dated 16/5/1447H (7 November 2025G). Administered by the General Real
Estate Authority (REGA).

DATE-ORDERING DISCREPANCY RESOLVED: a prior research pass flagged an
internally-inconsistent reading (Resolution dated AFTER the Decree it was
supposedly approved by). Direct reading of the Decree's own preamble from
TWO independent official sources (rega.gov.sa and qanoonsa.com, both
reproducing the Royal Decree's own text) confirms the Resolution is dated
24/3/1447H (Rabi' al-Awwal, month 3) -- NOT 24 Rabi' al-Thani (month 4) as
the earlier pass apparently misread. Correct causal/chronological order:
Shura Council Resolution 8/1 (22/3/1447H) -> Council of Ministers
Resolution 226 (24/3/1447H) -> Royal Decree M/73 (2/4/1447H) -> Gazette
publication, Issue 5120 (16/5/1447H). See date_discrepancy_resolution in
the source artifact for full detail and independent Gregorian-conversion
cross-checks (5/5 dates match cited Gregorian equivalents exactly).

WHICH INSTRUMENT, AND HOW CONFIRMED -- confirmed via uqn.gov.sa (Umm
Al-Qura official Gazette, direct HTTP 200 fetch of the born-digital page,
https://uqn.gov.sa/details?p=28602) AND independently via rega.gov.sa (the
administering Authority's own official site, which additionally reproduces
both the Royal Decree's and the Council of Ministers Resolution's own full
preambles) -- TWO independent official/primary sources, in full agreement
(differences are purely formatting: "1-" vs "1." list markers, tanwin
diacritics). Cross-verified further against qanoonsa.com (secondary
aggregator; one extraction glitch in Item 11 documented and NOT relied
upon -- see known_unresolved_discrepancies). laws.boe.gov.sa was checked
(site-restricted WebSearch) but has no dedicated lawId page for this
instrument -- expected, since it is a "أحكام نظامية" issued via a Council
of Ministers Resolution ratified by decree, not a fully numbered "نظام".

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE. Two independently-
produced official sources (Umm Al-Qura Gazette via uqn.gov.sa; REGA's own
official portal) agree verbatim (net of pure formatting) across all 12
items and both preambles, with no unresolved reachability gap.

12 items (البند أولاً..ثاني عشر), flat structure, no مادة/chapter
subdivision -- all 12 اصلية (fresh issuance, zero amendment history).
GEOGRAPHIC SCOPE: Items 2-5 (ثانياً-خامساً) apply to Riyadh city ONLY at
present (Item 6/سادساً, paragraph 1); nationwide/other-city expansion
requires a REGA Board decision approved by the Council of Economic and
Development Affairs (Item 6, paragraph 2). This scope limitation is
disclosed explicitly in geographic_scope_disclosure_ar in the source
artifact and is NOT presented as nationwide anywhere in this track.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "landlord_tenant_relationship_regulation", "regulation",
                   "official_source", "landlord_tenant_relationship_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "landlord_tenant_relationship_regulation", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "landlord_tenant_relationship_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "landlord_tenant_relationship_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "landlord_tenant_relationship_regulation_arabic_legal_llm",
                        "landlord_tenant_relationship_regulation_legal_llm_001_012.json")

LAW_ID = "sa-landlord-tenant-relationship-regulation-m73-1447"
LAW_AR = "الأحكام النظامية الخاصة بضبط العلاقة بين المؤجر والمستأجر"
STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_TEXT_AR_X_REGA_OFFICIAL_PORTAL_DUAL_PRIMARY_CROSSVERIFIED"
KEY_RE = r"landlord_tenant_relationship_regulation_art_(\d{3})$"
EXPECTED_LABELS = ["أولاً", "ثانياً", "ثالثاً", "رابعاً", "خامساً", "سادساً", "سابعاً",
                   "ثامناً", "تاسعاً", "عاشراً", "حادي عشر", "ثاني عشر"]
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة البند البنود هذه الأحكام يجب يجوز عليه "
            "دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال المؤجر المستأجر الهيئة").split())


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
        text = a["text"]
        ver.append({"law_key": "landlord_tenant_relationship_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "LANDLORD_TENANT_RELATIONSHIP_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "text_complete": a.get("text_complete", True),
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this is the Statutory Provisions "
                                              "Regulating the Landlord-Tenant Relationship, Royal "
                                              "Decree M/73 (2/4/1447H), following Council of Ministers "
                                              "Resolution 226 (24/3/1447H) -- a prior research pass's "
                                              "date-ordering discrepancy is RESOLVED (see "
                                              "date_discrepancy_resolution in the source artifact). "
                                              "Verbatim text confirmed via TWO independent official "
                                              "sources (uqn.gov.sa Umm Al-Qura Gazette; rega.gov.sa "
                                              "REGA's own portal), cross-verified against qanoonsa.com. "
                                              "TIER_1_PRIMARY_MULTI_SOURCE. GEOGRAPHIC SCOPE: items "
                                              "2-5 (ثانياً-خامساً) apply to Riyadh city ONLY at present "
                                              "(item 6/سادساً); NOT nationwide. See "
                                              "verification_methodology_note, "
                                              "geographic_scope_disclosure_ar, and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_added": ls == "مضافة", "is_amended": ls == "معدلة",
                    "text_complete": a.get("text_complete", True),
                    "record_id": "landlord-tenant-relationship-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — البند %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - البند %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "landlord_tenant_relationship_regulation/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["البند %s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s البند %s" % (LAW_AR, a["number_label_ar"]),
                                          "البند %s من الأحكام النظامية الخاصة بضبط العلاقة بين "
                                          "المؤجر والمستأجر" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/73, 2/4/1447H, following "
                                                          "Council of Ministers Resolution 226, "
                                                          "24/3/1447H, and Shura Council Resolution "
                                                          "8/1, 22/3/1447H -- Umm Al-Qura Gazette Issue "
                                                          "5120, 16/5/1447H. Verbatim text confirmed via "
                                                          "uqn.gov.sa AND rega.gov.sa (REGA's own "
                                                          "portal) -- two independent official sources "
                                                          "in agreement -- cross-verified against "
                                                          "qanoonsa.com. TIER_1_PRIMARY_MULTI_SOURCE. "
                                                          "Applies to Riyadh city only for items 2-5 "
                                                          "at present; not nationwide."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/73) وتاريخ 2/4/1447هـ، بعد قرار مجلس الوزراء رقم (226) وتاريخ 24/3/1447هـ وقرار مجلس الشورى رقم (8/1) وتاريخ 22/3/1447هـ -- جريدة أم القرى العدد (5120) بتاريخ 16/5/1447هـ. النص الحرفي مؤكَّد عبر uqn.gov.sa وrega.gov.sa (مصدران رسميان مستقلان متطابقان)، ومدقَّق مقارنة مع qanoonsa.com. TIER_1. يقتصر تطبيق البنود (ثانياً-خامساً) على مدينة الرياض حالياً؛ ليس نطاقاً وطنياً.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "landlord_tenant_relationship_regulation",
               "layer": "LANDLORD_TENANT_RELATIONSHIP_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication": src.get("gazette_publication"),
               "legal_status_ar": src.get("legal_status_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "geographic_scope_disclosure_ar": src.get("geographic_scope_disclosure_ar"),
               "date_discrepancy_resolution": src.get("date_discrepancy_resolution"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-landlord-tenant-relationship-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 بنداً؛ إصدار "
                                    "جديد كامل: 12 أصلية؛ يقتصر تطبيق البنود 2-5 على مدينة الرياض "
                                    "حالياً)",
               "title_en": ("Statutory Provisions Regulating the Landlord-Tenant Relationship "
                            "(Royal Decree M/73, 2/4/1447H) — Arabic LLM-ready layer (12 records: "
                            "fresh issuance, all original; items 2-5 apply to Riyadh city only at "
                            "present)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 12], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "geographic_scope_note_en": ("Items 2-5 (ثانياً-خامساً) currently apply to Riyadh "
                                            "city only; nationwide expansion requires a REGA Board "
                                            "decision approved by the Council of Economic and "
                                            "Development Affairs (item 6)."),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Landlord-Tenant Relationship Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
