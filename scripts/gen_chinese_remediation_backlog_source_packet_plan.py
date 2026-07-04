#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chinese remediation backlog + batch plan + source-packet manifest (planning only).

Converts the merged Chinese semantic-QA / gap-plan into an actionable, deterministic remediation
BACKLOG for all 281 articles, groups articles into practical future remediation BATCHES, and
defines a SOURCE-PACKET MANIFEST for future remediation PRs. It does NOT generate, correct,
retranslate, or expand any Chinese text; it stores only article numbers, statuses, references, and
hashes (never full Arabic/English/Chinese text). Chinese stays internal / non-official /
non-binding; Arabic is governing; English is guidance only. Not legal advice.

Reads : reports/chinese_translation_review/chinese_completion_gap_plan_001_281.json
        reports/chinese_translation_review/chinese_internal_llm_semantic_qa_189.json
        data/chinese_internal_legal_llm/…isolable_source_articles.json
        data/official_arabic_legal_llm/…001_281.json
        data/official_english_legal_llm/…001_281.json
Writes: reports/chinese_translation_review/chinese_remediation_backlog_001_281.json
        reports/chinese_translation_review/chinese_remediation_batch_plan.json
        reports/chinese_translation_review/chinese_remediation_source_packet_manifest.json
        reports/chinese_translation_review/CHINESE_REMEDIATION_BACKLOG_AND_SOURCE_PACKET_PLAN_AR.md
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
GAP = os.path.join(RV, "chinese_completion_gap_plan_001_281.json")
QA = os.path.join(RV, "chinese_internal_llm_semantic_qa_189.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
COVERAGE = os.path.join(RV, "chinese_article_coverage_index_001_281.json")

BACKLOG = os.path.join(RV, "chinese_remediation_backlog_001_281.json")
BATCH = os.path.join(RV, "chinese_remediation_batch_plan.json")
MANIFEST = os.path.join(RV, "chinese_remediation_source_packet_manifest.json")
MD = os.path.join(RV, "CHINESE_REMEDIATION_BACKLOG_AND_SOURCE_PACKET_PLAN_AR.md")

STAGE = "CHINESE_REMEDIATION_BACKLOG_AND_SOURCE_PACKET_PLAN"
TARGET = 281
MAX_BATCH = 20

REL = {
    "arabic": "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    "english": "data/official_english_legal_llm/companies_law_m132_1443_official_english_legal_llm_001_281.json",
    "candidate": "data/chinese_internal_legal_llm/companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json",
    "coverage": "reports/chinese_translation_review/chinese_article_coverage_index_001_281.json",
    "qa": "reports/chinese_translation_review/chinese_internal_llm_semantic_qa_189.json",
    "gap": "reports/chinese_translation_review/chinese_completion_gap_plan_001_281.json",
    "backlog": "reports/chinese_translation_review/chinese_remediation_backlog_001_281.json",
}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build():
    gap = {r["article_number"]: r for r in _read(GAP)["article_plan"]}
    qa = {r["article_number"]: r for r in _read(QA)["records"]}
    cand = _read(CANDF)
    cand_by = {r["article_number"]: r for r in cand["records"]}
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}

    records = []
    for n in range(1, TARGET + 1):
        g = gap[n]
        pr = g["priority"]
        bab = g["expected_bab_number"]
        has_cand = g["has_isolable_chinese_candidate"]
        q = qa.get(n)
        manual = bool(q and q["qa_use_status"] == "manual_review_required")

        if pr == "P0":
            track = "P0_no_isolable_text"
            action = "create_new_internal_chinese_translation_from_arabic"
            basis = "official_arabic_plus_chinese_summary_group"
            new_text = True
            human = True
            block_full = True
            block_align = True
            rationale = "لا يوجد نص صيني مستقل على مستوى المادة؛ يلزم إنشاء ترجمة صينية داخلية جديدة من النص العربي الرسمي."
            accept = "توجد ترجمة صينية داخلية جديدة لكل مادة، مطابقة للمعنى العربي الرسمي، موسومة داخلية غير رسمية، ومراجعة بشريًا."
        elif pr == "P1":
            track = "P1_retranslation_or_manual_review"
            action = "manual_legal_translation_review" if manual else "retranslate_internal_chinese_from_arabic"
            basis = "manual_legal_review" if manual else "official_arabic_plus_existing_chinese_candidate"
            new_text = True
            human = True
            block_full = True
            block_align = True
            rationale = ("النص الصيني الحالي يحتاج مراجعة قانونية يدوية." if manual
                         else "النص الصيني الحالي ناقص جوهريًا؛ يلزم إعادة ترجمة من النص العربي الرسمي.")
            accept = "إعادة ترجمة/مراجعة تُغطّي العناصر القانونية العربية، داخلية غير رسمية، ومراجعة بشريًا."
        elif pr == "P2":
            track = "P2_expansion_needed"
            action = "expand_existing_internal_chinese_from_arabic"
            basis = "official_arabic_plus_existing_chinese_candidate"
            new_text = True
            human = False
            block_full = True
            block_align = True
            rationale = "النص الصيني مضغوط؛ يلزم توسعته من النص العربي الرسمي قبل الطبقة الكاملة."
            accept = "توسعة تُضيف التفاصيل المضغوطة دون تغيير المعنى، داخلية غير رسمية."
        else:  # P3
            track = "P3_retain_internal_reference"
            action = "retain_as_internal_reference_no_immediate_action"
            basis = "existing_chinese_internal_candidate"
            new_text = False
            human = False
            block_full = False
            block_align = True
            rationale = "النص الصيني قريب من الاكتمال؛ يُبقى كمرجع داخلي دون إجراء فوري."
            accept = "يبقى كمرشح مرجعي داخلي؛ يُراجع ضمن دفعة تأكيد نهائية قبل أي طبقة كاملة."

        records.append({
            "article_number": n,
            "expected_bab_number": bab,
            "current_priority": pr,
            "current_chinese_status": g["current_chinese_status"],
            "has_isolable_chinese_candidate": has_cand,
            "current_blocker": g["full_layer_blocker"],
            "remediation_track": track,
            "remediation_action": action,
            "source_basis": basis,
            "future_batch_group": None,  # filled after batching
            "requires_new_chinese_text": new_text,
            "requires_human_legal_review": human,
            "should_block_full_chinese_layer": block_full,
            "should_block_trilingual_alignment": block_align,
            "arabic_source_hash_sha256": ar[n]["official_text_hash_sha256"],
            "existing_chinese_candidate_hash_sha256": (
                cand_by[n]["chinese_text_hash_sha256"] if n in cand_by else None),
            "english_guidance_hash_sha256": en[n]["legal_rule_text_hash_sha256"],
            "rationale_ar": rationale,
            "acceptance_criteria_ar": accept,
        })

    rec_by = {r["article_number"]: r for r in records}

    # -- deterministic batches: P0, P1, P2 (<=20, by bab then article); P3 -> 1 confirmation --
    batches = []
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}

    def _make(priority, arts, track, src_files, is_conf=False):
        arts = sorted(arts, key=lambda n: (rec_by[n]["expected_bab_number"], n))
        made = []
        chunks = [arts[i:i + MAX_BATCH] for i in range(0, len(arts), MAX_BATCH)] or []
        for i, ch in enumerate(chunks, start=1):
            bid = "%s-%s%03d" % (priority, ("CONF-" if is_conf else ""), i)
            babs = sorted({rec_by[n]["expected_bab_number"] for n in ch})
            for n in ch:
                rec_by[n]["future_batch_group"] = bid
            made.append({
                "batch_id": bid,
                "priority": priority,
                "remediation_track": track,
                "article_count": len(ch),
                "article_numbers": ch,
                "expected_babs": babs,
                "source_files_required": src_files,
                "output_not_to_create_yet": "remediated internal Chinese reference text for these "
                                            "articles (do NOT generate/correct in this PR)",
                "future_allowed_output_after_authorization": "new / retranslated / expanded "
                    "internal Chinese reference text for the listed articles, derived from the "
                    "official Arabic governing text, ONLY after Abdullah's explicit batch "
                    "authorization; output stays internal / non-official / non-binding",
                "acceptance_criteria_ar": rec_by[ch[0]]["acceptance_criteria_ar"],
            })
        return made

    p0 = _make("P0", [r["article_number"] for r in records if r["current_priority"] == "P0"],
               "P0_no_isolable_text", [REL["arabic"], REL["coverage"], REL["backlog"]])
    p1 = _make("P1", [r["article_number"] for r in records if r["current_priority"] == "P1"],
               "P1_retranslation_or_manual_review",
               [REL["arabic"], REL["candidate"], REL["qa"], REL["backlog"]])
    p2 = _make("P2", [r["article_number"] for r in records if r["current_priority"] == "P2"],
               "P2_expansion_needed", [REL["arabic"], REL["candidate"], REL["backlog"]])
    p3 = _make("P3", [r["article_number"] for r in records if r["current_priority"] == "P3"],
               "P3_retain_internal_reference", [REL["candidate"], REL["qa"], REL["backlog"]],
               is_conf=True)
    batches = p0 + p1 + p2 + p3
    counts = {"P0": len(p0), "P1": len(p1), "P2": len(p2), "P3": len(p3)}

    pc = {p: sum(1 for r in records if r["current_priority"] == p)
          for p in ("P0", "P1", "P2", "P3")}
    remediation_required = pc["P0"] + pc["P1"] + pc["P2"]

    backlog = {
        "stage": STAGE,
        "not_legal_advice": True,
        "total_articles": TARGET,
        "p0_count": pc["P0"],
        "p1_count": pc["P1"],
        "p2_count": pc["P2"],
        "p3_count": pc["P3"],
        "remediation_required_count": remediation_required,
        "no_action_internal_reference_count": pc["P3"],
        "full_chinese_translation_claimed": False,
        "official_chinese_translation_claimed": False,
        "chinese_binding_claimed": False,
        "chinese_governing_claimed": False,
        "corrected_chinese_created": False,
        "generated_chinese_created": False,
        "arabic_used_to_generate_chinese": False,
        "english_used_to_generate_chinese": False,
        "backlog_summary": {
            "remediation_track_counts": {
                t: sum(1 for r in records if r["remediation_track"] == t)
                for t in ("P0_no_isolable_text", "P1_retranslation_or_manual_review",
                          "P2_expansion_needed", "P3_retain_internal_reference")},
            "requires_new_chinese_text_count": sum(1 for r in records
                                                   if r["requires_new_chinese_text"]),
            "requires_human_legal_review_count": sum(1 for r in records
                                                     if r["requires_human_legal_review"]),
            "controlling_source": "official_arabic_governing_text",
            "note_ar": "خطة معالجة فقط؛ لا يُنشأ أي نص صيني في هذه المرحلة. العربية هي الحاكمة.",
        },
        "records": records,
    }
    with open(BACKLOG, "w", encoding="utf-8") as fh:
        json.dump(backlog, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    batch_plan = {
        "stage": STAGE,
        "not_legal_advice": True,
        "batch_count": len(batches),
        "p0_batch_count": counts["P0"],
        "p1_batch_count": counts["P1"],
        "p2_batch_count": counts["P2"],
        "p3_confirmation_batch_count": counts["P3"],
        "max_articles_per_batch": MAX_BATCH,
        "ordering": "priority (P0,P1,P2, then P3 confirmation) -> expected_bab -> article_number",
        "no_chinese_generated_in_this_pr": True,
        "batches": batches,
    }
    with open(BATCH, "w", encoding="utf-8") as fh:
        json.dump(batch_plan, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    manifest = {
        "stage": STAGE,
        "not_legal_advice": True,
        "source_files": [
            {"path": REL["arabic"], "role": "official_arabic_governing_text_controlling_source"},
            {"path": REL["english"], "role": "official_english_guidance_only_secondary"},
            {"path": REL["candidate"], "role": "existing_chinese_internal_candidate"},
            {"path": REL["coverage"], "role": "chinese_article_coverage_index"},
            {"path": REL["qa"], "role": "chinese_semantic_qa"},
            {"path": REL["gap"], "role": "chinese_completion_gap_plan"},
            {"path": REL["backlog"], "role": "chinese_remediation_backlog"},
            {"path": "inputs/chinese_translation_source_pdfs/",
             "role": "chinese_source_pdfs_optional_historical_context"},
            {"path": "data/chinese_translation_sources/",
             "role": "chinese_extracted_sources_optional_historical_context"},
        ],
        "protected_files": [
            "data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json",
            REL["arabic"], REL["english"],
            "data/english_reference/companies_law_m132_1443_en_reference_001_281.json",
            "data/chinese_legal_llm/ (old Chinese Legal LLM, 5 files / 23 records)",
            REL["candidate"],
            "inputs/chinese_translation_source_pdfs/ (Chinese source PDFs)",
            "data/chinese_translation_sources/ (Chinese extracted source files)",
            "reports/official_arabic_verification/ (OCR reports/queues)",
        ],
        "future_batch_requirements": {
            "authorization": "each remediation batch requires Abdullah's explicit authorization "
                             "before any Chinese text is created",
            "controlling_source": "official_arabic_governing_text",
            "english_role": "guidance_only_secondary",
            "output_trust_posture": "internal_working_translation_source; official_translation="
                                    "false; not_binding=true; governing_text_language=ar",
            "order": "P0 batches first, then P1, then P2; P3 is a final confirmation batch",
        },
        "forbidden_actions": [
            "no full Chinese 281 layer",
            "no trilingual alignment",
            "no official/binding/governing Chinese claim",
            "no modification of protected layers",
            "no bulk generation without batch authorization",
            "no source PDF rewrite",
            "no OCR/provenance detour",
        ],
        "required_trust_posture": {
            "arabic_governs": True,
            "chinese_official": False,
            "chinese_binding": False,
            "chinese_governing": False,
            "english_guidance_only": True,
        },
        "validation_requirements": [
            "each future remediation PR must keep all protected_files unchanged",
            "each future remediation PR must add a validator + tests for its batch",
            "each future remediation PR must not claim official/binding/governing/full Chinese",
        ],
    }
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    _write_md(backlog, batch_plan)
    print("wrote remediation backlog (%d) + %d batches (P0=%d P1=%d P2=%d P3conf=%d); "
          "remediation_required=%d" % (len(records), len(batches), counts["P0"], counts["P1"],
                                       counts["P2"], counts["P3"], remediation_required))


def _write_md(backlog, batch_plan):
    L = []
    L.append("# سجل معالجة الصينية وخطة حزمة المصادر")
    L.append("# Chinese remediation backlog & source-packet plan")
    L.append("")
    L.append("> **هذه خطة معالجة/حزمة مصادر فقط، وليست ترجمة ولا تصحيحًا ولا استشارة قانونية.** "
             "لم يُنشأ أو يُصحَّح أي نص صيني في هذه المرحلة.")
    L.append("")
    L.append("## ملخص تنفيذي / Executive summary")
    L.append("")
    L.append("- **حالة المشروع بعد PR #54:** توجد مراجعة دلالية (189) وخطة فجوات (281)؛ هذه "
             "المرحلة تحوّلها إلى سجل معالجة قابل للتنفيذ ودُفعات مستقبلية.")
    L.append("- **P0 = %d** · **P1 = %d** · **P2 = %d** · **P3 = %d**."
             % (backlog["p0_count"], backlog["p1_count"], backlog["p2_count"],
                backlog["p3_count"]))
    L.append("- **تتطلب معالجة (P0+P1+P2):** %d · **بلا إجراء (مرجع داخلي، P3):** %d."
             % (backlog["remediation_required_count"],
                backlog["no_action_internal_reference_count"]))
    L.append("")
    L.append("## معنى الأولويات / What P0–P3 mean")
    L.append("")
    L.append("- **P0** — لا نص صيني مستقل على مستوى المادة → إنشاء ترجمة صينية داخلية جديدة من العربية.")
    L.append("- **P1** — نص ناقص جوهريًا أو يحتاج مراجعة يدوية → إعادة ترجمة/مراجعة من العربية.")
    L.append("- **P2** — نص مضغوط → توسعة من العربية.")
    L.append("- **P3** — قريب من الاكتمال → يُبقى كمرجع داخلي (دفعة تأكيد نهائية فقط).")
    L.append("")
    L.append("## لماذا لا نبدأ المحاذاة الثلاثية الآن / Why no trilingual alignment yet")
    L.append("")
    L.append("لأن %d مادة (P0+P1+P2) تحتاج معالجة من النص العربي الحاكم أولًا؛ المحاذاة قبل ذلك "
             "ستُحاذي نصوصًا صينية ناقصة/مضغوطة." % backlog["remediation_required_count"])
    L.append("")
    L.append("## خطة الدُفعات / Batch plan")
    L.append("")
    L.append("- **إجمالي الدُفعات:** %d (P0: %d، P1: %d، P2: %d، دفعة تأكيد P3: %d)."
             % (batch_plan["batch_count"], batch_plan["p0_batch_count"],
                batch_plan["p1_batch_count"], batch_plan["p2_batch_count"],
                batch_plan["p3_confirmation_batch_count"]))
    L.append("- **حد أقصى للدفعة:** %d مادة · الترتيب: الأولوية ← الباب ← رقم المادة."
             % batch_plan["max_articles_per_batch"])
    L.append("")
    L.append("| الدفعة | الأولوية | عدد المواد | الأبواب |")
    L.append("|---|---|---|---|")
    for b in batch_plan["batches"]:
        L.append("| `%s` | %s | %d | %s |" % (
            b["batch_id"], b["priority"], b["article_count"],
            ", ".join(str(x) for x in b["expected_babs"])))
    L.append("")
    L.append("## ما الذي يحتاج موافقة عبدالله / Requires Abdullah's authorization")
    L.append("")
    L.append("إنشاء أي نص صيني معالَج (P0/P1/P2) يتطلب **موافقة صريحة على الدفعة** قبل التنفيذ. "
             "لا يُنشأ أي نص صيني في هذا الـPR.")
    L.append("")
    L.append("## ملفات يجب أن تبقى محمية / Protected files")
    L.append("")
    L.append("المصدر العربي الرسمي، الطبقة العربية 281، الطبقة الإنجليزية 281، المرجع الإنجليزي، "
             "الطبقة الصينية القديمة، مرشح الصينية الداخلي، ملفات مصادر الصينية وPDF، وتقارير الـOCR.")
    L.append("")
    L.append("## توصية المرحلة التالية / Next-stage recommendation")
    L.append("")
    L.append("بدء **Batch P0-001** فقط بعد موافقة عبدالله، مع إنشاء ترجمة صينية داخلية جديدة من "
             "النص العربي الرسمي للمواد المحددة فقط.")
    L.append("")
    L.append("**العربية هي اللغة الحاكمة. الصينية داخلية غير رسمية وغير مُلزِمة. الإنجليزية "
             "استرشادية. ليست استشارة قانونية.**")
    L.append("Arabic is governing. Chinese is internal, non-official, non-binding. English is "
             "guidance only. Not legal advice.")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    build()


if __name__ == "__main__":
    main()
