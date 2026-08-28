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
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "submission"
DOCS = ("main", "cover_letter")
# What a double-anonymous reviewer must not be able to read off the PDF.
IDENTITY = ("Almohammedi", "abdullah", "orcid", "0009-0001", "github.com",
            "Abdullah-m7", "zenodo")
CONTACT = HERE / "contact.tex"
EXAMPLE = HERE / "contact.example.tex"


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

    for junk in list(OUT.glob("*.aux")) + list(OUT.glob("*.log")) + \
            list(OUT.glob("*.out")) + list(OUT.glob("*.ent")):
        junk.unlink()
    print(f"submission copies written to {OUT}/ with the contact details")


if __name__ == "__main__":
    main()
