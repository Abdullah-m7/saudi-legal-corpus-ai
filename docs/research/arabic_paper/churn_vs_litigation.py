#!/usr/bin/env python3
"""Does the legislator amend where people litigate?

Paper 4 measured legislative churn — which instruments change, and how often.
This corpus measures which instruments courts apply. Putting them together
asks whether the two follow each other: is the amended part of the statute
book the part that is used, or does the legislature work where nobody sues?

Two tests, at two levels.

INSTRUMENT LEVEL, over the 266 tracks whose registry entry carries a
legal_status breakdown. Churn is the share of an instrument's articles marked
معدلة, مضافة or ملغاة. Citations come from the article-level join.

ARTICLE LEVEL, which is the sharper test and covers the 80 cited instruments
whose verified records are on disk. For each article, is it amended, added or
repealed, and how many times is it cited? If amendment tracked use, an
amended article would be cited more often than an original one in the same
instrument.

Spearman rather than Pearson: citation counts are heavily skewed - one
article carries 14% of everything - and a rank correlation says whether the
ordering agrees without letting that one article set the answer.
"""

import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
ARTICLES = HERE / "applied_articles_results.json"

CHANGED = ("معدلة", "مضافة", "ملغاة")


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    n = len(xs)
    if n < 3:
        return None
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    res = json.load(open(ARTICLES, encoding="utf-8"))
    by_inst = res["by_instrument"]
    cites = {t: sum(v.values()) for t, v in by_inst.items()}

    # ---- instrument level ----
    xs, ys, rows = [], [], []
    for t in tracks:
        rc = t.get("record_counts") or {}
        b = rc.get("legal_status_breakdown")
        total = rc.get("arabic_articles") or rc.get("total")
        if not b or not total:
            continue
        changed = sum(b.get(k, 0) for k in CHANGED)
        churn = changed / total
        c = cites.get(t["track_id"], 0)
        xs.append(churn); ys.append(c)
        rows.append((t["track_id"], churn, c, total))
    rho = spearman(xs, ys)
    cited_n = sum(1 for _, _, c, _ in rows if c)
    print(f"instrument level: {len(rows)} instruments with a churn figure, "
          f"{cited_n} of them cited")
    print(f"  Spearman(churn, citations) = {rho:+.3f}")

    hi = [r for r in rows if r[1] > 0]
    print(f"  instruments with any amended article: {len(hi)}")
    print(f"    of those, never cited: {sum(1 for r in hi if r[2]==0)}")
    zero = [r for r in rows if r[1] == 0]
    print(f"  instruments with no amended article: {len(zero)}, "
          f"never cited: {sum(1 for r in zero if r[2]==0)}")

    # ---- article level ----
    status = {}
    for t in tracks:
        tid = t["track_id"]
        if tid not in by_inst:
            continue
        for p in (t.get("data_paths") or []):
            path = REPO / str(p)
            if not str(p).endswith(".jsonl") or not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                num = r.get("article_number")
                if not isinstance(num, int):
                    continue
                st = r.get("legal_status_ar")
                status[(tid, num)] = st in CHANGED or bool(
                    r.get("is_amended") or r.get("is_added") or r.get("is_repealed"))
            break

    changed_cited = changed_total = orig_cited = orig_total = 0
    cc = oc = 0
    for (tid, num), is_changed in status.items():
        c = by_inst.get(tid, {}).get(str(num), 0)
        if is_changed:
            changed_total += 1; cc += c
            changed_cited += 1 if c else 0
        else:
            orig_total += 1; oc += c
            orig_cited += 1 if c else 0

    print(f"\narticle level: {len(status):,} articles with a status, "
          f"across {len({t for t,_ in status})} instruments")
    if changed_total and orig_total:
        print(f"  amended/added/repealed  {changed_total:>6,} articles, "
              f"{changed_cited/changed_total:>6.1%} ever cited, "
              f"{cc/changed_total:>7.2f} citations each")
        print(f"  original                {orig_total:>6,} articles, "
              f"{orig_cited/orig_total:>6.1%} ever cited, "
              f"{oc/orig_total:>7.2f} citations each")
        ratio = (cc/changed_total)/(oc/orig_total) if oc else None
        if ratio:
            print(f"  an amended article is cited {ratio:.2f}× as often "
                  f"as an original one")

    (HERE / "churn_vs_litigation_results.json").write_text(json.dumps({
        "instrument_level": {"n": len(rows), "spearman": rho,
                             "rows": [{"track": a, "churn": b, "citations": c,
                                       "articles": d} for a, b, c, d in rows]},
        "article_level": {"articles": len(status),
                          "changed": {"n": changed_total, "cited": changed_cited,
                                      "citations": cc},
                          "original": {"n": orig_total, "cited": orig_cited,
                                       "citations": oc}},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote churn_vs_litigation_results.json")


if __name__ == "__main__":
    main()
