#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR the OFFICIAL scanned Arabic PDF packet (Umm Al-Qura / Bureau of Experts — Companies Law,
M/132, 1443H) into a per-page text artifact for the verification-comparison stage.

The packet is a set of scanned-image PDF parts (no text layer). This script rasterizes each
page (PyMuPDF, 300 DPI) and OCRs it with Tesseract (`-l ara`). It writes a deterministic
per-page artifact that the (OCR-free) comparison + validator scripts and the tests read.

Requires: PyMuPDF (`fitz`) and the `tesseract` binary with the `ara` language pack. These are
NOT required by the comparison/validator/tests (which read the committed artifact), so CI does
not need OCR tooling. Run this once when the packet changes; commit the artifact.

Reads : inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/*.pdf
Writes: reports/official_arabic_verification/ocr_source_pages.json
"""

import glob
import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARTS_DIR = os.path.join(ROOT, "inputs", "official_arabic_verification",
                         "nizam_alsharikat_1443h_parts")
OUT = os.path.join(ROOT, "reports", "official_arabic_verification", "ocr_source_pages.json")
DPI = 300
LANG = "ara"
PSM = 3


def main():
    import fitz  # PyMuPDF — only needed to (re)generate the artifact
    parts = sorted(glob.glob(os.path.join(PARTS_DIR, "*.pdf")))
    if not parts:
        raise SystemExit("no PDF parts under %s" % PARTS_DIR)
    pages = []
    gpn = 0
    for f in parts:
        doc = fitz.open(f)
        for i in range(len(doc)):
            gpn += 1
            pix = doc[i].get_pixmap(dpi=DPI)
            tmp = tempfile.mktemp(suffix=".png")
            pix.save(tmp)
            r = subprocess.run(["tesseract", tmp, "stdout", "-l", LANG, "--psm", str(PSM)],
                               capture_output=True, text=True)
            os.remove(tmp)
            pages.append({"global_page": gpn, "part_file": os.path.basename(f),
                          "part_page_index": i + 1, "text": r.stdout})
    payload = {
        "source": "nizam_alsharikat_1443h scanned official Arabic PDF (single packet, split for upload)",
        "packet_dir": "inputs/official_arabic_verification/nizam_alsharikat_1443h_parts",
        "dpi": DPI, "engine": "tesseract", "lang": LANG, "psm": PSM,
        "page_count": len(pages), "pages": pages,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s (%d pages OCR'd, %s @ %d dpi, lang=%s)" % (OUT, len(pages), "tesseract", DPI, LANG))


if __name__ == "__main__":
    main()
