#!/usr/bin/env python3
"""
Retrieval Prompt Pack Builder — Primary Arabic Governing Records

Deterministic, offline prompt pack generator. Takes a query, runs the
existing local lexical search via the retrieval context pack builder,
and emits a safe, source-grounded prompt template for future LLM/RAG use.

This tool builds prompt packs only.
It does NOT execute prompts.
It does NOT call any model.
It does NOT produce final legal answers.
It does NOT generate legal advice.
It does NOT interpret legal text.
It does NOT summarize legal text as a legal conclusion.
It does NOT create RAG, embeddings, semantic search, API, UI, database,
or network calls.

Usage:
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة"
  python3 scripts/build_retrieval_prompt_pack.py "الجمعية العامة" --limit 5
  python3 scripts/build_retrieval_prompt_pack.py "التصفية" --track companies_law --limit 5
  python3 scripts/build_retrieval_prompt_pack.py "التوكيل" --record-type appendix --limit 1
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --mode evidence_brief
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --mode cautious_answer_draft
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --mode citation_check
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --format json
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --format markdown
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --output /tmp/prompt_pack.json
  python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --include-full-text --limit 3
"""

import argparse
import json
import os
import sys
from datetime import date
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import and reuse existing context pack builder functions
sys.path.insert(0, REPO_ROOT)
from scripts.build_retrieval_context_pack import build_context_pack, LEGAL_BOUNDARIES
from scripts.search_primary_arabic_export import normalize_arabic, load_records, search

PROMPT_PACK_VERSION = "1.0"
SOURCE_CONTEXT_PACK_TOOL = "scripts/build_retrieval_context_pack.py"
SOURCE_SEARCH_TOOL = "scripts/search_primary_arabic_export.py"
SOURCE_EXPORT_FILE = "data/exports/v1/primary_arabic_governing_records.jsonl"
RETRIEVAL_METHOD = "deterministic_lexical_search"

PROMPT_MODES = ["evidence_brief", "cautious_answer_draft", "citation_check"]

# ─── Prompt policy ───

PROMPT_POLICY = {
    "use_only_retrieved_records": True,
    "cite_every_legal_statement": True,
    "no_legal_advice": True,
    "no_official_translation": True,
    "no_legal_interpretation_by_tool": True,
    "no_generated_legal_conclusions_by_tool": True,
    "no_external_sources": True,
    "insufficient_context_rule": True,
    "Arabic official source governs": True,
    "repository-owner legal review active; external legal review optional for enterprise/official adoption": True,
}


# ─── Prompt text templates ───

def _build_evidence_brief_prompt(query: str, records: list, include_full_text: bool) -> str:
    """Build prompt text for evidence_brief mode."""
    lines = []
    lines.append("## تعليمات المهمة")
    lines.append("")
    lines.append("أنت مساعد قانوني يُطلب منه تنظيم موجز أدلة من الأحكام المسترجعة فقط.")
    lines.append(f"الاستعلام: {query}")
    lines.append("")
    lines.append("## القواعد الصارمة")
    lines.append("")
    lines.append("1. استخدم فقط السجلات المسترجعة المرفقة أدناه.")
    lines.append("2. لا تضف أحكامًا أو قوانين خارجية غير موجودة في السجلات.")
    lines.append("3. لا تختلق أرقام مواد أو إشارات قانونية غير موجودة.")
    lines.append("4. لا تقدم استشارة قانونية.")
    lines.append("5. لا تذكر استنتاجات قانونية نهائية.")
    lines.append("6. إذا كانت السجلات غير كافية، فاذكر صراحة أن السياق المسترجع غير كافٍ.")
    lines.append("7. استشهد بمعرف السجل (export_record_id) لكل عبارة قانونية أو واقعية.")
    lines.append("8. المصدر العربي الرسمي هو الحاكم.")
    lines.append("9. هذه المرحلة لتطبيق المراجعة القانونية من مالك المستودع؛ المراجعة القانونية الخارجية اختيارية للاعتماد المؤسسي أو الرسمي.")
    lines.append("")
    lines.append("## السجلات المسترجعة")
    lines.append("")
    for rec in records:
        rid = rec.get("export_record_id", "غير محدد")
        title = rec.get("title_ar") or "(بدون عنوان)"
        track = rec.get("source_track_id", "غير محدد")
        rtype = rec.get("record_type", "غير محدد")
        snippet = rec.get("snippet", "")
        lines.append(f"### السجل: {rid}")
        lines.append(f"- العنوان: {title}")
        lines.append(f"- المسار: {track}")
        lines.append(f"- النوع: {rtype}")
        if rec.get("article_number") is not None:
            lines.append(f"- رقم المادة: {rec['article_number']}")
        if rec.get("record_number") is not None:
            lines.append(f"- رقم السجل: {rec['record_number']}")
        lines.append(f"- مقتطف: {snippet}")
        if include_full_text and rec.get("text_ar"):
            lines.append(f"- النص الكامل: {rec['text_ar']}")
        lines.append("")
    lines.append("## المطلوب")
    lines.append("")
    lines.append("نظّم موجز أدلة مرتبًا حسب الموضوع، مع استشهاد صريح بمعرف السجل لكل عبارة.")
    lines.append("إذا كانت السجلات غير كافية لتغطية الاستعلام، اذكر ذلك صراحة.")
    lines.append("")
    return "\n".join(lines)


def _build_cautious_answer_draft_prompt(query: str, records: list, include_full_text: bool) -> str:
    """Build prompt text for cautious_answer_draft mode."""
    lines = []
    lines.append("## تعليمات المهمة")
    lines.append("")
    lines.append("أنت مساعد قانوني يُطلب منه صياغة إجابة معلوماتية حذرة ومستندة إلى الاستشهاد.")
    lines.append(f"الاستعلام: {query}")
    lines.append("")
    lines.append("## القواعد الصارمة")
    lines.append("")
    lines.append("1. ابدأ بملاحظة حدية واضحة تفيد بأن هذا ليس استشارة قانونية.")
    lines.append("2. لا تستخدم عبارة «يجب عليك» كتوجيه قانوني.")
    lines.append("3. لا تنصح بقرارات تقاضي أو امتثال.")
    lines.append("4. لا تحل محل المحامي أو المراجع القانوني.")
    lines.append("5. استشهد بمعرف السجل (export_record_id) لكل عبارة قانونية.")
    lines.append("6. حدّد عدم اليقين وعدم كفاية السياق بصراحة.")
    lines.append("7. لا تستخدم سجلات إنجليزية أو صينية.")
    lines.append("8. لا تعتمد على ذاكرة النموذج — استخدم فقط السجلات المرفقة.")
    lines.append("9. المصدر العربي الرسمي هو الحاكم.")
    lines.append("10. هذه المرحلة لتطبيق المراجعة القانونية من مالك المستودع؛ المراجعة القانونية الخارجية اختيارية للاعتماد المؤسسي أو الرسمي.")
    lines.append("")
    lines.append("## السجلات المسترجعة")
    lines.append("")
    for rec in records:
        rid = rec.get("export_record_id", "غير محدد")
        title = rec.get("title_ar") or "(بدون عنوان)"
        track = rec.get("source_track_id", "غير محدد")
        rtype = rec.get("record_type", "غير محدد")
        snippet = rec.get("snippet", "")
        lines.append(f"### السجل: {rid}")
        lines.append(f"- العنوان: {title}")
        lines.append(f"- المسار: {track}")
        lines.append(f"- النوع: {rtype}")
        if rec.get("article_number") is not None:
            lines.append(f"- رقم المادة: {rec['article_number']}")
        if rec.get("record_number") is not None:
            lines.append(f"- رقم السجل: {rec['record_number']}")
        lines.append(f"- مقتطف: {snippet}")
        if include_full_text and rec.get("text_ar"):
            lines.append(f"- النص الكامل: {rec['text_ar']}")
        lines.append("")
    lines.append("## المطلوب")
    lines.append("")
    lines.append("صياغة إجابة معلوماتية حذرة مع استشهاد صريح بمعرف السجل لكل عبارة قانونية.")
    lines.append("ابدأ بملاحظة حدية. حدّد عدم اليقين. لا تقدم استنتاجات قانونية نهائية.")
    lines.append("إذا كانت السجلات غير كافية، اذكر ذلك صراحة.")
    lines.append("")
    return "\n".join(lines)


def _build_citation_check_prompt(query: str, records: list, include_full_text: bool) -> str:
    """Build prompt text for citation_check mode."""
    lines = []
    lines.append("## تعليمات المهمة")
    lines.append("")
    lines.append("أنت مساعد قانوني يُطلب منه التحقق مما إذا كانت إجابة مقترحة مدعومة بالسجلات المسترجعة.")
    lines.append(f"الاستعلام: {query}")
    lines.append("")
    lines.append("## القواعد الصارمة")
    lines.append("")
    lines.append("1. تحقق من كل عبارة قانونية في الإجابة المقترحة مقابل السجلات المرفقة.")
    lines.append("2. استشهد بمعرف السجل (export_record_id) لكل عبارة مدعومة.")
    lines.append("3. علّم العبارات غير المدعومة بوضوح.")
    lines.append("4. لا تختلق استشهادات أو أرقام مواد غير موجودة.")
    lines.append("5. لا تقدم استشارة قانونية.")
    lines.append("6. المصدر العربي الرسمي هو الحاكم.")
    lines.append("7. لا تستخدم ذاكرة النموذج — اعتمد فقط على السجلات المرفقة.")
    lines.append("8. هذه المرحلة لتطبيق المراجعة القانونية من مالك المستودع؛ المراجعة القانونية الخارجية اختيارية للاعتماد المؤسسي أو الرسمي.")
    lines.append("")
    lines.append("## السجلات المسترجعة")
    lines.append("")
    for rec in records:
        rid = rec.get("export_record_id", "غير محدد")
        title = rec.get("title_ar") or "(بدون عنوان)"
        track = rec.get("source_track_id", "غير محدد")
        rtype = rec.get("record_type", "غير محدد")
        snippet = rec.get("snippet", "")
        lines.append(f"### السجل: {rid}")
        lines.append(f"- العنوان: {title}")
        lines.append(f"- المسار: {track}")
        lines.append(f"- النوع: {rtype}")
        if rec.get("article_number") is not None:
            lines.append(f"- رقم المادة: {rec['article_number']}")
        if rec.get("record_number") is not None:
            lines.append(f"- رقم السجل: {rec['record_number']}")
        lines.append(f"- مقتطف: {snippet}")
        if include_full_text and rec.get("text_ar"):
            lines.append(f"- النص الكامل: {rec['text_ar']}")
        lines.append("")
    lines.append("## ملاحظة حول الإجابة المقترحة")
    lines.append("")
    lines.append("وضع citation_check يتطلب إجابة مقترحة للتحقق منها.")
    lines.append("في هذه المرحلة، لا يتم تنفيذ التحقق — هذه حزمة تعليمات فقط.")
    lines.append("لتشغيل التحقق الفعلي، استخدم حزمة التعليمات هذه مع نموذج خارجي أو محلي لاحقًا.")
    lines.append("")
    return "\n".join(lines)


def build_prompt_text(mode: str, query: str, records: list, include_full_text: bool) -> str:
    """Build prompt text for the given mode."""
    if mode == "evidence_brief":
        return _build_evidence_brief_prompt(query, records, include_full_text)
    elif mode == "cautious_answer_draft":
        return _build_cautious_answer_draft_prompt(query, records, include_full_text)
    elif mode == "citation_check":
        return _build_citation_check_prompt(query, records, include_full_text)
    else:
        raise ValueError(f"Unknown mode: {mode}")


# ─── Main pack builder ───

def build_prompt_pack(
    query: str,
    limit: int = 5,
    track: Optional[str] = None,
    record_type: Optional[str] = None,
    mode: str = "evidence_brief",
    include_full_text: bool = False,
) -> dict:
    """Build a deterministic prompt pack from lexical search results.

    Returns a dict with all top-level fields, prompt_policy, retrieved_records,
    and prompt_text.
    """
    # Reuse existing context pack builder to get retrieval results
    context_pack = build_context_pack(
        query=query,
        limit=limit,
        track=track,
        record_type=record_type,
        include_full_text=include_full_text,
    )

    # Build records for prompt pack (same as context pack records)
    pack_records = context_pack["records"]

    # Build prompt text
    prompt_text = build_prompt_text(mode, query, pack_records, include_full_text)

    filters = {}
    if track:
        filters["track"] = track
    if record_type:
        filters["record_type"] = record_type

    pack = {
        "prompt_pack_version": PROMPT_PACK_VERSION,
        "query": query,
        "normalized_query": context_pack["normalized_query"],
        "mode": mode,
        "generated_at_date": date.today().isoformat(),
        "source_context_pack_tool": SOURCE_CONTEXT_PACK_TOOL,
        "source_search_tool": SOURCE_SEARCH_TOOL,
        "source_export_file": SOURCE_EXPORT_FILE,
        "source_export_record_count": context_pack["source_export_record_count"],
        "retrieval_method": RETRIEVAL_METHOD,
        "limit": limit,
        "filters": filters,
        "total_matches": context_pack["total_matches"],
        "returned": context_pack["returned"],
        "legal_boundaries": LEGAL_BOUNDARIES,
        "prompt_policy": PROMPT_POLICY,
        "retrieved_records": pack_records,
        "prompt_text": prompt_text,
    }

    return pack


# ─── Markdown formatting ───

def format_markdown(pack: dict, include_full_text: bool = False) -> str:
    """Format prompt pack as Markdown (Arabic-friendly layout)."""
    lines = []
    query = pack["query"]
    mode = pack["mode"]
    returned = pack["returned"]
    total = pack["total_matches"]

    # Heading
    lines.append(f"# حزمة تعليمات استرجاع — {query}")
    lines.append("")
    lines.append(f"**الوضع:** {mode} | **النتائج المعروضة:** {returned} / **إجمالي المطابقات:** {total}")
    lines.append("")
    lines.append("> **ملاحظة:** هذه حزمة تعليمات فقط — وليست إجابة قانونية.")
    lines.append("")

    # Boundary section
    lines.append("## الحدود القانونية")
    lines.append("")
    for b in pack["legal_boundaries"]:
        lines.append(f"- {b}")
    lines.append("")

    # Prompt policy section
    lines.append("## سياسة التعليمات")
    lines.append("")
    for key, val in pack["prompt_policy"].items():
        lines.append(f"- **{key}:** {val}")
    lines.append("")

    # Retrieved records section
    lines.append("## السجلات المسترجعة")
    lines.append("")
    for rec in pack["retrieved_records"]:
        rank = rec["rank"]
        title = rec.get("title_ar") or "(بدون عنوان)"
        lines.append(f"### {rank}. {title}")
        lines.append("")
        lines.append(f"- **الدرجة:** {rec['score']:.1f}")
        lines.append(f"- **معرف السجل:** {rec.get('export_record_id')}")
        lines.append(f"- **معيد المصدر:** {rec.get('source_record_id')}")
        lines.append(f"- **المسار:** {rec.get('source_track_id')}")
        lines.append(f"- **النوع:** {rec.get('record_type')}")
        lines.append(f"- **اللغة:** {rec.get('language')}")
        lines.append(f"- **الصفة الحاكمة:** {rec.get('governing_status')}")
        if rec.get("article_number") is not None:
            lines.append(f"- **رقم المادة:** {rec['article_number']}")
        if rec.get("record_number") is not None:
            lines.append(f"- **رقم السجل:** {rec['record_number']}")
        if rec.get("source_url"):
            lines.append(f"- **رابط المصدر:** {rec['source_url']}")
        if rec.get("source_authority"):
            lines.append(f"- **جهة المصدر:** {rec['source_authority']}")
        if rec.get("source_text_sha256"):
            lines.append(f"- **بصمة النص (SHA-256):** {rec['source_text_sha256']}")
        lines.append("")
        lines.append(f"**مقتطف:**")
        lines.append(f"> {rec.get('snippet', '')}")
        lines.append("")
        if include_full_text and rec.get("text_ar"):
            lines.append(f"**النص الكامل:**")
            lines.append("")
            lines.append(rec["text_ar"])
            lines.append("")

    # Prompt text section
    lines.append("## نص التعليمات")
    lines.append("")
    lines.append("```")
    lines.append(pack["prompt_text"])
    lines.append("```")
    lines.append("")
    lines.append("> **تذكير:** هذه حزمة تعليمات للاستخدام مع نموذج لغوي لاحقًا. لا يتم تنفيذ أي نموذج هنا.")
    lines.append("")

    return "\n".join(lines)


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(
        description="Build a retrieval prompt pack from local lexical search. "
                     "Deterministic, offline. Builds prompts only — does NOT call any model. "
                     "Not legal advice. Not an API.",
        prog="build_retrieval_prompt_pack",
    )
    parser.add_argument("query", help="Search query (Arabic)")
    parser.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--track", default=None,
                        help="Filter by track: companies_law, implementing_regulations_general, "
                             "implementing_regulations_listed_joint_stock")
    parser.add_argument("--record-type", default=None,
                        help="Filter by record type: article, form, appendix")
    parser.add_argument("--mode", choices=PROMPT_MODES, default="evidence_brief",
                        help="Prompt mode (default: evidence_brief)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--include-full-text", action="store_true",
                        help="Include full text_ar in each record")
    parser.add_argument("--draft-answer-file", default=None,
                        help="Path to draft answer file (for citation_check mode; not executed in this stage)")
    args = parser.parse_args()

    if not os.path.isfile(JSONL_PATH):
        print(f"ERROR: Export JSONL not found: {JSONL_PATH}", file=sys.stderr)
        sys.exit(1)

    # citation_check with --draft-answer-file: not executed in this stage
    if args.mode == "citation_check" and args.draft_answer_file:
        print(
            "NOTE: citation_check mode with --draft-answer-file is not executed in this stage. "
            "The prompt pack includes the citation_check prompt template only. "
            "No model is called, no answer is checked.",
            file=sys.stderr,
        )

    pack = build_prompt_pack(
        query=args.query,
        limit=args.limit,
        track=args.track,
        record_type=args.record_type,
        mode=args.mode,
        include_full_text=args.include_full_text,
    )

    if args.format == "json":
        output = json.dumps(pack, ensure_ascii=False, indent=2)
    else:
        output = format_markdown(pack, include_full_text=args.include_full_text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
            f.write("\n")
        print(f"Prompt pack written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()