#!/usr/bin/env python3
"""Structural checker for Labor Law reconciliation batch worksheets.

This checker is deterministic and local. It does not access the network,
does not interpret law, and does not verify legal correctness.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "worksheets" / "labor_law" / "reconciliation_batches"
SCAFFOLD_DIR = ROOT / "worksheets" / "labor_law" / "reconciliation_scaffold"
REPORT_DIR = ROOT / "reports" / "labor_law"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"missing CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"missing text file: {path}")
    return path.read_text(encoding="utf-8")


def parse_range(value: str) -> tuple[int, int]:
    try:
        start_s, end_s = value.split("-", 1)
        start = int(start_s)
        end = int(end_s)
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError("range must look like 126-150") from exc
    if start <= 0 or end < start:
        raise argparse.ArgumentTypeError("invalid positive article range")
    return start, end


def data_row_count(path: Path) -> int:
    return len(read_csv(path))


def build_prohibited_phrases() -> list[str]:
    # Built from parts so repository-wide literal scans do not mistake this
    # checker definition for a prohibited report claim.
    return [
        "human legal review" + " pending",
        "official translation" + " governs",
        "English" + " governs",
        "ready for public" + " release",
        "legally" + " verified",
        "legally" + " correct",
        "semantic verification" + " complete",
        "generated/co-authored/model/tool/session" + " attribution",
    ]


def approved_phrase() -> str:
    return "repository-owner legal review active; external legal review optional for enterprise/official adoption"


def check_batch_rows(rows: list[dict[str, str]], expected_rows: int) -> None:
    if len(rows) != expected_rows:
        fail(f"batch CSV row count {len(rows)} != expected {expected_rows}")

    keys = [row.get("article_key", "") for row in rows]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        fail(f"duplicate article_key values: {duplicates}")

    for row in rows:
        key = row.get("article_key", "<missing>")
        text = row.get("official_arabic_text_reconciled", "")
        digest = row.get("official_arabic_text_hash_sha256", "")
        length_raw = row.get("official_arabic_text_length_chars", "0") or "0"
        source = row.get("official_arabic_text_source_method", "")
        status = row.get("reconciliation_status", "")
        ready = row.get("ready_for_future_ingestion_flag", "")
        special = row.get("mukarrar_or_renumbered_or_deleted_flag", "")

        try:
            length = int(length_raw)
        except ValueError:
            fail(f"{key}: invalid official_arabic_text_length_chars={length_raw!r}")

        clean = status == "RECONCILED_FROM_BOE_OFFICIAL_AR" and ready == "yes"
        needs_popup = source == "NEEDS_AMENDMENT_POPUP_RECONCILIATION"
        deleted = source == "DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION" or special == "deleted_or_abolished"
        manual = ready == "needs_manual_review" or status in {"DO_NOT_INGEST_YET", "NEEDS_MANUAL_REVIEW", "BLOCKED_ARTICLE_NOT_FOUND"}

        if clean:
            if not text.strip():
                fail(f"{key}: clean row has empty official text")
            if not digest.strip():
                fail(f"{key}: clean row has empty hash")
            if length <= 0:
                fail(f"{key}: clean row has non-positive text length")

        if needs_popup:
            if text.strip() or digest.strip() or length != 0:
                fail(f"{key}: popup/manual row must have empty text/hash and length 0")
            if status != "DO_NOT_INGEST_YET":
                fail(f"{key}: popup row status must be DO_NOT_INGEST_YET")
            if ready != "needs_manual_review":
                fail(f"{key}: popup row ready flag must be needs_manual_review")

        if deleted:
            if text.strip() or digest.strip() or length != 0:
                fail(f"{key}: deleted/abolished row must not capture old/base text")
            if ready != "needs_manual_review":
                fail(f"{key}: deleted/abolished row ready flag must be needs_manual_review")

        if manual and ready == "yes":
            fail(f"{key}: manual-review row cannot be ready=yes")


def check_readiness(unresolved_floor: int | None) -> None:
    readiness_path = SCAFFOLD_DIR / "readiness_summary.csv"
    unresolved_path = SCAFFOLD_DIR / "unresolved_issues_log.csv"

    readiness_rows = read_csv(readiness_path)
    if len(readiness_rows) != 1:
        fail(f"readiness_summary.csv must have exactly one data row, got {len(readiness_rows)}")

    total_raw = readiness_rows[0].get("total_unresolved_issues", "")
    try:
        total = int(total_raw)
    except ValueError:
        fail(f"invalid readiness total_unresolved_issues={total_raw!r}")

    unresolved_count = data_row_count(unresolved_path)
    if total != unresolved_count:
        fail(f"readiness total_unresolved_issues {total} != unresolved log rows {unresolved_count}")

    if unresolved_floor is not None and total < unresolved_floor:
        fail(f"readiness total_unresolved_issues {total} fell below floor {unresolved_floor}")


def check_report(report_text: str) -> None:
    placeholder_phrases = [
        "يتم تشغيله بعد الكتابة",
        "لا فشل جديد متوقع",
        "to be run",
        "expected future validation",
    ]
    for phrase in placeholder_phrases:
        if phrase.lower() in report_text.lower():
            fail(f"report contains placeholder validation wording: {phrase}")

    if "make validate" not in report_text:
        fail("report does not mention make validate result")
    if "make test" not in report_text:
        fail("report does not mention make test result")

    for phrase in build_prohibited_phrases():
        if phrase.lower() in report_text.lower():
            fail(f"report contains prohibited phrase: {phrase}")

    count = report_text.count(approved_phrase())
    if count != 1:
        fail(f"approved owner-review phrase must appear exactly once in report, got {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Labor Law reconciliation batch structure.")
    parser.add_argument("--batch", required=True, help="Batch number, e.g. 006")
    parser.add_argument("--range", required=True, type=parse_range, help="Article range, e.g. 126-150")
    parser.add_argument("--unresolved-floor", type=int, default=None)
    parser.add_argument("--expected-rows", type=int, default=None)
    args = parser.parse_args()

    batch_num = int(args.batch)
    start, end = args.range
    expected_rows = args.expected_rows or (end - start + 1)

    batch_path = BATCH_DIR / f"labor_law_text_reconciliation_batch_{batch_num:03d}_articles_{start:03d}_{end:03d}.csv"
    report_path = REPORT_DIR / f"LABOR_LAW_TEXT_RECONCILIATION_BATCH_{batch_num:03d}_ARTICLES_{start:03d}_{end:03d}_REPORT.md"

    rows = read_csv(batch_path)
    check_batch_rows(rows, expected_rows)
    ok(f"batch CSV structure OK: {batch_path}")

    check_readiness(args.unresolved_floor)
    ok("readiness/unresolved counts OK")

    report_text = read_text(report_path)
    check_report(report_text)
    ok("report structure and boundary wording OK")

    ok("Labor Law reconciliation batch structural check completed")


if __name__ == "__main__":
    main()
