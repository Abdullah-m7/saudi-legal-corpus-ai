#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does the stored text say what the source says — and does it say it once?

The corpus already audits two narrow text questions: encoding damage, and the
same instrument held under two names. This audit asks the broader ones that sit
between "the file parses" and "the law is right", each phrased so that a finding
is a defect a reader could point at rather than a statistic.

  1. STRUCTURE THAT LEAKED INTO A PROVISION.
     A chapter heading, an annex marker, or the next article's own heading
     absorbed into the tail of the previous article. The provision then reads as
     saying something it does not say, and no count-based check can see it.

  2. NUMBERING THE SOURCE SKIPS.
     Every track records its own gaps in `missing_article_numbers`. This
     re-derives them from the stored records and reports any track whose
     declared gaps and actual gaps disagree — a declaration that has drifted from
     the thing it declares is worse than none.

  3. TEXT REPEATED INSIDE ONE INSTRUMENT.
     Two articles of the same instrument carrying identical text is either a real
     duplication in the gazette (which should be disclosed) or a segmentation
     fault that copied one article twice (which should be fixed). Both need
     naming; neither is visible to a per-article check.

  4. A DECLARED COMPLETENESS THAT THE TEXT CONTRADICTS.
     `text_complete: true` on a record whose text is a bare fragment — under a
     handful of words, or ending mid-clause — is the corpus asserting something
     about itself that its own content refutes.

  5. A LABEL THAT CONTRADICTS ITS OWN POSITION.
     `number_label_ar` is the string a citation is built from. Where it names a
     different article than the record IS, every quotation of that record is
     misattributed. Corpus-wide, 972 records disagree and almost all do so
     legitimately — a track holding two instruments runs one key sequence while
     each document keeps its own «المادة الأولى», annex tables are «الجدول (١)»,
     «نظام مراقبة البنوك» is drafted in «ثانيا - 1» bands — so the raw count
     measures the corpus's variety, not its errors. What is reported instead is
     a track whose labels track its keys EVERYWHERE ELSE and disagree on one or
     two records: there the track's own neighbours say which is wrong.

  6. DISCLOSURES THAT POINT AT NOTHING.
     Every entry in `known_unresolved_discrepancies` names an `article_key`.
     Where that key is neither a real article of the track nor one of the
     track-level keys the corpus uses by convention, the disclosure cannot be
     acted on, and an unactionable disclosure is decoration.

Read-only over the corpus; writes only its own report. Exit status is always 0 —
this measures, it does not gate.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gazette_autoingest import parse_ordinal  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "reports", "corpus_text_quality_audit")

# 1 — structure that leaked. These are headings, not provisions; a provision that
# ENDS on one has absorbed it from the document that follows.
TRAILING_STRUCTURE = re.compile(
    r"(?:الباب|الفصل|القسم|الجزء|الملحق|الملاحق|الجدول|المرفق)\s+"
    r"(?:الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|"
    r"الحادي|رقم|\(?\s*[0-9٠-٩]{1,3}\s*\)?)\s*[:：]?\s*$")
# A heading of the NEXT article left at the end of this one. The COLON is
# required and the demonstrative is excluded, because without both this pattern
# flags the commonest sentence ending in Saudi regulatory drafting — «... المنصوص
# عليها في الفقرة (1) من هذه المادة.» — and reports 300-odd well-formed articles
# as damaged. A heading ends on a colon; a cross-reference ends on a full stop.
TRAILING_ARTICLE_HEAD = re.compile(
    r"(?<![ء-ي])ا?لمادة\s*(?:\(\s*[0-9٠-٩]{1,4}\s*\)|[^\s:()]{2,20})\s*[:：]\s*$")
CROSS_REFERENCE_TAIL = re.compile(
    r"(?:هذه|تلك|هذا|من|في|وفق|وفقا|بموجب|إلى|الى)\s+"
    r"ا?ل?(?:مادة|باب|فصل|قسم|جزء|ملحق|جدول|مرفق)")

# 4 — a fragment that cannot be a whole provision.
# A repeal marker is the one short text that IS complete: «(ملغاة)» is the whole
# of what the source says about that article, and flagging it as a fragment says
# the corpus is missing words the source never printed.
REPEAL_MARKER = re.compile(r"^\(?\s*(?:ملغاة|ملغى|محذوفة|محذوف)\s*\)?\.?$")
FRAGMENT_WORDS = 4
MID_CLAUSE_END = re.compile(r"(?:\b(?:و|أو|في|من|على|إلى|عن|مع|بين|أن|التي|الذي)\s*)$")

# 5 — Which disclosures are article-bound?
#
# The first version of this check tried to recognise TRACK-level keys by a list
# of substrings and to call everything else article-bound. That is guessing, and
# it guessed wrong 1,349 times: «..._title_resembles_existing_track» is a
# track-level note and was reported as naming a missing article. The test here
# is structural instead. A key is article-bound only if it is SHAPED like this
# corpus's article keys — «<something>_art_017» — and such a key is a real
# finding only when the number it names is absent from the track. Every other
# key is a track-level note by construction and cannot dangle.
ARTICLE_BOUND_KEY = re.compile(r"_art_(\d{1,4})\b")

# 5 — a track must agree with itself this many times before a stray disagreement
# means anything, and disagree at most this many times before it is simply
# numbered differently rather than wrong.
LABEL_AGREE_FLOOR = 10
LABEL_MAX_ANOMALIES = 3


def norm(s):
    s = re.sub(r"[ً-ْـ]", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def tracks():
    """Every source artifact, under BOTH layouts the corpus uses.

    449 tracks keep their artifact at sources/<id>/official_source/, and the
    older ones nest it one level deeper under the component —
    sources/<id>/law/official_source/. Globbing only the first layout examines
    449 of 735 tracks and reports the result as if it covered the corpus, which
    is the kind of silent under-coverage this audit exists to catch."""
    seen = set()
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            if path in seen:
                continue
            seen.add(path)
            rel = os.path.relpath(path, os.path.join(ROOT, "sources"))
            tid = rel.split(os.sep)[0]
            component = rel.split(os.sep)[-3] if rel.count(os.sep) == 3 else None
            name = "%s/%s" % (tid, component) if component else tid
            try:
                yield name, json.load(open(path, encoding="utf-8"))
            except Exception as exc:                               # noqa: BLE001
                yield name, {"_unreadable": str(exc)}


# An implementing regulation often numbers its provisions after the LAW articles
# they implement, not in a sequence of its own: «اللائحة التنفيذية لنظام مكافحة
# غسل الأموال» holds 25 provisions numbered 1, 2, 5, 7, 8, … 49, and «اللائحة
# التنفيذية للنظام الصحي» starts at 2. Those are not gaps — the regulation simply
# has nothing to say about the law articles in between, and both artifacts state
# that outright («excluded_law_articles_not_recovered»). Deriving a gap list from
# 1..max is meaningless for that family, and reporting it as drift accuses the
# corpus of losing text it never had.
#
# The family is recognised STRUCTURALLY, by fields the artifacts already carry —
# never by the track's name or a guess about its type.
LAW_KEYED_FIELDS = ("base_law", "parent_law_key", "parent_law_article_range",
                    "article_numbers_present", "confirmed_covered_law_articles")


def law_keyed_numbering(src):
    return any(src.get(f) for f in LAW_KEYED_FIELDS)


def label_face_value(label):
    """The article number a label NAMES, or None if it does not name one."""
    if not label:
        return None
    m = re.search(r"\(?\s*([0-9\u0660-\u0669]{1,4})\s*\)?\s*$", label.strip())
    if m:
        try:
            return int(m.group(1).translate(str.maketrans("\u0660\u0661\u0662\u0663\u0664"
                                                          "\u0665\u0666\u0667\u0668\u0669",
                                                          "0123456789")))
        except ValueError:
            pass
    m = re.match(r"^\s*ا?لمادة\s*\(?\s*(.+?)\s*\)?\s*:?\s*$", label.strip())
    if m:
        return parse_ordinal(m.group(1))
    return None


def normalise_articles(arts):
    """Two artifacts map an article number straight to its text instead of to a
    record («gtpl», «gtpl_regulation»). Wrap those so every check below sees one
    shape; the wrapper carries no `text_complete`, so check 4 stays silent on
    them rather than inventing an assertion they never made."""
    if not isinstance(arts, dict) or not arts:
        return {}
    out = {}
    for key, val in arts.items():
        if isinstance(val, dict):
            out[key] = val
        elif isinstance(val, str):
            try:
                num = int(str(key).strip())
            except ValueError:
                num = None
            out[key] = {"text": val, "article_number": num}
    return out


def main():
    leaked, gap_drift, repeated, false_complete, dangling = [], [], [], [], []
    mislabelled = []
    n_tracks = n_records = 0

    for tid, src in tracks():
        if "_unreadable" in src:
            dangling.append({"track_id": tid, "problem": "artifact unreadable",
                             "detail": src["_unreadable"]})
            continue
        arts = normalise_articles(src.get("articles"))
        if not arts:
            continue
        n_tracks += 1
        n_records += len(arts)

        # 1 — structure leaked into a provision's tail
        for key, a in sorted(arts.items()):
            t = norm(a.get("text", ""))
            if not t:
                continue
            tail = t[-60:]
            if CROSS_REFERENCE_TAIL.search(tail):
                # «... المبينة في المرفق (1)» points AT a structure; it is not one.
                continue
            m = TRAILING_STRUCTURE.search(t) or TRAILING_ARTICLE_HEAD.search(t)
            if m:
                leaked.append({"track_id": tid, "article_key": key,
                               "trailing": t[-70:], "chars": len(t)})

        # 2 — declared gaps vs derived gaps
        nums = sorted(a.get("article_number") for a in arts.values()
                      if isinstance(a.get("article_number"), int))
        if not law_keyed_numbering(src):
            derived = [n for n in range(1, (max(nums) if nums else 0) + 1) if n not in set(nums)]
            declared = src.get("missing_article_numbers") or []
            if sorted(declared) != derived:
                gap_drift.append({"track_id": tid, "declared": sorted(declared),
                                  "derived_from_stored_records": derived})

        # 3 — the same text twice inside one instrument
        seen = defaultdict(list)
        for key, a in sorted(arts.items()):
            t = norm(a.get("text", ""))
            if len(t) >= 60:
                seen[t].append(key)
        for t, keys in seen.items():
            if len(keys) > 1:
                repeated.append({"track_id": tid, "article_keys": keys,
                                 "chars": len(t), "text_head": t[:110]})

        # 4 — text_complete asserted over a fragment
        for key, a in sorted(arts.items()):
            if not a.get("text_complete", False):
                continue
            t = norm(a.get("text", ""))
            if REPEAL_MARKER.match(t):
                continue
            words = len(t.split())
            if words <= FRAGMENT_WORDS or MID_CLAUSE_END.search(t):
                false_complete.append({"track_id": tid, "article_key": key,
                                       "words": words, "text": t[:120]})

        # 5 — a label that names a different article than the record is
        agree = disagree = 0
        anomalies = []
        for key, a in sorted(arts.items()):
            m = re.search(r"_art_(\d{1,4})$", key)
            if not m:
                continue
            face = label_face_value(a.get("number_label_ar"))
            if face is None:
                continue
            if face == int(m.group(1)):
                agree += 1
            else:
                disagree += 1
                anomalies.append({"article_key": key,
                                  "number_label_ar": a.get("number_label_ar"),
                                  "position_says": int(m.group(1)), "label_says": face})
        if agree >= LABEL_AGREE_FLOOR and 0 < disagree <= LABEL_MAX_ANOMALIES:
            mislabelled.append({"track_id": tid, "labels_agreeing": agree,
                                "labels_disagreeing": disagree, "records": anomalies})

        # 6 — a disclosure naming an article the track does not have
        keys = set(arts)
        have = {n for n in nums}
        for d in src.get("known_unresolved_discrepancies", []) or []:
            # Older artifacts write a discrepancy as a bare sentence rather than
            # as {article_key, description}. A free-text note names no article by
            # construction, so it cannot dangle and is not a finding here.
            if not isinstance(d, dict):
                continue
            k = d.get("article_key", "")
            if k in keys:
                continue
            m = ARTICLE_BOUND_KEY.search(k)
            if not m or int(m.group(1)) in have:
                continue
            dangling.append({"track_id": tid, "article_key": k,
                             "article_number_named": int(m.group(1)),
                             "description_head": (d.get("description") or "")[:110]})

    report = {
        "generated_note": (
            "Asks the text questions that sit between 'the file parses' and 'the law is right'. "
            "Each finding is phrased as a defect a reader could point at: a chapter heading "
            "absorbed into a provision's tail, a declared numbering gap that the stored records "
            "contradict, one instrument carrying the same text twice, a `text_complete: true` "
            "over a fragment, a disclosure naming an article that does not exist. None of these "
            "is visible to a count-based validator, and all of them change what a model reading "
            "the corpus would say. Read-only; writes only this report."),
        "tracks_examined": n_tracks,
        "records_examined": n_records,
        "1_structure_leaked_into_a_provision": {
            "count": len(leaked),
            "by_track": Counter(x["track_id"] for x in leaked).most_common(20),
            "entries": leaked[:120],
        },
        "2_declared_numbering_gaps_that_the_records_contradict": {
            "count": len(gap_drift), "entries": gap_drift[:120],
        },
        "3_same_text_held_twice_in_one_instrument": {
            "count": len(repeated),
            "by_track": Counter(x["track_id"] for x in repeated).most_common(20),
            "entries": repeated[:80],
        },
        "4_text_complete_asserted_over_a_fragment": {
            "count": len(false_complete),
            "by_track": Counter(x["track_id"] for x in false_complete).most_common(20),
            "entries": false_complete[:120],
        },
        "5_labels_that_contradict_their_own_position": {
            "count": sum(len(m["records"]) for m in mislabelled),
            "tracks": len(mislabelled),
            "note": ("Reported only for a track whose labels agree with its keys at least "
                     "%d times and disagree at most %d — elsewhere a disagreement means the "
                     "track simply numbers differently (two instruments in one track, annex "
                     "tables, band-numbered instruments), not that it is wrong."
                     % (LABEL_AGREE_FLOOR, LABEL_MAX_ANOMALIES)),
            "entries": mislabelled,
        },
        "6_disclosures_naming_an_article_that_does_not_exist": {
            "count": len(dangling), "entries": dangling[:120],
        },
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "corpus_text_quality_audit.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)

    print("tracks %d / records %d" % (n_tracks, n_records))
    print("  1 structure leaked into a provision      %d" % len(leaked))
    print("  2 declared gaps contradicted by records  %d" % len(gap_drift))
    print("  3 same text twice in one instrument      %d" % len(repeated))
    print("  4 text_complete over a fragment          %d" % len(false_complete))
    print("  5 label contradicts its own position    %d in %d track(s)"
          % (sum(len(m["records"]) for m in mislabelled), len(mislabelled)))
    print("  6 disclosures naming no such article     %d" % len(dangling))
    print("\nwrote reports/corpus_text_quality_audit/corpus_text_quality_audit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
