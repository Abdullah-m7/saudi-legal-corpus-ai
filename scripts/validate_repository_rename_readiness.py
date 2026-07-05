#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate repository rename readiness (saudi-companies-law-ar-zh-llm -> saudi-legal-corpus-ai).

Read-only and idempotent. Confirms the repository is internally prepared for the manual GitHub
rename: the README and rename note carry the new name, REPOSITORY_RENAME.md documents the former and
current names plus the local-remote update commands, schema `$id` fields no longer point at the old
repository slug, forward-looking docs never present the old name as current (only as the former name),
no corpus/layer data was changed, and no official/adoption/legal-advice overclaim was introduced. This
validator does NOT rename the GitHub repository and does NOT replace any existing validator.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD_NAME = "saudi-companies-law-ar-zh-llm"
NEW_NAME = "saudi-legal-corpus-ai"
OLD_PATH = "al3obdi/" + OLD_NAME
NEW_PATH = "al3obdi/" + NEW_NAME

README = os.path.join(ROOT, "README.md")
RENAME = os.path.join(ROOT, "REPOSITORY_RENAME.md")
# Forward-looking identity docs: the old name may only appear as an explicit "former" reference.
FORWARD_DOCS = ["README.md", "START_HERE.md", "STATUS.md", "REPOSITORY_MAP.md", "USE_CASES.md"]

# Affirmative overclaims only (must NOT match negated disclaimers like "not an official translation").
BANNED = ("chinese is official", "chinese is binding", "chinese is governing",
          "is an official translation", "is officially adopted", "constitutes legal advice",
          "this is legal advice", "provides legal advice")
FORMER_MARKER = re.compile(r"former|formerly|old name", re.I)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _rc(path):
    try:
        return len(_load(path)["records"])
    except Exception:
        return None


def main(argv=None) -> int:
    problems = []

    # 1. README carries the new repository name.
    if not os.path.exists(README):
        problems.append("README.md missing")
    elif NEW_NAME not in _read(README):
        problems.append("README.md must include the new repository name %r" % NEW_NAME)

    # 2-4. REPOSITORY_RENAME.md exists and documents former+current names and remote update commands.
    if not os.path.exists(RENAME):
        problems.append("REPOSITORY_RENAME.md must exist")
    else:
        r = _read(RENAME)
        if OLD_NAME not in r:
            problems.append("REPOSITORY_RENAME.md must state the former name %r" % OLD_NAME)
        if NEW_NAME not in r:
            problems.append("REPOSITORY_RENAME.md must state the target name %r" % NEW_NAME)
        if "git remote set-url origin" not in r:
            problems.append("REPOSITORY_RENAME.md must include the git remote set-url command")
        if ("git@github.com:%s.git" % NEW_PATH) not in r:
            problems.append("REPOSITORY_RENAME.md must include the SSH remote for the new path")
        if ("https://github.com/%s.git" % NEW_PATH) not in r:
            problems.append("REPOSITORY_RENAME.md must include the HTTPS remote for the new path")
        low = r.lower()
        if "redirect" not in low:
            problems.append("REPOSITORY_RENAME.md must note GitHub redirects after rename")
        if "do not create a new repository using the old name" not in low:
            problems.append("REPOSITORY_RENAME.md must warn against reusing the old name")

    # 5. Schema $id fields must not point at the old repository slug.
    for f in glob.glob(os.path.join(ROOT, "schemas", "**", "*.schema.json"), recursive=True):
        try:
            sid = _load(f).get("$id", "")
        except (ValueError, OSError):
            problems.append("schema not valid JSON: %s" % os.path.relpath(f, ROOT))
            continue
        if OLD_NAME in sid:
            problems.append("schema $id still points at old slug: %s" % os.path.relpath(f, ROOT))
        if NEW_NAME not in sid:
            problems.append("schema $id must reference the new slug: %s" % os.path.relpath(f, ROOT))

    # 6. Forward-looking identity docs must not present the old name as current: every mention of the
    #    old slug must be preceded (within a short window, tolerant of line wrapping) by a
    #    former/old-name marker.
    for name in FORWARD_DOCS:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        norm = re.sub(r"\s+", " ", _read(path))
        for m in re.finditer(re.escape(OLD_NAME), norm):
            ctx = norm[max(0, m.start() - 80):m.start()]
            if not FORMER_MARKER.search(ctx):
                problems.append("%s presents the old name without a nearby 'former' marker" % name)
                break

    # 7. Law profile repository metadata updated (not corpus data; value only).
    prof = os.path.join(ROOT, "data", "legal_corpus_factory", "law_profiles",
                        "sa_companies_law_m132_1443.profile.json")
    if os.path.exists(prof):
        p = _load(prof)
        cfr = p.get("created_for_repository", "")
        if OLD_NAME in cfr:
            problems.append("law profile created_for_repository still points at old slug")

    # 8. No corpus / layer data changed (counts intact).
    counts = {
        "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json": 281,
        "data/official_english_legal_llm/companies_law_m132_1443_official_english_legal_llm_001_281.json": 281,
        "data/english_reference/companies_law_m132_1443_en_reference_001_281.json": 281,
        "data/chinese_internal_legal_llm/companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json": 189,
    }
    for rel, n in counts.items():
        if _rc(os.path.join(ROOT, rel)) != n:
            problems.append("corpus layer changed (must be untouched): %s != %d" % (rel, n))
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum((_rc(x) or 0) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    if len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                  "bab*_zh_source_extracted_articles_*.json"))) != 14:
        problems.append("Chinese source extracted files must remain 14")
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_load(q).get("entries", [])) != 281:
        problems.append("OCR manual_review_queue must remain 281 entries")
    p1 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p1_001",
                      "companies_law_m132_1443_zh_internal_remediation_p1_001.json")
    if not os.path.exists(p1) or _rc(p1) != 20:
        problems.append("P1-001 remediation data must remain present with 20 records (untouched)")

    # 9. No official/adoption/legal-advice overclaim introduced by the rename note; it must keep the
    #    non-official / not-legal-advice posture.
    if os.path.exists(RENAME):
        low = _read(RENAME).lower()
        for term in BANNED:
            if term in low:
                problems.append("REPOSITORY_RENAME.md introduces a banned overclaim: %r" % term)
        if "not legal advice" not in low:
            problems.append("REPOSITORY_RENAME.md must retain the 'not legal advice' posture")
        if "not official" not in low:
            problems.append("REPOSITORY_RENAME.md must retain the non-official posture")

    print("=" * 60)
    print("Repository rename readiness validation (%s -> %s)" % (OLD_NAME, NEW_NAME))
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Rename readiness: README + REPOSITORY_RENAME.md carry the new name %r; the rename "
          "note documents the former name %r, the SSH/HTTPS remote update commands, the redirect "
          "note, and the reuse warning; all schema $id fields reference the new slug (none point at "
          "the old slug); forward-looking docs mention the old name only as the former name; the law "
          "profile repository metadata is updated; no corpus/P0/P1 data changed; no official / "
          "adoption / legal-advice overclaim introduced. The GitHub rename remains a manual step."
          % (NEW_NAME, OLD_NAME))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
