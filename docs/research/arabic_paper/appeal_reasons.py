#!/usr/bin/env python3
"""How often does an appeal court write reasons of its own?

Saudi appellate circuits may affirm «محمولاً على أسبابه» — on the reasons
below — and most of them do. That is a fact about the transparency of the
second instance rather than about any single case, and it bounds what can be
studied: a comparison of first-instance and appellate reasoning can only use
the minority of appeals that reasoned at all.

The test is the same structural one used everywhere else in this project:
does the appellate document carry «الأسباب:» followed by «حكمت الدائرة»
within itself. It is not a judgment about quality — a circuit that affirms on
the reasons below has given reasons, by adoption — it is a count of how often
the second instance puts its own reasoning on the record.

Reported by outcome, because whether a circuit writes is not independent of
what it decides.
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import appellate_outcome as AO      # noqa: E402
import voice_attribution as V       # noqa: E402


def main():
    by = collections.Counter()
    own = total = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            s = r.get("sections") or {}
            appeal = s.get("appealTextofRulling")
            if not appeal:
                continue
            total += 1
            text = r["text"]
            lo, hi = V.parts(text, s)[-1]
            rr = V.REASONS.search(text, lo, hi)
            kk = V.RULING.search(text, rr.end() if rr else lo, hi)
            has = bool(rr and kk)
            own += has
            by[(AO.outcome(appeal)[0], has)] += 1

    print(f"{total:,} appellate judgments")
    print(f"  write reasons of their own: {own:,} ({own/total:.1%})")
    print(f"  do not:                     {total-own:,} "
          f"({(total-own)/total:.1%})\n")
    print(f"{'outcome':<20}{'wrote':>8}{'of':>9}{'share':>9}")
    out = {}
    for label in ("affirmed", "reversed", "substituted", "not_admitted",
                  "other_disposition", "unclear"):
        y, n = by[(label, True)], by[(label, False)]
        if y + n == 0:
            continue
        print(f"{label:<20}{y:>8,}{y+n:>9,}{y/(y+n):>8.1%}")
        out[label] = {"wrote": y, "total": y + n}

    (HERE / "appeal_reasons_results.json").write_text(json.dumps({
        "appellate_judgments": total, "with_own_reasons": own,
        "share": 100 * own / total, "by_outcome": out,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote appeal_reasons_results.json")


if __name__ == "__main__":
    main()
