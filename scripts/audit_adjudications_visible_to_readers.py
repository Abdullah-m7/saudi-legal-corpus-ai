#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""An adjudication recorded only in a test is invisible to whoever reads the corpus.

Three times in one sitting a repair was proposed for something the corpus had
already decided and encoded — the arbitration label anomaly, the duplicate
«٣/١٠٤» in sharia_procedure, the «المادية» typo in its law. Each time a track
validator refused the change and named the reason. The corpus knew.

But a validator is read by whoever runs the tests, not by whoever reads the
corpus. A reader looking at «المادة الحادية والعشرون» on article 31 has no way
to learn it is the official text's own misprint faithfully preserved — unless
the ARTIFACT says so, in `known_unresolved_discrepancies`, where every other
disclosure lives.

This audit asks, for every deliberate judgment a track validator encodes,
whether a reader can see it too:

  * EXPECTED_ANOMALIES / ACCEPTED_* / EXPECTED_DUP* — a named deviation the
    track asserts is correct-as-published;
  * a comment marking a source typo, an anomaly, or text preserved verbatim
    against the temptation to correct it;
  * VISUALLY_ADJUDICATED — articles a human read off a page image because the
    text channel could not be trusted. That is a statement about how much of the
    track rests on one person's eyes, and a reader is entitled to know which
    articles those are.

For each, it looks for any disclosure on the track's own artifact that plausibly
covers it. A track that encodes a judgment and discloses nothing is the finding.

Read-only; writes only its own report.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "reports", "corpus_text_quality_audit")

# What counts as a recorded judgment, and how it reads in the validator source.
JUDGMENTS = [
    ("named_anomaly", re.compile(r"^\s*(EXPECTED_ANOMALIES|ACCEPTED_\w+|EXPECTED_DUP\w*)\s*=\s*(.+)$",
                                 re.M)),
    ("preserved_source_defect", re.compile(
        r"^\s*#\s*(.*(?:typo|anomal|preserved verbatim|verbatim as published|"
        r"flag-don't-correct|not silently (?:corrected|fixed)).*)$", re.M | re.I)),
    ("visually_adjudicated", re.compile(r"^\s*VISUALLY_ADJUDICATED\s*=\s*(.+)$", re.M)),
]
EMPTY = {"set()", "{}", "[]", "frozenset()", "None"}

# Words that, appearing in a disclosure, mean it is plausibly ABOUT a preserved
# source defect or a visual adjudication. Deliberately generous: the finding this
# audit wants is a track that discloses NOTHING, and a generous matcher makes
# that finding harder to reach rather than easier.
DISCLOSURE_HINTS = (
    "خطأ", "الخطأ", "شذوذ", "كما في المصدر", "حرفي", "حرفياً", "لم يُصحَّح", "لم يصحح",
    "أُبقي", "ابقي", "محفوظ", "المصدر نفسه", "مطابقة بصرية", "بصري", "قراءة بصرية",
    "غير مصحح", "typo", "anomal", "verbatim", "visually",
)


def track_id_from(path):
    name = os.path.basename(path)
    name = name[len("validate_"):]
    for suffix in ("_tracks.py", "_track.py"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def artifacts_for(track):
    """The artifacts a validator's track id might live under.

    A validator is named for the track AND its component («sharia_procedure_law»),
    so the longest matching directory prefix is the right one; matching on the
    first path segment alone would attribute the law's judgments to the
    regulation's artifact and vice versa."""
    out = []
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in glob.glob(os.path.join(ROOT, pattern)):
            rel = os.path.relpath(path, os.path.join(ROOT, "sources"))
            parts = rel.split(os.sep)
            tid = parts[0]
            comp = parts[-3] if len(parts) == 4 else None
            key = "%s_%s" % (tid, comp) if comp else tid
            if track == key or track == tid:
                out.append((key, path))
    # prefer an exact track+component match over the bare track id
    exact = [p for k, p in out if k == track]
    return exact or [p for _k, p in out]


def disclosures(path):
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception:                                              # noqa: BLE001
        return []
    out = []
    for d in doc.get("known_unresolved_discrepancies") or []:
        if isinstance(d, dict):
            out.append("%s %s" % (d.get("article_key", ""), d.get("description", "")))
        elif isinstance(d, str):
            out.append(d)
    note = doc.get("verification_methodology_note")
    if note:
        out.append(note)
    return out


def main():
    findings, covered = [], 0
    for vpath in sorted(glob.glob(os.path.join(ROOT, "scripts", "validate_*_track*.py"))):
        src = open(vpath, encoding="utf-8").read()
        track = track_id_from(vpath)
        judged = defaultdict(list)
        for kind, rx in JUDGMENTS:
            for m in rx.finditer(src):
                val = (m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)).strip()
                if val in EMPTY:
                    continue
                judged[kind].append(val[:200])
        if not judged:
            continue

        paths = artifacts_for(track)
        if not paths:
            findings.append({"track": track, "judgments": dict(judged),
                             "problem": "no artifact found for this validator's track id"})
            continue
        blob = " ".join(" ".join(disclosures(p)) for p in paths)
        if any(h in blob for h in DISCLOSURE_HINTS):
            covered += 1
            continue
        findings.append({"track": track,
                         "artifacts": [os.path.relpath(p, ROOT) for p in paths],
                         "judgments": dict(judged),
                         "problem": ("the validator encodes a deliberate judgment about this "
                                     "track's source, and nothing in the artifact tells a "
                                     "reader about it")})

    report = {
        "generated_note": (
            "Asks, for every deliberate judgment a track validator encodes about its source — a "
            "named anomaly, a preserved typo, an article read off a page image — whether a "
            "reader of the CORPUS can see it, or only a reader of the TESTS. Three times in one "
            "sitting a repair was proposed for something the corpus had already decided and "
            "encoded in a validator; each time the validator refused it and named the reason, "
            "and each time nothing in the artifact would have told a reader. The matcher for "
            "'is it disclosed' is deliberately generous, because the finding worth having is a "
            "track that discloses NOTHING. Read-only."),
        "validators_encoding_a_judgment": covered + len(findings),
        "of_those_disclosing_it_to_readers": covered,
        "of_those_disclosing_nothing": len(findings),
        "findings": findings,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "adjudications_visible_to_readers.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("validators encoding a judgment: %d | disclosed to readers: %d | disclosing nothing: %d"
          % (covered + len(findings), covered, len(findings)))
    for f in findings[:40]:
        kinds = ",".join(f["judgments"])
        print("   %-46s %s" % (f["track"][:46], kinds))
    print("wrote reports/corpus_text_quality_audit/adjudications_visible_to_readers.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
