#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a single unified retrieval index over every Arabic LLM-ready layer.

Normalizes the per-law enrichment layers — Companies Law, PDPL (law +
implementing regulation), and the Investment Law (law + implementing
regulations) — into one flat JSONL index of retrieval records sharing a common
schema, so a single search can query the whole corpus.

Each source layer already carries mechanical retrieval metadata (llm_title /
retrieval_title / article_path / keywords / search_queries).  This generator only
projects those fields into a common shape and stamps the owning law's friendly
Arabic title and corpus key.  It does not alter, summarize, translate, or
re-derive any legal text.  Arabic governs.

Read-only over its inputs; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "corpus_unified_index")
INDEX = os.path.join(OUT_DIR, "corpus_unified_llm_index.jsonl")
SUMMARY = os.path.join(OUT_DIR, "corpus_unified_llm_index_summary.json")

# (relative layer file, corpus key, default law_component when a record omits it)
LAYERS = [
    ("data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
     "companies_law", "law"),
    ("data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json",
     "pdpl", "law"),
    ("data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
     "pdpl", "implementing_regulation"),
    ("data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json",
     "investment", "law"),
    ("data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json",
     "investment", "implementing_regulation"),
    ("data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
     "civil", "law"),
    ("data/gtpl_arabic_legal_llm/gtpl_law_legal_llm_001_099.json",
     "gtpl", "law"),
    ("data/gtpl_arabic_legal_llm/gtpl_regulation_legal_llm_001_157.json",
     "gtpl", "implementing_regulation"),
    ("data/labor_arabic_legal_llm/labor_law_legal_llm_001_245.json",
     "labor", "law"),
    ("data/labor_arabic_legal_llm/labor_regulation_legal_llm_001_040.json",
     "labor", "implementing_regulation"),
    ("data/labor_arabic_legal_llm/labor_annex1_legal_llm_001_072.json",
     "labor", "model_work_regulation"),
    ("data/labor_arabic_legal_llm/labor_annex1_violation_tables_llm.json",
     "labor", "model_work_regulation"),
    ("data/labor_arabic_legal_llm/labor_annex3_legal_llm_001_020.json",
     "labor", "recruitment_mediation_rules"),
    ("data/labor_arabic_legal_llm/labor_annex4_legal_llm_001_072.json",
     "labor", "recruitment_services_rules"),
    ("data/labor_arabic_legal_llm/labor_annex2_accessibility_tables_llm.json",
     "labor", "accessibility_arrangements"),
    ("data/labor_arabic_legal_llm/labor_annex5_contract_forms_llm.json",
     "labor", "model_contract_forms"),
    ("data/evidence_arabic_legal_llm/evidence_law_legal_llm_001_129.json",
     "evidence", "law"),
    ("data/evidence_arabic_legal_llm/evidence_electronic_rules_legal_llm_001_024.json",
     "evidence", "electronic_procedures_rules"),
    ("data/evidence_arabic_legal_llm/evidence_procedural_manuals_legal_llm_001_135.json",
     "evidence", "procedural_manuals"),
    ("data/evidence_arabic_legal_llm/evidence_expertise_rules_legal_llm_001_034.json",
     "evidence", "expertise_rules"),
    ("data/personal_status_arabic_legal_llm/personal_status_law_legal_llm_001_252.json",
     "personal_status", "law"),
    ("data/personal_status_arabic_legal_llm/personal_status_regulation_legal_llm_001_041.json",
     "personal_status", "implementing_regulation"),
    ("data/sharia_procedure_arabic_legal_llm/sharia_procedure_law_legal_llm_001_243.json",
     "sharia_procedure", "law"),
    ("data/sharia_procedure_arabic_legal_llm/sharia_procedure_regulation_legal_llm_001_637.json",
     "sharia_procedure", "implementing_regulation"),
    ("data/criminal_procedure_arabic_legal_llm/criminal_procedure_law_legal_llm_001_222.json",
     "criminal_procedure", "law"),
    ("data/criminal_procedure_arabic_legal_llm/criminal_procedure_regulation_legal_llm_001_181.json",
     "criminal_procedure", "implementing_regulation"),
    ("data/enforcement_arabic_legal_llm/enforcement_law_legal_llm_001_098.json",
     "enforcement", "law"),
    ("data/enforcement_arabic_legal_llm/enforcement_regulation_legal_llm_001_273.json",
     "enforcement", "implementing_regulation"),
    ("data/judiciary_arabic_legal_llm/judiciary_law_legal_llm_001_085.json",
     "judiciary", "law"),
    ("data/board_of_grievances_arabic_legal_llm/board_of_grievances_law_legal_llm_001_026.json",
     "board_of_grievances", "law"),
    ("data/law_practice_arabic_legal_llm/law_practice_law_legal_llm_001_056.json",
     "law_practice", "law"),
    ("data/law_practice_arabic_legal_llm/law_practice_regulation_legal_llm_001_090.json",
     "law_practice", "implementing_regulation"),
    ("data/commercial_courts_arabic_legal_llm/commercial_courts_law_legal_llm_001_096.json",
     "commercial_courts", "law"),
    ("data/commercial_courts_arabic_legal_llm/commercial_courts_regulation_legal_llm_001_281.json",
     "commercial_courts", "implementing_regulation"),
    ("data/bankruptcy_arabic_legal_llm/bankruptcy_law_legal_llm_001_231.json",
     "bankruptcy", "law"),
    ("data/bankruptcy_arabic_legal_llm/bankruptcy_regulation_legal_llm_001_098.json",
     "bankruptcy", "implementing_regulation"),
    ("data/bankruptcy_arabic_legal_llm/bankruptcy_case_rules_legal_llm_001_024.json",
     "bankruptcy", "case_procedure_rules"),
    ("data/judicial_costs_arabic_legal_llm/judicial_costs_law_legal_llm_001_023.json",
     "judicial_costs", "law"),
    ("data/judicial_costs_arabic_legal_llm/judicial_costs_regulation_legal_llm_001_017.json",
     "judicial_costs", "implementing_regulation"),
    ("data/arbitration_arabic_legal_llm/arbitration_law_legal_llm_001_058.json",
     "arbitration", "law"),
    ("data/arbitration_arabic_legal_llm/arbitration_regulation_legal_llm_001_019.json",
     "arbitration", "implementing_regulation"),
    ("data/commercial_papers_arabic_legal_llm/commercial_papers_law_legal_llm_001_121.json",
     "commercial_papers", "law"),
    ("data/commercial_register_arabic_legal_llm/commercial_register_law_legal_llm_001_029.json",
     "commercial_register", "law"),
    ("data/trade_names_arabic_legal_llm/trade_names_law_legal_llm_001_023.json",
     "trade_names", "law"),
    ("data/commercial_agencies_arabic_legal_llm/commercial_agencies_law_legal_llm_001_006.json",
     "commercial_agencies", "law"),
    ("data/chambers_of_commerce_arabic_legal_llm/chambers_of_commerce_law_legal_llm_001_066.json",
     "chambers_of_commerce", "law"),
    ("data/commercial_books_arabic_legal_llm/commercial_books_law_legal_llm_001_016.json",
     "commercial_books", "law"),
    ("data/aml_arabic_legal_llm/aml_law_legal_llm_001_052.json",
     "aml", "law"),
    ("data/tawtheeq_arabic_legal_llm/tawtheeq_law_legal_llm_001_057.json",
     "tawtheeq", "law"),
    ("data/tawtheeq_arabic_legal_llm/tawtheeq_regulation_legal_llm_001_031.json",
     "tawtheeq", "implementing_regulation"),
    ("data/real_estate_registration_arabic_legal_llm/real_estate_registration_law_legal_llm_001_040.json",
     "real_estate_registration", "law"),
    ("data/real_estate_registration_arabic_legal_llm/real_estate_registration_regulation_legal_llm_001_051.json",
     "real_estate_registration", "implementing_regulation"),
    ("data/real_estate_mortgage_arabic_legal_llm/real_estate_mortgage_law_legal_llm_001_046.json",
     "real_estate_mortgage", "law"),
    ("data/real_estate_finance_arabic_legal_llm/real_estate_finance_law_legal_llm_001_015.json",
     "real_estate_finance", "law"),
    ("data/real_estate_units_arabic_legal_llm/real_estate_units_law_legal_llm_001_033.json",
     "real_estate_units", "law"),
    ("data/real_estate_units_arabic_legal_llm/real_estate_units_regulation_legal_llm_001_041.json",
     "real_estate_units", "implementing_regulation"),
    ("data/foreign_ownership_arabic_legal_llm/foreign_ownership_law_legal_llm_001_015.json",
     "foreign_ownership", "law"),
    ("data/municipal_realestate_arabic_legal_llm/municipal_realestate_law_legal_llm_001_006.json",
     "municipal_realestate", "law"),
    ("data/municipal_realestate_arabic_legal_llm/municipal_realestate_regulation_legal_llm_001_035.json",
     "municipal_realestate", "implementing_regulation"),
    ("data/gcc_ownership_arabic_legal_llm/gcc_ownership_law_legal_llm_001_006.json",
     "gcc_ownership", "law"),
    ("data/terrorism_arabic_legal_llm/terrorism_law_legal_llm_001_099.json",
     "terrorism", "law"),
    ("data/terrorism_arabic_legal_llm/terrorism_regulation_legal_llm_001_028.json",
     "terrorism", "implementing_regulation"),
    ("data/juveniles_arabic_legal_llm/juveniles_law_legal_llm_001_024.json",
     "juveniles", "law"),
    ("data/juveniles_arabic_legal_llm/juveniles_regulation_legal_llm_001_013.json",
     "juveniles", "implementing_regulation"),
    ("data/whistleblower_arabic_legal_llm/whistleblower_law_legal_llm_001_037.json",
     "whistleblower", "law"),
    ("data/judicial_inspection_arabic_legal_llm/judicial_inspection_regulation_legal_llm_001_068.json",
     "judicial_inspection", "regulation"),
    ("data/qismah_arabic_legal_llm/qismah_regulation_legal_llm_001_048.json",
     "qismah", "regulation"),
    ("data/sulook_arabic_legal_llm/sulook_regulation_legal_llm_001_047.json",
     "sulook", "regulation"),
    ("data/aawan_arabic_legal_llm/aawan_regulation_legal_llm_001_035.json",
     "aawan", "regulation"),
    ("data/muslaha_arabic_legal_llm/muslaha_regulation_legal_llm_001_029.json",
     "muslaha", "regulation"),
    ("data/iflas_hudud_arabic_legal_llm/iflas_hudud_regulation_legal_llm_001_023.json",
     "iflas_hudud", "regulation"),
    ("data/judicial_documents_arabic_legal_llm/judicial_documents_regulation_legal_llm_001_023.json",
     "judicial_documents", "regulation"),
    ("data/bankruptcy_fees_arabic_legal_llm/bankruptcy_fees_regulation_legal_llm_001_020.json",
     "bankruptcy_fees", "regulation"),
    ("data/enforcement_providers_arabic_legal_llm/enforcement_providers_regulation_legal_llm_001_018.json",
     "enforcement_providers", "regulation"),
    ("data/alimony_fund_arabic_legal_llm/alimony_fund_regulation_legal_llm_001_017.json",
     "alimony_fund", "regulation"),
    ("data/judiciary_bog_arabic_legal_llm/judiciary_bog_mechanism_legal_llm_001_015.json",
     "judiciary_bog", "mechanism"),
    ("data/documentation_settlement_arabic_legal_llm/documentation_settlement_regulation_legal_llm_001_015.json",
     "documentation_settlement", "regulation"),
    ("data/mosalaha_center_arabic_legal_llm/mosalaha_center_regulation_legal_llm_001_010.json",
     "mosalaha_center", "regulation"),
    ("data/medical_reports_arabic_legal_llm/medical_reports_regulation_legal_llm_001_013.json",
     "medical_reports", "regulation"),
    ("data/marriage_non_saudi_arabic_legal_llm/marriage_non_saudi_regulation_legal_llm_001_011.json",
     "marriage_non_saudi", "regulation"),
    ("data/state_funded_lawyer_arabic_legal_llm/state_funded_lawyer_regulation_legal_llm_001_011.json",
     "state_funded_lawyer", "regulation"),
    ("data/lessor_repossession_arabic_legal_llm/lessor_repossession_regulation_legal_llm_001_007.json",
     "lessor_repossession", "regulation"),
    ("data/elitigation_guide_arabic_legal_llm/elitigation_guide_regulation_legal_llm_001_005.json",
     "elitigation_guide", "regulation"),
    ("data/judicial_training_center_arabic_legal_llm/judicial_training_center_guide_legal_llm_001_018.json",
     "judicial_training_center", "guide"),
    ("data/judgment_objection_methods_arabic_legal_llm/judgment_objection_methods_regulation_legal_llm_001_062.json",
     "judgment_objection_methods", "regulation"),
    ("data/real_estate_expropriation_arabic_legal_llm/real_estate_expropriation_law_legal_llm_001_039.json",
     "real_estate_expropriation", "law"),
    ("data/marriage_contract_hearing_arabic_legal_llm/marriage_contract_hearing_regulation_legal_llm_001_010.json",
     "marriage_contract_hearing", "regulation"),
    ("data/anti_bribery_arabic_legal_llm/anti_bribery_law_legal_llm_001_023.json",
     "anti_bribery", "law"),
    ("data/basic_law_of_governance_arabic_legal_llm/basic_law_of_governance_legal_llm_001_083.json",
     "basic_law_of_governance", "law"),
    ("data/anti_cyber_crime_arabic_legal_llm/anti_cyber_crime_law_legal_llm_001_016.json",
     "anti_cyber_crime", "law"),
    ("data/anti_harassment_arabic_legal_llm/anti_harassment_law_legal_llm_001_008.json",
     "anti_harassment", "law"),
    ("data/anti_trafficking_arabic_legal_llm/anti_trafficking_law_legal_llm_001_017.json",
     "anti_trafficking", "law"),
    ("data/council_of_ministers_arabic_legal_llm/council_of_ministers_law_legal_llm_001_032.json",
     "council_of_ministers", "law"),
    ("data/regions_arabic_legal_llm/regions_law_legal_llm_001_041.json",
     "regions", "law"),
    ("data/electronic_transactions_arabic_legal_llm/electronic_transactions_law_legal_llm_001_031.json",
     "electronic_transactions", "law"),
    ("data/allegiance_commission_arabic_legal_llm/allegiance_commission_law_legal_llm_001_025.json",
     "allegiance_commission", "law"),
    ("data/shura_council_arabic_legal_llm/shura_council_law_legal_llm_001_030.json",
     "shura_council", "law"),
]


def _law_title(envelope):
    # envelope title_ar is like "نظام الشركات — الطبقة العربية ..." -> take the part before the em dash
    t = envelope.get("title_ar", "")
    return t.split(" — ", 1)[0].strip() if " — " in t else t.strip()


def _text_of(rec):
    return rec.get("article_text_ar") or rec.get("official_text_ar") or ""


def _status_of(rec):
    return (rec.get("text_status")
            or rec.get("source_trust", {}).get("source_status")
            or rec.get("record_type")
            or "unspecified")


def build():
    rows = []
    counts = {}
    for rel, corpus, default_component in LAYERS:
        env = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        recs = env["records"] if isinstance(env, dict) and "records" in env else env
        law_title = _law_title(env) if isinstance(env, dict) else corpus
        n = 0
        for r in recs:
            rows.append({
                "record_id": r["record_id"],
                "corpus": corpus,
                "law_id": r.get("law_id"),
                "law_component": r.get("law_component", default_component),
                "law_title_ar": law_title,
                "article_number": r["article_number"],
                "llm_title_ar": r.get("llm_title_ar"),
                "retrieval_title_ar": r.get("retrieval_title_ar"),
                "article_path": r.get("article_path"),
                "keywords_ar": r.get("keywords_ar", []),
                "search_queries_ar": r.get("search_queries_ar", []),
                "text_ar": _text_of(r),
                "text_status": _status_of(r),
                "source_layer": os.path.basename(rel),
            })
            n += 1
        counts[os.path.basename(rel)] = n

    # stable order: corpus, law_component (law before regulation), article_number
    comp_rank = {"law": 0, "implementing_regulation": 1}
    rows.sort(key=lambda x: (x["corpus"], comp_rank.get(x["law_component"], 9), x["article_number"]))
    return rows, counts


def main():
    rows, counts = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_corpus = {}
    for r in rows:
        by_corpus[r["corpus"]] = by_corpus.get(r["corpus"], 0) + 1
    summary = {
        "index": "CORPUS_UNIFIED_LLM_RETRIEVAL_INDEX",
        "total_records": len(rows),
        "records_per_layer": counts,
        "records_per_corpus": by_corpus,
        "layers": [os.path.basename(rel) for rel, _, _ in LAYERS],
        "fields": ["record_id", "corpus", "law_id", "law_component", "law_title_ar",
                   "article_number", "llm_title_ar", "retrieval_title_ar", "article_path",
                   "keywords_ar", "search_queries_ar", "text_ar", "text_status", "source_layer"],
        "note": ("Flat retrieval index projected from the per-law LLM-ready enrichment layers. "
                 "No legal text altered, summarized, translated, or re-derived. Arabic governs."),
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote unified index: %d records -> %s" % (len(rows), os.path.relpath(INDEX, ROOT)))
    for k, v in sorted(by_corpus.items()):
        print("  %-14s %d" % (k, v))


if __name__ == "__main__":
    main()
