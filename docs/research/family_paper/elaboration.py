#!/usr/bin/env python3
"""Which articles of the Personal Status Law did the executive elaborate?

The Saudi Personal Status Law (2022) codified 252 articles of family law. Its
implementing regulation has 41. The regulation is unusual and useful: it names
the article it elaborates, in words -- «وفقاً لما قضت به المادة (السابعة) من
النظام» -- so the mapping from regulation article to law article can be read
rather than inferred.

This script reads it, and reports which parts of the code the executive chose
to elaborate and which it left alone, at article level and by the law's own
chapter structure.

    python3 elaboration.py   ->  elaboration_results.json
"""

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs/research/arabic_paper"))
import arabic_ordinals  # noqa: E402

LAW = ROOT / ("data/personal_status_arabic_legal_llm/"
              "personal_status_law_legal_llm_001_252.json")
REG = ROOT / ("data/personal_status_arabic_legal_llm/"
              "personal_status_regulation_legal_llm_001_041.json")

# The regulation refers to the law it implements as «النظام». A reference is
# only counted when that word follows, so that «المادة الثانية من هذه اللائحة»
# -- a self-reference -- is not read as a reference to the law.
#
# The first version of this pattern anchored on «المادة» alone and read the
# singular only. It found 16 of the regulation's 41 articles and missed five,
# for three reasons that are the same three paper 8 documented in the
# judgments: Arabic attaches prefixes to the word (للمادة, بالمادة); the dual
# and the plural are different words (المادتان, المادتين, المواد); and a
# reference may carry a coordinated list of ordinals in parentheses. Each
# omission was silent, because every reference the pattern did reach still
# resolved.
HEAD = re.compile(r"(?:لل|بال|ال)(?:مادة|مادتان|مادتين|مواد)\s*"
                  r"(?P<body>(?:\([^)]{1,60}\)|[^()\n]){1,160}?)"
                  r"من\s+النظام")
ORDINAL = re.compile(r"\(([^)]{1,60})\)")


def records(path):
    return json.loads(path.read_text(encoding="utf-8"))["records"]


def chapter(rec):
    return (rec.get("section_ar") or "—").split("—")[0].strip()


def main():
    law, reg = records(LAW), records(REG)
    chapters = collections.OrderedDict()
    for r in law:
        chapters.setdefault(chapter(r), []).append(r["article_number"])

    elaborated = collections.Counter()
    unparsed = []
    per_reg = {}
    for r in reg:
        targets = []
        for m in HEAD.finditer(r.get("article_text_ar", "")):
            body = m.group("body")
            # A reference may name several articles: «المواد (الثانية
            # والأربعون) و(العاشرة بعد المائة) و(الحادية عشرة بعد المائة)».
            raws = ORDINAL.findall(body) or [body]
            for raw in raws:
                n, _ = arabic_ordinals.parse(raw.strip())
                if n is None:
                    unparsed.append(raw.strip())
                else:
                    targets.append(n)
                    elaborated[n] += 1
        per_reg[r["article_number"]] = sorted(set(targets))

    covered = set(elaborated)
    out = {
        "lawArticles": len(law),
        "regulationArticles": len(reg),
        "regulationArticlesCiting": sum(1 for v in per_reg.values() if v),
        "distinctLawArticlesElaborated": len(covered),
        "shareElaborated": round(100 * len(covered) / len(law), 1),
        "unparsedReferences": unparsed,
        "byChapter": [
            {
                "chapter": name,
                "articles": len(nums),
                "elaborated": sum(1 for n in nums if n in covered),
                "share": round(100 * sum(1 for n in nums if n in covered)
                               / len(nums), 1),
            }
            for name, nums in chapters.items()
        ],
        "mostElaborated": [
            {"article": n, "timesCited": c} for n, c in elaborated.most_common(10)
        ],
        "regulationToLaw": per_reg,
    }
    (Path(__file__).parent / "elaboration_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"law {out['lawArticles']} articles · regulation "
          f"{out['regulationArticles']} articles, "
          f"{out['regulationArticlesCiting']} of them naming a law article")
    print(f"distinct law articles elaborated: "
          f"{out['distinctLawArticlesElaborated']} "
          f"({out['shareElaborated']} per cent)\n")
    print(f"{'chapter':<44}{'arts':>5}{'elab':>6}{'share':>8}")
    for c in out["byChapter"]:
        print(f"{c['chapter']:<44}{c['articles']:>5}{c['elaborated']:>6}"
              f"{c['share']:>7}%")
    if unparsed:
        print("\nunparsed:", unparsed)


if __name__ == "__main__":
    main()
