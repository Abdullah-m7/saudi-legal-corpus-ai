#!/usr/bin/env python3
"""What makes a first-instance judgment likelier to be disturbed on appeal?

The appellate layer gives an outcome for 15,383 judgments. Counting how many
were affirmed is a description; asking what separates those that survived
from those that did not is a question, and the corpus carries enough about
each judgment to ask it: which court wrote it, in which year, how long it is,
how much statute it cites and of what kind, whether it wrote its own reasons,
whether it disposed of the case on the merits or on a preliminary point, and
whether a preliminary defence was raised in it.

Every feature is read from the FIRST-INSTANCE document alone. A model that
peeked at the appellate text would be predicting the outcome from itself.

The target is binary and deliberately narrow: disturbed (reversed, replaced
or varied) against affirmed. Judgments where the appeal did not reach the
merits — inadmissible objections, and dispositions the classifier could not
read — are excluded rather than folded into either side, because «the appeal
was not admitted» says nothing about whether the judgment was sound.

CENSORING, AND WHY THE WINDOW IS AN ARGUMENT
A judgment appears here with an appellate decision only if the appeal was
brought AND decided before the corpus was collected. For the most recent
years that selects the fast appeals, and the disturbed rate collapses
accordingly: 15.7 per cent in 1444, 9.0 in 1445, 0.7 in 1446. Reading a year
coefficient across the whole span therefore measures the collection date as
much as the courts. The model takes --from and --to, and the article reports
the mature window; the full span is kept as the comparison that shows why.

WHY THE ARITHMETIC IS WRITTEN OUT
numpy is installed on this machine and is not used. The replication guide
promises that the analysis runs with no third-party package, and a reviewer
who runs reproduce.sh should not discover otherwise because one script wanted
a matrix inverse. Iteratively reweighted least squares is forty lines, and
the Gauss-Jordan inverse of a twenty-by-twenty matrix is fifteen.
"""

import argparse
import collections
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))

import appellate_outcome as AO      # noqa: E402
import match_instruments as M       # noqa: E402
import voice_attribution as V       # noqa: E402

DISTURBED = {"reversed", "substituted", "varied"}
KEEP = DISTURBED | {"affirmed"}

MERITS = re.compile(r"بإلزام|إلزام\s+المدع|برفض\s+الدعوى|رفض\s+دعوى")
DEFENCE = re.compile(
    r"عدم\s+(?:ال)?اختصاص|عدم\s+قبول\s+الدعوى|سبق\s+الفصل|انتفاء\s+الصفة|"
    r"شرط\s+التحكيم|سقوط\s+الحق|التقادم")
CITIES = ("الرياض", "جدة", "الدمام")


# ---------------------------------------------------------------- the model

def inverse(a):
    """Gauss-Jordan, with partial pivoting."""
    n = len(a)
    m = [row[:] + [1.0 if i == j else 0.0 for j in range(n)]
         for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            raise ValueError("singular design matrix — a feature is collinear")
        m[col], m[piv] = m[piv], m[col]
        d = m[col][col]
        m[col] = [v / d for v in m[col]]
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f:
                m[r] = [v - f * w for v, w in zip(m[r], m[col])]
    return [row[n:] for row in m]


def logit(X, y, tol=1e-8, iters=40):
    """IRLS. Returns (coefficients, standard errors)."""
    n, k = len(X), len(X[0])
    b = [0.0] * k
    for _ in range(iters):
        eta = [sum(bj * xj for bj, xj in zip(b, row)) for row in X]
        mu = [1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, e)))) for e in eta]
        w = [max(m_ * (1 - m_), 1e-9) for m_ in mu]
        # z = eta + (y - mu) / w, weighted least squares on z
        xtwx = [[0.0] * k for _ in range(k)]
        xtwz = [0.0] * k
        for i in range(n):
            zi = eta[i] + (y[i] - mu[i]) / w[i]
            wi, row = w[i], X[i]
            for a in range(k):
                wa = wi * row[a]
                xtwz[a] += wa * zi
                for c in range(a, k):
                    xtwx[a][c] += wa * row[c]
        for a in range(k):
            for c in range(a):
                xtwx[a][c] = xtwx[c][a]
        cov = inverse(xtwx)
        nb = [sum(cov[a][c] * xtwz[c] for c in range(k)) for a in range(k)]
        shift = max(abs(x - y_) for x, y_ in zip(nb, b))
        b = nb
        if shift < tol:
            break
    se = [math.sqrt(cov[a][a]) for a in range(k)]
    return b, se


def pvalue(z):
    return math.erfc(abs(z) / math.sqrt(2))


# ------------------------------------------------------------- the features

def features(r, index, order):
    """What the first-instance judgment looks like, before anyone appealed."""
    s = r.get("sections") or {}
    text = r["text"]
    spans = V.parts(text, s)
    a, b = spans[0]
    body = text[a:b]
    if len(body) < 200:
        return None

    reasons = V.REASONS.search(body) and V.RULING.search(body)
    cites, proc, insts = 0, 0, set()
    last = M.Recent()
    for m in V.CITE.finditer(body):
        tid, kind = M.match(m.group(2), index, order, last)
        if kind == "named":
            last.note(tid)
        if not tid:
            continue
        cites += 1
        insts.add(tid)
        proc += tid in M.PROCEDURAL

    op = None
    stripped, back = AO.bare_with_map(body)
    k = re.search(r"حكمت\s+(?:الدائرة|دائرة)", stripped)
    if k:
        op = body[back[k.start()]:back[k.start()] + 800]

    year = int((r.get("hijri_date") or "0000")[:4] or 0)
    city = r.get("city") or ""
    return {
        "disturbed": None,
        "year": year,
        "riyadh": 1.0 if city == "الرياض" else 0.0,
        "jeddah": 1.0 if city == "جدة" else 0.0,
        "dammam": 1.0 if city == "الدمام" else 0.0,
        "log_length": math.log(len(body)),
        "citations": cites,
        "instruments": len(insts),
        "procedural_share": proc / cites if cites else 0.0,
        "has_reasons": 1.0 if reasons else 0.0,
        "on_merits": 1.0 if (op and MERITS.search(op)) else 0.0,
        "defence_raised": 1.0 if DEFENCE.search(body[:len(body) // 2]) else 0.0,
    }


TERMS = ["year", "riyadh", "jeddah", "dammam", "log_length", "citations",
         "instruments", "procedural_share", "has_reasons", "on_merits",
         "defence_raised"]
LABEL = {
    "year": "السنة الهجرية (لكل سنة)",
    "riyadh": "الرياض", "jeddah": "جدة", "dammam": "الدمام",
    "log_length": "طول الحكم (لوغاريتم)",
    "citations": "عدد الاستشهادات",
    "instruments": "عدد الأنظمة المستشهد بها",
    "procedural_share": "حصة الإجرائي من استشهاداته",
    "has_reasons": "كتب أسبابه بعناوينها",
    "on_merits": "فصل في الموضوع لا في شكليّ",
    "defence_raised": "أُثير فيه دفع شكلي",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=9999)
    args = ap.parse_args()
    index, order = M.build(REGISTRY)
    rows = []
    outcomes = collections.Counter()
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            appeal = (r.get("sections") or {}).get("appealTextofRulling")
            if not appeal:
                continue
            label = AO.outcome(appeal)[0]
            outcomes[label] += 1
            if label not in KEEP:
                continue
            f = features(r, index, order)
            if not f or not (args.lo <= f["year"] <= args.hi):
                continue
            f["disturbed"] = 1.0 if label in DISTURBED else 0.0
            rows.append(f)

    n = len(rows)
    base = sum(r["disturbed"] for r in rows) / n
    y0 = min(r["year"] for r in rows if r["year"] > 1400)
    window = ("" if args.lo == 0 and args.hi == 9999
              else f", within {args.lo}--{args.hi}")
    print(f"{sum(outcomes.values()):,} judgments carry an appellate decision; "
          f"{n:,} of them were affirmed or disturbed on the merits"
          f"{window} and enter the model")
    print(f"  disturbed: {base:.1%} — the rate any model has to beat\n")

    X, y = [], []
    for r in rows:
        X.append([1.0] + [(r["year"] - y0) if t == "year" else r[t]
                          for t in TERMS])
        y.append(r["disturbed"])
    b, se = logit(X, y)

    print(f"{'term':<34}{'odds ratio':>12}{'z':>9}{'p':>9}")
    print(f"{'(intercept)':<34}{math.exp(b[0]):>12.2f}"
          f"{b[0]/se[0]:>9.2f}{pvalue(b[0]/se[0]):>9.3f}")
    out = {}
    for i, t in enumerate(TERMS, start=1):
        z = b[i] / se[i]
        print(f"{LABEL[t]:<34}{math.exp(b[i]):>12.2f}{z:>9.2f}"
              f"{pvalue(z):>9.3f}")
        out[t] = {"coef": b[i], "se": se[i], "odds_ratio": math.exp(b[i]),
                  "z": z, "p": pvalue(z)}

    name = ("reversal_model_results.json" if args.hi == 9999
            else f"reversal_model_{args.lo}_{args.hi}_results.json")
    (HERE / name).write_text(json.dumps({
        "window": [args.lo, args.hi],
        "judgments": n, "base_rate": base, "year_zero": y0,
        "outcomes": dict(outcomes), "terms": out,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {name}")


if __name__ == "__main__":
    main()
