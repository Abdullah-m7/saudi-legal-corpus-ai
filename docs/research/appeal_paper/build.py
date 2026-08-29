#!/usr/bin/env python3
"""Build the IJCA submission for paper 9.

The International Journal for Court Administration reviews double blind and
wants Microsoft Word: 12 pt Times New Roman, 1.5 line spacing, footnotes in
the same face at 10 pt, and no more than 7,000 words including footnotes.
Requirements read from the journal's own submission page on 29 August 2026.

    python3 build.py

    main.pdf                    the identified typeset copy, for the record
    submission_manuscript.docx  anonymised, in the journal's format
    submission_title_page.docx  the identifying material, separately

The anonymity audit reads the built .docx back rather than trusting the
source, because the .docx is the file that gets uploaded. The repository URL
is the leak that matters: it names the author, and it lives in a footnote
about data availability, which is the last place anyone looks.
"""

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 7000                     # words including footnotes
IDENTITY = ("Almohammedi", "abdullah", "orcid", "0009-0001", "github.com",
            "Abdullah-m7", "zenodo")

TITLE_PAGE = r"""\documentclass[12pt]{article}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{times}\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}
\usepackage[hidelinks]{hyperref}
\pagestyle{empty}
\begin{document}
\begin{center}
{\large\bfseries Measuring Appellate Reason-Giving in Saudi Commercial Courts}

\vspace{1.4em}
Abdullah Almohammedi\footnote{Abdullah Almohammedi is an
independent researcher in Saudi Arabia working on machine-readable corpora of
Saudi legislation and adjudication. He built the corpus this article measures
and the citator that joins its two halves at the level of the article. His
work is published openly, with the code that produces every reported
figure.}\\
Independent Researcher, Kingdom of Saudi Arabia\\
\texttt{abdullah.m.almohammedi@gmail.com}\\
ORCID: 0009-0001-0832-0995
\end{center}

\vspace{1.2em}
\noindent\textbf{Competing interests.} None. This work received no funding,
and the author holds no position in, and no relationship with, the Ministry of
Justice or any court whose judgments it measures.

\vspace{0.8em}
\noindent\textbf{Word count.} __WORDCOUNT__ words including footnotes.
\end{document}
"""


def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"{cmd[0]} failed:\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
    return r


def latex(stem, source=None):
    if source is not None:
        (HERE / f"{stem}.tex").write_text(source, encoding="utf-8")
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{stem}.tex"],
                       cwd=HERE, capture_output=True, text=True)
    if not (HERE / f"{stem}.pdf").exists():
        sys.exit(f"{stem}.tex did not build")


def reference_docx():
    """pandoc ignores \\setspace, so the .docx format comes from a reference
    document. Build one from pandoc's own default and set what IJCA asks for:
    Times New Roman throughout, 1.5 spacing, 12 pt body and 10 pt notes."""
    ref = HERE / "reference.docx"
    run(["pandoc", "-o", ref.name, "--print-default-data-file",
         "reference.docx"])
    with zipfile.ZipFile(ref) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    styles = parts["word/styles.xml"].decode("utf-8")
    # w:line is in twentieths of a point; 360 = 18 pt, one-and-a-half for 12 pt.
    want = {"Normal": ("360", "24"), "BodyText": ("360", "24"),
            "FirstParagraph": ("360", "24"), "FootnoteText": ("360", "20")}
    for style_id, (line, half_points) in want.items():
        m = re.search(r'<w:style [^>]*w:styleId="%s"[^>]*>'
                      r'((?:(?!</w:style>).)*?)</w:style>' % style_id,
                      styles, re.S)
        if not m:
            continue
        block = new = m.group(0)
        new = re.sub(r"<w:spacing[^/]*/>", "", new)
        new = new.replace("<w:pPr>", '<w:pPr><w:spacing w:line="%s" '
                          'w:lineRule="auto" w:after="0"/>' % line, 1)
        if "<w:pPr>" not in block:
            new = new.replace("</w:style>",
                              '<w:pPr><w:spacing w:line="%s" w:lineRule="auto"'
                              ' w:after="0"/></w:pPr></w:style>' % line)
        rpr = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
               'w:cs="Times New Roman"/><w:sz w:val="%s"/>'
               '<w:szCs w:val="%s"/>' % (half_points, half_points))
        new = re.sub(r"<w:rFonts[^/]*/>|<w:sz w:val=\"\d+\"/>|"
                     r"<w:szCs w:val=\"\d+\"/>", "", new)
        if "<w:rPr>" in new:
            new = new.replace("<w:rPr>", "<w:rPr>" + rpr, 1)
        else:
            new = new.replace("</w:style>", "<w:rPr>%s</w:rPr></w:style>" % rpr)
        styles = styles.replace(block, new)
    parts["word/styles.xml"] = styles.encode("utf-8")
    with zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    return ref


# A .docx keeps its footnotes in a separate part. The first version of this
# audit read word/document.xml alone and reported the manuscript clean while
# the repository URL --- which carries the author's GitHub handle --- sat in a
# footnote about data availability. Read every part that can hold text.
TEXT_PARTS = re.compile(r"^word/(document|footnotes|endnotes|comments|"
                        r"header\d*|footer\d*)\.xml$")


# IJCA's limit is 7,000 words *including footnotes*, and this article carries
# its references in footnotes, so counting the body alone both understates the
# manuscript and makes the figure declared on the title page untrue. Count
# what the journal counts.
COUNTED_PARTS = ("word/document.xml", "word/footnotes.xml")


def plain(path, counting=False):
    """The text of a .docx. `counting` returns body and footnotes, which is
    what this journal's word limit means; the audit wants everything."""
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist()
                 if (n in COUNTED_PARTS if counting
                     else TEXT_PARTS.match(n))]
        xml = "\n".join(z.read(n).decode("utf-8", "ignore") for n in names)
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml)


def main():
    if not shutil.which("pandoc"):
        sys.exit("pandoc is required for the .docx build")
    source = (HERE / "main.tex").read_text(encoding="utf-8")
    if "\\anonfalse" not in source:
        sys.exit("REFUSING: main.tex has no \\anonfalse to flip")

    print("identified build (for the record)")
    latex("main")

    print("anonymised manuscript")
    anon = source.replace("\\anonfalse", "\\anontrue")
    (HERE / "main_anon.tex").write_text(anon, encoding="utf-8")
    latex("main_anon")
    ref = reference_docx()
    run(["pandoc", "main_anon.tex", "-o", "submission_manuscript.docx",
         "--reference-doc", ref.name])
    words = len(plain(HERE / "submission_manuscript.docx",
                      counting=True).split())
    print(f"  submission_manuscript.docx: {words} words "
          f"({'within' if words <= LIMIT else 'OVER'} IJCA's {LIMIT:,})")

    print("anonymity audit")
    low = plain(HERE / "submission_manuscript.docx").lower()
    leaks = [w for w in IDENTITY if w.lower() in low]
    if leaks:
        sys.exit(f"REFUSING: the anonymised manuscript names {leaks}")
    print(f"  clean of {len(IDENTITY)} identifying strings")

    print("title page")
    latex("submission_title_page",
          TITLE_PAGE.replace("__WORDCOUNT__", f"{words:,}"))
    run(["pandoc", "submission_title_page.tex", "-o",
         "submission_title_page.docx", "--reference-doc", ref.name])

    for junk in ("main_anon.tex", "main_anon.pdf", "submission_title_page.tex",
                 "reference.docx"):
        f = HERE / junk
        if f.exists():
            f.unlink()
    for pattern in ("*.aux", "*.log", "*.out"):
        for f in HERE.glob(pattern):
            if f.stem != "main":
                f.unlink()
    print("done")


if __name__ == "__main__":
    main()
