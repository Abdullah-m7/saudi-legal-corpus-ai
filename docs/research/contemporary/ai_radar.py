#!/usr/bin/env python3
"""When does artificial intelligence stop being a tool and become a party?

Two entirely different questions get confused in discussions of AI and law.
One is whether AI changes how legal work is done. The other is whether AI
itself starts generating disputes, evidence and doctrine. This file is only
about the second, and it is built to return zero honestly.

Three levels, and only the third matters:

  CONTEXT                       a legally relevant field (intellectual
                                property, personal data) with no algorithmic
                                system shown -- counted apart so that L2 does
                                not fill up with franchise boilerplate
  L1 EXPLICIT_AI_REFERENCE      the document says «ذكاء اصطناعي», «تعلم آلي»,
                                «خوارزمية» or similar, anywhere, in any role
  L2 AI_RELEVANT_TECHNOLOGY     an automated or algorithmic system appears in
                                a legally relevant position, without its AI
                                status being established
  L3 AI_LEGAL_ISSUE             the algorithmic or AI feature is materially
                                part of what is being decided

A judgment reaches L3 only if an AI term sits inside the dispute -- in the
claim, the defence, the evidence or the court's own reasoning -- rather than
in a company name, a technology-sector description of a party's business, or
a list of a contract's subject matter. Those exclusions are the whole of the
classifier and they are written out below so a reader can audit them.

WHAT THIS FILE WILL NOT DO. It will not infer that a document was written
with AI. There is no stylometry here, no detector, no fluency measure. The
only thing measured is whether the text of a judgment DISCUSSES an
algorithmic system as part of the legal question.

FREEZING A ZERO IS THE POINT. If the corpus contains no AI legal disputes,
that number is worth recording precisely, with its date, its denominator and
its method, because the first entry is only detectable against a baseline
that says there were none.

    python3 ai_radar.py
"""
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from function import MARKS              # noqa: E402
from windows import judgments, year_of  # noqa: E402

OUT = HERE / "ai_radar_results.json"
HITS = HERE / "ai_radar_hits.jsonl.gz"

# ---- the concept inventory. Arabic first, because the judgments are Arabic.
# Each family is a legal issue that could exist without the phrase "artificial
# intelligence" ever appearing, which is why the inventory is broader than the
# obvious term and narrower than "anything digital".
CONCEPTS = {
    "ai.explicit": [
        r"الذكاء\s+الاصطناع", r"ذكاء\s+اصطناع", r"التعلم\s+الآل",
        r"تعلم\s+آل", r"التعلم\s+العميق", r"الشبكات\s+العصب",
        r"النماذج\s+اللغوي", r"الذكاء\s+الاصطناعي\s+التوليد",
        r"ذكاء\s+اصطناعي\s+توليد", r"\bChatGPT\b", r"\bAI\b",
    ],
    "algorithmic.system": [
        r"خوارزم", r"نظام\s+آلي", r"النظام\s+الآلي", r"قرار\s+آلي",
        r"المعالجة\s+الآلية", r"أتمتة", r"الأتمتة", r"نظام\s+ذكي",
        r"المنصة\s+الذكية",
    ],
    "automated.decision": [
        r"اتخاذ\s+القرار\s+آلي", r"القرارات\s+الآلية", r"دون\s+تدخل\s+بشري",
        r"بدون\s+تدخل\s+بشري", r"التصنيف\s+التلقائي",
    ],
    "generated.content": [
        r"محتوى\s+منشأ", r"مولد\s+آلي", r"مُولّد", r"منشأ\s+بالذكاء",
        r"التزييف\s+العميق", r"تزييف\s+عميق", r"مزيف\s+عميق",
    ],
    "automated.contracting": [
        r"العقود\s+الذكية", r"عقد\s+ذكي", r"التعاقد\s+الآلي",
        r"التوقيع\s+الآلي",
    ],
    "algorithmic.evidence": [
        r"دليل\s+رقمي", r"الأدلة\s+الرقمية", r"تقرير\s+آلي",
        r"مخرجات\s+النظام", r"سجلات\s+النظام",
    ],
    "professional.use": [
        r"استخدام\s+التقنية\s+في\s+الترافع", r"إعداد\s+المذكرة\s+آليا",
    ],
    "data.privacy": [
        r"البيانات\s+الشخصية", r"حماية\s+البيانات", r"خصوصية\s+البيانات",
    ],
    "ip.generative": [
        r"حقوق\s+المؤلف", r"الملكية\s+الفكرية",
    ],
}
COMPILED = {k: [re.compile(p) for p in v] for k, v in CONCEPTS.items()}

# The families that, on their own, say nothing about AI. They are collected so
# that a future release can see them move, and they never reach L3 by
# themselves: a personal-data claim is a personal-data claim.
WEAK = ("data.privacy", "ip.generative", "algorithmic.evidence")

# ---- exclusions. An AI term inside these contexts is not a legal issue.
# «شركة الذكاء الاصطناعي المحدودة» is a party's NAME; «نشاط الشركة تقنية
# المعلومات والذكاء الاصطناعي» is a description of what a party sells.
NAME_CONTEXT = re.compile(
    r"(?:شركة|مؤسسة|مكتب|وكالة|مجموعة)\s+[^\n.،؛]{0,40}$")
BUSINESS_CONTEXT = re.compile(
    r"(?:نشاط|أنشطة|السجل\s+التجاري|غرض\s+الشركة|تعمل\s+في\s+مجال|"
    r"متخصصة\s+في)[^\n.،؛]{0,80}$")
# Named institutions whose TITLE contains an AI term. The Saudi Data and AI
# Authority appearing in a trademark judgment is the authority, not an issue.
# Found by reading the two judgments the first pass called L3; both were
# false positives and both are excluded here by rule rather than by hand.
ENTITY_NAME = re.compile(
    r"الهيئة\s+السعودية\s+للبيانات\s+و?ال?ذكاء|"
    r"سدايا|الهيئة\s+العامة\s+للذكاء|مركز\s+الذكاء\s+الاصطناع")
# «جهاز يعمل بنظام الذكاء الاصطناعي» is an attribute of goods being sold. The
# dispute is about the sale; the algorithm is not what is contested.
PRODUCT_ATTRIBUTE = re.compile(
    r"(?:الجهاز|جهاز|المنتج|منتج|السيارة|الآلة|آلة|البرنامج|النظام)"
    r"[^\n.،؛]{0,40}$")
ALIF = str.maketrans("أإآىة", "ااايه")


def norm(s):
    return re.sub(r"\s+", " ", MARKS.sub("", s)).translate(ALIF)


def classify(text, at, end, family, sections):
    """L1, L2 or L3 for one match, with the reason recorded."""
    before = text[max(0, at - 90):at]
    window = text[max(0, at - 60):end + 60]
    if ENTITY_NAME.search(window):
        return "L1", "named institution whose title contains an AI term"
    if NAME_CONTEXT.search(before):
        return "L1", "party name context"
    if BUSINESS_CONTEXT.search(before):
        return "L1", "party business description"
    if family in WEAK:
        # a franchise contract naming intellectual property is not an AI
        # issue, and lumping it into L2 would make L2 meaningless
        return "CONTEXT", "legally relevant field, no algorithmic system shown"
    if PRODUCT_ATTRIBUTE.search(before):
        return "L2", "AI as an advertised attribute of goods in dispute"
    # is the match inside the part of the judgment that decides anything?
    reasoning = sections.get("judgmentTextofRulling") or ""
    facts = sections.get("caseSummary") or sections.get("claim") or ""
    inside = (norm(text[at:end]) in norm(reasoning)
              or norm(text[at:end]) in norm(facts))
    if family == "ai.explicit" and inside:
        return "L3", "explicit AI term inside the reasoning or the claim"
    if family in ("automated.decision", "generated.content",
                  "automated.contracting") and inside:
        return "L3", f"{family} inside the reasoning or the claim"
    return "L2", "AI or algorithmic term present, not shown to be at issue"


def main():
    per_year = defaultdict(lambda: Counter())
    levels = Counter()
    fam = Counter()
    docs = 0
    years = Counter()
    hits = []
    for rec in judgments():
        y = year_of(rec)
        docs += 1
        years[y] += 1
        text = rec["text"]
        s = rec.get("sections") or {}
        best = None
        seen = set()
        for family, pats in COMPILED.items():
            for p in pats:
                m = p.search(text)
                if not m:
                    continue
                lvl, why = classify(text, m.start(), m.end(), family, s)
                fam[(family, lvl)] += 1
                key = (family, lvl)
                if key in seen:
                    continue
                seen.add(key)
                rank = {"CONTEXT": 0, "L1": 1, "L2": 2, "L3": 3}[lvl]
                if best is None or rank > best[0]:
                    best = (rank, lvl, family, why, m.start(), m.end())
        if best:
            lvl = best[1]
            levels[lvl] += 1
            per_year[y][lvl] += 1
            if lvl in ("L2", "L3"):
                a, b = best[4], best[5]
                hits.append({
                    "judgment": rec["id"], "year": y,
                    "city": rec.get("city") or "", "level": lvl,
                    "family": best[2], "why": best[3],
                    # the court's own words, with its identifier, as the
                    # programme requires -- never a paraphrase
                    "quote": re.sub(r"\s+", " ",
                                    text[max(0, a - 60):b + 60]).strip(),
                })
    with gzip.open(HITS, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": {
            "what": "every L2 and L3 candidate, with the matched wording in "
                    "the judgment's own words and its identifier, so the "
                    "classification can be audited without re-running the "
                    "corpus pass. L1 hits are counted but not quoted: they "
                    "are party names and business descriptions.",
            "levels": {"L1": "explicit AI reference anywhere",
                       "L2": "AI-relevant technology, status not established",
                       "L3": "the algorithmic feature is materially at issue"},
        }}, ensure_ascii=False) + "\n")
        for h in sorted(hits, key=lambda d: (d["level"], d["year"], d["judgment"])):
            fh.write(json.dumps(h, ensure_ascii=False) + "\n")
    res = {
        "what": "AI_LEGAL_ISSUE_RADAR: does artificial intelligence appear as "
                "a SUBJECT of Saudi commercial litigation in this corpus?",
        "judgmentsScanned": docs,
        "judgmentsByYear": {str(k): v for k, v in sorted(years.items())
                            if k},
        "byLevel": dict(sorted(levels.items())),
        "L3_count": levels.get("L3", 0),
        "L3_rate_per_10k": round(10000 * levels.get("L3", 0) / docs, 3)
                           if docs else None,
        "byFamilyAndLevel": {f"{a}|{b}": v for (a, b), v in
                             sorted(fam.items())},
        "byYear": {str(y): dict(sorted(c.items()))
                   for y, c in sorted(per_year.items()) if y},
        "firstL3": min([h for h in hits if h["level"] == "L3"],
                       key=lambda d: (d["year"], d["judgment"]), default=None),
        "method": {
            "conceptFamilies": {k: len(v) for k, v in sorted(CONCEPTS.items())},
            "weakFamiliesNeverL3ByThemselves": list(WEAK),
            "exclusions": ["named institution whose title contains an AI "
                           "term (SDAIA and the like)", "party name context",
                           "party business description",
                           "AI as an advertised attribute of goods, which is "
                           "L2 and never L3"],
            "firstPassCorrection": "the first pass returned 2 L3 judgments. "
                                   "Both were read and both were false "
                                   "positives: one names the Saudi Data and "
                                   "AI Authority as proof that a trademark "
                                   "is well known, the other describes a "
                                   "device sold as AI-powered. Two exclusion "
                                   "rules were added and the pass re-run. No "
                                   "judgment was reclassified by hand.",
            "noStylometry": "nothing here infers that a document was produced "
                            "with AI. Only what a judgment DISCUSSES is "
                            "measured.",
            "recall": "bounded by the inventory. A dispute about an "
                      "algorithmic system that never names one is invisible, "
                      "so every count is a floor.",
        },
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"scanned {docs:,} judgments")
    print(f"  L1 {levels.get('L1', 0):,}  L2 {levels.get('L2', 0):,}  "
          f"L3 {levels.get('L3', 0):,}")
    print(f"-> {OUT.name}, {HITS.name}")


if __name__ == "__main__":
    main()
