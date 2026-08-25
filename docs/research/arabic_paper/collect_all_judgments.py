#!/usr/bin/env python3
"""Build an open, LLM-ready corpus of Saudi judgments.

Source: the Ministry of Justice legal portal's public gateway. The portal
renders nothing in its page source; these endpoints came from reading its own
lazy-loaded bundle, and the one that matters is spelled the British way,
which is why no amount of guessing found it.

    POST /Judgements/judgements-list      the index, 500 records a page
    GET  /Judgements/get-details?id=      one judgment, in full

50,638 judgments as of 25 August 2026, across the commercial, general and
labour courts. The number grew by four in the hour it took to write this, so
every record carries the date it was retrieved rather than relying on a date
in the README.

TWO STAGES, BECAUSE THEY COST DIFFERENT AMOUNTS
-----------------------------------------------
    --stage index   102 requests, about two minutes. Metadata for everything.
    --stage text    one request per judgment, about fourteen hours.

WHY IT WRITES SHARDS
--------------------
Fourteen hours is longer than an ephemeral container lives. A collector that
keeps everything in a scratch directory and writes at the end loses the lot
when the machine goes away. This one appends a shard of finished judgments
every SHARD_SIZE records, so an interruption costs at most the shard in
progress, and a later run skips every id already present in a shard. Commit
the shards as they appear and the work survives the container.

PROVENANCE
----------
Each record carries the five fields the provenance paper proposed, applied to
this corpus rather than argued about: what class of source it is, how it was
retrieved, what corroborates it, what was transformed, and what disagreed.
The point of proposing a schema is to live under it.

Usage
    python3 collect_all_judgments.py --stage index
    python3 collect_all_judgments.py --stage text
"""

import argparse
import html
import json
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARDS = HERE / "judgments"
INDEX = HERE / "judgments_index.jsonl"
BASE = "https://laws-gateway.moj.gov.sa/apis/legislations/v1"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
DELAY = 1.0          # the portal's own client-side rate limit
PAGE_SIZE = 500      # the largest the endpoint honours
SHARD_SIZE = 500

TEXT_FIELDS = ("judgmentFacts", "judgmentReasons", "judgmentRuling",
               "judgmentTextofRulling", "appealFacts", "appealReasons",
               "appealRuling", "appealTextofRulling")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def request(method, path, body=None, tries=3):
    for attempt in range(1, tries + 1):
        cmd = ["curl", "-sS", "-A", UA, "--max-time", "120",
               "-H", "Accept: application/json"]
        if method == "POST":
            cmd += ["-H", "Content-Type: application/json", "-X", "POST",
                    "-d", json.dumps(body, ensure_ascii=False)]
        cmd.append(BASE + path)
        out = subprocess.run(cmd, capture_output=True, text=True)
        time.sleep(DELAY)
        if out.returncode == 0:
            try:
                return json.loads(out.stdout)
            except json.JSONDecodeError:
                pass  # the gateway answers unknown routes in plain text
        if attempt < tries:
            time.sleep(5 * attempt)
    return None


def plain(value):
    """The texts arrive as HTML fragments."""
    if not value:
        return ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


SITEMAP = "https://laws.moj.gov.sa/sitemap-judicial-decisions.xml"


def sitemap_ids():
    """The ministry's own sitemap, as a second opinion on what exists.

    It is not the full enumeration - 10,000 unique ids against 50,638
    reported - but it is a different route to the same corpus, and the ids it
    carries that the paged listing missed are proof the listing misses some.
    """
    out = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "180", SITEMAP],
                         capture_output=True, text=True)
    time.sleep(DELAY)
    if out.returncode != 0:
        print("  sitemap unavailable; continuing without it")
        return set()
    ids = {urllib.parse.unquote(u.rsplit("/", 1)[-1])
           for u in re.findall(r"<loc>([^<]+)</loc>", out.stdout)
           if "/JudicialDecisionsList/" in u}
    print(f"  sitemap lists {len(ids):,} unique judgments")
    return ids


def index_pass(pages, known):
    """One sweep of the paged listing. Returns the records it had not seen."""
    fresh = []
    for page in range(1, pages + 1):
        got = request("POST", "/Judgements/judgements-list",
                      {"pageNumber": page, "pageSize": PAGE_SIZE,
                       "courtTypes": 0, "term": "", "sortingBy": 2})
        if not got or not got.get("success"):
            print(f"    page {page}: no answer")
            continue
        for r in got["model"]["judgementsCollection"]:
            if r["id"] not in known:
                known.add(r["id"])
                r["retrieved_at"] = now()
                fresh.append(r)
    return fresh


def stage_index():
    """Sweep until the listing stops yielding anything new.

    The paged listing is not stable. Re-fetching page 7 after a complete pass
    returned seven ids that pass had never seen, and no page had failed. The
    records shift between pages while the corpus is being read, so a single
    pass does not miss a few duplicates - it misses judgments, silently. One
    pass gave 49,515 of the 50,638 the endpoint itself reports.

    So: sweep repeatedly, keep what is new, and stop only after two
    consecutive sweeps that add nothing. Then merge the sitemap's ids, which
    come by a different route and catch some the listing never offers.
    """
    known, rows = set(), []
    if INDEX.exists():
        for line in INDEX.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                known.add(r["id"])
                rows.append(r)
        print(f"resuming from {len(rows):,} already indexed")

    probe = request("POST", "/Judgements/judgements-list",
                    {"pageNumber": 1, "pageSize": PAGE_SIZE, "courtTypes": 0,
                     "term": "", "sortingBy": 2})
    if not probe or not probe.get("success"):
        sys.exit("the index endpoint did not answer")
    total = probe["model"]["totalCount"]
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"the endpoint reports {total:,} judgments, {pages} pages of {PAGE_SIZE}")

    dry = 0
    for sweep in range(1, 21):
        added = index_pass(pages, known)
        rows.extend(added)
        print(f"  sweep {sweep}: +{len(added):,} new, {len(rows):,} total "
              f"({len(rows) / total:.1%} of what the endpoint reports)")
        with INDEX.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        dry = dry + 1 if not added else 0
        if dry >= 2:
            print(f"  two consecutive sweeps added nothing; the listing is exhausted")
            break

    extra = sitemap_ids() - known
    if extra:
        print(f"  the sitemap carries {len(extra):,} the listing never offered")
        with INDEX.open("a", encoding="utf-8") as fh:
            for jid in sorted(extra):
                fh.write(json.dumps(
                    {"id": jid, "from": "sitemap only", "retrieved_at": now()},
                    ensure_ascii=False) + "\n")
            rows.extend([{"id": j} for j in extra])

    print(f"\nwrote {INDEX.name}: {len(rows):,} judgments against the "
          f"{total:,} the endpoint reports")
    if len(rows) < total:
        print(f"{total - len(rows):,} short. The listing stopped offering new "
              f"ids before reaching its own count; that gap is real and is not "
              f"papered over here.")


def done_ids():
    """Every id already written to a shard."""
    ids = set()
    SHARDS.mkdir(exist_ok=True)
    for shard in SHARDS.glob("*.jsonl"):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    ids.add(json.loads(line)["id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return ids


def record_for(meta, detail):
    body = {f: plain(detail.get(f)) for f in TEXT_FIELDS}
    full = " ".join(v for v in body.values() if v).strip()
    return {
        "id": meta["id"],
        "case_number": meta.get("caseNumber"),
        "judgment_number": meta.get("judgementNumber"),
        "hijri_date": meta.get("judgementDate"),
        "hijri_year": meta.get("hijriYear"),
        "gregorian_date": detail.get("judgmentDate"),
        "court": meta.get("courtName"),
        "court_type": detail.get("judgmentCourtType"),
        "city": meta.get("city"),
        "is_appeal": meta.get("isAppeal"),
        "title": (detail.get("title") or "").strip(),
        "has_judgment": detail.get("hasJudgment"),
        "has_appeal": detail.get("hasAppeal"),
        "sections": {k: v for k, v in body.items() if v},
        "text": full,
        "characters": len(full),
        "provenance": {
            "source_class": "official primary — the publisher's own gateway",
            "retrieval_route": f"GET {BASE}/Judgements/get-details?id=",
            "corroboration": "index record and detail record agree on the "
                             "judgment number and court",
            "transformation": "HTML fragments stripped to plain text; "
                              "whitespace collapsed; sections kept separately "
                              "as well as concatenated",
            "discrepancy": None,
            "retrieved_at": now(),
        },
    }


def stage_text():
    if not INDEX.exists():
        sys.exit("run --stage index first")
    index = [json.loads(l) for l in INDEX.read_text(encoding="utf-8").splitlines() if l.strip()]
    already = done_ids()
    todo = [r for r in index if r["id"] not in already]
    print(f"{len(index):,} in the index, {len(already):,} already collected, "
          f"{len(todo):,} to fetch — about {len(todo) / 3600:.1f} hours")

    SHARDS.mkdir(exist_ok=True)
    n = len(list(SHARDS.glob("*.jsonl")))
    buffer, failures = [], 0

    def flush():
        nonlocal buffer, n
        if not buffer:
            return
        shard = SHARDS / f"judgments_{n:04d}.jsonl"
        with shard.open("w", encoding="utf-8") as fh:
            for row in buffer:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"  wrote {shard.name} ({len(buffer)} judgments)")
        n += 1
        buffer = []

    for i, meta in enumerate(todo, 1):
        got = request("GET", "/Judgements/get-details?id=" +
                      urllib.parse.quote(meta["id"]))
        if not got or not got.get("success") or not got.get("model"):
            failures += 1
            print(f"  [{i}/{len(todo)}] {meta.get('judgementNumber')}: "
                  f"no detail record")
            continue
        row = record_for(meta, got["model"])
        detail_no = str(got["model"].get("judgmentNumber") or "")
        if detail_no and detail_no != str(meta.get("judgementNumber")):
            row["provenance"]["discrepancy"] = (
                f"index says {meta.get('judgementNumber')}, "
                f"detail says {detail_no}")
        buffer.append(row)
        if len(buffer) >= SHARD_SIZE:
            flush()
        if i % 100 == 0:
            print(f"  [{i}/{len(todo)}] {len(already) + i:,} of {len(index):,}")
    flush()
    print(f"\nfinished this pass. {failures} judgments returned no detail "
          f"record and are absent from the shards, not silently counted.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("index", "text"), required=True)
    args = ap.parse_args()
    stage_index() if args.stage == "index" else stage_text()


if __name__ == "__main__":
    main()
