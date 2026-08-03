#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract an APPLICABLE amendment from a gazette amendment notice.

The currency audit finds which tracks have been amended. This module answers
the next question for one notice: can the amendment be applied to the stored
text WITHOUT anyone writing a word of legal language?

It can only be applied when the notice itself does three things at once:

  1. names the article it amends («تعديل المادة (14) من ...»),
  2. says the article is being REPLACED with a stated wording («لتكون بالنص
     التالي», «ليكون نصها كالآتي»),
  3. delimits that wording unambiguously — parentheses, guillemets or quotes.

Anything short of all three is REFUSED, and the refusal reason is the output.
The refusals are not edge cases, they are the majority, and each is refused
for a different reason:

  * EFFECT-ONLY. The notice states the effect rather than the replacement
    text: «تعديل المادة (الثانية عشرة) ... ليكون الارتباط التنظيمي لمركز
    إدارة الكوارث والأزمات برئيس اللجنة التنفيذية». Applying this would mean
    composing the amended article, which is drafting, not ingestion.
  * ATTACHMENT. The wording lives in a file the page only links to («وفق
    الصيغة المرافقة», «تنزيل الملف»). The page does not carry the text.
  * NO TARGET. The notice amends "some articles" without naming them.

A refusal is a correct outcome: the track keeps its disclosed currency
warning, which is honest, instead of receiving text nobody published.

This module extracts and reports. It does not write to any track.
"""

from __future__ import annotations

import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from gazette_autoingest import norm_ar, page_text, parse_ordinal, strip_text  # noqa: E402


def _ordinal(raw):
    """Arabic ordinals decline. After a preposition the gazette writes the
    genitive — «المادة السابعة والسبعين من ...» — while the corpus's ordinal
    generator produces the nominative «السابعة والسبعون». Try the declined
    forms before giving up, or every compound-number citation is missed."""
    for cand in (raw, raw.replace("ين", "ون"), raw.replace("ون", "ين"),
                 raw.replace("ية", "ي"), raw.replace("ي عشر", "ة عشرة")):
        n = parse_ordinal(cand)
        if n:
            return n
    return None

# «المادة (14)» / «المادة (الثانية عشرة)» / «المادة السابعة والسبعين»
TARGET_RE = re.compile(
    r"الماد[ةه]\s*\(?\s*([0-9٠-٩]{1,3}|[^()\n]{3,40}?)\s*\)?\s*"
    r"(?:من|في)\s+(?:تنظيم|النظام|نظام|اللائحة|لائحة|القواعد|قواعد|الضوابط|ضوابط|الترتيبات)")

# The notice must say the article is being given a stated wording.
REPLACE_RE = re.compile(
    r"(?:لتكون|ليكون|يكون|تكون)\s*(?:نصها|نصه|بالنص)?\s*"
    r"(?:التالي|الآتي|الاتي|كالتالي|كالآتي|كما\s+يلي)\s*[:：]?\s*")

# The stated wording has to be delimited, so its start and end are the
# publisher's decision and not the reader's.
DELIMS = [("«", "»"), ("(", ")"), ('"', '"'), ("“", "”")]

ATTACHMENT_RE = re.compile(
    r"(وفق الصيغة المرافقة|الصيغة المرفقة|تنزيل الملف|وفقاً للصيغة المرافقة"
    r"|وفقا للصيغة المرافقة|المرافق لهذا القرار)")

MIN_TEXT = 40  # a replacement shorter than this is not an article


def _target_article(body):
    """The article number the notice names, or None."""
    for m in TARGET_RE.finditer(body):
        raw = m.group(1).strip()
        if re.fullmatch(r"[0-9٠-٩]{1,3}", raw):
            return int(raw.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))), raw
        n = _ordinal(raw)
        if n:
            return n, raw
    return None, None


def _replacement(body):
    """The delimited wording the notice states, or None."""
    m = REPLACE_RE.search(body)
    if not m:
        return None, "no replacement marker: the notice does not state a wording"
    tail = body[m.end():].lstrip()
    for op, cl in DELIMS:
        if tail.startswith(op):
            end = tail.find(cl, 1)
            if end > 0:
                return strip_text(tail[1:end]), None
    return None, ("replacement marker present but the wording is not delimited, "
                  "so its start and end would be the reader's guess")


def extract(path):
    """(amendment_or_None, reason). Never guesses; a refusal carries its cause."""
    title, raw = page_text(path)
    body = " ".join(raw.split())
    if ATTACHMENT_RE.search(body):
        return None, ("ATTACHMENT: the amended wording is in a linked file, not on the "
                      "page — nothing to ingest from here")
    num, label = _target_article(body)
    if not num:
        return None, "NO TARGET: the notice does not name the article it amends"
    text, why = _replacement(body)
    if not text:
        return None, "EFFECT-ONLY: %s" % why
    if len(text) < MIN_TEXT:
        return None, ("EFFECT-ONLY: the delimited fragment is %d characters, too short to be "
                      "a replacement article" % len(text))
    return {"title": title, "article_number": num, "article_label": label,
            "replacement_text": text}, None


MIN_JACCARD = 0.35   # see verify_against_current


def verify_against_current(current_text, replacement_text):
    """(ok, detail). An amendment may only be applied when the replacement is
    recognisably a rewrite OF THE STORED ARTICLE.

    Naming the article is not enough. A notice cites «المادة (التاسعة)» of the
    instrument IT amends, and that instrument is not always the track the
    currency audit paired it with -- the audit matches on title, and titles
    collide. Measured on the four notices that reached this stage, the two
    genuine amendments scored 0.78 and 0.58 word-Jaccard against the stored
    article while the two misidentified ones scored 0.05 each: a replacement
    defining «الوزير» aimed at an article about notifying contact-data changes,
    and one about legal personality aimed at an article listing board members.
    Without this check, half of what passed extraction would have overwritten
    the wrong article with text from another instrument.
    """
    a = set(norm_ar(current_text).split())
    b = set(norm_ar(replacement_text).split())
    if not a or not b:
        return False, "empty text on one side"
    jac = len(a & b) / len(a | b)
    if jac < MIN_JACCARD:
        return False, ("replacement shares only %.0f%% of its wording with the stored "
                       "article — the notice's article number almost certainly refers to a "
                       "different instrument, so applying it would overwrite the wrong text"
                       % (jac * 100))
    return True, "replacement shares %.0f%% of its wording with the stored article" % (jac * 100)


def main():
    for p in sys.argv[1:]:
        a, why = extract(p)
        if a:
            print("APPLICABLE  %s\n  article %d (%s)\n  %s\n"
                  % (p, a["article_number"], a["article_label"], a["replacement_text"][:200]))
        else:
            print("REFUSED     %s\n  %s\n" % (p, why))


if __name__ == "__main__":
    main()
