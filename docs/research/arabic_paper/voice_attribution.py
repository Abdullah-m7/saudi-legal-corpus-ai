#!/usr/bin/env python3
"""Who is speaking in الوقائع — the court, or a party?

The citator and `cite_by_voice.py` both split a judgment at its own headings:
everything before «الأسباب:» was labelled *pleadings*, everything between
«الأسباب:» and «حكمت الدائرة» *reasoning*, the rest *operative*. The middle
two labels say what they measure. The first does not.

الوقائع is not the parties' pleadings. It is the statement of the case, and
the court writes it. It carries the parties' arguments *reported by the
court*, and it also carries the court's own procedural narration — «وتشير
الدائرة إلى أنها عقدت هذه الجلسة التحضيرية بناءً على المادة التسعين». A
citation in that sentence is the court describing what it did, not a party
arguing anything. Counting it as an argument put to the court overstates the
bar's citation practice and understates the bench's.

This script measures the split. For every statutory citation in the الوقائع
segment it reads backwards to the nearest attribution cue in the same
sentence and records whether that cue is the court or a party. Where no cue
is found within the sentence, the citation is recorded as unattributed and
NOT assigned to either side.

The cue lists are a heuristic; `--sample N` prints N citations with their
sentences so the classification can be read against the text.
"""

import argparse
import collections
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

CITE = re.compile(
    r"الماد[ةه]\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+((?:نظام|لائحة|النظام|اللائحة)[^\.،؛\n\)]{0,60})")
REASONS = re.compile(r"(?<!فلهذه\s)الأسباب\s*[:：]")
RULING = re.compile(r"حكمت\s+الدائرة")
FACTS = re.compile(r"الوقائع\s*[:：]")
BREAK = re.compile(r"[.؛\n]")

BENCH = r"(?:الدائرة|المحكمة|هذه\s+الدائرة|هيئة\s+النظر)"
ACT = (r"(?:تشير|أشار[تث]?|باشر[تث]?|عقد[تث]?|اطلع[تث]?|قرر[تث]?|رأ[تث]|أحال[تث]?|"
       r"حدد[تث]?|كلف[تث]?|مكن[تث]?|استمع[تث]?|أفهم[تث]?|سأل[تث]?|أصدر[تث]?|"
       r"انته[تث]|وجد[تث]?|لاحظ[تث]?|رفع[تث]?|قض[تث]|ندب[تث]?|ع[يّ]?ن[تث]?|"
       r"استوف[تث]|تحقق[تث]?|أمهل[تث]?|بل[غّ]?غ?[تث]?|دع[تث]|نظر[تث]?|افتتح[تث]?|"
       r"أج[لّ]?ل[تث]?|تبين\s+ل|انتهت|سار[تث]|اكتف[تث])")
COURT_CUE = re.compile(rf"(?:{ACT}\s+(?:هذه\s+)?{BENCH})|(?:{BENCH}\s+(?:قد\s+)?{ACT})")

SIDE = (r"(?:المدّعي|المدعي|المدعية|المدعى\s+عليه[ا]?|المدعي\s+عليه[ا]?|"
        r"المستأنف[ةه]?|المستأنف\s+ضده[ا]?|الطاعن[ةه]?|المعترض[ةه]?|"
        r"المدعين|المدعى\s+عليهم|وكيل\s+\S+|المنفذ\s+ضده)")
SAY = (r"(?:قال[تث]?|ذكر[تث]?|أفاد[تث]?|ب[يّ]?ن[تث]?|دفع[تث]?|طلب[تث]?|أضاف[تث]?|"
       r"استند[تث]?|ادع[ىت]|أجاب[تث]?|ر[دّ]د?[تث]?|أوضح[تث]?|صر[حّ]ح?[تث]?|"
       r"تضمن[تث]?|أقام[تث]?|قد[مّ]م?[تث]?|التمس[تث]?|أورد[تث]?|زعم[تث]?|"
       r"نازع[تث]?|اعترض[تث]?|خالف[تث]?|تمسك[تث]?|أنكر[تث]?|طعن[تث]?|أقر[تث]?|"
       r"احتج[تث]?|استظهر[تث]?|أسس[تث]?)")
FIRST = r"(?:موكل[تي]|موكلتي|نتمسك|نؤكد|نطلب|ننكر|نلتمس|نفيد|ندفع|أطلب|ألتمس|أفيد)"
PARTY_CUE = re.compile(
    rf"(?:{SIDE}\s*(?:قد\s+)?{SAY})|(?:{SAY}\s+(?:وكيل\s+)?{SIDE})|(?:{FIRST})")

WINDOW = 400


def recital(text):
    """The الوقائع segment, or None when the judgment lacks the headings."""
    r = REASONS.search(text)
    k = RULING.search(text, r.end() if r else 0)
    if not r or not k:
        return None
    f = FACTS.search(text)
    start = f.start() if f and f.start() < r.start() else 0
    return text[start:r.start()]


def sentence(seg, at):
    """The sentence carrying the citation, and the citation's offset in it."""
    lo = max(0, at - WINDOW)
    hi = min(len(seg), at + WINDOW)
    left = max((m.end() for m in BREAK.finditer(seg, lo, at)), default=lo)
    m = BREAK.search(seg, at, hi)
    right = m.start() if m else hi
    return seg[left:right], at - left


def attribute(seg, at):
    """court | party | unattributed — the cue nearest the citation wins.

    Both directions, because Arabic puts the subject after the verb as often
    as before it: «قررت الدائرة … بناءً على المادة» and «بناءً على المادة …
    فقد أفهمت الدائرة» are the same speaker.
    """
    sent, off = sentence(seg, at)
    best = {"court": None, "party": None}
    for kind, rx in (("court", COURT_CUE), ("party", PARTY_CUE)):
        for m in rx.finditer(sent):
            d = 0 if m.start() <= off <= m.end() else min(
                abs(m.start() - off), abs(m.end() - off))
            if best[kind] is None or d < best[kind]:
                best[kind] = d
    c, p = best["court"], best["party"]
    if c is None and p is None:
        return "unattributed", sent, off
    if p is None or (c is not None and c < p):
        return "court", sent, off
    return "party", sent, off


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()

    counts = collections.Counter()
    seen = judgments = segmented = 0
    sample = []
    rng = random.Random(20260827)

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            judgments += 1
            r = json.loads(line)
            seg = recital(r["text"])
            if seg is None:
                continue
            segmented += 1
            for m in CITE.finditer(seg):
                seen += 1
                kind, sent, off = attribute(seg, m.start())
                counts[kind] += 1
                if args.sample:
                    row = (kind, r["judgment_number"],
                           sent[:off] + " «»" + sent[off:])
                    if len(sample) < args.sample:
                        sample.append(row)
                    elif rng.random() < args.sample / seen:
                        sample[rng.randrange(args.sample)] = row

    tot = sum(counts.values())
    print(f"{judgments:,} judgments; {segmented:,} carry the headings "
          f"({segmented/judgments:.1%})")
    print(f"{tot:,} statutory citations inside الوقائع\n")
    for k in ("court", "party", "unattributed"):
        print(f"  {k:<13} {counts[k]:>8,}  {counts[k]/tot:>6.1%}")

    (HERE / "voice_attribution_results.json").write_text(json.dumps({
        "judgments": judgments, "segmented": segmented,
        "recital_citations": tot, "counts": dict(counts),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    for kind, num, sent in sample:
        print(f"\n[{kind}] حكم {num}\n  {sent}")


if __name__ == "__main__":
    main()
