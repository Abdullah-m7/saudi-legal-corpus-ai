#!/usr/bin/env python3
"""What legal function does a statutory article perform?

The 79.7 per cent article-level non-overlap is the strongest result in the
manuscript and its most obvious weakness. A court decides jurisdiction whether
or not jurisdiction was argued; it decides the consequences of a defendant's
absence whether or not absence was pleaded. If the articles the bench adds are
mostly of that kind, then "the two sides cite different articles" is a fact
about the judicial office rather than about legal disagreement.

So articles are classified by FUNCTION, from their own enacted text, with the
distinction that the question actually needs:

  STRUCTURAL_PROCEDURAL      the court invokes it by virtue of its office --
                             jurisdiction, service, attendance and default,
                             standing, appeal and finality, costs, procedural
                             bars. Applied whether or not a party raised it.
  DISPUTE_SPECIFIC           applied because of what this dispute contains --
                             the rules of proof brought to bear on the
                             documents a party actually filed, substantive
                             obligation, contract, damages, corporate,
                             insolvency.
  AMBIGUOUS                  the text supports both readings.

Note where the line falls, because it is the whole argument. Evidence Law
article 29 -- an ordinary document is proof against the person who signed it
-- is DISPUTE_SPECIFIC, not structural: no court reaches for it unless a party
has produced a document. Commercial Courts Law article 16 -- jurisdiction --
is structural: every commercial judgment must satisfy itself of jurisdiction.

Rules are ordered and each carries an id, so a hand reading can be localised.

    python3 function.py label      # classify and report
    python3 function.py sheet --out <path>   # stratified validation sample
"""
import argparse
import collections
import gzip
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGISTRY = ROOT / "data" / "corpus_registry" / "corpus_registry.json"
LAYER = HERE / "authority_mentions.jsonl.gz"
OUT = HERE / "function_labels.json"
SEED = 101

FOCUS = ["commercial_courts_law", "commercial_courts_implementing_regulation",
         "evidence_law", "sharia_procedure_law", "civil_transactions_law",
         "companies_law", "arbitration_law", "bankruptcy_law",
         "enforcement_law", "law_practice_law"]

# ordered; first match wins. Each is a function, and each function is mapped
# to one of the three classes the decomposition needs.
RULES = [
    # definitions first: article 1 of most instruments is a glossary and will
    # otherwise match whichever substantive rule its vocabulary mentions.
    ("definitions", r"يقصد\s+بالألفاظ|المعاني\s+المبينة\s+أمام\s+كل\s+منها"
                    r"|يقصد\s+بالعبارات|التعريفات"),
    ("jurisdiction", r"تختص\s+(?:المحكمة|المحاكم|الدائرة)|الاختصاص\s+"
                     r"(?:النوعي|المكاني|الولائي)|تختص\s+بالنظر|ولاية\s+القضاء"),
    ("appeal_finality", r"الاستئناف|التمييز|النقض|قابل\s+للاعتراض"
                        r"|اكتساب\s+(?:الصفة\s+)?القطعية|نهائي[اًة]?\s+"
                        r"(?:غير\s+)?قابل"),
    ("service_notice", r"التبليغ|الإبلاغ|إبلاغ\s+الخصوم|صورة\s+التبليغ"
                       r"|الإخطار\s+كتاب"),
    ("attendance_default", r"تخلف\s+(?:عن\s+)?الحضور|لم\s+يحضر\s+المدعى"
                           r"|عُ?دت\s+الخصومة\s+حضورية|الغياب|غيابي"),
    ("standing_capacity", r"انعدام\s+الصفة|الصفة\s+أو\s+الأهلية|المصلحة"
                          r"|ذي\s+صفة|أهلية\s+التقاضي"),
    ("procedural_bar", r"عدم\s+قبول\s+الدعوى|سبق\s+الفصل|عدم\s+جواز\s+نظر"
                       r"|شطب\s+الدعوى|ترك\s+الخصومة|سقوط\s+الخصومة"),
    ("costs", r"مصاريف\s+التقاضي|أتعاب\s+المحاماة|التعويض\s+عن\s+الأضرار\s+"
              r"المادية\s+والمعنوية|نفقات\s+الدعوى"),
    ("case_management", r"الجلسة\s+التحضيرية|قفل\s+باب\s+المرافعة|تبادل\s+"
                        r"المذكرات|إدارة\s+الدعوى|قيد\s+الدعوى|صحيفة\s+الدعوى"),
    # --- dispute-specific from here
    ("proof_rules", r"المحرر\s+(?:الرسمي|العادي)|البينة\s+على|حجة\s+على"
                    r"|الإقرار|اليمين|شهادة\s+الشهود|القرينة|الخبرة"),
    ("obligation", r"الالتزام|يلتزم\s+|الوفاء\s+بالعقد|فسخ\s+العقد|العقد\s+"
                   r"شريعة|الثمن|الأجرة|التسليم"),
    ("damages", r"الضرر|التعويض\s+عن\s+الضرر|الغرامة|المسؤولية\s+التقصيرية"),
    ("corporate", r"الشركة|الشركاء|رأس\s+المال|مجلس\s+الإدارة|الحصص"
                  r"|الجمعية\s+العامة"),
    ("insolvency", r"الإفلاس|التصفية|إعادة\s+التنظيم\s+المالي|الدائنين"),
    ("arbitration", r"التحكيم|هيئة\s+التحكيم|حكم\s+المحكمين|شرط\s+التحكيم"),
    # «التنفيذية» is the adjective in «اللائحة التنفيذية» and is not
    # enforcement; the negative lookahead is why article 1 stopped being one.
    ("enforcement", r"التنفيذ(?!ية|ي)|السند\s+التنفيذي|الحجز"),
]
COMPILED = [(k, re.compile(v)) for k, v in RULES]
STRUCTURAL = {"definitions", "jurisdiction", "appeal_finality", "service_notice",
              "attendance_default", "standing_capacity", "procedural_bar",
              "costs", "case_management"}
DISPUTE = {"proof_rules", "obligation", "damages", "corporate",
           "insolvency", "arbitration", "enforcement"}


def klass(fn):
    if fn in STRUCTURAL:
        return "STRUCTURAL_PROCEDURAL"
    if fn in DISPUTE:
        return "DISPUTE_SPECIFIC"
    return "AMBIGUOUS"


def articles():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    out = {}
    for t in tracks:
        tid = t.get("track_id")
        if tid not in FOCUS:
            continue
        layer = (t.get("language_layers") or {}).get("arabic") or {}
        p = ROOT / (layer.get("data_path") or "")
        if not p.exists():
            continue
        for r in json.loads(p.read_text(encoding="utf-8")).get("records", []):
            n = r.get("article_number")
            if isinstance(n, int):
                out[(tid, n)] = {
                    "text": r.get("article_text_ar") or "",
                    "title": r.get("article_title_ar") or "",
                }
    return out


# the registry's article text is vocalised; «المحرَّر» with a shadda is not
# the string «المحرر». Parser v2 strips these in canonicalisation, and the
# same normalisation is applied here rather than assumed.
MARKS = re.compile(r"[\u064B-\u0652\u0670\u0653-\u0655\u0640]")


def classify(rec):
    blob = MARKS.sub("", rec["title"] + " " + rec["text"])[:1400]
    for fn, pat in COMPILED:
        if pat.search(blob):
            return fn
    return "other"


def cited_counts():
    court = collections.Counter()
    party = collections.Counter()
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r.get("art") is None:
                continue
            k = (r["inst"], r["art"])
            if r["role"] == "court_reasoning":
                court[k] += 1
            elif r["role"] in ("party_argument", "recital"):
                party[k] += 1
    return court, party


def label():
    arts = articles()
    fns = {k: classify(v) for k, v in arts.items()}
    court, party = cited_counts()
    OUT.write_text(json.dumps(
        {"seed": SEED, "rules": [r[0] for r in RULES],
         "structural": sorted(STRUCTURAL), "disputeSpecific": sorted(DISPUTE),
         "labels": {f"{k[0]}:{k[1]}": {"function": v, "class": klass(v),
                                       "court": court.get(k, 0),
                                       "party": party.get(k, 0)}
                    for k, v in fns.items()}},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    by_class = collections.Counter()
    cites_by_class = collections.Counter()
    for k, fn in fns.items():
        by_class[klass(fn)] += 1
        cites_by_class[klass(fn)] += court.get(k, 0)
    tot = sum(cites_by_class.values()) or 1
    print(f"{len(arts):,} enacted articles classified over {len(FOCUS)} instruments\n")
    print(f"{'class':<26}{'articles':>10}{'court citations':>18}{'share':>8}")
    for c in ("STRUCTURAL_PROCEDURAL", "DISPUTE_SPECIFIC", "AMBIGUOUS"):
        print(f"  {c:<24}{by_class[c]:>10,}{cites_by_class[c]:>18,}"
              f"{100*cites_by_class[c]/tot:>7.1f}%")
    print(f"\nthe top ten operational articles:")
    for k, n in court.most_common(10):
        if k in fns:
            print(f"  {n:>7,}  {k[0][:36]:<36} art {k[1]:<5} "
                  f"{fns[k]:<20}{klass(fns[k])}")
    print(f"\nwrote {OUT.name}")


def sheet(out_path):
    arts = articles()
    court, _ = cited_counts()
    fns = {k: classify(v) for k, v in arts.items()}
    rng = random.Random(SEED)
    top = [k for k, _ in court.most_common(25) if k in arts]
    rest = [k for k in arts if k not in set(top) and court.get(k, 0) > 0]
    rng.shuffle(rest)
    tail = rest[:35]
    lines = [f"FUNCTION GOLD  seed {SEED}   25 most-cited + 35 drawn from the "
             f"cited tail", ""]
    items = []
    for i, k in enumerate(top + tail):
        items.append({"id": f"F{i:03d}", "instrument": k[0], "article": k[1],
                      "proposedFunction": fns[k], "proposedClass": klass(fns[k]),
                      "courtCitations": court.get(k, 0),
                      "stratum": "top25" if k in set(top) else "tail"})
        body = re.sub(r"\s+", " ", arts[k]["text"])[:600]
        lines += ["=" * 78,
                  f"F{i:03d}  {k[0]} art {k[1]}   cited {court.get(k,0):,}",
                  f"      proposed: {fns[k]}  ->  {klass(fns[k])}",
                  "-" * 78, arts[k]["title"], body, ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    (HERE / "function_gold.json").write_text(json.dumps(
        {"seed": SEED, "items": items, "labels": []},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} items -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("label")
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    a = ap.parse_args()
    label() if a.cmd == "label" else sheet(a.out)
