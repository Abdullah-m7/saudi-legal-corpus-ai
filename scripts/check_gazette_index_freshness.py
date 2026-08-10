#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Has the official gazette published anything this corpus has never looked at?

WHY THIS EXISTS. Everything this corpus knows about what EXISTS comes from one
harvested artifact: reports/gazette_ingestion_backlog/gazette_title_index.json,
a title-and-date index of every addressable page in the Umm Al-Qura archive. It
was harvested once. The gazette did not stop publishing.

That gap is not hypothetical. Re-fetching the sitemaps once found 45 pages the
index had never seen; fourteen of them were published in a single day AFTER the
index's own end date, and four were in-force instruments that passed every
ingestion gate — «نظام إيرادات الدولة» among them. Four in-force instruments
were one diff away from being missed indefinitely, and nothing in the repository
would have said so.

So: the index has an END DATE and the gazette does not. This tool measures that
distance. It compares the live sitemaps against the index the corpus actually
holds and reports what the corpus has never seen — as page ids, ready to feed to
scripts/gazette_autoingest.py, which decides admissibility. This tool decides
nothing about legal content; it only answers "is there something new?".

*** NOT PART OF THE DETERMINISTIC QA GATE ***
    Like scripts/check_corpus_freshness.py, this makes live network requests and
    its result depends on external state. It is a periodic operational check, not
    a CI gate — run it after every ingestion round and before believing coverage
    numbers. Exit code is 0 even when stale, unless --fail-if-stale is passed.

*** ROBOTS.TXT IS A COMMITMENT, NOT A SUGGESTION ***
    www.uqn.gov.sa/robots.txt disallows /*page=, /*redirect= and /ajax/ for all
    agents, and DECLARES the sitemap this tool reads. Only the declared sitemaps
    are fetched — no crawling of disallowed paths, no egress-policy workarounds.
    (Contrast rulebook.sama.gov.sa, whose robots.txt is a blanket Disallow: / —
    which is why this corpus has no SAMA circular crawler and never will.)

*** READ-ONLY OVER THE CORPUS ***
    Writes exactly one report file under reports/. Never touches data/, never
    ingests anything, never edits a track. Discovery and ingestion are separate
    jobs on purpose: this tool is allowed to be wrong about what matters, because
    something else decides that.

WHAT IT COSTS. By default it fetches only the monthly sitemaps that could
possibly hold something new — those whose lastmod is at or after the corpus
index's newest recorded page, plus the two most recent months unconditionally.
That is a handful of requests, not 163. Pass --all for the full sweep.

Usage:
    python3 scripts/check_gazette_index_freshness.py
    python3 scripts/check_gazette_index_freshness.py --all
    python3 scripts/check_gazette_index_freshness.py --fail-if-stale
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLE_INDEX = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                           "gazette_title_index.json")
OUT = os.path.join(ROOT, "reports", "gazette_index_freshness",
                   "gazette_index_freshness.json")
TRIAGE = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                      "gazette_gate_triage.json")

SITEMAP_INDEX = "https://www.uqn.gov.sa/sitemap_0.xml"
USER_AGENT = ("Mozilla/5.0 (compatible; saudi-legal-corpus-ai freshness check; "
              "+https://github.com/al3obdi/saudi-legal-corpus-ai)")
POLITE_DELAY_SECONDS = 0.7

# The gazette's URL sections. Only the first carries legislative instruments;
# the rest are news, ads and author/section landing pages. Nothing is ingested
# from a section this map calls non-legislative — but unseen ids in the other
# sections are still COUNTED, because a section changing shape is itself news.
LEGISLATIVE_SECTIONS = ("decisions-and-regulations",)

_LOC_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
_PAIR_RE = re.compile(r"<loc>\s*(.*?)\s*</loc>\s*<lastmod>\s*(.*?)\s*</lastmod>", re.S)
_MONTH_RE = re.compile(r"/sitemaps/(\d{4})/(\d{1,2})/sitemap_\d+\.xml")
_ID_RE = re.compile(r"uqn\.gov\.sa/(?:([a-z0-9\-]+)/)?(?:[a-z0-9\-]+/)?(\d{3,})\s*$")


def fetch(url: str, timeout: int, attempts: int = 3) -> tuple[str | None, str | None]:
    """A plain HTTPS GET, retried on transport errors. Never routes around a block.

    RETRY IS NOT POLITENESS, IT IS ACCURACY. The first full sweep lost 19 of the
    163 monthly sitemaps to «Connection reset by peer» — all of them old months —
    and a sweep that silently covers 144 months reads exactly like a sweep that
    covers 163. The failures were always reported, but reporting a hole is not the
    same as not having one: every unseen page in a month that failed to fetch is a
    page this tool cannot see and cannot say it cannot see. An HTTP status is a
    real answer and is NOT retried; a reset connection is not an answer at all."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    err = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            return None, "HTTP %s" % e.code
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            err = "%s: %s" % (type(e).__name__, e)
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
    return None, err


def corpus_index():
    """The page ids this corpus has ever SEEN, and the date it stops at."""
    with open(TITLE_INDEX, encoding="utf-8") as f:
        d = json.load(f)
    ids = set(d["index"])
    dates = sorted(v.get("date") for v in d["index"].values() if v.get("date"))
    return ids, (dates[-1] if dates else None), d.get("pages")


def ingested_ids():
    """The page ids that actually became tracks — read off each source artifact's
    own recorded URL, never guessed."""
    out = set()
    pats = (re.compile(r"uqn\.gov\.sa/details\?p=(\d+)"),
            re.compile(r"uqn\.gov\.sa/decisions-and-regulations/(\d+)"))
    for p in (glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json"))
              + glob.glob(os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json"))):
        try:
            blob = open(p, encoding="utf-8").read()
        except OSError:
            continue
        for pat in pats:
            out.update(pat.findall(blob))
    return out


def judged_ids():
    """Page ids the ingestion gates have already ruled on and REFUSED.

    A page the gates read and turned down is not an unexamined page, and calling
    it one would make this tool re-report the same approval decrees after every
    run until somebody stopped believing it. The triage report exists precisely
    so an absence from the corpus can be argued with rather than merely noticed."""
    try:
        d = json.load(open(TRIAGE, encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {r["uid"] for r in d.get("rejected", []) if r.get("uid")}


def section_and_id(url: str):
    m = _ID_RE.search(url)
    if not m:
        return None, None
    sec = url.split("uqn.gov.sa/", 1)[-1].split("/")[0]
    return sec, m.group(2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true",
                    help="fetch every monthly sitemap, not only the ones that could be new")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--fail-if-stale", action="store_true",
                    help="exit 1 when the gazette holds legislative pages this corpus has "
                         "NEVER EXAMINED (not merely ones its harvested index lags behind)")
    args = ap.parse_args()

    seen_ids, index_end_date, index_pages = corpus_index()
    built = ingested_ids()
    refused = judged_ids()
    print("corpus gazette index: %s pages, newest recorded publication %s"
          % (index_pages, index_end_date))
    print("ingested as tracks:   %d gazette page ids" % len(built))
    print("judged and refused:   %d gazette page ids" % len(refused))

    body, err = fetch(SITEMAP_INDEX, args.timeout)
    if body is None:
        # A network failure says nothing about the real world. Say exactly that.
        print("\nCOULD NOT CHECK — %s is unreachable from here (%s)." % (SITEMAP_INDEX, err))
        print("This is inconclusive, NOT evidence that the gazette published nothing.")
        result = {"verdict": "UNREACHABLE", "error": err,
                  "sitemap_index": SITEMAP_INDEX,
                  "corpus_index_end_date": index_end_date}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 0

    months = []
    for loc, lastmod in _PAIR_RE.findall(body):
        if _MONTH_RE.search(loc):
            months.append((loc, lastmod.strip()[:10]))
    months.sort(key=lambda x: x[1])

    if args.all:
        selected = months
        why = "all %d monthly sitemaps (--all)" % len(months)
    else:
        cutoff = index_end_date or "0000-00-00"
        selected = [m for m in months if m[1] >= cutoff]
        for m in months[-2:]:
            if m not in selected:
                selected.append(m)
        selected.sort(key=lambda x: x[1])
        why = ("%d of %d monthly sitemaps — those modified on/after the corpus index's "
               "own end date (%s), plus the two most recent"
               % (len(selected), len(months), cutoff))
    print("\nfetching %s" % why)

    live, failures = {}, []
    for i, (loc, lastmod) in enumerate(selected):
        if i:
            time.sleep(POLITE_DELAY_SECONDS)
        page, e = fetch(loc, args.timeout)
        if page is None:
            failures.append({"sitemap": loc, "error": e})
            continue
        for url in _LOC_RE.findall(page):
            sec, pid = section_and_id(url)
            if pid:
                live.setdefault(pid, {"url": url, "section": sec, "month_lastmod": lastmod})

    unseen = {pid: v for pid, v in live.items() if pid not in seen_ids}
    unseen_legislative = {pid: v for pid, v in unseen.items()
                          if v["section"] in LEGISLATIVE_SECTIONS}
    # A MEASUREMENT CORRECTION WORTH KEEPING. The first run reported 15 unseen
    # legislative pages and four of them were already tracks — ingested in the
    # round that discovered them, from a manual diff, without the harvested index
    # ever being refreshed. Both facts are true and they are NOT the same fact:
    # the index is stale (it should be re-harvested), and the CORPUS is missing
    # eleven pages, not fifteen. Conflating them would overstate the gap every
    # time an ingestion round outruns the index — which is every round.
    actionable = {pid: v for pid, v in unseen_legislative.items()
                  if pid not in built and pid not in refused}
    unseen_but_already_ingested = sorted(
        pid for pid in unseen_legislative if pid in built)
    unseen_but_already_refused = sorted(
        pid for pid in unseen_legislative if pid not in built and pid in refused)
    # Seen by the index but never built. Not staleness — that's the ingestion
    # backlog's job — but reported so the two numbers are never confused.
    live_legislative = {pid for pid, v in live.items()
                        if v["section"] in LEGISLATIVE_SECTIONS}
    not_ingested = sorted(live_legislative - built)

    verdict = ("NEW_LEGISLATIVE_PAGES" if actionable else
               ("INDEX_STALE_ONLY" if unseen_legislative else
                ("FRESH_WITH_FETCH_FAILURES" if failures else "FRESH")))

    print("\nlive pages seen in the fetched sitemaps: %d" % len(live))
    print("  never seen by the corpus index:        %d" % len(unseen))
    print("  ...of those, legislative section:      %d" % len(unseen_legislative))
    print("  ...of those, already ingested anyway:  %d  (index stale, corpus is not)"
          % len(unseen_but_already_ingested))
    print("  ...of those, judged and refused:       %d  (argued with, not missed)"
          % len(unseen_but_already_refused))
    print("  NEVER EXAMINED BY THIS CORPUS:         %d" % len(actionable))
    print("  fetch failures:                        %d" % len(failures))
    print("\nVERDICT: %s" % verdict)
    if actionable:
        print("\nThe gazette holds legislative pages this corpus has never examined.")
        print("Feed these ids to scripts/gazette_autoingest.py — it, not this tool,")
        print("decides whether any of them is admissible:")
        for pid, v in sorted(actionable.items()):
            print("   %-10s %s" % (pid, v["url"]))
    elif unseen_legislative:
        print("\nEvery unseen legislative page is already a track or already judged and "
              "refused:\nthe harvested index lags the corpus, not the other way round. "
              "Re-harvest it when\nconvenient; no content is missing.")
    else:
        print("\nNo legislative page in the fetched sitemaps is absent from the corpus index.")
    if failures:
        print("\nsitemaps that could not be fetched (inconclusive, not 'empty'):")
        for f in failures:
            print("   %s  %s" % (f["sitemap"], f["error"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "كل ما يعرفه هذا المستودع عن **ما هو موجود** مصدرُه أثرٌ واحد حُصِد مرةً واحدة: "
            "فهرس عناوين أرشيف أم القرى. والجريدة لم تتوقف عن النشر. **للفهرس تاريخُ نهاية، "
            "وللجريدة ليس**. هذه الأداة تقيس تلك المسافة: تقارن خرائط الموقع الحيّة بالفهرس "
            "الذي يحمله المستودع، وتعرض ما لم يره قط — أرقامَ صفحات جاهزة لتمريرها على "
            "بوابات الإدخال، **لا حكماً على مضمونها**. وقد ثبت أن الفجوة ليست فرضية: إعادة "
            "الجلب مرةً واحدة كشفت 45 صفحة لم يرها الفهرس، أربعٌ منها أدوات سارية اجتازت كل "
            "البوابات — منها «نظام إيرادات الدولة». **وتُحترم robots.txt بوصفها التزاماً**: "
            "لا يُجلب إلا ما تُصرِّح به خريطة الموقع المعلنة."),
        "checked_sitemap_index": SITEMAP_INDEX,
        "selection_policy": why,
        "corpus_index_pages": index_pages,
        "corpus_index_end_date": index_end_date,
        "ingested_gazette_page_ids": len(built),
        "monthly_sitemaps_available": len(months),
        "monthly_sitemaps_fetched": len(selected) - len(failures),
        "fetch_failures": failures,
        "live_pages_seen": len(live),
        "unseen_by_corpus_index": len(unseen),
        "unseen_legislative": len(unseen_legislative),
        "unseen_legislative_already_ingested": unseen_but_already_ingested,
        "unseen_legislative_already_judged_and_refused": unseen_but_already_refused,
        "never_examined_by_this_corpus": len(actionable),
        "verdict": verdict,
        "verdict_vocabulary": {
            "FRESH": "لا صفحة تشريعية في الخرائط المجلوبة غائبة عن فهرس المستودع.",
            "INDEX_STALE_ONLY": ("الفهرس المحصود متأخر عن المستودع: الصفحات غير المرئية "
                                 "له إمّا مبنيةٌ مساراتٍ فعلاً وإمّا حكمت عليها البوابات "
                                 "ورفضتها. لا ينقص المستودع محتوى."),
            "NEW_LEGISLATIVE_PAGES": ("الجريدة نشرت صفحاتٍ تشريعية لم يفحصها المستودع قط. "
                                      "تُمرَّر أرقامها على بوابات الإدخال، وهي — لا هذه "
                                      "الأداة — من يقرر قبولها."),
            "FRESH_WITH_FETCH_FAILURES": "لا جديد فيما جُلب، وبعض الخرائط تعذّر جلبها فالنتيجة ناقصة.",
            "UNREACHABLE": "تعذّر الوصول إلى خريطة الموقع؛ نتيجة غير قاطعة، وليست دليلاً على عدم النشر.",
        },
        "never_examined_pages": [
            {"page_id": pid, **v} for pid, v in sorted(actionable.items())],
        "unseen_legislative_pages": [
            {"page_id": pid, **v} for pid, v in sorted(unseen_legislative.items())],
        "unseen_other_sections": [
            {"page_id": pid, **v} for pid, v in sorted(unseen.items())
            if v["section"] not in LEGISLATIVE_SECTIONS],
        "legislative_pages_seen_but_not_ingested": not_ingested,
        "legislative_pages_seen_but_not_ingested_note": (
            "ليست تقادماً بل متأخرات إدخال: صفحات رآها الفهرس ولم تُبنَ مساراً، وأكثرها "
            "مرفوض عن قصد ببوابات الإدخال (إعلانات، أخبار، أدوات ملغاة). تُعرض هنا كي لا "
            "يُخلط الرقمان."),
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))

    return 1 if (args.fail_if_stale and actionable) else 0


if __name__ == "__main__":
    sys.exit(main())
