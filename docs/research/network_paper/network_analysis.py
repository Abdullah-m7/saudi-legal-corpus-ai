#!/usr/bin/env python3
"""Network analysis of the Saudi legislative citation graph (paper 2).

Read-only over the corpus. Produces every figure reported in the paper:

  1. Edge-resolution QC — the corpus extractor resolves a cited law name to a
     target track; a share of those resolutions are wrong, so every resolved
     inter-instrument edge is scored by token overlap between the raw cited
     name and the target's registered Arabic title, and low-overlap edges are
     adjudicated against a hand-reviewed decision list before analysis.
  2. Centrality over the validated instrument-level citation network.
  3. Dangling citations: live instruments citing predecessors that the
     supersession graph records as repealed.
  4. Coverage: cited instruments absent from the corpus.
  5. Domain-level citation flows.

Run from the repository root:

    python3 docs/research/network_paper/network_analysis.py
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA = REPO_ROOT / "data"
OUT = Path(__file__).resolve().parent / "network_analysis_results.json"

sys.path.insert(0, str(REPO_ROOT / "docs" / "research" / "corpus_paper"))
from domain_coverage import classify_text  # noqa: E402

# --- Arabic normalization -------------------------------------------------

DIACRITICS = re.compile(r"[ً-ْٰـ]")
# Words that carry no identifying information when comparing a cited name to a
# registered law title.
STOPWORDS = {
    "نظام", "النظام", "لائحة", "اللائحة", "التنفيذية", "التنفيذي", "قواعد",
    "السابق", "السابقة", "الصادر", "الصادرة", "ولائحته", "ولوائحه", "ملغي",
    "ملغى", "من", "في", "على", "الى", "إلى", "و", "أو", "ذات", "الصلة",
    "وتعديلاته", "بالمرسوم", "الملكي", "رقم", "وتاريخ", "هـ", "مع", "مراعاة",
}


def normalize(text):
    text = DIACRITICS.sub("", text or "")
    text = (
        text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        .replace("ة", "ه").replace("ى", "ي")
    )
    text = re.sub(r"[^؀-ۿ\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def content_tokens(text):
    return {
        w for w in normalize(text).split()
        if len(w) > 2 and normalize(w) not in {normalize(s) for s in STOPWORDS}
    }


# --- Hand adjudication of low-overlap edge resolutions --------------------
# Reviewed one by one against the raw citation text and the target's title.
# Key: (raw cited name, resolved target_track_id). Value: True to keep the
# edge, False to drop it as a misresolution.
ADJUDICATED = {
    ("إفلاس", "bankruptcy_law"): True,            # morphological variant
    ("المقي", "accredited_valuers_law"): True,    # truncated but unambiguous
    ("تأديب الموظفين", "contractors_classification_law"): False,
    ("الشريعة الإسلامية", "public_prosecution_law"): False,
    ("إجراءات التراخيص البلدية ولائحته التنفيذية",
     "debt_collection_regulation"): False,
    ("المهن الصحية ولائحته التنفيذية ونظام وحدات الإخصاب والأجنة وع",
     "enforcement_law"): False,
    ("الطفل ولائحته التنفيذية وخاصة حالات الإيذاء", "enforcement_law"): False,
    ("البلديات والقرى ولوائحه التنفيذية", "press_law"): False,
    ("نظم المدفوعات المهمة ذات الصلة",
     "high_risk_professions_regulation"): False,
    ("أي دولة", "state_revenue_law"): False,
    ("الوزارة", "electricity_regulation"): False,
    ("الإيداع", "juveniles_law"): False,
}


def load():
    graph = json.load(open(
        DATA / "corpus_cross_reference_graph" / "corpus_cross_reference_graph.json",
        encoding="utf-8"))
    registry = json.load(open(
        DATA / "corpus_registry" / "corpus_registry.json", encoding="utf-8"))
    supersession = json.load(open(
        DATA / "corpus_supersession_graph" / "corpus_supersession_graph.json",
        encoding="utf-8"))
    return graph, registry, supersession


def validate_edges(inter, titles_ar):
    """Split resolved inter-instrument edges into kept and dropped."""
    kept, dropped, auto, adjudged = [], [], 0, 0
    for r in inter:
        tid = r.get("target_track_id")
        if not tid:
            continue
        raw = (r.get("target_law_name_raw") or "").strip()
        overlap = content_tokens(raw) & content_tokens(titles_ar.get(tid, ""))
        if overlap:
            kept.append(r)
            auto += 1
            continue
        decision = ADJUDICATED.get((raw, tid))
        adjudged += 1
        (kept if decision else dropped).append(r)
    return kept, dropped, auto, adjudged


def main():
    graph, registry, supersession = load()
    tracks = {t["track_id"]: t for t in registry["tracks"]}
    titles_ar = {k: v.get("display_name_ar", "") for k, v in tracks.items()}
    titles_en = {k: v.get("display_name_en", "") for k, v in tracks.items()}

    inter = [r for r in graph["references"] if r.get("type") == "inter_law"]
    resolved = [r for r in inter if r.get("target_track_id")]
    unresolved = [r for r in inter if not r.get("target_track_id")]

    kept, dropped, auto_accepted, adjudicated = validate_edges(inter, titles_ar)

    # --- 2. Instrument-level citation network -----------------------------
    G = nx.DiGraph()
    for t in tracks:
        if tracks[t].get("corpus_family") != "closure_audit":
            G.add_node(t)
    weights = Counter((r["source_track_id"], r["target_track_id"]) for r in kept)
    for (u, v), w in weights.items():
        if u != v:
            G.add_edge(u, v, weight=w)

    pagerank = nx.pagerank(G, weight="weight")
    betweenness = nx.betweenness_centrality(G)
    in_deg = dict(G.in_degree(weight="weight"))
    out_deg = dict(G.out_degree(weight="weight"))

    def top(metric, n=15, weighted=True):
        return [
            {
                "track_id": k,
                "title_en": titles_en.get(k, ""),
                "title_ar": titles_ar.get(k, ""),
                "value": round(v, 6) if isinstance(v, float) else v,
                "distinct_citing_instruments": G.in_degree(k),
            }
            for k, v in sorted(metric.items(), key=lambda kv: -kv[1])[:n] if v
        ]

    active = [n for n in G if G.degree(n) > 0]
    sub = G.subgraph(active)

    # --- 3. Dangling citations to repealed instruments ---------------------
    repealed = []
    for e in supersession["edges"]:
        desc = e.get("target_description_ar")
        if desc and e.get("relation", "").startswith("repeals"):
            repealed.append({
                "description_ar": desc,
                "tokens": content_tokens(desc),
                "repealed_by": e["from_track_id"],
                "relation": e["relation"],
                "target_track_id": e.get("target_track_id"),
            })

    # A cited name matches a repealed instrument only when all of its content
    # tokens appear in that instrument's description AND it carries at least
    # two of them. The second condition is essential: single generic tokens
    # such as "الهيئة" (the Authority) or "العمل" (work) are contained in many
    # descriptions and produce false matches, so one-token names are excluded
    # rather than counted.
    MIN_TOKENS = 2
    dangling, seen = [], set()
    for r in unresolved:
        raw = (r.get("target_law_name_raw") or "").strip()
        rt = content_tokens(raw)
        if len(rt) < MIN_TOKENS:
            continue
        for rep in repealed:
            if rt <= rep["tokens"]:
                key = (r["source_track_id"], r.get("source_article_number"), raw)
                if key in seen:
                    break
                seen.add(key)
                dangling.append({
                    "citing_track": r["source_track_id"],
                    "citing_title_en": titles_en.get(r["source_track_id"], ""),
                    "citing_article": r.get("source_article_number"),
                    "cited_name_raw": raw,
                    "raw_citation_text": r.get("raw_citation_text"),
                    "repealed_instrument": rep["description_ar"],
                    "repealed_by": rep["repealed_by"],
                    "repealed_by_title_en": titles_en.get(rep["repealed_by"], ""),
                    "relation": rep["relation"],
                })
                break

    # --- 4. Cited-but-absent instruments -----------------------------------
    unresolved_names = Counter(
        (r.get("target_law_name_raw") or "").strip() for r in unresolved
    )

    # --- 4b. Vertical vs horizontal citation -------------------------------
    # A law and its implementing regulation belong to one instrument family.
    # Citations inside a family are vertical (a regulation elaborating its own
    # parent statute); citations across families are horizontal (one body of
    # law reaching into another). Conflating them inflates the apparent
    # centrality of any statute that happens to carry a long regulation.
    SUFFIXES = [
        "_implementing_regulation", "_regulation", "_law", "_rules", "_statute",
        "_guide", "_mechanism", "_arrangements", "_forms", "_manuals",
        "_organizational_statute", "_enablers", "_legacy",
    ]

    def family(track_id):
        base = track_id
        changed = True
        while changed:
            changed = False
            for s in SUFFIXES:
                if base.endswith(s) and len(base) > len(s):
                    base, changed = base[: -len(s)], True
        return base

    vertical = [r for r in kept
                if family(r["source_track_id"]) == family(r["target_track_id"])]
    horizontal = [r for r in kept
                  if family(r["source_track_id"]) != family(r["target_track_id"])]

    H = nx.DiGraph()
    for r in horizontal:
        u, v = r["source_track_id"], r["target_track_id"]
        H.add_edge(u, v, weight=H.get_edge_data(u, v, {}).get("weight", 0) + 1)
    h_in = dict(H.in_degree(weight="weight"))
    h_sources = {n: H.in_degree(n) for n in H}

    horizontal_top = [
        {
            "track_id": k,
            "title_en": titles_en.get(k, ""),
            "citations": v,
            "distinct_citing_instruments": h_sources.get(k, 0),
        }
        for k, v in sorted(h_in.items(), key=lambda kv: -kv[1])[:15] if v
    ]

    # --- 5. Domain-level flows ---------------------------------------------
    flows = Counter()
    for r in kept:
        d_from = classify_text(r["source_track_id"])
        d_to = classify_text(r["target_track_id"])
        flows[(d_from, d_to)] += 1
    intra_domain = sum(v for (a, b), v in flows.items() if a == b)

    results = {
        "edge_validation": {
            "inter_instrument_references_extracted": len(inter),
            "resolved_to_a_corpus_track": len(resolved),
            "unresolved_target_names": len(unresolved),
            "auto_accepted_by_token_overlap": auto_accepted,
            "hand_adjudicated": adjudicated,
            "kept_after_validation": len(kept),
            "dropped_as_misresolution": len(dropped),
            "misresolution_rate_of_resolved_edges": round(
                len(dropped) / len(resolved), 4) if resolved else None,
            "dropped_examples": [
                {"raw": r.get("target_law_name_raw"),
                 "wrongly_resolved_to": r["target_track_id"],
                 "target_title_ar": titles_ar.get(r["target_track_id"], "")}
                for r in dropped
            ],
        },
        "network": {
            "nodes_total": G.number_of_nodes(),
            "nodes_with_at_least_one_citation": len(active),
            "edges_distinct_instrument_pairs": G.number_of_edges(),
            "citations_carried": int(sum(d["weight"] for _, _, d in G.edges(data=True))),
            "density_over_active_subgraph": round(nx.density(sub), 6),
            "weakly_connected_components": nx.number_weakly_connected_components(sub),
            "largest_weak_component_size": max(
                (len(c) for c in nx.weakly_connected_components(sub)), default=0),
            "reciprocal_pairs": sum(
                1 for u, v in G.edges() if G.has_edge(v, u)) // 2,
            "self_citations_excluded": sum(
                1 for (u, v) in weights if u == v),
        },
        "centrality": {
            "most_cited_in_degree": top(in_deg),
            "most_citing_out_degree": top(out_deg),
            "pagerank": top(pagerank),
            "betweenness": top(betweenness, n=10),
        },
        "vertical_vs_horizontal": {
            "vertical_citations_within_instrument_family": len(vertical),
            "horizontal_citations_across_families": len(horizontal),
            "horizontal_share": round(len(horizontal) / len(kept), 4) if kept else None,
            "horizontal_network_nodes": H.number_of_nodes(),
            "horizontal_network_edges": H.number_of_edges(),
            "horizontal_most_cited": horizontal_top,
        },
        "dangling_citations_to_repealed_instruments": {
            "count": len(dangling),
            "distinct_citing_instruments": len({d["citing_track"] for d in dangling}),
            "cases": dangling,
        },
        "cited_but_absent_from_corpus": {
            "reference_count": len(unresolved),
            "distinct_names": len(unresolved_names),
            "top_names": dict(unresolved_names.most_common(25)),
        },
        "domain_flows": {
            "intra_domain_citations": intra_domain,
            "inter_domain_citations": sum(flows.values()) - intra_domain,
            "top_flows": {f"{a} -> {b}": v
                          for (a, b), v in flows.most_common(15)},
            "all_flows": {f"{a} -> {b}": v
                          for (a, b), v in sorted(flows.items(),
                                                  key=lambda kv: -kv[1])},
        },
    }

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")

    v = results["edge_validation"]
    print(f"edges: {v['inter_instrument_references_extracted']} inter-instrument, "
          f"{v['resolved_to_a_corpus_track']} resolved, "
          f"{v['kept_after_validation']} kept, "
          f"{v['dropped_as_misresolution']} dropped "
          f"({v['misresolution_rate_of_resolved_edges']:.1%} misresolution)")
    n = results["network"]
    print(f"network: {n['nodes_with_at_least_one_citation']} active instruments, "
          f"{n['edges_distinct_instrument_pairs']} edges, "
          f"{n['reciprocal_pairs']} reciprocal pairs, "
          f"largest component {n['largest_weak_component_size']}")
    print(f"dangling citations to repealed instruments: "
          f"{results['dangling_citations_to_repealed_instruments']['count']}")
    print("\ntop cited:")
    for r in results["centrality"]["most_cited_in_degree"][:8]:
        print(f"  {r['value']:3d}  {r['title_en'][:60]}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
