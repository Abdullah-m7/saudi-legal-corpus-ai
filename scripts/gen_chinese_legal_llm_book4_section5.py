#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Legal LLM-ready layer — repo book4 Section 5
(Finance, Profits, and Capital Changes / المالية والأرباح وتغيير رأس المال /
财务、利润与资本变更).

"book4" is an internal repository label for the modeled Joint-Stock Company chapter/part
scope (repo book4 convention) — it is NOT a claim that Book Four is the whole Saudi
Companies Law or a separate legal book.

Adds Chinese Legal LLM-ready records for the repo book4 Section 5 provision groups ONLY —
[123, 124], [126, 127], [128, 129, 130], [132], [133] (5 article_reference records). The
source groups those articles into single provisions, and those groupings are preserved
exactly. Completing this section makes the Chinese Legal LLM layer cover repo book4
Sections 1-5 (still NOT full Chinese Legal LLM coverage — no Books 1-3).

SOURCE-FIELD SELECTION (same as the Section 1 pilot / Sections 2-4)
------------------------------------------------------------------
The source file `data/articles/book4_provisions_121_137.json` stores the existing internal
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

It does NOT create records for the uncovered Section-5 articles (121, 122, 125, 131, 134,
135, 136, 137 — Articles 134 and 135 specifically remain excluded / cross-reference-only),
for other books, or for Books 1-3. It does NOT modify the provision source / Arabic Legal
LLM / English layers, and makes no network calls.

Reads : data/articles/book4_provisions_121_137.json
Writes: data/chinese_legal_llm/book4_section5_zh_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/articles/book4_provisions_121_137.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "chinese_legal_llm", "book4_section5_zh_legal_llm.json")

SOURCE_FIELD = "chinese_translation"
GROUPS = [[123, 124], [126, 127], [128, 129, 130], [132], [133]]
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]

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
        "zh-llm-book4-prov019", [123, 124],
        "储备金的提取与动用",
        "mixed",
        actors_zh=["非常大会", "普通大会", "董事会"],
        conditions_zh=["公司章程可提取净利润的一定比例，作为用于特定用途的专项储备",
                       "专项储备的使用须经非常大会（EGM）决议"],
        legal_effects_zh=["非专项储备则由普通大会（OGM）依董事会的提议动用"],
        search_queries_zh=["专项储备如何动用？", "非专项储备由谁决定动用？"]),

    rec(
        "zh-llm-book4-prov020", [126, 127],
        "增资的条件与方式",
        "mixed",
        actors_zh=["非常大会"],
        conditions_zh=["增资须经非常大会（EGM）决议", "且已发行资本须已全额缴清"],
        legal_effects_zh=["方式包括：发行新股（现金或实物）、以债权抵充（债转股）、资本化储备（红股），"
                          "或对应债务工具/融资凭证发行"],
        search_queries_zh=["公司增资需要满足哪些条件？", "增资有哪些方式？"]),

    rec(
        "zh-llm-book4-prov021", [128, 129, 130],
        "优先认购权及其转让与取消",
        "mixed",
        actors_zh=["股东", "非常大会", "非股东"],
        rights_zh=["对新发行的现金股份享有优先认购权", "并可出售或转让该权利"],
        conditions_zh=["若公司章程有规定，非常大会（EGM）可为公司利益取消优先认购权，或将其授予非股东"],
        search_queries_zh=["股东对新发行股份有优先认购权吗？",
                           "优先认购权可以被取消或转让吗？"]),

    rec(
        "zh-llm-book4-prov022", [132],
        "重大亏损",
        "mandatory",
        actors_zh=["董事会", "非常大会"],
        conditions_zh=["当亏损达到已发行资本的二分之一时"],
        obligations_zh=["董事会须自知悉之日起六十（60）日内予以披露",
                        "并在一百八十（180）日内召集非常大会（EGM）"],
        deadlines_zh=["自知悉之日起六十（60）日内予以披露",
                      "在一百八十（180）日内召集非常大会（EGM）"],
        legal_effects_zh=["审议公司存续、亏损处置或解散"],
        search_queries_zh=["公司亏损达到资本一半时董事会须做什么？",
                           "重大亏损的披露与召集期限是多久？"]),

    rec(
        "zh-llm-book4-prov023", [133],
        "减资的方式",
        "procedural",
        actors_zh=["公司", "股东", "债权人"],
        legal_effects_zh=["减资的方式包括：注销股份",
                          "下调面值（注销相当于亏损的部分、向股东返还一部分，或豁免未缴部分）",
                          "或由公司回购并注销股份"],
        cross_references_zh=["债权人保护与异议的细则见第134–135条（在本源文件中未涵盖）"],
        search_queries_zh=["减资有哪些方式？", "公司如何通过回购股份减资？"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == GROUPS, got
    covered = {n for g in got for n in g}
    assert covered == {123, 124, 126, 127, 128, 129, 130, 132, 133}, covered
    assert not (covered & set(UNCOVERED)), covered
    for excluded in (134, 135):
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
        "scope": "book4_section5_finance_profits_and_capital_changes",
        "book": 4,
        "section_key": "finance_profits_and_capital_changes",
        "section_title_zh": "财务、利润与资本变更",
        "article_range": "121-137",
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
                          "阿拉伯文原文。仅仓库 book4 第五节（财务、利润与资本变更；book4 为仓库内部约定标签，"
                          "非完整《公司法》结构主张）——非完整中文法律 LLM 覆盖，非官方翻译，非法律意见。"),
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
