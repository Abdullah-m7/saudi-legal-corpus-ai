#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare the ingested user-provided Arabic candidate text against the OFFICIAL scanned-PDF
source (Umm Al-Qura / Bureau of Experts packet, OCR-extracted), article-by-article.

This is a COMPARISON/REPORT stage only. It does NOT verify, does NOT promote any record to
`verified_against_official_gazette`, does NOT set `article_by_article_verified = true`, and
does NOT change the candidate `official_text_ar`. The official-source side is OCR of a
*scanned image* PDF and is therefore itself lossy — so non-exact results reflect OCR noise
AND/OR genuine differences and REQUIRE manual review before any promotion or correction.

Inputs (both committed; this script needs no OCR engine and is deterministic):
- candidate : data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json
- OCR source: reports/official_arabic_verification/ocr_source_pages.json  (produced once by
              scripts/ocr_official_arabic_scanned_pdf.py; committed)

Outputs:
- reports/official_arabic_verification/official_arabic_candidate_comparison_report.json
- reports/official_arabic_verification/OFFICIAL_ARABIC_VERIFICATION_REPORT_AR.md
"""

import difflib
import hashlib
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
OCR = os.path.join(ROOT, "reports", "official_arabic_verification", "ocr_source_pages.json")
OUT_JSON = os.path.join(ROOT, "reports", "official_arabic_verification",
                        "official_arabic_candidate_comparison_report.json")
OUT_MD = os.path.join(ROOT, "reports", "official_arabic_verification",
                      "OFFICIAL_ARABIC_VERIFICATION_REPORT_AR.md")

TARGET = 281
ARTICLE_WORD = "المادة"          # المادة
ARTICLE_WORD_N = "الماده"        # الماده (after ة->ه normalization)

# -- Arabic feminine ordinal generator (1..281) — same grammar as ingestion -----
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


# Codepoints to DROP: Arabic combining marks / tashkeel / tatweel (NOT base letters
# U+0621–U+064A) and bidi/format marks. Built from explicit ranges so no base letter is touched.
_DROP = set()
for _lo, _hi in [(0x0610, 0x061A), (0x064B, 0x065F), (0x0670, 0x0670), (0x06D6, 0x06ED),
                 (0x0640, 0x0640), (0x200B, 0x200F), (0x202A, 0x202E), (0x2066, 0x2069)]:
    _DROP.update(chr(c) for c in range(_lo, _hi + 1))
# Kept in the alnum filter: Arabic base letters U+0621–U+064A + Arabic/Latin digits.
_KEEP = set(chr(c) for c in range(0x0621, 0x064B)) | set("0123456789٠١٢٣"
                                                         "٤٥٦٧٨٩")

_ALEF_HAMZA = "أإآٱ"   # أ إ آ ٱ


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(c for c in s if c not in _DROP)
    for a in _ALEF_HAMZA:
        s = s.replace(a, "ا")          # -> ا
    s = s.replace("ى", "ي")        # ى -> ي
    s = s.replace("ة", "ه")        # ة -> ه
    return re.sub(r"\s+", " ", s).strip()


def norm_alnum(s):
    """Normalized + punctuation/markdown/whitespace stripped (letters + digits only)."""
    return "".join(c for c in norm(s) if c in _KEEP)


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _detect_headings(ocr_lines):
    """Return [(line_index, ordinal_norm, title_raw)] for OCR lines that look like an article
    heading `المادة <ordinal>[: title]`. Detection is done on the normalized line (which maps
    المادة -> الماده) after stripping leading non-letter junk."""
    heads = []
    prefix = ARTICLE_WORD_N + " "
    for i, ln in enumerate(ocr_lines):
        n = norm(ln)
        n2 = re.sub(r"^[^ء-ي]+", "", n)   # strip leading non-Arabic-letter chars
        if not n2.startswith(prefix):
            continue
        after = n2[len(prefix):]
        ordinal_norm = re.split(r"[:：]", after, 1)[0].strip()
        title_raw = ln.split(":", 1)[1].strip() if ":" in ln else ""
        heads.append((i, ordinal_norm, title_raw))
    return heads


def compare():
    cand = json.load(open(CAND, encoding="utf-8"))["articles"]
    ocr_doc = json.load(open(OCR, encoding="utf-8"))
    ocr_full = "\n".join(p["text"] for p in ocr_doc["pages"])
    ocr_lines = ocr_full.split("\n")
    heads = _detect_headings(ocr_lines)

    # Sequentially align detected headings to expected article numbers 1..281. Exact normalized
    # ordinal match first; if none, a BOUNDED fuzzy fallback (ratio >= 0.90) tolerates OCR noise
    # in a heading's ordinal without letting a garbled heading consume later articles.
    aligned = {}
    hp = 0
    for n in range(1, TARGET + 1):
        exp = norm_alnum(arabic_ordinal(n))
        nxt = norm_alnum(arabic_ordinal(n + 1)) if n < TARGET else None
        found = None
        j = hp
        while j < len(heads) and j < hp + 40:
            if norm_alnum(heads[j][1]) == exp:
                found = j
                break
            j += 1
        if found is None:
            best, best_r = None, 0.0
            j = hp
            while j < len(heads) and j < hp + 6:
                g = norm_alnum(heads[j][1])
                r = difflib.SequenceMatcher(None, g, exp).ratio()
                # don't grab a heading that is clearly the NEXT article
                if nxt and difflib.SequenceMatcher(None, g, nxt).ratio() > r:
                    break
                if r > best_r:
                    best, best_r = j, r
                j += 1
            if best is not None and best_r >= 0.90:
                found = best
        if found is not None:
            aligned[n] = (heads[found][0], heads[found][2])
            hp = found + 1

    aligned_lines = sorted((idx, n) for n, (idx, _t) in aligned.items())
    next_boundary = {}
    for k, (idx, n) in enumerate(aligned_lines):
        end = aligned_lines[k + 1][0] if k + 1 < len(aligned_lines) else len(ocr_lines)
        next_boundary[n] = (idx, end)

    entries = []
    counts = {"exact_match": 0, "whitespace_or_markdown_only": 0, "punctuation_or_spacing": 0,
              "substantive_difference": 0, "missing_in_official_source": 0, "missing_in_candidate": 0}
    for c in cand:
        n = c["article_number"]
        cand_text = c["official_text_ar"]
        cand_hash = c["text_hash_sha256"]
        if n not in aligned:
            entries.append({
                "article_number": n, "candidate_title_ar": c["article_title_ar"],
                "official_source_title_ar": None, "candidate_hash": cand_hash,
                "official_source_hash": None, "exact_text_match": False,
                "normalized_text_match": False, "similarity": 0.0,
                "difference_type": "missing_in_official_source",
                "notes": "No matching article heading located in the OCR of the scanned official "
                         "source (OCR miss or segmentation gap) — manual review required."})
            counts["missing_in_official_source"] += 1
            continue
        idx, title_raw = aligned[n]
        s, e = next_boundary[n]
        body = "\n".join(ocr_lines[s + 1:e]).strip()
        off_hash = _sha256(body)
        exact = (cand_text == body)
        nmatch = (norm(cand_text) == norm(body))
        pmatch = (norm_alnum(cand_text) == norm_alnum(body))
        sim = round(difflib.SequenceMatcher(None, norm(cand_text), norm(body)).ratio(), 4)
        if exact:
            dt = "exact_match"
        elif nmatch:
            dt = "whitespace_or_markdown_only"
        elif pmatch:
            dt = "punctuation_or_spacing"
        else:
            dt = "substantive_difference"
        counts[dt] += 1
        entries.append({
            "article_number": n, "candidate_title_ar": c["article_title_ar"],
            "official_source_title_ar": title_raw or None, "candidate_hash": cand_hash,
            "official_source_hash": off_hash, "exact_text_match": exact,
            "normalized_text_match": nmatch, "similarity": sim, "difference_type": dt,
            "notes": ("Exact match." if exact else
                      "Official-source side is OCR of a scanned image (lossy); normalized "
                      "similarity=%.4f. Non-exact => manual review before any promotion/correction."
                      % sim)})

    report = {
        "report_type": "official_arabic_candidate_vs_scanned_source_comparison",
        "not_legal_advice": True,
        "candidate_file": "data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json",
        "official_source": {
            "kind": "scanned_pdf_ocr",
            "packet": "inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/ (6 parts, 119 pages)",
            "ocr_artifact": "reports/official_arabic_verification/ocr_source_pages.json",
            "ocr_engine": ocr_doc.get("engine"), "ocr_lang": ocr_doc.get("lang"),
            "ocr_dpi": ocr_doc.get("dpi"), "ocr_pages": ocr_doc.get("page_count"),
            "caveat_en": "Official source is OCR of a scanned image and is itself lossy; it is NOT "
                         "treated as byte-ground-truth. This comparison does not verify the candidate."
        },
        "candidate_articles": len(cand),
        "official_source_headings_detected": len(heads),
        "official_source_articles_aligned": len(aligned),
        "verification_status_unchanged": "ingested_unverified",
        "article_by_article_verified": False,
        "promoted_to_verified": False,
        "summary_counts": counts,
        "exact_match_count": counts["exact_match"],
        "normalized_match_count": counts["exact_match"] + counts["whitespace_or_markdown_only"],
        "substantive_difference_count": counts["substantive_difference"],
        "missing_or_extra_article_count": counts["missing_in_official_source"] + counts["missing_in_candidate"],
        "entries": entries,
    }
    return report


def write_md(report):
    c = report["summary_counts"]
    non_exact = [e for e in report["entries"] if e["difference_type"] != "exact_match"]
    L = []
    L.append("# تقرير مقارنة النص العربي المرشح مع المصدر الرسمي الممسوح ضوئيًا")
    L.append("# Official Arabic Candidate vs Scanned Official Source — Comparison Report")
    L.append("")
    L.append("> **هذا تقرير مقارنة فقط، وليس استشارة قانونية.** المصدر الرسمي هنا استُخرج نصه بالتعرّف "
             "الضوئي (OCR) من ملف PDF ممسوح ضوئيًا، وهو بطبيعته عرضة لأخطاء الاستخراج؛ لذلك لا يُعامَل "
             "كنص مرجعي حرفي، وكل اختلاف غير مطابق يتطلب مراجعة يدوية.")
    L.append(">")
    L.append("> This is a **comparison report, not legal advice.** The official source is OCR of a "
             "scanned image and is itself lossy.")
    L.append("")
    L.append("## الحالة / Status")
    L.append("- النص المرشح يبقى **`ingested_unverified`** (لم يُرقَّ). / Candidate remains "
             "**ingested_unverified**.")
    L.append("- **لا** سجل رُقّي إلى `verified_against_official_gazette` في هذا الـPR. / No record "
             "promoted to verified_against_official_gazette.")
    L.append("- `article_by_article_verified` = **false** (لم يتغير). / remains false.")
    L.append("")
    L.append("## الملخص العددي / Summary counts")
    L.append("- عدد مواد المرشح / candidate articles: **%d**" % report["candidate_articles"])
    L.append("- عناوين مواد اكتُشفت في المصدر / source headings detected: **%d**"
             % report["official_source_headings_detected"])
    L.append("- مواد المصدر المحاذاة / source articles aligned: **%d**"
             % report["official_source_articles_aligned"])
    L.append("- مطابقة تامة / exact match: **%d**" % c["exact_match"])
    L.append("- مطابقة بعد التطبيع / normalized match: **%d**" % report["normalized_match_count"])
    L.append("- اختلاف ترقيم/مسافات فقط / punctuation-or-spacing only: **%d**"
             % c["punctuation_or_spacing"])
    L.append("- اختلاف جوهري (يشمل ضجيج OCR) / substantive difference (incl. OCR noise): **%d**"
             % c["substantive_difference"])
    L.append("- مفقودة في المصدر / missing_in_official_source: **%d**" % c["missing_in_official_source"])
    L.append("- مفقودة في المرشح / missing_in_candidate: **%d**" % c["missing_in_candidate"])
    L.append("")
    L.append("## المواد غير المطابقة تمامًا / Non-exact articles (article number → reason)")
    if not non_exact:
        L.append("- (لا يوجد / none)")
    else:
        for e in non_exact:
            L.append("- المادة %d / Article %d → **%s** (similarity=%.4f)"
                     % (e["article_number"], e["article_number"], e["difference_type"],
                        e.get("similarity") or 0.0))
    L.append("")
    L.append("## التوصية للمرحلة التالية / Recommendation for next stage")
    L.append("- نظرًا لأن المصدر الرسمي مُستخرَج بالـOCR (ذو ضجيج)، فإن الاختلافات غير التامة تعكس "
             "ضجيج OCR و/أو اختلافات فعلية، ولا يمكن الترقية تلقائيًا. / Because the official source is "
             "OCR-derived (noisy), non-exact differences reflect OCR noise and/or genuine differences "
             "and cannot be auto-promoted.")
    L.append("- **(D) مطلوب مراجعة يدوية / require owner/manual review**، ثم **(A)** ترقية المواد "
             "المطابقة تمامًا فقط و/أو **(B)** إنشاء PR تصحيحات للاختلافات المؤكدة — بعد المراجعة فقط. / "
             "Then (A) promote only exactly-matched articles and/or (B) open a corrections PR — after review.")
    L.append("")
    L.append("**العربية هي اللغة الحاكمة. هذه المادة ليست استشارة قانونية.** Arabic is governing. "
             "Not legal advice.")
    return "\n".join(L) + "\n"


def main():
    report = compare()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(write_md(report))
    c = report["summary_counts"]
    print("wrote comparison report: %d articles | exact=%d normalized=%d punct/space=%d "
          "substantive=%d missing_source=%d aligned=%d/%d"
          % (report["candidate_articles"], c["exact_match"], report["normalized_match_count"],
             c["punctuation_or_spacing"], c["substantive_difference"], c["missing_in_official_source"],
             report["official_source_articles_aligned"], TARGET))


if __name__ == "__main__":
    main()
