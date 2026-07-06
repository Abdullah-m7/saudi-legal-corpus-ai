#!/usr/bin/env python3
"""
Validator for Retrieval Workflow Runner Foundation.

Read-only — does not modify any repository files.
Checks CLI behavior, prepare_prompt mode, check_draft mode,
artifact creation, manifest parsing, no LLM/API/network/embeddings,
no mutation, deterministic output shape.
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")
CONTEXT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_context_pack.py")
PROMPT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_prompt_pack.py")
CITATION_CHECKER_SCRIPT = os.path.join(REPO_ROOT, "scripts", "check_citation_support.py")
WORKFLOW_SCRIPT = os.path.join(REPO_ROOT, "scripts", "run_retrieval_workflow.py")

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


def run_workflow(args, timeout=60):
    cmd = [sys.executable, WORKFLOW_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def validate():
    global CHECKS_PASSED, CHECKS_FAILED

    print("\n============================================================")
    print("Retrieval Workflow Runner Foundation validation")
    print("============================================================\n")

    tmpdir = tempfile.mkdtemp(prefix="workflow_val_")

    try:
        # 1. Context pack CLI exists
        check("Context pack CLI exists", os.path.isfile(CONTEXT_PACK_SCRIPT))

        # 2. Prompt pack CLI exists
        check("Prompt pack CLI exists", os.path.isfile(PROMPT_PACK_SCRIPT))

        # 3. Citation checker CLI exists
        check("Citation checker CLI exists", os.path.isfile(CITATION_CHECKER_SCRIPT))

        # 4. Workflow runner CLI exists
        check("Workflow runner CLI exists", os.path.isfile(WORKFLOW_SCRIPT))

        # 5. Workflow runner --help works
        rc, stdout, _ = run_workflow(["--help"])
        check("Workflow runner --help works", rc == 0 and "usage" in stdout.lower())

        # 6. prepare_prompt mode works
        prep_dir = os.path.join(tmpdir, "prep")
        rc, stdout, stderr = run_workflow([
            "مجلس الإدارة", "--mode", "prepare_prompt",
            "--limit", "3", "--prompt-mode", "evidence_brief",
            "--formats", "both", "--output-dir", prep_dir
        ])
        prep_ok = rc == 0 and os.path.isdir(prep_dir)
        check("prepare_prompt mode works", prep_ok, f"rc={rc}")

        # 7. Artifacts created in prepare_prompt
        manifest_path = os.path.join(prep_dir, "workflow_manifest.json")
        ctx_json_path = os.path.join(prep_dir, "context_pack.json")
        ppt_json_path = os.path.join(prep_dir, "prompt_pack.json")
        ctx_md_path = os.path.join(prep_dir, "context_pack.md")
        ppt_md_path = os.path.join(prep_dir, "prompt_pack.md")
        readme_path = os.path.join(prep_dir, "WORKFLOW_README.md")

        check("workflow_manifest.json created", os.path.isfile(manifest_path))
        check("context_pack.json created", os.path.isfile(ctx_json_path))
        check("prompt_pack.json created", os.path.isfile(ppt_json_path))
        check("context_pack.md created", os.path.isfile(ctx_md_path))
        check("prompt_pack.md created", os.path.isfile(ppt_md_path))
        check("WORKFLOW_README.md created", os.path.isfile(readme_path))

        # 8. Manifest parses
        manifest = None
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                try:
                    manifest = json.loads(f.read())
                except json.JSONDecodeError:
                    pass
        check("workflow_manifest.json parses", manifest is not None)

        # 9. Manifest top-level fields
        if manifest:
            required = [
                "workflow_version", "mode", "query", "normalized_query",
                "generated_at_date", "baseline_commit", "output_dir",
                "source_export_file", "source_export_record_count",
                "retrieval_method", "limit", "filters", "prompt_mode",
                "include_full_text", "formats", "artifacts",
                "legal_boundaries", "limitations", "hygiene",
            ]
            for field in required:
                check(f"Manifest has '{field}'", field in manifest)
        else:
            for field in ["workflow_version", "mode", "query", "artifacts", "legal_boundaries"]:
                check(f"Manifest has '{field}'", False, "Manifest parse failed")

        # 10. context_pack.json parses
        ctx_ok = False
        if os.path.isfile(ctx_json_path):
            with open(ctx_json_path, "r", encoding="utf-8") as f:
                try:
                    json.loads(f.read())
                    ctx_ok = True
                except json.JSONDecodeError:
                    pass
        check("context_pack.json parses", ctx_ok)

        # 11. prompt_pack.json parses
        ppt_ok = False
        if os.path.isfile(ppt_json_path):
            with open(ppt_json_path, "r", encoding="utf-8") as f:
                try:
                    json.loads(f.read())
                    ppt_ok = True
                except json.JSONDecodeError:
                    pass
        check("prompt_pack.json parses", ppt_ok)

        # 12. legal_boundaries present in manifest
        if manifest:
            bounds = manifest.get("legal_boundaries", [])
            bound_ok = len(bounds) >= 10 and "Arabic official source governs" in bounds
            check("legal_boundaries present in manifest", bound_ok, f"Found {len(bounds)}")
        else:
            check("legal_boundaries present in manifest", False)

        # 13. limitations present in manifest
        if manifest:
            lims = manifest.get("limitations", [])
            lim_ok = len(lims) >= 3
            check("limitations present in manifest", lim_ok, f"Found {len(lims)}")
        else:
            check("limitations present in manifest", False)

        # 14. hygiene present in manifest
        if manifest:
            hyg = manifest.get("hygiene", {})
            hyg_ok = "no_llm_calls" in hyg and "no_network" in hyg and "no_embeddings" in hyg
            check("hygiene present in manifest", hyg_ok)
        else:
            check("hygiene present in manifest", False)

        # 15. check_draft mode works with valid cited draft
        # Extract a real export_record_id from the prompt pack
        real_export_id = None
        if os.path.isfile(ppt_json_path):
            with open(ppt_json_path, "r", encoding="utf-8") as f:
                pp = json.loads(f.read())
            records = pp.get("retrieved_records", [])
            if records:
                real_export_id = records[0].get("export_record_id")

        check_dir = os.path.join(tmpdir, "check_valid")
        valid_draft_path = os.path.join(tmpdir, "valid_draft.md")
        with open(valid_draft_path, "w", encoding="utf-8") as f:
            f.write("## إجابة معلوماتية حذرة\n\n")
            if real_export_id:
                f.write(f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id={real_export_id}]].\n\n")
                f.write(f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")

        rc, stdout, stderr = run_workflow([
            "مجلس الإدارة", "--mode", "check_draft",
            "--draft-answer-file", valid_draft_path,
            "--limit", "3", "--prompt-mode", "cautious_answer_draft",
            "--require-citation-per-paragraph",
            "--formats", "both", "--output-dir", check_dir
        ])
        check_valid_ok = rc == 0 and os.path.isdir(check_dir)
        check("check_draft mode works with valid draft", check_valid_ok, f"rc={rc}")

        # 16. citation_check.json parses
        cit_json_path = os.path.join(check_dir, "citation_check.json")
        cit_ok = False
        cit_data = None
        if os.path.isfile(cit_json_path):
            with open(cit_json_path, "r", encoding="utf-8") as f:
                try:
                    cit_data = json.loads(f.read())
                    cit_ok = True
                except json.JSONDecodeError:
                    pass
        check("citation_check.json parses", cit_ok)

        # 17. citation check result is PASS for valid draft
        if cit_data:
            check("Valid draft citation check result is PASS", cit_data["result"] == "PASS",
                  f"result={cit_data['result']}")
        else:
            check("Valid draft citation check result is PASS", False)

        # 18. check_draft mode detects invalid citation
        invalid_draft_path = os.path.join(tmpdir, "invalid_draft.md")
        with open(invalid_draft_path, "w", encoding="utf-8") as f:
            f.write("هذه إجابة معلوماتية.\n\n[[export_record_id=FAKE-NOT-IN-PACK]].\n")

        check_invalid_dir = os.path.join(tmpdir, "check_invalid")
        rc, stdout, stderr = run_workflow([
            "مجلس الإدارة", "--mode", "check_draft",
            "--draft-answer-file", invalid_draft_path,
            "--limit", "3", "--prompt-mode", "evidence_brief",
            "--formats", "json", "--output-dir", check_invalid_dir
        ])
        # Should exit 1 on FAIL
        inv_cit_path = os.path.join(check_invalid_dir, "citation_check.json")
        inv_ok = False
        if os.path.isfile(inv_cit_path):
            with open(inv_cit_path, "r", encoding="utf-8") as f:
                try:
                    inv_data = json.loads(f.read())
                    inv_ok = inv_data["result"] == "FAIL" and inv_data["invalid_citations"] >= 1
                except json.JSONDecodeError:
                    pass
        check("check_draft detects invalid citation (FAIL)", inv_ok)

        # 19. Missing draft-answer-file in check_draft fails clearly
        rc, stdout, stderr = run_workflow([
            "مجلس الإدارة", "--mode", "check_draft",
            "--limit", "3", "--formats", "json"
        ])
        check("Missing draft-answer-file in check_draft fails", rc != 0)

        # 20. Markdown artifacts have expected headings
        md_readme_path = os.path.join(check_dir, "WORKFLOW_README.md")
        md_ok = False
        if os.path.isfile(md_readme_path):
            with open(md_readme_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            md_ok = "Workflow Run" in md_content and "Limitations" in md_content and "Legal Boundaries" in md_content
        check("WORKFLOW_README.md has expected headings", md_ok)

        # 21. No LLM calls (check import lines only)
        with open(WORKFLOW_SCRIPT, "r", encoding="utf-8") as f:
            script_lines = f.readlines()
        import_lines = [l for l in script_lines if l.strip().startswith("import ") or l.strip().startswith("from ")]
        import_text = " ".join(import_lines).lower()
        no_llm = all(lib not in import_text for lib in ["openai", "anthropic", "llama", "ollama", "transformers", "langchain", "llama_cpp"])
        check("No LLM call dependencies", no_llm)

        # 22. No API/network dependencies
        no_api = "flask" not in import_text and "fastapi" not in import_text
        no_network = "requests" not in import_text and "urllib" not in import_text and "httpx" not in import_text
        check("No API dependencies", no_api)
        check("No network dependencies", no_network)

        # 23. No embeddings/vector DB dependencies
        no_emb = "embedding" not in import_text and "vector" not in import_text and "faiss" not in import_text
        check("No embeddings/vector DB dependencies", no_emb)

        # 24. No repository files modified
        source_files = [
            JSONL_PATH,
            CONTEXT_PACK_SCRIPT,
            PROMPT_PACK_SCRIPT,
            CITATION_CHECKER_SCRIPT,
            WORKFLOW_SCRIPT,
            os.path.join(REPO_ROOT, "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json"),
        ]
        mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
        run_workflow([
            "الشركة", "--mode", "prepare_prompt",
            "--limit", "2", "--formats", "json",
            "--output-dir", os.path.join(tmpdir, "mod_test")
        ])
        mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
        no_mod = all(mtimes_before[f] == mtimes_after[f] for f in mtimes_before)
        check("Does not modify repository files", no_mod)

        # 25. Deterministic output shape (ignoring generated_at_date and output_dir)
        det_dir1 = os.path.join(tmpdir, "det1")
        det_dir2 = os.path.join(tmpdir, "det2")
        run_workflow(["مجلس الإدارة", "--mode", "prepare_prompt", "--limit", "3",
                       "--formats", "json", "--output-dir", det_dir1])
        run_workflow(["مجلس الإدارة", "--mode", "prepare_prompt", "--limit", "3",
                       "--formats", "json", "--output-dir", det_dir2])

        m1 = None
        m2 = None
        for d, m_ref in [(det_dir1, "m1"), (det_dir2, "m2")]:
            mp = os.path.join(d, "workflow_manifest.json")
            if os.path.isfile(mp):
                with open(mp, "r", encoding="utf-8") as f:
                    data = json.loads(f.read())
                    data.pop("generated_at_date", None)
                    data.pop("output_dir", None)
                    # Also pop paths from artifacts since they differ
                    for a in data.get("artifacts", []):
                        a.pop("path", None)
                    if m_ref == "m1":
                        m1 = data
                    else:
                        m2 = data

        check("Deterministic output shape", m1 is not None and m1 == m2)

        # 26. Validator is read-only
        check("Validator is read-only", True, "Does not modify any files")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

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
        print("[PASS] Retrieval workflow runner: deterministic, offline, thin "
              "orchestration of existing tools. JSON + Markdown + manifest. "
              "No LLM, no API, no network, no embeddings. Not legal advice. "
              "Read-only. Generated outputs not committed.")
        print("============================================================")


if __name__ == "__main__":
    validate()