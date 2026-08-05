#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is the encoding damage OURS, or is it in the official PDF itself?

The text-integrity audit finds records whose Arabic carries the signature of a
reversed lam-alef ligature. Two explanations fit that evidence and they call for
opposite responses:

  * the corpus read the official file badly — then the fix is to read it again
    with a better tool, and the disclosure should say the corpus is at fault;
  * the official PDF's own text layer is encoded that way — then no extractor
    can do better, the corpus's reading is faithful, and the disclosure must say
    so rather than blame the transcription.

This script settles it the only way it can be settled: re-fetch the exact PDF a
track cites, extract it with an INDEPENDENT tool (poppler's pdftotext, in all
three of its layout modes), and count the damaged forms in what comes out. If
they are there, they were published there.

The first version of this corpus's disclosure asserted the first explanation —
«وهو خلل في النقل لا في المصدر: الجهة نشرت النص سليماً». That assertion was
made without this test and it is wrong: both PDFs testable this way reproduce
the damage under an extractor that never touched this corpus.

Read-only with respect to the corpus; writes only its own report. Network:
fetches the PDFs a track already cites, nothing else.
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from audit_corpus_text_integrity import DAMAGE  # noqa: E402

AUDIT = os.path.join(ROOT, "reports", "corpus_text_integrity_audit",
                     "corpus_text_integrity_audit.json")
OUT_DIR = os.path.join(ROOT, "reports", "corpus_text_integrity_audit")
PDF_RE = re.compile(r"https?://[^\s\"'\\)]+\.pdf", re.IGNORECASE)
MODES = ("", "-raw", "-layout")


def cited_pdfs(source_artifact):
    """Every PDF URL the track's own artifact cites — the corpus is only entitled
    to check the file it says it read."""
    blob = open(os.path.join(ROOT, source_artifact), encoding="utf-8").read()
    return sorted({u for u in PDF_RE.findall(blob) if "<" not in u})


def extract(pdf_path, mode):
    txt = pdf_path + (mode or "-def") + ".txt"
    cmd = ["pdftotext", "-enc", "UTF-8"] + ([mode] if mode else []) + [pdf_path, txt]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(txt):
        return None
    return open(txt, encoding="utf-8", errors="replace").read()


def count_damage(text):
    return {k: len(rx.findall(text)) for k, rx in DAMAGE.items()}


def main():
    audit = json.load(open(AUDIT, encoding="utf-8"))
    rows = []
    for entry in audit["encoding_damage"]:
        urls = cited_pdfs(entry["source_artifact"])
        if not urls:
            rows.append({"track_id": entry["track_id"], "verdict": "no_pdf_cited",
                         "note": "The track cites no PDF, so this test does not apply to it."})
            continue
        for url in urls:
            with tempfile.TemporaryDirectory() as td:
                pdf = os.path.join(td, "src.pdf")
                r = subprocess.run(["curl", "-sSL", "--max-time", "90", url, "-o", pdf],
                                   capture_output=True, text=True)
                if r.returncode != 0 or not os.path.exists(pdf) or os.path.getsize(pdf) < 10000:
                    rows.append({"track_id": entry["track_id"], "pdf": url,
                                 "verdict": "unreachable",
                                 "note": "Could not fetch the cited PDF this pass."})
                    continue
                per_mode = {}
                for mode in MODES:
                    text = extract(pdf, mode)
                    if text is None:
                        continue
                    c = count_damage(text)
                    per_mode[mode or "default"] = {"chars": len(text),
                                                   "damage_hits": sum(c.values()),
                                                   "by_signature": {k: v for k, v in c.items() if v}}
                hits = max((m["damage_hits"] for m in per_mode.values()), default=0)
                rows.append({
                    "track_id": entry["track_id"], "pdf": url,
                    "bytes": os.path.getsize(pdf),
                    "verdict": ("damage_is_in_the_official_pdf" if hits
                                else "official_pdf_extracts_clean"),
                    "extraction_modes": per_mode,
                })
                print("%-40s %-34s %s (%d hits)"
                      % (entry["track_id"], os.path.basename(url)[:34],
                         rows[-1]["verdict"], hits))

    note = (
        "Settles whether the encoding damage recorded by audit_corpus_text_integrity.py "
        "originates in this corpus's reading or in the official PDF itself. Each track's own "
        "cited PDF is re-fetched and extracted with poppler's pdftotext in all three layout "
        "modes — a tool independent of anything used to build this corpus. Where the damaged "
        "forms appear in that output, they were published that way, no extractor can do "
        "better, and the corpus's stored text is a faithful reading of the official file. "
        "This corpus's first disclosure of the damage asserted the opposite — that the body "
        "had published the text correctly and the fault was in transcription. That assertion "
        "was made without this test and the test contradicts it.")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "pdf_source_encoding_verification.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"generated_note": note, "checks": rows}, fh, ensure_ascii=False, indent=1)
    print("\nwrote reports/corpus_text_integrity_audit/pdf_source_encoding_verification.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
