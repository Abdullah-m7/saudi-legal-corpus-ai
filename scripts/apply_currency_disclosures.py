#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write the currency warning into every track the currency audit flags.

The audit produces a report. A report nobody reads changes nothing about what
the corpus ASSERTS, and the corpus asserts its text through the source
artifacts. So each flagged track gets one entry in its own
`known_unresolved_discrepancies`, in Arabic, saying exactly three things:

  1. the edition date the corpus holds,
  2. that N amendment notices whose TITLES carry every distinctive word of this
     instrument's name, and its instrument type, were published in Umm Al-Qura
     AFTER that date -- each named with its own date, title and URL,
  3. that the notice is NOT the amendment text, so nothing is claimed about
     the amendment's content and no article was altered on its authority; and
     that the match was made on titles rather than on bodies, so a neighbouring
     instrument can appear in a title, and the linked page is the arbiter.

Point 3 is the whole discipline, and both halves of it are load-bearing.

An amendment notice is evidence that the stored text MAY be out of date; it is
not evidence of what the new text says. Writing anything more than the warning
would be drafting law, which this corpus never does.

And the disclosure claims only what the audit can actually establish. "A notice
whose SUBJECT is this instrument" would be a reading of the notice; "a notice
whose title names this instrument in full, and names its type" is a fact about
the title, which is what was measured. Two residual ambiguities survive every
title rule tried and are the reason the weaker claim is the honest one:
«تعديل اللائحة التنفيذية لجباية الزكاة ونظام ضريبة الدخل» may amend one
regulation covering both subjects or two instruments, and «... اللائحة التنفيذية
لضريبة القيمة المضافة للموائمة مع ... لائحة الفوترة الإلكترونية» names a second
regulation only to say what the first was aligned TO. Nothing in either title
settles it; the gazette page does.

The warning is lifted only when the amended text is ingested from an official
source.

Idempotent: an existing currency entry is rewritten in place, so re-running
after a fresh audit updates the notice list rather than accumulating copies.
A track whose flag has cleared has its entry removed, since a warning that no
longer holds is itself a false assertion.
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "reports", "corpus_currency_audit", "corpus_currency_audit.json")

KEY_SUFFIX = "_amended_after_edition_on_file"

TEMPLATE = (
    "**تنبيه سريان**: النسخة المُستوعبة هنا منشورة بتاريخ {edition}، وقد رصد تدقيق السريان "
    "(scripts/audit_corpus_currency.py) {count}{noun} في أرشيف جريدة أم القرى **بعد** هذا "
    "التاريخ، يحمل عنوانه اسم هذه الأداة بكل كلماته المميِّزة ونوعها ذاته "
    "({kind}): {notices}. **الإشعار ليس نص التعديل**، ولذلك لا يُدَّعى هنا شيء عن مضمونه ولم "
    "يُعدَّل نص أي مادة استناداً إليه. والمطابقة على العنوان لا على المتن، وقد يَرِد اسم أداة "
    "داخل عنوانٍ موضوعُه أداة مجاورة، فالصفحة الرسمية المذكورة هي الفيصل. المُفصَح عنه هو أن "
    "نص هذا المسار **قد لا يكون محدَّثاً**. يُرفع هذا التنبيه فقط عند استيعاب النص المعدَّل من "
    "مصدر رسمي.")

# Some instruments carry no type word at all — «إجراءات وشروط الترخيص لممارسة النقل العام
# بالحافلات داخل المدن», «آلية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم». For those
# the type was not matched, it was INAPPLICABLE, and the disclosure must not say otherwise:
# writing «ونوعها ذاته (غير مُصنَّف)» would assert a comparison that never took place. The
# claim is narrowed to what was actually established — the full name, and nothing else.
TEMPLATE_UNTYPED = (
    "**تنبيه سريان**: النسخة المُستوعبة هنا منشورة بتاريخ {edition}، وقد رصد تدقيق السريان "
    "(scripts/audit_corpus_currency.py) {count}{noun} في أرشيف جريدة أم القرى **بعد** هذا "
    "التاريخ، يحمل عنوانه اسم هذه الأداة بكل كلماته المميِّزة. وعنوان هذه الأداة لا يتضمن "
    "كلمةَ نوعٍ (نظام/لائحة/قواعد/ضوابط/تنظيم)، فلم تُقابَل الأنواع أصلاً واستندت المطابقة "
    "إلى الاسم كاملاً وحده: {notices}. **الإشعار ليس نص التعديل**، ولذلك لا يُدَّعى هنا شيء "
    "عن مضمونه ولم يُعدَّل نص أي مادة استناداً إليه. والمطابقة على العنوان لا على المتن، وقد "
    "يَرِد اسم أداة داخل عنوانٍ موضوعُه أداة مجاورة، فالصفحة الرسمية المذكورة هي الفيصل. "
    "المُفصَح عنه هو أن نص هذا المسار **قد لا يكون محدَّثاً**. يُرفع هذا التنبيه فقط عند "
    "استيعاب النص المعدَّل من مصدر رسمي.")

# Said in the disclosure so the reader knows which distinction the match rested on: an
# implementing regulation's amendment is not evidence about the law it implements.
KIND_AR = {
    "LAW": "نظام", "REGULATION": "لائحة", "RULES": "قواعد", "INSTRUCTIONS": "تعليمات",
    "CONTROLS": "ضوابط", "STATUTE": "تنظيم/ترتيبات تنظيمية",
}

# The anchor may be a Hijri date converted arithmetically rather than a gazette
# date read off the page. Saying so is part of the disclosure: a reader must be
# able to tell a measured date from a computed one.
CONVERTED_NOTE = (
    " (تاريخ الطبعة أعلاه محسوب من التاريخ الهجري المُثبَت في المصدر، لا مقروءاً من ترويسة "
    "الجريدة؛ وقد اشتُرط فارق ثلاثين يوماً على الأقل حتى لا يُنتج خطأ التحويل تنبيهاً كاذباً.)")


def save(path, raw, data):
    """Write `data` back to `path` in the file's OWN formatting.

    The 614 source artifacts were built over many batches and are not uniformly
    formatted: 570 use a two-space indent, 111 a one-space indent, 43 end with a
    newline and the rest do not. Re-serialising them all one way would rewrite
    every line of a hundred files carrying legal text, burying a one-entry change
    in a diff nobody could review. So the file's own style is measured by
    round-tripping what was read, and only that style is written back."""
    for indent in (2, 1):
        for tail in ("", "\n"):
            if json.dumps(json.loads(raw), ensure_ascii=False, indent=indent) + tail == raw:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(json.dumps(data, ensure_ascii=False, indent=indent) + tail)
                return True
    print("SKIPPED (unrecognised formatting, would rewrite the whole file)  %s"
          % os.path.relpath(path, ROOT))
    return False


def _noun(n):
    """Arabic counts decline. «إشعار تعديل واحد», «إشعارا تعديل», «3 إشعارات»."""
    if n == 1:
        return "إشعار تعديل واحداً"
    if n == 2:
        return "إشعاري تعديل"
    if n <= 10:
        return "إشعارات تعديل"
    return "إشعار تعديل"


def _count(n):
    return "" if n <= 2 else "%d " % n


def build_description(entry):
    notices = entry["amendment_notices"]
    shown = notices[:6]
    parts = ["%s — %s (%s)" % (n["date"], n["title_ar"], n["url"]) for n in shown]
    tail = ""
    if len(notices) > len(shown):
        tail = "، وغيرها %d إشعاراً مسرودة في تقرير التدقيق" % (len(notices) - len(shown))
    kind = KIND_AR.get(entry.get("instrument_type"))
    desc = (TEMPLATE if kind else TEMPLATE_UNTYPED).format(
        edition=entry["edition_on_file"],
        count=_count(len(notices)),
        noun=_noun(len(notices)),
        kind=kind,
        notices="؛ ".join(parts) + tail)
    if not entry.get("anchor_is_exact_gazette_date", True):
        desc += CONVERTED_NOTE
    return desc


def apply(report_path=REPORT, write=True):
    rep = json.load(open(report_path, encoding="utf-8"))
    flagged = {e["track_id"]: e for e in rep["at_risk"]}
    added = updated = removed = unchanged = 0

    for entry in rep["at_risk"]:
        path = os.path.join(ROOT, entry["source_artifact"])
        if not os.path.isfile(path):
            print("MISSING ARTIFACT  %s" % entry["source_artifact"])
            continue
        raw = open(path, encoding="utf-8").read()
        src = json.loads(raw)
        disc = src.setdefault("known_unresolved_discrepancies", [])
        key = entry["track_id"] + KEY_SUFFIX
        desc = build_description(entry)
        for d in disc:
            if isinstance(d, dict) and d.get("article_key", "").endswith(KEY_SUFFIX):
                if d["description"] == desc and d["article_key"] == key:
                    unchanged += 1
                    break
                d["article_key"], d["description"] = key, desc
                updated += 1
                break
        else:
            disc.append({"article_key": key, "description": desc})
            added += 1
            src["known_unresolved_discrepancies"] = disc
        if write:
            save(path, raw, src)

    # A track whose flag has cleared -- because the amended text was ingested,
    # or because a matching rule was corrected -- must lose its warning.
    import glob
    for path in (glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json"))
                 + glob.glob(os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json"))):
        tid = re.sub(r"_official_[a-z_]*source$", "", os.path.basename(path)[:-5])
        if tid in flagged:
            continue
        raw = open(path, encoding="utf-8").read()
        src = json.loads(raw)
        disc = src.get("known_unresolved_discrepancies")
        if not disc:
            continue
        # A few of the earliest artifacts record discrepancies as plain strings rather than
        # {article_key, description} objects. They are left exactly as they are.
        keep = [d for d in disc
                if not (isinstance(d, dict)
                        and d.get("article_key", "").endswith(KEY_SUFFIX))]
        if len(keep) == len(disc):
            continue
        src["known_unresolved_discrepancies"] = keep
        removed += 1
        if write:
            save(path, raw, src)

    print("currency disclosures: %d added, %d updated, %d already current, %d withdrawn"
          % (added, updated, unchanged, removed))
    return added, updated, unchanged, removed


if __name__ == "__main__":
    apply(sys.argv[1] if len(sys.argv) > 1 else REPORT, write="--dry-run" not in sys.argv)
