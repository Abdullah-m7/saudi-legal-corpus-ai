#!/usr/bin/env python3
"""Point the project's extractors at another institution, unchanged.

The applied-law paper's pipeline was built and validated on one publisher's
text: the Ministry of Justice gateway, which returns clean API strings from
courts that share a drafting house style. The strongest lesson in this
project came when that pipeline was pointed at a document written by a
practising lawyer and silently dropped two citations in four.

This is the same test at institutional scale. Nothing is adapted first: the
citation pattern, the Arabic ordinal parser and the instrument matcher run on
the tax and customs committees' digests exactly as they run on judgments, and
what breaks is the measurement.

    python3 transport.py   ->  transport_results.json
"""

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
sys.path.insert(0, str(HERE))
import arabic_ordinals as A          # noqa: E402
import match_instruments as M        # noqa: E402
import voice_attribution as V        # noqa: E402
from privacy_scan import normalise   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
RAW = HERE / "raw"
OUT = HERE / "transport_results.json"


def main():
    index, order = M.build(REGISTRY)
    texts = sorted(RAW.glob("*.txt"))
    if not texts:
        sys.exit("no pilot text: run collect.py --pilot first")

    per_file, agg = [], collections.Counter()
    unmatched_names = collections.Counter()
    unparsed_articles = collections.Counter()
    matched_instruments = collections.Counter()

    for path in texts:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        # The only concession made here, and it is a reading concession not a
        # tuning one: bidi controls are stripped and digits normalised, exactly
        # as privacy_scan does, because otherwise no pattern can span a number
        # and the words around it. Everything downstream is unchanged.
        clean, bidi = normalise(raw)
        found = V.CITE.findall(clean)
        last = M.Recent()
        matched = parsed = 0
        for art, name in found:
            tid, kind = M.match(name, index, order, last)
            if tid:
                matched += 1
                matched_instruments[tid] += 1
                if kind == "named":
                    last.note(tid)
            else:
                unmatched_names[" ".join(name.split())[:60]] += 1
            n, _ = A.parse(art)
            if n is None:
                unparsed_articles[" ".join(art.split())[:40]] += 1
            else:
                parsed += 1
        # A crude but honest floor on how many citations the pattern never
        # reached: occurrences of the word for «article» at all.
        article_word = len(re.findall(r"(?:لل|بال|ال)?مادة", clean))
        per_file.append({
            "file": path.name,
            "characters": len(raw),
            "bidiControlsStripped": bidi,
            "occurrencesOfArticleWord": article_word,
            "citationsDetected": len(found),
            "detectionRate": round(len(found) / article_word, 3)
            if article_word else None,
            "instrumentMatched": matched,
            "instrumentMatchRate": round(matched / len(found), 3) if found else None,
            "articleNumberParsed": parsed,
            "articleParseRate": round(parsed / len(found), 3) if found else None,
        })
        agg["articleWord"] += article_word
        agg["detected"] += len(found)
        agg["matched"] += matched
        agg["parsed"] += parsed

    out = {
        "population": "quasi-judicial committee digests (GSTC), not courts",
        "toolsUnchanged": ["voice_attribution.CITE", "arabic_ordinals.parse",
                           "match_instruments.match"],
        "concession": ("bidi controls stripped and digits normalised before "
                       "reading; no pattern, parser or matcher was altered"),
        "files": per_file,
        "totals": {
            "occurrencesOfArticleWord": agg["articleWord"],
            "citationsDetected": agg["detected"],
            "detectionRate": round(agg["detected"] / agg["articleWord"], 3)
            if agg["articleWord"] else None,
            "instrumentMatched": agg["matched"],
            "instrumentMatchRate": round(agg["matched"] / agg["detected"], 3)
            if agg["detected"] else None,
            "articleNumberParsed": agg["parsed"],
            "articleParseRate": round(agg["parsed"] / agg["detected"], 3)
            if agg["detected"] else None,
        },
        "topUnmatchedInstrumentNames": unmatched_names.most_common(15),
        "topUnparsedArticleExpressions": unparsed_articles.most_common(15),
        "topMatchedInstruments": matched_instruments.most_common(10),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    t = out["totals"]
    print(f"{'file':<14}{'chars':>10}{'«مادة»':>9}{'found':>8}{'det%':>7}"
          f"{'match%':>8}{'parse%':>8}")
    for f in per_file:
        print(f"{f['file']:<14}{f['characters']:>10}{f['occurrencesOfArticleWord']:>9}"
              f"{f['citationsDetected']:>8}"
              f"{(f['detectionRate'] or 0)*100:>6.1f}"
              f"{(f['instrumentMatchRate'] or 0)*100:>8.1f}"
              f"{(f['articleParseRate'] or 0)*100:>8.1f}")
    print(f"\nTOTAL  «مادة» {t['occurrencesOfArticleWord']:,} · detected "
          f"{t['citationsDetected']:,} ({t['detectionRate']:.1%}) · instrument "
          f"matched {t['instrumentMatchRate']:.1%} · article parsed "
          f"{t['articleParseRate']:.1%}")
    print("\ntop unmatched instrument names:")
    for n, c in out["topUnmatchedInstrumentNames"][:8]:
        print(f"   {c:>5}  {n}")
    print("\ntop unparsed article expressions:")
    for n, c in out["topUnparsedArticleExpressions"][:8]:
        print(f"   {c:>5}  {n!r}")


if __name__ == "__main__":
    main()
