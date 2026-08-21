#!/usr/bin/env python3
"""Collect the UK Public General Acts, recording provenance as we go.

This is the second jurisdiction for the provenance study, and it inverts the
first one's method. The Saudi corpus's provenance record was a by-product:
someone wrote down, in prose, what each retrieval attempt returned, and
`../provenance_paper/` had to recover a measurement from 158 distinct free-text
strings --- of which a quarter turned out not to be provenance at all. Here the
five-field schema that paper proposed is populated at the moment of collection,
which is the claim it makes about cost: a process that knows how it obtained a
document knows all five fields already.

The fields are those of Table 2 in the provenance paper, unchanged:

    source_class     official-primary | official-secondary | independent
                     | aggregator
    retrieval_route  live | archived-capture | offline-artefact | proxy
    corroboration    integer --- independent sources found to agree
    transformation   none | text-extraction | optical-recognition
                     | manual-transcription
    discrepancy      null, or a short structured note

For legislation.gov.uk most records will be `official-primary`, `live`, and
`none`. That is the point of the comparison rather than a weakness of it: the
Saudi finding was that a fifth of articles were none of those things, and a
second jurisdiction where nearly all of them are is what makes the first
number mean something.

What this collector measures is on the *other* axis. The service publishes,
in each Act's own metadata, a block of `ukm:UnappliedEffect` elements:
amendments that have been enacted but are not yet incorporated into the text
the same service displays. That is the same class of defect as the four Saudi
instruments whose portal text and amendment log disagree --- except that here
it is declared by the publisher, machine-readable, and countable across a whole
national statute book.

Politeness: robots.txt sets `Crawl-delay: 5`, and this script honours it. A
full sweep therefore takes hours rather than minutes. It is resumable, so it
can be stopped and restarted without refetching, and it never requests a
document it already holds.

Read-only against legislation.gov.uk. Run from the repository root:

    python3 docs/research/comparison_paper/collect_uk.py --years 2018-2020
    python3 docs/research/comparison_paper/collect_uk.py --all
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE / "uk_collection"
BASE = "https://www.legislation.gov.uk"

# robots.txt: Crawl-delay: 5. Not negotiable, and not a parameter --- an
# article about how publishers are treated by the people who consume them
# should not be built by ignoring what this one asked for.
CRAWL_DELAY = 5.0

# `data.xml` carries the whole Act; `introduction/data.xml` carries the
# metadata, including the complete UnappliedEffects block, at about a ninth of
# the bytes. Verified equal on the Data Protection Act 2018: 309 elements in
# both. Nine times less traffic for the same measurement.
ACT_META = BASE + "/ukpga/{year}/{num}/introduction/data.xml"
YEAR_FEED = BASE + "/ukpga/{year}/data.feed?results-count=200"


def fetch(url, timeout=60):
    """One retrieval attempt, with everything the schema needs to describe it.

    urllib does not honour this environment's outbound proxy, so curl does the
    request. The timing and status are recorded whether or not the request
    succeeded: a failed attempt is evidence about availability, which is the
    measurement, so it must not be silently retried away.
    """
    started = time.time()
    p = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", str(timeout),
         # This flag does nothing here, and the measurement is why it is kept.
         # It was added on the theory that failures were connections that never
         # opened, so capping the connect phase would fail them fast. The
         # recorded time_connect refutes that: it is ~0.0002s on successes and
         # failures alike, because outbound traffic goes through a local proxy
         # that accepts instantly. The connect phase never reaches the origin,
         # so no connect timeout can bound a stall beyond it --- only
         # --max-time can, and every success here answers in under two seconds,
         # so that is the lever to lower on the next full run.
         #
         # time_connect is still recorded, but it does NOT separate "could not
         # reach the host" from "host was slow to answer" through a proxy: it
         # is constant. An earlier version of this comment claimed it did.
         "--connect-timeout", "10",
         "-w", "\n%{http_code}\t%{num_redirects}\t%{size_download}"
               "\t%{time_connect}", url],
        capture_output=True, text=True)
    elapsed = round(time.time() - started, 3)
    body, _, tail = p.stdout.rpartition("\n")
    parts = tail.split("\t")
    status = parts[0] if parts and parts[0] else "000"

    def field(i, cast):
        try:
            return cast(parts[i])
        except (IndexError, ValueError):
            return None

    return {
        "url": url,
        "http_status": status,
        "redirects": field(1, int) or 0,
        "bytes": field(2, int) or 0,
        "seconds": elapsed,
        "connect_seconds": field(3, float),
        "curl_error": p.stderr.strip()[:200] or None,
    }, body


def provenance(attempt):
    """The five fields of the proposed schema, populated at collection time.

    Written out in full rather than defaulted, because the schema's claim is
    that this costs nothing when the collector knows how it got the document.
    If that claim is false, it should be false here, visibly.
    """
    ok = attempt["http_status"] == "200" and attempt["bytes"] > 0
    return {
        "source_class": "official-primary",
        "retrieval_route": "live" if ok else None,
        # One official source, machine-readable, taken as published. Nothing
        # was cross-checked against a second source, so this is 0 by the
        # schema's own definition and must not be inflated to 1 by counting
        # the source itself.
        "corroboration": 0,
        "transformation": "none",
        "discrepancy": None if ok else {
            "kind": "retrieval-failed",
            "http_status": attempt["http_status"],
            "curl_error": attempt["curl_error"],
        },
    }


# Attributes kept from each effect. `AffectingYear` is how long the amendment
# has gone unincorporated, and `AffectedProvisions` is the unit against which
# the Saudi per-article figures will have to be set --- neither is recoverable
# from a count, and re-fetching the statute book to get them would cost hours
# against a five-second crawl delay. Keeping the attributes rather than a
# summary also leaves the choice of what matters to the analysis, where it
# belongs, instead of freezing it in the collector.
EFFECT_ATTRS = ("Type", "RequiresApplied", "AffectingYear", "AffectingNumber",
                "AffectingClass", "AffectingURI", "AffectingProvisions",
                "AffectedProvisions", "AffectedURI", "AppliedModified",
                "Modified")


def unapplied_effects(xml):
    """Effects the service itself flags as not incorporated into its own text."""
    elements = re.findall(r"<ukm:UnappliedEffect\b[^>]*>", xml)
    effects, types = [], {}
    for element in elements:
        attrs = {}
        for key in EFFECT_ATTRS:
            m = re.search(rf'\b{key}="([^"]*)"', element)
            if m:
                attrs[key] = m.group(1)
        effects.append(attrs)
        if attrs.get("RequiresApplied") == "true":
            kind = attrs.get("Type", "?")
            types[kind] = types.get(kind, 0) + 1
    return {
        "unapplied_total": len(elements),
        "unapplied_requiring_application": sum(
            1 for a in effects if a.get("RequiresApplied") == "true"),
        "by_type": types,
        "effects": effects,
    }


def act_metadata(xml):
    """The descriptive fields the same response already carries.

    Two of these decide whether the headline figure means anything.

    `document_status` separates Acts the Statute Law Database maintains in
    revised form from those served only as enacted. An unmaintained Act carries
    no unapplied effects **because nobody is applying any**, not because its
    text is current --- and in a count of "Acts displaying out-of-date text" it
    would sit silently in the denominator looking clean. It has to be visible
    so the share can be computed over the maintained set as well as over all.

    `body_paragraphs` and `schedule_paragraphs` are the denominator for the
    per-provision figure. Without them the analysis can only report how many
    provisions are affected, never what share of the Act that is, which is the
    unit paper 5's Saudi per-article numbers would have to be set against.

    `last_modified` is the date the service last revised the record, which
    separates a backlog from work in progress.

    All of it arrives in bytes already being fetched, so keeping it costs one
    parse and no extra request.
    """
    def one(pattern, group=1):
        m = re.search(pattern, xml)
        return m.group(group) if m else None

    stats = {}
    for name, key in (("TotalParagraphs", "total_paragraphs"),
                      ("BodyParagraphs", "body_paragraphs"),
                      ("ScheduleParagraphs", "schedule_paragraphs")):
        v = one(rf'<ukm:{name} Value="(\d+)"')
        stats[key] = int(v) if v else None

    return {
        "title": one(r"<dc:title>([^<]*)</dc:title>"),
        "enactment_date": one(r'<ukm:EnactmentDate Date="([^"]*)"'),
        "last_modified": one(r"<dc:modified>([^<]*)</dc:modified>"),
        "document_status": one(r'<ukm:DocumentStatus Value="([^"]*)"'),
        "document_main_type": one(r'<ukm:DocumentMainType Value="([^"]*)"'),
        **stats,
    }

def act_numbers(year):
    attempt, body = fetch(YEAR_FEED.format(year=year))
    if attempt["http_status"] != "200":
        return None, attempt
    seen, out = set(), []
    for num in re.findall(rf"/id/ukpga/{year}/(\d+)\b", body):
        if num not in seen:
            seen.add(num)
            out.append(int(num))
    return sorted(out), attempt


def collect(years):
    STORE.mkdir(exist_ok=True)
    for year in years:
        path = STORE / f"{year}.json"
        if path.exists():
            print(f"{year}: already collected, skipping")
            continue
        nums, feed_attempt = act_numbers(year)
        time.sleep(CRAWL_DELAY)
        if nums is None:
            print(f"{year}: feed failed ({feed_attempt['http_status']})")
            path.write_text(json.dumps(
                {"year": year, "feed_attempt": feed_attempt, "acts": None},
                ensure_ascii=False, indent=1), encoding="utf-8")
            continue
        acts = []
        for num in nums:
            attempt, body = fetch(ACT_META.format(year=year, num=num))
            record = {
                "id": f"ukpga/{year}/{num}",
                "retrieval": attempt,
                "provenance": provenance(attempt),
            }
            if attempt["http_status"] == "200":
                record.update(unapplied_effects(body))
                record.update(act_metadata(body))
            acts.append(record)
            print(f"  {record['id']:>18s}  {attempt['http_status']}  "
                  f"{attempt['seconds']:5.2f}s  "
                  f"unapplied={record.get('unapplied_requiring_application', '-')}")
            time.sleep(CRAWL_DELAY)
        path.write_text(json.dumps(
            {"year": year, "feed_attempt": feed_attempt, "acts": acts},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{year}: {len(acts)} Acts written to {path.name}")


def retry_failures():
    """Second pass over the Acts whose first retrieval failed.

    The collector deliberately does not retry: a non-200 is evidence about
    availability, and retrying it away would erase the measurement. That was
    right while availability was part of the comparison. It is not right now.
    The comparison has been narrowed to consistency (see README), so a failed
    retrieval no longer buys a measurement --- it only costs an Act's worth of
    coverage in the count of unincorporated amendments.

    Both attempts are kept. The first stays exactly where it was, so the
    availability record remains what the collector actually saw; the second is
    recorded beside it under `retrieval_retry`, and only it fills the
    consistency data. Nothing is overwritten, so a reader can see that the
    document arrived on a second try and decide what to make of it.

    Every failure seen so far has been a connection that never opened ---
    60-second timeouts on documents of a few kilobytes that then return in
    under a second --- which is the signature of this collector's network, not
    of the service.
    """
    recovered = still_failing = 0
    for path in sorted(STORE.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("acts"):
            continue
        changed = False
        for act in data["acts"]:
            if act["retrieval"]["http_status"] == "200":
                continue
            if act.get("retrieval_retry", {}).get("http_status") == "200":
                continue
            year, num = act["id"].split("/")[1:]
            attempt, body = fetch(ACT_META.format(year=year, num=num))
            act["retrieval_retry"] = attempt
            changed = True
            if attempt["http_status"] == "200":
                act.update(unapplied_effects(body))
                act.update(act_metadata(body))
                # The record now has the text, so the discrepancy that stood
                # for "we could not get this" is resolved rather than deleted.
                act["provenance"]["retrieval_route"] = "live"
                act["provenance"]["discrepancy"] = {
                    "kind": "retrieval-failed-then-recovered",
                    "first_attempt_status": act["retrieval"]["http_status"],
                    "first_attempt_seconds": act["retrieval"]["seconds"],
                }
                recovered += 1
                print(f"  recovered {act['id']} in {attempt['seconds']:.2f}s")
            else:
                still_failing += 1
                print(f"  still failing {act['id']} ({attempt['http_status']})")
            time.sleep(CRAWL_DELAY)
        if changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    print(f"recovered {recovered}, still failing {still_failing}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", help="e.g. 2018-2020 or 2019")
    ap.add_argument("--all", action="store_true",
                    help="1801 to the present")
    ap.add_argument("--retry-failures", action="store_true",
                    help="second pass over Acts whose first retrieval failed")
    a = ap.parse_args()
    if a.retry_failures:
        retry_failures()
        return
    if a.all:
        years = range(1801, 2027)
    elif a.years and "-" in a.years:
        lo, hi = a.years.split("-")
        years = range(int(lo), int(hi) + 1)
    elif a.years:
        years = [int(a.years)]
    else:
        sys.exit("give --years or --all")
    collect(list(years))


if __name__ == "__main__":
    main()
