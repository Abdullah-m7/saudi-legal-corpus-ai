#!/usr/bin/env python3
"""
Operator Demo Pack Validator

Read-only validator for the operator demo pack documentation files.

Checks:
- All required operator demo pack files exist.
- Required boundary phrases exist across the pack.
- Required commands are referenced.
- No public release claim.
- No legal advice claim.
- No official translation claim.
- No generated answers claim.
- No LLM/RAG/API/network-as-feature claim.
- Referenced scripts exist on disk.
- Demo scenario validator exists.
- No generated artifacts committed in docs/operator_demo_pack.

This is NOT RAG.
This does NOT call an LLM.
This does NOT generate legal answers.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK_DIR = os.path.join(REPO_ROOT, "docs", "operator_demo_pack")

REQUIRED_FILES = [
    "START_HERE_AR.md",
    "DEMO_SCRIPT_AR.md",
    "REHEARSAL_CHECKLIST_AR.md",
    "COMMANDS_AR.md",
    "BOUNDARIES_AR.md",
]

REQUIRED_BOUNDARY_PHRASES = [
    "المصدر العربي الرسمي هو الحاكم",
    "ليست استشارة قانونية",
    "ليست ترجمة رسمية",
    "لا تفسير قانوني",
    "لا استنتاجات قانونية مولدة",
    "لا حكم على الصحة القانونية",
    "لا تحقق الدعم الدلالي",
    "لا استدعاء LLM",
    "لا RAG",
    "لا إصدار عام",
]

REQUIRED_COMMANDS = [
    "make validate",
    "make corpus-retrieval-demo-scenarios-validate",
    "make corpus-retrieval-demo-scenarios-smoke",
    "run_retrieval_demo_scenarios.py",
    "run_retrieval_workflow.py",
]

PROHIBITED_CLAIMS = [
    ("public release claim", r"إصدار عام نشط|public release active|تم الإصدار公开"),
    ("legal advice claim", r"نقدم استشارة قانونية|provides legal advice"),
    ("official translation claim", r"ترجمة رسمية معتمدة|official translation provided"),
    ("generated answers claim", r"يولد إجابات قانونية بنجاح|successfully generates legal answers"),
    ("LLM call claim", r"يستدعي نموذجاً لغوياً بنجاح|calls an LLM successfully|uses GPT|uses Claude"),
    ("RAG claim", r"نظام RAG نشط|RAG system active"),
    ("API claim", r"API نشط|API endpoint live|serves an API"),
    ("network claim", r"يتطلب اتصالاً بالشبكة|requires network|network required"),
]

REFERENCED_SCRIPTS = [
    "scripts/run_retrieval_demo_scenarios.py",
    "scripts/run_retrieval_workflow.py",
    "scripts/validate_retrieval_demo_scenarios.py",
    "scripts/search_primary_arabic_export.py",
    "scripts/build_retrieval_context_pack.py",
    "scripts/build_retrieval_prompt_pack.py",
    "scripts/check_citation_support.py",
]

DEMO_SCENARIO_VALIDATOR = os.path.join(REPO_ROOT, "scripts", "validate_retrieval_demo_scenarios.py")


def main() -> int:
    errors: list[str] = []
    checks_passed = 0
    checks_total = 0

    # ── 1. Required files exist ──
    for fname in REQUIRED_FILES:
        checks_total += 1
        path = os.path.join(PACK_DIR, fname)
        if os.path.isfile(path):
            checks_passed += 1
        else:
            errors.append(f"Missing file: {fname}")

    # Read all files into one text blob
    all_text = ""
    file_contents: dict[str, str] = {}
    for fname in REQUIRED_FILES:
        path = os.path.join(PACK_DIR, fname)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                file_contents[fname] = content
                all_text += content + "\n"

    if not file_contents:
        print(f"FAIL: No operator demo pack files found in {PACK_DIR}")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    # ── 2. Required boundary phrases ──
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        checks_total += 1
        if phrase in all_text:
            checks_passed += 1
        else:
            errors.append(f"Missing boundary phrase: {phrase}")

    # ── 3. Required commands referenced ──
    for cmd in REQUIRED_COMMANDS:
        checks_total += 1
        if cmd in all_text:
            checks_passed += 1
        else:
            errors.append(f"Missing command reference: {cmd}")

    # ── 4. No prohibited claims ──
    for claim_name, pattern in PROHIBITED_CLAIMS:
        checks_total += 1
        if not re.search(pattern, all_text, re.IGNORECASE):
            checks_passed += 1
        else:
            errors.append(f"Prohibited claim found: {claim_name}")

    # ── 5. Referenced scripts exist ──
    for script_rel in REFERENCED_SCRIPTS:
        checks_total += 1
        script_path = os.path.join(REPO_ROOT, script_rel)
        if os.path.isfile(script_path):
            checks_passed += 1
        else:
            errors.append(f"Referenced script not found: {script_rel}")

    # ── 6. Demo scenario validator exists ──
    checks_total += 1
    if os.path.isfile(DEMO_SCENARIO_VALIDATOR):
        checks_passed += 1
    else:
        errors.append(f"Demo scenario validator not found: {DEMO_SCENARIO_VALIDATOR}")

    # ── 7. No generated artifacts committed in docs/operator_demo_pack ──
    checks_total += 1
    pack_files = []
    if os.path.isdir(PACK_DIR):
        for fname in os.listdir(PACK_DIR):
            if os.path.isfile(os.path.join(PACK_DIR, fname)):
                pack_files.append(fname)
    # Only .md files should be in the pack dir
    non_md_files = [f for f in pack_files if not f.endswith(".md")]
    if not non_md_files:
        checks_passed += 1
    else:
        errors.append(f"Non-markdown files in operator_demo_pack: {non_md_files}")

    # ── 8. START_HERE has quick start section ──
    checks_total += 1
    if "البدء السريع" in file_contents.get("START_HERE_AR.md", "") or "quick start" in file_contents.get("START_HERE_AR.md", "").lower():
        checks_passed += 1
    else:
        errors.append("START_HERE_AR.md: missing quick start section")

    # ── 9. DEMO_SCRIPT has all 10 sections ──
    script_text = file_contents.get("DEMO_SCRIPT_AR.md", "")
    expected_sections = ["المشكلة", "الأساس القانوني", "البحث المحلي", "حزمة السياق",
                          "حزمة الطلب", "فاحص الاستشهادات", "سير العمل المتكامل",
                          "سيناريوهات العرض", "الحدود", "RAG"]
    for section in expected_sections:
        checks_total += 1
        if section in script_text:
            checks_passed += 1
        else:
            errors.append(f"DEMO_SCRIPT_AR.md: missing section '{section}'")

    # ── 10. REHEARSAL_CHECKLIST has key items ──
    checklist_text = file_contents.get("REHEARSAL_CHECKLIST_AR.md", "")
    checklist_items = ["المستودع نظيف", "make validate", "demo-scenarios-validate",
                       "demo-scenarios-smoke", "خارج المستودع", "لا إصدار عام", "LLM"]
    for item in checklist_items:
        checks_total += 1
        if item in checklist_text:
            checks_passed += 1
        else:
            errors.append(f"REHEARSAL_CHECKLIST_AR.md: missing item '{item}'")

    # ── 11. COMMANDS has manual workflow commands ──
    commands_text = file_contents.get("COMMANDS_AR.md", "")
    manual_cmds = ["مجلس الإدارة", "التصفية", "نموذج", "--track", "--record-type"]
    for cmd_text in manual_cmds:
        checks_total += 1
        if cmd_text in commands_text:
            checks_passed += 1
        else:
            errors.append(f"COMMANDS_AR.md: missing manual command for '{cmd_text}'")

    # ── 12. BOUNDARIES has all boundary categories ──
    boundaries_text = file_contents.get("BOUNDARIES_AR.md", "")
    boundary_categories = ["قانونية", "تقنية", "الإصدار", "المراجعة", "المخرجات"]
    for cat in boundary_categories:
        checks_total += 1
        if cat in boundaries_text:
            checks_passed += 1
        else:
            errors.append(f"BOUNDARIES_AR.md: missing category '{cat}'")

    # ── 13. No co-author/tool/model attribution ──
    checks_total += 1
    attribution_patterns = [r"Co-authored-by", r"Generated by", r"Created by.*AI", r"Powered by.*GPT"]
    has_attribution = any(re.search(p, all_text, re.IGNORECASE) for p in attribution_patterns)
    if not has_attribution:
        checks_passed += 1
    else:
        errors.append("Found co-author/tool/model attribution in pack files")

    # ── Result ──
    print(f"\n{'='*60}")
    print(f"Operator Demo Pack Validator")
    print(f"{'='*60}")
    print(f"Checks passed: {checks_passed} / {checks_total}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\nFAIL")
        return 1
    else:
        print(f"\nPASS — All {checks_total} checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())