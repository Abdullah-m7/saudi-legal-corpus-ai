#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One provision stored twice means another provision is not stored at all.

The text-quality audit found nine cases of two articles in one instrument
carrying identical text. Most are the source repeating itself, which is a fact
about the gazette and not a defect. ONE is something else entirely, and this
script fixes it: both members of the pair carry THE SAME ARTICLE LABEL, so the
instrument's own numbering says they are one provision — and the slot that
should hold a different provision holds a copy instead.

That is the most dangerous shape a defect can take in a corpus meant to be read
by a model. Nothing looks wrong. The article count is right, the numbering has
no hole, every validator passes, and a question about the duplicated slot
returns a confident answer that belongs to a different article.

  telecommunications_regulation, articles 45 and 46
      Both hold «يلتزم مقدم الخدمة ذي البنية التحتية بالمحافظة على سرية بيانات
      البنية التحتية الحرجة ...» and both are labelled «المادة الخامسة والأربعون».
      The ministry's own published PDF (mcit.gov.sa, «اللائحة التنفيذية لنظام
      الاتصالات وتقنية المعلومات») settles which is which: that text is article
      FORTY-SIX. Article forty-five is a different provision entirely, on sharing
      infrastructure sites, and the corpus does not hold it. The regulation
      itself confirms the two are distinct — article fifty refers to «الطلبات
      الواردة في المادتين (45) الخامسة والأربعين و(46) السادسة والأربعين».

  sharia_procedure/regulation, records 300 and 301
      Both hold «للخصم في الدعاوى التجارية استجواب خصمه مباشرة تحت إشراف
      القاضي.» under the same label «٣/١٠٤», and this script REMOVED one of them
      until that track's own validator refused the change: it asserts an expected
      set of five duplicate labels, «٣/١٠٤» among them, because the official MOJ
      PDF carries the provision twice. The track was built from that PDF, two
      genuine portal redundancies were already removed to match it, and these
      five were kept deliberately. The removal was reverted.

      Recorded because the lesson is the point: an identical-text pair is
      evidence of a question, never of an answer. The same shape meant a lost
      provision in one track and a faithful transcription in another, and only
      the official source could tell them apart.

WHY THE RECOVERED TEXT IS NOT WRITTEN BACK

Article forty-five was located, in full, in the ministry's PDF. It is not
restored here, and that is deliberate. That file's text layer carries the
lam-alef transposition this corpus has already verified and documented as
originating in the official PDFs themselves — «االتصاالت» for «الاتصالات» — and
on top of it the extractor reorders parenthesised numbers («خالل ( )30ثالثين»)
and detaches commas from the words they follow. Producing readable Arabic from
that requires three separate judgment calls per sentence, and a reading arrived
at by judgment is not the official text however plausible it looks.

So the provision is set aside rather than guessed: the false record is removed,
the gap is declared through the corpus's own mechanism, the disclosure names the
file and quotes the opening words verbatim as that file encodes them, and a
human can finish it. «الترجيح بلا دليل ممنوع» applies to reconstruction exactly
as it applies to citation.

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

# Each entry names a pair the audit found, the record to drop, and the evidence
# that decided which one is wrong. Nothing here is inferred at run time: the
# decision was made by reading the official source, and the script only carries
# it out.
CASES = [
    {
        "track": "telecommunications_regulation",
        "component": "law",
        "drop_key": "telecommunications_regulation_art_045",
        "keeps_key": "telecommunications_regulation_art_046",
        "declare_missing": 45,
        "evidence": (
            "الملف الرسمي المنشور على موقع وزارة الاتصالات وتقنية المعلومات "
            "(mcit.gov.sa/sites/default/files/2026-03/اللائحةالتنفيذية لنظام الاتصالات وتقنية "
            "المعلومات.pdf) يفصل المادتين: نصّ «سرية بيانات البنية التحتية الحرجة» هو **المادة "
            "السادسة والأربعون**، والمادة الخامسة والأربعون حكمٌ آخر في مشاركة مواقع التمديدات "
            "بين مقدمي الخدمة. وتؤكد اللائحة ذلك بنفسها: المادة الخمسون تحيل إلى «الطلبات "
            "الواردة في المادتين (45) الخامسة والأربعين و(46) السادسة والأربعين»."),
        "recovered_opening_verbatim_from_that_file": (
            "المادة الخامسة واألربعون\n"
            ".1على مقدم الخدمة ذي البنية التحتية عند رغبته في مشاركة مقدم خدمة ذي بنية تحتية "
            "آخر في مواقع التمديدات أن يتقدم بطلب لمقدم الخدمة ذي البنية التحتية اآلخر متضمنا "
            "بيان ومقدار الحاجة للمشاركة ،وإذا تعذر الوصول إلى اتفاق خالل ( )30ثالثين يوما ..."),
        "disclosure_key": "telecommunications_regulation_article_45_not_recovered",
        "disclosure": (
            "**المادة الخامسة والأربعون غير محفوظة في هذا المسار.** كان المستودع يحمل نصّ المادة "
            "السادسة والأربعين مرتين — تحت المفتاحين (45) و(46) وبالعنوان نفسه «المادة الخامسة "
            "والأربعون» — فبدا العدد مكتملا (108 مادة) والترقيم بلا ثغرة، **وكان سؤالٌ عن المادة "
            "الخامسة والأربعين يُجاب بنصّ مادةٍ أخرى**. حُذف السجل الخاطئ وأُعلنت الثغرة.\n\n"
            "والنصّ الرسمي للمادة الخامسة والأربعين موجودٌ ومحدَّد الموضع في ملف الوزارة المذكور "
            "أعلاه (الفصل الخامس: استخدام العقارات)، **ولم يُنقل إلى هنا**: طبقة النصّ في ذلك "
            "الملف تحمل خلل انقلاب لام-ألف الذي أثبت هذا المستودع أنه في ملفات الجهات الرسمية "
            "نفسها («االتصاالت» بدل «الاتصالات»)، ويضاف إليه أن المستخرج يعكس مواضع الأرقام بين "
            "قوسين ويفصل الفواصل عمّا قبلها. **وإخراجُ عربيةٍ مقروءة من ذلك يقتضي ترجيحاتٍ ثلاثة "
            "في كل جملة، والقراءة المُرجَّحة ليست النصّ الرسمي مهما بدت معقولة.** فتُرك الحكم "
            "لنظرٍ بشري، ولم يُخمَّن حرف."),
    },
]


def artifact_path(track, component):
    pats = [os.path.join(ROOT, "sources", track, "official_source", "*.json")]
    if component:
        pats.insert(0, os.path.join(ROOT, "sources", track, component, "official_source", "*.json"))
    for p in pats:
        hits = glob.glob(p)
        if hits:
            return hits[0]
    return None


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
    for case in CASES:
        path = artifact_path(case["track"], case["component"])
        if not path:
            skipped.append({**{k: case[k] for k in ("track", "drop_key")},
                            "reason": "artifact not found"})
            continue
        doc = json.load(open(path, encoding="utf-8"))
        arts = doc.get("articles") or {}
        if case["drop_key"] not in arts:
            skipped.append({"track": case["track"], "drop_key": case["drop_key"],
                            "reason": "already removed"})
            continue
        if arts.get(case["drop_key"], {}).get("text") != arts.get(case["keeps_key"], {}).get("text"):
            skipped.append({"track": case["track"], "drop_key": case["drop_key"],
                            "reason": "the two records no longer carry identical text — "
                                      "re-adjudicate before removing anything"})
            continue

        if args.apply:
            del arts[case["drop_key"]]
            if isinstance(doc.get("article_count"), int):
                doc["article_count"] = len(arts)
            if case["declare_missing"] is not None:
                miss = sorted(set(doc.get("missing_article_numbers") or [])
                              | {case["declare_missing"]})
                doc["missing_article_numbers"] = miss
            disc = doc.setdefault("known_unresolved_discrepancies", [])
            if not any(isinstance(d, dict) and d.get("article_key") == case["disclosure_key"]
                       for d in disc):
                disc.append({"article_key": case["disclosure_key"],
                             "description": case["disclosure"]})
            save(path, doc)

        done.append({"track": case["track"], "removed_record": case["drop_key"],
                     "kept_record": case["keeps_key"],
                     "declared_missing_article": case["declare_missing"],
                     "evidence": case["evidence"],
                     "recovered_text_not_written_back":
                         case["recovered_opening_verbatim_from_that_file"]})

    report = {
        "generated_note": (
            "Two of the nine duplicate-text findings were duplicated RECORDS, not repeated "
            "provisions: in each pair both members carry the same article label, so the "
            "instrument's own numbering says they are one provision — and where the pair is "
            "consecutive, the slot that should hold a different provision holds a copy instead. "
            "That defect is invisible to every count-based check: the article total is right, "
            "the numbering has no hole, and a question about the duplicated slot returns a "
            "confident answer belonging to another article. Article 45 of the Telecom "
            "Implementing Regulation was located in the ministry's own published PDF but is NOT "
            "written back, because that file's text layer carries the lam-alef transposition "
            "this corpus has verified as originating in official PDFs, and reading it requires "
            "judgment calls a transcription may not make."),
        "applied": bool(args.apply),
        "cases_actioned": done,
        "cases_skipped": skipped,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "duplicated_record_repair.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("%s %d duplicated records; %d skipped"
          % ("removed" if args.apply else "would remove", len(done), len(skipped)))
    for d in done:
        print("   %-34s drop %-40s keep %s"
              % (d["track"][:34], d["removed_record"][:40], d["kept_record"]))
    for s in skipped:
        print("   SKIP %-30s %s" % (s.get("drop_key", "")[:30], s["reason"]))
    print("wrote reports/corpus_text_quality_audit/duplicated_record_repair.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
