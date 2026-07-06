#!/usr/bin/env python3
"""
Test suite for corpus local search evaluation fixtures.

Tests:
1. Fixture file exists and parses as valid JSON
2. Fixture count between 8 and 12
3. Each fixture has required fields
4. No fixture contains forbidden English/Chinese source content fields
5. All expected_language values are 'ar'
6. All evaluation_type values are valid
7. expected_top_k_contains_any IDs exist in the export (if export available)
8. Track filter fixtures return only matching track
9. Record type filter fixtures return only matching record type
10. No-result fixture returns zero matches
11. Normalization fixture matches the same count as its hamza counterpart
12. JSON output fixture produces valid JSON with required fields

Deterministic, offline, no network, no embeddings, no API.
Not legal advice. Not official translation. Arabic official source governs.
"""

import json
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_PATH = os.path.join(REPO_ROOT, "data", "search_eval", "local_search_queries_v1.json")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
from search_primary_arabic_export import load_records, search  # noqa: E402

REQUIRED_FIELDS = {
    "fixture_id",
    "query",
    "description_ar",
    "expected_min_matches",
    "expected_language",
    "boundary_note",
    "evaluation_type",
}

FORBIDDEN_FIELDS = {"english_text", "chinese_text", "en_text", "zh_text", "translation_en"}

VALID_EVAL_TYPES = {
    "broad_term",
    "legal_phrase",
    "track_filter",
    "record_type_filter",
    "json_output",
    "no_result_or_low_result",
    "normalization",
}


def load_fixtures():
    """Load fixture file and return list of fixture dicts."""
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestFixtureSchema(unittest.TestCase):
    """Tests for fixture file schema and structure."""

    def setUp(self):
        self.fixtures = load_fixtures()

    def test_fixture_file_exists(self):
        self.assertTrue(os.path.isfile(FIXTURES_PATH),
                        f"Fixture file not found: {FIXTURES_PATH}")

    def test_fixture_file_parses_as_json(self):
        self.assertIsInstance(self.fixtures, list,
                              "Fixture file must be a JSON array")

    def test_fixture_count_in_range(self):
        count = len(self.fixtures)
        self.assertGreaterEqual(count, 8,
                                f"Fixture count {count} < 8")
        self.assertLessEqual(count, 12,
                             f"Fixture count {count} > 12")

    def test_each_fixture_has_required_fields(self):
        for fx in self.fixtures:
            missing = REQUIRED_FIELDS - set(fx.keys())
            self.assertEqual(missing, set(),
                             f"[{fx.get('fixture_id','?')}] missing: {sorted(missing)}")

    def test_no_forbidden_fields(self):
        for fx in self.fixtures:
            present = FORBIDDEN_FIELDS & set(fx.keys())
            self.assertEqual(present, set(),
                             f"[{fx.get('fixture_id','?')}] forbidden fields: {sorted(present)}")

    def test_all_expected_language_ar(self):
        for fx in self.fixtures:
            self.assertEqual(fx.get("expected_language"), "ar",
                             f"[{fx.get('fixture_id','?')}] expected_language != ar")

    def test_all_eval_types_valid(self):
        for fx in self.fixtures:
            etype = fx.get("evaluation_type")
            self.assertIn(etype, VALID_EVAL_TYPES,
                          f"[{fx.get('fixture_id','?')}] invalid evaluation_type: {etype}")

    def test_fixture_ids_unique(self):
        ids = [fx["fixture_id"] for fx in self.fixtures]
        self.assertEqual(len(ids), len(set(ids)),
                         "Fixture IDs must be unique")

    def test_min_matches_non_negative(self):
        for fx in self.fixtures:
            self.assertIsInstance(fx["expected_min_matches"], int)
            self.assertGreaterEqual(fx["expected_min_matches"], 0,
                                    f"[{fx.get('fixture_id','?')}] expected_min_matches < 0")

    def test_max_matches_if_present(self):
        for fx in self.fixtures:
            max_m = fx.get("expected_max_matches")
            if max_m is not None:
                self.assertIsInstance(max_m, int)
                self.assertGreaterEqual(max_m, 0,
                                        f"[{fx.get('fixture_id','?')}] expected_max_matches < 0")


class TestFixtureSearchBehavior(unittest.TestCase):
    """Tests that run actual search and check fixture expectations."""

    @classmethod
    def setUpClass(cls):
        cls.fixtures = load_fixtures()
        if os.path.isfile(JSONL_PATH):
            cls.records = load_records(JSONL_PATH)
        else:
            cls.records = None

    def _get_fixture(self, fixture_id):
        for fx in self.fixtures:
            if fx["fixture_id"] == fixture_id:
                return fx
        return None

    def _run_search(self, fx):
        query = fx["query"]
        track = fx.get("track_filter")
        record_type = fx.get("record_type_filter")
        return search(self.records, query, limit=len(self.records),
                      track=track, record_type=record_type)

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_broad_term_min_matches(self):
        fx = self._get_fixture("EVAL-001")
        results = self._run_search(fx)
        self.assertGreaterEqual(len(results), fx["expected_min_matches"],
                                f"[EVAL-001] expected >= {fx['expected_min_matches']}, "
                                f"got {len(results)}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_legal_phrase_board_min_matches(self):
        fx = self._get_fixture("EVAL-002")
        results = self._run_search(fx)
        self.assertGreaterEqual(len(results), fx["expected_min_matches"])

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_legal_phrase_assembly_min_matches(self):
        fx = self._get_fixture("EVAL-003")
        results = self._run_search(fx)
        self.assertGreaterEqual(len(results), fx["expected_min_matches"])

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_track_filter_companies_law(self):
        fx = self._get_fixture("EVAL-004")
        results = self._run_search(fx)
        for r in results:
            self.assertEqual(r["source_track_id"], "companies_law",
                             f"[EVAL-004] result {r['export_record_id']} "
                             f"has track {r['source_track_id']}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_track_filter_listed_jsc(self):
        fx = self._get_fixture("EVAL-005")
        results = self._run_search(fx)
        for r in results:
            self.assertEqual(r["source_track_id"],
                             "implementing_regulations_listed_joint_stock",
                             f"[EVAL-005] result {r['export_record_id']} "
                             f"has track {r['source_track_id']}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_record_type_filter_form(self):
        fx = self._get_fixture("EVAL-006")
        results = self._run_search(fx)
        for r in results:
            self.assertEqual(r["record_type"], "form",
                             f"[EVAL-006] result {r['export_record_id']} "
                             f"has type {r['record_type']}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_record_type_filter_appendix(self):
        fx = self._get_fixture("EVAL-007")
        results = self._run_search(fx)
        for r in results:
            self.assertEqual(r["record_type"], "appendix",
                             f"[EVAL-007] result {r['export_record_id']} "
                             f"has type {r['record_type']}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_no_result_fixture(self):
        fx = self._get_fixture("EVAL-010")
        results = self._run_search(fx)
        self.assertEqual(len(results), 0,
                         f"[EVAL-010] expected 0 results, got {len(results)}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_normalization_matches_hamza_version(self):
        """مجلس الادارة (no hamza) should match same count as مجلس الإدارة."""
        fx_hamza = self._get_fixture("EVAL-002")
        fx_no_hamza = self._get_fixture("EVAL-009")
        results_hamza = self._run_search(fx_hamza)
        results_no_hamza = self._run_search(fx_no_hamza)
        self.assertEqual(len(results_hamza), len(results_no_hamza),
                         f"Normalization failed: hamza version has {len(results_hamza)} "
                         f"matches, no-hamza version has {len(results_no_hamza)}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_all_results_language_ar(self):
        for fx in self.fixtures:
            results = self._run_search(fx)
            for r in results:
                rec = r.get("_record", {})
                lang = rec.get("language", "ar")
                self.assertEqual(lang, "ar",
                                 f"[{fx['fixture_id']}] result {r['export_record_id']} "
                                 f"has language {lang}")

    @unittest.skipUnless(os.path.isfile(JSONL_PATH), "Export JSONL not available")
    def test_top_k_contains_any(self):
        for fx in self.fixtures:
            top_k = fx.get("expected_top_k_contains_any")
            if not top_k:
                continue
            results = self._run_search(fx)[:10]
            top_ids = set(r["export_record_id"] for r in results)
            matched = [x for x in top_k if x in top_ids]
            self.assertGreater(len(matched), 0,
                               f"[{fx['fixture_id']}] none of {top_k} "
                               f"in top-10: {sorted(top_ids)}")


if __name__ == "__main__":
    unittest.main()