#!/usr/bin/env python3
"""Collect Saudi judgments from the Ministry of Justice legal portal.

The portal at laws.moj.gov.sa renders nothing in its page source: it is a
Nuxt application that fetches everything from a public gateway. Reading the
app's own lazy-loaded chunks gives the three endpoints it calls. The one that
mattered was invisible to every guess because the ministry spells it the
British way:

    POST /Judgements/judgements-list      search and page
    GET  /Judgements/get-details?id=      one judgment, in full
    POST /Judgements/add-share-info       not used here

Base: https://laws-gateway.moj.gov.sa/apis/legislations/v1
No authentication. 50,634 judgments as of 25 August 2026.

The search body the portal sends:

    {pageNumber, pageSize, judgmentNo, decisionNo, cityId, courtTypes,
     courtId, term, dateFrom, dateTo, sortingBy}

`term` is free text over the judgment body, which is what makes this usable
for the definitional question: it finds the word inside the reasoning, not
just in a title.

ON COLLECTING THIS AT ALL
-------------------------
robots.txt says `Allow: /` and lists sitemap-judicial-decisions.xml, so the
ministry publishes these pages for indexing. Its own client throttles itself
to one request per second; that is the publisher's declared pace and this
script keeps to it rather than inventing a faster one. Every response is
cached, so re-running costs nothing and a resumed run re-fetches nothing.

Usage
    python3 collect_judgments.py --term المنشأة --max 40
    python3 collect_judgments.py --term المنشأة --count-only
"""

import argparse
import html
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "judgments_cache"
BASE = "https://laws-gateway.moj.gov.sa/apis/legislations/v1"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
DELAY = 1.0  # the portal's own client-side limit

def occurrences(text, term):
    """Count the term the way the ministry's search finds it.

    A plain substring count is wrong here. The portal matches morphologically:
    it returns a judgment for المستهلك whose body only ever says للمستهلك and
    مستهلك. Counting the literal string gives zero on a judgment where the
    word appears six times, and anyone filtering on a positive count would
    discard exactly the judgments the search was right to return.

    So the count strips the definite article to a stem and allows the ordinary
    Arabic proclitics in front of it: the article, و ف ب ك ل and their pairs.
    It will still miss a broken-plural form such as منشآت, which shares no
    surface with منشأة; that is a floor on the count, not a ceiling.
    """
    stem = re.sub(r"^ال", "", term)
    pattern = re.compile(r"[وف]?[بكل]?(?:ال)?" + re.escape(stem))
    return len(pattern.findall(text))


TEXT_FIELDS = ("judgmentFacts", "judgmentReasons", "judgmentRuling",
               "judgmentTextofRulling", "appealFacts", "appealReasons",
               "appealRuling", "appealTextofRulling")


def request(method, path, body=None):
    cmd = ["curl", "-sS", "-A", UA, "--max-time", "90",
           "-H", "Accept: application/json"]
    if method == "POST":
        cmd += ["-H", "Content-Type: application/json",
                "-X", "POST", "-d", json.dumps(body, ensure_ascii=False)]
    cmd.append(BASE + path)
    out = subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(DELAY)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        # The gateway answers unknown routes with a plain-text error block.
        return None


def search(term, page, size=20):
    return request("POST", "/Judgements/judgements-list", {
        "pageNumber": page, "pageSize": size, "judgmentNo": None,
        "decisionNo": None, "cityId": None, "courtTypes": 0, "courtId": None,
        "term": term, "dateFrom": None, "dateTo": None, "sortingBy": 2,
    })


def details(jid):
    safe = re.sub(r"[^A-Za-z0-9]", "_", jid)[:60]
    cached = CACHE / f"{safe}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    got = request("GET", "/Judgements/get-details?id=" + urllib.parse.quote(jid))
    if not got or not got.get("success"):
        return None
    model = got.get("model") or {}
    cached.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
    return model


def plain(value):
    """The texts arrive as HTML fragments."""
    if not value:
        return ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--term", required=True, help="free-text query")
    ap.add_argument("--max", type=int, default=40, help="judgments to fetch")
    ap.add_argument("--count-only", action="store_true")
    args = ap.parse_args()

    CACHE.mkdir(exist_ok=True)
    first = search(args.term, 1)
    if not first or not first.get("success"):
        sys.exit("the search endpoint did not answer")
    total = first["model"]["totalCount"]
    print(f"«{args.term}» matches {total:,} judgments")
    if args.count_only:
        return

    wanted = min(args.max, total)
    rows, page = [], 1
    while len(rows) < wanted:
        got = first if page == 1 else search(args.term, page)
        if not got or not got.get("success"):
            print(f"  page {page} did not answer; stopping early")
            break
        batch = got["model"]["judgementsCollection"]
        if not batch:
            break
        for r in batch:
            if len(rows) >= wanted:
                break
            d = details(r["id"])
            if d is None:
                print(f"  {r['judgementNumber']}: details unavailable")
                continue
            body = " ".join(plain(d.get(f)) for f in TEXT_FIELDS).strip()
            rows.append({
                "id": r["id"],
                "judgementNumber": r.get("judgementNumber"),
                "hijriDate": r.get("judgementDate"),
                "city": r.get("city"),
                "court": r.get("courtName"),
                "isAppeal": r.get("isAppeal"),
                "characters": len(body),
                "occurrences": occurrences(body, args.term),
                "text": body,
            })
            print(f"  [{len(rows)}/{wanted}] {r.get('courtName')} "
                  f"{r.get('judgementNumber')} — {len(body)} حرفًا, "
                  f"«{args.term}» ×{occurrences(body, args.term)}")
        page += 1

    slug = re.sub(r'[\\/:*?"<>|\s]+', "_", args.term).strip("_")
    out = HERE / f"judgments_{slug}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    empty = sum(1 for r in rows if not r["text"])
    print(f"\nwrote {out.name}: {len(rows)} judgments, "
          f"{sum(r['characters'] for r in rows):,} characters")
    if empty:
        print(f"{empty} of them carry no text body — the list matched but the "
              f"detail record is empty, and they are kept so the gap is visible")
    print(f"matched {total:,} in total; this run took {len(rows)}")


if __name__ == "__main__":
    main()
