#!/usr/bin/env python3
"""What is pressing on Saudi law now, and where AI would land if it arrived.

This is the forward half of the observatory. It holds no retrospective
analysis. Three kinds of statement live here and are never mixed:

    OBSERVED     measured in this corpus, or quoted from an enacted text this
                 repository holds
    EXPECTED     a consequence that follows from an OBSERVED fact plus a
                 stated legal or institutional mechanism
    SPECULATIVE  a possibility with neither

Every AI legal anchor below is quoted from an official Arabic text held in
this repository, with its instrument and article. Nothing is asserted to
apply. The question is only where the current system would have to absorb a
problem, not how it would resolve one, and nothing here is legal advice.

    python3 futures.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

OUT = HERE / "futures_results.json"
PRESSURE = HERE / "legal_pressure_map.json"
AIMAP = HERE / "ai_law_map.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
RECORDED_AT = "2026-08-31"

# --------------------------------------------------------------- PART 3
# A bounded CURRENT official-signal pass. Timestamped when it became known to
# the repository, not when it happened. Official sources only; secondary
# material was used for discovery and is not cited as authority.
CURRENT_SIGNALS = [
    {"signal_id": "CUR-2026-001",
     "title": "2026 designated the Year of Artificial Intelligence; SDAIA "
              "issues guidelines to unify national effort",
     "date": "2026-03", "domain": "AI governance",
     "institution": "SDAIA / Council of Ministers",
     "source": "https://www.spa.gov.sa/en/N2546742",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NOW",
     "affected_statutes": [],
     "observable_evidence": "an official state announcement; no corpus "
                            "observable follows from it directly",
     "possible_legal_consequence": "increased institutional AI adoption "
                                   "across government, including justice "
                                   "bodies",
     "consequence_status": "EXPECTED",
     "confidence": "HIGH_ON_THE_EVENT_NONE_ON_THE_CONSEQUENCE"},
    {"signal_id": "CUR-2026-002",
     "title": "SDAIA opens public consultation on a draft Responsible AI "
              "policy via the Istitlaa platform",
     "date": "2026-04", "domain": "AI governance",
     "institution": "SDAIA",
     "source": "https://www.spa.gov.sa/en/N2551533",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NEAR",
     "affected_statutes": [],
     "observable_evidence": "a named draft instrument under official "
                            "consultation",
     "possible_legal_consequence": "a binding or advisory AI policy "
                                   "instrument; if binding and breached, a "
                                   "regulatory rather than commercial forum "
                                   "would see it first",
     "consequence_status": "EXPECTED",
     "confidence": "HIGH_ON_THE_CONSULTATION"},
    {"signal_id": "CUR-2026-003",
     "title": "SDAIA issues rules governing personal data protection "
              "licensing and accreditation",
     "date": "2026", "domain": "data protection",
     "institution": "SDAIA",
     "source": "https://spa.gov.sa/en/N2517131",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NOW",
     "affected_statutes": ["pdpl_law"],
     "observable_evidence": "a licensing regime around the Personal Data "
                            "Protection Law",
     "possible_legal_consequence": "a compliance market and an enforcement "
                                   "channel; disputes would surface in a "
                                   "regulatory forum before a commercial one",
     "consequence_status": "EXPECTED", "confidence": "MEDIUM"},
    {"signal_id": "CUR-2026-004",
     "title": "Personal Data Protection Law committees to impose penalties on "
              "confirmed violations",
     "date": "2026", "domain": "data protection",
     "institution": "SDAIA",
     "source": "https://spa.gov.sa/en/N2489505",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NOW",
     "affected_statutes": ["pdpl_law"],
     "observable_evidence": "an operating penalty mechanism",
     "possible_legal_consequence": "the first data-protection disputes with a "
                                   "decided record; NOT in this corpus, whose "
                                   "forum is commercial adjudication",
     "consequence_status": "EXPECTED", "confidence": "MEDIUM"},
    {"signal_id": "CUR-2026-005",
     "title": "Law permitting non-Saudi ownership of real estate enters into "
              "force 22 January 2026",
     "date": "2026-01-22", "domain": "real estate / commercial",
     "institution": "REGA",
     "source": "https://spa.gov.sa/en/N2496274",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NEAR",
     "affected_statutes": [],
     "observable_evidence": "an instrument in force with a stated date",
     "possible_legal_consequence": "new transaction volume, and eventually "
                                   "new dispute families; whether any of it "
                                   "reaches published commercial adjudication "
                                   "is unknown",
     "consequence_status": "EXPECTED", "confidence": "MEDIUM"},
    {"signal_id": "CUR-2026-006",
     "title": "Labour Law amendments: 38 articles revised, 7 omitted, 2 added",
     "date": "2025", "domain": "labour",
     "institution": "Ministry of Human Resources and Social Development",
     "source": "https://www.hrsd.gov.sa/en/media-center/news/060720242",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NOW",
     "affected_statutes": ["labor_law"],
     "observable_evidence": "an amendment package in force; the Labour Law is "
                            "cited only 12 times in this corpus, so its "
                            "visibility here is minimal",
     "possible_legal_consequence": "labour disputes are not the commercial "
                                   "forum's docket; observable uptake here is "
                                   "unlikely",
     "consequence_status": "EXPECTED", "confidence": "MEDIUM"},
    {"signal_id": "CUR-2026-007",
     "title": "New Enforcement Law welcomed by the Minister of Justice",
     "date": "2026-04-15", "domain": "enforcement",
     "institution": "Ministry of Justice",
     "source": "https://www.spa.gov.sa/en/N2560642",
     "source_type": "S1_OFFICIAL_STATE_AGENCY",
     "status": "OBSERVED", "horizon": "NEAR",
     "affected_statutes": ["enforcement_law"],
     "observable_evidence": "already carried as LSIG-0004 in the legal signal "
                            "registry",
     "possible_legal_consequence": "enforcement output is not published as "
                                   "reasoned judgments, so this corpus cannot "
                                   "observe its uptake",
     "consequence_status": "OBSERVED_LIMIT", "confidence": "HIGH"},
]

# --------------------------------------------------------------- PART 7
# AI -> CURRENT LEGAL ANCHOR MAP. Every quote is verbatim from an official
# Arabic text held in this repository. The anchor says where the system would
# have to absorb a problem; it does not say how the problem resolves.
ANCHORS = [
    {"anchor_id": "ANCH-EVID-PROC-23",
     "instrument": "الأدلة الإجرائية لنظام الإثبات",
     "instrument_key": "evidence_procedural_manuals",
     "article": "المادة الثالثة والعشرون",
     "quote_ar": "يجوز الاستعانة بالتقنيات الحديثة في إجراءات الإثبات، بما في "
                 "ذلك الذكاء الاصطناعي، ويُستغنى عن أي إجراء تحققت غايته "
                 "باستخدام هذه التقنيات.",
     "class": "EXPLICIT_RULE",
     "what_it_anchors": "AI as a TOOL OF THE EVIDENTIARY PROCESS",
     "what_it_does_not_anchor": "AI as a source of liability, as an author, "
                                "or as a subject of a claim"},
    {"anchor_id": "ANCH-CCL-REG-24",
     "instrument": "اللائحة التنفيذية لنظام المحاكم التجارية",
     "instrument_key": "commercial_courts_implementing_regulation",
     "article": "المادة الرابعة والعشرون",
     "quote_ar": "يجوز الاستفادة من تقنيات الذكاء الاصطناعي في الإجراءات "
                 "الإلكترونية، ويستغنى عن أي إجراء تحققت غايته باستخدام تلك "
                 "التقنية.",
     "class": "EXPLICIT_RULE",
     "what_it_anchors": "AI as a TOOL OF COMMERCIAL COURT PROCEDURE, in the "
                        "instrument governing the forum this corpus observes",
     "what_it_does_not_anchor": "any substantive AI dispute"},
    {"anchor_id": "ANCH-ENF-PROV-16",
     "instrument": "لائحة مقدمي خدمات التنفيذ",
     "instrument_key": "enforcement_providers_regulation",
     "article": "المادة السادسة عشرة",
     "quote_ar": "وللوكالة استخدام تقنيات الذكاء الاصطناعي للقيام بخدمات "
                 "التنفيذ.",
     "class": "EXPLICIT_RULE",
     "what_it_anchors": "AI in the delivery of enforcement services",
     "what_it_does_not_anchor": "liability for an AI-delivered enforcement act"},
    {"anchor_id": "ANCH-TAWTHEEQ-REG-20",
     "instrument": "اللائحة التنفيذية لنظام التوثيق",
     "instrument_key": "tawtheeq_regulation",
     "article": "المادة العشرون",
     "quote_ar": "يستفاد من التقنيات الحديثة والذكاء الاصطناعي في إجراءات "
                 "التوثيق، ويستغنى عن أي إجراء تحققت غايته باستخدام تلك "
                 "التقنيات.",
     "class": "EXPLICIT_RULE",
     "what_it_anchors": "AI in notarisation procedure",
     "what_it_does_not_anchor": "the validity consequences of an AI-assisted "
                                "notarial act"},
    {"anchor_id": "ANCH-EVID-54",
     "instrument": "نظام الإثبات",
     "instrument_key": "evidence_law",
     "article": "المادة الرابعة والخمسون",
     "quote_ar": "يشمل الدليل الرقمي الآتي: 1. السجل الرقمي. 2. المحرَّر "
                 "الرقمي. 3. التوقيع الرقمي. 4. المراسلات الرقمية بما فيها "
                 "البريد الرقمي. 5. وسائل الاتصال. 6. الوسائط الرقمية. 7. أي "
                 "دليل رقمي آخر.",
     "class": "GENERAL_RULE",
     "what_it_anchors": "the category into which AI-generated or "
                        "AI-manipulated material would arrive as EVIDENCE. "
                        "Item 7 is open-ended on its own terms.",
     "what_it_does_not_anchor": "authenticity of synthetic material, which the "
                                "text does not address in these words"},
    {"anchor_id": "ANCH-CCL-55",
     "instrument": "نظام المحاكم التجارية",
     "instrument_key": "commercial_courts_law",
     "article": "المادة الخامسة والخمسون",
     "quote_ar": "يجوز اعتبار الدليل الإلكتروني حجة في الإثبات، على أن تتضمن "
                 "اللائحة وسائل التحقق من الدليل الإلكتروني وإجراءات تقديمه.",
     "class": "GENERAL_RULE",
     "what_it_anchors": "admissibility of electronic evidence in the observed "
                        "forum, with verification delegated to the regulation",
     "what_it_does_not_anchor": "a verification standard for synthetic media"},
    {"anchor_id": "ANCH-SDAIA-ORG",
     "instrument": "الترتيبات التنظيمية للهيئة السعودية للبيانات والذكاء "
                   "الاصطناعي",
     "instrument_key": "sdaia_organizational_arrangements",
     "article": "البند ثالثاً",
     "quote_ar": "تكون الهيئة الجهة المختصة في المملكة بالبيانات (بما في ذلك "
                 "البيانات الضخمة) والذكاء الاصطناعي، والمرجع الوطني في كل ما "
                 "يتعلق بهما من تنظيم وتطوير وتعامل",
     "class": "EXPLICIT_RULE",
     "what_it_anchors": "the REGULATORY competence for AI, which is an "
                        "authority and not a court",
     "what_it_does_not_anchor": "any private-law claim"},
]


# ----------------------------------------------------------- PARTS 6 and 9
# EMERGING AI LAW MAP. Nothing here is claimed to be present in the corpus.
# The gap class answers only: how much of the problem could existing law
# already absorb? A missing AI-specific statute is NOT by itself a gap.
def issue(name, status, anchors, entry, first_signal, watch, gap, note=None):
    return {"issue_family": name, "CURRENT_STATUS": status,
            "RELEVANT_EXISTING_SAUDI_LAW": anchors,
            "LIKELY_LEGAL_ENTRY_POINT": entry,
            "FIRST_OBSERVABLE_SIGNAL": first_signal,
            "WATCH_CONDITION": watch, "GAP_CLASS": gap,
            "note": note}


AI_ISSUES = [
    issue("AI_GENERATED_EVIDENCE",
          "NOT_OBSERVED_IN_THIS_CORPUS",
          ["ANCH-EVID-54", "ANCH-CCL-55", "ANCH-EVID-PROC-23"],
          "the digital-evidence chapter of the Evidence Law and article 55 of "
          "the Commercial Courts Law, whose verification means are delegated "
          "to the implementing regulation",
          "a judgment in which a party disputes the authenticity of digital "
          "material on grounds of synthetic generation",
          "any court-voice citation of the digital-evidence articles "
          "co-occurring with a dispute over authenticity",
          "GENERAL_RULE",
          "the category exists and is open-ended; what the quoted text does "
          "not contain in these words is a standard for synthetic material"),
    issue("DEEPFAKE_SYNTHETIC_EVIDENCE",
          "NOT_OBSERVED_IN_THIS_CORPUS",
          ["ANCH-EVID-54", "ANCH-CCL-55"],
          "the same evidentiary route, plus forgery procedure "
          "(دعوى التزوير) which the Evidence Law carries as its own chapter",
          "a forgery claim whose subject is machine-generated material",
          "co-occurrence of forgery-procedure articles with digital-evidence "
          "articles in one judgment",
          "ANALOGICAL_ENTRY_POINT"),
    issue("AI_ASSISTED_CONTRACTING",
          "NOT_OBSERVED_IN_THIS_CORPUS",
          ["ANCH-CCL-55"],
          "the Civil Transactions Law's general contract formation rules, "
          "which this repository holds but which contain no AI-specific "
          "wording",
          "a dispute over consent or authority where one side's act was "
          "machine-generated",
          "a CTL contract-formation article rising sharply alongside "
          "electronic-evidence articles",
          "GENERAL_RULE"),
    issue("AI_MISREPRESENTATION",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "general civil liability and contractual good-faith rules",
          "a claim founded on a statement produced by a system rather than a "
          "person", "no specific marker; caught by the surprise ledger",
          "GENERAL_RULE"),
    issue("AI_PROFESSIONAL_NEGLIGENCE",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "professional regulation plus general liability. The Law Practice "
          "Law is in this corpus at low volume.",
          "a claim against a regulated professional whose work product was "
          "machine-generated",
          "law-practice articles co-occurring with a liability claim",
          "UNCLEAR"),
    issue("AUTOMATED_DECISION_SYSTEMS",
          "NOT_OBSERVED_IN_THIS_CORPUS",
          ["ANCH-SDAIA-ORG"],
          "regulatory supervision by SDAIA, and sector rules such as the "
          "credit-information regulation's treatment of a negative decision "
          "taken wholly or partly on recorded information",
          "an administrative or regulatory challenge, which is the "
          "administrative judiciary's forum and NOT this corpus",
          "NOT_OBSERVABLE_HERE: the forum is wrong",
          "PROCEDURAL_ONLY_ENTRY"),
    issue("ALGORITHMIC_DISCRIMINATION",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "labour and regulatory routes, neither of which is this corpus's "
          "docket", "a labour or regulatory complaint",
          "NOT_OBSERVABLE_HERE", "NO_OBVIOUS_ANCHOR"),
    issue("AI_EMPLOYMENT_DECISIONS",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "the Labour Law, recently amended, whose disputes go to labour "
          "courts", "a labour claim naming an automated process",
          "NOT_OBSERVABLE_HERE", "NO_OBVIOUS_ANCHOR"),
    issue("GENERATIVE_AI_IP",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "the Copyright Law, which appears in this corpus at low volume",
          "an authorship or infringement claim involving generated material",
          "copyright articles rising in the commercial forum",
          "UNCLEAR"),
    issue("DATA_AND_PRIVACY_INVOLVING_AI",
          "REGULATORY_ACTIVITY_OBSERVED_OUTSIDE_THIS_CORPUS",
          ["ANCH-SDAIA-ORG"],
          "the Personal Data Protection Law and its licensing and penalty "
          "machinery, which are regulatory rather than commercial",
          "a PDPL penalty decision, which this corpus does not carry",
          "NOT_OBSERVABLE_HERE; tracked through CUR-2026-003 and CUR-2026-004",
          "EXPLICIT_RULE",
          "explicit in its own domain, and that domain is not this forum"),
    issue("AI_PROCUREMENT",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "government tenders and procurement law; disputes go to the "
          "administrative judiciary",
          "a procurement challenge naming an AI system",
          "NOT_OBSERVABLE_HERE", "PROCEDURAL_ONLY_ENTRY"),
    issue("GOVERNMENT_AI_DECISIONS",
          "NOT_OBSERVED_IN_THIS_CORPUS", ["ANCH-SDAIA-ORG"],
          "administrative-law review, the Board of Grievances' forum",
          "an administrative claim", "NOT_OBSERVABLE_HERE",
          "PROCEDURAL_ONLY_ENTRY"),
    issue("AI_GENERATED_COMMERCIAL_ADVICE",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "general liability plus sector licensing", "a claim over reliance "
          "on machine-generated advice", "no specific marker",
          "UNCLEAR"),
    issue("AUTONOMOUS_SERVICE_FAILURE",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "contractual liability under the Civil Transactions Law",
          "a service-failure claim where performance was autonomous",
          "a CTL liability article rising with a technology counterparty",
          "GENERAL_RULE"),
    issue("LIABILITY_FOR_AI_AGENTS",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "agency and vicarious-liability concepts in the Civil Transactions "
          "Law", "a claim allocating responsibility for an autonomous act",
          "no specific marker; this is the family most likely to need new law",
          "UNCLEAR",
          "the honest answer is that the quoted texts this repository holds "
          "do not address it in these words, and that is a statement about "
          "the texts held, not a finding that Saudi law is silent"),
    issue("AI_GENERATED_CORPORATE_ACTS",
          "NOT_OBSERVED_IN_THIS_CORPUS", [],
          "the Companies Law's rules on organs, authority and resolutions",
          "a challenge to a corporate act taken by an automated process",
          "companies-law authority articles rising", "UNCLEAR"),
    issue("AI_USE_BY_REGULATED_PROFESSIONALS",
          "PROCEDURAL_PERMISSION_OBSERVED",
          ["ANCH-EVID-PROC-23", "ANCH-CCL-REG-24", "ANCH-TAWTHEEQ-REG-20",
           "ANCH-ENF-PROV-16"],
          "the procedural instruments already permit AI use; the question is "
          "what follows when the permitted use goes wrong",
          "a judgment in which an AI-assisted procedural step is challenged",
          "any court-voice citation of the four permission articles",
          "EXPLICIT_RULE",
          "the strongest anchor family, and it anchors PERMISSION rather than "
          "CONSEQUENCE"),
]


# --------------------------------------------------------------- PART 8
FIRST_CASE_CAPTURE = {
    "what": "FIRST-AI-CASE READINESS. The capture schema is defined BEFORE "
            "the first validated AI-material dispute appears, so the first "
            "one is recorded against a fixed template rather than described "
            "after the fact.",
    "trigger": "a judgment in this corpus in which an AI system is material "
               "to the dispute, not merely mentioned. Materiality is decided "
               "by the AI radar's existing L3 rule, which currently returns "
               "zero.",
    "capture_fields": [
        "date", "quarter", "city", "court_type", "domain",
        "ai_issue_family (from the emerging AI law map)",
        "party_legal_anchors (instrument, article)",
        "court_legal_anchors (instrument, article)",
        "evidence_law_involvement (which articles)",
        "civil_transactions_law_involvement",
        "non_statutory_authority_used",
        "new_doctrinal_source (identity not previously in the canon)",
        "new_statutory_interpretation (an article not previously court-cited)",
        "court_versus_bar_divergence",
        "traceability_of_the_authority_used",
        "authority_adjacent_formula_novelty",
        "was_the_existing_anchor_sufficient (OBSERVED_ADEQUATE / "
        "OBSERVED_STRAINED / UNRESOLVED)",
    ],
    "forbidden": [
        "inferring AI involvement from writing style",
        "treating a mention of AI as an AI-material dispute",
        "predicting the outcome of the case",
        "naming a judge, a party or a firm",
    ],
    "baseline_at_definition": "zero AI-material disputes in the observed "
                              "corpus. The schema is armed against a base "
                              "rate of zero, which is the point.",
}

# --------------------------------------------------------------- PART 10
AI_COMPONENTS = {
    "noSingleScore": "no AI readiness index is computed. A single number "
                     "would hide which component moved, and we do not yet "
                     "know which components matter.",
    "components": {
        "regulatory_pressure": {"state": "RISING", "evidence":
                                ["CUR-2026-001", "CUR-2026-002",
                                 "CUR-2026-003", "CUR-2026-004"],
                                "status": "OBSERVED"},
        "litigation_observability": {"state": "ZERO", "evidence":
                                     "no AI-material dispute in the corpus",
                                     "status": "OBSERVED"},
        "statutory_anchor_availability": {"state": "PROCEDURAL_ONLY",
                                          "evidence": "four explicit "
                                          "permission articles, no "
                                          "substantive liability rule in the "
                                          "texts held",
                                          "status": "OBSERVED"},
        "evidence_complexity": {"state": "OPEN_CATEGORY", "evidence":
                                "ANCH-EVID-54 item 7 and ANCH-CCL-55's "
                                "delegation of verification means",
                                "status": "OBSERVED"},
        "liability_ambiguity": {"state": "UNRESOLVED_IN_TEXTS_HELD",
                                "evidence": "no liability-allocation wording "
                                "for autonomous acts in the instruments this "
                                "repository holds",
                                "status": "OBSERVED_LIMIT"},
        "institutional_ai_adoption": {"state": "VERIFIED_BUT_NOT_LINKABLE",
                                      "evidence": "seven adoption events, "
                                      "none at L3_WORKFLOW_MATCH",
                                      "status": "OBSERVED"},
        "court_data_observability": {"state": "LAGGING",
                                     "evidence": "the latest mature quarter "
                                     "is roughly two years behind the session "
                                     "clock and no publication date exists "
                                     "per judgment",
                                     "status": "OBSERVED"},
    },
}

# ------------------------------------------------------------ PARTS 5, 16
BRANCHES = [
    {"id": "F0", "name": "CURRENT_CONDITIONS_CONTINUE",
     "expect_first": "nothing outside the frozen detector bounds",
     "metrics": ["all armed detector series"],
     "falsifier": "any REGIME_CANDIDATE or confirmed detector shift",
     "data_needed": "none; this is the default and it wins by default"},
    {"id": "F1", "name": "MAJOR_NEW_LAW_OR_REGULATORY_PACKAGE",
     "expect_first": "court statutory visibility of the new instrument in the "
                     "first mature quarter at or after its commencement",
     "metrics": ["instrument court share", "top-100 entry", "article HHI"],
     "falsifier": "commencement passes and the instrument stays absent for "
                  "three mature quarters",
     "data_needed": "a verified commencement date, which the legal clock "
                    "layer now produces"},
    {"id": "F2", "name": "VERIFIED_BAR_LEGAL_AI_ADOPTION",
     "expect_first": "party-side long-tail statutory use and party source "
                     "diversity",
     "metrics": ["party article breadth", "party source diversity",
                 "court/bar top-50 overlap", "formula concentration in the "
                 "bar's voice"],
     "falsifier": "verified bar adoption with party-side breadth inside its "
                  "historical bounds while the court's moves",
     "data_needed": "an adoption event at L3_WORKFLOW_MATCH, of which there "
                    "are currently none"},
    {"id": "F3", "name": "VERIFIED_BENCH_JUDICIAL_RESEARCH_AI",
     "expect_first": "court source diversity and traceability",
     "metrics": ["named-source share", "source HHI", "long-tail doctrine",
                 "companion structure", "formula concentration"],
     "falsifier": "verified bench adoption and only statutory ranking moves",
     "data_needed": "the same linkability, in the observed forum"},
    {"id": "F4", "name": "AI_BECOMES_A_MATERIAL_SUBJECT_OF_LITIGATION",
     "expect_first": "the first-case capture schema fires",
     "metrics": ["AI radar L3 count", "digital-evidence article visibility"],
     "falsifier": "none needed; this branch is observed or it is not",
     "data_needed": "one qualifying judgment"},
    {"id": "F5", "name": "PUBLICATION_OR_DATA_ACCESS_CHANGE",
     "expect_first": "the publication and docket families, which are already "
                     "the least stationary part of the corpus",
     "metrics": ["judgments per quarter", "median reasons length",
                 "claim-family mix"],
     "falsifier": "an access change with the publication family inside its "
                  "bounds",
     "data_needed": "none; this branch is the one the corpus is best able to "
                    "see, and least able to distinguish from legal change"},
    {"id": "F6", "name": "MAJOR_INSTITUTIONAL_RESTRUCTURING",
     "expect_first": "jurisdiction-sensitive docket composition",
     "metrics": ["claim-family mix", "court-type mix", "instrument mix"],
     "falsifier": "restructuring with no docket movement",
     "data_needed": "an official restructuring event, of which the bounded "
                    "lookup found none in the observed window"},
]

HYPOTHESES = [
    {"id": "H1", "name": "HOMOGENISATION",
     "claim": "AI concentrates authorities and formulations",
     "metrics": ["source HHI", "top-10 formula concentration",
                 "article HHI"],
     "falsifier": "verified adoption with concentration flat or falling",
     "required_linkability": "L3_WORKFLOW_MATCH"},
    {"id": "H2", "name": "DISCOVERY",
     "claim": "AI expands the long tail",
     "metrics": ["distinct sources", "distinct articles", "rare-article share"],
     "falsifier": "verified adoption with the long tail flat or shrinking",
     "required_linkability": "L3_WORKFLOW_MATCH"},
    {"id": "H3", "name": "TRACEABILITY",
     "claim": "AI increases named and retrievable authority",
     "metrics": ["named-identity share of court non-statutory mentions"],
     "falsifier": "verified adoption with the named share flat or falling",
     "required_linkability": "L3_WORKFLOW_MATCH"},
    {"id": "H4", "name": "GENERIC_DRAFTING",
     "claim": "AI increases generic legal language",
     "metrics": ["GENERIC_REASONING formula class share",
                 "generic-identity share"],
     "falsifier": "verified adoption with the generic share flat or falling",
     "required_linkability": "L3_WORKFLOW_MATCH"},
    {"id": "H5", "name": "NO_MATERIAL_CHANGE",
     "claim": "nothing measurable moves",
     "metrics": ["all of the above"],
     "falsifier": "any confirmed shift in an expected layer",
     "required_linkability": "L3_WORKFLOW_MATCH",
     "note": "this is the default and it wins by default"},
    {"id": "H6", "name": "CHANNEL_DEPENDENT",
     "claim": "bar AI and bench AI produce different changes",
     "metrics": ["every metric above, split by voice"],
     "falsifier": "both channels adopted and the voice split shows the same "
                  "movement",
     "required_linkability": "two separately verified events, one per channel"},
]


# --------------------------------------------------------- PARTS 20 and 21
def frontier():
    """PART 20. Where future law-in-action is most likely to change."""
    ck = {c["instrument"]: c for c in J("legal_clock_registry.json")["instruments"]}
    rows = []
    for s in CURRENT_SIGNALS:
        state = ("UNDER_OFFICIAL_CONSULTATION" if "consultation" in s["title"]
                 else "RECENTLY_EFFECTIVE" if "force" in s["title"]
                 or "amendments" in s["title"] else "ANNOUNCED")
        rows.append({
            "item": s["title"], "state": state, "date": s["date"],
            "domain": s["domain"], "source": s["source"],
            "relevanceToObservedCommercialAdjudication":
                "HIGH" if s["affected_statutes"] and any(
                    a in ck and ck[a]["courtCitations"] >= 150
                    for a in s["affected_statutes"]) else "LOW",
            "aiRelevance": "HIGH" if s["domain"].startswith("AI")
                           or s["domain"] == "data protection" else "LOW",
            "dataObservability": ("OBSERVABLE_IN_THIS_CORPUS"
                                  if s["affected_statutes"] else
                                  "NOT_OBSERVABLE_IN_THIS_CORPUS"),
            "signal_id": s["signal_id"],
        })
    order = {"HIGH": 0, "LOW": 1}
    rows.sort(key=lambda r: (order[r["relevanceToObservedCommercialAdjudication"]],
                             order[r["aiRelevance"]], r["item"]))
    return {
        "states": ["RECENTLY_EFFECTIVE", "COMING_INTO_FORCE",
                   "UNDER_OFFICIAL_CONSULTATION", "ANNOUNCED",
                   "IMPLEMENTATION_PENDING"],
        "items": rows,
        "rankedBy": ["relevance to observed commercial adjudication",
                     "AI relevance", "data observability"],
        "notForecast": "the frontier says where change is most likely to "
                       "originate. It does not forecast any item.",
        "honestSummary": "the two most active current frontiers -- AI "
                         "governance and data protection -- are the two least "
                         "observable in this corpus, because their forum is "
                         "regulatory rather than commercial adjudication.",
    }


DISPUTE_FRONTIER = [
    {"family": "AI evidence authenticity", "current_evidence":
     "explicit digital-evidence categories with verification delegated to a "
     "regulation; zero disputes observed",
     "anchors": ["ANCH-EVID-54", "ANCH-CCL-55"],
     "first_signal": "an authenticity challenge to digital material",
     "watch": "digital-evidence articles rising in the court's voice",
     "status": "EXPECTED"},
    {"family": "Automated contracting", "current_evidence":
     "the Civil Transactions Law is newly operational and rising; no "
     "AI-specific wording",
     "anchors": [], "first_signal": "a consent or authority dispute over a "
     "machine-generated act",
     "watch": "CTL formation articles rising with electronic-evidence "
              "articles", "status": "SPECULATIVE"},
    {"family": "Data liability", "current_evidence":
     "an operating PDPL penalty mechanism outside this corpus",
     "anchors": ["ANCH-SDAIA-ORG"], "first_signal": "a PDPL penalty decision",
     "watch": "NOT_OBSERVABLE_HERE", "status": "EXPECTED"},
    {"family": "AI professional duty", "current_evidence":
     "four articles permitting professional AI use, none addressing "
     "consequence",
     "anchors": ["ANCH-EVID-PROC-23", "ANCH-CCL-REG-24",
                 "ANCH-TAWTHEEQ-REG-20", "ANCH-ENF-PROV-16"],
     "first_signal": "a challenge to an AI-assisted procedural step",
     "watch": "court-voice citation of any permission article",
     "status": "EXPECTED"},
    {"family": "Algorithmic public decisions", "current_evidence":
     "SDAIA regulatory competence; administrative forum",
     "anchors": ["ANCH-SDAIA-ORG"], "first_signal": "an administrative claim",
     "watch": "NOT_OBSERVABLE_HERE", "status": "SPECULATIVE"},
    {"family": "Platform and intermediary liability", "current_evidence":
     "none in this corpus", "anchors": [],
     "first_signal": "a claim against an intermediary for automated conduct",
     "watch": "e-commerce or telecommunications articles rising",
     "status": "SPECULATIVE"},
    {"family": "Cross-border data and AI service contracts",
     "current_evidence": "PDPL licensing and accreditation rules",
     "anchors": ["ANCH-SDAIA-ORG"],
     "first_signal": "a commercial claim naming a data-transfer obligation",
     "watch": "PDPL articles appearing in the commercial forum at all",
     "status": "SPECULATIVE"},
]

# --------------------------------------------------------- PARTS 22 and 23
SURPRISE_READINESS = {
    "what": "UNKNOWN-UNKNOWN WATCH. The project must be able to discover a "
            "future it did not name.",
    "notAClassifier": True,
    "rule": "any recurring legal concept, statutory instrument or "
            "non-statutory identity that is NOT in a known family and that "
            "crosses the support threshold used elsewhere in this repository "
            "-- observed in at least ten judgments, in at least two mature "
            "quarters -- opens a SURPRISE_LEDGER entry.",
    "appliesTo": ["instrument track ids not previously court-cited",
                  "canonical non-statutory identities outside the 28-identity "
                  "canon, which currently surface as RAW strings",
                  "authority-adjacent formula classes not in the mechanical "
                  "taxonomy"],
    "discipline": "the entry is opened FIRST and the explanation is searched "
                  "for afterwards. An entry with no explanation stays "
                  "UNKNOWN, and resemblance to an expectation is never "
                  "evidence.",
    "ledger": "SURPRISE_LEDGER.json",
}

LIVE_CHAIN = {
    "what": "LIVE LEGAL CHANGE CHAIN. From this commit onward, an event "
            "captured PROSPECTIVELY records milestones as they occur.",
    "milestones": ["SIGNAL", "FIRST_OBSERVABLE_USE", "PARTY_USE", "COURT_USE",
                   "DOCTRINAL_COMPANION", "OPERATIONAL_CORE",
                   "RETRIEVAL_IMPACT"],
    "orderingIsNotRequired": "the milestones are stored, not sequenced. The "
                             "transition programme already showed that an "
                             "apparent ordering can be an artefact of when "
                             "the clock was started.",
    "captureClass": "computed from recorded_at against the event's "
                    "observable_from, never declared. An event recorded after "
                    "its observable_from is BACKFILLED and can never be "
                    "reported as foresight.",
    "currentProspectiveEntries": 0,
    "why": "every event this repository holds was recorded after the fact. "
           "The chain starts empty on purpose, and that is the point of "
           "defining it now.",
}


def pressure_map(nc):
    """PART 2 and PART 4. What is exerting pressure, with horizons."""
    mom = nc["part11_14_momentum"]
    rows = list(CURRENT_SIGNALS)
    # corpus-internal pressure: things measured, not announced
    code = mom["part12_codeMomentum"]
    for r in code["rising"][:6] + code["newlyVisible"][:4]:
        rows.append({
            "signal_id": f"CUR-CORPUS-{r['key']}",
            "title": f"{r['key']} {r['class'].lower().replace('_', ' ')} in "
                     "the court's voice",
            "date": nc["part1_windows"]["CURRENT_MATURE_PERIOD"][0],
            "domain": "commercial adjudication",
            "institution": "commercial courts",
            "source": "measured in this corpus",
            "source_type": "S1_OWN_MEASUREMENT",
            "status": "OBSERVED", "horizon": "NOW",
            "affected_statutes": [r["key"]],
            "observable_evidence": f"court citations {r['before']} -> "
                                   f"{r['now']} between adjacent "
                                   "four-quarter windows",
            "possible_legal_consequence": "further visibility, doctrinal "
                                          "companion formation, or neither",
            "consequence_status": "EXPECTED",
            "confidence": "MEASURED_ON_TWO_WINDOWS_ONLY"})
    art = mom["part11_articleMomentum"]
    for r in art["newlyVisible"][:6]:
        k = r["key"]
        rows.append({
            "signal_id": f"CUR-ART-{k[0]}-{k[1]}",
            "title": f"article {k[1]} of {k[0]} newly visible in the court's "
                     "voice",
            "date": nc["part1_windows"]["CURRENT_MATURE_PERIOD"][0],
            "domain": "commercial adjudication",
            "institution": "commercial courts",
            "source": "measured in this corpus",
            "source_type": "S1_OWN_MEASUREMENT",
            "status": "OBSERVED", "horizon": "NOW",
            "affected_statutes": [k[0]],
            "observable_evidence": f"{r['now']} court citations in the "
                                   "current window, none in the preceding one",
            "possible_legal_consequence": "entry into the operational core",
            "consequence_status": "EXPECTED",
            "confidence": "MEASURED_ON_TWO_WINDOWS_ONLY"})
    counts = Counter(r["status"] for r in rows)
    hor = Counter(r["horizon"] for r in rows)
    return {
        "what": "LEGAL PRESSURE MAP. What is exerting pressure on the current "
                "system. Not a prediction.",
        "statusClasses": {
            "OBSERVED": "measured in this corpus or quoted from an enacted "
                        "text this repository holds",
            "EXPECTED": "follows from an OBSERVED fact plus a stated legal or "
                        "institutional mechanism",
            "SPECULATIVE": "neither"},
        "neverMixed": True,
        "horizons": {"NOW": "0-6 months", "NEAR": "6-12 months",
                     "MID": "12-24 months", "LONG": "24+ months",
                     "aHorizonIsNotAForecast": "it says when an observable "
                                               "consequence could plausibly "
                                               "emerge, with no probability "
                                               "attached"},
        "byStatus": dict(sorted(counts.items())),
        "byHorizon": dict(sorted(hor.items())),
        "signals": rows,
        "recorded_at": RECORDED_AT,
    }


def main():
    nc = J("nowcast_results.json")
    pm = pressure_map(nc)
    fr = frontier()
    gap = Counter(i["GAP_CLASS"] for i in AI_ISSUES)
    res = {
        "what": "SAUDI LEGAL FORESIGHT. Current pressure, the legal frontier, "
                "and where AI would land if it arrived in the observed forum.",
        "recorded_at": RECORDED_AT,
        "threeKindsOfStatement": pm["statusClasses"],
        "part2_4_pressureMap": {"file": PRESSURE.name,
                                "signals": len(pm["signals"]),
                                "byStatus": pm["byStatus"],
                                "byHorizon": pm["byHorizon"]},
        "part3_currentOfficialSignalPass": {
            "signals": len(CURRENT_SIGNALS),
            "sourcesUsed": sorted({s["source_type"] for s in CURRENT_SIGNALS}),
            "boundedBy": "official state sources only; stopped once a "
                         "high-value current set existed. No news archive, no "
                         "historical completion.",
            "items": CURRENT_SIGNALS},
        "part5_16_branches": BRANCHES,
        "part6_9_aiLawMap": {"file": AIMAP.name,
                             "issueFamilies": len(AI_ISSUES),
                             "gapClasses": dict(sorted(gap.items()))},
        "part7_anchorMap": {"anchors": len(ANCHORS),
                            "explicitRuleAnchors": sum(
                                1 for a in ANCHORS
                                if a["class"] == "EXPLICIT_RULE"),
                            "allQuotedFromLocalOfficialTexts": True},
        "part8_firstCaseReadiness": FIRST_CASE_CAPTURE,
        "part10_aiComponents": AI_COMPONENTS,
        "part17_hypothesisTournament": {
            "hypotheses": HYPOTHESES,
            "noWinnerToday": True,
            "allRequire": "an adoption event at L3_WORKFLOW_MATCH, of which "
                          "the registry holds none"},
        "part20_frontier": fr,
        "part21_disputeFrontier": {
            "families": DISPUTE_FRONTIER,
            "max": 10, "listed": len(DISPUTE_FRONTIER),
            "notGuaranteed": "these are candidate families with stated "
                             "evidence, not predicted disputes."},
        "part22_surpriseReadiness": SURPRISE_READINESS,
        "part23_liveChain": LIVE_CHAIN,
        "part16_aiBaseline": {
            "aiMaterialDisputesInCorpus": 0,
            "source": "ai_radar_results.json, L3 rule",
            "explicitAIProvisionsFoundInHeldTexts": len(
                [a for a in ANCHORS if a["class"] == "EXPLICIT_RULE"]),
            "reading": "Saudi law already permits AI in the procedures of the "
                       "very forum this corpus observes, while the corpus "
                       "contains no dispute in which AI is material. "
                       "Permission is present; consequence is untested.",
        },
        "standingLimitations": [
            "the forum. This corpus is published Ministry of Justice "
            "commercial adjudication. The two most active current AI "
            "frontiers -- AI governance and data protection -- are "
            "regulatory, so their first disputes will not appear here.",
            "the observation lag. The latest mature quarter is roughly two "
            "years behind the session clock.",
            "nothing in the anchor map asserts that an instrument applies. It "
            "records where the system would have to absorb a problem, quoted "
            "from the text.",
            "no probability is attached to any branch, horizon or hypothesis.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    PRESSURE.write_text(json.dumps(pm, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    AIMAP.write_text(json.dumps({
        "what": "EMERGING AI LAW MAP and AI -> CURRENT LEGAL ANCHOR MAP.",
        "recorded_at": RECORDED_AT,
        "notLegalAdvice": True,
        "noOutcomePrediction": True,
        "gapClassMeaning": {
            "EXPLICIT_RULE": "the text addresses it in its own words",
            "GENERAL_RULE": "a general category the problem would arrive in",
            "ANALOGICAL_ENTRY_POINT": "a route by analogy to an existing "
                                      "procedure",
            "PROCEDURAL_ONLY_ENTRY": "a forum and a procedure, no substantive "
                                     "rule",
            "UNCLEAR": "the texts held do not settle it",
            "NO_OBVIOUS_ANCHOR": "no route found in the texts held"},
        "aMissingAIStatuteIsNotAGap": "the question is not whether Saudi "
                                      "Arabia needs an AI law. It is how much "
                                      "of the emerging problem existing law "
                                      "can already absorb.",
        "anchors": ANCHORS,
        "issueFamilies": AI_ISSUES,
        "firstCaseReadiness": FIRST_CASE_CAPTURE,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"pressure signals {len(pm['signals'])} {pm['byStatus']} "
          f"{pm['byHorizon']}")
    print(f"  AI issue families {len(AI_ISSUES)}; gap classes {dict(gap)}")
    print(f"  anchors {len(ANCHORS)}, explicit {res['part7_anchorMap']['explicitRuleAnchors']}")
    print(f"  frontier items {len(fr['items'])}")
    print(f"-> {OUT.name}, {PRESSURE.name}, {AIMAP.name}")


if __name__ == "__main__":
    main()
