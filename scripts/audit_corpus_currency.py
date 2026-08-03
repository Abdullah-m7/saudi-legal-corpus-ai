#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Currency audit: which tracks have been amended since the edition on file?

WHY THIS EXISTS
---------------
The ingestion gates protect against two things -- ingesting a document twice,
and ingesting a document badly. They cannot protect against a third, which is
the one that quietly rots a legal corpus: an instrument the corpus already
holds is AMENDED, and the corpus goes on asserting the older text as in force.

Two shapes of change matter, and they need different detection:

  * a full RE-ISSUE, where the gazette republishes the whole instrument. The
    ingestion gate now catches this itself (G2-LATER-EDITION), because the
    re-issue scores as a near-duplicate of the track while carrying a later
    publication date.

  * an AMENDMENT NOTICE — «تعديل مواد في اللائحة التنفيذية لنظام الزراعة»,
    «تحديث اللائحة التنفيذية لنظام مكافحة غسل الأموال». These are the common
    case, and the ingestion gate deliberately drops them at G1: an amendment
    notice is not a standalone instrument and must never be built as a track.
    Dropping them for INGESTION was right; dropping them for AUDIT was the
    blind spot. The notice is evidence about a track we already hold.

This script reads the harvested gazette title index (title + publication date
for every addressable archive URL) and reports, for each track, every
amendment notice published AFTER the edition the corpus holds.

It asserts nothing about the amendment's content -- it cannot, since the
notice is not the amended text. It reports a track as AT RISK and names the
gazette page to go read. Nothing here rewrites a track or infers legal effect.

Read-only. Exit 0 always: this is a report, not a gate.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from gazette_autoingest import norm_ar  # noqa: E402

# Title shapes that announce a change to an instrument rather than a new one.
AMENDMENT_RE = re.compile(r"(تعديل|تعديلات|تحديث|إلغاء|الغاء|استبدال|إضافة\s+مادة|حذف\s+مادة)")

# Words that carry no discriminating power when matching an amendment notice
# against a track title: they appear in almost every legal title.
STOP = {"نظام", "النظام", "لنظام", "لائحه", "اللائحه", "التنفيذيه", "التنظيميه",
        "قواعد", "القواعد", "المنظمه", "ضوابط", "الضوابط", "تنظيم", "الترتيبات",
        "تعليمات", "الاساس", "في", "من", "علي", "بعض", "بنود", "مواد", "الماده",
        "المواد", "تعديل", "تعديلات", "تحديث", "الغاء", "استبدال", "الوارده",
        "علي", "الخاص", "الخاصه", "بشان", "على"}

MIN_SHARED = 2          # a match needs at least this many discriminating words
MIN_RATIO = 0.60        # ...covering this share of the shorter title
# A notice must additionally cover this share of the TRACK's own distinctive
# words. Without it, a notice about «تنظيم الهيئة السعودية للبحر الأحمر» matches
# any track whose title happens to contain «الهيئة السعودية», and a notice about
# «المؤسسة العامة للصناعات العسكرية» matches «المؤسسة العامة للري». The subject
# of the notice has to be the track, not merely overlap with it.
MIN_TRACK_COVER = 0.70


def toks(s):
    return {w for w in norm_ar(s).split() if len(w) > 2 and w not in STOP}


def track_editions():
    """{track_id: (arabic title, gazette date or '')} for every track on file."""
    out = {}
    for pat in (os.path.join(ROOT, "sources", "*", "official_source", "*.json"),
                os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json")):
        for p in glob.glob(pat):
            tid = os.path.relpath(p, os.path.join(ROOT, "sources")).split(os.sep)[0]
            if tid in out:
                continue
            try:
                s = json.load(open(p, encoding="utf-8"))
            except (ValueError, OSError):
                continue
            doc = s.get("document")
            if doc:
                out[tid] = (doc, s.get("gazette_publication_date_gregorian") or "")
    return out


def main(index_path):
    if not os.path.isfile(index_path):
        print("no gazette title index at %s" % index_path)
        return 0
    index = json.load(open(index_path, encoding="utf-8"))
    tracks = track_editions()
    dated = {t: d for t, (_a, d) in tracks.items() if d}
    print("gazette pages indexed: %d | tracks on file: %d (%d with an edition date)"
          % (len(index), len(tracks), len(dated)))

    notices = [(uid, v["title"], v.get("date", "")) for uid, v in index.items()
               if v.get("title") and AMENDMENT_RE.search(v["title"])]
    print("amendment-shaped gazette titles: %d" % len(notices))

    T = {tid: (toks(a), d) for tid, (a, d) in tracks.items()}
    at_risk = {}
    for uid, title, ndate in notices:
        nt = toks(title)
        if len(nt) < MIN_SHARED:
            continue
        for tid, (tt, tdate) in T.items():
            if not tt:
                continue
            shared = nt & tt
            if len(shared) < MIN_SHARED:
                continue
            if len(shared) / min(len(nt), len(tt)) < MIN_RATIO:
                continue
            if len(shared) / len(tt) < MIN_TRACK_COVER:
                continue
            # Only a notice published AFTER the edition on file is evidence of
            # staleness. Without a date on either side we cannot tell, and this
            # audit does not guess.
            if not (tdate and ndate) or ndate <= tdate:
                continue
            at_risk.setdefault(tid, []).append((ndate, uid, title))

    print("\ntracks whose edition on file predates a published amendment notice: %d"
          % len(at_risk))
    rows = sorted(at_risk.items(), key=lambda kv: max(n[0] for n in kv[1]), reverse=True)
    for tid, notes in rows:
        held = tracks[tid][1]
        print("\n  %s  (edition on file: %s)" % (tid, held))
        print("    %s" % tracks[tid][0][:96])
        for ndate, uid, title in sorted(notes, reverse=True)[:6]:
            print("      %s  p=%-8s %s" % (ndate, uid, title[:92]))
        if len(notes) > 6:
            print("      ... and %d more" % (len(notes) - 6))

    out = os.path.join(ROOT, "reports", "corpus_currency_audit")
    os.makedirs(out, exist_ok=True)
    json.dump({
        "generated_note": (
            "Currency audit. For every track, every AMENDMENT NOTICE published in the Umm "
            "Al-Qura archive after the edition the corpus holds. An amendment notice is not "
            "a standalone instrument and is deliberately never ingested as a track (gate G1 "
            "drops it); it is evidence ABOUT a track already on file. This report asserts "
            "nothing about the amendment's content -- the notice is not the amended text. It "
            "names the track, the edition date on file, and the gazette page to go read. "
            "Matching is on the notice's SUBJECT: a notice must cover at least "
            "MIN_TRACK_COVER of the track title's distinctive words, which is what stops a "
            "notice about one authority from matching another that merely shares a word."),
        "gazette_pages_indexed": len(index),
        "amendment_notices_found": len(notices),
        "tracks_on_file": len(tracks),
        "tracks_with_edition_date": len(dated),
        "tracks_predating_an_amendment": len(rows),
        "match_thresholds": {"min_shared_words": MIN_SHARED,
                             "min_shorter_title_cover": MIN_RATIO,
                             "min_track_title_cover": MIN_TRACK_COVER},
        "at_risk": [
            {"track_id": tid,
             "title_ar": tracks[tid][0],
             "edition_on_file": tracks[tid][1],
             "amendment_notices": [
                 {"date": d, "url": "https://www.uqn.gov.sa/details?p=%s" % u
                  if not u.startswith("400")
                  else "https://www.uqn.gov.sa/decisions-and-regulations/%s" % u,
                  "title_ar": ti}
                 for d, u, ti in sorted(notes, reverse=True)]}
            for tid, notes in rows],
    }, open(os.path.join(out, "corpus_currency_audit.json"), "w", encoding="utf-8"),
        ensure_ascii=False, indent=1)
    print("\nwrote reports/corpus_currency_audit/corpus_currency_audit.json")
    return rows


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "reports",
        "gazette_ingestion_backlog", "gazette_title_index.json")
    main(p)
