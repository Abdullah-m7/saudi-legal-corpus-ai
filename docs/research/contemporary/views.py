#!/usr/bin/env python3
"""Research views computed from the mention layer, not from the corpus.

Everything here is a scan of `authority_mentions.jsonl.gz` — 160,157 rows,
2.9 MB — so a new question costs seconds instead of a pass over 44,144
judgments. That is the point of the layer.

    graph      an edge list: who invokes what, and which judgment cites which
               article. Analysable as a table; no graph database.
    core       the operational statutory core, with rank trajectory per year
    hybrid     the shape of hybrid reasoning, per year
    align      how far the bench reasons from the materials the parties raised

    python3 views.py all
"""
import argparse
import collections
import csv
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYER = HERE / "authority_mentions.jsonl.gz"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
VIEWS = {"contemporary_5y": range(1442, 1447),
         "contemporary_3y": range(1444, 1447),
         "post_Evidence": range(1443, 1447),
         "post_CTL": range(1445, 1447)}


def rows(skip_quoted=True):
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r:
                continue
            if skip_quoted and r.get("q"):
                continue
            yield r


def party_side(r, spec):
    if r["role"] == "court_reasoning":
        return "court"
    if spec == "strict":
        return "party" if r["role"] == "party_argument" else None
    return "party" if r["role"] in ("party_argument", "recital") else None


# ------------------------------------------------------------------ graph
def graph(out):
    """Edges, as a CSV anyone can load. Four edge kinds, one file."""
    inv = collections.Counter()      # (role, type)
    cites = collections.Counter()    # (judgment, instrument, article)
    coocc = collections.Counter()    # (typeA, typeB) inside one judgment's reasons
    per_doc = collections.defaultdict(set)
    for r in rows():
        inv[(r["role"], r["t"])] += 1
        if r.get("inst") and r.get("art") is not None:
            cites[(r["j"], r["inst"], r["art"])] += 1
        if r["role"] == "court_reasoning":
            per_doc[r["j"]].add(r["t"])
    for ts in per_doc.values():
        for a in sorted(ts):
            for b in sorted(ts):
                if a < b:
                    coocc[(a, b)] += 1
    p = HERE / "graph_edges.csv.gz"
    with gzip.open(p, "wt", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["edge_kind", "source", "target", "weight"])
        for (role, t), n in sorted(inv.items()):
            w.writerow(["role_invokes_authority", role, t, n])
        for (a, b), n in coocc.most_common():
            w.writerow(["cooccurs_in_court_reasoning", a, b, n])
        for (j, inst, art), n in cites.items():
            w.writerow(["judgment_cites_article", j, f"{inst}:{art}", n])
    print(f"graph: {len(inv)} role-authority edges, {len(coocc)} co-occurrence "
          f"edges, {len(cites):,} judgment-article edges -> {p.name}")
    return {"roleAuthorityEdges": len(inv), "cooccurrenceEdges": len(coocc),
            "judgmentArticleEdges": len(cites),
            "topCooccurrence": [[f"{a}+{b}", n] for (a, b), n
                                in coocc.most_common(10)]}


# ------------------------------------------------------------------- core
def core(out):
    by_year = collections.defaultdict(collections.Counter)
    by_view = collections.defaultdict(collections.Counter)
    for r in rows():
        if r["role"] != "court_reasoning" or r.get("art") is None:
            continue
        key = (r["inst"], r["art"])
        by_year[r["y"]][key] += 1
        for v, yrs in VIEWS.items():
            if r["y"] in yrs:
                by_view[v][key] += 1

    def levels(c):
        tot = sum(c.values()) or 1
        run, out_, need = 0, {}, [50, 75, 90]
        for i, (_, v) in enumerate(c.most_common(), 1):
            run += v
            while need and 100 * run / tot >= need[0]:
                out_[need.pop(0)] = i
        for lv in need:
            out_[lv] = None
        return out_

    ranks = {y: {k: i for i, (k, _) in enumerate(c.most_common(), 1)}
             for y, c in by_year.items()}
    res = {"views": {}, "byYear": {}, "trajectory": []}
    for v, c in by_view.items():
        lv = levels(c)
        tot = sum(c.values()) or 1
        run = 0
        table = []
        for i, (k, n) in enumerate(c.most_common(50), 1):
            run += n
            table.append({"rank": i, "instrument": k[0], "article": k[1],
                          "citations": n, "share": round(100 * n / tot, 2),
                          "cumulative": round(100 * run / tot, 2)})
        res["views"][v] = {"articlesFor50": lv[50], "articlesFor75": lv[75],
                           "articlesFor90": lv[90], "distinct": len(c),
                           "citations": tot, "top50": table}
    for y, c in sorted(by_year.items()):
        lv = levels(c)
        res["byYear"][y] = {"articlesFor50": lv[50], "articlesFor75": lv[75],
                            "articlesFor90": lv[90], "distinct": len(c),
                            "citations": sum(c.values())}
    core3 = by_view["contemporary_3y"]
    for k, _ in core3.most_common(15):
        res["trajectory"].append({
            "article": f"{k[0]}:{k[1]}",
            "rankByYear": {str(y): ranks[y].get(k) for y in sorted(by_year)
                           if by_year[y] and sum(by_year[y].values()) > 2000},
        })
    p = HERE / "core_view.json"
    p.write_text(json.dumps(
        {"_limitation": "This measures ADJUDICATORY VISIBILITY only. It is not"
                        " a measure of legal importance, validity, or"
                        " normative hierarchy. An article that is never cited"
                        " may be so clear that nobody litigates it.",
         **res}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"core: contemporary_3y {res['views']['contemporary_3y']['articlesFor50']}"
          f"/{res['views']['contemporary_3y']['articlesFor75']}"
          f"/{res['views']['contemporary_3y']['articlesFor90']} articles for "
          f"50/75/90% -> {p.name}")
    return res


# ----------------------------------------------------------------- hybrid
def hybrid(out):
    doc = collections.defaultdict(lambda: {"y": None, "court": set(),
                                           "arts": set(), "n": 0})
    for r in rows():
        d = doc[r["j"]]
        d["y"] = r["y"]
        if r["role"] == "court_reasoning":
            d["court"].add(r["t"])
            d["n"] += 1
            if r.get("art") is not None:
                d["arts"].add((r["inst"], r["art"]))
    per_year = collections.defaultdict(collections.Counter)
    combos = collections.defaultdict(collections.Counter)
    arts_by_shape = collections.defaultdict(list)
    for j, d in doc.items():
        if not d["court"]:
            continue
        stat = "statute" in d["court"]
        non = sorted(d["court"] & set(NONSTATUTE))
        shape = ("HYBRID" if stat and non else "STATUTE_ONLY" if stat
                 else "NONSTATUTE_ONLY" if non else "NO_EXPLICIT_AUTHORITY")
        per_year[d["y"]][shape] += 1
        arts_by_shape[shape].append(len(d["arts"]))
        if shape == "HYBRID":
            combos[d["y"]]["+".join(["STATUTE"] + [t.upper() for t in non])] += 1
            combos[d["y"]][f"__families_{len(non)}"] += 1
    res = {"byYear": {}, "combinations": {}, "articlesPerJudgment": {}}
    for y in sorted(per_year):
        tot = sum(per_year[y].values())
        res["byYear"][y] = {"n": tot, **{k: round(100 * v / tot, 1)
                                         for k, v in per_year[y].items()}}
        h = per_year[y]["HYBRID"] or 1
        res["combinations"][y] = {
            k: round(100 * v / h, 1)
            for k, v in combos[y].most_common(12) if not k.startswith("__")}
        res["combinations"][f"{y}_familyCount"] = {
            k.split("_")[-1]: round(100 * v / h, 1)
            for k, v in combos[y].items() if k.startswith("__families_")}
    for shape, ns in arts_by_shape.items():
        ns.sort()
        res["articlesPerJudgment"][shape] = {
            "judgments": len(ns), "median": ns[len(ns) // 2],
            "mean": round(sum(ns) / len(ns), 2)}
    p = HERE / "hybrid_view.json"
    p.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    print(f"hybrid: {len(doc):,} judgments profiled -> {p.name}")
    return res


# ------------------------------------------------------------------ align
def align(out):
    """Does the bench reason from the materials the parties raised?"""
    doc = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows():
        for spec in ("strict", "wide"):
            s = party_side(r, spec)
            if not s:
                continue
            doc[r["j"]][f"{spec}_{s}_t"].add(r["t"])
            if r.get("inst"):
                doc[r["j"]][f"{spec}_{s}_i"].add(r["inst"])
                if r.get("art") is not None:
                    doc[r["j"]][f"{spec}_{s}_a"].add((r["inst"], r["art"]))
    res = {}
    for spec in ("strict", "wide"):
        js = [d for d in doc.values()
              if d[f"{spec}_court_t"] and d[f"{spec}_party_t"]]
        if not js:
            continue
        out_ = {"pairedJudgments": len(js)}
        for lvl, suffix in (("authorityFamily", "t"), ("instrument", "i"),
                            ("article", "a")):
            vals, zero, full = [], 0, 0
            for d in js:
                a, b = d[f"{spec}_court_{suffix}"], d[f"{spec}_party_{suffix}"]
                if not a or not b:
                    continue
                jac = len(a & b) / len(a | b)
                vals.append(jac)
                zero += (not a & b)
                full += (a == b)
            if not vals:
                continue
            vals.sort()
            out_[lvl] = {
                "n": len(vals),
                "medianJaccard": round(vals[len(vals) // 2], 3),
                "meanJaccard": round(sum(vals) / len(vals), 3),
                "shareNoOverlap": round(100 * zero / len(vals), 1),
                "shareIdentical": round(100 * full / len(vals), 1)}
        res[spec] = out_
    p = HERE / "alignment_view.json"
    p.write_text(json.dumps(
        {"_reading": "Jaccard over the SETS a judgment contains, court side"
                     " against party side. It is descriptive: a low overlap"
                     " does not mean the court ignored the party, because a"
                     " court answers a contract argument by applying a"
                     " statute and that is a legitimate answer.",
         **res}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"align: strict {res['strict']['pairedJudgments']:,} paired, "
          f"median family Jaccard "
          f"{res['strict']['authorityFamily']['medianJaccard']} -> {p.name}")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["graph", "core", "hybrid", "align", "all"])
    a = ap.parse_args()
    todo = ["graph", "core", "hybrid", "align"] if a.what == "all" else [a.what]
    for name in todo:
        globals()[name](None)
