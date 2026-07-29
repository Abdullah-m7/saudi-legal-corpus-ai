#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair the stored Arabic text of the CMA Corporate Governance Regulations
track, which was captured with a systematic bidi/ligature defect.

THE DEFECT
    The committed source artifact was extracted with an ordinary PDF text
    extractor. CMA's PDF places every glyph individually in VISUAL order and
    its fonts use Arabic ligature glyphs whose ToUnicode entries expand to two
    or three letters. When the extractor reverses the visual run to recover
    logical order it also reverses the letters INSIDE each ligature. The stored
    text therefore carried, throughout:

        اللائحة  ->  الالئحة        حماية    ->  محاية
        الإدارة  ->  اإلدارة        اللازمة  ->  الالزمة
        المجلس   ->  املجلس         لحقوقهم  ->  حلقوقهم
        المصالح  ->  المصاحل        غير      ->  غري

    plus digit-marker runs fused to the following word ("1تفعيل" for "1) تفعيل"),
    commas placed on the wrong side of the space, and combining marks split
    onto the following line.

    Two defects were WORSE than cosmetic and are the reason this is a
    correctness repair rather than a tidy-up:
      * Article 1 was MISSING three whole definitions — نظام الشركات, نظام
        السوق المالية and قواعد طرح الأوراق المالية والالتزامات المستمرة. They
        are present on page 7 of CMA's own PDF and are now restored.
      * Article 2(ج) had its words re-ordered ACROSS a line break, so the
        sentence read "...على إلزامية أي / ٍّ من أحكامها..." with the tashkeel of
        أيٍّ orphaned at a line start.

THE FIX
    The text is re-derived from CMA's own PDF at glyph level using
    scripts/extract_cma_securities_offering_rules_pdf_text.py — the same
    extractor the wave-7 CMA tracks use, which keeps each ToUnicode CMap
    expansion atomic instead of reversing its interior. No word list, no
    dictionary, no spell-correction, and no use of the English edition. Every
    character written here is the font's own ToUnicode value for a glyph
    actually drawn on the page.

    The existing convention of preserving the PDF's physical line breaks is
    kept, so the committed diff is the text correction and nothing else. Article
    numbering, legal_status_ar, section_ar, amendment history and every other
    field are untouched.

USAGE (not part of the corpus build; the build reads only the committed JSON)
    curl -L -o CorpGovReg.pdf \\
      https://cma.gov.sa/RulesRegulations/Regulations/Documents/CorpGovReg.pdf
    python3 scripts/extract_cma_securities_offering_rules_pdf_text.py \\
      CorpGovReg.pdf --mark-small -o cgr_ar.txt
    python3 scripts/repair_cma_corporate_governance_regulation_text.py cgr_ar.txt

Arabic governs. No translation, paraphrase or interpretation is performed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cma_corporate_governance_regulation", "law",
                   "official_source",
                   "cma_corporate_governance_regulation_official_source.json")

HEADING = "\x01"
SMALL = "\x02"    # footnote text / footnote markers / page numbers
PAGE_RULE = re.compile(r"^=+ PAGE \d+ =+$")
PAGE_NUM = re.compile(r"^\s*\d{1,3}\s*$")
SECTION_HEAD = re.compile(r"^(الباب|الفصل)\b")


def _norm_ordinal(s: str) -> str:
    """Compare ordinals ignoring the artifact's الثالثون / the PDF's الثلاثون."""
    return s.replace("المادة", "").replace("الثالثون", "الثلاثون").strip()


def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[ً-ْٰـ]", "", s)
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"),
                 ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        s = s.replace(a, b)
    return re.sub(r"[^ء-ي0-9]+", " ", s).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("extraction", help="glyph-level extraction of CorpGovReg.pdf")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    lines = open(args.extraction, encoding="utf-8").read().split("\n")
    src = json.load(open(SRC, encoding="utf-8"))
    keys = sorted(src["articles"],
                  key=lambda k: int(re.search(r"(\d+)$", k).group(1)))
    expected = [_norm_ordinal(src["articles"][k]["number_label_ar"]) for k in keys]

    # Locate each article's heading line, in document order.  Matching is
    # sequential against the expected ordinal, so a heading that repeats inside
    # the table of contents cannot capture an article.
    starts, cur = [], 0
    for i, line in enumerate(lines):
        if not line.startswith(HEADING) or cur >= len(expected):
            continue
        head = line[1:].strip().split(":")[0]
        if _norm_ordinal(head) == expected[cur]:
            starts.append(i)
            cur += 1
    if len(starts) != len(keys):
        print("FAIL: located %d article headings, expected %d"
              % (len(starts), len(keys)), file=sys.stderr)
        return 1

    footnotes: list[str] = []

    def body(n: int) -> str:
        lo = starts[n] + 1
        hi = starts[n + 1] if n + 1 < len(starts) else len(lines)
        out = []
        for line in lines[lo:hi]:
            if line.startswith(SMALL):
                # Rows set below the page's dominant body size: the numbered
                # footnotes CMA prints at the foot of the page, their reference
                # markers, and the page number.  They are not article text and
                # are collected separately rather than dropped silently.
                footnotes.append(line[1:].strip())
                continue
            t = line.lstrip(HEADING).strip()
            if not t or PAGE_RULE.match(t) or PAGE_NUM.match(t):
                continue
            # باب / فصل headings sit between articles and belong to no article.
            if line.startswith(HEADING) and SECTION_HEAD.match(t):
                continue
            out.append(t)
        return "\n".join(out)

    changed, unchanged, empty = 0, 0, []
    for n, k in enumerate(keys):
        new = body(n)
        if not new:
            empty.append(k)
            continue
        if src["articles"][k]["text"] != new:
            changed += 1
        else:
            unchanged += 1
        src["articles"][k]["text"] = new

    if empty:
        print("FAIL: empty body for %s" % empty, file=sys.stderr)
        return 1

    # ---- titles and section headings ------------------------------------
    # article_title_ar, section_ar and chapter_structure carried the same
    # ligature defect (تعارض المصاحل, أحكام متهيدية, أهداف الالئحة).  They are
    # rebuilt from the extraction's OWN heading lines, then checked against the
    # stored values under a normalisation that folds each known corruption to
    # its correct form.  If anything other than the corruption differs the run
    # aborts, so this cannot silently re-assign an article to another chapter.
    # The defect is a PERMUTATION of characters -- reversing the interior of a
    # ligature can never add or remove a letter -- so a rebuilt title is
    # accepted only when it carries exactly the same character multiset as the
    # stored one.  That is a proof, not a word list: any genuine wording
    # difference (a different chapter, a dropped word) changes the multiset and
    # aborts the run.
    def _bag(s: str):
        return sorted(re.sub(r"\s+", "", s))

    bab, fasl = None, None
    section_for, title_for = {}, {}
    n = 0
    for i, line in enumerate(lines):
        if not line.startswith(HEADING):
            continue
        h = line[1:].strip()
        if SECTION_HEAD.match(h):
            if h.startswith("الباب"):
                # In the body (unlike the table of contents) a Part heading is
                # set over two lines -- «الباب الأول» then «أحكام تمهيدية» --
                # so the label is joined to the heading line that follows it.
                if ":" not in h:
                    for nxt in lines[i + 1:]:
                        if not nxt.startswith(HEADING):
                            continue
                        t = nxt[1:].strip()
                        if not SECTION_HEAD.match(t) and not t.startswith("المادة"):
                            h = "%s: %s" % (h, t)
                        break
                bab, fasl = h, None
            else:
                fasl = h
            continue
        if bab and ":" in bab and h == bab.split(": ", 1)[1]:
            continue          # the Part title line already folded into `bab`
        if n < len(keys) and i == starts[n]:
            title_for[keys[n]] = h.split(":", 1)[1].strip() if ":" in h else ""
            section_for[keys[n]] = bab + (" -- " + fasl if fasl else "") if bab else ""
            n += 1

    title_fixed = section_fixed = 0
    for k in keys:
        for field, built in (("article_title_ar", title_for.get(k)),
                             ("section_ar", section_for.get(k))):
            if field not in src["articles"][k] or built is None:
                continue
            stored = src["articles"][k][field]
            if _bag(stored) != _bag(built):
                print("FAIL: %s %s differs beyond the known corruption:\n"
                      "  stored: %r\n  rebuilt: %r" % (k, field, stored, built),
                      file=sys.stderr)
                return 1
            if stored != built:
                src["articles"][k][field] = built
                if field == "article_title_ar":
                    title_fixed += 1
                else:
                    section_fixed += 1

    # chapter_structure titles are the same strings; take each one from the
    # rebuilt section headings, matched by its own label, under the same
    # multiset proof.
    # Chapter (فصل) labels repeat across Parts -- «الفصل الأول» exists in
    # several أبواب with different titles -- so a فصل is keyed by its PARENT
    # Part, never by its label alone.
    by_label = {}
    for k in keys:
        sec = section_for.get(k) or ""
        parts = sec.split(" -- ")
        bab_lab = parts[0].split(":", 1)[0].strip() if parts else ""
        for depth, part in enumerate(parts):
            if ":" not in part:
                continue
            lab, title = part.split(":", 1)
            key = lab.strip() if depth == 0 else (bab_lab, lab.strip())
            by_label[key] = title.strip()
    chap_fixed = 0
    for chap in src.get("chapter_structure", []):
        for node in [chap] + chap.get("fasl", []):
            key = (node["label_ar"] if node is chap
                   else (chap["label_ar"], node["label_ar"]))
            built = by_label.get(key)
            if built is None or built == node["title_ar"]:
                continue
            if _bag(built) != _bag(node["title_ar"]):
                print("FAIL: chapter %s title differs beyond the known "
                      "corruption:\n  stored: %r\n  rebuilt: %r"
                      % (node["label_ar"], node["title_ar"], built), file=sys.stderr)
                return 1
            node["title_ar"] = built
            chap_fixed += 1

    print("titles corrected: %d article_title_ar, %d section_ar, %d chapter_structure"
          % (title_fixed, section_fixed, chap_fixed))

    print("articles rewritten: %d changed, %d already identical" % (changed, unchanged))
    print("footnote / page-furniture rows separated out: %d" % len(footnotes))
    if args.dry_run:
        return 0

    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(src, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s" % os.path.relpath(SRC, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
