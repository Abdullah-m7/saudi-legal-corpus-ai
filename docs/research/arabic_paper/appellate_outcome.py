#!/usr/bin/env python3
"""What did the appeal court do with the judgment below?

A published record often carries two judgments: the first-instance decision
and, where the case went up, the appellate one. That makes 13,924 matched
pairs — the same dispute at two levels — and it answers the question a
practitioner asks before relying on a judgment at all: did it survive?

The answer must be read from the appellate operative part and nowhere else.
An appellate recital routinely narrates the history of the case, including
earlier affirmances — «أصدرت بشأنها الحكم محل الالتماس ... الذي تم تأييده» —
so a pattern applied to the whole document reads an old affirmance as this
court's disposition. The operative part is introduced by «(لذلك)» or «حكمت
الدائرة», and only the text after the last such marker is classified.

Labels
  affirmed      تأييد الحكم
  reversed      نقض أو إلغاء الحكم
  varied        تعديل الحكم
  substituted   العدول عن الحكم والحكم مجددًا
  not_admitted  عدم قبول الاعتراض أو الاستئناف شكلاً
  reconsidered  التماس إعادة نظر — a different track, flagged not forced
  other_disposition  the circuit disposed of the case on another ground
  unclear       the operative part says none of these

Nothing is guessed: a record whose appellate operative part cannot be located,
or says something the list does not cover, is `unclear` and is reported as
such rather than folded into the majority label.

    python3 appellate_outcome.py --sample 40    # read the classification
"""

import argparse
import collections
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")


def bare(s):
    """Diacritics off, alef and ya unified.

    The operative part is often set with full vowelling — «حَكَمَتِ
    الدَائِرَةُ» — and a pattern written in plain script misses every one of
    them. Nearly four thousand appellate judgments were unclassified for this
    reason alone before the text was normalised first.
    """
    s = DIACRITICS.sub("", s)
    s = re.sub(r"[أإآٱ]", "ا", s)
    return s.replace("ى", "ي")


OPERATIVE = re.compile(
    r"\(\s*لذلك\s*\)|لذلك\s*[:：]|فلهذه\s+الاسباب|"
    r"نص\s+الحكم\s*[:：]|\(\s*منطوق\s+الحكم\s*\)|منطوق\s+الحكم\s*[:：]|"
    r"حكمت\s+(?:الدائرة|دائرة)|قررت\s+الدائرة\s+عدم|وبه\s+تقضي")

AFFIRMED = re.compile(r"بتاييد|تاييد\s+(?:ال)?حكم|تاييد\s+ما\s+قضي|تاييده|"
                      r"تاييد\s+نتيجه|رفضه?\s+موضوعا")
REVERSED = re.compile(r"بنقض|نقض\s+(?:ال)?حكم|بالغاء|الغاء\s+(?:ال)?حكم|"
                      r"بفسخ\s+(?:ال)?حكم")
VARIED = re.compile(r"بتعديل|تعديل\s+(?:ال)?حكم")
SUBSTITUTED = re.compile(r"بالعدول\s+عن|العدول\s+عن\s+(?:ال)?حكم|الحكم\s+مجددا")
# «عدم قبول طلب الاستئناف» is the appeal failing at the threshold; «عدم قبول
# طلب التحكيم» is a request for arbitration refused, and has nothing to do
# with the judgment below. An earlier pattern accepted any «طلب» after «عدم
# قبول» and conflated them.
NOT_ADMITTED = re.compile(r"عدم\s+قبول\s+(?:طلب\s+)?(?:ال)?(?:اعتراض|استئناف|التماس)|"
                          r"برفض\s+الالتماس|رفض\s+الاعتراض\s+شكل|"
                          r"عدم\s+قبوله\s+شكل")
RECONSIDERED = re.compile(r"التماس\s+اعاده\s+النظر|محل\s+الالتماس")
# Dispositions that are neither an affirmance nor a reversal: the circuit
# disposes of the case itself on another ground. Kept apart rather than
# folded into either side, because a lawyer asking «did it survive?» is
# owed the distinction.
OTHER = re.compile(r"عدم\s+قبول\s+(?:هذه\s+)?الدعوي|انقضاء\s+(?:هذه\s+)?الدعوي|"
                   r"عدم\s+اختصاص|اعتماد\s+تشكيل|شطب\s+الدعوي|"
                   r"ترك\s+الخصومه|وقف\s+الدعوي")


def operative(text):
    """The appellate operative part: everything after the last marker."""
    marks = list(OPERATIVE.finditer(text))
    if not marks:
        return None
    return text[marks[-1].start():]


# Where the appellate operative part stops speaking for itself and starts
# quoting the judgment below: «...بتأييد حكم الدائرة الثالثة ... القاضي
# بإلزام...». Everything after this belongs to the court below, and reading
# the whole window classified an affirmance of a reconsideration as a
# reconsideration.
QUOTED = re.compile(r"\s(?:و?القاضي|و?المنتهي\s+الي|و?المتضمن|ونصه)\b")


def outcome(appeal_text):
    """(label, the operative words it was read from)."""
    part = operative(bare(appeal_text))
    if part is None:
        return "unclear", None
    head = " ".join(part.split())[:400]
    cut = QUOTED.search(head)
    if cut and cut.start() > 25:
        head = head[:cut.start()]

    # Whichever disposition the court states FIRST is its disposition. A fixed
    # order of tests reads «بتأييد الحكم … الصادر … بإلغاء قرار اللجنة» as a
    # reversal, because the reversal pattern is tested first and the word is
    # there — inside a description of what was affirmed.
    found = {}
    for label, rx in (("not_admitted", NOT_ADMITTED), ("varied", VARIED),
                      ("reversed", REVERSED), ("affirmed", AFFIRMED),
                      ("reconsidered", RECONSIDERED),
                      ("other_disposition", OTHER)):
        m = rx.search(head)
        if m:
            found[label] = m.start()
    if not found:
        return "unclear", head
    label = min(found, key=found.get)
    # «ألغت الحكم وحكمت مجددًا» is a reversal that substitutes a new judgment,
    # and a practitioner needs to know the case was decided, not just undone.
    if label == "reversed" and SUBSTITUTED.search(head):
        label = "substituted"
    return label, head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()

    counts = collections.Counter()
    paired = appeal_only = n = 0
    by_id = {}
    sample = []
    rng = random.Random(20260827)
    seen = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            s = r.get("sections") or {}
            appeal = s.get("appealTextofRulling")
            if not appeal:
                continue
            paired += bool(s.get("judgmentTextofRulling"))
            appeal_only += not s.get("judgmentTextofRulling")
            label, head = outcome(appeal)
            counts[label] += 1
            by_id[r["id"]] = label
            seen += 1
            if args.sample:
                row = (label, r["judgment_number"], r["court"], r["city"], head)
                if len(sample) < args.sample:
                    sample.append(row)
                elif rng.random() < args.sample / seen:
                    sample[rng.randrange(args.sample)] = row

    total = sum(counts.values())
    print(f"{n:,} records; {total:,} carry an appellate judgment "
          f"({paired:,} paired with the first-instance text, "
          f"{appeal_only:,} appellate only)\n")
    for k in ("affirmed", "reversed", "substituted", "varied", "not_admitted",
              "reconsidered", "other_disposition", "unclear"):
        print(f"  {k:<14}{counts[k]:>7,}{counts[k]/total:>8.1%}")

    (HERE / "appellate_outcome_results.json").write_text(json.dumps({
        "records": n, "with_appeal": total, "paired": paired,
        "appeal_only": appeal_only, "counts": dict(counts),
        "by_judgment": by_id,
    }, ensure_ascii=False), encoding="utf-8")
    print("\nwrote appellate_outcome_results.json")

    for label, num, court, city, head in sample:
        print(f"\n[{label}] {court} ب{city}، حكم {num}\n  {(head or '—')[:300]}")


if __name__ == "__main__":
    main()
