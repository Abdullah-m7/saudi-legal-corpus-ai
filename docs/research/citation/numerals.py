#!/usr/bin/env python3
"""Arabic ordinal numerals as legislative drafting writes them.

Article numbers are written three ways in the same corpus, sometimes in the
same paragraph: «المادة (68)», «المادة 68», «المادة الثامنة والستين». The
third is not a stylistic variant that can be normalised away by stripping
diacritics -- it is a different number system, and 21 of 118 hand-labelled
GSTC citations use it.

Gender and case both vary and neither is informative: «الخامسة والأربعون» and
«الخامسة والأربعين» are the same article. The unit precedes the ten and is
joined by «و», so «الحادية والسبعين» is 71 and never 17; «الحادية عشر» is 11.
Both feminine (agreeing with مادة) and masculine forms appear.

    parse_ordinal("الثامنة والستين")  -> 68
    parse_ordinal("السابعة عشر")      -> 17
"""

import re

# unit ordinals, every attested spelling of each
UNITS = {
    1: ("الأولى", "الأول", "الحادية", "الحادي", "الواحدة"),
    2: ("الثانية", "الثاني"),
    3: ("الثالثة", "الثالث"),
    4: ("الرابعة", "الرابع"),
    5: ("الخامسة", "الخامس"),
    6: ("السادسة", "السادس"),
    7: ("السابعة", "السابع"),
    8: ("الثامنة", "الثامن"),
    9: ("التاسعة", "التاسع"),
    10: ("العاشرة", "العاشر"),
}

TENS = {
    20: ("العشرون", "العشرين"),
    30: ("الثلاثون", "الثلاثين"),
    40: ("الأربعون", "الأربعين"),
    50: ("الخمسون", "الخمسين"),
    60: ("الستون", "الستين"),
    70: ("السبعون", "السبعين"),
    80: ("الثمانون", "الثمانين"),
    90: ("التسعون", "التسعين"),
}

TEEN_MARK = ("عشرة", "عشر")
HUNDRED = ("المائة", "المئة", "مائة", "مئة")
# «المادة الثامنة والستين بعد المئة» is article 168 and «المادة المائتين» is
# article 200. Both appear in ministry judgments and neither is a variant
# spelling of anything already listed: «بعد المئة» adds a hundred to what
# precedes it, and «المائتين» is the dual of a hundred.
AFTER = ("بعد",)
TWO_HUNDRED = ("المائتين", "المئتين", "المائتان", "المئتان", "مائتين", "مئتين")
THREE_PLUS = {"الثلاثمائة": 300, "الثلاثمئة": 300, "الأربعمائة": 400,
              "الأربعمئة": 400, "الخمسمائة": 500, "الخمسمئة": 500,
              "الستمائة": 600, "الستمئة": 600, "السبعمائة": 700,
              "السبعمئة": 700, "الثمانمائة": 800, "الثمانمئة": 800,
              "التسعمائة": 900, "التسعمئة": 900}

_ALEF = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"})


def _norm(word):
    """Fold the alef seats and drop harakat. Nothing else."""
    word = re.sub(r"[ً-ْٰ]", "", word)
    return word.translate(_ALEF)


def _table(pairs):
    out = {}
    for value, spellings in pairs.items():
        for spelling in spellings:
            out[_norm(spelling)] = value
    return out


UNIT_BY_WORD = _table(UNITS)
TENS_BY_WORD = _table(TENS)
# a ten may also carry the article-less form after «و»
TENS_BY_WORD.update({_norm(s).replace("ال", "", 1): v
                     for v, ss in TENS.items() for s in ss})
TEEN_WORDS = {_norm(w) for w in TEEN_MARK}
HUNDRED_WORDS = {_norm(w) for w in HUNDRED}
AFTER_WORDS = {_norm(w) for w in AFTER}
TWO_HUNDRED_WORDS = {_norm(w) for w in TWO_HUNDRED}
BIG = {_norm(k): v for k, v in THREE_PLUS.items()}

WORD = re.compile(r"[ء-ي]+")


def parse_ordinal(text):
    """Return the integer an ordinal phrase denotes, or None.

    Refuses rather than guesses: a phrase with a word it does not know
    returns None, so that a wrong number never reaches a citation record.
    """
    words = [_norm(w) for w in WORD.findall(text or "")]
    words = [w for w in words if w != "و"]
    if not words:
        return None

    # strip a leading «و» attached as a proclitic to the first word
    if words[0].startswith("و") and words[0][1:] in UNIT_BY_WORD:
        words[0] = words[0][1:]

    total, unit, seen, after = 0, None, False, False
    for i, w in enumerate(words):
        base = w[1:] if (w.startswith("و") and
                         (w[1:] in TENS_BY_WORD or w[1:] in HUNDRED_WORDS)) else w
        if base in UNIT_BY_WORD:
            if unit is not None:
                return None            # two units, not a number we know
            unit = UNIT_BY_WORD[base]
            seen = True
        elif base in TEEN_WORDS:
            if unit is None:
                return None            # «عشر» with nothing before it
            unit += 10
        elif base in TENS_BY_WORD:
            total += TENS_BY_WORD[base]
            seen = True
        elif base in AFTER_WORDS:
            # «بعد» keeps what precedes it and adds the hundreds that follow
            after = True
        elif base in TWO_HUNDRED_WORDS:
            total += 200
            seen = True
        elif base in BIG:
            total += BIG[base]
            seen = True
        elif base in HUNDRED_WORDS:
            if after:
                total += 100
            else:
                total += 100 * (unit if unit and unit < 10 else 1)
                unit = None
            seen = True
        else:
            return None                # an unknown word: refuse
    if not seen:
        return None
    return total + (unit or 0)


# Every spelling the tables know, with and without the definite article,
# longest first, and refusing to end inside a word.
#
# An earlier version put an optional «ال» in front of the alternation. That
# looks harmless and is not: «العشرون» has its «ال» stripped by the optional
# group, the alternation then matches the shorter «عشر» inside what remains,
# the whole match succeeds, and the engine never backtracks. Article 20 was
# read as article 10 -- silently, because a match had been found.
def _spellings():
    out = set()
    for group in (UNITS, TENS):
        for forms in group.values():
            out.update(forms)
    out.update(TEEN_MARK)
    out.update(HUNDRED)
    out.update(AFTER)
    out.update(TWO_HUNDRED)
    out.update(THREE_PLUS)
    for word in list(out):
        if word.startswith("ال"):
            out.add(word[2:])
    return out


ORDINAL_RE = re.compile(
    r"(?:"
    + "|".join(re.escape(w) for w in sorted(_spellings(), key=len, reverse=True))
    + r")(?![ء-ي])"
)


def ordinal_phrase(text, start):
    """Longest run of ordinal words beginning at `start`, or ('', start)."""
    pos, end = start, start
    while True:
        m = re.compile(r"\s*(?:و)?\s*(" + ORDINAL_RE.pattern + r")").match(text, pos)
        if not m:
            break
        pos = end = m.end()
    return text[start:end], end
