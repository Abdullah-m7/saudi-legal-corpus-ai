#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update the manual-review queue to reflect resolved P0 items.

This is a QUEUE STATUS UPDATE ONLY — it does NOT verify, promote, correct, or modify any
legal text. It re-runs the (deterministic, resolution-aware) queue builder, which folds
committed P0 segmentation-review resolutions into the queue: a P0 item classified
`segmentation_ocr_miss` (article present in the official source; heading OCR-corrupted) is
moved to bucket `resolved_segmentation_ocr_miss` / priority `P6`, with resolution provenance
recorded on the entry (`p0_resolution_status = resolved`, source, classification, note).
`verification_action_allowed` stays false for every entry.

Currently resolved: Article 3 (جنسية الشركة) — present on packet page 6; original P0 was an
OCR heading-ordinal corruption (الثالثة -> الثالئة), per
reports/official_arabic_verification/p0_article3_segmentation_review.json.

Reads : reports/official_arabic_verification/official_arabic_candidate_comparison_report.json,
        reports/official_arabic_verification/ocr_source_pages.json,
        reports/official_arabic_verification/p0_article*_segmentation_review.json,
        data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json
Writes: reports/official_arabic_verification/manual_review_queue.json / .csv,
        reports/official_arabic_verification/OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_official_arabic_manual_review_queue as builder


def main():
    builder.main()


if __name__ == "__main__":
    main()
