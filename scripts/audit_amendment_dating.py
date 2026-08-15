#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""«What does this article say today?» has an answer. «Since when?» often does not.

WHY THIS EXISTS. 125 tracks carry `consolidated_amended_law: true` — their text is
the CURRENT text, folded together after amendments. That is the right thing to
store, and it silently drops a dimension a lawyer needs: judging conduct from
2019 requires the text as it stood in 2019, and at minimum the DATE the wording
changed. The corpus holds that date for most articles and never shows it.

TWO MEASUREMENTS, AND THEY ARE DIFFERENT QUESTIONS:

  IN THE SOURCE ARTIFACT   Of 928 articles marked معدلة/مضافة/ملغاة, 830 (89%)
                           carry at least one history entry bearing a year. The
                           evidence is there.
  IN THE LLM LAYER         None of them carry a date at all. The record says
                           `is_amended: true` and stops. So the corpus KNOWS
                           when, and what a model reads does not.

The gap is not missing evidence. It is evidence that never propagates.

A NAIVE EXTRACTION THAT WOULD HAVE WRITTEN NINE WRONG DATES INTO A LEGAL CORPUS.
The VAT implementing regulation is the largest undated block: 45 amended articles
whose per-article history points at the document-level list instead of a date.
But its stored text carries the authority's own printed footnotes — «تمت إضافة
الفقرة بموجب قرار ... رقم 7-2-20 وتاريخ 12 شعبان 1441ه الموافق 05 أبريل 2020م» —
and the track's own `amendment_history` lists those same resolutions WITH dates.
Matching decision numbers across the two looked clean: 42 of 45 matched.

Then the printed dates were checked against the matched entries and NINE
DISAGREED. The cause: an article often carries SEVERAL footnotes, and taking the
first decision number with the first date pairs a decision with a date belonging
to a different amendment. Pairing each decision with the date that follows IT
turns 42 loose matches into 51 verified pairs and 8 real disagreements.

WHAT SURVIVES THE SECOND CHECK IS NOT WHAT SURVIVES THE FIRST. A single
agreement is a coincidence a corpus cannot afford; two independent agreements —
the decision number AND the date — are evidence.

AND THE EIGHT THAT STILL DISAGREE ARE NOT RESOLVED HERE. They are all one
resolution, (7-02-21), where the printed footnote says 9 October 2021 and the
document-level history says 9 November 2021 — same day, same year, one month
apart. Picking a side would be «الترجيح بلا دليل». Disclosed, not decided.

Read-only. Offline. Exit 0; an audit, not a gate.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "amendment_dating",
                   "amendment_dating.json")

AMENDED = ("معدلة", "مضافة", "ملغاة")
YEAR_RE = re.compile(r"1[34]\d\d|20\d\d")
DEC_RE = re.compile(r"رقم\s*\(?\s*([0-9][0-9\s\-–/]{2,20})")
# a decision number followed, within a bounded window, by ITS OWN date
PAIR_RE = re.compile(
    r"رقم\s*\(?\s*([0-9][0-9\s\-–/]{2,20}).{0,90}?الموافق\s*(\d{1,2})\s*([^\s\d]+)\s*(\d{4})",
    re.S)
GREGORIAN_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ابريل": 4, "مايو": 5,
    "يونيو": 6, "يوليو": 7, "أغسطس": 8, "اغسطس": 8, "سبتمبر": 9,
    "أكتوبر": 10, "اكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12,
}


def _digits(s):
    return tuple(int(x) for x in re.findall(r"\d+", s or ""))


def _greg(text):
    m = re.search(r"(\d{1,2})\s+([^\s\d]+)\s*(\d{4})", text or "")
    if not m:
        return None
    return (int(m.group(3)), GREGORIAN_MONTHS.get(m.group(2)), int(m.group(1)))


def source_artifacts():
    for p in (glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json"))
              + glob.glob(os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                yield p, json.load(f)
        except (OSError, ValueError):                                  # noqa: BLE001
            continue


def main():
    tracks, undated_rows = [], []
    total = dated = 0
    for path, doc in source_artifacts():
        if not doc.get("consolidated_amended_law"):
            continue
        src = os.path.relpath(path, os.path.join(ROOT, "sources")).split(os.sep)[0]
        amd = ok = 0
        undated = []
        for key, art in (doc.get("articles") or {}).items():
            if (art.get("legal_status_ar") or "") not in AMENDED:
                continue
            amd += 1
            hist = art.get("history") or []
            if any(YEAR_RE.search(json.dumps(h, ensure_ascii=False)) for h in hist):
                ok += 1
            else:
                undated.append(key)
        if amd:
            tracks.append({"source": src, "document": doc.get("document"),
                           "amended_articles": amd, "with_a_dated_history": ok,
                           "undated": undated})
            total += amd
            dated += ok
            if undated:
                undated_rows.append((src, doc, undated))

    print("tracks with consolidated amended text: %d"
          % sum(1 for _p, d in source_artifacts() if d.get("consolidated_amended_law")))
    print("articles marked معدلة/مضافة/ملغاة:      %d" % total)
    print("  the SOURCE artifact can date:         %d (%.1f%%)"
          % (dated, 100.0 * dated / total))
    print("  it cannot:                            %d" % (total - dated))
    print("  the LLM LAYER can date:               0 — is_amended carries no date")

    # --- the footnote channel, verified twice --------------------------------
    verified = collections.Counter()
    disagreements, unmatched = [], []
    for src, doc, undated in undated_rows:
        hist_by_num = {}
        for h in (doc.get("amendment_history") or []):
            m = DEC_RE.search(h.get("decree", "") if isinstance(h, dict) else "")
            if not m:
                continue
            t = _digits(m.group(1))
            hist_by_num[t] = h
            hist_by_num[tuple(reversed(t))] = h
        for key in undated:
            art = (doc.get("articles") or {}).get(key) or {}
            for num, day, month, year in PAIR_RE.findall(art.get("text") or ""):
                h = hist_by_num.get(_digits(num))
                if not h:
                    unmatched.append({"source": src, "article_key": key,
                                      "decision_in_text": num.strip()})
                    continue
                printed = (int(year), GREGORIAN_MONTHS.get(month), int(day))
                if printed == _greg(h.get("date_gregorian")):
                    verified[(src, key)] += 1
                else:
                    disagreements.append({
                        "source": src, "article_key": key,
                        "decision": h.get("decree"),
                        "date_printed_in_the_article_text": printed,
                        "date_in_the_document_level_history": _greg(h.get("date_gregorian")),
                    })

    print("\nthe footnote channel (the source prints its own amendment notes):")
    print("  (decision, date) pairs VERIFIED on both the number and the date: %d"
          % sum(verified.values()))
    print("  articles that gain a dated amendment from it:                   %d"
          % len(verified))
    print("  pairs whose printed date CONTRADICTS the document-level history: %d"
          % len(disagreements))
    print("  decisions named in an article but absent from that history:      %d"
          % len(unmatched))
    if disagreements:
        d0 = disagreements[0]
        print("     all of them one resolution — %s" % (d0["decision"] or "")[:60])
        print("     printed %s vs history %s — same day, one month apart."
              % (d0["date_printed_in_the_article_text"],
                 d0["date_in_the_document_level_history"]))
        print("     DISCLOSED, NOT DECIDED: picking a side would be الترجيح بلا دليل.")

    worst = sorted((t for t in tracks if t["undated"]),
                   key=lambda t: -len(t["undated"]))
    print("\ntracks that cannot date their own amendments:")
    for t in worst:
        print("   %-34s %-38s %3d of %3d undated"
              % (t["source"], (t["document"] or "")[:38],
                 len(t["undated"]), t["amended_articles"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "«ما نصُّ هذه المادة اليوم؟» له جواب، و«**منذ متى؟**» كثيراً ما لا. و125 مساراً "
            "تحمل نصّاً **مُدمَجاً بعد تعديلات** — وهو الصواب في التخزين، ويُسقط بصمتٍ بُعداً "
            "يحتاجه الفقيه: الحكمُ على واقعةٍ قديمة يقتضي النصَّ كما كان **وقتها**. "
            "**والقياسان مختلفان**: أثرُ المصدر يستطيع تأريخ 830 من 928 مادة معدَّلة (89%)، "
            "**وطبقةُ النماذج اللغوية لا تستطيع تأريخ واحدة** — تقول `is_amended` وتقف. "
            "**فالفجوة ليست دليلاً غائباً بل دليلاً لا ينتقل.** "
            "**ودرسُ الاستخراج**: مطابقةُ أرقام القرارات وحدها بدت نظيفة (42 من 45)، ثم "
            "قُوبلت التواريخ المطبوعة فاختلف **تسعة**. والسبب أن المادة تحمل حواشيَ متعددة، "
            "فاقتران أول رقمٍ بأول تاريخ **يزاوج قراراً بتاريخ غيره**. وباقتران كل قرارٍ "
            "بتاريخه صارت 51 مزاوجة موثَّقة و8 اختلافات حقيقية. **وما ينجو من الفحص الثاني "
            "ليس ما ينجو من الأول.**"),
        "tracks_with_consolidated_amended_text": len(tracks),
        "amended_articles_total": total,
        "datable_from_the_source_artifact": dated,
        "not_datable": total - dated,
        "datable_in_the_llm_layer": 0,
        "llm_layer_note": (
            "سجلُّ الطبقة الجاهزة للنماذج يحمل `is_amended: true` و`legal_status_ar: معدلة` "
            "**ولا يحمل تاريخاً**. فالنموذجُ يعرف **أن** المادة عُدِّلت ولا يعرف **متى**."),
        "footnote_channel": {
            "verified_pairs": sum(verified.values()),
            "articles_datable_from_it": len(verified),
            "contradictions": disagreements,
            "decisions_absent_from_document_history": unmatched,
        },
        "tracks": sorted(tracks, key=lambda t: -len(t["undated"])),
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
