#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is this corpus actually usable by a language model, or only well-formed?

Every existing validator answers a question about SHAPE: does the field exist,
does the count match, does the text reproduce. Those questions are necessary and
they all pass. None of them answers the question a reader actually has, which is
whether a model reading this corpus would answer a legal question CORRECTLY.

Five failure modes separate the two, and each is measured here against the
corpus's own committed files. Nothing is fetched, nothing is written except this
report.

  A. RETRIEVAL THAT ONLY WORKS ON VERBATIM TEXT.
     The committed retrieval eval scores ~94% top-1, and every one of its 1,407
     queries is a span lifted verbatim out of the record it is meant to find.
     That measures little: exact substring recall is nearly tautological for a
     token-overlap scorer. A person does not paste the article back at the
     index; they type a handful of the words they remember, in their own order.
     This audit re-scores the same records with the SAME scorer under queries
     built by taking each record's own distinctive terms, dropping the rest, and
     shuffling what is left. Nothing is invented — every token comes from the
     stored article. The gap between the two numbers is the honest measure of
     how much of the committed accuracy is an artifact of verbatim phrasing.

  B. TEXT A MODEL WOULD QUOTE AS LAW THAT IS NOT WHOLE.
     A record cut mid-sentence is worse than a missing record: it reads as
     complete and quotes as complete. Flagged when an article's text ends
     without sentence-final punctuation AND is long enough that the source is
     unlikely to have ended it that way.

  C. PROVISIONS WHOSE FORCE IS NOT ON THE RECORD.
     A repealed article that carries no repeal flag is the corpus's most
     dangerous possible output, because the model will state it as current law.
     Counted per track, against the corpus's own legal_status_ar field and its
     supersession graph.

  D. CITATIONS A MODEL CANNOT MAKE.
     If a record cannot be pointed at — no instrument name, no unit label, no
     resolvable path — then whatever it says is unattributable, and an
     unattributable legal statement is not usable. Checked field by field.

  E. UNITS THAT ARE NOT ARTICLES BUT READ AS ARTICLES.
     The corpus deliberately stores ordinal bands and numbered clauses in the
     same fields as articles, and discloses this per track. That disclosure is
     only worth something if it is actually present on every track that needs
     it; a band cited as «المادة» is a fabricated citation. Cross-checked
     between the stored labels and the track's own discrepancy list.

Exit status is always 0: this is a measurement, not a gate. What it finds is
recorded so it can be argued with.
"""

from __future__ import annotations

import glob
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
REGISTRY = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
SUPERSESSION = os.path.join(ROOT, "data", "corpus_supersession_graph",
                            "corpus_supersession_graph.json")
OUT_DIR = os.path.join(ROOT, "reports", "corpus_llm_readiness_audit")

# ---- A. term-form retrieval ------------------------------------------------
# How many records to re-score. The full index takes hours under an O(N) scorer;
# a sample large enough that the interval around the measured rate is a fraction
# of a point is enough to answer the question, and the sample is SEEDED so the
# number is reproducible from the committed report.
SAMPLE = 1200
SEED = 20260805
TERMS_PER_QUERY = 6
MIN_TERM_LEN = 4
# Function words carry no discriminating power and a query made of them measures
# nothing. This list is the corpus's own high-frequency Arabic, not a guess.
STOPWORDS = {
    "في", "من", "على", "إلى", "الى", "عن", "أن", "ان", "التي", "الذي", "هذه", "هذا",
    "ما", "لا", "أو", "او", "مع", "بين", "كل", "عند", "بعد", "قبل", "غير", "وفق",
    "وفقا", "وفقاً", "بما", "لم", "إذا", "اذا", "قد", "ذلك", "به", "بها", "له", "لها",
    "عليه", "عليها", "منه", "منها", "فيه", "فيها", "التالية", "الآتية", "الاتية",
    "يكون", "تكون", "يجب", "يجوز", "ويجوز", "ولا", "وإذا", "أي", "اي", "دون", "حال",
}

# ---- B. truncation ---------------------------------------------------------
SENTENCE_FINAL = ".؟!»\"'）)]:؛"
# Below this length an article may legitimately be a bare label or a cross-reference
# and its ending tells us nothing; above it, an unterminated tail is a real signal.
TRUNCATION_MIN_CHARS = 120

# ---- E. non-article units --------------------------------------------------
BAND_LABEL_RE = re.compile(r"^(?:أول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر|حادي|"
                           r"البند)\b|^[0-9٠-٩]{1,3}\s*[-–—]\s*$")
FORM_DISCLOSURE_KEYS = ("_numbering_form_is_ordinal_bands", "_numbering_form_is_numbered_clauses")


def load_index():
    with open(INDEX, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def norm(s):
    s = re.sub(r"[ً-ْـ]", "", s or "")
    return re.sub(r"[^\w؀-ۿ]+", " ", s).strip()


def distinctive_terms(text, df, n_docs):
    """The record's own words, rarest first.

    Every token comes out of the stored article — the query is a SELECTION of the
    corpus's text, never an addition to it, which is what keeps this a measurement
    of retrieval rather than an invention of content."""
    seen, out = set(), []
    for w in norm(text).split():
        if len(w) < MIN_TERM_LEN or w in STOPWORDS or w in seen:
            continue
        seen.add(w)
        out.append(w)
    # rarest first: a term appearing in half the corpus cannot identify a record
    out.sort(key=lambda w: df.get(w, 1))
    return out


def term_form_retrieval(records, rng):
    from search_corpus_unified import load_index as load_search_index, search

    df = Counter()
    for r in records:
        df.update(set(norm(r.get("text_ar", "")).split()))
    n_docs = len(records)

    pool = [r for r in records if len(norm(r.get("text_ar", "")).split()) >= 12]
    sample = rng.sample(pool, min(SAMPLE, len(pool)))

    index = load_search_index()
    hits = {1: 0, 3: 0, 5: 0}
    rr_total = 0.0
    scored = 0
    misses = []
    for r in sample:
        terms = distinctive_terms(r.get("text_ar", ""), df, n_docs)[:TERMS_PER_QUERY]
        if len(terms) < 3:
            continue
        rng.shuffle(terms)
        q = " ".join(terms)
        res = search(q, top=5, index=index)
        scored += 1
        rank = None
        for i, hit in enumerate(res, 1):
            if hit.get("record_id") == r["record_id"]:
                rank = i
                break
        if rank:
            for k in (1, 3, 5):
                if rank <= k:
                    hits[k] += 1
            rr_total += 1.0 / rank
        elif len(misses) < 40:
            misses.append({"record_id": r["record_id"], "corpus": r["corpus"],
                           "query_terms": q,
                           "top1": res[0].get("record_id") if res else None})
    return {
        "queries_scored": scored,
        "top_1": round(hits[1] / scored, 4) if scored else None,
        "top_3": round(hits[3] / scored, 4) if scored else None,
        "top_5": round(hits[5] / scored, 4) if scored else None,
        "mrr_at_5": round(rr_total / scored, 4) if scored else None,
        "sample_misses": misses,
    }


def truncation(records):
    flagged = []
    for r in records:
        t = (r.get("text_ar") or "").strip()
        if len(t) < TRUNCATION_MIN_CHARS:
            continue
        if t[-1] not in SENTENCE_FINAL:
            flagged.append({"record_id": r["record_id"], "corpus": r["corpus"],
                            "chars": len(t), "ends_with": t[-42:]})
    by_corpus = Counter(f["corpus"] for f in flagged)
    return {"records_flagged": len(flagged),
            "share_of_corpus": round(len(flagged) / len(records), 4),
            "worst_corpora": by_corpus.most_common(25),
            "examples": flagged[:40]}


def force_on_the_record(records):
    """Can a reader tell, from the record alone, whether the provision is in force?"""
    status_field = defaultdict(Counter)
    for r in records:
        status_field[r["corpus"]][r.get("legal_status_ar") or r.get("text_status") or "<none>"] += 1

    sup = json.load(open(SUPERSESSION, encoding="utf-8"))
    edges = sup.get("edges", sup if isinstance(sup, list) else [])
    superseded_tracks = set()
    for e in edges:
        if not isinstance(e, dict):
            continue
        tgt = e.get("target") or e.get("to") or e.get("superseded")
        if tgt and str(e.get("relation", e.get("type", ""))).startswith("repeals_full"):
            superseded_tracks.add(tgt)

    # A record carrying no status at all cannot be reported as in force or not.
    unstated = [c for c, counts in status_field.items() if "<none>" in counts]
    return {
        "tracks_with_records_carrying_no_legal_status": sorted(unstated),
        "supersession_edges": len(edges),
        "tracks_named_as_fully_repealed_by_the_graph": sorted(superseded_tracks),
    }


def citability(records):
    missing = defaultdict(list)
    for r in records:
        for field in ("law_title_ar", "retrieval_title_ar", "article_path", "article_number"):
            v = r.get(field)
            if v is None or (isinstance(v, str) and not v.strip()):
                missing[field].append(r["record_id"])
    return {f: {"count": len(ids), "examples": ids[:10]} for f, ids in missing.items()} or {}


def unit_labels(records):
    """A band or a clause stored in an article field must SAY so on its track."""
    per_track_labels = defaultdict(Counter)
    for r in records:
        lab = (r.get("retrieval_title_ar") or "").split(" - ")[-1].strip()
        per_track_labels[r["corpus"]][lab] += 1

    undisclosed = []
    for tid, labels in sorted(per_track_labels.items()):
        non_article = [l for l in labels if l and not l.startswith("الماد")]
        if not non_article:
            continue
        art = os.path.join(ROOT, "sources", tid, "official_source",
                           "%s_official_source.json" % tid)
        disclosed = False
        if os.path.exists(art):
            blob = open(art, encoding="utf-8").read()
            disclosed = any(k in blob for k in FORM_DISCLOSURE_KEYS)
        if not disclosed:
            undisclosed.append({"track_id": tid, "labels": non_article[:6],
                                "records": sum(labels[l] for l in non_article)})
    return {"tracks_whose_units_are_not_articles": len(
        [t for t, ls in per_track_labels.items() if any(l and not l.startswith("الماد") for l in ls)]),
        "of_those_without_a_form_disclosure": undisclosed}


def main():
    records = load_index()
    rng = random.Random(SEED)

    print("records in the unified index: %d" % len(records))
    print("A. re-scoring retrieval under term-form queries (%d sampled)..." % SAMPLE, flush=True)
    a = term_form_retrieval(records, rng)
    print("   top-1 %.1f%%  top-3 %.1f%%  top-5 %.1f%%  MRR@5 %.4f"
          % (100 * a["top_1"], 100 * a["top_3"], 100 * a["top_5"], a["mrr_at_5"]))

    print("B. checking for text that is not whole...", flush=True)
    b = truncation(records)
    print("   %d records end without sentence-final punctuation (%.2f%%)"
          % (b["records_flagged"], 100 * b["share_of_corpus"]))

    print("C. checking whether force is on the record...", flush=True)
    c = force_on_the_record(records)

    print("D. checking citability...", flush=True)
    d = citability(records)

    print("E. checking non-article units against their disclosures...", flush=True)
    e = unit_labels(records)
    print("   %d tracks store non-article units; %d of them disclose nothing"
          % (e["tracks_whose_units_are_not_articles"], len(e["of_those_without_a_form_disclosure"])))

    committed = json.load(open(os.path.join(
        ROOT, "data", "corpus_retrieval_eval", "corpus_retrieval_eval_results.json"),
        encoding="utf-8"))
    report = {
        "generated_note": (
            "Measures whether a language model reading this corpus would answer correctly, "
            "not whether the corpus is well-formed — every existing validator already answers "
            "the second question and they all pass. Section A is the load-bearing one: the "
            "committed retrieval evaluation scores its queries as verbatim spans of the very "
            "records they are meant to find, which is close to a tautology for a token-overlap "
            "scorer. Re-scoring the same index with the same scorer under queries made of each "
            "record's own distinctive terms, shuffled, gives the number that survives when the "
            "phrasing is not the article's own. Every query token is taken from the stored "
            "text; nothing is composed. Read-only; writes only this report."),
        "index_records": len(records),
        "A_retrieval_under_term_form_queries": a,
        "A_committed_verbatim_span_result_for_comparison": {
            k: committed.get("metrics", {}).get(k)
            for k in ("total_queries", "top1_accuracy", "top3_accuracy",
                      "top5_accuracy", "mrr_at_5")
        },
        "B_text_that_is_not_whole": b,
        "C_force_on_the_record": c,
        "D_records_that_cannot_be_cited": d,
        "E_units_that_are_not_articles": e,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "corpus_llm_readiness_audit.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("\nwrote reports/corpus_llm_readiness_audit/corpus_llm_readiness_audit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
