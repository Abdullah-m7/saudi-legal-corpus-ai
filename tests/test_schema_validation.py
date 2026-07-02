"""Schema validation + full-corpus validate_all() must pass."""


def test_validate_all_passes():
    from saudi_law_corpus.validate import validate_all

    ok, report = validate_all()
    problems = {k: v for k, v in report.items() if v}
    assert ok, f"validation problems: {problems}"


def test_each_article_matches_schema(articles, repo_root):
    from saudi_law_corpus.validate import validate_against_schema
    import json
    import os

    with open(os.path.join(repo_root, "schemas", "article.schema.json"),
              encoding="utf-8") as fh:
        schema = json.load(fh)
    for a in articles:
        problems = validate_against_schema(a, schema, f"article {a['article_number']}")
        assert not problems, problems


def test_chunk_ids_are_well_formed(articles):
    for a in articles:
        cid = a["llm"]["chunk_id"]
        assert cid == f"sa-companies-book1-art{a['article_number']:03d}", cid


def test_official_text_check_flagged(articles):
    # Provenance honesty: nothing is claimed as officially checked in this build.
    for a in articles:
        assert a["source"]["official_text_check"] in ("checked", "needs_check")


def test_translation_mode_is_internally_reviewed(articles):
    # Trust posture: internally reviewed, NOT officially verified.
    for a in articles:
        assert a["translation_mode"] == "internally_reviewed_summary", a["article_number"]


def test_no_verified_summary_in_canonical_json_or_schema(repo_root):
    import os

    targets = [
        os.path.join(repo_root, "data", "articles", "book1_articles_001_034.json"),
        os.path.join(repo_root, "schemas", "article.schema.json"),
    ]
    for path in targets:
        with open(path, encoding="utf-8") as fh:
            assert "verified_summary" not in fh.read(), path
