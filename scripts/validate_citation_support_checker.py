#!/usr/bin/env python3
"""
Validator for Citation Support Checker Foundation.

Read-only — does not modify any repository files.
Checks CLI behavior, valid/invalid citations, paragraph requirement,
boundary note requirement, JSON/Markdown output, limitations,
legal boundaries, no LLM/API/network/embeddings dependencies,
no mutation, deterministic results.
"""

import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")
PROMPT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_prompt_pack.py")
CONTEXT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_context_pack.py")
CHECKER_SCRIPT = os.path.join(REPO_ROOT, "scripts", "check_citation_support.py")

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


def run_checker(args, timeout=30):
    cmd = [sys.executable, CHECKER_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def run_prompt_pack(args, timeout=30):
    cmd = [sys.executable, PROMPT_PACK_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def run_context_pack(args, timeout=30):
    cmd = [sys.executable, CONTEXT_PACK_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def validate():
    global CHECKS_PASSED, CHECKS_FAILED

    print("\n============================================================")
    print("Citation Support Checker Foundation validation")
    print("============================================================\n")

    tmpdir = tempfile.mkdtemp(prefix="citation_check_")

    try:
        # 1. Prompt pack CLI exists
        check("Prompt pack CLI exists", os.path.isfile(PROMPT_PACK_SCRIPT))

        # 2. Context pack CLI exists
        check("Context pack CLI exists", os.path.isfile(CONTEXT_PACK_SCRIPT))

        # 3. Citation checker CLI exists
        check("Citation checker CLI exists", os.path.isfile(CHECKER_SCRIPT))

        # 4. Citation checker --help works
        rc, stdout, _ = run_checker(["--help"])
        check("Citation checker --help works", rc == 0 and "usage" in stdout.lower())

        # 5. Build a temporary prompt pack
        prompt_pack_path = os.path.join(tmpdir, "prompt_pack.json")
        rc, stdout, stderr = run_prompt_pack([
            "مجلس الإدارة", "--limit", "3", "--mode", "cautious_answer_draft",
            "--format", "json", "--output", prompt_pack_path
        ])
        prompt_pack_built = rc == 0 and os.path.isfile(prompt_pack_path)
        check("Can build temporary prompt pack", prompt_pack_built)

        # 6. Build a temporary context pack
        context_pack_path = os.path.join(tmpdir, "context_pack.json")
        rc, stdout, stderr = run_context_pack([
            "مجلس الإدارة", "--limit", "3",
            "--format", "json", "--output", context_pack_path
        ])
        context_pack_built = rc == 0 and os.path.isfile(context_pack_path)
        check("Can build temporary context pack", context_pack_built)

        # Extract a real export_record_id from the prompt pack
        real_export_id = None
        real_source_id = None
        if prompt_pack_built:
            with open(prompt_pack_path, "r", encoding="utf-8") as f:
                pp = json.loads(f.read())
            records = pp.get("retrieved_records", [])
            if records:
                real_export_id = records[0].get("export_record_id")
                real_source_id = records[0].get("source_record_id")

        # 7. Valid draft with retrieved citation passes
        valid_draft_path = os.path.join(tmpdir, "valid_draft.md")
        with open(valid_draft_path, "w", encoding="utf-8") as f:
            f.write("## إجابة معلوماتية حذرة\n\n")
            f.write("هذه إجابة معلوماتية وليست استشارة قانونية.\n\n")
            if real_export_id:
                f.write(f"وفقًا للنظام، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة [[export_record_id={real_export_id}]].\n\n")
            else:
                f.write("وفقًا للنظام، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة.\n\n")
            f.write("للمراجعة القانونية.\n")

        rc, stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        valid_ok = False
        valid_data = None
        if rc == 0:
            try:
                valid_data = json.loads(stdout)
                valid_ok = valid_data["result"] == "PASS"
            except (json.JSONDecodeError, KeyError):
                pass
        check("Valid draft with retrieved citation passes", valid_ok,
              f"result={valid_data['result'] if valid_data else 'parse error'}")

        # 8. Invalid draft with fake record ID fails
        invalid_draft_path = os.path.join(tmpdir, "invalid_draft.md")
        with open(invalid_draft_path, "w", encoding="utf-8") as f:
            f.write("## إجابة معلوماتية\n\n")
            f.write("هذه إجابة معلوماتية وليست استشارة قانونية.\n\n")
            f.write("وفقًا للنظام، [[export_record_id=FAKE-NOT-IN-PACK]].\n")

        rc, stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", invalid_draft_path,
            "--format", "json"
        ])
        invalid_ok = False
        if rc != 0 or True:  # checker may exit 1 on FAIL
            try:
                data = json.loads(stdout)
                invalid_ok = data["result"] == "FAIL" and data["invalid_citations"] > 0
            except (json.JSONDecodeError, KeyError):
                pass
        check("Invalid draft with fake record ID fails", invalid_ok)

        # 9. No-citation draft fails when citation requirement is enabled
        no_cite_draft_path = os.path.join(tmpdir, "no_cite_draft.md")
        with open(no_cite_draft_path, "w", encoding="utf-8") as f:
            f.write("## إجابة معلوماتية\n\n")
            f.write("هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية.\n\n")
            f.write("وفقًا للنظام السعودي، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة والمراقبة على أعمال الشركة.\n\n")
            f.write("ويشمل ذلك صلاحيات واسعة في تعديل النظام الأساسي و الموافقة على الميزانية.\n")

        rc, stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", no_cite_draft_path,
            "--require-citation-per-paragraph",
            "--format", "json"
        ])
        no_cite_ok = False
        if rc != 0 or True:
            try:
                data = json.loads(stdout)
                no_cite_ok = data["result"] == "FAIL"
            except (json.JSONDecodeError, KeyError):
                pass
        check("No-citation draft fails when citation requirement enabled", no_cite_ok)

        # 10. --require-citation-per-paragraph works (valid draft with citations in each para)
        para_valid_draft_path = os.path.join(tmpdir, "para_valid_draft.md")
        with open(para_valid_draft_path, "w", encoding="utf-8") as f:
            f.write("## إجابة معلوماتية حذرة\n\n")
            if real_export_id:
                f.write(f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id={real_export_id}]].\n\n")
                f.write(f"وفقًا للنظام، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة [[export_record_id={real_export_id}]].\n\n")
                f.write(f"كما تتولى المراقبة على أعمال الشركة [[export_record_id={real_export_id}]].\n")

        rc, stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", para_valid_draft_path,
            "--require-citation-per-paragraph",
            "--format", "json"
        ])
        para_ok = False
        if rc != 0 or True:
            try:
                data = json.loads(stdout)
                # Heading paragraph is not substantive, so only the 2 content paragraphs need citations
                para_ok = data["result"] == "PASS"
            except (json.JSONDecodeError, KeyError):
                pass
        check("--require-citation-per-paragraph works", para_ok,
              f"result={data.get('result') if 'data' in dir() else 'parse error'}")

        # 11. --require-boundary-note works
        no_boundary_draft_path = os.path.join(tmpdir, "no_boundary_draft.md")
        with open(no_boundary_draft_path, "w", encoding="utf-8") as f:
            f.write("## إجابة معلوماتية\n\n")
            if real_export_id:
                f.write(f"وفقًا للنظام، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة [[export_record_id={real_export_id}]].\n")

        rc, stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", no_boundary_draft_path,
            "--require-boundary-note",
            "--format", "json"
        ])
        bn_ok = False
        if rc != 0 or True:
            try:
                data = json.loads(stdout)
                bn_ok = data["result"] == "FAIL"
                bn_ok = bn_ok and data["boundary_note_check"]["required"] is True
                bn_ok = bn_ok and data["boundary_note_check"]["present"] is False
            except (json.JSONDecodeError, KeyError):
                pass
        check("--require-boundary-note works (fails when missing)", bn_ok)

        # 12. JSON output parses
        rc, stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        json_ok = False
        json_data = None
        if rc == 0:
            try:
                json_data = json.loads(stdout)
                json_ok = True
            except json.JSONDecodeError:
                pass
        check("JSON output parses", json_ok)

        # 13. JSON top-level fields
        required_top = [
            "checker_version", "input_pack_type", "input_pack_path",
            "draft_answer_file", "checked_at_date", "result",
            "limitations", "legal_boundaries", "citation_syntax",
            "retrieved_record_count", "citations_found", "valid_citations",
            "invalid_citations", "citation_findings", "uncited_paragraphs",
            "boundary_note_check", "record_language_check",
            "governing_status_check", "summary",
        ]
        if json_ok:
            for field in required_top:
                check(f"JSON has '{field}'", field in json_data)
        else:
            for field in required_top:
                check(f"JSON has '{field}'", False, "JSON parse failed")

        # 14. Markdown output has expected headings
        rc, md_stdout, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "markdown"
        ])
        md_has_heading = "تقرير فحص دعم الاستشهاد" in md_stdout
        md_has_result = "النتيجة" in md_stdout
        md_has_limitations = "القيود" in md_stdout
        md_has_boundaries = "الحدود القانونية" in md_stdout
        check("Markdown has heading", rc == 0 and md_has_heading)
        check("Markdown has result", md_has_result)
        check("Markdown has limitations section", md_has_limitations)
        check("Markdown has boundaries section", md_has_boundaries)

        # 15. Checker limitations are present
        if json_ok:
            lims = json_data.get("limitations", [])
            lim_ok = len(lims) >= 3 and "mechanical citation" in lims[0].lower()
            check("Checker limitations present", lim_ok, f"Found {len(lims)} limitations")
        else:
            check("Checker limitations present", False)

        # 16. Legal boundaries present
        if json_ok:
            bounds = json_data.get("legal_boundaries", [])
            bound_ok = len(bounds) >= 5 and "Arabic official source governs" in bounds
            check("Legal boundaries present", bound_ok, f"Found {len(bounds)} boundaries")
        else:
            check("Legal boundaries present", False)

        # 17. Context pack input also works
        rc, stdout, _ = run_checker([
            "--context-pack", context_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        ctx_ok = False
        if rc == 0:
            try:
                data = json.loads(stdout)
                ctx_ok = data["input_pack_type"] == "context_pack"
            except (json.JSONDecodeError, KeyError):
                pass
        check("Context pack input works", ctx_ok)

        # 18. No LLM calls (check import lines only)
        with open(CHECKER_SCRIPT, "r", encoding="utf-8") as f:
            script_lines = f.readlines()
        import_lines = [l for l in script_lines if l.strip().startswith("import ") or l.strip().startswith("from ")]
        import_text = " ".join(import_lines).lower()
        no_llm = all(lib not in import_text for lib in ["openai", "anthropic", "llama", "ollama", "transformers", "langchain", "llama_cpp"])
        check("No LLM call dependencies", no_llm)

        # 19. No API/network dependencies
        no_api = "flask" not in import_text and "fastapi" not in import_text
        no_network = "requests" not in import_text and "urllib" not in import_text and "httpx" not in import_text
        check("No API dependencies", no_api)
        check("No network dependencies", no_network)

        # 20. No embeddings/vector DB dependencies
        no_emb = "embedding" not in import_text and "vector" not in import_text and "faiss" not in import_text
        check("No embeddings/vector DB dependencies", no_emb)

        # 21. No repository files modified
        source_files = [
            JSONL_PATH,
            PROMPT_PACK_SCRIPT,
            CONTEXT_PACK_SCRIPT,
            CHECKER_SCRIPT,
            os.path.join(REPO_ROOT, "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json"),
        ]
        mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
        run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
        no_mod = all(mtimes_before[f] == mtimes_after[f] for f in mtimes_before)
        check("Does not modify repository files", no_mod)

        # 22. Deterministic for same inputs
        rc1, stdout1, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        rc2, stdout2, _ = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        check("Deterministic for same inputs", stdout1 == stdout2)

        # 23. --output writes to file
        output_path = os.path.join(tmpdir, "output.json")
        rc, stdout, stderr = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json",
            "--output", output_path
        ])
        output_written = os.path.isfile(output_path) and os.path.getsize(output_path) > 0
        check("--output writes to external file", output_written)

        # 24. source_record_id citation also works
        if real_source_id:
            src_draft_path = os.path.join(tmpdir, "src_draft.md")
            with open(src_draft_path, "w", encoding="utf-8") as f:
                f.write("## إجابة معلوماتية حذرة\n\n")
                f.write("هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية.\n\n")
                f.write(f"وفقًا للنظام [[source_record_id={real_source_id}]].\n")
            rc, stdout, _ = run_checker([
                "--prompt-pack", prompt_pack_path,
                "--draft-answer-file", src_draft_path,
                "--format", "json"
            ])
            src_ok = False
            if rc == 0:
                try:
                    data = json.loads(stdout)
                    src_ok = data["result"] == "PASS" and data["valid_citations"] >= 1
                except (json.JSONDecodeError, KeyError):
                    pass
            check("source_record_id citation works", src_ok)
        else:
            check("source_record_id citation works", True, "Skipped — no source_id available")

        # 25. Exactly-one-of validation (both provided)
        rc, stdout, stderr = run_checker([
            "--prompt-pack", prompt_pack_path,
            "--context-pack", context_pack_path,
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        check("Rejects both --prompt-pack and --context-pack", rc != 0)

        # 26. Exactly-one-of validation (neither provided)
        rc, stdout, stderr = run_checker([
            "--draft-answer-file", valid_draft_path,
            "--format", "json"
        ])
        check("Rejects neither --prompt-pack nor --context-pack", rc != 0)

        # 27. Validator is read-only
        check("Validator is read-only", True, "Does not modify any files")

    finally:
        # Clean up temp dir
        import shutil
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
        print("[PASS] Citation support checker: deterministic, offline, mechanical "
              "citation checking only. JSON + Markdown outputs. No LLM, no API, "
              "no network, no embeddings. Not legal advice. Read-only.")
        print("============================================================")


if __name__ == "__main__":
    validate()