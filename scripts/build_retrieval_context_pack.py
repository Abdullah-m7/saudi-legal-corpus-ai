#!/usr/bin/env python3
"""
Retrieval Context Pack Builder — Primary Arabic Governing Records

Deterministic, offline, lexical-only context pack generator.
Takes a query, runs the existing local lexical search, and exports
top results as a structured evidence/context pack (JSON or Markdown).

This is NOT RAG.
This is NOT an answer generator.
This is NOT legal advice.
This is NOT legal interpretation.
This is NOT semantic search.
This is NOT embeddings.
This is NOT an API.
This is NOT a public release.

Usage:
  python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة"
  python3 scripts/build_retrieval_context_pack.py "الجمعية العامة" --limit 5
  python3 scripts/build_retrieval_context_pack.py "التصفية" --track companies_law --limit 5
  python3 scripts/build_retrieval_context_pack.py "التوكيل" --record-type appendix --limit 3
  python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --format json
  python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --format markdown
  python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --output /tmp/context_pack.json
  python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --include-full-text --limit 3
"""

import argparse
import json
import os
import sys
from datetime import date
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import search functions from the existing local lexical search CLI
sys.path.insert(0, REPO_ROOT)
from scripts.search_primary_arabic_export import (
    normalize_arabic,
    load_records,
    search,
)

PACK_VERSION = "1.0"
SOURCE_SEARCH_TOOL = "scripts/search_primary_arabic_export.py"
RETRIEVAL_METHOD = "deterministic_lexical_search"

LEGAL_BOUNDARIES = [
    "Arabic official source governs",
    "Not legal advice",
    "Not official translation",
    "No legal interpretation",
    "No generated legal conclusions",
    "No English/Chinese records",
    "No trilingual alignment",
    "No public release",
]


def build_context_pack(
    query: str,
    limit: int = 5,
    track: Optional[str] = None,
    record_type: Optional[str] = None,
    include_full_text: bool = False,
) -> dict:
    """Build a deterministic context pack from lexical search results.

    Returns a dict with all top-level fields and records.
    """
    records = load_records(JSONL_PATH)
    norm_query = normalize_arabic(query)

    # Get total matches (before limit) and limited results
    all_results = search(
        records, query, limit=len(records), track=track, record_type=record_type
    )
    total_matches = len(all_results)
    results = all_results[:limit]

    pack_records = []
    for i, r in enumerate(results, 1):
        rec = {
            "rank": i,
            "score": r["score"],
            "export_record_id": r.get("export_record_id"),
            "source_track_id": r.get("source_track_id"),
            "source_record_id": r.get("source_record_id"),
            "corpus_family": r["_record"].get("corpus_family"),
            "document_type": r["_record"].get("document_type"),
            "record_type": r.get("record_type"),
            "language": r["_record"].get("language"),
            "governing_status": r["_record"].get("governing_status"),
            "title_ar": r.get("title_ar"),
        }

        # Article number or record number
        if r.get("article_number") is not None:
            rec["article_number"] = r["article_number"]
        if r.get("record_number") is not None:
            rec["record_number"] = r["record_number"]

        rec["snippet"] = r.get("snippet")

        # Full text only if requested
        if include_full_text:
            rec["text_ar"] = r["_record"].get("text_ar")

        # Optional provenance fields
        if r["_record"].get("source_url"):
            rec["source_url"] = r["_record"].get("source_url")
        if r["_record"].get("source_authority"):
            rec["source_authority"] = r["_record"].get("source_authority")
        if r["_record"].get("publication_date_hijri"):
            rec["publication_date_hijri"] = r["_record"].get("publication_date_hijri")
        if r["_record"].get("publication_date_gregorian"):
            rec["publication_date_gregorian"] = r["_record"].get("publication_date_gregorian")
        if r.get("source_data_path"):
            rec["source_data_path"] = r.get("source_data_path")
        if r["_record"].get("source_text_sha256"):
            rec["source_text_sha256"] = r["_record"].get("source_text_sha256")

        pack_records.append(rec)

    filters = {}
    if track:
        filters["track"] = track
    if record_type:
        filters["record_type"] = record_type

    pack = {
        "pack_version": PACK_VERSION,
        "query": query,
        "normalized_query": norm_query,
        "generated_at_date": date.today().isoformat(),
        "source_search_tool": SOURCE_SEARCH_TOOL,
        "source_export_file": "data/exports/v1/primary_arabic_governing_records.jsonl",
        "source_export_record_count": len(records),
        "retrieval_method": RETRIEVAL_METHOD,
        "limit": limit,
        "filters": filters,
        "total_matches": total_matches,
        "returned": len(pack_records),
        "legal_boundaries": LEGAL_BOUNDARIES,
        "records": pack_records,
    }

    return pack


def format_markdown(pack: dict, include_full_text: bool = False) -> str:
    """Format context pack as Markdown (Arabic-friendly layout)."""
    lines = []
    query = pack["query"]
    returned = pack["returned"]
    total = pack["total_matches"]

    # Heading
    lines.append(f"# حزمة سياق استرجاع — {query}")
    lines.append("")
    lines.append(f"**النتائج المعروضة:** {returned} / **إجمالي المطابقات:** {total}")
    lines.append("")

    # Boundary note
    lines.append("## الحدود القانونية")
    lines.append("")
    for b in pack["legal_boundaries"]:
        lines.append(f"- {b}")
    lines.append("")

    # Metadata
    lines.append("## البيانات الوصفية")
    lines.append("")
    lines.append(f"- **إصدار الحزمة:** {pack['pack_version']}")
    lines.append(f"- **الاستعلام:** {query}")
    lines.append(f"- **الاستعلام المُطبَّع:** {pack['normalized_query']}")
    lines.append(f"- **التاريخ:** {pack['generated_at_date']}")
    lines.append(f"- **أداة البحث:** {pack['source_search_tool']}")
    lines.append(f"- **ملف المصدر:** {pack['source_export_file']}")
    lines.append(f"- **عدد سجلات المصدر:** {pack['source_export_record_count']}")
    lines.append(f"- **طريقة الاسترجاع:** {pack['retrieval_method']}")
    lines.append(f"- **الحد الأقصى للنتائج:** {pack['limit']}")
    if pack["filters"]:
        filters_str = ", ".join(f"{k}={v}" for k, v in pack["filters"].items())
        lines.append(f"- **المرشحات:** {filters_str}")
    lines.append("")

    # Records
    lines.append("## السجلات المسترجعة")
    lines.append("")
    for rec in pack["records"]:
        rank = rec["rank"]
        score = rec["score"]
        title = rec.get("title_ar") or "(بدون عنوان)"
        lines.append(f"### {rank}. {title}")
        lines.append("")
        lines.append(f"- **الدرجة:** {score:.1f}")
        lines.append(f"- **معرف السجل:** {rec.get('export_record_id')}")
        lines.append(f"- **معيد المصدر:** {rec.get('source_record_id')}")
        lines.append(f"- **المسار:** {rec.get('source_track_id')}")
        lines.append(f"- **النوع:** {rec.get('record_type')}")
        lines.append(f"- **عائلة المدونة:** {rec.get('corpus_family')}")
        lines.append(f"- **نوع الوثيقة:** {rec.get('document_type')}")
        lines.append(f"- **اللغة:** {rec.get('language')}")
        lines.append(f"- **الصفة الحاكمة:** {rec.get('governing_status')}")
        if rec.get("article_number") is not None:
            lines.append(f"- **رقم المادة:** {rec['article_number']}")
        if rec.get("record_number") is not None:
            lines.append(f"- **رقم السجل:** {rec['record_number']}")
        if rec.get("source_url"):
            lines.append(f"- **رابط المصدر:** {rec['source_url']}")
        if rec.get("source_authority"):
            lines.append(f"- **جهة المصدر:** {rec['source_authority']}")
        if rec.get("publication_date_hijri"):
            lines.append(f"- **تاريخ النشر (هجري):** {rec['publication_date_hijri']}")
        if rec.get("publication_date_gregorian"):
            lines.append(f"- **تاريخ النشر (ميلادي):** {rec['publication_date_gregorian']}")
        if rec.get("source_data_path"):
            lines.append(f"- **مسار بيانات المصدر:** {rec['source_data_path']}")
        if rec.get("source_text_sha256"):
            lines.append(f"- **بصمة النص (SHA-256):** {rec['source_text_sha256']}")
        lines.append("")
        lines.append(f"**مقتطف:**")
        lines.append(f"> {rec.get('snippet', '')}")
        lines.append("")
        if include_full_text and rec.get("text_ar"):
            lines.append(f"**النص الكامل:**")
            lines.append("")
            lines.append(rec["text_ar"])
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build a retrieval context pack from local lexical search. "
                     "Deterministic, offline. Not RAG. Not legal advice. Not an API.",
        prog="build_retrieval_context_pack",
    )
    parser.add_argument("query", help="Search query (Arabic)")
    parser.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--track", default=None,
                        help="Filter by track: companies_law, implementing_regulations_general, "
                             "implementing_regulations_listed_joint_stock")
    parser.add_argument("--record-type", default=None,
                        help="Filter by record type: article, form, appendix")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--include-full-text", action="store_true",
                        help="Include full text_ar in each record")
    args = parser.parse_args()

    if not os.path.isfile(JSONL_PATH):
        print(f"ERROR: Export JSONL not found: {JSONL_PATH}", file=sys.stderr)
        sys.exit(1)

    pack = build_context_pack(
        query=args.query,
        limit=args.limit,
        track=args.track,
        record_type=args.record_type,
        include_full_text=args.include_full_text,
    )

    if args.format == "json":
        output = json.dumps(pack, ensure_ascii=False, indent=2)
    else:
        output = format_markdown(pack, include_full_text=args.include_full_text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
            f.write("\n")
        print(f"Context pack written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()