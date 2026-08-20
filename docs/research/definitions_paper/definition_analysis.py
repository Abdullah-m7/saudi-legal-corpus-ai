#!/usr/bin/env python3
"""Definitional fragmentation across Saudi legislation (paper 3).

Saudi statutes conventionally open with a definitions article, and the same
term is often defined by many instruments. Counting that directly is
misleading: the most frequently defined terms are *indexical* — "the Law",
"the Ministry", "the Minister" — which every instrument defines as pointing
to itself or its own supervising body. Those are a drafting convention, not
a disagreement.

This script therefore (1) separates indexical from substantive definitions,
(2) measures, among substantive terms defined by more than one instrument,
how far the definitions actually diverge, and (3) surfaces the divergent
cases for legal reading.

Read-only and deterministic. Run from the repository root:

    python3 docs/research/definitions_paper/definition_analysis.py
"""

import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GLOSSARY = REPO_ROOT / "data" / "corpus_glossary" / "corpus_glossary.json"
REGISTRY = REPO_ROOT / "data" / "corpus_registry" / "corpus_registry.json"
OUT = Path(__file__).resolve().parent / "definition_analysis_results.json"

DIACRITICS = re.compile(r"[ً-ْٰـ]")

# Heads that name an instrument or an organ of state. A definition built
# around one of these, with no class quantifier, names a particular thing.
NAMING_HEADS = {
    "نظام", "النظام", "لائحة", "اللائحة", "قواعد", "القواعد", "تنظيم", "التنظيم",
    "وزارة", "الوزارة", "وزير", "الوزير", "هيئة", "الهيئة", "مجلس", "المجلس",
    "مركز", "المركز", "مؤسسة", "المؤسسة", "صندوق", "الصندوق", "بنك", "البنك",
    "محكمة", "المحكمة", "امانه", "الامانه", "لجنه", "اللجنه", "رئيس", "الرئيس",
    "محافظ", "المحافظ", "ادارة", "الادارة", "برنامج", "البرنامج",
    "جهة", "الجهة", "جهات", "الجهات", "سلطة", "السلطة", "لوائح", "اللوائح",
    "امانة", "الامانة", "اللجنة", "وكالة", "الوكالة",
}

# Genus words that open a class definition. Arabic statutory drafting puts
# the genus first ("any natural person who…", "a document issued by…"), so
# these count only when they head the definition; "من" and "ما" are excluded
# entirely because they are far more often relative pronouns inside an
# otherwise naming definition.
CLASS_MARKERS = {
    "كل", "اي", "جميع", "الشخص", "شخص", "مجموعه", "عمليه", "نشاط", "وثيقه",
    "اذن", "الاذن", "مبلغ", "عقد", "اتفاق", "حاله", "فعل", "تصرف", "خدمه",
    "منتج", "سلعه", "بيانات", "معلومات", "مكان", "موقع", "جهاز", "اجراء",
}
CLASS_MARKER_HEAD_WINDOW = 2


# --- Hand adjudication of the most widely shared substantive terms --------
# Lexical divergence is not semantic conflict: "الشخص" is defined by 27
# instruments in wording that varies while the meaning does not. Each of the
# twelve most widely shared substantive terms was therefore read across its
# instruments and placed in one of five classes:
#
#   harmonized       same concept, same scope, varied wording
#   instrument_local same concept, referent fixed by the enacting instrument
#                    (each sector's own licence, its own service provider)
#   indexical_missed a designated-body definition the automatic pass did not
#                    catch — reported, not silently corrected
#   homonymous       different concepts sharing a label; not a defect
#   conflicting      same concept, materially different scope — the legally
#                    significant class
ADJUDICATION = {
    "الشخص": "harmonized",
    "المرخص له": "harmonized",
    "صاحب العمل": "harmonized",
    "الترخيص": "instrument_local",
    "مقدم الخدمة": "instrument_local",
    "الجهات ذات العلاقة": "indexical_missed",
    "الجهة المشرفة": "indexical_missed",
    "التصريح": "homonymous",
    "المملكة": "conflicting",
    "المستهلك": "conflicting",
    "النشاط": "conflicting",
    "المنشأة": "conflicting",
}


def normalize(text):
    text = DIACRITICS.sub("", text or "")
    text = (text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
                .replace("ة", "ه").replace("ى", "ي").replace("ؤ", "و")
                .replace("ئ", "ي"))
    text = re.sub(r"[^؀-ۿ\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text):
    return [w for w in normalize(text).split() if len(w) > 1]


# The keyword sets above are written in ordinary orthography, while tokens()
# emits normalized forms (teh-marbuta folded to heh, hamza forms folded), so
# both sets must be normalized before any membership test. Comparing raw
# against normalized silently matches nothing for every head ending in a
# teh-marbuta ("لائحة", "وزارة", "هيئة").
NAMING_HEADS = {normalize(w) for w in NAMING_HEADS}
CLASS_MARKERS = {normalize(w) for w in CLASS_MARKERS}


def is_indexical(definition_text):
    """True when the definition names a particular instrument or organ.

    A definition is indexical when it is short, headed by an
    instrument/organ word, and carries no class marker — "the Law" defined
    as "the Agriculture Law", "the Ministry" as "the Ministry of Justice".
    A class definition ("any natural or legal person practising an economic
    activity") fails the test on both the length and the class-marker
    condition.
    """
    toks = tokens(definition_text)
    if not toks:
        return False
    if len(toks) > 12:
        return False
    if any(t in CLASS_MARKERS for t in toks[:CLASS_MARKER_HEAD_WINDOW]):
        return False
    return any(t in NAMING_HEADS for t in toks)


def jaccard(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb) if (sa or sb) else 1.0


def main():
    glossary = json.load(open(GLOSSARY, encoding="utf-8"))
    registry = json.load(open(REGISTRY, encoding="utf-8"))
    titles = {t["track_id"]: t.get("display_name_en", t["track_id"])
              for t in registry["tracks"]}
    terms = glossary["terms"]

    total_occurrences = sum(len(v) for v in terms.values())
    indexical_occ = 0
    term_kind = {}

    for term, occurrences in terms.items():
        flags = [is_indexical(o["definition_text"]) for o in occurrences]
        indexical_occ += sum(flags)
        # A term counts as indexical when most of its definitions are.
        term_kind[term] = "indexical" if sum(flags) > len(flags) / 2 else "substantive"

    kinds = Counter(term_kind.values())

    # --- multi-instrument terms, split by kind --------------------------
    multi = {t: v for t, v in terms.items()
             if len({o["track_id"] for o in v}) > 1}
    multi_by_kind = Counter(term_kind[t] for t in multi)

    # --- divergence among substantive multi-instrument terms ------------
    IDENTICAL, NEAR = 0.95, 0.75
    buckets = Counter()
    divergent_cases = []

    for term, occurrences in multi.items():
        if term_kind[term] != "substantive":
            continue
        # one definition per instrument (the first, deterministically)
        by_track = {}
        for o in occurrences:
            by_track.setdefault(o["track_id"], o)
        if len(by_track) < 2:
            continue
        sims = [jaccard(tokens(a["definition_text"]), tokens(b["definition_text"]))
                for a, b in combinations(by_track.values(), 2)]
        worst = min(sims)
        if worst >= IDENTICAL:
            buckets["identical"] += 1
        elif worst >= NEAR:
            buckets["near_identical"] += 1
        else:
            buckets["divergent"] += 1
            divergent_cases.append({
                "term": term,
                "instruments": len(by_track),
                "min_similarity": round(worst, 3),
                "definitions": [
                    {"track_id": tid,
                     "title_en": titles.get(tid, tid),
                     "definition_ar": o["definition_text"]}
                    for tid, o in sorted(by_track.items())
                ],
            })

    divergent_cases.sort(key=lambda c: (c["min_similarity"], -c["instruments"]))
    substantive_multi = sum(buckets.values())

    # --- most-defined terms, both kinds ---------------------------------
    def top_terms(kind, n=12):
        rows = [(t, len({o["track_id"] for o in v}))
                for t, v in terms.items() if term_kind[t] == kind]
        rows.sort(key=lambda r: -r[1])
        return [{"term": t, "instruments": c} for t, c in rows[:n]]

    results = {
        "corpus": {
            "terms_total": len(terms),
            "definition_occurrences_total": total_occurrences,
            "instruments_with_a_definitions_article":
                glossary.get("tracks_with_definitions_article_parsed"),
        },
        "kind_split": {
            "method": (
                "A definition is indexical when it is at most 12 content tokens, "
                "is headed by an instrument or state-organ word, and does not open "
                "with a genus word; a term is indexical when most of its definitions "
                "are. Indexical definitions name a particular instrument or body "
                "and are instrument-local by design, so they cannot disagree."
            ),
            "indexical_terms": kinds["indexical"],
            "substantive_terms": kinds["substantive"],
            "indexical_definition_occurrences": indexical_occ,
            "substantive_definition_occurrences": total_occurrences - indexical_occ,
        },
        "multi_instrument": {
            "terms_defined_by_more_than_one_instrument": len(multi),
            "of_which_indexical": multi_by_kind["indexical"],
            "of_which_substantive": multi_by_kind["substantive"],
        },
        "divergence_among_substantive": {
            "thresholds": {"identical": IDENTICAL, "near_identical": NEAR,
                           "measure": "worst pairwise Jaccard over content tokens"},
            "terms_compared": substantive_multi,
            "identical": buckets["identical"],
            "near_identical": buckets["near_identical"],
            "divergent": buckets["divergent"],
            "divergent_share": round(buckets["divergent"] / substantive_multi, 4)
            if substantive_multi else None,
        },
        "hand_adjudication_of_most_shared_substantive_terms": {
            "method": (
                "The twelve most widely shared substantive terms were read "
                "across every instrument that defines them and classified by "
                "hand. Lexical similarity measures wording; this measures "
                "meaning."
            ),
            "terms_reviewed": len(ADJUDICATION),
            "classes": dict(Counter(ADJUDICATION.values()).most_common()),
            "assignments": [
                {"term": t, "class": k,
                 "instruments": len({o["track_id"] for o in terms[t]})}
                for t, k in sorted(ADJUDICATION.items(),
                                   key=lambda kv: -len({o["track_id"]
                                                        for o in terms[kv[0]]}))
            ],
        },
        "most_defined_indexical_terms": top_terms("indexical"),
        "most_defined_substantive_terms": top_terms("substantive"),
        "divergent_cases": divergent_cases,
    }

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")

    k, m, d = results["kind_split"], results["multi_instrument"], results["divergence_among_substantive"]
    print(f"terms: {len(terms)} ({k['indexical_terms']} indexical, "
          f"{k['substantive_terms']} substantive)")
    print(f"defined by >1 instrument: {m['terms_defined_by_more_than_one_instrument']} "
          f"({m['of_which_indexical']} indexical, {m['of_which_substantive']} substantive)")
    print(f"substantive terms compared: {d['terms_compared']} -> "
          f"identical {d['identical']}, near {d['near_identical']}, "
          f"divergent {d['divergent']} ({d['divergent_share']:.1%})")
    a = results["hand_adjudication_of_most_shared_substantive_terms"]
    print(f"hand-adjudicated {a['terms_reviewed']} most-shared substantive terms: "
          + ", ".join(f"{v} {k}" for k, v in a["classes"].items()))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
