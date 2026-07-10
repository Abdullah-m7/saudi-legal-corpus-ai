#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate cleaned Arabic text for the PDPL Implementing Regulation (38 articles).

The article inventory (``pdpl_implementing_regulation_arabic_article_inventory.jsonl``)
carries ``article_text_extracted`` taken directly from a two-column PDF text
extraction.  That extraction is faithful in its body sentences but carries a
narrow, systematic set of structural artifacts:

  * the leading title line of each article is word-order reversed (the clean
    title already exists, verified, in ``arabic_heading``);
  * the reversed title of the *next* article bleeds into the tail of most
    articles at the page/column boundary;
  * Article 1 (definitions) has its short term-labels word-order reversed;
  * stray extraction markers ( ! % & # " * + ( ) $ ' etc.), running-header
    ``عام`` lines, and displaced line-initial diacritics are scattered through
    the text;
  * numbered / lettered list markers are split across physical lines.

This generator removes those artifacts deterministically.  It never reorders,
drops, or rewrites body sentences: the legal content is the extraction's body
verbatim, only de-noised.  Because the output is not a certified line-by-line
transcription of the official gazette, ``official_text_status`` stays
``EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT`` — the cleaning is structural only.

Arabic is the governing source.  No translation, no legal interpretation, and no
use of any English text is performed.

Read-only over its inputs; deterministic and idempotent over its outputs.
"""

from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTORY = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "inventory",
    "pdpl_implementing_regulation_arabic_article_inventory.jsonl",
)
OUT_DIR = os.path.join(ROOT, "sources", "pdpl", "regulation", "cleaned")
RECORDS_PATH = os.path.join(
    OUT_DIR, "pdpl_implementing_regulation_arabic_cleaned_records.jsonl")
SUMMARY_PATH = os.path.join(
    OUT_DIR, "pdpl_implementing_regulation_arabic_cleaned_summary.json")

SOURCE_PDF_SHA256 = "4b4b24e3bcb744a04a39a65d890454fc63ea282be85501af125d5f36134919df"

# Article 1 definition term-labels: reversed extraction form -> correct form.
ART1_LABELS = [
    ("المباشر التسويق", "التسويق المباشر"),
    ("الشخصية البيانات تسرب", "تسرب البيانات الشخصية"),
    ("الحيوية المصلحة", "المصلحة الحيوية"),
    ("المتحققة المصلحة", "المصلحة المتحققة"),
    ("المشروعة المصلحة", "المصلحة المشروعة"),
    ("الهوية إخفاء", "إخفاء الهوية"),
    ("الصريحة الموافقة", "الموافقة الصريحة"),
]

ARTIFACT_CHARS = "!%&#\"*+()$'@~^`|{}[]<>§"
COMBINING = r"[ً-ْٰ]"

# Reversed-title residue lines that survive the heading-word-set strip because
# the reversed form uses different word morphology than the clean heading.
# Identified by manual review; matched by denoised token tuple, any position.
RESIDUE_TOKEN_TUPLES = {
    ("الشخصية", "البيانات", "أصحاب", "لحقوق", "العامة", "الأحكام"),
    ("الشخصية", "البيانات", "إتلاف", "طلب", "ي"),
    ("متحققة", "لمصلحة", "الشخصية", "البيانات", "معالجة", "عشرة"),
    ("والعشرون", "الحادية", "المادة", "العامة", "المصلحة",
     "لأغراض", "الشخصية", "البيانات", "معالجة", "ضوابط"),
    ("الأثر", "تقويم", "والعشرون"),
    ("والثلاثون", "السابعة", "تقديم", "الشكاوى", "و"),
}

BARE_MARKER = re.compile(r"^(?:\d+\s*-?|-|[ء-ي]\s*-)$")


def _denoise_token(t: str) -> str:
    for c in ARTIFACT_CHARS:
        t = t.replace(c, "")
    return t.strip().strip(":：").strip()


def _tok_tuple(s: str):
    return tuple(t for t in (_denoise_token(x) for x in s.split()) if t)


def _is_artifact_line(s: str) -> bool:
    z = s.strip()
    if z == "" or z == "عام":
        return True
    return all(
        (c in ARTIFACT_CHARS) or c.isspace() or c in ":：ـ."
        for c in z
    ) and not any(ch.isalnum() for ch in z if ch not in "٠١٢٣٤٥٦٧٨٩")


def _head_wordset(heading: str):
    ws = set()
    for w in re.split(r"[\s:：()]+", heading):
        w = _denoise_token(w)
        if w:
            ws.add(w)
    ws.add("المادة")
    return ws


def clean_article(row: dict, next_heading: str | None):
    """Return (cleaned_text, operations) for one inventory record."""
    heading = row["arabic_heading"]
    this_ws = _head_wordset(heading)
    next_ws = _head_wordset(next_heading) if next_heading else set()
    text = row["article_text_extracted"]

    ops = {
        "article1_label_corrections": 0,
        "explicit_reversed_title_lines_removed": 0,
        "leading_title_lines_removed": 0,
        "trailing_title_lines_removed": 0,
        "artifact_only_lines_removed": 0,
        "artifact_chars_stripped": 0,
        "line_initial_combining_marks_stripped": 0,
        "bare_list_markers_merged": 0,
    }

    if row["article_number"] == 1:
        for bad, good in ART1_LABELS:
            if bad in text:
                ops["article1_label_corrections"] += text.count(bad)
                text = text.replace(bad, good)

    lines = text.split("\n")

    kept_after_residue = []
    for ln in lines:
        if _tok_tuple(ln) in RESIDUE_TOKEN_TUPLES:
            ops["explicit_reversed_title_lines_removed"] += 1
            continue
        kept_after_residue.append(ln)
    lines = kept_after_residue

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s == "":
            i += 1
            continue
        toks = [t for t in (_denoise_token(x) for x in s.split()) if t]
        if toks and all(t in this_ws for t in toks):
            ops["leading_title_lines_removed"] += 1
            i += 1
            continue
        if _is_artifact_line(s):
            i += 1
            continue
        break

    j = len(lines) - 1
    while j >= i:
        s = lines[j].strip()
        if s == "":
            j -= 1
            continue
        if _is_artifact_line(s):
            j -= 1
            continue
        toks = [t for t in (_denoise_token(x) for x in s.split()) if t]
        if next_ws and toks and all(t in next_ws for t in toks):
            ops["trailing_title_lines_removed"] += 1
            j -= 1
            continue
        break

    core = lines[i:j + 1]

    kept = []
    for ln in core:
        if _is_artifact_line(ln):
            ops["artifact_only_lines_removed"] += 1
            continue
        s = ln
        for c in ARTIFACT_CHARS:
            if c in s:
                ops["artifact_chars_stripped"] += s.count(c)
                s = s.replace(c, " ")
        new_s = re.sub(r"^\s*" + COMBINING + r"+", "", s)
        if new_s != s:
            ops["line_initial_combining_marks_stripped"] += 1
        s = re.sub(r"[ \t]+", " ", new_s).strip()
        if s:
            kept.append(s)

    merged = []
    k = 0
    while k < len(kept):
        if BARE_MARKER.match(kept[k]):
            mk = ""
            while k < len(kept) and BARE_MARKER.match(kept[k]):
                mk += kept[k].replace(" ", "")
                k += 1
            mk = mk.rstrip("-")
            if re.fullmatch(r"\d+|[ء-ي]", mk):
                mk = mk + "-"
            if k < len(kept):
                ops["bare_list_markers_merged"] += 1
                merged.append(mk + " " + kept[k])
                k += 1
            else:
                merged.append(mk)
        else:
            merged.append(kept[k])
            k += 1

    body = "\n".join(merged)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body, ops


def build_records():
    rows = [json.loads(l) for l in open(INVENTORY, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["article_number"])
    by_num = {r["article_number"]: r for r in rows}

    records = []
    for row in rows:
        num = row["article_number"]
        nxt = by_num.get(num + 1)
        cleaned, ops = clean_article(row, nxt["arabic_heading"] if nxt else None)
        records.append({
            "law_key": "pdpl",
            "law_component": "implementing_regulation",
            "language": "ar",
            "record_layer": "PDPL_IMPLEMENTING_REGULATION_ARABIC_CLEANED_TEXT",
            "article_number": num,
            "article_key": row["article_key"],
            "arabic_heading": row["arabic_heading"],
            "article_text_cleaned": cleaned,
            "article_text_source_field": "article_text_extracted",
            "source_inventory_file": os.path.relpath(INVENTORY, ROOT),
            "source_pdf_sha256": SOURCE_PDF_SHA256,
            "cleaning_operations": ops,
            "text_cleaning_status": "STRUCTURAL_EXTRACTION_ARTIFACTS_REMOVED",
            "official_text_status": "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT",
            "governing_source_note": (
                "Arabic is the governing source. Body sentences are the "
                "inventory extraction verbatim; only reversed title lines and "
                "extraction artifacts were removed. Not a certified official "
                "transcription."
            ),
            "english_used_for_correction": False,
            "translation_performed": False,
            "legal_interpretation_performed": False,
        })
    return records


def main():
    records = build_records()
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(RECORDS_PATH, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    totals = {}
    for rec in records:
        for k, v in rec["cleaning_operations"].items():
            totals[k] = totals.get(k, 0) + v

    summary = {
        "law_key": "pdpl",
        "law_component": "implementing_regulation",
        "language": "ar",
        "layer": "PDPL_IMPLEMENTING_REGULATION_ARABIC_CLEANED_TEXT",
        "record_count": len(records),
        "article_number_range": [records[0]["article_number"],
                                 records[-1]["article_number"]],
        "source_inventory_file": os.path.relpath(INVENTORY, ROOT),
        "source_pdf_sha256": SOURCE_PDF_SHA256,
        "cleaning_operation_totals": totals,
        "text_cleaning_status": "STRUCTURAL_EXTRACTION_ARTIFACTS_REMOVED",
        "official_text_status": "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT",
        "spot_verified_against_official_source": {
            "source": "https://dgp.sdaia.gov.sa/wps/portal/pdp/knowledgecenter/details/PDPL2",
            "articles_checked": [3],
            "result": "heading and body sentence matched verbatim",
        },
        "boundaries": {
            "arabic_governs": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "english_used_for_correction": False,
            "body_sentences_reordered_or_rewritten": False,
        },
        "recommended_next_stage": "PDPL_IMPLEMENTING_REGULATION_ARABIC_CLEANED_TEXT_VALIDATE",
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote %d cleaned records -> %s" % (len(records), os.path.relpath(RECORDS_PATH, ROOT)))
    print("Cleaning operation totals:")
    for k in sorted(totals):
        print("  %-42s %d" % (k, totals[k]))


if __name__ == "__main__":
    main()
