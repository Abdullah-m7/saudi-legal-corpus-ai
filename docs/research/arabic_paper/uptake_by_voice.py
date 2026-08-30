#!/usr/bin/env python3
"""What the courts cite, and what the courts *themselves* cite, side by side.

Every headline figure this project has published counts citations anywhere in
a judgment's text. The hand-labelled sets say that on ministry judgments an
unfiltered count over-states the bench's own citations by a factor of 1.24,
so the published figures are not the figures for the court's voice, and the
difference has never been measured on the corpus rather than on a sample.

Three columns, not two, because the segment filter and the sample it can be
applied to are different effects and must not be confused:

  ALL_TEXT             every judgment, every citation. What is published.
  ALL_TEXT_SEGMENTABLE the judgments that carry الوقائع → الأسباب →
                       حكمت الدائرة headings, every citation in them. The
                       like-for-like control: it isolates the selection.
  COURT_REASONING_ONLY the same judgments, citations in the الأسباب segment
                       only. The court's own voice.

ALL_TEXT is reported unchanged next to the new figures and is not replaced.
Anything that moves between column one and column two is selection --- the
judgments that carry headings are not a random half of the corpus. Anything
that moves between column two and column three is voice.

    python3 uptake_by_voice.py [--json]
"""
import argparse, collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))
import arabic_ordinals as A            # noqa: E402
import match_instruments as M          # noqa: E402
import voice_attribution as V          # noqa: E402

CITE = V.CITE
PROCEDURAL = M.PROCEDURAL
COLUMNS = ("ALL_TEXT", "ALL_TEXT_SEGMENTABLE", "COURT_REASONING_ONLY")
NAMED = ("commercial_courts_law", "commercial_courts_implementing_regulation",
         "sharia_procedure_law", "evidence_law", "companies_law",
         "civil_transactions_law", "bankruptcy_law", "arbitration_law")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    index, order = M.build(REGISTRY)
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    size = {}
    for t in tracks:
        rc = t.get("record_counts") or {}
        v = rc.get("arabic_articles") or rc.get("total")
        if isinstance(v, int) and v > 0:
            size[t["track_id"]] = v

    cites = {c: collections.Counter() for c in COLUMNS}          # track -> n
    arts = {c: collections.defaultdict(set) for c in COLUMNS}    # track -> {article}
    judgments = {c: set() for c in COLUMNS}
    n = segmented = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            text = r["text"]
            spans = V.segments(text, r.get("sections"))
            ok = any(v != "unknown" for _, _, v in spans)
            segmented += ok
            last = M.Recent()
            for m in CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                num, _ = A.parse(m.group(1))
                if num is not None and tid in size and num > size[tid]:
                    num = None
                where = ["ALL_TEXT"]
                if ok:
                    where.append("ALL_TEXT_SEGMENTABLE")
                    if V.voice_at(spans, m.start()) == "reasoning":
                        where.append("COURT_REASONING_ONLY")
                for col in where:
                    cites[col][tid] += 1
                    judgments[col].add(r.get("id") or n)
                    if num is not None:
                        arts[col][tid].add(num)

    universe = sum(size.values())
    out = {"judgments": n, "segmentable": segmented, "columns": {}}
    for col in COLUMNS:
        c = cites[col]
        tot = sum(c.values())
        proc = sum(v for k, v in c.items() if k in PROCEDURAL)
        distinct = sum(len(v) for v in arts[col].values())
        covered = sum(size[t] for t in arts[col] if t in size)
        top10 = sum(v for _, v in c.most_common(10))
        out["columns"][col] = {
            "citations": tot,
            "judgmentsWithAtLeastOne": len(judgments[col]),
            "instrumentsCited": len(c),
            "proceduralShare": round(100 * proc / tot, 1) if tot else 0.0,
            "top10Share": round(100 * top10 / tot, 1) if tot else 0.0,
            "distinctArticles": distinct,
            "articleCoverageOfStatuteBook": round(100 * distinct / universe, 2),
            "articleCoverageWithinCitedInstruments":
                round(100 * distinct / covered, 1) if covered else 0.0,
            "byInstrument": {k: c.get(k, 0) for k in NAMED},
            "articlesByInstrument": {k: len(arts[col].get(k, ())) for k in NAMED},
            # the share of each instrument's own articles that this column
            # ever reaches. This is the unit the uptake claim is made in, and
            # it has only ever been published for column one.
            "articleShareByInstrument": {
                k: (round(100 * len(arts[col].get(k, ())) / size[k], 1)
                    if k in size else None) for k in NAMED},
            "articleCountByInstrument": {k: size.get(k) for k in NAMED},
        }

    (HERE / "uptake_by_voice_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    print(f"{n:,} judgments; {segmented:,} carry the headings "
          f"({segmented/n:.1%})\n")
    w = 34
    print(f"{'':{w}}" + "".join(f"{c[:20]:>24}" for c in COLUMNS))
    rows = [("citations", "citations", "{:,}"),
            ("judgments with >=1 citation", "judgmentsWithAtLeastOne", "{:,}"),
            ("instruments ever cited", "instrumentsCited", "{:,}"),
            ("procedural share of citations", "proceduralShare", "{}%"),
            ("top-10 instruments' share", "top10Share", "{}%"),
            ("distinct articles cited", "distinctArticles", "{:,}"),
            ("  as % of the statute book", "articleCoverageOfStatuteBook", "{}%"),
            ("  as % within cited instruments",
             "articleCoverageWithinCitedInstruments", "{}%")]
    for label, key, fmt in rows:
        print(f"{label:{w}}" + "".join(
            f"{fmt.format(out['columns'][c][key]):>24}" for c in COLUMNS))
    print(f"\n{'instrument':{w}}" + "".join(f"{c[:20]:>24}" for c in COLUMNS))
    for k in NAMED:
        print(f"{k:{w}}" + "".join(
            f"{out['columns'][c]['byInstrument'][k]:>16,}"
            f"{out['columns'][c]['articlesByInstrument'][k]:>8}"
            for c in COLUMNS))
    print(f"\n(second number in each cell is distinct articles cited)")
    print(f"\n{'instrument':{w}}{'articles':>10}" +
          "".join(f"{c[:20]:>24}" for c in COLUMNS))
    for k in NAMED:
        n_art = out["columns"]["ALL_TEXT"]["articleCountByInstrument"][k]
        print(f"{k:{w}}{(n_art if n_art else '?'):>10}" + "".join(
            f"{(str(out['columns'][c]['articleShareByInstrument'][k]) + '%'):>24}"
            for c in COLUMNS))
    print("\n(share of the instrument's own articles that the column reaches)")


if __name__ == "__main__":
    main()
