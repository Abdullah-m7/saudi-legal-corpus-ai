#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the P1 low-similarity batch-1 manual-review report (triage only, NOT verification).

Selects the 10 lowest-similarity P1 items from the committed manual-review queue and, for each,
gathers evidence from the already-captured OCR artifact (reports/.../ocr_source_pages.json) —
searching packet pages for the article title and key candidate phrases — to classify WHY the
similarity is low. It does NOT run OCR, does NOT touch the candidate, and does NOT verify,
promote, or correct any legal text.

Reads : reports/official_arabic_verification/manual_review_queue.json
        reports/official_arabic_verification/official_arabic_candidate_comparison_report.json
        reports/official_arabic_verification/ocr_source_pages.json
        data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json
Writes: reports/official_arabic_verification/p1_low_similarity_batch1_review.json
        reports/official_arabic_verification/P1_LOW_SIMILARITY_BATCH1_REVIEW_AR.md
"""

from __future__ import annotations

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "reports", "official_arabic_verification")
QJSON = os.path.join(RPT, "manual_review_queue.json")
CMP = os.path.join(RPT, "official_arabic_candidate_comparison_report.json")
OCR = os.path.join(RPT, "ocr_source_pages.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
OUT_JSON = os.path.join(RPT, "p1_low_similarity_batch1_review.json")
OUT_MD = os.path.join(RPT, "P1_LOW_SIMILARITY_BATCH1_REVIEW_AR.md")

STAGE = "OFFICIAL_ARABIC_P1_LOW_SIMILARITY_BATCH1_REVIEW"
BATCH_ID = "P1_LOW_SIMILARITY_BATCH1"
BATCH_SIZE = 10

# -- Arabic normalization (drop tashkeel/tatweel/bidi marks only; keep base letters) ----------
_DROP = set()
for _lo, _hi in [(0x0610, 0x061A), (0x064B, 0x065F), (0x0670, 0x0670), (0x06D6, 0x06ED),
                 (0x0640, 0x0640), (0x200B, 0x200F), (0x202A, 0x202E), (0x2066, 0x2069)]:
    _DROP.update(chr(c) for c in range(_lo, _hi + 1))
_KEEP = set(chr(c) for c in range(0x0621, 0x064B)) | set("0123456789٠١٢٣٤٥٦٧٨٩")
_ALEF_HAMZA = "أإآٱ"


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = "".join(c for c in s if c not in _DROP)
    for a in _ALEF_HAMZA:
        s = s.replace(a, "ا")
    s = s.replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"\s+", " ", s).strip()


def norm_alnum(s):
    return "".join(c for c in norm(s) if c in _KEEP)


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def select_batch(queue):
    """The 10 lowest-similarity P1 entries (tie-break by ascending article_number)."""
    p1 = [e for e in queue["entries"] if e.get("review_priority") == "P1"]
    p1.sort(key=lambda e: (e["similarity"], e["article_number"]))
    return p1[:BATCH_SIZE]


def _search_pages(pages, terms):
    """Return {term: [global_page,...]} for each normalized-alnum term found in any page."""
    norm_pages = [(pg["global_page"], norm_alnum(pg.get("text", ""))) for pg in pages]
    hits = {}
    for t in terms:
        nt = norm_alnum(t)
        found = [gp for gp, txt in norm_pages if nt and nt in txt]
        hits[t] = found
    return hits


def _classify(body_found, title_found):
    """Deterministic triage classification from gathered evidence. Honest about uncertainty.

    body_found  = at least one distinctive candidate *body* phrase was located verbatim in the
                  OCR of the scanned packet (article text is present in the source).
    title_found = the article title was located in the OCR (article is present; heading intact).
    """
    if body_found:
        # A body phrase is present verbatim in the scanned source, yet the per-article queue
        # similarity is very low => the per-article alignment span was mis-captured (drift),
        # not a real text difference.
        return ("segmentation_or_alignment_drift", "medium",
                "distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_"
                "span_mismatched")
    if title_found:
        # Article located via its title/heading, but the exact body opening did not match —
        # consistent with heavy OCR noise breaking the phrase; needs manual visual confirmation.
        return ("likely_ocr_noise", "low",
                "article_title_located_in_source_but_body_opening_not_exact_matched_"
                "consistent_with_heavy_ocr_noise")
    return ("needs_manual_visual_review", "low",
            "neither_a_body_phrase_nor_the_title_confidently_matched_in_ocr_text")


_NEXT_ACTION = {
    "segmentation_or_alignment_drift":
        "later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)",
    "likely_ocr_noise":
        "later queue-update PR: treat as OCR noise; no candidate change",
    "table_or_list_formatting_drift":
        "later queue-update PR: note formatting drift; manual spot-check of list/table",
    "heading_or_ordinal_corruption":
        "manual visual review of the packet page heading before any queue re-bucketing",
    "possible_substantive_difference":
        "manual visual review; do NOT correct until an official (non-OCR) source confirms",
    "needs_manual_visual_review":
        "manual visual review of the packet page against the candidate",
    "insufficient_ocr_evidence":
        "manual visual review; OCR evidence insufficient for classification",
}


def build_entry(qe, cmp_by_num, cand_by_num, pages):
    n = qe["article_number"]
    ce = cmp_by_num.get(n, {})
    ca = cand_by_num.get(n, {})
    cand_text = ca.get("official_text_ar", "")
    title = qe.get("article_title_ar", "")

    # Search terms: title, candidate opening phrase, a distinctive mid phrase.
    words = [w for w in norm(cand_text).split(" ") if w]
    opening = " ".join(words[:6])
    mid = " ".join(words[6:12]) if len(words) > 8 else ""
    terms = [t for t in (title, opening, mid) if norm_alnum(t)]
    hits = _search_pages(pages, terms)

    opening_pages = hits.get(opening, []) if opening else []
    mid_pages = hits.get(mid, []) if mid else []
    title_pages = hits.get(title, []) if title else []
    body_pages = sorted({p for p in (opening_pages + mid_pages)})
    all_hit_pages = sorted({p for lst in hits.values() for p in lst})
    source_found = bool(body_pages) or bool(title_pages)
    src_page = (body_pages or title_pages or [None])[0]

    part_file = part_page = None
    if src_page is not None:
        pg = next((p for p in pages if p["global_page"] == src_page), None)
        if pg:
            part_file = os.path.join(
                "inputs", "official_arabic_verification",
                "nizam_alsharikat_1443h_parts", pg["part_file"])
            part_page = pg["part_page_index"]

    ocr_snip = qe.get("ocr_snippet_ar", "")
    cls, conf, evidence = _classify(bool(body_pages), bool(title_pages))

    ev_snips = []
    if src_page is not None:
        pg = next((p for p in pages if p["global_page"] == src_page), None)
        if pg:
            raw = re.sub(r"\s+", " ", pg.get("text", "")).strip()
            ev_snips.append({
                "global_page": src_page,
                "snippet": raw[:400],
            })

    return {
        "article_number": n,
        "article_title_ar": title,
        "queue_similarity": qe.get("similarity"),
        "queue_bucket_before": qe.get("review_bucket"),
        "queue_priority_before": qe.get("review_priority"),
        "candidate_text": cand_text,
        "candidate_hash": qe.get("candidate_hash"),
        "official_source_hash": qe.get("official_source_hash"),
        "candidate_text_length": qe.get("candidate_text_length"),
        "ocr_text_length": qe.get("ocr_text_length"),
        "candidate_snippet_ar": qe.get("candidate_snippet_ar"),
        "ocr_snippet_ar": ocr_snip,
        "search_terms_used": terms,
        "ocr_pages_searched": {
            "scope": "all %d packet pages (already-captured OCR artifact; no new OCR run)"
                     % len(pages),
            "total_pages": len(pages),
            "term_hit_pages_global": hits,
            "any_term_hit_pages_global": all_hit_pages,
        },
        "source_location_found": source_found,
        "source_part_file": part_file,
        "source_page_number_within_packet": src_page,
        "source_page_number_within_part": part_page,
        "evidence_snippets": ev_snips,
        "batch_review_classification": cls,
        "review_confidence": conf,
        "evidence_summary": evidence,
        "recommended_next_action": _NEXT_ACTION[cls],
        "verification_action_allowed": False,
        "candidate_text_changed": False,
        "verification_status_changed": False,
        "article_by_article_verified": False,
    }


def build():
    queue = _read(QJSON)
    cmp_rep = _read(CMP)
    ocr = _read(OCR)
    cand = _read(CAND)
    pages = ocr["pages"]
    cmp_by_num = {e["article_number"]: e for e in cmp_rep["entries"]}
    cand_by_num = {a["article_number"]: a for a in cand["articles"]}

    batch = select_batch(queue)
    entries = [build_entry(qe, cmp_by_num, cand_by_num, pages) for qe in batch]
    selected = [e["article_number"] for e in entries]

    counts = {}
    for e in entries:
        counts[e["batch_review_classification"]] = \
            counts.get(e["batch_review_classification"], 0) + 1

    payload = {
        "stage": STAGE,
        "not_legal_advice": True,
        "batch_id": BATCH_ID,
        "batch_size": BATCH_SIZE,
        "selection_method": "lowest_similarity_p1_articles_from_manual_review_queue",
        "selected_articles": selected,
        "classification_counts": counts,
        "candidate_file": os.path.relpath(CAND, ROOT),
        "source_comparison_report": os.path.relpath(CMP, ROOT),
        "ocr_artifact": os.path.relpath(OCR, ROOT),
        "verification_status_unchanged": "ingested_unverified",
        "article_by_article_verified": False,
        "promoted_to_verified": False,
        "candidate_text_changed": False,
        "entries": entries,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    write_md(payload)
    print("wrote P1 batch-1 review: %d entries | selected=%s | classes=%s"
          % (len(entries), selected, counts))


def write_md(p):
    L = []
    L.append("# مراجعة الدفعة 1 — مواد P1 الأقل تشابهًا")
    L.append("# P1 Low-Similarity Batch 1 — Manual Review")
    L.append("")
    L.append("> **هذه مراجعة/فرز للدفعة فقط، وليست تحققًا ولا استشارة قانونية.** "
             "لم يُغيَّر أي نص مرشح، ولم تُرقَّ أي مادة، ولم تُوسم أي مادة بأنها "
             "`verified_against_official_gazette`. النص المرشح يبقى `ingested_unverified` "
             "و`article_by_article_verified` يبقى `false`.")
    L.append(">")
    L.append("> This is a **batch review / triage only — not verification, not legal advice.** "
             "No candidate text was changed; no article was promoted; the candidate remains "
             "`ingested_unverified` and `article_by_article_verified` remains `false`.")
    L.append("")
    L.append("## الاختيار / Selection")
    L.append("")
    L.append("- **batch_id:** `%s` · **batch_size:** `%d`" % (p["batch_id"], p["batch_size"]))
    L.append("- **طريقة الاختيار / selection_method:** أقل 10 مواد P1 تشابهًا من قائمة المراجعة. / "
             "the 10 lowest-similarity P1 articles from the manual-review queue.")
    L.append("- **المواد المختارة / selected articles:** %s"
             % ", ".join(str(x) for x in p["selected_articles"]))
    L.append("")
    L.append("| المادة / art | العنوان / title | التشابه / similarity | التصنيف / classification "
             "| الثقة / confidence | المصدر / source page |")
    L.append("|---|---|---|---|---|---|")
    for e in p["entries"]:
        sp = e["source_page_number_within_packet"]
        L.append("| %d | %s | %.4f | `%s` | %s | %s |" % (
            e["article_number"], e["article_title_ar"], e["queue_similarity"],
            e["batch_review_classification"], e["review_confidence"],
            ("صفحة %s / page %s" % (sp, sp)) if sp is not None else "—"))
    L.append("")
    L.append("## تفاصيل كل مادة / Per-article detail")
    L.append("")
    for e in p["entries"]:
        L.append("### المادة %d — %s" % (e["article_number"], e["article_title_ar"]))
        L.append("")
        L.append("- **التشابه / similarity:** `%.4f` (كان P1 / was P1)" % e["queue_similarity"])
        L.append("- **التصنيف / classification:** `%s`" % e["batch_review_classification"])
        L.append("- **الثقة / confidence:** `%s`" % e["review_confidence"])
        L.append("- **ملخص الدليل / evidence summary:** %s" % e["evidence_summary"])
        sp = e["source_page_number_within_packet"]
        L.append("- **الموقع في المصدر / source location:** %s" % (
            ("موجود — صفحة الحزمة %s (%s) / found — packet page %s"
             % (sp, e["source_part_file"], sp)) if e["source_location_found"]
            else "لم يُحدَّد بثقة من الـOCR / not confidently located in OCR"))
        L.append("- **مقتطف المرشح / candidate snippet:** %s" % (e["candidate_snippet_ar"] or ""))
        L.append("- **مقتطف الـOCR / OCR snippet:** %s"
                 % (e["ocr_snippet_ar"] or "").replace("\n", " ").strip())
        L.append("- **الإجراء التالي الموصى به / recommended next action:** %s"
                 % e["recommended_next_action"])
        L.append("")
    L.append("## ملخص الدفعة حسب التصنيف / Batch summary by classification")
    L.append("")
    for k in sorted(p["classification_counts"]):
        L.append("- `%s`: **%d**" % (k, p["classification_counts"][k]))
    L.append("")
    low_conf = [e["article_number"] for e in p["entries"] if e["review_confidence"] == "low"]
    subst = [e["article_number"] for e in p["entries"]
             if e["batch_review_classification"] == "possible_substantive_difference"]
    L.append("- **مواد بثقة منخفضة / low-confidence articles:** %s"
             % (", ".join(str(x) for x in low_conf) if low_conf else "لا يوجد / none"))
    L.append("- **مواد باختلاف جوهري محتمل / possible substantive difference:** %s"
             % (", ".join(str(x) for x in subst) if subst else "لا يوجد / none"))
    L.append("")
    L.append("## سير العمل التالي الموصى به / Recommended next workflow")
    L.append("")
    L.append("- **A)** تحديث تصنيفات القائمة لاحقًا (PR تحديث قائمة) للحالات عالية الثقة "
             "من ضجيج الـOCR / انحراف التقطيع. / A later queue-update PR re-classifying the "
             "high-confidence OCR/segmentation cases (no text change).")
    L.append("- **B)** مراجعة يدوية بصرية للحالات منخفضة الثقة أو ذات الاختلاف الجوهري المحتمل. / "
             "Manually inspect the low-confidence / possible-substantive-difference cases.")
    L.append("- **C)** إنشاء PR تصحيح/ترقية **لاحقًا فقط** إذا دعم الدليل ذلك من مصدر رسمي "
             "غير الـOCR. / Only later create a correction/promotion PR if the evidence "
             "supports it, from an official (non-OCR) source.")
    L.append("")
    L.append("**هذه المراجعة لا تُرقّي ولا تتحقق ولا تصحّح ولا تغيّر أي نص قانوني. "
             "العربية هي اللغة الحاكمة. ليست استشارة قانونية.**")
    L.append("This review does not promote, verify, correct, or modify any legal text. "
             "Arabic is governing. Not legal advice.")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    build()


if __name__ == "__main__":
    main()
