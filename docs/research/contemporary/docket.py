#!/usr/bin/env python3
"""Case morphology, and code-local authority neighbourhoods, in one pass.

The instrument effect has now survived citation load, enacted-text features,
age, domain, three functional taxonomies, article composition, matched legal
function and year. One large competitor is untested: the codes may simply be
invoked in different kinds of dispute.

Testing that needs two things the mention layer cannot give.

    DOCKET FEATURES. What kind of case this was, read from the RECITAL only.
    The recital states the parties' requests and what happened procedurally,
    before the court reasons. Taking the features from there and the outcome
    from the reasons keeps the predictor upstream of the thing being
    explained, which is the whole point: a feature read out of the reasons
    would be a symptom of supplementation, not a cause of it.

    MENTION POSITIONS. To ask whether ONE code inside a judgment sits beside
    non-statutory authority while ANOTHER in the same judgment does not, the
    whole-judgment flag is useless -- it marks every code in the document the
    moment one jurist is quoted anywhere. So the offsets are recomputed here
    and a local neighbourhood is measured around each statutory mention.

Neither is a claim about causation. A docket feature is a description of the
case as the recital reports it; a neighbourhood is co-occurrence within a
window, and it is called LOCAL NON-STATUTORY CO-AUTHORITY throughout, never
"supplementation of" the code.

Writes `docket_layer.jsonl.gz`: one row per judgment, no text.

    python3 docket.py
"""
import collections
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from function import MARKS            # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "docket_layer.jsonl.gz"
YEARS = {1442, 1443, 1444, 1445, 1446}
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
WINDOWS = (500, 1000)

# Every marker is matched against the RECITAL, vocalisation stripped.
R = {
    "default": r"تخلف عن الحضور|لم يحضر|ولم يحضر|غاب عن|رغم تبلغه|غيابي",
    "appeared": r"أجاب وكيل المدعى عليه|أجابت المدعى عليها|مذكرة (?:ب)?جوابية"
                r"|قدم المدعى عليه|وأجاب المدعى عليه|دفع المدعى عليه",
    "admission": r"أقر(?:ت|)\s|إقرار|صادق(?:ت|)\s|مصادقة|لا ينكر",
    "settlement": r"صلح|تصالح|مخالصة|تنازل عن الدعوى|اتفاق(?:ية|) تسوية",
    "expert": r"خبير|الخبرة|ندب|تقرير هندسي|تقرير محاسب",
    "jurisdictionChallenge": r"عدم الاختصاص|بعدم اختصاص|الدفع بالاختصاص",
    "arbitrationPlea": r"شرط التحكيم|اتفاق التحكيم|الدفع بالتحكيم|هيئة التحكيم",
    "proofDispute": r"إنكار|أنكر|تزوير|شهود|الشهادة|اليمين|بينة|المضاهاة",
    "feesClaim": r"أتعاب المحاماة|أتعاب المحامي|مصاريف التقاضي|أتعاب الخبرة",
    "damagesClaim": r"تعويض|الأضرار|ضرر",
    "priceClaim": r"قيمة|ثمن|أجرة|مستحقات|فواتير|كشف حساب|المتبقي",
    "corporateClaim": r"شركاء|الشراكة|حصص|مضاربة|الشركة المدعى|تصفية الشركة",
    "insolvencyClaim": r"إفلاس|التصفية|إعادة التنظيم|التسوية الوقائية",
}
COMPILED = {k: re.compile(v) for k, v in R.items()}
REQUEST = re.compile(r"إلزام المدعى عليه|إلزام المدعى عليها|يطلب|طلباته في|"
                     r"حصر(?:ت|) (?:دعواه|طلبه|طلباته)")
BLOCK = re.compile(r"[.؛\n]")


def claim_family(f):
    """One family per judgment, by a fixed priority so it is reproducible."""
    for k, name in (("insolvencyClaim", "INSOLVENCY"),
                    ("corporateClaim", "CORPORATE"),
                    ("feesClaim", "FEES"),
                    ("damagesClaim", "DAMAGES"),
                    ("priceClaim", "CONTRACT_PRICE")):
        if f[k]:
            return name
    return "OTHER"


def blocks(text, lo, hi):
    """Start offsets of sentence-like blocks inside a span."""
    cuts = [lo] + [m.end() + lo for m in BLOCK.finditer(text[lo:hi])] + [hi]
    return cuts


def main():
    index, order = M.build(REGISTRY)
    n = 0
    with gzip.open(OUT, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": {
            "years": sorted(YEARS),
            "note": "one row per judgment; NO judgment text. Docket flags are "
                    "read from the recital only, which precedes the court's "
                    "reasoning, so they are upstream of the outcome. Local "
                    "co-authority counts are co-occurrence inside a character "
                    "window and are not a claim that the authority supplements "
                    "the code.",
            "windows": list(WINDOWS)}}, ensure_ascii=False) + "\n")
        for rec in judgments():
            y = year_of(rec)
            if y not in YEARS:
                continue
            text, s = rec["text"], rec.get("sections") or {}
            segs = V.segments(text, s)
            rec_spans = [(a, b) for a, b, v in segs if v == "recital"]
            rea_spans = [(a, b) for a, b, v in segs if v == "reasoning"]
            op_spans = [(a, b) for a, b, v in segs if v == "operative"]
            if not rea_spans:
                continue
            recital = MARKS.sub("", " ".join(text[a:b] for a, b in rec_spans))
            flags = {k: bool(p.search(recital)) for k, p in COMPILED.items()}

            court = collections.Counter()
            stat_at = collections.defaultdict(list)
            nonstat_at = []
            for m in A.mentions(text, s, index, order):
                if m.get("inQuote") or A.voice(m) != "court_reasoning":
                    continue
                court[m["type"]] += 1
                if m["type"] == "statute" and m.get("instrument"):
                    stat_at[m["instrument"]].append(m["at"])
                elif m["type"] in NONSTATUTE:
                    nonstat_at.append(m["at"])

            local = {}
            if stat_at:
                cuts = []
                for a, b in rea_spans:
                    cuts += blocks(text, a, b)
                cuts = sorted(set(cuts))

                def blk(p):
                    lo = 0
                    for c in cuts:
                        if c <= p:
                            lo = c
                        else:
                            return (lo, c)
                    return (lo, len(text))

                nb = {blk(p) for p in nonstat_at}
                for inst, ps in stat_at.items():
                    row = {"mentions": len(ps)}
                    for w in WINDOWS:
                        row[f"w{w}"] = sum(
                            1 for p in ps
                            if any(abs(q - p) <= w for q in nonstat_at))
                    row["block"] = sum(1 for p in ps if blk(p) in nb)
                    local[inst] = row

            fh.write(json.dumps({
                "j": rec["id"], "y": y,
                "ct": rec.get("court_type") or "",
                "city": rec.get("city") or "",
                "appeal": bool(rec.get("is_appeal")),
                "recitalChars": sum(b - a for a, b in rec_spans),
                "reasonChars": sum(b - a for a, b in rea_spans),
                "operativeChars": sum(b - a for a, b in op_spans),
                "requestMarkers": len(REQUEST.findall(recital)),
                **{k: int(v) for k, v in flags.items()},
                "claimFamily": claim_family(flags),
                "courtStatuteMentions": court["statute"],
                "courtNonStatuteMentions": sum(court[t] for t in NONSTATUTE),
                "hybrid": int(court["statute"] > 0
                              and any(court[t] for t in NONSTATUTE)),
                "local": local,
            }, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n:,} judgments -> {OUT.name} "
          f"({OUT.stat().st_size/1e6:.1f} MB gzipped)")


if __name__ == "__main__":
    main()
