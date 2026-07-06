#!/usr/bin/env python3
"""
Citation Support Checker — Primary Arabic Governing Records

Deterministic, offline citation support checker. Takes a draft answer
file and a retrieval prompt pack or context pack, then mechanically
checks whether cited record IDs exist in the supplied pack.

This checker does NOT verify semantic support.
This checker does NOT verify legal correctness.
This checker does NOT interpret legal text.
This checker does NOT generate answers.
This checker does NOT call any LLM.
This checker does NOT provide legal advice.
This checker does NOT build RAG, embeddings, semantic search, API, UI,
database, or network calls.

It only verifies mechanical citation presence and ID validity.

Usage:
  python3 scripts/check_citation_support.py --prompt-pack /tmp/prompt_pack.json --draft-answer-file /tmp/draft.md
  python3 scripts/check_citation_support.py --context-pack /tmp/context_pack.json --draft-answer-file /tmp/draft.md
  python3 scripts/check_citation_support.py --prompt-pack /tmp/prompt_pack.json --draft-answer-file /tmp/draft.md --format json
  python3 scripts/check_citation_support.py --prompt-pack /tmp/prompt_pack.json --draft-answer-file /tmp/draft.md --format markdown
  python3 scripts/check_citation_support.py --prompt-pack /tmp/prompt_pack.json --draft-answer-file /tmp/draft.md --require-citation-per-paragraph
  python3 scripts/check_citation_support.py --prompt-pack /tmp/prompt_pack.json --draft-answer-file /tmp/draft.md --require-boundary-note
  python3 scripts/check_citation_support.py --prompt-pack /tmp/prompt_pack.json --draft-answer-file /tmp/draft.md --output /tmp/citation_check.json
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from typing import Optional

CHECKER_VERSION = "1.0"

LEGAL_BOUNDARIES = [
    "Arabic official source governs",
    "Not legal advice",
    "Not official translation",
    "No legal interpretation by the checker",
    "No generated legal conclusions",
    "No semantic/legal correctness judgment",
    "No English/Chinese records",
    "No trilingual alignment",
    "No public release",
]

LIMITATIONS = [
    "This checker only verifies mechanical citation presence and ID validity.",
    "It does not verify that the cited record semantically supports the sentence.",
    "It does not verify legal correctness.",
    "It does not replace repository-owner legal review active; external legal review optional for enterprise/official adoption.",
]

CITATION_SYNTAX = [
    "[[export_record_id=<ID>]] — cites a record by its export_record_id",
    "[[source_record_id=<ID>]] — cites a record by its source_record_id",
]

BOUNDARY_NOTE_PHRASES = [
    "ليست استشارة قانونية",
    "للمراجعة القانونية",
    "not legal advice",
    "legal review",
]

# Citation regex patterns
CITATION_PATTERN = re.compile(
    r"\[\[(export_record_id|source_record_id)=([^\]]+)\]\]"
)


def load_pack(pack_path: str) -> dict:
    """Load a prompt pack or context pack from a JSON file."""
    with open(pack_path, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def extract_retrieved_records(pack: dict) -> list:
    """Extract retrieved records from a prompt pack or context pack.

    Prompt packs use 'retrieved_records', context packs use 'records'.
    """
    if "retrieved_records" in pack:
        return pack["retrieved_records"]
    elif "records" in pack:
        return pack["records"]
    else:
        return []


def detect_pack_type(pack: dict) -> str:
    """Detect whether the pack is a prompt pack or context pack."""
    if "prompt_pack_version" in pack:
        return "prompt_pack"
    elif "pack_version" in pack:
        return "context_pack"
    else:
        return "unknown"


def build_allowed_citations(records: list) -> dict:
    """Build sets of allowed export_record_id and source_record_id values."""
    export_ids = {}
    source_ids = {}
    for rec in records:
        eid = rec.get("export_record_id")
        sid = rec.get("source_record_id")
        if eid:
            export_ids[eid] = rec
        if sid:
            source_ids[sid] = rec
    return {"export_record_id": export_ids, "source_record_id": source_ids}


def extract_citations(text: str) -> list:
    """Extract all citations from text using the accepted syntax.

    Returns list of dicts: {citation_text, citation_type, cited_id, match_start, match_end}
    """
    citations = []
    for match in CITATION_PATTERN.finditer(text):
        citations.append({
            "citation_text": match.group(0),
            "citation_type": match.group(1),
            "cited_id": match.group(2).strip(),
            "match_start": match.start(),
            "match_end": match.end(),
        })
    return citations


def split_paragraphs(text: str) -> list:
    """Split text into paragraphs. A paragraph is a non-empty block
    separated by double newlines. Single newlines within a block are
    treated as part of the same paragraph.

    Returns list of {index, text, start, end}.
    """
    paragraphs = []
    blocks = text.split("\n\n")
    idx = 0
    offset = 0
    for block in blocks:
        stripped = block.strip()
        if stripped:
            paragraphs.append({
                "index": idx,
                "text": stripped,
                "start": offset,
                "end": offset + len(block),
            })
            idx += 1
        offset += len(block) + 2  # +2 for the \n\n separator
    return paragraphs


def is_substantive_paragraph(text: str) -> bool:
    """Check if a paragraph is substantive (not just a heading, boundary note, or metadata)."""
    stripped = text.strip()
    if not stripped:
        return False
    # Skip very short paragraphs (< 20 chars) that are likely headings/labels
    if len(stripped) < 20:
        return False
    # Skip lines that look like headings (start with # or are all caps short)
    if stripped.startswith("#"):
        return False
    # Skip lines that are just citation markers
    if CITATION_PATTERN.fullmatch(stripped):
        return False
    return True


def find_paragraph_for_citation(citation: dict, paragraphs: list) -> Optional[int]:
    """Find which paragraph index a citation belongs to."""
    cite_start = citation["match_start"]
    cite_end = citation["match_end"]
    for para in paragraphs:
        # Citation is within or at the end of this paragraph
        if para["start"] <= cite_start < para["end"]:
            return para["index"]
        # Citation at the very end (boundary case)
        if cite_start >= para["end"] - 2 and cite_start <= para["end"] + 2:
            return para["index"]
    # If no paragraph found, assign to last paragraph if exists
    if paragraphs:
        return paragraphs[-1]["index"]
    return None


def check_boundary_note(text: str) -> bool:
    """Check if the draft answer contains a boundary note phrase."""
    text_lower = text.lower()
    for phrase in BOUNDARY_NOTE_PHRASES:
        if phrase.lower() in text_lower:
            return True
    return False


def run_check(
    pack: dict,
    pack_path: str,
    pack_type: str,
    draft_text: str,
    draft_path: str,
    require_citation_per_paragraph: bool = False,
    require_boundary_note: bool = False,
) -> dict:
    """Run the citation support check and return the result dict."""

    records = extract_retrieved_records(pack)
    allowed = build_allowed_citations(records)

    citations = extract_citations(draft_text)
    paragraphs = split_paragraphs(draft_text)

    # Validate each citation
    citation_findings = []
    valid_count = 0
    invalid_count = 0

    for cite in citations:
        cite_type = cite["citation_type"]
        cited_id = cite["cited_id"]
        allowed_set = allowed.get(cite_type, {})

        if cited_id in allowed_set:
            matched_rec = allowed_set[cited_id]
            para_idx = find_paragraph_for_citation(cite, paragraphs)
            citation_findings.append({
                "citation_text": cite["citation_text"],
                "citation_type": cite_type,
                "cited_id": cited_id,
                "valid": True,
                "matched_record": {
                    "export_record_id": matched_rec.get("export_record_id"),
                    "source_track_id": matched_rec.get("source_track_id"),
                    "title_ar": matched_rec.get("title_ar"),
                },
                "paragraph_index": para_idx,
                "message": "Citation references a retrieved record in the supplied pack.",
            })
            valid_count += 1
        else:
            para_idx = find_paragraph_for_citation(cite, paragraphs)
            citation_findings.append({
                "citation_text": cite["citation_text"],
                "citation_type": cite_type,
                "cited_id": cited_id,
                "valid": False,
                "matched_record": None,
                "paragraph_index": para_idx,
                "message": f"Citation references a record ID ({cited_id}) not found in the supplied pack.",
            })
            invalid_count += 1

    # Check uncited paragraphs
    cited_paragraph_indices = set()
    for cf in citation_findings:
        if cf["valid"] and cf["paragraph_index"] is not None:
            cited_paragraph_indices.add(cf["paragraph_index"])

    uncited_paragraphs = []
    if require_citation_per_paragraph:
        for para in paragraphs:
            if is_substantive_paragraph(para["text"]) and para["index"] not in cited_paragraph_indices:
                uncited_paragraphs.append({
                    "paragraph_index": para["index"],
                    "text_preview": para["text"][:100] + ("..." if len(para["text"]) > 100 else ""),
                    "message": "Substantive paragraph has no valid citation.",
                })

    # Boundary note check
    boundary_note_present = check_boundary_note(draft_text)
    boundary_note_check = {
        "required": require_boundary_note,
        "present": boundary_note_present,
        "passed": (not require_boundary_note) or boundary_note_present,
    }

    # Record language check (all retrieved records should be ar)
    all_ar = all(r.get("language") == "ar" for r in records) if records else True
    record_language_check = {
        "all_records_arabic": all_ar,
        "passed": all_ar,
    }

    # Governing status check
    all_governing = all(
        r.get("governing_status") == "arabic_governing_text" for r in records
    ) if records else True
    governing_status_check = {
        "all_records_arabic_governing_text": all_governing,
        "passed": all_governing,
    }

    # Overall result
    has_citations = len(citations) > 0
    all_citations_valid = invalid_count == 0
    no_uncited = len(uncited_paragraphs) == 0
    boundary_ok = boundary_note_check["passed"]
    lang_ok = record_language_check["passed"]
    gov_ok = governing_status_check["passed"]

    if require_citation_per_paragraph:
        result = "PASS" if (has_citations and all_citations_valid and no_uncited and boundary_ok and lang_ok and gov_ok) else "FAIL"
    elif require_boundary_note:
        result = "PASS" if (has_citations and all_citations_valid and boundary_ok and lang_ok and gov_ok) else "FAIL"
    else:
        result = "PASS" if (has_citations and all_citations_valid and lang_ok and gov_ok) else "FAIL"

    summary = {
        "result": result,
        "total_citations": len(citations),
        "valid_citations": valid_count,
        "invalid_citations": invalid_count,
        "uncited_paragraphs": len(uncited_paragraphs),
        "retrieved_record_count": len(records),
        "boundary_note_present": boundary_note_present,
    }

    return {
        "checker_version": CHECKER_VERSION,
        "input_pack_type": pack_type,
        "input_pack_path": pack_path,
        "draft_answer_file": draft_path,
        "checked_at_date": date.today().isoformat(),
        "result": result,
        "limitations": LIMITATIONS,
        "legal_boundaries": LEGAL_BOUNDARIES,
        "citation_syntax": CITATION_SYNTAX,
        "retrieved_record_count": len(records),
        "citations_found": len(citations),
        "valid_citations": valid_count,
        "invalid_citations": invalid_count,
        "citation_findings": citation_findings,
        "uncited_paragraphs": uncited_paragraphs,
        "boundary_note_check": boundary_note_check,
        "record_language_check": record_language_check,
        "governing_status_check": governing_status_check,
        "summary": summary,
    }


def format_markdown(result: dict) -> str:
    """Format citation check result as Markdown."""
    lines = []
    lines.append("# تقرير فحص دعم الاستشهاد")
    lines.append("")

    result_emoji = "✅" if result["result"] == "PASS" else "❌"
    lines.append(f"**النتيجة:** {result_emoji} {result['result']}")
    lines.append("")

    # Limitations
    lines.append("## القيود")
    lines.append("")
    for lim in result["limitations"]:
        lines.append(f"- {lim}")
    lines.append("")

    # Legal boundaries
    lines.append("## الحدود القانونية")
    lines.append("")
    for b in result["legal_boundaries"]:
        lines.append(f"- {b}")
    lines.append("")

    # Citation syntax
    lines.append("## صيغة الاستشهاد")
    lines.append("")
    for s in result["citation_syntax"]:
        lines.append(f"- `{s}`")
    lines.append("")

    # Summary
    s = result["summary"]
    lines.append("## الملخص")
    lines.append("")
    lines.append(f"- **النتيجة:** {s['result']}")
    lines.append(f"- **إجمالي الاستشهادات:** {s['total_citations']}")
    lines.append(f"- **استشهادات صالحة:** {s['valid_citations']}")
    lines.append(f"- **استشهادات غير صالحة:** {s['invalid_citations']}")
    lines.append(f"- **فقرات بلا استشهاد:** {s['uncited_paragraphs']}")
    lines.append(f"- **سجلات مسترجعة:** {s['retrieved_record_count']}")
    lines.append(f"- **ملاحظة حدية موجودة:** {s['boundary_note_present']}")
    lines.append("")

    # Input info
    lines.append("## معلومات المدخلات")
    lines.append("")
    lines.append(f"- **نوع الحزمة:** {result['input_pack_type']}")
    lines.append(f"- **مسار الحزمة:** {result['input_pack_path']}")
    lines.append(f"- **ملف مسودة الإجابة:** {result['draft_answer_file']}")
    lines.append(f"- **تاريخ الفحص:** {result['checked_at_date']}")
    lines.append("")

    # Invalid citations
    invalid_findings = [cf for cf in result["citation_findings"] if not cf["valid"]]
    if invalid_findings:
        lines.append("## استشهادات غير صالحة")
        lines.append("")
        for cf in invalid_findings:
            lines.append(f"- `{cf['citation_text']}` — {cf['message']}")
        lines.append("")

    # Uncited paragraphs
    if result["uncited_paragraphs"]:
        lines.append("## فقرات بلا استشهاد")
        lines.append("")
        for up in result["uncited_paragraphs"]:
            lines.append(f"- **فقرة {up['paragraph_index']}:** {up['text_preview']}")
            lines.append(f"  - {up['message']}")
        lines.append("")

    # Valid citations
    valid_findings = [cf for cf in result["citation_findings"] if cf["valid"]]
    if valid_findings:
        lines.append("## استشهادات صالحة")
        lines.append("")
        for cf in valid_findings:
            mr = cf["matched_record"]
            title = mr.get("title_ar") or "(بدون عنوان)"
            lines.append(f"- `{cf['citation_text']}` → {title}")
        lines.append("")

    # Boundary note check
    bnc = result["boundary_note_check"]
    lines.append("## فحص الملاحظة الحدية")
    lines.append("")
    lines.append(f"- **مطلوبة:** {bnc['required']}")
    lines.append(f"- **موجودة:** {bnc['present']}")
    lines.append(f"- **اجتياز:** {bnc['passed']}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check citation support for a draft answer against a retrieval prompt/context pack. "
                     "Deterministic, offline. Mechanical citation checking only — not semantic verification. "
                     "Not legal advice. Not an API.",
        prog="check_citation_support",
    )
    parser.add_argument("--prompt-pack", default=None,
                        help="Path to a retrieval prompt pack JSON file")
    parser.add_argument("--context-pack", default=None,
                        help="Path to a retrieval context pack JSON file")
    parser.add_argument("--draft-answer-file", required=True,
                        help="Path to the draft answer file to check")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--require-citation-per-paragraph", action="store_true",
                        help="Require every substantive paragraph to have at least one valid citation")
    parser.add_argument("--require-boundary-note", action="store_true",
                        help="Require the draft to contain a boundary note phrase")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: stdout)")
    args = parser.parse_args()

    # Validate: exactly one of --prompt-pack or --context-pack
    if not args.prompt_pack and not args.context_pack:
        print("ERROR: Exactly one of --prompt-pack or --context-pack is required.", file=sys.stderr)
        sys.exit(2)
    if args.prompt_pack and args.context_pack:
        print("ERROR: Only one of --prompt-pack or --context-pack may be specified.", file=sys.stderr)
        sys.exit(2)

    pack_path = args.prompt_pack or args.context_pack

    if not os.path.isfile(pack_path):
        print(f"ERROR: Pack file not found: {pack_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.draft_answer_file):
        print(f"ERROR: Draft answer file not found: {args.draft_answer_file}", file=sys.stderr)
        sys.exit(1)

    # Load pack
    with open(pack_path, "r", encoding="utf-8") as f:
        pack = json.loads(f.read())

    pack_type = detect_pack_type(pack)

    # Load draft answer
    with open(args.draft_answer_file, "r", encoding="utf-8") as f:
        draft_text = f.read()

    # Run check
    result = run_check(
        pack=pack,
        pack_path=pack_path,
        pack_type=pack_type,
        draft_text=draft_text,
        draft_path=args.draft_answer_file,
        require_citation_per_paragraph=args.require_citation_per_paragraph,
        require_boundary_note=args.require_boundary_note,
    )

    # Output
    if args.format == "json":
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output = format_markdown(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
            f.write("\n")
        print(f"Citation check written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit with non-zero if FAIL
    if result["result"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()