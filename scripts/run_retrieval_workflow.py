#!/usr/bin/env python3
"""
Retrieval Workflow Runner — Primary Arabic Governing Records

Deterministic, offline workflow runner that orchestrates existing corpus
tools into one practical end-to-end workflow.

Mode 1 — prepare_prompt:
  Takes a query, builds a retrieval context pack and a retrieval prompt pack,
  writes all artifacts + a workflow manifest to an output directory.

Mode 2 — check_draft:
  Takes a query + a draft answer file, builds context + prompt packs,
  runs the citation support checker against the draft, writes all artifacts
  + citation check report + workflow manifest.

This is NOT RAG.
This does NOT call an LLM.
This does NOT generate legal answers.
This does NOT generate legal advice.
This does NOT interpret legal text.
This does NOT verify legal correctness.
This does NOT verify semantic support.
This does NOT create embeddings, semantic search, API, UI, database, or network.

It is a thin orchestration layer over existing deterministic tools.

Usage:
  python3 scripts/run_retrieval_workflow.py "مجلس الإدارة"
  python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode prepare_prompt --limit 3
  python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode check_draft --draft-answer-file /tmp/draft.md
  python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode check_draft --draft-answer-file /tmp/draft.md --require-citation-per-paragraph
  python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" --prompt-mode cautious_answer_draft --formats both
  python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" --output-dir /tmp/corpus_workflow
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import date
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import existing tools — no logic duplication
sys.path.insert(0, REPO_ROOT)
from scripts.build_retrieval_context_pack import build_context_pack, format_markdown as format_context_markdown
from scripts.build_retrieval_prompt_pack import build_prompt_pack, format_markdown as format_prompt_markdown, PROMPT_MODES
from scripts.check_citation_support import run_check, format_markdown as format_citation_markdown, load_pack, detect_pack_type
from scripts.search_primary_arabic_export import normalize_arabic, load_records

WORKFLOW_VERSION = "1.0"
SOURCE_EXPORT_FILE = "data/exports/v1/primary_arabic_governing_records.jsonl"
RETRIEVAL_METHOD = "deterministic_lexical_search"

# Read stable baseline from corpus registry instead of git rev-parse HEAD
REGISTRY_PATH = os.path.join(REPO_ROOT, "data", "corpus_registry", "corpus_registry.json")

LEGAL_BOUNDARIES = [
    "Arabic official source governs",
    "Not legal advice",
    "Not official translation",
    "No legal interpretation by the workflow runner",
    "No generated legal conclusions",
    "No legal correctness judgment",
    "No semantic support verification",
    "No English/Chinese records",
    "No trilingual alignment",
    "No public release",
    "No LLM calls, no API, no network, no embeddings",
    "Workflow runner orchestrates deterministic local tools only",
]

LIMITATIONS = [
    "The workflow prepares retrieval and prompt/citation artifacts only.",
    "It does not produce or evaluate legal correctness.",
    "Citation checker is mechanical ID validation only, not semantic/legal support.",
    "repository-owner legal review active; external legal review optional for enterprise/official adoption",
]


def get_stable_baseline() -> str:
    """Read baseline_commit from corpus registry (stable, not git HEAD)."""
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.loads(f.read())
        return registry.get("baseline_commit", "unknown")
    except (FileNotFoundError, json.JSONDecodeError):
        return "unknown"


def run_workflow(
    query: str,
    mode: str = "prepare_prompt",
    draft_answer_file: Optional[str] = None,
    limit: int = 5,
    track: Optional[str] = None,
    record_type: Optional[str] = None,
    prompt_mode: str = "evidence_brief",
    include_full_text: bool = False,
    output_dir: Optional[str] = None,
    formats: str = "both",
    require_citation_per_paragraph: bool = False,
    require_boundary_note: bool = False,
) -> dict:
    """Run the retrieval workflow and return the manifest dict.

    Artifacts are written to output_dir (or a temporary directory).
    Returns the workflow manifest.
    """
    # Validate mode-specific requirements
    if mode == "check_draft":
        if not draft_answer_file:
            raise ValueError("check_draft mode requires --draft-answer-file")
        if not os.path.isfile(draft_answer_file):
            raise FileNotFoundError(f"Draft answer file not found: {draft_answer_file}")

    # Create output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = tempfile.mkdtemp(prefix="corpus_workflow_")

    # Build context pack
    context_pack = build_context_pack(
        query=query,
        limit=limit,
        track=track,
        record_type=record_type,
        include_full_text=include_full_text,
    )

    # Write context pack artifacts
    artifacts = []
    if formats in ("json", "both"):
        ctx_json_path = os.path.join(output_dir, "context_pack.json")
        with open(ctx_json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(context_pack, ensure_ascii=False, indent=2))
            f.write("\n")
        artifacts.append({"name": "context_pack.json", "path": ctx_json_path})

    if formats in ("markdown", "both"):
        ctx_md_path = os.path.join(output_dir, "context_pack.md")
        ctx_md = format_context_markdown(context_pack, include_full_text=include_full_text)
        with open(ctx_md_path, "w", encoding="utf-8") as f:
            f.write(ctx_md)
            f.write("\n")
        artifacts.append({"name": "context_pack.md", "path": ctx_md_path})

    # Build prompt pack
    prompt_pack = build_prompt_pack(
        query=query,
        limit=limit,
        track=track,
        record_type=record_type,
        mode=prompt_mode,
        include_full_text=include_full_text,
    )

    # Write prompt pack artifacts
    if formats in ("json", "both"):
        ppt_json_path = os.path.join(output_dir, "prompt_pack.json")
        with open(ppt_json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(prompt_pack, ensure_ascii=False, indent=2))
            f.write("\n")
        artifacts.append({"name": "prompt_pack.json", "path": ppt_json_path})

    if formats in ("markdown", "both"):
        ppt_md_path = os.path.join(output_dir, "prompt_pack.md")
        ppt_md = format_prompt_markdown(prompt_pack, include_full_text=include_full_text)
        with open(ppt_md_path, "w", encoding="utf-8") as f:
            f.write(ppt_md)
            f.write("\n")
        artifacts.append({"name": "prompt_pack.md", "path": ppt_md_path})

    # Citation check if check_draft mode
    citation_check_result = None
    if mode == "check_draft":
        # Run citation check using the prompt pack we just built
        with open(draft_answer_file, "r", encoding="utf-8") as f:
            draft_text = f.read()

        cit_result = run_check(
            pack=prompt_pack,
            pack_path=ppt_json_path,
            pack_type="prompt_pack",
            draft_text=draft_text,
            draft_path=draft_answer_file,
            require_citation_per_paragraph=require_citation_per_paragraph,
            require_boundary_note=require_boundary_note,
        )

        # Write citation check artifacts
        if formats in ("json", "both"):
            cit_json_path = os.path.join(output_dir, "citation_check.json")
            with open(cit_json_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(cit_result, ensure_ascii=False, indent=2))
                f.write("\n")
            artifacts.append({"name": "citation_check.json", "path": cit_json_path})

        if formats in ("markdown", "both"):
            cit_md_path = os.path.join(output_dir, "citation_check.md")
            cit_md = format_citation_markdown(cit_result)
            with open(cit_md_path, "w", encoding="utf-8") as f:
                f.write(cit_md)
                f.write("\n")
            artifacts.append({"name": "citation_check.md", "path": cit_md_path})

        citation_check_result = {
            "result": cit_result["result"],
            "valid_citations": cit_result["valid_citations"],
            "invalid_citations": cit_result["invalid_citations"],
            "uncited_paragraphs": len(cit_result["uncited_paragraphs"]),
            "citations_found": cit_result["citations_found"],
        }

    # Build workflow manifest
    filters = {}
    if track:
        filters["track"] = track
    if record_type:
        filters["record_type"] = record_type

    manifest = {
        "workflow_version": WORKFLOW_VERSION,
        "mode": mode,
        "query": query,
        "normalized_query": normalize_arabic(query),
        "generated_at_date": date.today().isoformat(),
        "baseline_commit": get_stable_baseline(),
        "output_dir": output_dir,
        "source_export_file": SOURCE_EXPORT_FILE,
        "source_export_record_count": context_pack["source_export_record_count"],
        "retrieval_method": RETRIEVAL_METHOD,
        "limit": limit,
        "filters": filters,
        "prompt_mode": prompt_mode,
        "include_full_text": include_full_text,
        "formats": formats,
        "artifacts": [{"name": a["name"], "path": a["path"]} for a in artifacts],
        "legal_boundaries": LEGAL_BOUNDARIES,
        "limitations": LIMITATIONS,
        "hygiene": {
            "no_committed_run_outputs": True,
            "no_llm_calls": True,
            "no_api": True,
            "no_network": True,
            "no_embeddings": True,
            "read_only_source_files": True,
        },
    }

    if draft_answer_file:
        manifest["draft_answer_file"] = draft_answer_file
    if citation_check_result:
        manifest["citation_check_result"] = citation_check_result

    # Write manifest
    manifest_path = os.path.join(output_dir, "workflow_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2))
        f.write("\n")
    artifacts.append({"name": "workflow_manifest.json", "path": manifest_path})

    # Write WORKFLOW_README.md
    readme_path = os.path.join(output_dir, "WORKFLOW_README.md")
    readme_lines = [
        "# Workflow Run — Retrieval Workflow Runner",
        "",
        f"**Query:** {query}",
        f"**Mode:** {mode}",
        f"**Date:** {manifest['generated_at_date']}",
        f"**Baseline:** {manifest['baseline_commit']}",
        "",
        "## Artifacts",
        "",
    ]
    for a in artifacts:
        readme_lines.append(f"- `{a['name']}`")
    readme_lines.append("")
    readme_lines.append("## Limitations")
    readme_lines.append("")
    for lim in LIMITATIONS:
        readme_lines.append(f"- {lim}")
    readme_lines.append("")
    readme_lines.append("## Legal Boundaries")
    readme_lines.append("")
    for b in LEGAL_BOUNDARIES:
        readme_lines.append(f"- {b}")
    readme_lines.append("")
    if citation_check_result:
        result_emoji = "✅" if citation_check_result["result"] == "PASS" else "❌"
        readme_lines.append(f"## Citation Check Result: {result_emoji} {citation_check_result['result']}")
        readme_lines.append("")
        readme_lines.append(f"- Valid citations: {citation_check_result['valid_citations']}")
        readme_lines.append(f"- Invalid citations: {citation_check_result['invalid_citations']}")
        readme_lines.append(f"- Uncited paragraphs: {citation_check_result['uncited_paragraphs']}")
        readme_lines.append("")
    readme_lines.append("> This is a workflow run output — not legal advice. Not an answer. Arabic official source governs.")
    readme_lines.append("")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines))
        f.write("\n")
    artifacts.append({"name": "WORKFLOW_README.md", "path": readme_path})

    # Update manifest with final artifacts list and re-write
    manifest["artifacts"] = [{"name": a["name"], "path": a["path"]} for a in artifacts]
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2))
        f.write("\n")

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Run a retrieval workflow: context pack + prompt pack + optional citation check. "
                     "Deterministic, offline. Thin orchestration of existing tools. "
                     "Not RAG. Not legal advice. Not an API.",
        prog="run_retrieval_workflow",
    )
    parser.add_argument("query", help="Search query (Arabic)")
    parser.add_argument("--mode", choices=["prepare_prompt", "check_draft"], default="prepare_prompt",
                        help="Workflow mode (default: prepare_prompt)")
    parser.add_argument("--draft-answer-file", default=None,
                        help="Path to draft answer file (required for check_draft mode)")
    parser.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--track", default=None,
                        help="Filter by track: companies_law, implementing_regulations_general, "
                             "implementing_regulations_listed_joint_stock")
    parser.add_argument("--record-type", default=None,
                        help="Filter by record type: article, form, appendix")
    parser.add_argument("--prompt-mode", choices=PROMPT_MODES, default="evidence_brief",
                        help="Prompt mode (default: evidence_brief)")
    parser.add_argument("--include-full-text", action="store_true",
                        help="Include full text_ar in records")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: temporary directory)")
    parser.add_argument("--formats", choices=["json", "markdown", "both"], default="both",
                        help="Output formats (default: both)")
    parser.add_argument("--require-citation-per-paragraph", action="store_true",
                        help="Require every substantive paragraph to have a valid citation (check_draft only)")
    parser.add_argument("--require-boundary-note", action="store_true",
                        help="Require draft to contain a boundary note phrase (check_draft only)")
    args = parser.parse_args()

    if not os.path.isfile(JSONL_PATH):
        print(f"ERROR: Export JSONL not found: {JSONL_PATH}", file=sys.stderr)
        sys.exit(1)

    if args.mode == "check_draft" and not args.draft_answer_file:
        print("ERROR: check_draft mode requires --draft-answer-file", file=sys.stderr)
        sys.exit(2)

    if args.draft_answer_file and not os.path.isfile(args.draft_answer_file):
        print(f"ERROR: Draft answer file not found: {args.draft_answer_file}", file=sys.stderr)
        sys.exit(1)

    try:
        manifest = run_workflow(
            query=args.query,
            mode=args.mode,
            draft_answer_file=args.draft_answer_file,
            limit=args.limit,
            track=args.track,
            record_type=args.record_type,
            prompt_mode=args.prompt_mode,
            include_full_text=args.include_full_text,
            output_dir=args.output_dir,
            formats=args.formats,
            require_citation_per_paragraph=args.require_citation_per_paragraph,
            require_boundary_note=args.require_boundary_note,
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Print manifest summary to stdout
    print(f"Workflow complete: {manifest['mode']}")
    print(f"Output directory: {manifest['output_dir']}")
    print(f"Artifacts: {len(manifest['artifacts'])}")
    if manifest.get("citation_check_result"):
        ccr = manifest["citation_check_result"]
        print(f"Citation check: {ccr['result']} (valid={ccr['valid_citations']}, invalid={ccr['invalid_citations']})")

    # Exit non-zero if citation check failed
    if manifest.get("citation_check_result", {}).get("result") == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()