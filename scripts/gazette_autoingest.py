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
  G2  not already covered by a live registry track (token-overlap dedup)
  G3  segmentation yields >= MIN_ARTICLES articles
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

Arabic governs throughout. Read-only over the corpus; the only writes are
the emitted artifacts under sources/ and scripts/, plus the JSON report.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIN_ARTICLES = 5
SHORT_ARTICLE_CHARS = 15
SENTENCE_FINAL = ".؟!:》”\"'）)"

# ---------------------------------------------------------------- normalisation

TASHKEEL = re.compile("[ً-ٰٟ]")  # excludes Arabic-Indic digits U+0660-0669
MADDA = r"ا\s*ل\s*م\s*ا\s*د\s*ة"  # tolerates stray intra-word spaces from typesetting
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

TRAILING_CH_RE = re.compile(
    r"\s*(الباب|الفصل)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر"
    r"|(?:الحادي|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)\s+عشر"
    r"|العشرون|التمهيدي)\s*:?\s*[^\n]{0,90}$")

# Both heading conventions used by the Gazette: Arabic feminine ordinals
# ("المادة الخامسة:") and explicit digits ("المادة (5):", Western or
# Arabic-Indic). A trailing colon is mandatory, which is what excludes
# in-text cross-references such as "المادة (التاسعة) من اللائحة".
HEADING_RE = re.compile(
    MADDA +
    r"(?:"
    # digit form — unambiguous, so an inline heading title before the colon is safe:
    #   «المادة (5):»   «المادة (5) المصطلحات والتعاريف:»
    r"\s*\(\s*([0-9\u0660-\u0669]{1,4})\s*\)(?:[^:\n]{0,40})?:"
    # ordinal form — the colon must follow the ordinal directly (optionally after a
    # duplicated digit, «المادة الخامسة (5):»). Keeping this strict is what excludes
    # in-text cross-references such as «المادة (التاسعة) من اللائحة».
    r"|\s*\(?\s*([^\s:\n()\.،؛][^:\n()\.،؛]{0,44}?)\s*\)?"
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
    return title, t


def chapters(body: str):
    return [(m.start(), f"{m.group(1)} {m.group(2)}", strip_text(m.group(3)))
            for m in CH_RE.finditer(body)]


def segment(body: str):
    """Article headings in document order -> (articles, diagnostics).

    Robustness: every heading candidate is resolved to an integer, then the
    longest strictly-increasing subsequence is kept. A spurious match (an
    in-text cross-reference that happens to be followed by a colon) is
    therefore dropped on its own, instead of truncating every genuine
    heading that follows it.
    """
    cands = []
    for m in HEADING_RE.finditer(body):
        if m.group(1) is not None:
            try:
                n = int(m.group(1).translate(_ARABIC_DIGITS))
            except ValueError:
                continue
            if not 1 <= n <= 999:
                continue
        else:
            n = parse_ordinal(m.group(2))
            if n is None:
                continue
        cands.append((n, m.start(), m.end()))

    if not cands:
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
            stripped = TRAILING_CH_RE.sub("", txt)
            if stripped == txt:
                break
            txt = stripped
        arts.append((num, ordinal(num), strip_text(txt), chapter_at(s)))

    present = {a[0] for a in arts}
    missing = [n for n in range(1, max(present) + 1) if n not in present]
    return arts, {"count": len(arts), "max": max(present), "missing": missing}


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

AMENDMENT_MARKERS = ("تعديل", "مشروع", "إلغاء")
LEGAL_PREFIX = re.compile(
    r"^(نظام|النظام|اللائحة|لائحة|قواعد|القواعد|تنظيم|الترتيبات|ضوابط|الضوابط|تعليمات|الآلية|آلية)")


def registry_titles():
    path = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
    reg = json.load(open(path, encoding="utf-8"))
    return ([(t["track_id"], t.get("display_name_ar", "")) for t in reg["tracks"]],
            {t["track_id"] for t in reg["tracks"]})


_DEDUP_STOP = {"نظام", "اللائحه", "التنفيذيه", "لنظام", "قواعد", "لائحه", "تنظيم",
               "النظام", "الترتيبات", "التنظيميه", "الاساس", "ضوابط", "تعليمات",
               "القواعد", "المنظمه", "الاليه", "في", "من", "على"}


def _dedup_tokens(s: str):
    return {w for w in norm_ar(s).split() if len(w) > 2 and w not in _DEDUP_STOP}


def evaluate(title: str, body: str, reg_names, taken):
    """Run every gate. Returns (spec_or_None, reject_reasons)."""
    reasons = []

    # G1 — shape of the document
    if not title or not LEGAL_PREFIX.match(title):
        reasons.append("G1: title is not legal-document shaped")
    if any(k in title for k in AMENDMENT_MARKERS):
        reasons.append("G1: title marks an amendment/draft/repeal, not a standalone instrument")

    # G2 — already covered?
    tt = _dedup_tokens(title)
    if tt:
        for tid, dn in reg_names:
            rt = _dedup_tokens(dn)
            if rt and len(tt & rt) / max(1, min(len(tt), len(rt))) >= 0.75:
                reasons.append(f"G2: already covered by registry track '{tid}'")
                break

    arts, diag = segment(body)

    # G3 — enough structure to be a track
    if diag["count"] < MIN_ARTICLES:
        reasons.append(f"G3: only {diag['count']} article(s) segmented (min {MIN_ARTICLES})")

    # G4..G7 — per-article integrity
    for num, _o, txt, _ch in arts:
        if len(txt) < SHORT_ARTICLE_CHARS:
            reasons.append(f"G4: article {num} is empty/near-empty")
        if any(nav in txt for nav in NAV_MARKERS):
            reasons.append(f"G5: article {num} contains site-navigation boilerplate")
        if TRAILING_CH_RE.search(txt):
            reasons.append(f"G6: article {num} has a trailing chapter heading")
        if TASHKEEL.search(txt) or "ـ" in txt:
            reasons.append(f"G7: article {num} has residual tashkeel/tatweel")

    # G8 — numbering gaps must be provably safe
    by_num = {a[0]: a for a in arts}
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

    if reasons:
        return None, sorted(set(reasons))

    # ---- derive the spec (only reached when every gate passed)
    gh, gg = derive_dates(body)
    if not gh or not gg:
        return None, ["G1: could not read the gazette publication date from the masthead"]

    return {
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
        "articles": arts,
    }, []


def main():
    print(__doc__.strip().splitlines()[0])
    print("This module is a library + driver used by the gazette ingestion batches;")
    print("import `evaluate`, `segment`, `page_text` from it rather than duplicating logic.")


if __name__ == "__main__":
    main()
