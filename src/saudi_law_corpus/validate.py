"""Corpus validation: JSON-schema checks + legal-translation QA rules.

Schema validation uses ``jsonschema`` when available; otherwise it falls back to
a minimal built-in structural check so the pipeline still works with only the
standard library. QA rules (``qa_rules``) always run.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple

from . import qa_rules

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

DATA = os.path.join(_REPO_ROOT, "data")
SCHEMAS = os.path.join(_REPO_ROOT, "schemas")


def _read(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


try:  # optional dependency
    import jsonschema  # type: ignore

    _HAVE_JSONSCHEMA = True
except Exception:  # pragma: no cover - exercised only when dep missing
    _HAVE_JSONSCHEMA = False


def _fallback_check(obj: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> List[str]:
    """Very small subset validator used when jsonschema is unavailable."""
    problems: List[str] = []
    for key in schema.get("required", []):
        if key not in obj:
            problems.append(f"{path or '<root>'}: missing required key '{key}'")
    props = schema.get("properties", {})
    for key, subschema in props.items():
        if key not in obj:
            continue
        val = obj[key]
        t = subschema.get("type")
        if t == "string" and not isinstance(val, str):
            problems.append(f"{path}.{key}: expected string")
        elif t == "integer" and not isinstance(val, int):
            problems.append(f"{path}.{key}: expected integer")
        elif t == "array" and not isinstance(val, list):
            problems.append(f"{path}.{key}: expected array")
    return problems


def validate_against_schema(obj: Any, schema: Dict[str, Any], label: str) -> List[str]:
    if _HAVE_JSONSCHEMA:
        validator = jsonschema.Draft7Validator(schema)
        return [f"{label}: {e.message} (at {'/'.join(str(p) for p in e.path)})"
                for e in validator.iter_errors(obj)]
    return _fallback_check(obj, schema, label)


def validate_all() -> Tuple[bool, Dict[str, List[str]]]:
    """Validate every structured file. Returns (ok, {section: [problems]})."""
    report: Dict[str, List[str]] = {}

    article_schema = _read(os.path.join(SCHEMAS, "article.schema.json"))
    glossary_schema = _read(os.path.join(SCHEMAS, "glossary.schema.json"))
    coverage_schema = _read(os.path.join(SCHEMAS, "coverage.schema.json"))

    articles_doc = _read(os.path.join(DATA, "articles", "book1_articles_001_034.json"))
    articles = articles_doc["articles"]
    work = _read(os.path.join(DATA, "metadata", "work.json"))
    glossary = _read(os.path.join(DATA, "glossary", "ar_zh_legal_terms.json"))
    coverage = _read(os.path.join(DATA, "coverage", "book1_coverage_matrix.json"))

    # -- schema validation --
    schema_problems: List[str] = []
    for a in articles:
        schema_problems += validate_against_schema(
            a, article_schema, f"article {a.get('article_number')}"
        )
    schema_problems += validate_against_schema(glossary, glossary_schema, "glossary")
    schema_problems += validate_against_schema(coverage, coverage_schema, "coverage")
    report["schema"] = schema_problems

    # -- QA rules --
    qa = qa_rules.run_all(articles, work)
    for name, problems in qa.items():
        if problems:
            report[name] = problems

    # -- coverage <-> articles consistency --
    cov_expanded = set(coverage.get("expanded_after_review", []))
    art_expanded = {a["article_number"] for a in articles
                    if a["coverage_status"] == "expanded_after_review"}
    if cov_expanded != art_expanded:
        report["coverage_consistency"] = [
            f"coverage expanded {sorted(cov_expanded)} != articles expanded {sorted(art_expanded)}"
        ]

    ok = all(len(v) == 0 for v in report.values())
    return ok, report
