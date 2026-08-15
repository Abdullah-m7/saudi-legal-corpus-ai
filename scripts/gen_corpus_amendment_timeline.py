#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Carry «since when?» to the layer that is actually read.

WHY THIS LAYER EXISTS. 125 tracks store CONSOLIDATED text — the wording as it
stands today, after amendments. That is the right thing to store. It costs a
dimension: judging conduct from 2019 needs the text as it stood in 2019, or at
minimum the date the wording changed. The corpus already knows that date for 830
of its 928 amended articles — the evidence sits in each source artifact's
per-article `history`. And the LLM-ready layer, the thing a model actually reads,
carries `is_amended: true` and NO DATE AT ALL.

So the gap was never missing evidence. It was evidence that never propagated.
This layer propagates it, keyed by `record_id`, so a retrieval hit can answer
«متى عُدِّلت هذه المادة؟» from the same identifier it already has.

DERIVED, NOT INVASIVE. The alternative was to add a date field to the LLM records
of 125 tracks, which means editing 125 hand-written generators — a large edit
whose failure mode is a silently wrong date in a legal text. A derived layer
touches nothing, regenerates from the artifacts, and can be validated against
them independently.

THREE THINGS THIS LAYER SAYS, AND THE THIRD IS THE ONE THAT MATTERS:

  dated               the article's own history names an instrument and a date.
  disclosed_conflict  two records in the corpus disagree about the date, and
                      this layer reports BOTH rather than choosing. All eight of
                      these are resolution (7-02-21), where a printed footnote
                      says 9 October 2021 and the document-level history says
                      9 November 2021 — same day, one month apart. Choosing
                      would be «الترجيح بلا دليل».
  undated             the corpus marks the article amended and cannot say when.
                      NAMED, not omitted, because an absent row reads as "never
                      amended" and that is a different — and false — statement.

THE FOOTNOTE CHANNEL, AND WHY IT IS CHECKED TWICE. The VAT implementing
regulation's 45 amended articles carry no dated history, but its stored text
carries the authority's own printed footnotes — «بموجب قرار ... رقم 7-2-20
وتاريخ ... الموافق 05 أبريل 2020م» — and its `amendment_history` lists those same
resolutions with dates. Matching decision NUMBERS alone matched 42 of 45 and NINE
of those pairings were wrong: an article carries several footnotes, so the first
number and the first date belong to different amendments. Each decision is
therefore paired with the date that follows IT, and kept only when the printed
date agrees with the document-level history. One agreement is a coincidence a
legal corpus cannot afford; two independent agreements are evidence.

Read-only over sources/ and data/. Deterministic and idempotent.

Usage:
    python3 scripts/gen_corpus_amendment_timeline.py
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
OUT_DIR = os.path.join(ROOT, "data", "corpus_amendment_timeline")
OUT_PATH = os.path.join(OUT_DIR, "corpus_amendment_timeline.jsonl")
SUMMARY_PATH = os.path.join(OUT_DIR, "corpus_amendment_timeline_summary.json")

SCHEMA_VERSION = "1.0.0"
GENERATED_BY = "scripts/gen_corpus_amendment_timeline.py"

AMENDED_STATUSES = ("معدلة", "مضافة", "ملغاة")
YEAR_RE = re.compile(r"1[34]\d\d|20\d\d")
DEC_RE = re.compile(r"رقم\s*\(?\s*([0-9][0-9\s\-–/]{2,20})")
PAIR_RE = re.compile(
    r"رقم\s*\(?\s*([0-9][0-9\s\-–/]{2,20}).{0,90}?الموافق\s*(\d{1,2})\s*([^\s\d]+)\s*(\d{4})",
    re.S)
GREGORIAN_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ابريل": 4, "مايو": 5,
    "يونيو": 6, "يوليو": 7, "أغسطس": 8, "اغسطس": 8, "سبتمبر": 9,
    "أكتوبر": 10, "اكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12,
}

# The per-article `history` field has seven distinct shapes across the corpus,
# because it was written by different build passes over two years. Read by
# ALIAS rather than by one schema: inventing a migration would rewrite 125
# artifacts to gain nothing this layer cannot get by reading what is there.
# A date written into the note's prose rather than a date field: «... بموجب
# المرسوم الملكي رقم (م/32) بتاريخ 10 / 8 / 1400 هـ». Several build passes wrote
# it this way, and refusing to read it would leave the layer reporting an
# "amendment" with no date — the one thing this layer exists to prevent.
_HIJRI_IN_TEXT_RE = re.compile(
    r"(?:و?بتاريخ|وتاريخ)\s*(\d{1,2})\s*[/\-]\s*(\d{1,2})\s*[/\-]\s*(1[34]\d\d)")

INSTRUMENT_KEYS = ("decree", "instrument", "decree_note")
HIJRI_KEYS = ("date_hijri", "decreeDate")
GREGORIAN_KEYS = ("gregorianDecreeDate", "date_gregorian")
NOTE_KEYS = ("note", "description", "effect_ar")


def _digits(s):
    return tuple(int(x) for x in re.findall(r"\d+", s or ""))


def _greg_tuple(text):
    m = re.search(r"(\d{1,2})\s+([^\s\d]+)\s*(\d{4})", text or "")
    if not m:
        return None
    return (int(m.group(3)), GREGORIAN_MONTHS.get(m.group(2)), int(m.group(1)))


def _first(entry, keys):
    for k in keys:
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _amendments_from_history(history):
    """Dated amendments an article's own history states. Entries with no date at
    all are skipped: many are prior-text snapshots labelled اصلية, which are not
    amendments and must not be counted as undated ones."""
    out = []
    for h in history or []:
        if not isinstance(h, dict):
            continue
        blob = json.dumps(h, ensure_ascii=False)
        if not YEAR_RE.search(blob):
            continue
        hijri = _first(h, HIJRI_KEYS)
        greg = _first(h, GREGORIAN_KEYS)
        read_from = "date_field"
        if not (hijri or greg):
            m = _HIJRI_IN_TEXT_RE.search(re.sub(r"\s+", " ", blob))
            if m:
                hijri = "%d/%d/%s" % (int(m.group(1)), int(m.group(2)), m.group(3))
                read_from = "parsed_from_the_notes_own_prose"
            else:
                # No date anywhere in this entry, only a year somewhere in its
                # prose. Recording it as a dated amendment would be a lie of
                # shape; it is dropped and the article falls through to undated.
                continue
        out.append({
            "instrument_ar": _first(h, INSTRUMENT_KEYS),
            "date_hijri": hijri,
            "date_gregorian": greg,
            "date_read_from": read_from,
            "note_ar": _first(h, NOTE_KEYS),
            "evidence": "per_article_history_in_the_source_artifact",
        })
    return out


def _footnote_amendments(article_text, amendment_history):
    """Amendments read from the source's own printed footnotes, kept only when
    the printed date agrees with the document-level history. Returns
    (verified, conflicts)."""
    by_number = {}
    for h in amendment_history or []:
        if not isinstance(h, dict):
            continue
        m = DEC_RE.search(h.get("decree") or "")
        if not m:
            continue
        t = _digits(m.group(1))
        by_number[t] = h
        by_number[tuple(reversed(t))] = h
    verified, conflicts = [], []
    for num, day, month, year in PAIR_RE.findall(article_text or ""):
        h = by_number.get(_digits(num))
        if not h:
            continue
        printed = (int(year), GREGORIAN_MONTHS.get(month), int(day))
        recorded = _greg_tuple(h.get("date_gregorian"))
        if printed == recorded:
            verified.append({
                "instrument_ar": h.get("decree"),
                "date_hijri": h.get("date_hijri"),
                "date_gregorian": h.get("date_gregorian"),
                "date_read_from": "date_field",
                "note_ar": h.get("note"),
                "evidence": ("printed_footnote_matched_to_the_document_level_history_"
                             "on_BOTH_the_decision_number_and_the_date"),
            })
        else:
            conflicts.append({
                "instrument_ar": h.get("decree"),
                "date_printed_in_the_article_text": "%04d-%02d-%02d" % printed
                if all(printed) else None,
                "date_in_the_document_level_history": h.get("date_gregorian"),
                "note_ar": ("المصدرُ يقول تاريخين لقرارٍ واحد: الحاشيةُ المطبوعة داخل "
                            "نصّ المادة، وقائمةُ تعديلات الوثيقة. **يُعرضان معاً ولا "
                            "يُرجَّح أحدهما** — الترجيح بلا دليل ممنوع."),
            })
    return verified, conflicts


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_rows():
    registry = _load(REGISTRY_PATH)
    rows, unjoinable = [], []
    for track in registry.get("tracks", []):
        data_path = (track.get("language_layers", {}).get("arabic") or {}).get("data_path")
        source_paths = [p for p in track.get("data_paths", [])
                        if "/official_source/" in p]
        if not data_path or not source_paths:
            continue
        full_llm = os.path.join(ROOT, data_path)
        full_src = os.path.join(ROOT, source_paths[0])
        if not (os.path.exists(full_llm) and os.path.exists(full_src)):
            continue
        source = _load(full_src)
        if not source.get("consolidated_amended_law"):
            continue
        articles = source.get("articles") or {}
        history_doc = source.get("amendment_history") or []
        for rec in _load(full_llm).get("records", []):
            key = rec.get("article_key")
            art = articles.get(key)
            if art is None:
                if (rec.get("legal_status_ar") or "") in AMENDED_STATUSES:
                    unjoinable.append({"track_id": track["track_id"],
                                       "record_id": rec.get("record_id"),
                                       "article_key": key})
                continue
            if (art.get("legal_status_ar") or "") not in AMENDED_STATUSES:
                continue
            amendments = _amendments_from_history(art.get("history"))
            conflicts = []
            if not amendments:
                amendments, conflicts = _footnote_amendments(
                    art.get("text"), history_doc)
            if amendments:
                status = "dated"
                note = ("التعديلاتُ أدناه مؤرَّخةٌ بدليلٍ من أثر المصدر نفسه؛ "
                        "و«منذ متى؟» له جوابٌ لهذه المادة.")
            elif conflicts:
                status = "disclosed_conflict"
                note = ("المستودعُ يحمل تاريخين متعارضين لهذا التعديل، **ويعرضهما "
                        "معاً ولا يرجّح**. و«منذ متى؟» **لا يُجاب هنا بتاريخٍ واحد**.")
            else:
                status = "undated"
                note = ("**المستودعُ يقول إن هذه المادة عُدِّلت ولا يستطيع أن يقول "
                        "متى.** يُذكر هذا صراحةً لأن غياب السطر يُقرأ «لم تُعدَّل»، "
                        "وهي عبارةٌ أخرى، وكاذبة.")
            rows.append({
                "record_id": rec.get("record_id"),
                "track_id": track["track_id"],
                "article_key": key,
                "article_number": rec.get("article_number"),
                "law_id": rec.get("law_id"),
                "law_component": rec.get("law_component"),
                "legal_status_ar": art.get("legal_status_ar"),
                "dating_status": status,
                "amendments": amendments,
                "conflicting_dates": conflicts,
                "since_when_note_ar": note,
            })
    rows.sort(key=lambda r: (r["track_id"], r["article_number"] or 0,
                             r["record_id"] or ""))
    return rows, unjoinable


def main() -> int:
    rows, unjoinable = build_rows()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")

    by_status = collections.Counter(r["dating_status"] for r in rows)
    by_evidence = collections.Counter(
        a["evidence"] for r in rows for a in r["amendments"] if a.get("evidence"))
    undated_by_track = collections.Counter(
        r["track_id"] for r in rows if r["dating_status"] == "undated")

    summary = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "generated_from": ("sources/*/official_source/*.json (per-article history, "
                           "amendment_history and the printed footnotes inside the "
                           "stored article text) joined to the Arabic LLM-ready "
                           "layer by article_key, so every row carries the same "
                           "record_id retrieval already uses"),
        "purpose_ar": (
            "**«ما نصُّ هذه المادة اليوم؟» له جواب، و«منذ متى؟» لم يكن له.** 125 مساراً "
            "تحمل نصّاً مُدمَجاً بعد التعديلات — وهو الصواب في التخزين — والطبقةُ التي "
            "يقرأها النموذج تقول `is_amended: true` **ولا تحمل تاريخاً**. والدليلُ موجودٌ "
            "في آثار المصادر منذ البداية؛ **الفجوةُ أنه لا ينتقل**. هذه الطبقة تنقله، "
            "**مفتاحُها `record_id`** نفسه الذي يستعمله الاسترجاع."),
        "total_rows": len(rows),
        "by_dating_status": dict(by_status),
        "by_evidence": dict(by_evidence),
        "counting_note_ar": (
            "**رقمُ هذه الطبقة ليس رقمَ تدقيق التأريخ، والفرقُ مقصود.** التدقيق يعدّ المواد "
            "التي **يظهر في سجلّها سنة** (830)؛ وهذه الطبقة تعدّ المواد التي لها **تاريخُ "
            "تعديلٍ فعلي** (852): فتُسقط المدخلات التي فيها سنةٌ عابرة بلا تاريخ — **تسجيلُها "
            "تعديلاً مؤرَّخاً كذبٌ في الشكل** — وتضيف تواريخَ مقروءةً من نثر الحاشية نفسها "
            "ومن الحواشي المطبوعة الموثَّقة مرّتين. **المعياران مختلفان، والأدقُّ هو هذا.**"),
        "undated_by_track": dict(undated_by_track.most_common()),
        "records_marked_amended_that_could_not_be_joined": unjoinable,
        "reading_rules_ar": {
            "dated": "التعديلاتُ مؤرَّخةٌ بدليلٍ من أثر المصدر.",
            "disclosed_conflict": ("تاريخان متعارضان في المستودع، **يُعرضان ولا "
                                    "يُرجَّح بينهما**."),
            "undated": ("عُدِّلت المادة ولا يُعرف متى. **مذكورةٌ صراحةً**: غيابُ "
                        "السطر يُقرأ «لم تُعدَّل»، وهي عبارةٌ أخرى وكاذبة."),
        },
        "known_limitations_ar": [
            ("لا تحمل هذه الطبقة **النصَّ كما كان قبل التعديل** إلا حيث سجّله أثرُ "
             "المصدر؛ فهي تجيب «متى تغيّر» لا «ماذا كان»."),
            ("التعديلاتُ المؤرَّخة على مستوى الوثيقة لا تُنسب إلى موادَّ بعينها ما لم "
             "يقل المصدرُ ذلك بنفسه — **والنسبةُ بلا نصٍّ ترجيحٌ بلا دليل**."),
        ],
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote %s" % os.path.relpath(OUT_PATH, ROOT))
    print("  rows: %d  %s" % (len(rows), dict(by_status)))
    print("  evidence: %s" % dict(by_evidence))
    print("  unjoinable amended records: %d" % len(unjoinable))
    return 0


if __name__ == "__main__":
    sys.exit(main())
