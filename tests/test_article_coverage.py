"""Coverage: Articles 1-34 present, unique, bilingual, and correctly flagged."""

EXPANDED = {5, 6, 8, 9, 12, 13, 14, 17, 19, 20, 29}


def test_exactly_34_articles(articles):
    assert len(articles) == 34


def test_numbers_are_1_to_34(articles):
    nums = [a["article_number"] for a in articles]
    assert nums == list(range(1, 35))


def test_no_duplicate_numbers(articles):
    nums = [a["article_number"] for a in articles]
    assert len(nums) == len(set(nums))


def test_every_article_has_arabic_and_chinese(articles):
    for a in articles:
        assert a["arabic_reference_summary"].strip(), a["article_number"]
        assert a["chinese_translation"].strip(), a["article_number"]
        assert a["article_title_ar"].strip(), a["article_number"]
        assert a["article_title_zh"].strip(), a["article_number"]


def test_expanded_articles_flagged(by_number):
    for n in EXPANDED:
        assert by_number[n]["coverage_status"] == "expanded_after_review", n


def test_non_expanded_not_flagged_expanded(by_number):
    for n, a in by_number.items():
        if n not in EXPANDED:
            assert a["coverage_status"] != "expanded_after_review", n


def test_coverage_matrix_matches_articles(coverage, by_number):
    assert len(coverage["rows"]) == 34
    for r in coverage["rows"]:
        n = r["article_number"]
        assert r["article_title_zh"] == by_number[n]["article_title_zh"], n
        assert r["coverage_status"] == by_number[n]["coverage_status"], n
    assert set(coverage["expanded_after_review"]) == EXPANDED


def test_loader_api(repo_root):
    from saudi_law_corpus import list_articles, get_article, search_keyword

    assert len(list_articles()) == 34
    assert get_article(8)["article_title_zh"] == "设立文件及修改的登记"
    assert get_article(999) is None
    hits = [a["article_number"] for a in search_keyword("破产法")]
    assert 29 in hits
