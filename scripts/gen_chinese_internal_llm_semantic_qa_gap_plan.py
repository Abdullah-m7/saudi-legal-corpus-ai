#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chinese internal candidate — semantic QA (189) + completion gap plan (281).

Assesses the 189 Chinese internal candidate records against the official Arabic governing text
(conservative, automated heuristic QA — needs human confirmation), classifies which are usable as
internal reference vs too condensed/incomplete, keeps the 92 excluded articles BLOCKED until
Arabic-based expansion/retranslation, and produces a practical next-work plan for all 281 articles.

This QA does NOT generate, correct, rewrite, expand, or summarize any Chinese legal text, does NOT
modify the candidate/source data, and does NOT create a full Chinese layer or multilingual
alignment. Chinese is internal working/reference only — not official, not binding, not governing;
Arabic is governing. English is used only as secondary conceptual guidance. Not legal advice.

Reads : data/chinese_internal_legal_llm/…isolable_source_articles.json
        reports/chinese_translation_review/chinese_article_coverage_index_001_281.json
        reports/chinese_translation_review/chinese_all_babs_source_inventory.json
        reports/chinese_translation_review/bab1_original_pdf_translation_review.json
        data/official_arabic_legal_llm/…001_281.json
        data/official_english_legal_llm/…001_281.json (secondary guidance only)
Writes: reports/chinese_translation_review/chinese_internal_llm_semantic_qa_189.json
        reports/chinese_translation_review/chinese_completion_gap_plan_001_281.json
        reports/chinese_translation_review/CHINESE_INTERNAL_LLM_SEMANTIC_QA_AND_GAP_PLAN_AR.md
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
CAND = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                    "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
IDX = os.path.join(RV, "chinese_article_coverage_index_001_281.json")
INV = os.path.join(RV, "chinese_all_babs_source_inventory.json")
BAB1_REVIEW = os.path.join(RV, "bab1_original_pdf_translation_review.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
QA_JSON = os.path.join(RV, "chinese_internal_llm_semantic_qa_189.json")
GAP_JSON = os.path.join(RV, "chinese_completion_gap_plan_001_281.json")
MD = os.path.join(RV, "CHINESE_INTERNAL_LLM_SEMANTIC_QA_AND_GAP_PLAN_AR.md")

STAGE = "CHINESE_INTERNAL_LLM_SEMANTIC_QA_AND_GAP_PLAN"
TARGET = 281

BAB_RANGES = {1: (1, 34), 2: (35, 50), 3: (51, 57), 4: (58, 137), 5: (138, 155),
              6: (156, 184), 7: (185, 196), 8: (197, 215), 9: (216, 219), 10: (220, 234),
              11: (235, 241), 12: (242, 259), 13: (260, 271), 14: (272, 281)}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _bab_of(n):
    for b, (lo, hi) in BAB_RANGES.items():
        if lo <= n <= hi:
            return b
    return None


def _classify(n, zh_text, ar_text, style, bab1_status):
    """Conservative, deterministic QA. All records stay non-official / internal / not full-ready."""
    zl, al = len(zh_text), len(ar_text)
    ratio = (zl / al) if al else 0.0

    # anomaly: Chinese much longer than Arabic (likely a thematic chunk spanning items)
    if ratio > 2.0:
        return dict(align="not_assessed", complete="not_assessed",
                    use="manual_review_required",
                    action="manual_legal_translation_review_required", priority="P1",
                    missing=["تعذّر تقييم آلي موثوق (نسبة الطول غير معتادة)؛ تحتاج مراجعة يدوية"],
                    risk=["قد يشمل النص الصيني عدة بنود مجمّعة؛ المطابقة على مستوى المادة غير مؤكدة"],
                    note="نسبة طول غير معتادة؛ مراجعة يدوية مطلوبة قبل أي استخدام كامل")

    # Bab 1: preserve the prior conservative review posture where it was flagged worse
    if bab1_status == "materially_incomplete_needs_retranslation":
        complete = "materially_incomplete"
    elif bab1_status == "summary_needs_expansion":
        complete = "condensed" if ratio >= 0.20 else "materially_incomplete"
    else:
        if ratio < 0.20:
            complete = "materially_incomplete"
        elif ratio < 0.45:
            complete = "condensed"
        else:
            complete = "near_full"
    # style cap: thematic summary sources are never rated near_full
    if style == "summary_or_core_terms" and complete == "near_full":
        complete = "condensed"

    if complete == "materially_incomplete":
        return dict(align="low", complete=complete,
                    use="not_safe_for_full_layer_needs_retranslation",
                    action="retranslate_from_arabic_before_full_chinese_layer", priority="P1",
                    missing=["النص الصيني مضغوط بشدة مقارنةً بالنص العربي؛ يُرجَّح إسقاط عناصر "
                             "قانونية جوهرية"],
                    risk=["قد يكون النص الصيني ناقصًا أو ملخِّصًا لدرجة تُخلّ بالمعنى القانوني"],
                    note="غير آمن كطبقة كاملة؛ يحتاج إعادة ترجمة من العربية")
    if complete == "condensed":
        return dict(align="medium", complete=complete,
                    use="usable_for_retrieval_but_needs_expansion_before_full_layer",
                    action="expand_from_arabic_before_full_chinese_layer", priority="P2",
                    missing=["تفاصيل إجرائية/فرعية مضغوطة مقارنةً بالنص العربي الرسمي"],
                    risk=[],
                    note="صالح للاسترجاع كمرجع داخلي؛ يحتاج توسعة من العربية قبل الطبقة الكاملة")
    return dict(align="high", complete=complete,
                use="usable_internal_reference_with_caution",
                action="retain_as_internal_reference_candidate", priority="P3",
                missing=[],
                risk=[],
                note="متوافق إلى حد كبير؛ يُبقى كمرشح مرجعي داخلي مع الحذر (ليس طبقة كاملة)")


def build():
    cand = _read(CAND)
    idx = {r["article_number"]: r for r in _read(IDX)["records"]}
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    bab1 = {r["article_number"]: r.get("coverage_status")
            for r in _read(BAB1_REVIEW)["records"]}
    _ = _read(ENGLISH)  # secondary guidance only (not used to generate Chinese)

    excluded = list(cand["excluded_articles"])
    excluded_set = set(excluded)

    qa_records = []
    qa_by_num = {}
    for c in cand["records"]:
        n = c["article_number"]
        style = c["source_coverage"]["likely_translation_style"]
        cl = _classify(n, c["chinese_text"], ar[n]["official_text_ar"], style, bab1.get(n))
        rec = {
            "article_number": n,
            "expected_bab_number": c["expected_bab_number"],
            "chinese_record_id": c["record_id"],
            "chinese_text_hash_sha256": c["chinese_text_hash_sha256"],
            "arabic_text_hash_sha256": ar[n]["official_text_hash_sha256"],
            "chinese_source_coverage_posture": c["source_coverage"]["coverage_posture"],
            "chinese_likely_translation_style": style,
            "semantic_alignment_rating": cl["align"],
            "legal_completeness_rating": cl["complete"],
            "qa_use_status": cl["use"],
            "missing_or_compressed_legal_elements_ar": cl["missing"],
            "possible_risk_notes_ar": cl["risk"],
            "recommended_action": cl["action"],
            "priority": cl["priority"],
            "reviewer_note_ar": cl["note"],
        }
        qa_records.append(rec)
        qa_by_num[n] = rec

    def _count(key):
        d = {}
        for r in qa_records:
            d[r[key]] = d.get(r[key], 0) + 1
        return d

    qa_summary = {
        "semantic_alignment_rating_counts": _count("semantic_alignment_rating"),
        "legal_completeness_rating_counts": _count("legal_completeness_rating"),
        "qa_use_status_counts": _count("qa_use_status"),
        "priority_counts": _count("priority"),
        "review_method": "automated_conservative_heuristic (zh/ar length ratio + coverage "
                         "translation style + Bab1 prior review); needs human confirmation. No "
                         "Chinese generated/corrected; Arabic is the controlling comparison.",
    }

    qa = {
        "stage": STAGE,
        "not_legal_advice": True,
        "source_candidate_file": os.path.relpath(CAND, ROOT),
        "arabic_governing_file": os.path.relpath(ARABIC, ROOT),
        "english_guidance_file": os.path.relpath(ENGLISH, ROOT),
        "candidate_record_count": len(cand["records"]),
        "reviewed_record_count": len(qa_records),
        "excluded_article_count": len(excluded),
        "full_chinese_translation_claimed": False,
        "official_chinese_translation_claimed": False,
        "chinese_binding_claimed": False,
        "chinese_governing_claimed": False,
        "corrected_chinese_created": False,
        "arabic_used_to_generate_chinese": False,
        "english_used_to_generate_chinese": False,
        "qa_summary": qa_summary,
        "records": qa_records,
    }
    with open(QA_JSON, "w", encoding="utf-8") as fh:
        json.dump(qa, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # -- 281-article gap plan --
    plan = []
    for n in range(1, TARGET + 1):
        b = _bab_of(n)
        if n in excluded_set:
            plan.append({
                "article_number": n,
                "expected_bab_number": b,
                "current_chinese_status": "excluded_no_isolable_article_text",
                "has_isolable_chinese_candidate": False,
                "semantic_qa_status": "excluded_not_in_qa",
                "full_layer_blocker": "no_isolable_chinese_text",
                "required_next_action": "manually_segment_or_replace_source",
                "priority": "P0",
                "source_for_next_action": "chinese_source_pdf_summary_group",
            })
        else:
            q = qa_by_num[n]
            blocker = {
                "materially_incomplete": "incomplete_translation_needs_retranslation",
                "condensed": "condensed_translation_needs_expansion",
                "near_full": "none_for_internal_reference_only",
                "not_assessed": "manual_review_required",
            }[q["legal_completeness_rating"]]
            nxt = {
                "materially_incomplete": ("retranslate_from_arabic", "official_arabic_governing_text"),
                "condensed": ("expand_existing_chinese_from_arabic", "official_arabic_governing_text"),
                "near_full": ("retain_candidate_for_internal_reference",
                              "existing_chinese_internal_candidate"),
                "not_assessed": ("manual_review_before_alignment", "manual_legal_translation_review"),
            }[q["legal_completeness_rating"]]
            plan.append({
                "article_number": n,
                "expected_bab_number": b,
                "current_chinese_status": "internal_candidate_exists",
                "has_isolable_chinese_candidate": True,
                "semantic_qa_status": q["qa_use_status"],
                "full_layer_blocker": blocker,
                "required_next_action": nxt[0],
                "priority": q["priority"],
                "source_for_next_action": nxt[1],
            })

    def _plan_count(key):
        d = {}
        for r in plan:
            d[r[key]] = d.get(r[key], 0) + 1
        return d

    gap_summary = {
        "current_chinese_status_counts": _plan_count("current_chinese_status"),
        "full_layer_blocker_counts": _plan_count("full_layer_blocker"),
        "priority_counts": _plan_count("priority"),
        "p0_articles": [r["article_number"] for r in plan if r["priority"] == "P0"],
        "p1_articles": [r["article_number"] for r in plan if r["priority"] == "P1"],
    }

    gap = {
        "stage": STAGE,
        "not_legal_advice": True,
        "total_articles": TARGET,
        "candidate_articles": len(cand["records"]),
        "excluded_articles": len(excluded),
        "qa_reviewed_articles": len(qa_records),
        "completion_strategy": "Fix P0 (92 articles with no isolable Chinese text) and P1 "
                               "(materially-incomplete candidates) from the official Arabic "
                               "governing text before building any full Chinese 281 layer or "
                               "multilingual alignment. Expand P2 condensed candidates; retain "
                               "P3 near-full candidates as internal reference. Chinese stays "
                               "internal / non-official / non-binding; Arabic governs.",
        "gap_summary": gap_summary,
        "article_plan": plan,
    }
    with open(GAP_JSON, "w", encoding="utf-8") as fh:
        json.dump(gap, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    _write_md(qa, gap)
    print("wrote Chinese semantic QA (%d) + gap plan (%d); P0=%d P1=%d"
          % (len(qa_records), len(plan), len(gap_summary["p0_articles"]),
             len(gap_summary["p1_articles"])))


def _write_md(qa, gap):
    qs = qa["qa_summary"]
    gsum = gap["gap_summary"]
    L = []
    L.append("# مراجعة دلالية وخطة سدّ الفجوات — الطبقة الصينية الداخلية")
    L.append("# Chinese internal candidate — semantic QA & completion gap plan")
    L.append("")
    L.append("> **هذه مراجعة جودة/خطة فقط، وليست ترجمة ولا تصحيحًا ولا استشارة قانونية.** لم "
             "يُنشأ أو يُصحَّح أي نص صيني، ولم تُعدَّل بيانات المرشح.")
    L.append("")
    L.append("## ملخص تنفيذي / Executive summary")
    L.append("")
    L.append("- **عدد المواد ذات المرشح الصيني الداخلي:** %d." % qa["candidate_record_count"])
    L.append("- **عدد المواد المستبعدة:** %d." % qa["excluded_article_count"])
    L.append("- **هل هذه طبقة صينية كاملة؟** **لا** (`full_chinese_translation_claimed = false`).")
    L.append("- **هل الصينية رسمية أو حاكمة؟** **لا**. **العربية هي النص الحاكم.**")
    L.append("- المراجعة آلية تحفّظية (نسبة الطول + نمط الترجمة + مراجعة الباب الأول)؛ تحتاج "
             "تأكيدًا بشريًا.")
    L.append("")
    L.append("## جدول ملخص التصنيف / Classification summary")
    L.append("")
    L.append("**درجة المطابقة الدلالية / semantic_alignment_rating:**")
    for k in ("high", "medium", "low", "not_assessed"):
        L.append("- `%s`: **%d**" % (k, qs["semantic_alignment_rating_counts"].get(k, 0)))
    L.append("")
    L.append("**اكتمال قانوني / legal_completeness_rating:**")
    for k in ("near_full", "condensed", "materially_incomplete", "not_assessed"):
        L.append("- `%s`: **%d**" % (k, qs["legal_completeness_rating_counts"].get(k, 0)))
    L.append("")
    L.append("**حالة الاستخدام / qa_use_status:**")
    for k in ("usable_internal_reference_with_caution",
              "usable_for_retrieval_but_needs_expansion_before_full_layer",
              "not_safe_for_full_layer_needs_retranslation", "manual_review_required"):
        L.append("- `%s`: **%d**" % (k, qs["qa_use_status_counts"].get(k, 0)))
    L.append("")
    L.append("## أولويات P0 / P1 / Priority lists")
    L.append("")
    L.append("- **P0 (المواد المستبعدة — لا نص صيني مستقل، %d):** `%s`"
             % (len(gsum["p0_articles"]), ", ".join(str(x) for x in gsum["p0_articles"])))
    L.append("- **P1 (مرشحات ناقصة جوهريًا / مراجعة يدوية، %d):** `%s`"
             % (len(gsum["p1_articles"]), ", ".join(str(x) for x in gsum["p1_articles"])))
    L.append("")
    L.append("## توصية عملية للمرحلة التالية / Recommendation")
    L.append("")
    L.append("سدّ مواد **P0** (الـ92 بلا نص صيني مستقل) و**P1** (المرشحات الناقصة جوهريًا) من "
             "**النص العربي الرسمي الحاكم** أولًا، ثم توسعة مواد **P2** المضغوطة، مع إبقاء مواد "
             "**P3** القريبة من الاكتمال كمرجع داخلي. الصينية تبقى داخلية غير رسمية وغير مُلزِمة؛ "
             "العربية هي الحاكمة.")
    L.append("")
    L.append("> **تنبيه:** لا تبدأ المحاذاة الثلاثية (عربي/إنجليزي/صيني) قبل معالجة مواد "
             "**P0/P1** وتقرير مصير الـ**92** مادة مستبعدة.")
    L.append("")
    L.append("**العربية هي اللغة الحاكمة. الصينية ترجمة داخلية غير رسمية وغير مُلزِمة. "
             "ليست ترجمة كاملة موثّقة. ليست استشارة قانونية.**")
    L.append("Arabic is governing. Chinese is internal, non-official, non-binding. Not a "
             "complete verified translation. Not legal advice.")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    build()


if __name__ == "__main__":
    main()
