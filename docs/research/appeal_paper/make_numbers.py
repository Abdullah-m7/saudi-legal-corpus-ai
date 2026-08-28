#!/usr/bin/env python3
"""Generate numbers.tex for paper 9 from the analysis outputs.

Same discipline as papers 5, 6 and 8, adopted here from the first draft
rather than retrofitted: every measurement in the manuscript is computed by a
script, written to JSON, and typeset from a macro. check_numbers.py refuses to
build a manuscript that types one by hand.

Paper 8 learned this the expensive way. Its cover letter was written by hand
because a letter «is not the paper», and it went out carrying two figures from
a stale run.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "arabic_paper"
sys.path.insert(0, str(SRC))


def load(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))


def pv(p):
    """A p-value the way a table prints one, not the way a float stores one."""
    return "<.001" if p < 0.001 else f"{p:.3f}".lstrip("0")


def pp(v):
    """A signed difference in percentage points, the way a table prints one."""
    return f"{v:+.1f}".replace("-", "$-$")


def holm(terms):
    """Holm-adjusted p-values across the terms tested in one model.

    Eleven coefficients are tested here, so a term at p = .04 is not news. This
    is a derivation from the deposited p-values, not a new measurement: it is
    computed in the script for the same reason everything else is.
    """
    ordered = sorted(terms.items(), key=lambda kv: kv[1]["p"])
    out, run = {}, 0.0
    for i, (name, term) in enumerate(ordered):
        run = max(run, min(1.0, (len(ordered) - i) * term["p"]))
        out[name] = run
    return out


WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine")


def word(n):
    """A small count as prose spells one; still generated, not typed."""
    return WORDS[n] if n < len(WORDS) else f"{n:,}".replace(",", "{,}")


def fmt(v):
    if isinstance(v, float):
        return f"{v:.2f}" if abs(v) < 10 else f"{v:.1f}"
    if isinstance(v, int):
        return f"{v:,}".replace(",", "{,}")
    return str(v)


def main():
    outcome = load("appellate_outcome_results.json")
    reasons = load("appeal_reasons_results.json")
    voices = load("appeal_vs_first_results.json")
    select = load("appeal_selection_results.json")
    model = load("reversal_model_1439_1444_results.json")
    full = load("reversal_model_results.json")
    comp = load("corpus_composition_results.json")

    c = outcome["counts"]
    decided = c["affirmed"] + c["reversed"] + c["substituted"] + c["varied"]
    disturbed = c["reversed"] + c["substituted"] + c["varied"]
    w = select["writing"]
    st = select["strata"]
    t = model["terms"]
    h = holm(t)
    pr = select["paired"]

    N = {
        "nJudgments": comp["judgments"],
        "nAppeals": outcome["with_appeal"],
        "nPaired": outcome["paired"],
        "nAppealOnly": outcome["appeal_only"],
        "nAffirmed": c["affirmed"],
        "nAffirmedShare": 100 * c["affirmed"] / outcome["with_appeal"],
        "nReversed": c["reversed"],
        "nSubstituted": c["substituted"],
        "nNotAdmitted": c["not_admitted"],
        "nNotAdmittedShare": 100 * c["not_admitted"] / outcome["with_appeal"],
        "nUnclearOutcome": c["unclear"],
        "nUnclearShare": 100 * c["unclear"] / outcome["with_appeal"],
        "nDecidedOnMerits": decided,
        "nDisturbedShare": 100 * disturbed / decided,

        "nOwnReasons": reasons["with_own_reasons"],
        "nOwnReasonsShare": reasons["share"],
        "nNoReasonsShare": 100 - reasons["share"],
        "nWroteAffirming": 100 * w["affirmed"]["wrote"] /
                           (w["affirmed"]["wrote"] + w["affirmed"]["did_not"]),
        "nWroteReversing": 100 * w["reversed"]["wrote"] /
                           (w["reversed"]["wrote"] + w["reversed"]["did_not"]),

        "nBothReasoned": voices["both_reasoned"],
        "nBothReasonedShare": 100 * voices["both_reasoned"] / voices["paired"],
        "nFirstProcedural": voices["levels"]["first"]["procedural"],
        "nAppealProcedural": voices["levels"]["appeal"]["procedural"],
        "nFirstInstruments": voices["levels"]["first"]["instruments"],
        "nAppealInstruments": voices["levels"]["appeal"]["instruments"],
        "nAffirmedFirstProc": st["affirmed_first"]["procedural"],
        "nAffirmedAppealProc": st["affirmed_appeal"]["procedural"],
        "nDisturbedFirstProc": st["disturbed_first"]["procedural"],
        "nDisturbedAppealProc": st["disturbed_appeal"]["procedural"],

        # a Hijri year is a label, not a quantity: no thousands separator
        "nWindowFrom": str(model["window"][0]),
        "nWindowTo": str(model["window"][1]),
        "nModelN": model["judgments"],
        "nModelBase": 100 * model["base_rate"],
        "nModelFullN": full["judgments"],
        "nModelFullBase": 100 * full["base_rate"],
        "nOrYear": t["year"]["odds_ratio"],
        "nPYear": pv(t["year"]["p"]),
        "nOrDammam": t["dammam"]["odds_ratio"],
        "nPDammam": pv(t["dammam"]["p"]),
        "nOrProcedural": t["procedural_share"]["odds_ratio"],
        "nPProcedural": pv(t["procedural_share"]["p"]),
        "nOrMerits": t["on_merits"]["odds_ratio"],
        "nPMerits": pv(t["on_merits"]["p"]),
        "nOrReasons": t["has_reasons"]["odds_ratio"],
        "nPReasons": pv(t["has_reasons"]["p"]),
        "nOrCitations": t["citations"]["odds_ratio"],
        "nPCitations": pv(t["citations"]["p"]),
        "nVaried": c["varied"],
        "nOtherDisposition": c["other_disposition"],
        "nReversedShare": 100 * c["reversed"] / outcome["with_appeal"],
        "nSubstitutedShare": 100 * c["substituted"] / outcome["with_appeal"],
        "nOtherShare": 100 * c["other_disposition"] / outcome["with_appeal"],
        "nWroteSubstituting": 100 * w["substituted"]["wrote"] /
            (w["substituted"]["wrote"] + w["substituted"]["did_not"]),
        "nWroteNotAdmitting": 100 * w["not_admitted"]["wrote"] /
            (w["not_admitted"]["wrote"] + w["not_admitted"]["did_not"]),

        # the same comparison tested over pairs rather than over citations
        "nPairsTested": pr["all"]["pairs"],
        "nPairsAffirmed": pr["affirmed"]["pairs"],
        "nPairsDisturbed": pr["disturbed"]["pairs"],
        "nDiffAll": pp(pr["all"]["mean_diff"]),
        "nDiffAffirmed": pp(pr["affirmed"]["mean_diff"]),
        "nDiffDisturbed": pp(pr["disturbed"]["mean_diff"]),
        "nPDiffAll": pv(pr["all"]["p"]),
        "nPDiffAffirmed": pv(pr["affirmed"]["p"]),
        "nPDiffDisturbed": pv(pr["disturbed"]["p"]),
    }
    # the remaining model terms, so the table can be typeset in full
    NAMES = {"riyadh": "Riyadh", "jeddah": "Jeddah", "log_length": "Length",
             "instruments": "Instruments", "defence_raised": "Defence",
             "year": "Year", "dammam": "Dammam", "citations": "Citations",
             "procedural_share": "Procedural", "on_merits": "Merits",
             "has_reasons": "Reasons"}
    for term, tag in NAMES.items():
        N[f"nOr{tag}"] = t[term]["odds_ratio"]
        N[f"nP{tag}"] = pv(t[term]["p"])
        N[f"nHolm{tag}"] = pv(h[term])
    # how many of the eleven terms survive correction for testing eleven
    N["nHolmSurvivors"] = word(sum(1 for v in h.values() if v < 0.05))
    lines = ["% Generated by make_numbers.py from the analysis outputs.",
             "% Do not edit: every value here has exactly one source, and it is",
             "% not this file. Regenerated before each build.", ""]
    for k, v in sorted(N.items()):
        lines.append(f"\\newcommand{{\\{k}}}{{{fmt(v)}}}")
    (HERE / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote numbers.tex with {len(N)} values")
    for k, v in sorted(N.items()):
        print(f"  {k:<24}{fmt(v)}")


if __name__ == "__main__":
    main()
