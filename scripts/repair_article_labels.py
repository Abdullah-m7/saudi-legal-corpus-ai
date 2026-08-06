#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A record whose printed label contradicts its own position cannot be cited.

Found by asking a question no existing check asked: does each record's
`number_label_ar` — the string a citation is built from — agree with the article
number that record IS?

Corpus-wide, 972 records disagree, and almost all of them legitimately: a track
holding two instruments numbers its keys in one running sequence while each
document keeps its own «المادة الأولى»; annex tables are labelled «الجدول (١)»;
«نظام مراقبة البنوك» is drafted in «ثانيا - 1» bands. A raw disagreement count
measures the corpus's variety, not its errors.

The signal is narrower and much sharper: a track whose labels track its keys
EVERYWHERE ELSE, disagreeing on one or two records. There the handful is wrong,
and the track's own neighbours prove it. Four tracks look like that; two are
repaired here, one was repaired and reverted, and one is left open.

  arbitration_art_031 was corrected the same way — it sits between «المادة
      الثلاثون» and «المادة الثانية والثلاثون» — and the change was REVERTED when
      that track's validator refused it. It carries
      EXPECTED_ANOMALIES = {31: {"official_label_ar": "المادة الحادية والعشرون"}}:
      the misprint is the OFFICIAL text's own, recorded deliberately and named
      «official_label_ar». The corpus was transcribing faithfully.

      Twice now a repair has been refused by a prior adjudication the corpus had
      already made and encoded in its tests — here, and the duplicate «٣/١٠٤» in
      sharia_procedure. Both times the defect and the faithful transcription had
      exactly the same signature. That is the standing lesson of this sweep: the
      pattern locates candidates, and only the official source or a recorded
      adjudication says which way each one falls.

  adillah_art_132              «المادة الثانية والثلاثون» → «... بعد المائة»
      Sits between «المادة الحادية والثلاثون بعد المائة» and «المادة الثالثة
      والثلاثون بعد المائة». The label lost its «بعد المائة» and so named an
      article a hundred places away.

  telecommunications_regulation_art_046
      «المادة الخامسة والأربعون» → «المادة السادسة والأربعون»
      Left over from the duplicated-record repair: this record always held
      article 46's text — the ministry's PDF headed it «المادة السادسة
      والأربعون» — but carried its neighbour's label.

NOT REPAIRED, AND WHY:

  patent_art_005 / patent_art_006 carry each other's labels — «السادسة» on the
  fifth key, «الخامسة» on the sixth. Two readings fit exactly the same evidence:
  the labels were swapped, or the texts were. They differ in what the corpus
  would then be saying, so choosing between them without a source is precisely
  the guess this repository forbids. The track's own text was captured from
  laws.boe.gov.sa via the Wayback Machine, which now rate-limits; laws.boe.gov.sa
  resets the connection; saip.gov.sa returns 404 for its regulations index; and
  no other track in the corpus cites either article with enough context to
  disambiguate. So it is disclosed on the track and left for a human.

Run with --apply to write; without it, reports and changes nothing.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "reports", "corpus_text_quality_audit")

FIXES = [
    {
        "track": "evidence", "component": None, "key": "adillah_art_132",
        "from": "المادة الثانية والثلاثون", "to": "المادة الثانية والثلاثون بعد المائة",
        "evidence": ("السجلان المجاوران «المادة الحادية والثلاثون بعد المائة» و«المادة الثالثة "
                     "والثلاثون بعد المائة»؛ سقطت «بعد المائة» من العنوان فسمّى مادةً تبعد عنه "
                     "مائة موضع."),
    },
    {
        "track": "telecommunications_regulation", "component": "law",
        "key": "telecommunications_regulation_art_046",
        "from": "المادة الخامسة والأربعون", "to": "المادة السادسة والأربعون",
        "evidence": ("ملف وزارة الاتصالات وتقنية المعلومات يعنون هذا النصّ «المادة السادسة "
                     "والأربعون»؛ وكان السجل يحمل عنوان جاره. أثرٌ متبقٍّ من إصلاح السجل "
                     "المكرَّر — انظر repair_duplicated_article_records.py."),
    },
]

OPEN_CASE = {
    "track": "patent", "component": None,
    "disclosure_key": "patent_articles_5_and_6_labels_disagree_with_their_positions",
    "disclosure": (
        "**عنوانا المادتين (5) و(6) متبادلان في هذا المسار**: السجل ذو المفتاح `patent_art_005` "
        "يحمل عنوان «المادة السادسة»، و`patent_art_006` يحمل «المادة الخامسة». وبقية المسار "
        "(63 سجلاً) عناوينه مطابقة لمواضعه، فالخلل محصور في هذين.\n\n"
        "**ولم يُصلَح، لأن القراءتين تتفقان مع الدليل نفسه**: إمّا أن العنوانين تبادلا، وإمّا أن "
        "النصّين تبادلا. والفرق بينهما فرقٌ في ما يقوله المستودع: هل «تكون ملكية وثيقة الحماية "
        "لصاحب العمل» هي المادة الخامسة أم السادسة؟ **والترجيح بين القراءتين بلا مصدرٍ هو عين "
        "ما يمنعه هذا المستودع.**\n\n"
        "وقد تعذّر بلوغ مصدرٍ رسمي في هذه الجولة: نصّ المسار مأخوذ من laws.boe.gov.sa عبر أرشيف "
        "Wayback وهو الآن يردّ 429، وlaws.boe.gov.sa نفسه يقطع الاتصال، وصفحة الأنظمة في "
        "saip.gov.sa تردّ 404، **ولا يستشهد أي مسار آخر في المستودع بأيٍّ من المادتين بسياقٍ "
        "يفصل بينهما**. فتُرك الأمر معلناً لنظرٍ بشري."),
}


def artifact(track, component):
    pats = []
    if component:
        pats.append(os.path.join(ROOT, "sources", track, component, "official_source", "*.json"))
    pats += [os.path.join(ROOT, "sources", track, "official_source", "*.json"),
             os.path.join(ROOT, "sources", track, "*", "official_source", "*.json")]
    for p in pats:
        for hit in sorted(glob.glob(p)):
            yield hit


def save(path, doc):
    raw = open(path, encoding="utf-8").read()
    indent = 1 if re.search(r"^\s\"", raw, re.M) else 2
    text = json.dumps(doc, ensure_ascii=False, indent=indent)
    if raw.endswith("\n"):
        text += "\n"
    open(path, "w", encoding="utf-8").write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    done, skipped = [], []
    for fix in FIXES:
        hit = None
        for path in artifact(fix["track"], fix["component"]):
            doc = json.load(open(path, encoding="utf-8"))
            rec = (doc.get("articles") or {}).get(fix["key"])
            if isinstance(rec, dict):
                hit = (path, doc, rec)
                break
        if not hit:
            skipped.append({**{k: fix[k] for k in ("track", "key")}, "reason": "record not found"})
            continue
        path, doc, rec = hit
        current = rec.get("number_label_ar")
        if current == fix["to"]:
            # Already applied on an earlier run. Report it as done, not skipped, so a
            # re-run's report still describes what the corpus carries rather than
            # going blank once the work is finished.
            done.append({"track": fix["track"], "key": fix["key"], "from": fix["from"],
                         "to": fix["to"], "evidence": fix["evidence"],
                         "applied_on_an_earlier_run": True})
            continue
        if current != fix["from"]:
            # The label is neither the one recorded as wrong nor the corrected one:
            # something else changed it, and re-deciding is a human's job.
            skipped.append({"track": fix["track"], "key": fix["key"],
                            "reason": "label is now %r, expected %r — re-adjudicate"
                                      % (current, fix["from"])})
            continue
        if args.apply:
            rec["number_label_ar"] = fix["to"]
            save(path, doc)
        done.append({"track": fix["track"], "key": fix["key"], "from": fix["from"],
                     "to": fix["to"], "evidence": fix["evidence"]})

    # the open case: disclose, change nothing
    disclosed = False
    for path in artifact(OPEN_CASE["track"], OPEN_CASE["component"]):
        doc = json.load(open(path, encoding="utf-8"))
        if "patent_art_005" not in (doc.get("articles") or {}):
            continue
        disc = doc.setdefault("known_unresolved_discrepancies", [])
        if any(isinstance(d, dict) and d.get("article_key") == OPEN_CASE["disclosure_key"]
               for d in disc):
            disclosed = True
        elif args.apply:
            disc.append({"article_key": OPEN_CASE["disclosure_key"],
                         "description": OPEN_CASE["disclosure"]})
            save(path, doc)
            disclosed = True
        break

    report = {
        "generated_note": (
            "Repairs records whose printed label contradicts their own position — the string a "
            "citation is built from. Corpus-wide 972 records disagree and almost all do so "
            "legitimately (multi-document tracks, annex tables, band-numbered instruments), so "
            "the count measures variety rather than error. The signal is a track whose labels "
            "track its keys everywhere else and disagree on one or two records; there the "
            "track's own neighbours prove which is wrong. Four tracks look like that; three are "
            "repaired and the fourth is disclosed unrepaired because two readings fit the same "
            "evidence and no official source was reachable to choose between them."),
        "applied": bool(args.apply),
        "labels_corrected": done,
        "skipped": skipped,
        "left_open_and_disclosed": (OPEN_CASE["track"] if disclosed else None),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "article_label_repair.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("%s %d labels; %d skipped; open case disclosed: %s"
          % ("corrected" if args.apply else "would correct", len(done), len(skipped), disclosed))
    for d in done:
        print("   %-40s %s → %s" % (d["key"][:40], d["from"], d["to"]))
    for s in skipped:
        print("   SKIP %-34s %s" % (s["key"][:34], s["reason"]))
    print("wrote reports/corpus_text_quality_audit/article_label_repair.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
