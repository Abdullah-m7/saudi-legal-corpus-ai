#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a best-effort cross-reference graph between articles.

Many articles across this corpus's 122 tracks explicitly cite other
articles — either within the same law ("وفق المادة (16) من هذا النظام")
or in a different law ("وفقاً لأحكام نظام كذا"). This scans every article's
own text in the unified retrieval index
(data/corpus_unified_index/corpus_unified_llm_index.jsonl) for such
citations and resolves them into a queryable "see also" graph.

THIS IS A BEST-EFFORT, REGEX/PATTERN-BASED NLP EXTRACTION, NOT AN
INDEPENDENTLY LEGALLY VERIFIED DATASET (unlike the rest of this corpus's
article text, which is independently source-verified). It favors precision
over recall: ambiguous or vague references (e.g. "الأنظمة ذات العلاقة")
are skipped rather than force-matched. See `extraction_caveat` and
`known_limitations` in the generated output for details.

Extraction method
------------------
1. Intra-law citations: occurrences of "المادة" followed by a parseable
   digit or Arabic ordinal-word article number (e.g. "المادة (السادسة
   عشرة)", "المادة 16"), scoped to the SAME law by an explicit or
   contextual same-document marker ("من هذا النظام" / "من النظام" /
   "من هذه اللائحة" / bare, contextual default).
2. Inter-law citations naming a different law: (a) a "المادة (X) من نظام
   <Name>"-style citation, where the number is intra-citation but the law
   named is a different instrument; (b) a standalone law-name citation
   with no specific article ("وفقاً لنظام الإثبات"). Named laws are
   resolved against this corpus's own track titles
   (data/corpus_registry/corpus_registry.json display_name_ar) via
   fuzzy string matching; unresolved/out-of-corpus names are still
   recorded with `target_track_id: null` and the raw matched text.
3. Genuinely ambiguous same-law-vs-different-law cases (a bare backward
   demonstrative reference such as "من ذلك النظام" that this generator
   cannot resolve without deeper discourse tracking) are recorded with
   type `ambiguous_scope` rather than guessed.

The Arabic ordinal-to-integer parser was built and cross-validated against
this corpus's OWN article-numbering fields (`llm_title_ar`), which already
spell out patterns like "المادة الثامنة والعشرون بعد المائة" (article
128) for every one of this corpus's ~8,300 articles — used here as a
Rosetta stone. Cross-checked against >5,500 of this corpus's own ordinal
titles, the parser round-trips >99.8% of them correctly; the handful of
misses are the corpus's own documented drafting typos/anomalies (e.g. a
missing "و" conjunction, or the Arbitration Law's own documented "31st
article labeled الحادية والعشرون" numbering anomaly) which this generator
correctly declines to force-match.

Read-only over data/corpus_unified_index/, data/corpus_registry/, and
scripts/gen_corpus_unified_llm_index.py; deterministic and idempotent over
its own output.

Usage:
    python3 scripts/gen_corpus_cross_reference_graph.py
"""
from __future__ import annotations

import difflib
import importlib.util
import collections
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
GEN_UNIFIED_INDEX_SCRIPT = os.path.join(ROOT, "scripts", "gen_corpus_unified_llm_index.py")
OUT_DIR = os.path.join(ROOT, "data", "corpus_cross_reference_graph")
OUT_PATH = os.path.join(OUT_DIR, "corpus_cross_reference_graph.json")

SCHEMA_VERSION = "1.0.0"
GENERATED_BY = "scripts/gen_corpus_cross_reference_graph.py"

EXTRACTION_CAVEAT = (
    "This graph is a BEST-EFFORT, regex/pattern-based NLP extraction over "
    "each article's own free text. It is NOT an independently legally "
    "verified dataset in the way the rest of this corpus's article text "
    "is (MOJ-portal / BOE-portal cross-checked, etc.) — it is a heuristic "
    "reading of citation phrasing. It favors PRECISION over RECALL: many "
    "genuine cross-references are skipped rather than guessed (vague "
    "mentions like 'الأنظمة ذات العلاقة' with no specific article or a "
    "confidently-matchable law title are not extracted at all). It may "
    "still contain false positives (a citation scoped to the wrong law, "
    "an Arabic ordinal misread, a self-referential article heading "
    "misread as a citation) and false negatives (a real citation whose "
    "phrasing this generator's patterns do not cover). Treat every edge "
    "as a candidate 'see also' pointer to verify against the article text "
    "itself, not as a confirmed legal citation. Not legal advice."
)

KNOWN_LIMITATIONS = [
    "A subordinate instrument's «النظام» is resolved to the parent named in its "
    "own article 1, which is right whenever the regulation and the law it "
    "implements are the CURRENT pair — and can mistarget when the regulation "
    "PREDATES the law now holding that title. Two of the graph's four dangling "
    "references are exactly this: hospitality_mgmt and tourism_travel_services "
    "cite «المادة التاسعة والعشرين من النظام», and the tourism_law this corpus "
    "holds (M/18, 1444H) has 19 articles, because their «النظام» is the repealed "
    "predecessor tourism law, which this corpus does not hold. The dangle is the "
    "SYMPTOM and it is the lucky case: a citation to an article number that DOES "
    "exist in the current law would resolve silently to the wrong provision. A "
    "date-based check (regulation older than its parent) was written and "
    "measured, and abandoned as unreliable: only 10 of 1,255 parent references "
    "have a gazette date recorded on BOTH ends, so the check would have been "
    "shaped by which tracks happen to record a date rather than by which are "
    "mistargeted. Recorded here rather than papered over with a heuristic.",
    "Parent resolution matches the self-declared name against law-shaped track "
    "TITLES, so a parent published as a «تنظيم» rather than a «نظام» is not "
    "matched even when this corpus holds it. Eight tracks name a parent no held "
    "title matches; some of those names are genuinely absent from the corpus "
    "(«نظام البلديات والقرى», «نظام الهيئة السعودية للتخصصات الصحية», «نظام "
    "إجراءات التراخيص البلدية») and are a real coverage signal, while others are "
    "too generic to match anything («نظام الهيئة»). Left unresolved either way.",
    "Ordinal parsing only covers article numbers up to 999 and only the "
    "standard Arabic feminine ordinal forms (with tolerant variants: "
    "nominative/genitive tens endings -ون/-ين, teen 'عشر'/'عشرة', "
    "الحادية/الواحدة for 1, المائة/المئة for 100, and a spaceless fallback "
    "for missing-space typos). Genuine source typos that drop the 'و' "
    "conjunction in a compound ordinal (e.g. a documented 'التاسعة "
    "الثلاثون' instead of 'التاسعة والثلاثون' anomaly) are intentionally "
    "left unmatched rather than force-corrected.",
    "Same-law vs. different-law scoping is a lookahead-window heuristic "
    "(looking for 'من هذا النظام' / 'من النظام' / a named 'من نظام X' "
    "clause etc. within ~220 characters after the citation). Chained "
    "citations sharing one trailing scope clause ('المادة (5) والمادة "
    "(10) من النظام') are handled, but a scope clause belonging to an "
    "unrelated adjacent sentence could in principle be picked up "
    "incorrectly (not observed in spot-checks, but not exhaustively ruled "
    "out).",
    "Citations with no explicit same-law marker anywhere nearby default "
    "to intra_law at 'medium' confidence (the dominant convention in this "
    "corpus's drafting style), rather than being classified 'ambiguous' "
    "wholesale — 'ambiguous_scope' is reserved for a narrower, explicitly "
    "detected backward-demonstrative pattern ('من ذلك النظام' / 'من تلك "
    "اللائحة' / 'النظام المشار إليه' / 'النظام سالف/آنف الذكر') this "
    "generator cannot resolve without deeper discourse tracking.",
    "Named-law resolution against this corpus's own track titles uses "
    "fuzzy string matching (difflib) against each track's display_name_ar "
    "with its 'نظام/لائحة/...' prefix stripped. Two of this corpus's own "
    "tracks (social_insurance_law / social_insurance_legacy_law) share an "
    "identical bare title ('نظام التأمينات الاجتماعية') by the corpus's "
    "own documented design (see corpus_supersession_graph's "
    "concurrent_title_collisions) — an unqualified citation to that bare "
    "title cannot be resolved to one specific track and is recorded with "
    "target_track_id null rather than an arbitrary guess.",
    "Records whose own text_ar embeds a self-heading restating their own "
    "article number as the very first characters of the text (observed "
    "in the civil_aviation_law and pdpl_law tracks, e.g. text_ar starting "
    "'المادة الثالثة والثمانون: ...') are filtered out at position 0 so "
    "the article does not spuriously cite itself.",
    "Sub-article citations with a slash notation (e.g. 'المادة (223/3)') "
    "are resolved to their base article number only; the specific "
    "sub-item is not modeled.",
    "'مكرر' (repeated/inserted) article citations (e.g. 'المادة (16) "
    "مكرر') are skipped entirely rather than guessed, since resolving "
    "them to a specific مكرر record requires more context than a bare "
    "number provides.",
    "This generator does not attempt every possible reference in Saudi "
    "legal Arabic; vague collective references with no specific article "
    "or confidently-matchable law title (e.g. 'الأنظمة ذات العلاقة', "
    "'نظام آخر') are intentionally skipped, per this project's precision-"
    "over-recall instruction.",
]

# ---------------------------------------------------------------------------
# Arabic ordinal (feminine, agrees with المادة) <-> integer parser.
#
# Validated as a Rosetta stone against this corpus's OWN article-numbering
# fields (see module docstring): >99.8% round-trip match over >5,500 of
# this corpus's own ordinal-word article titles.
# ---------------------------------------------------------------------------

_AR_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_ar(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.translate(_AR_INDIC)
    s = re.sub(r"[ً-ٰٟـ]", "", s)  # diacritics + tatweel
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    return s


_ONES = {1: "الأولى", 2: "الثانية", 3: "الثالثة", 4: "الرابعة", 5: "الخامسة",
          6: "السادسة", 7: "السابعة", 8: "الثامنة", 9: "التاسعة"}
# used in teens (X عشر/عشرة) and tens-compounds (X و Y); 1 -> الحادية/الواحدة
_ONES_C = {k: [v] for k, v in _ONES.items()}
_ONES_C[1] = ["الحادية", "الواحدة"]
_TENS = {20: ["العشرون", "العشرين"], 30: ["الثلاثون", "الثلاثين"],
          40: ["الأربعون", "الأربعين"], 50: ["الخمسون", "الخمسين"],
          60: ["الستون", "الستين"], 70: ["السبعون", "السبعين"],
          80: ["الثمانون", "الثمانين"], 90: ["التسعون", "التسعين"]}
_HUNDRED_100 = ["المائة", "المئة", "مائة", "مئة"]
_HUNDRED_200 = ["المائتين", "المئتين"]
_HUNDRED_STANDALONE_200 = ["المائتان", "المئتان", "المائتين", "المئتين"]
_HUNDRED_N = {3: ["الثلاثمائة", "الثلاثمئة"], 4: ["الأربعمائة", "الأربعمئة"],
              5: ["الخمسمائة", "الخمسمئة"], 6: ["الستمائة", "الستمئة"],
              7: ["السبعمائة", "السبعمئة"], 8: ["الثمانمائة", "الثمانمئة"],
              9: ["التسعمائة", "التسعمئة"]}


def _phrases_1_99(n: int):
    if n == 1:
        return ["الأولى", "الواحدة"]
    if 1 <= n <= 9:
        return [_ONES[n]]
    if n == 10:
        return ["العاشرة"]
    if 11 <= n <= 19:
        out = []
        for base in _ONES_C[n - 10]:
            out.append(base + " عشرة")
            out.append(base + " عشر")
        return out
    if n % 10 == 0:
        return list(_TENS[n])
    ones, tens = n % 10, (n // 10) * 10
    return [ow + " و" + tw for ow in _ONES_C[ones] for tw in _TENS[tens]]


def _phrases(n: int):
    if n <= 99:
        return _phrases_1_99(n)
    h, rem = divmod(n, 100)
    if h == 1:
        hwords = _HUNDRED_100
    elif h == 2:
        hwords = _HUNDRED_200
    else:
        hwords = _HUNDRED_N.get(h)
        if hwords is None:
            return []
    if rem == 0:
        if h == 1:
            return ["المائة", "المئة", "مائة", "مئة"]
        if h == 2:
            return list(_HUNDRED_STANDALONE_200)
        return list(hwords)
    return [b + " بعد " + hw for b in _phrases_1_99(rem) for hw in hwords]


def _build_ordinal_dicts(max_n: int = 999):
    forward, spaceless = {}, {}
    for n in range(1, max_n + 1):
        for p in _phrases(n):
            key = normalize_ar(p)
            forward.setdefault(key, n)
            spaceless.setdefault(key.replace(" ", ""), n)
    return forward, spaceless


_ORDINAL_FORWARD, _ORDINAL_SPACELESS = _build_ordinal_dicts()

# Every individual word that can appear in a bare (non-parenthesized)
# ordinal run, used to bound the greedy word-run scanner below.
_ORDINAL_VOCAB = {"بعد"}
for _n in range(1, 300):
    for _p in _phrases(_n):
        _ORDINAL_VOCAB.update(_p.split(" "))


def parse_ordinal_phrase(phrase: str):
    key = normalize_ar(phrase)
    if key in _ORDINAL_FORWARD:
        return _ORDINAL_FORWARD[key]
    skey = key.replace(" ", "")
    if skey in _ORDINAL_SPACELESS:
        return _ORDINAL_SPACELESS[skey]
    return None


# ---------------------------------------------------------------------------
# Citation (المادة + number) scanner.
# ---------------------------------------------------------------------------

_PAREN_CLOSE = {"(": ")", '"': '"', "“": "”", "«": "»", "'": "'"}


def find_article_citations(text: str):
    """Yield (start, end, article_number, raw_span) for each 'المادة <n>'
    occurrence in `text` with a parseable article number. `start` is the
    index of 'المادة'; `end` is just past the parsed number/ordinal span."""
    out = []
    for m in re.finditer("المادة", text):
        i = m.end()
        j = i
        while j < len(text) and text[j] in " \t":
            j += 1
        if j >= len(text):
            continue
        ch = text[j]
        num = None
        span_end = j
        if ch in _PAREN_CLOSE:
            close = _PAREN_CLOSE[ch]
            k = text.find(close, j + 1)
            if k == -1 or k - j > 40:
                continue
            content = text[j + 1:k].strip()
            span_end = k + 1
            if "مكرر" in content:
                continue
            content_ascii = content.translate(_AR_INDIC)
            if re.fullmatch(r"\d+", content_ascii):
                num = int(content_ascii)
            elif re.fullmatch(r"\d+\s*/\s*\d+", content_ascii):
                num = int(re.match(r"\d+", content_ascii).group(0))
            else:
                num = parse_ordinal_phrase(content)
        else:
            dm = re.match(r"[0-9٠-٩]+", text[j:])
            if dm:
                num = int(dm.group(0).translate(_AR_INDIC))
                span_end = j + len(dm.group(0))
            else:
                words, pos = [], j
                while True:
                    wm = re.match(r"[ء-ي]+", text[pos:])
                    if not wm or wm.group(0) not in _ORDINAL_VOCAB:
                        break
                    words.append(wm.group(0))
                    pos += len(wm.group(0))
                    if pos < len(text) and text[pos] == " ":
                        pos += 1
                    else:
                        break
                    if len(words) >= 6:
                        break
                if words:
                    phrase = " ".join(words)
                    if "مكرر" not in phrase:
                        num = parse_ordinal_phrase(phrase)
                        span_end = j + len(phrase)
        if num is not None and 1 <= num <= 999 and m.start() != 0:
            out.append((m.start(), span_end, num, text[m.start():span_end]))
    return out


# ---------------------------------------------------------------------------
# Law-name resolution against this corpus's own track titles.
# ---------------------------------------------------------------------------

_LAW_PREFIXES = [
    "اللائحة التنفيذية لنظام ", "اللائحة التنفيذية للائحة ", "اللائحة التنفيذية ل",
    "لائحة نظام ", "لائحة ", "قانون (نظام) ", "قانون ", "نظام ", "تنظيم ",
    "آلية العمل التنفيذية لنظام ", "آلية ", "الدليل التنظيمي ل", "الدليل الإجرائي ل",
    "الترتيبات الخاصة ب", "القواعد الخاصة ب", "قواعد ", "ضوابط ", "جدول ",
]

_GENERIC_PLACEHOLDER_NAMES = {"اخر", "اخرى", "معين", "معينه", "خاص", "خاصه", "محدد", "محدده"}


def _strip_law_prefix(name: str) -> str:
    for p in _LAW_PREFIXES:
        if name.startswith(p):
            return name[len(p):].strip()
    return name


def _categorize_track(display_name_ar: str) -> str:
    """A law and its OWN implementing regulation share an identical 'core'
    after the نظام/لائحة prefix is stripped (e.g. both 'نظام الإفلاس' and
    'اللائحة التنفيذية لنظام الإفلاس' strip down to 'الإفلاس') — so prefix
    -stripped fuzzy matching alone cannot tell them apart. This keeps the
    instrument TYPE (law vs. its implementing regulation vs. other) as a
    first-class matching key so a citation that named 'نظام X' resolves to
    the LAW track, not its regulation, and vice versa."""
    d = display_name_ar or ""
    if d.startswith("اللائحة التنفيذية") or d.startswith("لائحة نظام"):
        return "implementing_regulation"
    if d.startswith("نظام") or d.startswith("قانون"):
        return "law"
    return "other"


def _categorize_kind(kind_text: str) -> str:
    k = normalize_ar(kind_text or "")
    if "التنفيذية" in k:
        return "implementing_regulation"
    if "نظام" in k or "قانون" in k:
        return "law"
    return "other"


def _build_track_cores(registry: dict):
    cores = []
    for t in registry.get("tracks", []):
        disp = t.get("display_name_ar", "") or ""
        core = normalize_ar(_strip_law_prefix(disp))
        cores.append((t["track_id"], core, _categorize_track(disp)))
    return cores


def _best_match(cand: str, subset, threshold: float, tie_epsilon: float):
    scored = []
    for tid, core in subset:
        if not core:
            continue
        ratio = difflib.SequenceMatcher(None, cand, core).ratio()
        if core in cand or cand in core:
            ratio = max(ratio, 0.9)
        scored.append((ratio, tid))
    if not scored:
        return None, 0.0
    scored.sort(reverse=True)
    best_ratio, best_tid = scored[0]
    if best_ratio < threshold:
        return None, best_ratio
    rivals = {tid for ratio, tid in scored if ratio >= best_ratio - tie_epsilon and tid != best_tid}
    if rivals:
        return None, best_ratio
    return best_tid, best_ratio


def match_law_name(candidate: str, track_cores, kind_text: str = "",
                    threshold: float = 0.62, tie_epsilon: float = 0.03):
    """Fuzzy-match a raw citation's law-name text against this corpus's own
    track titles. Returns (track_id_or_None, score).

    `kind_text` is the instrument-type word the citation itself used
    ('نظام' / 'اللائحة التنفيذية لنظام' / bare 'لائحة'/'قواعد'/etc.).
    Matching is first restricted to registry tracks of the SAME instrument
    type (a citation naming 'نظام الإفلاس' must resolve to bankruptcy_law,
    never to bankruptcy_implementing_regulation, which shares the identical
    'الإفلاس' core once prefixes are stripped) and only falls back to the
    full track list if nothing matches within that type. If the top two
    distinct-track candidates are within `tie_epsilon` of each other (e.g.
    this corpus's own documented social_insurance_law /
    social_insurance_legacy_law identical-title collision), returns
    (None, best_score) rather than arbitrarily picking one."""
    cand = normalize_ar(_strip_law_prefix(candidate))
    if len(cand) < 3 or cand in _GENERIC_PLACEHOLDER_NAMES:
        return None, 0.0

    category = _categorize_kind(kind_text)
    if category in ("law", "implementing_regulation"):
        same_type = [(tid, core) for tid, core, cat in track_cores if cat == category]
        tid, score = _best_match(cand, same_type, threshold, tie_epsilon)
        if tid is not None:
            return tid, score

    full = [(tid, core) for tid, core, _cat in track_cores]
    return _best_match(cand, full, threshold, tie_epsilon)


# ---------------------------------------------------------------------------
# Scope detection for an intra-law-shaped "المادة (X)" citation.
# ---------------------------------------------------------------------------

_SELF_NOUNS = r"(?:النظام|اللائحة|القانون|القواعد|الدليل|الآلية|التنظيم|الضوابط)"
_INDEF_NOUNS = r"(?:نظام|لائحة|قانون|قواعد|دليل|آلية|تنظيم|ضوابط)"

_SELF_RE = re.compile(
    r"من\s+(?P<dem>هذا\s+|هذه\s+)?(?P<noun>" + _SELF_NOUNS + r")\b"
    r"(?!\s+(?:التنفيذية\s+ل|الخاصة\s+ب))"
)
_INSTR_FRAGMENT = r"(?P<instr>اللائحة\s+التنفيذية\s+ل(?:نظام|لائحة)|ل?" + _INDEF_NOUNS + r")"
_NAMED_LAW_RE = re.compile(
    r"(?:من|طبقا|طبقاً|وفقا|وفقاً|بموجب|حسب|وفق)\s+" + _INSTR_FRAGMENT + r"\s+"
    r"(?!آخر\b|اخرى\b)(?P<name>[ء-ي](?:[ء-ي ]{0,60}))"
)
_AMBIGUOUS_BACKREF_RE = re.compile(
    r"من\s+(?:ذلك|تلك)\s+" + _SELF_NOUNS + r"\b"
    r"|" + _SELF_NOUNS + r"\s+(?:المشار\s+إليه[ا]?|سالف\s+الذكر|آنف\s+الذكر)"
)

_NAME_STOPWORDS = {"من", "الصادر", "الصادرة", "الذي", "التي", "وذلك", "حيث",
                   "رقم", "بتاريخ", "بموجب", "عدا", "باستثناء", "وتاريخ",
                   "أو", "او", "و"}

# Many "وفق ضوابط/قواعد/آلية ..." phrases are generic regulatory-delegation
# boilerplate ("قواعد يحددها المجلس" = "rules the Council shall determine"),
# not an actual reference to a named instrument. These consistently start
# with a present-tense verb carrying an attached object pronoun
# (يحددها/تحددها/تصدرها/تضعها/يصدرها/تصدره/...). Filtering them out front-
# loads precision: a citation this generator cannot tell apart from
# boilerplate is better skipped than recorded as a meaningless "law name".
_VERB_CONTINUATION_RE = re.compile(r"^[تين]\S{2,}(?:ها|ه|هما|هم)$")


def _looks_like_law_name(raw_name: str) -> bool:
    if not raw_name:
        return False
    first_word = raw_name.split(" ")[0]
    return not _VERB_CONTINUATION_RE.match(normalize_ar(first_word))


# A common closing phrase, "...ولائحته التنفيذية" ("...and its implementing
# regulation"), doesn't change WHICH primary law is named — stripped only
# for the match lookup, never from the stored raw citation text.
_IR_SUFFIX_RE = re.compile(
    r"\s+و(?:لائحته|لوائحه|الئحته|لوائحها|لائحتها)\s+التنفيذية\S*$"
)


def _strip_ir_suffix(name: str) -> str:
    return _IR_SUFFIX_RE.sub("", name).strip()


def _trim_law_name(raw: str) -> str:
    words = raw.split(" ")
    out = []
    for w in words:
        w_clean = re.split(r"[،,.؛:)\"'”»]", w)[0]
        if not w_clean:
            break
        if w_clean in _NAME_STOPWORDS:
            break
        out.append(w_clean)
        if w != w_clean:
            break
    return " ".join(out).strip()


def detect_scope(lookahead: str):
    """Returns a dict describing the citation's scope from the text right
    after a parsed 'المادة (X)' span: {'kind': 'self'} |
    {'kind': 'named', 'raw_name': ..., 'instr': ...} |
    {'kind': 'ambiguous'} | {'kind': 'none'}."""
    named = _NAMED_LAW_RE.search(lookahead)
    self_m = _SELF_RE.search(lookahead)
    # Prefer whichever pattern matches earliest in the lookahead window.
    if named and (not self_m or named.start() <= self_m.start()):
        raw_name = _trim_law_name(named.group("name"))
        if (raw_name and normalize_ar(raw_name) not in _GENERIC_PLACEHOLDER_NAMES
                and _looks_like_law_name(raw_name)):
            return {"kind": "named", "raw_name": raw_name, "instr": named.group("instr")}
    if self_m:
        # WHICH noun, and whether it was demonstrative, both matter downstream.
        # «من هذا النظام» inside a law is that law. «من النظام» inside an
        # IMPLEMENTING REGULATION is the parent law — a different instrument —
        # and reading it as self is the difference between citing article 217 of
        # the Bankruptcy Law and citing a 24-article set of case rules that has
        # no article 217. See resolve_parent_law() below.
        return {"kind": "self",
                "noun": normalize_ar(self_m.group("noun")),
                "demonstrative": bool(self_m.group("dem"))}
    if _AMBIGUOUS_BACKREF_RE.search(lookahead):
        return {"kind": "ambiguous"}
    return {"kind": "none"}


# ---------------------------------------------------------------------------
# Pass B: standalone law-name citations (no attached المادة number).
# ---------------------------------------------------------------------------

_STANDALONE_LAW_RE = re.compile(
    r"(?:وفقا|وفقاً|طبقا|طبقاً|وفق|حسب|بموجب|أحكام)\s+" + _INSTR_FRAGMENT + r"\s+"
    r"(?!آخر\b|اخرى\b)(?P<name>[ء-ي](?:[ء-ي ]{0,60}))"
)


def find_standalone_law_citations(text: str, consumed_spans):
    out = []
    for m in _STANDALONE_LAW_RE.finditer(text):
        if any(s <= m.start() < e for s, e in consumed_spans):
            continue
        raw_name = _trim_law_name(m.group("name"))
        if not raw_name or normalize_ar(raw_name) in _GENERIC_PLACEHOLDER_NAMES:
            continue
        if not _looks_like_law_name(raw_name):
            continue
        out.append((m.start(), m.end(), raw_name, m.group(0), m.group("instr")))
    return out


# ---------------------------------------------------------------------------
# Layer (unified-index source_layer) -> track_id map, cross-referenced from
# scripts/gen_corpus_unified_llm_index.py's own LAYERS list and the
# registry's own data_paths (never hand-copied).
# ---------------------------------------------------------------------------

def _load_layer_to_track_id(registry: dict):
    spec = importlib.util.spec_from_file_location("gen_corpus_unified_llm_index", GEN_UNIFIED_INDEX_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    path_to_track = {}
    for t in registry.get("tracks", []):
        for p in t.get("data_paths", []):
            path_to_track.setdefault(p, []).append(t["track_id"])

    layer_to_track = {}
    problems = []
    for rel, corpus, _default_component in mod.LAYERS:
        tids = path_to_track.get(rel, [])
        if len(tids) != 1:
            problems.append((rel, tids))
            continue
        layer_to_track[os.path.basename(rel)] = tids[0]
    if problems:
        raise SystemExit(
            "gen_corpus_cross_reference_graph: could not uniquely map these "
            "unified-index layers to a registry track_id: %r" % (problems,)
        )
    return layer_to_track


# ---------------------------------------------------------------------------
# «من النظام» inside a subordinate instrument is its PARENT LAW.
# ---------------------------------------------------------------------------
# This was the graph's largest single defect and it was invisible until the
# targets were checked against the corpus. An implementing regulation that says
# «المادة (٢١٧) من النظام» is citing article 217 of the LAW it implements. The
# scope detector read «من النظام» as a self-marker and pointed the reference
# back at the citing instrument, so:
#
#   * 224 references landed on an article number their own track does not have —
#     visibly broken, e.g. «قواعد نظر دعاوى الإفلاس» (24 records) cited as having
#     an article 217, or «لائحة طرق الاعتراض على الأحكام» (62) an article 185;
#   * and 1,110 more «resolved» — TO THE WRONG INSTRUMENT. A model following the
#     graph landed on a real article of the regulation when the citation meant an
#     article of the law. That is worse than the dangling ones: a silent wrong
#     answer does more damage than a visible missing one.
#
# The parent is read off the corpus's own structure, never guessed:
#
#   1. the citing track's own `base_law_track`, where its source artifact
#      declares one — an explicit statement by the track about itself;
#   2. otherwise the sibling track carrying the SAME corpus key with the
#      component «law». The unified index's corpus key is exactly the grouping
#      that pairs «arbitration_law» with «arbitration_implementing_regulation»;
#   3. otherwise nothing. The reference is emitted with a null target and the
#      type `parent_law_unresolved`, because a citation whose parent this corpus
#      cannot name is not a citation to the citing instrument.
#
# Only the NON-demonstrative «من النظام» is retargeted. «من هذا النظام» says
# THIS one, and where a drafter wrote that inside a regulation the reading is a
# judgement rather than a fact, so it is left alone.
_PARENT_NOUN = normalize_ar("النظام")
LAW_COMPONENTS = ("law",)


def _load_base_law_tracks():
    """{track_id: base_law_track} for every source artifact that declares one."""
    out = {}
    for pattern in ("sources/*/official_source/*.json",
                    "sources/*/*/official_source/*.json"):
        for path in glob.glob(os.path.join(ROOT, pattern)):
            try:
                with open(path, encoding="utf-8") as f:
                    doc = json.load(f)
            except Exception:                                     # noqa: BLE001
                continue
            base = (doc.get("base_law_track") or "").strip()
            if base:
                key = os.path.relpath(path, os.path.join(ROOT, "sources")).split(os.sep)[0]
                out.setdefault(key, base)
    return out


# ---------------------------------------------------------------------------
# A subordinate instrument usually SAYS what «النظام» means, in its own article 1
# ---------------------------------------------------------------------------
#
# The first two evidence tiers — a declared base_law_track, or the law component
# sitting in the same corpus key — left 415 citations across 75 tracks pointing
# at nothing, because those regulations declare no base and their parent law is
# filed under a different corpus key. The evidence was in the text the whole
# time: an implementing regulation opens by DEFINING its terms, and the first of
# them is almost always «النظام: نظام كذا».
#
# So the third tier reads the regulation's own definition and matches that NAME
# against the titles of the law tracks this corpus holds. That is reading the
# source, not inferring from topic — the regulation names its own parent.
#
# TITLE COLLISIONS ARE NOT A DETAIL, THEY ARE THE TRAP. Exactly two law titles
# are held twice: «نظام التنفيذ» and «نظام إيرادات الدولة». In both cases the pair
# is a law and its PUBLISHED-BUT-NOT-YET-IN-FORCE replacement — a shape this
# corpus only acquired when it started ingesting deferred repeals. A dictionary
# keyed by title silently keeps whichever it saw last, and the first run of this
# matcher duly pointed enforcement_providers_regulation at enforcement_law_1447:
# a regulation resolved to a law that will not be in force for months. The fix is
# not a preference for older tracks; it is to ASK THE SUPERSESSION GRAPH. A
# repeals_full_deferred edge names, in classified data, which of the pair is
# still the law in force — and that is the one a subordinate instrument's
# «النظام» means today.
#
# Anything still ambiguous stays unresolved. A citation with no target is a
# visible gap; a citation with the wrong target is a confident wrong answer.

_NIZAM_DEF_RE = re.compile(r"(?:^|[\s:،])ال?نظام\s*:\s*([^\n.،؛]{6,160})")
_DECREE_TAIL_RE = re.compile(r"\s*(?:الصادر|الصادرة|,|;)\s*")


def _norm_title(s):
    s = re.sub(r"[\u064B-\u0652\u0640]", "", s or "")
    s = (s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
          .replace("ة", "ه").replace("ى", "ي"))
    s = re.sub(r"[«»\"'()\[\]]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _held_law_titles(registry):
    """{normalised title: [track_id, ...]} for law-shaped tracks. A LIST, not a
    single id, because two titles are held twice and losing that is the bug."""
    out = {}
    for t in registry.get("tracks", []):
        nm = t.get("display_name_ar") or ""
        if nm.startswith(("نظام", "النظام")) and "لائحة" not in nm and "قواعد" not in nm:
            out.setdefault(_norm_title(nm), []).append(t["track_id"])
    return out


def _in_force_of_pair(candidates):
    """Given colliding law tracks, the one still in force per the supersession
    graph's own repeals_full_deferred edges. Returns None if it cannot tell."""
    path = os.path.join(ROOT, "data", "corpus_supersession_graph",
                        "corpus_supersession_graph.json")
    try:
        with open(path, encoding="utf-8") as f:
            graph = json.load(f)
    except (OSError, ValueError):                                  # noqa: BLE001
        return None
    deferred = {e["from_track_id"]: e.get("target_track_id")
                for e in graph.get("edges", [])
                if e.get("relation") == "repeals_full_deferred"}
    cand = set(candidates)
    for successor, predecessor in deferred.items():
        if successor in cand and predecessor in cand:
            return predecessor          # the successor has not commenced yet
    return None


def _self_declared_parent_names(rows, layer_to_track):
    """{track_id: the name it gives «النظام» in its own opening articles}."""
    first_texts = {}
    for r in rows:
        tid = layer_to_track.get(r.get("source_layer"))
        if tid is None or r.get("article_number") is None or r["article_number"] > 3:
            continue
        first_texts.setdefault(tid, []).append(r.get("text_ar") or "")
    out = {}
    for tid, texts in first_texts.items():
        m = _NIZAM_DEF_RE.search(re.sub(r"\s+", " ", " ".join(texts)))
        if m:
            out[tid] = _DECREE_TAIL_RE.split(m.group(1))[0].strip()
    return out


def build_parent_law_map(rows, layer_to_track, registry=None):
    """{track_id: parent_track_id or None} for every subordinate track.

    Also returns the evidence used per track, so the resolution can be audited
    rather than trusted."""
    corpus_of, component_of = {}, {}
    law_track_of_corpus = {}
    for r in rows:
        tid = layer_to_track.get(r.get("source_layer"))
        if tid is None:
            continue
        corpus_of[tid] = r["corpus"]
        component_of[tid] = r["law_component"]
        if r["law_component"] in LAW_COMPONENTS:
            law_track_of_corpus.setdefault(r["corpus"], tid)
    declared = _load_base_law_tracks()
    titles = _held_law_titles(registry or {})
    self_named = _self_declared_parent_names(rows, layer_to_track)

    parent, basis = {}, {}
    for tid, comp in component_of.items():
        if comp in LAW_COMPONENTS:
            continue                                   # a law's «النظام» is itself
        base = declared.get(tid)
        if base and base in component_of:
            parent[tid], basis[tid] = base, "declared_base_law_track"
            continue
        same = law_track_of_corpus.get(corpus_of[tid])
        if same:
            parent[tid], basis[tid] = same, "law_component_of_the_same_corpus"
            continue
        name = self_named.get(tid)
        if name:
            key = _norm_title(name)
            # «النظام الأساس للمستشفى / للجامعة / للمؤسسة» is a constitutive
            # statute naming ITSELF in shorthand. Six tracks say it, and the full
            # registry title («النظام الأساس لمستشفى الملك فيصل التخصصي ومركز
            # الأبحاث») never matches the shorthand, so a title matcher reports
            # "names a law this corpus does not hold" — which reads as a coverage
            # gap and is nothing of the kind. The phrase itself is the evidence.
            if key.startswith("النظام الاساس"):
                parent[tid] = tid
                basis[tid] = "self_declared_name_is_this_track_itself"
                continue
            cands = titles.get(key) or [
                v for k, vs in titles.items() for v in vs
                if len(key) > 12 and (key in k or k in key)]
            cands = sorted(set(cands))
            if len(cands) == 1 and cands[0] in component_of:
                parent[tid] = cands[0]
                # A constitutive statute that defines «النظام» as ITSELF is not
                # naming a parent. Kept in the map so the citation routes to
                # intra_law, labelled apart so no report calls it a parent.
                basis[tid] = ("self_declared_name_is_this_track_itself"
                              if cands[0] == tid
                              else "self_declared_definition_of_al_nizam")
                continue
            if len(cands) > 1:
                pick = _in_force_of_pair(cands)
                if pick and pick in component_of:
                    parent[tid] = pick
                    basis[tid] = ("self_declared_definition_of_al_nizam"
                                  "_collision_resolved_to_the_law_in_force")
                    continue
                parent[tid] = None
                basis[tid] = "ambiguous_title_matches_%d_held_laws" % len(cands)
                continue
            parent[tid] = None
            basis[tid] = "self_declared_name_matches_no_held_law"
            continue
        parent[tid], basis[tid] = None, "no_evidence_in_the_corpus"
    return parent, component_of, basis


# ---------------------------------------------------------------------------
# Main extraction.
# ---------------------------------------------------------------------------

def load_index():
    with open(INDEX_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def extract_references(rows, layer_to_track, track_cores,
                       parent_law=None, component_of=None):
    parent_law = parent_law or {}
    component_of = component_of or {}
    references = []
    for r in rows:
        track_id = layer_to_track.get(r.get("source_layer"))
        if track_id is None:
            continue
        text = r.get("text_ar") or ""
        if not text:
            continue
        source_article = r["article_number"]
        record_id = r["record_id"]

        pass_a_spans = []
        for (_s, e, num, raw_span) in find_article_citations(text):
            lookahead = text[e:e + 220]
            scope = detect_scope(lookahead)
            pass_a_spans.append((_s, e + len(scope.get("raw_name", ""))))

            if scope["kind"] == "named":
                tgt_tid, _score = match_law_name(_strip_ir_suffix(scope["raw_name"]), track_cores, scope.get("instr", ""))
                if tgt_tid == track_id:
                    # formally named itself by its own title -> treat as self
                    if num == source_article:
                        continue
                    references.append({
                        "source_track_id": track_id, "source_record_id": record_id,
                        "source_article_number": source_article, "type": "intra_law",
                        "target_track_id": track_id, "target_article_number": num,
                        "target_law_name_raw": None,
                        "raw_citation_text": raw_span.strip(),
                        "confidence": "high",
                    })
                else:
                    references.append({
                        "source_track_id": track_id, "source_record_id": record_id,
                        "source_article_number": source_article, "type": "inter_law",
                        "target_track_id": tgt_tid, "target_article_number": num,
                        "target_law_name_raw": scope["raw_name"],
                        "raw_citation_text": _clip_citation(raw_span, lookahead, scope["raw_name"]),
                        "confidence": "high" if tgt_tid else "medium",
                    })
            elif scope["kind"] == "self":
                # «من النظام» inside a subordinate instrument names its PARENT
                # law, not itself. See build_parent_law_map above for why, and
                # for the two facts the parent is read from.
                retarget = (scope.get("noun") == _PARENT_NOUN
                            and not scope.get("demonstrative")
                            and component_of.get(track_id) not in LAW_COMPONENTS
                            and track_id in parent_law)
                if retarget:
                    tgt = parent_law.get(track_id)
                    # A statute that DEFINES «النظام» as its own constitutive
                    # statute is not citing a parent — it is citing itself. The
                    # named-citation branch above already treats that as intra_law
                    # and this must agree, or the graph would carry a track listed
                    # as its own parent, which is how the earlier 1,110-reference
                    # mistargeting looked from the outside.
                    if tgt == track_id:
                        if num == source_article:
                            continue
                        references.append({
                            "source_track_id": track_id, "source_record_id": record_id,
                            "source_article_number": source_article, "type": "intra_law",
                            "target_track_id": track_id, "target_article_number": num,
                            "target_law_name_raw": None,
                            "raw_citation_text": _clip_citation(raw_span, lookahead, None),
                            "confidence": "high",
                        })
                        continue
                    references.append({
                        "source_track_id": track_id, "source_record_id": record_id,
                        "source_article_number": source_article,
                        "type": "parent_law" if tgt else "parent_law_unresolved",
                        "target_track_id": tgt, "target_article_number": num,
                        "target_law_name_raw": "النظام",
                        "raw_citation_text": _clip_citation(raw_span, lookahead, None),
                        "confidence": "high" if tgt else "medium",
                    })
                    continue
                if num == source_article:
                    continue
                references.append({
                    "source_track_id": track_id, "source_record_id": record_id,
                    "source_article_number": source_article, "type": "intra_law",
                    "target_track_id": track_id, "target_article_number": num,
                    "target_law_name_raw": None,
                    "raw_citation_text": _clip_citation(raw_span, lookahead, None),
                    "confidence": "high",
                })
            elif scope["kind"] == "ambiguous":
                references.append({
                    "source_track_id": track_id, "source_record_id": record_id,
                    "source_article_number": source_article, "type": "ambiguous_scope",
                    "target_track_id": None, "target_article_number": num,
                    "target_law_name_raw": None,
                    "raw_citation_text": _clip_citation(raw_span, lookahead, None),
                    "confidence": "medium",
                })
            else:  # no scope marker found nearby -> default same-law, lower confidence
                if num == source_article:
                    continue
                references.append({
                    "source_track_id": track_id, "source_record_id": record_id,
                    "source_article_number": source_article, "type": "intra_law",
                    "target_track_id": track_id, "target_article_number": num,
                    "target_law_name_raw": None,
                    "raw_citation_text": raw_span.strip(),
                    "confidence": "medium",
                })

        for (_s, _e, raw_name, matched_text, instr_text) in find_standalone_law_citations(text, pass_a_spans):
            tgt_tid, _score = match_law_name(_strip_ir_suffix(raw_name), track_cores, instr_text)
            if tgt_tid == track_id:
                continue  # self-citation by name, not a cross-reference
            references.append({
                "source_track_id": track_id, "source_record_id": record_id,
                "source_article_number": source_article, "type": "inter_law",
                "target_track_id": tgt_tid, "target_article_number": None,
                "target_law_name_raw": raw_name,
                "raw_citation_text": matched_text.strip(),
                "confidence": "high" if tgt_tid else "medium",
            })
    return references


def _clip_citation(raw_span: str, lookahead: str, raw_name):
    """Build a readable raw_citation_text: the matched المادة span plus a
    short trailing scope clause, capped to a sane length."""
    tail_len = min(len(lookahead), (len(raw_name) + 25) if raw_name else 30)
    tail = lookahead[:tail_len]
    combined = (raw_span + " " + tail).strip()
    combined = re.sub(r"\s+", " ", combined)
    return combined[:160].strip()


# A self-target the corpus provably cannot follow is not a self-target.
#
# Where no scope marker sits near a citation, this generator defaults it to the
# citing instrument at 'medium' confidence — the dominant convention, and the
# right default. It is still sometimes wrong, and when it is, the corpus can say
# so without any judgement at all: a five-article instrument has no article 155.
# That is arithmetic, not interpretation.
#
# So a reference that points at its own track at an article number that track
# does not hold is re-typed `intra_law_unresolved` and its target cleared. The
# citation is kept — the text really does say it — but the graph stops asserting
# a destination that is not there. 72 references were asserting one.
def mark_unfollowable_self_targets(references, rows, layer_to_track):
    held = {}
    for r in rows:
        tid = layer_to_track.get(r.get("source_layer"))
        if tid is not None:
            held.setdefault(tid, set()).add(r["article_number"])
    out = []
    for ref in references:
        tid = ref.get("target_track_id")
        num = ref.get("target_article_number")
        if (ref["type"] == "intra_law" and tid and tid == ref["source_track_id"]
                and num is not None and num not in held.get(tid, set())):
            ref = dict(ref, type="intra_law_unresolved", target_track_id=None,
                       confidence="medium")
        out.append(ref)
    return out


def build_graph():
    registry = load_registry()
    layer_to_track = _load_layer_to_track_id(registry)
    track_cores = _build_track_cores(registry)
    rows = load_index()

    parent_law, component_of, parent_basis = build_parent_law_map(
        rows, layer_to_track, registry)
    references = extract_references(rows, layer_to_track, track_cores,
                                    parent_law, component_of)
    references = mark_unfollowable_self_targets(references, rows, layer_to_track)

    intra = sum(1 for r in references if r["type"] == "intra_law")
    inter = sum(1 for r in references if r["type"] == "inter_law")
    ambiguous = sum(1 for r in references if r["type"] == "ambiguous_scope")

    graph = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "generated_from": "data/corpus_unified_index/corpus_unified_llm_index.jsonl "
                           "(text_ar of every article, across all 122 tracks) and "
                           "data/corpus_registry/corpus_registry.json (track "
                           "display_name_ar, for cross-law title resolution)",
        "extraction_caveat": EXTRACTION_CAVEAT,
        "known_limitations": KNOWN_LIMITATIONS,
        "total_records_scanned": len(rows),
        "total_references_extracted": len(references),
        "parent_law_resolution": {
            "note": (
                "كيف عُرف «النظام» الأمّ لكل أداةٍ تابعة، **مرتَّباً بقوة الدليل**: حقلُ "
                "`base_law_track` المُصرَّح به، ثم مكوّنُ النظام في مفتاح المدونة نفسه، ثم "
                "**تعريفُ الأداة نفسها لـ«النظام» في مادتها الأولى** — وهو قراءةٌ للمصدر لا "
                "استنتاجٌ من الموضوع. **وتصادمُ العناوين ليس تفصيلاً بل هو الفخّ**: عنوانان "
                "محمولان مرتين («نظام التنفيذ» و«نظام إيرادات الدولة»)، وكلاهما نظامٌ "
                "وخَلَفُه **المنشور غير النافذ**. أولُ تشغيلٍ صوّب لائحةَ مقدمي خدمات التنفيذ "
                "إلى النظام الذي **لن ينفذ قبل أشهر**. والحلُّ ليس تفضيلَ الأقدم بل **سؤالُ "
                "رسم النسخ**: ضلعُ `repeals_full_deferred` يسمّي — ببياناتٍ مُصنَّفة — أيَّهما "
                "**السَّاري اليوم**. وما بقي ملتبساً **يبقى بلا وجهة**: إحالةٌ بلا هدف ثغرةٌ "
                "مرئية، وإحالةٌ بهدفٍ خاطئ **جوابٌ واثقٌ خاطئ**."),
            "by_evidence": dict(sorted(collections.Counter(parent_basis.values()).items())),
            "resolved_parents": {k: v for k, v in sorted(parent_law.items())
                                 if v and v != k},
            "tracks_whose_al_nizam_is_themselves": sorted(
                k for k, v in parent_law.items() if v == k),
            "unresolved_tracks": sorted(k for k, v in parent_law.items() if not v),
        },
        "intra_law_count": intra,
        "inter_law_count": inter,
        "ambiguous_scope_count": ambiguous,
        "confidence_counts": {
            "high": sum(1 for r in references if r["confidence"] == "high"),
            "medium": sum(1 for r in references if r["confidence"] == "medium"),
        },
        "confidence_methodology": (
            "high: an explicit same-law marker ('من هذا النظام'/'من هذه "
            "اللائحة'/'من النظام'/etc, definite article) directly follows the "
            "citation, OR a named different/same law ('من نظام <X>') was "
            "matched against this corpus's own track titles with a "
            "distinctive, unambiguous score. medium: (a) an inter-law "
            "citation's law name text did not confidently resolve to one "
            "specific corpus track (target_track_id is null) — including "
            "the case of a bare title shared by two corpus tracks (this "
            "corpus's own documented social_insurance_law / "
            "social_insurance_legacy_law identical-title collision); or "
            "(b) no explicit scope marker was found near the citation at "
            "all, so it defaults to intra_law under this corpus's dominant "
            "bare-citation-means-same-law drafting convention, without the "
            "explicit confirmation that would warrant 'high'. "
            "ambiguous_scope citations are always 'medium' by construction."
        ),
        "references": references,
    }
    return graph


def main() -> int:
    graph = build_graph()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    print("Wrote %s" % OUT_PATH)
    print("  records scanned: %d" % graph["total_records_scanned"])
    print("  references extracted: %d (intra=%d inter=%d ambiguous=%d)"
          % (graph["total_references_extracted"], graph["intra_law_count"],
             graph["inter_law_count"], graph["ambiguous_scope_count"]))
    print("  confidence: %s" % graph["confidence_counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
