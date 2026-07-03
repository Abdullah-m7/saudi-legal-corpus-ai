#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Legal LLM-ready layer — Book Four, Section 3
(General Assemblies / الجمعية العامة / 股东大会).

Adds Chinese Legal LLM-ready records for the Book Four Section 3 provision groups ONLY —
[85, 87], [92, 93], [99], [101], [102] (5 article_reference records). The source groups
Articles 85 & 87 into one provision and 92 & 93 into one provision, and those groupings
are preserved exactly. NOT full Chinese Legal LLM coverage.

SOURCE-FIELD SELECTION (same as the Section 1 pilot / Section 2)
---------------------------------------------------------------
The source file `data/articles/book4_provisions_084_102.json` stores the existing internal
Chinese legal content per provision in the **`chinese_translation`** field (a title also
exists in `provision_title_zh`, but that is only a heading). `chinese_translation` is the
most authoritative existing Chinese *legal content* field and is the one selected here.

The core field `legal_rule_text_zh` is copied VERBATIM from that provision's
`chinese_translation`, keyed by the provision's `source_article_numbers`, so the layer can
never drift, contains NO new/machine translation, and contains NO model-generated summary.
There is NO `legal_rule_summary_zh`. Only the DERIVED structured metadata is authored here,
kept conservative and traceable to that provision's own Chinese text (empty arrays where
unsupported). `keywords_zh` reuses the provision's own approved `llm.keywords_zh`.

Chinese trust posture: Chinese is an INTERNAL WORKING TRANSLATION / LLM-ready metadata
only; Arabic remains governing (governing_text_language = ar); official_text_check =
needs_check; manual_review_status = needs_manual_check; not an official translation; not
legal advice.

It does NOT create records for the uncovered / owner-reconciled Section-3 articles (84, 86,
88, 89, 90, 91, 94, 95, 96, 97, 98, 100 — Articles 84, 89 and 100 specifically remain
excluded), for other Book Four sections, or for Books 1-3. It does NOT modify the provision
source / Arabic Legal LLM / English layers, and makes no network calls.

Reads : data/articles/book4_provisions_084_102.json
Writes: data/chinese_legal_llm/book4_section3_zh_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/articles/book4_provisions_084_102.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "chinese_legal_llm", "book4_section3_zh_legal_llm.json")

SOURCE_FIELD = "chinese_translation"
GROUPS = [[85, 87], [92, 93], [99], [101], [102]]
UNCOVERED = [84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100]

_TRUST_NOTE = ("中文法律 LLM 元数据层，基于仓库中已有的内部中文条款文本（provision 的 "
               "chinese_translation 字段，逐字引用，非新译/机器翻译，非模型生成摘要）。中文仅为内部工作"
               "译文，具约束力的法定文本为阿拉伯文原文；official_text_check=needs_check。非官方翻译，"
               "非法律意见。")


def _load_provisions():
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
        "zh-llm-book4-prov010", [85, 87],
        "普通大会与非常大会的职权",
        "mixed",
        actors_zh=["普通大会", "非常大会", "董事", "审计师"],
        rights_zh=["选举与解聘董事", "任命审计师", "审议财务报表与报告",
                   "分配利润", "提取储备"],
        legal_effects_zh=["修改公司章程", "决定公司存续或解散", "批准公司回购自身股份"],
        prohibitions_zh=["不得剥夺股东的基本权利"],
        conditions_zh=["增加财务负担须经全体股东同意"],
        search_queries_zh=["普通大会有哪些职权？", "非常大会可以修改公司章程吗？"]),

    rec(
        "zh-llm-book4-prov011", [92, 93],
        "普通大会与非常大会的法定人数与表决多数",
        "procedural",
        actors_zh=["普通大会", "非常大会"],
        conditions_zh=["首次会议须代表四分之一股份",
                       "第二次会议无论出席多少均有效",
                       "决议以出席所代表表决权的多数通过",
                       "决议以所代表表决权的三分之二通过"],
        legal_effects_zh=["若涉及增减资本、延长公司期限、提前解散、合并或分立，则须四分之三多数"],
        monetary_thresholds=[
            {"amount": 0.75, "currency": "ratio",
             "description_zh": "须四分之三多数"},
        ],
        search_queries_zh=["普通大会的法定人数是多少？",
                           "非常大会的表决多数要求是多少？"]),

    rec(
        "zh-llm-book4-prov012", [99],
        "撤销股东大会决议",
        "mixed",
        actors_zh=["股东", "原告", "善意第三人"],
        rights_zh=["可请求撤销违反本法或公司章程的决议"],
        conditions_zh=["在会上提出异议、或有正当理由缺席的股东",
                       "原告须在诉讼全程保持股东身份"],
        deadlines_zh=["自决议作出之日起满九十（90）日后不予受理"],
        legal_effects_zh=["不影响善意第三人的权利"],
        search_queries_zh=["哪些股东可以请求撤销股东大会决议？",
                           "撤销决议的期限是多久？"]),

    rec(
        "zh-llm-book4-prov013", [101],
        "以传阅方式作出决议",
        "procedural",
        actors_zh=["非上市公司", "普通大会", "非常大会"],
        legal_effects_zh=["普通大会事项可以传阅方式以表决权多数通过",
                          "非常大会事项须以至少百分之七十五（75%）的表决权通过"],
        conditions_zh=["公司章程要求更高比例的，从其规定"],
        monetary_thresholds=[
            {"amount": 0.75, "currency": "ratio",
             "description_zh": "非常大会事项须以至少百分之七十五（75%）的表决权通过"},
        ],
        search_queries_zh=["非上市公司可以传阅方式作出决议吗？",
                           "传阅决议的表决比例是多少？"]),

    rec(
        "zh-llm-book4-prov014", [102],
        "申请对公司进行检查",
        "mixed",
        actors_zh=["股东", "董事会成员", "审计师", "主管司法机关", "申请人"],
        rights_zh=["可向主管司法机关申请对公司进行检查"],
        conditions_zh=["持有公司资本百分之五（5%）的股东",
                       "在有理由怀疑董事会成员或审计师行为的情形下"],
        legal_effects_zh=["主管司法机关可判令由申请人承担检查费用"],
        competent_authorities_zh=["主管司法机关"],
        monetary_thresholds=[
            {"amount": 0.05, "currency": "ratio",
             "description_zh": "持有公司资本百分之五（5%）的股东"},
        ],
        search_queries_zh=["哪些股东可以申请对公司进行检查？",
                           "申请公司检查的费用由谁承担？"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == {85, 87, 92, 93, 99, 101, 102}, covered
    assert not (covered & set(UNCOVERED)), covered
    for excluded in (84, 89, 100):
        assert excluded not in covered, excluded
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        key = tuple(r["article_numbers"])
        assert key in PROV, "missing source provision group %s" % (key,)
        assert r["legal_rule_text_zh"] == PROV[key][0], r["record_id"]
        assert "legal_rule_summary_zh" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-chinese-legal-llm",
        "layer_status": "pilot_extension",
        "scope": "book4_section3_general_assemblies",
        "book": 4,
        "section_key": "general_assemblies",
        "section_title_zh": "股东大会",
        "article_range": "84-102",
        "explicit_articles": sorted(covered),
        "provision_groups": GROUPS,
        "uncovered_articles_excluded": UNCOVERED,
        "source_field": SOURCE_FIELD,
        "summary_source": ("legal_rule_text_zh is copied verbatim from the provision's "
                           + SOURCE_FIELD + " field in " + SRC_REL
                           + " (no new/machine translation, no model-generated summary)."),
        "chinese_source_status": "internal_working_translation",
        "governing_text_language": "ar",
        "official_text_check": "needs_check",
        "disclaimer_zh": ("中文法律 LLM 元数据层，基于仓库中已有的内部中文条款文本；具约束力的法定文本为"
                          "阿拉伯文原文。仅第四编第三节（股东大会）——非完整中文法律 LLM 覆盖，非官方翻译，"
                          "非法律意见。"),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d Chinese legal LLM records (groups %s; source field '%s')" % (
        OUT, len(RECORDS), GROUPS, SOURCE_FIELD))


if __name__ == "__main__":
    main()
