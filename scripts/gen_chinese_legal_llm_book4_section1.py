#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Legal LLM-ready layer — PILOT: Book Four, Section 1
(Establishment and Capital / 设立与资本).

This STARTS the Chinese Legal LLM layer with the Book Four Section 1 pilot ONLY —
article groups [58], [59], [60], [66]. It is NOT full Chinese Legal LLM coverage.

SOURCE-FIELD SELECTION
----------------------
The source file `data/articles/book4_provisions_058_066.json` stores, per provision,
the existing internal Chinese legal content in the `chinese_translation` field (a title
also exists in `provision_title_zh`, but that is only a heading). The most authoritative
existing Chinese *legal content* field is therefore **`chinese_translation`**, and it is
the field selected here.

The core field `legal_rule_text_zh` is copied VERBATIM from that provision's
`chinese_translation`, keyed by the provision's `source_article_numbers`, so the layer
can never drift, contains NO new/machine translation, and contains NO model-generated
summary. There is NO `legal_rule_summary_zh`. Only the DERIVED structured metadata
(subject, basis type, actors, ... queries) is authored here, and it is kept conservative
and traceable to that provision's own Chinese text (empty arrays where the text does not
clearly support an item). `keywords_zh` reuses the provision's own approved
`llm.keywords_zh` (an existing approved Chinese field), not new terms.

Chinese trust posture: Chinese is an INTERNAL WORKING TRANSLATION / LLM-ready metadata
only; Arabic remains governing (governing_text_language = ar); official_text_check =
needs_check; manual_review_status = needs_manual_check; not an official translation; not
legal advice.

It does NOT create records for the uncovered Section-1 articles (61-65), for Book Four
Sections 2-5, or for Books 1-3. It does NOT modify the provision source / Arabic Legal
LLM / English layers, and makes no network calls.

Reads : data/articles/book4_provisions_058_066.json
Writes: data/chinese_legal_llm/book4_section1_zh_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/articles/book4_provisions_058_066.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "chinese_legal_llm", "book4_section1_zh_legal_llm.json")

# The selected authoritative existing Chinese source field (documented above).
SOURCE_FIELD = "chinese_translation"

COVERED = [58, 59, 60, 66]
UNCOVERED = [61, 62, 63, 64, 65]

_TRUST_NOTE = ("中文法律 LLM 元数据层，基于仓库中已有的内部中文条款文本（provision 的 "
               "chinese_translation 字段，逐字引用，非新译/机器翻译，非模型生成摘要）。中文仅为内部工作"
               "译文，具约束力的法定文本为阿拉伯文原文；official_text_check=needs_check。非官方翻译，"
               "非法律意见。")


def _load_provisions():
    """Map tuple(source_article_numbers) -> (chinese_translation, keywords_zh) from the
    Section 1 provisions. legal_rule_text_zh is sourced from chinese_translation, never
    authored, so the layer stays byte-identical to the provision's Chinese text."""
    with open(SRC, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    out = {}
    for p in doc["provisions"]:
        key = tuple(p["source_article_numbers"])
        out[key] = (p[SOURCE_FIELD], p.get("llm", {}).get("keywords_zh", []))
    return out


PROV = _load_provisions()


def rec(record_id, article_numbers, legal_subject_zh, legal_basis_type,
        actors_zh=None, rights_zh=None, obligations_zh=None, prohibitions_zh=None,
        conditions_zh=None, exceptions_zh=None, legal_effects_zh=None,
        liability_zh=None, monetary_thresholds=None, deadlines_zh=None,
        competent_authorities_zh=None, cross_references_zh=None,
        search_queries_zh=None, risk_flags=None):
    key = tuple(article_numbers)
    text, kw = PROV[key]  # VERBATIM from the provision's chinese_translation
    return {
        "book": 4,
        "record_type": "article_reference",
        "record_id": record_id,
        "article_numbers": article_numbers,
        "legal_subject_zh": legal_subject_zh,
        "legal_rule_text_zh": text,
        "legal_basis_type": legal_basis_type,
        "actors_zh": actors_zh or [],
        "rights_zh": rights_zh or [],
        "obligations_zh": obligations_zh or [],
        "prohibitions_zh": prohibitions_zh or [],
        "conditions_zh": conditions_zh or [],
        "exceptions_zh": exceptions_zh or [],
        "legal_effects_zh": legal_effects_zh or [],
        "liability_zh": liability_zh or [],
        "monetary_thresholds": monetary_thresholds or [],
        "deadlines_zh": deadlines_zh or [],
        "competent_authorities_zh": competent_authorities_zh or [],
        "cross_references_zh": cross_references_zh or [],
        "keywords_zh": list(kw),  # reuse the provision's own approved keywords_zh
        "search_queries_zh": search_queries_zh or [],
        "risk_flags": risk_flags or [],
        "source_trust": {
            "chinese_source_status": "internal_working_translation",
            "governing_text_language": "ar",
            "official_text_check": "needs_check",
            "manual_review_status": "needs_manual_check",
            "source_reference_file": SRC_REL,
            "notes": _TRUST_NOTE,
        },
    }


RECORDS = [
    rec(
        "zh-llm-book4-art058", [58],
        "股份公司的定义与责任",
        "definition",
        actors_zh=["股份公司", "股东"],
        legal_effects_zh=["公司独立对其债务与义务负责",
                          "股东的责任仅限于缴付其所认购股份的价值"],
        search_queries_zh=["什么是股份公司？", "股份公司股东承担什么责任？"]),

    rec(
        "zh-llm-book4-art059", [59],
        "股份公司的最低资本",
        "mandatory",
        obligations_zh=["已发行资本不得低于五十万（500,000）里亚尔",
                        "设立时实缴部分不得低于已发行资本的四分之一"],
        monetary_thresholds=[
            {"amount": 500000, "currency": "SAR",
             "description_zh": "已发行资本不得低于五十万（500,000）里亚尔"},
            {"amount": 0.25, "currency": "ratio",
             "description_zh": "设立时实缴部分不得低于已发行资本的四分之一"},
        ],
        search_queries_zh=["股份公司的最低已发行资本是多少？",
                           "设立时实缴资本比例是多少？"]),

    rec(
        "zh-llm-book4-art060", [60],
        "已发行资本与授权资本",
        "procedural",
        actors_zh=["董事会", "公司"],
        conditions_zh=["增加已发行资本以已发行资本已全额缴清为前提"],
        legal_effects_zh=["已发行资本代表已认购的股份",
                          "公司章程可规定授权资本",
                          "董事会可在授权资本限度内增加已发行资本"],
        search_queries_zh=["已发行资本与授权资本有何区别？",
                           "董事会可以在什么条件下增加已发行资本？"]),

    rec(
        "zh-llm-book4-art066", [66],
        "实物出资的评估",
        "procedural",
        actors_zh=["认证评估师", "实物出资人"],
        obligations_zh=["实物出资须由认证评估师评估其公允价值"],
        prohibitions_zh=["实物出资人不得参与对其评估决议的表决"],
        conditions_zh=["若决定下调其实物出资的对价，须经该出资人同意"],
        search_queries_zh=["实物出资如何评估？",
                           "实物出资人可以参与评估决议的表决吗？"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == [[n] for n in COVERED], got
    covered = {n for g in got for n in g}
    assert covered == set(COVERED), covered
    assert not (covered & set(UNCOVERED)), covered
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        key = tuple(r["article_numbers"])
        assert r["legal_rule_text_zh"] == PROV[key][0], r["record_id"]
        assert "legal_rule_summary_zh" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-chinese-legal-llm",
        "layer_status": "pilot",
        "scope": "book4_section1_establishment_and_capital",
        "book": 4,
        "section_key": "formation_and_capital",
        "section_title_zh": "设立与资本",
        "article_range": "58-66",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": UNCOVERED,
        "source_field": SOURCE_FIELD,
        "summary_source": ("legal_rule_text_zh is copied verbatim from the provision's "
                           + SOURCE_FIELD + " field in " + SRC_REL
                           + " (no new/machine translation, no model-generated summary)."),
        "chinese_source_status": "internal_working_translation",
        "governing_text_language": "ar",
        "official_text_check": "needs_check",
        "disclaimer_zh": ("中文法律 LLM 元数据层，基于仓库中已有的内部中文条款文本；具约束力的法定文本为"
                          "阿拉伯文原文。此为试点（仅第四编第一节）——非完整中文法律 LLM 覆盖，非官方翻译，"
                          "非法律意见。"),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d Chinese legal LLM records (articles %s; source field '%s')" % (
        OUT, len(RECORDS), COVERED, SOURCE_FIELD))


if __name__ == "__main__":
    main()
