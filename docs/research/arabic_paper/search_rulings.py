#!/usr/bin/env python3
"""Search the published Saudi zakat, tax and customs board decisions.

Paper 3 found four widely shared statutory terms that genuinely conflict:
المملكة, المستهلك, النشاط, المنشأة. Two of them - المملكة and النشاط - are
anchored in fiscal instruments (Income Tax, VAT, RETT, Zakat), which is why
this source comes first: it is where the conflict actually litigates, and it
is the only Saudi adjudicating body that publishes its decisions as
machine-readable PDFs rather than as a portal.

    https://gstc.gov.sa/ar/DocumentsLb/DecisionsRules/Pages/default.aspx

THE TRAP THIS SCRIPT EXISTS TO AVOID
------------------------------------
pdftotext transposes the pair "لم" into "مل" throughout these files. So a
plain search for المملكة returns zero and a plain search for المقدمة returns
zero, in a document that contains each of them scores of times. Measured on
the 2024 VAT volume: المملكة 0 hits, its transposed form اململكة 141.

A null result from a broken search is worse than no search at all. It would
have been reported as "the boards have never addressed this", which is the
opposite of what the record shows. So every query is run in both forms, and
the script refuses to report a zero it has not tested both ways.

The repair is applied to the QUERY, never to the text: rewriting "مل" back to
"لم" across the corpus would corrupt every genuine word containing it - عمل,
أمل, عامل, حمل - and quietly invent hits.

Usage
    python3 search_rulings.py --limit 8       # a bounded trial
    python3 search_rulings.py                 # the whole set

Downloads are cached, so a second run costs nothing. Text is kept, PDFs are
discarded once read.
"""

import argparse
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "rulings_cache"
INDEX = "https://gstc.gov.sa/ar/DocumentsLb/DecisionsRules/Pages/default.aspx"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")
DELAY = 3.0  # seconds between requests, unprompted by any robots directive

# The four terms paper 3 adjudicated as substantively conflicting, and the
# vocabulary a decision would use when it has to choose between definitions.
TERMS = ["المملكة", "المستهلك", "النشاط", "المنشأة"]
CONFLICT_WORDS = [
    "تعريف", "التعريف", "المقصود بـ", "مدلول", "نطاق تطبيق",
    "تعارض", "التعارض", "الخاص يقيد العام", "يقيد العام",
    "التكييف", "تكييف الدعوى", "المادة الأولى",
]


def transpose(text: str) -> str:
    """Apply the extractor's own corruption to a query so it can be found."""
    return text.replace("لم", "مل")


def variants(term: str):
    """The term as written and as the extractor renders it, deduplicated."""
    return list(dict.fromkeys([term, transpose(term)]))


def strip_marks(text: str) -> str:
    """Remove bidi controls and tatweel; leave letters alone."""
    text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return text.replace("ـ", "")


def fetch(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    r = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "120",
                        "-o", str(dest), url], capture_output=True, text=True)
    time.sleep(DELAY)
    if r.returncode != 0 or not dest.exists() or dest.stat().st_size < 1024:
        dest.unlink(missing_ok=True)
        return False
    return True


def pdf_urls():
    page = CACHE / "_index.html"
    if not fetch(INDEX, page):
        sys.exit("could not retrieve the index page")
    html = page.read_text(encoding="utf-8", errors="replace")
    found = re.findall(r'SourceUrl=(https://[^"&]+\.pdf)', html)
    return list(dict.fromkeys(urllib.parse.unquote(u) for u in found))


def text_of(url: str):
    """Download, extract, cache the text; discard the PDF."""
    name = re.sub(r"[^A-Za-z0-9._-]", "_", url.rsplit("/", 1)[-1])
    txt_path = CACHE / (name + ".txt")
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8", errors="replace")
    pdf_path = CACHE / name
    if not fetch(url, pdf_path):
        return None
    out = subprocess.run(["pdftotext", str(pdf_path), "-"],
                         capture_output=True, text=True)
    pdf_path.unlink(missing_ok=True)
    if out.returncode != 0:
        return None
    text = strip_marks(out.stdout)
    txt_path.write_text(text, encoding="utf-8")
    return text


def snippets(text: str, needle: str, width=140):
    """Every occurrence, not a sample.

    An earlier version stopped after three. Scanning three of the 298 places
    a term appears and reporting no co-occurrence is how a search invents the
    finding that the boards have never addressed the question. Truncation
    belongs in what gets printed, never in what gets examined.
    """
    out = []
    for m in re.finditer(re.escape(needle), text):
        a, b = max(0, m.start() - width), m.end() + width
        out.append(" ".join(text[a:b].split()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="stop after N documents")
    args = ap.parse_args()

    CACHE.mkdir(exist_ok=True)
    urls = pdf_urls()
    print(f"{len(urls)} documents published on the boards' site")
    if args.limit:
        urls = urls[:args.limit]
        print(f"reading the first {len(urls)} of them\n")

    results, read, failed = [], 0, []
    for i, url in enumerate(urls, 1):
        name = url.rsplit("/", 1)[-1]
        text = text_of(url)
        if text is None:
            failed.append(name)
            print(f"  [{i}/{len(urls)}] {name}: could not read")
            continue
        read += 1
        hits = {}
        for term in TERMS + CONFLICT_WORDS:
            total = sum(text.count(v) for v in variants(term))
            if total:
                hits[term] = total
        results.append({"document": name, "url": url,
                        "characters": len(text), "hits": hits})
        top = ", ".join(f"{k} {v}" for k, v in
                        sorted(hits.items(), key=lambda x: -x[1])[:4]) or "nothing"
        print(f"  [{i}/{len(urls)}] {name}: {top}")

    # Where a conflicting term and conflict vocabulary sit close together is
    # where a decision may actually be choosing between two definitions.
    leads, scanned = [], 0
    for r in results:
        text = (CACHE / (re.sub(r"[^A-Za-z0-9._-]", "_",
                                r["document"]) + ".txt")).read_text(
                                    encoding="utf-8", errors="replace")
        for term in TERMS:
            if term not in r["hits"]:
                continue
            for v in variants(term):
                for passage in snippets(text, v):
                    scanned += 1
                    matched = [w for w in CONFLICT_WORDS
                               if w in passage or transpose(w) in passage]
                    if matched:
                        leads.append({"document": r["document"], "term": term,
                                      "matched": matched, "passage": passage})

    out = {
        "source": INDEX,
        "documents_published": len(pdf_urls()),
        "documents_read": read,
        "documents_unreadable": failed,
        "terms": TERMS,
        "conflict_vocabulary": CONFLICT_WORDS,
        "extraction_note": (
            "pdftotext transposes لم into مل in these files; every query was "
            "run in both forms. A zero here means both forms were absent."),
        "passages_examined": scanned,
        "per_document": results,
        "leads": leads,
    }
    (HERE / "rulings_search_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nread {read} of {len(urls)}; examined {scanned} passages; "
          f"{len(leads)} pair a conflicting term with conflict vocabulary")
    print("wrote rulings_search_results.json")
    if failed:
        print(f"unreadable, and excluded from every count: {', '.join(failed)}")


if __name__ == "__main__":
    main()
