#!/usr/bin/env python3
"""When the court reaches outside a statute, where exactly does it reach?

The programme has shown that statute books differ in HOW MUCH non-statutory
authority accompanies them, and that the difference survives the composition
of the docket. This asks what that authority IS. For every non-statutory
mention `companions.py` recorded, we have an identity, the nearest statutory
citation at two locality definitions, the speaker, the year, the city, and a
fingerprint of the surrounding wording. That is enough to ask whether each
code carries a recurring doctrinal companion structure, and -- more to the
point -- to ask what would falsify that claim.

Seven answers are on the table and none is preferred:

    A  stable code-specific doctrinal companions
    B  article-specific companions, not code-specific
    C  one generic fiqh reservoir shared by every code
    D  recurring judicial templates rather than doctrine
    E  a party-driven source ecology the bench merely echoes
    F  mixed mechanisms, different per code
    G  no stable structure at all

Three limits are structural and are stated before any number is read.

1.  THE IDENTITY UNIVERSE IS BOUNDED BY THE EXTRACTOR. `authority.py` can name
    five jurists, eight books, six maxim texts and a set of hadith
    transmission markers. A source outside that vocabulary is invisible.
    "The canon is compact" and "the extractor's vocabulary is compact" are not
    distinguishable here, so no concentration statistic is read as a claim
    about the canon.
2.  PROXIMITY IS CO-OCCURRENCE. `locality_check.py` measured the ±500
    neighbourhood as 42.9 per cent related overall, and asymmetrically so.
    Nothing here says a source supplements an article.
3.  LOCAL ATTACHMENT IS RARE FOR MOST CODES. Only four codes carry enough
    locally attached non-statutory mentions to support an identity profile.
    The other seven are reported as INSUFFICIENT_DATA rather than estimated.

    python3 companion_analysis.py
"""
import gzip
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import arabic_ordinals as AO            # noqa: E402
LAYER = HERE / "companion_layer.jsonl.gz"
OUT = HERE / "companion_analysis_results.json"
EDGES = HERE / "code_source_network.json"
R_NULL = 200
R_PAIR = 500
SEED = 20250831
# a code needs this many judgment x code units before an identity profile is
# reported at all. Below it the answer is INSUFFICIENT_DATA, not a small number.
MIN_UNITS = 100
GENERIC = "GENERIC."
UNTRACED = ("GENERIC.fiqh.unattributed", "GENERIC.principle.settled",
            "GENERIC.custom.trade", "GENERIC.maxim.named",
            "GENERIC.quran.citation", "GENERIC.hadith.untraced")
# PHASE 13: the measured share of ±500 neighbourhoods that a human reader
# judged genuinely related, from locality_gold.json. Used only as a
# sensitivity parameter, never as a correction applied to a headline.
THETA = {"evidence_law": 0.600, "commercial_courts_law": 0.231}
THETA_DEFAULT = 0.429


def load():
    rows, schema = [], None
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r:
                schema = r["_schema"]
                continue
            rows.append(r)
    return rows, schema


def rank(d):
    """A Counter as an ordered list, ties broken on the key so runs agree."""
    return sorted(d.items(), key=lambda kv: (-kv[1], str(kv[0])))


def entropy(counts):
    n = sum(counts)
    if n <= 0:
        return 0.0
    return -sum((c / n) * math.log(c / n) for c in counts if c > 0)


def hhi(counts):
    n = sum(counts)
    return round(sum((c / n) ** 2 for c in counts), 4) if n else None


def cosine(a, b):
    ks = set(a) | set(b)
    num = sum(a.get(k, 0) * b.get(k, 0) for k in ks)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return round(num / (da * db), 4) if da and db else None


ART_STRIP = re.compile(r"^[^\d٠-٩ء-ي]+")


def artkey(raw):
    """An article string as a number, orthography and paragraph absorbed.

    «١٦» «16» «السادسة عشرة» are one article; «: (١٦٤» is article 164 behind
    punctuation. The slash form is genuinely ambiguous in this corpus --
    «29/1» and «1/29» both occur for the same provision -- so when both sides
    are numeric the LARGER is read as the article. That is a stated rule, not
    a guess about any one citation: paragraph numbers in these codes are small
    and article numbers are not. Where it is wrong it merges two articles, and
    merging is the conservative direction for a leave-article-out test.
    """
    if not raw:
        return None
    a, para = AO.parse(ART_STRIP.sub("", str(raw)))
    if a is None:
        return None
    if para and str(para).strip().isdigit() and int(para) > a:
        a = int(para)
    return str(a)


def units_of(rows, loc, voice="court"):
    """judgment x code -> the set of source identities attached to it there."""
    key = "instW" if loc == "w500" else "instBlock"
    u = defaultdict(set)
    ment = Counter()
    for r in rows:
        if voice and r["voice"] != voice:
            continue
        c = r[key]
        if not c:
            continue
        u[(r["j"], c)].add(r["cid"])
        ment[(r["j"], c)] += 1
    return u, ment


# ------------------------------------------------------------------ PHASE 4
def phase4(rows):
    named_rules = {"fiqh.jurist", "fiqh.book", "maxim.text", "hadith.citation"}
    named = [r for r in rows if r["rule"] in named_rules]
    res = [r for r in named if r["resolved"]]
    merged = [r for r in named if r.get("merged")]
    raws = Counter(r["cid"] for r in named if r["cid"].startswith("RAW."))
    untraced = [r for r in named if r["cid"] == "GENERIC.hadith.untraced"]
    # the audit set: every merge decision, printed, so over-merging is visible
    import companions as C
    audit = defaultdict(list)
    for surface, (cid, _lab) in sorted(C.CANON.items()):
        audit[cid].append(surface)
    # The one merge in the table that crosses a title and a name: «شيخ
    # الإسلام» is read as Ibn Taymiyya. In Hanbali writing it almost always
    # is, but it is a merge on convention rather than on string identity, so
    # the split is reported and every Ibn Taymiyya figure can be halved by a
    # reader who rejects it. The title form reaches the identity already
    # normalised, the name form only after normalisation.
    it = [r for r in rows if r["cid"] == "J.IBN_TAYMIYYA"]
    title = sum(1 for r in it if not r.get("merged"))
    return {
        "ibnTaymiyyaMentions": len(it),
        "ibnTaymiyyaAsTitleShaykhAlIslamPct": round(100 * title / len(it), 1)
                                              if it else None,
        "mentionsTotal": len(rows),
        "namedSourceMentions": len(named),
        "genericMentions": len(rows) - len(named),
        "resolved": len(res),
        "resolvedPct": round(100 * len(res) / len(named), 1),
        "untracedHadith": len(untraced),
        "untracedHadithPct": round(100 * len(untraced) / len(named), 1),
        "unresolvedRawMentions": sum(raws.values()),
        "unresolvedRawPct": round(100 * sum(raws.values()) / len(named), 1),
        "uniqueRawStrings": len(raws),
        "uniqueCanonicalIdentities": len({r["cid"] for r in res}),
        "mergedByAliasHandling": len(merged),
        "mergedByAliasHandlingPct": round(100 * len(merged) / max(1, len(res)), 1),
        "topUnresolvedRaw": [[k, v] for k, v in rank(raws)[:12]],
        "auditSet": {k: sorted(v) for k, v in sorted(audit.items())},
    }


# --------------------------------------------------------------- PHASES 5-9
def profiles(rows, loc, voice="court"):
    u, ment = units_of(rows, loc, voice)
    byCode = defaultdict(Counter)
    codeN = Counter()
    srcN = Counter()
    for (j, c), srcs in u.items():
        codeN[c] += 1
        for s in srcs:
            byCode[c][s] += 1
            srcN[s] += 1
    return u, ment, byCode, codeN, srcN


def phase5_9(rows, loc, codeN, byCode, srcN, allN):
    out = {}
    for c, n in rank(codeN):
        if n < MIN_UNITS:
            out[c] = {"units": n, "verdict": "INSUFFICIENT_DATA"}
            continue
        prof = byCode[c]
        tot = sum(prof.values())
        rows_ = []
        for s, k in rank(prof)[:15]:
            p_s_c = k / n
            p_c_s = k / srcN[s]
            base = srcN[s] / allN
            rows_.append({
                "source": s, "judgments": k,
                "P_source_given_code": round(p_s_c, 4),
                "P_code_given_source": round(p_c_s, 4),
                "lift": round(p_s_c / base, 3) if base else None,
            })
        counts = [v for _, v in rank(prof)]
        cum = lambda k: round(100 * sum(counts[:k]) / tot, 1)
        named = {s: v for s, v in prof.items() if not s.startswith(GENERIC)}
        traceable = sum(named.values())
        fiqh_named = sum(v for s, v in prof.items()
                         if s.startswith("J.") or s.startswith("B."))
        fiqh_gen = prof.get("GENERIC.fiqh.unattributed", 0)
        out[c] = {
            "units": n, "verdict": "PROFILED",
            "distinctSources": len(prof),
            "top": rows_,
            # PHASE 8: effective canon size
            "coverageTop1": cum(1), "coverageTop3": cum(3),
            "coverageTop5": cum(5), "coverageTop10": cum(10),
            "hhi": hhi(counts),
            "entropy": round(entropy(counts), 3),
            "effectiveSources": round(math.exp(entropy(counts)), 2),
            # PHASE 9: generic fiqh is data, not noise
            "namedShare": round(100 * traceable / tot, 1),
            "untracedShare": round(100 * sum(prof.get(g, 0) for g in UNTRACED) / tot, 1),
            "fiqhNamed": fiqh_named, "fiqhUnattributed": fiqh_gen,
            "fiqhNamedShareOfFiqh": (round(100 * fiqh_named / (fiqh_named + fiqh_gen), 1)
                                     if fiqh_named + fiqh_gen else None),
        }
    return out


# ------------------------------------------------------------------ PHASE 6
def phase6(byCode, srcN, codeN, allN):
    """Specificity is not popularity: rank by lift and by spread over codes."""
    percode = defaultdict(Counter)
    for c, prof in byCode.items():
        for s, k in prof.items():
            percode[s][c] = k
    out = []
    for s, n in rank(srcN):
        if n < 40:
            continue
        spread = [v for _, v in rank(percode[s])]
        H = entropy(spread)
        best = rank(percode[s])[0]
        base = n / allN
        p_s_c = best[1] / codeN[best[0]]
        out.append({
            "source": s, "judgments": n,
            "codesPresent": len(spread),
            "entropyOverCodes": round(H, 3),
            "effectiveCodes": round(math.exp(H), 2),
            "topCode": best[0], "topCodeJudgments": best[1],
            "P_code_given_source": round(best[1] / n, 4),
            "liftInTopCode": round(p_s_c / base, 3) if base else None,
        })
    return sorted(out, key=lambda d: (-(d["liftInTopCode"] or 0), d["source"]))


# ------------------------------------------------------------------ PHASE 7
def phase7(rows, loc, byCode, codeN, focal, reps=R_NULL):
    """A constrained null that keeps everything except who said what.

    Within each year x city stratum the identities are permuted across the
    mention slots. Year, city, the number of authorities in each judgment, the
    code each slot is attached to, and the global frequency of every source are
    all held exactly. What is destroyed is the pairing of source to code.
    Rare strata barely mix, which makes the null CLOSER to the observed data
    and the resulting z conservative.
    """
    key = "instW" if loc == "w500" else "instBlock"
    live = [r for r in rows if r["voice"] == "court" and r[key]]
    strata = defaultdict(list)
    for i, r in enumerate(live):
        strata[(r["y"], r["city"])].append(i)
    rng = random.Random(SEED)
    watch = {}
    for c in focal:
        for s, _ in rank(byCode[c])[:10]:
            watch[(c, s)] = []
    for _ in range(reps):
        cids = [r["cid"] for r in live]
        for _k, idx in sorted(strata.items(), key=lambda kv: str(kv[0])):
            vals = [cids[i] for i in idx]
            rng.shuffle(vals)
            for i, v in zip(idx, vals):
                cids[i] = v
        u = defaultdict(set)
        for r, cid in zip(live, cids):
            u[(r["j"], r[key])].add(cid)
        cnt = defaultdict(Counter)
        for (j, c), srcs in u.items():
            for s in srcs:
                cnt[c][s] += 1
        for (c, s) in watch:
            watch[(c, s)].append(cnt[c][s])
    out = defaultdict(list)
    for (c, s), draws in sorted(watch.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        obs = byCode[c][s]
        mu = sum(draws) / len(draws)
        sd = math.sqrt(sum((d - mu) ** 2 for d in draws) / len(draws))
        ge = sum(1 for d in draws if d >= obs)
        out[c].append({
            "source": s, "observed": obs, "nullMean": round(mu, 1),
            "nullSd": round(sd, 2),
            "z": round((obs - mu) / sd, 2) if sd > 0 else None,
            "pOneSided": round((ge + 1) / (len(draws) + 1), 4),
            "ratio": round(obs / mu, 2) if mu else None,
        })
    return dict(out)


# --------------------------------------------------------------- PHASE 12
def phase12(rows, loc, a, b, reps=R_PAIR):
    """The same judgment, the same bench, two codes. Do the sources differ?

    Restricting to judgments that attach non-statutory authority locally to
    BOTH codes removes year, city, court, dispute and speaker by construction:
    whatever remains is between the two codes. The null shuffles identities
    across the slots WITHIN each judgment, which is the strongest available
    control -- it holds the judgment's own source pool fixed.
    """
    key = "instW" if loc == "w500" else "instBlock"
    per = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["voice"] != "court" or r[key] not in (a, b):
            continue
        per[r["j"]][r[key]].append(r["cid"])
    both = sorted(j for j, d in per.items() if a in d and b in d)
    if not both:
        return {"judgments": 0, "verdict": "NO_OVERLAP"}
    pa, pb = Counter(), Counter()
    for j in both:
        for s in set(per[j][a]):
            pa[s] += 1
        for s in set(per[j][b]):
            pb[s] += 1
    obs = cosine(pa, pb)
    rng = random.Random(SEED + 1)
    draws = []
    for _ in range(reps):
        qa, qb = Counter(), Counter()
        for j in both:
            slots = [(a, x) for x in per[j][a]] + [(b, x) for x in per[j][b]]
            vals = [s for _, s in slots]
            rng.shuffle(vals)
            ga, gb = set(), set()
            for (c, _), v in zip(slots, vals):
                (ga if c == a else gb).add(v)
            for s in ga:
                qa[s] += 1
            for s in gb:
                qb[s] += 1
        draws.append(cosine(qa, qb))
    mu = sum(draws) / len(draws)
    sd = math.sqrt(sum((d - mu) ** 2 for d in draws) / len(draws))
    le = sum(1 for d in draws if d <= obs)
    na, nb = sum(pa.values()), sum(pb.values())
    diff = []
    for s in sorted(set(pa) | set(pb)):
        fa, fb = pa[s] / na, pb[s] / nb
        if max(fa, fb) >= 0.03:
            diff.append({"source": s, f"share_{a}": round(100 * fa, 1),
                         f"share_{b}": round(100 * fb, 1),
                         "ptDiff": round(100 * (fa - fb), 1)})
    return {
        "judgments": len(both), "codeA": a, "codeB": b,
        "cosine": obs, "nullCosineMean": round(mu, 4), "nullCosineSd": round(sd, 4),
        "z": round((obs - mu) / sd, 2) if sd > 0 else None,
        "pOneSided": round((le + 1) / (reps + 1), 4),
        "topA": [[k, v] for k, v in rank(pa)[:8]],
        "topB": [[k, v] for k, v in rank(pb)[:8]],
        "differences": sorted(diff, key=lambda d: (-abs(d["ptDiff"]), d["source"])),
    }


# --------------------------------------------------------------- PHASE 13
def phase13(rows, loc, a, b):
    """If only the related neighbourhoods are real, does the gap survive?

    p_obs = theta * p_true + (1 - theta) * p_background, where the background
    is what the same judgments cite regardless of code. Inverting it is a
    sensitivity analysis, not a correction: it says which way the known
    imperfection of the locality measure pushes the answer.
    """
    key = "instW" if loc == "w500" else "instBlock"
    per = defaultdict(lambda: defaultdict(list))
    pool = defaultdict(Counter)
    for r in rows:
        if r["voice"] != "court":
            continue
        if r[key] in (a, b):
            per[r["j"]][r[key]].append(r["cid"])
    both = sorted(j for j, d in per.items() if a in d and b in d)
    bg = Counter()
    prof = {a: Counter(), b: Counter()}
    for j in both:
        for c in (a, b):
            for s in set(per[j][c]):
                prof[c][s] += 1
                bg[s] += 1
    tb = sum(bg.values())
    pbg = {s: v / tb for s, v in bg.items()}

    def corrected(c):
        t = sum(prof[c].values())
        th = THETA.get(c, THETA_DEFAULT)
        out = {}
        for s in set(prof[c]) | set(pbg):
            v = (prof[c].get(s, 0) / t - (1 - th) * pbg.get(s, 0)) / th
            out[s] = max(0.0, v)
        z = sum(out.values())
        return {s: v / z for s, v in out.items() if v > 0} if z else {}

    ca, cb = corrected(a), corrected(b)
    oa = {s: v / sum(prof[a].values()) for s, v in prof[a].items()}
    ob = {s: v / sum(prof[b].values()) for s, v in prof[b].items()}
    return {
        "judgments": len(both),
        "thetaA": THETA.get(a, THETA_DEFAULT), "thetaB": THETA.get(b, THETA_DEFAULT),
        "observedCosine": cosine(oa, ob),
        "correctedCosine": cosine(ca, cb),
        "direction": ("WIDENS" if (cosine(ca, cb) or 1) < (cosine(oa, ob) or 0)
                      else "NARROWS"),
        "correctedTopA": [[k, round(100 * v, 1)] for k, v in rank(ca)[:6]],
        "correctedTopB": [[k, round(100 * v, 1)] for k, v in rank(cb)[:6]],
    }


# ------------------------------------------------------------ PHASES 14-15
def phase14(rows, loc, focal):
    """Is the companion carried by the code or by the article?"""
    key = "instW" if loc == "w500" else "instBlock"
    akey = "artW" if loc == "w500" else "artBlock"
    out = {}
    for c in focal:
        arts = defaultdict(lambda: defaultdict(set))
        for r in rows:
            if r["voice"] != "court" or r[key] != c:
                continue
            a = artkey(r[akey])
            if not a:
                continue
            arts[a][r["j"]].add(r["cid"])
        rows_ = []
        allc = Counter()
        for art, js in arts.items():
            prof = Counter()
            for j, srcs in js.items():
                for s in srcs:
                    prof[s] += 1
                    allc[s] += 1
            if len(js) >= 30:
                rows_.append({"article": art, "judgments": len(js),
                              "top": [[k, v] for k, v in rank(prof)[:5]],
                              "profile": prof})
        rows_.sort(key=lambda d: (-d["judgments"], int(d["article"])))
        # do the articles of one code look like each other, or not?
        sims = []
        for i in range(len(rows_)):
            for k in range(i + 1, len(rows_)):
                sims.append(cosine(rows_[i]["profile"], rows_[k]["profile"]))
        for d in rows_:
            d.pop("profile")
        out[c] = {
            "articlesWith30plus": len(rows_),
            "articles": rows_[:8],
            "meanWithinCodeArticleCosine": (round(sum(sims) / len(sims), 4)
                                            if sims else None),
            "minPairCosine": round(min(sims), 4) if sims else None,
        }
    return out


def phase15(rows, loc, drop, focal):
    """Leave the dominant article out and ask the same question again.

    Two drops are reported: the articles the programme named in advance, and
    -- for every profiled code -- the two articles that in fact carry the most
    locally attached authority. If the profile is really the dominant
    article's profile, removing it should change the profile.
    """
    key = "instW" if loc == "w500" else "instBlock"
    akey = "artW" if loc == "w500" else "artBlock"
    out = {}

    def prof(rs):
        u = defaultdict(set)
        for r in rs:
            u[r["j"]].add(r["cid"])
        p = Counter()
        for _j, srcs in u.items():
            for x in srcs:
                p[x] += 1
        return p, len(u)

    for c in focal:
        full = [r for r in rows if r["voice"] == "court" and r[key] == c]
        pf, nf = prof(full)
        counts = Counter()
        for r in full:
            a = artkey(r[akey])
            if a:
                counts[a] += 1
        empirical = [a for a, _v in rank(counts)[:2]]
        named = [str(x) for x in drop.get(c, [])]
        res = {"judgmentsFull": nf,
               "topFull": [[k, round(100 * v / nf, 1)] for k, v in rank(pf)[:6]],
               "articlesByMentions": [[a, v] for a, v in rank(counts)[:5]]}
        for tag, bad in (("named", named), ("empirical", empirical)):
            if not bad:
                res[tag] = {"verdict": "NOT_SPECIFIED"}
                continue
            kept = [r for r in full if (artkey(r[akey]) or "") not in bad]
            pk, nk = prof(kept)
            res[tag] = {
                "droppedArticles": bad,
                "mentionsDroppedPct": round(100 * (len(full) - len(kept)) / len(full), 1),
                "judgmentsAfterDrop": nk,
                "top": [[k, round(100 * v / nk, 1)] for k, v in rank(pk)[:6]] if nk else [],
                "cosineFullVsDropped": cosine({k: v / nf for k, v in pf.items()},
                                              {k: v / nk for k, v in pk.items()})
                                       if nf and nk else None,
            }
        out[c] = res
    for c, bad in sorted(drop.items()):
        if c not in focal:
            out[c] = {"verdict": "INSUFFICIENT_DATA",
                      "namedArticles": [str(x) for x in bad]}
    return out


# ------------------------------------------------------------ PHASES 16-17
def phase16(rows, loc, focal):
    """Doctrine or boilerplate? A companion carried by one fingerprint,
    repeated verbatim, is a template. One carried by many fingerprints across
    many courts is not."""
    key = "instW" if loc == "w500" else "instBlock"
    out = {}
    for c in focal:
        rs = [r for r in rows if r["voice"] == "court" and r[key] == c]
        by = defaultdict(list)
        for r in rs:
            by[r["cid"]].append(r)
        items = []
        for s, g in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]:
            f = Counter(r["tmpl"] for r in g)
            top, topn = rank(f)[0]
            dom = [r for r in g if r["tmpl"] == top]
            items.append({
                "source": s, "mentions": len(g),
                "distinctFingerprints": len(f),
                "topFingerprintShare": round(100 * topn / len(g), 1),
                "topFingerprintJudgments": len({r["j"] for r in dom}),
                "topFingerprintCities": len({r["city"] for r in dom}),
                "fingerprintsPer100": round(100 * len(f) / len(g), 1),
                "repeatedFingerprintShare": round(
                    100 * sum(v for _k, v in f.items() if v > 1) / len(g), 1),
            })
        out[c] = items
    return out


def phase17(rows):
    """Proposition families: feasible only as fingerprint families here."""
    f = Counter(r["tmpl"] for r in rows if r["voice"] == "court")
    n = sum(f.values())
    rep = sum(v for _k, v in f.items() if v > 1)
    big = [v for _k, v in f.items() if v >= 5]
    return {
        "courtMentions": n, "distinctFingerprints": len(f),
        "sharePartOfARepeatedFamily": round(100 * rep / n, 1),
        "familiesWith5plus": len(big),
        "shareInFamiliesWith5plus": round(100 * sum(big) / n, 1),
        "verdict": "FEASIBLE_ONLY_AS_WORDING_FAMILIES",
        "note": "a fingerprint is shared wording, not a shared legal "
                "proposition. Two courts can state the same proposition in "
                "different words and be counted apart, and one formula can "
                "carry different propositions. Proposition families are NOT "
                "attempted: it would require reading, and reading is what the "
                "layer deliberately does not store.",
    }


def boilerplate(rows, min_j=10):
    """Fingerprints that circulate: the same wording in >= min_j judgments."""
    by = defaultdict(set)
    for r in rows:
        if r["voice"] == "court":
            by[r["tmpl"]].add(r["j"])
    return {t for t, js in by.items() if len(js) >= min_j}


def phase16b(rows, loc, focal, min_j=10):
    """The falsification that matters: strip the circulating wording and run
    the two positive tests again on what is left."""
    bp = boilerplate(rows, min_j)
    kept = [r for r in rows if r["tmpl"] not in bp]
    court = [r for r in rows if r["voice"] == "court"]
    return {
        "circulatingFingerprints": len(bp),
        "minJudgmentsToCount": min_j,
        "courtMentionsRemoved": len(court) - sum(1 for r in kept if r["voice"] == "court"),
        "courtMentionsRemovedPct": round(
            100 * (len(court) - sum(1 for r in kept if r["voice"] == "court"))
            / len(court), 1),
        "phase12_deboilerplated": phase12(kept, loc, "evidence_law",
                                          "commercial_courts_law"),
        "phase26_deboilerplated": signature(kept, loc, focal),
        "phase27_deboilerplatedShuffled": signature(kept, loc, focal, shuffled=True),
    }


# --------------------------------------------------------------- PHASE 18
def phase18(rows, loc, focal):
    key = "instW" if loc == "w500" else "instBlock"
    out = {}
    for c in focal:
        u = defaultdict(set)
        for r in rows:
            if r["voice"] == "court" and r[key] == c:
                u[r["j"]].add(r["cid"])
        n = len(u)
        if not n:
            continue
        p = Counter()
        for _j, srcs in u.items():
            for s in srcs:
                p[s] += 1
        named = {s: v for s, v in p.items() if s.startswith("M.")}
        out[c] = {
            "judgments": n,
            "namedMaximTextPct": round(100 * sum(named.values()) / n, 1),
            "maximLabelOnlyPct": round(100 * p.get("GENERIC.maxim.named", 0) / n, 1),
            "topMaxims": [[k, v, round(100 * v / n, 1)] for k, v in rank(named)[:5]],
        }
    return out


# ------------------------------------------------------------ PHASES 19-21
def phase19_21(rows, loc, focal):
    key = "instW" if loc == "w500" else "instBlock"
    out = {}
    for c in focal:
        per = defaultdict(lambda: {"court": set(), "party": set()})
        for r in rows:
            if r[key] == c:
                per[r["j"]][r["voice"]].add(r["cid"])
        bench = Counter()
        bar = Counter()
        nb = np_ = 0
        for _j, d in per.items():
            if d["court"]:
                nb += 1
                for s in d["court"]:
                    bench[s] += 1
            if d["party"]:
                np_ += 1
                for s in d["party"]:
                    bar[s] += 1
        both = [j for j, d in per.items() if d["court"] and d["party"]]
        surv = kept = benchgen = tot_b = 0
        for j in both:
            d = per[j]
            surv += len(d["party"])
            kept += len(d["party"] & d["court"])
            tot_b += len(d["court"])
            benchgen += len(d["court"] - d["party"])
        out[c] = {
            "judgmentsBench": nb, "judgmentsBar": np_,
            "judgmentsBoth": len(both),
            "topBench": [[k, round(100 * v / nb, 1)] for k, v in rank(bench)[:6]] if nb else [],
            "topBar": [[k, round(100 * v / np_, 1)] for k, v in rank(bar)[:6]] if np_ else [],
            "benchBarCosine": cosine(bench, bar) if nb and np_ else None,
            "survivalBarToBenchPct": round(100 * kept / surv, 1) if surv else None,
            "benchGeneratedPct": round(100 * benchgen / tot_b, 1) if tot_b else None,
            "marginalVerdict": ("PROFILED" if min(nb, np_) >= 40
                                else "INSUFFICIENT_DATA"),
            # survival and bench-generation are PAIRED measures and need
            # judgments where both voices attach authority to the same code.
            # There are almost none, so they are reported and disqualified.
            "pairedVerdict": ("PROFILED" if len(both) >= 40
                              else "INSUFFICIENT_DATA"),
        }
    return out


# ------------------------------------------------------------ PHASES 22-24
def phase22_23(rows, loc, focal):
    key = "instW" if loc == "w500" else "instBlock"
    out = {}
    for c in focal:
        def prof(pred):
            u = defaultdict(set)
            for r in rows:
                if r["voice"] == "court" and r[key] == c and pred(r):
                    u[r["j"]].add(r["cid"])
            p = Counter()
            for _j, s in u.items():
                for x in s:
                    p[x] += 1
            return p, len(u)
        years = {}
        for y in (1444, 1445, 1446):
            p, n = prof(lambda r, y=y: r["y"] == y)
            if n >= 40:
                years[y] = (p, n)
        ycos = []
        ks = sorted(years)
        for i in range(len(ks)):
            for k in range(i + 1, len(ks)):
                ycos.append(cosine(years[ks[i]][0], years[ks[k]][0]))
        cities = Counter(r["city"] for r in rows
                         if r["voice"] == "court" and r[key] == c)
        top = [x for x, v in rank(cities)[:4] if v >= 60]
        cprof = {}
        for ct in top:
            p, n = prof(lambda r, ct=ct: r["city"] == ct)
            if n >= 40:
                cprof[ct] = (p, n)
        ccos = []
        cs = sorted(cprof)
        for i in range(len(cs)):
            for k in range(i + 1, len(cs)):
                ccos.append(cosine(cprof[cs[i]][0], cprof[cs[k]][0]))
        out[c] = {
            "yearsCompared": {str(k): years[k][1] for k in ks},
            "meanYearCosine": round(sum(ycos) / len(ycos), 4) if ycos else None,
            "minYearCosine": round(min(ycos), 4) if ycos else None,
            "citiesCompared": {k: cprof[k][1] for k in cs},
            "meanCityCosine": round(sum(ccos) / len(ccos), 4) if ccos else None,
            "minCityCosine": round(min(ccos), 4) if ccos else None,
        }
    return out


def phase24(byCode, srcN, codeN, focal):
    """Portable sources travel; code-bound sources do not."""
    percode = defaultdict(Counter)
    for c in focal:
        for s, k in byCode[c].items():
            percode[s][c] = k
    out = []
    for s, per in sorted(percode.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])):
        tot = sum(per.values())
        if tot < 40:
            continue
        shares = {c: per[c] / codeN[c] for c in per}
        H = entropy(list(per.values()))
        eff = math.exp(H)
        out.append({
            "source": s, "judgments": tot,
            "codes": len(per), "effectiveCodes": round(eff, 2),
            "presenceRateByCode": {c: round(100 * v, 1) for c, v in
                                   sorted(shares.items(), key=lambda kv: (-kv[1], kv[0]))},
            "class": ("PORTABLE" if eff >= 2.5 else
                      "SEMI_PORTABLE" if eff >= 1.6 else "CODE_BOUND"),
        })
    return out


# ------------------------------------------------------------ PHASES 26-28
def split(j):
    return int(hashlib.sha1(j.encode()).hexdigest(), 16) % 5 == 0


def signature(rows, loc, focal, shuffled=False, seed=SEED):
    key = "instW" if loc == "w500" else "instBlock"
    live = [r for r in rows if r["voice"] == "court" and r[key] in focal]
    if shuffled:
        rng = random.Random(seed)
        strata = defaultdict(list)
        for i, r in enumerate(live):
            strata[(r["y"], r["city"])].append(i)
        cids = [r["cid"] for r in live]
        for _k, idx in sorted(strata.items(), key=lambda kv: str(kv[0])):
            vals = [cids[i] for i in idx]
            rng.shuffle(vals)
            for i, v in zip(idx, vals):
                cids[i] = v
        live = [dict(r, cid=c) for r, c in zip(live, cids)]
    tr, te = defaultdict(set), defaultdict(set)
    for r in live:
        (te if split(r["j"]) else tr)[(r["j"], r[key])].add(r["cid"])
    prof = defaultdict(Counter)
    n = Counter()
    vocab = set()
    for (j, c), srcs in tr.items():
        n[c] += 1
        for s in srcs:
            prof[c][s] += 1
            vocab.add(s)
    V = len(vocab) or 1
    a = 0.5
    tot = sum(n.values())
    scores = {}
    for use_prior in (False, True):
        hit = seen = 0
        conf = defaultdict(Counter)
        for (j, c), srcs in sorted(te.items()):
            if len(srcs) < 2 or c not in n:
                continue
            best, bs = None, None
            for cand in sorted(focal):
                if cand not in n:
                    continue
                sc = sum(math.log((prof[cand][s] + a) / (n[cand] + a * V))
                         for s in sorted(srcs))
                if use_prior:
                    sc += math.log(n[cand] / tot)
                if bs is None or sc > bs:
                    bs, best = sc, cand
            seen += 1
            hit += (best == c)
            conf[c][best] += 1
        per = {}
        f1s = []
        for c in sorted(conf):
            rec = conf[c][c] / sum(conf[c].values()) if conf[c] else 0
            pre_d = sum(conf[x][c] for x in conf)
            pre = conf[c][c] / pre_d if pre_d else 0
            f1 = 2 * pre * rec / (pre + rec) if pre + rec else 0
            f1s.append(f1)
            per[c] = {"n": sum(conf[c].values()), "recall": round(100 * rec, 1),
                      "precision": round(100 * pre, 1), "f1": round(100 * f1, 1)}
        scores["withPrior" if use_prior else "uniformPrior"] = {
            "accuracy": round(100 * hit / seen, 1) if seen else None,
            "macroF1": round(100 * sum(f1s) / len(f1s), 1) if f1s else None,
            "perCode": per,
            "confusion": {c: dict(sorted(v.items())) for c, v in sorted(conf.items())},
        }
        if not use_prior:
            n_test = seen
    prior = max(n.values()) / tot if n else None
    return {
        "trainUnits": tot, "testUnits": n_test,
        "codes": sorted(k for k in n),
        "accuracy": scores["uniformPrior"]["accuracy"],
        "macroF1": scores["uniformPrior"]["macroF1"],
        "chance": round(100 / len([k for k in n]), 1) if n else None,
        "majorityBaseline": round(100 * prior, 1) if prior else None,
        "uniformPrior": scores["uniformPrior"],
        "withPrior": scores["withPrior"],
    }


def phase28(rows, loc, focal):
    """What would a retrieval system have to carry beside the statute?"""
    key = "instW" if loc == "w500" else "instBlock"
    out = {}
    for c in focal:
        live = [r for r in rows if r["voice"] == "court" and r[key] == c]
        tr = [r for r in live if not split(r["j"])]
        te = [r for r in live if split(r["j"])]
        if len(te) < 40:
            out[c] = {"verdict": "INSUFFICIENT_DATA", "testMentions": len(te)}
            continue
        u = defaultdict(set)
        for r in tr:
            u[r["j"]].add(r["cid"])
        p = Counter()
        for _j, s in u.items():
            for x in s:
                p[x] += 1
        order = [k for k, _v in rank(p)]
        cov = {}
        for k in (0, 1, 3, 5, 10):
            top = set(order[:k])
            cov[f"top{k}"] = round(100 * sum(1 for r in te if r["cid"] in top)
                                   / len(te), 1)
        # the whole court-reasoning universe, for comparison
        allsrc = {r["cid"] for r in rows if r["voice"] == "court"}
        cov["courtReasoningUniverse"] = round(
            100 * sum(1 for r in te if r["cid"] in allsrc) / len(te), 1)
        cov["distinctSourcesInTrain"] = len(order)
        cov["testMentions"] = len(te)
        out[c] = cov
    return out


# --------------------------------------------------------------- PHASE 29
def phase29(rows, loc, focal):
    key = "instW" if loc == "w500" else "instBlock"
    out = {}
    for c in focal:
        live = [r for r in rows if r["voice"] == "court" and r[key] == c]
        if not live:
            continue
        n = len(live)
        unt = sum(1 for r in live if r["cid"] in UNTRACED)
        raw = sum(1 for r in live if r["cid"].startswith("RAW."))
        out[c] = {
            "mentions": n,
            "untraceablePct": round(100 * unt / n, 1),
            "unresolvedRawPct": round(100 * raw / n, 1),
            "traceablePct": round(100 * (n - unt - raw) / n, 1),
            "byKind": {k: round(100 * v / n, 1) for k, v in
                       sorted(Counter(r["cid"] for r in live
                                      if r["cid"] in UNTRACED).items())},
        }
    return out


# --------------------------------------------------------------- PHASE 30
def phase30(block, focal):
    """Classify each profiled code by mechanism, from stated thresholds.

    The thresholds are arbitrary in the way every cut is arbitrary; they are
    written here so a reader who prefers different ones can re-classify from
    the signal table rather than from the label.

        A  CODE_SPECIFIC_STABLE   a named companion set, robust to dropping
                                  the dominant article and stable over years
        B  ARTICLE_CARRIED        the profile is one article's profile
        C  GENERIC_RESERVOIR      unnamed fiqh, scripture and settled practice
                                  with no distinctive named companion
        D  TEMPLATE_CARRIED       carried by circulating wording
        E  PARTY_DRIVEN           the bench echoes the bar
        F  MIXED
        G  NO_STABLE_STRUCTURE
        H  INSUFFICIENT_DATA
    """
    prof = block["phase5_8_9_profiles"]
    p15 = block["phase15_leaveArticleOut"]
    p16 = block["phase16_templates"]
    p22 = block["phase22_23_stability"]
    p29 = block["phase29_untraceable"]
    nulls = {c: {d["source"]: d for d in v}
             for c, v in block.get("phase7_null", {}).items()}
    f1 = block["phase26_signature"]["uniformPrior"]["perCode"]
    f1s = block["phase27_shuffledControl"]["uniformPrior"]["perCode"]
    out = {}
    for c in focal:
        drop = p15[c]["empirical"]["cosineFullVsDropped"]
        tmplmax = max((r["topFingerprintShare"] for r in p16[c][:5]), default=0)
        spec = [r for r in prof[c]["top"]
                if (r["lift"] or 0) >= 2 and r["judgments"] >= 40
                and not r["source"].startswith(GENERIC)
                and (nulls.get(c, {}).get(r["source"], {}).get("z") or 0) >= 3]
        sig = f1.get(c, {}).get("f1", 0)
        sig0 = f1s.get(c, {}).get("f1", 0)
        S = {
            "units": prof[c]["units"],
            "articleDropCosine": drop,
            "articleCarried": drop is not None and drop < 0.75,
            "articleRobust": drop is not None and drop >= 0.85,
            "topFingerprintShareMax": tmplmax,
            "templateHeavy": tmplmax >= 25,
            "untraceablePct": p29[c]["untraceablePct"],
            "genericDominated": p29[c]["untraceablePct"] >= 70,
            "namedCompanionsWithLift2AndZ3": [r["source"] for r in spec],
            "yearCosine": p22[c]["meanYearCosine"],
            "yearStable": (p22[c]["meanYearCosine"] or 0) >= 0.90,
            "cityCosine": p22[c]["meanCityCosine"],
            "signatureF1": sig, "shuffledF1": sig0,
            "identifiable": sig >= 40 and sig - sig0 >= 15,
        }
        if S["articleCarried"]:
            m = "B_ARTICLE_CARRIED" + ("_WITH_D_TEMPLATE" if S["templateHeavy"] else "")
        elif S["namedCompanionsWithLift2AndZ3"] and S["articleRobust"] and S["identifiable"]:
            m = "A_CODE_SPECIFIC_STABLE" + ("_WITH_D_TEMPLATE" if S["templateHeavy"] else "")
        elif S["genericDominated"] and not S["namedCompanionsWithLift2AndZ3"]:
            m = "C_GENERIC_RESERVOIR" + ("_WITH_D_TEMPLATE" if S["templateHeavy"] else "")
        elif S["templateHeavy"]:
            m = "D_TEMPLATE_CARRIED"
        else:
            m = "F_MIXED"
        S["mechanism"] = m
        out[c] = S
    out["_notTestable"] = {
        "E_PARTY_DRIVEN": "not testable: the paired bench-and-bar measure "
                          "needs judgments where both voices attach authority "
                          "to the same code locally, and there are 5 to 22 of "
                          "them per code",
        "G_NO_STABLE_STRUCTURE": "rejected corpus-wide by PHASE 12 and PHASE "
                                 "26, not per code",
    }
    return out


def main():
    rows, schema = load()
    focal_all = ["evidence_law", "commercial_courts_law",
                 "commercial_courts_implementing_regulation",
                 "sharia_procedure_law", "civil_transactions_law",
                 "companies_law", "law_practice_law", "arbitration_law",
                 "bankruptcy_law", "sharia_procedure_implementing_regulation",
                 "law_practice_implementing_regulation"]
    res = {"schema": schema, "rows": len(rows),
           "judgments": len({r["j"] for r in rows}),
           "minUnitsForProfile": MIN_UNITS}
    res["phase4_resolution"] = phase4(rows)

    for loc in ("w500", "block"):
        u, ment, byCode, codeN, srcN = profiles(rows, loc)
        allN = len(u)
        tag = f"loc_{loc}"
        focal = [c for c in focal_all if codeN[c] >= MIN_UNITS]
        block = {
            "unitsTotal": allN,
            "codesProfiled": focal,
            "codesInsufficient": [c for c in focal_all if codeN[c] < MIN_UNITS],
            "phase5_8_9_profiles": phase5_9(rows, loc, codeN, byCode, srcN, allN),
            "phase6_specificity": phase6(byCode, srcN, codeN, allN),
            "phase14_articles": phase14(rows, loc, focal),
            "phase15_leaveArticleOut": phase15(rows, loc, {
                "evidence_law": [1, 29],
                "civil_transactions_law": [120, 720],
                "law_practice_law": [26],
            }, focal),
            "phase16_templates": phase16(rows, loc, focal),
            "phase16b_deboilerplated": phase16b(rows, loc, focal),
            "phase18_maxims": phase18(rows, loc, focal),
            "phase19_21_voice": phase19_21(rows, loc, focal_all),
            "phase22_23_stability": phase22_23(rows, loc, focal),
            "phase24_portability": phase24(byCode, srcN, codeN, focal),
            "phase26_signature": signature(rows, loc, focal),
            "phase27_shuffledControl": signature(rows, loc, focal, shuffled=True),
            "phase28_retrieval": phase28(rows, loc, focal),
            "phase29_untraceable": phase29(rows, loc, focal),
        }
        if loc == "w500":
            block["phase7_null"] = phase7(rows, loc, byCode, codeN, focal)
        block["phase12_sameJudgment"] = phase12(
            rows, loc, "evidence_law", "commercial_courts_law")
        block["phase12_sameJudgment_ccir"] = phase12(
            rows, loc, "evidence_law", "commercial_courts_implementing_regulation")
        block["phase13_relatednessSensitivity"] = phase13(
            rows, loc, "evidence_law", "commercial_courts_law")
        res[tag] = block

    res["phase17_propositions"] = phase17(rows)
    res["phase30_mechanism"] = phase30(res["loc_w500"],
                                       res["loc_w500"]["codesProfiled"])

    # -------------------------------------------------- PHASE 25: the asset
    u, ment, byCode, codeN, srcN = profiles(rows, "w500")
    allN = len(u)
    nulls = {c: {d["source"]: d for d in v}
             for c, v in res["loc_w500"]["phase7_null"].items()}
    tmpl = {c: {d["source"]: d for d in v}
            for c, v in res["loc_w500"]["phase16_templates"].items()}
    edges = []
    for c in sorted(byCode):
        if codeN[c] < MIN_UNITS:
            continue
        for s, k in rank(byCode[c]):
            if k < 10:
                continue
            base = srcN[s] / allN
            e = {"code": c, "source": s, "judgments": k,
                 "P_source_given_code": round(k / codeN[c], 4),
                 "P_code_given_source": round(k / srcN[s], 4),
                 "lift": round((k / codeN[c]) / base, 3) if base else None}
            if s in nulls.get(c, {}):
                e["nullZ"] = nulls[c][s]["z"]
                e["nullP"] = nulls[c][s]["pOneSided"]
            if s in tmpl.get(c, {}):
                e["topFingerprintShare"] = tmpl[c][s]["topFingerprintShare"]
            edges.append(e)
    EDGES.write_text(json.dumps({
        "note": "code -> non-statutory source edges, court voice, nearest "
                "statutory citation within 500 characters. An edge is "
                "CO-OCCURRENCE INSIDE A WINDOW, not a claim that the source "
                "supplements the article. The identity universe is bounded by "
                "authority.py's vocabulary, so every weight is a floor.",
        "window": 500, "voice": "court", "years": [1444, 1445, 1446],
        "unit": "judgment x code presence",
        "codeUnits": {c: codeN[c] for c in sorted(byCode) if codeN[c] >= MIN_UNITS},
        "edges": edges}, ensure_ascii=False, indent=1), encoding="utf-8")
    res["phase25_network"] = {"edges": len(edges), "file": EDGES.name}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    p4 = res["phase4_resolution"]
    print(f"{res['rows']:,} mentions / {res['judgments']:,} judgments")
    print(f"named-source mentions {p4['namedSourceMentions']:,}, "
          f"resolved {p4['resolvedPct']} %, untraced hadith "
          f"{p4['untracedHadithPct']} %, unresolved raw {p4['unresolvedRawPct']} %")
    print(f"profiled codes: {res['loc_w500']['codesProfiled']}")
    print(f"signature accuracy {res['loc_w500']['phase26_signature']['accuracy']} % "
          f"vs shuffled {res['loc_w500']['phase27_shuffledControl']['accuracy']} % "
          f"(chance {res['loc_w500']['phase26_signature']['chance']} %)")
    print(f"-> {OUT.name}, {EDGES.name}")


if __name__ == "__main__":
    main()
