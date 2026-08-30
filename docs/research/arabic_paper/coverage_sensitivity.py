#!/usr/bin/env python3
"""How much do the citation forms V.CITE cannot see move the published claims?

MOJ_ARTICLE_GOLD.md, reading 32 whole judgments, found seven forms the
published pattern never matches, and citation_forms.py counted them across
the corpus. The question this answers is the only one that matters for the
papers: if those citations were counted, would the uptake and concentration
figures move enough to change a claim?

This is a SENSITIVITY BOUND, not a new extractor and not a replacement
figure. The published numbers stand unchanged beside it. Two readings are
computed for every quantity:

  PUBLISHED   exactly what uptake_by_voice.py counts today, reproduced here
              so the two columns are computed by one pass over one corpus
  BOUND       the same, plus every citation the extended pattern recovers

The bound is deliberately permissive: it resolves an anaphoric instrument to
the last one named of the same kind, accepts a possessive suffix, a paragraph
placed after the article, a head noun carrying diacritics, the later members
of an enumerated list, and a bracketed number cited straight to an
instrument. It will therefore recover some things that are not citations. It
is an upper bound on the movement, and the interesting result is if the
movement is small even so.

    python3 coverage_sensitivity.py [--json]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))
import arabic_ordinals as A            # noqa: E402
import match_instruments as M          # noqa: E402
import voice_attribution as V          # noqa: E402

D = "0-9٠-٩۰-۹"
MARKS = re.compile(r"[ً-ْٰ]")
HEAD = r"(?<![ء-ي])(?:ال|لل|بال|كال|فال|وال|ول|بل|ب|ل|و)?ماد[ةه]"
INSTR = r"(?:نظام|لائحة|النظام|اللائحة)"

# every form the gold found, as one alternation over the same anchor. Group 1
# is always the article, group 2 the instrument as written.
EXTENDED = re.compile(
    # «المادة N من ذات/هذا النظام» and «من لائحته التنفيذية»
    HEAD + r"\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+"
    r"((?:ذات|هذا|هذه|نفس|ذلك|تلك)\s+(?:ال)?(?:نظام|لائحة|لائحه)[^\.،؛\n\)]{0,40}"
    r"|(?:ال)?(?:نظام|لائحت|لائحه)(?:ها|هما|هم|ه)[^\.،؛\n\)]{0,40})"
    r"|"
    # «المادة (N) فقرة (M) من <instrument>»
    + HEAD + rf"\s*\(?\s*([{D}]{{1,3}})\s*\)?\s*(?:فقرة|الفقرة)\s*\(?\s*"
    rf"[{D}أ-ي]{{1,3}}\s*\)?\s*من\s+({INSTR}[^\.،؛\n\)]{{0,60}})"
    r"|"
    # a bracketed number cited straight to an instrument, head noun absent,
    # truncated, diacriticised, or governing an earlier member of a list
    rf"\(\s*([{D}]{{1,3}}(?:\s*/\s*[{D}]{{1,3}})?)\s*\)\s*من\s+"
    rf"({INSTR}[^\.،؛\n\)]{{0,60}})"
    r"|"
    # articles under the plural head noun
    r"(?<![ء-ي])(?:ال|لل|بال|كال|فال|وال|ول|بل|ب|ل|و)?مواد"
    rf"\s*\(?\s*([{D}][{D}\s,،\-/و]{{0,60}}?)\s*\)?\s*من\s+"
    rf"({INSTR}[^\.،؛\n\)]{{0,60}})")
NUM = re.compile(rf"[{D}]{{1,3}}")
TR = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
# a bracketed number that is a decree, circular, case or record number, not an
# article, judged by the word standing before it
NOT_ARTICLE = re.compile(r"(?:رقم|الصك|القضية|المرسوم|القرار|التعميم|الأمر|صك)"
                         r"\s*$")


def pairs(m):
    """(article string, instrument string) from whichever branch matched."""
    for a, b in ((1, 2), (3, 4), (5, 6), (7, 8)):
        if m.group(a) is not None:
            return m.group(a), m.group(b)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    index, order = M.build(REGISTRY)
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    size = {}
    for t in tracks:
        rc = t.get("record_counts") or {}
        v = rc.get("arabic_articles") or rc.get("total")
        if isinstance(v, int) and v > 0:
            size[t["track_id"]] = v

    cites = {k: collections.Counter() for k in ("PUBLISHED", "BOUND")}
    arts = {k: collections.defaultdict(set) for k in ("PUBLISHED", "BOUND")}
    recovered = 0
    n = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            text = r["text"]
            # tatweel is stripped by canonicalisation; diacritics are not, and
            # the gold found 234 citations lost to a shadda. The extended pass
            # reads the stripped text, the published pass reads the text as
            # published, so that PUBLISHED reproduces the figure in UPTAKE.md
            # exactly rather than a slightly improved version of it.
            plain = MARKS.sub("", text.replace("ـ", ""))

            last = M.Recent()
            for m in V.CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                num, _ = A.parse(m.group(1))
                if num is not None and tid in size and num > size[tid]:
                    num = None
                for col in ("PUBLISHED", "BOUND"):
                    cites[col][tid] += 1
                    if num is not None:
                        arts[col][tid].add(num)

            # offsets in `plain` are not offsets in `text`, so the published
            # pattern is re-run over `plain` purely to know which positions the
            # extended pass must not double-count.
            probe = M.Recent()
            seen = set()
            for m in V.CITE.finditer(plain):
                tid, kind = M.match(m.group(2), index, order, probe)
                if kind == "named":
                    probe.note(tid)
                seen.add(m.start())

            # second pass, extended, over the same judgment. `last` is rebuilt
            # so anaphora resolves against what the extended pass itself has
            # named, which is what an extractor doing this would do.
            last = M.Recent()
            for m in EXTENDED.finditer(plain):
                art, raw = pairs(m)
                if art is None:
                    continue
                if NOT_ARTICLE.search(plain[max(0, m.start() - 24):m.start()]):
                    continue
                tid, kind = M.match(raw, index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid or m.start() in seen:
                    continue
                nums = [A.parse(art)[0]] if not NUM.search(art) else [
                    int(x.translate(TR)) for x in NUM.findall(art)]
                got = False
                for num in nums:
                    if num is None or (tid in size and num > size[tid]):
                        continue
                    arts["BOUND"][tid].add(num)
                    got = True
                cites["BOUND"][tid] += 1
                recovered += 1 if got else 0

    universe = sum(size.values())
    out = {"judgments": n, "citationsRecoveredByTheBound": recovered,
           "readings": {}}
    for col in ("PUBLISHED", "BOUND"):
        c = cites[col]
        tot = sum(c.values())
        proc = sum(v for k, v in c.items() if k in M.PROCEDURAL)
        distinct = sum(len(v) for v in arts[col].values())
        top10 = sum(v for _, v in c.most_common(10))
        out["readings"][col] = {
            "citations": tot,
            "instrumentsCited": len(c),
            "proceduralShare": round(100 * proc / tot, 1) if tot else 0.0,
            "top10Share": round(100 * top10 / tot, 1) if tot else 0.0,
            "distinctArticles": distinct,
            "articleCoverageOfStatuteBook": round(100 * distinct / universe, 2),
        }

    (HERE / "coverage_sensitivity_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    p, b = out["readings"]["PUBLISHED"], out["readings"]["BOUND"]
    print(f"{n:,} judgments; the bound recovers {recovered:,} citations "
          f"the published pattern does not match\n")
    print(f"{'':<38}{'PUBLISHED':>14}{'BOUND':>14}{'move':>10}")
    for label, key, fmt in [
            ("citations", "citations", "{:,}"),
            ("instruments ever cited", "instrumentsCited", "{:,}"),
            ("procedural share of citations, %", "proceduralShare", "{:.1f}"),
            ("top-10 instruments' share, %", "top10Share", "{:.1f}"),
            ("distinct articles ever cited", "distinctArticles", "{:,}"),
            ("share of the statute book, %",
             "articleCoverageOfStatuteBook", "{:.2f}")]:
        d = b[key] - p[key]
        print(f"  {label:<36}{fmt.format(p[key]):>14}{fmt.format(b[key]):>14}"
              f"{d:>+10.2f}")
    print("\nThe published figures are unchanged and are not replaced. This is"
          "\nan upper bound on how far they could move, computed with a"
          "\ndeliberately permissive pattern.")


if __name__ == "__main__":
    main()
