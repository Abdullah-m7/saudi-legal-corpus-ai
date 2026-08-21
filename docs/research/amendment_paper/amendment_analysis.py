#!/usr/bin/env python3
"""Legislative churn in Saudi legislation (paper 4).

Papers 1--3 treated the corpus as a still photograph: what is in it, how its
instruments cite each other, whether they share a vocabulary. This one asks
the temporal question --- what changes, where, and how much.

The corpus records a legal status for every article it verified against an
official source: original, amended, repealed or added. For a subset it also
records an amendment history. That history comes in two shapes, and conflating
them would corrupt every number below:

  event log     entries carrying a decree but no text --- one entry per
                amending instrument, so the entry count is the number of
                amendment events the article has been through
  prior version entries carrying the superseded text --- so the current text
                can be compared against what it replaced

Read-only and deterministic over `sources/` and `data/`. Run from the
repository root:

    python3 docs/research/amendment_paper/amendment_analysis.py
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "data" / "corpus_registry" / "corpus_registry.json"
XREF = (REPO_ROOT / "data" / "corpus_cross_reference_graph"
        / "corpus_cross_reference_graph.json")
SUPERSESSION = (REPO_ROOT / "data" / "corpus_supersession_graph"
                / "corpus_supersession_graph.json")
OUT = Path(__file__).resolve().parent / "amendment_analysis_results.json"

ORIGINAL, AMENDED, REPEALED, ADDED = "اصلية", "معدلة", "ملغاة", "مضافة"
CHURN_STATUSES = (AMENDED, REPEALED, ADDED)

DIACRITICS = re.compile(r"[ً-ْٰـ]")


def normalize(text):
    """Same normalisation as the definitional study: strip diacritics and
    tatweel, fold the hamza forms, teh marbuta and alif maqsura."""
    text = DIACRITICS.sub("", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    return text


def tokens(text):
    return [t for t in re.split(r"[^\w]+", normalize(text or "")) if t]


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return None
    return len(sa & sb) / len(sa | sb)


def gini(values):
    """Gini coefficient over a non-negative series; 0 = even, 1 = all in one."""
    xs = sorted(v for v in values if v >= 0)
    n = len(xs)
    if n == 0 or sum(xs) == 0:
        return 0.0
    cumulative = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cumulative) / (n * sum(xs)) - (n + 1) / n


def normalise_decree(raw):
    """Decree strings arrive with inconsistent bracketing, spacing and
    trailing commentary. Reduce each to its issuing body plus its number so
    that 'المرسوم الملكي رقم (م/43)' and 'المرسوم الملكي رقم م/43 ' are one
    decree rather than two."""
    s = " ".join((raw or "").split())
    s = s.split(" وتاريخ")[0].split(" (المصادق")[0]
    s = s.replace("(", "").replace(")", "")
    return " ".join(s.split()).strip(" ,،.")


def load_tracks():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tracks = {t["track_id"]: t for t in registry["tracks"]}
    path_to_track = {}
    for t in registry["tracks"]:
        for key in ("data_paths", "manifest_paths", "report_paths"):
            for p in (t.get(key) or []):
                path_to_track[p] = t["track_id"]
    return tracks, path_to_track


def resolve(rel_path, tracks, path_to_track):
    """Registries name some verified-record files explicitly; the rest sit
    under sources/<track_id>/, which is the fallback."""
    if rel_path in path_to_track:
        return path_to_track[rel_path]
    segment = Path(rel_path).parts[1]
    return segment if segment in tracks else None


def load_articles(tracks, path_to_track):
    """Every verified article record that carries a legal status."""
    articles = []
    unresolved = []
    for path in sorted(REPO_ROOT.glob("sources/**/verified/*verified_records.jsonl")):
        rel = str(path.relative_to(REPO_ROOT))
        track_id = resolve(rel, tracks, path_to_track)
        if track_id is None:
            unresolved.append(rel)
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "legal_status_ar" not in rec:
                    continue
                articles.append({
                    "track_id": track_id,
                    "article_number": rec.get("article_number"),
                    "status": rec.get("legal_status_ar"),
                    "text": rec.get("article_text_verified") or "",
                    "history": [e for e in (rec.get("amendment_history") or [])
                                if isinstance(e, dict)],
                })
    return articles, unresolved


def inventory(articles, tracks):
    by_status = Counter(a["status"] for a in articles)
    covered = {a["track_id"] for a in articles}
    churn = sum(by_status[s] for s in CHURN_STATUSES)
    return {
        "articles_with_a_recorded_legal_status": len(articles),
        "instruments_covered": len(covered),
        "instruments_in_registry": len(tracks),
        "by_status": {
            "original": by_status[ORIGINAL],
            "amended": by_status[AMENDED],
            "repealed": by_status[REPEALED],
            "added": by_status[ADDED],
            "unrecorded": by_status[None],
        },
        "articles_not_in_their_original_form": churn,
        "share_not_in_their_original_form": round(churn / len(articles), 4),
    }


def churn_concentration(articles, tracks):
    per_track = defaultdict(Counter)
    for a in articles:
        per_track[a["track_id"]][a["status"]] += 1
    rows = []
    for track_id, counts in per_track.items():
        total = sum(counts.values())
        changed = sum(counts[s] for s in CHURN_STATUSES)
        rows.append({
            "track_id": track_id,
            "title_en": (tracks.get(track_id) or {}).get("display_name_en"),
            "articles": total,
            "changed": changed,
            "amended": counts[AMENDED],
            "repealed": counts[REPEALED],
            "added": counts[ADDED],
            "churn_rate": round(changed / total, 4) if total else 0.0,
        })
    rows.sort(key=lambda r: (-r["changed"], r["track_id"]))
    changed_total = sum(r["changed"] for r in rows)
    untouched = [r for r in rows if r["changed"] == 0]
    top10 = sum(r["changed"] for r in rows[:10])
    # Instruments large enough for a rate to mean anything.
    rated = [r for r in rows if r["articles"] >= 20]
    rated.sort(key=lambda r: (-r["churn_rate"], r["track_id"]))
    return {
        "instruments": len(rows),
        "instruments_with_no_recorded_change": len(untouched),
        "share_of_instruments_with_no_recorded_change":
            round(len(untouched) / len(rows), 4),
        "changed_articles_total": changed_total,
        "top_10_instruments_share_of_changed_articles":
            round(top10 / changed_total, 4) if changed_total else 0.0,
        "gini_of_changed_articles_across_instruments":
            round(gini([r["changed"] for r in rows]), 4),
        "most_changed_instruments": rows[:15],
        "highest_churn_rate_min_20_articles": rated[:15],
    }


def repeal_concentration(articles, tracks):
    per_track = Counter(a["track_id"] for a in articles
                        if a["status"] == REPEALED)
    total = sum(per_track.values())
    rows = [{"track_id": t,
             "title_en": (tracks.get(t) or {}).get("display_name_en"),
             "repealed_articles": n}
            for t, n in per_track.most_common()]
    return {
        "repealed_articles_total": total,
        "instruments_holding_them": len(per_track),
        "largest_holder_share":
            round(rows[0]["repealed_articles"] / total, 4) if rows else 0.0,
        "by_instrument": rows[:10],
    }


def history_shapes(articles):
    """The two shapes, counted, because every later measure depends on which
    subset it can legitimately use."""
    event_log = prior_version = mixed = 0
    events_per_article = Counter()
    for a in articles:
        h = a["history"]
        if not h:
            continue
        with_text = sum(1 for e in h if e.get("text"))
        if with_text == 0:
            event_log += 1
            events_per_article[len(h)] += 1
        elif with_text == len(h):
            prior_version += 1
        else:
            mixed += 1
    return {
        "articles_with_an_amendment_history":
            sum(1 for a in articles if a["history"]),
        "event_log_shape": event_log,
        "prior_version_shape": prior_version,
        "mixed_shape": mixed,
        "amendment_events_per_article_event_log_shape":
            {str(k): v for k, v in sorted(events_per_article.items())},
        "articles_amended_more_than_once_event_log_shape":
            sum(v for k, v in events_per_article.items() if k > 1),
    }


def amending_instruments(articles):
    decrees = Counter()
    dated = Counter()
    undated = 0
    for a in articles:
        seen = set()
        for entry in a["history"]:
            name = normalise_decree(entry.get("decree"))
            if not name:
                continue
            seen.add(name)
            greg = entry.get("gregorianDecreeDate")
            if greg:
                dated[(name, greg[:4])] += 1
            else:
                undated += 1
        for name in seen:
            decrees[name] += 1
    years = Counter(year for (_, year), n in dated.items() for _ in range(n))
    total = sum(decrees.values())
    top = decrees.most_common(12)
    return {
        "distinct_amending_instruments": len(decrees),
        "article_amendment_pairs": total,
        "top_10_share_of_amended_articles":
            round(sum(n for _, n in decrees.most_common(10)) / total, 4)
            if total else 0.0,
        "most_active_amending_instruments":
            [{"decree": d, "articles_touched": n} for d, n in top],
        "history_entries_without_a_gregorian_date": undated,
        "amendments_by_gregorian_year": dict(sorted(years.items())),
    }


def prior_text_selection(articles):
    """Why only entries labelled `original` are treated as superseded text.

    An amendment-history entry that carries text is not automatically a prior
    version. Measured against the article's current wording, entries labelled
    `amended` or carrying no label at all are the *current* text restated, so
    comparing them would report that amendments barely change anything. This
    block publishes the evidence for the exclusion instead of asserting it.
    """
    by_label = defaultdict(list)
    for a in articles:
        if a["status"] != AMENDED or not a["text"]:
            continue
        for entry in a["history"]:
            if not entry.get("text"):
                continue
            s = jaccard(tokens(a["text"]), tokens(entry["text"]))
            if s is not None:
                by_label[entry.get("legalStatusName")].append(s)
    out = {}
    for label, values in by_label.items():
        values.sort()
        identical = sum(1 for v in values if v > 0.98)
        out[label or "unlabelled"] = {
            "entries": len(values),
            "median_similarity_to_current_text":
                round(values[len(values) // 2], 4),
            "share_effectively_identical_to_current_text":
                round(identical / len(values), 4),
        }
    return {
        "similarity_of_history_text_to_the_current_article_text": out,
        "conclusion": "Only entries labelled 'original' are superseded "
                      "wording; the rest restate the current text and are "
                      "excluded from the magnitude measure.",
    }


def amendment_magnitude(articles):
    """How far an amendment moves the text, on the articles whose superseded
    wording the corpus actually records."""
    rows = []
    for a in articles:
        if a["status"] != AMENDED or not a["text"]:
            continue
        priors = [e for e in a["history"]
                  if e.get("text") and e.get("legalStatusName") == ORIGINAL]
        if not priors:
            continue
        similarity = jaccard(tokens(a["text"]), tokens(priors[0]["text"]))
        if similarity is None:
            continue
        rows.append({
            "track_id": a["track_id"],
            "article_number": a["article_number"],
            "similarity": round(similarity, 4),
            "tokens_now": len(tokens(a["text"])),
            "tokens_before": len(tokens(priors[0]["text"])),
        })
    rows.sort(key=lambda r: r["similarity"])
    buckets = Counter()
    for r in rows:
        s = r["similarity"]
        if s >= 0.90:
            buckets["near_identical"] += 1
        elif s >= 0.50:
            buckets["moderate_revision"] += 1
        else:
            buckets["substantial_rewrite"] += 1
    n = len(rows)
    median = rows[n // 2]["similarity"] if n else None
    growth = [r["tokens_now"] - r["tokens_before"] for r in rows]
    return {
        "amended_articles_total":
            sum(1 for a in articles if a["status"] == AMENDED),
        "amended_articles_with_a_recorded_prior_text": n,
        "coverage_of_amended_articles":
            round(n / sum(1 for a in articles if a["status"] == AMENDED), 4)
            if n else 0.0,
        "measure": "Jaccard over normalised content tokens, current vs "
                   "superseded wording",
        "median_similarity": median,
        "buckets": {
            "near_identical_ge_0.90": buckets["near_identical"],
            "moderate_revision_0.50_to_0.90": buckets["moderate_revision"],
            "substantial_rewrite_lt_0.50": buckets["substantial_rewrite"],
        },
        "articles_that_grew": sum(1 for g in growth if g > 0),
        "articles_that_shrank": sum(1 for g in growth if g < 0),
        "median_token_change": sorted(growth)[n // 2] if n else None,
        "most_rewritten": rows[:10],
    }


def citations_into_changed_articles(articles, tracks):
    """Paper 2 found instruments citing repealed instruments. The article-level
    question is sharper: does a live citation point at an article that has
    since been amended or repealed?"""
    status = {(a["track_id"], a["article_number"]): a["status"]
              for a in articles if a["article_number"] is not None}
    graph = json.loads(XREF.read_text(encoding="utf-8"))
    resolved = hits = 0
    by_status = Counter()
    by_type_resolved = Counter()
    by_type_hit = Counter()
    cases = []
    for ref in graph["references"]:
        target_track = ref.get("target_track_id")
        target_article = ref.get("target_article_number")
        if not target_track or target_article is None:
            continue
        key = (target_track, target_article)
        if key not in status:
            continue
        resolved += 1
        st = status[key]
        by_type_resolved[ref.get("type")] += 1
        if st in (AMENDED, REPEALED):
            hits += 1
            by_status[st] += 1
            by_type_hit[ref.get("type")] += 1
            if len(cases) < 60:
                cases.append({
                    "citing_track": ref.get("source_track_id"),
                    "citing_article": ref.get("source_article_number"),
                    "cited_track": target_track,
                    "cited_title_en":
                        (tracks.get(target_track) or {}).get("display_name_en"),
                    "cited_article": target_article,
                    "cited_article_status": st,
                    "type": ref.get("type"),
                })
    changed = sum(1 for a in articles if a["status"] in CHURN_STATUSES)
    base_rate = changed / len(articles) if articles else 0.0
    return {
        "citations_resolved_to_an_article_with_a_known_status": resolved,
        "citations_pointing_at_an_amended_or_repealed_article": hits,
        "share": round(hits / resolved, 4) if resolved else 0.0,
        "corpus_base_rate_of_changed_articles": round(base_rate, 4),
        "ratio_to_base_rate":
            round((hits / resolved) / base_rate, 3) if resolved and base_rate
            else None,
        "reading": "The share is close to the corpus-wide base rate, so "
                   "citations are not markedly over-exposed to changed text. "
                   "The finding is the absolute count: live cross-references "
                   "that point at wording which has since moved.",
        "by_status": {"amended": by_status[AMENDED],
                      "repealed": by_status[REPEALED]},
        "by_reference_type": {
            t: {"resolved": by_type_resolved[t],
                "pointing_at_changed_text": by_type_hit[t],
                "share": round(by_type_hit[t] / by_type_resolved[t], 4)
                if by_type_resolved[t] else 0.0}
            for t in sorted(by_type_resolved)},
        "examples": [c for c in cases if c["type"] == "inter_law"] or cases,
    }


def churn_against_citation(articles, tracks):
    """Do the instruments other instruments lean on change more, or less?"""
    graph = json.loads(XREF.read_text(encoding="utf-8"))
    in_degree = Counter()
    for ref in graph["references"]:
        if ref.get("type") == "inter_law" and ref.get("target_track_id"):
            in_degree[ref["target_track_id"]] += 1

    per_track = defaultdict(Counter)
    for a in articles:
        per_track[a["track_id"]][a["status"]] += 1

    rows = []
    for track_id, counts in per_track.items():
        total = sum(counts.values())
        if total < 20:
            continue
        changed = sum(counts[s] for s in CHURN_STATUSES)
        rows.append({"track_id": track_id,
                     "title_en": (tracks.get(track_id) or {}).get("display_name_en"),
                     "articles": total,
                     "churn_rate": changed / total,
                     "citations_received": in_degree.get(track_id, 0)})
    cited = [r for r in rows if r["citations_received"] > 0]
    uncited = [r for r in rows if r["citations_received"] == 0]

    def mean(rs):
        return round(sum(r["churn_rate"] for r in rs) / len(rs), 4) if rs else None

    ranked = sorted(rows, key=lambda r: -r["citations_received"])
    top = ranked[:15]
    return {
        "instruments_compared_min_20_articles": len(rows),
        "cited_instruments": len(cited),
        "uncited_instruments": len(uncited),
        "mean_churn_rate_cited": mean(cited),
        "mean_churn_rate_uncited": mean(uncited),
        "mean_churn_rate_top_15_most_cited": mean(top),
        "note": "In-degree is the unvalidated inter-instrument citation count "
                "from the cross-reference layer; the companion citation study "
                "showed hand validation moves aggregate shares by about one "
                "percentage point.",
        "confound": "Age is not controlled for. An older instrument has had "
                    "more time to be amended and more time to be cited, so "
                    "the gradient below is consistent with both a real "
                    "relationship and pure ageing. The registry carries a "
                    "publication date for only 2 of 291 tracks, so this "
                    "cannot be tested from the corpus as it stands.",
        "most_cited_with_churn":
            [{k: (round(v, 4) if isinstance(v, float) else v)
              for k, v in r.items()} for r in top],
    }


def supersession_summary():
    graph = json.loads(SUPERSESSION.read_text(encoding="utf-8"))
    return {
        "edges": graph["edge_count"],
        "relation_counts": graph["relation_counts"],
        "targets_outside_the_corpus": sum(
            1 for e in graph["edges"] if not e.get("target_track_id")),
    }


def main():
    tracks, path_to_track = load_tracks()
    articles, unresolved = load_articles(tracks, path_to_track)
    if unresolved:
        raise SystemExit(f"unresolved verified-record files: {unresolved[:5]}")

    results = {
        "inventory": inventory(articles, tracks),
        "churn_concentration": churn_concentration(articles, tracks),
        "repeal_concentration": repeal_concentration(articles, tracks),
        "history_shapes": history_shapes(articles),
        "amending_instruments": amending_instruments(articles),
        "prior_text_selection": prior_text_selection(articles),
        "amendment_magnitude": amendment_magnitude(articles),
        "citations_into_changed_articles":
            citations_into_changed_articles(articles, tracks),
        "churn_against_citation": churn_against_citation(articles, tracks),
        "supersession": supersession_summary(),
    }
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"wrote {OUT}")
    inv = results["inventory"]
    print(f"  {inv['articles_with_a_recorded_legal_status']:,} articles, "
          f"{inv['instruments_covered']} instruments")
    print(f"  {inv['articles_not_in_their_original_form']:,} not in their "
          f"original form ({inv['share_not_in_their_original_form']:.1%})")
    cc = results["churn_concentration"]
    print(f"  {cc['share_of_instruments_with_no_recorded_change']:.1%} of "
          f"instruments record no change at all; Gini "
          f"{cc['gini_of_changed_articles_across_instruments']}")
    cd = results["citations_into_changed_articles"]
    print(f"  {cd['citations_pointing_at_an_amended_or_repealed_article']} of "
          f"{cd['citations_resolved_to_an_article_with_a_known_status']} "
          f"resolved citations point at a changed article ({cd['share']:.1%})")


if __name__ == "__main__":
    main()
