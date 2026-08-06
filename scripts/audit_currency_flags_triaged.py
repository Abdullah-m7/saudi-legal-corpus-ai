#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Which of the currency warnings mean the corpus is actually behind?

The freshness manifest flags 50 tracks with `published_amendment_after_edition_
on_file`: the gazette carried an amendment notice naming this instrument, dated
after the edition the corpus holds. That flag is honest and deliberately weak —
it says a notice exists, not that the stored text is stale, because the notice
is not the amended text and nothing may be concluded from its existence alone.

Weak is right for a flag and useless for a reader. Fifty warnings that cannot be
told apart are read as fifty problems or, worse, as none. This triages them
against what each track already says about ITSELF:

  ALREADY CONSOLIDATED THROUGH IT — the track records an amendment in its own
  `amendment_history` dated at or after the newest notice, or declares itself
  consolidated through a decree issued later. The corpus is not behind; the
  notice is one it has already absorbed. Nothing to do but say so.

  BEHIND, OR CANNOT BE SHOWN OTHERWISE — the track records no amendment that
  reaches the notice. This is the list that deserves a reader's attention, and
  the only one worth calling a currency risk.

The distinction is drawn from the artifacts, never from a reading of the notice:
this script never claims to know what an amendment SAYS. It only asks whether
the corpus's own record already reaches past the date of the newest notice.

Read-only; writes only its own report.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "corpus_freshness_manifest",
                        "corpus_freshness_manifest.json")
OUT_DIR = os.path.join(ROOT, "reports", "corpus_currency_audit")

DATE_RE = re.compile(r"most recently (\d{4}-\d{2}-\d{2})")
EDITION_RE = re.compile(r"edition on file (\d{4}-\d{2}-\d{2})")
# Any ISO date anywhere in the track's own amendment record.
ANY_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
# Hijri years appear in decree citations («M/223 1447H», «وتاريخ 14/2/1439هـ»);
# a Hijri year alone is enough to place an amendment on the timeline to within a
# year, which is all this comparison needs.
HIJRI_YEAR = re.compile(r"\b(1[34][0-9]{2})\s*(?:هـ|ه\b|H\b)")


def artifact_paths(track_id):
    """sources/<id>/... and sources/<base>/<component>/... — «aml_law» lives at
    sources/aml/law/, and looking only for sources/aml_law/ finds nothing at all,
    which would silently report every component-nested track as unexaminable."""
    direct = glob.glob(os.path.join(ROOT, "sources", track_id, "official_source", "*.json"))
    if direct:
        return direct
    for cut in (1, 2, 3):
        parts = track_id.rsplit("_", cut)
        if len(parts) != cut + 1:
            continue
        base, comp = parts[0], "_".join(parts[1:])
        hit = glob.glob(os.path.join(ROOT, "sources", base, comp, "official_source", "*.json"))
        if hit:
            return hit
    hit = glob.glob(os.path.join(ROOT, "sources", track_id, "*", "official_source", "*.json"))
    if hit:
        return hit
    # last resort: the longest source directory that prefixes this track id
    for d in sorted(glob.glob(os.path.join(ROOT, "sources", "*")), key=len, reverse=True):
        base = os.path.basename(d)
        if track_id.startswith(base + "_"):
            comp = track_id[len(base) + 1:]
            hit = glob.glob(os.path.join(d, comp, "official_source", "*.json"))
            if hit:
                return hit
    return []


def hijri_to_gregorian_year(hy):
    """Hijri year -> the Gregorian year it mostly falls in. Approximate by
    construction and used only to compare two dates a year or more apart."""
    return int(round(int(hy) * 0.970224 + 621.5774))


# The ONLY fields that assert what the stored text incorporates. Scanning the
# whole artifact was tried first and is worthless: it picks up the gazette
# publication date, the verification date, dates inside source URLs — and then
# declares 48 of 50 tracks consolidated, which flatters the corpus instead of
# measuring it.
AMENDMENT_FIELDS = ("amendment_history", "consolidated_amended_law", "decree",
                    "decree_date_hijri", "legal_status_ar", "amendments",
                    "consolidation_note", "amendment_note")
# A methodology note discusses many things; only its sentences ABOUT amendments
# make a claim about how current the text is. Scoping to the fields alone was
# tried and is too narrow — «نظام الاستثمار التعديني» records its amendment
# coverage in prose («Royal Decree M/12 (8/1/1442)») and nowhere else, and
# excluding the note reported it as behind on the strength of a field it does not
# use. A date in a sentence about amendments is a claim about amendment coverage;
# a date elsewhere in the note is when the document was published or checked.
AMENDMENT_SENTENCE = re.compile(
    r"[^.\n]*(?:تعديل|تعديلات|معدلة|معدل|مُعدَّل|amend|consolidat|"
    r"مرسوم\s+ملكي|Royal\s+Decree|م/\d+)[^.\n]*\.?")


def latest_amendment_reach(doc):
    """The newest date the track's own AMENDMENT record claims to incorporate.

    Restricted to the fields that make that claim. A date found anywhere else in
    the artifact says when the document was published or checked, not how far its
    text is current, and treating the two alike turns this audit into a rubber
    stamp."""
    parts = []
    for f in AMENDMENT_FIELDS:
        v = doc.get(f)
        if v:
            parts.append(json.dumps(v, ensure_ascii=False))
    note = doc.get("verification_methodology_note") or ""
    parts.extend(AMENDMENT_SENTENCE.findall(note))
    blob = " ".join(parts)

    best = None
    for m in ANY_DATE.finditer(blob):
        d = m.group(0)
        if "1000" < d[:4] < "2100" and (best is None or d > best):
            best = d
    for m in HIJRI_YEAR.finditer(blob):
        g = "%d-12-31" % hijri_to_gregorian_year(m.group(1))
        if best is None or g > best:
            best = g
    return best


def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    flagged = [t for t in manifest["tracks"]
               if t.get("published_amendment_after_edition_on_file")]

    consolidated, behind, unexaminable = [], [], []
    for t in flagged:
        tid = t["track_id"]
        pointer = t.get("published_amendment_pointer") or ""
        m = DATE_RE.search(pointer)
        notice = m.group(1) if m else None
        edition = (EDITION_RE.search(pointer).group(1)
                   if EDITION_RE.search(pointer) else None)
        paths = artifact_paths(tid)
        if not paths or not notice:
            unexaminable.append({"track_id": tid, "notice_date": notice,
                                 "reason": "no artifact found" if not paths
                                           else "no dated notice in the pointer"})
            continue
        doc = json.load(open(paths[0], encoding="utf-8"))
        reach = latest_amendment_reach(doc)
        row = {"track_id": tid, "edition_on_file": edition, "newest_notice": notice,
               "track_record_reaches": reach,
               "artifact": os.path.relpath(paths[0], ROOT),
               "amendment_history_entries": len(doc.get("amendment_history") or []),
               "declares_consolidated": bool(doc.get("consolidated_amended_law"))}
        if reach and reach >= notice:
            consolidated.append(row)
        else:
            behind.append(row)

    report = {
        "generated_note": (
            "Triages the freshness manifest's 50 «published_amendment_after_edition_on_file» "
            "warnings against what each track already says about itself. The flag is "
            "deliberately weak — a gazette notice exists naming this instrument, dated after "
            "the edition on file — and weak is right for a flag and useless for a reader: fifty "
            "warnings that cannot be told apart are read as fifty problems or as none. A track "
            "whose own amendment record already reaches past the newest notice is not behind; "
            "the rest are the list that deserves attention. Nothing here claims to know what an "
            "amendment SAYS — only whether the corpus's own record reaches past its date."),
        "flagged_by_the_manifest": len(flagged),
        "already_consolidated_through_the_newest_notice": len(consolidated),
        "behind_or_not_shown_otherwise": len(behind),
        "unexaminable": len(unexaminable),
        "behind": sorted(behind, key=lambda r: r["newest_notice"], reverse=True),
        "consolidated": sorted(consolidated, key=lambda r: r["newest_notice"], reverse=True),
        "unexaminable_entries": unexaminable,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "currency_flags_triaged.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)

    print("flagged %d | already consolidated through the notice %d | behind %d | unexaminable %d"
          % (len(flagged), len(consolidated), len(behind), len(unexaminable)))
    print("\nBEHIND — the corpus's own record does not reach the newest notice:")
    for r in report["behind"][:40]:
        print("   %-46s edition %s  notice %s  reaches %s"
              % (r["track_id"][:46], r["edition_on_file"], r["newest_notice"],
                 r["track_record_reaches"]))
    for u in unexaminable[:10]:
        print("   UNEXAMINABLE %-40s %s" % (u["track_id"][:40], u["reason"]))
    print("\nwrote reports/corpus_currency_audit/currency_flags_triaged.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
