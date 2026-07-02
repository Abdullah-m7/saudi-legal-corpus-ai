"""Legal-translation terminology rules (brief section I checklist 5-12)."""


def test_art8_no_good_faith_third_party(by_number):
    zh = by_number[8]["chinese_translation"]
    assert "善意第三人" not in zh
    assert "第三人" in zh


def test_art13_both_company_forms(by_number):
    zh = by_number[13]["chinese_translation"]
    assert "股份公司" in zh
    assert "简易股份公司" in zh


def test_art27_public_competition(by_number):
    zh = by_number[27]["chinese_translation"]
    assert "公开竞争程序" in zh


def test_art29_bankruptcy(by_number):
    assert "破产法" in by_number[29]["chinese_translation"]


def test_art31_decision_rule_and_bjr(by_number):
    zh = by_number[31]["chinese_translation"]
    assert "决策评估规则" in zh
    assert "BJR" in zh


def test_art34_redemption_and_preemption(by_number):
    zh = by_number[34]["chinese_translation"]
    assert "赎回权" in zh
    assert "优先购买权" in zh


def test_art5_name_rules(by_number):
    zh = by_number[5]["chinese_translation"]
    assert "商号法" in zh
    assert "继承人" in zh


def test_art6_actual_founder(by_number):
    zh = by_number[6]["chinese_translation"]
    assert "实际创始人" in zh
    assert "60" in zh and "30" in zh


def test_art9_formation_liability(by_number):
    zh = by_number[9]["chinese_translation"]
    assert "设立期间" in zh
    assert "连带责任" in zh


def test_disclaimer_non_official(work):
    ts = work["translation_status"]
    assert ts["is_official"] is False
    assert ts["is_legal_advice"] is False
    assert "并非官方译本" in ts["disclaimer_zh"]


def test_scope_is_1_34(work):
    assert work["articles_covered"] == "1-34"
    assert "第三十四条" in work["scope_zh"]
    assert ("1–34" in work["scope_ar"]) or ("1-34" in work["scope_ar"])


def test_glossary_uses_public_competition(glossary):
    terms = {t["ar"]: t["zh"] for t in glossary["terms"]}
    assert terms.get("المنافسة العامة") == "公开竞争程序"
    # redemption vs pre-emption kept distinct
    assert terms.get("حق الاسترداد") == "赎回权"
    assert terms.get("حق الأولوية في الشراء") == "优先购买权"
