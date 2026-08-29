#!/usr/bin/env python3
"""Pilot collector: the Zakat, Tax and Customs Committees' published digests.

A separate population from the courts. These are quasi-judicial committees,
not a judiciary, and nothing collected here may enter a denominator built
from court judgments.

SOURCE CONTRACT
---------------
authority            الأمانة العامة للجان الزكوية والضريبية والجمركية
                     (General Secretariat of the Zakat, Tax and Customs
                     Committees)
landing page         https://gstc.gov.sa/ar/DocumentsLb/DecisionsRules/Pages/
                     default.aspx
retrieval route      GET the direct document path. The landing page links each
                     digest through /_layouts/download.aspx?SourceUrl=..., and
                     robots.txt disallows /_layouts/ -- so the wrapper is not
                     used and the SourceUrl it carries is fetched directly.
                     That path, /ar/DocumentsLb/DecisionsRules/Documents/NN.pdf,
                     is not disallowed.
robots.txt           Disallow: /_layouts/, /_vti_bin/, /_catalogs/. Read on
                     29 August 2026 and respected.
record identifier    the digest's file number on that path. There is no
                     per-decision identifier in the source; a decision is
                     located by digest and page.
body                 committee (first instance and appeal), not a court
adjudication level   stated in each digest's own title, not inferred
dates                the publisher redacts dates to .../.../... in the body;
                     the covered period appears in the digest title
text components      one PDF per digest, containing many decisions
appeal/final status  not machine-readable; a digest may be first-instance or
                     appeal committee decisions, per its title
publication scope    SELECTED, not exhaustive. These are digests the
                     Secretariat chose to publish. Nothing here supports a
                     rate, a share of filings, or any denominator.
privacy              identifiers are redacted AT SOURCE: names as .../,
                     ID numbers as ( )..., dates as .../.../... . Verified by
                     privacy_scan.py before collection, not after.
transformations      PDF -> text by pdftotext -enc UTF-8; bidi controls and
                     Arabic-Indic digits normalised at read time, never in
                     the stored artefact.
discrepancies        recorded per digest in the manifest when the page count
                     or byte length differs from what the landing page implies

WHAT IS AND IS NOT KEPT
-----------------------
The PDFs and their extracted text are written to a git-ignored directory.
Only the manifest -- hashes, sizes, provenance, privacy result -- is
committed. «Publicly available» is not «appropriate to republish in bulk»,
and the collector is reproducible from the manifest alone.

    python3 collect.py --list            what the landing page offers
    python3 collect.py --pilot 3         fetch the first three, with the gate
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from privacy_scan import scan  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"                 # git-ignored
MANIFEST = HERE / "manifest.json"
LANDING = ("https://gstc.gov.sa/ar/DocumentsLb/DecisionsRules/Pages/"
           "default.aspx")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
DELAY = 2.0        # slower than the publisher asks, because nothing here is urgent


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get(url, out=None, tries=3):
    """Fetch, with every attempt accounted for. Never returns silently empty."""
    # curl's -w output is appended to the body on stdout, so it needs a marker
    # a Content-Type cannot be mistaken for. Parsing it by splitting on spaces
    # read «text/html; charset=utf-8» as three fields and reported the byte
    # count as the status code -- a live page as unreachable.
    MARK = "\n@@CURL@@ "
    attempts = []
    for i in range(1, tries + 1):
        cmd = ["curl", "-s", "--max-time", "120", "-A", UA,
               "-w", MARK + "%{http_code}", url]
        if out:
            cmd[1:1] = ["-o", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        head, _, code = (r.stdout or "").rpartition(MARK)
        code = code.strip() or "000"
        attempts.append({"attempt": i, "status": code, "at": now()})
        if code == "200":
            return (None if out else head), attempts
        time.sleep(DELAY * i)
    return None, attempts


def listing():
    """Every digest the landing page links, by its direct document path."""
    body, attempts = get(LANDING)
    if body is None:
        sys.exit(f"landing page unreachable: {attempts}")
    urls = set()
    for href in re.findall(r'href="([^"]+)"', body):
        if "SourceUrl=" in href and ".pdf" in href.lower():
            src = urllib.parse.unquote(
                re.search(r"SourceUrl=([^\"&]+)", href).group(1))
            urls.add(src)
        elif href.lower().endswith(".pdf") and "/_layouts/" not in href:
            urls.add(urllib.parse.urljoin(LANDING, href))
    return sorted(urls), attempts


def text_of(pdf):
    txt = pdf.with_suffix(".txt")
    subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), str(txt)],
                   capture_output=True)
    return txt if txt.exists() else None


def pages(pdf):
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    m = re.search(r"Pages:\s+(\d+)", r.stdout)
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pilot", type=int, default=0,
                    help="fetch this many digests, smallest file number first")
    a = ap.parse_args()

    urls, listing_attempts = listing()
    if a.list or not a.pilot:
        print(f"{len(urls)} digests offered by the landing page")
        for u in urls:
            print("  ", u)
        return

    RAW.mkdir(exist_ok=True)
    records, refused = [], []
    for url in urls[: a.pilot]:
        name = url.rsplit("/", 1)[-1]
        pdf = RAW / name
        print(f"{name} …", end=" ", flush=True)
        _, attempts = get(url, out=pdf)
        if not pdf.exists() or pdf.stat().st_size == 0:
            print("FAILED")
            records.append({"file": name, "url": url, "retrieved": False,
                            "attempts": attempts})
            continue
        txt = text_of(pdf)
        body = txt.read_text(encoding="utf-8", errors="ignore") if txt else ""
        privacy = scan(body, name)
        rec = {
            "file": name,
            "url": url,
            "retrieved": True,
            "retrievedAt": now(),
            "attempts": attempts,
            "bytes": pdf.stat().st_size,
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "pages": pages(pdf),
            "characters": len(body),
            "title": " ".join(body.split()[:14]),
            "privacy": {k: privacy[k] for k in
                        ("counts", "samples", "labelsPresent",
                         "bidiControlsRemoved", "arabicIndicDigits", "clean")},
        }
        records.append(rec)
        if not privacy["clean"]:
            refused.append(name)
        print(f"{rec['pages']} pages, "
              f"{'clean' if privacy['clean'] else 'PRIVACY HIT'}")
        time.sleep(DELAY)

    out = {
        "source": "General Secretariat of the Zakat, Tax and Customs Committees",
        "population": "quasi-judicial committee decisions, not court judgments",
        "landingPage": LANDING,
        "landingAttempts": listing_attempts,
        "digestsOffered": len(urls),
        "digestsAttempted": len(records),
        "digestsRetrieved": sum(1 for r in records if r["retrieved"]),
        "digestsFailed": [r["file"] for r in records if not r["retrieved"]],
        "privacyRefusals": refused,
        "collectedAt": now(),
        "records": records,
        "allOfferedUrls": urls,
    }
    MANIFEST.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"\n{out['digestsRetrieved']}/{out['digestsAttempted']} retrieved, "
          f"{len(refused)} refused on privacy, manifest written")
    if refused:
        sys.exit("REFUSING to proceed: privacy patterns matched")


if __name__ == "__main__":
    main()
