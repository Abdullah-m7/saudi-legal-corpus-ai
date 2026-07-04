#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest the USER-PROVIDED official Arabic text candidate for the Saudi Companies Law
(Royal Decree M/132, 1443/12/01 AH) into structured, per-article records.

This does NOT verify the text against any official source. The result is an
`ingested_unverified` / `user_provided_official_text_candidate` layer: the full Arabic text
supplied by the owner, segmented into exactly 281 article records, each with a SHA-256 of its
verbatim `official_text_ar`. Nothing is marked verified; `article_by_article_verified` stays
false; official gazette / Bureau of Experts verification is still required (Phase E–F of
docs/official_arabic_text/OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md).

Segmentation
------------
Article headings are Markdown level-3 headings of the form `### المادة <ordinal>: <title>`.
Structural headings — `# الباب …` (books), `## الفصل …` (chapters), `### الفرع …`
(subsections) — and the Royal Decree / Council of Ministers preamble are NOT article records;
the preamble is preserved as source metadata. Each article's `official_text_ar` is the verbatim
text between its heading and the next Markdown heading of any level (horizontal-rule `---`
separators removed). Legal wording is preserved verbatim — nothing is rewritten, paraphrased,
normalized, or annotated.

Integrity
---------
Article numbers are assigned by document order (1..281) AND cross-checked against a generated
Arabic feminine-ordinal for each number (diacritic/hamza-normalized). The script FAILS if the
count is not exactly 281, if any heading's ordinal does not match its position (missing /
duplicated / out-of-order), or if any article body is empty.

Reads : inputs/official_arabic_companies_law_m132_1443_user_provided.md
Writes: data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json
"""

import hashlib
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SRC_REL = "inputs/official_arabic_companies_law_m132_1443_user_provided.md"
OUT_REL = "data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, OUT_REL)

LAW_ID = "sa-companies-law-m132-1443"
TARGET_ARTICLE_COUNT = 281
# Owner-side handoff hash (see PR notes). Recorded for transparency; the committed file's own
# hash is computed at runtime and both are stored so any drift is visible, not hidden.
OWNER_REPORTED_FILE_SHA256 = "8f75574b3aac2da6b2ed6ad50f13868760c2fe3cfabc78e3de3c1e1cd08fb1fc"

_NOTE = ("User-provided official Arabic text candidate. NOT yet verified against Umm Al-Qura or "
         "the Bureau of Experts at the Council of Ministers. Arabic is governing; this is the "
         "candidate official source pending article-by-article verification.")

# -- Arabic feminine ordinal generator (1..281) -----------------------------
_UNIT = ["", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة",
         "الثامنة", "التاسعة", "العاشرة"]
_UNIT_C = ["", "الحادية", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة",
           "الثامنة", "التاسعة"]
_TENS = {20: "العشرون", 30: "الثلاثون", 40: "الأربعون", 50: "الخمسون", 60: "الستون",
         70: "السبعون", 80: "الثمانون", 90: "التسعون"}


def _base(n):
    if 1 <= n <= 10:
        return _UNIT[n]
    if 11 <= n <= 19:
        return _UNIT_C[n - 10] + " عشرة"
    if n in _TENS:
        return _TENS[n]
    u = n % 10
    return _UNIT_C[u] + " و" + _TENS[n - u]


def arabic_ordinal(n):
    if n <= 99:
        return _base(n)
    if n == 100:
        return "المائة"
    if n < 200:
        return _base(n - 100) + " بعد المائة"
    if n == 200:
        return "المائتان"
    return _base(n - 200) + " بعد المائتين"


def _norm(s):
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ـ", "")
    for a in "أإآ":
        s = s.replace(a, "ا")
    s = s.replace("ى", "ي")
    return re.sub(r"\s+", " ", s).strip()


_ART_RE = re.compile(r"^###\s+المادة\s+(.+?)\s*$")
_ANY_HEADING_RE = re.compile(r"^#{1,6}\s+")

# Non-statutory source-packet boundary / commentary markers. Lines containing any of these
# are NOT article text and are excluded from official_text_ar. These phrases never occur in
# genuine statutory article wording, so a keyword match is safe.
PACKET_MARKER_KEYWORDS = (
    "نهاية النص", "النص المرشح", "نهاية الملف", "نهاية الحزمة",
    "source packet", "end of packet", "end of file", "end of text",
)


def is_packet_marker(line):
    s = line.strip()
    if not s:
        return False
    low = s.lower()
    return any(k.lower() in low for k in PACKET_MARKER_KEYWORDS)


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse(md_text):
    lines = md_text.split("\n")
    # locate article heading line indices
    art_idx = [i for i, ln in enumerate(lines) if _ART_RE.match(ln.strip())]
    if len(art_idx) != TARGET_ARTICLE_COUNT:
        raise SystemExit("expected %d article headings, found %d" % (TARGET_ARTICLE_COUNT, len(art_idx)))

    preamble = "\n".join(lines[: art_idx[0]]).strip()

    records = []
    for pos, start in enumerate(art_idx):
        n = pos + 1
        head = _ART_RE.match(lines[start].strip()).group(1).strip()
        ordinal, _, title = head.partition(":")
        ordinal = ordinal.strip()
        title = title.strip()
        # integrity: heading ordinal must equal the generated ordinal for this position
        if _norm(ordinal) != _norm(arabic_ordinal(n)):
            raise SystemExit("article %d: ordinal mismatch (heading %r != expected %r) — "
                             "missing/duplicated/out-of-order" % (n, ordinal, arabic_ordinal(n)))
        # body = lines after the heading, up to the next markdown heading of any level
        j = start + 1
        body_lines = []
        while j < len(lines) and not _ANY_HEADING_RE.match(lines[j]):
            body_lines.append(lines[j])
            j += 1
        # drop markdown horizontal-rule separators and non-statutory source-packet boundary /
        # commentary markers; keep all legal text verbatim
        body_lines = [b for b in body_lines
                      if b.strip() not in ("---", "***", "___") and not is_packet_marker(b)]
        body = "\n".join(body_lines).strip()
        if not body:
            raise SystemExit("article %d (%s): empty official_text_ar" % (n, ordinal))
        records.append({
            "law_id": LAW_ID,
            "article_number": n,
            "article_title_ar": title or ordinal,
            "official_text_ar": body,
            "source_authority": "user_provided_text_claimed_official_pending_gazette_or_boe_verification",
            "source_publication": "Companies Law, Royal Decree No. (M/132), dated 1443/12/01 AH",
            "royal_decree_number": "م/132",
            "royal_decree_date_hijri": "1443/12/01",
            "official_gazette_name": "pending_verification",
            "source_file": SRC_REL,
            "extraction_method": "direct_user_provided_markdown_packet",
            "verification_status": "ingested_unverified",
            "manual_review_status": "needs_manual_check",
            "text_hash_sha256": _sha256(body),
            "notes": _NOTE,
        })
    return preamble, records


def main():
    with open(SRC, "r", encoding="utf-8") as fh:
        md = fh.read()
    file_sha = hashlib.sha256(md.encode("utf-8")).hexdigest()
    preamble, records = parse(md)

    nums = [r["article_number"] for r in records]
    assert nums == list(range(1, TARGET_ARTICLE_COUNT + 1)), "article numbers must be 1..281 in order"
    assert records[0]["article_title_ar"] == "التعريفات", records[0]["article_title_ar"]
    assert records[-1]["article_title_ar"] == "نفاذ النظام", records[-1]["article_title_ar"]
    for r in records:
        assert r["verification_status"] == "ingested_unverified", r["article_number"]
        assert r["text_hash_sha256"] == _sha256(r["official_text_ar"]), r["article_number"]

    payload = {
        "layer_id": "sa-companies-official-arabic-user-provided",
        "law_id": LAW_ID,
        "source_status": "user_provided_official_text_candidate",
        "official_arabic_text_status": "user_provided_source_ingested",
        "verification_status": "ingested_unverified",
        "article_by_article_verified": False,
        "source_authority": "user_provided_text_claimed_official_pending_gazette_or_boe_verification",
        "source_publication_reference": "Companies Law, Royal Decree No. (M/132), dated 1443/12/01 AH",
        "source_url_or_file_reference": SRC_REL,
        "extraction_method": "direct_user_provided_markdown_packet",
        "target_article_count": TARGET_ARTICLE_COUNT,
        "articles_ingested": len(records),
        "articles_verified": 0,
        "raw_source_file": {
            "path": SRC_REL,
            "sha256_committed": file_sha,
            "sha256_owner_reported": OWNER_REPORTED_FILE_SHA256,
            "file_hash_matches_owner_report": file_sha == OWNER_REPORTED_FILE_SHA256,
            "note_en": ("SHA-256 of the committed raw packet. If it differs from the owner-reported "
                        "hash, the byte-level file differs (e.g. markdown re-serialized on upload) — "
                        "surfaced here for reconciliation. The 281-article content (count, sequence, "
                        "first/last article) was checked and each article carries its own text hash.")
        },
        "source_preamble_ar": preamble,
        "disclaimer_en": ("User-provided official Arabic text candidate, ingested unverified. NOT "
                          "verified against Umm Al-Qura or the Bureau of Experts. Arabic remains "
                          "governing. Current Arabic summaries remain secondary/non-official until "
                          "verification and reconciliation. Not legal advice."),
        "articles": records,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d official Arabic (user-provided, unverified) article records"
          % (OUT, len(records)))
    print("committed raw-file sha256: %s (owner-reported: %s; match=%s)"
          % (file_sha, OWNER_REPORTED_FILE_SHA256, file_sha == OWNER_REPORTED_FILE_SHA256))


if __name__ == "__main__":
    main()
