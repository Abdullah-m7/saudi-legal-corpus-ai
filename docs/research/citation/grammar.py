#!/usr/bin/env python3
"""A staged citation grammar for Saudi adjudicatory texts.

The stages are separate because the failures are separate. When the extractor
scored 0.0 per cent on GSTC and 90.9 per cent on MOJ, a single regex could not
say which of the two corpora it had learned; staged output can, because every
stage reports its own success and every stage can be switched off.

    DETECTION            an article expression is present at all
    ARTICLE EXPRESSION   its number, however written
    PARAGRAPH            its paragraph and subparagraph, prefixed or postfixed
    INSTRUMENT           the instrument named in the same attachment
    ANAPHORA             the instrument named earlier and resumed by a clitic
    ATTRIBUTION          whose citation this is: the tribunal's, a party's,
                         the reporter's list of authorities
    RECORD               the citation, with every stage's verdict kept

The grammar is written against forms attested in hand-labelled data and is not
specific to one publisher. Where a form is ambiguous the grammar refuses:
`instrument` stays None and `instrumentSource` says why. A refusal is a
result. A guess is a false positive that no evaluation can see.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numerals import ORDINAL_RE, ordinal_phrase, parse_ordinal   # noqa: E402

STAGES = ("detection", "article", "paragraph", "instrument", "anaphora",
          "attribution")

# ---------------------------------------------------------------- detection

# «المادة», «للمادة», «بالمادة», «والمادة», «المادتين», and the bare «مادة».
HEAD = re.compile(r"(?:(?<=^)|(?<=[^ء-ي]))"
                  r"(?:[وفبكل]|لل|بال|كال|فال|وال)?"
                  r"(?:ال)?ماد[ةت](?:ين|ي)?\b")

# ------------------------------------------------------- article expression

DIGITS = r"\d+"
NUM_IN_PARENS = re.compile(r"\s*\(\s*(" + DIGITS + r")\s*\)")
NUM_BARE = re.compile(r"\s*(" + DIGITS + r")(?![\d/])")
NUM_AFTER_RAQM = re.compile(r"\s*رقم\s*")
ORD_IN_PARENS = re.compile(r"\s*\(\s*(" + ORDINAL_RE.pattern + r"[^)]*?)\s*\)")

# --------------------------------------------------------------- paragraph

# a paragraph label: digits, an Arabic letter, an ordinal word, or any of
# these joined by «/» or «-» in either order («8-ج», «/1أ», «أولا/9»).
LABEL = r"[^\s()]{1,20}"
PARA_WORDS = r"(?:الفقرة|الفقرات|الفقرتين|البند|البنود|بند|فقرة)"
# prefixed: «الفقرة (3) من المادة», «الفقرة الرابعة من المادة»
PARA_PREFIX = re.compile(
    PARA_WORDS + r"\s*(?:رقم\s*)?(?:\(\s*(" + LABEL + r")\s*\)|("
    + ORDINAL_RE.pattern + r"))")
# postfixed: «المادة (4) البند ثانيا», «المادة (5) الفقرة (1) بند (أ)»
PARA_POSTFIX = re.compile(
    r"\s*" + PARA_WORDS + r"\s*(?:رقم\s*)?(?:\(\s*(" + LABEL + r")\s*\)|("
    + ORDINAL_RE.pattern + r"[ء-ي]*)|(" + LABEL + r"))")
# parenthesised straight after the article number: «الرابعة (أولا/9)»
PARA_TRAILING_PARENS = re.compile(r"\s*\(\s*(" + LABEL + r")\s*\)")

# --------------------------------------------------------------- instrument

# «من» / «ل» / «لـ» introduce the instrument. Page numbers and line breaks may
# intervene: pagination is not drafting.
GAP = r"(?:[\s ]|\d{1,4}(?=\s))*"
INSTRUMENT_LINK = re.compile(r"\s*(?:من|ل)\s*")
# an instrument name begins with one of these heads
INST_HEAD = (r"(?:الالئحة|اللائحة|لائحة|الئحة|لائحته|الئحته|النظام|نظام|"
             r"الاتفاقية|الإتفاقية|الاتفاقيه|اتفاقية|قواعد|القواعد|"
             r"تعليمات|التعليمات|قرار|القرار|المرسوم|مرسوم|الأمر)")
INST = re.compile(INST_HEAD + r"(?:[^،؛.\n\r]{0,120}?)"
                  r"(?=\s*(?:،|؛|\.|\n|\r|الصادر|الصادرة|على|التي|والتي|$))")

# a coordinated article expression that stands between this one and the
# instrument, e.g. «المادة (13) والفقرة (2) من المادة (20) من الالئحة ...»
COORD = re.compile(r"^[\s,،؛]*(?:و|أو)?[\s]*(?:" + PARA_WORDS + r"|"
                   r"(?:[وفبكل]|لل|بال|كال|فال|وال)?(?:ال)?ماد[ةت])")

# ----------------------------------------------------------------- anaphora

ANAPHOR = re.compile(
    r"^\s*(?:من\s*)?("
    r"منها|منه|"
    r"(?:ذات|هذه|تلك)\s*(?:الالئحة|اللائحة|الالئحه)|"
    r"(?:ذات|هذا)\s*النظام|"
    r"الالئحة|اللائحة|النظام|"
    r"لائحته\s*التنفيذية|الئحته\s*التنفيذية"
    r")\b")
# a fully named instrument, for the anaphor to bind to
FULL_INST = re.compile(
    r"(?:الالئحة|اللائحة|الئحة|لائحة)\s*(?:التنفيذية\s*)?"
    r"(?:ل(?:نظام|جباية|ضريبة)[^،؛.\n]{0,60})"
    r"|نظام\s+[ء-ي]+(?:\s+[ء-ي]+){0,4}"
    r"|قواعد\s+عمل[^،؛.\n]{0,60}"
    r"|الاتفاقية\s+الموحدة[^،؛.\n]{0,60}")

# -------------------------------------------------------------- attribution

# section headings, in the order a decision uses them. The label attaches to
# every citation until the next heading.
SECTIONS = [
    ("authorities", re.compile(r"^\s*المستند\s*:?\s*$|^\s*المستندات\s*:?\s*$"
                               r"|^\s*الاستناد\s*:?\s*$")),
    ("party", re.compile(r"دفوع\s+(?:ال)?(?:أطراف|اطراف|مدعية|مدعي|"
                         r"مدعى\s*عليه|مستأنف|المكلف|الهيئة)")),
    ("reasoning", re.compile(r"موقف\s+(?:اللجنة|الدائرة)|^\s*الأسباب\s*:?"
                             r"|^\s*األسباب\s*:?|ولهذه\s+الأسباب"
                             r"|من\s+حيث\s+الموضوع")),
    ("disposition", re.compile(r"^\s*القرار\s*:?\s*$|^\s*المنطوق\s*:?\s*$")),
    ("summary", re.compile(r"^\s*الملخص\s*:?\s*$|^\s*المفاتيح\s*:?\s*$")),
    ("facts", re.compile(r"^\s*الوقائع\s*:?\s*$")),
]
QUOTE_OPEN = '"“«'
QUOTE_CLOSE = '"”»'


def _digits(text, pos):
    for pat, form in ((NUM_IN_PARENS, "parens"), (NUM_BARE, "bare")):
        m = pat.match(text, pos)
        if m:
            return int(m.group(1)), m.group(0).strip(), m.end(), form
    return None, None, pos, None


def article_expression(text, pos):
    """Parse the article number that follows the head token at `pos`.

    Returns (number, surface form, end offset, how it was written) or a
    four-tuple of Nones when there is no number -- which is how «مادة الفحم»
    is separated from «المادة (4)» without a stop-word list.
    """
    m = NUM_AFTER_RAQM.match(text, pos)
    after_raqm = bool(m)
    if m:
        pos = m.end()
    n, surface, end, form = _digits(text, pos)
    if n is not None:
        return n, ("رقم " + surface) if after_raqm else surface, end, form
    m = ORD_IN_PARENS.match(text, pos)
    if m:
        n = parse_ordinal(m.group(1))
        if n is not None:
            return n, m.group(0).strip(), m.end(), "ordinal-parens"
        return None, None, pos, None
    phrase, end = ordinal_phrase(text, pos)
    if phrase.strip():
        n = parse_ordinal(phrase)
        if n is not None:
            return n, phrase.strip(), end, "ordinal"
    return None, None, pos, None


def paragraph(text, head_start, article_end):
    """Paragraph label, prefixed before the article or postfixed after it."""
    window = text[max(0, head_start - 90):head_start]
    hits = list(PARA_PREFIX.finditer(window))
    if hits:
        m = hits[-1]
        tail = window[m.end():]
        # the prefix must attach to this article, not sit two clauses back
        if len(tail) <= 20:
            label = m.group(1) or m.group(2)
            return label.strip(), "prefix"
    m = PARA_TRAILING_PARENS.match(text, article_end)
    if m and not m.group(1).isdigit():
        return m.group(1).strip(), "trailing-parens"
    m = PARA_POSTFIX.match(text, article_end)
    if m:
        label = m.group(1) or m.group(2) or m.group(3)
        if label and label.strip():
            return label.strip(), "postfix"
    return None, None


def instrument(text, article_end, max_hops=4):
    """The instrument named after the article, hopping coordinated articles.

    Returns (name, source) where source is 'local' when the instrument follows
    this article directly and 'list_trailing' when it follows a coordinated
    list this article belongs to.
    """
    pos, hops = article_end, 0
    while hops <= max_hops:
        m = INSTRUMENT_LINK.match(text, pos)
        if m:
            after = m.end()
            inst = INST.match(text, after)
            if inst:
                name = " ".join(inst.group(0).split())
                return name, ("local" if hops == 0 else "list_trailing")
            if ANAPHOR.match(text, pos):
                return None, "anaphora"
        # allow a coordinated article expression to intervene
        nxt = COORD.match(text[pos:pos + 40])
        if not nxt:
            # tolerate a page number or a line break before the link
            skip = re.match(r"^[\s ]*\d{1,4}[\s ]+", text[pos:])
            if skip and hops == 0:
                pos += skip.end()
                continue
            return None, None
        head = HEAD.search(text, pos, pos + 80)
        if not head:
            return None, None
        n, _, end, _ = article_expression(text, head.end())
        pos = end if n is not None else head.end()
        hops += 1
    return None, None


def resolve_anaphora(text, article_end, back=1800):
    """Bind «منها» / «ذات الالئحة» / «هذا النظام» to a named instrument.

    Returns (name, note). The note is non-empty when the binding is doubtful,
    and the caller must not treat a doubtful binding as a resolution.
    """
    m = ANAPHOR.match(text, article_end) or ANAPHOR.match(
        text, article_end + len(text[article_end:]) - len(text[article_end:].lstrip()))
    if not m:
        return None, "no anaphor"
    anaphor = " ".join(m.group(1).split())
    window = text[max(0, article_end - back):article_end]
    names = list(FULL_INST.finditer(window))
    if not names:
        return None, "anaphor with no antecedent in window"
    wants_regulation = any(w in anaphor for w in ("الالئحة", "اللائحة", "لائحته",
                                                  "الئحته"))
    wants_statute = "النظام" in anaphor and not wants_regulation
    for cand in reversed(names):
        name = " ".join(cand.group(0).split())
        is_reg = name.startswith(("الالئحة", "اللائحة", "لائحة", "الئحة"))
        if wants_regulation and not is_reg:
            continue
        if wants_statute and is_reg:
            continue
        return name, ""
    nearest = " ".join(names[-1].group(0).split())
    return None, (f"nearest antecedent «{nearest}» does not match the anaphor "
                  f"«{anaphor}»")


def attribution(text, pos):
    """Which section of the decision this citation sits in."""
    head = text[:pos]
    if head.count('"') % 2 == 1 or any(
            head.rfind(o) > head.rfind(c) >= -1 and head.rfind(o) > pos - 1200
            for o, c in zip(QUOTE_OPEN[1:], QUOTE_CLOSE[1:])):
        inside_quote = True
    else:
        inside_quote = False
    best, best_at = None, -1
    for line_match in re.finditer(r"[^\n]*", head):
        line = line_match.group(0)
        if not line.strip():
            continue
        for name, pat in SECTIONS:
            if pat.search(line):
                if line_match.start() > best_at:
                    best, best_at = name, line_match.start()
    if inside_quote:
        return "quotation", best
    return best, best


def parse(text, stages=None):
    """Every citation in `text`, one record each, with per-stage verdicts."""
    on = set(STAGES if stages is None else stages)
    out = []
    for head in HEAD.finditer(text):
        if "detection" not in on:
            continue
        rec = {"offset": head.start(), "token": head.group(0),
               "articleNumber": None, "articleForm": None, "articleWritten": None,
               "paragraph": None, "paragraphPosition": None,
               "instrument": None, "instrumentSource": None,
               "segment": None, "enclosingSection": None, "note": ""}
        n, surface, end, written = (article_expression(text, head.end())
                                    if "article" in on else (None, None, head.end(), None))
        if n is None:
            continue                      # not a citation: no number follows
        rec.update(articleNumber=n, articleForm=surface, articleWritten=written)
        if "paragraph" in on:
            label, where = paragraph(text, head.start(), end)
            rec.update(paragraph=label, paragraphPosition=where)
        if "instrument" in on:
            name, source = instrument(text, end)
            rec.update(instrument=name, instrumentSource=source)
            if source == "anaphora" and "anaphora" in on:
                m = INSTRUMENT_LINK.match(text, end)
                bound, note = resolve_anaphora(text, m.end() if m else end)
                rec["instrument"] = bound
                rec["note"] = note
        if "attribution" in on:
            seg, section = attribution(text, head.start())
            rec.update(segment=seg, enclosingSection=section)
        out.append(rec)
    return out
