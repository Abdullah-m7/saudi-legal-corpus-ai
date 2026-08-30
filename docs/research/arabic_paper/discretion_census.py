#!/usr/bin/env python3
"""Before measuring whether codification displaced discretion, ask the corpus
what discretion sounds like.

vocabulary_census.py learned this the hard way: a guessed phrase list produces
a zero, and a zero from a broken search reads exactly like a finding. So this
counts every candidate marker of NON-STATUTORY authority across all 50,666
judgments first. Phrases the courts never use score zero and are dropped;
what survives becomes the instrument.

Counted inside the court's own reasons only — «الأسباب:» to «حكمت الدائرة» —
because a party quoting Ibn Taymiyya is not a court reasoning from him.

    python3 discretion_census.py
"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import voice_attribution as V         # noqa: E402

OUT = HERE / "discretion_census_results.json"

CANDIDATES = {
    # named authorities
    "ابن تيمية": r"ابن\s+تيمية",
    "ابن القيم": r"ابن\s+القيم",
    "ابن قدامة": r"ابن\s+قدامة",
    "محمد بن إبراهيم": r"محمد\s+بن\s+إبراهيم",
    "ابن باز": r"ابن\s+باز",
    "ابن عثيمين": r"ابن\s+عثيمين",
    "شيخ الإسلام": r"شيخ\s+الإسلام",
    # named works
    "مجموع الفتاوى": r"مجموع\s+الفتاوى",
    "كشاف القناع": r"كشاف\s+القناع",
    "المغني": r"(?<![ء-ي])المغني(?![ء-ي])",
    "شرح منتهى الإرادات": r"منتهى\s+الإرادات",
    "الروض المربع": r"الروض\s+المربع",
    "مطالب أولي النهى": r"مطالب\s+أولي\s+النهى",
    "الإنصاف": r"(?<![ء-ي])الإنصاف(?![ء-ي])",
    "زاد المعاد": r"زاد\s+المعاد",
    # maxims
    "القاعدة الفقهية": r"القاعدة\s+الفقهية|القواعد\s+الفقهية",
    "الضرر يزال": r"الضرر\s+يزال",
    "الأصل براءة الذمة": r"الأصل\s+براءة\s+الذمة",
    "اليقين لا يزول بالشك": r"اليقين\s+لا\s+يزول\s+بالشك",
    "الأمور بمقاصدها": r"الأمور\s+بمقاصدها",
    "العادة محكمة": r"العادة\s+محكمة",
    "المشقة تجلب التيسير": r"المشقة\s+تجلب\s+التيسير",
    "الخراج بالضمان": r"الخراج\s+بالضمان",
    # scripture
    "قوله تعالى": r"قول[هـ]?\s+تعالى|قال\s+تعالى",
    "قوله صلى الله عليه وسلم": r"قول[هـ]?\s+صلى\s+الله\s+عليه\s+وسلم"
                                r"|قال\s+صلى\s+الله\s+عليه\s+وسلم",
    "متفق عليه": r"متفق\s+عليه",
    "رواه البخاري أو مسلم": r"رواه\s+(?:البخاري|مسلم)",
    # doctrinal consensus, unattributed
    "المقرر فقهاً": r"المقرر\s+فقه[اًـ]?|المتقرر\s+فقه[اًـ]?",
    "استقر القضاء": r"استقر\s+(?:عليه\s+)?القضاء|ما\s+استقر\s+عليه\s+القضاء",
    "جرى العمل": r"جرى\s+(?:بذلك\s+)?العمل|العرف\s+(?:التجاري|الجاري)",
    "عند الفقهاء": r"عند\s+الفقهاء|لدى\s+الفقهاء|جمهور\s+الفقهاء",
    "أهل العلم": r"أهل\s+العلم",
    "الراجح": r"(?<![ء-ي])الراجح(?![ء-ي])",
    # explicit discretion
    "السلطة التقديرية": r"السلطة\s+التقديرية|سلطة\s+تقديرية|ولاية\s+تقديرية",
    "ما تراه المحكمة": r"ما\s+ترا[هى]\s+(?:المحكمة|الدائرة)"
                       r"|حسب\s+ما\s+ترا[هى]\s+(?:المحكمة|الدائرة)",
    "الاجتهاد": r"(?<![ء-ي])الاجتهاد(?![ء-ي])",
}
PAT = {k: re.compile(v) for k, v in CANDIDATES.items()}


def reasons(text, sections):
    """The court's own reasons, or None where the headings are absent."""
    spans = V.parts(text, sections)
    if not spans:
        return None
    a, b = spans[-1]
    r = V.REASONS.search(text, a, b)
    k = V.RULING.search(text, r.end() if r else a, b)
    return text[r.end():k.start()] if r and k else None


def main():
    hits = collections.Counter()        # marker -> occurrences
    docs = collections.Counter()        # marker -> judgments carrying it
    n = reasoned = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            seg = reasons(r["text"], r.get("sections") or {})
            if seg is None:
                continue
            reasoned += 1
            for name, pat in PAT.items():
                c = len(pat.findall(seg))
                if c:
                    hits[name] += c
                    docs[name] += 1

    print(f"{n:,} judgments; {reasoned:,} carry reasons ({reasoned/n:.1%})\n")
    print(f"{'marker':<30}{'occurrences':>13}{'judgments':>12}{'% of reasoned':>15}")
    for name in CANDIDATES:
        print(f"  {name:<28}{hits[name]:>13,}{docs[name]:>12,}"
              f"{100*docs[name]/reasoned:>14.2f}%")
    dead = [k for k in CANDIDATES if not hits[k]]
    print(f"\n{len(dead)} candidates the courts never use: {dead}")

    OUT.write_text(json.dumps(
        {"judgments": n, "reasoned": reasoned,
         "occurrences": dict(hits), "judgmentsWith": dict(docs),
         "neverUsed": dead}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
