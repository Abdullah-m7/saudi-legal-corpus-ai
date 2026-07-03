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


def validate_book4() -> Tuple[bool, Dict[str, List[str]]]:
    """Validate Book Four (model 1b) infrastructure: coverage matrix + guardrails.

    There is NO per-article Book Four dataset at this stage; this validates the
    80-row coverage matrix, the model-1b decision doc, the registry disclaimer
    scope, and that no full article dataset has been created.
    """
    from . import books

    spec = books.get_book(4)
    report: Dict[str, List[str]] = {}

    if not os.path.exists(spec.coverage_json):
        return False, {"coverage_exists": [f"missing {spec.coverage_json}"]}

    with open(spec.coverage_json, "r", encoding="utf-8") as fh:
        coverage_text = fh.read()
    coverage = _read(spec.coverage_json)

    model_doc = os.path.join(
        _REPO_ROOT, "docs", "book4_preflight", "BOOK4_MODEL_1B_DECISION.md"
    )
    # A full per-article Book Four dataset must NOT exist at this stage.
    article_dataset_exists = os.path.exists(spec.articles_json)

    qa = qa_rules.run_all_book4(
        coverage=coverage,
        coverage_text=coverage_text,
        disclaimer_ar=spec.disclaimer_ar,
        disclaimer_zh=spec.disclaimer_zh,
        model_doc_exists=os.path.exists(model_doc),
        article_dataset_exists=article_dataset_exists,
    )
    for name, problems in qa.items():
        if problems:
            report[name] = problems

    # Provision schema must exist for the future content stage.
    prov_schema_path = os.path.join(SCHEMAS, "book4_provision.schema.json")
    if not os.path.exists(prov_schema_path):
        report["b4_10_provision_schema_exists"] = [
            "schemas/book4_provision.schema.json must exist"]

    # -- Validate any Book Four provision datasets that exist (model 1b) --
    import glob

    prov_schema = _read(prov_schema_path) if os.path.exists(prov_schema_path) else None
    explicit = set(coverage.get("explicit_in_source", []))
    provisioned_articles = set()
    prov_problems: List[str] = []
    trust_problems: List[str] = []

    for path in sorted(glob.glob(os.path.join(DATA, "articles", "book4_provisions_*.json"))):
        doc = _read(path)
        label = os.path.basename(path)
        for p in doc.get("provisions", []):
            if prov_schema is not None:
                prov_problems += validate_against_schema(
                    p, prov_schema, f"{label}:{p.get('provision_id')}")
            nums = p.get("source_article_numbers", [])
            provisioned_articles.update(nums)
            # Every mapped article must be explicit_in_source (never an uncovered one).
            for n in nums:
                if n not in explicit:
                    trust_problems.append(
                        f"{label}:{p.get('provision_id')} maps to non-explicit article {n}")
            src = p.get("source", {})
            if p.get("translation_mode") != "internally_reviewed_summary":
                trust_problems.append(f"{p.get('provision_id')}: translation_mode must be internally_reviewed_summary")
            if src.get("official_text_check") != "needs_check":
                trust_problems.append(f"{p.get('provision_id')}: official_text_check must be needs_check")
            if src.get("source_coverage_status") != "explicit_in_source":
                trust_problems.append(f"{p.get('provision_id')}: source_coverage_status must be explicit_in_source")
        # No trust overclaim anywhere in the provisions file.
        with open(path, "r", encoding="utf-8") as fh:
            blob = fh.read()
        for term in ("verified_summary", "verified", "محققة", "经核验"):
            if term in blob:
                trust_problems.append(f"{label}: banned trust term '{term}'")

    if prov_problems:
        report["b4_11_provision_schema_valid"] = prov_problems
    if trust_problems:
        report["b4_12_provision_trust_posture"] = trust_problems

    # Coverage/provision consistency: rows for provisioned articles must be
    # provision_created; provision_created rows must have a provision.
    cov_created = {r["article_number"] for r in coverage.get("rows", [])
                   if r.get("content_record_status") == "provision_created"}
    consistency = []
    if provisioned_articles != cov_created:
        consistency.append(
            f"coverage provision_created {sorted(cov_created)} != provisioned "
            f"articles {sorted(provisioned_articles)}")
    if consistency:
        report["b4_13_coverage_provision_consistency"] = consistency

    ok = all(len(v) == 0 for v in report.values())
    return ok, report


def validate_book(book: int = 1) -> Tuple[bool, Dict[str, List[str]]]:
    """Validate one book's structured files (schema + QA). Returns (ok, report)."""
    from . import books

    if book == 4:
        return validate_book4()

    spec = books.get_book(book)
    report: Dict[str, List[str]] = {}

    article_schema = _read(os.path.join(SCHEMAS, "article.schema.json"))
    glossary_schema = _read(os.path.join(SCHEMAS, "glossary.schema.json"))
    coverage_schema = _read(os.path.join(SCHEMAS, "coverage.schema.json"))

    articles_doc = _read(spec.articles_json)
    articles = articles_doc["articles"]
    work = _read(books.WORK_JSON)
    glossary = _read(books.GLOSSARY_JSON)
    coverage = _read(spec.coverage_json)

    # -- schema validation (shared schemas) --
    schema_problems: List[str] = []
    for a in articles:
        schema_problems += validate_against_schema(
            a, article_schema, f"article {a.get('article_number')}"
        )
    schema_problems += validate_against_schema(glossary, glossary_schema, "glossary")
    schema_problems += validate_against_schema(coverage, coverage_schema, "coverage")
    report["schema"] = schema_problems

    # -- QA rules (per book) --
    if book == 1:
        qa = qa_rules.run_all(articles, work)
    elif book == 2:
        qa = qa_rules.run_all_book2(articles, work, glossary, articles_doc)
    elif book == 3:
        qa = qa_rules.run_all_book3(articles, work, glossary, articles_doc)
    else:
        qa = {}
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


def validate_all() -> Tuple[bool, Dict[str, List[str]]]:
    """Validate Book One (backward-compatible entry point)."""
    return validate_book(1)
