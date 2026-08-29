#!/usr/bin/env python3
"""Build two copies of the manuscript, and keep them apart on purpose.

The repository is public. The submission needs a postal address and a
telephone number on its title page, because the journal asks for them; the
repository does not need either, and a personal telephone number pushed to a
public remote is not retrievable afterwards. So:

  main.pdf, cover_letter.pdf   built against contact.example.tex, tracked
  submission/                  built against contact.tex, git-ignored

The Journal of Empirical Legal Studies reviews double-anonymously and asks for
both an anonymised manuscript and a full one, so build.py writes a third copy
with \anontrue and reads it back for anything that names the author --- the
title page, the correspondence block, the ORCID, and the repository URL, which
is the leak an author remembers last because it is a footnote about data.

The submission copy is the one to upload. It is identical in every other
respect: same source, same numbers.tex, same references. The audit at the end
reads both PDFs back and refuses to finish if the private details appear in
the public copy or are missing from the submission copy — the check has to
read the artefact, because that is the file that gets pushed.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "submission"
DOCS = ("main", "cover_letter")
# What a double-anonymous reviewer must not be able to read off the PDF.
IDENTITY = ("Almohammedi", "abdullah", "orcid", "0009-0001", "github.com",
            "Abdullah-m7", "zenodo")
CONTACT = HERE / "contact.tex"
EXAMPLE = HERE / "contact.example.tex"

# What Wiley's portal actually asks for, read off the upload screen rather
# than assumed: one Main Manuscript (Word or LaTeX, and a LaTeX manuscript may
# be bundled as a single archive), and one Title Page, in Word, which is not
# sent to reviewers. So the identity does not go in the manuscript at all --
# it goes in the title page, which is a separate required file. Two artefacts
# neither of which existed until the screen was read.
TITLE_PAGE = """\
# {title}

**Abdullah Almohammedi**

Independent Researcher\\
{address}

Corresponding author: Abdullah Almohammedi, {email}\\
Telephone: {phone}\\
ORCID: 0009-0001-0832-0995 (https://orcid.org/0009-0001-0832-0995)

## Acknowledgements

None.

## Funding statement

This research received no specific grant from any funding agency in the
public, commercial, or not-for-profit sectors.

## Conflict of interest statement

The author declares no conflicts of interest.

## Ethics statement

Not applicable. The study analyses court judgments published in full text by
the Saudi Ministry of Justice, with party names masked at source, and
legislation published in the Official Gazette. It involves no human subjects,
no personal data collected by the author, and no intervention; no ethics
review or informed consent was required.

## Data availability statement

The legislative corpus, the judgment corpus, the extraction and matching
code, the segmentation and voice-attribution code, and the scripts that
generate every number reported in this article are openly available at
https://github.com/Abdullah-m7/saudi-legal-corpus-ai under the MIT licence,
and archived on Zenodo. The underlying legislation and judgments are official
Saudi government publications; the binding Arabic original governs in all
cases.

## Use of AI tools

The analysis code deposited with this article, and drafts of the manuscript,
were produced with the assistance of a large language model (Anthropic's
Claude), working under the author's direction. Its purpose was implementation
and drafting; it did not originate the argument of the article or its
conclusions. The author designed the study, framed every question, verified
each result against the corpus, and is responsible for the content. No
measurement in the article is produced by a language model: every number is
computed by the deposited code from the deposited data, and the manuscript is
typeset from a generated file of macros.

## Prior submission

This manuscript was submitted to the *Journal of Legal Analysis* on
27 August 2026 and desk-rejected on scope on 28 August 2026 without external
review. It is not under consideration elsewhere.
"""


def latex(name, cwd):
    for _ in range(2):
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"{name}.tex"],
            cwd=cwd, capture_output=True, text=True)
    if not (cwd / f"{name}.pdf").exists():
        sys.exit(f"{name}.tex did not build:\n{r.stdout[-2000:]}")


def text_of(pdf):
    return subprocess.run(["pdftotext", str(pdf), "-"],
                          capture_output=True, text=True).stdout


def private_strings():
    """The values contact.tex sets, as they will appear in a PDF."""
    if not CONTACT.exists():
        return []
    out = []
    for m in re.finditer(r"\\newcommand\{\\Contact(\w+)\}\{(.+)\}",
                         CONTACT.read_text(encoding="utf-8")):
        field, value = m.group(1), m.group(2)
        if field == "Email":          # the email is on the paper either way
            continue
        out.append(re.sub(r"\\\\|--|~", lambda s: {"--": "\u2013"}.get(
            s.group(0), " "), value).strip())
    return out


def numbers():
    """The generated macros, so the title page cannot type a figure by hand."""
    out = {}
    for name, raw in re.findall(
            r"\\newcommand\{\\(\w+)\}\{([^{}]*(?:\{,\}[^{}]*)*)\}",
            (HERE / "numbers.tex").read_text(encoding="utf-8")):
        out[name] = raw.replace("{,}", ",")
    return out


def contact_fields():
    """Address, phone and email as contact.tex sets them, for the title page."""
    out = {}
    for m in re.finditer(r"\\newcommand\{\\Contact(\w+)\}\{(.+)\}",
                         CONTACT.read_text(encoding="utf-8")):
        out[m.group(1).lower()] = m.group(2).replace("\\\\", ", ").replace(
            "--", "\u2013").strip()
    return out


def build_archive(anon_source):
    """One Main Manuscript file: the anonymised LaTeX, bundled as an archive.

    The portal takes exactly one Main Manuscript, in Word or LaTeX, and says a
    LaTeX manuscript may be bundled as a single archive. So the upload is a zip
    of two files -- the source and the macros it cannot build without -- and
    the check compiles the zip's contents in an empty directory, because a
    manuscript that builds here and not there is a manuscript the editor
    cannot read.
    """
    source = "\n".join(line for line in anon_source.splitlines()
                        if "contact" not in line.lower())
    archive = OUT / "jels_main_manuscript.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("main.tex", source)
        z.writestr("numbers.tex",
                   (HERE / "numbers.tex").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(archive) as z:
            z.extractall(tmp)
        latex("main", tmp)
        body = text_of(tmp / "main.pdf")
        leaks = [w for w in IDENTITY if w.lower() in body.lower()]
        if leaks:
            sys.exit(f"REFUSING: the archive builds a PDF naming {leaks}")
        pages = int(subprocess.run(["pdfinfo", str(tmp / "main.pdf")],
                                   capture_output=True, text=True
                                   ).stdout.split("Pages:")[1].split()[0])
        here = int(subprocess.run(["pdfinfo", str(OUT / "main_anonymous.pdf")],
                                  capture_output=True, text=True
                                  ).stdout.split("Pages:")[1].split()[0])
        if pages != here:
            sys.exit(f"REFUSING: the archive builds {pages} pages, the "
                     f"anonymised manuscript has {here}")
        # The portal wants the PDF alongside the .tex, and the only PDF that
        # cannot disagree with the source uploaded beside it is the one that
        # source just built. Keep that one, not the sibling.
        shutil.copy2(tmp / "main.pdf", OUT / "jels_main_manuscript.pdf")
    print(f"jels_main_manuscript.zip builds standalone to {pages} clean "
          f"pages, kept as jels_main_manuscript.pdf")


def build_title_page():
    """The identified title page, in Word, which reviewers never see."""
    n = numbers()
    c = contact_fields()
    md = TITLE_PAGE.format(
        title=f"{n['nCCLShareRound']} Per Cent of the Procedure, "
              f"{n['nCivilShareRound']} Per Cent of the Code: The Enacted Law "
              f"and the Applied Law in {n['nJudgments']} Judgments",
        address=c["address"], email=c["email"], phone=c["phone"])
    src = OUT / "title_page.md"
    src.write_text(md, encoding="utf-8")
    docx = OUT / "title_page.docx"
    r = subprocess.run(["pandoc", str(src), "-o", str(docx)],
                       capture_output=True, text=True)
    if r.returncode or not docx.exists():
        sys.exit(f"title page did not convert:\n{r.stderr[-1000:]}")
    # The opposite audit to the manuscript's: this file MUST identify.
    body = subprocess.run(["pandoc", str(docx), "-t", "plain"],
                          capture_output=True, text=True).stdout
    required = ["Almohammedi", "0009-0001-0832-0995", c["address"],
                c["phone"], c["email"], n["nJudgments"]]
    missing = [v for v in required if v not in body]
    if missing:
        sys.exit(f"REFUSING: the title page does not carry {missing}")
    src.unlink()
    print(f"title_page.docx carries all {len(required)} required details")


def main():
    private = private_strings()

    # 1. the public copy, built against the placeholder file
    if CONTACT.exists():
        CONTACT.rename(CONTACT.with_suffix(".tex.held"))
    try:
        for name in DOCS:
            latex(name, HERE)
    finally:
        held = CONTACT.with_suffix(".tex.held")
        if held.exists():
            held.rename(CONTACT)

    for name in DOCS:
        body = text_of(HERE / f"{name}.pdf")
        for value in private:
            if value and value in body:
                sys.exit(f"REFUSING: {value!r} is in the public {name}.pdf")
    print(f"public copies clean of {len(private)} private value(s)")

    # 2. the submission copy, built against the real file
    if not CONTACT.exists():
        print("no contact.tex — submission copy not built")
        return
    OUT.mkdir(exist_ok=True)
    for f in ("main.tex", "cover_letter.tex", "numbers.tex", "contact.tex",
              "contact.example.tex"):
        shutil.copy2(HERE / f, OUT / f)
    for name in DOCS:
        latex(name, OUT)
        body = text_of(OUT / f"{name}.pdf")
        missing = [v for v in private if v and v not in body]
        if name == "main" and missing:
            sys.exit(f"REFUSING: submission main.pdf lacks {missing}")
    # 3. the anonymised copy, for a double-anonymous journal
    anon = OUT / "main_anonymous.tex"
    source = (HERE / "main.tex").read_text(encoding="utf-8")
    if "\\anonfalse" not in source:
        sys.exit("REFUSING: main.tex has no \\anonfalse to flip")
    anon.write_text(source.replace("\\anonfalse", "\\anontrue"),
                    encoding="utf-8")
    latex("main_anonymous", OUT)
    body = text_of(OUT / "main_anonymous.pdf").lower()
    leaks = [w for w in IDENTITY + tuple(private) if w and w.lower() in body]
    if leaks:
        sys.exit(f"REFUSING: anonymised manuscript names {leaks}")
    print(f"main_anonymous.pdf clean of {len(IDENTITY) + len(private)} "
          f"identifying string(s)")

    # 4. the two files the portal actually has slots for
    build_archive(anon.read_text(encoding="utf-8"))
    build_title_page()

    for junk in list(OUT.glob("*.aux")) + list(OUT.glob("*.log")) + \
            list(OUT.glob("*.out")) + list(OUT.glob("*.ent")):
        junk.unlink()
    print(f"submission copies written to {OUT}/ with the contact details")


if __name__ == "__main__":
    main()
