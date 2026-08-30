#!/usr/bin/env python3
"""Did codification displace the court's own discretion? A feasibility study.

Saudi Arabia codified in a rush: the Commercial Courts Law (م/93, 1441), the
Evidence Law (م/43, 1443), the Civil Transactions Law (م/191, 29 Dhū al-Qaʿda
1444 — the corpus dates it in the judgments' own words). Before them, a
commercial judge reasoning about an obligation reached for Ibn Taymiyya, for
Kashshāf al-Qināʿ, for «المقرر فقهاً» and «استقر القضاء». The question is
whether the codes replaced that, or merely joined it.

The measurement is possible here and almost nowhere else, because three
things are already built: a corpus with Hijri years, a segmenter that isolates
the bench's own reasons from the parties' pleadings, and a census
(discretion_census.py) that asked the corpus what non-statutory authority
sounds like rather than guessing. 32 of 36 candidate markers are attested; the
four the courts never use are dropped.

WHAT IS AND IS NOT CLAIMED

This is a feasibility study, and the design is stated so its weaknesses can be
seen rather than argued with.

  It is a prevalence series by year, not a causal estimate. Nothing here
  identifies the effect of a statute coming into force. The corpus's year mix
  changes by two orders of magnitude across the span and its publication
  practice changed with it.

  Rising statutory citation after a code is enacted is mechanical: the
  articles did not exist before. The informative quantity is whether
  non-statutory authority FALLS, which is not mechanical either way.

  Density per thousand words is reported beside prevalence, because reasons
  get longer and a longer text carries more of everything.

  Everything is confined to the court's own reasons. A party quoting Ibn
  Taymiyya is not a court reasoning from him.

    python3 discretion.py [--json]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import voice_attribution as V         # noqa: E402
from discretion_census import CANDIDATES, reasons   # noqa: E402

OUT = HERE / "discretion_results.json"

# the five families the census attests, with the four dead candidates dropped
FAMILIES = {
    "jurists and their books": [
        "ابن تيمية", "ابن القيم", "ابن قدامة", "محمد بن إبراهيم",
        "شيخ الإسلام", "مجموع الفتاوى", "كشاف القناع", "المغني",
        "شرح منتهى الإرادات", "الروض المربع", "مطالب أولي النهى",
        "الإنصاف", "زاد المعاد"],
    "maxims of fiqh": [
        "القاعدة الفقهية", "الضرر يزال", "الأصل براءة الذمة",
        "اليقين لا يزول بالشك", "العادة محكمة", "الخراج بالضمان"],
    "scripture": [
        "قوله تعالى", "قوله صلى الله عليه وسلم", "متفق عليه",
        "رواه البخاري أو مسلم"],
    "unattributed doctrine": [
        "المقرر فقهاً", "استقر القضاء", "جرى العمل", "عند الفقهاء",
        "أهل العلم", "الراجح"],
    "discretion named as such": [
        "السلطة التقديرية", "ما تراه المحكمة", "الاجتهاد"],
}
PAT = {k: re.compile(v) for k, v in CANDIDATES.items()}
FAM_OF = {m: f for f, ms in FAMILIES.items() for m in ms}

# 1439 is the first year with more than a thousand judgments; 1447 and 1448
# hold 90 and 277, which is not a year, it is a tail. Court type is held to
# first-instance lawsuits, 93.7 per cent of the corpus, so the series is not
# tracking a changing mix of courts.
# hijri_year is an int in some shards and a string in others
YEARS = [str(y) for y in range(1439, 1447)]
COURT = "Lawsuit"
# the Civil Transactions Law, matched on the name the judgments use for it
CTL = re.compile(r"نظام\s+المعاملات\s+المدنية")


def wilson(k, n, z=1.96):
    if not n:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - r) / d * 100, 1), round((c + r) / d * 100, 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    per = collections.defaultdict(lambda: {
        "inYear": 0, "reasoned": 0, "words": 0, "withFiqh": 0, "withStatute": 0,
        "withNeither": 0, "markerHits": 0, "citeHits": 0,
        "family": collections.Counter(), "familyDocs": collections.Counter(),
        # the within-year contrast: among judgments of the SAME year, do those
        # reasoning from the new civil code use less non-statutory authority
        # than those that do not? Year, court and selection are held constant
        # by construction, which no comparison across years can claim.
        "ctl": 0, "ctlFiqh": 0, "noCtl": 0, "noCtlFiqh": 0})
    skipped_year = skipped_court = no_reasons = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            y = str(r.get("hijri_year") or "").strip()
            if y not in YEARS:
                skipped_year += 1
                continue
            if (r.get("court_type") or "") != COURT:
                skipped_court += 1
                continue
            per[y]["inYear"] += 1
            seg = reasons(r["text"], r.get("sections") or {})
            if seg is None:
                no_reasons += 1
                continue
            b = per[y]
            b["reasoned"] += 1
            b["words"] += len(seg.split())
            fams = set()
            hits = 0
            for name, pat in PAT.items():
                c = len(pat.findall(seg))
                if c:
                    hits += c
                    fam = FAM_OF.get(name)
                    if fam:
                        b["family"][fam] += c
                        fams.add(fam)
            for fam in fams:
                b["familyDocs"][fam] += 1
            cites = len(V.CITE.findall(seg))
            b["markerHits"] += hits
            b["citeHits"] += cites
            b["withFiqh"] += hits > 0
            b["withStatute"] += cites > 0
            b["withNeither"] += (hits == 0 and cites == 0)
            if CTL.search(seg):
                b["ctl"] += 1
                b["ctlFiqh"] += hits > 0
            else:
                b["noCtl"] += 1
                b["noCtlFiqh"] += hits > 0

    rows = []
    for y in YEARS:
        b = per[y]
        n, w = b["reasoned"], b["words"] or 1
        if not n:
            continue
        rows.append({
            "year": y, "inYear": b["inYear"], "reasoned": n,
            # the selection control: whether a circuit writes its own reasons
            # is not constant across years, and everything else here is
            # conditioned on it
            "reasonedShare": round(100 * n / b["inYear"], 1),
            "medianWordsPerReasons": round(w / n),
            "fiqhPrevalence": round(100 * b["withFiqh"] / n, 1),
            "fiqhCI": wilson(b["withFiqh"], n),
            "statutePrevalence": round(100 * b["withStatute"] / n, 1),
            "statuteCI": wilson(b["withStatute"], n),
            "neither": round(100 * b["withNeither"] / n, 1),
            "fiqhPer1kWords": round(1000 * b["markerHits"] / w, 2),
            "citesPer1kWords": round(1000 * b["citeHits"] / w, 2),
            "familyPrevalence": {f: round(100 * b["familyDocs"][f] / n, 1)
                                 for f in FAMILIES},
            "citesCivilCode": b["ctl"],
            "fiqhWhenCitingCivilCode":
                round(100 * b["ctlFiqh"] / b["ctl"], 1) if b["ctl"] else None,
            "fiqhCIWhenCitingCivilCode": wilson(b["ctlFiqh"], b["ctl"]),
            "fiqhWhenNot":
                round(100 * b["noCtlFiqh"] / b["noCtl"], 1) if b["noCtl"] else None,
            "fiqhCIWhenNot": wilson(b["noCtlFiqh"], b["noCtl"]),
        })

    out = {"years": YEARS, "courtType": COURT,
           "skippedOutsideYears": skipped_year,
           "skippedOtherCourt": skipped_court,
           "withoutReasons": no_reasons,
           "civilTransactionsLaw":
               "م/191, 29 Dhū al-Qaʿda 1444, as the judgments themselves date it",
           "rows": rows}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    print(f"first-instance lawsuits, {YEARS[0]}–{YEARS[-1]}, "
          f"court's own reasons only\n")
    print(f"{'year':<6}{'judgments':>10}{'reasoned':>9}{'(%)':>7}{'words':>7}"
          f"{'fiqh %':>20}{'statute %':>20}{'neither':>9}"
          f"{'fiqh/1k':>9}{'cites/1k':>9}")
    for r in rows:
        f = f"{r['fiqhPrevalence']:.1f} [{r['fiqhCI'][0]}, {r['fiqhCI'][1]}]"
        t = f"{r['statutePrevalence']:.1f} [{r['statuteCI'][0]}, {r['statuteCI'][1]}]"
        print(f"{r['year']:<6}{r['inYear']:>10,}{r['reasoned']:>9,}"
              f"{r['reasonedShare']:>7.1f}{r['medianWordsPerReasons']:>7,}"
              f"{f:>20}{t:>20}{r['neither']:>9.1f}"
              f"{r['fiqhPer1kWords']:>9.2f}{r['citesPer1kWords']:>9.2f}")

    print(f"\nprevalence by family of authority, per cent of reasoned judgments")
    print(f"{'year':<7}" + "".join(f"{f[:19]:>21}" for f in FAMILIES))
    for r in rows:
        print(f"{r['year']:<7}" +
              "".join(f"{r['familyPrevalence'][f]:>21.1f}" for f in FAMILIES))
    print("\nwithin one year, judgments that reason from the Civil Transactions"
          "\nLaw against judgments of the same year that do not:\n")
    print(f"{'year':<7}{'cites the code':>16}{'fiqh % when it does':>34}"
          f"{'fiqh % when it does not':>34}")
    for r in rows:
        if not r["citesCivilCode"]:
            continue
        a = (f"{r['fiqhWhenCitingCivilCode']:.1f} "
             f"[{r['fiqhCIWhenCitingCivilCode'][0]}, "
             f"{r['fiqhCIWhenCitingCivilCode'][1]}]")
        c = (f"{r['fiqhWhenNot']:.1f} [{r['fiqhCIWhenNot'][0]}, "
             f"{r['fiqhCIWhenNot'][1]}]")
        print(f"{r['year']:<7}{r['citesCivilCode']:>16,}{a:>34}{c:>34}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
