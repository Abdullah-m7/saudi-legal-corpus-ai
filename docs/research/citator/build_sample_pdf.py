#!/usr/bin/env python3
"""One sendable PDF: the index of the twenty digests, and one of them in full.

The digests live as Markdown in this repository and read well on GitHub. A
person met on a professional network does not always want a repository link,
so this produces a single Arabic PDF small enough to be read in one sitting:
the index, then article 16 of the Commercial Courts Law as the exemplar --
the most-cited article in the corpus.

    python3 build_sample_pdf.py     ->  digests_sample.pdf

Rendered through the browser rather than through LaTeX. The TeX installation
here has no working Arabic bidi support, and fighting that produces a PDF whose
shaping cannot be trusted --- which for a document whose whole claim is
fidelity to an official text would be the wrong corner to cut. Chromium shapes
and reorders Arabic correctly, so the page is written as HTML and printed.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIG = HERE / "digests"
OUT = HERE / "digests_sample.pdf"
EXEMPLAR = "commercial_courts_law__16.md"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
html { direction: rtl; }
body { font-family: "Noto Naskh Arabic", serif; font-size: 11.5pt;
       line-height: 1.85; color: #14171c; text-align: right; }
h1 { font-size: 19pt; line-height: 1.5; margin: 0 0 .2em;
     border-bottom: 2px solid #14171c; padding-bottom: .3em; }
h2 { font-size: 14pt; margin: 1.9em 0 .5em; color: #14171c;
     border-bottom: 1px solid #c9cfd6; padding-bottom: .2em; }
p { margin: .7em 0; }
blockquote { margin: .9em 0; padding: .55em 1em .55em 1em;
             border-right: 3px solid #8a949e; background: #f5f6f8;
             color: #2b3138; font-size: 10.5pt; line-height: 1.75; }
table { border-collapse: collapse; width: 100%; margin: 1em 0;
        font-size: 10pt; }
th, td { border-bottom: 1px solid #d7dce1; padding: .38em .6em;
         text-align: right; white-space: nowrap; }
/* only the column naming an article is allowed to wrap; letting the numeric
   columns wrap gives them width they do not need and squeezes the name into
   four lines. */
td:nth-child(2), th:nth-child(2) { white-space: normal;
                                   width: 52%; }
th { border-bottom: 1.5px solid #14171c; font-weight: 700; }
tr:last-child td { border-bottom: 1.5px solid #14171c; }
ul { padding-right: 1.2em; }
li { margin: .35em 0; }
strong { font-weight: 700; }
hr { border: none; border-top: 1px solid #d7dce1; margin: 2em 0; }
.newpage { page-break-before: always; }
a { color: #14171c; text-decoration: none; }
"""

COVER = """# خلاصات المواد الأكثر استشهادًا

*من ذخيرة الأحكام التجارية المنشورة*

هذه صفحتان من عملٍ أوسع: **٥٠٬٦٦٦ حكمًا** تجاريًّا منشورًا بنصّه الكامل،
مربوطًا بالأنظمة **على مستوى المادة** — ٩٩٬١٥٨ استشهادًا نظاميًّا، كلٌّ منها
مسنَدٌ إلى المادة التي عناها، ومعه موضعه من الحكم، ومن المتكلّم فيه، وهل صمد
ذلك الحكم أمام الاستئناف.

يلي ذلك **فهرس المواد العشرين الأكثر استشهادًا**، ثم **صفحةٌ واحدة كاملة**
نموذجًا — المادة ١٦ من نظام المحاكم التجارية، وهي أكثر مواد الذخيرة استشهادًا.
والتسع عشرة الباقية على المستودع العامّ.

<div class="newpage"></div>
"""


def clean(md):
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)      # links, not paths
    md = re.sub(r"</?sub>", "", md)
    md = re.sub(r"`([^`]+)`", r"\1", md)
    return md


def main():
    if not shutil.which("pandoc"):
        sys.exit("pandoc is required")
    if not Path(CHROME).exists():
        sys.exit(f"no browser at {CHROME}")

    # the cover already carries the title; the index page repeats it as its
    # own H1, which then prints on top of the cover's
    index = clean((DIG / "README.md").read_text(encoding="utf-8"))
    index = re.sub(r"\A#[^\n]*\n", "", index)
    md = "\n".join([
        COVER,
        index,
        '\n<div class="newpage"></div>\n',
        clean((DIG / EXEMPLAR).read_text(encoding="utf-8"))])
    src = HERE / "digests_sample.md"
    src.write_text(md, encoding="utf-8")

    html = HERE / "digests_sample.html"
    r = subprocess.run(
        ["pandoc", str(src), "-f", "markdown+raw_html", "-t", "html5",
         "--standalone", "--metadata", "title=خلاصات المواد الأكثر استشهادًا",
         "--metadata", "lang=ar", "-o", str(html)],
        capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"pandoc failed:\n{r.stderr[-3000:]}")
    body = html.read_text(encoding="utf-8").replace(
        "</head>", f"<style>{CSS}</style></head>")
    html.write_text(body, encoding="utf-8")

    r = subprocess.run(
        [CHROME, "--headless", "--no-sandbox", "--disable-gpu",
         "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
         html.as_uri()], capture_output=True, text=True)
    if r.returncode or not OUT.exists():
        sys.exit(f"chromium failed:\n{r.stderr[-3000:]}")
    src.unlink()
    html.unlink()
    pages = subprocess.run(["pdfinfo", str(OUT)], capture_output=True,
                           text=True).stdout
    print(f"wrote {OUT.name} — "
          + next(l for l in pages.splitlines() if l.startswith("Pages")))


if __name__ == "__main__":
    main()
