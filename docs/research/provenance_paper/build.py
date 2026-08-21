#!/usr/bin/env python3
"""Build the Statute Law Review submission files for this article.

The journal wants two Word documents: an anonymised manuscript, double-spaced,
with figures referenced rather than embedded; and a separate title page
carrying the author's identity, the declarations, and the total word count.

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

import html
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "main.tex"

# A whole figure environment becomes a one-cell Word table if it is left
# intact, so the docx build replaces each one with ordinary paragraphs.
FIGURE_ENV = re.compile(
    r"\\begin\{figure\}(?:\[[^\]]*\])?\s*"
    r"\\centering\s*"
    r"\\includegraphics\[[^\]]*\]\{fig(\d)_([a-z_]+)\.png\}\s*"
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
    if for_docx:
        # The \\ inside \title and \author is a line break for the typeset
        # PDF. pandoc drops it without putting anything in its place, so the
        # .docx read "Record?Availability" and ran the byline's four lines into
        # one word. Flattening them is also what ScholarOne's pre-fill parser
        # needs: given a two-line title it reads two title candidates and
        # concatenates them, which is how an earlier submission arrived with
        # its title entered twice.
        def flatten(cmd, joiner):
            def sub(m):
                parts = [p.strip() for p in re.split(r"\\\\", m.group(1))]
                return f"\\{cmd}{{" + joiner.join(p for p in parts if p) + "}"
            return sub
        text = re.sub(r"\\title\{(.*?)\}\n\n", flatten("title", " "),
                      text, flags=re.S)
        text = re.sub(r"\\author\{(.*?)\}\n", flatten("author", ", "),
                      text, flags=re.S)
        # The journal wants the manuscript double-spaced, and figures supplied
        # as separate files rather than embedded in the text.
        text = text.replace("\\onehalfspacing", "\\doublespacing")
        # \ref survives into Word as a broken internal hyperlink --- and the
        # figure labels are removed below anyway --- so resolve every
        # cross-reference to its number before pandoc sees it. The numbers
        # come from the .aux LaTeX just wrote, which is authoritative for
        # sections, tables and figures alike.
        numbers = {}
        aux = HERE / "main_anon.aux"
        if aux.exists():
            for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}",
                                 aux.read_text(encoding="utf-8",
                                               errors="replace")):
                numbers[m.group(1)] = m.group(2)
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


def to_plain(path):
    """Every run of text in the .docx, read from the XML rather than pandoc.

    `pandoc -t plain` was used here first, and it silently omits the title and
    byline: reading a .docx back, it lifts those paragraphs into document
    metadata and prints only the body. That hid a duplicated title, and it
    left a hole in the anonymity audit below --- an author name surviving in
    the byline is exactly the leak that matters most, and it was the one
    string the audit could not see. Nothing in the XML is invisible.
    """
    parts = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        # Footnotes are a separate part. Reading only document.xml dropped
        # them, which understated the word count by 253 against a limit the
        # journal states as including them, and would have let a name in a
        # footnote pass the audit.
        for name in ("word/document.xml", "word/footnotes.xml",
                     "word/endnotes.xml"):
            if name in names:
                parts.append(z.read(name).decode("utf-8"))
    xml = re.sub(r"</w:p>", "\n", "\n".join(parts))
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


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


# The submission form's abstract box and its Policy Significance box take plain
# text. Generating them here rather than by hand is not tidiness: when the
# abstract was trimmed to the form's 250-word limit, the hand-made
# abstract_plain.txt kept the old 307-word text and would have been pasted into
# the form. The manuscript is the only source either file may come from.
FORM_FIELDS = (
    ("abstract_plain.txt", r"\\begin\{abstract\}\s*\\noindent\s*(.*?)\s*\\end\{abstract\}"),
    ("policy_significance_plain.txt",
     r"\\textbf\{Policy Significance Statement\}\s*\\noindent\s*(.*?)\s*\\vspace"),
)


def form_fields(source):
    """Write the plain-text forms of the fields the submission form asks for."""
    for name, pattern in FORM_FIELDS:
        m = re.search(pattern, source, re.S)
        if not m:
            sys.exit(f"cannot find the source text for {name}")
        text = " ".join(m.group(1).split())
        text = text.replace("---", "\u2014").replace("--", "\u2013")
        text = re.sub(r"\\%", "%", text)
        # A LaTeX command or a stray brace reaching the form would be pasted
        # into the journal's record verbatim, so refuse instead of shipping it.
        residue = re.findall(r"\\[a-zA-Z]+|[{}$]", text)
        if residue:
            sys.exit(f"{name} still carries LaTeX: {sorted(set(residue))}")
        (HERE / name).write_text(text + "\n", encoding="utf-8")
        print(f"  {name}: {len(text.split())} words")


def title_appears_once(path, source):
    """The title must appear exactly once in the .docx.

    It appeared twice, in two different wordings, for as long as this script
    kept its own copy of the title: pandoc emitted the \\title metadata and the
    substituted block followed it, still carrying the article's pre-retitle
    name. The reviewer would have read one title and the submission form
    another. Checking the built file is the only way to catch that, since both
    halves looked correct in the source.
    """
    m = re.search(r"\\title\{(.*?)\}\n\n", source, re.S)
    if not m:
        sys.exit("cannot find \\title in the manuscript")
    # pandoc curls the apostrophe in "State's", so compare on a form that
    # does not depend on which quote character each tool chose.
    def flat(s):
        for c in "\u2018\u2019\u201c\u201d":
            s = s.replace(c, "'")
        return " ".join(s.split())
    title = flat(re.sub(r"\\\\", " ", m.group(1)))
    n = flat(to_plain(path)).count(title)
    if n != 1:
        sys.exit(f"{path.name}: title appears {n} times, expected once")
    return title

def main():
    if not shutil.which("pandoc"):
        sys.exit("pandoc is required for the .docx build")

    print("identified build (for the record)")
    latex("main_identified", prepare(anon=False, for_docx=False))
    shutil.copy(HERE / "main_identified.pdf", HERE / "main.pdf")

    print("anonymised build")
    latex("main_anon", prepare(anon=True, for_docx=False))

    # The submission portal asks for two complete manuscripts --- one carrying
    # the author's details and one anonymous --- rather than a manuscript plus
    # a separate title page. Both are produced from the same source.
    print("submission manuscripts")  # read main_anon.aux for \\ref numbers
    ref = double_spaced_reference()
    (HERE / "submission_manuscript_anonymous.tex").write_text(
        prepare(anon=True, for_docx=True), encoding="utf-8")
    words = docx("submission_manuscript_anonymous",
                 "submission_manuscript_anonymous.docx", ref)
    (HERE / "submission_manuscript_with_author_details.tex").write_text(
        prepare(anon=False, for_docx=True), encoding="utf-8")
    docx("submission_manuscript_with_author_details",
         "submission_manuscript_with_author_details.docx", ref)
    print(f"  anonymous: {words} words including footnotes "
          "(check against the chosen journal's limit)")

    for name in ("submission_manuscript_anonymous.docx",
                 "submission_manuscript_with_author_details.docx"):
        title = title_appears_once(HERE / name, SRC.read_text(encoding="utf-8"))
    print(f"  title appears once in both, as: {title}")

    print("submission form fields")
    form_fields(SRC.read_text(encoding="utf-8"))

    print("anonymity audit")
    terms = ("Almohammedi", "abdullah", "orcid", "Abdullah-m7",
             "github.com", "zenodo", "0009-0001")
    anon_text = to_plain(HERE / "submission_manuscript_anonymous.docx").lower()
    leaks = [w for w in terms if w.lower() in anon_text]
    if leaks:
        sys.exit(f"anonymised manuscript leaks: {leaks}")
    print("  anonymous: clean")
    # The identified file must carry the details the anonymous one hides ---
    # a silent failure here would submit two anonymous manuscripts.
    named = to_plain(
        HERE / "submission_manuscript_with_author_details.docx").lower()
    missing = [w for w in terms if w.lower() not in named]
    if missing:
        sys.exit(f"identified manuscript is missing: {missing}")
    print("  with author details: carries author, ORCID, repository and DOIs")
    # The journal's AI-policy checkbox confirms that the manuscript names the
    # tool WITH ITS VERSION. Shipping the placeholder would make that
    # confirmation untrue, so refuse rather than let it through quietly.
    if "anonversion" in named:
        sys.exit("the AI declaration still says ANONVERSION -- the author must "
                 "supply the tool version before these files are uploaded")

    for f in ("fig1_access.eps", "fig2_tiers.eps"):
        if not (HERE / f).exists():
            print(f"  ! {f} missing --- run make_figures.py")

    clean("main_identified", "main_anon")
    for junk in ("reference.docx",
                 "main_identified.tex", "main_identified.pdf",
                 "main_anon.tex", "main_anon.docx",
                 "submission_manuscript.tex", "submission_manuscript.docx",
                 "submission_manuscript_anonymous.tex",
                 "submission_manuscript_with_author_details.tex",
                 "submission_title_page.tex", "submission_title_page.docx",
                 "submission_title_page.pdf"):
        f = HERE / junk
        if f.exists():
            f.unlink()
    print("done")


if __name__ == "__main__":
    main()
