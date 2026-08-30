#!/usr/bin/env python3
"""Who is speaking in الوقائع — the court, or a party? And where is a citation?

This module also owns CITE, the pattern every other script uses to find a
statutory citation, so that there is one definition to correct when it turns
out to be wrong — and it did turn out to be wrong.

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
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Two representation faults were found by reading whole judgments
# (gstc_pilot/MOJ_ARTICLE_GOLD.md) and a candidate third source
# (gstc_pilot/SOURCE_C.md), after the held-out evaluations were run and
# reported. Neither is a matching rule; both are the text arriving as
# something other than the characters it renders as.
#
#   presentation forms   «ﺍﻟﻤﺎﺩﺓ» is six codepoints in U+FB50..U+FEFF, not the
#                        string «المادة». A document written in them reads
#                        downstream as one that cites nothing. 30.2 per cent
#                        of ministry judgments carry some.
#   combining marks      «المادَّة» with a shadda is the same word, and is not
#                        the same string. 234 citations corpus-wide were lost
#                        to that one mark; 99.4 per cent of judgments carry
#                        marks somewhere.
#
# CITE is made tolerant of marks directly, because a caller that forgets to
# normalise should not silently lose citations. Presentation forms cannot be
# absorbed into a pattern -- every letter is a different codepoint -- so a
# caller that reads sources other than the ministry API must call normalise()
# and then work on the normalised string throughout, since stripping
# characters moves every offset after them.
PRESENTATION = re.compile(r"[\uFB50-\uFDFF\uFE70-\uFEFE]")
MARKS = re.compile(r"[\u064B-\u0652\u0670\u0653-\u0655]")
TATWEEL = "\u0640"


def normalise(text):
    """Presentation forms to letters, marks and tatweel away. Same rules as
    canon/canonical.py, for callers that read raw text rather than the
    canonical record."""
    text = PRESENTATION.sub(
        lambda m: unicodedata.normalize("NFKC", m.group(0)), text)
    return MARKS.sub("", text.replace(TATWEEL, ""))


_M = r"[\u064B-\u0652\u0670\u0653-\u0655]*"     # marks, anywhere, any number
# marks after the final letter too: «المادةُ» is attested
_HEAD = ("م" + _M + "ا" + _M + "د" + _M + "[ةه]" + _M)

CITE = re.compile(
    r"(?<![ء-ي])(?:ال|لل|بال|كال|فال|وال|ول|بل|ب|ل|و)?" + _HEAD +
    r"\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+"
    r"((?:نظام|لائحة|النظام|اللائحة)[^\.،؛\n\)]{0,60})")

# The prefix alternation is not decoration. A judgment writes «وفقاً للمادة
# التاسعة والعشرين من نظام الإثبات» as readily as «المادة التاسعة والعشرين»,
# and a pattern anchored on «المادة» alone missed 16,682 citations — 15.7 per
# cent of everything this project had counted. It surfaced when the same
# extractor was pointed at a lawyer's draft and silently dropped two of his
# four articles. The lookbehind keeps «عمادة» and «شهادة» out.
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


PART_ORDER = ("judgmentFacts", "judgmentReasons", "judgmentRuling",
              "judgmentTextofRulling", "appealFacts", "appealReasons",
              "appealRuling", "appealTextofRulling")


def parts(text, sections):
    """The (start, end) span of each source document inside a record's text.

    A published record can hold two judgments: the first-instance one and,
    where the case went up, the appellate one, concatenated by the collector
    in the publisher's own field order. Segmenting the concatenation as if it
    were one document lets the boundary straddle — the first «الأسباب:» opens
    in the first judgment and the first «حكمت الدائرة» after it can close in
    the second, so an appellate recital is read as first-instance reasoning.
    It happens in 416 of the 27,350 segmented records, which is small and is
    not a reason to leave it wrong. Each document is segmented on its own.
    """
    if not sections:
        return [(0, len(text))]
    spans, pos = [], 0
    for f in PART_ORDER:
        v = sections.get(f)
        if not v:
            continue
        spans.append((pos, pos + len(v)))
        pos += len(v) + 1          # the single space the collector joined on
    return spans or [(0, len(text))]


def segments(text, sections):
    """(start, end, voice) over the whole record, document by document.

    Voices are recital, reasoning and operative where a document carries the
    headings in order, and unknown for the whole of a document that does not.
    """
    out = []
    for a, b in parts(text, sections):
        r = REASONS.search(text, a, b)
        k = RULING.search(text, r.end() if r else a, b)
        if not r or not k:
            out.append((a, b, "unknown"))
            continue
        out.append((a, r.start(), "recital"))
        out.append((r.end(), k.start(), "reasoning"))
        out.append((k.start(), b, "operative"))
    return out


def voice_at(spans, at):
    for a, b, v in spans:
        if a <= at < b:
            return v
    return "unknown"


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
