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
# the manuscript is contemporary_3y throughout, so the overlap figures come
# from overlap.py (which restricts to 1444-1446), not from alignment_view.json
# (which spans the whole five-year layer). Pointing the guard at the wrong one
# is exactly the error it exists to catch.
ov = json.loads((C / "overlap_results.json").read_text(encoding="utf-8"))
ret = json.loads((C / "retrieval_results.json").read_text(encoding="utf-8"))
win = json.loads((C / "windows_results.json").read_text(encoding="utf-8"))
# section VII's functional-robustness paragraph reads from the two-layer test
tl = json.loads((C / "twolayers_results.json").read_text(encoding="utf-8"))
eco = json.loads((C / "ecology_results.json").read_text(encoding="utf-8"))

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

# section VII, the functional-divergence robustness paragraph
T = tl["transitions"]["party"]
want("judgments sharing an instrument", f"{T['judgmentsSharingAnInstrument']:,}")
for lab, k in (
        ("inst->inst, different articles",
         "party=INSTITUTIONAL_OPERATION -> court=INSTITUTIONAL_OPERATION "
         "[different articles]"),
        ("inst->dispute, different articles",
         "party=INSTITUTIONAL_OPERATION -> court=DISPUTE_DECISION "
         "[different articles]"),
        ("dispute->inst, different articles",
         "party=DISPUTE_DECISION -> court=INSTITUTIONAL_OPERATION "
         "[different articles]")):
    want(lab, T["table"][k])
E = {r["article"]: r for r in eco["dives"]["evidence_law"]["articles"]}
want("evidence 29 court judgments", f"{E[29]['courtJudgments']:,}")
want("evidence 29 party judgments", E[29]["partyJudgments"])
want("evidence 29 both", E[29]["bothPct"])

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

# overlap, contemporary_3y, strict
o = ov["specs"]["strict"]
for key, label in (("fam", "family"), ("inst_all", "instrument"),
                   ("art_all", "article")):
    want(f"overlap {label} median", f"{o[key]['medianJaccard']:.3f}")
    want(f"overlap {label} no-overlap", f"{o[key]['noOverlapPct']}")
    want(f"overlap {label} exact", f"{o[key]['exactMatchPct']}")
want("overlap article, structural removed", f"{o['art_nostruct']['noOverlapPct']}")
want("overlap article, dispute only", f"{o['art_dispute']['noOverlapPct']}")
want("overlap instrument, dispute only exact",
     f"{o['inst_dispute']['exactMatchPct']}")

# the conditional
c = ov["conditional"]["strict"]
want("P(shared instrument)", f"{c['sharedInstrumentPct']}")
want("P(shared article | shared instrument)",
     f"{c['sharedArticleGivenInstrumentPct']}")
want("P(shared article | statute)", f"{c['sharedArticleGivenStatutePct']}")
want("arbitration same-article",
     f"{c['byInstrument']['arbitration_law']['sameArticlePct']}")
want("regulation same-article",
     f"{c['byInstrument']['commercial_courts_implementing_regulation']['sameArticlePct']}")

# retrieval
want("spearman court vs party", f"{ret['spearman']['court_vs_party']}")
want("articles ranked", f"{ret['articlesTotal']:,}")
want("court top50 not in full top50", 50 - ret["overlap@50"]["full_vs_court"])

# windows
for v in ("contemporary_5y", "contemporary_3y", "post_Evidence", "post_CTL"):
    want(f"{v} judgments", f"{win['views'][v]['judgments']:,}")

bad = [c for c in checks if not c[2]]
print(f"{len(checks) - len(bad)} of {len(checks)} manuscript figures "
      f"trace to a results file")
for label, val, _ in bad:
    print(f"  MISSING  {label:<38}{val}")
sys.exit(1 if bad else 0)
