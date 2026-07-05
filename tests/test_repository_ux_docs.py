"""Tests for the repository UX / navigation docs (README top + START_HERE/STATUS/REPOSITORY_MAP/USE_CASES).

Read-only documentation checks that lock the public-facing navigation files for a multilingual,
LLM-ready, official-source-based Saudi legal corpus for AI: the identity is stated, the four
navigation docs are cross-linked from README, STATUS records the baseline commit / counts /
boundaries, and no hidden legal claim creeps in (official Arabic source governs; external legal
review optional; not legal advice). This suite does not touch or replace any existing validator.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
START_HERE = os.path.join(ROOT, "START_HERE.md")
STATUS = os.path.join(ROOT, "STATUS.md")
REPO_MAP = os.path.join(ROOT, "REPOSITORY_MAP.md")
USE_CASES = os.path.join(ROOT, "USE_CASES.md")
UX_PRINCIPLES = os.path.join(ROOT, "docs", "REPOSITORY_UX_PRINCIPLES_AR.md")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_repository_ux_docs.py")

IDENTITY = "multilingual, llm-ready, official-source-based saudi legal corpus for ai"
BASELINE = "0a2e5c3e6457009ddf1d0ba2fb4d669091317ced"


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _norm(text):
    """Lowercase and collapse whitespace / blockquote markers for hard-wrap-tolerant matching."""
    return re.sub(r"\s+", " ", text.replace(">", " ")).lower()


def test_nav_docs_exist():
    for path in (README, START_HERE, STATUS, REPO_MAP, USE_CASES):
        assert os.path.exists(path), path


def test_readme_top_states_identity():
    top = _norm(_read(README)[:2000])
    assert IDENTITY in top


def test_readme_links_navigation_docs():
    low = _norm(_read(README))
    for link in ("start_here.md", "status.md", "repository_map.md", "use_cases.md"):
        assert link in low, link


def test_identity_in_every_nav_doc():
    for path in (START_HERE, STATUS, REPO_MAP, USE_CASES):
        assert IDENTITY in _norm(_read(path)), path


def test_not_legal_advice_in_every_nav_doc():
    for path in (START_HERE, STATUS, REPO_MAP, USE_CASES):
        assert "not legal advice" in _norm(_read(path)), path


def test_status_records_baseline_commit():
    assert BASELINE in _read(STATUS)


def test_status_records_counts():
    s = _read(STATUS)
    for token in ("281", "189", "5 files", "23 records", "14"):
        assert token in s, token


def test_status_records_boundaries():
    low = _norm(_read(STATUS))
    for boundary in (
        "p2-002 qa / p2-003 onward / p3: not started",
        "full chinese 281 layer: not created",
        "trilingual alignment: not created",
        "public release: not created",
        "official government adoption: not claimed",
        "official translation: not claimed",
    ):
        assert boundary in low, boundary


def test_review_model_language_present():
    low = _norm(_read(STATUS))
    assert "official arabic source governs" in low
    assert "external legal review is optional" in low
    assert "bachelor of law" in low


def test_arabic_ux_principles_present_and_concise():
    # Optional doc; if present it must stay concise (no research-style bloat).
    if os.path.exists(UX_PRINCIPLES):
        text = _read(UX_PRINCIPLES)
        assert "المصدر العربي الرسمي هو النص الحاكم" in text
        assert "المراجعة الخارجية اختيارية" in text
        assert len(text.splitlines()) < 80


def test_validator_passes():
    proc = subprocess.run([sys.executable, VALIDATOR], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
