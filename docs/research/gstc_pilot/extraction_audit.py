#!/usr/bin/env python3
"""What each digest's text layer actually is, before anything is annotated.

The pilot found three different faults in five documents and treated them as
one kind of problem. They are not. A fault that *permutes* characters -- the
transposed definite article, bidirectional reordering, a bracket's contents
carried past it -- is recoverable from the text alone, and the canonicalisation
layer recovers it. A fault that *substitutes* characters -- «نظام» reaching
the reader as «نلام» -- is not, because the PDF's own ToUnicode map says «ل»
and no amount of reading the text can know otherwise.

Telling the two apart is what decides whether a document may be sampled, and
it has to be decided per document, from evidence, before a sample is drawn.

The substitution test is a letter-frequency comparison against the clean
family. Arabic letter frequencies in legal prose are stable to within a few
per cent across these digests; a letter that is depressed several-fold has not
become rarer, it has been mapped to something else. «ظ» runs at 0.38 per cent
of Arabic letters in the 2024 digests and 0.05 per cent in the customs
compendium: eight-fold, on a hundred and fifty thousand letters.

    python3 extraction_audit.py            # table
    python3 extraction_audit.py --json     # extraction_audit.json
"""

import collections
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE))
from canonical import canonicalise, lam_swap_diagnosis   # noqa: E402

RAW = HERE / "raw"
MANIFEST = HERE / "manifest.json"
OUT = HERE / "extraction_audit.json"
BIDI = set(range(0x200E, 0x200F + 1)) | set(range(0x202A, 0x202E + 1)) \
    | set(range(0x2066, 0x2069 + 1)) | {0x061C}
ARABIC = re.compile(r"[ء-ي]")
# letters whose frequency is stable enough across legal Arabic to be a probe,
# and which the observed substitutions destroy
PROBES = "ظضصثقفغعهبجحخذزطشسنملكيتار"
SUBSTITUTION_FACTOR = 3.0     # depressed this many times over: not rarity
FRAGMENT_RATE = 5.0           # per cent of Arabic tokens that are one letter

# Why a second detector. The letter-frequency test finds a ToUnicode map that
# sends one letter to another: the letter's rate collapses and the others take
# up the slack. It cannot find a map that sends a letter's *medial* form to
# nothing, because that damage is spread over every letter equally and shows up
# instead as words breaking into pieces. 9.pdf is 442,315 characters of
# apparently ordinary Arabic in which «مادة» never once occurs; its letter
# profile is unremarkable, and 15.1 per cent of its tokens are a single letter.
# The two tests are complementary and neither alone would have caught both
# defective documents.

# What the publisher calls each family, from the file name and the title.
SUBJECT = [
    ("customs", r"customs|جمرك"),
    ("vat", r"\bvat\b|القيمة المضافة"),
    ("zakat", r"zakat|الزكاة|الزكوي"),
    ("income tax", r"incometax|income-tax|ضريبة الدخل"),
    ("excise", r"excise|الانتقائية|االنتقائية"),
    ("real estate transaction tax", r"\brett\b|التصرفات العقارية"),
    ("tax, unspecified", r"tax|ضريب"),
]
KIND = [("principles", r"principles|مبادئ"),
        ("defences", r"defense|defence|دفوع|pleas"),
        ("decisions", r"decision|قرارات|أحكام")]


def classify(name, title):
    hay = f"{name} {title}".lower()
    subj = next((s for s, p in SUBJECT if re.search(p, hay, re.I)), None)
    kind = next((k for k, p in KIND if re.search(p, hay, re.I)), None)
    years = sorted({int(y) for y in re.findall(r"\b(20[0-2]\d)\b", hay)})
    return subj, kind, years


def fonts(pdf):
    r = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True)
    rows = [l.split() for l in r.stdout.splitlines()[2:] if l.strip()]
    out = {"total": len(rows), "noToUnicode": 0, "cid": 0, "embedded": 0}
    for row in rows:
        if len(row) < 6:
            continue
        emb, sub, uni = row[-5], row[-4], row[-3]
        out["noToUnicode"] += uni == "no"
        out["embedded"] += emb == "yes"
        out["cid"] += "CID" in " ".join(row)
    return out


def fragmentation(text):
    """One-letter-token rate, and whether the citation frame survives at all.

    A font that drops contextual forms leaves the letters that remain adrift:
    «باعتراض» comes back as «باعت اض». Nothing about the letter histogram is
    strange; the words are simply in pieces.
    """
    tokens = [w for w in text.split() if ARABIC.search(w)]
    if not tokens:
        return {"arabicTokens": 0, "fragmentRate": None, "framePerK": None}
    letters = len(ARABIC.findall(text)) or 1
    return {"arabicTokens": len(tokens),
            "fragmentRate": round(sum(1 for w in tokens if len(w) == 1)
                                  / len(tokens) * 100, 1),
            "framePerK": round(text.count("مادة") / letters * 1000, 2)}


def letter_profile(text):
    counts = collections.Counter(ARABIC.findall(text))
    total = sum(counts.values())
    return {c: counts.get(c, 0) / total for c in PROBES} if total else {}, total


def engines(pdf, page):
    """Same page, three engines. Not for choosing one -- for asking whether
    the fault is in the extraction or in the document."""
    out = {}
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", str(page),
                        "-l", str(page), str(pdf), "-"],
                       capture_output=True, text=True)
    out["pdftotext"] = r.stdout
    try:
        import pymupdf
        with pymupdf.open(pdf) as d:
            out["pymupdf"] = d[page - 1].get_text()
    except Exception as exc:
        out["pymupdf"] = f"__error__ {exc}"
    r = subprocess.run(["mutool", "draw", "-F", "txt", "-i", str(pdf),
                        str(page)], capture_output=True, text=True)
    out["mutool"] = r.stdout
    return out


def audit(resume=True):
    """One row per digest, written as each finishes.

    Canonicalising thirty-three digests of up to two million characters, with
    a thirty-letter transposition diagnosis inside each, is minutes of regex.
    The partial file is kept so the work is resumable and so a crash in
    document thirty does not discard twenty-nine.
    """
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = {}
    if resume and OUT.exists():
        try:
            rows = json.loads(OUT.read_text(encoding="utf-8"))["documents"]
        except Exception:
            rows = {}
    for rec in manifest["records"]:
        name = rec["file"]
        txt = RAW / name.replace(".pdf", ".txt")
        pdf = RAW / name
        if not txt.exists() or name in rows:
            continue
        print(f"  {name} …", end=" ", flush=True)
        raw = txt.read_text(encoding="utf-8", errors="ignore")
        can = canonicalise(raw)
        edits = {t["rule"]: t["edits"] for t in can["transformations"]}
        prof, letters = letter_profile(can["canonical"])
        subj, kind, years = classify(name, rec.get("title", ""))
        lam = lam_swap_diagnosis(raw.translate({c: None for c in BIDI}))
        rows[name] = {
            "subject": subj, "kind": kind, "years": years,
            "pages": rec.get("pages"), "bytes": rec.get("bytes"),
            "privacyClean": rec.get("privacy", {}).get("clean"),
            "rawChars": len(raw), "canonicalChars": len(can["canonical"]),
            "arabicLetters": letters,
            "edits": edits,
            "bidiPerKiloChar": round(1000 * edits.get("bidi", 0) / max(1, len(raw)), 1),
            "lettersRepairedBySwap": sorted(
                c for c, d in lam.items() if d["repair"]),
            "fonts": fonts(pdf) if pdf.exists() else None,
            "letterProfile": {c: round(100 * v, 3) for c, v in prof.items()},
            **fragmentation(can["canonical"]),
        }
        print(f"{letters:,} letters", flush=True)
        OUT.write_text(json.dumps({"documents": rows}, ensure_ascii=False,
                                  indent=1) + "\n", encoding="utf-8")
    # the reference is the pooled profile of documents that show no
    # substitution signature on the first pass -- computed, not assumed
    pooled = collections.Counter()
    weight = 0
    for r in rows.values():
        if r["arabicLetters"] > 50_000:
            for c, v in r["letterProfile"].items():
                pooled[c] += v * r["arabicLetters"]
            weight += r["arabicLetters"]
    ref = {c: pooled[c] / weight for c in PROBES} if weight else {}
    for name, r in rows.items():
        depressed = {}
        for c, v in r["letterProfile"].items():
            if ref.get(c, 0) > 0.05 and v * SUBSTITUTION_FACTOR < ref[c]:
                depressed[c] = {"observed": v, "reference": round(ref[c], 3),
                                "factor": round(ref[c] / max(v, 1e-6), 1)}
        r["depressedLetters"] = depressed
        frag = r.get("fragmentRate")
        r["corruption"] = (
            "substitution, dropped glyphs" if frag and frag >= FRAGMENT_RATE
            else "substitution" if depressed
            else "permutation only" if r["edits"].get("lam_swap")
            else "none detected")
    return {"reference": {c: round(v, 3) for c, v in ref.items()},
            "substitutionFactor": SUBSTITUTION_FACTOR,
            "documents": rows}


if __name__ == "__main__":
    a = audit()
    if "--json" in sys.argv:
        OUT.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
        print(f"{len(a['documents'])} documents -> {OUT.name}")
    else:
        d = a["documents"]
        print(f"{'document':34} {'subject':14} {'yrs':10} {'pages':>6} "
              f"{'arabic':>10} {'bidi/k':>7} {'swap':>6} {'brk':>6}  corruption")
        for name in sorted(d, key=lambda n: (d[n]["subject"] or "~", n)):
            r = d[name]
            print(f"{name:34} {(r['subject'] or '?'):14} "
                  f"{('-'.join(map(str, r['years'][:2])) or '?'):10} "
                  f"{(r['pages'] or 0):6d} {r['arabicLetters']:10,} "
                  f"{r['bidiPerKiloChar']:7.1f} "
                  f"{r['edits'].get('lam_swap', 0):6d} "
                  f"{r['edits'].get('brackets', 0):6d}  {r['corruption']}"
                  + ("  " + "".join(r["depressedLetters"]) if r["depressedLetters"] else ""))
