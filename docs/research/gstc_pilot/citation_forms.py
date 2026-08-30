#!/usr/bin/env python3
"""Census of the citation forms the published pattern cannot see.

Reading 32 whole judgments (MOJ_ARTICLE_GOLD.md) turned up seven ways a
Saudi judgment names an article that `V.CITE` never matches. Each was found
by hand, once; this counts all of them over all 50,666 judgments, so that the
write-up quotes a census rather than an impression.

`V.CITE` is:

    ماد[ةه] \\s*\\(? (article) \\)? \\s* من \\s+ (نظام|لائحة|النظام|اللائحة …)

so the instrument word must stand immediately after «من», the head noun must
be «مادة» singular and undecorated, and the paragraph must not come after the
instrument. Each form below breaks one of those.

Nothing here changes the parser. It is a measurement.

    python3 citation_forms.py
"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from moj_splits import judgments                  # noqa: E402
import voice_attribution as V                     # noqa: E402

OUT = HERE / "citation_forms_results.json"

D = "0-9٠-٩۰-۹"
TR = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
HEAD = (r"(?<![ء-ي])(?:ال|لل|بال|كال|فال|وال|ول|بل|ب|ل|و)?ماد[ةه]")
INSTR = r"(?:نظام|لائحة|النظام|اللائحة)"

# 1. a modifier between «من» and the instrument word
ANAPH = re.compile(HEAD + r"\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+"
                   r"((?:ذات|هذا|هذه|نفس|ذلك|تلك)\s+(?:ال)?(?:نظام|لائحة|لائحه))")
# 2. a possessive suffix on the instrument word; ة becomes ت before it
SUFFIX = re.compile(HEAD + r"\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+"
                    r"((?:ال)?(?:نظام|لائحت|لائحه)(?:ها|هما|هم|ه)(?:\s|$))")
# 3. the paragraph placed after the article and before the instrument
POSTFIX = re.compile(HEAD + rf"\s*\(?\s*([{D}]{{1,3}})\s*\)?\s*"
                     rf"(?:فقرة|الفقرة)\s*\(?\s*([{D}أ-ي]{{1,3}})\s*\)?\s*من\s+"
                     + INSTR)
# 4. articles under the plural head noun
PLURAL = re.compile(r"(?<![ء-ي])(?:ال|لل|بال|كال|فال|وال|ول|بل|ب|ل|و)?مواد"
                    rf"\s*\(?\s*([{D}][{D}\s,،\-/و]{{0,60}}?)\s*\)?\s*من\s+"
                    + INSTR)
# 5/6/7. a bracketed number cited straight to an instrument, with no head noun
BARE = re.compile(rf"\(\s*(?:[{D}]{{1,3}}\s*/\s*[{D}]{{1,3}}|[{D}]{{1,3}})\s*\)"
                  r"\s*من\s+" + INSTR)
IMMED = re.compile(r"(?:ماد[ةه]|مواد|مادتي?ن|رقم|فقرة|بند|الصك|القضية|المرسوم|"
                   r"القرار|التعميم|الأمر|حكم|الحكم|صك)\s*$")
ANYHEAD = re.compile(r"ماد[ةه]|مواد|مادتي?ن")
MARKS = re.compile(r"[ً-ْٰ]")
TRUNC = re.compile(r"الماد\s*$")
PACK = re.compile(rf"^\s*([{D}]{{1,3}})\s*/\s*([{D}]{{1,3}})\s*$")
LETPACK = re.compile(rf"^\s*(?:[{D}]{{1,3}}\s*/\s*[أ-ي]|[أ-ي]\s*/\s*[{D}]{{1,3}})\s*$")
NUM = re.compile(rf"[{D}]{{1,3}}")


def norm(s):
    return str(int(s.translate(TR)))


def main():
    c = collections.Counter()
    docs = 0
    for rec in judgments():
        raw = rec.get("text") or ""
        if not raw:
            continue
        docs += 1
        t = raw.replace("ـ", "")          # canonicalisation strips tatweel
        seen = {m.start() for m in V.CITE.finditer(t)}

        for m in ANAPH.finditer(t):
            c["anaphoricSites"] += 1
            if m.start() not in seen:
                c["anaphoricMissed"] += 1
        for m in SUFFIX.finditer(t):
            c["suffixSites"] += 1
            if m.start() not in seen:
                c["suffixMissed"] += 1
        for m in POSTFIX.finditer(t):
            c["postfixSites"] += 1
            if m.start() not in seen:
                c["postfixMissed"] += 1

        singles = {norm(n) for mm in V.CITE.finditer(t)
                   for n in NUM.findall(mm.group(1))}
        for m in PLURAL.finditer(t):
            nums = {norm(n) for n in NUM.findall(m.group(1))}
            c["pluralSites"] += 1
            c["pluralArticles"] += len(nums)
            c["pluralArticlesUnseen"] += len(nums - singles)

        for m in BARE.finditer(t):
            before = t[max(0, m.start() - 60):m.start()]
            if IMMED.search(before):
                continue
            if ANYHEAD.search(before):
                c["listContinuation"] += 1
                continue
            stripped = MARKS.sub("", before)
            if IMMED.search(stripped) or ANYHEAD.search(stripped):
                c["headNounDiacritics"] += 1
            elif TRUNC.search(before.rstrip()) or TRUNC.search(stripped.rstrip()):
                c["headNounTruncated"] += 1
            else:
                c["headless"] += 1

        for art, _ in V.CITE.findall(t):
            if LETPACK.match(art):
                c["packedWithLetter"] += 1
                continue
            p = PACK.match(art)
            if not p:
                continue
            c["packed"] += 1
            a, b = int(p.group(1).translate(TR)), int(p.group(2).translate(TR))
            if a > b:
                c["packedArticleFirst"] += 1
            elif b > a:
                c["packedParagraphFirst"] += 1
            else:
                c["packedEqual"] += 1
            if 2 <= a <= 30 and 2 <= b <= 30:
                c["packedAmbiguous"] += 1

    rows = [
        ("«المادة N من ذات/هذا النظام» (modifier before the instrument)",
         c["anaphoricSites"], c["anaphoricMissed"]),
        ("«المادة N من لائحته التنفيذية» (possessive suffix)",
         c["suffixSites"], c["suffixMissed"]),
        ("«المادة (N) فقرة (M) من …» (paragraph after the article)",
         c["postfixSites"], c["postfixMissed"]),
        ("later members of an enumerated list, «(51) و (56) و …»",
         c["listContinuation"], c["listContinuation"]),
        ("head noun carrying Arabic diacritics, «المادَّة»",
         c["headNounDiacritics"], c["headNounDiacritics"]),
        ("head noun truncated to «الماد»",
         c["headNounTruncated"], c["headNounTruncated"]),
        ("bracketed number with no head noun, «(1/29) من نظام الإثبات»",
         c["headless"], c["headless"]),
    ]
    print(f"{docs:,} judgments\n")
    print(f"{'form':<62}{'sites':>8}{'missed':>9}")
    for label, sites, missed in rows:
        print(f"{label:<62}{sites:>8,}{missed:>9,}")
    print(f"\narticles under the plural head noun «المواد»:")
    print(f"  sites {c['pluralSites']:,}   distinct numbers "
          f"{c['pluralArticles']:,}   never named singly in the same judgment "
          f"{c['pluralArticlesUnseen']:,}")

    p = c["packed"]
    print(f"\npacked «a/b» citation bodies                      {p:,}")
    print(f"  article first  {c['packedArticleFirst']:,}"
          f"   paragraph first {c['packedParagraphFirst']:,}"
          f"   equal {c['packedEqual']:,}")
    print(f"  both numbers in 2..30, both readings plausible  "
          f"{c['packedAmbiguous']:,}  ({c['packedAmbiguous']/p*100:.1f}%)")
    print(f"  packed with an Arabic letter (unambiguous)      "
          f"{c['packedWithLetter']:,}")

    OUT.write_text(json.dumps({"judgments": docs, **dict(c)},
                              ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
