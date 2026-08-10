#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge into the archive title index every page the sitemaps expose and it has
never seen — and put the newly-found legislative ones through the gates.

WHY THIS EXISTS. Every coverage claim this corpus makes rests on
reports/gazette_ingestion_backlog/gazette_title_index.json: a title-and-date
index of the Umm Al-Qura archive, harvested once, ending 2026-07-31. The
freshness watcher can now tell you the index is behind. This is the tool that
puts it back in front.

INCREMENTAL, AND THAT IS A JUDGEMENT WORTH STATING. It would be simpler to
describe this as "re-harvest the index" and re-fetch all 8,997 pages. That would
cost hours and gigabytes to re-confirm titles that do not change, and it would
discard a round of work already done — the index's titles went through a
truncation-recovery pass that pulled 2,043 clipped titles from og:title. So this
tool only ADDS: an id already in the index is never re-fetched and never
overwritten. What it cannot do is notice a title the gazette has since edited;
that is a real limit and it is recorded in the index's own refresh log rather
than papered over.

THE SITEMAPS ARE NOT AN INVENTORY. Measured: all 163 monthly sitemaps together
expose 638 addressable pages, against 8,997 in the index. The gazette's sitemaps
list a rotating slice, not the archive. So this tool can extend the index and can
NEVER rebuild it, and a caller who reads "refreshed" as "complete" would be
wrong. The number that matters is how many pages it ADDED, not how many it saw.

WHAT IT FOUND THE FIRST TIME. 479 addressable pages absent from the index, 76 of
them in the legislative section — and they live under URL SUB-SECTIONS the
original harvest never walked: /decisions-and-regulations/rules-and-regulations/,
/authorities/, /the-royal-court/, /council-of-ministers-decisions/. The index was
not merely out of date at its tail; it had a shape it never covered.

Read-only over data/. Writes the title index and the gate triage report, both
under reports/. Live network; not part of the QA gate.

Usage:
    python3 scripts/refresh_gazette_title_index.py            # sweep, merge, gate
    python3 scripts/refresh_gazette_title_index.py --dry-run  # report only
    python3 scripts/refresh_gazette_title_index.py --limit 50
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

INDEX_PATH = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                          "gazette_title_index.json")
TRIAGE_PATH = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                           "gazette_gate_triage.json")
OUT = os.path.join(ROOT, "reports", "gazette_index_freshness",
                   "gazette_index_refresh.json")
TMP = "/tmp/refresh_gazette_page.html"

# Sections whose pages are not documents and carry no publication date. The
# /infographic/ pages are picture summaries OF instruments published elsewhere:
# they have a title and no date, so merging them would put 34 dateless rows into
# an index whose end date is the number everything else is measured against.
# Skipped by section rather than dropped for being "incomplete" — the difference
# matters, because "incomplete" invites somebody to go fix them.
EXCLUDED_SECTIONS = ("infographic",)

_H1_RE = re.compile(r'<h1 class="article-title">\s*(.*?)\s*</h1>', re.S)
_OG_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"')
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
_DATE_RE = re.compile(r"(\d{1,2})-(\d{1,2})-(\d{4})")
_TAG_RE = re.compile(r"<[^>]+>")


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(ROOT, "scripts", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clean(s):
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", s or "")).replace("&nbsp;", " ").strip()


def page_title_and_date(html):
    """The untruncated title and the Gregorian publication date.

    The CMS clips its own <title> at ~70 characters, which is what put 2,043
    truncated titles in the index the first time. The <h1> carries the full one,
    so it is preferred and <title> is the last resort, never the first."""
    title = ""
    for rx in (_H1_RE, _OG_RE, _TITLE_RE):
        m = rx.search(html)
        if m:
            t = clean(m.group(1))
            if t and not t.endswith(("...", "…")):
                title = t
                break
            title = title or t
    # The masthead is searched across the WHOLE page, not a head slice. The first
    # version capped the search at 200 KB and every date came back empty: these
    # pages run to ~800 KB and the date-item div sits around 740 KB in, after the
    # site chrome. Six entries were merged with blank dates before the check
    # caught it — which is why the merge is verified on the pages it adds and not
    # only on the ones it skips.
    date = ""
    m = re.search(r'class="date-item".*?</div>', html, re.S)
    if m:
        d = _DATE_RE.search(clean(m.group(0)))
        if d:
            date = "%s-%02d-%02d" % (d.group(3), int(d.group(2)), int(d.group(1)))
    return title, date


def fetch_page(url, timeout=45, attempts=3):
    for attempt in range(attempts):
        r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url, "-o", TMP],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(TMP) and os.path.getsize(TMP) > 20000:
            return open(TMP, encoding="utf-8", errors="replace").read()
        if attempt < attempts - 1:
            time.sleep(2 ** attempt)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    fresh = _load("check_gazette_index_freshness")
    G = _load("gazette_autoingest")

    index = json.load(open(INDEX_PATH, encoding="utf-8"))
    known = set(index["index"])

    body, err = fresh.fetch(fresh.SITEMAP_INDEX, 60)
    if body is None:
        print("COULD NOT CHECK — %s unreachable (%s). Inconclusive." %
              (fresh.SITEMAP_INDEX, err))
        return 0
    months = [(l.strip(), m.strip()[:10])
              for l, m in fresh._PAIR_RE.findall(body)
              if fresh._MONTH_RE.search(l.strip())]
    print("monthly sitemaps: %d" % len(months))

    live, failures = {}, []
    for i, (loc, lastmod) in enumerate(months):
        if i:
            time.sleep(fresh.POLITE_DELAY_SECONDS)
        page, e = fresh.fetch(loc, 60)
        if page is None:
            failures.append({"sitemap": loc, "error": e})
            continue
        for url in fresh._LOC_RE.findall(page):
            sec, pid = fresh.section_and_id(url)
            if pid:
                live.setdefault(pid, {"url": url, "section": sec})

    unseen = {pid: v for pid, v in live.items()
              if pid not in known and v["section"] not in EXCLUDED_SECTIONS}
    skipped_sections = sum(1 for pid, v in live.items()
                           if pid not in known and v["section"] in EXCLUDED_SECTIONS)
    print("live pages %d | absent from the index %d | sitemap failures %d"
          % (len(live), len(unseen), len(failures)))
    if skipped_sections:
        print("skipped %d unseen pages in non-document sections %s (no publication date)"
              % (skipped_sections, list(EXCLUDED_SECTIONS)))
    if failures:
        print("A PARTIAL SWEEP IS NOT A COMPLETE ONE — %d monthly sitemaps could not "
              "be fetched; pages published in those months cannot be seen." % len(failures))
    if args.dry_run:
        print("--dry-run: nothing written")
        return 0

    order = sorted(unseen)
    if args.limit:
        order = order[:args.limit]

    names, taken = G.registry_titles()
    triage = json.load(open(TRIAGE_PATH, encoding="utf-8"))
    already_judged = ({r["uid"] for r in triage["rejected"]}
                      | {r["uid"] for r in triage["accepted_pages"]})

    added, gated, fetch_failed, incomplete = [], [], [], []
    for i, pid in enumerate(order):
        v = unseen[pid]
        if i:
            time.sleep(0.35)
        html = fetch_page(v["url"])
        if html is None:
            fetch_failed.append(pid)
            continue
        title, date = page_title_and_date(html)
        if not title or not date:
            # An entry with a blank title or date is worse than a missing one: it
            # reads as harvested and answers nothing. Report it, do not merge it.
            incomplete.append({"page_id": pid, "url": v["url"],
                               "title": title, "date": date})
            continue
        index["index"][pid] = {"title": title, "date": date}
        added.append(pid)

        if v["section"] in fresh.LEGISLATIVE_SECTIONS and pid not in already_judged:
            notes = []
            open(TMP, "w", encoding="utf-8").write(html)
            t, b = G.page_text(TMP, notes)
            spec, reasons = G.evaluate(t, b, names, taken, extraction_notes=notes)
            row = {"uid": pid, "url": v["url"], "title_ar": title, "date": date}
            if spec and not reasons:
                triage["accepted_pages"].append(dict(row, verdict="accepted"))
                gated.append((pid, "ACCEPTS", spec["article_count"], title))
            else:
                triage["rejected"].append(dict(row, verdict="refused",
                                               blocking_gates=reasons))
                gated.append((pid, "refused", spec["article_count"] if spec else 0, title))

    if os.path.exists(TMP):
        os.remove(TMP)

    index["pages"] = len(index["index"])
    dates = sorted(x.get("date") for x in index["index"].values() if x.get("date"))
    index.setdefault("refresh_log", []).append({
        "added_pages": len(added),
        "sitemap_months_swept": len(months) - len(failures),
        "sitemap_months_unreachable": len(failures),
        "page_fetch_failures": len(fetch_failed),
        "incomplete_pages_not_merged": len(incomplete),
        "new_end_date": dates[-1] if dates else None,
        "note": ("حصادٌ **تزايدي** لا إعادةَ بناء: لا يُعاد جلبُ صفحةٍ يحملها الفهرس "
                 "ولا يُكتب فوقها — عناوينُه مرّت بجولة استعادةٍ للعناوين المبتورة، "
                 "وإعادةُ جلب تسعة آلاف صفحة تُنفق ساعاتٍ لتؤكد ما لا يتغيّر. **والحدُّ "
                 "المعروف**: لا يلاحظ هذا عنواناً عدّلته الجريدة بعد حصاده. **وخرائطُ "
                 "الموقع ليست جرداً**: الـ163 خريطة تعرض 638 صفحة مقابل ما يقارب تسعة "
                 "آلاف في الفهرس، فهذه الأداة **تُوسِّع الفهرس ولا تبنيه**."),
    })
    json.dump(index, open(INDEX_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    triage["pages_examined"] = triage.get("pages_examined", 0) + len(gated)
    triage["accepted"] = len(triage["accepted_pages"])
    triage["refused"] = len(triage["rejected"])
    triage["rejected_count"] = len(triage["rejected"])
    json.dump(triage, open(TRIAGE_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    accepts = [g for g in gated if g[1] == "ACCEPTS"]
    print("\nadded to the index: %d pages (index now %d, ends %s)"
          % (len(added), index["pages"], index["refresh_log"][-1]["new_end_date"]))
    print("put through the gates: %d legislative pages | ACCEPTED %d | refused %d"
          % (len(gated), len(accepts), len(gated) - len(accepts)))
    if fetch_failed:
        print("page fetch failures (not merged, not judged): %d" % len(fetch_failed))
    if incomplete:
        print("pages with no readable title or date (NOT merged): %d" % len(incomplete))
    for pid, verdict, n, title in accepts:
        print("   ACCEPTS %-10s %3d articles  %s" % (pid, n, title[:66]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "حصادٌ تزايدي لفهرس أرشيف الجريدة: مسحٌ كامل للخرائط الشهرية، ثم جلبُ "
            "**ما لم يره الفهرس وحده** لعنوانه وتاريخه، ثم تمريرُ الصفحات التشريعية "
            "الجديدة على بوابات الإدخال. **الخرائطُ ليست جرداً** — تعرض 638 صفحة مقابل "
            "نحو تسعة آلاف في الفهرس — فالأداة **تُوسِّع الفهرس ولا تبنيه**، والرقمُ "
            "الذي يعني شيئاً هو **كم أضافت** لا كم رأت."),
        "sitemap_months_swept": len(months) - len(failures),
        "sitemap_failures": failures,
        "live_pages_seen": len(live),
        "absent_from_index": len(unseen),
        "skipped_non_document_sections": skipped_sections,
        "added_to_index": len(added),
        "index_pages_after": index["pages"],
        "index_end_date_after": index["refresh_log"][-1]["new_end_date"],
        "page_fetch_failures": fetch_failed,
        "incomplete_not_merged": incomplete,
        "legislative_pages_gated": len(gated),
        "accepted": [{"page_id": p, "articles": n, "title_ar": t}
                     for p, v, n, t in accepts],
        "refused": [{"page_id": p, "title_ar": t}
                    for p, v, n, t in gated if v != "ACCEPTS"],
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
