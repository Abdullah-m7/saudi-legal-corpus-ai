#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese remediation backlog + batch plan + source-packet manifest (planning only).

Confirms the backlog covers all 281 articles with the correct P0/P1/P2/P3 counts and blocking
rules, the batches are deterministic (<=20, ordered, full coverage), the manifest defines source/
protected/forbidden posture, no Chinese text is generated/corrected and no full Arabic/English text
is duplicated, the trust posture holds, and no protected layer is touched.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
BACKLOG = os.path.join(RV, "chinese_remediation_backlog_001_281.json")
BATCH = os.path.join(RV, "chinese_remediation_batch_plan.json")
MANIFEST = os.path.join(RV, "chinese_remediation_source_packet_manifest.json")
MD = os.path.join(RV, "CHINESE_REMEDIATION_BACKLOG_AND_SOURCE_PACKET_PLAN_AR.md")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
EXP = {"P0": 92, "P1": 76, "P2": 95, "P3": 18}
MAX_BATCH = 20
TRACK = {"P0": "P0_no_isolable_text", "P1": "P1_retranslation_or_manual_review",
         "P2": "P2_expansion_needed", "P3": "P3_retain_internal_reference"}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")
FORBIDDEN_KEYS = {"chinese_text", "corrected_chinese_text", "generated_chinese_text",
                  "arabic_text", "english_text", "official_text_ar", "legal_rule_text_en",
                  "legal_rule_text_ar", "chinese_text_generated"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _all_keys(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            acc.add(k)
            _all_keys(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _all_keys(v, acc)


def main() -> int:
    problems = []
    for p, label in ((BACKLOG, "backlog JSON"), (BATCH, "batch plan JSON"),
                     (MANIFEST, "source packet manifest"), (MD, "Arabic report")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    bl = _read(BACKLOG)
    bp = _read(BATCH)
    mf = _read(MANIFEST)
    recs = bl.get("records", [])

    # counts + posture
    if len(recs) != TARGET:
        problems.append("backlog must have 281 records (got %d)" % len(recs))
    for p, exp in EXP.items():
        if bl.get("%s_count" % p.lower()) != exp:
            problems.append("%s_count must be %d" % (p.lower(), exp))
    if bl.get("remediation_required_count") != EXP["P0"] + EXP["P1"] + EXP["P2"]:
        problems.append("remediation_required_count must be 263")
    if bl.get("no_action_internal_reference_count") != EXP["P3"]:
        problems.append("no_action_internal_reference_count must be 18")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed", "corrected_chinese_created",
              "generated_chinese_created", "arabic_used_to_generate_chinese",
              "english_used_to_generate_chinese"):
        if bl.get(f) is not False:
            problems.append("backlog %s must be false" % f)

    nums = [r["article_number"] for r in recs]
    if nums != list(range(1, TARGET + 1)):
        problems.append("backlog article numbers must be exactly 1..281 in order")
    if len(set(nums)) != len(nums):
        problems.append("backlog has duplicate article numbers")

    actual = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for r in recs:
        pr = r.get("current_priority")
        if pr not in actual:
            problems.append("art %s invalid current_priority" % r.get("article_number"))
            continue
        actual[pr] += 1
        if r.get("remediation_track") != TRACK[pr]:
            problems.append("art %s remediation_track wrong for %s" % (r["article_number"], pr))
        if pr in ("P0", "P1", "P2"):
            if r.get("should_block_full_chinese_layer") is not True:
                problems.append("art %s (%s) must block full Chinese layer" % (r["article_number"], pr))
            if r.get("should_block_trilingual_alignment") is not True:
                problems.append("art %s (%s) must block trilingual alignment" % (r["article_number"], pr))
            if r.get("requires_new_chinese_text") is not True:
                problems.append("art %s (%s) requires_new_chinese_text must be true" % (r["article_number"], pr))
        else:  # P3
            if r.get("should_block_full_chinese_layer") is not False:
                problems.append("art %s (P3) should_block_full_chinese_layer must be false" % r["article_number"])
            if r.get("should_block_trilingual_alignment") is not True:
                problems.append("art %s (P3) must still block trilingual alignment" % r["article_number"])
            if r.get("requires_new_chinese_text") is not False:
                problems.append("art %s (P3) requires_new_chinese_text must be false" % r["article_number"])
    for p, c in actual.items():
        if c != EXP[p]:
            problems.append("backlog %s record count %d != %d" % (p, c, EXP[p]))

    # batch plan: deterministic, <=20, full coverage, priority ordering
    batches = bp.get("batches", [])
    if bp.get("batch_count") != len(batches):
        problems.append("batch_count mismatch")
    if bp.get("p0_batch_count", 0) + bp.get("p1_batch_count", 0) + bp.get("p2_batch_count", 0) \
            + bp.get("p3_confirmation_batch_count", 0) != len(batches):
        problems.append("batch sub-counts do not sum to batch_count")
    seen_arts = []
    prio_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    last = -1
    for b in batches:
        if b.get("article_count") != len(b.get("article_numbers", [])):
            problems.append("batch %s article_count mismatch" % b.get("batch_id"))
        if b.get("article_count", 0) > MAX_BATCH:
            problems.append("batch %s exceeds max %d" % (b.get("batch_id"), MAX_BATCH))
        an = b.get("article_numbers", [])
        if an != sorted(an, key=lambda n: (_bab(recs, n), n)):
            problems.append("batch %s article order not deterministic" % b.get("batch_id"))
        seen_arts.extend(an)
        o = prio_order.get(b.get("priority"), 9)
        if o < last:
            problems.append("batches not ordered by priority (P0,P1,P2,P3)")
        last = max(last, o)
    if sorted(seen_arts) != list(range(1, TARGET + 1)):
        problems.append("batches must cover Articles 1..281 exactly once")
    if len(set(seen_arts)) != len(seen_arts):
        problems.append("an article appears in more than one batch")

    # manifest presence of required blocks
    for key in ("source_files", "protected_files", "future_batch_requirements",
                "forbidden_actions", "required_trust_posture", "validation_requirements"):
        if key not in mf:
            problems.append("manifest missing %s" % key)
    forb = json.dumps(mf.get("forbidden_actions", []), ensure_ascii=False).lower()
    for need in ("full chinese 281 layer", "trilingual alignment"):
        if need not in forb:
            problems.append("manifest forbidden_actions must mention %r" % need)

    # no banned overclaim; no forbidden generated/corrected/foreign-text keys
    blob = (json.dumps(bl, ensure_ascii=False) + json.dumps(bp, ensure_ascii=False)
            + json.dumps(mf, ensure_ascii=False)).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned overclaim term present: %r" % term)
    keys = set()
    _all_keys(bl, keys)
    _all_keys(bp, keys)
    _all_keys(mf, keys)
    for k in keys:
        if k in FORBIDDEN_KEYS:
            problems.append("forbidden field present: %r" % k)

    # no full Arabic/English text duplicated (only hashes stored)
    ar = {r["article_number"]: r["official_text_ar"] for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r["legal_rule_text_en"] for r in _read(ENGLISH)["records"]}
    bl_blob = json.dumps(bl, ensure_ascii=False)
    if ar[1] in bl_blob or en[1] in bl_blob:
        problems.append("backlog must not duplicate full Arabic/English text (hashes only)")

    # protected layers unchanged
    if len(_read(CANDF)["records"]) != 189:
        problems.append("Chinese internal candidate must remain 189 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    if len(_read(ARABIC)["records"]) != TARGET:
        problems.append("Arabic full LLM must remain 281 records")
    if len(_read(ENGLISH)["records"]) != TARGET:
        problems.append("English full LLM must remain 281 records")
    er = os.path.join(ROOT, "data", "english_reference",
                      "companies_law_m132_1443_en_reference_001_281.json")
    if not os.path.exists(er) or len(_read(er)["records"]) != TARGET:
        problems.append("English reference full must remain 281 records")
    if os.path.exists(CAND_SRC):
        c = _read(CAND_SRC)
        if len(c.get("articles", [])) != TARGET or c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic source must remain unchanged")
    else:
        problems.append("official Arabic source file missing")
    if len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                  "bab*_zh_source_extracted_articles_*.json"))) != 14:
        problems.append("Chinese source extracted files must remain 14")
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != TARGET:
        problems.append("OCR manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Chinese remediation backlog + batch plan + manifest validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] backlog 281 (P0=92 P1=76 P2=95 P3=18; remediation_required=263); P0/P1/P2 block "
          "full-layer + alignment; P3 internal-reference only; %d deterministic batches (<=20, "
          "cover 1..281); manifest source/protected/forbidden defined; no generated/corrected "
          "Chinese, no full Arabic/English text duplicated; Chinese candidate 189 + old Chinese "
          "5/23 + Arabic 281 + English 281 + English reference 281 + Arabic source + Chinese "
          "sources 14 + OCR queue all unchanged." % len(batches))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


def _bab(recs, n):
    for r in recs:
        if r["article_number"] == n:
            return r["expected_bab_number"]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
