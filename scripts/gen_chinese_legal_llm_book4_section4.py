#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Legal LLM-ready layer — Book Four, Section 4
(Shares, Debt Instruments and Sukuk / 股份、债务工具与融资凭证).

Adds Chinese Legal LLM-ready records for the Book Four Section 4 provision groups ONLY —
[108], [113], [115], [117] (4 article_reference records). NOT full Chinese Legal LLM
coverage.

SOURCE-FIELD SELECTION (same as the Section 1 pilot / Sections 2-3)
-------------------------------------------------------------------
The source file `data/articles/book4_provisions_103_120.json` stores the existing internal
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

It does NOT create records for the uncovered / owner-reconciled Section-4 articles (103,
104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120 — Article 110 specifically
remains excluded), for Book Four Section 5, or for Books 1-3. It does NOT modify the
provision source / Arabic Legal LLM / English layers, and makes no network calls.

Reads : data/articles/book4_provisions_103_120.json
Writes: data/chinese_legal_llm/book4_section4_zh_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/articles/book4_provisions_103_120.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "chinese_legal_llm", "book4_section4_zh_legal_llm.json")

SOURCE_FIELD = "chinese_translation"
GROUPS = [[108], [113], [115], [117]]
UNCOVERED = [103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120]

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
        "zh-llm-book4-prov015", [108],
        "股份的种类与类别",
        "mixed",
        actors_zh=["非常大会", "专门大会"],
        legal_effects_zh=["股份分为三大种类：普通股、优先股、可赎回股",
                          "同一种类或类别的股份，其权利与义务相等"],
        conditions_zh=["变更某一类别的权利，除经非常大会（EGM）外，还须经该类别持有人组成的专门大会批准"],
        search_queries_zh=["股份分为哪几种类？", "变更某一类别股份的权利需要哪些批准？"]),

    rec(
        "zh-llm-book4-prov016", [113],
        "强制出售：拖售权与随售权",
        "mixed",
        actors_zh=["多数股东", "少数股东", "善意买方"],
        rights_zh=["多数股东有权强制少数股东接受善意买方按同一价格与条件收购全部股份",
                   "少数股东有权在多数股东出售时，要求其保证按同一条件一并售出少数股东的股份"],
        conditions_zh=["在不违反《资本市场法》的前提下",
                       "经代表至少百分之九十（90%）表决权的股东同意"],
        monetary_thresholds=[
            {"amount": 0.9, "currency": "ratio",
             "description_zh": "经代表至少百分之九十（90%）表决权的股东同意"},
        ],
        search_queries_zh=["什么是拖售权与随售权？",
                           "多数股东强制出售需要多少表决权同意？"]),

    rec(
        "zh-llm-book4-prov017", [115],
        "违约未缴款",
        "mixed",
        actors_zh=["股东", "董事会", "公司"],
        conditions_zh=["股东逾期未缴清其股款的", "董事会经通知后"],
        legal_effects_zh=["可在公开拍卖或资本市场出售该违约股份",
                          "从出售所得中受偿并将余额返还股东",
                          "在出售或缴清之前，暂停该股份相关的权利（如分红权与表决权）"],
        search_queries_zh=["股东未按期缴清股款会怎样？",
                           "违约股份可以被拍卖吗？"]),

    rec(
        "zh-llm-book4-prov018", [117],
        "债务工具与融资凭证（Sukuk）的发行",
        "procedural",
        actors_zh=["股份公司", "非常大会"],
        legal_effects_zh=["股份公司可依《资本市场法》的规定，发行可交易的债务工具或融资凭证"],
        conditions_zh=["发行可转换为股份的债务工具或凭证的，须经非常大会（EGM）决议",
                       "并在决议中列明可据以发行的股份上限"],
        search_queries_zh=["股份公司如何发行债务工具或融资凭证？",
                           "发行可转换债务工具需要哪些批准？"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == {108, 113, 115, 117}, covered
    assert not (covered & set(UNCOVERED)), covered
    assert 110 not in covered, "Article 110 must remain excluded"
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        key = tuple(r["article_numbers"])
        assert key in PROV, "missing source provision group %s" % (key,)
        assert r["legal_rule_text_zh"] == PROV[key][0], r["record_id"]
        assert "legal_rule_summary_zh" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-chinese-legal-llm",
        "layer_status": "pilot_extension",
        "scope": "book4_section4_shares_debt_instruments_and_sukuk",
        "book": 4,
        "section_key": "shares_debt_instruments_and_sukuk",
        "section_title_zh": "股份、债务工具与融资凭证",
        "article_range": "103-120",
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
                          "阿拉伯文原文。仅第四编第四节（股份、债务工具与融资凭证）——非完整中文法律 LLM 覆盖，"
                          "非官方翻译，非法律意见。"),
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
