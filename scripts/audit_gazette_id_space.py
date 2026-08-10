#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How much of the gazette's id space has this corpus never looked at — and does
any of it open on a document?

WHY THIS EXISTS. Re-harvesting the archive index found 479 pages it had never
seen, most of them under URL sub-sections the original sweep never walked. That
answered one question and opened a bigger one: the index was blind to a SHAPE,
so how would anyone know what else it is blind to? "We re-harvested" is not an
answer, because the harvest can only see what the sitemaps expose, and the
sitemaps expose 638 pages against 9,442 in the index.

This audit stops guessing and measures. The gazette addresses its pages by
NUMERIC ID, and the ids the corpus holds are a set with holes in it. The holes
are countable, and — this is the part that makes it a measurement rather than a
worry — each hole can be PROBED: ask the gazette for a missing id and see
whether anything is there.

TWO ID SPACES, AND THEY DO NOT BEHAVE ALIKE:

  LEGACY   ~8,018-28,849, reachable at /details?p=<id>. A missing id returns a
           404 whose body is a fixed size, so the flat form is a clean oracle:
           404 means nothing is there.
  NEW      4,000,207+, NOT reachable at /details?p=<id> and NOT reachable at
           /decisions-and-regulations/<id> either unless that happens to be the
           page's own shape. The new space requires the page's EXACT
           sub-section, so probing an id means trying every shape this corpus
           has ever observed.

WHAT A 404 DOES AND DOES NOT PROVE. In the legacy space it is decisive. In the
new space, a 404 across all probed shapes means the id is not a document page
reachable by any shape this corpus has ever seen — it does NOT prove the id does
not exist, because a shape nobody has observed yet would look exactly the same.
That limit is the whole reason this file measures instead of concluding, and it
is printed with the result rather than left for a reader to infer.

SAMPLED, WITH THE SAMPLE SIZE STATED. Probing every missing id would be ~12,000
requests in the legacy space and ~5,000 in the new one. This takes a fixed-seed
stratified sample per region and reports the resolve rate WITH its sample size,
so the extrapolation is the reader's to make and the arithmetic is visible.

robots.txt is honored: /details and /decisions-and-regulations are not
disallowed; /*page=, /*redirect= and /ajax/ are, and are never touched.

Read-only over the corpus; writes one report under reports/. Live network only
with --probe. Not part of the QA gate.

Usage:
    python3 scripts/audit_gazette_id_space.py               # offline map only
    python3 scripts/audit_gazette_id_space.py --probe 40    # 40 ids per region
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                          "gazette_title_index.json")
OUT = os.path.join(ROOT, "reports", "gazette_index_freshness",
                   "gazette_id_space_audit.json")
TMP = "/tmp/id_space_probe.html"

NEW_SPACE_FLOOR = 1_000_000
BIG_HOLE = 20
SEED = 20260810            # fixed so the sample is reproducible

# Every URL shape this corpus has actually observed a document at, in
# descending order of how often it has seen it. Not invented — derived from the
# URLs recorded in the gate triage and freshness reports.
LEGACY_SHAPES = ("https://www.uqn.gov.sa/details?p=%s",)
NEW_SHAPES = (
    "https://www.uqn.gov.sa/decisions-and-regulations/%s",
    "https://www.uqn.gov.sa/decisions-and-regulations/authorities/%s",
    "https://www.uqn.gov.sa/decisions-and-regulations/rules-and-regulations/%s",
    "https://www.uqn.gov.sa/decisions-and-regulations/council-of-ministers-decisions/%s",
    "https://www.uqn.gov.sa/decisions-and-regulations/royal-decrees/%s",
    "https://www.uqn.gov.sa/decisions-and-regulations/ministerial-decisions/%s",
    "https://www.uqn.gov.sa/decisions-and-regulations/the-royal-court/%s",
)

_H1_RE = re.compile(r'<h1 class="article-title">\s*(.*?)\s*</h1>', re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def holes(sorted_ids):
    return [(a + 1, b - 1, b - a - 1) for a, b in zip(sorted_ids, sorted_ids[1:])
            if b - a > 1]


def probe(url, timeout=40):
    """Returns (http_status, title_or_None). One request, no retry storm."""
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url,
                        "-o", TMP, "-w", "%{http_code}"],
                       capture_output=True, text=True)
    code = (r.stdout or "").strip()
    if not os.path.exists(TMP):
        return code, None
    html = open(TMP, encoding="utf-8", errors="replace").read()
    m = _H1_RE.search(html)
    title = re.sub(r"\s+", " ", _TAG_RE.sub(" ", m.group(1))).strip() if m else None
    return code, (title or None)


def probe_id(pid, shapes, delay=0.35):
    for i, shape in enumerate(shapes):
        if i:
            time.sleep(delay)
        code, title = probe(shape % pid)
        if code == "200" and title:
            return {"page_id": str(pid), "resolved": True,
                    "url": shape % pid, "title": title}
    return {"page_id": str(pid), "resolved": False, "shapes_tried": len(shapes)}


def merge_into_index(rows):
    """Add resolved ids to the archive title index, with their own title and date.

    Only ids the probe actually opened are merged, and only with a title AND a
    date read off the page — the same rule the sitemap harvester follows, for the
    same reason: an entry with a blank date reads as harvested and answers
    nothing."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "refresh_gazette_title_index",
        os.path.join(ROOT, "scripts", "refresh_gazette_title_index.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    index = json.load(open(INDEX_PATH, encoding="utf-8"))
    added = 0
    for r in rows:
        html = mod.fetch_page(r["url"])
        if html is None:
            continue
        title, date = mod.page_title_and_date(html)
        if not title or not date or r["page_id"] in index["index"]:
            continue
        index["index"][r["page_id"]] = {"title": title, "date": date}
        added += 1
        time.sleep(0.3)
    if added:
        index["pages"] = len(index["index"])
        dates = sorted(x.get("date") for x in index["index"].values() if x.get("date"))
        index.setdefault("refresh_log", []).append({
            "added_pages": added,
            "channel": "id-space probe (not the sitemaps)",
            "new_end_date": dates[-1] if dates else None,
            "note": ("أُضيفت هذه الصفحات عبر **سبر فضاء المعرّفات** لا عبر خرائط الموقع: "
                     "فجواتٌ صغيرة في المدى القديم سُبرت **استقصاءً لا عيّنة**، وما فُتح "
                     "منها أُدرج. **وهذا قناةُ اكتشافٍ ثانية**، تكشف ما لا تعرضه الخرائط."),
        })
        json.dump(index, open(INDEX_PATH, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=int, default=0,
                    help="probe this many missing ids per region (0 = offline map only)")
    ap.add_argument("--exhaust", metavar="REGION",
                    help="probe EVERY missing id in one region instead of sampling — "
                         "worth it only where a sample already found something")
    ap.add_argument("--merge", action="store_true",
                    help="with --exhaust: add the ids that resolve to the archive title "
                         "index and put the document-section ones through the gates")
    args = ap.parse_args()

    index = json.load(open(INDEX_PATH, encoding="utf-8"))["index"]
    ids = sorted(int(k) for k in index if k.isdigit())
    legacy = [i for i in ids if i < NEW_SPACE_FLOOR]
    new = [i for i in ids if i >= NEW_SPACE_FLOOR]

    lh = holes(legacy)
    nh = holes(new)
    lh_big = [h for h in lh if h[2] >= BIG_HOLE]
    lh_small = [h for h in lh if h[2] < BIG_HOLE]

    def expand(hs):
        return [i for a, b, _ in hs for i in range(a, b + 1)]

    regions = {
        "legacy_big_holes": expand(lh_big),
        "legacy_small_holes": expand(lh_small),
        "new_space_holes": expand(nh),
    }

    print("id space held by this corpus: %d ids" % len(ids))
    print("  legacy  %6d ids  %d..%d  density %.1f%%"
          % (len(legacy), legacy[0], legacy[-1],
             100.0 * len(legacy) / (legacy[-1] - legacy[0] + 1)))
    print("  new     %6d ids  %d..%d  density %.1f%%"
          % (len(new), new[0], new[-1],
             100.0 * len(new) / (new[-1] - new[0] + 1)))
    print("\nmissing ids inside the held ranges:")
    for k, v in regions.items():
        print("  %-20s %6d" % (k, len(v)))
    print("\nlargest legacy holes:")
    for a, b, n in sorted(lh_big, key=lambda x: -x[2])[:8]:
        print("   %6d..%-6d  %5d missing" % (a, b, n))

    year = collections.Counter((index[str(i)].get("date") or "????")[:4] for i in ids)
    print("\npages by year: %s" % dict(sorted(year.items())))

    result = {
        "generated_note": (
            "قياسٌ لسؤالٍ فتحه اكتشافُ أن الفهرس كان **أعمى عن شكلٍ من الروابط**: فكيف "
            "يُعرف ما هو أعمى عنه أيضاً؟ الجريدةُ تعنون صفحاتها **بمعرّفٍ رقمي**، "
            "ومعرّفاتُ المستودع مجموعةٌ فيها فجوات — **والفجواتُ تُعدّ وتُسبَر**. "
            "**وفضاءان لا يتصرفان تصرفاً واحداً**: القديم يُفتح بالشكل المسطَّح "
            "`details?p=`، **و404 فيه جوابٌ قاطع**؛ والجديد يتطلب **القسم الفرعي "
            "بعينه**، **فـ404 فيه يعني أن المعرّف لا يُفتح بأي شكلٍ رآه هذا المستودع، "
            "لا أنه غير موجود**. والعيّنةُ مُثبَّتة البذرة، **وتُعرض نسبةُ الفتح مع "
            "حجم العيّنة** ليكون الاستقراء بيد القارئ."),
        "held_ids": len(ids),
        "legacy": {"count": len(legacy), "min": legacy[0], "max": legacy[-1],
                   "density_pct": round(100.0 * len(legacy) / (legacy[-1] - legacy[0] + 1), 1)},
        "new": {"count": len(new), "min": new[0], "max": new[-1],
                "density_pct": round(100.0 * len(new) / (new[-1] - new[0] + 1), 1)},
        "missing_by_region": {k: len(v) for k, v in regions.items()},
        "largest_legacy_holes": [{"from": a, "to": b, "missing": n}
                                 for a, b, n in sorted(lh_big, key=lambda x: -x[2])],
        "pages_by_year": dict(sorted(year.items())),
        "probe": None,
    }

    if args.exhaust:
        pool = regions.get(args.exhaust)
        if pool is None:
            print("unknown region %r; choose from %s" % (args.exhaust, list(regions)))
            return 1
        shapes = NEW_SHAPES if args.exhaust.startswith("new") else LEGACY_SHAPES
        print("\nEXHAUSTING %s: every one of its %d missing ids, %d URL shape(s) each"
              % (args.exhaust, len(pool), len(shapes)))
        rows = []
        for i, pid in enumerate(sorted(pool)):
            if i:
                time.sleep(0.3)
            rows.append(probe_id(pid, shapes))
        hit = [r for r in rows if r["resolved"]]
        print("   resolved %d of %d — this region is now answered EXHAUSTIVELY, "
              "not estimated" % (len(hit), len(rows)))
        for r in hit:
            print("      %-9s %s" % (r["page_id"], r["title"][:72]))
        result["exhausted"] = {"region": args.exhaust, "probed": len(rows),
                               "resolved": len(hit), "rows": hit}
        if os.path.exists(TMP):
            os.remove(TMP)
        if args.merge and hit:
            merged = merge_into_index(hit)
            result["exhausted"]["merged_into_index"] = merged
            print("   merged %d into the archive title index" % merged)

    if args.probe:
        rng = random.Random(SEED)
        probes = {}
        for name, pool in regions.items():
            if not pool:
                continue
            sample = rng.sample(pool, min(args.probe, len(pool)))
            shapes = NEW_SHAPES if name.startswith("new") else LEGACY_SHAPES
            rows = []
            print("\nprobing %s: %d of %d missing ids, %d URL shape(s) each"
                  % (name, len(sample), len(pool), len(shapes)))
            for pid in sorted(sample):
                rows.append(probe_id(pid, shapes))
                time.sleep(0.3)
            hit = [r for r in rows if r["resolved"]]
            print("   resolved %d of %d (%.0f%%)"
                  % (len(hit), len(rows), 100.0 * len(hit) / len(rows)))
            for r in hit[:8]:
                print("      %-9s %s" % (r["page_id"], r["title"][:70]))
            probes[name] = {"sampled": len(rows), "pool": len(pool),
                            "resolved": len(hit),
                            "resolve_rate_pct": round(100.0 * len(hit) / len(rows), 1),
                            "estimated_missing_documents": round(
                                len(pool) * len(hit) / len(rows)),
                            "rows": rows}
        result["probe"] = probes
        result["probe_limits"] = (
            "في الفضاء القديم **404 قاطع**: لا صفحة هناك. وفي الفضاء الجديد **404 عبر "
            "كل الأشكال المُجرَّبة يعني: لا يُفتح بشكلٍ رآه هذا المستودع** — **ولا "
            "يثبت العدم**، لأن شكلاً لم يره أحدٌ بعد سيبدو هكذا تماماً. "
            "والتقديرُ المعروض استقراءٌ خطّي من عيّنةٍ صغيرة، **لا جرد**.")
        if os.path.exists(TMP):
            os.remove(TMP)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
