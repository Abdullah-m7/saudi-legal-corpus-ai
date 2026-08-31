#!/usr/bin/env python3
"""What exactly is recurring when a legal formula reappears?

The diffusion pass ended on an uncomfortable fact: remove every mention whose
+-90 character wording fingerprint recurs in ten or more judgments and the
matched doctrinal first-mover verdict flips. That was reported, frozen, and
correctly NOT explained. It is tempting to read it as "templates caused the
effect". Nothing established that. A recurring form of words can be an empty
procedural shell; it can equally be the observable carrier of a stable legal
proposition, in which case the de-boilerplating control deleted the signal it
was built to protect.

So the recurring wording is not called a TEMPLATE here. It is a RECURRING
LEGAL FORMULA until measurement says what it is.

The programme:

    what one fingerprint is                          (the unit, documented)
    exact recurrence versus near recurrence          (minhash, no embeddings)
    does the SOURCE recur, or a shell that receives  (the key mask)
        different sources
    does the ARTICLE or the CODE recur               (two more masks)
    a coarse mechanical taxonomy from keyword        (no model, no labels)
        markers, with unseparable classes merged
    quotation versus judicial wording
    the source-to-formula coupling
    AND THEN the falsification that matters: instead of deleting all
        recurring formulas at once, delete ONE CLASS AT A TIME and re-run
        the doctrinal first-mover result

Nothing here is causal. A formula appearing in two judgments is co-occurrence
of wording. It is never copying, influence, or citation of one court by
another, and the word is never used.

    python3 formula_analysis.py
"""
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diffusion as D                      # noqa: E402
import foresight as F                      # noqa: E402
import formula as FM                       # noqa: E402

OUT = HERE / "formula_analysis_results.json"
ASSET = HERE / "formula_diffusion_asset.json"
LAYER = HERE / "formula_layer.jsonl.gz"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY
MIN_J = 10          # the circulation threshold the frozen control used
K = 32              # minhash length, from formula.py


def load():
    with gzip.open(HERE / "judgment_dates.json.gz", "rt", encoding="utf-8") as fh:
        dates = {k: tuple(v) for k, v in json.load(fh)["dates"].items()}
    rows, schema = [], None
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r:
                schema = r["_schema"]
                continue
            d = dates.get(r["j"])
            if not d:
                continue
            p = (d[0], (d[1] - 1) // 3 + 1)
            if p in PKEY:
                r["p"], r["i"] = p, PKEY[p]
                rows.append(r)
    return rows, schema


# ------------------------------------------------------------------ PHASE 2
def unit_spec(rows, schema):
    """What does ONE fingerprint scientifically represent?

    Read off the code that built it rather than assumed. This is written
    before anything is changed, because the object under interrogation is the
    existing unit and a tidier one would be a different object.
    """
    nt = sorted(r["nt"] for r in rows)
    nc = Counter(r["nc"] for r in rows)
    q = lambda s: s[int(len(s) * 0.5)] if s else None
    withcite = [r for r in rows if r["nc"]]
    return {
        "definition": "SHA-1, first 12 hex characters, of a normalised "
                      "window of +-90 characters around the matched "
                      "authority string.",
        "normalisation": [
            "diacritics and tatweel removed",
            "whitespace collapsed to single spaces",
            "orthography folded: أ إ آ -> ا, ى -> ي, ة -> ه",
            "every character outside [Arabic letter, space] deleted -- so "
            "DIGITS AND PUNCTUATION ARE REMOVED",
            "every word of 1 or 2 characters removed -- so most particles, "
            "conjunctions and prepositions are gone",
            "no stemming, no stop-word list beyond the length filter",
        ],
        "contextRadius": schema["contextRadius"],
        "minimumLength": "none. A window is hashed however short it is; the "
                         "observed token count is reported below rather than "
                         "enforced.",
        "windowTokens": {"median": q(nt), "p10": nt[len(nt) // 10],
                         "p90": nt[len(nt) * 9 // 10],
                         "min": nt[0], "max": nt[-1],
                         "under5Tokens": round(
                             sum(1 for x in nt if x < 5) / len(nt), 4)},
        "authorityTokensIncluded": True,
        "authorityTokensNote": "the matched authority string sits inside the "
                               "window, so the existing unit is "
                               "SOURCE_PRESERVING: two mentions of different "
                               "sources cannot share a fingerprint unless "
                               "the source names normalise identically.",
        "articleNumbersPreserved": "PARTIALLY, and this was not obvious. "
                                   "Numeric article references die with the "
                                   "digits. ARABIC-SPELLED ordinals -- "
                                   "«المادة الثانية عشرة» -- are ordinary "
                                   "words and survive.",
        "codeNamesPreserved": True,
        "courtNamesRemoved": "NOT removed by rule. Nothing strips a court or "
                             "city name; they survive if they fall in the "
                             "window.",
        "numericNormalisation": "none needed -- numbers are deleted, not "
                                "normalised.",
        "punctuation": "deleted, so a sentence boundary inside the window is "
                       "invisible and a fingerprint may straddle two "
                       "sentences.",
        "exactOrNearExact": "EXACT. A cryptographic hash has no neighbourhood; "
                            "one different surviving word is a different "
                            "fingerprint. No near-duplicate grouping existed "
                            "before this pass.",
        "citationsInWindow": {
            "mentionsWithAStatutoryCitationInWindow": len(withcite),
            "share": round(len(withcite) / len(rows), 4),
            "citationsPerWindow": dict(sorted(nc.items())),
            "instrumentTitleBounded": round(
                sum(r["ncTrunc"] for r in rows) / max(1, sum(r["nc"] for r in rows)), 4),
            "boundingNote": "CITE's instrument capture runs greedily to the "
                            "next punctuation, so the code mask bounds the "
                            "title at a fixed stop-word list. The share above "
                            "is how often that bounding fired.",
        },
        "whatOneFingerprintIs": "a claim that two passages, after losing "
                                "their numbers, punctuation and short words, "
                                "are the SAME ~25-word neighbourhood of an "
                                "authority. It is a statement about wording. "
                                "It is not a statement about meaning, and it "
                                "is not evidence that one passage was copied "
                                "from another.",
        "whyThisMattersForTheFrozenControl": "the de-boilerplating control "
                                             "removed mentions on this "
                                             "criterion alone. Whether that "
                                             "removed noise or signal is the "
                                             "question the rest of this file "
                                             "asks.",
    }


# ------------------------------------------------------------------ PHASE 3
def circulating(rows, key="tmpl", min_j=MIN_J):
    by = defaultdict(set)
    for r in rows:
        by[r[key]].add(r["j"])
    return {t for t, js in by.items() if len(js) >= min_j}


def families(rows):
    """EXACT_FORMULA versus FORMULA_FAMILY, with a stability gate.

    Grouping is a banded minhash over token 3-shingles: 8 bands of 4, then an
    estimated-Jaccard check on the full 32-value sketch. No embedding model,
    no learned representation, no opaque clustering -- a family is a
    transitive closure of pairs whose token 3-shingle sets are estimated to
    overlap above a stated threshold, and the threshold is varied to see
    whether the answer holds.

    If the grouping is not stable across thresholds the finding is that it is
    not stable, and the rest of the file uses EXACT only.
    """
    circ = circulating(rows)
    sk = {}
    for r in rows:
        if r["tmpl"] in circ:
            sk.setdefault(r["tmpl"], tuple(r["sk"]))
    keys = sorted(sk)
    bands, rband = 8, K // 8
    buckets = defaultdict(list)
    for t in keys:
        v = sk[t]
        for b in range(bands):
            buckets[(b, v[b * rband:(b + 1) * rband])].append(t)
    cand = set()
    for members in buckets.values():
        if len(members) < 2:
            continue
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                cand.add((members[a], members[b]))
    est = {(a, b): sum(1 for x, y in zip(sk[a], sk[b]) if x == y) / K
           for a, b in sorted(cand)}

    def group(th):
        parent = {t: t for t in keys}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for (a, b), j in sorted(est.items()):
            if j >= th:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
        g = defaultdict(list)
        for t in keys:
            g[find(t)].append(t)
        return {r: sorted(v) for r, v in g.items()}

    out, mapping = {}, {}
    for th in (0.6, 0.7, 0.8):
        g = group(th)
        sizes = sorted((len(v) for v in g.values()), reverse=True)
        mapping[th] = {t: r for r, v in g.items() for t in v}
        out[f"threshold{int(th * 100)}"] = {
            "families": len(g),
            "exactFormulasGrouped": sum(1 for v in g.values() if len(v) > 1),
            "largestFamily": sizes[0] if sizes else 0,
            "familiesLargerThanOne": sum(1 for s in sizes if s > 1),
        }
    # stability: of the pairs co-grouped at 0.7, how many survive at 0.8 and
    # are already together at 0.6?
    def pairs_of(m):
        inv = defaultdict(list)
        for t, r in m.items():
            inv[r].append(t)
        s = set()
        for v in inv.values():
            v = sorted(v)
            for a in range(len(v)):
                for b in range(a + 1, len(v)):
                    s.add((v[a], v[b]))
        return s
    p6, p7, p8 = (pairs_of(mapping[t]) for t in (0.6, 0.7, 0.8))
    keep = round(len(p7 & p8) / len(p7), 4) if p7 else None
    grow = round(len(p7 & p6) / len(p7), 4) if p7 else None
    stable = bool(p7) and keep is not None and keep >= 0.6
    return {
        "exactFormulas": len(circ),
        "mentionsInCirculatingFormulas": sum(
            1 for r in rows if r["tmpl"] in circ),
        "grouping": out,
        "stability": {
            "pairsAt70": len(p7),
            "shareSurvivingAt80": keep,
            "shareAlreadyTogetherAt60": grow,
            "verdict": "FAMILY_GROUPING_STABLE" if stable
                       else "FAMILY_GROUPING_UNSTABLE_USE_EXACT_ONLY",
        },
        "decision": ("families are reported alongside exact formulas"
                     if stable else
                     "every downstream phase uses EXACT formulas. Near-exact "
                     "grouping was built, tested and set aside because it "
                     "does not survive a change of threshold, which is the "
                     "honest outcome of a fuzzy-grouping check rather than a "
                     "reason to pick a threshold and proceed."),
        "method": "banded minhash (8 bands of 4) over token 3-shingles, "
                  "seeded and deterministic; no embedding model.",
    }


# --------------------------------------------------------------- PHASE 4
def source_masking(rows):
    """Does the SOURCE recur, or does a judicial SHELL receive many sources?

    This is the methodological centre of the programme. The existing unit
    keeps the authority's own words inside the window, so "the same formula"
    and "the same source" cannot be told apart by construction. Masking the
    matched string separates them: two mentions sharing tmplS but not tmpl
    are the same wording around DIFFERENT authorities.
    """
    circ_p = circulating(rows, "tmpl")
    circ_m = circulating(rows, "tmplS")
    shells = defaultdict(lambda: {"cid": Counter(), "j": set(), "tmpl": set(),
                                  "voice": set(), "code": set()})
    for r in rows:
        d = shells[r["tmplS"]]
        d["cid"][r["cid"]] += 1
        d["j"].add(r["j"])
        d["tmpl"].add(r["tmpl"])
        d["voice"].add(r["voice"])
        if r["instW"]:
            d["code"].add(r["instW"])
    circ_shells = {t: d for t, d in shells.items() if t in circ_m}
    multi = {t: d for t, d in circ_shells.items() if len(d["cid"]) > 1}
    ment_multi = sum(sum(d["cid"].values()) for d in multi.values())
    top = []
    for t, d in sorted(multi.items(),
                       key=lambda kv: (-len(kv[1]["cid"]), -len(kv[1]["j"]),
                                       kv[0]))[:10]:
        top.append({"shell": t, "distinctSources": len(d["cid"]),
                    "judgments": len(d["j"]),
                    "exactVariants": len(d["tmpl"]),
                    "sources": [c for c, _ in sorted(
                        d["cid"].items(), key=lambda kv: (-kv[1], kv[0]))[:6]]})
    share = round(len(multi) / len(circ_shells), 4) if circ_shells else None
    verdict = ("SHELL_RECEIVES_DIFFERENT_SOURCES" if share and share >= 0.5
               else "RECURRENCE_IS_LARGELY_SOURCE_BOUND" if share is not None
               and share < 0.2 else "MIXED")
    return {
        "distinctFormulas": {"sourcePreserving": len({r["tmpl"] for r in rows}),
                             "sourceMasked": len({r["tmplS"] for r in rows})},
        "circulatingFormulas": {"sourcePreserving": len(circ_p),
                                "sourceMasked": len(circ_m)},
        "circulatingShells": len(circ_shells),
        "shellsWithMoreThanOneSource": len(multi),
        "shellsWithMoreThanOneSourceShare": share,
        "mentionsInMultiSourceShells": ment_multi,
        "medianSourcesPerCirculatingShell": (
            sorted(len(d["cid"]) for d in circ_shells.values())[
                len(circ_shells) // 2] if circ_shells else None),
        "topMultiSourceShells": top,
        "verdict": verdict,
        "verdictMeans": "AT THE CURRENT EXACT-FINGERPRINT RESOLUTION, no "
                        "circulating formula is observed with more than one "
                        "canonical authority identity. Near-family "
                        "equivalence is unresolved, so this is an absence of "
                        "observation and not a demonstration that a "
                        "source-independent shell cannot exist.",
        "reading": "a circulating shell that carries only one source is a "
                   "recurring passage about that source. A shell carrying "
                   "several is a judicial form of words into which different "
                   "authorities are placed. The two are different objects and "
                   "the de-boilerplating control removed both.",
        "notCopying": "two judgments sharing a shell is co-occurrence of "
                      "wording. No claim is made that either was written from "
                      "the other, or from a common draft.",
    }


# --------------------------------------------------------------- PHASE 5
def article_code_masking(rows):
    """ARTICLE FORMULA, CODE FORMULA, or GENERAL JUDICIAL FORMULA."""
    n = {k: len({r[k] for r in rows})
         for k in ("tmpl", "tmplS", "tmplA", "tmplC", "tmplX")}
    withcite = [r for r in rows if r["nc"]]
    n_cite = {k: len({r[k] for r in withcite})
              for k in ("tmpl", "tmplA", "tmplC", "tmplX")}
    circ = circulating(rows, "tmpl")
    # classify each circulating formula by the loci it actually visits
    prof = defaultdict(lambda: {"code": Counter(), "art": Counter(),
                                "j": set()})
    for r in rows:
        if r["tmpl"] not in circ:
            continue
        d = prof[r["tmpl"]]
        d["j"].add(r["j"])
        if r["instW"]:
            d["code"][r["instW"]] += 1
            if r["artW"]:
                d["art"][(r["instW"], r["artW"])] += 1
    cls = Counter()
    for t, d in prof.items():
        if not d["code"]:
            cls["NO_LOCAL_CODE"] += 1
        elif len(d["code"]) > 1:
            cls["GENERAL_JUDICIAL_FORMULA"] += 1
        elif d["art"] and max(d["art"].values()) / sum(d["art"].values()) >= 0.8:
            cls["ARTICLE_FORMULA"] += 1
        else:
            cls["CODE_FORMULA"] += 1
    return {
        "distinctFingerprintsByMask": n,
        "distinctFingerprintsByMaskCitationWindowsOnly": n_cite,
        "collapseFromArticleMask": round(
            1 - n_cite["tmplA"] / n_cite["tmpl"], 4) if n_cite["tmpl"] else None,
        "collapseFromCodeMask": round(
            1 - n_cite["tmplC"] / n_cite["tmpl"], 4) if n_cite["tmpl"] else None,
        "collapseFromAllMasks": round(
            1 - n["tmplX"] / n["tmpl"], 4) if n["tmpl"] else None,
        "circulatingFormulaLocus": dict(sorted(cls.items())),
        "reading": "the article mask can only collapse fingerprints that "
                   "differ by an ARABIC-SPELLED ordinal, because digits were "
                   "already gone. Its collapse rate is therefore a direct "
                   "measure of how much of the recurring wording is tied to a "
                   "specific article rather than to a code or to nothing.",
        "note": "locus classification uses the observed spread of a formula "
                "over codes and articles, which is independent of the masks "
                "and does not inherit their bounding rule.",
    }


# --------------------------------------------------------------- PHASE 6
# A COARSE taxonomy, assigned by a fixed priority over mechanical keyword
# markers. No model, no clustering, no LLM label. The priority is written down
# before any outcome is read, and classes that the markers cannot separate are
# merged rather than reported as if they were distinct.
PRIORITY = [
    ("AUTHORITY_QUOTATION", None),          # decided by quote characters
    ("BURDEN_PRESUMPTION", "BURDEN"),
    ("COMPENSATION_HARM", "HARM"),
    ("CONTRACT", "CONTRACT"),
    ("JURISDICTION", "JURISDICTION"),
    ("PROCEDURAL_OPERATION", "PROCEDURAL"),
    ("DISPOSITION", "DISPOSITION"),
    ("FACT_RECITAL", "FACT_RECITAL"),
    ("DOCTRINAL_RULE", "DOCTRINAL"),
    ("AUTHORITY_INTRODUCTION_FRAME", "FRAME"),
]
SUBSTANTIVE = [c for c, m in PRIORITY if m and c not in
               ("DOCTRINAL_RULE", "AUTHORITY_INTRODUCTION_FRAME")]


def classify(r):
    mk = set(r["mk"])
    if r["qm"] or r["qn"]:
        return "AUTHORITY_QUOTATION"
    hits = [c for c, m in PRIORITY if m and m in mk]
    if not hits:
        return "GENERIC_REASONING"
    subs = [c for c in hits if c in SUBSTANTIVE]
    if len(subs) >= 3:
        return "AMBIGUOUS"
    return hits[0]


def taxonomy(rows):
    raw = Counter(classify(r) for r in rows)
    mk_of = {c: m for c, m in PRIORITY if m}
    # separability: of the mentions assigned to A, how many also carry B's
    # marker? Two classes that co-fire in both directions are not being
    # separated by these markers and are merged.
    groups = defaultdict(list)
    for r in rows:
        groups[classify(r)].append(r)
    names = sorted(c for c in groups if c in mk_of)
    co = {}
    for a in names:
        for b in names:
            if a == b:
                continue
            g = groups[a]
            co[f"{a}|{b}"] = round(
                sum(1 for r in g if mk_of[b] in r["mk"]) / len(g), 4) if g else None
    parent = {c: c for c in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    merges = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ab, ba = co.get(f"{a}|{b}"), co.get(f"{b}|{a}")
            if ab is not None and ba is not None and ab >= 0.7 and ba >= 0.7:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)
                    merges.append([a, b, ab, ba])
    merged_name = {c: find(c) for c in names}
    final = Counter()
    for r in rows:
        c = classify(r)
        final[merged_name.get(c, c)] += 1
    return {
        "priorityOrder": [c for c, _ in PRIORITY] + ["GENERIC_REASONING",
                                                     "AMBIGUOUS"],
        "assignedBeforeMerging": dict(sorted(raw.items())),
        "markerCoFiring": {k: v for k, v in sorted(co.items())},
        "mergesPerformed": merges,
        "mergeRule": "two classes merge when at least 70 per cent of each "
                     "one's mentions also carry the other's marker. A "
                     "taxonomy that cannot separate two classes should not "
                     "report them as separate.",
        "classes": dict(sorted(final.items())),
        "ambiguousShare": round(raw.get("AMBIGUOUS", 0) / len(rows), 4),
        "genericShare": round(raw.get("GENERIC_REASONING", 0) / len(rows), 4),
        "markerLists": {k: sorted(v) for k, v in sorted(FM.MARKERS.items())},
        "whatThisIsNot": "keyword presence in a 180-character neighbourhood. "
                         "It is not a reading of the passage and no class "
                         "here is a claim about what the court decided.",
    }, merged_name


def formula_classes(rows, merged_name):
    """One class per circulating formula: the modal class of its mentions."""
    circ = circulating(rows, "tmpl")
    per = defaultdict(Counter)
    for r in rows:
        if r["tmpl"] in circ:
            c = classify(r)
            per[r["tmpl"]][merged_name.get(c, c)] += 1
    out, purity = {}, []
    for t, c in per.items():
        best = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        out[t] = best[0]
        purity.append(best[1] / sum(c.values()))
    purity.sort()
    return out, {
        "circulatingFormulasClassified": len(out),
        "byClass": dict(sorted(Counter(out.values()).items())),
        "modalClassPurity": {
            "median": round(purity[len(purity) // 2], 4) if purity else None,
            "p10": round(purity[len(purity) // 10], 4) if purity else None,
            "shareFullyPure": round(
                sum(1 for x in purity if x == 1.0) / len(purity), 4)
            if purity else None},
        "note": "a fingerprint fixes the window's long words but not its "
                "short ones, so two mentions of one formula can differ in a "
                "marker. Purity reports how often that happens rather than "
                "hiding it.",
    }


# --------------------------------------------------------------- PHASE 7
def quotation_layer(rows, fclass):
    """Is the recurring text the SOURCE's words, or the court's own?"""
    def bucket(r):
        if r["qn"]:
            return "SOURCE_QUOTATION_OPENED"
        if r["qm"]:
            return "QUOTATION_IN_NEIGHBOURHOOD"
        if "FRAME" in r["mk"]:
            return "INTRODUCTORY_FRAME"
        return "JUDICIAL_WORDING"
    circ = circulating(rows, "tmpl")
    allb = Counter(bucket(r) for r in rows)
    cirb = Counter(bucket(r) for r in rows if r["tmpl"] in circ)
    per = defaultdict(Counter)
    for r in rows:
        if r["tmpl"] in circ:
            per[r["tmpl"]][bucket(r)] += 1
    mixed = sum(1 for c in per.values() if len(c) > 1)
    return {
        "allMentions": dict(sorted(allb.items())),
        "mentionsInCirculatingFormulas": dict(sorted(cirb.items())),
        "circulatingFormulasWithMixedStatus": mixed,
        "circulatingFormulasWithMixedStatusShare": round(
            mixed / len(per), 4) if per else None,
        "byFormulaClass": {c: dict(sorted(Counter(
            bucket(r) for r in rows
            if fclass.get(r["tmpl"]) == c).items()))
            for c in sorted(set(fclass.values()))},
        "limitation": "quotation is detected from quotation characters and a "
                      "frame keyword, not from comparing the passage to a "
                      "source text. An unmarked quotation reads as judicial "
                      "wording here and there is no way to find it without "
                      "the sources, which this repository does not hold.",
    }


# --------------------------------------------------------------- PHASE 8
def coupling(rows):
    """Four archetypes for the source-to-formula relation."""
    circ = circulating(rows, "tmpl")
    f2s, s2f = defaultdict(set), defaultdict(set)
    for r in rows:
        if r["tmpl"] not in circ:
            continue
        f2s[r["tmpl"]].add(r["cid"])
        s2f[r["cid"]].add(r["tmpl"])
    arche = Counter()
    for t, ss in f2s.items():
        many_s = len(ss) > 1
        many_f = any(len(s2f[s]) > 1 for s in ss)
        arche["ONE_FORMULA_MANY_SOURCES" if many_s and not many_f else
              "MANY_FORMULAS_ONE_SOURCE" if many_f and not many_s else
              "MANY_TO_MANY" if many_s and many_f else
              "ONE_TO_ONE"] += 1
    fps = sorted((len(v) for v in s2f.values()))
    return {
        "circulatingFormulas": len(f2s),
        "sourcesCarryingACirculatingFormula": len(s2f),
        "archetypes": dict(sorted(arche.items())),
        "formulasPerSource": {
            "median": fps[len(fps) // 2] if fps else None,
            "max": fps[-1] if fps else None},
        "sourcesPerFormula": {
            "median": sorted(len(v) for v in f2s.values())[len(f2s) // 2]
                      if f2s else None,
            "max": max((len(v) for v in f2s.values()), default=None)},
        "topSourcesByFormulaCount": [
            {"source": s, "formulas": len(v)}
            for s, v in sorted(s2f.items(),
                               key=lambda kv: (-len(kv[1]), kv[0]))[:10]],
        "reading": "ONE_TO_ONE is a source with one recurring passage. "
                   "MANY_FORMULAS_ONE_SOURCE is a source the courts phrase "
                   "several settled ways. ONE_FORMULA_MANY_SOURCES is a "
                   "shell. The mix decides whether removing formulas removes "
                   "wording or removes sources.",
    }


# --------------------------------------------------------------- PHASE 9
def class_ablation(crows, fclass, scorable):
    """THE FALSIFICATION. Delete ONE CLASS of formula at a time.

    The frozen control deleted every circulating fingerprint at once and the
    matched doctrinal verdict flipped. That is compatible with two stories:
    the removed wording was empty, or the removed wording carried the legal
    propositions. Deleting classes separately distinguishes them. If the flip
    follows the procedural class, the frozen control removed noise. If it
    follows the doctrinal class, the control removed the signal it was meant
    to protect, and the flip is an artefact of the criterion.

    Nothing here is causal. Removing a set of mentions and re-computing is an
    ablation of the measurement, not an intervention on courts.
    """
    def run(boiler):
        u = D.survival(D.typology(D.units(crows, "CODE", scorable, boiler)),
                       scorable)
        m = D.matched(u)
        bt = D.by_type(u)
        elig = [d for d in u.values() if d["eligible"]]
        keep = ("n", "survive1q", "survive2q", "survive4q", "persistentShare")
        return {"mentionsRemoved": (sum(1 for r in crows if r["tmpl"] in boiler)
                                    if boiler else 0),
                "eligibleUnits": len(elig),
                "survival": {t: {k: bt[t][k] for k in keep}
                             for t in ("COURT_FIRST", "BAR_FIRST") if t in bt},
                "matchedPairs": m["matchedPairs"],
                "matchedVerdict": m["verdict"]}

    circ = set(fclass)
    out = {"NONE_REMOVED": run(None),
           "ALL_CIRCULATING_REMOVED": run(circ)}
    for c in sorted(set(fclass.values())):
        s = {t for t, k in fclass.items() if k == c}
        out[f"ONLY_{c}_REMOVED"] = run(s)
        out[f"ALL_EXCEPT_{c}_REMOVED"] = run(circ - s)
    flips = sorted(k for k, v in out.items()
                   if k.startswith("ONLY_")
                   and v["matchedVerdict"] == "BAR_FIRST_NOT_WORSE_AFTER_MATCHING")
    base = out["NONE_REMOVED"]["matchedVerdict"]
    return {
        "baselineVerdict": base,
        "allRemovedVerdict": out["ALL_CIRCULATING_REMOVED"]["matchedVerdict"],
        "singleClassRemovalsThatReproduceTheFlip": flips,
        "arms": out,
        "interpretationRule": "written before the numbers were read. If the "
                              "flip reproduces when only PROCEDURAL_OPERATION "
                              "or AUTHORITY_QUOTATION wording is removed, the "
                              "frozen control removed boilerplate. If it "
                              "reproduces only when DOCTRINAL_RULE wording is "
                              "removed, the control removed legal "
                              "propositions and the flip is an artefact of "
                              "the removal criterion. If it reproduces for "
                              "every class, the flip is about VOLUME rather "
                              "than about wording, and the criterion is not "
                              "identifying anything.",
        "whyNotJustDeleteEverything": "deleting all repetitive wording in the "
                                      "name of de-boilerplating can delete a "
                                      "real signal. That is the risk this "
                                      "phase exists to measure.",
    }


def volume_control(crows, fclass, scorable, draws=20):
    """Is the flip about WORDING, or about how much data leaves?

    PHASE 9 removed one class at a time and nothing flipped; the arms that
    flip are the ones that remove a lot. That is a competing explanation with
    a direct test: remove a RANDOM set of circulating formulas of the same
    size and see how often the verdict flips anyway. If random removal flips
    as readily as class removal, the de-boilerplating criterion is not
    identifying a kind of wording -- it is identifying a quantity of data, and
    the verdict rests on how many matched pairs survive.

    Seeded and reported; the seed is fixed so the arm is reproducible.
    """
    import random
    circ = sorted(fclass)
    size = Counter()
    for r in crows:
        if r["tmpl"] in circ:
            size[r["tmpl"]] += 1
    total = sum(size.values())
    out = {}
    for frac in (0.25, 0.5, 0.75, 0.9):
        target, flips, pairs, removed = total * frac, 0, [], []
        for s in range(draws):
            rng = random.Random(20260831 + s)
            order = circ[:]
            rng.shuffle(order)
            take, acc = set(), 0
            for t in order:
                if acc >= target:
                    break
                take.add(t)
                acc += size[t]
            u = D.survival(D.typology(D.units(crows, "CODE", scorable, take)),
                           scorable)
            m = D.matched(u)
            pairs.append(m["matchedPairs"])
            removed.append(acc)
            flips += int(m["verdict"] == "BAR_FIRST_NOT_WORSE_AFTER_MATCHING")
        out[f"remove{int(frac * 100)}pct"] = {
            "draws": draws,
            "meanMentionsRemoved": round(sum(removed) / draws, 1),
            "flipShare": round(flips / draws, 4),
            "matchedPairs": {"min": min(pairs), "max": max(pairs),
                             "median": sorted(pairs)[draws // 2]},
        }
    return {
        "seed": 20260831,
        "circulatingFormulas": len(circ),
        "mentionsInThem": total,
        "arms": out,
        "question": "does a random removal of the same size flip the verdict "
                    "as often as a targeted one?",
    }


# ------------------------------------------------------------ PHASES 10-11
def formula_first_mover(rows, scorable):
    """Who is first observed using a recurring formula, and does it last?

    The same machinery as the doctrinal first-mover result, with the identity
    swapped from a source to a fingerprint. FIRST OBSERVED, again, means
    exactly that: the earliest quarter this corpus shows the wording. It is
    not the first use in Saudi adjudication and it is never called invention.
    """
    circ = circulating(rows, "tmpl")
    out = {}
    for name, sel, level in (("GLOBAL_ALL_FORMULAS", None, "GLOBAL"),
                             ("GLOBAL_CIRCULATING", circ, "GLOBAL"),
                             ("CODE_LOCAL_CIRCULATING", circ, "CODE"),
                             ("ARTICLE_LOCAL_CIRCULATING", circ, "ARTICLE")):
        fr = [dict(r, cid=r["tmpl"]) for r in rows
              if sel is None or r["tmpl"] in sel]
        u = D.survival(D.typology(D.units(fr, level, scorable)), scorable)
        elig = sum(1 for d in u.values() if d["eligible"])
        out[name] = {"units": len(u), "eligible": elig,
                     "typology": dict(sorted(Counter(
                         d["type"] for d in u.values() if d["eligible"]).items())),
                     "survival": D.by_type(u)}
        if name == "GLOBAL_CIRCULATING":
            out["crossVoiceRecurrence"] = D.crossing(u)
    out["crossVoiceRecurrence"]["note"] = (
        "CROSS-VOICE FORMULA RECURRENCE. A formula first observed in one "
        "voice and later observed in the other is a recurrence of wording "
        "across voices. It is not copying, not influence, and not evidence "
        "that either side read the other.")
    return out


# ------------------------------------------------------------ PHASES 13-15
def formula_travel(rows, fclass, scorable):
    """How far does a formula travel: second city, second code, second article?"""
    idx = {i for i, l in enumerate(LBL) if l in scorable}
    circ = circulating(rows, "tmpl")
    prof = defaultdict(lambda: {"city": {}, "code": {}, "art": {},
                                "q": set(), "j": set(), "voice": {}})
    for r in rows:
        if r["tmpl"] not in circ or r["i"] not in idx:
            continue
        d = prof[r["tmpl"]]
        d["q"].add(r["i"])
        d["j"].add(r["j"])
        for key, val in (("city", r["city"]), ("code", r["instW"]),
                         ("art", (r["instW"], r["artW"]) if r["instW"]
                          and r["artW"] else None),
                         ("voice", r["voice"])):
            if val in (None, ""):
                continue
            d[key].setdefault(val, r["i"])

    def lag(d, key):
        firsts = sorted(d[key].values())
        return firsts[1] - firsts[0] if len(firsts) > 1 else None

    def med(v):
        v = sorted(x for x in v if x is not None)
        return v[len(v) // 2] if v else None

    rowsout = []
    for t, d in sorted(prof.items()):
        rowsout.append({"formula": t, "class": fclass.get(t),
                        "judgments": len(d["j"]),
                        "quartersPresent": len(d["q"]),
                        "cities": len(d["city"]), "codes": len(d["code"]),
                        "articles": len(d["art"]), "voices": len(d["voice"]),
                        "toSecondCity": lag(d, "city"),
                        "toSecondCode": lag(d, "code"),
                        "toSecondArticle": lag(d, "art"),
                        "toSecondVoice": lag(d, "voice")})
    by_class = {}
    for c in sorted({r["class"] for r in rowsout if r["class"]}):
        g = [r for r in rowsout if r["class"] == c]
        by_class[c] = {
            "n": len(g),
            "medianCities": med([r["cities"] for r in g]),
            "medianCodes": med([r["codes"] for r in g]),
            "medianArticles": med([r["articles"] for r in g]),
            "medianQuartersToSecondCity": med([r["toSecondCity"] for r in g]),
            "medianQuartersToSecondCode": med([r["toSecondCode"] for r in g]),
            "reachedBothVoices": sum(1 for r in g if r["voices"] > 1),
            "reachedBothVoicesShare": round(
                sum(1 for r in g if r["voices"] > 1) / len(g), 4)}
    return {
        "formulas": len(rowsout),
        "overall": {
            "medianCities": med([r["cities"] for r in rowsout]),
            "medianCodes": med([r["codes"] for r in rowsout]),
            "medianArticles": med([r["articles"] for r in rowsout]),
            "medianQuartersToSecondCity": med(
                [r["toSecondCity"] for r in rowsout]),
            "medianQuartersToSecondCode": med(
                [r["toSecondCode"] for r in rowsout]),
            "medianQuartersToSecondArticle": med(
                [r["toSecondArticle"] for r in rowsout]),
            "reachedBothVoicesShare": round(
                sum(1 for r in rowsout if r["voices"] > 1) / len(rowsout), 4)
            if rowsout else None},
        "byClass": by_class,
        "note": "counted on SCORABLE quarters only, so a formula whose second "
                "city falls in an immature quarter is not credited with it.",
        "rows": rowsout,
    }


# ------------------------------------------------------------ PHASES 16-19
def variation(rows, fclass, scorable):
    """Does a formula VARY over time, and are new formulas still appearing?

    The word evolution is not used. What is measured is whether the set of
    recurring formulas attached to a source in the later half of the window is
    the same set as in the earlier half.
    """
    idx = sorted(i for i, l in enumerate(LBL) if l in scorable)
    if len(idx) < 4:
        return {"verdict": "INSUFFICIENT_SCORABLE_QUARTERS"}
    cut = idx[len(idx) // 2]
    circ = circulating(rows, "tmpl")
    early, late = defaultdict(set), defaultdict(set)
    for r in rows:
        if r["tmpl"] not in circ or r["i"] not in set(idx):
            continue
        (early if r["i"] < cut else late)[r["cid"]].add(r["tmpl"])
    js = []
    for s in sorted(set(early) & set(late)):
        a, b = early[s], late[s]
        js.append(len(a & b) / len(a | b))
    js.sort()
    # PHASE 19: formula innovation rate on scorable quarters
    firstq, perq = {}, defaultdict(set)
    for r in rows:
        if r["i"] not in set(idx):
            continue
        firstq[r["tmpl"]] = min(firstq.get(r["tmpl"], r["i"]), r["i"])
        perq[r["i"]].add(r["tmpl"])
    innov = []
    for i in idx[1:]:
        seen = perq[i]
        new = {t for t in seen if firstq[t] == i}
        innov.append({"quarter": LBL[i], "formulasPresent": len(seen),
                      "firstObservedHere": len(new),
                      "innovationRate": round(len(new) / len(seen), 4)
                      if seen else None})
    # PHASE 18: does one formula sit beside more than one article over time?
    multi_art, sub_lag = 0, []
    for t in sorted(circ):
        arts = {}
        for r in rows:
            if r["tmpl"] != t or not (r["instW"] and r["artW"]):
                continue
            k = (r["instW"], r["artW"])
            arts[k] = min(arts.get(k, r["i"]), r["i"])
        if len(arts) > 1:
            multi_art += 1
            f = sorted(arts.values())
            sub_lag.append(f[1] - f[0])
    sub_lag.sort()
    return {
        "sourceFormulaSetStability": {
            "sourcesInBothHalves": len(js),
            "medianJaccardEarlyVersusLate": round(js[len(js) // 2], 4) if js else None,
            "sourcesWithIdenticalFormulaSets": sum(1 for x in js if x == 1.0),
            "cutQuarter": LBL[cut],
            "reading": "a Jaccard near 1 means the courts keep phrasing a "
                       "source the same way; near 0 means the recurring "
                       "wording around it has changed. Neither is called "
                       "evolution and no direction is attributed to anyone."},
        "innovationByQuarter": innov,
        "meanInnovationRate": round(
            sum(r["innovationRate"] for r in innov if r["innovationRate"]
                is not None) / len(innov), 4) if innov else None,
        "innovationCaveat": "the first scorable quarter is dropped because "
                            "every formula is new in it by construction, and "
                            "the remaining rates are still left-truncated by "
                            "the start of the corpus.",
        "articleSubstitutionInsideFormulas": {
            "circulatingFormulasBesideMoreThanOneArticle": multi_art,
            "medianQuartersToSecondArticle": (
                sub_lag[len(sub_lag) // 2] if sub_lag else None)},
    }


def source_substitution(rows):
    """PHASE 17. Does one shell receive a DIFFERENT source later on?"""
    circ_m = circulating(rows, "tmplS")
    per = defaultdict(dict)
    for r in rows:
        if r["tmplS"] not in circ_m:
            continue
        d = per[r["tmplS"]]
        d[r["cid"]] = min(d.get(r["cid"], r["i"]), r["i"])
    multi = {t: d for t, d in per.items() if len(d) > 1}
    lags = sorted(sorted(d.values())[1] - sorted(d.values())[0]
                  for d in multi.values())
    return {
        "circulatingShells": len(per),
        "shellsReceivingMoreThanOneSource": len(multi),
        "medianQuartersToSecondSource": (lags[len(lags) // 2] if lags else None),
        "verdict": ("NO_SOURCE_SUBSTITUTION_OBSERVED" if not multi
                    else "SOURCE_SUBSTITUTION_OBSERVED"),
        "note": "this phase can only report what PHASE 4 found. A shell that "
                "never carries a second source cannot substitute one, and a "
                "count of zero here is a consequence of that, not an "
                "independent finding.",
    }


# ------------------------------------------------------------ PHASES 20-22
def entropy(counter):
    n = sum(counter.values())
    if not n:
        return None
    return round(-sum((c / n) * math.log(c / n, 2) for c in counter.values()), 4)


def rarefy(counter, m):
    """Expected distinct formulas in a sample of m mentions (Hurlbert).

    Deterministic: no subsampling, no seed. Court and bar do not produce the
    same number of mentions, and a raw distinct count would just report that.
    """
    n = sum(counter.values())
    if m > n or n == 0:
        return None
    tot = 0.0
    for c in counter.values():
        # P(a formula with c mentions is missed) = C(n-c, m) / C(n, m)
        miss = 0.0
        for k in range(m):
            if n - c - k <= 0:
                miss = float("-inf")
                break
            miss += math.log(n - c - k) - math.log(n - k)
        tot += 1 - (math.exp(miss) if miss != float("-inf") else 0.0)
    return round(tot, 2)


def concentration(rows, fclass):
    """PHASES 20 and 21. A frozen concentration baseline, split every way."""
    def stats(sel):
        c = Counter(r["tmpl"] for r in sel)
        n = sum(c.values())
        if not n:
            return None
        ranked = sorted(c.values(), reverse=True)
        return {"mentions": n, "distinctFormulas": len(c),
                "top10Share": round(sum(ranked[:10]) / n, 4),
                "top50Share": round(sum(ranked[:50]) / n, 4),
                "herfindahl": round(sum((x / n) ** 2 for x in ranked), 6),
                "entropyBits": entropy(c),
                "singletonShare": round(
                    sum(1 for x in ranked if x == 1) / len(c), 4)}
    court = [r for r in rows if r["voice"] == "court"]
    bar = [r for r in rows if r["voice"] == "party"]
    proc = {"PROCEDURAL_OPERATION", "DISPOSITION", "JURISDICTION",
            "FACT_RECITAL"}
    doct = {"DOCTRINAL_RULE", "BURDEN_PRESUMPTION", "COMPENSATION_HARM",
            "CONTRACT"}
    circ = set(fclass)
    m = min(len(court), len(bar))
    cc = Counter(r["tmpl"] for r in court)
    bc = Counter(r["tmpl"] for r in bar)
    return {
        "ALL": stats(rows),
        "COURT": stats(court),
        "BAR": stats(bar),
        "CIRCULATING_ONLY": stats([r for r in rows if r["tmpl"] in circ]),
        "PROCEDURAL_GROUP": stats(
            [r for r in rows if fclass.get(r["tmpl"]) in proc]),
        "DOCTRINAL_GROUP": stats(
            [r for r in rows if fclass.get(r["tmpl"]) in doct]),
        "courtVersusBarDiversity": {
            "rarefactionSampleSize": m,
            "courtExpectedDistinct": rarefy(cc, m),
            "barExpectedDistinct": rarefy(bc, m),
            "note": "expected distinct formulas in a sample of the same size, "
                    "computed analytically. A raw distinct count would mostly "
                    "report that the bench writes more."},
        "classGrouping": {"PROCEDURAL_GROUP": sorted(proc),
                          "DOCTRINAL_GROUP": sorted(doct),
                          "excluded": sorted(
                              {"AUTHORITY_QUOTATION",
                               "AUTHORITY_INTRODUCTION_FRAME",
                               "GENERIC_REASONING", "AMBIGUOUS"})},
        "frozen": "this table is the baseline a later era is compared "
                  "against. It is computed on the whole window and is not "
                  "re-derived when the window grows.",
    }


def three_layer_mobility(rows, scorable):
    """PHASE 22. Statute, doctrine and formula on one mobility scale."""
    full = _mobility(rows, scorable, None)
    circ = _mobility(rows, scorable, circulating(rows, "tmpl"))
    d = J("diffusion_results.json")["phase21_statuteVsDoctrine"]
    return {
        "formulaLayer": full,
        "formulaLayerCirculatingOnly": circ,
        "articlesAndDoctrineFromFrozenEra": d,
        "whichToRead": "the CIRCULATING-ONLY row is the comparable one. The "
                       "full formula universe is 84 per cent singletons, so "
                       "its rank autocorrelation is dominated by wording that "
                       "appears once and never again -- a real fact about the "
                       "layer, but not a mobility statistic that can sit "
                       "beside a 34-identity doctrinal universe.",
        "comparabilityWarning": "three universes of very different size: "
                                "about 2,000 articles, 34 doctrinal "
                                "identities, and roughly 15,000 formulas of "
                                "which 218 recur. Persistence at a decile "
                                "means something different in each. Only the "
                                "DIRECTION is read, and even that is read "
                                "cautiously.",
    }


def _mobility(rows, scorable, keep):
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    per = defaultdict(Counter)
    for r in rows:
        if r["i"] in set(idx) and (keep is None or r["tmpl"] in keep):
            per[r["i"]][r["tmpl"]] += 1
    steps, auto = [], []
    for a, b in zip(idx, idx[1:]):
        ca, cb = per[a], per[b]
        keys = sorted(set(ca) | set(cb))
        if len(keys) < 10:
            continue
        ra = {k: i for i, k in enumerate(sorted(keys, key=lambda k: (-ca[k], k)))}
        rb = {k: i for i, k in enumerate(sorted(keys, key=lambda k: (-cb[k], k)))}
        n = len(keys)
        mu = (n - 1) / 2
        num = sum((ra[k] - mu) * (rb[k] - mu) for k in keys)
        den = math.sqrt(sum((ra[k] - mu) ** 2 for k in keys)
                        * sum((rb[k] - mu) ** 2 for k in keys))
        auto.append(num / den if den else 0.0)
        top = {k for k in keys if ra[k] < max(1, n // 10)}
        topb = {k for k in keys if rb[k] < max(1, n // 10)}
        bottom = {k for k in keys if ra[k] >= n // 2}
        steps.append({"from": LBL[a], "to": LBL[b], "universe": n,
                      "topDecilePersistence": round(
                          len(top & topb) / len(top), 4) if top else None,
                      "bottomHalfToTopDecile": round(
                          len(bottom & topb) / len(bottom), 4) if bottom else None})
    return {
        "steps": len(steps),
        "rankAutocorrelation": round(sum(auto) / len(auto), 4) if auto else None,
        "topDecilePersistence": round(
            sum(s["topDecilePersistence"] for s in steps
                if s["topDecilePersistence"] is not None) / len(steps), 4)
        if steps else None,
        "bottomHalfToTopDecileMobility": round(
            sum(s["bottomHalfToTopDecile"] for s in steps
                if s["bottomHalfToTopDecile"] is not None) / len(steps), 4)
        if steps else None,
        "universeSize": len({r["tmpl"] for r in rows
                             if keep is None or r["tmpl"] in keep}),
        "perStep": steps}


# --------------------------------------------------------------- PHASE 24
def code_formula_dependence(rows, fclass):
    """How much of each code's non-statutory environment is recurring wording?"""
    circ = set(fclass)
    per = defaultdict(lambda: {"n": 0, "circ": 0, "cid": set(),
                               "cidFree": set(), "tmpl": set()})
    for r in rows:
        if not r["instW"]:
            continue
        d = per[r["instW"]]
        d["n"] += 1
        d["cid"].add(r["cid"])
        d["tmpl"].add(r["tmpl"])
        if r["tmpl"] in circ:
            d["circ"] += 1
        else:
            d["cidFree"].add(r["cid"])
    out = {}
    for code, d in sorted(per.items(), key=lambda kv: (-kv[1]["n"], kv[0])):
        if d["n"] < 50:
            continue
        # a source survives de-boilerplating beside this code only if at
        # least one of its mentions there is NOT in a circulating formula
        survivors = len(d["cidFree"])
        out[code] = {
            "mentions": d["n"],
            "inCirculatingFormula": d["circ"],
            "formulaDependence": round(d["circ"] / d["n"], 4),
            "distinctSources": len(d["cid"]),
            "distinctFormulas": len(d["tmpl"]),
            "sourcesLostIfCirculatingRemoved": len(d["cid"]) - survivors,
        }
    vals = [v["formulaDependence"] for v in out.values()]
    return {
        "byCode": out,
        "spread": {"min": min(vals) if vals else None,
                   "max": max(vals) if vals else None,
                   "codesReported": len(out)},
        "reading": "a code whose non-statutory environment is mostly "
                   "recurring wording is a code where the de-boilerplating "
                   "control removes most of the evidence. That is a property "
                   "of the measurement, not of the code.",
        "minimumMentions": 50,
    }


# --------------------------------------------------------------- PHASE 25
def companion_reinterpretation(rows, fclass):
    """What is a doctrinal companion, now that formulas are visible?"""
    circ = set(fclass)
    per = defaultdict(lambda: {"n": 0, "circ": 0, "tmpl": Counter(),
                               "art": Counter(), "quote": 0, "j": set()})
    for r in rows:
        if not r["instW"]:
            continue
        d = per[(r["instW"], r["cid"])]
        d["n"] += 1
        d["j"].add(r["j"])
        d["tmpl"][r["tmpl"]] += 1
        if r["artW"]:
            d["art"][r["artW"]] += 1
        if r["tmpl"] in circ:
            d["circ"] += 1
        if r["qn"] or r["qm"]:
            d["quote"] += 1
    cls = Counter()
    rowsout = []
    for k, d in sorted(per.items()):
        if d["n"] < 5:
            continue
        fshare = d["circ"] / d["n"]
        qshare = d["quote"] / d["n"]
        topf = max(d["tmpl"].values()) / d["n"]
        artc = (max(d["art"].values()) / sum(d["art"].values())
                if d["art"] else 0.0)
        if fshare >= 0.5 and topf >= 0.3:
            c = "FORMULA_ASSOCIATED_SOURCE_ENVIRONMENT"
        elif qshare >= 0.5:
            c = "SOURCE_QUOTATION_REUSE"
        elif artc >= 0.6 and d["art"]:
            c = "ARTICLE_ASSOCIATED"
        elif fshare < 0.2 and len(d["tmpl"]) / d["n"] >= 0.8:
            c = "GENERIC_FIELD"
        elif fshare < 0.35:
            c = "CODE_ASSOCIATED"
        else:
            c = "MIXED"
        cls[c] += 1
        rowsout.append({"code": k[0], "source": k[1], "mentions": d["n"],
                        "judgments": len(d["j"]),
                        "formulaShare": round(fshare, 4),
                        "quotationShare": round(qshare, 4),
                        "topFormulaShare": round(topf, 4),
                        "class": c})
    rowsout.sort(key=lambda r: (-r["mentions"], r["code"], r["source"]))
    return {
        "companionPairsClassified": len(rowsout),
        "byClass": dict(sorted(cls.items())),
        "thresholds": {"minMentions": 5, "formulaAssociated": "formulaShare "
                       ">= 0.5 and topFormulaShare >= 0.3",
                       "quotationReuse": "quotationShare >= 0.5",
                       "articleAssociated": "top article >= 0.6 of the "
                                            "pair's article-bearing mentions",
                       "genericField": "formulaShare < 0.2 and distinct "
                                       "formulas >= 0.8 of mentions"},
        "reading": "DOCTRINE.md called these doctrinal companions of a code. "
                   "Some of them are: a source the code's disputes genuinely "
                   "reach for. Others are one recurring passage counted many "
                   "times. The classification separates the two without "
                   "asserting that either is legally significant.",
        "top": rowsout[:25],
    }


# --------------------------------------------------------------- PHASE 26
def _fold_verdict(v):
    ok = (v["foldsWithSupport"] >= 4
          and v["foldsAboveOne"] >= max(2, v["foldsWithSupport"] * 0.75))
    if not ok or v["meanLift"] is None:
        return "NO_USABLE_SIGNAL_USE_DETECT_OR_WATCH"
    if v["medianCohortSupport"] < 20:
        return "SIGNAL_ON_FOLDS_LOW_SUPPORT"
    if v["meanLift"] >= 1.5:
        return "USABLE_SIGNAL_ON_FOLDS"
    return "WEAK_BUT_CONSISTENT_ON_FOLDS"


def forecastability(rows, fclass, scorable):
    """Is a formula's persistence predictable from how it first appears?"""
    idx = sorted(i for i, l in enumerate(LBL) if l in scorable)
    sidx = set(idx)
    # EVERY feature is read from the formula's FIRST scorable quarter only.
    # An earlier draft used cities and codes observed over the whole window,
    # which is the same information as the outcome and produced a lift of 22.
    # A feature that can only be known after the fact is not a forecast.
    per = defaultdict(lambda: {"q": set(), "first": None})
    for r in rows:
        if r["i"] not in sidx:
            continue
        d = per[r["tmpl"]]
        d["q"].add(r["i"])
        d["first"] = r["i"] if d["first"] is None else min(d["first"], r["i"])
    at_first = defaultdict(lambda: {"j": set(), "city": set(), "code": set(),
                                    "voice": set()})
    for r in rows:
        if r["i"] not in sidx or r["i"] != per[r["tmpl"]]["first"]:
            continue
        d = at_first[r["tmpl"]]
        d["j"].add(r["j"])
        d["city"].add(r["city"])
        d["voice"].add(r["voice"])
        if r["instW"]:
            d["code"].add(r["instW"])
    units = []
    for t, d in sorted(per.items()):
        later = [i for i in idx if i > d["first"]]
        if len(later) < 2:
            continue
        hits = [i for i in later if i in d["q"]]
        f = at_first[t]
        units.append({
            "formula": t,
            "persistent": len(hits) / len(later) >= 0.5,
            "firstQuarterJudgments": len(f["j"]),
            "courtOrigin": "court" in f["voice"],
            "multiCity": len(f["city"]) > 1,
            "multiCode": len(f["code"]) > 1,
            "class": fclass.get(t, "NOT_CIRCULATING"),
        })
    n = len(units)
    base = round(sum(1 for u in units if u["persistent"]) / n, 4) if n else None
    feats = {}
    for f in ("courtOrigin", "multiCity", "multiCode"):
        g = [u for u in units if u[f]]
        feats[f] = {"n": len(g),
                    "precision": round(
                        sum(1 for u in g if u["persistent"]) / len(g), 4)
                    if g else None}
    g = [u for u in units if u["firstQuarterJudgments"] >= 3]
    feats["firstQuarterJudgmentsAtLeast3"] = {
        "n": len(g), "precision": round(
            sum(1 for u in g if u["persistent"]) / len(g), 4) if g else None}
    # ROLLING-ORIGIN FOLDS. Each fold is one first-observation cohort scored
    # on the quarters after it, so no fold reads an outcome it could not have
    # seen. This is what BET_002 was refused for lacking.
    folds = []
    for i in idx:
        later = [x for x in idx if x > i]
        if len(later) < 2:
            continue
        cohort = [u for u in units if per[u["formula"]]["first"] == i]
        if len(cohort) < 30:
            continue
        b = sum(1 for u in cohort if u["persistent"]) / len(cohort)
        row = {"cohort": LBL[i], "units": len(cohort), "baseRate": round(b, 4)}
        for f in ("courtOrigin", "multiCity", "multiCode"):
            g = [u for u in cohort if u[f]]
            row[f] = {"n": len(g),
                      "precision": round(
                          sum(1 for u in g if u["persistent"]) / len(g), 4)
                      if g else None,
                      "lift": round((sum(1 for u in g if u["persistent"])
                                     / len(g)) / b, 4) if g and b else None}
        folds.append(row)
    fold_summary = {}
    for f in ("courtOrigin", "multiCity", "multiCode"):
        ls = [r[f]["lift"] for r in folds if r[f]["lift"] is not None]
        ns = [r[f]["n"] for r in folds]
        fold_summary[f] = {
            "foldsWithSupport": len(ls),
            "meanLift": round(sum(ls) / len(ls), 4) if ls else None,
            "worstLift": min(ls) if ls else None,
            "foldsAboveOne": sum(1 for x in ls if x > 1),
            "medianCohortSupport": sorted(ns)[len(ns) // 2] if ns else None}

    best = max((v for v in feats.values() if v["precision"] is not None),
               key=lambda v: (v["precision"], v["n"]), default=None)
    bestname = next((k for k, v in sorted(feats.items())
                     if v is best), None)
    lift = round(best["precision"] / base, 4) if best and base else None
    return {
        "units": n, "baseRate": base, "features": feats,
        "bestFeature": bestname, "liftOverBaseRate": lift,
        "rollingOriginFolds": folds,
        "foldSummary": fold_summary,
        "verdicts": {f: _fold_verdict(v) for f, v in
                     sorted(fold_summary.items())},
        "verdict": max((_fold_verdict(v) for v in fold_summary.values()),
                       key=lambda x: ("USABLE_SIGNAL_ON_FOLDS",
                                      "SIGNAL_ON_FOLDS_LOW_SUPPORT",
                                      "WEAK_BUT_CONSISTENT_ON_FOLDS",
                                      "NO_USABLE_SIGNAL_USE_DETECT_OR_WATCH"
                                      ).index(x) * -1),
        "supportGate": "a fold whose feature fires on a handful of formulas "
                       "cannot carry a lift of ten. The gate is a median "
                       "cohort support of 20; multiCity does not pass it and "
                       "is reported as low support rather than as skill.",
        "featuresAreFirstQuarterOnly": True,
        "leakageNote": "features read from the whole window -- cities or "
                       "codes a formula EVER reached -- give a lift above 20 "
                       "and are worthless, because reaching a second code is "
                       "the outcome restated. Only the first scorable quarter "
                       "is used.",
        "temporalFolds": "NONE. Every unit is scored on the whole remaining "
                         "window, so this is a single-sample ranking check "
                         "and not a backtest. It cannot be reported as "
                         "forecasting skill, whatever the lift.",
    }


# --------------------------------------------------------------- PHASE 27
def detector_era(rows, fclass, scorable):
    """FORMULA_DETECTOR_ERA_1: an independent era, Era 1's contract shape.

    Nothing in the doctrinal or article detector eras is touched. This arms
    new metrics on a new layer, with no historical replay to borrow, and says
    so.
    """
    import detectors as DT
    idx = {i for i, l in enumerate(LBL) if l in scorable}
    circ = set(fclass)
    firstq = {}
    for r in rows:
        firstq[r["tmpl"]] = min(firstq.get(r["tmpl"], r["i"]), r["i"])
    metrics = {"formulaShareOfMentions": [], "courtFormulaShare": [],
               "formulaInnovationRate": [], "top10FormulaConcentration": []}
    for i, l in enumerate(LBL):
        sel = [r for r in rows if r["i"] == i]
        if i not in idx or not sel:
            for k in metrics:
                metrics[k].append(None)
            continue
        c = Counter(r["tmpl"] for r in sel)
        ranked = sorted(c.values(), reverse=True)
        court = [r for r in sel if r["voice"] == "court"]
        metrics["formulaShareOfMentions"].append(
            sum(1 for r in sel if r["tmpl"] in circ) / len(sel))
        metrics["courtFormulaShare"].append(
            (sum(1 for r in court if r["tmpl"] in circ) / len(court))
            if court else None)
        metrics["formulaInnovationRate"].append(
            sum(1 for t in c if firstq[t] == i) / len(c))
        metrics["top10FormulaConcentration"].append(
            sum(ranked[:10]) / sum(ranked))
    det = {k: DT.replay(v, scorable, k) for k, v in sorted(metrics.items())}
    return {
        "era": "FORMULA_DETECTOR_ERA_1",
        "contract": {"baseline": "rolling median of prior scorable periods",
                     "spread": "MAD x 1.4826, floored at "
                               "max(1e-4, 0.05 x |baseline|)",
                     "threshold": DT.K_MAD, "confirmation": DT.CONFIRM,
                     "inheritedFrom": "PROSPECTIVE_DETECTOR_ERA_1, unchanged"},
        "metrics": {k: {"currentState": v["currentState"],
                        "periodsEvaluated": v["periodsEvaluated"],
                        "signals": v["signals"],
                        "confirmedShifts": v["confirmedShifts"],
                        "alarmRatePerEvaluablePeriod":
                            v["alarmRatePerEvaluablePeriod"],
                        "baselineLastValue": next(
                            (s.get("baseline") for s in reversed(v["byPeriod"])
                             if s.get("baseline") is not None), None)}
                    for k, v in det.items()},
        "independence": "Era 1 and Era 2 of the earlier detectors are "
                        "untouched: their series, alarm budgets and pending "
                        "scores stand exactly as frozen. This era shares "
                        "their CONTRACT and none of their history, so their "
                        "measured alarm rate does not transfer to it.",
        "replay": det,
    }


# ------------------------------------------------------------ PHASES 32-35
def contamination(rows, fclass, scorable):
    """What a legal AI would learn if it counted passages instead of contexts.

    RAW SUPPORT counts every mention. FORMULA-ADJUSTED SUPPORT counts distinct
    recurring formulas plus every non-recurring mention once, so a passage
    that recurs in 400 judgments contributes what a passage contributes, not
    what 400 independent readings contribute. The gap is the inflation a
    frequency-trained system would absorb.
    """
    circ = set(fclass)

    def adjusted(sel):
        seen, n = set(), 0
        for r in sel:
            if r["tmpl"] in circ:
                if r["tmpl"] in seen:
                    continue
                seen.add(r["tmpl"])
            n += 1
        return n

    raws, adjs = Counter(), {}
    for r in rows:
        raws[r["cid"]] += 1
    for cid in raws:
        adjs[cid] = adjusted([r for r in rows if r["cid"] == cid])
    tbl = []
    for cid in sorted(raws, key=lambda c: (-raws[c], c)):
        tbl.append({"source": cid, "rawSupport": raws[cid],
                    "formulaAdjustedSupport": adjs[cid],
                    "inflation": round(raws[cid] / adjs[cid], 3)
                    if adjs[cid] else None})
    rank_raw = [r["source"] for r in tbl]
    rank_adj = [r["source"] for r in sorted(
        tbl, key=lambda r: (-r["formulaAdjustedSupport"], r["source"]))]
    disp = {s: rank_adj.index(s) - rank_raw.index(s) for s in rank_raw}
    moved = sorted(disp.items(), key=lambda kv: (-abs(kv[1]), kv[0]))
    top10raw, top10adj = set(rank_raw[:10]), set(rank_adj[:10])

    # PHASE 35: does the ageing curve differ raw versus adjusted?
    idx = sorted(i for i, l in enumerate(LBL) if l in scorable)
    series = []
    for i in idx:
        sel = [r for r in rows if r["i"] == i]
        if not sel:
            continue
        series.append({"quarter": LBL[i], "rawMentions": len(sel),
                       "formulaAdjusted": adjusted(sel),
                       "ratio": round(len(sel) / adjusted(sel), 4)
                       if adjusted(sel) else None})
    rs = [s["rawMentions"] for s in series]
    as_ = [s["formulaAdjusted"] for s in series]

    def pearson(a, b):
        n = len(a)
        if n < 3:
            return None
        ma, mb = sum(a) / n, sum(b) / n
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = math.sqrt(sum((x - ma) ** 2 for x in a)
                        * sum((y - mb) ** 2 for y in b))
        return round(num / den, 4) if den else None
    return {
        "phase32_rawVersusAdjustedFrequency": {
            "sources": len(tbl),
            "totalRawMentions": sum(raws.values()),
            "totalAdjusted": sum(adjs.values()),
            "overallInflation": round(sum(raws.values()) / sum(adjs.values()), 3)
            if sum(adjs.values()) else None,
            "maxSourceInflation": max((r["inflation"] for r in tbl
                                       if r["inflation"]), default=None),
            "table": tbl},
        "phase33_effectiveIndependentContexts": {
            "definition": "RAW SUPPORT is mentions. FORMULA-ADJUSTED SUPPORT "
                          "counts each circulating formula once for a source "
                          "and every other mention once. It is a floor on "
                          "independent contexts, not an estimate of them.",
            "note": "this does not claim the recurring passages are copies. "
                    "It claims they are not independent evidence, which is a "
                    "weaker and safer statement."},
        "phase34_retrievalRanking": {
            "rankChangesAtLeastOnePlace": sum(1 for v in disp.values() if v),
            "largestDisplacements": [{"source": s, "places": v}
                                     for s, v in moved[:8]],
            "top10Stability": round(len(top10raw & top10adj) / 10, 4),
            "enteringTop10UnderDeduplication": sorted(top10adj - top10raw),
            "leavingTop10UnderDeduplication": sorted(top10raw - top10adj)},
        "phase35_temporalAgeing": {
            "series": series,
            "correlationRawVersusAdjusted": pearson(rs, as_),
            "inflationTrend": {"first": series[0]["ratio"] if series else None,
                               "last": series[-1]["ratio"] if series else None},
            "reading": "if the two series move together, formula "
                       "de-duplication changes the LEVEL of apparent support "
                       "and not its shape over time."},
    }


# --------------------------------------------------------------- PHASE 36
def vintages(rows, fclass, scorable):
    """Formula cohorts by the quarter they are first observed."""
    idx = sorted(i for i, l in enumerate(LBL) if l in scorable)
    sidx = set(idx)
    firstq, present = {}, defaultdict(set)
    for r in rows:
        if r["i"] not in sidx:
            continue
        firstq[r["tmpl"]] = min(firstq.get(r["tmpl"], r["i"]), r["i"])
        present[r["tmpl"]].add(r["i"])
    circ = set(fclass)
    out = []
    for i in idx:
        cohort = [t for t, f in firstq.items() if f == i]
        if not cohort:
            continue
        later = [x for x in idx if x > i]
        surv = [t for t in cohort if any(x in present[t] for x in later[:4])]
        out.append({
            "vintage": LBL[i], "formulas": len(cohort),
            "circulating": sum(1 for t in cohort if t in circ),
            "laterMatureQuarters": len(later),
            "survivedWithin4Quarters": (round(len(surv) / len(cohort), 4)
                                        if later else None),
            "rightCensored": len(later) < 2})
    return {"cohorts": out,
            "note": "the last cohorts are right-censored by construction and "
                    "are marked rather than dropped, so nobody reads the "
                    "final vintage as a collapse in formula survival."}


# ------------------------------------------------------------ PHASES 28-31
def bar_origin_import(rows, scorable):
    """PHASE 31 baseline. Formulas first observed in the bar's voice, later
    observed in the court's."""
    idx = {i for i, l in enumerate(LBL) if l in scorable}
    circ = circulating(rows, "tmpl")
    fv = defaultdict(dict)
    for r in rows:
        if r["tmpl"] not in circ or r["i"] not in idx:
            continue
        d = fv[r["tmpl"]]
        d[r["voice"]] = min(d.get(r["voice"], r["i"]), r["i"])
    bar_first = [t for t, d in fv.items()
                 if "party" in d and ("court" not in d or d["party"] < d["court"])]
    imported = [t for t in bar_first if "court" in fv[t]]
    court_ments = [r for r in rows if r["voice"] == "court" and r["i"] in idx]
    share = (sum(1 for r in court_ments if r["tmpl"] in set(bar_first))
             / len(court_ments)) if court_ments else None
    lags = sorted(fv[t]["court"] - fv[t]["party"] for t in imported)
    return {
        "circulatingFormulasFirstObservedInBarVoice": len(bar_first),
        "ofWhichLaterObservedInCourtVoice": len(imported),
        "shareOfCourtMentionsInSuchFormulas": round(share, 6)
        if share is not None else None,
        "medianQuartersToCourtVoice": lags[len(lags) // 2] if lags else None,
        "reading": "a small number by construction: only 5.5 per cent of "
                   "circulating formulas appear in both voices at all. This "
                   "is the baseline an advocacy-side drafting tool would have "
                   "to move.",
        "notInfluence": "a formula observed in the bar's voice and later in "
                        "the court's is an ordering of observations. It is "
                        "not evidence that the court took it from the bar.",
    }


def ai_hypotheses(conc, trav, var, imp, det):
    """PHASES 28-31, frozen with scoring rules and competing hypotheses.

    Every one of these is about the FUTURE and none of them is a claim about
    the past. No AI deployment is attributed to any observed change in this
    corpus, and no observed change is offered as evidence that any tool
    exists.
    """
    ent = conc["ALL"]["entropyBits"]
    hhi = conc["ALL"]["herfindahl"]
    top10 = conc["ALL"]["top10Share"]
    innov = var.get("meanInnovationRate")
    return {
        "phase28_homogenisation": {
            "hypothesis": "H_FORMULA_HOMOGENISATION. If drafting assistance "
                          "is adopted in adjudication, recurring formulas "
                          "concentrate: entropy falls, top-10 share rises, "
                          "innovation rate falls.",
            "competing": [
                {"name": "H_FORMULA_VARIATION",
                 "claim": "a generative tool produces MORE distinct "
                          "phrasings, not fewer: entropy rises and the "
                          "innovation rate rises."},
                {"name": "H_FORMULA_DISCOVERY",
                 "claim": "the formula layer is untouched and what moves is "
                          "which sources appear, not how they are phrased."},
                {"name": "H_NO_CHANGE",
                 "claim": "nothing moves outside the detector's alarm "
                          "budget. This is the default and it wins by "
                          "default."}],
            "frozenBaselines": {"entropyBits": ent, "herfindahl": hhi,
                                "top10Share": top10,
                                "meanInnovationRate": innov},
            "scoredBy": "FORMULA_DETECTOR_ERA_1 on "
                        "top10FormulaConcentration and "
                        "formulaInnovationRate. A confirmed shift in the "
                        "stated direction scores the hypothesis; a confirmed "
                        "shift in the other direction scores the competitor; "
                        "no confirmed shift scores H_NO_CHANGE.",
            "cannotBeAttributed": "a confirmed shift would be a change in the "
                                  "corpus. Attributing it to AI would need an "
                                  "adoption event at L3_WORKFLOW_MATCH, and "
                                  "the registry holds none.",
        },
        "phase29_sourceShellStandardisation": {
            "hypothesis": "H_SHELL_STANDARDISATION. AI changes HOW authority "
                          "is introduced before it changes WHICH authority is "
                          "used: the introduction-frame and quotation classes "
                          "move before the source distribution does.",
            "frozenBaselines": {
                "introductionFrameShareOfMentions": None,
                "quotationOpenedShareOfMentions": None},
            "whyThisOrderIsPlausibleAndUntested": "at the current exact-"
                                                  "fingerprint resolution no "
                                                  "circulating formula "
                                                  "carries a second canonical "
                                                  "authority identity, so "
                                                  "shell and source cannot be "
                                                  "told apart here and this "
                                                  "hypothesis may not be "
                                                  "separable from PHASE 28. "
                                                  "Recorded now rather than "
                                                  "discovered later.",
            "scoredBy": "the same detector era, on the quotation and frame "
                        "shares, once they have four scorable quarters of "
                        "history.",
        },
        "phase30_judicialResearchReinforcement": {
            "hypothesis": "H_REINFORCEMENT. A retrieval tool trained on this "
                          "record would surface the sources the record "
                          "already favours, so concentration in the SOURCE "
                          "layer rises rather than falls.",
            "frozenBaselines": {
                "doctrinalRankAutocorrelation": 0.8954,
                "doctrinalTopQuartilePersistence": 0.937,
                "doctrinalBottomHalfMobility": 0.0,
                "formulaRankAutocorrelation": None},
            "note": "the doctrinal layer is already at 0.937 persistence with "
                    "zero upward mobility, so this hypothesis proposes to "
                    "concentrate something with very little room left. That "
                    "is a reason to doubt it, and it is stated as such.",
        },
        "phase31_advocacyFormulaImport": {
            "hypothesis": "H_ADVOCACY_IMPORT. A bar-side drafting tool "
                          "increases the share of court-voice mentions "
                          "sitting in formulas first observed in the bar's "
                          "voice.",
            "frozenBaseline": imp,
            "scoredBy": "a detector armed on that share once it has four "
                        "scorable quarters. It is NOT armed now: the base "
                        "rate is small enough that the dispersion floor would "
                        "dominate, which is exactly the failure the positive "
                        "control exposed in the first detector era.",
        },
        "standingRule": "no retrospective AI attribution. Nothing measured "
                        "before an adoption event is evidence about that "
                        "event, and nothing in this file is offered as such.",
    }


# --------------------------------------------------------------- PHASE 38
def flow_map(rows, fclass):
    """ARTICLE, SOURCE and FORMULA as three layers, with counted relations.

    Edges are CO-OCCURRENCE COUNTS. There are no arrows, no directions and no
    causal edges, and the forbidden list is part of the artefact.
    """
    circ = set(fclass)
    af, sf, as_ = set(), set(), set()
    for r in rows:
        if r["tmpl"] in circ:
            sf.add((r["cid"], r["tmpl"]))
            if r["instW"] and r["artW"]:
                af.add(((r["instW"], r["artW"]), r["tmpl"]))
        if r["instW"] and r["artW"]:
            as_.add(((r["instW"], r["artW"]), r["cid"]))
    return {
        "layers": {"ARTICLE": len({k for k, _ in as_}),
                   "SOURCE": len({r["cid"] for r in rows}),
                   "FORMULA": len({r["tmpl"] for r in rows}),
                   "CIRCULATING_FORMULA": len(circ)},
        "relations": {"ARTICLE_SOURCE": len(as_),
                      "ARTICLE_FORMULA": len(af),
                      "SOURCE_FORMULA": len(sf)},
        "observedTransitions": "counted co-occurrences within one judgment "
                               "and within a +-500 character locality window. "
                               "Nothing here is a path, a flow, or a route.",
        "forbidden": ["caused", "influenced", "copied", "spread to",
                      "adopted from", "propagated", "diffused into"],
        "note": "the word FLOW in this function's name describes the picture "
                "a reader draws, not a mechanism this repository measured.",
    }


# --------------------------------------------------------------- PHASE 37
def asset(rows, fclass, trav):
    """A redistributable formula-diffusion asset: hashes and features only.

    No judgment text and no formula text. A row is a fingerprint, its
    mechanical class, and the shape of its appearance. Anyone can join it to
    their own corpus by recomputing the fingerprint from formula.py; nobody
    can recover a passage from it.
    """
    circ = set(fclass)
    per = defaultdict(lambda: {"j": set(), "q": set(), "city": set(),
                               "code": set(), "voice": set(), "cid": set()})
    for r in rows:
        if r["tmpl"] not in circ:
            continue
        d = per[r["tmpl"]]
        d["j"].add(r["j"])
        d["q"].add(r["i"])
        d["city"].add(r["city"])
        d["voice"].add(r["voice"])
        d["cid"].add(r["cid"])
        if r["instW"]:
            d["code"].add(r["instW"])
    lag = {r["formula"]: r for r in trav["rows"]}
    out = []
    for t, d in sorted(per.items(), key=lambda kv: (-len(kv[1]["j"]), kv[0])):
        qs = sorted(d["q"])
        out.append({
            "fingerprint": t, "class": fclass[t],
            "judgments": len(d["j"]),
            "firstQuarterObserved": LBL[qs[0]] if qs else None,
            "lastQuarterObserved": LBL[qs[-1]] if qs else None,
            "quartersPresent": len(qs),
            "cities": len(d["city"]), "codes": len(d["code"]),
            "sources": sorted(d["cid"]),
            "voices": sorted(d["voice"]),
            "quartersToSecondCity": lag.get(t, {}).get("toSecondCity"),
            "quartersToSecondCode": lag.get(t, {}).get("toSecondCode")})
    return {
        "what": "RECURRING LEGAL FORMULA DIFFUSION ASSET. One row per formula "
                "recurring in ten or more judgments in the observed window.",
        "unit": "SHA-1[:12] of a normalised +-90 character window; see "
                "formula.py and PHASE 2 of formula_analysis_results.json for "
                "the exact construction.",
        "noText": "no judgment text, no formula text, no reconstructible "
                  "content. The fingerprint is one-way and the asset carries "
                  "counts.",
        "notCopying": "a shared fingerprint is shared wording. It is not "
                      "evidence that one judgment was written from another.",
        "identityUniverse": "sources are bounded by the extractor's "
                            "vocabulary of 28 canonical identities; every "
                            "count is a floor.",
        "rows": out,
    }


# ------------------------------------------------------------ PHASES 39-41
def decisions(abl, vol, p4, p8, fam, fore):
    """Watches, the bet, and whether any of this is a paper."""
    flip_random = vol["arms"]["remove90pct"]["flipShare"]
    single = abl["singleClassRemovalsThatReproduceTheFlip"]
    verdict = ("FLIP_TRACKS_REMOVAL_VOLUME_NOT_WORDING_CLASS"
               if not single and flip_random and flip_random >= 0.5
               else "FLIP_TRACKS_A_WORDING_CLASS" if single
               else "INCONCLUSIVE")
    bet = {
        "id": "REPOSITORY_BET_003",
        "candidate": "that the class of recurring wording, rather than the "
                     "quantity removed, decides the de-boilerplated "
                     "doctrinal verdict.",
        "decision": "REFUSED",
        "why": ["no single formula class reproduces the flip",
                "a random removal of the same size flips the verdict in "
                f"{flip_random} of draws",
                "every arm's matched comparison rests on 6 or 7 pairs",
                "the candidate is a claim about WORDING CLASS, and the "
                "measurement cannot distinguish class from quantity at this "
                "corpus size"],
        "whatWouldEarnIt": "a matched comparison with at least 30 pairs, "
                           "which needs more corpus, not more analysis.",
        "keptBecauseRefused": "the refusal is the record. A later session "
                              "that finds this attractive should read this "
                              "entry before placing it.",
    }
    near_miss = {
        "id": "NEAR_MISS_FORMULA_PERSISTENCE",
        "what": "the closest thing to a forecastable signal this programme "
                "has produced: a formula observed in more than one CITY in "
                "its first scorable quarter persists at "
                f"{fore['features']['multiCity']['precision']} against a base "
                f"rate of {fore['baseRate']}, mean fold lift "
                f"{fore['foldSummary']['multiCity']['meanLift']} over "
                f"{fore['foldSummary']['multiCity']['foldsWithSupport']} "
                "rolling-origin folds.",
        "whyNotABet": "median cohort support is "
                      f"{fore['foldSummary']['multiCity']['medianCohortSupport']}"
                      " formulas per fold and one fold is zero. Court origin "
                      "is the consistent one -- 8 folds of 8 above a lift of "
                      "one -- and its mean lift is "
                      f"{fore['foldSummary']['courtOrigin']['meanLift']}, "
                      "which is too small to bet on.",
        "status": "recorded, not issued",
    }
    watches = [
        {"id": "WATCH_FORMULA_SHELL",
         "target": "the first circulating formula observed carrying a SECOND "
                   "canonical source",
         "baseline": p4["shellsWithMoreThanOneSource"],
         "why": "PHASE 4 found zero. A single one would be the first "
                "observation of a judicial shell that is genuinely "
                "source-independent, and it changes what the "
                "de-boilerplating control removes.",
         "probability": "none, by design"},
        {"id": "WATCH_FORMULA_FAMILY_STABILITY",
         "target": "near-exact formula grouping becoming stable across "
                   "thresholds 0.6 to 0.8",
         "baseline": fam["stability"]["shareSurvivingAt80"],
         "why": "the family layer was built and set aside. More data may "
                "make it stable, and if it does, every exact-only count here "
                "is a floor.",
         "probability": "none, by design"},
        {"id": "WATCH_ONE_TO_ONE_COUPLING",
         "target": "ONE_FORMULA_MANY_SOURCES appearing at all in the "
                   "coupling archetypes",
         "baseline": p8["archetypes"].get("ONE_FORMULA_MANY_SOURCES", 0),
         "why": "the same question as the first watch, counted at the "
                "coupling level rather than the shell level, so a change "
                "shows up in whichever is measured first.",
         "probability": "none, by design"},
    ]
    return {
        "phase23_causalLanguage": {
            "rule": "no causal language anywhere in this programme",
            "bannedFormulations": [
                "templates caused the effect",
                "the formula spread from X to Y",
                "the court copied the formula",
                "AI standardised judicial wording"],
            "permittedFormulations": [
                "the fingerprint recurs in N judgments",
                "it is first observed in quarter Q in voice V",
                "removing it changes the measured verdict"],
        },
        "phase39_watches": watches,
        "phase40_bet": bet,
        "phase40_nearMiss": near_miss,
        "phase41_paper": {
            "criteria": {
                "A_newMeasuredObject": True,
                "B_negativeResultThatCorrectsAPublishedClaim": False,
                "C_methodOthersCanReuse": True,
                "D_resultSurvivesItsOwnControls": bool(
                    verdict != "INCONCLUSIVE")},
            "decision": "ASSET_ONLY_FOR_NOW",
            "why": "the programme's strongest output is a NEGATIVE "
                   "methodological result -- a de-boilerplating control that "
                   "does not identify boilerplate -- resting on a matched "
                   "comparison of six or seven pairs. That is worth "
                   "publishing as a method note only if the pair count grows. "
                   "Criterion B fails because nothing here corrects a "
                   "published claim; the claim it corrects is this "
                   "repository's own, and correcting yourself in your own "
                   "repository is not a paper.",
            "whatWouldChangeIt": "30 or more matched pairs, or a second "
                                 "corpus in which the same fingerprint "
                                 "construction reproduces the class "
                                 "taxonomy.",
        },
        "phase42_assetGoal": {
            "goal": "the durable artefact is not this analysis. It is "
                    "formula.py plus the fingerprint asset: a reproducible, "
                    "text-free unit of recurring legal wording that another "
                    "corpus can recompute and join.",
            "whatItEnables": ["de-duplicating a training or retrieval corpus "
                              "by legal formula rather than by document",
                             "measuring how much of an apparent doctrinal "
                              "trend is one passage counted many times",
                             "a class taxonomy that needs no model and no "
                              "human labelling"],
            "whatItDoesNotEnable": ["recovering any judgment text",
                                    "identifying a court, a judge or a party",
                                    "any claim that one judgment was written "
                                    "from another"],
        },
        "headlineVerdict": verdict,
    }


def main():
    rows, schema = load()
    crows = D.load_rows()
    hz = J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])

    tax, merged = taxonomy(rows)
    fclass, fclass_report = formula_classes(rows, merged)
    fam = families(rows)
    p4 = source_masking(rows)
    p5 = article_code_masking(rows)
    p7 = quotation_layer(rows, fclass)
    p8 = coupling(rows)
    abl = class_ablation(crows, fclass, scorable)
    vol = volume_control(crows, fclass, scorable)
    fm = formula_first_mover(rows, scorable)
    trav = formula_travel(rows, fclass, scorable)
    var = variation(rows, fclass, scorable)
    sub = source_substitution(rows)
    conc = concentration(rows, fclass)
    mob = three_layer_mobility(rows, scorable)
    dep = code_formula_dependence(rows, fclass)
    comp = companion_reinterpretation(rows, fclass)
    fore = forecastability(rows, fclass, scorable)
    det = detector_era(rows, fclass, scorable)
    cont = contamination(rows, fclass, scorable)
    vin = vintages(rows, fclass, scorable)
    imp = bar_origin_import(rows, scorable)
    hyp = ai_hypotheses(conc, trav, var, imp, det)
    dec = decisions(abl, vol, p4, p8, fam, fore)

    # fill the two baselines the hypotheses could not know before measurement
    q = p7["allMentions"]
    n = sum(q.values())
    hyp["phase29_sourceShellStandardisation"]["frozenBaselines"] = {
        "introductionFrameShareOfMentions": round(
            q.get("INTRODUCTORY_FRAME", 0) / n, 4),
        "quotationOpenedShareOfMentions": round(
            q.get("SOURCE_QUOTATION_OPENED", 0) / n, 4)}
    hyp["phase30_judicialResearchReinforcement"]["frozenBaselines"][
        "formulaRankAutocorrelation"] = mob[
            "formulaLayerCirculatingOnly"]["rankAutocorrelation"]

    res = {
        "what": "RECURRING LEGAL FORMULA AND REASONING-DIFFUSION "
                "OBSERVATORY. What is actually recurring when a legal formula "
                "reappears, and what that means for a control that removed "
                "recurring wording wholesale.",
        "scopeCorrections": {
            "recordedAt": "the transition-sequencing programme",
            "changesNoNumber": True,
            "1_unitName": "AUTHORITY-ADJACENT RECURRING FORMULA. The unit is "
                          "an exact normalised +-90 character window around an "
                          "authority mention. It is NOT a representation of a "
                          "judgment's language, and no finding here is about "
                          "judicial writing in general.",
            "2_prospectiveClaimWithdrawn": {
                "withdrawn": "if AI changes Saudi legal reasoning, the "
                             "wording layer will move first",
                "permitted": "among the three measured layers, "
                             "authority-adjacent recurring formulas show the "
                             "greatest historical mobility. Whether this "
                             "layer responds first to future AI adoption is a "
                             "prospective hypothesis.",
                "why": "historical mobility is not a statement about response "
                       "to a future event, and the two were conflated."},
            "3_inseparabilityNarrowed": {
                "withdrawn": "source and formula are inseparable",
                "permitted": "at the current exact-fingerprint resolution, no "
                             "circulating formula is observed with more than "
                             "one canonical authority identity",
                "unresolved": "near-family equivalence. A shell differing by "
                              "one surviving word is a different fingerprint "
                              "here, and the family grouping that would catch "
                              "it is unstable (PHASE 3). Answer E of the "
                              "original list -- the citation shell -- is "
                              "UNOBSERVED, not disproved."},
        },
        "terminology": {
            "RECURRING_LEGAL_FORMULA": "a wording fingerprint observed in "
                                       "several judgments. Neutral by "
                                       "construction: it may be boilerplate, "
                                       "it may be the carrier of a legal "
                                       "proposition, and the word TEMPLATE is "
                                       "not used because it presumes the "
                                       "first.",
            "notCopying": "recurrence is co-occurrence of wording, never "
                          "copying or influence.",
            "notCausal": "no phase in this file makes or implies a causal "
                         "claim.",
        },
        "phase1_frozenStartingPoint": {
            "file": "frozen/doctrinal_diffusion_era_1.json",
            "statement": "the apparent COURT_FIRST doctrinal advantage "
                         "largely disappears after removing recurring wording "
                         "fingerprints",
            "whatWasNotEstablished": "that the recurring wording is "
                                     "boilerplate, or that it caused the "
                                     "effect.",
        },
        "phase2_unitSpecification": unit_spec(rows, schema),
        "phase3_exactVersusFamily": fam,
        "phase4_sourceMasking": p4,
        "phase5_articleAndCodeMasking": p5,
        "phase6_taxonomy": tax,
        "phase6_formulaClasses": fclass_report,
        "phase7_quotationVersusJudicialWording": p7,
        "phase8_sourceFormulaCoupling": p8,
        "phase9_classSpecificAblation": abl,
        "phase9b_volumeControl": vol,
        "phase10_11_formulaFirstMoverAndSurvival": fm,
        "phase13_15_formulaTravel": {k: v for k, v in trav.items()
                                     if k != "rows"},
        "phase16_18_19_variation": var,
        "phase17_sourceSubstitution": sub,
        "phase20_21_concentration": conc,
        "phase22_threeLayerMobility": mob,
        "phase24_codeFormulaDependence": dep,
        "phase25_companionReinterpretation": comp,
        "phase26_formulaForecastability": fore,
        "phase27_formulaDetectorEra1": {k: v for k, v in det.items()
                                        if k != "replay"},
        "phase28_31_aiHypotheses": hyp,
        "phase32_35_contaminationAndRetrieval": cont,
        "phase36_vintages": vin,
        "phase37_asset": {"file": ASSET.name,
                          "rows": len(fclass)},
        "phase38_flowMap": flow_map(rows, fclass),
        "decisions": dec,
        "standingLimitations": [
            "28 canonical identities. Every source-level count is a floor.",
            "the fingerprint is exact-match only; near-exact grouping was "
            "tested and is not stable at this corpus size.",
            "quotation is detected from quotation characters, not by "
            "comparing text to a source.",
            "the matched doctrinal comparison rests on 6 or 7 pairs in every "
            "arm, which is the binding constraint on the whole programme.",
            "only about 3 per cent of authority windows contain a statutory "
            "citation, so the article and code masks act on a small "
            "sub-population and their collapse rates are not a general "
            "statement about legal wording.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    ASSET.write_text(json.dumps(asset(rows, fclass, trav), ensure_ascii=False,
                                indent=1) + "\n", encoding="utf-8")
    print(f"{len(rows):,} mentions, {len(fclass)} circulating formulas")
    print(f"  PHASE 4  {p4['verdict']} "
          f"({p4['shellsWithMoreThanOneSource']} multi-source shells)")
    print(f"  PHASE 9  {abl['baselineVerdict']} -> {abl['allRemovedVerdict']}; "
          f"single-class flips: {abl['singleClassRemovalsThatReproduceTheFlip']}")
    print(f"  PHASE 9b random 90 per cent removal flips "
          f"{vol['arms']['remove90pct']['flipShare']} of draws")
    print(f"  VERDICT  {dec['headlineVerdict']}")
    print(f"-> {OUT.name}, {ASSET.name}")


if __name__ == "__main__":
    main()
