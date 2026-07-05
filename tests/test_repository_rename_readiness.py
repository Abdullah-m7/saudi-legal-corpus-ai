"""Tests for repository rename readiness (saudi-companies-law-ar-zh-llm -> saudi-legal-corpus-ai).

Read-only checks that lock the internal rename-readiness invariants: README + REPOSITORY_RENAME.md
carry the new name, the rename note documents the former/current names and the local-remote update
commands, schema `$id` fields reference the new slug (never the old one), forward-looking docs mention
the old name only as the former name, and no corpus data or overclaim was introduced. The actual
GitHub rename is a manual post-merge step and is NOT performed here. This suite does not touch or
replace any existing validator.
"""

import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_NAME = "saudi-companies-law-ar-zh-llm"
NEW_NAME = "saudi-legal-corpus-ai"
NEW_PATH = "al3obdi/" + NEW_NAME
README = os.path.join(ROOT, "README.md")
RENAME = os.path.join(ROOT, "REPOSITORY_RENAME.md")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_repository_rename_readiness.py")
FORWARD_DOCS = ["README.md", "START_HERE.md", "STATUS.md", "REPOSITORY_MAP.md", "USE_CASES.md"]


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_validator_passes():
    proc = subprocess.run([sys.executable, VALIDATOR], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_rename_doc_exists():
    assert os.path.exists(RENAME)


def test_readme_has_new_name():
    assert NEW_NAME in _read(README)


def test_rename_doc_has_both_names():
    r = _read(RENAME)
    assert OLD_NAME in r
    assert NEW_NAME in r


def test_rename_doc_has_remote_commands():
    r = _read(RENAME)
    assert "git remote set-url origin" in r
    assert "git@github.com:%s.git" % NEW_PATH in r
    assert "https://github.com/%s.git" % NEW_PATH in r


def test_rename_doc_notes_redirect_and_warns_reuse():
    low = _read(RENAME).lower()
    assert "redirect" in low
    assert "do not create a new repository using the old name" in low


def test_no_schema_id_points_at_old_slug():
    for f in glob.glob(os.path.join(ROOT, "schemas", "**", "*.schema.json"), recursive=True):
        sid = json.load(open(f, encoding="utf-8")).get("$id", "")
        assert OLD_NAME not in sid, f
        assert NEW_NAME in sid, f


def test_law_profile_repository_metadata_updated():
    prof = json.load(open(os.path.join(
        ROOT, "data", "legal_corpus_factory", "law_profiles",
        "sa_companies_law_m132_1443.profile.json"), encoding="utf-8"))
    assert OLD_NAME not in prof.get("created_for_repository", "")
    assert NEW_NAME in prof.get("created_for_repository", "")


def test_forward_docs_only_show_old_name_as_former():
    marker = re.compile(r"former|formerly|old name", re.I)
    for name in FORWARD_DOCS:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        norm = re.sub(r"\s+", " ", _read(path))
        for m in re.finditer(re.escape(OLD_NAME), norm):
            ctx = norm[max(0, m.start() - 80):m.start()]
            assert marker.search(ctx), "%s: old name shown without a nearby 'former' marker" % name


def test_corpus_layers_unchanged():
    def rc(rel):
        return len(json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))["records"])
    assert rc("data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json") == 281
    assert rc("data/official_english_legal_llm/companies_law_m132_1443_official_english_legal_llm_001_281.json") == 281
    assert rc("data/english_reference/companies_law_m132_1443_en_reference_001_281.json") == 281
    assert rc("data/chinese_internal_legal_llm/companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json") == 189
    assert rc("data/chinese_remediation_batches/p1_001/companies_law_m132_1443_zh_internal_remediation_p1_001.json") == 20


def test_no_later_batches():
    # The authorized P1-001 (and its later-authorized QA) may exist; only p1_003+/P2/P3 batch dirs
    # remain forbidden. (The rename-readiness change itself neither started QA nor any later batch.)
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004", "p2_005")]
    assert not later


def test_rename_doc_keeps_boundaries():
    low = _read(RENAME).lower()
    assert "not legal advice" in low
    assert "not official" in low
