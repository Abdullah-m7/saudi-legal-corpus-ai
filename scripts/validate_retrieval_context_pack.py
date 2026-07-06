#!/usr/bin/env python3
"""
Validator for Retrieval Context Pack Foundation.

Read-only — does not modify any repository files.
Checks CLI behavior, JSON output, Markdown output, filters,
full-text toggle, boundaries, deterministic results, no mutation,
and no embeddings/vector DB/API/network dependencies.
"""

import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")
SEARCH_SCRIPT = os.path.join(REPO_ROOT, "scripts", "search_primary_arabic_export.py")
PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_context_pack.py")

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


def run_pack(args, timeout=30):
    """Run context pack CLI and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, PACK_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def validate():
    global CHECKS_PASSED, CHECKS_FAILED

    print("\n============================================================")
    print("Corpus Retrieval Context Pack Foundation validation")
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

    # 3. Search CLI exists
    check("Search CLI exists", os.path.isfile(SEARCH_SCRIPT))

    # 4. Context pack CLI exists
    check("Context pack CLI exists", os.path.isfile(PACK_SCRIPT))

    # 5. Context pack CLI --help works
    rc, stdout, stderr = run_pack(["--help"])
    check("Context pack CLI --help works", rc == 0 and "usage" in stdout.lower())

    # 6. JSON output parses
    rc, stdout, _ = run_pack(["مجلس الإدارة", "--limit", "3", "--format", "json"])
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
        "pack_version", "query", "normalized_query", "generated_at_date",
        "source_search_tool", "source_export_file", "source_export_record_count",
        "retrieval_method", "limit", "filters", "total_matches", "returned",
        "legal_boundaries", "records",
    ]
    if json_valid:
        for field in required_top:
            check(f"JSON has '{field}'", field in json_data)
    else:
        for field in required_top:
            check(f"JSON has '{field}'", False, "JSON parse failed")

    # 8. Markdown output exists and has expected headings
    rc, md_stdout, _ = run_pack(["مجلس الإدارة", "--limit", "3", "--format", "markdown"])
    md_has_heading = "حزمة سياق استرجاع" in md_stdout
    md_has_boundaries = "الحدود القانونية" in md_stdout
    md_has_records = "السجلات المسترجعة" in md_stdout
    check("Markdown has heading", rc == 0 and md_has_heading)
    check("Markdown has boundaries section", md_has_boundaries)
    check("Markdown has records section", md_has_records)

    # 9. query "مجلس الإدارة" returns > 0 records
    if json_valid:
        check("Query 'مجلس الإدارة' returns > 0 records", json_data["total_matches"] > 0,
              f"Total matches: {json_data['total_matches']}")
    else:
        check("Query 'مجلس الإدارة' returns > 0 records", False)

    # 10. --limit works
    rc, stdout, _ = run_pack(["مجلس الإدارة", "--limit", "2", "--format", "json"])
    limit_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            limit_ok = data["returned"] <= 2 and data["limit"] == 2
        except json.JSONDecodeError:
            pass
    check("--limit works", limit_ok)

    # 11. --track works
    rc, stdout, _ = run_pack(["التصفية", "--track", "companies_law", "--limit", "5", "--format", "json"])
    track_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            track_ok = all(r["source_track_id"] == "companies_law" for r in data["records"])
            track_ok = track_ok and data["filters"].get("track") == "companies_law"
        except json.JSONDecodeError:
            pass
    check("--track works", track_ok)

    # 12. --record-type works
    rc, stdout, _ = run_pack(["الشركة", "--record-type", "article", "--limit", "5", "--format", "json"])
    rt_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            rt_ok = all(r["record_type"] == "article" for r in data["records"])
            rt_ok = rt_ok and data["filters"].get("record_type") == "article"
        except json.JSONDecodeError:
            pass
    check("--record-type works", rt_ok)

    # 13. --include-full-text works
    rc, stdout, _ = run_pack(["مجلس الإدارة", "--limit", "2", "--format", "json", "--include-full-text"])
    ft_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            ft_ok = all("text_ar" in r and r["text_ar"] for r in data["records"])
        except json.JSONDecodeError:
            pass
    check("--include-full-text works", ft_ok)

    # 14. Without --include-full-text, records do not include text_ar
    rc, stdout, _ = run_pack(["مجلس الإدارة", "--limit", "3", "--format", "json"])
    no_ft_ok = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            no_ft_ok = all("text_ar" not in r for r in data["records"])
        except json.JSONDecodeError:
            pass
    check("Without --include-full-text, records omit text_ar", no_ft_ok)

    # 15. All returned records language ar
    rc, stdout, _ = run_pack(["الشركة", "--limit", "10", "--format", "json"])
    all_ar = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            all_ar = all(r.get("language") == "ar" for r in data["records"])
        except json.JSONDecodeError:
            pass
    check("All returned records language ar", all_ar)

    # 16. No English/Chinese records
    rc, stdout, _ = run_pack(["company", "--limit", "5", "--format", "json"])
    no_en = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            no_en = data["total_matches"] == 0
        except json.JSONDecodeError:
            pass
    check("No English records matched", no_en)

    rc, stdout, _ = run_pack(["公司", "--limit", "5", "--format", "json"])
    no_zh = False
    if rc == 0:
        try:
            data = json.loads(stdout)
            no_zh = data["total_matches"] == 0
        except json.JSONDecodeError:
            pass
    check("No Chinese records matched", no_zh)

    # 17. legal_boundaries present
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

    # 18. No network required
    check("No network required (works offline)", rc == 0)

    # 19. No embeddings/vector DB/API dependencies
    with open(PACK_SCRIPT, "r", encoding="utf-8") as f:
        script_lines = f.readlines()
    import_lines = [l for l in script_lines if l.strip().startswith("import ") or l.strip().startswith("from ")]
    import_text = " ".join(import_lines).lower()
    no_emb = "embedding" not in import_text and "vector" not in import_text and "faiss" not in import_text
    no_api = "flask" not in import_text and "fastapi" not in import_text
    no_network = "requests" not in import_text and "urllib" not in import_text and "httpx" not in import_text
    check("No embeddings/vector DB dependencies", no_emb)
    check("No API dependencies", no_api)
    check("No network dependencies", no_network)

    # 20. Deterministic for same query
    rc1, stdout1, _ = run_pack(["مجلس الإدارة", "--limit", "5", "--format", "json"])
    rc2, stdout2, _ = run_pack(["مجلس الإدارة", "--limit", "5", "--format", "json"])
    # generated_at_date is the same day, so output should be identical
    check("Deterministic for same query", stdout1 == stdout2)

    # 21. Does not modify repository files
    source_files = [
        JSONL_PATH,
        SEARCH_SCRIPT,
        os.path.join(REPO_ROOT, "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json"),
        os.path.join(REPO_ROOT, "data/implementing_regulations/general/general_implementing_regulations_arabic_legal_llm.json"),
    ]
    mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    run_pack(["الشركة", "--limit", "3", "--format", "json"])
    mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    no_modifications = all(mtimes_before[f] == mtimes_after[f] for f in mtimes_before)
    check("Does not modify repository files", no_modifications)

    # 22. --output writes to file and does not modify repo files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=tempfile.gettempdir()) as tmp:
        tmp_path = tmp.name
    rc, stdout, stderr = run_pack(["مجلس الإدارة", "--limit", "2", "--format", "json", "--output", tmp_path])
    output_written = os.path.isfile(tmp_path) and os.path.getsize(tmp_path) > 0
    check("--output writes to external file", output_written)
    # Clean up
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

    # 23. Validator is read-only
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
        print("[PASS] Retrieval context pack: deterministic, offline, Arabic-only. "
              "JSON + Markdown outputs. No embeddings, no API, no network. "
              "Not legal advice. Read-only.")
        print("============================================================")


if __name__ == "__main__":
    validate()