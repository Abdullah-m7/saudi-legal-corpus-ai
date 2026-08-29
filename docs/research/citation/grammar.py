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

import bisect
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numerals import ORDINAL_RE, ordinal_phrase, parse_ordinal   # noqa: E402

STAGES = ("detection", "article", "paragraph", "instrument", "anaphora",
          "attribution")

# ---------------------------------------------------------------- detection

# «المادة», «للمادة», «بالمادة», «والمادة», «المادتين», and the bare «مادة».
# The dual «المادتين» and the plural «المواد» head citations of more than one
# article and are kept, because dropping them drops the citation.
HEAD = re.compile(r"(?:(?<=^)|(?<=[^ء-ي]))"
                  r"(?:[وفبكل]|لل|بال|كال|فال|وال)?"
                  r"(?:ال)?(?:ماد[ةت](?:ين|ي)?|مواد)(?![ء-ي])")

# ------------------------------------------------------- article expression

DIGITS = r"\d+"
NUM_IN_PARENS = re.compile(r"\s*\(\s*(" + DIGITS + r")\s*\)")
NUM_BARE = re.compile(r"\s*(" + DIGITS + r")(?![\d/])")
NUM_AFTER_RAQM = re.compile(r"\s*(?:رقم\s*)?[:：]?\s*(?=[\d(ء-ي])")
# «المادة (57/1)», «المادة 93/1», «المادة (2/ ب )». The pair is packed into
# one expression and -- this is the awkward part -- the corpus writes it in
# both orders: «93/1» is article 93 paragraph 1, «2/76» is article 76
# paragraph 2. See `packed` for how that is resolved and flagged.
PACKED = re.compile(r"\s*\(?\s*(\d+)\s*/\s*([\d]+|[ء-ي]{1,3})\s*\)?")
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
WHITESPACE = re.compile(r"\s*")
# an instrument name begins with one of these heads
# What an instrument name can begin with. «العقد» and «مجلة» are here because
# tribunals cite them the same way they cite a statute -- «المادة (16) من
# العقد», «المادة (2046) من مجلة الأحكام الشرعية» -- and a pipeline that
# silently drops them reports fewer citations than the court made. They are
# not legislation, and the record says which is which by its name.
INST_HEAD = (r"(?:الالئحة|اللائحة|لائحة|الئحة|لائحته|الئحته|النظام|نظام|"
             r"الاتفاقية|الإتفاقية|الاتفاقيه|اتفاقية|قواعد|القواعد|"
             r"تعليمات|التعليمات|قرار|القرار|المرسوم|مرسوم|الأمر|"
             r"العقد|عقد|مجلة|المجلة|مرافعات|إجراءات)")
# What ends an instrument name. The list is not decorative: without «تنص»
# the name swallowed «الالئحة التنفيذية لنظام الضريبة الانتقائية تنص», and
# without the coordinated-article terminator it swallowed a second citation
# whole -- «نظام ضريبة الدخل والمادة الثالثة والستين من الالئحة التنفيذية».
# Hard terminators end a name beyond argument: punctuation, a quotation mark,
# an issuing clause, the end of a line. Weak ones usually end it -- a relative
# pronoun, a verb of provision -- but only where the drafter happens to use
# them, and the two sources here do not use the same ones.
#
# The distinction matters because the inventory is built from hard
# terminators only. A name that ran on until a weak terminator, or until the
# 120-character bound, is not evidence of what the document calls anything,
# and letting such a span into the inventory lets it be picked as the
# "longest attested prefix" of the next over-run -- the corpus then confirms
# its own mistakes.
HARD = (r"،|؛|\.|:|\"|”|«|\n|\r|"
        r"الصادر|الصادرة|المصدقة|الموقعة|"
        r"-\s*\d|$")
WEAK = (r"على|التي|والتي|المتعلقة|والمتعلقة|بشأن|المشار|"
        r"تنص|ينص|نصت|نص|ونصها|ونصه|جاء|جاءت|حيث|وحيث|فإن|فقد|"
        r"و(?:ال)?(?:ماد[ةت]|فقرة|بند|تعميم|فتوى|قرار)")
STOP = HARD + r"|" + WEAK
INST = re.compile(INST_HEAD + r"(?:[^،؛.\n\r]{0,120}?)"
                  r"(?=\s*(?:" + STOP + r"))")
INST_CLEAN = re.compile(INST_HEAD + r"(?:[^،؛.\n\r]{0,120}?)"
                        r"(?=\s*(?:" + HARD + r"))")

# The same name, allowed to run across the line breaks that PDF wrapping puts
# inside it. Used only to propose a completion, never accepted on its own.
INST_WRAPPED = re.compile(INST_HEAD + r"(?:[^،؛.]{0,140}?)"
                          r"(?=\s*(?:" + STOP.replace(r"\n|\r|", "") + r"))")

# a coordinated article expression that stands between this one and the
# instrument, e.g. «المادة (13) والفقرة (2) من المادة (20) من الالئحة ...»
COORD = re.compile(r"^[\s,،؛]*(?:و|أو)?[\s]*(?:" + PARA_WORDS + r"|"
                   r"(?:[وفبكل]|لل|بال|كال|فال|وال)?(?:ال)?ماد[ةت])")

# ----------------------------------------------------------------- anaphora

# No «^» here: `pattern.match(text, pos)` anchors the match at pos, but «^»
# would still mean the start of the whole string, so it never fires.
ANAPHOR = re.compile(
    r"\s*(?:من\s*)?("
    r"منها|منه|"
    r"(?:ذات|هذه|تلك)\s*(?:الالئحة|اللائحة|الالئحه)|"
    r"(?:الالئحة|اللائحة|النظام)\s*(?:ذاتها|ذاته|نفسها|نفسه)|"
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
# Section markers, matched wherever they stand rather than at the start of a
# line. Ministry judgment text arrives as a single line with no breaks in it
# at all, so every line-anchored pattern silently matched nothing and every
# citation in the corpus came back with no section -- a stage reporting zero
# because of a newline, not because of the law.
#
# A marker is a heading word delimited on both sides. It opens after the end
# of a sentence, a bracket either way, a line break, or the start of the text
# -- because in judgment text with no line breaks the heading is introduced
# by a full stop and nothing else -- and it closes on a bracket, a colon, or
# a line break.
def _marker(*names):
    body = "|".join(names)
    return re.compile(r"(?:^|\n|[(){}\[\]]|[.؟!]\s)\s*(?:" + body
                      + r")\s*(?:\)|:|\uff1a|\n|$)")


SECTIONS = [
    ("authorities", _marker("المستند", "المستندات", "الاستناد", "الأسانيد")),
    ("party", re.compile(
        r"دفوع\s+(?:ال)?(?:أطراف|اطراف|مدعية|مدعي|مدعى\s*عليه|مستأنف|"
        r"المكلف|الهيئة)")),
    ("reasoning", re.compile(
        r"موقف\s+(?:اللجنة|الدائرة)|ولهذه\s+الأسباب|من\s+حيث\s+الموضوع|"
        + _marker("الأسباب", "األسباب", "الاسباب", "التسبيب",
                  "أسباب\s+الحكم").pattern)),
    # «الحكم» alone is not a marker: it is the commonest noun in the corpus.
    ("disposition", _marker("القرار", "المنطوق", "نص\s+الحكم",
                            "منطوق\s+الحكم")),
    ("summary", _marker("الملخص", "المفاتيح")),
    ("facts", _marker("الوقائع", "وقائع\s+الدعوى")),
]

# A citation inside a quoted legislative text is the drafter's, not the
# tribunal's: «دون الإخلال بالمادة الثانية من النظام» is what article 14 says,
# quoted by a panel that is citing article 14. Counting it as the panel's
# citation of article 2 attributes to a court words it did not choose.
#
# Quotation marks are not balanced across a whole decision -- a reporter opens
# one and never closes it -- so a parity count over the document is worthless.
# The test is local: within a short window, is the nearest quote mark before
# this point an opening one that has not been closed.
# A citation inside a quoted legislative text is the drafter's, not the
# tribunal's: «دون الإخلال بالمادة الثانية من النظام» is what article 14 says,
# quoted by a panel that is citing article 14. Counting it as the panel's own
# citation of article 2 attributes to a court words it did not choose.
#
# Quotation marks cannot be counted for parity. A reporter opens one and never
# closes it, and the straight mark is the same character either way, so a
# parity count over any window is arbitrary. What is not arbitrary is how
# Arabic legal drafting opens a quotation: a colon, or a verb of provision --
# «نصت المادة (14) على: "», «جاء فيها "», «التي تنص على ما يلي (». Bidi
# reordering moves the colon to the far side of the mark, so it is looked for
# on both.
OPENER_CUE = re.compile(
    r"(?::|على|فيها|يلي|الآتي|التالي|نصه|اآلتي)\s*$|^\s*(?::|أنه\s*:)")
QUOTE_MARKS = '"\u201c\u201d\u00ab\u00bb'
QUOTE_WINDOW = 1200


def _is_opener(text, i):
    ch = text[i]
    if ch in "\u201c\u00ab":
        return True
    if ch in "\u201d\u00bb":
        return False
    before, after = text[max(0, i - 14):i], text[i + 1:i + 10]
    return bool(OPENER_CUE.search(before) or OPENER_CUE.search(after))


def in_quotation(text, pos):
    """Whether `pos` falls inside quoted matter.

    The test is the nearest quotation mark before this point: an opener means
    inside, a closer means outside. Nothing further back is consulted, because
    nothing further back is reliable.
    """
    window_start = max(0, pos - QUOTE_WINDOW)
    for i in range(pos - 1, window_start - 1, -1):
        if text[i] in QUOTE_MARKS:
            return _is_opener(text, i)
    return False


# Who is speaking, where no heading says so. A decision narrates a party's
# argument inside its own account of the facts and gives it no heading; the
# verbs of saying are the only marker, and they are ordinary Arabic rather
# than one publisher's template.
PARTY_CUE = re.compile(
    r"(?:ذكرت?|دفعت?|أفادت?|توضح|أوضحت?|تطلب|طلبت?|تتمسك|تمسكت|تشير|أشارت?|"
    r"أجابت?|ترى|تعترض|اعترضت?|تدعي|ادعت|نصت مذكر)\s+"
    r"(?:ال)?(?:هيئة|مدعية|مدعي|مدعى\s*عليها?|مستأنف\w*|مكلف|شركة)"
    r"|وبعرض\s+(?:ال)?لائحة\s+الدعوى[^.\n]{0,60}أجابت"
    r"|دفوع\s+(?:ال)?(?:مدعية|مدعي|مستأنف|هيئة|أطراف|اطراف)")
TRIBUNAL_CUE = re.compile(
    r"(?:تبين|ثبت|اتضح|خلصت|انتهت|تنتهي|ترى|رأت|قررت|تقرر)\s+"
    r"(?:معه\s+)?(?:لدى\s+)?(?:ال)?(?:دائرة|لجنة|هيئة\s+الدائرة)"
    r"|(?:الدائرة|اللجنة)\s+(?:إلى|الى)\s+"
    r"|موقف\s+(?:اللجنة|الدائرة)"
    r"|(?:األمر|الأمر)\s+الذي\s+(?:تنتهي|يتعين|ترى)")
CUE_WINDOW = 420


def speaker(text, pos):
    """A party or the tribunal, from the verbs of saying nearest to `pos`."""
    window = text[max(0, pos - CUE_WINDOW):pos]
    party = max((m.end() for m in PARTY_CUE.finditer(window)), default=-1)
    tribunal = max((m.end() for m in TRIBUNAL_CUE.finditer(window)), default=-1)
    if party < 0 and tribunal < 0:
        return None
    return "party" if party > tribunal else "reasoning"


def packed(a, b):
    """Split «57/1» into an article and a paragraph, and say if it is a guess.

    When one side is a letter it is the paragraph and there is nothing to
    decide. When both are digits the order is not fixed in the corpus, and
    the only regularity that holds across every attested case is that the
    article is the larger number: paragraph numbers stay small, article
    numbers run into the hundreds. That is a heuristic, not a rule, so a
    record resolved this way is flagged `packedAmbiguous` and any count that
    depends on the article number can exclude it.
    """
    if not b.isdigit():
        return int(a), b, False
    x, y = int(a), int(b)
    if x == y:
        return x, b, True
    return (max(x, y), str(min(x, y)), True)


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
    after_raqm = bool(m) and "رقم" in m.group(0)
    if m:
        pos = m.end()
    m = PACKED.match(text, pos)
    if m:
        n, para, guessed = packed(m.group(1), m.group(2))
        return n, m.group(0).strip(), m.end(), ("packed-guess" if guessed
                                                else "packed"), para
    n, surface, end, form = _digits(text, pos)
    if n is not None:
        return (n, ("رقم " + surface) if after_raqm else surface, end, form,
                None)
    m = ORD_IN_PARENS.match(text, pos)
    if m:
        n = parse_ordinal(m.group(1))
        if n is not None:
            return n, m.group(0).strip(), m.end(), "ordinal-parens", None
        return None, None, pos, None, None
    phrase, end = ordinal_phrase(text, pos)
    if phrase.strip():
        n = parse_ordinal(phrase)
        if n is not None:
            return n, phrase.strip(), end, "ordinal", None
        # «المادتين الأولى والثانية» is two articles, and parse_ordinal
        # rightly refuses a phrase with two units in it. Take the first.
        first = ordinal_phrase(text, pos)[0].split(" و")[0]
        n = parse_ordinal(first)
        if n is not None:
            return n, phrase.strip(), end, "ordinal-multiple", None
    return None, None, pos, None, None


# «أولا», «ثانيا» and their kin enumerate paragraphs and are the same label
# whether the text writes «أولا» or, after the lam-alef ligature is decomposed
# and reordered, «أوال». They are folded to numbers so the two spellings stop
# being two labels.
ENUM = {}
for _i, _forms in enumerate(
        (("أولا", "أوال", "اولا", "اوال"),
         ("ثانيا", "ثانيا"), ("ثالثا",), ("رابعا",), ("خامسا",),
         ("سادسا",), ("سابعا",), ("ثامنا",), ("تاسعا",), ("عاشرا",)), start=1):
    for _f in _forms:
        ENUM[_f] = _i

LABEL_CHARS = r"[^\s()]{1,24}"
PARA_WORD = r"(?:الفقرات|الفقرتين|الفقرة|فقرة|البنود|البند|بند)"
# one paragraph expression: the word, then a label in brackets, an ordinal
# phrase, or a bare token
PARA_EXPR = re.compile(
    PARA_WORD + r"\s*(?:رقم\s*)?(?:"
    r"\(\s*(" + LABEL_CHARS + r")\s*\)"
    r"|(" + ORDINAL_RE.pattern + r"(?:\s*و?\s*" + ORDINAL_RE.pattern + r")*)"
    r"|(" + LABEL_CHARS + r")"
    r")")
# a bare bracketed number standing in for «الفقرة (1)»: «استنادا إلى (1) من
# المادة (5)» drops the word entirely and still means a paragraph
BARE_PARA = re.compile(r"\(\s*(\d+)\s*\)\s*من\s*$")
# what may sit between two coordinated paragraph expressions, and between the
# last of them and the article. Anything else ends the chain, so a paragraph
# belonging to an earlier citation is not attached to this one.
LINK = re.compile(r"^[\s,،؛]*(?:و|أو|ال)?[\s]*(?:من|في|رقم)?[\s]*$")


def _label(match):
    for group in match.groups():
        if group and group.strip():
            return group.strip()
    return None


def _chain_before(window):
    """Coordinated paragraph expressions ending at the end of `window`."""
    labels, end = [], len(window)
    while True:
        hits = [m for m in PARA_EXPR.finditer(window) if m.end() <= end]
        if not hits:
            break
        m = hits[-1]
        if not LINK.match(window[m.end():end]):
            break
        labels.append(_label(m))
        end = m.start()
    return list(reversed([l for l in labels if l]))


def _chain_after(text, pos):
    """Paragraph expressions following the article number."""
    labels = []
    while True:
        m = PARA_EXPR.match(text, pos) or re.compile(
            r"\s*").match(text, pos) and PARA_EXPR.match(
                text, re.compile(r"\s*").match(text, pos).end())
        if not m:
            break
        label = _label(m)
        if not label:
            break
        labels.append(label)
        pos = m.end()
    return labels


def paragraph(text, head_start, article_end):
    """Every paragraph label attached to this article, prefixed or postfixed.

    A list, not a single label: «الفقرة (أولا) والفقرة (أولا/5) والفقرة (8)
    من البند (أولا) من المادة (4)» cites three paragraphs of one article, and
    returning the last of them silently drops two.
    """
    window = text[max(0, head_start - 140):head_start]
    labels = _chain_before(window)
    where = "prefix" if labels else None
    if not labels:
        m = BARE_PARA.search(window)
        if m:
            labels, where = [m.group(1)], "prefix-bare"
    if not labels:
        m = PARA_TRAILING_PARENS.match(text, article_end)
        if m and not m.group(1).isdigit():
            labels, where = [m.group(1).strip()], "trailing-parens"
    after = _chain_after(text, article_end)
    if after:
        labels = labels + after
        where = where or "postfix"
    return (labels or None), where


def inventory(text, shared=None):
    """Instrument names stated cleanly, in this document and across the corpus.

    `shared` is a gazetteer built the same way from every document being
    processed. It is needed because a ministry judgment is short: an
    instrument may be named once in it and that once may run into the next
    clause, leaving the document with no clean statement of its own name.
    Across a few hundred judgments the same instruments are named cleanly
    many times, and the corpus can then tell a document what it meant.

    Only names, and only from hard-terminated mentions. Nothing about the
    content of one document reaches another.

    PDF line wrapping breaks names in the middle -- «قواعد عمل لجان الفصل في /
    المخالفات والمنازعات الضريبية» -- and a name truncated at the wrap is not
    the same instrument as the whole one. Extending blindly across the break
    is worse: in one digest the line that follows the break belongs to a
    different paragraph entirely, and extending would have invented a name.

    So the document is asked. A name that appears unbroken somewhere is
    available to complete a name broken elsewhere, and a completion that is
    not attested is refused. The inventory is per document and is never
    carried between documents.
    """
    counts = collections.Counter()
    names = {}
    for key, (name, n) in (shared or {}).items():
        names[key] = name
        counts[key] = n
    for m in INST.finditer(text):
        # only names that end at punctuation or at an issuing clause are
        # whole; one that ends at a line break is itself a broken name and
        # cannot be the authority for repairing another
        if text[m.end():m.end() + 2].lstrip(" ")[:1] in ("\n", "\r", ""):
            continue
        name = " ".join(m.group(0).split())
        if len(name.split()) >= 2 and '"' not in name and "”" not in name:
            key = _fold(name)
            names.setdefault(key, name)
            counts[key] += 1
    return {k: (v, counts[k]) for k, v in names.items()}


_FOLD_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})


def _fold(name):
    """Compare names ignoring spaces and orthographic variants.

    Three of the five development digests insert spaces inside words on
    justified lines -- «نظام المر افعات الشرعية» -- so a comparison that
    respects spaces reports two instruments where the document has one.
    """
    tight = "".join(name.split())
    # the transposed spellings first, while the orthography is still intact
    tight = tight.replace("الالئحة", "اللائحة").replace("الئحة", "لائحة")
    return tight.translate(_FOLD_MAP)


# Heads that name no instrument on their own. «الالئحة التنفيذية» is every
# implementing regulation in the corpus and «نظام» is every statute; a name
# truncated down to one of these has lost its identity, and completing it by
# picking the document's only other candidate is a guess dressed as a result.
_GENERIC_NAMES = ("اللائحة", "اللائحة التنفيذية", "لائحة", "الالئحة",
                  "الالئحة التنفيذية", "النظام", "نظام", "قواعد", "القواعد",
                  "قواعد عمل", "الاتفاقية", "اتفاقية", "الاتفاقية الموحدة",
                  "تعليمات", "التعليمات", "قرار", "القرار", "المرسوم")
ANAPHORIC_TAIL = re.compile(r"\s*(?:ذاتها|ذاته|نفسها|نفسه|المذكورة|المذكور)$")


MIN_ATTESTATIONS = 2
GENERIC = None          # filled below, once _fold exists


def resolve_name(text, start, fallback_end, stock, reach=150):
    """The instrument name at `start`, trimmed or extended to what is attested.

    One mechanism for two opposite failures, because they are the same
    failure. A name can run *short* -- PDF wrapping breaks «قواعد عمل لجان
    الفصل في / المخالفات والمنازعات الضريبية» across a line -- and it can run
    *long* -- «من نظام المحاكم التجارية والتي نصت على...», where no comma
    ends it. Both are answered by asking the document what names it states
    cleanly, and taking the longest one that begins what was read.

    A terminator list cannot do this. It is a guess about how one publisher
    punctuates, and the two sources here punctuate differently; the inventory
    is a fact about the document in hand.

    Returns None when no attested name begins the span, which is the correct
    answer for a name broken across a linearisation fault: nothing the
    document states starts with what is there.
    """
    span = text[start:min(len(text), start + reach)]
    span = re.split(r'[،؛."”\u061b]', span)[0]
    if span.count("\n") > 1:                  # at most one wrapped line
        span = span[:span.find("\n", span.find("\n") + 1)]
    # The SHORTEST attested prefix, not the longest. A name that ran on into
    # the next clause is itself attested somewhere -- the corpus repeats its
    # own mistakes -- so taking the longest match lets one over-run certify
    # the next. The shortest attested prefix is the name the corpus states
    # most tersely, which is the name.
    #
    # It also still repairs a wrapped name, because the truncated half is
    # never attested on its own: matches that end at a line break are kept
    # out of the inventory, so the shortest attested prefix of «الالئحة
    # التنفيذية لنظام ضريبة / القيمة المضافة» is the whole of it.
    best = None
    if stock:
        for end in range(1, len(span) + 1):
            if end < len(span) and span[end] not in " \n\r":
                continue
            key = _fold(span[:end])
            entry = stock.get(key)
            # attested more than once. A name the corpus states cleanly only
            # once may be one broken line rather than a name -- «نظام المر
            # افعات», where justification put a space inside the word -- and
            # the shortest-prefix rule would otherwise prefer exactly that.
            if entry and entry[1] >= MIN_ATTESTATIONS and key not in GENERIC:
                best = " ".join(span[:end].split())
                break
    if best:
        return best
    # nothing attested begins this span. Fall back to what the terminators
    # gave, bounded in tokens: an instrument name in either source is at most
    # eight words, and a longer "name" is a sentence that swallowed one.
    raw = " ".join(text[start:fallback_end].split())
    words = raw.split()
    if len(words) > 8:
        raw = " ".join(words[:8])
    return raw if _fold(raw) not in GENERIC else None


# How far back an instrument named before its article may sit, and what may
# stand between. «نظام الإثبات المادة 29» puts it immediately before; «بناء
# على المواد من نظام الإثبات: (92/2) ... والمادة (105/1)» puts it before a
# list. Anything that is not article, paragraph or coordination material ends
# the search, so a name from an unrelated clause is not picked up.
BACK_REACH = 220
# Words that may stand between an instrument and the article it governs.
# Checked token by token rather than by regex: the regex form of this test
# nests two unbounded quantifiers and backtracks catastrophically on a long
# gap, which is not a bug you notice in a unit test -- it is a run that never
# returns.
BRIDGE = {"و", "أو", "من", "في", "على", "التي", "والتي", "الذي", "نصت", "نص",
          "ونصها", "ونصه", "بأن", "أن", "رقم", "المادة", "المواد", "المادتين",
          "مادة", "الفقرة", "الفقرات", "الفقرتين", "البند", "البنود", "فقرة",
          "بند", "وفق", "وفقا", "بموجب", "وكذلك", "كما", "أيضا", "منها",
          "الآتي", "التالي", "ما", "هو", "قد", "ثم"}
BRIDGE_MAX = 12
_STRIP = " \t\n\r()[]،؛:.,/\u061b\u060c«»\"'"


def _bridges(gap):
    """True when nothing between the name and the article changes the subject."""
    tokens = [t.strip(_STRIP) for t in gap.split()]
    tokens = [t for t in tokens if t]
    if len(tokens) > BRIDGE_MAX:
        return False
    for token in tokens:
        if not token or token.isdigit():
            continue
        bare = token.lstrip("ولفبك") or token
        if token in BRIDGE or bare in BRIDGE:
            continue
        if ORDINAL_RE.fullmatch(token):
            continue
        return False
    return True


def preceding_instrument(text, head_start, stock):
    """An instrument named before the article rather than after it."""
    window_start = max(0, head_start - BACK_REACH)
    window = text[window_start:head_start]
    best = None
    for m in INST.finditer(window):
        gap = window[m.end():]
        if len(gap.split()) > 12:
            continue
        if not _bridges(gap):
            continue
        name = resolve_name(text, window_start + m.start(),
                            window_start + m.end(), stock)
        if name:
            best = name
    return best


def instrument(text, article_end, max_hops=4, stock=None):
    """The instrument named after the article, hopping coordinated articles.

    Returns (name, source). `source` is 'local' when the instrument follows
    this article directly, 'list_trailing' when it follows a coordinated list
    this article belongs to, 'anaphora' when what follows is a clitic for the
    next stage to bind, 'unresolved' when what follows is a bare head that
    names nothing, and None when nothing follows at all.
    """
    pos, hops = article_end, 0
    while hops <= max_hops:
        link = INSTRUMENT_LINK.match(text, pos)
        # «من» is sometimes simply absent: «المادة (41) نظام المرافعات
        # الشرعية», «المادة (8) الالئحة التنفيذية». Four of 118 hand-labelled
        # citations drop it, so its absence cannot end the search.
        after = link.end() if link else WHITESPACE.match(text, pos).end()
        inst = INST.match(text, after)
        source = "local" if hops == 0 else "list_trailing"
        if inst:
            raw = " ".join(inst.group(0).split())
            stem = ANAPHORIC_TAIL.sub("", raw)
            if ANAPHOR.match(text, pos) and _fold(stem) in GENERIC:
                return None, "anaphora"
            name = resolve_name(text, after, inst.end(), stock)
            if name:
                return name, source
            return None, "unresolved"
        if ANAPHOR.match(text, pos):
            return None, "anaphora"
        if not COORD.match(text[pos:pos + 40]):
            skip = re.match(r"^[\s ]*\d{1,4}[\s ]+", text[pos:])
            if skip and hops == 0:
                pos += skip.end()
                continue
            return None, None
        head = HEAD.search(text, pos, pos + 80)
        if not head:
            return None, None
        n, _, end, _, _ = article_expression(text, head.end())
        pos = end if n is not None else head.end()
        # a postfixed paragraph sits between the article and its instrument:
        # «المادة (4) البند ثانيا من لائحة جباية الزكاة»
        tail = PARA_EXPR.match(text, WHITESPACE.match(text, pos).end())
        if tail:
            pos = tail.end()
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
    # «ذاتها», «هذه», «نفسها» mean the one just named. If the one just named
    # is not of the kind the clitic asks for, the reference is broken and the
    # honest answer is that the document does not resolve it -- not the next
    # candidate back, which is a guess with a citation attached.
    proximal = any(w in anaphor for w in ("ذات", "هذه", "هذا", "تلك",
                                          "نفسها", "نفسه", "ذاتها", "ذاته"))
    if proximal:
        nearest = " ".join(names[-1].group(0).split())
        is_reg = nearest.startswith(("الالئحة", "اللائحة", "لائحة", "الئحة"))
        if (wants_regulation and not is_reg) or (wants_statute and is_reg):
            return None, (f"proximal anaphor «{anaphor}» but the nearest "
                          f"antecedent is «{nearest}»")
        return nearest, ""
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


# One pass, one pattern. Scanning line by line with six separate patterns
# took half a minute on a 1.2-megabyte digest, and the version before that
# rescanned the text before every citation and did not finish at all.
SECTION_SCAN = re.compile(
    "|".join("(?P<%s>%s)" % (name, pat.pattern) for name, pat in SECTIONS),
    re.MULTILINE)


def sections(text):
    """Where each section of the decision begins, in order. Once per document."""
    marks = []
    for m in SECTION_SCAN.finditer(text):
        if not marks or marks[-1][0] != m.start():
            marks.append((m.start(), m.lastgroup))
    return marks


def section_at(marks, pos):
    i = bisect.bisect_right(marks, (pos, "\uffff")) - 1
    return marks[i][1] if i >= 0 else None


def attribution(text, pos, marks=None):
    """Which part of the decision this citation belongs to.

    Two answers, deliberately. `section` is structural -- the last heading
    before this point -- and `segment` is what the citation is. They differ,
    and the difference is a finding rather than a defect: a decision that
    recounts a party's argument inside its own narrative gives no heading to
    say so, and no amount of heading matching will recover it.
    """
    marks = sections(text) if marks is None else marks
    section = section_at(marks, pos)
    if in_quotation(text, pos):
        return "quotation", section
    # A heading is authoritative where there is one. Where the decision has
    # given none -- inside its account of the facts, or before any heading at
    # all -- the verbs of saying are consulted instead.
    if section in (None, "facts", "summary"):
        return (speaker(text, pos) or section), section
    return section, section


def parse(text, stages=None, gazetteer=None):
    """Every citation in `text`, one record each, with per-stage verdicts."""
    on = set(STAGES if stages is None else stages)
    stock = inventory(text, gazetteer) if "instrument" in on else None
    marks = sections(text) if "attribution" in on else []
    out = []
    for head in HEAD.finditer(text):
        if "detection" not in on:
            continue
        rec = {"offset": head.start(), "token": head.group(0),
               "articleNumber": None, "articleForm": None, "articleWritten": None,
               "paragraph": None, "paragraphPosition": None,
               "packedAmbiguous": False,
               "instrument": None, "instrumentSource": None,
               "segment": None, "enclosingSection": None, "note": ""}
        n, surface, end, written, packed_para = (
            article_expression(text, head.end()) if "article" in on
            else (None, None, head.end(), None, None))
        if n is None:
            continue                      # not a citation: no number follows
        rec.update(articleNumber=n, articleForm=surface, articleWritten=written,
                   packedAmbiguous=(written == "packed-guess"))
        if "paragraph" in on:
            labels, where = paragraph(text, head.start(), end)
            if packed_para:
                labels = (labels or []) + [packed_para]
                where = where or "packed"
            rec.update(paragraph=labels, paragraphPosition=where)
        if "instrument" in on:
            # the instrument follows any paragraph postfixed to the article
            search_from = end
            for tail in (PARA_TRAILING_PARENS.match(text, end),
                         PARA_EXPR.match(text, WHITESPACE.match(text, end).end())):
                if tail:
                    search_from = max(search_from, tail.end())
            name, source = instrument(text, search_from, stock=stock)
            if name is None and source in (None, "unresolved"):
                earlier = preceding_instrument(text, head.start(), stock)
                if earlier:
                    name, source = earlier, "preceding"
            rec.update(instrument=name, instrumentSource=source)
            if source == "anaphora" and "anaphora" in on:
                bound, note = resolve_anaphora(text, search_from)
                rec["instrument"] = bound
                rec["note"] = note
        if "attribution" in on:
            seg, section = attribution(text, head.start(), marks)
            rec.update(segment=seg, enclosingSection=section)
        out.append(rec)
    return out


GENERIC = {_fold(_n) for _n in _GENERIC_NAMES}
