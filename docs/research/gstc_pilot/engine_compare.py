"""Compare the three extraction engines on the same pages (PHASE 3).

There is no ground-truth text for these PDFs, so this is not a character
error rate.  It measures the things that decide whether a *legal* reading
survives extraction, on identical pages, per engine:

  ARTICLE_TOKEN     how many «مادة» tokens the page yields at all
  ARTICLE_NUMBERED  of those, how many carry a number a reader could resolve
  NUMBER_SCRAMBLE   digit runs the bracket repair has to move
  NEGATION_TOKENS   negation particles, which flip a holding if lost
  AMOUNT_TOKENS     currency amounts
  DATE_TOKENS       hijri/gregorian dates
  BIDI_PER_K        directional controls the engine leaves in the stream
  ORDER             من : نم ratio — reversed character order shows up here

A count that is *lower* than another engine's on the same page is a loss:
the token was in the page and one engine failed to give it back.
"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from research.canon.canonical import canonicalise  # noqa: E402

PDFS = HERE / "raw"
OUT = HERE / "engine_compare.json"
PAGES_PER_DOC = 6

BIDI = "‎‏‪‫‬‭‮⁦⁧⁨⁩"
ARTICLE = re.compile(r"(?:^|[^ء-ي])((?:ال)?مادة|(?:ال)?مادتين|(?:ال)?مواد)(?![ء-ي])")
NUMBERED = re.compile(r"[٠-٩0-9]")
NEGATION = re.compile(r"(?:^|[^ء-ي])(لا|لم|لن|غير|دون|ليس|عدم)(?![ء-ي])")
AMOUNT = re.compile(r"[٠-٩0-9][٠-٩0-9,،.]*\s*(?:ريال|ر\.س|SAR)")
DATE = re.compile(r"[٠-٩0-9]{1,2}\s*/\s*[٠-٩0-9]{1,2}\s*/\s*[٠-٩0-9]{4}"
                  r"|[٠-٩0-9]{4}\s*(?:هـ|ه\b|م\b)")
SCRAMBLE = re.compile(r"[٠-٩0-9]+\s*[)\]}]|[({\[]\s*$", re.M)
DIGIT_SPLIT = re.compile(r"[٠-٩0-9]\s*\n\s*[٠-٩0-9]")
ART_ADJ = re.compile(r"(?:^|[^ء-ي])(?:ال)?مادة(?![ء-ي])[^\n]{0,20}?[٠-٩0-9]")


def pdftotext(pdf, page):
    r = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-enc", "UTF-8", str(pdf), "-"],
                       capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def pymupdf(pdf, page):
    import fitz
    with fitz.open(pdf) as d:
        return d[page - 1].get_text()


def mutool(pdf, page):
    r = subprocess.run(["mutool", "draw", "-F", "txt", "-o", "-", str(pdf), str(page)],
                       capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


ENGINES = {"pdftotext": pdftotext, "pymupdf": pymupdf, "mutool": mutool}


def measure(raw):
    bidi = sum(raw.count(c) for c in BIDI)
    canon = canonicalise(raw)["canonical"]
    arts = [m for m in ARTICLE.finditer(canon)]
    numbered = 0
    for m in arts:
        if NUMBERED.search(canon[m.end():m.end() + 40]):
            numbered += 1
    letters = sum(1 for c in canon if "ء" <= c <= "ي")
    return {
        "chars": len(raw),
        "arabicLetters": letters,
        "ARTICLE_TOKEN": len(arts),
        "ARTICLE_NUMBERED": numbered,
        "NUMBER_SCRAMBLE": len(SCRAMBLE.findall(raw)),
        "DIGIT_SPLIT": len(DIGIT_SPLIT.findall(canon)),
        "ARTICLE_ADJACENT": len(ART_ADJ.findall(canon)),
        "NEGATION_TOKENS": len(NEGATION.findall(canon)),
        "AMOUNT_TOKENS": len(AMOUNT.findall(canon)),
        "DATE_TOKENS": len(DATE.findall(canon)),
        "BIDI_PER_K": round(bidi / max(len(raw), 1) * 1000, 1),
        "MIN": canon.count("من"), "NIM": canon.count("نم"),
    }


def pages_of(pdf):
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0


def main():
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    names = [r["file"] for r in manifest["records"] if r.get("retrieved")]
    if len(sys.argv) > 1:
        names = [n for n in names if n in sys.argv[1:]]
    out = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for name in names:
        if name in out:
            continue
        pdf = PDFS / name
        if not pdf.exists():
            continue
        n = pages_of(pdf)
        if n < 3:
            continue
        # deterministic spread, skipping front matter
        step = max(1, (n - 4) // PAGES_PER_DOC)
        pages = [min(n, 3 + i * step) for i in range(PAGES_PER_DOC)]
        rec = {"pages": pages, "engines": {}}
        for eng, fn in ENGINES.items():
            tot = None
            for p in pages:
                try:
                    m = measure(fn(pdf, p))
                except Exception as exc:                       # noqa: BLE001
                    rec["engines"][eng] = {"error": str(exc)[:120]}
                    tot = None
                    break
                tot = m if tot is None else {k: tot[k] + m[k] for k in tot}
            if tot:
                tot["BIDI_PER_K"] = round(tot["BIDI_PER_K"] / len(pages), 1)
                rec["engines"][eng] = tot
        out[name] = rec
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(name, "done", flush=True)


if __name__ == "__main__":
    main()
