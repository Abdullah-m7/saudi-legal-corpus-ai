#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Legal LLM-ready layer — Book Four, Section 2
(Board of Directors and Governance / 董事会与治理).

Adds Chinese Legal LLM-ready records for the Book Four Section 2 provision groups ONLY —
[67, 68], [71], [72], [75], [77] (5 article_reference records). The source groups Articles
67 & 68 into one provision, and that grouping is preserved exactly. NOT full Chinese Legal
LLM coverage.

SOURCE-FIELD SELECTION (same as the Section 1 pilot)
----------------------------------------------------
The source file `data/articles/book4_provisions_067_083.json` stores the existing internal
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

It does NOT create records for the uncovered Section-2 articles (69, 70, 73, 74, 76,
78-83), for other Book Four sections, or for Books 1-3. It does NOT modify the provision
source / Arabic Legal LLM / English layers, and makes no network calls.

Reads : data/articles/book4_provisions_067_083.json
Writes: data/chinese_legal_llm/book4_section2_zh_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/articles/book4_provisions_067_083.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "chinese_legal_llm", "book4_section2_zh_legal_llm.json")

SOURCE_FIELD = "chinese_translation"
GROUPS = [[67, 68], [71], [72], [75], [77]]
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]

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
        "keywords_zh": list(kw),
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
        "zh-llm-book4-prov005", [67, 68],
        "董事会的组成、任期与解聘",
        "mixed",
        actors_zh=["董事会", "董事", "普通股东大会"],
        rights_zh=["普通股东大会有权解聘董事，即使公司章程另有约定",
                   "董事可连选连任"],
        conditions_zh=["董事会至少由三（3）名自然人成员组成",
                       "董事任期不超过四（4）年"],
        search_queries_zh=["股份公司董事会由多少人组成？",
                           "董事的任期有多长？普通股东大会能解聘董事吗？"]),

    rec(
        "zh-llm-book4-prov006", [71],
        "董事利益披露、表决回避与责任",
        "mixed",
        actors_zh=["董事", "董事会", "股东大会"],
        obligations_zh=["董事一旦知悉其直接或间接利益，须即时披露并记入会议纪要"],
        prohibitions_zh=["不得在董事会或股东大会就该事项表决"],
        liability_zh=["在会议纪要中明确记录反对的董事免除责任",
                      "缺席的董事仅在证明其不知情、或知情后无法提出反对时方免除责任"],
        search_queries_zh=["董事有利益冲突时须如何处理？",
                           "有利益的董事可以就该事项表决吗？"]),

    rec(
        "zh-llm-book4-prov007", [72],
        "禁止向董事提供贷款或担保",
        "prohibition",
        actors_zh=["公司", "董事", "亲属", "银行及融资公司"],
        prohibitions_zh=["公司不得向其任何董事提供贷款",
                         "亦不得为该董事向第三方的借款作保或提供担保",
                         "该禁止延伸至其亲属"],
        legal_effects_zh=["违反该禁止的合同无效"],
        exceptions_zh=["银行及融资公司按其对公众适用的一般条件办理的交易",
                       "经批准的员工激励计划"],
        search_queries_zh=["公司可以向董事提供贷款吗？",
                           "禁止向董事提供贷款有哪些例外？"]),

    rec(
        "zh-llm-book4-prov008", [75],
        "重大资产出售与股东大会批准",
        "mandatory",
        actors_zh=["股东大会"],
        obligations_zh=["出售价值超过公司总资产百分之五十（50%）的资产，须经股东大会批准"],
        conditions_zh=["该比例自此前十二（12）个月内的首笔交易起累计计算"],
        monetary_thresholds=[
            {"amount": 0.5, "currency": "ratio",
             "description_zh": "出售价值超过公司总资产百分之五十（50%）的资产"},
        ],
        deadlines_zh=["该比例自此前十二（12）个月内的首笔交易起累计计算"],
        search_queries_zh=["出售公司资产何时须经股东大会批准？",
                           "50% 的资产出售比例如何计算？"]),

    rec(
        "zh-llm-book4-prov009", [77],
        "董事会对第三人的权限",
        "mixed",
        actors_zh=["董事会", "股东大会", "公司", "交易相对人"],
        rights_zh=["除专属于股东大会的事项外，董事会享有为实现公司宗旨所需的最广泛权限"],
        legal_effects_zh=["公司受董事会以公司名义所为行为的约束，即使该行为超出其权限"],
        exceptions_zh=["专属于股东大会的事项除外",
                       "交易相对人为恶意、或明知该行为越权的除外"],
        search_queries_zh=["董事会有哪些权限？",
                           "公司是否受董事会越权行为的约束？"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == {67, 68, 71, 72, 75, 77}, covered
    assert not (covered & set(UNCOVERED)), covered
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        key = tuple(r["article_numbers"])
        assert key in PROV, "missing source provision group %s" % (key,)
        assert r["legal_rule_text_zh"] == PROV[key][0], r["record_id"]
        assert "legal_rule_summary_zh" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-chinese-legal-llm",
        "layer_status": "pilot_extension",
        "scope": "book4_section2_board_and_governance",
        "book": 4,
        "section_key": "board_and_governance",
        "section_title_zh": "董事会与治理",
        "article_range": "67-83",
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
                          "阿拉伯文原文。仅第四编第二节（董事会与治理）——非完整中文法律 LLM 覆盖，非官方翻译，"
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
