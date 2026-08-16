#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is any track this corpus serves as law actually REPEALED?

WHY THIS EXISTS, AND WHY IT IS SEPARATE FROM THE CURRENCY AUDIT. The currency
audit asks whether a track's text has been AMENDED since the edition on file. It
is the right question and it is not this one. An amended text is stale; a
repealed text is not law at all, and serving one as current is the worst thing a
legal corpus can do. The two need different evidence, because a repeal notice in
Umm Al-Qura is written differently from an amendment notice:

    «إلغاء مجلس التنمية السياحي ومجالس التنمية السياحية في المناطق»

That title names the BODY being abolished. It does not name an instrument, it
carries no instrument type word, and NOTHING IN IT distinguishes abolishing a
council from repealing the statute that created it. Only the decision text does
— and in that case it did both, in its second operative clause. So the currency
audit was right to classify it as a lead rather than assert it, and a lead that
nobody reads is a silence. This audit exists to produce the short list that a
human actually reads.

HOW THE LIST IS NARROWED, AND WHY EACH EXCLUSION IS WRITTEN DOWN RATHER THAN
APPLIED SILENTLY. Of 9,448 indexed archive pages, 33 announce an إلغاء in the
title. A title must name every distinctive word of a track's own title, must not
be outranked by a track it names more fully, and then three exclusions apply,
each of which is REPORTED with its reason:

  * the notice repeals a NUMBERED DECISION («إلغاء البند ثانياً من قرار مجلس
    الوزراء رقم (95)») — it repeals that decision, not the Law of the Council of
    Ministers whose title happens to share two words with it;
  * the page IS the track's own source — «قواعد نظر دعاوى إلغاء القرارات» has
    إلغاء in its own name, and a track cannot be evidence that it is repealed;
  * the notice predates the edition on file — it cannot repeal a later text.

THE SELF-PAGE TEST READS PROVENANCE FIELDS ONLY, AND THAT IS NOT A DETAIL. The
first version of this check searched the whole source artifact for gazette URLs.
It then reported the one genuine repeal in the corpus as "the track's own source
page" — because the repeal disclosure written into that artifact quotes the URL
of the page that repealed it. A filter that reads disclosures as provenance lets
a recorded finding erase itself, and would suppress any notice a track's own
caveats happen to cite. So only the fields that DECLARE where the text came from
are read.

WHAT IT CANNOT DO, STATED SO NOBODY READS MORE INTO A CLEAN RESULT. It sees
titles, not decisions: a repeal enacted inside a new instrument's issuing decree
(«ويلغي كل ما يتعارض معه») has no إلغاء in its title and belongs to the
supersession graph's channel, not this one. It sees the ADDRESSABLE archive,
which effectively begins in 2021. And it requires the notice to name the track in
full, so a repeal using a shortened name is invisible to it. A clean run means
"no repeal notice in the addressable archive names a held track in full", which
is a smaller sentence than "nothing this corpus holds is repealed".

Read-only. Offline — it reads only artifacts this corpus already holds. Exit 0;
an audit, not a gate.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                     "gazette_title_index.json")
OUT = os.path.join(ROOT, "reports", "repealed_tracks", "repeal_notice_sweep.json")

ILGHA_RE = re.compile(r"إلغاء|الغاء")
PAGE_ID_RE = re.compile(r"details\?p=(\d+)|decisions-and-regulations/(\d+)")

# The fields that DECLARE where a track's text came from. Deliberately not the
# whole artifact: `known_unresolved_discrepancies` holds disclosures, and a
# disclosure that cites a repealing page must never be read as provenance.
PROVENANCE_FIELDS = ("verification_methodology_note", "legal_basis_ar",
                     "issuing_authority_ar", "source_url", "source_urls",
                     "gazette_url", "official_source_url")


def _currency():
    spec = importlib.util.spec_from_file_location(
        "audit_corpus_currency",
        os.path.join(ROOT, "scripts", "audit_corpus_currency.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _own_pages(artifact_path):
    """Gazette page ids this track DECLARES as its source."""
    try:
        doc = json.load(open(artifact_path, encoding="utf-8"))
    except (OSError, ValueError):                                   # noqa: BLE001
        return set()
    blob = json.dumps({k: doc.get(k) for k in PROVENANCE_FIELDS if k in doc},
                      ensure_ascii=False)
    return {a or b for a, b in PAGE_ID_RE.findall(blob)}


def main():
    m = _currency()
    index = json.load(open(INDEX, encoding="utf-8"))["index"]
    tracks = m.track_editions()
    toks = {tid: (m.toks(a), d, m.instrument_type(a))
            for tid, (a, d, _e, _p) in tracks.items()}
    own = {tid: _own_pages(p) for tid, (_a, _d, _e, p) in tracks.items()}

    titled = [(uid, v["title"], v.get("date", "")) for uid, v in index.items()
              if v.get("title") and ILGHA_RE.search(v["title"])]

    rows = []
    for uid, title, ndate in sorted(titled, key=lambda x: x[2]):
        nt = m.toks(title)
        if len(nt) < m.MIN_SHARED:
            continue
        numbered = bool(m.NUMBERED_DECISION_RE.search(title))
        hits = []
        for tid, (tt, tdate, _ty) in toks.items():
            if not tt:
                continue
            shared = m.shared_words(nt, tt)
            if len(shared) < m.MIN_SHARED:
                continue
            cover = len(shared) / len(tt)
            if cover < m.MIN_TRACK_COVER:
                continue
            hits.append((tid, shared, cover, tdate))
        for tid, shared, cover, tdate in hits:
            if any(other > shared for _t, other, _c, _d in hits):
                continue
            excluded = []
            if numbered:
                excluded.append("the notice repeals a NUMBERED DECISION, not this instrument")
            if uid in own.get(tid, ()):
                excluded.append("this page is the track's OWN declared source")
            if tdate and ndate and ndate <= tdate:
                excluded.append("the notice predates the edition on file (%s <= %s)"
                                % (ndate, tdate))
            rows.append({
                "date": ndate, "page_id": uid, "track_id": tid,
                "title_cover": round(cover, 2), "notice_title_ar": title,
                "url": ("https://www.uqn.gov.sa/details?p=%s" % uid
                        if not uid.startswith("400")
                        else "https://www.uqn.gov.sa/decisions-and-regulations/%s" % uid),
                "excluded_because": excluded,
            })

    # Every إلغاء-titled page that named NO held track is listed too. Twenty-five
    # of the thirty-three land here, and they are not noise: most abolish a body
    # or an instrument this corpus does not hold, and one of them — «إلغاء المادة
    # الخامسة عشرة من تنظيم هيئة المدن والمناطق الاقتصادية الخاصة» — turned out to
    # name the missing PARENT of nine held special-economic-zone tracks. A sweep
    # that printed only its matches would have shown a clean result and hidden that.
    matched_pages = {r["page_id"] for r in rows}
    unmatched = [{"date": d, "page_id": u, "notice_title_ar": t,
                  "url": ("https://www.uqn.gov.sa/details?p=%s" % u
                          if not u.startswith("400")
                          else "https://www.uqn.gov.sa/decisions-and-regulations/%s" % u)}
                 for u, t, d in sorted(titled, key=lambda x: x[2])
                 if u not in matched_pages]

    live = [r for r in rows if not r["excluded_because"]]
    print("gazette pages indexed:            %d" % len(index))
    print("pages whose TITLE announces إلغاء: %d" % len(titled))
    print("naming a held track in full:      %d" % len(rows))
    print("still standing after exclusions:  %d" % len(live))
    print("naming NO held track (listed, not dropped): %d" % len(unmatched))
    for r in rows:
        print("\n%s %s  p=%-9s  %s" % ("READ ME" if not r["excluded_because"] else "excluded",
                                       r["date"], r["page_id"], r["track_id"]))
        print("    %s" % r["notice_title_ar"][:100])
        for x in r["excluded_because"]:
            print("      └ %s" % x)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "**النصُّ المعدَّل متقادم، والنصُّ الملغى ليس نظاماً أصلاً** — والفرق بينهما هو "
            "أسوأ ما يمكن أن يخطئ فيه مستودعٌ قانوني. وقرارُ الإلغاء في الجريدة يُكتب "
            "بخلاف إشعار التعديل: **يسمّي الجهةَ المُلغاة لا الأداة**، ولا يحمل عنوانُه "
            "كلمةَ نوع، **ولا شيء فيه يفرِّق بين إلغاء مجلسٍ وإلغاء تنظيمِه** — والنصُّ "
            "وحده يفرِّق. فمهمّةُ هذا التدقيق أن يُخرج القائمةَ القصيرة **التي يقرؤها "
            "إنسان**. ومن 9,448 صفحة مفهرسة، **33** يعلن عنوانُها إلغاءً، **وكلُّ "
            "استبعادٍ مذكورٌ بسببه** لا مُطبَّقٌ بصمت. **واختبارُ «صفحة المسار نفسه» يقرأ "
            "حقولَ المصدر وحدها**: نسختُه الأولى قرأت الأثر كلَّه فأبلغت عن الإلغاء "
            "الوحيد المُسجَّل بوصفه «صفحة المسار نفسه» — لأن بيانَ الإلغاء المكتوبَ في "
            "الأثر يقتبس رابطَ الصفحة التي ألغته. **ومرشِّحٌ يقرأ الإفصاحات مصدراً يجعل "
            "النتيجةَ المسجَّلة تمحو نفسها.** **وحدُّه معلَن**: يرى العناوين لا القرارات، "
            "فالإلغاءُ المنصوصُ داخل مرسوم إصدار أداةٍ جديدة («ويلغي كل ما يتعارض معه») "
            "لا إلغاءَ في عنوانه، وهو من قناة بيان النسخ لا من هذه."),
        "gazette_pages_indexed": len(index),
        "pages_with_an_ilgha_title": len(titled),
        "naming_a_held_track_in_full": len(rows),
        "standing_after_exclusions": len(live),
        "limits": [
            "titles only — a repeal enacted inside a new instrument's issuing decree "
            "carries no إلغاء in its title and belongs to the supersession graph's channel",
            "the addressable archive effectively begins in 2021",
            "requires the notice to name the track in FULL — a shortened name is invisible",
        ],
        "candidates": rows,
        "ilgha_notices_naming_no_held_track": unmatched,
        "adjudicated_by_hand": [{
            "notice": "إلغاء المادة الخامسة عشرة من تنظيم هيئة المدن والمناطق الاقتصادية الخاصة",
            "page_id": "27296",
            "verdict": "not a repeal of anything this corpus holds — it names a PARENT the corpus lacks",
            "instrument_named": ("تنظيم هيئة المدن والمناطق الاقتصادية الخاصة، الصادر "
                                 "بالأمر الملكي رقم (أ/19) وتاريخ 10/3/1431هـ"),
            "read_from": ("the two royal orders' own gazette pages, which both recite the "
                          "parent's issuing instrument verbatim: p=27296 (أمر ملكي أ/19، "
                          "25/1/1447هـ — repeals article 15 and renumbers, effective from the "
                          "commencement of نظام تملك غير السعوديين للعقار) and p=27458 "
                          "(أمر ملكي أ/76، 19/3/1447هـ — deletes «تحدد فيه مكافآتهم» from "
                          "article 4)"),
            "held_artifacts_naming_it": 20,
            "sez_tracks_with_an_unresolved_parent": 9,
            "why_it_cannot_be_fetched": ("issued 10/3/1431H (2010) — eleven years before the "
                                         "gazette's addressable archive effectively begins, so "
                                         "it is not obtainable through this channel however "
                                         "thoroughly it is swept"),
        }],
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
