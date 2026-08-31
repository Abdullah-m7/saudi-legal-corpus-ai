#!/usr/bin/env python3
"""What exactly is recurring when a legal formula reappears?

The diffusion pass found 218 wording fingerprints circulating in ten or more
judgments, and removing them flipped the matched doctrinal first-mover verdict.
That is a fact about the corpus. It is NOT a demonstration that boilerplate
caused the effect, because nothing so far establishes WHAT those fingerprints
are. A recurring form of words can be an empty procedural shell; it can also be
the observable carrier of a stable legal proposition. Deleting the second kind
in the name of de-boilerplating would delete the signal.

So this pass re-reads the corpus and writes, for every non-statutory authority
mention, a family of fingerprints over the SAME +-90 character window, each
built by masking a different component:

    tmpl    source-preserving, identical to companions.py -- the existing unit
    tmplS   the matched authority string replaced by a placeholder
    tmplA   the article-number span of any statutory citation replaced
    tmplC   the instrument-name span of any statutory citation replaced
    tmplX   all three replaced -- the bare judicial shell

Two mentions sharing tmplX but not tmplS sit in one shell around different
authorities. Two sharing tmpl are the same passage. The difference between the
counts is the whole question.

It also writes a 32-value minhash sketch of token 3-shingles, so near-exact
variants can be grouped without an embedding model, and a set of mechanical
class markers (keyword presence, deterministic lists) so a coarse taxonomy can
be built and revised in analysis without re-reading the corpus.

NO JUDGMENT TEXT is written. Every fingerprint is a truncated SHA-1 of a
normalised window; the sketch is a set of minima of hashed shingles. Neither
can be inverted to a passage.

    python3 formula.py
"""
import gzip
import hashlib
import json
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import authority as A                 # noqa: E402
import companions as C                # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "formula_layer.jsonl.gz"
# 1442-1443 are the FORECAST_CALIBRATION_BACKFILL window and 1444-1446 the
# main window. Both are written to ONE file here because the fingerprint
# result being interrogated (218 circulating fingerprints) was itself computed
# on the union; splitting them would interrogate a different object.
YEARS = {1442, 1443, 1444, 1445, 1446}
NONSTATUTE = C.NONSTATUTE
W = C.W
PAD = 90                       # the context radius of the existing unit
BLOCK = C.BLOCK
norm = C.norm

# Placeholders. Arabic letters, so they survive norm()'s letter filter; five
# characters, so they survive the 1-2 character word filter; a fivefold repeat
# of one letter, which no Arabic word is.
MASK = {"SRC": "ططططط", "ART": "ضضضضض", "COD": "ظظظظظ"}

# ---------------------------------------------------------------- markers
# Deterministic keyword presence over the normalised window. These are
# MARKERS, not classes: the taxonomy is assembled from them in analysis, where
# classes that cannot be separated stably can be merged without re-reading the
# corpus. No model, no LLM label, no clustering.
MARKERS = {
    "PROCEDURAL": ("نظر الدعوى", "شطب", "الإحالة", "الجلسة", "المرافعة",
                   "اللائحة الجوابية", "التبليغ", "الميعاد", "القيد",
                   "الاستئناف", "الدفع بعدم", "الشكلية"),
    "JURISDICTION": ("الاختصاص", "الولاية", "نوعياً", "مكانياً",
                     "عدم اختصاص"),
    "DOCTRINAL": ("ومن المقرر", "الأصل", "يشترط", "لا يجوز", "يجب على",
                  "القاعدة", "مقتضى", "من المستقر"),
    "FRAME": ("ومن المقرر فقهاً", "وقد جاء في", "جاء في", "ورد في",
              "نص على", "استناداً إلى", "عملاً بـ", "قال", "ذكر",
              "كما في", "راجع"),
    "BURDEN": ("البينة", "اليمين", "براءة الذمة", "عبء الإثبات",
               "القرينة", "على المدعي", "الأصل براءة"),
    "HARM": ("التعويض", "الضرر", "الضمان", "العطل", "الكسب الفائت",
             "جبر الضرر", "الفائت"),
    "CONTRACT": ("العقد", "الشرط الجزائي", "الالتزام", "الإخلال", "الفسخ",
                 "الاتفاق", "التعاقد"),
    "DISPOSITION": ("حكمت", "إلزام", "رفض الدعوى", "المنطوق", "لذا تحكم",
                    "ترى الدائرة", "انتهت الدائرة"),
    "FACT_RECITAL": ("بمبلغ", "فاتورة", "بتاريخ", "سند لأمر", "طلبت المدعية",
                     "أقامت المدعية", "أقام المدعي", "قيدت"),
}
MARKERS_N = {k: tuple(sorted({norm(x) for x in v} - {""}))
             for k, v in sorted(MARKERS.items())}
QUOTE_CHARS = "«»“”\""

# ------------------------------------------------------------------ sketch
# A minhash over token 3-shingles. K permutations of one crc32, generated from
# a fixed seed at import, so the sketch is byte-identical across runs and
# across machines. This is what replaces an embedding model: Jaccard between
# two windows is estimated from 32 integers and nothing about word order or
# meaning is learned.
K, PRIME = 32, (1 << 31) - 1
_r = __import__("random").Random(20260831)
PERM = [(_r.randrange(1, PRIME), _r.randrange(0, PRIME)) for _ in range(K)]
SHINGLE = 3


def collapse(window):
    """Exactly what companions.fingerprint hashes, up to the hashing.

    The trailing space matters. companions.py collapses whitespace and does
    NOT strip afterwards, so a window ending in a two-letter particle hashes
    with a trailing blank. Reproducing that byte for byte is what makes tmpl
    here join to companion_layer.tmpl; a tidier implementation would silently
    fork the unit under interrogation.
    """
    w = re.sub(r"\b\w{1,2}\b", " ", norm(window))
    return re.sub(r"\s+", " ", w)


def digest(s):
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def tokens(s):
    return s.split()


def sketch(s):
    toks = tokens(s)
    if len(toks) >= SHINGLE:
        sh = {" ".join(toks[i:i + SHINGLE])
              for i in range(len(toks) - SHINGLE + 1)}
    else:
        sh = set(toks)
    if not sh:
        return [0] * K
    hs = [zlib.crc32(s.encode()) for s in sorted(sh)]
    return [min((a * h + b) % PRIME for h in hs) for a, b in PERM]


def apply_masks(window, spans):
    """spans: (start, end, kind) in window coordinates, non-overlapping wins."""
    out, prev = [], len(window)
    for s, e, kind in sorted(spans, key=lambda x: -x[0]):
        if e > prev or s < 0 or e <= s:
            continue                        # overlapping or degenerate: drop
        out.append((s, e, kind))
        prev = s
    w = window
    for s, e, kind in out:
        w = w[:s] + " " + MASK[kind] + " " + w[e:]
    return w


# CITE's instrument group runs greedily to the next punctuation, so it
# captures «نظام الإثبات على ذلك» where the instrument name is «نظام
# الإثبات». Masking the raw group would erase two clauses of judicial wording
# and call the result a code mask. The name is therefore truncated at the
# first word that cannot continue an instrument title -- a fixed, closed list
# of particles and clause openers -- with a hard ceiling of six words. Every
# truncation is counted and reported; tmplC is a BOUNDED approximation of a
# code mask, not an exact one, and is read alongside the locus fields rather
# than instead of them.
STOP = {norm(x) for x in (
    "على", "عن", "إلى", "أن", "بأن", "حيث", "وقد", "فإن", "كما", "وهو",
    "مما", "بما", "التي", "الذي", "وذلك", "ذلك", "وهي", "إذ", "وإذ", "بل",
    "ثم", "وهذا", "هذا", "قد", "لا", "ما", "في", "و", "أو", "لم", "قال",
    "نصت", "تنص", "وهذه", "منه", "منها", "عليه", "عليها")}
NAME_MAX = 5


def name_span(text, a2, e2):
    """The instrument title inside CITE's greedy instrument capture."""
    toks, i = [], a2
    while i < e2:
        while i < e2 and text[i].isspace():
            i += 1
        j = i
        while j < e2 and not text[j].isspace():
            j += 1
        if j > i:
            toks.append((i, j))
        i = j
    end, trunc = e2, False
    for k, (i, j) in enumerate(toks):
        if k == 0:
            end = j
            continue
        if k >= NAME_MAX or norm(text[i:j]) in STOP:
            trunc = True
            break
        end = j
    return end, (trunc or end < e2)


def cites(text):
    """(match span, article span, instrument-title span, truncated?)."""
    out = []
    for m in V.CITE.finditer(text):
        a2, e2 = m.span(2)
        end, trunc = name_span(text, a2, e2)
        out.append((m.start(), m.end(), m.span(1), (a2, end), trunc))
    return out


def main():
    index, order = M.build(REGISTRY)
    n = docs = 0
    with gzip.open(OUT, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": {
            "years": sorted(YEARS), "contextRadius": PAD, "window": W,
            "sketch": {"algorithm": "minhash", "k": K, "shingle": SHINGLE,
                       "seed": 20260831, "base": "crc32", "prime": PRIME},
            "fields": "j y city ct voice type rule cid label resolved "
                      "instBlock artBlock instW artW nt nc ncTrunc rel qm qn mk "
                      "tmpl tmplS tmplA tmplC tmplX sk",
            "fingerprints": {
                "tmpl": "source-preserving; identical by construction to "
                        "companion_layer.tmpl",
                "tmplS": "matched authority string masked",
                "tmplA": "article-number span of every statutory citation in "
                         "the window masked",
                "tmplC": "instrument-title span of every statutory citation "
                         "in the window masked, the title bounded by a fixed "
                         "stop-word rule; ncTrunc counts how many needed "
                         "bounding, so tmplC can be read on unbounded windows "
                         "only",
                "tmplX": "all three masked: the bare judicial shell"},
            "note": "one row per non-statutory authority mention. NO judgment "
                    "text. Every tmpl* is a truncated SHA-1 of a normalised "
                    "window; sk is a minhash sketch. Neither is invertible. "
                    "mk is mechanical keyword presence, not a class: the "
                    "taxonomy is assembled downstream. Co-occurrence of a "
                    "mask class with a fingerprint is not evidence of "
                    "copying, influence, or legal dependence.",
            "digitsAndPunctuation": "removed by norm() before hashing, so "
                                    "numeric article references were already "
                                    "invisible to the existing unit; what "
                                    "tmplA adds is the removal of ARABIC-"
                                    "SPELLED ordinals, which survived",
        }}, ensure_ascii=False) + "\n")
        for rec in judgments():
            y = year_of(rec)
            if y not in YEARS:
                continue
            text, s = rec["text"], rec.get("sections") or {}
            spans = V.segments(text, s)
            rea = [(a, b) for a, b, v in spans if v == "reasoning"]
            if not rea:
                continue
            docs += 1
            ments = A.mentions(text, s, index, order)
            stat = [(m["at"], m["instrument"], m["article"]) for m in ments
                    if m["type"] == "statute" and not m.get("inQuote")
                    and m.get("instrument")]
            cts = cites(text)
            cuts = sorted({c for a, b in rea
                           for c in [a] + [x.end() + a for x in
                                           BLOCK.finditer(text[a:b])] + [b]})

            def blk(p):
                lo = 0
                for c in cuts:
                    if c <= p:
                        lo = c
                    else:
                        return (lo, c)
                return (lo, len(text))

            for m in ments:
                if m["type"] not in NONSTATUTE or m.get("inQuote"):
                    continue
                voice = A.voice(m)
                if voice not in ("court_reasoning", "party_argument",
                                 "recital"):
                    continue
                at = m["at"]
                raw = ""
                for t, rid, pat, _ in A.COMPILED:
                    if rid != m["rule"]:
                        continue
                    mm = pat.match(text, at) or pat.search(text, at, at + 60)
                    if mm:
                        raw = mm.group(0)
                    break
                cid, label, resolved, merged = C.canonical(m["rule"], raw)
                a, b = at, at + max(1, len(raw))
                w0, w1 = max(0, a - PAD), min(len(text), b + PAD)
                win = text[w0:w1]
                src = [(a - w0, min(b, w1) - w0, "SRC")]
                arts, cods = [], []
                ctrunc = 0
                for cs, ce, (a1, e1), (a2, e2), tr in cts:
                    if ce <= w0 or cs >= w1:
                        continue
                    if w0 <= a1 and e1 <= w1:
                        arts.append((a1 - w0, e1 - w0, "ART"))
                    if w0 <= a2 and e2 <= w1:
                        cods.append((a2 - w0, e2 - w0, "COD"))
                        ctrunc += int(tr)
                t_base = collapse(win)
                mb = blk(at)
                ib = [(p, i, ar) for p, i, ar in stat if mb[0] <= p < mb[1]]
                iw = [(p, i, ar) for p, i, ar in stat if abs(p - at) <= W]
                nb = min(ib, key=lambda x: abs(x[0] - at)) if ib else None
                nw = min(iw, key=lambda x: abs(x[0] - at)) if iw else None
                wn = norm(win)
                mk = sorted(k for k, pats in MARKERS_N.items()
                            if any(p in wn for p in pats))
                fh.write(json.dumps({
                    "j": rec["id"], "y": y,
                    "city": rec.get("city") or "",
                    "ct": rec.get("court_type") or "",
                    "voice": ("court" if voice == "court_reasoning"
                              else "party"),
                    "type": m["type"], "rule": m["rule"],
                    "cid": cid, "label": label, "resolved": resolved,
                    "merged": merged,
                    "instBlock": nb[1] if nb else None,
                    "artBlock": nb[2] if nb else None,
                    "instW": nw[1] if nw else None,
                    "artW": nw[2] if nw else None,
                    "nt": len(tokens(t_base)),
                    "nc": len(cods), "ncTrunc": ctrunc,
                    "rel": round(at / max(1, len(text)), 3),
                    "qm": any(c in win for c in QUOTE_CHARS),
                    "qn": any(c in text[b:b + 40] for c in "«“\""),
                    "mk": mk,
                    "tmpl": digest(t_base),
                    "tmplS": digest(collapse(apply_masks(win, src))),
                    "tmplA": digest(collapse(apply_masks(win, arts))),
                    "tmplC": digest(collapse(apply_masks(win, cods))),
                    "tmplX": digest(collapse(apply_masks(win, src + arts + cods))),
                    "sk": sketch(t_base),
                }, ensure_ascii=False) + "\n")
                n += 1
    print(f"{n:,} non-statutory mentions from {docs:,} judgments -> "
          f"{OUT.name} ({OUT.stat().st_size/1e6:.1f} MB gzipped)")


if __name__ == "__main__":
    main()
