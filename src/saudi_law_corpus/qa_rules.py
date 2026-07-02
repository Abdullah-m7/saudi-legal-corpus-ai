"""Legal-translation QA rules for the Book One corpus.

Each rule is a pure function over the loaded corpus data returning a list of
human-readable problem strings (empty == pass). ``run_all`` aggregates them.
Standard-library only, so it can run in ``validate_corpus.py`` and in tests.
"""

from __future__ import annotations

from typing import Any, Dict, List

EXPECTED_RANGE = list(range(1, 35))
EXPANDED_ARTICLES = {5, 6, 8, 9, 12, 13, 14, 17, 19, 20, 29}


def _by_number(articles: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    return {a["article_number"]: a for a in articles}


def rule_full_coverage(articles: List[Dict[str, Any]]) -> List[str]:
    nums = sorted(a["article_number"] for a in articles)
    problems = []
    if nums != EXPECTED_RANGE:
        missing = sorted(set(EXPECTED_RANGE) - set(nums))
        extra = sorted(set(nums) - set(EXPECTED_RANGE))
        if missing:
            problems.append(f"Missing articles: {missing}")
        if extra:
            problems.append(f"Unexpected articles: {extra}")
    return problems


def rule_no_duplicates(articles: List[Dict[str, Any]]) -> List[str]:
    nums = [a["article_number"] for a in articles]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    return [f"Duplicate article numbers: {dupes}"] if dupes else []


def rule_bilingual_present(articles: List[Dict[str, Any]]) -> List[str]:
    problems = []
    for a in articles:
        n = a["article_number"]
        if not a.get("arabic_reference_summary", "").strip():
            problems.append(f"Article {n}: missing Arabic text")
        if not a.get("chinese_translation", "").strip():
            problems.append(f"Article {n}: missing Chinese text")
        if not a.get("article_title_ar", "").strip():
            problems.append(f"Article {n}: missing Arabic title")
        if not a.get("article_title_zh", "").strip():
            problems.append(f"Article {n}: missing Chinese title")
    return problems


def rule_expanded_marked(articles: List[Dict[str, Any]]) -> List[str]:
    by = _by_number(articles)
    problems = []
    for n in sorted(EXPANDED_ARTICLES):
        a = by.get(n)
        if a is None:
            problems.append(f"Article {n}: expected but missing")
            continue
        if a.get("coverage_status") != "expanded_after_review":
            problems.append(
                f"Article {n}: coverage_status is "
                f"'{a.get('coverage_status')}', expected 'expanded_after_review'"
            )
    return problems


def rule_art8_no_good_faith_third_party(articles: List[Dict[str, Any]]) -> List[str]:
    a = _by_number(articles).get(8)
    if a and "善意第三人" in a.get("chinese_translation", ""):
        return ["Article 8: must not contain 善意第三人 (use 第三人 only)"]
    return []


def rule_art13_both_forms(articles: List[Dict[str, Any]]) -> List[str]:
    a = _by_number(articles).get(13)
    if not a:
        return ["Article 13 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    if "股份公司" not in zh:
        problems.append("Article 13: must contain 股份公司")
    if "简易股份公司" not in zh:
        problems.append("Article 13: must contain 简易股份公司")
    return problems


def rule_art27_public_competition(articles: List[Dict[str, Any]]) -> List[str]:
    a = _by_number(articles).get(27)
    if not a:
        return ["Article 27 missing"]
    zh = a.get("chinese_translation", "")
    if "公开竞争程序" in zh or "公开招标或其他公开竞争程序" in zh:
        return []
    return ["Article 27: must contain 公开竞争程序 (or 公开招标或其他公开竞争程序)"]


def rule_art29_bankruptcy(articles: List[Dict[str, Any]]) -> List[str]:
    a = _by_number(articles).get(29)
    if not a:
        return ["Article 29 missing"]
    if "破产法" not in a.get("chinese_translation", ""):
        return ["Article 29: must contain 破产法"]
    return []


def rule_art31_decision_rule_and_bjr(articles: List[Dict[str, Any]]) -> List[str]:
    a = _by_number(articles).get(31)
    if not a:
        return ["Article 31 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    if "决策评估规则" not in zh:
        problems.append("Article 31: must contain 决策评估规则")
    if "BJR" not in zh:
        problems.append("Article 31: must contain BJR")
    return problems


def rule_art34_redemption_and_preemption(articles: List[Dict[str, Any]]) -> List[str]:
    a = _by_number(articles).get(34)
    if not a:
        return ["Article 34 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    if "赎回权" not in zh:
        problems.append("Article 34: must contain 赎回权")
    if "优先购买权" not in zh:
        problems.append("Article 34: must contain 优先购买权")
    return problems


def rule_disclaimer_non_official(work: Dict[str, Any]) -> List[str]:
    ts = work.get("translation_status", {})
    problems = []
    if ts.get("is_official") is not False:
        problems.append("work.json: translation must be marked non-official")
    if ts.get("is_legal_advice") is not False:
        problems.append("work.json: translation must be marked not legal advice")
    disc_zh = ts.get("disclaimer_zh", "")
    if "并非官方译本" not in disc_zh:
        problems.append("work.json: Chinese disclaimer must state non-official (并非官方译本)")
    if "不构成法律意见" not in ts.get("note_en", "") + disc_zh + ts.get("binding_text_note_en", "") \
            and ts.get("is_legal_advice") is not False:
        pass  # covered by is_legal_advice check
    return problems


def rule_scope_1_34(work: Dict[str, Any]) -> List[str]:
    problems = []
    if work.get("articles_covered") != "1-34":
        problems.append("work.json: articles_covered must be '1-34'")
    scope_zh = work.get("scope_zh", "")
    scope_ar = work.get("scope_ar", "")
    if "第三十四条" not in scope_zh:
        problems.append("work.json: scope_zh must state through 第三十四条")
    if "1–34" not in scope_ar and "1-34" not in scope_ar:
        problems.append("work.json: scope_ar must state المواد 1–34")
    return problems


def run_all(articles: List[Dict[str, Any]], work: Dict[str, Any]) -> Dict[str, List[str]]:
    """Run every rule; return {rule_name: [problems]} for failing rules only kept."""
    results = {
        "1_full_coverage_1_34": rule_full_coverage(articles),
        "2_no_duplicate_numbers": rule_no_duplicates(articles),
        "3_bilingual_present": rule_bilingual_present(articles),
        "4_expanded_after_review_marked": rule_expanded_marked(articles),
        "5_art8_no_good_faith_third_party": rule_art8_no_good_faith_third_party(articles),
        "6_art13_both_company_forms": rule_art13_both_forms(articles),
        "7_art27_public_competition": rule_art27_public_competition(articles),
        "8_art29_bankruptcy": rule_art29_bankruptcy(articles),
        "9_art31_decision_rule_and_bjr": rule_art31_decision_rule_and_bjr(articles),
        "10_art34_redemption_and_preemption": rule_art34_redemption_and_preemption(articles),
        "11_disclaimer_non_official": rule_disclaimer_non_official(work),
        "12_scope_1_34": rule_scope_1_34(work),
    }
    return results
