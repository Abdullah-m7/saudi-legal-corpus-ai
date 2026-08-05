#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write what the text-integrity audit found into the tracks it found it in.

The audit produces a report. What the corpus ASSERTS lives in the source
artifacts, so a finding that stays in a report changes nothing about what a
reader is told. Three kinds of finding are written here, each into the track it
concerns and each saying only what was measured:

  1. ENCODING DAMAGE — the exact count of records in this track carrying the
     signature of Arabic PDF text extraction, and a plain statement that the
     spelling of some words does not match what the issuing body published. No
     character is corrected: «ال» is itself an Arabic word, both the negative
     particle and the definite article, so rewriting it wherever it appears
     would corrupt sound text.

  2. THE SAME INSTRUMENT TWICE — the corpus holds two tracks whose titles name
     the same subject and the same instrument type. Each is told about the
     other, with both dates, so a reader meets the pair rather than one half of
     it. Which one is in force is NOT decided here: an edition being later is
     not proof the earlier one was repealed, and «نظام التأمينات الاجتماعية»
     exists twice precisely because both remain valid for different populations.

  3. A LAW AND ITS IMPLEMENTING TEXT THAT NEARLY COINCIDE — where an
     implementing regulation restates its law almost article for article, the
     figure is disclosed in both, because someone opening the regulation
     expecting implementing detail should know how much of it is the law again.

Idempotent: an existing entry of each kind is rewritten, and one whose cause has
cleared is withdrawn. Each artifact is written back in its own JSON formatting.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "reports", "corpus_text_integrity_audit",
                      "corpus_text_integrity_audit.json")

DAMAGE_SUFFIX = "_pdf_extraction_letter_transposition"
PAIR_SUFFIX = "_same_instrument_held_twice"
RESTATE_SUFFIX = "_implementing_text_restates_its_law"

DAMAGE_TEXT = (
    "**تحفُّظ على سلامة النص**: يحمل {n} سجلاً من {total} في هذا المسار أثر خللٍ في استخراج "
    "النص العربي من ملف PDF: انقلاب رابطة لام-ألف وتبادل مواضع حروفٍ متجاورة — «االطلاع» "
    "موضع «الاطلاع»، و«اإلدارية» موضع «الإدارية»، و«ال يجوز» موضع «لا يجوز»، و«الالئحة» موضع "
    "«اللائحة»، و«محاية» موضع «حماية». وهو خلل في **النقل** لا في المصدر: الجهة نشرت النص "
    "سليماً. **ولم يُصحَّح حرف واحد**، لأن التصحيح بقاعدةٍ غير مأمون: «ال» كلمة عربية قائمة "
    "بذاتها — أداة نفي وأداة تعريف — فقلبها إلى «لا» حيثما وردت يُفسد نصوصاً سليمة. المُفصَح "
    "عنه أن **رسم بعض الكلمات في هذه السجلات لا يطابق ما نشرته الجهة**، وإن بقي المعنى "
    "مقروءاً؛ فلا يصح النسخ الحرفي منها قبل المقابلة بالمصدر الرسمي. ويُرفع هذا التحفُّظ "
    "بإعادة قراءة النص من مصدره واستبداله حرفياً. (رصدَه scripts/audit_corpus_text_integrity.py)")

PAIR_TEXT = (
    "**المستودع يحمل هذه الأداة مرتين**: يوجد مسارٌ آخر عنوانه يسمّي **الموضوع نفسه والنوع "
    "نفسه** — «{other_title}» (المسار `{other_id}`، {other_records} سجلاً، تاريخه {other_date}) "
    "بينما تاريخ هذا المسار {self_date}، والنصّان يتقاطعان في {overlap}% من مفرداتهما. "
    "**ولا يُقرَّر هنا أيّهما النافذ**: تأخُّرُ طبعةٍ ليس دليلاً على إلغاء ما قبلها — ففي هذا "
    "المستودع «نظام التأمينات الاجتماعية» مرتان لأن الطبعتين معاً ساريتان لفئتين مختلفتين. "
    "المُفصَح عنه أن **من يقرأ هذا المسار وحده يقرأ نصفَ الصورة**، وأن الحسم يكون بمراجعة "
    "المصدرين الرسميين. (رصدَه scripts/audit_corpus_text_integrity.py)")

RESTATE_TEXT = (
    "**تطابق شبه تام مع {kind}**: يتقاطع نص هذا المسار مع المسار `{other_id}` («{other_title}») "
    "في **{overlap}%** من مفرداته، و{same}/{tot} من مواده متطابقة تطابقاً شبه تام. وهذا ما "
    "نشرته الجريدة في الصفحتين كلتيهما، ولم يُنسَخ نصٌّ من أحدهما إلى الآخر. المُفصَح عنه أن "
    "**من يفتح اللائحة التنفيذية باحثاً عن تفصيلٍ زائدٍ على النظام سيجد النظام نفسه في أغلبه**، "
    "فليراجع المسارين معاً. (رصدَه scripts/audit_corpus_text_integrity.py)")


RESTATE_FLOOR = 0.75  # below this, a regulation restating its law is unremarkable


def save(path, raw, data):
    """Write back in the file's own formatting; the artifacts are not uniformly
    formatted and reserialising them all one way would bury a one-entry change."""
    for indent in (2, 1):
        for tail in ("", "\n"):
            if json.dumps(json.loads(raw), ensure_ascii=False, indent=indent) + tail == raw:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(json.dumps(data, ensure_ascii=False, indent=indent) + tail)
                return True
    print("SKIPPED (unrecognised formatting)  %s" % os.path.relpath(path, ROOT))
    return False


def put(path, key, description, wanted):
    """Add, update or withdraw one entry. Returns 'added'|'updated'|'same'|'withdrawn'|None."""
    raw = open(path, encoding="utf-8").read()
    src = json.loads(raw)
    disc = src.get("known_unresolved_discrepancies")
    if disc is None:
        if not wanted:
            return None
        disc = src["known_unresolved_discrepancies"] = []
    existing = next((d for d in disc
                     if isinstance(d, dict) and d.get("article_key") == key), None)
    if not wanted:
        if existing is None:
            return None
        disc.remove(existing)
        save(path, raw, src)
        return "withdrawn"
    if existing is not None:
        if existing.get("description") == description:
            return "same"
        existing["description"] = description
        save(path, raw, src)
        return "updated"
    disc.append({"article_key": key, "description": description})
    save(path, raw, src)
    return "added"


def main():
    rep = json.load(open(REPORT, encoding="utf-8"))
    tally = {}

    def note(r):
        if r:
            tally[r] = tally.get(r, 0) + 1

    damaged = {}
    for row in rep["encoding_damage"]:
        damaged[row["track_id"]] = row
        note(put(os.path.join(ROOT, row["source_artifact"]),
                 row["track_id"] + DAMAGE_SUFFIX,
                 DAMAGE_TEXT.format(n=row["records_affected"], total=row["total_records"]),
                 True))

    paired, restating = set(), set()
    for pr in rep["same_text_under_two_names"]:
        a, b = pr["tracks"]
        if pr["verdict"] == "A_same_instrument_twice":
            for x, y in ((a, b), (b, a)):
                paired.add(x["track_id"])
                note(put(os.path.join(ROOT, x["source_artifact"]),
                         x["track_id"] + PAIR_SUFFIX,
                         PAIR_TEXT.format(
                             other_title=y["title_ar"], other_id=y["track_id"],
                             other_records=y["records"],
                             other_date=y["gazette_gregorian"] or y["decree_date_hijri"] or "غير مثبت",
                             self_date=x["gazette_gregorian"] or x["decree_date_hijri"] or "غير مثبت",
                             overlap=int(round(pr["content_overlap"] * 100))),
                         True))
        elif (pr["verdict"] == "B_instrument_and_its_implementing_text"
              and pr["content_overlap"] >= RESTATE_FLOOR):
            for x, y in ((a, b), (b, a)):
                restating.add(x["track_id"])
                note(put(os.path.join(ROOT, x["source_artifact"]),
                         x["track_id"] + RESTATE_SUFFIX,
                         RESTATE_TEXT.format(
                             kind="لائحته التنفيذية" if x["instrument_type"] == "LAW" else "نظامه",
                             other_id=y["track_id"], other_title=y["title_ar"],
                             overlap=int(round(pr["content_overlap"] * 100)),
                             same=int(round(pr["content_overlap"] * min(x["records"], y["records"]))),
                             tot=min(x["records"], y["records"])),
                         True))

    # Withdraw entries whose cause has cleared.
    import glob
    import re
    for path in (glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json"))
                 + glob.glob(os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json"))):
        tid = re.sub(r"_official_[a-z_]*source$", "", os.path.basename(path)[:-5])
        for suffix, held in ((DAMAGE_SUFFIX, tid in damaged),
                             (PAIR_SUFFIX, tid in paired),
                             (RESTATE_SUFFIX, tid in restating)):
            if not held:
                note(put(path, tid + suffix, "", False))

    print("text-integrity disclosures: " + ", ".join(
        "%d %s" % (v, k) for k, v in sorted(tally.items())) or "nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
