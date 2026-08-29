#!/usr/bin/env python3
"""Scan a text for personal data, before it is collected in bulk.

This runs on a sample and gates collection; it is not a post-hoc audit. Two
normalisation steps are compulsory and both were learned by getting the
answer wrong on the first Saudi tax-committee digest:

  digits    Arabic-Indic ٠١٢٣ and Extended Arabic-Indic ۰۱۲۳ are different
            code points from 0123. A pattern written in Latin digits reports
            zero on a document written in Arabic ones, and zero is exactly
            the answer that makes a collector proceed.

  bidi      Arabic PDFs carry Unicode bidirectional control characters --
            LRE, RLE, PDF, LRI..PDI -- between a number and the words around
            it. The first digest carried 109,258 of them in 1.56 million
            characters. Any pattern that spans a digit and its context is
            broken by them silently.

A scan that returns zero for a reason other than absence is worse than no
scan, so both normalisations are applied before any pattern runs, and the
report states what it normalised.

    python3 privacy_scan.py FILE [FILE ...]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ARABIC_INDIC = "٠١٢٣٤٥٦٧٨٩"
EXTENDED_ARABIC_INDIC = "۰۱۲۳۴۵۶۷۸۹"
DIGITS = str.maketrans(ARABIC_INDIC + EXTENDED_ARABIC_INDIC, "0123456789" * 2)
BIDI = {0x200E, 0x200F, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
        0x2066, 0x2067, 0x2068, 0x2069, 0x061C}

# Each pattern is a thing a Saudi legal document could carry that a bulk
# republication would aggregate into a risk it does not carry one at a time.
PATTERNS = {
    "national_or_iqama_id": r"(?<!\d)[12]\d{9}(?!\d)",
    "any_ten_digit_run": r"(?<!\d)\d{10}(?!\d)",
    "vat_number_15": r"(?<!\d)\d{15}(?!\d)",
    "saudi_mobile": r"(?<!\d)(?:\+?966|00966|0)5\d{8}(?!\d)",
    "iban_sa": r"\bSA\d{22}\b",
    "email": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    "url_with_query": r"https?://\S+\?\S+",
}
# Arabic labels that mark a field where a person is usually named.
LABELS = ["رقم الهوية", "الهوية الوطنية", "رقم السجل", "السجل التجاري",
          "الرقم الضريبي", "المدعي", "المدعى عليه", "المكلف", "الجوال",
          "البريد الإلكتروني", "العنوان الوطني", "رقم الحساب", "الآيبان"]


def normalise(text):
    stripped = text.translate({c: None for c in BIDI})
    return stripped.translate(DIGITS), len(text) - len(stripped)


def _fingerprint(value):
    """A stable, non-reversing reference to a hit, so a report never carries it.

    The first version of this scanner put the matched strings in its output,
    and the output is a committed manifest. Two of twelve tax digests carry an
    identifier the publisher failed to redact -- in one case a national ID
    beside a named person, in a document where thirty-three other instances
    are masked -- so the report itself would have republished exactly what the
    gate exists to stop.
    """
    import hashlib
    return (f"{len(value)}-char {'digits' if value.isdigit() else 'mixed'} "
            f"#{hashlib.sha256(value.encode()).hexdigest()[:12]}")


def scan(text, name="<text>"):
    clean, bidi_removed = normalise(text)
    hits = {k: [_fingerprint(v) for v in sorted(set(re.findall(p, clean)))[:5]]
            for k, p in PATTERNS.items()}
    counts = {k: len(re.findall(p, clean)) for k, p in PATTERNS.items()}
    labels = {lab: clean.count(lab) for lab in LABELS if clean.count(lab)}
    runs = {}
    for m in re.findall(r"\d+", clean):
        runs[len(m)] = runs.get(len(m), 0) + 1
    return {
        "name": name,
        "characters": len(text),
        "bidiControlsRemoved": bidi_removed,
        "arabicIndicDigits": sum(text.count(c) for c in ARABIC_INDIC),
        "digitRunLengths": dict(sorted(runs.items())),
        "counts": counts,
        "samples": {k: v for k, v in hits.items() if v},
        "labelsPresent": labels,
        "clean": all(v == 0 for v in counts.values()),
    }


def main(argv):
    if not argv:
        sys.exit(__doc__)
    out = [scan(Path(p).read_text(encoding="utf-8", errors="ignore"), p)
           for p in argv]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if not all(r["clean"] for r in out):
        print("\nREFUSING: personal-data patterns matched. Do not collect in "
              "bulk until each match is explained.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
