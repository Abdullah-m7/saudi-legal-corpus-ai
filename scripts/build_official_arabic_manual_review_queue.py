#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a practical MANUAL-REVIEW QUEUE from the existing OCR comparison report so the owner
can efficiently triage the 281 articles. This does NOT verify anything, does NOT promote any
article, and does NOT modify any candidate legal text. Every queue entry carries
`verification_action_allowed = false`.

Deterministic and OCR-free: it reads the committed comparison report + candidate + OCR
artifact, and reuses the comparison module's (deterministic) segmentation only to pull short
OCR snippets for reviewer context.

Reads:
- reports/official_arabic_verification/official_arabic_candidate_comparison_report.json
- reports/official_arabic_verification/ocr_source_pages.json
- data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json
Writes:
- reports/official_arabic_verification/manual_review_queue.json
- reports/official_arabic_verification/manual_review_queue.csv
- reports/official_arabic_verification/OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import compare_official_arabic_candidate_to_source as cmp  # deterministic helpers, no OCR engine

RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
REPORT = os.path.join(RPT_DIR, "official_arabic_candidate_comparison_report.json")
OCR = os.path.join(RPT_DIR, "ocr_source_pages.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
OUT_JSON = os.path.join(RPT_DIR, "manual_review_queue.json")
OUT_CSV = os.path.join(RPT_DIR, "manual_review_queue.csv")
OUT_MD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md")

TARGET = 281
SNIPPET = 220

BUCKET_PRIORITY = {
    "missing_or_segmentation_issue": "P0",
    "low_similarity_manual_review": "P1",
    "possible_substantive_difference_manual_review": "P2",
    "likely_ocr_noise_medium_similarity": "P3",
    "likely_ocr_noise_high_similarity": "P4",
    "normalized_or_punctuation_review": "P5",
    "exact_match_no_action": "P6",
    # A P0 item resolved as an OCR segmentation miss (article present in the source, heading
    # OCR-corrupted) is de-prioritised to P6. This is a triage status change only — no
    # verification, no promotion, no legal-text change.
    "resolved_segmentation_ocr_miss": "P6",
}

# P0 segmentation-review reports whose resolutions are folded into the queue (deterministic).
import glob as _glob
_RESOLUTION_REPORTS = sorted(_glob.glob(os.path.join(
    ROOT, "reports", "official_arabic_verification", "p0_article*_segmentation_review.json")))


def _apply_p0_resolutions(entries):
    """Fold committed P0 segmentation-review resolutions into the queue: a segmentation_ocr_miss
    (source_location_found, not verified) moves the article to bucket resolved_segmentation_ocr_miss
    / priority P6 and records the resolution provenance. Returns the sorted list of resolved
    article numbers."""
    by_num = {e["article_number"]: e for e in entries}
    resolved = []
    for path in _RESOLUTION_REPORTS:
        with open(path, encoding="utf-8") as fh:
            r = json.load(fh)
        n = r.get("article_number")
        if (r.get("classification") == "segmentation_ocr_miss" and r.get("source_location_found")
                and r.get("verification_action_allowed") is False and n in by_num):
            e = by_num[n]
            e["review_bucket"] = "resolved_segmentation_ocr_miss"
            e["review_priority"] = "P6"
            e["p0_resolution_status"] = "resolved"
            e["p0_resolution_source"] = os.path.relpath(path, ROOT)
            e["p0_resolution_classification"] = r.get("classification")
            e["p0_resolution_note"] = (
                "Article %d is present on packet page %s; original P0 was caused by OCR heading "
                "ordinal corruption." % (n, r.get("source_page_number_within_packet")))
            e["verification_action_allowed"] = False
            resolved.append(n)
    return sorted(resolved)

_SUSPECTED = {
    "exact_match_no_action": "لا يوجد اختلاف — مطابقة تامة. / None — exact match.",
    "normalized_or_punctuation_review": "اختلاف مسافات/ترقيم/تنسيق فقط. / whitespace/punctuation/markdown only.",
    "missing_or_segmentation_issue": "لم يُعثر على المادة في مخرجات OCR (فشل استخراج العنوان أو فجوة تقطيع). / article not located in OCR (heading miss / segmentation gap).",
    "likely_ocr_noise_high_similarity": "على الأرجح ضجيج OCR (تشابه عالٍ جدًا). / likely OCR noise (very high similarity).",
    "likely_ocr_noise_medium_similarity": "على الأرجح ضجيج OCR (تشابه متوسط). / likely OCR noise (medium similarity).",
    "low_similarity_manual_review": "تشابه منخفض — قد يكون ضجيج OCR شديدًا أو اختلافًا فعليًا. / low similarity — heavy OCR noise or a real difference.",
    "possible_substantive_difference_manual_review": "قد يكون اختلافًا جوهريًا — مراجعة يدوية مطلوبة. / possible substantive difference — manual review.",
}

_ACTION = {
    "exact_match_no_action": "لا إجراء. / No action.",
    "normalized_or_punctuation_review": "مراجعة سريعة للتأكد أنه تنسيق فقط. / quick check that it is formatting only.",
    "missing_or_segmentation_issue": "مراجعة الصفحة الممسوحة يدويًا وتأكيد وجود/رقم المادة. / manually check the scanned page; confirm the article exists / its number.",
    "likely_ocr_noise_high_similarity": "فحص عيّني فقط. / spot-check only.",
    "likely_ocr_noise_medium_similarity": "فحص عيّني. / spot-check.",
    "low_similarity_manual_review": "مراجعة يدوية للنص الأصلي مقابل الصفحة الرسمية. / manual review of candidate text vs the official page.",
    "possible_substantive_difference_manual_review": "مراجعة يدوية دقيقة لتحديد ما إذا كان الاختلاف حقيقيًا. / careful manual review to decide if the difference is real.",
}


def _bucket(diff_type, sim):
    if diff_type == "exact_match":
        return "exact_match_no_action"
    if diff_type in ("whitespace_or_markdown_only", "punctuation_or_spacing"):
        return "normalized_or_punctuation_review"
    if diff_type in ("missing_in_official_source", "missing_in_candidate"):
        return "missing_or_segmentation_issue"
    if diff_type == "substantive_difference":
        if sim >= 0.95:
            return "likely_ocr_noise_high_similarity"
        if sim >= 0.80:
            return "likely_ocr_noise_medium_similarity"
        if sim < 0.60:
            return "low_similarity_manual_review"
        return "possible_substantive_difference_manual_review"
    return "possible_substantive_difference_manual_review"


def _ocr_bodies():
    """Reconstruct OCR body text per article using the comparison module's deterministic
    segmentation (same alignment as the committed comparison report)."""
    ocr_doc = json.load(open(OCR, encoding="utf-8"))
    ocr_lines = "\n".join(p["text"] for p in ocr_doc["pages"]).split("\n")
    heads = cmp._detect_headings(ocr_lines)
    import difflib
    aligned = {}
    hp = 0
    for n in range(1, TARGET + 1):
        exp = cmp.norm_alnum(cmp.arabic_ordinal(n))
        nxt = cmp.norm_alnum(cmp.arabic_ordinal(n + 1)) if n < TARGET else None
        found, j = None, hp
        while j < len(heads) and j < hp + 40:
            if cmp.norm_alnum(heads[j][1]) == exp:
                found = j
                break
            j += 1
        if found is None:
            best, best_r, j = None, 0.0, hp
            while j < len(heads) and j < hp + 6:
                g = cmp.norm_alnum(heads[j][1])
                r = difflib.SequenceMatcher(None, g, exp).ratio()
                if nxt and difflib.SequenceMatcher(None, g, nxt).ratio() > r:
                    break
                if r > best_r:
                    best, best_r = j, r
                j += 1
            if best is not None and best_r >= 0.90:
                found = best
        if found is not None:
            aligned[n] = heads[found][0]
            hp = found + 1
    lines_idx = sorted((idx, n) for n, idx in aligned.items())
    bounds = {}
    for k, (idx, n) in enumerate(lines_idx):
        end = lines_idx[k + 1][0] if k + 1 < len(lines_idx) else len(ocr_lines)
        bounds[n] = (idx, end)
    bodies = {}
    for n, (s, e) in bounds.items():
        bodies[n] = "\n".join(ocr_lines[s + 1:e]).strip()
    return bodies


def build():
    report = json.load(open(REPORT, encoding="utf-8"))
    cand = {a["article_number"]: a for a in json.load(open(CAND, encoding="utf-8"))["articles"]}
    ocr_bodies = _ocr_bodies()
    by_num = {e["article_number"]: e for e in report["entries"]}

    entries = []
    for n in range(1, TARGET + 1):
        e = by_num[n]
        c = cand[n]
        sim = e.get("similarity") or 0.0
        bucket = _bucket(e["difference_type"], sim)
        prio = BUCKET_PRIORITY[bucket]
        cand_text = c["official_text_ar"]
        ocr_text = ocr_bodies.get(n, "")
        entries.append({
            "article_number": n,
            "article_title_ar": c["article_title_ar"],
            "original_difference_type": e["difference_type"],
            "similarity": sim,
            "review_bucket": bucket,
            "review_priority": prio,
            "candidate_hash": e["candidate_hash"],
            "official_source_hash": e.get("official_source_hash"),
            "candidate_text_length": len(cand_text),
            "ocr_text_length": len(ocr_text),
            "candidate_snippet_ar": cand_text[:SNIPPET],
            "ocr_snippet_ar": ocr_text[:SNIPPET],
            "suspected_issue": _SUSPECTED[bucket],
            "recommended_action": _ACTION[bucket],
            "verification_action_allowed": False,
        })

    resolved_p0 = _apply_p0_resolutions(entries)

    bucket_counts = {}
    prio_counts = {}
    for e in entries:
        bucket_counts[e["review_bucket"]] = bucket_counts.get(e["review_bucket"], 0) + 1
        prio_counts[e["review_priority"]] = prio_counts.get(e["review_priority"], 0) + 1

    queue = {
        "queue_type": "official_arabic_ocr_manual_review_queue",
        "not_legal_advice": True,
        "note_en": "Manual-review queue derived from the lossy OCR comparison. This is NOT "
                   "verification and promotes NO article. The candidate text is unchanged and "
                   "remains ingested_unverified; article_by_article_verified remains false. "
                   "Resolved P0 items (OCR segmentation misses) are de-prioritised to P6 with "
                   "provenance; no legal text is changed.",
        "source_comparison_report": "reports/official_arabic_verification/official_arabic_candidate_comparison_report.json",
        "candidate_file": "data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json",
        "verification_status_unchanged": "ingested_unverified",
        "article_by_article_verified": False,
        "promoted_to_verified": False,
        "queue_entries": len(entries),
        "bucket_counts": bucket_counts,
        "priority_counts": prio_counts,
        "p0_articles": sorted(e["article_number"] for e in entries if e["review_priority"] == "P0"),
        "p1_articles": sorted(e["article_number"] for e in entries if e["review_priority"] == "P1"),
        "resolved_p0_articles": resolved_p0,
        "unresolved_p0_count": sum(1 for e in entries if e["review_priority"] == "P0"),
        "entries": entries,
    }
    return queue


def write_csv(queue):
    cols = ["review_priority", "article_number", "review_bucket", "p0_resolution_status",
            "original_difference_type", "similarity", "candidate_text_length", "ocr_text_length",
            "candidate_hash", "official_source_hash", "verification_action_allowed",
            "article_title_ar", "suspected_issue", "recommended_action"]
    rows = sorted(queue["entries"], key=lambda e: (e["review_priority"], e["article_number"]))
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for e in rows:
            w.writerow({k: e.get(k) for k in cols})


def write_md(queue):
    bc, pc = queue["bucket_counts"], queue["priority_counts"]
    L = []
    L.append("# قائمة المراجعة اليدوية لمخرجات OCR — النص العربي الرسمي المرشح")
    L.append("# Official Arabic OCR — Manual Review Queue")
    L.append("")
    L.append("> **هذه قائمة مراجعة يدوية، وليست تحققًا ولا استشارة قانونية.** لم يُغيَّر أي نص مرشح، "
             "ولم تُرقَّ أي مادة. النص المرشح يبقى `ingested_unverified` و`article_by_article_verified` "
             "يبقى `false`. المصدر الرسمي مُستخرَج بالـOCR (ذو ضجيج) ولا يُعامَل كنص حرفي.")
    L.append(">")
    L.append("> This is a **manual-review queue, not verification and not legal advice.** No "
             "candidate text was changed; no article was marked verified. This PR promotes no article.")
    L.append("")
    L.append("## الحالة / Status")
    L.append("- النص المرشح: **`ingested_unverified`** (281 مادة، دون تغيير). / candidate unchanged.")
    L.append("- `article_by_article_verified` = **false** · `articles_verified` = **0** · لا مادة "
             "بحالة `verified_against_official_gazette`.")
    L.append("")
    L.append("## العدد حسب فئة المراجعة / Counts by review_bucket")
    for b in ["exact_match_no_action", "normalized_or_punctuation_review",
              "likely_ocr_noise_high_similarity", "likely_ocr_noise_medium_similarity",
              "possible_substantive_difference_manual_review", "low_similarity_manual_review",
              "missing_or_segmentation_issue", "resolved_segmentation_ocr_miss"]:
        L.append("- `%s`: **%d**" % (b, bc.get(b, 0)))
    L.append("")
    L.append("## العدد حسب الأولوية / Counts by review_priority")
    for p in ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]:
        L.append("- **%s**: %d" % (p, pc.get(p, 0)))
    L.append("")
    L.append("## مواد P0 غير المُحلّة / Unresolved P0 articles")
    L.append("- عدد P0 غير المُحلّة / unresolved P0 count: **%d**" % queue.get("unresolved_p0_count", 0))
    L.append("- " + (", ".join(str(x) for x in queue["p0_articles"]) or "(لا يوجد / none)"))
    L.append("")
    L.append("## عناصر P0 المُحلّة / P0 resolved items")
    resolved = queue.get("resolved_p0_articles", [])
    if not resolved:
        L.append("- (لا يوجد / none)")
    else:
        for n in resolved:
            e = next(x for x in queue["entries"] if x["article_number"] == n)
            L.append("- المادة %d / Article %d → **%s** — %s"
                     % (n, n, e.get("review_bucket"), e.get("p0_resolution_note", "")))
    L.append("")
    L.append("## مواد P1 (تشابه منخفض) / P1 articles (low similarity)")
    L.append("- " + (", ".join(str(x) for x in queue["p1_articles"]) or "(لا يوجد / none)"))
    L.append("")
    L.append("## سير العمل الموصى به / Recommended manual workflow")
    L.append("1. راجع **P0** (المفقود/التقطيع) أولًا. / Review P0 missing/segmentation first.")
    L.append("2. راجع **P1** (التشابه المنخفض). / Review P1 low similarity.")
    L.append("3. راجع **P2** (اختلاف جوهري محتمل). / Review P2 possible substantive differences.")
    L.append("4. فحص عيّني لـ **P3/P4** (ضجيج OCR). / Spot-check P3/P4 OCR noise.")
    L.append("5. لاحقًا فقط: أنشئ PR منفصلًا للترقية/التصحيح. / Only later: a separate "
             "promotion/correction PR.")
    L.append("")
    L.append("**هذا الـPR لا يرقّي أي مادة. العربية هي اللغة الحاكمة. ليست استشارة قانونية.** This PR "
             "promotes no article. Arabic is governing. Not legal advice.")
    return "\n".join(L) + "\n"


def main():
    queue = build()
    os.makedirs(RPT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    write_csv(queue)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(write_md(queue))
    print("wrote manual review queue: %d entries | buckets=%s | priorities=%s"
          % (queue["queue_entries"], queue["bucket_counts"], queue["priority_counts"]))


if __name__ == "__main__":
    main()
