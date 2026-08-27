#!/usr/bin/env python3
"""What the published record is, so the article can say what it is not.

Every result in paper 8 is a statement about the judgments the Ministry
publishes, and the threats-to-validity section can only be as specific as
this measurement. Court, city, year and duplication are counted here rather
than described, and the numbers feed numbers.tex like every other figure.

The appeal flag is audited rather than trusted. `is_appeal` is present and
well-typed on every record and reads false on every record, including the
judgments whose own court field names a court of appeal or the Supreme
Court. A field that never varies is not a field, and the audit below is what
allows the article to say so precisely rather than loosely.

Duplication matters more than it looks. The portal serves some judgments
twice --- the same text under different identifiers --- and a citation
analysis that counts both would report a repeated formula as a trend. Exact
duplicates are counted on the normalised full text.
"""

import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

COMMERCIAL = ("المحكمة التجارية", "محكمة الاستئناف")


def main():
    courts = collections.Counter()
    cities = collections.Counter()
    years = collections.Counter()
    seen = collections.Counter()
    n = 0
    appeal_field = appellate = appellate_flagged_false = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            courts[r.get("court") or "—"] += 1
            cities[r.get("city") or "—"] += 1
            years[(r.get("hijri_date") or "")[:4]] += 1
            if r.get("is_appeal") is not None:
                appeal_field += 1
            court = r.get("court") or ""
            if "استئناف" in court or "العليا" in court:
                appellate += 1
                if r.get("is_appeal") is False:
                    appellate_flagged_false += 1
            body = " ".join((r.get("text") or "").split())
            seen[hashlib.sha1(body.encode("utf-8")).hexdigest()] += 1

    commercial = sum(v for k, v in courts.items()
                     if k.startswith("المحكمة التجارية"))
    labour = sum(v for k, v in courts.items() if "عمالي" in k)
    recent = sum(v for y, v in years.items() if y.isdigit() and int(y) >= 1442)
    dup_groups = sum(1 for v in seen.values() if v > 1)
    dup_extra = sum(v - 1 for v in seen.values() if v > 1)
    ys = sorted(y for y in years if y.isdigit())

    print(f"{n:,} judgments, {len(seen):,} distinct texts")
    print(f"  exact duplicates: {dup_extra:,} extra copies across "
          f"{dup_groups:,} groups ({dup_extra/n:.2%} of the corpus)")
    print(f"  commercial first instance: {commercial:,} ({commercial/n:.1%})")
    print(f"  labour court: {labour:,}")
    print(f"  Hijri 1442 or later: {recent:,} ({recent/n:.1%})")
    print(f"  records carrying an appeal flag: {appeal_field:,}")
    print(f"  issued by an appellate or supreme court: {appellate:,}, "
          f"of which {appellate_flagged_false:,} are flagged is_appeal=false")
    print(f"  Hijri years {ys[0]}–{ys[-1]}\n")
    print("  courts:")
    for k, v in courts.most_common(8):
        print(f"    {v:>7,}  {v/n:>6.1%}  {k}")
    print("  cities:")
    for k, v in cities.most_common(6):
        print(f"    {v:>7,}  {v/n:>6.1%}  {k}")
    print("  years:")
    for y in ys:
        print(f"    {y}  {years[y]:>7,}  {years[y]/n:>6.1%}")

    (HERE / "corpus_composition_results.json").write_text(json.dumps({
        "judgments": n, "distinct_texts": len(seen),
        "duplicate_extra": dup_extra, "duplicate_groups": dup_groups,
        "commercial_first_instance": commercial,
        "labour": labour,
        "recent_1442_plus": recent,
        "appeal_flag_present": appeal_field,
        "appellate_judgments": appellate,
        "appellate_flagged_false": appellate_flagged_false,
        "first_year": ys[0], "last_year": ys[-1],
        "courts": dict(courts.most_common()),
        "cities": dict(cities.most_common(20)),
        "years": {y: years[y] for y in ys},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote corpus_composition_results.json")


if __name__ == "__main__":
    main()
