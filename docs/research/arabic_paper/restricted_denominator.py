#!/usr/bin/env python3
"""Is the applied law small, or is the denominator wrong?

The headline of paper 8 — that a ninth of the statute book is ever cited —
invites one obvious objection, and it is a fair one. The published judgments
are overwhelmingly commercial, so the denominator holds instruments a
commercial court could never reach: juveniles, traffic, public health. Divide
by all of them and the share is small by construction.

The objection is answered with a measurement, not a paragraph, and the scope
is drawn by the statute rather than by the author. Article 16 of the
Commercial Courts Law enumerates what the court may hear, and each paragraph
names its instruments:

  ¶3  partnership contracts under the Civil Transactions Law
  ¶4  claims and violations arising from the Companies Law
  ¶5  claims and violations arising from the Bankruptcy Law
  ¶6  claims and violations arising from the intellectual property laws
  ¶7  claims and violations arising from the other commercial laws

Only ¶7 requires judgement, so it is drawn twice — narrowly, as the core
instruments of trade and companies, and broadly, as everything whose subject
is trade, finance or commercial regulation — and every result below is
reported under both. A finding that survives the broad reading is not an
artefact of a hand-picked denominator.

Four denominators are reported, from the widest to the narrowest:
  the whole registry, as in the headline
  the scope of Article 16, narrow and broad
  the instruments actually cited at least once — 'even where the court goes'
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ARTICLES = HERE / "applied_articles_results.json"

# The court's own procedure: what it uses to hear anything at all.
PROCEDURE = [
    "commercial_courts_law", "commercial_courts_implementing_regulation",
    "sharia_procedure_law", "sharia_procedure_implementing_regulation",
    "evidence_law", "evidence_procedural_manuals", "evidence_expertise_rules",
    "evidence_electronic_procedures_rules",
    "arbitration_law", "arbitration_implementing_regulation",
    "law_practice_law", "law_practice_implementing_regulation",
    "enforcement_law", "enforcement_implementing_regulation",
    "judiciary_law", "judgment_objection_methods_regulation",
    "judicial_costs_law", "judicial_costs_implementing_regulation",
]

PARA_3 = ["civil_transactions_law"]
PARA_4 = ["companies_law", "implementing_regulations_general",
          "implementing_regulations_listed_joint_stock",
          "cma_corporate_governance_regulation"]
PARA_5 = ["bankruptcy_law", "bankruptcy_implementing_regulation",
          "bankruptcy_case_rules", "bankruptcy_fees_regulation",
          "iflas_hudud_regulation"]
PARA_6 = ["trademark_law", "patent_law", "patent_regulation", "copyright_law"]

# ¶7, narrowly: the instruments that constitute trade itself.
PARA_7_NARROW = [
    "commercial_papers_law", "commercial_register_law",
    "commercial_register_regulation", "commercial_books_law",
    "trade_names_law", "trade_names_regulation",
    "commercial_agencies_law", "commercial_agencies_regulation",
    "franchise_law", "franchise_regulation",
    "ecommerce_law", "ecommerce_regulation",
    "competition_law", "competition_regulation",
    "anti_fraud_law", "anti_fraud_regulation",
    "anti_concealment_law", "anti_concealment_regulation",
    "maritime_commercial_law", "maritime_commercial_regulation",
    "chambers_of_commerce_law", "chambers_of_commerce_regulation",
]

# ¶7, broadly: everything whose subject is trade, finance, or the regulation
# of commercial activity, including instruments a commercial court would reach
# only at the edge of its jurisdiction.
PARA_7_BROAD = PARA_7_NARROW + [
    "finance_lease_law", "finance_lease_regulation",
    "finance_companies_law", "finance_companies_regulation",
    "insurance_control_law", "insurance_authority_statute",
    "credit_information_law", "credit_information_regulation",
    "payment_systems_law", "payment_systems_regulation",
    "banking_control_law", "banking_control_regulation",
    "capital_market_law", "sama_law", "bnpl_regulation",
    "electronic_transactions_law", "electronic_transactions_regulation",
    "real_estate_brokerage_law", "real_estate_brokerage_regulation",
    "accredited_valuers_law", "contractors_classification_law",
    "offplan_sale_law", "offplan_sale_implementing_regulation",
    "real_estate_contributions_law",
    "real_estate_contributions_implementing_regulation",
    "real_estate_finance_law", "real_estate_finance_implementing_regulation",
    "real_estate_mortgage_law", "real_estate_units_law",
    "real_estate_units_implementing_regulation",
    "investment_law", "investment_implementing_regulation",
    "mining_investment_law", "mining_investment_implementing_regulation",
    "privatization_law", "privatization_regulation",
    "gtpl_law", "gtpl_implementing_regulation",
    "engineering_practice_law", "engineering_practice_regulation",
    "accounting_auditing_law", "accounting_auditing_regulation",
    "debt_collection_regulation", "pharmaceutical_establishments_law",
    "product_safety_law", "standards_quality_law",
    "standards_quality_regulation", "telecommunications_law",
    "telecommunications_regulation", "audiovisual_media_law",
    "customs_law", "customs_regulation", "vat_law", "vat_regulation",
    "income_tax_law", "income_tax_regulation", "zakat_law", "rett_law",
    "rett_regulation", "state_revenue_law", "state_revenue_regulation",
]

SUBSTANTIVE = PARA_3 + PARA_4 + PARA_5 + PARA_6
NARROW = PROCEDURE + SUBSTANTIVE + PARA_7_NARROW
BROAD = PROCEDURE + SUBSTANTIVE + PARA_7_BROAD


def coverage(sizes, cited, keep):
    """(instruments, articles, articles cited, instruments cited) over a set."""
    keep = [t for t in keep if t in sizes]
    arts = sum(sizes[t] for t in keep)
    hit = sum(len(cited.get(t, {})) for t in keep)
    insts = sum(1 for t in keep if cited.get(t))
    return len(keep), arts, hit, insts


def main():
    d = json.loads(ARTICLES.read_text(encoding="utf-8"))
    sizes, cited = d["instrument_sizes"], d["by_instrument"]
    everything = list(sizes)
    applied = [t for t in sizes if cited.get(t)]

    unknown = sorted(set(NARROW + BROAD) - set(sizes))
    if unknown:
        print(f"note: {len(unknown)} scope entries carry no article records "
              f"and are skipped: {', '.join(unknown)}\n")

    rows = [
        ("the whole registry", everything),
        ("art. 16 scope, broad", BROAD),
        ("art. 16 scope, narrow", NARROW),
        ("instruments ever cited", applied),
    ]
    print(f"{'denominator':<26}{'instr':>7}{'articles':>10}{'cited':>8}"
          f"{'share':>8}{'instr cited':>13}")
    out = {}
    for label, keep in rows:
        n, arts, hit, insts = coverage(sizes, cited, keep)
        print(f"{label:<26}{n:>7,}{arts:>10,}{hit:>8,}"
              f"{hit/arts:>8.1%}{insts:>7,}/{n:<5}")
        out[label] = {"instruments": n, "articles": arts, "articles_cited": hit,
                      "share": hit / arts, "instruments_cited": insts}

    print("\nand inside single instruments, at the top of the distribution:")
    for t in ("commercial_courts_law", "evidence_law", "companies_law",
              "civil_transactions_law", "bankruptcy_law"):
        if t in sizes:
            print(f"  {t:<44}{len(cited.get(t, {})):>5,} of {sizes[t]:>5,}"
                  f"{len(cited.get(t, {}))/sizes[t]:>8.0%}")
            out.setdefault("instruments", {})[t] = {
                "articles": sizes[t], "cited": len(cited.get(t, {}))}

    (HERE / "restricted_denominator_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote restricted_denominator_results.json")


if __name__ == "__main__":
    main()
