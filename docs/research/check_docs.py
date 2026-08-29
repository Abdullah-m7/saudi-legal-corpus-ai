#!/usr/bin/env python3
"""Refuse to let the notes drift from the analysis they describe.

The manuscript cannot carry a stale number: it is typeset from generated
macros and check_numbers.py refuses a hand-typed one. The Arabic notes in
this repository had no such guard, and they drifted twice — once when the
matcher was corrected, and again when the citation pattern was found to be
missing 15.7 per cent of everything.

So the same discipline, one level down. Every headline figure in the notes is
declared here with its source, rendered the way Arabic prose writes it, and
checked against the file. The script does not rewrite prose — a number in a
sentence often needs the sentence changed too — it says which figure moved,
what it now is, and where.

    python3 check_docs.py
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NUMBERS = HERE / "applied_law_paper" / "numbers.tex"
APPEAL = HERE / "appeal_paper" / "numbers.tex"
DEFS = HERE / "definitions_paper" / "numbers.tex"
CITATOR = HERE / "citator" / "index.json"

EASTERN = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def ar_int(n):
    return f"{int(n):,}".replace(",", "٬").translate(EASTERN)


def ar_dec(x):
    return f"{float(x):.1f}".replace(".", "٫").translate(EASTERN)


def macros(*paths):
    """Every value the manuscripts use, as plain numbers."""
    out = {}
    for path in (paths or (NUMBERS, APPEAL, DEFS)):
        text = path.read_text(encoding="utf-8")
        for name, raw in re.findall(
                r"\\newcommand\{\\(\w+)\}\{([^{}]*(?:\{,\}[^{}]*)*)\}", text):
            out[name] = raw.replace("{,}", "").lstrip(".") or raw
    return out


def article(track, num, field):
    d = json.loads((HERE / "citator" / "articles" / track /
                    f"{num}.json").read_text(encoding="utf-8"))
    return d[field] if field in d else d["by_voice"].get(field, 0)


def facts():
    m = macros()
    cit = json.loads(CITATOR.read_text(encoding="utf-8"))
    C = "citator/README.md"
    K = "arabic_paper/applied_law_concept.md"
    # A paper's own README is the first thing a reader opens and the last
    # thing anyone re-runs. This one drifted through two corrections while
    # every guard passed, because no guard was pointed at it.
    P = "applied_law_paper/README.md"
    # The citation file is the repository's front door: it is what a citing
    # researcher reads and what a stranger quotes. It carried a citator total
    # from before the citation pattern was corrected -- 99,158 against the
    # 113,052 the citator actually holds -- and that stale figure reached a
    # message sent to a practitioner before anyone noticed. Guarded now.
    F = "../../CITATION.cff"
    # The decision map answers «who could act on this, and what decision would
    # it change» for each finding. It is the one document in the repository a
    # non-researcher is most likely to read on its own, so its figures are
    # guarded like everything else.
    D = "decision_map.md"
    return [
        (C, "مدخلات الكشّاف", ar_int(cit["entries"])),
        (C, "أدوات نظامية", ar_int(cit["instruments"])),
        (C, "مواد متمايزة", ar_int(cit["articles"])),
        (C, "مواد بنصّ رسمي", ar_int(cit["with_official_text"])),
        (C, "استشهادات المادة ٩٠",
         ar_int(article("commercial_courts_implementing_regulation", 90,
                        "citations"))),
        (C, "وقائع المادة ٩٠",
         ar_int(article("commercial_courts_implementing_regulation", 90,
                        "recital"))),
        (C, "تعليل المادة ٩٠",
         ar_int(article("commercial_courts_implementing_regulation", 90,
                        "reasoning"))),
        (C, "المادة ٩٠ بفاعل الدائرة",
         ar_int(article("commercial_courts_implementing_regulation", 90,
                        "recital_by_court"))),
        (C, "استشهادات المادة ١٦",
         ar_int(article("commercial_courts_law", 16, "citations"))),
        (K, "الاستشهادات المستخرجة", ar_int(m["nCitations"])),
        (K, "أدوات مستشهَد بها", ar_int(m["nInstrumentsCited"])),
        (K, "أدوات لم تُستشهد", ar_int(m["nInstrumentsNever"])),
        (K, "الحصة الإجرائية", ar_dec(m["nProceduralShare"])),
        (K, "مواد مستشهَد بها", ar_int(m["nArticlesCited"])),
        (K, "حصة المواد", ar_dec(m["nArticlesCitedShare"])),
        (K, "أكثر مادة استشهادًا", ar_int(m["nTopArticleCitations"])),
        (K, "استشهادات التعليل", ar_int(m["nReasoningCitations"])),
        (K, "إجرائية التعليل", ar_dec(m["nReasoningProcedural"])),
        (K, "إجرائية الوقائع", ar_dec(m["nRecitalProcedural"])),
        (K, "الوقائع بفاعل الدائرة", ar_dec(m["nRecitalByCourtShare"])),

        (P, "مواد نظام المحاكم التجارية", ar_int(m["nCCLArticles"])),
        (P, "حصة نظام المحاكم التجارية", ar_dec(m["nCCLShare"])),
        (P, "مواد نظام المعاملات المدنية", ar_int(m["nCivilArticles"])),
        (P, "حصة نظام المعاملات المدنية", ar_dec(m["nCivilShare"])),
        (P, "الاستشهادات المستخرجة", ar_int(m["nCitations"])),
        (P, "غير المطابَقة", ar_dec(m["nUnmatchedShare"])),
        (P, "مواد مستشهَد بها", ar_int(m["nArticlesCited"])),
        (P, "حصة المواد", ar_dec(m["nArticlesCitedShare"])),
        (P, "داخل النطاق الضيّق", ar_dec(m["nScopeNarrowShare"])),
        (P, "أدوات لم تُستشهد", ar_int(m["nInstrumentsNever"])),
        (P, "الحصة الإجرائية", ar_dec(m["nProceduralShare"])),
        (P, "أكثر مادة استشهادًا", ar_int(m["nTopArticleCitations"])),
        (P, "إجرائية التعليل", ar_dec(m["nReasoningProcedural"])),
        (P, "إجرائية الوقائع", ar_dec(m["nRecitalProcedural"])),
        (P, "الوقائع بفاعل الدائرة", ar_dec(m["nRecitalByCourtShare"])),
        (P, "إجرائية ما فاعله الدائرة", ar_dec(m["nRecitalCourtProcedural"])),
        (P, "إجرائية صوت الخصوم", ar_dec(m["nRecitalOtherProcedural"])),

        # CITATION.cff writes its figures in Western digits
        (F, "مواد الذخيرة التشريعية", f"{int(m['nRegistryArticles']):,}"),
        (F, "أدوات", f"{int(m['nInstruments']):,}"),
        (F, "أحكام", f"{int(m['nJudgments']):,}"),
        (F, "أحكام تحمل استئنافًا", f"{int(m['nAppeals']):,}"),
        (F, "مدخلات الكشّاف", f"{int(cit['entries']):,}"),
        (F, "أدوات الكشّاف", f"{int(cit['instruments']):,}"),
        (F, "مواد الكشّاف", f"{int(cit['articles']):,}"),

        (D, "قرارات الاستئناف", ar_int(m["nAppeals"])),
        (D, "بلا أسباب خاصة", ar_dec(m["nNoReasonsShare"])),
        (D, "تكتب حين تؤيّد", ar_dec(m["nWroteAffirming"])),
        (D, "تكتب حين تنقض", ar_dec(m["nWroteReversing"])),
        (D, "حصة نظام المحاكم التجارية", ar_dec(m["nCCLShare"])),
        (D, "حصة نظام المعاملات المدنية", ar_dec(m["nCivilShare"])),
        (D, "أحكام النموذج", ar_int(m["nModelN"])),
        (D, "نسبة أرجحية الإجرائي", ar_dec(m["nOrProcedural"])),
        (D, "ألفاظ معرَّفة", ar_int(m["nTerms"])),
        (D, "أدوات", ar_int(m["nInstruments"])),
        (D, "حصة المختلف صياغةً", ar_dec(m["nDivergentShare"])),
        (D, "ألفاظ مشتركة موضوعية", ar_int(m["nSharedSubstantive"])),
        (D, "مقروءة باليد", ar_int(m["nReviewed"])),
        (D, "متعارضة", ar_int(m["nConflicting"])),
        (D, "مدخلات الكشّاف", ar_int(cit["entries"])),
    ]


def main():
    bad = []
    for path, label, value in facts():
        text = (HERE / path).read_text(encoding="utf-8")
        if value not in text:
            bad.append((path, label, value))
    if bad:
        print(f"{len(bad)} figure(s) in the notes no longer match the "
              f"analysis:\n")
        for path, label, value in bad:
            print(f"  {path}\n    {label}: should read {value}")
        print("\nFix the sentence, not only the number.")
        return 1
    print(f"all {len(facts())} guarded figures match the analysis")
    return 0


if __name__ == "__main__":
    sys.exit(main())
