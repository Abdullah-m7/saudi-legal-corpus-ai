#!/usr/bin/env python3
"""Build the two files Government Information Quarterly wants, and audit them.

The journal reviews double anonymized and asks for the title page and the
manuscript as separate files. It also asks for LaTeX source, not a PDF. That
second requirement is the one that makes a conditional switch insufficient:
a `.tex` carrying the author inside a disabled `\\else` branch still carries
the author in plain text, one flag away from any reader of the upload. So the
anonymous manuscript is produced by physically resolving every `\\ifanon`
block and deleting the identified branch, not by flipping `\\anonfalse`.

Outputs
  main_anonymous.tex   uploaded as the manuscript source
  main_anonymous.pdf   what the reviewer reads
  title_page.tex/.pdf  identity, declarations and the vitae, seen by the editor

The audit runs in both directions: the manuscript must contain no identifying
token, and the title page must contain them all. A title page that passed the
anonymity check would mean the identity had been stripped from the one file
that is supposed to carry it.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "main.tex"

# Anything that names the author, or resolves to the author in one hop.
# The GitHub account name is the subtlest: it identifies as surely as the
# name does, and it sits inside a URL rather than a byline.
IDENTIFIERS = [
    "Almohammedi",
    "Abdullah",
    "abdullah.m.almohammedi",
    "0009-0001-0832-0995",
    "Abdullah-m7",
    "Rabigh",
]


def read_source() -> str:
    if not SOURCE.exists():
        sys.exit(f"missing {SOURCE}")
    return SOURCE.read_text(encoding="utf-8")


def split_conditionals(tex, anon=True):
    """Resolve every \\ifanon block, nesting included.

    With anon=True the anonymous branch is kept; with anon=False the identified
    one. The same resolver drives both files, so the two can never drift into
    disagreeing about what a conditional meant. Also returns the branches that
    were discarded, which is how the title page finds the author block.
    """
    # \newif\ifanon declares the switch; it is not a conditional, and a
    # parser that treats it as one runs off the end of the file looking for a
    # \fi that was never opened. Remove the declaration and the setting first.
    tex = re.sub(r"\\newif\\ifanon\s*\n", "", tex)
    tex = re.sub(r"\\anon(true|false)\s*\n", "", tex)

    out, identified = [], []
    i, depth = 0, 0
    # depth 0 means "outside any conditional"; a nested \if... inside the
    # branch we are skipping must not be mistaken for the end of the branch.
    while i < len(tex):
        m = re.compile(r"\\ifanon\b").search(tex, i)
        if not m:
            out.append(tex[i:])
            break
        out.append(tex[i:m.start()])
        j = m.end()
        # Walk forward to the matching \else and \fi at this level.
        anon_branch, other_branch = [], []
        target = anon_branch
        depth = 0
        while j < len(tex):
            nxt = re.compile(r"\\(ifanon|iftrue|iffalse|ifnum|ifx|else|fi)\b").search(tex, j)
            if not nxt:
                sys.exit("unterminated \\ifanon in main.tex")
            target.append(tex[j:nxt.start()])
            token = nxt.group(1)
            if token.startswith("if"):
                depth += 1
                target.append(nxt.group(0))
            elif token == "else":
                if depth == 0:
                    target = other_branch
                else:
                    target.append(nxt.group(0))
            else:  # fi
                if depth == 0:
                    j = nxt.end()
                    break
                depth -= 1
                target.append(nxt.group(0))
            j = nxt.end()
        kept, dropped = (anon_branch, other_branch) if anon else (other_branch, anon_branch)
        out.append("".join(kept))
        if "".join(dropped).strip():
            identified.append("".join(dropped).strip())
        i = j
    return "".join(out), identified


def inline_numbers(tex):
    """Fold numbers.tex into the manuscript.

    The uploaded file is compiled by the publisher's system, not here. An
    \\input that resolves on this machine is a second file that has to arrive,
    be recognised, and be found by name at their end - three ways for a build
    to fail on a dependency the reader never sees. The values are still
    generated; they are pasted in by this script rather than read at compile
    time.
    """
    numbers = (HERE / "numbers.tex").read_text(encoding="utf-8")
    if "\\input{numbers}" not in tex:
        sys.exit("main.tex no longer inputs numbers.tex; check before building")
    return tex.replace("\\input{numbers}",
                       "%% numbers.tex, inlined so the upload is one file.\n"
                       + numbers.strip(), 1)


def harden_metadata(tex):
    """Stop the PDF carrying an author in metadata the page never shows."""
    marker = "\\hypersetup{pdfauthor={},pdftitle={},pdfsubject={},pdfkeywords={},pdfcreator={}}\n"
    if marker in tex:
        return tex
    return tex.replace("\\begin{document}", marker + "\\begin{document}", 1)


def extract(pattern, tex, what):
    m = re.search(pattern, tex, re.S)
    if not m:
        sys.exit(f"could not find {what} in main.tex")
    return m.group(1).strip()


def build_title_page(tex, identified):
    title = extract(r"\\title\{(.+?)\n*\}", tex, "the title")
    author_block = next((b for b in identified if "\\author" in b), None)
    if author_block is None:
        sys.exit("the identified branches no longer carry the author block; "
                 "check main.tex")
    author = extract(r"\\author\{(.+?)\}\s*\\date", author_block, "the author block")

    # The editor sees every declaration, including the two the manuscript
    # withholds. Resolved in identified mode from the same source, so the two
    # files cannot disagree about what a declaration says.
    region = extract(r"(\\section\*\{Declarations\}.*?)\\end\{document\}", tex,
                     "the declarations")
    declarations, _ = split_conditionals(region, anon=False)
    bio = read_biography()

    return r"""\documentclass[11pt]{article}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{times}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[hidelinks]{hyperref}
\emergencystretch=3em
\pagestyle{empty}

%% TITLE PAGE - submitted as a separate file, per the journal's double
%% anonymized policy. The manuscript file carries none of this.

\begin{document}

\begin{center}
{\Large\bfseries """ + title + r"""}

\vspace{2em}

""" + author + r"""
\end{center}

\vspace{2em}

\noindent\textbf{Corresponding author.} Abdullah Almohammedi,
\texttt{abdullah.m.almohammedi@gmail.com}.

\vspace{1em}

\noindent\textbf{Author contact and affiliation.} Independent researcher.
No institutional affiliation; the work was carried out independently and
received no funding.

\vspace{1em}

""" + declarations + r"""

\section*{Vitae}

""" + bio + r"""

\vspace{1em}

\noindent A passport-type photograph of the author accompanies this
submission as a separate file: \texttt{Almohammedi\_photo.jpg}.

\end{document}
"""


def read_biography():
    """Take the chosen biography from biography.md rather than retyping it.

    The file marks one option as chosen; a biography that is typed twice is a
    biography that will disagree with itself.
    """
    path = HERE / "biography.md"
    if not path.exists():
        sys.exit("missing biography.md")
    text = path.read_text(encoding="utf-8")
    # [^\n]* rather than .* : re.S makes a dot match newlines, and a dot-star
    # here swallows the rest of the file, blanks and all.
    m = re.search(r"## Option B.*?\n((?:^>[^\n]*\n)+)", text, re.M | re.S)
    if not m:
        sys.exit("could not find the chosen biography (Option B) in biography.md")
    bio = " ".join(line.lstrip("> ").rstrip() for line in m.group(1).splitlines())
    bio = re.sub(r"\s+", " ", bio).strip()
    if "\u27e8" in bio or "<" in bio.replace("\\", ""):
        sys.exit(f"the biography still contains an unfilled blank: {bio}")
    words = len(bio.split())
    if words > 100:
        sys.exit(f"the biography runs to {words} words; the journal allows 100")
    print(f"  biography: {words} words, no blanks")
    return bio


def write_vitae_docx(bio: str) -> Path:
    """The journal wants the biography in an editable format, so a PDF will
    not do. Generated from the same string the title page uses, so the two
    cannot come to disagree about what the author's biography says.
    """
    out = HERE / "Almohammedi_biography.docx"
    md = HERE / "_vitae.md"
    md.write_text(f"**Abdullah Almohammedi**\n\n{bio}\n", encoding="utf-8")
    try:
        subprocess.run(["pandoc", str(md), "-o", str(out)], check=True,
                       capture_output=True, text=True)
    finally:
        md.unlink(missing_ok=True)
    return out


def latex(path: Path):
    for _ in range(2):
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", path.name],
            cwd=HERE, capture_output=True, text=True)
        if r.returncode != 0:
            tail = "\n".join(r.stdout.splitlines()[-25:])
            sys.exit(f"pdflatex failed on {path.name}:\n{tail}")
    return path.with_suffix(".pdf")


def pdf_text(pdf: Path) -> str:
    return subprocess.run(["pdftotext", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout


def audit(anon_tex: Path, anon_pdf: Path, title_pdf: Path):
    """Check in both directions, and check the source as well as the PDF."""
    failures = []

    # The manuscript, as a PDF and as the source file that is actually
    # uploaded. The source matters more: it is the one a switch would betray.
    for target, label in ((anon_tex.read_text(encoding="utf-8"), "main_anonymous.tex"),
                          (pdf_text(anon_pdf), "main_anonymous.pdf")):
        for token in IDENTIFIERS:
            if token.lower() in target.lower():
                failures.append(f"{label} contains {token!r}")

    # PDF metadata is not in the extracted text and is read by anyone with a
    # PDF viewer's properties dialog.
    meta = subprocess.run(["pdfinfo", str(anon_pdf)],
                          capture_output=True, text=True).stdout
    for token in IDENTIFIERS:
        if token.lower() in meta.lower():
            failures.append(f"main_anonymous.pdf metadata contains {token!r}")

    # And the other direction. A title page that passes an anonymity check has
    # had the identity stripped from the one file meant to carry it.
    title_text = pdf_text(title_pdf)
    for token in ("Almohammedi", "abdullah.m.almohammedi", "0009-0001-0832-0995"):
        if token.lower() not in title_text.lower():
            failures.append(f"title_page.pdf is missing {token!r}")

    return failures


def main():
    print("Building the Government Information Quarterly submission files.\n")
    tex = read_source()
    anon, identified = split_conditionals(tex)
    anon = harden_metadata(inline_numbers(anon))

    anon_path = HERE / "main_anonymous.tex"
    anon_path.write_text(anon, encoding="utf-8")
    print(f"  wrote {anon_path.name} ({len(anon.splitlines())} lines, "
          f"{len(tex.splitlines()) - len(anon.splitlines())} removed)")

    title_path = HERE / "title_page.tex"
    title_path.write_text(build_title_page(tex, identified), encoding="utf-8")
    print(f"  wrote {title_path.name}")

    vitae = write_vitae_docx(read_biography())
    print(f"  wrote {vitae.name}")

    anon_pdf = latex(anon_path)
    title_pdf = latex(title_path)
    print(f"  compiled {anon_pdf.name} and {title_pdf.name}\n")

    failures = audit(anon_path, anon_pdf, title_pdf)
    if failures:
        print("ANONYMITY AUDIT FAILED")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("Anonymity audit passed in both directions:")
    print(f"  manuscript source and PDF carry none of: {', '.join(IDENTIFIERS)}")
    print("  PDF metadata carries none of them either")
    print("  title page carries the name, the email and the ORCID\n")
    print("Upload, by the file type the submission system asks for:")
    print("  Manuscript without author details  main_anonymous.tex")
    print("  Title page with author details     title_page.pdf")
    print("  Author biography                   Almohammedi_biography.docx")
    print("  Cover letter                       cover_letter.pdf")
    print("  Highlights                         highlights.txt")
    print("  Figures (supplementary section)    fig1_*.pdf, fig2_*.pdf")
    print("  Author photograph                  Almohammedi_photo.jpg")


if __name__ == "__main__":
    main()
