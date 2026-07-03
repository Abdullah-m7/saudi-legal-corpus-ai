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


# ==========================================================================
# Book Two — شركة التضامن / 无限公司（普通合伙性质）— Articles 35–50
# ==========================================================================
BOOK2_RANGE = list(range(35, 51))
_INTERNAL_MODE = "internally_reviewed_summary"


def rule_range(articles: List[Dict[str, Any]], expected: List[int]) -> List[str]:
    nums = sorted(a["article_number"] for a in articles)
    problems = []
    if nums != expected:
        missing = sorted(set(expected) - set(nums))
        extra = sorted(set(nums) - set(expected))
        if missing:
            problems.append(f"Missing articles: {missing}")
        if extra:
            problems.append(f"Unexpected articles: {extra}")
    return problems


def rule_trust_posture(articles: List[Dict[str, Any]]) -> List[str]:
    """Every article must be internally-reviewed and flagged needs_check."""
    problems = []
    for a in articles:
        n = a["article_number"]
        if a.get("translation_mode") != _INTERNAL_MODE:
            problems.append(
                f"Article {n}: translation_mode is '{a.get('translation_mode')}', "
                f"expected '{_INTERNAL_MODE}'"
            )
        if a.get("source", {}).get("official_text_check") != "needs_check":
            problems.append(f"Article {n}: official_text_check must be 'needs_check'")
    return problems


def rule_no_verified_wording(articles: List[Dict[str, Any]]) -> List[str]:
    """No overclaiming trust wording inside canonical article fields."""
    banned = ["verified_summary", "经核验", "محققة"]
    problems = []
    for a in articles:
        blob = " ".join([
            a.get("translation_mode", ""),
            a.get("arabic_reference_summary", ""),
            a.get("chinese_translation", ""),
        ] + a.get("legal_notes", []))
        for term in banned:
            if term in blob:
                problems.append(f"Article {a['article_number']}: banned trust term '{term}'")
    return problems


def rule_b2_company_form(articles: List[Dict[str, Any]], glossary: Dict[str, Any]) -> List[str]:
    """شركة التضامن must map to 无限公司（普通合伙性质）in the glossary."""
    terms = {t["ar"]: t["zh"] for t in glossary.get("terms", [])}
    zh = terms.get("شركة التضامن", "")
    # Accept an annotated form like 无限公司（普通合伙性质，...）as long as both
    # anchor tokens are present.
    if "无限公司" in zh and "普通合伙性质" in zh:
        return []
    return ["glossary: شركة التضامن must map to 无限公司（普通合伙性质）"]


def rule_b2_unlimited_liability(articles: List[Dict[str, Any]]) -> List[str]:
    """无限连带责任 must appear in the definition article (35)."""
    a = _by_number(articles).get(35)
    if not a:
        return ["Article 35 missing"]
    if "无限连带责任" not in a.get("chinese_translation", ""):
        return ["Article 35: must contain 无限连带责任"]
    return []


def rule_b2_merchant_status(articles: List[Dict[str, Any]]) -> List[str]:
    """商人资格 (merchant status) must appear in the definition article (35)."""
    a = _by_number(articles).get(35)
    if not a:
        return ["Article 35 missing"]
    if "商人资格" not in a.get("chinese_translation", ""):
        return ["Article 35: must contain 商人资格"]
    return []


def rule_b2_legal_personality_caveat(glossary: Dict[str, Any]) -> List[str]:
    """The glossary must preserve the caveat that Saudi شركة التضامن has legal
    personality and is NOT identical to Chinese partnership entities."""
    blob = ""
    for note in glossary.get("notes", []):
        blob += " ".join(str(v) for v in note.values())
    if "法人资格" in blob and ("不" in blob) and ("合伙" in blob):
        return []
    return ["glossary: must preserve legal-personality caveat for شركة التضامن "
            "(Saudi general partnership is not identical to Chinese partnership entities)"]


def rule_b2_benefit_of_excussion(articles: List[Dict[str, Any]]) -> List[str]:
    """Prior-recourse defence (先诉抗辩权) must appear in Article 48."""
    a = _by_number(articles).get(48)
    if not a:
        return ["Article 48 missing"]
    if "先诉抗辩权" not in a.get("chinese_translation", ""):
        return ["Article 48: must contain 先诉抗辩权 (benefit of excussion)"]
    return []


def rule_b2_art37_representation(articles: List[Dict[str, Any]]) -> List[str]:
    """Article 37 must cover legal-person representation and external representation
    before courts / arbitration bodies / third parties."""
    a = _by_number(articles).get(37)
    if not a:
        return ["Article 37 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    for token in ["法人合伙人", "法院", "仲裁机构", "第三人"]:
        if token not in zh:
            problems.append(f"Article 37: must contain {token}")
    return problems


def rule_b2_art39_business_asset(articles: List[Dict[str, Any]]) -> List[str]:
    """Article 39 must use 营业资产（商业店铺）, never 营业场所（商号）."""
    a = _by_number(articles).get(39)
    if not a:
        return ["Article 39 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    if "营业资产（商业店铺）" not in zh:
        problems.append("Article 39: must contain 营业资产（商业店铺）")
    if "营业场所（商号）" in zh:
        problems.append("Article 39: must NOT contain 营业场所（商号）")
    return problems


def rule_b2_glossary_business_asset(glossary: Dict[str, Any]) -> List[str]:
    """Glossary must map المحل التجاري (المتجر) to 营业资产（商业店铺）, not 商号."""
    terms = {t["ar"]: t["zh"] for t in glossary.get("terms", [])}
    zh = terms.get("المحل التجاري (المتجر)", "")
    problems = []
    if zh != "营业资产（商业店铺）":
        problems.append("glossary: المحل التجاري (المتجر) must map to 营业资产（商业店铺）")
    if "商号" in zh:
        problems.append("glossary: المحل التجاري (المتجر) must NOT use 商号")
    return problems


def rule_scope_35_50(work: Dict[str, Any], doc: Dict[str, Any]) -> List[str]:
    problems = []
    scope_zh = doc.get("scope_zh", "")
    scope_ar = doc.get("scope_ar", "")
    if "第三十五条" not in scope_zh or "第五十条" not in scope_zh:
        problems.append("book2 scope_zh must state 第三十五条 至 第五十条")
    if "35" not in scope_ar or "50" not in scope_ar:
        problems.append("book2 scope_ar must state المواد 35–50")
    return problems


def run_all_book2(articles: List[Dict[str, Any]], work: Dict[str, Any],
                  glossary: Dict[str, Any], doc: Dict[str, Any]) -> Dict[str, List[str]]:
    """Run Book Two QA rules; returns {rule_name: [problems]}."""
    return {
        "b2_1_range_35_50": rule_range(articles, BOOK2_RANGE),
        "b2_2_no_duplicate_numbers": rule_no_duplicates(articles),
        "b2_3_bilingual_present": rule_bilingual_present(articles),
        "b2_4_trust_posture": rule_trust_posture(articles),
        "b2_5_no_verified_wording": rule_no_verified_wording(articles),
        "b2_6_company_form_terminology": rule_b2_company_form(articles, glossary),
        "b2_7_unlimited_joint_liability": rule_b2_unlimited_liability(articles),
        "b2_8_merchant_status": rule_b2_merchant_status(articles),
        "b2_9_legal_personality_caveat": rule_b2_legal_personality_caveat(glossary),
        "b2_10_benefit_of_excussion": rule_b2_benefit_of_excussion(articles),
        "b2_11_disclaimer_non_official": rule_disclaimer_non_official(work),
        "b2_12_scope_35_50": rule_scope_35_50(work, doc),
        "b2_13_art37_representation": rule_b2_art37_representation(articles),
        "b2_14_art39_business_asset": rule_b2_art39_business_asset(articles),
        "b2_15_glossary_business_asset": rule_b2_glossary_business_asset(glossary),
    }


# ==========================================================================
# Book Three — شركة التوصية البسيطة / 两合公司（有限合伙性质）— Articles 51–57
# ==========================================================================
BOOK3_RANGE = list(range(51, 58))


def rule_b3_book_number(articles: List[Dict[str, Any]]) -> List[str]:
    return [f"Article {a['article_number']}: book must be 3"
            for a in articles if a.get("book") != 3]


def rule_b3_company_form(glossary: Dict[str, Any]) -> List[str]:
    """شركة التوصية البسيطة must map to 两合公司（有限合伙性质）."""
    terms = {t["ar"]: t["zh"] for t in glossary.get("terms", [])}
    zh = terms.get("شركة التوصية البسيطة", "")
    if "两合公司" in zh and "有限合伙性质" in zh:
        return []
    return ["glossary: شركة التوصية البسيطة must map to 两合公司（有限合伙性质）"]


def rule_b3_partner_terms(glossary: Dict[str, Any]) -> List[str]:
    """General/limited partner terminology must be present and correct."""
    terms = {t["ar"]: t["zh"] for t in glossary.get("terms", [])}
    problems = []
    gen = terms.get("الشريك المتضامن", "")
    if "普通合伙人" not in gen or "无限责任" not in gen:
        problems.append("glossary: الشريك المتضامن must map to 普通合伙人（无限责任合伙人）")
    if terms.get("الشريك الموصي", "") != "有限合伙人":
        problems.append("glossary: الشريك الموصي must map to 有限合伙人")
    return problems


def rule_b3_limited_partner_liability(articles: List[Dict[str, Any]]) -> List[str]:
    """Art 51: limited partner liable only up to contribution (出资额为限)."""
    a = _by_number(articles).get(51)
    if not a:
        return ["Article 51 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    if "有限合伙人" not in zh:
        problems.append("Article 51: must mention 有限合伙人")
    if "出资额为限" not in zh:
        problems.append("Article 51: limited partner liability must be capped (出资额为限)")
    return problems


def rule_b3_limited_partner_no_merchant(articles: List[Dict[str, Any]]) -> List[str]:
    """Art 51: limited partner does NOT acquire merchant status."""
    a = _by_number(articles).get(51)
    if not a:
        return ["Article 51 missing"]
    if "有限合伙人不取得商人资格" not in a.get("chinese_translation", ""):
        return ["Article 51: must contain 有限合伙人不取得商人资格"]
    return []


def rule_b3_no_external_management(articles: List[Dict[str, Any]]) -> List[str]:
    """Art 53: limited partner must NOT participate in external management."""
    a = _by_number(articles).get(53)
    if not a:
        return ["Article 53 missing"]
    zh = a.get("chinese_translation", "")
    problems = []
    if "有限合伙人" not in zh or "对外管理" not in zh:
        problems.append("Article 53: must address 有限合伙人 / 对外管理")
    if "不得" not in zh:
        problems.append("Article 53: must prohibit (不得) external-management participation")
    # Liability consequence of interfering must be captured (present in source).
    if "连带责任" not in zh:
        problems.append("Article 53: interference liability (连带责任) must be captured")
    return problems


def rule_b3_legal_personality_caveat(articles: List[Dict[str, Any]]) -> List[str]:
    """Preserve caveat: Saudi توصية بسيطة not identical to Chinese limited partnership."""
    a = _by_number(articles).get(51)
    if not a:
        return ["Article 51 missing"]
    blob = " ".join(a.get("legal_notes", []))
    if "有限合伙企业" in blob and "الشخصية الاعتبارية" in blob:
        return []
    return ["Article 51: legal-personality caveat (not identical to Chinese 有限合伙企业) "
            "must be preserved in legal_notes"]


def rule_scope_51_57(doc: Dict[str, Any]) -> List[str]:
    problems = []
    scope_zh = doc.get("scope_zh", "")
    scope_ar = doc.get("scope_ar", "")
    if "第五十一条" not in scope_zh or "第五十七条" not in scope_zh:
        problems.append("book3 scope_zh must state 第五十一条 至 第五十七条")
    if "51" not in scope_ar or "57" not in scope_ar:
        problems.append("book3 scope_ar must state المواد 51–57")
    return problems


def run_all_book3(articles: List[Dict[str, Any]], work: Dict[str, Any],
                  glossary: Dict[str, Any], doc: Dict[str, Any]) -> Dict[str, List[str]]:
    """Run Book Three QA rules; returns {rule_name: [problems]}."""
    return {
        "b3_1_range_51_57": rule_range(articles, BOOK3_RANGE),
        "b3_2_no_duplicate_numbers": rule_no_duplicates(articles),
        "b3_3_bilingual_present": rule_bilingual_present(articles),
        "b3_4_book_number_3": rule_b3_book_number(articles),
        "b3_5_trust_posture": rule_trust_posture(articles),
        "b3_6_no_verified_wording": rule_no_verified_wording(articles),
        "b3_7_company_form": rule_b3_company_form(glossary),
        "b3_8_partner_terms": rule_b3_partner_terms(glossary),
        "b3_9_limited_partner_liability": rule_b3_limited_partner_liability(articles),
        "b3_10_limited_partner_no_merchant": rule_b3_limited_partner_no_merchant(articles),
        "b3_11_no_external_management": rule_b3_no_external_management(articles),
        "b3_12_legal_personality_caveat": rule_b3_legal_personality_caveat(articles),
        "b3_13_disclaimer_non_official": rule_disclaimer_non_official(work),
        "b3_14_scope_51_57": rule_scope_51_57(doc),
    }


# ==========================================================================
# Book Four — شركة المساهمة / 股份公司 (JSC) — Articles 58–137 — MODEL 1b
# Infrastructure-stage QA: validates the COVERAGE MATRIX (all 80 articles) and
# the model-1b guardrails, NOT a per-article dataset (which does not exist yet).
# ==========================================================================
BOOK4_RANGE = list(range(58, 138))
_B4_BANNED = ["verified_summary", "verified", "محققة", "经核验"]
_B4_ALLOWED_COVERAGE = {"explicit_in_source", "not_explicit_in_source"}
_B4_ALLOWED_CHECK = {"needs_check", "needs_official_text_check"}
_B4_ALLOWED_RECORD = {"pending", "no_record_until_source_available"}
# Coverage rows must NOT carry legal provision text (that belongs on provision
# records under model 1b, not the coverage matrix).
_B4_FORBIDDEN_ROW_KEYS = {"arabic_reference_summary", "chinese_translation"}


def rule_b4_coverage_range(coverage: Dict[str, Any]) -> List[str]:
    rows = coverage.get("rows", [])
    nums = [r.get("article_number") for r in rows]
    problems = []
    if len(rows) != 80:
        problems.append(f"coverage must have exactly 80 rows, found {len(rows)}")
    if sorted(n for n in nums if isinstance(n, int)) != BOOK4_RANGE:
        problems.append("coverage article numbers must be exactly 58–137")
    return problems


def rule_b4_no_duplicates(coverage: Dict[str, Any]) -> List[str]:
    nums = [r.get("article_number") for r in coverage.get("rows", [])]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    return [f"coverage duplicate article numbers: {dupes}"] if dupes else []


def rule_b4_status_fields(coverage: Dict[str, Any]) -> List[str]:
    problems = []
    for r in coverage.get("rows", []):
        n = r.get("article_number")
        if r.get("source_coverage_status") not in _B4_ALLOWED_COVERAGE:
            problems.append(f"article {n}: bad source_coverage_status {r.get('source_coverage_status')!r}")
        if r.get("official_text_check") not in _B4_ALLOWED_CHECK:
            problems.append(f"article {n}: bad official_text_check {r.get('official_text_check')!r}")
        if r.get("content_record_status") not in _B4_ALLOWED_RECORD:
            problems.append(f"article {n}: bad content_record_status {r.get('content_record_status')!r}")
    return problems


def rule_b4_uncovered_needs_check(coverage: Dict[str, Any]) -> List[str]:
    problems = []
    for r in coverage.get("rows", []):
        if r.get("source_coverage_status") == "not_explicit_in_source":
            if r.get("official_text_check") != "needs_official_text_check":
                problems.append(
                    f"article {r.get('article_number')}: uncovered rows must be "
                    f"needs_official_text_check")
            if r.get("content_record_status") != "no_record_until_source_available":
                problems.append(
                    f"article {r.get('article_number')}: uncovered rows must be "
                    f"no_record_until_source_available")
    return problems


def rule_b4_no_invented_text(coverage: Dict[str, Any]) -> List[str]:
    """Coverage rows must not carry legal provision text or invented titles."""
    problems = []
    for r in coverage.get("rows", []):
        n = r.get("article_number")
        for k in _B4_FORBIDDEN_ROW_KEYS:
            if r.get(k):
                problems.append(f"article {n}: coverage row must not contain '{k}'")
        # Uncovered rows must not carry invented titles.
        if r.get("source_coverage_status") == "not_explicit_in_source":
            if r.get("article_title_ar") not in (None, "", "NEEDS_OFFICIAL_TEXT_CHECK"):
                problems.append(f"article {n}: uncovered row must not have an invented AR title")
            if r.get("article_title_zh") not in (None, "", "NEEDS_OFFICIAL_TEXT_CHECK"):
                problems.append(f"article {n}: uncovered row must not have an invented ZH title")
    return problems


def rule_b4_no_overclaim(coverage_text: str) -> List[str]:
    return [f"Book Four coverage contains banned trust term '{t}'"
            for t in _B4_BANNED if t in coverage_text]


def rule_b4_disclaimer_scope(disclaimer_ar: str, disclaimer_zh: str) -> List[str]:
    problems = []
    if "الباب الرابع" not in disclaimer_ar or "58" not in disclaimer_ar or "137" not in disclaimer_ar:
        problems.append("book4 disclaimer_ar must state الباب الرابع and المواد 58–137")
    if "شركة المساهمة" not in disclaimer_ar:
        problems.append("book4 disclaimer_ar must mention شركة المساهمة")
    if "第四编" not in disclaimer_zh or "第五十八条" not in disclaimer_zh or "第一百三十七条" not in disclaimer_zh:
        problems.append("book4 disclaimer_zh must state 第四编 and 第五十八条至第一百三十七条")
    if "股份公司" not in disclaimer_zh:
        problems.append("book4 disclaimer_zh must mention 股份公司")
    # Must not leak prior books' scope.
    for bad in ("الباب الأول", "الباب الثاني", "الباب الثالث",
                "第一编", "第二编", "第三编", "1–34", "35–50", "51–57"):
        if bad in disclaimer_ar or bad in disclaimer_zh:
            problems.append(f"book4 disclaimer must not contain prior-book scope '{bad}'")
    return problems


def rule_b4_no_full_article_dataset(article_dataset_exists: bool) -> List[str]:
    return (["Book Four per-article dataset must NOT exist at the model-1b "
             "infrastructure stage"] if article_dataset_exists else [])


def rule_b4_model_doc_exists(model_doc_exists: bool) -> List[str]:
    return ([] if model_doc_exists else
            ["docs/book4_preflight/BOOK4_MODEL_1B_DECISION.md must exist"])


def run_all_book4(coverage: Dict[str, Any], coverage_text: str,
                  disclaimer_ar: str, disclaimer_zh: str,
                  model_doc_exists: bool, article_dataset_exists: bool
                  ) -> Dict[str, List[str]]:
    """Book Four (model 1b) infrastructure QA."""
    return {
        "b4_1_coverage_range_58_137": rule_b4_coverage_range(coverage),
        "b4_2_no_duplicate_numbers": rule_b4_no_duplicates(coverage),
        "b4_3_status_fields": rule_b4_status_fields(coverage),
        "b4_4_uncovered_needs_check": rule_b4_uncovered_needs_check(coverage),
        "b4_5_no_invented_text_or_titles": rule_b4_no_invented_text(coverage),
        "b4_6_no_overclaim": rule_b4_no_overclaim(coverage_text),
        "b4_7_disclaimer_scope": rule_b4_disclaimer_scope(disclaimer_ar, disclaimer_zh),
        "b4_8_no_full_article_dataset": rule_b4_no_full_article_dataset(article_dataset_exists),
        "b4_9_model_1b_doc_exists": rule_b4_model_doc_exists(model_doc_exists),
    }
