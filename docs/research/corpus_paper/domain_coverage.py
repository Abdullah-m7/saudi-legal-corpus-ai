#!/usr/bin/env python3
"""Group corpus tracks into legal domains for the journal paper's coverage table.

The registry records no domain field, so the domain grouping below is an
AUTHOR-ASSIGNED taxonomy, applied by explicit, ordered keyword rules over
track and corpus identifiers. It is reported as such in the paper: it
organizes coverage for the reader and is not a property of the underlying
legislation.

Rules are ordered; the first matching rule wins. Every track lands in exactly
one domain, and any track matching no rule is reported under "unclassified"
so the mapping can never silently mislabel coverage.

Run from the repository root:

    python3 docs/research/corpus_paper/domain_coverage.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "data" / "corpus_registry" / "corpus_registry.json"
INDEX = REPO_ROOT / "data" / "corpus_unified_index" / "corpus_unified_llm_index.jsonl"
OUT = Path(__file__).resolve().parent / "domain_coverage.json"

# (domain, [keys matched on token boundaries against the identifier])
# Ordered: first match wins, so put specific rules before general ones.
RULES = [
    # Placed first: these would otherwise be captured by broader rules below
    # ("social_insurance" by insurance, "mining_investment" by investment).
    ("Labor and social insurance", [
        "labor", "domestic_labor", "social_insurance", "social_insurance_legacy",
        "osh", "high_risk_professions", "civil_service",
    ]),
    ("Energy, industry and infrastructure", [
        "mining_investment", "electricity", "petroleum", "dry_gas",
        "energy_supplies", "building_code", "engineering_practice",
        "saudi_engineers", "standards_quality", "railway", "road_transport",
        "civil_aviation", "gaca", "aviation_passenger_rights", "maritime_commercial",
        "mawani", "tga", "fisheries", "agriculture",
    ]),
    ("Courts, procedure and enforcement", [
        "judiciary", "board_of_grievances", "bog_", "commercial_courts",
        "sharia_procedure", "criminal_procedure", "enforcement", "evidence",
        "judicial", "law_practice", "arbitration", "muslaha", "mosalaha",
        "public_prosecution", "judgment_objection", "elitigation", "aawan",
        "state_funded_lawyer", "prison_detention", "juveniles", "iflas_hudud",
        "documentation_settlement", "tawtheeq", "qismah", "sulook",
    ]),
    ("Financial and capital markets", [
        "capital_market", "banking_control", "sama", "finance_companies",
        "finance_lease", "payment_systems", "credit_information",
        "insurance_control", "insurance_authority", "cooperative_health_insurance",
        "aml", "bnpl", "debt_collection", "cma", "investment", "foreign_ownership",
        "gcc_ownership", "privatization", "state_revenue", "seized_confiscated",
    ]),
    ("Commercial and corporate", [
        "companies", "implementing_regulations_general",
        "implementing_regulations_listed_joint_stock",
        "commercial_register", "commercial_books",
        "commercial_papers", "commercial_agencies", "trade_names", "franchise",
        "bankruptcy", "chambers_of_commerce", "competition", "ecommerce",
        "anti_concealment", "anti_fraud", "product_safety", "gtpl",
        "contractors_classification", "gcc_anti_dumping",
    ]),
    ("Tax and zakat", [
        "vat", "zakat", "income_tax", "rett", "customs", "einvoicing",
        "white_land_fees",
    ]),
    ("Civil, personal status and property", [
        "civil_arabic", "civil_transactions", "personal_status", "alimony",
        "=civil",  # the Civil Transactions Law's own corpus key
        "marriage", "awqaf", "real_estate", "rega", "offplan", "landlord",
        "lessor", "municipal_realestate", "expropriation",
    ]),
    ("Criminal justice, security and civil status", [
        "anti_bribery", "anti_narcotics", "anti_trafficking", "anti_harassment",
        "terrorism", "weapons", "anti_smoking", "nazaha", "whistleblower",
        "civil_defense", "traffic", "residency", "premium_residency",
        "travel_documents", "nationality", "civil_status",
    ]),
    ("Technology, data, telecommunications and IP", [
        "pdpl", "cybersecurity", "nca_", "anti_cyber_crime",
        "electronic_transactions", "telecommunications", "frequency_spectrum",
        "sdaia", "cst", "nca", "postal", "copyright", "patent", "trademark",
    ]),
    ("Health, environment and safety", [
        "health", "healthcare", "pharmaceutical", "mental_health", "organ_donation",
        "medical_reports", "environmental", "waste_management", "food", "water",
        "elderly_care", "disability", "child_protection", "protection_from_abuse",
    ]),
    ("Education, culture, media and civil society", [
        "education", "universities", "etec", "tvtc", "private_schools",
        "foreign_schools", "press", "audiovisual_media", "antiquities",
        "sports", "tourism", "hajj", "associations_ngo", "cooperative_societies",
        "accredited_valuers", "accounting_auditing",
    ]),
    ("Constitutional and administrative", [
        "basic_law", "shura", "council_of_ministers", "allegiance_commission",
        "regions", "municipal_councils",
    ]),
]


def classify_text(text):
    """Return the domain for a track_id or corpus key.

    Keys match on underscore-delimited token boundaries, never as bare
    substrings: the rule "vat" matches "vat_law" but not "private_schools".
    A key may itself be a multi-token prefix (e.g. "real_estate"). A key
    written as "=value" requires the whole identifier to equal `value`, for
    short corpus keys such as "civil" that would otherwise swallow unrelated
    tracks like "civil_defense_law".
    """
    hay = text.lower()
    for domain, keys in RULES:
        for k in keys:
            if k.startswith("="):
                if hay == k[1:]:
                    return domain
            elif re.search(rf"(?:^|_){re.escape(k)}(?:_|$)", hay):
                return domain
    return "unclassified"


def classify(track):
    # track_id only: display names introduce false matches (e.g. the
    # insurance-supervision law's official English name contains "Companies").
    return classify_text(track.get("track_id", ""))


def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]

    # Records per corpus key, so domain record counts come from the index.
    per_corpus = defaultdict(int)
    with open(INDEX, encoding="utf-8") as f:
        for line in f:
            per_corpus[json.loads(line)["corpus"]] += 1

    domains = defaultdict(lambda: {"tracks": 0, "records": 0, "track_ids": []})

    # Track counts: classify each legislative track.
    for t in tracks:
        if t.get("corpus_family") == "closure_audit":
            continue  # QA artifact, not legislation
        d = classify(t)
        domains[d]["tracks"] += 1
        domains[d]["track_ids"].append(t["track_id"])

    # Record counts: classify each corpus key directly with the same rules, so
    # every indexed record lands in a domain regardless of track/corpus naming.
    for corpus, n in per_corpus.items():
        domains[classify_text(corpus)]["records"] += n

    out = {
        "note": (
            "Author-assigned domain grouping produced by explicit ordered "
            "keyword rules over track_id (track counts) and over the corpus "
            "key (record counts); not a property of the "
            "legislation itself. First matching rule wins."
        ),
        "total_tracks_classified": sum(d["tracks"] for d in domains.values()),
        "total_records_classified": sum(d["records"] for d in domains.values()),
        "domains": {
            k: {"tracks": v["tracks"], "records": v["records"],
                "track_ids": sorted(v["track_ids"])}
            for k, v in sorted(domains.items(), key=lambda kv: -kv[1]["tracks"])
        },
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", "utf-8")

    for k, v in out["domains"].items():
        print(f"{v['tracks']:3d} tracks {v['records']:6d} records  {k}")
    print(f"\ntracks classified: {out['total_tracks_classified']}")
    print(f"records classified: {out['total_records_classified']}")
    if "unclassified" in out["domains"]:
        print("\nUNCLASSIFIED:", out["domains"]["unclassified"]["track_ids"])


if __name__ == "__main__":
    main()
