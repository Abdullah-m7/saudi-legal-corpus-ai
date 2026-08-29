#!/usr/bin/env python3
"""Canonicalise Arabic legal text without destroying it or guessing at it.

Every source in this project arrives damaged in a different way. The Ministry
of Justice gateway returns clean API strings. The tax committees' digests
arrive as PDF text carrying bidi control characters, justification kashida,
and a systematic transposition of the definite article. Repairing those inside
a scraper hides them; repairing them here makes them measurable.

FIVE RULES, AND THE FOURTH IS THE DANGEROUS ONE
-----------------------------------------------
Each transformation is deterministic, individually switchable, individually
counted, and asserted not to change legal meaning. Raw text is never
overwritten: canonicalise() returns a record carrying raw, canonical, and the
list of what ran with how many edits each.

  bidi        strip U+200E..U+2069 directional controls. They carry no
              linguistic content and they sit between a number and the words
              around it, which breaks any pattern spanning the two.

  tatweel     strip U+0640. It is a justification glyph, not a letter.

  digits      Arabic-Indic ٠-٩ and Extended Arabic-Indic ۰-۹ to 0-9. The code
              points differ; the numbers do not.

  lam_swap    repair «المادة» emitted as «املادة». EVIDENCE-GATED, per
              document, and never from a dictionary. The rule is structural --
              alif, a consonant, lam -- and that shape also matches real Arabic
              imperatives: «اجلس» would become «الجس». So a candidate is
              repaired only where the repaired form does not already occur in
              the same document. A document that writes «المادة» correctly even
              once is left alone. A document where «المادة» occurs zero times
              and «املادة» 1,112 times is not writing Arabic imperatives; it is
              a broken encoding.

  brackets    «المادة ( )142» to «المادة (142)». Bidi reordering pushes a
              number out of the brackets that hold it. Applied only to the
              empty-bracket-then-digits shape, which is not a form anyone
              writes on purpose.

    from canonical import canonicalise
    rec = canonicalise(raw)          # all rules
    rec = canonicalise(raw, rules=["bidi", "digits"])   # ablation
"""

import re
import unicodedata

BIDI_CHARS = {0x200E, 0x200F, 0x061C, 0x202A, 0x202B, 0x202C, 0x202D,
              0x202E, 0x2066, 0x2067, 0x2068, 0x2069}
TATWEEL = "ـ"
ARABIC_INDIC = "٠١٢٣٤٥٦٧٨٩"
EXTENDED_ARABIC_INDIC = "۰۱۲۳۴۵۶۷۸۹"
DIGIT_MAP = str.maketrans(ARABIC_INDIC + EXTENDED_ARABIC_INDIC,
                          "0123456789" * 2)
# The letters the transposition test can see. «ل» is excluded on purpose and
# not for lack of evidence: the correct shape «ال» + «ل» and the transposed
# shape «ا» + «ل» + «ل» are the same three characters, so the test returns a
# ratio of exactly 1.0 for it in every document measured, which is an artefact
# of the test rather than a fact about the text. A rule cannot be gated on a
# measurement that cannot come out either way.
#
# The hamza-carrying alefs were missing from the first version and cost real
# parses: «المادة السابعة والأربعون» reaches the reader as «واألربعون», where
# the lam and the hamza-alef are transposed exactly as «الم» is, and an
# ordinal parser reads only «السابعة» and returns article 7 for article 47.
# Across the five development digests the correct:swapped ratio for أ is
# 0.00-0.11 and for إ 0.00-0.03, on thousands of occurrences each.
#
# Bare «ا» is included and is the case that shows the gate is doing work
# rather than rubber-stamping: four of the five digests transpose it (ratios
# 0.07-0.32) while the customs digest writes it correctly more often than not
# (2.34), and only the four are repaired.
CONSONANT = "بتثجحخدذرزسشصضطظعغفقكمنهوياأإآ"
LAM_CANDIDATE = re.compile(r"ا([" + CONSONANT + r"])ل(?=[ء-ي])")
# «المادة (5)، الفقرة» reaches the text layer as «المادة ( , )5الفقرة»: the
# digits are carried past the closing bracket and whatever punctuation sat
# after the bracket is carried inside it. The repair puts both back, and is
# not cosmetic -- in the authorities blocks, where citations are densest, it
# is the difference between detecting a citation and not.
EMPTY_BRACKET_NUMBER = re.compile(r"\(\s*([،,;؛]?)\s*\)\s*(\d+)")

RULES = ["bidi", "tatweel", "digits", "lam_swap", "brackets"]


def _bidi(text):
    out = text.translate({c: None for c in BIDI_CHARS})
    return out, len(text) - len(out)


def _tatweel(text):
    out = text.replace(TATWEEL, "")
    return out, len(text) - len(out)


def _digits(text):
    out = text.translate(DIGIT_MAP)
    n = sum(text.count(c) for c in ARABIC_INDIC + EXTENDED_ARABIC_INDIC)
    return out, n


# A first attempt gated this rule token by token: repair «املادة» only where
# «المادة» is absent. It failed twice and both failures are instructive. The
# «correct form» test matched inside other words -- «العالمية» contains «المي»
# -- so the gate was always satisfied and nothing was ever repaired. And on a
# short string with no context it corrupted real Arabic: «اجلس» became «الجس».
#
# The gate is therefore about the document, not the token. Word-initial «ال»
# is the commonest sequence in Arabic prose. A document in which it is
# effectively absent while the transposed shape is abundant is not prose
# containing imperatives; it is an encoding failure, and the repair is safe
# across the whole of it. A document that writes the article normally is left
# entirely alone.
# Arabic prefixes the article with و ف ب ك ل, so «والمادة» is one word and a
# plain non-letter boundary never fires on it. 81 of 14,327 swapped tokens in
# the first digest sat behind exactly that, which is 0.6 per cent of the
# repair silently declined.
BOUNDARY = r"(?:(?<=^)|(?<=[^ء-ي])|(?<=[وفبكل]))"
WORD_INITIAL_AL = re.compile(BOUNDARY + r"ال([" + CONSONANT + r"])[ء-ي]")
LAM_SWAP_MIN_EVIDENCE = 50    # occurrences of the swapped shape
# The two populations are not close. In the first tax digest meem sits at a
# correct:swapped ratio of 0.07 while taa -- which is fine -- sits at 9.4, and
# every other letter has no swapped occurrences at all. A threshold anywhere
# between them separates them, so it is set in the middle rather than tuned to
# either side.
LAM_SWAP_MAX_RATIO = 0.5


def lam_swap_diagnosis(text):
    """Which letters, if any, this document transposes -- measured per letter.

    A document-wide test is too blunt. The first tax digest writes «الجمارك»
    and «اللجنة» correctly and only «الم» wrongly: 14,246 swapped against 605
    correct for meem, and zero swapped for every other consonant. Repairing
    the whole alphabet on that evidence would corrupt the letters that are
    fine, so the gate is per letter and reported per letter.
    """
    out = {}
    for c in CONSONANT:
        correct = len(re.findall(BOUNDARY + r"ال" + c + r"[ء-ي]", text))
        swapped = len(re.findall(BOUNDARY + r"ا" + c + r"ل[ء-ي]", text))
        ratio = correct / swapped if swapped else None
        out[c] = {
            "correct": correct, "swapped": swapped, "ratio": ratio,
            "repair": (swapped >= LAM_SWAP_MIN_EVIDENCE
                       and ratio is not None and ratio < LAM_SWAP_MAX_RATIO),
        }
    return out


def _lam_swap(text):
    """Repair the definite article, per letter, only where the shape is broken."""
    diag = lam_swap_diagnosis(text)
    letters = "".join(c for c, d in diag.items() if d["repair"])
    if not letters:
        return text, 0
    pattern = re.compile(BOUNDARY + r"ا([" + letters + r"])ل(?=[ء-ي])")
    return pattern.subn(r"ال\1", text)[0], len(pattern.findall(text))


def _brackets(text):
    n = len(EMPTY_BRACKET_NUMBER.findall(text))
    return EMPTY_BRACKET_NUMBER.sub(r"(\2)\1", text), n


FUNCS = {"bidi": _bidi, "tatweel": _tatweel, "digits": _digits,
         "lam_swap": _lam_swap, "brackets": _brackets}


def canonicalise(raw, rules=None):
    """Return {raw, canonical, transformations:[{rule, edits}]}."""
    rules = RULES if rules is None else [r for r in RULES if r in rules]
    text = raw
    applied = []
    for name in rules:
        text, edits = FUNCS[name](text)
        applied.append({"rule": name, "edits": edits})
    return {"raw": raw, "canonical": text, "transformations": applied,
            "rulesRequested": rules}


def digest(text):
    """A stable fingerprint of a canonical form, for provenance records."""
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
