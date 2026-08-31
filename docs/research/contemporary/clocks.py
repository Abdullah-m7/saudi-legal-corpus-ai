#!/usr/bin/env python3
"""A verified legal clock for every instrument the corpus cites.

The transition programme ended on one binding constraint: 59 statutory
arrivals inside the window and only 2 with a legal clock independent of the
corpus. Everything else would have had to take T=0 from the first citation,
which is the outcome.

This builds the missing layer, and it does so WITHOUT a new source. The
repository already holds official enacted texts for 277 instruments, captured
from the Ministry of Justice legal portal and verified against official PDFs.
Those texts carry the decree, its date, and -- in the final article -- the
commencement rule in the legislature's own words:

    «يعمل بهذا النظام بعد (مائة وثمانين) يوماً من تاريخ نشره في الجريدة الرسمية»

So the clock is read off the enacted text, not inferred from citations.

WHAT THIS IMMEDIATELY SHOWS, and it is uncomfortable. The Law of Evidence's
decree is 26/05/1443 and it commences 180 days after publication, which is
1443Q4. CALIBRATION ERA 1 used 1443Q1, taken from the signal registry's
`observable_in_courts_from`, which was itself read off the first citation. The
Era 1 T=0 was three quarters early, and the Civil Transactions Law's was one
quarter early. Era 1 is frozen and is NOT rewritten; a corrected clock opens
CALIBRATION ERA 2.

    python3 clocks.py
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hijri as H                          # noqa: E402

REG = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
ROOT = HERE.parents[2]
OUT = HERE / "clocks_results.json"
CLOCKS = HERE / "legal_clock_registry.json"

# The corpus window, in hijri quarters.
FIRST_Q, LAST_Q = (1442, 1), (1446, 2)

# ---------------------------------------------------------------- PHASE 3
# Arabic number words as they appear in commencement provisions. Written out
# rather than parsed loosely, so an unrecognised form is reported as
# NONE_FOUND instead of guessed at.
NUM = {
    "ثلاثين": 30, "أربعين": 40, "خمسين": 50, "ستين": 60, "تسعين": 90,
    "مائة وعشرين": 120, "مائة وثمانين": 180, "مائة وخمسين": 150,
    "تسعين يوما": 90, "سنة": 365, "ستة أشهر": 180, "ثلاثة أشهر": 90,
    "مائة وثمانين يوما": 180,
}
COMMENCE = re.compile(r"يعمل\s+ب|يُعمل\s+ب|يعمل\s+بهذا|النفاذ|نفاذ\s+هذا")
AFTER_PUB = re.compile(r"من\s+تاريخ\s+نشر|بعد\s+نشر|من\s+تاريخ\s+النشر")


def norm_ar(s):
    return re.sub(r"\s+", " ", (s or "").replace("ـ", "")).strip()


def parse_rule(text):
    """-> (rule, days, verbatim) read from the enacted commencement article."""
    t = norm_ar(text)
    n = None
    for word, days in sorted(NUM.items(), key=lambda kv: -len(kv[0])):
        if word in t.replace("ً", "").replace("ٍ", ""):
            n = days
            break
    if n is None:
        m = re.search(r"\((\d{1,3})\)\s*يوم", t)
        if m:
            n = int(m.group(1))
    if n is not None and AFTER_PUB.search(t):
        return "N_DAYS_AFTER_PUBLICATION", n, t
    if n is not None:
        return "N_DAYS_AFTER_UNSTATED_ANCHOR", n, t
    if AFTER_PUB.search(t):
        return "IMMEDIATE_ON_PUBLICATION", 0, t
    return "NONE_FOUND", None, t


HIJ = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})")


def parse_hijri(s):
    if not isinstance(s, str):
        return None
    m = HIJ.search(s)
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 30 and 1300 <= y <= 1500):
        return None
    return (y, mo, d)


def load_doc(path):
    p = ROOT / path
    if not p.exists():
        return None
    if p.suffix == ".jsonl":
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
                if l.strip()]
        return {"_rows": rows}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------- PHASE 4
# Publication dates that are NOT in the local official texts. Each carries its
# source, its grade and -- where the fetch failed -- exactly how it failed.
# S1 is an official enacted text or gazette record we hold or fetched; S3 is a
# search-engine summary of an official portal page we could not fetch.
EXTERNAL_PUBLICATION = {
    "evidence_law": {
        "publication_hijri": "04/06/1443",
        "publication_gregorian": "2022-01-07",
        "source": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/"
                  "2716057c-c097-4bad-8e1e-ae1400c678d5/1",
        "source_type": "S3_SEARCH_SUMMARY_OF_OFFICIAL_PORTAL",
        "fetch_status": "NOT_FETCHED: laws.boe.gov.sa closed our TLS tunnel "
                        "mid-exchange (ws_closed_mid_exchange after 12s). That "
                        "is OUR network failing, not evidence the source is "
                        "unavailable, and the date is graded accordingly.",
        "corroboration": "the decree number and date in the same summary "
                         "(م/43, 26/05/1443) match the locally held official "
                         "MoJ text exactly",
    },
    "civil_transactions_law": {
        "publication_hijri": "01/12/1444",
        "publication_gregorian": "2023-06-19",
        "source": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/"
                  "655fdb42-8c96-422b-b8c4-b04f0095c94c/1",
        "source_type": "S3_SEARCH_SUMMARY_OF_OFFICIAL_PORTAL",
        "fetch_status": "NOT_FETCHED, same tunnel reset",
        "corroboration": "decree م/191 of 29/11/1444 matches the locally held "
                         "official text",
    },
}
PUB_KEYS = ["gazette_publication_date_hijri", "gazette_publication_hijri",
            "publication_date_hijri", "gazette_issue_date_hijri"]

# Instruments whose enacted text lives in the repository OUTSIDE the
# official_source layout, with the decree metadata that layer would have
# carried. Every value here is attested in locally held repository files; none
# is typed from memory.
LOCAL_TEXT_OVERRIDE = {
    "companies_law": {
        "path": "data/official_arabic_legal_llm/"
                "companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
        "decree": "المرسوم الملكي رقم (م/132)",
        "decree_date_hijri": "01/12/1443",
        "attestation": "the decree number and date appear verbatim in "
                       "locally held repository text as «المرسوم الملكي رقم "
                       "(م / 132) وتاريخ 1 / 12 / 1443هـ»; the commencement "
                       "and replacement articles are articles 281 and 280 of "
                       "the same local official Arabic layer.",
    },
}


def publication_of(doc, tid):
    """-> (hijri tuple or None, grade, raw)"""
    for k in PUB_KEYS:
        v = doc.get(k) if isinstance(doc, dict) else None
        if isinstance(v, dict):
            v = v.get("date_hijri") or v.get("hijri")
        p = parse_hijri(v) if isinstance(v, str) else None
        if p:
            return p, "S1_LOCAL_OFFICIAL_SOURCE_FIELD", v
    ext = EXTERNAL_PUBLICATION.get(tid)
    if ext:
        return parse_hijri(ext["publication_hijri"]), ext["source_type"], ext
    return None, "NONE", None


def commencement_article(doc):
    """The enacted commencement provision, verbatim."""
    arts = doc.get("articles") if isinstance(doc, dict) else None
    cands = []
    if isinstance(arts, dict):
        for k, v in arts.items():
            txt = v.get("text") if isinstance(v, dict) else None
            if txt and COMMENCE.search(txt) and (
                    AFTER_PUB.search(txt) or "يوما" in txt.replace("ً", "")):
                cands.append((v.get("number_label_ar") or k, txt))
    elif isinstance(doc, dict) and "_rows" in doc:
        for r in doc["_rows"]:
            txt = (r.get("article_text_verified") or r.get("official_text_ar")
                   or r.get("text") or "")
            if txt and COMMENCE.search(txt) and (
                    AFTER_PUB.search(txt) or "يوما" in txt.replace("ً", "")):
                cands.append((r.get("article_number") or r.get("article_key"),
                              txt))
    if not cands:
        return None, None
    # the commencement provision is the LAST such article: an earlier one is
    # usually about the implementing regulation, not the law itself
    return cands[-1]


# ---------------------------------------------------------------- PHASE 7
NEW_REG = re.compile(r"لائحة|اللائحة")


def event_type(tid, doc, eff_q, first_court_q, bounded_q=None):
    """NEW_INSTRUMENT / NEW_IMPLEMENTING_REGULATION / ... / UNKNOWN."""
    name = (doc.get("document") or doc.get("title_ar") or tid) if isinstance(
        doc, dict) else tid
    is_reg = bool(NEW_REG.search(str(name))) or tid.endswith("_regulation")
    if doc.get("supersedes") or doc.get("supersedes_ar") or doc.get(
            "repealed_predecessor"):
        base = "REPLACEMENT"
    elif doc.get("amendment_history") or doc.get("amending_decree"):
        base = "MAJOR_AMENDMENT"
    else:
        base = "NEW_IMPLEMENTING_REGULATION" if is_reg else "NEW_INSTRUMENT"
    if eff_q is None:
        if bounded_q == "BEFORE_WINDOW":
            return "FIRST_CORPUS_APPEARANCE_OF_OLD_LAW"
        if bounded_q == "AFTER_WINDOW":
            return "COMMENCES_AFTER_THE_WINDOW"
        if isinstance(bounded_q, tuple):
            eff_q = bounded_q
        else:
            return "UNKNOWN"
    if eff_q < FIRST_Q:
        return "FIRST_CORPUS_APPEARANCE_OF_OLD_LAW"
    if eff_q > LAST_Q:
        return "COMMENCES_AFTER_THE_WINDOW"
    return base


def qkey(q):
    return q[0] * 4 + q[1] if q else None


def quality(rule, days, pub, pub_grade, eff, boundary, bounded_q=None):
    """PHASE 5. C0 to C4, decided by the WEAKEST component."""
    if rule == "NONE_FOUND" and pub is None:
        return "C0_NO_CLOCK"
    if eff is None:
        return ("C2_APPROX_QUARTER" if bounded_q else "C1_YEAR_ONLY")
    if pub is None:
        return "C1_YEAR_ONLY"
    if boundary:
        return "C2_APPROX_QUARTER"
    if pub_grade.startswith("S1"):
        return "C4_EXACT_EFFECTIVE_AND_PUBLICATION"
    return "C3_EXACT_EFFECTIVE_DATE"


def rows_text(doc):
    """Article text out of a verified-records jsonl."""
    return [(r.get("article_number") or r.get("article_key"),
             r.get("article_text_verified") or r.get("official_text_ar")
             or r.get("text") or "")
            for r in doc.get("_rows", [])]


def build_clock(tid, doc, lag):
    ov = LOCAL_TEXT_OVERRIDE.get(tid)
    dd = parse_hijri(doc.get("decree_date_hijri") if isinstance(doc, dict)
                     else None)
    if dd is None and ov:
        dd = parse_hijri(ov["decree_date_hijri"])
    if dd is None and isinstance(doc, dict) and doc.get("_rows"):
        for r in doc["_rows"]:
            dd = parse_hijri(str(r.get("royal_decree") or ""))
            if dd:
                break
    lbl, art = commencement_article(doc) if isinstance(doc, dict) else (None, None)
    rule, days, verbatim = parse_rule(art) if art else ("NONE_FOUND", None, None)
    pub, pub_grade, pub_raw = publication_of(doc, tid)
    eff = eff_q = boundary = None
    lower = upper = None
    if rule == "N_DAYS_AFTER_PUBLICATION" and days is not None:
        if pub:
            eff = H.add_days(*pub, days)
        if dd:
            # publication cannot precede the decree, so decree+N is a hard
            # lower bound; the p90 of the measured gazette lag gives a soft
            # upper one. Neither is a date; both are bounds, and they are used
            # only to CLASSIFY, never to supply an effective date.
            lower = H.add_days(*dd, days)
            upper = H.add_days(*dd, days + (lag.get("p90") or 0))
    elif rule == "IMMEDIATE_ON_PUBLICATION":
        eff = pub
        lower = dd
        upper = H.add_days(*dd, lag.get("p90") or 0) if dd else None
    if eff:
        eff_q = H.quarter(eff[0], eff[1])
        # a date within seven days of a quarter edge is not safely quarterable
        # given the tabular calendar and an unverified publication date
        boundary = eff[2] <= 7 and eff[1] in (1, 4, 7, 10)
    bounded_q = None
    if eff_q is None and lower and upper:
        lo, up = H.quarter(lower[0], lower[1]), H.quarter(upper[0], upper[1])
        if lo == up:
            bounded_q = lo
        elif up < FIRST_Q:
            bounded_q = "BEFORE_WINDOW"
        elif lo > LAST_Q:
            bounded_q = "AFTER_WINDOW"
    return {
        "instrument": tid,
        "official_title_ar": doc.get("document") or doc.get("title_ar")
                             if isinstance(doc, dict) else None,
        "decree": (doc.get("decree") if isinstance(doc, dict) else None)
                  or (ov["decree"] if ov else None),
        "decree_attestation": ov["attestation"] if ov else None,
        "decree_date_hijri": H.fmt(*dd) if dd else None,
        "decree_date_gregorian": H.fmt_g(H.h2jd(*dd)) if dd else None,
        "commencement_article": lbl,
        "commencement_rule_verbatim_ar": verbatim,
        "clock_rule": rule,
        "clock_delay_days": days,
        "official_publication_hijri": H.fmt(*pub) if pub else None,
        "publication_source_grade": pub_grade,
        "publication_source": (pub_raw.get("source")
                               if isinstance(pub_raw, dict) else pub_raw),
        "publication_fetch_status": (pub_raw.get("fetch_status")
                                     if isinstance(pub_raw, dict) else None),
        "first_possible_application_hijri": H.fmt(*eff) if eff else None,
        "first_possible_application_gregorian": (H.fmt_g(H.h2jd(*eff))
                                                 if eff else None),
        "lower_bound_if_publication_unknown": H.fmt(*lower) if lower else None,
        "upper_bound_if_publication_unknown": H.fmt(*upper) if upper else None,
        "bounded_quarter_if_publication_unknown": (
            bounded_q if isinstance(bounded_q, str)
            else f"{bounded_q[0]}Q{bounded_q[1]}" if bounded_q else None),
        "first_observable_quarter": (f"{eff_q[0]}Q{eff_q[1]}" if eff_q else None),
        "quarterBoundaryRisk": bool(boundary),
        "clock_quality": quality(rule, days, pub, pub_grade, eff, boundary,
                                 bounded_q),
        "_eff_q": eff_q,
        "_bounded_q": bounded_q,
    }


def corpus_observations(scorable):
    """First and sustained court/party quarters, and core entry, per instrument."""
    import foresight as F
    rows, _d, _x = F.load()
    S = F.build(rows)
    idx = [i for i, l in enumerate(F.LBL) if l in scorable]
    court = defaultdict(lambda: [0] * len(F.P))
    party = defaultdict(lambda: [0] * len(F.P))
    arts = defaultdict(set)
    for i, p in enumerate(F.P):
        for (inst, a), n in S[p]["courtStat"].items():
            court[inst][i] += n
            arts[inst].add(a)
        for (inst, a), n in S[p]["partyStat"].items():
            party[inst][i] += n
    out = {}
    for inst in sorted(set(court) | set(party)):
        c, pa = court[inst], party[inst]

        def first(v):
            return next((i for i in range(len(F.P)) if v[i]), None)

        def sustained(v):
            run = 0
            for i in idx:
                run = run + 1 if v[i] else 0
                if run >= 3:
                    return i
            return None
        t100 = next((i for i in idx if any(
            k[0] == inst for k in F.top(S[F.P[i]]["courtStat"], 100))), None)
        t50 = next((i for i in idx if any(
            k[0] == inst for k in F.top(S[F.P[i]]["courtStat"], 50))), None)
        fc, fp = first(c), first(pa)
        out[inst] = {
            "courtCitations": sum(c), "partyCitations": sum(pa),
            "articlesCited": len(arts[inst]),
            "firstCourtQuarter": F.LBL[fc] if fc is not None else None,
            "firstPartyQuarter": F.LBL[fp] if fp is not None else None,
            "sustainedCourtQuarter": (F.LBL[sustained(c)]
                                      if sustained(c) is not None else None),
            "sustainedPartyQuarter": (F.LBL[sustained(pa)]
                                      if sustained(pa) is not None else None),
            "top100Quarter": F.LBL[t100] if t100 is not None else None,
            "top50Quarter": F.LBL[t50] if t50 is not None else None,
            "courtByQuarter": {F.LBL[i]: c[i] for i in range(len(F.P)) if c[i]},
            "partyByQuarter": {F.LBL[i]: pa[i] for i in range(len(F.P)) if pa[i]},
            "_fc": fc, "_fp": fp,
        }
    return out, F


def qdiff(lbl, q):
    """quarters between a corpus label and a hijri quarter tuple."""
    if lbl is None or q is None:
        return None
    y, k = int(lbl[:4]), int(lbl[-1])
    return (y * 4 + k) - (q[0] * 4 + q[1])


# ---------------------------------------------------------- PHASES 8 and 9
def falsification(clocks, obs):
    """Is corpus arrival anywhere near legal commencement? And if it is EARLY?

    A citation before the effective date is not assumed to be an error. It is
    classified, and the classes are stated before the counts are read.
    """
    rows, anomalies = [], []
    for c in clocks:
        q, bounded = c["_eff_q"], False
        if q is None and isinstance(c.get("_bounded_q"), tuple):
            q, bounded = c["_bounded_q"], True
        o = obs.get(c["instrument"])
        if q is None or not o:
            continue
        dc = qdiff(o["firstCourtQuarter"], q)
        dp = qdiff(o["firstPartyQuarter"], q)
        r = {"instrument": c["instrument"], "clock_quality": c["clock_quality"],
             "quarterIsBounded": bounded,
             "effectiveQuarter": c["first_observable_quarter"],
             "firstCourtQuarter": o["firstCourtQuarter"],
             "firstPartyQuarter": o["firstPartyQuarter"],
             "courtMinusEffectiveQuarters": dc,
             "partyMinusEffectiveQuarters": dp,
             "courtCitations": o["courtCitations"]}
        if dc is not None and dc < 0:
            pre = sum(n for lbl, n in o["courtByQuarter"].items()
                      if qdiff(lbl, q) < 0)
            r["preEffectiveCourtCitations"] = pre
            r["preEffectiveShare"] = round(pre / o["courtCitations"], 4)
            r["class"] = ("PRE_EFFECTIVE_REFERENCE" if pre <= 0.10 *
                          o["courtCitations"] else
                          "UNKNOWN_LIKELY_IDENTITY_COLLISION")
            anomalies.append(r)
        rows.append(r)
    ok = [r for r in rows if r["courtMinusEffectiveQuarters"] is not None]
    return {
        "instrumentsWithBothAClockAndCorpusUse": len(ok),
        "medianCourtMinusEffectiveQuarters": (
            sorted(r["courtMinusEffectiveQuarters"] for r in ok)[len(ok) // 2]
            if ok else None),
        "arrivingBeforeTheirEffectiveDate": len(anomalies),
        "byClass": None,   # filled below
        "anticipatoryClasses": {
            "PRE_EFFECTIVE_REFERENCE": "a citation dated before the law's "
                                       "effective date. Verified only as an "
                                       "ordering of dates; the judgment's use "
                                       "of the provision is not read.",
            "TRANSITIONAL_APPLICATION": "the law's own transitional article "
                                        "makes it apply to pending cases. "
                                        "Requires the article to say so.",
            "FUTURE_EFFECTIVE_DISCUSSION": "the provision is discussed as "
                                           "forthcoming. NOT SEPARABLE with "
                                           "the layers this repository holds, "
                                           "so it is never assigned.",
            "UNKNOWN_LIKELY_IDENTITY_COLLISION": "more than a tenth of the "
                "instrument's citations fall before its effective date. The "
                "extractor matches an instrument by TITLE, and a replacement "
                "usually keeps its predecessor's title, so the most likely "
                "reading is that the corpus is citing the old law under the "
                "new law's clock. Not anticipatory practice, and not assumed "
                "to be either.",
        },
        "byInstrument": rows,
        "anomalies": anomalies,
        "readingRule": "a large pre-effective share is more likely an "
                       "extractor identity collision -- an old law and its "
                       "replacement share a title -- than anticipatory legal "
                       "practice. Neither is assumed; the share decides which "
                       "class is recorded and both remain falsifiable.",
    }


# --------------------------------------------------------------- PHASE 10
def promotion(clocks, obs, scorable, F):
    """The gate. Eight conditions, all fixed before any outcome was read."""
    sq = [l for l in F.LBL if l in scorable]
    rows = []
    for c in clocks:
        o = obs.get(c["instrument"], {})
        q = c["_eff_q"]
        eff_lbl = c["first_observable_quarter"]
        post = [l for l in sq if q and qdiff(l, q) is not None
                and qdiff(l, q) >= 0]
        pre = [l for l in sq if q and qdiff(l, q) is not None
               and qdiff(l, q) < 0]
        checks = {
            "clockQualityAtLeastC3": c["clock_quality"].startswith(("C3", "C4")),
            "eventTypeLegallyMeaningful": c["event_type"] in (
                "NEW_INSTRUMENT", "NEW_IMPLEMENTING_REGULATION",
                "MAJOR_AMENDMENT", "REPLACEMENT"),
            "commencementInsideWindow": bool(
                q and FIRST_Q <= q <= LAST_Q),
            "atLeastThreeMaturePostQuarters": len(post) >= 3,
            "atLeast150CourtCitations": o.get("courtCitations", 0) >= 150,
            "notTheCollectionEdge": bool(eff_lbl and eff_lbl != F.LBL[-1]),
            "clockNotDerivedFromOutcome": True,
            "aPreQuarterExistsForBaselines": len(pre) >= 1,
        }
        rows.append({
            "instrument": c["instrument"],
            "clock_quality": c["clock_quality"],
            "event_type": c["event_type"],
            "effectiveQuarter": eff_lbl,
            "courtCitations": o.get("courtCitations", 0),
            "maturePostQuarters": len(post),
            "checks": checks,
            "promoted": all(checks.values()),
            "failed": [k for k, v in checks.items() if not v],
        })
    rows.sort(key=lambda r: (not r["promoted"], -r["courtCitations"],
                             r["instrument"]))
    return {
        "gate": {
            "clockQuality": "C3 or C4 -- an exact effective date. C1 never "
                            "becomes a headline calibration event.",
            "eventType": "a legally meaningful event, not the first corpus "
                         "appearance of an old law",
            "commencement": "inside the corpus window",
            "maturePostQuarters": "at least 3",
            "courtSupport": "at least 150 court citations, so eight layers "
                            "have something to read",
            "collectionEdge": "not the last quarter",
            "clockIndependence": "the clock comes from the enacted text and "
                                 "the gazette, never from a citation",
            "baseline": "at least one mature pre-event quarter",
        },
        "promoted": [r["instrument"] for r in rows if r["promoted"]],
        "rejected": [{"instrument": r["instrument"], "why": r["failed"],
                      "clock_quality": r["clock_quality"],
                      "event_type": r["event_type"],
                      "courtCitations": r["courtCitations"]}
                     for r in rows if not r["promoted"]][:40],
        "rows": rows,
        "quotaRule": "the target is four events because TRANSITION_BET_001 "
                     "named four as its earning condition. A weak event is "
                     "NOT promoted to reach it; if three qualify, three is "
                     "the answer.",
    }


def publication_lag_evidence():
    """How long after a decree does the gazette publish it, in local S1 data?

    Measured so that an unknown publication date has a stated empirical range
    rather than an invented value. It is never used to manufacture a date.
    """
    import glob
    lags = []
    for f in sorted(glob.glob(str(ROOT / "sources/*/*/official_source/"
                                  "*_official_source.json"))):
        try:
            j = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        d = parse_hijri(j.get("decree_date_hijri"))
        p = None
        for k in PUB_KEYS:
            p = parse_hijri(j.get(k)) if isinstance(j.get(k), str) else None
            if p:
                break
        if d and p:
            n = H.days_between(d, p)
            if 0 <= n <= 400:
                lags.append((n, Path(f).parts[-3]))
    lags.sort()
    v = [n for n, _ in lags]
    return {
        "pairs": len(v),
        "medianDays": v[len(v) // 2] if v else None,
        "p10": v[len(v) // 10] if v else None,
        "p90": v[len(v) * 9 // 10] if v else None,
        "min": v[0] if v else None, "max": v[-1] if v else None,
        "note": "measured from locally held official texts that carry BOTH a "
                "decree date and a gazette publication date. It bounds how "
                "wrong a missing publication date can make a computed "
                "commencement; it is never substituted for one.",
    }


def main():
    reg = json.loads(REG.read_text(encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    hz = json.loads((HERE / "horizon_results.json").read_text(encoding="utf-8"))
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    obs, F = corpus_observations(scorable)
    lag = publication_lag_evidence()

    clocks, nodoc = [], []
    for t in sorted(tracks, key=lambda x: x["track_id"]):
        tid = t["track_id"]
        if tid not in obs:
            continue                     # the corpus never cites it
        doc = None
        for p in t.get("data_paths", []):
            if "official_source" in p:
                doc = load_doc(p)
                if doc:
                    break
        if doc is None:
            for p in t.get("data_paths", []):
                doc = load_doc(p)
                if doc:
                    break
        if not isinstance(doc, dict):
            nodoc.append(tid)
            continue
        if tid in LOCAL_TEXT_OVERRIDE:
            alt = load_doc(LOCAL_TEXT_OVERRIDE[tid]["path"])
            if isinstance(alt, dict) and alt.get("records"):
                doc = dict(doc)
                doc["_rows"] = alt["records"]
        c = build_clock(tid, doc, lag)
        o = obs[tid]
        c["event_type"] = event_type(tid, doc, c["_eff_q"],
                                     o["firstCourtQuarter"], c["_bounded_q"])
        c.update({k: o[k] for k in
                  ("courtCitations", "partyCitations", "articlesCited",
                   "firstCourtQuarter", "firstPartyQuarter",
                   "sustainedCourtQuarter", "sustainedPartyQuarter",
                   "top100Quarter", "top50Quarter")})
        clocks.append(c)

    fals = falsification(clocks, obs)
    prom = promotion(clocks, obs, scorable, F)
    qual = Counter(c["clock_quality"] for c in clocks)
    types = Counter(c["event_type"] for c in clocks)

    res = {
        "what": "VERIFIED LEGAL CLOCK LAYER. When each instrument the corpus "
                "cites legally became capable of governing, read from the "
                "enacted text rather than from a citation.",
        "whyThisIsNotHistoricalExpansion": "no new source, no new corpus, no "
                "backward extension. The enacted texts were already in the "
                "repository; what was missing was the arithmetic that turns a "
                "commencement provision into a corpus quarter.",
        "phase3_clockComponents": [
            "ROYAL_DECREE_DATE", "COUNCIL_DECISION_DATE",
            "OFFICIAL_PUBLICATION_DATE", "GAZETTE_ISSUE",
            "COMMENCEMENT_RULE", "DELAY_FROM_PUBLICATION",
            "FIRST_POSSIBLE_APPLICATION_DATE", "FIRST_OBSERVABLE_QUARTER"],
        "phase3_note": "these are not synonyms. A statute that commences 180 "
                       "days after PUBLICATION does not commence 180 days "
                       "after its decree, and the two differ by the gazette "
                       "lag measured below.",
        "phase4_sourceHierarchy": {
            "S1": "the enacted text held in this repository, captured from "
                  "the Ministry of Justice legal portal and verified against "
                  "the official PDF. Supplies the decree, its date and the "
                  "commencement rule verbatim.",
            "S2": "an official ministry or regulator page stating "
                  "commencement",
            "S3": "a search-engine summary of an official portal page we "
                  "could not fetch. Used only for publication dates, always "
                  "labelled, and never for a rule.",
            "accessFailure": "laws.boe.gov.sa closes our TLS tunnel "
                             "mid-exchange and www.uqn.gov.sa's older "
                             "permalinks 404 on its redesigned site. Both are "
                             "OUR failures to reach a source, not evidence "
                             "that the source is unavailable, and neither is "
                             "worked around.",
        },
        "phase5_clockQuality": dict(sorted(qual.items())),
        "phase6_delayedCommencement": {
            "rulesObserved": dict(sorted(Counter(
                c["clock_rule"] for c in clocks).items())),
            "staggeredCommencement": "no instrument in this set carries a "
                                     "per-article commencement in its own "
                                     "text, so no ARTICLE_CLOCK overrides are "
                                     "created. An article-version system is "
                                     "not built.",
        },
        "phase7_eventTypes": dict(sorted(types.items())),
        "phase8_falsification": fals,
        "publicationLagEvidence": lag,
        "phase10_promotion": prom,
        "instrumentsWithoutALocalOfficialText": nodoc,
        "phase30_observabilityVersusImportance": "failure to appear in this "
            "corpus does NOT mean a law is unused nationally. It means NO "
            "OBSERVABLE UPTAKE IN THIS PUBLISHED COMMERCIAL ADJUDICATION "
            "CORPUS, and that sentence is carried in every derived record.",
        "calendarNote": "dates are computed on the tabular Islamic calendar, "
                        "which can differ from the observed Umm al-Qura date "
                        "by about one day. Immaterial at quarter resolution "
                        "except at a quarter edge, which is flagged as "
                        "quarterBoundaryRisk rather than resolved.",
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    for c in clocks:
        c.pop("_eff_q", None)
        c.pop("_bounded_q", None)
    CLOCKS.write_text(json.dumps({
        "what": "LEGAL CLOCK REGISTRY. One row per instrument this corpus "
                "cites, with its legal timeline and its corpus timeline side "
                "by side and never mixed.",
        "capture_class": "BACKFILLED: every clock here was recorded after the "
                         "commencement it describes. A clock may calibrate a "
                         "method; it is never foresight.",
        "observabilityDisclosure": res["phase30_observabilityVersusImportance"],
        "calendarNote": res["calendarNote"],
        "sourceHierarchy": res["phase4_sourceHierarchy"],
        "instruments": sorted(clocks, key=lambda c: (-c["courtCitations"],
                                                     c["instrument"])),
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(clocks)} instruments clocked; quality {dict(sorted(qual.items()))}")
    print(f"  event types {dict(sorted(types.items()))}")
    print(f"  promoted: {prom['promoted']}")
    print(f"  arriving before their effective date: "
          f"{fals['arrivingBeforeTheirEffectiveDate']}")
    print(f"-> {OUT.name}, {CLOCKS.name}")


if __name__ == "__main__":
    main()
