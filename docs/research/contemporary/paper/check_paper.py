#!/usr/bin/env python3
"""Every figure in the manuscript must come from a results file.

check_docs.py does this for the research notes. The manuscript is where a
hand-typed number does the most damage, so it gets its own guard, and the
guard is deliberately literal: it re-reads the JSON the analysis wrote and
asserts the string is present in the markdown.

    python3 check_paper.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = HERE.parent
MS = (HERE / "MANUSCRIPT.md").read_text(encoding="utf-8")
claim = json.loads((C / "claim_results.json").read_text(encoding="utf-8"))
align = json.loads((C / "alignment_view.json").read_text(encoding="utf-8"))
win = json.loads((C / "windows_results.json").read_text(encoding="utf-8"))

V3 = claim["views"]["contemporary_3y"]
TYPES = ["contract", "legal_maxim", "custom", "fiqh_source", "discretion",
         "judicial_principle", "statute", "quran", "hadith"]
checks = []


def want(label, value):
    checks.append((label, str(value), str(value) in MS))


# the main table: court share, both party shares, for every type
for t in TYPES:
    want(f"{t} court share", f"{V3['strict_court'][t]:.2f}")
    want(f"{t} party strict", f"{V3['strict_party'][t]:.2f}")
    want(f"{t} party wide", f"{V3['wide_party'][t]:.2f}")

# the robustness grid
for v in ("contemporary_5y", "contemporary_3y", "post_Evidence", "post_CTL"):
    for t in TYPES:
        s, w = claim["views"][v][f"strict_ratio"][t], claim["views"][v]["wide_ratio"][t]
        want(f"{v}/{t}", f"{s:.2f} / {w:.2f}")

# mention totals
want("court mentions", f"{V3['strict_courtN']:,}")
want("party strict mentions", f"{V3['strict_partyN']:,}")
want("party wide mentions", f"{V3['wide_partyN']:,}")

# non-statutory conditioning
ns = V3["strata"]["non_statutory"]
for t in ("contract", "legal_maxim", "custom", "fiqh_source", "discretion",
          "judicial_principle", "quran", "hadith"):
    want(f"non-stat court {t}", f"{ns['court'][t]:.2f}")
    want(f"non-stat party {t}", f"{ns['party'][t]:.2f}")
want("non-stat court n", f"{ns['courtN']:,}")
want("non-stat party n", f"{ns['partyN']:,}")

# transitions
want("paired judgments", f"{V3['pairedDocs']:,}")
for t in TYPES:
    r = V3["transitions"].get(f"{t}->statute")
    if r:
        want(f"lift {t}->statute", f"{r['lift']:.2f}")

# alignment
a = align["strict"]
for lvl, key in (("authorityFamily", "0.5"), ("instrument", "0.333")):
    want(f"align {lvl} median", a[lvl]["medianJaccard"])
want("align article no-overlap", f"{a['article']['shareNoOverlap']}")
want("align family no-overlap", f"{a['authorityFamily']['shareNoOverlap']}")
want("align family identical", f"{a['authorityFamily']['shareIdentical']}")
want("align instrument no-overlap", f"{a['instrument']['shareNoOverlap']}")

# windows
for v in ("contemporary_5y", "contemporary_3y", "post_Evidence", "post_CTL"):
    want(f"{v} judgments", f"{win['views'][v]['judgments']:,}")

bad = [c for c in checks if not c[2]]
print(f"{len(checks) - len(bad)} of {len(checks)} manuscript figures "
      f"trace to a results file")
for label, val, _ in bad:
    print(f"  MISSING  {label:<38}{val}")
sys.exit(1 if bad else 0)
