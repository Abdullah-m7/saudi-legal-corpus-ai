#!/usr/bin/env python3
"""Instrument identity is the strongest predictor in this programme. What is it?

Three functional taxonomies have now lost to it out of sample --
procedural/substantive, statutory completeness, institutional-operation
against dispute-decision. That is a result about the taxonomies. It is not a
result about statute books, because "which code the article is in" is a label,
not an explanation, and a label that predicts is a phenomenon that needs one.

This builds the instrument as a unit of analysis: one row per statute book,
with its OUTCOMES (what appears beside it when a court cites it) kept strictly
apart from its PREDICTORS (properties of its enacted text and of what kind of
law it is). No predictor column is derived from an outcome column, and the
outcomes are computed first and frozen so that the features cannot be tuned
against them.

Sections:

    ecology       the frozen baseline: what each code draws beside it
    features      article count, length, referral language, granularity,
                  commencement, domain, legislative function
    hypotheses    H1 age, H2 domain, H3 granularity, H4 explicit referral,
                  H5 institution-creation, H6 fiqh-dense subject matter
    composition   the authority vector per code, and the distances between
    variance      within-code against between-code, and against year,
                  function and voice
    voices        the court's ecology for a code against the bar's
    stability     year by year, inside the contemporary window
    risk          code-specific statute-only retrieval risk
    traceability  what share of each code's supplementary authority names a
                  source that can be followed

    python3 instruments.py
"""
import collections
import gzip
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from function import articles, MARKS          # noqa: E402
from map import wilson                        # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
FUNC = HERE / "adjudicative_function_gold.json"
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "instruments_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
KINDS = {"named_fiqh": ("fiqh_source",), "maxim": ("legal_maxim",),
         "scripture": ("quran", "hadith"),
         "judicial_principle": ("judicial_principle",),
         "custom": ("custom",)}
YEARS = (1442, 1443, 1444, 1445, 1446)
RECENT = {1444, 1445, 1446}
MIN_JUDGMENTS = 80

# Hand fields, each defensible from the registry note or the statute's own
# title and structure. Nothing here is guessed from behaviour.
DOMAIN = {
    "commercial_courts_law": "procedure",
    "commercial_courts_implementing_regulation": "procedure",
    "sharia_procedure_law": "procedure",
    "evidence_law": "evidence",
    "civil_transactions_law": "obligations",
    "companies_law": "corporate",
    "bankruptcy_law": "insolvency",
    "arbitration_law": "arbitration",
    "law_practice_law": "professional_regulation",
    "enforcement_law": "enforcement",
}
# "does the statute mainly codify a field the fiqh had long governed, or
# mainly create an institution or a procedure?" Assigned from the subject
# matter named in the registry note and the statute's own chapter headings.
RELATION = {
    "evidence_law": "codifies_a_fiqh_field",
    "civil_transactions_law": "codifies_a_fiqh_field",
    "commercial_courts_law": "creates_procedure_or_institution",
    "commercial_courts_implementing_regulation": "creates_procedure_or_institution",
    "sharia_procedure_law": "creates_procedure_or_institution",
    "companies_law": "creates_procedure_or_institution",
    "bankruptcy_law": "creates_procedure_or_institution",
    "arbitration_law": "creates_procedure_or_institution",
    "law_practice_law": "creates_procedure_or_institution",
    "enforcement_law": "mixed",
}
HIJRI = re.compile(r"(?:دated|dated)\s*(\d{1,2})/(\d{1,2})/(\d{4})H|"
                   r"issued\s*(\d{1,2})/(\d{1,2})/(\d{4})H")

DEFN = re.compile(r"يقصد ب|هي التي|هو الذي|في تطبيق أحكام|تسري أحكام")
XREF = re.compile(r"المادة\s*\(|المادتين|المواد\s*\(|من النظام|من اللائحة")
SHARIA = re.compile(r"الشريعة|أحكام الشرع|الفقه|شرعا|شرعي")
CUSTOM = re.compile(r"العرف|العادة المستقرة|المتعارف")
DISCRETION = re.compile(r"يجوز|للمحكمة أن|فللمحكمة|ما تراه|تقدير|السلطة التقديرية")
OPEN = re.compile(r"مناسب|ملائم|معقول|جسامة|عذر|مسوغ|ضرورة|الحاجة|"
                  r"عند الاقتضاء|بحسب الأحوال|جوهري|كافي|كافية|الظاهر")
DELEG = re.compile(r"تحدد اللائحة|تنظم اللائحة|وفق ما تحدده|وفقا لما تحدده")
SUBPARA = re.compile(r"[أ-ي]\s*-\s|[١-٩]\s*[-.]|\([أ-ي]\)")


def commencement(track):
    m = HIJRI.search(track.get("notes") or "")
    if not m:
        return None
    g = [x for x in m.groups() if x]
    return f"{int(g[0]):02d}/{int(g[1]):02d}/{g[2]}"


def features():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    meta = {t["track_id"]: t for t in tracks if t.get("track_id")}
    A = articles()
    by = collections.defaultdict(list)
    for (inst, num), rec in A.items():
        t = MARKS.sub("", rec["text"])
        if t.strip():
            by[inst].append(t)
    out = {}
    for inst, texts in by.items():
        n = len(texts)
        lens = sorted(len(t) for t in texts)
        words = sorted(len(t.split()) for t in texts)
        d = commencement(meta.get(inst, {}))
        yr = int(d.split("/")[-1]) if d else None
        out[inst] = {
            "articlesInRegistry": n,
            "medianArticleChars": lens[n // 2],
            "medianArticleWords": words[n // 2],
            "p90ArticleWords": words[9 * n // 10],
            "definitionSharePct": round(
                100 * sum(bool(DEFN.search(t)) for t in texts) / n, 1),
            "crossRefPerArticle": round(
                sum(len(XREF.findall(t)) for t in texts) / n, 2),
            "shariaReferenceSharePct": round(
                100 * sum(bool(SHARIA.search(t)) for t in texts) / n, 1),
            "customReferenceSharePct": round(
                100 * sum(bool(CUSTOM.search(t)) for t in texts) / n, 1),
            "discretionarySharePct": round(
                100 * sum(bool(DISCRETION.search(t)) for t in texts) / n, 1),
            "openTexturedSharePct": round(
                100 * sum(bool(OPEN.search(t)) for t in texts) / n, 1),
            "delegationSharePct": round(
                100 * sum(bool(DELEG.search(t)) for t in texts) / n, 1),
            "subparagraphsPerArticle": round(
                sum(len(SUBPARA.findall(t)) for t in texts) / n, 2),
            "commencement": d,
            "commencementYear": yr,
            "yearsObservedTo1446": (1446 - yr) if yr else None,
            "domain": DOMAIN.get(inst),
            "codificationRelation": RELATION.get(inst),
        }
    return out


def scan():
    docs = collections.defaultdict(
        lambda: {"c": collections.Counter(), "ca": set(),
                 "ps": set(), "pw": set(), "pc": collections.Counter(),
                 "y": 0, "rules": collections.Counter()})
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            d = docs[r["j"]]
            d["y"] = r["y"]
            a = ((r["inst"], r["art"]) if r.get("inst")
                 and r.get("art") is not None else None)
            if r["role"] == "court_reasoning":
                d["c"][r["t"]] += 1
                d["rules"][(r["t"], r["r"])] += 1
                if a:
                    d["ca"].add(a)
            elif r["role"] in ("party_argument", "recital"):
                d["pc"][r["t"]] += 1
                if a:
                    d["pw"].add(a)
                    if r["role"] == "party_argument":
                        d["ps"].add(a)
    return docs


NAMED = {"fiqh.book", "fiqh.jurist", "maxim.named", "quran.citation",
         "hadith.citation"}


def ecology(docs, inst, years, voice="court"):
    ckey, akey = (("c", "ca") if voice == "court"
                  else ("pc", "pw") if voice == "party_wide" else ("pc", "ps"))
    n = hyb = 0
    kinds = collections.Counter()
    arts = collections.Counter()
    named = generic = 0
    for d in docs.values():
        if d["y"] not in years:
            continue
        cited = {a for a in d[akey] if a[0] == inst}
        if not cited:
            continue
        n += 1
        for a in cited:
            arts[a] += 1
        types = d[ckey]
        if any(types[t] for t in NONSTATUTE):
            hyb += 1
        for name, ts in KINDS.items():
            if any(types[t] for t in ts):
                kinds[name] += 1
        if voice == "court":
            for (t, rule), v in d["rules"].items():
                if t in NONSTATUTE:
                    if rule in NAMED:
                        named += v
                    else:
                        generic += v
    if not n:
        return None
    tot = sum(arts.values())
    top10 = sum(v for _, v in arts.most_common(10))
    row = {"judgments": n,
           "citations": tot,
           "distinctArticles": len(arts),
           "statuteOnlyPct": round(100 * (n - hyb) / n, 1),
           "hybridPct": round(100 * hyb / n, 1),
           "hybridCI": wilson(hyb, n),
           **{k: round(100 * kinds[k] / n, 1) for k in KINDS},
           "top10ConcentrationPct": round(100 * top10 / tot, 1)}
    if voice == "court" and (named + generic):
        row["supplementaryNamedSourcePct"] = round(
            100 * named / (named + generic), 1)
        row["supplementaryMentions"] = named + generic
    return row


def main():
    docs = scan()
    feats = features()
    counts = collections.Counter()
    for d in docs.values():
        if d["y"] in RECENT:
            for a in d["ca"]:
                counts[a[0]] += 1
    insts = [i for i, c in counts.most_common() if c >= MIN_JUDGMENTS]

    res = {"window": sorted(RECENT), "minJudgments": MIN_JUDGMENTS,
           "instruments": insts, "ecology": {}, "features": {},
           "voices": {}, "stability": {}}
    for i in insts:
        res["ecology"][i] = ecology(docs, i, RECENT)
        res["features"][i] = feats.get(i, {})
        res["voices"][i] = {
            "court": res["ecology"][i],
            "party_strict": ecology(docs, i, RECENT, "party_strict"),
            "party_wide": ecology(docs, i, RECENT, "party_wide")}
        res["stability"][i] = {
            str(y): ecology(docs, i, {y}) for y in YEARS
            if ecology(docs, i, {y}) and ecology(docs, i, {y})["judgments"] >= 40}

    # PHASE 7 --- the composition vector, and the distance between codes.
    vec = {}
    for i in insts:
        e = res["ecology"][i]
        v = {k: e[k] for k in KINDS}
        v["statute_only"] = e["statuteOnlyPct"]
        s = sum(v.values()) or 1
        vec[i] = {k: round(x / s, 4) for k, x in v.items()}
    res["compositionVectors"] = vec
    dist = {}
    for a in insts:
        for b in insts:
            if a >= b:
                continue
            # total variation distance between the two profiles: half the sum
            # of absolute differences. Interpretable, and no clustering.
            dist[f"{a} | {b}"] = round(
                sum(abs(vec[a][k] - vec[b][k]) for k in vec[a]) / 2, 3)
    res["profileDistance"] = dict(sorted(dist.items(), key=lambda kv: -kv[1]))

    # PHASE 8 and 16 --- variance decomposition on article-level rates.
    fn = json.loads(FUNC.read_text(encoding="utf-8"))["labels"]
    an = collections.Counter()
    ah = collections.Counter()
    for d in docs.values():
        mixed = any(d["c"][t] for t in NONSTATUTE)
        for a in d["ca"]:
            an[a] += 1
            if mixed:
                ah[a] += 1
    rates = {a: 100 * ah[a] / an[a] for a in an
             if an[a] >= 30 and a[0] in insts}
    grand = statistics.mean(rates.values())
    tss = sum((v - grand) ** 2 for v in rates.values())

    def decomp(assign, label):
        g = collections.defaultdict(list)
        for a, v in rates.items():
            g[assign(a)].append(v)
        bss = sum(len(x) * (statistics.mean(x) - grand) ** 2
                  for x in g.values())
        return {"grouping": label, "groups": len(g),
                "betweenSharePct": round(100 * bss / tss, 1),
                "withinSharePct": round(100 * (tss - bss) / tss, 1)}

    res["varianceDecomposition"] = {
        "articles": len(rates), "grandMeanPct": round(grand, 1),
        "byInstrument": decomp(lambda a: a[0], "instrument"),
        "byFunctionClass": decomp(
            lambda a: (fn.get(f"{a[0]}:{a[1]}") or {}).get("function",
                                                           "unlabelled"),
            "adjudicative function"),
        "byCitationDecile": decomp(
            lambda a: min(9, an[a] // 100), "citation frequency band"),
        "perInstrument": {
            i: {"articles": sum(1 for a in rates if a[0] == i),
                "meanPct": round(statistics.mean(
                    [v for a, v in rates.items() if a[0] == i]), 1),
                "sdPct": round(statistics.pstdev(
                    [v for a, v in rates.items() if a[0] == i]), 1),
                "minPct": round(min(v for a, v in rates.items() if a[0] == i), 1),
                "maxPct": round(max(v for a, v in rates.items() if a[0] == i), 1)}
            for i in insts if sum(1 for a in rates if a[0] == i) >= 3},
    }

    # PHASE 19 --- code-specific statute-only retrieval risk is the hybrid
    # rate under another name, and is stated as such rather than rebranded.
    res["retrievalRisk"] = {
        i: {"statuteOnlyRetrievalMissesPct": res["ecology"][i]["hybridPct"],
            "ci": res["ecology"][i]["hybridCI"],
            "judgments": res["ecology"][i]["judgments"]}
        for i in insts}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    w = 42
    print(f"{'instrument':<{w}}{'judg':>7}{'hybrid':>8}{'fiqh':>7}{'maxim':>7}"
          f"{'script':>8}{'princ':>7}{'custom':>7}{'named src':>11}")
    for i in insts:
        e = res["ecology"][i]
        print(f"  {i[:w-2]:<{w-2}}{e['judgments']:>7,}{e['hybridPct']:>7.1f}%"
              f"{e['named_fiqh']:>6.1f}%{e['maxim']:>6.1f}%"
              f"{e['scripture']:>7.1f}%{e['judicial_principle']:>6.1f}%"
              f"{e['custom']:>6.1f}%"
              f"{e.get('supplementaryNamedSourcePct', float('nan')):>10.1f}%")
    print(f"\n{'instrument':<{w}}{'arts':>6}{'med words':>11}{'xref/art':>10}"
          f"{'sharia%':>9}{'custom%':>9}{'discr%':>8}{'open%':>7}{'subpara':>9}"
          f"{'since':>7}")
    for i in insts:
        f = res["features"][i]
        if not f:
            continue
        print(f"  {i[:w-2]:<{w-2}}{f['articlesInRegistry']:>6}"
              f"{f['medianArticleWords']:>11}{f['crossRefPerArticle']:>10}"
              f"{f['shariaReferenceSharePct']:>8.1f}%"
              f"{f['customReferenceSharePct']:>8.1f}%"
              f"{f['discretionarySharePct']:>7.1f}%"
              f"{f['openTexturedSharePct']:>6.1f}%"
              f"{f['subparagraphsPerArticle']:>9}"
              f"{str(f['commencementYear']):>7}")
    v = res["varianceDecomposition"]
    print(f"\nvariance in the article-level rate ({v['articles']} articles):")
    for k in ("byInstrument", "byFunctionClass", "byCitationDecile"):
        d = v[k]
        print(f"  {d['grouping']:<24}{d['groups']:>3} groups   between "
              f"{d['betweenSharePct']:>5.1f}%   within {d['withinSharePct']:>5.1f}%")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
