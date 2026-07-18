#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a best-effort cross-law glossary of each track's own defined terms.

Almost every one of this corpus's 123 tracks opens with a definitions
article — "يُقصد بالعبارات والمصطلحات التالية ..." / "تكون للكلمات والعبارات
الآتية ... المعاني المبينة أمام كل منها" / etc — listing term: definition
pairs. This scans every article's own text in the unified retrieval index
(data/corpus_unified_index/corpus_unified_llm_index.jsonl) for such articles,
splits each one into individual term:definition pairs, and groups the
results by (lightly normalized) term across the whole corpus — so a
consumer can ask "how does every law that defines «المشترك» define it?" and
see, e.g., that the current Social Insurance Law and the legacy Social
Insurance Law define «المشترك» differently, side by side.

THIS IS A BEST-EFFORT, REGEX/PATTERN-BASED NLP EXTRACTION, NOT AN
INDEPENDENTLY LEGALLY VERIFIED DATASET (unlike the rest of this corpus's
article text, which is independently source-verified). It favors precision
over recall: a definitions article whose format is too irregular to split
reliably is skipped rather than force-split. See `extraction_caveat` and
`known_limitations` in the generated output for details.

Extraction method
------------------
1. Identify each candidate definitions article by matching an opening
   "intro clause" against every article's own text (diacritic- and
   tatweel-insensitive, so "يُقصد" / "يقصد" / "تكون للألفاظ" / "تدل
   الكلمات والعبارات الواردة" / etc. all match regardless of harakat):
   a trigger verb (يقصد/يراد/تدل/يكون/تكون) followed, within a short
   window, by a carrier noun (كلمات/عبارات/ألفاظ/مصطلحات/اصطلاحات) and
   then by "الآتية/التالية/الواردة ... المعنى/المعاني". This is checked
   against EVERY article in the corpus (not just Article 1), since a
   handful of tracks carry a second, chapter-scoped definitions article
   later in the same law (e.g. Civil Aviation Law art. 133, scoped "in
   this chapter", for air-carrier-liability terms).
2. Within a matched article, term:definition pairs are split on a
   diacritic-insensitive "TERM: DEFINITION" boundary anchored at a
   paragraph/sentence start (start of article body, after a newline, or
   after a period/semicolon+space), tolerating a leading list marker
   (digit, dash, en dash, or none). A definition's span is capped at the
   next such boundary, or at a hard paragraph break (blank line), so a
   trailing unrelated clause (e.g. a closing non-list paragraph after the
   glossary, as in the Companies Law's Article 1) is not swallowed into
   the last term's definition.
3. A secondary, narrower pattern also recognizes the distinct
   "يقصد باصطلاح (TERM) DEFINITION" single-term-per-clause style used by a
   handful of tracks (e.g. the Banking Control Law), used only as a
   fallback when the primary colon-pair pattern finds nothing in an
   article whose intro clause otherwise matched.
4. A narrow, stricter fallback (no intro clause, >=5 parsed pairs, and the
   pairs must cover >=85% of the article's own text) also catches the
   small number of tracks whose definitions article has no boilerplate
   intro sentence at all and jumps straight into a numbered list (e.g. the
   Electronic Transactions Law's Article 1).
5. Extracted terms are grouped by a LIGHTLY normalized key (diacritics and
   tatweel stripped, whitespace collapsed) — deliberately NOT unifying
   alef/hamza variants (أ/إ/آ/ا), since that risks conflating genuinely
   different words (e.g. أمر "order" vs امر "matter"); see
   `known_limitations`. `definition_text` and `term_as_written` are always
   byte-exact substrings of the source article's own text_ar, never
   altered.

Read-only over data/corpus_unified_index/, data/corpus_registry/,
scripts/gen_corpus_unified_llm_index.py, and scripts/validate_corpus_registry.py;
deterministic and idempotent over its own output.

Usage:
    python3 scripts/gen_corpus_glossary.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
GEN_UNIFIED_INDEX_SCRIPT = os.path.join(ROOT, "scripts", "gen_corpus_unified_llm_index.py")
VALIDATE_REGISTRY_SCRIPT = os.path.join(ROOT, "scripts", "validate_corpus_registry.py")
OUT_DIR = os.path.join(ROOT, "data", "corpus_glossary")
OUT_PATH = os.path.join(OUT_DIR, "corpus_glossary.json")

SCHEMA_VERSION = "1.0.0"
GENERATED_BY = "scripts/gen_corpus_glossary.py"

EXTRACTION_CAVEAT = (
    "This glossary is a BEST-EFFORT, regex/pattern-based NLP extraction over "
    "each article's own free text. It is NOT an independently legally "
    "verified dataset in the way the rest of this corpus's article text is "
    "(MOJ-portal / BOE-portal cross-checked, etc.) — it is a heuristic "
    "reading of each law's own definitions-article boilerplate and list "
    "formatting. It favors PRECISION over RECALL: a definitions article "
    "whose format is too irregular to split into clean term:definition "
    "pairs is skipped rather than force-split (see tracks_skipped), and a "
    "handful of individual local single-term clarifications scattered "
    "elsewhere in a law's body (e.g. \"ويقصد بالمصطلحين ... لأغراض هذه "
    "المادة\" inside a substantive article, as opposed to the law's actual "
    "definitions article) are intentionally NOT extracted. definition_text "
    "and term_as_written are always byte-exact substrings of the source "
    "article's own text_ar — never summarized, translated, or reworded. "
    "Treat every entry as a candidate reading of that law's own defined "
    "term to verify against the article text itself, not as a confirmed, "
    "independently adjudicated legal definition. Not legal advice."
)

KNOWN_LIMITATIONS = [
    "Identification of a 'definitions article' relies on matching an "
    "opening intro clause (trigger verb + carrier noun + "
    "الآتية/التالية/الواردة + المعنى/المعاني, diacritic-insensitive) near "
    "the start of an article's own text. A law that defines its terms "
    "using different phrasing entirely outside this pattern set will be "
    "missed and will appear in tracks_skipped with a generic reason, not "
    "because it necessarily lacks definitions.",
    "A small, explicitly narrower fallback (no intro clause required, but "
    "the article must yield >=5 term:definition pairs covering >=85% of "
    "the article's own text, and only articles numbered <=5 are "
    "considered) recognizes the handful of tracks whose definitions "
    "article skips the boilerplate intro sentence entirely and jumps "
    "straight into a numbered term:definition list (e.g. the Electronic "
    "Transactions Law's Article 1). This fallback is intentionally strict "
    "to avoid mistaking an unrelated colon-heavy article (e.g. a penalty "
    "table) for a definitions list.",
    "Two Labor Law annex source layers (labor_annex1_violation_tables_llm.json, "
    "a violation/penalty table, and labor_annex2_accessibility_tables_llm.json "
    "and labor_annex5_contract_forms_llm.json, tabular/form annexes) are "
    "excluded from consideration entirely: their 'م: 1 | نوع المخالفة: ... "
    "| أول مرة: ...' pipe-table and form-field formatting is structurally "
    "colon-heavy in a way that superficially resembles a term:definition "
    "list but is not one, and forcing this generator's parser over it "
    "produced spurious matches in testing.",
    "A single article can carry TWO independent term:definition splitting "
    "strategies: the primary 'TERM: DEFINITION' colon-pair pattern, and a "
    "narrower 'يقصد باصطلاح (TERM) DEFINITION' parenthesized-term pattern "
    "used as a fallback only when the primary pattern finds nothing in an "
    "article whose intro clause otherwise matched (e.g. the Banking "
    "Control Law's Article 1, which defines each term via '(TERM)' rather "
    "than 'TERM:'). Both are best-effort regexes, not a general parser.",
    "At least 3 tracks' definitions articles are pure cross-references to "
    "another law's own Article 1 ('يكون للألفاظ ... المعاني المبينة في "
    "المادة الأولى من نظام كذا') with no local term:definition pairs of "
    "their own (bankruptcy_case_rules, judicial_costs_implementing_regulation, "
    "and — alongside one embedded single-term clarification this "
    "generator's patterns do not reliably isolate — bankruptcy_fees_regulation). "
    "These are recorded in tracks_skipped rather than forced; the terms "
    "they refer to are already captured under the referenced law's own "
    "track (e.g. bankruptcy_law's Article 1).",
    "Term grouping normalization strips Arabic diacritics/tatweel and "
    "collapses whitespace, but deliberately does NOT unify alef/hamza "
    "variants (أ vs إ vs آ vs ا) the way this corpus's cross-reference-"
    "graph generator does for LAW NAMES — for individual defined TERMS, "
    "unifying hamza forms risks silently conflating genuinely different "
    "words (e.g. أمر 'order/decree' vs امر 'matter/affair'). A term "
    "spelled with a different hamza form in two different laws will "
    "therefore appear as two separate keys in this glossary rather than "
    "being merged.",
    "The parser assumes each definitions article's list entries are "
    "separated by newlines, or run together in one paragraph separated by "
    "'N- term: definition.' markers; a definition's span is capped at a "
    "hard blank-line paragraph break so a trailing non-list sentence after "
    "the glossary isn't absorbed into the last term (observed in the "
    "Companies Law's Article 1, which appends a non-list closing sentence "
    "after its term list) — but a definitions list using some other "
    "internal separator entirely (no newlines, no numbering, run-on "
    "prose) would not be reliably split and should fail this generator's "
    "validity checks and be skipped rather than mis-split.",
    "A definitions article's SOURCE TEXT occasionally omits the expected "
    "sentence-ending period before the next term's own 'TERM:' clause "
    "(using a comma, or no punctuation at all, instead) — since this "
    "generator only anchors a new entry after a newline, a period, or a "
    "semicolon (plus whitespace), that next term's clause is swallowed "
    "into the PRECEDING term's definition_text instead of being split out "
    "as its own entry, for that occurrence. This is a source-text "
    "formatting inconsistency, not a generator bug: it is most visible in "
    "labor_recruitment_services_rules (Labor Law Annex 4), where roughly a "
    "quarter of its list entries are affected this way (e.g. its "
    "'صاحب العمل' entry runs on into an unsplit 'العامل: ...' clause). The "
    "swallowed term is usually still captured correctly under this "
    "glossary from ANOTHER track that defines the same word cleanly (e.g. "
    "'العامل' and 'صاحب العمل' are both correctly isolated under labor_law "
    "and social_insurance_law).",
    "A definitions article that itself nests lettered sub-categories "
    "inside one parent term's definition (e.g. '... وينقسم إلى قسمين: أ – "
    "... ب – ...') can have one of those inner sub-headings ALSO "
    "independently satisfy this generator's entry pattern, producing an "
    "extra, separate — still byte-exact, still accurate — term entry for "
    "that inner sub-heading alongside the parent term's own full "
    "definition (whose span still includes that same inner text). This is "
    "redundancy, not incorrect data, but means the same underlying source "
    "text can appear attached to two different term keys.",
    "3 registry tracks (implementing_regulations_general, "
    "implementing_regulations_listed_joint_stock, "
    "implementing_regulations_arabic_program_closure) have no records at "
    "all in data/corpus_unified_index/corpus_unified_llm_index.jsonl (that "
    "index only projects the primary per-law Arabic layers listed in "
    "gen_corpus_unified_llm_index.py's LAYERS, and these 3 companies-law "
    "sub-tracks are not among them) — there is nothing for this generator "
    "to scan for them, so they appear in tracks_skipped for that reason.",
]

# ---------------------------------------------------------------------------
# Diacritic-insensitive normalization with an index map back to the
# ORIGINAL text, so every extracted term_as_written / definition_text is a
# byte-exact substring of the source article despite matching being done on
# a normalized copy.
# ---------------------------------------------------------------------------

_ALEF_VARIANTS = set("أإآ")
_TATWEEL = "ـ"
_STRIP_EXTRA = set("*_")  # stray markdown-style emphasis punctuation seen in one track


def _is_ignorable(ch: str) -> bool:
    return unicodedata.combining(ch) != 0 or ch == _TATWEEL or ch in _STRIP_EXTRA


def build_norm_map(text: str):
    """Returns (normalized_text, idx_map) where idx_map[i] is the index in
    `text` of normalized_text[i]. Diacritics/tatweel/stray emphasis
    punctuation are dropped; أ/إ/آ are folded to ا for MATCHING purposes
    only (the original text is never altered)."""
    norm_chars, idx_map = [], []
    for i, ch in enumerate(text):
        if _is_ignorable(ch):
            continue
        c = "ا" if ch in _ALEF_VARIANTS else ch
        norm_chars.append(c)
        idx_map.append(i)
    return "".join(norm_chars), idx_map


def norm_span_to_orig(idx_map, orig_len, start, end):
    orig_start = idx_map[start] if start < len(idx_map) else orig_len
    if end <= 0:
        orig_end = 0
    elif end - 1 < len(idx_map):
        orig_end = idx_map[end - 1] + 1
    else:
        orig_end = orig_len
    return orig_start, orig_end


# ---------------------------------------------------------------------------
# Definitions-article intro-clause detector.
# ---------------------------------------------------------------------------

INTRO_RE = re.compile(
    r"(?:يقصد|يراد|تدل|يكون|تكون)[^.\n]{0,60}?"
    r"(?:كلمات|عبارات|لفاظ|مصطلحات|صطلاح)[^.\n]{0,40}?"
    r"(?:اتية|تالية|وارد)[^.\n]{0,100}?"
    r"(?:معان|معني|معنى)"
)
INTRO_MAX_START = 250  # normalized-char offset; keeps the check anchored near the article's own opening
# (some tracks front a short referential sentence — e.g. Investment
# Implementing Regulation art. 1's "تسري ذات المعاني ... على اللائحة
# أينما وردت." — before their own numbered "٢. يقصد بالألفاظ ..." list;
# 250 comfortably covers that while a full-corpus scan up to 400
# normalized chars found no other, spurious, deep-in-article match)

# Primary "TERM: DEFINITION" pair pattern. Anchored at string start, after a
# newline, or after a sentence/clause terminator + a single space; tolerates
# an optional leading list marker (digit(s) then a separator, and/or a bare
# dash/en-dash bullet with no digit).
ENTRY_RE = re.compile(
    r"(?:^|\n|(?<=[.۔])\s|(?<=؛)\s)"
    r"(?:"
    r"[0-9٠-٩]{1,3}\s*[-–.)۔]?\s*"      # 1- / ١. / ١- / ١ – ...
    r"|[ء-ي]{1,2}\s*[-–]\s*"            # أ- / ب– (abjad-letter bullet; dash required so a
                                          # real term's own first 1-2 letters are never eaten)
    r"|[-–.)۔]\s*"                       # bare dash/bullet, no leading digit or letter
    r")?"
    r"([ء-ي][ء-ي ]{0,45}?)"
    r"\s*:\s*"
)

# Secondary "يقصد باصطلاح (TERM) DEFINITION" pattern (e.g. Banking Control Law).
ALT_RE = re.compile(
    r"(?:^|\n)\s*(?:[0-9٠-٩]{1,3}\s*[-.)]\s*|[ء-ي]{1,3}\s*[-–]\s*)?"
    r"يقصد\s*ب(?:اصطلاح|مصطلح|كلمة|عبارة|لفظ)?\s*\(([ء-ي ]{1,60})\)\s*"
)

# A captured "term" that actually contains one of these is leftover intro
# boilerplate (the colon search landed on the wrong ':'), not a real term.
BOILERPLATE_SUBSTRINGS = [
    "يقصد", "يراد", "المعاني", "المعني", "الاتية", "التالية",
    "الوارد", "لاغراض", "اينما", "حيثما", "خلاف ذلك",
]


def term_ok(term: str) -> bool:
    t = term.strip()
    if not t or len(t) > 60:
        return False
    if len(t.split()) > 6:
        return False
    if any(b in t for b in BOILERPLATE_SUBSTRINGS):
        return False
    return True


def _entries_from_matches(matches, norm_text):
    out = []
    for i, m in enumerate(matches):
        term_start, term_end = m.span(1)
        def_start = m.end()
        def_end = matches[i + 1].start() if i + 1 < len(matches) else len(norm_text)
        # A hard paragraph break inside what would otherwise be this
        # definition's span means the list already ended (see Companies
        # Law art. 1's trailing non-list closing sentence).
        blank = norm_text.find("\n\n", def_start, def_end)
        if blank != -1:
            def_end = blank
        out.append({
            "term": m.group(1), "term_start": term_start, "term_end": term_end,
            "def_start": def_start, "def_end": def_end,
        })
    return out


def find_entries_norm(norm_text: str):
    return _entries_from_matches(list(ENTRY_RE.finditer(norm_text)), norm_text)


def find_alt_entries_norm(norm_text: str):
    return _entries_from_matches(list(ALT_RE.finditer(norm_text)), norm_text)


def _translate_entries(entries, offset, idx_map, orig_text):
    out = []
    for e in entries:
        ts, te = norm_span_to_orig(idx_map, len(orig_text), offset + e["term_start"], offset + e["term_end"])
        ds, de = norm_span_to_orig(idx_map, len(orig_text), offset + e["def_start"], offset + e["def_end"])
        term_as_written = orig_text[ts:te].strip()
        definition_text = orig_text[ds:de].strip()
        if not term_as_written or not definition_text:
            continue
        out.append({"term_as_written": term_as_written, "definition_text": definition_text})
    return out


def process_intro_matched_record(text: str):
    """Try to split a record whose text_ar carries a definitions-article
    intro clause into term:definition pairs. Returns (method, pairs) with
    method None and pairs [] if nothing usable was found."""
    norm, idx_map = build_norm_map(text)
    im = INTRO_RE.search(norm)
    if not (im and im.start() < INTRO_MAX_START):
        return None, []

    colon_pos = norm.find(":", im.end())
    if colon_pos == -1:
        colon_pos = norm.find("،", im.end())  # Arabic comma, rare alternate closer
    start_offset = colon_pos + 1 if colon_pos != -1 else im.end()

    entries = find_entries_norm(norm[start_offset:])
    valid = [e for e in entries if term_ok(e["term"])]
    if valid:
        return "colon_pairs", _translate_entries(valid, start_offset, idx_map, text)

    alt_entries = find_alt_entries_norm(norm)
    valid_alt = [e for e in alt_entries if term_ok(e["term"])]
    if valid_alt:
        return "parenthesized_term", _translate_entries(valid_alt, 0, idx_map, text)

    return None, []


TIER_B_MAX_ARTICLE_NUMBER = 5
TIER_B_MIN_ENTRIES = 5
TIER_B_MIN_COVERAGE = 0.85


def process_no_intro_record(text: str):
    """Narrow fallback for a definitions article with no boilerplate intro
    clause at all (e.g. Electronic Transactions Law art. 1). Requires many
    entries covering almost the entire article body, to avoid mistaking an
    unrelated colon-heavy article for a definitions list."""
    norm, idx_map = build_norm_map(text)
    if not norm:
        return None, []
    entries = find_entries_norm(norm)
    valid = [e for e in entries if term_ok(e["term"])]
    if len(valid) < TIER_B_MIN_ENTRIES:
        return None, []
    covered = sum(e["def_end"] - e["term_start"] for e in valid)
    if covered / len(norm) < TIER_B_MIN_COVERAGE:
        return None, []
    return "entries_only_no_intro", _translate_entries(valid, 0, idx_map, text)


# ---------------------------------------------------------------------------
# Source layers that are known tabular/form annexes, not prose law text —
# excluded outright (see known_limitations).
# ---------------------------------------------------------------------------

EXCLUDED_TABULAR_LAYERS = {
    "labor_annex1_violation_tables_llm.json",
    "labor_annex2_accessibility_tables_llm.json",
    "labor_annex5_contract_forms_llm.json",
}


# ---------------------------------------------------------------------------
# track_id resolution: derive it from the SAME LAYERS list + registry
# data_paths that the unified index generator itself uses, never hand-copied.
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
    for rel, _corpus, _default_component in mod.LAYERS:
        tids = path_to_track.get(rel, [])
        if len(tids) != 1:
            problems.append((rel, tids))
            continue
        layer_to_track[os.path.basename(rel)] = tids[0]
    if problems:
        raise SystemExit(
            "gen_corpus_glossary: could not uniquely map these unified-index "
            "layers to a registry track_id: %r" % (problems,)
        )
    return layer_to_track


def _import_required_track_ids():
    spec = importlib.util.spec_from_file_location("validate_corpus_registry", VALIDATE_REGISTRY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return list(mod.REQUIRED_TRACK_IDS)


def load_index():
    with open(INDEX_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def normalize_term_for_grouping(term: str) -> str:
    t = unicodedata.normalize("NFKC", term)
    t = "".join(ch for ch in t if not _is_ignorable(ch))
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ---------------------------------------------------------------------------
# Main extraction.
# ---------------------------------------------------------------------------

def build_glossary():
    registry = load_registry()
    layer_to_track = _load_layer_to_track_id(registry)
    required_track_ids = _import_required_track_ids()
    rows = load_index()

    records_by_track = {}
    for r in rows:
        if r.get("source_layer") in EXCLUDED_TABULAR_LAYERS:
            continue
        track_id = layer_to_track.get(r.get("source_layer"))
        if track_id is None:
            continue
        records_by_track.setdefault(track_id, []).append(r)

    terms: dict[str, list[dict]] = {}
    tracks_parsed = []
    tracks_skipped = []

    for track_id in required_track_ids:
        records = records_by_track.get(track_id)
        if not records:
            tracks_skipped.append({
                "track_id": track_id,
                "reason": ("No records for this track in "
                           "data/corpus_unified_index/corpus_unified_llm_index.jsonl "
                           "(either genuinely absent from that index, or every "
                           "candidate record belonged to an excluded tabular/form "
                           "source layer) — nothing to scan."),
            })
            continue
        records = sorted(records, key=lambda r: (r["article_number"], r["record_id"]))

        accepted = []  # list of (record, method, pairs)
        any_intro_hit = False
        for r in records:
            norm, _ = build_norm_map(r.get("text_ar") or "")
            im = INTRO_RE.search(norm)
            if im and im.start() < INTRO_MAX_START:
                any_intro_hit = True
                method, pairs = process_intro_matched_record(r.get("text_ar") or "")
                if method and pairs:
                    accepted.append((r, method, pairs))

        if not accepted:
            for r in records:
                if r["article_number"] > TIER_B_MAX_ARTICLE_NUMBER:
                    continue
                norm, _ = build_norm_map(r.get("text_ar") or "")
                im = INTRO_RE.search(norm)
                if im and im.start() < INTRO_MAX_START:
                    continue  # already attempted above and failed
                method, pairs = process_no_intro_record(r.get("text_ar") or "")
                if method and pairs:
                    accepted.append((r, method, pairs))

        if not accepted:
            if any_intro_hit:
                reason = ("A definitions-style intro clause was found, but this "
                          "generator's term:definition splitting patterns "
                          "(colon-pair and parenthesized-term) could not "
                          "reliably parse it — most commonly because the "
                          "article is a pure cross-reference to another law's "
                          "own Article 1 with no local term:definition pairs "
                          "of its own. Skipped per precision-over-recall "
                          "rather than force-split.")
            else:
                reason = ("No definitions-article intro clause "
                          "(يقصد بـ.../تكون للكلمات.../etc.) or a "
                          "reliably-parseable term:definition list was found "
                          "anywhere in this track's articles. This track may "
                          "genuinely lack a formal definitions article, or "
                          "define terms via phrasing outside this generator's "
                          "pattern coverage.")
            tracks_skipped.append({"track_id": track_id, "reason": reason})
            continue

        tracks_parsed.append(track_id)
        for r, method, pairs in accepted:
            for pair in pairs:
                key = normalize_term_for_grouping(pair["term_as_written"])
                if not key:
                    continue
                terms.setdefault(key, []).append({
                    "track_id": track_id,
                    "article_number": r["article_number"],
                    "term_as_written": pair["term_as_written"],
                    "definition_text": pair["definition_text"],
                    "source_record_id": r["record_id"],
                    "extraction_method": method,
                })

    # Deterministic ordering.
    for key in terms:
        terms[key].sort(key=lambda e: (e["track_id"], e["article_number"], e["source_record_id"]))
    sorted_terms = {k: terms[k] for k in sorted(terms.keys())}
    tracks_skipped.sort(key=lambda x: x["track_id"])

    total_definitions = sum(len(v) for v in sorted_terms.values())

    glossary = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "generated_from": ("data/corpus_unified_index/corpus_unified_llm_index.jsonl "
                            "(text_ar of every article, across all 123 tracks) and "
                            "data/corpus_registry/corpus_registry.json (track_id "
                            "resolution via each track's own data_paths)"),
        "extraction_caveat": EXTRACTION_CAVEAT,
        "known_limitations": KNOWN_LIMITATIONS,
        "total_tracks_in_registry": len(required_track_ids),
        "total_terms": len(sorted_terms),
        "total_definitions": total_definitions,
        "tracks_with_definitions_article_parsed": len(tracks_parsed),
        "tracks_skipped": tracks_skipped,
        "terms": sorted_terms,
    }
    return glossary


def main() -> int:
    glossary = build_glossary()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    print("Wrote %s" % OUT_PATH)
    print("  tracks in registry: %d" % glossary["total_tracks_in_registry"])
    print("  tracks with a parsed definitions article: %d" % glossary["tracks_with_definitions_article_parsed"])
    print("  tracks skipped: %d" % len(glossary["tracks_skipped"]))
    print("  total terms: %d" % glossary["total_terms"])
    print("  total definitions: %d" % glossary["total_definitions"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
