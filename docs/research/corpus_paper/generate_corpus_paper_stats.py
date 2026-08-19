#!/usr/bin/env python3
"""Generate the statistics reported in the corpus resource paper.

Read-only: scans the corpus data layers and writes a single JSON stats file
next to this script. Every number cited in the paper must be reproducible by
re-running this script from the repository root:

    python3 docs/research/corpus_paper/generate_corpus_paper_stats.py
"""

import json
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA = REPO_ROOT / "data"
OUT_PATH = Path(__file__).resolve().parent / "corpus_paper_stats.json"

ARABIC_CHAR = re.compile(r"[؀-ۿ]")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def registry_stats():
    reg = load_json(DATA / "corpus_registry" / "corpus_registry.json")
    tracks = reg["tracks"]
    families = Counter(t.get("corpus_family", "unknown") for t in tracks)
    authorities = Counter(t.get("source_authority", "unknown") for t in tracks)
    governing = Counter(t.get("governing_language", "unknown") for t in tracks)
    years = []
    for t in tracks:
        date = t.get("publication_date_gregorian") or ""
        m = re.match(r"(\d{4})", str(date))
        if m:
            years.append(int(m.group(1)))
    return {
        "registry_version": reg.get("registry_version"),
        "generated_date": reg.get("generated_date"),
        "total_tracks": reg.get("total_tracks"),
        "total_registry_counted_records": reg.get("total_registry_counted_records"),
        "total_primary_arabic_governing_records": reg.get(
            "total_primary_arabic_governing_records"
        ),
        "total_implementing_regulations_records": reg.get(
            "total_implementing_regulations_records"
        ),
        "total_reference_records": reg.get("total_reference_records"),
        "total_internal_reference_records": reg.get("total_internal_reference_records"),
        "tracks_by_corpus_family": dict(families.most_common()),
        "tracks_by_source_authority": dict(authorities.most_common()),
        "tracks_by_governing_language": dict(governing),
        "publication_year_min": min(years) if years else None,
        "publication_year_max": max(years) if years else None,
        "tracks_with_publication_year": len(years),
    }


def unified_index_stats():
    total = 0
    words = 0
    chars = 0
    arabic_chars = 0
    components = Counter()
    text_status = Counter()
    laws = set()
    corpora = set()
    with open(
        DATA / "corpus_unified_index" / "corpus_unified_llm_index.jsonl",
        encoding="utf-8",
    ) as f:
        for line in f:
            rec = json.loads(line)
            total += 1
            text = rec.get("text_ar") or ""
            words += len(text.split())
            chars += len(text)
            arabic_chars += len(ARABIC_CHAR.findall(text))
            components[rec.get("law_component", "unknown")] += 1
            text_status[rec.get("text_status", "unknown")] += 1
            laws.add(rec.get("law_id"))
            corpora.add(rec.get("corpus"))
    # text_status values are fine-grained per-track provenance labels; report
    # only their cardinality and the most common ones to keep the paper table
    # readable.
    return {
        "total_records": total,
        "distinct_law_ids": len(laws),
        "distinct_corpora": len(corpora),
        "total_arabic_whitespace_tokens": words,
        "total_characters": chars,
        "total_arabic_characters": arabic_chars,
        "records_by_law_component": dict(components.most_common()),
        "distinct_text_status_labels": len(text_status),
        "top_text_status_labels": dict(text_status.most_common(10)),
    }


def cross_reference_stats():
    g = load_json(
        DATA / "corpus_cross_reference_graph" / "corpus_cross_reference_graph.json"
    )
    refs = g["references"]
    inter = [r for r in refs if r.get("type") == "inter_law"]
    source_tracks = Counter(r["source_track_id"] for r in inter)
    target_names = Counter(
        (r.get("target_law_name_raw") or r.get("target_track_id") or "unknown")
        for r in inter
    )
    return {
        "total_records_scanned": g.get("total_records_scanned"),
        "total_references_extracted": g.get("total_references_extracted"),
        "intra_law_count": g.get("intra_law_count"),
        "inter_law_count": g.get("inter_law_count"),
        "ambiguous_scope_count": g.get("ambiguous_scope_count"),
        "confidence_counts": g.get("confidence_counts"),
        "inter_law_distinct_source_tracks": len(source_tracks),
        "inter_law_distinct_target_names": len(target_names),
        "top_referenced_target_laws": dict(target_names.most_common(10)),
    }


def supersession_stats():
    g = load_json(
        DATA / "corpus_supersession_graph" / "corpus_supersession_graph.json"
    )
    edges = (
        g.get("edges")
        or g.get("supersessions")
        or g.get("relations")
        or []
    )
    out = {k: v for k, v in g.items() if isinstance(v, (int, str))}
    out["edge_count"] = len(edges) if isinstance(edges, list) else None
    return out


def glossary_stats():
    gl = load_json(DATA / "corpus_glossary" / "corpus_glossary.json")
    return {
        "total_terms": gl.get("total_terms"),
        "total_definitions": gl.get("total_definitions"),
        "total_tracks_in_registry": gl.get("total_tracks_in_registry"),
        "tracks_with_definitions_article_parsed": gl.get(
            "tracks_with_definitions_article_parsed"
        ),
    }


def retrieval_eval_stats():
    ev = load_json(
        DATA / "corpus_retrieval_eval" / "corpus_retrieval_eval_queries.json"
    )
    queries = ev.get("queries", [])
    return {
        "eval_id": ev.get("eval_id"),
        "gold_basis": ev.get("gold_basis"),
        "total_queries": len(queries),
        "sample_query_keys": sorted(queries[0].keys()) if queries else [],
    }


def chunking_stats():
    path = DATA / "corpus_chunking_layer" / "corpus_chunking_layer_summary.json"
    if not path.exists():
        return None
    s = load_json(path)
    return {k: v for k, v in s.items() if isinstance(v, (int, str))}


def verification_tier_stats():
    v = load_json(
        DATA / "corpus_verification_tiers" / "corpus_verification_tiers.json"
    )
    out = {
        "tier_order": v.get("tier_order"),
        "taxonomy_size": len(v.get("taxonomy", {})),
    }
    assignments = v.get("assignments") or v.get("tracks")
    if isinstance(assignments, list):
        out["assignments_by_tier"] = dict(
            Counter(a.get("tier", "unknown") for a in assignments).most_common()
        )
    elif isinstance(assignments, dict):
        out["assignments_by_tier"] = dict(
            Counter(a.get("tier", "unknown") for a in assignments.values()).most_common()
        )
    return out


def makefile_validator_count():
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    targets = re.findall(r"^([a-z0-9][a-z0-9_-]*):", makefile, flags=re.M)
    validators = [t for t in targets if "validate" in t]
    return {
        "total_make_targets": len(set(targets)),
        "validator_targets": len(set(validators)),
    }


def main():
    stats = {
        "registry": registry_stats(),
        "unified_index": unified_index_stats(),
        "cross_reference_graph": cross_reference_stats(),
        "supersession_graph": supersession_stats(),
        "glossary": glossary_stats(),
        "retrieval_eval": retrieval_eval_stats(),
        "chunking_layer": chunking_stats(),
        "verification_tiers": verification_tier_stats(),
        "makefile": makefile_validator_count(),
    }
    OUT_PATH.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_PATH}")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
