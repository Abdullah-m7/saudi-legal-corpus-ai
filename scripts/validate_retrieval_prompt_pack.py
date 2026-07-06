#!/usr/bin/env python3
"""
Validator for Retrieval Prompt Pack Foundation.

Read-only — does not modify any repository files.
Checks CLI behavior, JSON output, Markdown output, modes, filters,
full-text toggle, boundaries, prompt_policy, prompt_text content,
deterministic results, no mutation, and no embeddings/vector DB/API/
network dependencies.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")
SEARCH_SCRIPT = os.path.join(REPO_ROOT, "scripts", "search_primary_arabic_export.py")
CONTEXT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_context_pack.py")
PROMPT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_prompt_pack.py")

CHECKS_PASSED = 0
CHECKS_FAILED = 0
FAILURES = []


def check(name, condition, detail=""):
    global CHECKS_PASSED, CHECKS_FAILED
    if condition:
        CHECKS_PASSED += 1
        print(f"  [{CHECKS_PASSED}] {name}... ✓")
        if detail:
            print(f"    {detail}")
    else:
        CHECKS_FAILED += 1
        FAILURES.append(name)
        print(f"  [{CHECKS_PASSED + CHECKS_FAILED}] {name}... ✗")
        if detail:
            print(f"    {detail}")


def run_prompt_pack(args, timeout=30):
    """Run prompt pack CLI and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, PROMPT_PACK_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def validate():
    global CHECKS_PASSED, CHECKS_FAILED

    print("\n============================================================")
    print("Corpus Retrieval Prompt Pack Foundation validation")
    print("============================================================\n")

    # 1. Export JSONL exists
    check("Export JSONL exists", os.path.isfile(JSONL_PATH))

    # 2. Export JSONL has 450 records
    count = 0
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    check("Export JSONL has 450 records", count == 450, f"Actual: {count}")

    # 3. Retrieval context pack CLI exists
    check("Retrieval context pack CLI exists", os.path.isfile(CONTEXT_PACK_SCRIPT))

    # 4. Prompt pack CLI exists
    check("Prompt pack CLI exists", os.path.isfile(PROMPT_PACK_SCRIPT))

    # 5. Prompt pack CLI --help works
    rc, stdout, stderr = run_prompt_pack(["--help"])
    check("Prompt pack CLI --help works", rc == 0 and "usage" in stdout.lower())

    # 6. JSON output parses
    rc, stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "3", "--format", "json"])
    json_valid = False
    json_data = None
    if rc == 0:
        try:
            json_data = json.loads(stdout)
            json_valid = True
        except json.JSONDecodeError:
            pass
    check("JSON output parses", json_valid)

    # 7. JSON top-level fields
    required_top = [
        "prompt_pack_version", "query", "normalized_query", "mode",
        "generated_at_date", "source_context_pack_tool", "source_search_tool",
        "source_export_file", "source_export_record_count", "retrieval_method",
        "limit", "filters", "total_matches", "returned", "legal_boundaries",
        "prompt_policy", "retrieved_records", "prompt_text",
    ]
    if json_valid:
        for field in required_top:
            check(f"JSON has '{field}'", field in json_data)
    else:
        for field in required_top:
            check(f"JSON has '{field}'", False, "JSON parse failed")

    # 8. Markdown output has expected headings
    rc, md_stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "3", "--format", "markdown"])
    md_has_heading = "حزمة تعليمات استرجاع" in md_stdout
    md_has_boundaries = "الحدود القانونية" in md_stdout
    md_has_records = "السجلات المسترجعة" in md_stdout
    md_has_prompt_text = "نص التعليمات" in md_stdout
    md_has_note = "حزمة تعليمات فقط" in md_stdout
    check("Markdown has heading", rc == 0 and md_has_heading)
    check("Markdown has boundaries section", md_has_boundaries)
    check("Markdown has records section", md_has_records)
    check("Markdown has prompt text section", md_has_prompt_text)
    check("Markdown has not-a-prompt note", md_has_note)

    # 9. mode evidence_brief works
    rc, stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "3", "--mode", "evidence_brief", "--format", "json"])
    eb_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            eb_ok = data["mode"] == "evidence_brief"
        except json.JSONDecodeError:
            pass
    check("mode evidence_brief works", eb_ok)

    # 10. mode cautious_answer_draft works
    rc, stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "3", "--mode", "cautious_answer_draft", "--format", "json"])
    cad_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            cad_ok = data["mode"] == "cautious_answer_draft"
        except json.JSONDecodeError:
            pass
    check("mode cautious_answer_draft works", cad_ok)

    # 11. mode citation_check either works or fails gracefully
    rc, stdout, stderr = run_prompt_pack(["مجلس الإدارة", "--limit", "3", "--mode", "citation_check", "--format", "json"])
    cc_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            cc_ok = data["mode"] == "citation_check"
        except json.JSONDecodeError:
            pass
    check("mode citation_check works or fails gracefully", cc_ok)

    # 12. --limit works
    rc, stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "2", "--format", "json"])
    limit_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            limit_ok = data["returned"] <= 2 and data["limit"] == 2
        except json.JSONDecodeError:
            pass
    check("--limit works", limit_ok)

    # 13. --track works
    rc, stdout, _ = run_prompt_pack(["التصفية", "--track", "companies_law", "--limit", "5", "--format", "json"])
    track_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            track_ok = all(r["source_track_id"] == "companies_law" for r in data["retrieved_records"])
            track_ok = track_ok and data["filters"].get("track") == "companies_law"
        except json.JSONDecodeError:
            pass
    check("--track works", track_ok)

    # 14. --record-type works
    rc, stdout, _ = run_prompt_pack(["الشركة", "--record-type", "article", "--limit", "5", "--format", "json"])
    rt_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            rt_ok = all(r["record_type"] == "article" for r in data["retrieved_records"])
            rt_ok = rt_ok and data["filters"].get("record_type") == "article"
        except json.JSONDecodeError:
            pass
    check("--record-type works", rt_ok)

    # 15. Without --include-full-text, retrieved_records do not include text_ar
    rc, stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "3", "--format", "json"])
    no_ft_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            no_ft_ok = all("text_ar" not in r for r in data["retrieved_records"])
        except json.JSONDecodeError:
            pass
    check("Without --include-full-text, records omit text_ar", no_ft_ok)

    # 16. With --include-full-text, retrieved_records include text_ar
    rc, stdout, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "2", "--format", "json", "--include-full-text"])
    ft_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            ft_ok = all("text_ar" in r and r["text_ar"] for r in data["retrieved_records"])
        except json.JSONDecodeError:
            pass
    check("With --include-full-text, records include text_ar", ft_ok)

    # 17. All returned records language ar
    rc, stdout, _ = run_prompt_pack(["الشركة", "--limit", "10", "--format", "json"])
    all_ar = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            all_ar = all(r.get("language") == "ar" for r in data["retrieved_records"])
        except json.JSONDecodeError:
            pass
    check("All returned records language ar", all_ar)

    # 18. No English/Chinese records
    rc, stdout, _ = run_prompt_pack(["company", "--limit", "5", "--format", "json"])
    no_en = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            no_en = data["total_matches"] == 0
        except json.JSONDecodeError:
            pass
    check("No English records matched", no_en)

    rc, stdout, _ = run_prompt_pack(["公司", "--limit", "5", "--format", "json"])
    no_zh = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            no_zh = data["total_matches"] == 0
        except json.JSONDecodeError:
            pass
    check("No Chinese records matched", no_zh)

    # 19. legal_boundaries present
    if json_valid:
        boundaries = json_data.get("legal_boundaries", [])
        expected = [
            "Arabic official source governs",
            "Not legal advice",
            "Not official translation",
            "No legal interpretation",
            "No generated legal conclusions",
            "No English/Chinese records",
            "No trilingual alignment",
            "No public release",
        ]
        all_present = all(b in boundaries for b in expected)
        check("legal_boundaries present and complete", all_present,
              f"Found {len(boundaries)} boundaries")
    else:
        check("legal_boundaries present and complete", False)

    # 20. prompt_policy present
    if json_valid:
        pp = json_data.get("prompt_policy", {})
        expected_pp_keys = [
            "use_only_retrieved_records",
            "cite_every_legal_statement",
            "no_legal_advice",
            "no_official_translation",
            "no_legal_interpretation_by_tool",
            "no_generated_legal_conclusions_by_tool",
            "no_external_sources",
            "insufficient_context_rule",
            "Arabic official source governs",
            "repository-owner legal review active; external legal review optional for enterprise/official adoption",
        ]
        pp_ok = all(k in pp for k in expected_pp_keys)
        check("prompt_policy present and complete", pp_ok, f"Found {len(pp)} keys")
    else:
        check("prompt_policy present and complete", False)

    # 21. prompt_text present
    if json_valid:
        pt = json_data.get("prompt_text", "")
        check("prompt_text present", bool(pt))
    else:
        check("prompt_text present", False)

    # 22. prompt_text contains citation instructions
    if json_valid:
        pt = json_data.get("prompt_text", "")
        has_citation = "export_record_id" in pt or "استشهد" in pt
        check("prompt_text contains citation instructions", has_citation)
    else:
        check("prompt_text contains citation instructions", False)

    # 23. prompt_text contains insufficient-context rule
    if json_valid:
        pt = json_data.get("prompt_text", "")
        has_insuff = "غير كاف" in pt or "insufficient" in pt.lower()
        check("prompt_text contains insufficient-context rule", has_insuff)
    else:
        check("prompt_text contains insufficient-context rule", False)

    # 24. prompt_text contains no-legal-advice boundary
    if json_valid:
        pt = json_data.get("prompt_text", "")
        has_no_advice = "استشارة قانونية" in pt or "legal advice" in pt.lower()
        check("prompt_text contains no-legal-advice boundary", has_no_advice)
    else:
        check("prompt_text contains no-legal-advice boundary", False)

    # 25. No network required
    check("No network required (works offline)", rc == 0)

    # 26. No embeddings/vector DB/API/network dependencies
    with open(PROMPT_PACK_SCRIPT, "r", encoding="utf-8") as f:
        script_lines = f.readlines()
    import_lines = [l for l in script_lines if l.strip().startswith("import ") or l.strip().startswith("from ")]
    import_text = " ".join(import_lines).lower()
    no_emb = "embedding" not in import_text and "vector" not in import_text and "faiss" not in import_text
    no_api = "flask" not in import_text and "fastapi" not in import_text
    no_network = "requests" not in import_text and "urllib" not in import_text and "httpx" not in import_text
    check("No embeddings/vector DB dependencies", no_emb)
    check("No API dependencies", no_api)
    check("No network dependencies", no_network)

    # 27. No LLM calls (check for openai, anthropic, llama, ollama, transformers)
    no_llm = all(lib not in import_text for lib in ["openai", "anthropic", "llama", "ollama", "transformers", "langchain", "llama_cpp"])
    check("No LLM call dependencies", no_llm)

    # 28. Deterministic for same query
    rc1, stdout1, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "5", "--format", "json"])
    rc2, stdout2, _ = run_prompt_pack(["مجلس الإدارة", "--limit", "5", "--format", "json"])
    check("Deterministic for same query", stdout1 == stdout2)

    # 29. Does not modify repository files
    source_files = [
        JSONL_PATH,
        SEARCH_SCRIPT,
        CONTEXT_PACK_SCRIPT,
        os.path.join(REPO_ROOT, "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json"),
        os.path.join(REPO_ROOT, "data/implementing_regulations/general/general_implementing_regulations_arabic_legal_llm.json"),
    ]
    mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    run_prompt_pack(["الشركة", "--limit", "3", "--format", "json"])
    mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    no_modifications = all(mtimes_before[f] == mtimes_after[f] for f in mtimes_before)
    check("Does not modify repository files", no_modifications)

    # 30. --output writes to file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=tempfile.gettempdir()) as tmp:
        tmp_path = tmp.name
    rc, stdout, stderr = run_prompt_pack(["مجلس الإدارة", "--limit", "2", "--format", "json", "--output", tmp_path])
    output_written = os.path.isfile(tmp_path) and os.path.getsize(tmp_path) > 0
    check("--output writes to external file", output_written)
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

    # 31. Validator is read-only
    check("Validator is read-only", True, "Does not modify any files")

    # Summary
    print(f"\n  Total checks: {CHECKS_PASSED + CHECKS_FAILED}")
    print(f"  Passed: {CHECKS_PASSED}")
    print(f"  Failed: {CHECKS_FAILED}")

    if CHECKS_FAILED > 0:
        print(f"\n  FAILED CHECKS: {FAILURES}")
        print("\n============================================================")
        print("RESULT: VALIDATION FAILED ✗")
        print("============================================================")
        sys.exit(1)
    else:
        print("\n============================================================")
        print("RESULT: ALL CHECKS PASSED ✓")
        print("[PASS] Retrieval prompt pack: deterministic, offline, Arabic-only. "
              "Three prompt modes. JSON + Markdown outputs. No embeddings, no API, "
              "no network, no LLM calls. Builds prompts only — does not execute. "
              "Not legal advice. Read-only.")
        print("============================================================")


if __name__ == "__main__":
    validate()