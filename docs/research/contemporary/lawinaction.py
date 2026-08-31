#!/usr/bin/env python3
"""What distinguishes enacted law from law that becomes operational?

`core_view.json` says seven articles carry half of what the bench cites. The
obvious next question is not "how many articles are cited" -- that is already
measured -- but *which kind* of article becomes repeatedly operational.

This joins the enacted statute book, article by article from the registry,
against the articles the bench actually cites, and profiles the two groups on
features that exist in the data rather than features that would be convenient:

    length          characters of the article's own Arabic text
    position        where it sits in its instrument, as a percentile
    legal status    original / amended / repealed, as the registry records it
    grants          whether the article's text contains the vocabulary of
                    jurisdiction, of time limits, or of proof -- three
                    families this corpus has already shown to dominate

DESCRIPTIVE ONLY, and deliberately no model. An article that is never cited
is not thereby inoperative: it may be so clear that nobody litigates it, or
govern transactions that never reach a commercial court. This measures
adjudicatory visibility.

    python3 lawinaction.py
"""
import collections
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGISTRY = ROOT / "data" / "corpus_registry" / "corpus_registry.json"
LAYER = HERE / "authority_mentions.jsonl.gz"
OUT = HERE / "lawinaction_results.json"

# the instruments that carry the operational core; profiling the whole
# 291-track registry would mix statute books that no commercial court can ever
# apply into the denominator, which would inflate the gap for free.
FOCUS = ["commercial_courts_law", "commercial_courts_implementing_regulation",
         "evidence_law", "sharia_procedure_law", "civil_transactions_law",
         "companies_law", "arbitration_law", "bankruptcy_law"]

JURISDICTION = re.compile(r"تختص|الاختصاص|ولاية")
TIMELIMIT = re.compile(r"خلال\s+\(?\s*[\d٠-٩]|مدة\s+لا\s+تزيد|ميعاد|مهلة")
PROOF = re.compile(r"البينة|الإثبات|المحرر|حجة|القرينة|اليمين")
DUTY = re.compile(r"يجب|يلتزم|على\s+المحكمة|لا\s+يجوز")


def enacted():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    out = {}
    for t in tracks:
        tid = t.get("track_id")
        if tid not in FOCUS:
            continue
        layer = (t.get("language_layers") or {}).get("arabic") or {}
        path = ROOT / (layer.get("data_path") or "")
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        arts = {}
        for r in doc.get("records", []):
            n = r.get("article_number")
            if not isinstance(n, int):
                continue
            txt = r.get("article_text_ar") or ""
            arts[n] = {
                "len": len(txt),
                "repealed": bool(r.get("is_repealed")),
                "amended": bool(r.get("is_amended")),
                "added": bool(r.get("is_added")),
                "jurisdiction": bool(JURISDICTION.search(txt)),
                "timeLimit": bool(TIMELIMIT.search(txt)),
                "proof": bool(PROOF.search(txt)),
                "duty": bool(DUTY.search(txt)),
            }
        if arts:
            out[tid] = arts
    return out


def cited():
    c = collections.Counter()
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            if r["role"] == "court_reasoning" and r.get("art") is not None:
                c[(r["inst"], r["art"])] += 1
    return c


def profile(rows):
    if not rows:
        return {}
    lens = sorted(r["len"] for r in rows)
    n = len(rows)
    return {
        "articles": n,
        "medianLength": lens[n // 2],
        "repealed": round(100 * sum(r["repealed"] for r in rows) / n, 1),
        "amended": round(100 * sum(r["amended"] for r in rows) / n, 1),
        "jurisdiction": round(100 * sum(r["jurisdiction"] for r in rows) / n, 1),
        "timeLimit": round(100 * sum(r["timeLimit"] for r in rows) / n, 1),
        "proof": round(100 * sum(r["proof"] for r in rows) / n, 1),
        "duty": round(100 * sum(r["duty"] for r in rows) / n, 1),
        "positionPct": round(100 * sum(r["pos"] for r in rows) / n, 1),
    }


def main():
    book = enacted()
    hits = cited()
    per_inst = {}
    groups = {"core": [], "cited": [], "uncited": []}
    core_keys = {k for k, _ in hits.most_common(40)}
    for tid, arts in book.items():
        m = max(arts) or 1
        c = u = 0
        for num, a in arts.items():
            a["pos"] = num / m
            n = hits.get((tid, num), 0)
            if n:
                c += 1
                groups["cited"].append(a)
                if (tid, num) in core_keys:
                    groups["core"].append(a)
            else:
                u += 1
                groups["uncited"].append(a)
        per_inst[tid] = {"enacted": len(arts), "cited": c,
                         "share": round(100 * c / len(arts), 1),
                         "citations": sum(v for (t2, _), v in hits.items()
                                          if t2 == tid)}
    res = {"_limitation": "Adjudicatory visibility only. An uncited article is"
                          " not an inoperative one.",
           "instruments": per_inst,
           "profile": {k: profile(v) for k, v in groups.items()}}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print(f"{'instrument':<44}{'enacted':>9}{'cited':>7}{'%':>7}{'citations':>11}")
    for tid, d in sorted(per_inst.items(), key=lambda kv: -kv[1]["citations"]):
        print(f"  {tid:<42}{d['enacted']:>9}{d['cited']:>7}{d['share']:>7.1f}"
              f"{d['citations']:>11,}")
    tot_e = sum(d["enacted"] for d in per_inst.values())
    tot_c = sum(d["cited"] for d in per_inst.values())
    print(f"  {'TOTAL':<42}{tot_e:>9}{tot_c:>7}{100*tot_c/tot_e:>7.1f}\n")
    print(f"{'feature':<20}{'core 40':>10}{'cited':>10}{'uncited':>10}")
    p = res["profile"]
    for f in ("articles", "medianLength", "positionPct", "repealed",
              "amended", "jurisdiction", "timeLimit", "proof", "duty"):
        print(f"  {f:<18}{p['core'].get(f, 0):>10}{p['cited'].get(f, 0):>10}"
              f"{p['uncited'].get(f, 0):>10}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
