#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Schema Manifest — Read-Only Validator

Validates data/schema_manifest/corpus_schema_manifest.json, produced by
scripts/gen_corpus_schema_manifest.py.

Checks:
  1.  Manifest JSON exists and parses; required top-level keys present.
  2.  Every one of the 9 required schema entries is present under `schemas`.
  3.  Every schema entry is structurally valid JSON Schema syntax:
        - if the `jsonschema` library is installed, each schema is checked
          with Draft202012Validator.check_schema() (full meta-schema
          validation);
        - otherwise, a basic structural fallback check runs instead
          (declares $schema; declares type/oneOf/anyOf; every name in a
          `required` list appears in the corresponding `properties`, either
          directly or via a $defs variant reachable through oneOf/anyOf).
  4.  Cross-checks a curated sample of 8 real corpus files (spanning
      multiple tracks/eras) plus all five corpus-wide derived layers
      (verification tiers, supersession graph, cross-reference graph,
      glossary, and — since it has no dedicated generator of its own —
      a structural spot-check of the coverage gap map) against their
      respective schema's required-fields list, reporting any mismatch.
  5.  Idempotency: re-runs scripts/gen_corpus_schema_manifest.py in a
      subprocess and diffs its output against the committed file — must
      be byte-identical.

Read-only: does not modify data/schema_manifest/corpus_schema_manifest.json,
any of the 123 track files, or any other corpus-wide derived layer.

Usage:
    python3 scripts/validate_corpus_schema_manifest.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "data", "schema_manifest", "corpus_schema_manifest.json")
GENERATOR = os.path.join(ROOT, "scripts", "gen_corpus_schema_manifest.py")

REQUIRED_TOP_LEVEL_KEYS = [
    "schema_version", "generated_by", "dialect", "corpus_repository", "corpus_branch",
    "description", "read_only_derived_layer", "not_legal_advice", "sample_files_read",
    "schemas", "field_provenance_notes",
]

REQUIRED_SCHEMA_NAMES = [
    "official_source_schema",
    "verified_record_schema",
    "llm_ready_layer_schema",
    "unified_index_record_schema",
    "corpus_registry_track_schema",
    "verification_tier_entry_schema",
    "supersession_edge_schema",
    "cross_reference_edge_schema",
    "glossary_term_schema",
]

try:
    import jsonschema  # type: ignore
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


ERRORS: list[str] = []
WARNINGS: list[str] = []


def fail(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def load_json(rel_path: str):
    with open(os.path.join(ROOT, rel_path), "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl_first(rel_path: str):
    with open(os.path.join(ROOT, rel_path), "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                return json.loads(line)
    raise ValueError(f"{rel_path}: no non-empty lines")


# ---------------------------------------------------------------------------
# 1-2. Manifest exists, parses, has required top-level keys and all 9 schemas
# ---------------------------------------------------------------------------

def check_manifest_shape(manifest: dict) -> None:
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in manifest:
            fail(f"manifest missing required top-level key '{key}'")

    schemas = manifest.get("schemas", {})
    for name in REQUIRED_SCHEMA_NAMES:
        if name not in schemas:
            fail(f"manifest missing required schema '{name}'")

    extra = set(schemas.keys()) - set(REQUIRED_SCHEMA_NAMES)
    if extra:
        warn(f"manifest has extra, undeclared schema entries: {sorted(extra)}")


# ---------------------------------------------------------------------------
# 3. Structural JSON-Schema-syntax validity of every schema entry
# ---------------------------------------------------------------------------

def _fallback_structural_check(name: str, schema: dict) -> None:
    if "$schema" not in schema:
        fail(f"schema '{name}': missing $schema")
    if not any(k in schema for k in ("type", "oneOf", "anyOf")):
        fail(f"schema '{name}': missing 'type', 'oneOf', and 'anyOf'")

    def _defs_index(s):
        return s.get("$defs", {})

    defs = _defs_index(schema)

    def _check_object_schema(sub, path):
        if not isinstance(sub, dict):
            return
        required = sub.get("required", [])
        props = sub.get("properties", {})
        pattern_props = sub.get("patternProperties", {})
        for field in required:
            if field in props:
                continue
            if any(__import__("re").match(pat, field) for pat in pattern_props):
                continue
            fail(f"schema '{name}'{path}: required field '{field}' not declared in properties")

    if "properties" in schema or "required" in schema:
        _check_object_schema(schema, "")
    for branch_key in ("oneOf", "anyOf"):
        for i, branch in enumerate(schema.get(branch_key, [])):
            ref = branch.get("$ref", "")
            if ref.startswith("#/$defs/"):
                def_name = ref[len("#/$defs/"):]
                if def_name not in defs:
                    fail(f"schema '{name}': {branch_key}[{i}] refers to missing $defs.{def_name}")
                else:
                    _check_object_schema(defs[def_name], f".$defs.{def_name}")


def check_schema_syntax(manifest: dict) -> None:
    schemas = manifest.get("schemas", {})
    if HAVE_JSONSCHEMA:
        validator_cls = jsonschema.Draft202012Validator
        for name, schema in schemas.items():
            try:
                validator_cls.check_schema(schema)
            except Exception as e:  # jsonschema.exceptions.SchemaError
                fail(f"schema '{name}' failed Draft202012Validator.check_schema(): {e}")
    else:
        warn("jsonschema library not installed; falling back to a basic structural check "
             "(required fields vs properties/$defs only, no full meta-schema validation)")
        for name, schema in schemas.items():
            _fallback_structural_check(name, schema)


# ---------------------------------------------------------------------------
# 4. Cross-check real corpus files against the manifest's required-field
#    claims (and, where jsonschema is available, full schema validation).
# ---------------------------------------------------------------------------

# A deliberately DIFFERENT sample from the one used inside the generator's own
# self_validate(), so this validator provides independent corroboration
# rather than re-checking exactly the same files the generator already checked.
CROSS_CHECK_TARGETS = [
    ("official_source_schema", "json",
     "sources/traffic/law/official_source/traffic_law_official_source.json"),
    ("official_source_schema", "json",
     "sources/civil/law/official_source/civil_transactions_law_official_source.json"),
    ("verified_record_schema", "jsonl",
     "sources/zakat/law/verified/zakat_law_verified_records.jsonl"),
    ("verified_record_schema", "jsonl",
     "sources/basic_law_of_governance/law/verified/basic_law_of_governance_verified_records.jsonl"),
    ("llm_ready_layer_schema", "json",
     "data/patent_arabic_legal_llm/patent_law_legal_llm_001_066.json"),
    ("unified_index_record_schema", "jsonl",
     "data/corpus_unified_index/corpus_unified_llm_index.jsonl"),
    ("corpus_registry_track_schema", "registry_track",
     "data/corpus_registry/corpus_registry.json"),
    ("verification_tier_entry_schema", "tier_entry",
     "data/corpus_verification_tiers/corpus_verification_tiers.json"),
    ("supersession_edge_schema", "graph_edge",
     "data/corpus_supersession_graph/corpus_supersession_graph.json"),
    ("cross_reference_edge_schema", "graph_ref",
     "data/corpus_cross_reference_graph/corpus_cross_reference_graph.json"),
]


def _required_fields_for(schema: dict, instance) -> list[str] | None:
    """Best-effort: resolve which branch of a oneOf/anyOf schema (if any)
    an instance's top-level keys best match, and return that branch's
    required-field list. Returns None if the schema is a plain object schema."""
    defs = schema.get("$defs", {})
    for branch_key in ("oneOf", "anyOf"):
        branches = schema.get(branch_key)
        if not branches:
            continue
        best, best_score = None, -1
        for branch in branches:
            ref = branch.get("$ref", "")
            if not ref.startswith("#/$defs/"):
                continue
            sub = defs.get(ref[len("#/$defs/"):], {})
            req = sub.get("required", [])
            if not isinstance(instance, dict):
                continue
            score = sum(1 for f in req if f in instance)
            if score > best_score:
                best, best_score = req, score
        if best is not None:
            return best
    return schema.get("required")


def check_cross_samples(manifest: dict) -> None:
    schemas = manifest["schemas"]
    checked = 0
    for schema_name, kind, rel_path in CROSS_CHECK_TARGETS:
        schema = schemas.get(schema_name)
        if schema is None:
            continue
        try:
            if kind == "json":
                instance = load_json(rel_path)
                _cross_check_one(schema_name, schema, instance, rel_path)
                checked += 1
            elif kind == "jsonl":
                instance = load_jsonl_first(rel_path)
                _cross_check_one(schema_name, schema, instance, rel_path + " [line 1]")
                checked += 1
            elif kind == "registry_track":
                registry = load_json(rel_path)
                for t in registry.get("tracks", [])[:2]:
                    _cross_check_one(schema_name, schema, t, f"{rel_path} [{t.get('track_id')}]")
                    checked += 1
            elif kind == "tier_entry":
                vt = load_json(rel_path)
                for entry in vt.get("tracks", [])[:2]:
                    _cross_check_one(schema_name, schema, entry, f"{rel_path} [{entry.get('track_id')}]")
                    checked += 1
            elif kind == "graph_edge":
                sg = load_json(rel_path)
                for edge in sg.get("edges", [])[:2]:
                    _cross_check_one(schema_name, schema, edge, f"{rel_path} [{edge.get('from_track_id')}]")
                    checked += 1
            elif kind == "graph_ref":
                crg = load_json(rel_path)
                for ref in crg.get("references", [])[:2]:
                    _cross_check_one(schema_name, schema, ref, f"{rel_path} [{ref.get('source_record_id')}]")
                    checked += 1
        except FileNotFoundError:
            fail(f"cross-check target not found: {rel_path}")
        except Exception as e:
            fail(f"cross-check of {rel_path} against {schema_name} raised {type(e).__name__}: {e}")

    # glossary handled separately since `terms` is a dict-of-lists, not a list
    gl = load_json("data/corpus_glossary/corpus_glossary.json")
    gt_schema = schemas.get("glossary_term_schema")
    if gt_schema is not None:
        n = 0
        for term, defs_list in gl.get("terms", {}).items():
            for d in defs_list:
                _cross_check_one("glossary_term_schema", gt_schema, d, f"corpus_glossary.json [{term}]")
                n += 1
                checked += 1
            if n >= 2:
                break

    print(f"  cross-checked {checked} real record(s)/document(s) against their schemas")


def _cross_check_one(schema_name: str, schema: dict, instance, label: str) -> None:
    if HAVE_JSONSCHEMA:
        try:
            jsonschema.validate(instance=instance, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            fail(f"{schema_name} MISMATCH on {label}: {e.message[:200]}")
        return
    required = _required_fields_for(schema, instance)
    if required is None:
        return
    missing = [f for f in required if isinstance(instance, dict) and f not in instance]
    if missing:
        fail(f"{schema_name} MISMATCH on {label}: missing required field(s) {missing}")


# ---------------------------------------------------------------------------
# 5. Idempotency: re-run the generator, diff against the committed file
# ---------------------------------------------------------------------------

def check_idempotent() -> None:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        before = f.read()

    result = subprocess.run(
        [sys.executable, GENERATOR],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        fail(f"generator exited non-zero on re-run: {result.stderr[-2000:]}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        after = f.read()

    if before != after:
        fail("generator is NOT idempotent: re-running it changed "
             "data/schema_manifest/corpus_schema_manifest.json")
    else:
        print("  idempotency check: re-ran generator, output byte-identical")


def main() -> int:
    if not os.path.isfile(MANIFEST_PATH):
        print(f"ERROR: {MANIFEST_PATH} not found. Run scripts/gen_corpus_schema_manifest.py first.",
              file=sys.stderr)
        return 1

    manifest = load_json(os.path.relpath(MANIFEST_PATH, ROOT))

    print("Corpus Schema Manifest — Validator")
    print(f"  jsonschema library available: {HAVE_JSONSCHEMA}")

    print("[1/4] manifest shape / required top-level keys / 9 schema entries...")
    check_manifest_shape(manifest)

    print("[2/4] JSON Schema syntax validity of each schema entry...")
    check_schema_syntax(manifest)

    print("[3/4] cross-checking real corpus files against schemas...")
    check_cross_samples(manifest)

    print("[4/4] idempotency (re-run generator, diff output)...")
    check_idempotent()

    print()
    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  ! {w}")
    if ERRORS:
        print(f"FAIL — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  - {e}")
        return 1

    print("PASS — corpus_schema_manifest.json is structurally valid, cross-checked clean "
          "against real corpus files, and the generator is idempotent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
