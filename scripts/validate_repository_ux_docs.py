#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the repository UX / navigation docs (README top + START_HERE/STATUS/REPOSITORY_MAP/USE_CASES).

Multilingual, LLM-ready, official-source-based Saudi legal corpus for AI. Read-only and idempotent.
Confirms the public-facing navigation files exist and carry the correct project identity and legal/
status boundaries, so a new visitor understands the repository quickly and no hidden legal claim
creeps in. This validator ONLY checks documentation presence/content; it does not touch, replace, or
re-run any existing corpus/layer validator.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

README = os.path.join(ROOT, "README.md")
START_HERE = os.path.join(ROOT, "START_HERE.md")
STATUS = os.path.join(ROOT, "STATUS.md")
REPO_MAP = os.path.join(ROOT, "REPOSITORY_MAP.md")
USE_CASES = os.path.join(ROOT, "USE_CASES.md")

# Identity phrase every top-level UX doc must carry (lowercased match).
IDENTITY = "multilingual, llm-ready, official-source-based saudi legal corpus for ai"

# Legal / status boundary phrases (lowercased) that must appear where required.
NOT_LEGAL_ADVICE = "not legal advice"
ARABIC_GOVERNS = "official arabic source governs"
EXTERNAL_OPTIONAL = "external legal review is optional"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _norm(text: str) -> str:
    """Lowercase and collapse whitespace / markdown blockquote markers so a required phrase is
    matched even when hard-wrapped across lines."""
    return re.sub(r"\s+", " ", text.replace(">", " ")).lower()


def main(argv=None) -> int:
    problems = []

    required = {
        "README.md": README,
        "START_HERE.md": START_HERE,
        "STATUS.md": STATUS,
        "REPOSITORY_MAP.md": REPO_MAP,
        "USE_CASES.md": USE_CASES,
    }
    texts = {}
    for name, path in required.items():
        if not os.path.exists(path):
            problems.append("missing UX doc: %s" % name)
            continue
        texts[name] = _read(path)

    # README must cross-link to the four navigation docs.
    if "README.md" in texts:
        low = _norm(texts["README.md"])
        if IDENTITY not in low:
            problems.append("README.md must state the corpus identity phrase")
        for link in ("start_here.md", "status.md", "repository_map.md", "use_cases.md"):
            if link not in low:
                problems.append("README.md must link to %s" % link)
        # README top must position the repo, not old Chinese-remediation detail.
        top = _norm(texts["README.md"][:2000])
        if IDENTITY not in top:
            problems.append("README.md top (first ~2000 chars) must carry the identity phrase")

    # Every top-level UX doc must carry the identity phrase and the not-legal-advice boundary.
    for name in ("START_HERE.md", "STATUS.md", "REPOSITORY_MAP.md", "USE_CASES.md"):
        if name not in texts:
            continue
        low = _norm(texts[name])
        if IDENTITY not in low:
            problems.append("%s must state the corpus identity phrase" % name)
        if NOT_LEGAL_ADVICE not in low:
            problems.append("%s must state 'not legal advice'" % name)

    # STATUS.md must carry the baseline commit, counts, and the explicit boundaries.
    if "STATUS.md" in texts:
        s = texts["STATUS.md"]
        low = _norm(s)
        if "0a2e5c3e6457009ddf1d0ba2fb4d669091317ced" not in s:
            problems.append("STATUS.md must record the baseline main commit")
        for token in ("281", "189", "5 files", "23 records", "14"):
            if token not in low:
                problems.append("STATUS.md must record count token %r" % token)
        for boundary in (
            "p2-003 onward / p3: not started",
            "full chinese 281 layer: not created",
            "trilingual alignment: not created",
            "public release: not created",
            "official government adoption: not claimed",
            "official translation: not claimed",
        ):
            if boundary not in low:
                problems.append("STATUS.md must state boundary: %r" % boundary)
        if ARABIC_GOVERNS not in low:
            problems.append("STATUS.md must state that the official Arabic source governs")
        if EXTERNAL_OPTIONAL not in low:
            problems.append("STATUS.md must state external legal review is optional")

    # START_HERE.md and USE_CASES.md must not overclaim official/production status.
    for name in ("START_HERE.md", "USE_CASES.md"):
        if name not in texts:
            continue
        low = _norm(texts[name])
        if ARABIC_GOVERNS not in low:
            problems.append("%s must state that the official Arabic source governs" % name)

    print("=" * 60)
    print("Repository UX / navigation docs validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Repository UX docs (README top + START_HERE + STATUS + REPOSITORY_MAP + "
          "USE_CASES): identity = multilingual, LLM-ready, official-source-based Saudi legal "
          "corpus for AI; README links the four navigation docs; STATUS records baseline commit, "
          "layer counts, and the not-started/not-created/not-claimed boundaries; official Arabic "
          "source governs; external legal review optional; not legal advice. Documentation only; "
          "no existing validator or corpus data touched.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
