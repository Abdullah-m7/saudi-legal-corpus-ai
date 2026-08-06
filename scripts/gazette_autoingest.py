#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Industrial ingestion pipeline for Umm Al-Qura Official Gazette documents.

WHY THIS EXISTS
---------------
Tracks in this corpus were historically added one at a time, each with a
hand-written spec (title, dates, issuing decision, component type, track id)
and a hand-cloned generator/validator pair. That is accurate but does not
scale: the Gazette's own sitemap enumerates ~9,500 archived documents, of
which a few hundred are laws/regulations genuinely missing from the corpus.

This module turns that hand process into a deterministic pipeline that
derives every spec field FROM THE PAGE ITSELF and then refuses to emit a
track unless it passes an explicit battery of quality gates. Nothing is
guessed: a document that cannot be read cleanly is REJECTED WITH A REASON,
never force-built. The rejection report is a first-class output.

WHAT IT DOES NOT DO
-------------------
It does not fabricate, translate, paraphrase, summarize, renumber, or
"repair" legal text. It does not invent an issuing decision number: if the
gazette page does not state one, the emitted artifact says so and the
publication date is the only asserted anchor. It does not silently correct
source anomalies (numbering gaps, unfilled placeholders, typesetting
defects) — it detects them, refuses to build when they are unsafe, and
discloses them when they are safe.

PIPELINE
--------
  fetch (cached) -> parse -> segment -> GATES -> derive spec -> emit

GATES (a document must pass ALL of them)
  G1  title is legal-document shaped and is not an amendment/draft
  G2  not already covered by a live registry track. The decision is made on
      ARTICLE TEXT, matched by word shingles against every track in the unified
      index -- titles are the weaker signal in both directions. >= 
      DUPLICATE_OVERLAP is a duplicate ONLY if it is not published later than
      the track it matches -- a later re-issue amending a few articles scores in
      exactly that band, and rejecting it as a duplicate would keep superseded
      text; such a document is reported as G2-LATER-EDITION instead. >= GRAY_BAND
      is refused as a possible
      version difference needing human adjudication. The same GRAY_BAND applies
      to DOCUMENT-level containment, which is the only measure that sees the
      same instrument in an edited later edition (see document_overlap). And a
      body's «الترتيبات التنظيمية» is refused when the corpus already holds that
      same body's «تنظيم», which is its successor. Below all of that the document is
      distinct even if its title collides (Saudi practice issues legally
      distinct instruments under near-identical titles: an authority's «تنظيم»
      vs its «لائحة التراخيص»).
  G3  segmentation yields >= MIN_ARTICLES articles, OR -- for the large family
      of instruments drafted in ordinal bands («أولاً: ... ثانياً: ...») rather
      than in «مادة» -- a COMPLETE band run of >= MIN_BANDS starting at «أولاً»
      with no gap, OR -- for instruments drafted as a flat numbered list
      («1- ... 2- ...») -- a COMPLETE clause run of >= MIN_CLAUSES starting at 1
      with no gap and no decimal sectioning (see segment_clauses). A band or a
      clause is not an article and is never relabelled as one; the form is
      carried on the spec as `numbering_form`.
  G4  no empty / near-empty article bodies
  G5  no site-navigation or masthead boilerplate leaked into any article
  G6  no chapter-heading leaked into the tail of any article
  G7  no residual tashkeel or in-word decorative tatweel
  G8  any source-side article-numbering gap is SAFE: the missing ordinal
      appears nowhere in the document AND both neighbouring articles end on
      sentence-final punctuation (i.e. no two articles were merged into one
      record). Otherwise the document is rejected, not patched.
  G9  a curated track id must be supplied at emission time; the pipeline only
      proposes a triage slug (permanent identifiers are not machine-generated)
  G10 no article dwarfs the document's own median length, which would mean an
      unheaded annex/schedule block was absorbed into the preceding article.
      Before this gate runs, split_appendices() tries to CUT such a block off
      the last record at the gazette's own «الملحق N:» marks; G10 remains as
      the safety net for every block that cut cannot prove safe to separate
  G11 batch-level (see screen_batch): the same instrument must not reach the
      batch twice, and a document the batch's own text declares REPEALED must
      not be built as if in force. Neither is visible to a per-document gate.
  G12 the page is not a COUNCIL SESSION SUMMARY -- a list of unrelated decisions
      that the CMS titles after one of its items.
  G13 the records are prose provisions, not flattened reference TABLES.

Arabic governs throughout. Read-only over the corpus; the only writes are
the emitted artifacts under sources/ and scripts/, plus the JSON report.
"""

from __future__ import annotations

import difflib
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIN_ARTICLES = 5

# See G12/G13 in evaluate(). Both thresholds sit in a measured gap, not at a guess.
DECISION_OPENING_RE = re.compile(
    r"^(الموافقة\s+على|تفويض|اعتماد|قيام|الإذن\s+ل|الترخيص\s+ل|إنشاء\s+(?:هيئة|مركز|مجلس))")
SESSION_SUMMARY_RATIO = 0.60
NON_ARABIC_TOKEN_RE = re.compile(r"[A-Za-z0-9\u0660-\u0669]")
TABLE_DENSITY = 0.25
SHORT_ARTICLE_CHARS = 15
SENTENCE_FINAL = ".؟!:》”\"'）)"

# ---------------------------------------------------------------- normalisation

TASHKEEL = re.compile("[ً-ٰٟ]")  # excludes Arabic-Indic digits U+0660-0669
MADDA = r"ا\s*ل\s*م\s*ا\s*د\s*ة"  # tolerates stray intra-word spaces from typesetting
# The same word without its definite article. Used ONLY by the fallback segmenter: «مادة»
# alone is a common noun and matching it everywhere manufactures headings, but «النظام
# الموحد لإدارة نفايات الرعاية الصحية بدول مجلس التعاون» heads every one of its articles
# «مادة (6):» and reads as zero articles without it.
MADDA_LOOSE = r"(?:ا\s*ل\s*)?م\s*ا\s*د\s*ة"
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def strip_text(s: str) -> str:
    """Uniform display normalisation: drop tashkeel, decorative tatweel, and
    zero-width / bidi / non-breaking artifacts. Touches no letter, digit or
    ruling — consistent with every other track in this corpus."""
    s = TASHKEEL.sub("", s).replace("ـ", "")
    for junk in ("​", "‏", "‎", "\xa0"):
        s = s.replace(junk, " ")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def norm_ar(s: str) -> str:
    """Aggressive normalisation used only for comparison / dedup, never for
    stored text."""
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("ـ", "")
    for a in "أإآ":
        s = s.replace(a, "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"\s+", " ", re.sub(r"[^ء-ي\s]", " ", s)).strip()


# ---------------------------------------------------------------- Arabic ordinals

_UNIT = ["", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
         "السابعة", "الثامنة", "التاسعة", "العاشرة"]
_UNIT_C = ["", "الحادية", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
           "السابعة", "الثامنة", "التاسعة"]
_TENS = {20: "العشرون", 30: "الثلاثون", 40: "الأربعون", 50: "الخمسون",
         60: "الستون", 70: "السبعون", 80: "الثمانون", 90: "التسعون"}


def _base(n: int) -> str:
    if 1 <= n <= 10:
        return _UNIT[n]
    if 11 <= n <= 19:
        return _UNIT_C[n - 10] + " عشرة"
    if n in _TENS:
        return _TENS[n]
    u = n % 10
    return _UNIT_C[u] + " و" + _TENS[n - u]


def ordinal(n: int) -> str:
    if n <= 99:
        return _base(n)
    if n == 100:
        return "المائة"
    if n < 200:
        return _base(n - 100) + " بعد المائة"
    if n == 200:
        return "المائتان"
    return _base(n - 200) + " بعد المائتين"


_ORD_INDEX = None


def parse_ordinal(txt: str):
    global _ORD_INDEX
    if _ORD_INDEX is None:
        _ORD_INDEX = {norm_ar(ordinal(n)): n for n in range(1, 251)}
    return _ORD_INDEX.get(norm_ar(txt.strip().strip("()").strip()))


def _flex(o: str) -> str:
    return r"\s*\(?\s*" + r"\s+".join(re.escape(w) for w in o.split()) + r"\s*\)?\s*"


# ---------------------------------------------------------------- page parsing

CH_RE = re.compile(
    r"(الباب|الفصل)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر"
    r"|(?:الحادي|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)\s+عشر"
    r"|العشرون|التمهيدي)\b[:\s]*([^\n]{0,60}?)(?=\s*المادة|\s*$)")

# The heading of the NEXT structural unit, left at the end of an article's text.
#
# The leading boundary is load-bearing and was missing. Without it this pattern
# also matches a CROSS-REFERENCE to a chapter that happens to fall near the end
# of a sentence, and because it consumes everything to the end of the line, it
# deletes the rest of the provision with it. «قواعد الكفاية المالية», article 12,
# was stored as «... التعرّضات الخاضعة لمتطلبات رأس المال لمخاطر السوق المنصوص
# عليها في» — the gazette's own text continues «الفصل الثاني من هذا الباب، ولا
# يشمل ذلك التعرّضات لصفقات عقود المشتقات.», and the stripper took all of it
# because the sentence said «في الفصل الثاني».
#
# A cross-reference to a chapter is introduced by a PREPOSITION — «المنصوص عليها
# في الفصل الثاني», «الواردة في الباب الثالث». A stacked heading is introduced by
# nothing at all: it simply follows the previous unit's last word or its own
# parent heading. Testing the preceding token is what separates them, and it is a
# fact about the two strings rather than a reading of them.
#
# Anchoring on a sentence end instead was tried and is wrong in the other
# direction: «... التنقيب عن الآثار الفصل الأول: المسح الأثري» is a genuine
# stacked heading that follows a noun, not a full stop, and would survive.
#
# The chapter words also carry the gazette's stray intra-word spaces — «ا لباب
# الثالث» appears in «اللائحة التنفيذية لنظام الآثار والمتاحف والتراث العمراني» —
# so they are matched with the same space tolerance as «المادة». Without it the
# outer heading of a stacked pair cannot be stripped once the inner one is gone.
# Only prepositions that can INTRODUCE a following noun. The pronoun-suffixed
# forms — «بها», «عليه», «إليها» — close a phrase instead of opening one, and
# putting them here suppressed genuine headings: «... والتقيد بها. الفصل الخامس:
# أحكام عامة» was read as a citation because the token before «الفصل» was «بها».
_CH_PREPOSITIONS = {"في", "من", "إلى", "الى", "على", "وفق", "وفقا", "وفقاً",
                    "بموجب", "حسب", "ضمن", "بحسب"}
# A preposition that ends a SENTENCE is not introducing what follows it either.
_SENTENCE_END = ".؛:!؟"
_BAB = r"ا\s*ل\s*ب\s*ا\s*ب"
_FASL = r"ا\s*ل\s*ف\s*ص\s*ل"
_CH_ORDINAL = (r"(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر"
               r"|(?:الحادي|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)\s+عشر"
               r"|العشرون|التمهيدي)")
TRAILING_CH_RE = re.compile(
    r"\s*(" + _BAB + r"|" + _FASL + r")\s+" + _CH_ORDINAL + r"\s*:?\s*[^\n]{0,90}$")
# The same opening, without the run-to-end-of-line tail: used only to enumerate
# candidate positions so each can be tested where it sits.
CH_WORD_RE = re.compile(r"\s*(" + _BAB + r"|" + _FASL + r")\s+" + _CH_ORDINAL)


def trailing_chapter_heading(txt):
    """The match, if the tail is a stacked HEADING rather than a cross-reference.

    Python cannot express «not preceded by any of these words» as a lookbehind
    (they are not all the same width), so the preceding token is read off the
    string instead. That keeps the decision in one place and lets it be stated
    plainly: a chapter word introduced by a preposition is a citation, and
    deleting it deletes the rest of the provision with it.

    EVERY candidate is examined, and the LAST admissible one wins. Stopping at the
    leftmost match and giving up when it turned out to be a citation was measured
    and is wrong in the other direction: «... المنصوص عليها في الباب الثالث من هذه
    القواعد. الباب الثاني قاعدة رأس المال» carries a citation AND, after it, a real
    heading — and rejecting on the citation left the heading inside the article."""
    best = None
    # finditer over TRAILING_CH_RE itself cannot be used: its first match runs to
    # the end of the line, so a heading that FOLLOWS a citation is inside that
    # match and never offered as a candidate of its own. Candidate positions are
    # located separately and each is tested where it sits.
    for c in CH_WORD_RE.finditer(txt):
        m = TRAILING_CH_RE.match(txt, c.start())
        if not m:
            continue
        before = txt[:c.start()].rstrip()
        if before and before[-1] in _SENTENCE_END:
            best = m
            continue
        last = re.split(r"[\s،؛]", before)[-1] if before else ""
        if last.strip("،()") in _CH_PREPOSITIONS:
            continue
        best = m
    return best

# Both heading conventions used by the Gazette: Arabic feminine ordinals
# ("المادة الخامسة:") and explicit digits ("المادة (5):", Western or
# Arabic-Indic). A trailing colon is mandatory, which is what excludes
# in-text cross-references such as "المادة (التاسعة) من اللائحة".
# A heading's terminator is a colon OR a dash. The gazette uses both, and often the
# dash alone: «المادة (1) – التعريفات يقصد بالألفاظ ...» carries no colon anywhere, so
# a colon-only rule read «اللائحة التنفيذية لمنع ومعالجة تلوث التربة» as zero articles
# and G3 refused it. 42 uncovered pages were blocked this way, among them substantial
# environmental and technical regulations.
TERMINATOR = r"[:\u2013\u2014\-]"

HEADING_RE = re.compile(
    MADDA +
    r"(?:"
    # digit form — unambiguous, so an inline heading title before the terminator is
    # safe, and the terminator may sit on either side of that title:
    #   «المادة (5):»  «المادة (5) المصطلحات والتعاريف:»  «المادة (5) – التعريفات»
    #   «المادة (2): – نطاق التطبيق»
    r"\s*\(\s*(?P<d1>[0-9\u0660-\u0669]{1,4})\s*\)\s*" + TERMINATOR +
    r"|\s*\(\s*(?P<d2>[0-9\u0660-\u0669]{1,4})\s*\)(?:[^:\n]{0,40})?:"
    # ordinal form — the colon must follow the ordinal directly (optionally after a
    # duplicated digit, «المادة الخامسة (5):»). Keeping this strict is what excludes
    # in-text cross-references such as «المادة (التاسعة) من اللائحة».
    r"|\s*\(?\s*(?P<ord>[^\s:\n()\.،؛][^:\n()\.،؛]{0,44}?)\s*\)?"
    r"\s*(?:\(\s*[0-9\u0660-\u0669]{1,4}\s*\))?\s*:"
    r")")

# The permissive heading pattern, used ONLY when the strict one finds too little to be
# a document. It drops the definite article and makes the terminator optional, because
# the gazette does head articles «المادة (5) تحديد المواقع ذات التربة الملوثة 1- يقوم
# المركز ...» with no punctuation at all.
#
# It is a FALLBACK rather than a widening, and the difference was measured: applied to
# every page, it changes the article count on two of the 397 already-built pages that
# segment correctly today — phantom headings picked up from running text. Applied only
# where the strict pattern yields less than MIN_ARTICLES, it cannot touch those pages at
# all, and it still recovers the documents that strictness was refusing.
#
# It also carries two placements of the number that the strict pattern does not admit,
# each found by reading the documents the gates were still refusing:
#   * the colon BEFORE the parenthesis — «المادة: (1) المصطلحات والتعاريف» heads every
#     article of «اللائحة الفنية للصهاريج – الجزء الثاني», which read as two articles;
#   * a BARE digit with no parenthesis at all — «المادة 1: يقصد بالتعابير ...», the form
#     used by «اتفاقية تنظيم النقل بالعبور بين الدول العربية» and «اتفاقية لاهاي بشأن
#     إلغاء إلزامية المصادقة على الوثائق العمومية الأجنبية». The bare form REQUIRES its
#     terminator — «المادة 5 من نظام كذا» must stay a citation — and it is placed ahead
#     of the ordinal alternative, which would otherwise capture the digit as an ordinal
#     word and then discard it for not parsing.
HEADING_RE_LOOSE = re.compile(
    MADDA_LOOSE +
    r"(?:"
    r"\s*(?::\s*)?\(\s*(?P<d1>[0-9\u0660-\u0669]{1,4})\s*\)\s*" + TERMINATOR + r"?"
    r"|\s*(?::\s*)?\(\s*(?P<d2>[0-9\u0660-\u0669]{1,4})\s*\)(?:[^:\n]{0,40})?:"
    r"|\s+(?P<d3>[0-9\u0660-\u0669]{1,4})\s*" + TERMINATOR +
    r"|\s*\(?\s*(?P<ord>[^\s:\n()\.،؛][^:\n()\.،؛]{0,44}?)\s*\)?"
    r"\s*(?:\(\s*[0-9\u0660-\u0669]{1,4}\s*\))?\s*:"
    r")")

NAV_MARKERS = ("نسخة تجريبية", "الرئيسية القرارات", "تسجيل الدخول", "اشترك في نشرتنا")


def page_text(path: str):
    """Return (title, body) with scripts/styles/nav/footer removed."""
    html = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = strip_text(m.group(1)) if m else ""
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", html).replace("&nbsp;", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    end = t.find("{{ art.hijri_date }}")
    if end == -1:
        end = t.find("جميع الحقوق محفوظة")
    t = t[:end] if end > 0 else t
    if "طباعة" in t[:6000]:            # last item of the site nav / share bar
        t = t.split("طباعة", 1)[1]

    # The CMS truncates its own <title> tag at ~70 characters and appends an
    # ellipsis, which would store a CLIPPED legal title as the document name
    # (e.g. "اللائحة التنفيذية لنظام تنفيذ اتفاقية حظر تطوير وإنتاج وتكديس الأسل...").
    # The untruncated title is the page's first heading line, immediately above
    # the publication date. Prefer it, but only when it genuinely extends the
    # clipped stem -- never substitute an unrelated line.
    if title.endswith("...") or title.endswith("…"):
        stem = title.rstrip(".…").strip()
        for line in t.split("\n"):
            line = strip_text(line)
            if line.startswith(stem[:40]) and len(line) > len(stem):
                title = line
                break
    return title, t


def chapters(body: str):
    return [(m.start(), f"{m.group(1)} {m.group(2)}", strip_text(m.group(3)))
            for m in CH_RE.finditer(body)]


# ---------------------------------------------------------------- ordinal bands
# A large family of Saudi instruments is not drafted in «مادة» at all. Controls,
# rules, executive mechanisms and many «ترتيبات تنظيمية» are drafted as ordinal
# BANDS -- «أولاً: يقصد بالعبارات ...  ثانياً: يجب الالتزام ...» -- and the
# article segmenter, which only knows «المادة», reads such a page as zero
# articles and G3 rejects it as unparseable. 45 instruments the corpus does not
# hold were being refused for this reason alone, among them «الترتيبات
# التنظيمية لهيئة الصحة العامة»، «قواعد مراقبة عقارات الدولة وإزالة التعديات»
# and «ضوابط الإعلانات العقارية». The text was on the page the whole time; the
# pipeline simply had no name for its shape.
#
# A band is NOT an article, and the distinction is preserved rather than papered
# over: the band's own label is carried verbatim, and the integer beside it is
# positional, used for ordering and keying only.
_BAND_WORDS = ["أول", "ثاني", "ثالث", "رابع", "خامس", "سادس", "سابع", "ثامن", "تاسع",
               "عاشر", "حادي عشر", "ثاني عشر", "ثالث عشر", "رابع عشر", "خامس عشر",
               "سادس عشر", "سابع عشر", "ثامن عشر", "تاسع عشر", "عشرون", "عشرين"]
_BAND_NUM = {w: i for i, w in enumerate(_BAND_WORDS, 1)}
_BAND_NUM["عشرين"] = 20
def _tatweel_tolerant(word):
    """The gazette stretches words with decorative tatweel — «ثالثـــاً» — and a
    plain alternation misses exactly those headings, which is worse than missing
    all of them: the run then has a hole in it and the whole document is refused
    as unbanded. Allow tatweel between any two characters, and a run of spaces
    where the word itself has one («حادي عشر»)."""
    parts = [r"\s+" if ch == " " else re.escape(ch) for ch in word]
    return r"\u0640*".join(parts)


BAND_RE = re.compile(
    r"(?:(?<=\s)|^)((?:%s)\u0640*(?:اً|ًا|ا|ً)?)\s*[:：]"
    % "|".join(_tatweel_tolerant(w) for w in _BAND_WORDS))

MIN_BANDS = 4


def segment_bands(body: str):
    """Ordinal-band headings in document order -> (bands, diagnostics).

    Deliberately stricter than the article segmenter. An article list may
    legitimately have gaps (a repealed article is simply absent) and the
    article segmenter reconstructs the longest increasing run to survive stray
    cross-references. A banded instrument has no such freedom: its bands are a
    short, complete enumeration that starts at «أولاً» and runs without a gap.
    Requiring exactly that is what stops an in-text «ثانياً:» inside a list from
    being read as a structural heading -- if the run does not start at one and
    close without gaps, this is not a banded instrument and nothing is
    returned."""
    hits = []
    for m in BAND_RE.finditer(body):
        base = m.group(1).replace("\u0640", "")
        for suf in ("ًا", "اً", "ا", "ً"):
            if base.endswith(suf):
                base = base[: -len(suf)]
                break
        n = _BAND_NUM.get(re.sub(r"\s+", " ", base).strip())
        if n:
            hits.append((n, m.start(), m.end(), m.group(1)))

    seen, ordered = set(), []
    for h in hits:
        if h[0] in seen:
            continue
        seen.add(h[0])
        ordered.append(h)
    if not ordered:
        return [], {"count": 0, "max": 0, "missing": []}
    nums = [h[0] for h in ordered]
    if nums != list(range(1, len(nums) + 1)):
        return [], {"count": 0, "max": 0, "missing": []}

    bands = []
    for i, (num, s, e, label) in enumerate(ordered):
        nxt = ordered[i + 1][1] if i + 1 < len(ordered) else len(body)
        # The tatweel in «ثالثـــاً» is typesetting, not orthography, and the
        # pipeline already strips it from body text at G7. The label is stored
        # the same way, so the band reads as the gazette wrote the WORD.
        bands.append((num, label.replace("\u0640", ""), strip_text(body[e:nxt]),
                      ("", "")))
    return bands, {"count": len(bands), "max": len(bands), "missing": []}


# A third drafting form, and the one that is easiest to read wrongly. A sizeable
# family of «قواعد / ضوابط / إجراءات» is published as a flat numbered list —
# «1- ... 2- ... 3- ...» — with no «مادة» heading and no ordinal band anywhere in
# it, so both segmenters above return nothing and G3 refuses the document. Seven
# instruments in the measured backlog are shaped exactly that way, among them
# «إجراءات طلبات التنفيذ المقدمة من الجهات الإدارية» (14 clauses) and «قواعد نظر
# دعاوى إلغاء القرارات المتعلقة بتطبيق أحكام أوامر الطوارئ» (8).
#
# The danger is the mirror image of the opportunity: a numbered list is also the
# commonest INCIDENTAL structure in Arabic legal prose — a definitions list, an
# exceptions list nested inside one article. Reading such a list as the
# instrument's own division would invent a structure the gazette never gave it.
# Four conditions separate the two, and all four must hold:
#
#   * the run is complete and gap-free from 1 (same rule as the bands, and for
#     the same reason: an incidental list rarely enumerates the whole document);
#   * it is at least MIN_CLAUSES long — set above MIN_ARTICLES deliberately,
#     because a bare digit is far weaker evidence of structure than the word
#     «المادة» is;
#   * the article and band segmenters both came up short first, so a document
#     that IS article-drafted is never re-read as clauses (measured: «اللائحة
#     التنظيمية لتصنيف الوسائط البحرية» segments to 6 articles, and its
#     exceptions list 1-9 sits INSIDE article four);
#   * the document is not decimally sectioned. The railway guides head their
#     sections «1.1، 2.1، 3.1» and also carry a short flat run; the decimal
#     markers are the real division and the flat run is not.
CLAUSE_RE = re.compile(r"(?:(?<=\s)|^)([0-9٠-٩]{1,3})\s*[-–—]\s*(?=[ء-ي])")
DECIMAL_SECTION_RE = re.compile(r"(?<![\d.])\d{1,2}\.\d{1,2}(?![\d.])")
MIN_CLAUSES = 6


def segment_clauses(body: str):
    """Flat numbered clauses in document order -> (clauses, diagnostics).

    Returns nothing at all unless the run is a complete 1..N enumeration; see
    the note above for why every one of the four conditions is load-bearing."""
    hits = []
    for m in CLAUSE_RE.finditer(body):
        try:
            n = int(m.group(1).translate(_ARABIC_DIGITS))
        except ValueError:
            continue
        hits.append((n, m.start(), m.end(), m.group(1)))

    nums = [h[0] for h in hits]
    if len(nums) < MIN_CLAUSES or nums != list(range(1, len(nums) + 1)):
        return [], {"count": 0, "max": 0, "missing": []}
    if len(DECIMAL_SECTION_RE.findall(body)) >= len(nums):
        return [], {"count": 0, "max": 0, "missing": []}

    clauses = []
    for i, (num, s, e, label) in enumerate(hits):
        nxt = hits[i + 1][1] if i + 1 < len(hits) else len(body)
        # The label is stored as the gazette printed the NUMBER — Arabic-Indic
        # digits stay Arabic-Indic — because the clause is cited by that mark.
        clauses.append((num, "%s-" % label, strip_text(body[e:nxt]), ("", "")))
    return clauses, {"count": len(clauses), "max": len(clauses), "missing": []}


# ------------------------------------------------------------------- appendices
# An instrument's ANNEX BLOCK carries no «المادة N:» heading, so the article
# segmenter has nothing to end the last article on and the whole block — forms,
# prospectus contents, declaration templates — is absorbed into it. G10 catches
# the result and refuses the document, which is right as a safety net and wrong
# as an outcome: the text is on the page, correctly, and only its boundary is
# missing. Measured: the 2026 consolidation of «قواعد طرح الأوراق المالية
# والالتزامات المستمرة» absorbed thirty annexes into article 112 — 268,802 chars
# against a 667-char median — and was refused for that alone.
#
# The hard part is that the annex MARK is also the commonest cross-reference in
# the same document — thirty-eight headings against some seventy references in
# the CMA rules alone — and the two are not told apart by their punctuation.
# «الملحق 1:» heads a block there while «الملحق (9)» cites one, but the technical
# regulations invert it: «ملحق رقم (1): الشعار الوطني» heads a block in the
# organic-farming guide and «كما ورد في ملحق (4)» cites one. Keying on the
# parentheses would therefore read one family right and the other backwards.
#
# What does separate them, in every document measured, is the SENTENCE AROUND
# the mark — the same lesson the chapter stripper above had to learn:
#
#     citation   «... متطلبات السلامة المنصوص عليها في الملحق (2) من هذه اللائحة»
#     citation   «... يحدد الملحق (14) من هذه القواعد الحد الأدنى للمعلومات ...»
#     heading    «... نافذة وفقا لقرار اعتمادها.  الملحق 1: محتويات مستند الطرح»
#
# A citation is either introduced by a preposition or closed by a back-reference
# to the instrument itself («من هذه القواعد»، «من هذا الدليل»). Requiring a
# candidate to survive BOTH tests is what makes the two families read alike;
# neither test alone is sufficient, because «يحدد الملحق (14) من هذه القواعد»
# opens on a verb and «كما ورد في ملحق (4).» closes on a full stop.
#
# Four further conditions hold the split to cases where no judgement is needed:
#
#   * only the LAST record is split. An annex heading anywhere else would mean
#     the block is interleaved with provisions, and cutting there would move
#     normative text out of its article;
#   * the run is complete and gap-free from 1 (an incomplete run means some
#     heading was not recognised, and a partial cut is worse than none);
#   * at least MIN_APPENDICES of them, so a lone «الملحق 1:» inside prose cannot
#     amputate an article;
#   * the host record keeps substantive text of its own and ends sentence-final
#     once its trailing chapter heading («الباب الثالث عشر الملاحق») is stripped.
#     If the cut would leave the article empty or mid-sentence, the reading was
#     wrong and nothing is split.
APPENDIX_RE = re.compile(
    r"(?:(?<=\s)|^)(?:ال)?ملحق\s*(?:رقم\s*)?"
    r"(?:\(\s*(?P<pn>[0-9٠-٩]{1,3})\s*\)|(?P<n>[0-9٠-٩]{1,3}))"
    r"\s*(?:\(\s*(?P<letter>[ء-ي])\s*\)\s*)?[:：]?")
# A candidate introduced by one of these is a citation, not a heading.
_APPENDIX_CITE_BEFORE = {"في", "من", "إلى", "الى", "على", "وفق", "وفقا", "وفقاً",
                         "بموجب", "حسب", "بحسب", "ضمن", "بمقتضى", "لـ", "و"}
# ... and so is one closed by a back-reference to the instrument itself, or by a
# conjunction naming a second annex — «الملحق (3) أو الملحق (4) من هذه القواعد»
# opens on the noun «متطلبات» and so passes the test above, and only the «أو»
# that follows it says it is one item of a citation list rather than a heading.
_APPENDIX_CITE_AFTER = re.compile(
    r"\s*(?:(?:من|في|ل)\s*(?:هذه|هذا|قواعد|لائحة|دليل|نظام)|(?:أو|و)\s*(?:ال)?ملحق)")
MIN_APPENDICES = 3
MIN_HOST_TAIL = 40


def _appendix_headings(text):
    """Annex-heading matches only — citations of an annex are dropped."""
    out = []
    for m in APPENDIX_RE.finditer(text):
        before = text[:m.start()].rstrip()
        last = re.split(r"[\s،؛]", before)[-1] if before else ""
        if last.strip("،()") in _APPENDIX_CITE_BEFORE:
            continue
        if _APPENDIX_CITE_AFTER.match(text[m.end():]):
            continue
        out.append(m)
    return out


def split_appendices(arts):
    """Cut a trailing annex block off the last record.

    Returns (arts, appendices). `appendices` is a list of
    (index, label_ar, text, letter) in document order; it is empty — and `arts`
    is returned untouched — whenever any condition above fails.
    """
    if not arts:
        return arts, []
    num, label, text, ch = arts[-1]
    hits = [(m.start(), m.end(), m.group("pn") or m.group("n"), m.group("letter"))
            for m in _appendix_headings(text or "")]
    if len(hits) < MIN_APPENDICES:
        return arts, []
    try:
        nums = [int(h[2].translate(_ARABIC_DIGITS)) for h in hits]
    except ValueError:
        return arts, []
    if sorted(set(nums)) != list(range(1, max(nums) + 1)) or nums != sorted(nums):
        return arts, []

    # Any annex heading in an EARLIER record means the block is interleaved.
    for a in arts[:-1]:
        if _appendix_headings(a[2] or ""):
            return arts, []

    host = strip_text(text[:hits[0][0]])
    m = trailing_chapter_heading(host)
    if m:
        host = strip_text(host[:m.start()])
    if len(host) < MIN_HOST_TAIL or host.rstrip()[-1:] not in SENTENCE_FINAL:
        return arts, []

    appendices = []
    for i, (s, e, digits, letter) in enumerate(hits):
        nxt = hits[i + 1][0] if i + 1 < len(hits) else len(text)
        # The label is stored as the gazette printed it, letter suffix and all,
        # because «الملحق 9 (أ)» is cited by that mark and is not annex 9.
        lab = "الملحق %s" % digits + (" (%s)" % letter if letter else "")
        appendices.append((i + 1, lab, strip_text(text[e:nxt]), letter or ""))

    return arts[:-1] + [(num, label, host, ch)], appendices


def segment(body: str, pattern=None):
    """Article headings in document order -> (articles, diagnostics).

    Robustness: every heading candidate is resolved to an integer, then the
    longest strictly-increasing subsequence is kept. A spurious match (an
    in-text cross-reference that happens to be followed by a colon) is
    therefore dropped on its own, instead of truncating every genuine
    heading that follows it.
    """
    cands = []
    for m in (pattern or HEADING_RE).finditer(body):
        # Named groups, because the two patterns admit different numbers of digit
        # placements and positional groups would silently shift under the next one.
        g = m.groupdict()
        digits = g.get("d1") or g.get("d2") or g.get("d3")
        if digits is not None:
            try:
                n = int(digits.translate(_ARABIC_DIGITS))
            except ValueError:
                continue
            if not 1 <= n <= 999:
                continue
        else:
            n = parse_ordinal(g.get("ord"))
            if n is None:
                continue
        # A CROSS-REFERENCE, not a heading: «المادة الثالثة (فقرة - 1) من تنظيم الهيئة
        # السعودية للمواصفات». A real heading is followed by the article's own words; a
        # citation is followed by «من» and the name of the instrument it cites. Without
        # this, loosening the terminator turns every citation into a phantom article.
        tail = body[m.end():m.end() + 16].lstrip()
        if tail.startswith("من ") or tail.startswith("منه") or tail.startswith("وما "):
            continue
        # Extending the same preposition test to ARTICLE headings — «الاشتراطات
        # الواردة في مادة (8) أو وحدة تجميد» is a citation the tail rule cannot see,
        # because its tail is «أو» — was tried and is NOT kept. Measured on the two
        # articles it was meant to repair, it made both worse: «اتفاقية ربط أنظمة
        # المدفوعات الخليجية» article 13 swallowed article 14 whole, and the GCC
        # healthcare-waste article 7 came out shorter than it is stored. The
        # interaction with the longest-increasing-subsequence reconstruction is not
        # understood well enough to ship, and a segmenter change that silently
        # merges two articles is worse than the fragment it was fixing.
        #
        # The two affected records stay as they are and are disclosed by
        # audit_corpus_text_quality.py, which is the honest state: a known defect
        # named in a report beats an unverified fix in the segmenter.
        cands.append((n, m.start(), m.end()))

    if not cands:
        if pattern is None:
            return segment(body, HEADING_RE_LOOSE)
        return [], {"count": 0, "max": 0, "missing": []}

    import bisect
    tails, idx, prev = [], [], [-1] * len(cands)
    for i, (n, _s, _e) in enumerate(cands):
        j = bisect.bisect_left(tails, n)
        if j == len(tails):
            tails.append(n)
            idx.append(i)
        else:
            tails[j] = n
            idx[j] = i
        prev[i] = idx[j - 1] if j > 0 else -1
    seq, cur = [], idx[len(tails) - 1]
    while cur != -1:
        seq.append(cur)
        cur = prev[cur]
    hits = [cands[i] for i in reversed(seq)]

    chs = chapters(body)

    def chapter_at(pos):
        cur = ("", "")
        for cp, lab, ttl in chs:
            if cp <= pos:
                cur = (lab, ttl)
            else:
                break
        return cur

    arts = []
    for i, (num, s, e) in enumerate(hits):
        nxt = hits[i + 1][1] if i + 1 < len(hits) else len(body)
        txt = strip_text(body[e:nxt])
        while True:                              # headings can stack: «الباب X الفصل Y»
            m = trailing_chapter_heading(txt)
            if not m:
                break
            txt = txt[:m.start()]
        arts.append((num, ordinal(num), strip_text(txt), chapter_at(s)))

    present = {a[0] for a in arts}
    missing = [n for n in range(1, max(present) + 1) if n not in present]
    diag = {"count": len(arts), "max": max(present), "missing": missing}
    # Fall back when the strict pattern found too little to be a document, and ALSO
    # when what it found has holes in it: «اللائحة التنفيذية لمنع ومعالجة تلوث التربة»
    # segments to articles 1-4, 7, 8 because 5 and 6 are headed with no punctuation at
    # all, and a run with holes is itself the signal that headings were missed.
    #
    # The loose result is accepted only if it is strictly larger AND gap-free. That
    # second condition is the safety: a permissive pattern that picks phantom headings
    # out of running text produces a run with holes, so it cannot win by being sloppier.
    if pattern is None and (diag["count"] < MIN_ARTICLES or diag["missing"]):
        loose_arts, loose_diag = segment(body, HEADING_RE_LOOSE)
        if loose_diag["count"] > diag["count"] and not loose_diag["missing"]:
            return loose_arts, loose_diag
    return arts, diag


# ---------------------------------------------------------------- spec derivation

DATE_RE = re.compile(r"(\d{3,4})-(\d{1,2})-(\d{1,2})\s*الموافق\s*(\d{2})-(\d{2})-(\d{4})")

DECISION_RE = re.compile(
    r"(?:الصادر(?:ة)?\s+(?:عن|بموجب|ب)|المعتمدة\s+ب|اعتمدت\s+ب|صدرت\s+ب|"
    r"[اأ]صدرت\s+هذه\s+(?:اللائحة|القواعد)\s+بموجب)\s*"
    r"((?:قرار|مرسوم)[^\n]{0,150}?رقم\s*\(?\s*[^\)\s،؛]{1,24}\s*\)?"
    r"(?:[^\n]{0,60}?(?:وتاريخ|بتاريخ)\s*[\d\s/]{4,16}\s*ه?)?)")

COMPONENT_BY_PREFIX = [
    ("النظام الأساس", "statute"),
    ("تنظيم ", "statute"),
    ("الترتيبات التنظيمية", "statute"),
    ("نظام ", "law"),
    ("النظام ", "law"),
    ("اللائحة", "regulation"),
    ("لائحة", "regulation"),
    ("القواعد", "rules"),
    ("قواعد", "rules"),
    ("الآلية", "rules"),
    ("آلية", "rules"),
    ("ضوابط", "rules"),
    ("تعليمات", "rules"),
    ("الضوابط", "rules"),
]


def derive_component(title: str) -> str:
    for prefix, comp in COMPONENT_BY_PREFIX:
        if title.startswith(prefix):
            return comp
    return "regulation"


def derive_dates(body: str):
    """(hijri 'd/m/yyyy', gregorian 'YYYY-MM-DD') from the masthead, else None."""
    m = DATE_RE.search(body[:1200])
    if not m:
        return None, None
    hy, hm, hd, gd, gm, gy = m.groups()
    return f"{int(hd)}/{int(hm)}/{int(hy)}", f"{gy}-{gm}-{gd}"


def derive_decision(body: str):
    """Issuing decision, ONLY if literally present in the masthead (before the
    first article heading). Never inferred from cross-references in the body."""
    head = body[:body.find("المادة")] if "المادة" in body else body[:1500]
    m = DECISION_RE.search(head)
    return strip_text(m.group(1)) if m else None


# ---------------------------------------------------------------- identifiers
#
# DELIBERATE AUTOMATION BOUNDARY.
#
# A track_id is a permanent, public identifier and every one of the corpus's
# existing tracks uses a clean English semantic name (medical_devices_law,
# antiquities_heritage_regulation, ...). Machine transliteration of an Arabic
# title produces neither: measured over the 225-document gated backlog, the
# titles draw on 656 distinct Arabic tokens and 522 are needed just to cover
# 90% of occurrences, so any dictionary small enough to hand-author still
# leaves a long tail rendered as unreadable consonant strings
# ("lahh_mjls_aljmayat_alahlyh").
#
# Shipping those as permanent identifiers would trade a durable quality
# property for throughput. So this pipeline deliberately does NOT assign final
# ids: it proposes a slug for triage only, and emission requires a curated
# name. Everything else in the spec is derived mechanically from the page and
# is safe to automate; naming is the step that stays human.

def propose_slug(title: str) -> str:
    """A rough ASCII handle for triage/reporting ONLY. Never use as a track_id:
    see the automation-boundary note above."""
    return re.sub(r"[^a-z0-9_]", "", "_".join(norm_ar(title).split()[:5]).lower()) or "doc"


# ---------------------------------------------------------------- quality gates

# The gazette's vocabulary for naming an instrument is wider than this filter used
# to allow, and every word missing from it was a class of document the pipeline
# never even looked at: «الأحكام النظامية الخاصة بضبط العلاقة بين المؤجر
# والمستأجر»، «الإطار التنظيمي لمشاريع النقل العام»، «الكود السعودي لمصادر
# المياه»، «المعايير المهنية لتقييم أضرار المركبات»، «الأدلة الإجرائية لنظام
# الإثبات». 138 addressable pages sat outside discovery for no reason but the
# absence of their first word from this list.
#
# Being generous here is safe in a way it would not have been before: G1 judges
# only the SHAPE of a title. Whether the page carries a real instrument is settled
# downstream by G3 (it must segment into articles or a complete band run), G2
# (both the per-article and the whole-document duplicate measures) and G4-G10. A
# cooperation MOU announced as «اتفاقية تعاون مع ...» reaches G3 and is refused
# there for having no articles, which is the correct place to refuse it.
LEGAL_PREFIX = re.compile(
    r"^(نظام|النظام|اللائحة|لائحة|اللوائح|قواعد|القواعد|تنظيم|التنظيم|الترتيبات|ضوابط|الضوابط"
    r"|تعليمات|التعليمات|الآلية|آلية|الاشتراطات|اشتراطات|المعايير|معايير|الدليل|دليل|الأدلة"
    r"|السياسة|الميثاق|الشروط|شروط|المتطلبات|متطلبات|الإطار|إطار|التعرفة|تعرفة|الكود"
    r"|المواصفات|المواصفة|الإجراءات|إجراءات|الأحكام|أحكام|البروتوكول|الاتفاقية|اتفاقية|الأسس)")

# «مشروع» marks a DRAFT, but only as the title's first word. As a bare substring it
# also matches «المشروعات» and «مشروعات» — so «تنظيم هيئة كفاءة الإنفاق
# والمشروعات الحكومية» and «نظام بيع وتأجير مشروعات عقارية على الخارطة» were both
# discarded as drafts.
DRAFT_RE = re.compile(r"^\s*مشروع\b")

# «تعديل» / «إلغاء» mark an AMENDING instrument only when they are what the
# instrument DOES — «نظام (قانون) بتعديل بعض أحكام نظام براءات الاختراع» — which in
# Arabic shows as a ب/ل prefix or as the word sitting directly after the instrument
# noun. As bare substrings they also matched titles where the word belongs to the
# SUBJECT MATTER: «قواعد نظر دعاوى إلغاء القرارات المتعلقة بأوامر الطوارئ» is a
# rules instrument about annulment actions, not a repeal, and «... وبروتوكولاتها
# وتعديلاتها» merely says the convention has protocols and amendments.
AMENDING_RE = re.compile(
    r"^\s*(?:تعديل|تعديلات|إلغاء|الغاء|استبدال)\b"          # the title IS the amendment
    r"|^[^\n]{0,24}?\s[بل](?:تعديل|إلغاء|الغاء)\b"          # «نظام (قانون) بتعديل ...»
    r"|^\S+\s+(?:تعديل|إلغاء|الغاء)\b")                     # «لائحة تعديل ...»


def is_amendment_shaped(title):
    return bool(DRAFT_RE.search(title) or AMENDING_RE.search(title))


# Kept for callers that still read the old tuple; the decision lives in
# is_amendment_shaped(), which knows where in the title the word has to be.
AMENDMENT_MARKERS = ("تعديل", "مشروع", "إلغاء")


def registry_titles():
    path = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
    reg = json.load(open(path, encoding="utf-8"))
    return ([(t["track_id"], t.get("display_name_ar", "")) for t in reg["tracks"]],
            {t["track_id"] for t in reg["tracks"]})


# G2 confirmation corpus: the article texts of every track already on disk,
# fingerprinted as normalised 300-char prefixes. Built lazily and cached because
# a gating sweep evaluates hundreds of pages against the same corpus.
_FINGERPRINTS = None
DUPLICATE_OVERLAP = 0.97
# Fraction of an article's shingles that must already exist in a track for that
# article to count as ingested there.
ARTICLE_CONTAINMENT = 0.80
# Overlap below DUPLICATE_OVERLAP but at or above this is neither clearly new
# nor clearly a duplicate; such a document is refused rather than auto-built.
GRAY_BAND = 0.35
SHINGLE_WORDS = 8


def shingles(text):
    """Hashed 8-word shingles of an article, for order-preserving fuzzy matching."""
    w = norm_ar(text).split()
    if not w:
        return frozenset()
    if len(w) <= SHINGLE_WORDS:
        return frozenset({hash(" ".join(w))})
    return frozenset(hash(" ".join(w[i:i + SHINGLE_WORDS]))
                     for i in range(len(w) - SHINGLE_WORDS + 1))


def document_overlap(article_texts, exclude=None):
    """(fraction, track_id) — how much of this DOCUMENT'S shingle vocabulary a
    single existing track already contains.

    best_content_match() asks a per-ARTICLE question: how many of these articles
    are ~verbatim copies of something on file. That catches a document re-ingested
    unchanged, and it is blind to the case that matters just as much — the SAME
    instrument in a later edition, where every article was edited. «اللائحة
    التنفيذية لنظام البيئة لمقدمي الخدمات البيئية» is article-for-article the
    regulation the corpus already held, but the two editions differ inside every
    article: the highest per-article containment was 0.79, just under the 0.80
    bar, so not one article counted and the document scored 0% — a clean pass as
    a brand-new instrument. Measured across the whole document instead, the two
    share half their vocabulary, which is squarely in the band that must be
    adjudicated by a human rather than auto-built.

    Both measures are needed. Neither subsumes the other: a short document quoting
    a long one scores high here and low there, and a verbatim re-ingestion scores
    high there and can score low here if the track is much larger."""
    doc = frozenset().union(*[shingles(t) for t in article_texts if t]) \
        if any(article_texts) else frozenset()
    if not doc:
        return 0.0, None
    best = (0.0, None)
    for tid, fp in track_fingerprints().items():
        if tid == exclude or not fp:
            continue
        ov = len(doc & fp) / len(doc)
        if ov > best[0]:
            best = (ov, tid)
    return best


def track_fingerprints():
    """{track_id: {shingle, ...}} for every track already in the corpus.

    Built from the unified LLM index rather than from sources/, because the
    source artifacts do not share one schema: only the pipeline-produced tracks
    keep an `articles` dict, so reading sources/ fingerprinted 113 of 548 tracks
    and left the rest -- including the Companies Law, the Evidence Law and the
    Personal Status Law -- invisible to the duplicate check. The unified index
    holds every track's article text in one shape."""
    global _FINGERPRINTS
    if _FINGERPRINTS is None:
        _FINGERPRINTS = {}
        path = os.path.join(ROOT, "data", "corpus_unified_index",
                            "corpus_unified_llm_index.jsonl")
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                s = shingles(r.get("text_ar", ""))
                if s:
                    _FINGERPRINTS.setdefault(r["corpus"], set()).update(s)
    return _FINGERPRINTS


_TRACK_DATES = None


def track_dates():
    """{track_id: gazette publication date (YYYY-MM-DD)} for every track that
    records one. Used by G2 to tell a duplicate from a LATER EDITION."""
    global _TRACK_DATES
    if _TRACK_DATES is None:
        _TRACK_DATES = {}
        for pat in (os.path.join(ROOT, "sources", "*", "official_source", "*.json"),
                    os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json")):
            for p in glob.glob(pat):
                tid = os.path.relpath(p, os.path.join(ROOT, "sources")).split(os.sep)[0]
                try:
                    d = json.load(open(p, encoding="utf-8")).get("gazette_publication_date_gregorian")
                except (ValueError, OSError):
                    continue
                if d and tid not in _TRACK_DATES:
                    _TRACK_DATES[tid] = d
    return _TRACK_DATES


NAME_TOKEN_OVERLAP = 0.80
SPELLING_VARIANT_RATIO = 0.75


def _name_tokens(title):
    s = re.sub(r"[ً-ٰٟـ]", "", title or "")
    s = (s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
          .replace("ة", "ه").replace("ى", "ي"))
    return {w for w in re.sub(r"[^\w؀-ۿ]+", " ", s).split() if len(w) > 1}


def same_instrument_name(a, b):
    """Do these two titles name the SAME instrument, allowing for spelling?

    Two conditions, and the second is what makes the first safe. Token overlap
    alone puts «اتفاقية خدمات جوية مع غانا» and «... مع قطر» at 82% — the same
    instrument type between different parties, which is not the same instrument.
    So every token present in one title and absent from the other must also be a
    SPELLING VARIANT of some token in the other: «مكافاه»/«مكافات» are, «غانا»
    and «قطر» are not. See G14 in evaluate() for what this is used to refuse."""
    ta, tb = _name_tokens(a), _name_tokens(b)
    if not ta or not tb:
        return False
    if len(ta & tb) / len(ta | tb) < NAME_TOKEN_OVERLAP:
        return False
    for w in ta ^ tb:
        other = tb if w in ta else ta
        if not any(difflib.SequenceMatcher(None, w, o).ratio() >= SPELLING_VARIANT_RATIO
                   for o in other):
            return False
    return True


def best_content_match(article_texts, exclude=None):
    """(overlap_fraction, track_id) for the built track that best already
    contains `article_texts`. (0.0, None) when nothing is on disk to compare to.

    An article counts as already ingested when ARTICLE_CONTAINMENT of its word
    shingles appear in that track. Shingles, not a text prefix: the same article
    is stored across the corpus with different leading matter -- the gazette
    renders an inline heading («التعريفات: ...») that the corpus copy lacks, and
    older tracks carry markdown emphasis and hard line breaks. A prefix
    comparison reads those as a total mismatch, so a law the corpus already
    holds (the Companies Law, the Evidence Law) scored 0% overlap and would
    have been re-ingested under a second track id. Shingle containment is
    insensitive to where the difference falls.

    `exclude` skips a track id -- needed when REBUILDING an existing track,
    which would otherwise be reported as a perfect duplicate of itself."""
    cands = [shingles(t) for t in article_texts if t]
    cands = [c for c in cands if c]
    if not cands:
        return 0.0, None
    best = (0.0, None)
    for tid, fp in track_fingerprints().items():
        if tid == exclude:
            continue
        hit = sum(1 for c in cands if len(c & fp) / len(c) >= ARTICLE_CONTAINMENT)
        ov = hit / len(cands)
        if ov > best[0]:
            best = (ov, tid)
    return best


_DEDUP_STOP = {"نظام", "اللائحه", "التنفيذيه", "لنظام", "قواعد", "لائحه", "تنظيم",
               "النظام", "الترتيبات", "التنظيميه", "الاساس", "ضوابط", "تعليمات",
               "القواعد", "المنظمه", "الاليه", "في", "من", "على"}


def _dedup_tokens(s: str):
    return {w for w in norm_ar(s).split() if len(w) > 2 and w not in _DEDUP_STOP}


def evaluate(title: str, body: str, reg_names, taken, exclude=None):
    """Run every gate. Returns (spec_or_None, reject_reasons)."""
    reasons = []
    notes = []

    # G1 — shape of the document
    if not title or not LEGAL_PREFIX.match(title):
        reasons.append("G1: title is not legal-document shaped")
    if is_amendment_shaped(title):
        reasons.append("G1: title marks an amendment/draft/repeal, not a standalone instrument")

    arts, diag = segment(body)
    # A document drafted in ordinal bands rather than «مادة» reads as zero
    # articles here. Falling back to the band segmenter is what lets that whole
    # drafting family through; the form is recorded on the spec so a builder
    # never labels a band «المادة».
    numbering_form = "articles"
    if diag["count"] < MIN_ARTICLES:
        bands, bdiag = segment_bands(body)
        if bdiag["count"] >= MIN_BANDS:
            arts, diag, numbering_form = bands, bdiag, "ordinal_bands"
        else:
            # Last of the three forms, and tried last on purpose: a bare «1-» is
            # the weakest structural mark of the three, so it only speaks when
            # neither «المادة» nor «أولاً» is present to speak instead.
            cls, cdiag = segment_clauses(body)
            if cdiag["count"] >= MIN_CLAUSES:
                arts, diag, numbering_form = cls, cdiag, "numbered_clauses"

    # Cut a trailing annex block off the last record before any gate reads the
    # records. Done here rather than after the gates on purpose: G2's content
    # overlap, G10's length sanity and G13's table density all measure the
    # records, and a 268,000-char annex block sitting inside article 112 skews
    # every one of them.
    arts, appendices = split_appendices(arts)
    if appendices:
        notes.append("APPENDIX-SPLIT: %d annexes (%s … %s) were separated from the last "
                     "record; the annex headings are the gazette's own «الملحق N:»"
                     % (len(appendices), appendices[0][1], appendices[-1][1]))

    # G2 — already covered?
    #
    # Title similarity alone is NOT sufficient evidence of duplication, and
    # acting on it silently hides real coverage gaps. Saudi practice routinely
    # issues, under near-identical titles, instruments that are legally distinct:
    # an authority's «تنظيم» (its constitutive statute) against that same
    # authority's «لائحة التراخيص»; a «لائحة» against the «الآلية التفصيلية»
    # implementing it; a «تنظيم» against its own «اللائحة التنفيذية». Conversely
    # boilerplate-heavy families (the special-economic-zone regulations) look
    # ~90% alike by text while being separate instruments for separate zones.
    #
    # So the title match is only a suspicion; rejection additionally requires
    # that the candidate's own article text be substantially reproduced by a
    # track already on disk. The reported track is the best CONTENT match, not
    # the first title match -- token overlap picks the wrong sibling often
    # inside these families.
    #
    # This gate previously rejected on the title alone. Re-gating the backlog
    # after the fix recovered 13 wrongly-suppressed documents / 205 articles,
    # among them all nine cultural-authority constitutive statutes.
    tt = _dedup_tokens(title)
    title_hit = None
    if tt:
        for tid, dn in reg_names:
            rt = _dedup_tokens(dn)
            if rt and len(tt & rt) / max(1, min(len(tt), len(rt))) >= 0.75:
                title_hit = tid
                break
    # The content check runs ALWAYS, not only when the title collided: the title
    # is the weaker signal in both directions.
    overlap, match = best_content_match([a[2] for a in arts], exclude=exclude)
    if overlap >= DUPLICATE_OVERLAP:
        # High overlap is NOT enough to call this a duplicate. A later edition of
        # the same instrument -- a re-issue amending a handful of articles --
        # scores exactly here, so rejecting on overlap alone silently discards the
        # CURRENT text while the corpus keeps the superseded one. Observed in the
        # wild: the 2024 edition of لائحة التصرف في عقارات الدولة scores 97%
        # against the 2022 text we held, and its article 47 carries a whole clause
        # the older text lacks. So compare dates too.
        cand_date = derive_dates(body)[1]
        held = track_dates().get(match)
        if cand_date and held and cand_date > held:
            reasons.append("G2-LATER-EDITION: this document is %.0f%% the same as track '%s' "
                           "but was published LATER (%s vs the %s edition on file) — the corpus "
                           "is holding superseded text; refresh that track from this page rather "
                           "than discarding this document as a duplicate"
                           % (overlap * 100, match, cand_date, held))
        else:
            reasons.append("G2: already covered by registry track '%s' (%.0f%% of this "
                           "document's articles are already ingested there)"
                           % (match, overlap * 100))
    elif overlap >= GRAY_BAND:
        # Substantial but not total overlap. This is where a superseded edition,
        # a partial re-issue, or a segmentation difference lives, and it is not
        # safe to auto-build either way. Refuse and hand it to a human.
        reasons.append("G2: %.0f%% of this document's articles already exist in track "
                       "'%s' — substantial but not total overlap, so this is a possible "
                       "version difference or partial duplicate and must be adjudicated "
                       "by hand, not auto-built" % (overlap * 100, match))
    else:
        # The article-level measure found nothing. Ask the document-level question
        # too, which is the only one that sees an edited re-edition.
        dov, dmatch = document_overlap([a[2] for a in arts], exclude=exclude)
        if dov >= GRAY_BAND:
            reasons.append(
                "G2-EDITION: only %.0f%% of this document's articles are verbatim matches, but "
                "%.0f%% of its whole text already exists in track '%s' — that is the signature of "
                "the SAME instrument in a different edition, with every article edited. Which "
                "edition is in force cannot be settled from text overlap, so this is adjudicated "
                "by hand, not auto-built" % (overlap * 100, dov * 100, dmatch))

    # G2-PREDECESSOR. Saudi practice issues a body's founding «الترتيبات التنظيمية»
    # and later replaces it with a «تنظيم» for the SAME body. Five such pairs turned
    # up in one batch -- Public Health, Government Resource Systems, the Red Sea
    # Authority, the Coral Reefs and Turtles Corporation, Environmental Service
    # Providers -- and text overlap is an unreliable way to see them: the five
    # scored 0.30 to 0.58 document containment, straddling the gray band in both
    # directions, because the successor is a genuine rewrite. The body NAME is the
    # reliable signal, and it is a fact about the two titles rather than a reading.
    #
    # This does not decide that the earlier instrument is repealed -- a successor
    # that never says so leaves that unproven. It decides only that the corpus must
    # not silently gain a predecessor alongside the successor it already holds, as
    # if both stood. Which one is in force is a human question, and the document is
    # handed over rather than built.
    if title.startswith("الترتيبات التنظيمية"):
        bt = _dedup_tokens(re.sub(r"^الترتيبات التنظيمية\s*(ل|لل)?", "", title))
        for tid, dn in reg_names:
            if tid == exclude or not dn.startswith("تنظيم"):
                continue
            ot = _dedup_tokens(re.sub(r"^تنظيم\s*(ل|لل)?", "", dn))
            if bt and ot and len(bt & ot) / max(1, min(len(bt), len(ot))) >= 0.80:
                reasons.append(
                    "G2-PREDECESSOR: this is the «الترتيبات التنظيمية» of a body whose «تنظيم» "
                    "the corpus already holds as track '%s' («%s»). The two name the same body, "
                    "so this document is that track's predecessor. Whether it was repealed is "
                    "not settled by either text, so it is adjudicated by hand rather than built "
                    "alongside its own successor" % (tid, dn[:70]))
                break

    # G14 — the SAME instrument name, and the corpus already holds a LATER edition.
    #
    # Found by auditing, not by design. «ضوابط مكافأة أعضاء مجالس إدارة الأجهزة
    # واللجان المنبثقة عنها» (Umm Al-Qura, 2021-03-05) passed every gate above
    # while the corpus already held «ضوابط مكافآت أعضاء مجالس إدارة الأجهزة
    # واللجان المنبثقة عنها» (2023-09-21) — the same instrument, one word apart in
    # spelling, rewritten enough that document containment came to 8% and no
    # overlap-based gate could see it. Building it would have added SUPERSEDED
    # text to a corpus that already carried its successor, and a model reading
    # both has no way to tell which one to answer with.
    #
    # Title similarity alone is not enough to say «same instrument» — the treaty
    # family shares 82% of its title tokens across different counterparties
    # («اتفاقية خدمات جوية مع غانا» vs «... مع قطر»). So a token-overlap floor is
    # paired with a second condition: every token that differs must be a spelling
    # variant of a token in the other title, not a different word. «مكافاه» and
    # «مكافات» pass that; «غانا» and «قطر» do not. Measured over the whole corpus,
    # the two conditions together call exactly two existing pairs the same
    # instrument — cma_corporate_governance_regulation / corporate_governance_
    # regulation, and social_insurance / social_insurance_legacy — and the corpus
    # holds both of those deliberately and says so in their names.
    #
    # As with G2-PREDECESSOR, this does not decide that the earlier text is
    # repealed. It decides that the corpus must not silently gain it alongside
    # the later edition it already holds.
    dates = track_dates()
    this_date = derive_dates(body)[1]
    for tid, dn in reg_names:
        if tid == exclude or not dn:
            continue
        held = dates.get(tid, "")
        if not held or not this_date or held <= this_date:
            continue
        if same_instrument_name(title, dn):
            reasons.append(
                "G14-LATER-EDITION-HELD: the corpus already holds this same instrument name as "
                "track '%s' («%s») published %s, later than this document's %s. Every differing "
                "word between the two titles is a spelling variant, not a different subject, so "
                "this is an EARLIER EDITION of a text already on file. Which edition is in force "
                "is not settled by either document, so it is adjudicated by hand rather than "
                "built alongside its own successor"
                % (tid, dn[:70], held, this_date))
            break

    if title_hit and not any(r.startswith("G2") for r in reasons):
        notes.append("G2-NOTE: title resembles registry track '%s', but only %.0f%% "
                     "of its articles are already ingested (best content match: '%s') "
                     "— treated as a DISTINCT instrument, not a duplicate"
                     % (title_hit, overlap * 100, match or "none"))

    # G3 — enough structure to be a track
    floor = {"ordinal_bands": MIN_BANDS,
             "numbered_clauses": MIN_CLAUSES}.get(numbering_form, MIN_ARTICLES)
    if diag["count"] < floor:
        reasons.append(f"G3: only {diag['count']} article(s) segmented (min {MIN_ARTICLES}), "
                       f"and no complete ordinal-band run either (min {MIN_BANDS}), "
                       f"and no complete numbered-clause run either (min {MIN_CLAUSES})")

    # G4..G7 — per-article integrity
    for num, _o, txt, _ch in arts:
        if len(txt) < SHORT_ARTICLE_CHARS:
            reasons.append(f"G4: article {num} is empty/near-empty")
        if any(nav in txt for nav in NAV_MARKERS):
            reasons.append(f"G5: article {num} contains site-navigation boilerplate")
        if trailing_chapter_heading(txt):
            reasons.append(f"G6: article {num} has a trailing chapter heading")
        if TASHKEEL.search(txt) or "ـ" in txt:
            reasons.append(f"G7: article {num} has residual tashkeel/tatweel")

    # G8 — numbering gaps must be provably safe.
    #
    # A gap at the FIRST article number is categorically different from one in
    # the middle: the neighbour test cannot look "before the start", so if the
    # document opens with substantive prose that simply lacks a «المادة الأولى:»
    # heading, that text is silently DROPPED rather than skipped. Observed in
    # the wild (Yanbu/Umluj/Al-Wajh/Duba Development Authority arrangements,
    # whose unlabelled definitions article would have been lost). Treat any
    # leading gap accompanied by real text before the first heading as unsafe.
    by_num = {a[0]: a for a in arts}
    if arts and diag["missing"]:
        first_captured = arts[0][0]
        lead = strip_text(body[:body.find("المادة")]) if "المادة" in body else ""
        # drop the masthead (title + dates) before judging whether prose remains
        lead_body = re.sub(r"^.{0,200}?\d{2}-\d{2}-\d{4}", "", lead).strip()
        for gap in [g for g in diag["missing"] if g < first_captured]:
            if len(lead_body) >= 120:
                reasons.append(
                    "G8: article %d has no heading in the source but substantive text "
                    "precedes the first captured heading (%d chars) — that text would be "
                    "dropped, not skipped" % (gap, len(lead_body)))

    for gap in diag["missing"]:
        o = ordinal(gap)
        if re.search(MADDA + _flex(o), body):
            reasons.append(f"G8: article {gap} is referenced in the document but was not "
                           f"segmented — possible merged/lost text")
            continue
        for neighbour in (gap - 1, gap + 1):
            a = by_num.get(neighbour)
            if a and a[2] and a[2].rstrip()[-1:] not in SENTENCE_FINAL:
                reasons.append(f"G8: article {neighbour} adjoining gap {gap} does not end on "
                               f"sentence-final punctuation — text may be merged")

    # G10 — length sanity. A non-article block (annexes, schedules, long tables)
    # that carries no «المادة N:» heading gets absorbed into whichever article
    # precedes it, producing one pathologically long record while every gate
    # above still passes. Observed in the wild: the 2026 consolidation of the
    # CMA Rules on the Offer of Securities absorbed its entire annex block into
    # article 112 (268,802 chars against a ~1,500-char median). Flag any article
    # that dwarfs the document's own median.
    if len(arts) >= 5:
        lengths = sorted(len(a[2]) for a in arts)
        median = lengths[len(lengths) // 2]
        for num, _o, txt, _ch in arts:
            if median > 0 and len(txt) > max(20 * median, 40000):
                reasons.append(
                    "G10: article %d is %d chars against a %d-char median — a non-article "
                    "block (annexes/schedules) was probably absorbed into it"
                    % (num, len(txt), median))

    # G12 — a COUNCIL SESSION SUMMARY is not an instrument. The archive publishes
    # each Council of Ministers session as one page listing every decision taken:
    # authorising a minister to negotiate, creating an authority, approving a law,
    # approving promotions. The CMS titles the page after ONE of those items, so
    # «دليل استرشادي لاقتراح سن أحكام المخالفات الإدارية» arrived as an eleven-band
    # document whose bands were eleven unrelated decisions, only the ninth of which
    # was the guide the title names. Building it would file eleven unrelated
    # decisions under one instrument's name.
    #
    # The signal is that every record OPENS with a governmental decision verb.
    # Measured over the 70-document batch that surfaced this: the session summary
    # scored 1.00 and the next highest document scored 0.12, so the threshold sits
    # in a gap five times wider than the margin it needs.
    if arts:
        dec = sum(1 for a in arts if DECISION_OPENING_RE.match((a[2] or "").strip()))
        if dec / len(arts) >= SESSION_SUMMARY_RATIO:
            reasons.append(
                "G12: %d of %d records open with a governmental decision verb — this is a "
                "council SESSION SUMMARY listing unrelated decisions, not an instrument, and "
                "the page's title names only one of the items on it"
                % (dec, len(arts)))

    # G13 — a flattened TABLE is not a provision. Standards-adoption pages and some
    # annexes are tables of reference numbers, and the segmenter renders a table as
    # a run-on line of codes: «م رقم المواصفة ... 1 SASO 2986:2022 GB/T ...». Such a
    # record carries no normative sentence to retrieve or cite. Measured on the same
    # batch, the three table documents scored 0.26-0.48 mean non-Arabic-token
    # density and the next document scored 0.08.
    if arts:
        dens = []
        for a in arts:
            w = (a[2] or "").split()
            if w:
                dens.append(sum(1 for k in w if NON_ARABIC_TOKEN_RE.search(k)) / len(w))
        if dens and sum(dens) / len(dens) >= TABLE_DENSITY:
            reasons.append(
                "G13: %.0f%% of this document's words are reference codes rather than Arabic "
                "prose — its records are flattened TABLES, not provisions, and carry no "
                "normative sentence to cite" % (100 * sum(dens) / len(dens)))

    if reasons:
        return None, sorted(set(reasons))

    # ---- derive the spec (only reached when every gate passed)
    gh, gg = derive_dates(body)
    if not gh or not gg:
        return None, ["G1: could not read the gazette publication date from the masthead"]

    return {
        "numbering_form": numbering_form,
        "track_id_proposed": propose_slug(title),
        "track_id": None,   # curated at emission time — see the automation-boundary note
        "title_ar": title,
        "component": derive_component(title),
        "gazette_hijri": gh,
        "gazette_gregorian": gg,
        "decision": derive_decision(body),
        "article_count": diag["count"],
        "max_article_number": diag["max"],
        "missing_article_numbers": diag["missing"],
        "notes": notes,
        "articles": arts,
        "appendices": appendices,
    }, []


# ---------------------------------------------------------------- G11: batch screen
# G1-G10 judge one document against the corpus. Two things they structurally
# cannot see, because both need the BATCH:
#
#   (a) the same instrument reaching the batch twice. G2 compares a document
#       against the registry, and a document absent from the registry passes it
#       no matter how many of its siblings are the same text. The gazette does
#       republish: «الترتيبات التنظيمية لمركز الأمير محمد بن سلمان العالمي للخط
#       العربي» arrived twice on one day, and «قواعد تحديد درجات إركاب الموظفين»
#       a week apart, all four identical.
#
#   (b) a document that SAYS it repeals another. A Saudi instrument routinely
#       closes with «تحل هذه الضوابط محل ...». When what it names is an
#       instrument the batch also carries, or one the corpus already holds, that
#       predecessor is superseded — and the document said so itself, so no
#       inference is involved. Building it as if in force would be asserting
#       repealed law.
#
# Most replacement clauses name a NUMBERED COUNCIL DECISION rather than a titled
# instrument. Those are left alone: the corpus does not hold decisions by number,
# so there is nothing to withdraw and nothing to claim.
SUPERSEDES_RE = re.compile(
    r"(?:تحل|يحل)\s+(?:هذه|هذا|هذان)?\s*\S*\s*محل\s+([^\.،؛]{6,160})")


def supersedes_titles(articles):
    """Instrument titles this document declares it replaces, in its own words."""
    out = []
    for _num, _lab, txt, _ch in articles:
        for m in SUPERSEDES_RE.finditer(txt):
            cand = strip_text(m.group(1))
            cand = re.split(r"\s+(?:الصادر|المعتمد|المُعتمد)", cand)[0].strip()
            if cand and LEGAL_PREFIX.match(cand):
                out.append(cand)
    return out


def screen_batch(specs, reg_names):
    """(keep, dropped) — apply G11 across a whole batch.

    Returns the specs safe to build and, for every one withheld, the reason in
    the same shape as a gate rejection. Nothing is merged or edited; a document
    is either kept whole or set aside whole."""
    order = sorted(specs, key=lambda x: (x.get("gazette_gregorian") or "", x.get("uid") or ""))
    fps = {id(x): set().union(*[shingles(a[2]) for a in x["articles"]]) if x["articles"]
           else set() for x in order}
    dropped, superseded = [], {}

    # (b) first: a supersession claim is evidence about a NAMED instrument and
    # does not depend on how the duplicate pass resolves.
    for x in order:
        for claimed in supersedes_titles(x["articles"]):
            ct = _dedup_tokens(claimed)
            if not ct:
                continue
            for y in order:
                if y is x:
                    continue
                yt = _dedup_tokens(y["title_ar"])
                if yt and len(ct & yt) / max(1, min(len(ct), len(yt))) >= 0.80:
                    superseded[id(y)] = (
                        "G11-SUPERSEDED: '%s' (%s) states in its own text that it replaces "
                        "«%s», which is this document — it is repealed law and must not be "
                        "built as if in force"
                        % (x["title_ar"][:60], x.get("gazette_gregorian"), claimed[:80]))
            for tid, dn in reg_names:
                dt = _dedup_tokens(dn)
                if dt and len(ct & dt) / max(1, min(len(ct), len(dt))) >= 0.80:
                    x.setdefault("notes", []).append(
                        "G11-NOTE: this document states it replaces «%s», which the corpus "
                        "holds as track '%s' — that track is holding repealed text and must "
                        "be refreshed or retired from this page" % (claimed[:80], tid))

    keep = []
    for x in order:
        if id(x) in superseded:
            dropped.append({"uid": x.get("uid"), "title_ar": x["title_ar"],
                            "blocking_gates": [superseded[id(x)]]})
            continue
        dup = None
        for k in keep:
            a, b = fps[id(x)], fps[id(k)]
            if not a or not b:
                continue
            ov = len(a & b) / min(len(a), len(b))
            # Across the CORPUS, only near-verbatim text may be called a duplicate:
            # distinct instruments share long stretches of boilerplate. Within one
            # BATCH the title is available as a second, independent signal, so a
            # lower text bar is safe when the two also carry the same name. That is
            # what separates «الاتفاقية العربية لمنع ومكافحة الاستنساخ البشري»
            # published twice (0.93, identical title, identical article count) and
            # the renewable-energy framework's two editions (0.75, identical title)
            # from two documents that merely resemble each other.
            # The two titles must be the SAME name, not a similar one. Token overlap
            # is the wrong test here and fails loudly: «اتفاقية عامة للتعاون بين
            # حكومتي المملكة وجمهورية نيبال» and «... وحكومة تشاد» differ in exactly
            # one token, the country, and template treaties share 40-76% of their
            # text — so an 85%-overlap rule discarded five distinct bilateral
            # agreements as duplicates of each other. Equality after normalisation
            # keeps the discriminating word discriminating.
            same_name = norm_ar(x["title_ar"]) == norm_ar(k["title_ar"])
            if ov >= DUPLICATE_OVERLAP or (ov >= GRAY_BAND and same_name):
                dup = k
                break
        if dup is not None:
            # `order` is by date, so the one already kept is the earlier edition.
            # The later one supersedes it: swap, and withhold the earlier.
            dropped.append({"uid": dup.get("uid"), "title_ar": dup["title_ar"],
                            "blocking_gates": [
                                "G11-DUPLICATE-IN-BATCH: %.0f%% the same text as '%s' (%s), "
                                "which carries the same title and was published later in this "
                                "same batch — the later edition is built and this one is withheld"
                                % (ov * 100, x["title_ar"][:60], x.get("gazette_gregorian"))]})
            keep[keep.index(dup)] = x
        else:
            keep.append(x)
    return keep, dropped


def main():
    print(__doc__.strip().splitlines()[0])
    print("This module is a library + driver used by the gazette ingestion batches;")
    print("import `evaluate`, `segment`, `page_text` from it rather than duplicating logic.")


if __name__ == "__main__":
    main()
