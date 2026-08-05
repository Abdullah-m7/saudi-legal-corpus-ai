#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What is still missing, and is every absence accounted for?

The corpus holds 735 instruments drawn from an Umm Al-Qura archive of 8,997
addressable pages. The interesting number is not 735; it is the 8,262 pages that
did not become tracks, and whether each of them is absent for a REASON THE
CORPUS CAN STATE, or merely absent.

An unexplained absence and a justified exclusion look identical from outside,
and only one of them is honest. This audit forces every uncovered page into one
of a small set of accounted-for classes, each decided by a test over the page's
own title and date — never by assumption — and reports what is left over. The
leftovers are the real backlog: the pages the corpus has no answer for.

Classes, in the order they are tried (first match wins, so the order is part of
the claim):

  covered              a track already cites this page id
  covered_by_title     no track cites the page, but a track carries that exact
                       instrument name. The corpus holds the instrument from
                       another source (the BOE portal, the MOJ portal), which is
                       coverage — but it is WEAKER evidence than a cited id and
                       is reported apart from it, because an identical name over
                       a different edition is exactly how a superseded text
                       hides. Every member of this class is a currency question
                       to answer, not a gap to fill
  not_an_instrument    the title is news, an appointment, a statement, an
                       obituary, a session summary — the archive is a gazette,
                       and most of a gazette is not legislation
  amendment            the title marks itself as a change to something else
                       («تعديل ...», «إلغاء ...»). Amendments belong in the
                       amended instrument's own history, not as separate tracks
  draft                the title marks itself «مشروع»
  gated               the ingestion pipeline reached this page and refused it;
                       the blocking gate is quoted
  unreached           none of the above — the page has never been looked at

That last class is the honest bottom line, and it is what a reader should be
told. Everything else in the archive is either in the corpus or excluded for a
stated reason.

Read-only. Writes only its own report.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

TITLE_INDEX = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                           "gazette_title_index.json")
OUT_DIR = os.path.join(ROOT, "reports", "corpus_coverage_accounting")

# A gazette page that is legislation opens with the kind of word legislation
# opens with. This vocabulary is the ingestion pipeline's own G1 list, imported
# rather than restated so the two cannot drift apart.
from gazette_autoingest import LEGAL_PREFIX, is_amendment_shaped, DRAFT_RE  # noqa: E402

# News and administrative notices, identified by how the CMS titles them. Each
# pattern was read off the archive, not guessed; the count each one claims is
# reported so an over-broad pattern is visible rather than silent.
NOT_INSTRUMENT = [
    ("appointment", re.compile(r"^(?:تعيين|ترقية|إعفاء|تكليف|نقل)\s")),
    ("royal_order_personal", re.compile(r"^أمر\s+ملكي\b")),
    ("statement_or_news", re.compile(
        r"^(?:المملكة|خادم الحرمين|سمو|صاحب السمو|ولي العهد|بيان|تصريح|كلمة|إعلان|"
        r"وفاة|تعزية|برقية|استقبال|زيارة|انطلاق|اختتام|توقيع|بحث|مباحثات)\b")),
    ("council_session", re.compile(r"^(?:مجلس الوزراء|مجلس الشورى)\s+(?:يعقد|يوافق|يقر|يستكمل)")),
    ("approval_notice", re.compile(r"^الموافقة\s+على\b")),
    ("call_or_tender", re.compile(r"^(?:إعلان|مناقصة|منافسة|دعوة|مزايدة)\b")),
]


def registry_page_ids():
    """Every gazette page id the corpus's own artifacts cite."""
    ids = set()
    pat = re.compile(r"(?:details\?p=|decisions-and-regulations/)(\d+)")
    for path in glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json")):
        ids.update(pat.findall(open(path, encoding="utf-8").read()))
    return ids


def gated_pages():
    """Pages the pipeline reached and refused, with the gate that refused them.

    Read from the triage files the ingestion runs leave behind, if any are
    committed; absent those, this class is simply empty and its members fall
    through to `unreached`, which understates the corpus's diligence rather than
    overstating it — the safe direction."""
    out = {}
    for path in sorted(glob.glob(os.path.join(
            ROOT, "reports", "gazette_ingestion_backlog", "*.json"))):
        try:
            blob = json.load(open(path, encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        rejected = blob.get("rejected") if isinstance(blob, dict) else None
        for r in rejected or []:
            if isinstance(r, dict) and r.get("uid"):
                gates = r.get("blocking_gates") or []
                if isinstance(gates, str):
                    try:
                        gates = json.loads(gates)
                    except ValueError:
                        gates = [gates]
                out[str(r["uid"])] = gates[:2]
    return out


def registry_titles_normalised():
    """Every instrument name the corpus holds, normalised for comparison."""
    names = {}
    for path in glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json")):
        try:
            doc = json.load(open(path, encoding="utf-8")).get("document", "")
        except Exception:                                          # noqa: BLE001
            continue
        if doc:
            names[norm_title(doc)] = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return names


def norm_title(s):
    s = re.sub(r"[ً-ْـ]", "", s or "")
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"[^\w؀-ۿ]+", " ", s).strip()


def classify(uid, title, covered, gated, titles):
    if uid in covered:
        return "covered", None
    hit = titles.get(norm_title(title))
    if hit:
        return "covered_by_title", hit
    for name, rx in NOT_INSTRUMENT:
        if rx.search(title):
            return "not_an_instrument", name
    if DRAFT_RE.match(title):
        return "draft", None
    if is_amendment_shaped(title):
        return "amendment", None
    if uid in gated:
        return "gated", gated[uid]
    if not LEGAL_PREFIX.match(title):
        return "not_an_instrument", "title_does_not_open_with_an_instrument_word"
    return "unreached", None


def main():
    idx = json.load(open(TITLE_INDEX, encoding="utf-8"))["index"]
    covered = registry_page_ids()
    gated = gated_pages()
    titles = registry_titles_normalised()

    classes = Counter()
    subreasons = Counter()
    by_title = []
    unreached = []
    for uid, meta in idx.items():
        title = (meta.get("title") or "").strip()
        cls, why = classify(str(uid), title, covered, gated, titles)
        classes[cls] += 1
        if cls == "not_an_instrument" and why:
            subreasons[why] += 1
        if cls == "covered_by_title":
            by_title.append({"uid": uid, "title": title, "date": meta.get("date"),
                             "held_as_track": why})
        if cls == "unreached":
            unreached.append({"uid": uid, "title": title, "date": meta.get("date")})

    unreached.sort(key=lambda r: r.get("date") or "", reverse=True)

    report = {
        "generated_note": (
            "Forces every page in the Umm Al-Qura archive into one accounted-for class, so an "
            "unexplained absence cannot hide among justified exclusions. The classes are tried "
            "in a fixed order and the first match wins, which makes the order part of the claim: "
            "a page is only called unreached after it has failed to be covered, failed to look "
            "like news, failed to mark itself an amendment or a draft, was not refused by a "
            "recorded gate, AND opens with an instrument word. The `gated` class is read from "
            "committed triage reports only; where no triage is committed those pages fall "
            "through into `unreached`, which understates the work done rather than overstating "
            "it. Read-only."),
        "archive_pages": len(idx),
        "tracks_in_corpus": len(glob.glob(os.path.join(ROOT, "sources", "*", "official_source"))),
        "gazette_page_ids_cited_by_the_corpus": len(covered),
        "classes": dict(classes.most_common()),
        "not_an_instrument_breakdown": dict(subreasons.most_common()),
        "covered_by_title_not_by_cited_page": {
            "count": len(by_title),
            "note": ("The corpus holds an instrument of exactly this name, but no track cites "
                     "this gazette page. That is coverage from another source — or the same "
                     "name over a LATER edition the corpus has not read, which is how a "
                     "superseded text hides in plain sight. Each of these is a currency "
                     "question, and the currency audit is where it gets answered."),
            "entries": sorted(by_title, key=lambda r: r.get("date") or "", reverse=True)[:300],
        },
        "unreached_count": len(unreached),
        "unreached_most_recent_first": unreached[:400],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "corpus_coverage_accounting.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)

    for k, v in classes.most_common():
        print("  %-20s %5d" % (k, v))
    print("\nwrote reports/corpus_coverage_accounting/corpus_coverage_accounting.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
