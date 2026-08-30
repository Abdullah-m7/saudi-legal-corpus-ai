#!/usr/bin/env python3
"""MOJ commercial courts against the tax and zakat committees, on the metrics
both bodies actually support.

The temptation is to run the whole map on both and print two columns. That
would be wrong, and the reason is structural rather than statistical: the
committees' decisions arrive as PDF digests with no «الوقائع / الأسباب / حكمت
الدائرة» headings, so `voice_attribution` cannot separate the bench's reasons
from the parties' pleadings in them. Every voice-conditioned figure in the map
— the court/party divergence, the hybrid rate, the silence rate — is therefore
NOT comparable across the two, and none is reported here.

What both support is the mix of authority types across all mentions, and the
concentration of the instruments cited. Those two are reported and nothing
else.

Note what is NOT comparable even among the metrics computed here. A ministry
"document" is one judgment; a committee "document" is a digest carrying
scores of decisions, up to 400,000 characters. So the share of DOCUMENTS
carrying a type is meaningless across the two — a digest of two hundred
decisions contains a maxim somewhere with near-certainty — and it is written
to the JSON flagged, but not printed beside the ministry column.

And a standing caveat on direction: the committees publish «مختزلة», abridged
decisions. If the publisher's abridgement strips the reasoning and keeps the
statutory basis, that alone would produce the difference measured below. This
comparison cannot distinguish an institution that reasons differently from a
publisher that summarises differently. Neither is a claim about the Saudi
judiciary: two publishers, one of them 33 documents wide, cannot carry one.

    python3 institutions.py
"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
sys.path.insert(0, str(HERE.parent / "canon"))
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
from canonical import canonicalise    # noqa: E402
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
GSTC_RAW = HERE.parent / "gstc_pilot" / "raw"
OUT = HERE / "institutions_results.json"
YEARS = set(VIEWS["contemporary_3y"])


def profile(texts, index, order, label):
    types = collections.Counter()
    instruments = collections.Counter()
    docs_with = collections.defaultdict(int)
    quoted = 0
    n = 0
    for text in texts:
        n += 1
        ms = A.mentions(text, {}, index, order)
        seen = set()
        for m in ms:
            if m.get("inQuote"):
                quoted += 1
                continue
            types[m["type"]] += 1
            seen.add(m["type"])
            if m["type"] == "statute" and m["instrument"]:
                instruments[m["instrument"]] += 1
        for t in seen:
            docs_with[t] += 1
    tot = sum(types.values()) or 1
    itot = sum(instruments.values()) or 1
    return {
        "label": label, "documents": n,
        "mentions": sum(types.values()), "quotedHeldApart": quoted,
        "typeShare": {t: round(100 * types[t] / tot, 1) for t in A.TYPES},
        "documentsWith": {t: round(100 * docs_with[t] / n, 1) for t in A.TYPES},
        "instrumentConcentration": {
            f"top{k}": round(100 * sum(v for _, v in instruments.most_common(k))
                             / itot, 1) for k in (1, 3, 5, 10)},
        "distinctInstruments": len(instruments),
        "topInstruments": instruments.most_common(6),
    }


def main():
    index, order = M.build(REGISTRY)

    moj = (rec["text"] for rec in judgments() if year_of(rec) in YEARS)
    a = profile(moj, index, order, "MOJ commercial courts, 1444-1446")

    gstc = []
    for f in sorted(GSTC_RAW.glob("*.txt")):
        raw = f.read_text(encoding="utf-8", errors="replace")
        # the committees' PDFs need the canonical layer; ministry judgments do
        # not. Running the comparison on raw text on both sides would compare
        # a repaired corpus with an unrepaired one.
        gstc.append(canonicalise(raw)["canonical"])
    b = profile(gstc, index, order, "Tax and zakat committees' digests")

    out = {"comparable": ["typeShare", "instrumentConcentration"],
           "notComparableUnitMismatch":
               ["documentsWith: an MOJ document is one judgment, a GSTC"
                " document is a digest of many"],
           "notComparable": ["anything conditioned on voice: the committees'"
                             " digests carry no reasons headings"],
           "moj": a, "gstc": b}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print(f"{a['label']}: {a['documents']:,} documents, "
          f"{a['mentions']:,} mentions")
    print(f"{b['label']}: {b['documents']:,} documents, "
          f"{b['mentions']:,} mentions\n")
    print(f"{'type':<22}{'MOJ share':>12}{'GSTC share':>13}   (share of all"
          f" authority mentions; document rates are not comparable)")
    for t in A.TYPES:
        print(f"  {t:<20}{a['typeShare'][t]:>11.1f}%{b['typeShare'][t]:>12.1f}%")
    print(f"\ninstrument concentration (statute citations)")
    print(f"  MOJ  {a['instrumentConcentration']}  "
          f"{a['distinctInstruments']} instruments")
    print(f"  GSTC {b['instrumentConcentration']}  "
          f"{b['distinctInstruments']} instruments")
    print("\n  MOJ top:", [k for k, _ in a["topInstruments"]])
    print("  GSTC top:", [k for k, _ in b["topInstruments"]])
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
