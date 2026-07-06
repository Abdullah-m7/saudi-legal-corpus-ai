#!/usr/bin/env python3
"""
Local Lexical Search — Primary Arabic Governing Export

Deterministic, offline, lexical-only search over the 450 Arabic governing
records in data/exports/v1/primary_arabic_governing_records.jsonl.

No embeddings, no vector DB, no LLM calls, no network, no API.
Not legal advice. Not official translation. Arabic official source governs.

Usage:
  python3 scripts/search_primary_arabic_export.py "الشركة"
  python3 scripts/search_primary_arabic_export.py "مجلس الإدارة" --limit 10
  python3 scripts/search_primary_arabic_export.py "التصفية" --track companies_law
  python3 scripts/search_primary_arabic_export.py "الجمعية العامة" --json
  python3 scripts/search_primary_arabic_export.py "اندماج" --show-text
"""

import argparse
import json
import re
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")


# ─── Arabic normalization for search only (does not alter stored text) ───

_TATWEEL = "\u0640"  # ـ

def normalize_arabic(text: str) -> str:
    """Light normalization for search matching only. Does not alter stored text."""
    if not text:
        return ""
    # Remove tatweel
    t = text.replace(_TATWEEL, "")
    # Normalize alef forms
    t = t.replace("\u0623", "\u0627")  # أ → ا
    t = t.replace("\u0625", "\u0627")  # إ → ا
    t = t.replace("\u0671", "\u0627")  # ٱ → ا
    t = t.replace("\u0622", "\u0627")  # آ → ا
    # Normalize ya
    t = t.replace("\u0649", "\u064A")  # ى → ي
    # Normalize ta marbuta → ha (for search matching only)
    t = t.replace("\u0629", "\u0647")  # ة → ه
    # Normalize dagger alef
    t = t.replace("\u0670", "\u0627")  # ٰ → ا
    # Remove diacritics (harakat)
    t = re.sub(r"[\u064B-\u0652\u0670]", "", t)
    # Normalize whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ─── Search logic ───

def load_records(path: str) -> list:
    """Load all records from JSONL."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def get_searchable_text(record: dict) -> str:
    """Get concatenated searchable text from a record."""
    parts = []
    title = record.get("title_ar") or ""
    text = record.get("text_ar") or ""
    parts.append(title)
    parts.append(text)
    # Also include article_ordinal_ar if present
    ordinal = record.get("article_ordinal_ar") or ""
    if ordinal:
        parts.append(ordinal)
    return " ".join(parts)


def score_record(record: dict, query_terms: list, norm_query: str, norm_title: str, norm_text: str) -> float:
    """
    Deterministic lexical scoring:
    - exact phrase match: highest weight
    - all terms present: bonus
    - title match: bonus
    - more matches: higher score
    """
    score = 0.0

    # Exact phrase match in text
    if norm_query in norm_text:
        score += 100.0

    # Exact phrase match in title
    if norm_query in norm_title:
        score += 50.0

    # Individual term matches
    terms_found_in_text = 0
    terms_found_in_title = 0
    for term in query_terms:
        if term in norm_text:
            terms_found_in_text += 1
            score += 10.0
        if term in norm_title:
            terms_found_in_title += 1
            score += 15.0

    # All terms present bonus
    if len(query_terms) > 1 and terms_found_in_text == len(query_terms):
        score += 25.0

    if len(query_terms) > 1 and terms_found_in_title == len(query_terms):
        score += 20.0

    return score


def make_snippet(text: str, query: str, norm_text: str, norm_query: str, max_len: int = 200) -> str:
    """Create a snippet around the first match."""
    if not text or not norm_text:
        return ""

    # Try exact phrase match first
    pos = norm_text.find(norm_query)
    if pos < 0:
        query_terms_norm = normalize_arabic(query).split()
        if query_terms_norm:
            pos = norm_text.find(query_terms_norm[0])

    if pos < 0:
        # No match found, return beginning
        return text[:max_len] + ("..." if len(text) > max_len else "")

    # Find the approximate position in the original text
    # (normalized text may have different length, so we approximate)
    # Map normalized position back to original using character count ratio
    if len(norm_text) > 0:
        ratio = len(text) / len(norm_text)
        orig_pos = int(pos * ratio)
    else:
        orig_pos = 0

    half = max_len // 2
    start = max(0, orig_pos - half)
    end = min(len(text), start + max_len)

    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet


def search(records: list, query: str, limit: int = 10, track: str = None,
           record_type: str = None) -> list:
    """
    Search records and return ranked results.
    Returns list of dicts with score, record, and snippet.
    """
    norm_query = normalize_arabic(query)
    query_terms = norm_query.split()

    results = []
    for rec in records:
        # Apply filters
        if track and rec.get("source_track_id") != track:
            continue
        if record_type and rec.get("record_type") != record_type:
            continue

        title = rec.get("title_ar") or ""
        text = rec.get("text_ar") or ""
        norm_title = normalize_arabic(title)
        norm_text = normalize_arabic(text)

        score = score_record(rec, query_terms, norm_query, norm_title, norm_text)

        if score > 0:
            snippet = make_snippet(text, query, norm_text, norm_query)
            results.append({
                "score": score,
                "export_record_id": rec.get("export_record_id"),
                "source_track_id": rec.get("source_track_id"),
                "source_record_id": rec.get("source_record_id"),
                "record_type": rec.get("record_type"),
                "title_ar": title,
                "article_number": rec.get("article_number"),
                "record_number": rec.get("record_number"),
                "snippet": snippet,
                "source_url": rec.get("source_url"),
                "source_data_path": rec.get("source_data_path"),
                "_record": rec,  # kept for --show-text; stripped in JSON output
            })

    # Sort by score desc, then by export_record_id asc for stable tie-break
    results.sort(key=lambda r: (-r["score"], r["export_record_id"]))

    return results[:limit]


# ─── Output formatting ───

def format_human(results: list, query: str, total_matches: int, limit: int) -> str:
    """Format results for human-readable terminal output."""
    lines = []
    lines.append(f"Query: {query}")
    lines.append(f"Total matches: {total_matches}")
    lines.append(f"Showing: {len(results)} (limit: {limit})")
    lines.append("")

    if not results:
        lines.append("No matches found.")
        return "\n".join(lines)

    for i, r in enumerate(results, 1):
        lines.append(f"─── {i} ───")
        lines.append(f"  Score:       {r['score']:.1f}")
        lines.append(f"  Record ID:   {r['export_record_id']}")
        lines.append(f"  Track:       {r['source_track_id']}")
        lines.append(f"  Source ID:   {r['source_record_id']}")
        lines.append(f"  Type:        {r['record_type']}")
        title = r.get("title_ar") or "(no title)"
        lines.append(f"  Title:       {title}")
        if r.get("article_number") is not None:
            lines.append(f"  Article:     {r['article_number']}")
        elif r.get("record_number") is not None:
            lines.append(f"  Record #:    {r['record_number']}")
        if r.get("source_url"):
            lines.append(f"  Source URL:  {r['source_url']}")
        lines.append(f"  Snippet:     {r['snippet']}")
        lines.append("")

    return "\n".join(lines)


def format_json(results: list, query: str, norm_query: str, total_matches: int, limit: int) -> str:
    """Format results as JSON."""
    output = {
        "query": query,
        "normalized_query": norm_query,
        "total_matches": total_matches,
        "returned": len(results),
        "results": [],
    }
    for r in results:
        result_obj = {
            "score": r["score"],
            "export_record_id": r["export_record_id"],
            "source_track_id": r["source_track_id"],
            "source_record_id": r["source_record_id"],
            "record_type": r["record_type"],
            "title_ar": r.get("title_ar"),
            "article_number": r.get("article_number"),
            "record_number": r.get("record_number"),
            "snippet": r["snippet"],
            "source_url": r.get("source_url"),
            "source_data_path": r.get("source_data_path"),
        }
        output["results"].append(result_obj)
    return json.dumps(output, ensure_ascii=False, indent=2)


def format_text(results: list, query: str, total_matches: int, limit: int) -> str:
    """Format results with full text."""
    lines = []
    lines.append(f"Query: {query}")
    lines.append(f"Total matches: {total_matches}")
    lines.append(f"Showing: {len(results)} (limit: {limit})")
    lines.append("")

    if not results:
        lines.append("No matches found.")
        return "\n".join(lines)

    for i, r in enumerate(results, 1):
        lines.append(f"─── {i} ───")
        lines.append(f"  Score:       {r['score']:.1f}")
        lines.append(f"  Record ID:   {r['export_record_id']}")
        lines.append(f"  Track:       {r['source_track_id']}")
        lines.append(f"  Source ID:   {r['source_record_id']}")
        lines.append(f"  Type:        {r['record_type']}")
        title = r.get("title_ar") or "(no title)"
        lines.append(f"  Title:       {title}")
        if r.get("article_number") is not None:
            lines.append(f"  Article:     {r['article_number']}")
        elif r.get("record_number") is not None:
            lines.append(f"  Record #:    {r['record_number']}")
        if r.get("source_url"):
            lines.append(f"  Source URL:  {r['source_url']}")
        rec = r.get("_record", {})
        full_text = rec.get("text_ar") or ""
        lines.append(f"  Full text:")
        lines.append(f"    {full_text}")
        lines.append("")

    return "\n".join(lines)


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(
        description="Local lexical search over Arabic governing records (450 records). "
                     "No embeddings, no network, no API. Not legal advice.",
        prog="search_primary_arabic_export",
    )
    parser.add_argument("query", help="Search query (Arabic or normalized)")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--track", default=None,
                        help="Filter by track: companies_law, implementing_regulations_general, "
                             "implementing_regulations_listed_joint_stock")
    parser.add_argument("--record-type", default=None,
                        help="Filter by record type: article, form, appendix")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--show-text", action="store_true", help="Show full text_ar in output")
    args = parser.parse_args()

    if not os.path.isfile(JSONL_PATH):
        print(f"ERROR: Export JSONL not found: {JSONL_PATH}", file=sys.stderr)
        sys.exit(1)

    records = load_records(JSONL_PATH)
    norm_query = normalize_arabic(args.query)

    # Get total matches (before limit)
    all_results = search(records, args.query, limit=len(records), track=args.track, record_type=args.record_type)
    total_matches = len(all_results)

    # Get limited results
    results = all_results[:args.limit]

    if args.json:
        print(format_json(results, args.query, norm_query, total_matches, args.limit))
    elif args.show_text:
        print(format_text(results, args.query, total_matches, args.limit))
    else:
        print(format_human(results, args.query, total_matches, args.limit))


if __name__ == "__main__":
    main()