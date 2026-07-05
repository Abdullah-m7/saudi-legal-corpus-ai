#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the sovereign legal corpus factory FOUNDATION (docs, schemas, profile, config, seed).

Multilingual, LLM-ready, official-source-based Saudi legal corpus for AI. Read-only and idempotent.
Confirms the foundation artifacts exist and parse, that the schemas carry the required top-level
structure, and that the law profile reflects current repository facts under the repository
legal-review model: the official Arabic source governs; the repository owner has a legal background
(bachelor_of_law) and runs active repository review (repository_owner_review_active); external legal
review is optional for enterprise/official adoption and NOT required for repository use; no false
Chinese official/binding/governing/full-281/trilingual claim and no official government
publication/translation/adoption claim. Also verifies the example P0-005 QA batch config matches the
existing P0-005 QA scope/babs, that the terminology bank uses the repository-owner review model
(seed_repository_owner_review_active / seed_pending_repository_owner_review), that no stale
human-legal-review framing remains in the foundation files, and that no P1/P2/P3 batch dirs and no
full Chinese 281 layer / trilingual alignment exist. Touches no existing corpus data.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCTRINE = os.path.join(ROOT, "docs", "SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md")
ARCH = os.path.join(ROOT, "docs", "LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md")
SCHEMA_DIR = os.path.join(ROOT, "schemas", "legal_corpus_factory")
LAW_PROFILE_SCHEMA = os.path.join(SCHEMA_DIR, "law_profile.schema.json")
BATCH_SCHEMA = os.path.join(SCHEMA_DIR, "batch_config.schema.json")
PROV_SCHEMA = os.path.join(SCHEMA_DIR, "provenance_passport.schema.json")
PROFILE = os.path.join(ROOT, "data", "legal_corpus_factory", "law_profiles",
                       "sa_companies_law_m132_1443.profile.json")
BATCH = os.path.join(ROOT, "data", "legal_corpus_factory", "batch_configs",
                     "sa_companies_law_m132_1443_p0_005_qa.batch.json")
TERMS = os.path.join(ROOT, "data", "legal_corpus_factory", "terminology",
                     "sa_companies_law_core_terms_ar_en_zh_seed.json")
P0_005_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_005_qa.json")

ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
ENREF = os.path.join(ROOT, "data", "english_reference",
                     "companies_law_m132_1443_en_reference_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
OCRQ = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")

BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _rc(p):
    return len(_read(p)["records"])


def main() -> int:
    problems = []

    # 1. existence
    files = {
        "doctrine": DOCTRINE, "architecture": ARCH, "law_profile_schema": LAW_PROFILE_SCHEMA,
        "batch_config_schema": BATCH_SCHEMA, "provenance_schema": PROV_SCHEMA,
        "law_profile": PROFILE, "batch_config": BATCH, "terminology_seed": TERMS,
    }
    for label, p in files.items():
        if not os.path.exists(p):
            problems.append("missing %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    # 2. JSON parses
    docs = {}
    for label, p in (("law_profile_schema", LAW_PROFILE_SCHEMA), ("batch_config_schema", BATCH_SCHEMA),
                     ("provenance_schema", PROV_SCHEMA), ("law_profile", PROFILE),
                     ("batch_config", BATCH), ("terminology_seed", TERMS)):
        try:
            docs[label] = _read(p)
        except (ValueError, OSError) as e:
            problems.append("%s is not valid JSON: %s" % (label, e))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    # 3. schema top-level structure
    for label, req_props in (
        ("law_profile_schema", ("law_id", "law_name_ar", "law_name_en", "jurisdiction",
                                "governing_language", "reference_languages", "article_count",
                                "official_source_status", "source_files", "legal_hierarchy",
                                "source_basis", "repository_legal_review", "external_legal_review",
                                "official_status", "release_policy", "created_for_repository",
                                "notes")),
        ("batch_config_schema", ("law_id", "batch_id", "stage", "priority", "remediation_track",
                                 "scope_articles", "expected_babs", "expected_bab_distribution",
                                 "source_status_before", "remediation_action", "translation_basis",
                                 "english_guidance_role", "qa_required", "source_basis",
                                 "repository_legal_review", "external_legal_review", "official_status",
                                 "prohibited_claims", "protected_layers", "validation_policy")),
        ("provenance_schema", ("law_id", "article_number", "article_title_ar", "bab", "source_language",
                               "governing_text_source", "governing_text_hash_sha256", "reference_layers",
                               "extraction_status", "remediation_status", "qa_status",
                               "source_basis", "repository_legal_review_status",
                               "external_legal_review_status", "official_status",
                               "risk_lane", "risk_reasons",
                               "last_batch_id", "last_changed_commit", "notes")),
    ):
        sc = docs[label]
        if sc.get("type") != "object":
            problems.append("%s must be a JSON-schema object" % label)
        props = sc.get("properties", {})
        for rp in req_props:
            if rp not in props:
                problems.append("%s missing property %s" % (label, rp))
        for rp in req_props:
            if rp not in sc.get("required", []):
                problems.append("%s must require %s" % (label, rp))

    # 4. law profile facts match current repository counts
    prof = docs["law_profile"]
    if prof.get("law_id") != "sa_companies_law_m132_1443":
        problems.append("profile law_id wrong")
    if prof.get("governing_language") != "ar":
        problems.append("profile governing_language must be ar")
    if prof.get("article_count") != 281:
        problems.append("profile article_count must be 281")
    counts = {
        "arabic_full_llm 281": _rc(ARABIC) == 281,
        "english_full_llm 281": _rc(ENGLISH) == 281,
        "english_reference 281": _rc(ENREF) == 281,
        "chinese_internal_candidate 189": _rc(CANDF) == 189,
    }
    for label, ok in counts.items():
        if not ok:
            problems.append("current repository count mismatch: %s" % label)
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(_rc(x) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must be 5 files / 23 records")
    if len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                  "bab*_zh_source_extracted_articles_*.json"))) != 14:
        problems.append("Chinese source extracted files must be 14")
    if os.path.exists(OCRQ) and len(_read(OCRQ).get("entries", [])) != 281:
        problems.append("OCR manual_review_queue must be 281 entries")
    # profile's own recorded source-file counts must match reality
    sf = prof.get("source_files", {})
    if sf.get("arabic_full_llm", {}).get("records") != 281:
        problems.append("profile arabic_full_llm records must be 281")
    if sf.get("english_full_llm", {}).get("records") != 281:
        problems.append("profile english_full_llm records must be 281")
    if sf.get("english_reference", {}).get("records") != 281:
        problems.append("profile english_reference records must be 281")
    if sf.get("chinese_internal_candidate_isolable", {}).get("records") != 189:
        problems.append("profile chinese_internal_candidate records must be 189")
    if sf.get("old_chinese_legal_llm", {}).get("files") != 5 or \
            sf.get("old_chinese_legal_llm", {}).get("records") != 23:
        problems.append("profile old_chinese_legal_llm must be 5 files / 23 records")
    if sf.get("chinese_source_extracted", {}).get("files") != 14:
        problems.append("profile chinese_source_extracted files must be 14")
    if sf.get("ocr_manual_review_queue", {}).get("entries") != 281:
        problems.append("profile ocr_manual_review_queue entries must be 281")

    # 5. profile must NOT overclaim
    claims = prof.get("claims", {})
    for f in ("full_chinese_281_layer_created", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed", "trilingual_alignment_created",
              "full_chinese_translation_claimed"):
        if claims.get(f) is not False:
            problems.append("profile claims.%s must be false" % f)
    lh = prof.get("legal_hierarchy", {})
    if lh.get("arabic") != "governing":
        problems.append("profile legal_hierarchy.arabic must be governing")
    if lh.get("chinese") != "internal_reference_only":
        problems.append("profile legal_hierarchy.chinese must be internal_reference_only")
    for f in ("chinese_official", "chinese_binding", "chinese_governing"):
        if lh.get(f) is not False:
            problems.append("profile legal_hierarchy.%s must be false" % f)

    # 5b. repository-review identity model (official-source-based; repo-owner review; external optional)
    sb = prof.get("source_basis", {})
    if sb.get("status") != "official_source_based":
        problems.append("profile source_basis.status must be official_source_based")
    if sb.get("governing_source_language") != "ar":
        problems.append("profile source_basis.governing_source_language must be ar")
    rlr = prof.get("repository_legal_review", {})
    if rlr.get("repository_owner_has_legal_background") is not True:
        problems.append("profile repository_owner_has_legal_background must be true")
    if rlr.get("repository_owner_legal_qualification") != "bachelor_of_law":
        problems.append("profile repository_owner_legal_qualification must be bachelor_of_law")
    if rlr.get("repository_legal_review_status") != "repository_owner_review_active":
        problems.append("profile repository_legal_review_status must be repository_owner_review_active")
    if not isinstance(rlr.get("repository_review_scope"), list) or not rlr.get("repository_review_scope"):
        problems.append("profile repository_review_scope must be a non-empty list")
    elr = prof.get("external_legal_review", {})
    if elr.get("external_legal_review_required_for_repository_use") is not False:
        problems.append("profile external_legal_review_required_for_repository_use must be false")
    if elr.get("external_legal_review_optional_for_enterprise_or_official_adoption") is not True:
        problems.append("profile external_legal_review_optional_for_enterprise_or_official_adoption must be true")
    if elr.get("external_legal_review_status") != "not_performed":
        problems.append("profile external_legal_review_status must be not_performed")
    ost = prof.get("official_status", {})
    for f in ("official_government_publication", "official_translation_claimed",
              "official_adoption_claimed"):
        if ost.get(f) is not False:
            problems.append("profile official_status.%s must be false" % f)
    for f in ("chinese_official", "chinese_binding", "chinese_governing"):
        if f in ost and ost.get(f) is not False:
            problems.append("profile official_status.%s must be false" % f)
    if ost.get("not_legal_advice") is not True:
        problems.append("profile official_status.not_legal_advice must be true")
    if prof.get("release_policy", {}).get("public_release_created") is not False:
        problems.append("profile public_release_created must be false")

    # 6. batch config matches existing P0-005 QA
    bc = docs["batch_config"]
    ARTS = [188, 189, 190, 191, 192, 194, 218, 220, 260, 261, 262, 274]
    DIST = {"7": [188, 189, 190, 191, 192, 194], "9": [218], "10": [220],
            "13": [260, 261, 262], "14": [274]}
    if bc.get("batch_id") != "P0-005":
        problems.append("batch config batch_id must be P0-005")
    if bc.get("stage") != "CHINESE_REMEDIATION_BATCH_P0_005_QA":
        problems.append("batch config stage must be CHINESE_REMEDIATION_BATCH_P0_005_QA")
    if bc.get("scope_articles") != ARTS:
        problems.append("batch config scope_articles must match the P0-005 list")
    if bc.get("expected_babs") != [7, 9, 10, 13, 14]:
        problems.append("batch config expected_babs must be [7,9,10,13,14]")
    if {str(k): list(v) for k, v in (bc.get("expected_bab_distribution") or {}).items()} != DIST:
        problems.append("batch config expected_bab_distribution must match the authorized split")
    if os.path.exists(P0_005_QA):
        qa = _read(P0_005_QA)
        if bc.get("scope_articles") != qa.get("scope_articles"):
            problems.append("batch config scope_articles must match the existing P0-005 QA")
        if bc.get("expected_babs") != qa.get("expected_babs"):
            problems.append("batch config expected_babs must match the existing P0-005 QA")
        if {str(k): list(v) for k, v in (bc.get("expected_bab_distribution") or {}).items()} != \
                {str(k): list(v) for k, v in (qa.get("expected_bab_distribution") or {}).items()}:
            problems.append("batch config expected_bab_distribution must match the existing P0-005 QA")
    else:
        problems.append("existing P0-005 QA file missing (cannot cross-check batch config)")

    # 7. terminology seed statuses use the repository-owner review model (no old human-review status)
    allowed_term_status = {"seed_repository_owner_review_active", "seed_pending_repository_owner_review"}
    terms = docs["terminology_seed"].get("terms", [])
    if not terms:
        problems.append("terminology seed must contain terms")
    for t in terms:
        for f in ("term_ar", "term_en", "term_zh", "domain_context", "notes_ar", "status"):
            if f not in t:
                problems.append("terminology entry missing %s: %r" % (f, t.get("term_ar")))
        if t.get("status") not in allowed_term_status:
            problems.append("terminology entry status must use the repository-owner review model: %r"
                            % t.get("term_ar"))

    # 8. doctrine/architecture principles; no banned overclaim; no old blanket human-review framing
    with open(DOCTRINE, encoding="utf-8") as fh:
        doctrine = fh.read()
    with open(ARCH, encoding="utf-8") as fh:
        arch = fh.read()
    if "المصدر العربي الرسمي هو النص الحاكم" not in doctrine and \
            "المصدر العربي الرسمي حاكم" not in doctrine:
        problems.append("doctrine must state the official Arabic source governs")
    if "ملف تعريف" not in arch and "law profile" not in arch.lower():
        problems.append("architecture must describe the law profile component")
    # doctrine must NOT imply external legal review is required for repository use
    if "المراجعة الخارجية اختيارية" not in doctrine:
        problems.append("doctrine must state external review is optional (not required for use)")
    new_files_text = doctrine + "\n" + arch + "\n" + \
        json.dumps(prof, ensure_ascii=False) + "\n" + json.dumps(bc, ensure_ascii=False) + "\n" + \
        json.dumps(docs["terminology_seed"], ensure_ascii=False)
    blob = new_files_text.lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned overclaim term present in foundation artifacts: %r" % term)

    # 8b. the old blanket human-legal-review framing must not remain in ANY foundation file.
    # The forbidden phrases are assembled from fragments so this validator's own source (and the
    # test's) does not contain the full literals and cannot self-match.
    _phlr = "pending_" + "human_legal_review"
    stale_framings = (
        "human legal review " + "remains pending",
        "human legal review " + "still pending",
        "human legal review " + "pending",
        _phlr,
        "seed_" + _phlr,
        "بانتظار مراجعة " + "قانونية بشرية",
        "المراجعة القانونية " + "البشرية معلّقة",
    )
    foundation_texts = {}
    for p in (DOCTRINE, ARCH, LAW_PROFILE_SCHEMA, BATCH_SCHEMA, PROV_SCHEMA, PROFILE, BATCH, TERMS,
              os.path.abspath(__file__),
              os.path.join(ROOT, "tests", "test_legal_corpus_factory_foundation.py")):
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                foundation_texts[os.path.relpath(p, ROOT)] = fh.read()
    # README: scan only the factory-foundation section (historical P0 notes elsewhere are untouched).
    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme):
        with open(readme, encoding="utf-8") as fh:
            rtext = fh.read()
        marker = "## Multilingual Saudi legal corpus for AI (foundation)"
        if marker in rtext:
            seg = rtext.split(marker, 1)[1].split("\n## ", 1)[0]
            foundation_texts["README.md#foundation-section"] = seg
    for rel, text in foundation_texts.items():
        for stale in stale_framings:
            if stale in text:
                problems.append("stale human-legal-review framing must be removed from foundation "
                                "file %s: %r" % (rel, stale))

    # 9. no P1/P2/P3 batch dirs; no full-Chinese-281 / trilingual artifacts created
    later = glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
    if later:
        problems.append("P1/P2/P3 batch dirs must not exist: %s"
                        % sorted(os.path.basename(x) for x in later))
    for pat in ("*trilingual*", "*full_chinese_281*", "*chinese_full_281*"):
        hits = glob.glob(os.path.join(ROOT, "data", "**", pat), recursive=True) + \
            glob.glob(os.path.join(ROOT, "reports", "**", pat), recursive=True)
        if hits:
            problems.append("no full-Chinese-281 / trilingual artifacts allowed: %s"
                            % sorted(os.path.relpath(x, ROOT) for x in hits))

    # 10. base corpora still intact (read-only sanity)
    if _rc(ARABIC) != 281 or _rc(ENGLISH) != 281 or _rc(ENREF) != 281 or _rc(CANDF) != 189:
        problems.append("base corpora counts changed (must be untouched)")

    print("=" * 60)
    print("Sovereign legal corpus factory foundation validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Foundation (multilingual, LLM-ready, official-source-based Saudi legal corpus): "
          "doctrine + architecture + 3 schemas (law_profile/batch_config/provenance) + Saudi "
          "Companies Law profile (facts match Arabic 281 / English 281 / English reference 281 / "
          "Chinese candidate 189 / old Chinese 5-files-23-records / Chinese sources 14 / OCR 281) + "
          "example P0-005 QA batch config (matches existing QA scope/babs) + terminology seed (all "
          "seed_repository_owner_review_active); official Arabic source governs; repository-owner "
          "legal review active (bachelor of law); external legal review optional, not required for "
          "repository use; no official government publication / official translation / "
          "official adoption / Chinese binding/governing / full-281 / trilingual claim; no P1/P2/P3; "
          "base corpora untouched.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
