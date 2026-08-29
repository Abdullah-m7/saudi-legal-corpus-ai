#!/usr/bin/env python3
"""Build the submission files for this article.

Written first for Statute Law Review, which desk-rejected it, and kept intact
because the anonymised Word build is what a peer-reviewed journal will want if
the law reviews decline. **US law reviews are not anonymous**: for the Notre
Dame Journal of Legislation and its peers the file to upload is the identified
`main.pdf`, with the CV and the cover letter beside it. Nothing here needs to
change for that; the anonymised copy is simply not used.

`main.tex` is the single source. It carries an \\ifanon switch that pdfLaTeX
honours, but pandoc --- which produces the .docx --- does not evaluate TeX
conditionals: it silently keeps the identifying material while dropping
\\maketitle. Both failures are invisible in the output and one of them would
de-anonymise a double-anonymous submission, so this script resolves the
conditionals itself before either tool sees the file, and audits the result.

Outputs:

    main.pdf / main_identified.pdf   identified build, for the record
    main_anon.pdf                    anonymised build, to read before upload
    submission_manuscript.docx       UPLOAD: anonymised, double-spaced
    submission_title_page.docx       UPLOAD: identity and declarations
    fig1_funnel.eps, fig2_adjudication.eps
                                     UPLOAD: figures, from make_figures.py

Run from this directory:

    python3 build.py
"""

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "main.tex"

TITLE = r"""\begin{center}
{\Large\bfseries How Much Do Statutes Disagree?\\[2pt]
Measuring Definitional Fragmentation Across a Legal System\par}
\end{center}
"""

BYLINE = r"""\begin{center}
Abdullah Almohammedi\\
Independent Researcher\\
\texttt{abdullah.m.almohammedi@gmail.com}\\
ORCID: 0009-0001-0832-0995
\end{center}
"""

TITLE_PAGE = r"""\documentclass[11pt]{article}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{times}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{setspace}
\doublespacing
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\usepackage{url}
\emergencystretch=4em
\sloppy
\input{numbers}
\begin{document}
""" + TITLE + r"""
\vspace{1em}
""" + BYLINE + r"""
\vspace{1.5em}

\subsection*{Abstract}

__ABSTRACT__

\subsection*{Keywords}

__KEYWORDS__

\subsection*{Word count}

__WORDCOUNT__ words, including footnotes.

\subsection*{Funding}

No funding was received for conducting this study.

\subsection*{Conflict of interest}

The author declares no conflict of interest.

\subsection*{Ethics approval}

Not applicable. The study involves no human participants, no animal subjects
and no personal data. It analyses published national legislation only.

\subsection*{Acknowledgements}

None.

\subsection*{Data availability}

The corpus, its glossary layer, and the analysis and figure scripts that
reproduce every number and figure reported in the article are openly
available at \url{https://github.com/Abdullah-m7/saudi-legal-corpus-ai} and
archived on Zenodo under the MIT licence
(\href{https://doi.org/10.5281/zenodo.22019183}{10.5281/zenodo.22019183};
concept DOI
\href{https://doi.org/10.5281/zenodo.22019182}{10.5281/zenodo.22019182}).

\subsection*{Related work by the author}

Two companion manuscripts drawing on the same corpus are under review
elsewhere: one describing the corpus as a resource, and one analysing its
citation network. Neither overlaps with the present article's contribution,
and neither is under consideration by this journal.

\subsection*{Legal status of the sources}

The article analyses a non-official research corpus. Nothing in it
constitutes legal advice, and the binding text of any instrument is the
Arabic original published in \emph{Umm al-Qura}. Instrument identifiers are
given as recorded in the corpus registry.

\end{document}
"""

# A whole figure environment becomes a one-cell Word table if it is left
# intact, so the docx build replaces each one with ordinary paragraphs.
FIGURE_ENV = re.compile(
    r"\\begin\{figure\}(?:\[[^\]]*\])?\s*"
    r"\\centering\s*"
    r"\\includegraphics\[[^\]]*\]\{fig(\d)_([a-z]+)\.png\}\s*"
    r"\\caption\{(.*?)\}\s*"
    r"(?:\\label\{[^}]*\}\s*)?"
    r"\\end\{figure\}",
    re.S)


def figure_paragraphs(m):
    n, name, caption = m.group(1), m.group(2), m.group(3)
    stem = f"fig{n}_{name}".replace("_", r"\_")
    return (f"\\bigskip\n\\noindent\\textit{{[Figure {n} near here --- supplied "
            f"as a separate file, {stem}.eps]}}\n\n"
            f"\\noindent\\textbf{{Figure {n}.}} {caption}\n\\bigskip\n")


def resolve_conditionals(text, anon):
    """Evaluate every \\ifanon ... [\\else ...] \\fi region.

    Written as a scanner rather than a regex because \\ifanon\\else and
    \\ifanon <block> \\else are both used in the source, and a non-greedy
    regex over the whole file pairs the wrong \\fi with the wrong \\ifanon.
    """
    out, i = [], 0
    while True:
        start = text.find(r"\ifanon", i)
        if start == -1:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:start])
        depth, j = 1, start + len(r"\ifanon")
        else_at = None
        while depth:
            m = re.compile(r"\\(ifanon|else|fi)").search(text, j)
            if m is None:
                raise SystemExit(r"unterminated \ifanon")
            tok, j = m.group(1), m.end()
            if tok == "ifanon":
                depth += 1
            elif tok == "fi":
                depth -= 1
                if depth == 0:
                    end_start, end_stop = m.start(), m.end()
            elif tok == "else" and depth == 1:
                else_at = (m.start(), m.end())
        if else_at:
            taken = (text[start + len(r"\ifanon"):else_at[0]] if anon
                     else text[else_at[1]:end_start])
        else:
            taken = text[start + len(r"\ifanon"):end_start] if anon else ""
        out.append(taken)
        i = end_stop


def prepare(anon, for_docx):
    text = SRC.read_text(encoding="utf-8")
    text = text.replace("\\newif\\ifanon\n", "").replace("\\anonfalse\n", "")
    text = resolve_conditionals(text, anon)
    block = TITLE if anon else TITLE + BYLINE
    text = text.replace("\\maketitle", block + "\\vspace{1em}\n")
    if for_docx:
        # ScholarOne's pre-fill parser reads the two-line title block as two
        # title candidates and concatenates them, so the submission form comes
        # up with the title entered twice. One line in the Word file, two in
        # the typeset PDF where the break looks better.
        text = text.replace(r"How Much Do Statutes Disagree?\\[2pt]" + "\n",
                            "How Much Do Statutes Disagree? ")
        # The journal wants the manuscript double-spaced, and figures supplied
        # as separate files rather than embedded in the text.
        text = text.replace("\\onehalfspacing", "\\doublespacing")
        # \ref survives into Word as a broken internal hyperlink --- and the
        # figure labels are removed below anyway --- so resolve every
        # cross-reference to its number before pandoc sees it.
        numbers = {}
        for i, m in enumerate(FIGURE_ENV.finditer(text), 1):
            label = re.search(r"\\label\{([^}]*)\}", m.group(0))
            if label:
                numbers[label.group(1)] = str(i)
        for i, m in enumerate(re.finditer(r"\\label\{(tab:[^}]*)\}", text), 1):
            numbers[m.group(1)] = str(i)
        # Section cross-references cannot be counted from the source the way
        # figures and tables can --- LaTeX numbers them --- so they are read
        # from the .aux the identified build has just written. Hardcoding
        # «section 3.1» in prose was the alternative, and it rots silently the
        # first time a section moves.
        aux = HERE / "main_identified.aux"
        if aux.exists():
            for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}",
                                 aux.read_text(encoding="utf-8")):
                numbers.setdefault(m.group(1), m.group(2))
        def deref(m):
            if m.group(1) not in numbers:
                sys.exit(f"unresolved cross-reference: {m.group(1)}")
            return numbers[m.group(1)]
        text = re.sub(r"\\ref\{([^}]*)\}", deref, text)
        text, n = FIGURE_ENV.subn(figure_paragraphs, text)
        if n != 2:
            sys.exit(f"expected 2 figure environments, rewrote {n}")
        # pandoc hoists \begin{abstract} into document metadata, which would
        # put the abstract above the title in the .docx.
        text = text.replace("\\begin{abstract}", "\\subsection*{Abstract}\n")
        text = text.replace("\\end{abstract}", "")
    return text


def latex(stem, source):
    (HERE / f"{stem}.tex").write_text(source, encoding="utf-8")
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", stem],
                       cwd=HERE, capture_output=True, text=True)
    log = (HERE / f"{stem}.log").read_text(encoding="utf-8", errors="replace")
    bad = [ln for ln in log.splitlines()
           if re.search(r"Overfull|Underfull|Undefined control", ln)]
    if bad:
        print(f"  ! {len(bad)} layout warnings in {stem}")
        for ln in bad[:5]:
            print("   ", ln[:100])
    if not (HERE / f"{stem}.pdf").exists():
        sys.exit(f"{stem} failed to compile")
    pages = re.search(r"Output written on \S+ \((\d+) pages", log)
    print(f"  {stem}.pdf: {pages.group(1) if pages else '?'} pages")


def double_spaced_reference():
    """pandoc ignores setspace, so the .docx line spacing comes from a
    reference document. Build one from pandoc's own default and set the
    Normal and footnote styles to double spacing, which the journal
    requires."""
    ref = HERE / "reference.docx"
    subprocess.run(["pandoc", "-o", str(ref), "--print-default-data-file",
                    "reference.docx"], cwd=HERE, check=True,
                   stdout=subprocess.DEVNULL)
    with zipfile.ZipFile(ref) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    styles = parts["word/styles.xml"].decode("utf-8")
    # w:line is in twentieths of a point; 480 = 24pt, double for 12pt text.
    spacing = '<w:spacing w:line="480" w:lineRule="auto" w:after="0"/>'
    patched, done = styles, []
    for style_id in ("Normal", "BodyText", "FootnoteText"):
        m = re.search(
            r'<w:style [^>]*w:styleId="%s"[^>]*>((?:(?!</w:style>).)*?)'
            r'</w:style>' % style_id, patched, re.S)
        if not m:
            continue
        block = m.group(0)
        if "<w:pPr>" in block:
            fixed = re.sub(r"<w:spacing[^>]*/>", "", block, count=1)
            fixed = fixed.replace("<w:pPr>", "<w:pPr>" + spacing, 1)
        else:
            fixed = block.replace("</w:style>",
                                  "<w:pPr>" + spacing + "</w:pPr></w:style>")
        patched = patched.replace(block, fixed, 1)
        done.append(style_id)
    if "Normal" not in done:
        sys.exit("could not set double spacing on the Normal style")
    # The journal asks for Times New Roman; pandoc's default reference
    # document uses the theme fonts, which resolve to Calibri.
    fonts = ('<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
             'w:cs="Times New Roman" w:eastAsia="Times New Roman"/>')
    patched, hits = re.subn(r"<w:rFonts[^>]*/>", fonts, patched)
    if hits == 0:
        sys.exit("could not set the document font")
    # Hyperlink styling underlines the text, which the journal asks authors
    # to avoid; the anonymised manuscript has no external links anyway.
    patched = re.sub(
        r'(<w:style [^>]*w:styleId="Hyperlink"[^>]*>)'
        r'((?:(?!</w:style>).)*?)</w:style>',
        lambda m: m.group(1) + re.sub(r"<w:u [^>]*/>", "", m.group(2))
        + "</w:style>", patched, flags=re.S)
    parts["word/styles.xml"] = patched.encode("utf-8")
    with zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    return ref


# ALQ requires that "the document properties should also be anonymised", and a
# .docx carries them in docProps/, which no amount of reading the body will
# show. So: blank the fields that can name a person, then audit the archive
# whole -- every part, as bytes -- rather than the rendered text. The appeal
# paper's audit passed while the repository URL sat in a footnote part; this
# one does not read a projection of the file, it reads the file.
PROPERTY_FIELDS = ("dc:creator", "cp:lastModifiedBy", "cp:lastPrinted",
                   "Company", "Manager")


def scrub_properties(path):
    """Empty every docProps field that could name the author."""
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    for name in ("docProps/core.xml", "docProps/app.xml"):
        if name not in parts:
            continue
        xml = parts[name].decode("utf-8")
        for field in PROPERTY_FIELDS:
            xml = re.sub(r"<%s>.*?</%s>" % (field, field),
                         "<%s></%s>" % (field, field), xml, flags=re.S)
        parts[name] = xml.encode("utf-8")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)


def archive_text(path):
    """Every part of the .docx, decoded, so nothing hides in a part."""
    with zipfile.ZipFile(path) as z:
        return "\n".join(z.read(n).decode("utf-8", "ignore")
                          for n in z.namelist())


def abstract_and_keywords():
    """Lift both from main.tex, so the title page cannot drift from the paper.

    ALQ's Attach Files step reads this document to pre-fill the submission
    form, and its instructions require the title page to carry the abstract
    and the keywords. Retyping either here would put a second copy of the
    article's own words in a file nothing checks.
    """
    src = SRC.read_text(encoding="utf-8")
    a = src.index(r"\begin{abstract}") + len(r"\begin{abstract}")
    b = src.index(r"\end{abstract}")
    abstract = src[a:b].replace(r"\noindent", "").strip()
    m = re.search(r"\\textbf\{Keywords:\}(.*?)\n\\vspace", src, re.S)
    if not m:
        sys.exit("REFUSING: main.tex has no keywords line to copy")
    return abstract, " ".join(m.group(1).split())


def to_plain(path):
    return subprocess.run(["pandoc", str(path), "-t", "plain"],
                          cwd=HERE, capture_output=True, text=True).stdout


def docx(tex_stem, out_name, reference=None):
    cmd = ["pandoc", f"{tex_stem}.tex", "-o", out_name]
    if reference:
        cmd += ["--reference-doc", reference.name]
    subprocess.run(cmd, cwd=HERE, check=True)
    return len(to_plain(HERE / out_name).split())


def clean(*stems):
    for stem in stems:
        for suffix in (".aux", ".log", ".out"):
            f = HERE / f"{stem}{suffix}"
            if f.exists():
                f.unlink()


def main():
    if not shutil.which("pandoc"):
        sys.exit("pandoc is required for the .docx build")

    print("identified build (for the record)")
    latex("main_identified", prepare(anon=False, for_docx=False))
    shutil.copy(HERE / "main_identified.pdf", HERE / "main.pdf")

    print("anonymised build")
    latex("main_anon", prepare(anon=True, for_docx=False))

    print("submission manuscript")
    (HERE / "submission_manuscript.tex").write_text(
        prepare(anon=True, for_docx=True), encoding="utf-8")
    ref = double_spaced_reference()
    words = docx("submission_manuscript", "submission_manuscript.docx", ref)
    # US law reviews state no word limit and run long; the count is reported
    # because the cover letter quotes it, not because a cap binds.
    print(f"  submission_manuscript.docx: {words} words including footnotes")

    print("title page")
    abstract, keywords = abstract_and_keywords()
    latex("submission_title_page",
          TITLE_PAGE.replace("__WORDCOUNT__", f"{words:,}")
                    .replace("__ABSTRACT__", abstract)
                    .replace("__KEYWORDS__", keywords))
    # the cover letter states the same count, so it reads it rather than
    # repeating it: an earlier letter carried a figure from a stale build.
    (HERE / "wordcount.tex").write_text(
        "\\newcommand{\\nWords}{" + f"{words:,}".replace(",", "{,}") + "}\n",
        encoding="utf-8")
    docx("submission_title_page", "submission_title_page.docx", ref)

    print("anonymity audit")
    scrub_properties(HERE / "submission_manuscript.docx")
    identity = ("Almohammedi", "abdullah", "orcid", "Abdullah-m7",
                "github.com", "zenodo", "0009-0001")
    body = archive_text(HERE / "submission_manuscript.docx").lower()
    leaks = [w for w in identity if w.lower() in body]
    if leaks:
        sys.exit(f"anonymised manuscript leaks: {leaks}")
    print(f"  submission_manuscript.docx: clean of {len(identity)} strings "
          f"across every part of the archive, properties included")

    for f in ("fig1_funnel.eps", "fig2_adjudication.eps"):
        if not (HERE / f).exists():
            print(f"  ! {f} missing --- run make_figures.py")

    clean("main_identified", "main_anon", "submission_title_page")
    for junk in ("reference.docx",
                 "main_identified.tex", "main_identified.pdf",
                 "main_anon.tex", "main_anon.docx",
                 "submission_manuscript.tex", "submission_title_page.tex"):
        f = HERE / junk
        if f.exists():
            f.unlink()
    print("done")


if __name__ == "__main__":
    main()
