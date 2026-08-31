#!/usr/bin/env python3
"""What, by name, does the court reach for when it reaches outside a statute?

The programme has established that statute books differ in HOW MUCH
non-statutory authority accompanies them. This asks the next question, which
is about content rather than quantity: when the court reaches out, does it
reach into a recognisable, recurring set of named sources associated with that
statute?

That needs an identity, not a type. The mention layer records that a fiqh
source was invoked; it does not record WHICH. So this pass captures, for every
non-statutory mention in the court's or a party's voice:

    the matched string itself, canonicalised by explicit deterministic rules
    the nearest statutory article, at two locality definitions
    a template fingerprint of the surrounding wording

The identity universe is bounded by what `authority.py` was built to see --
five jurists, eight books, six maxim texts, a set of hadith transmission
markers -- and that bound is a finding in itself rather than a defect to hide:
a source outside that vocabulary is invisible here, so every count is a floor.

NO JUDGMENT TEXT is written to the layer. The template fingerprint is a hash
of a normalised window with numbers, names and punctuation removed; it can
tell whether two passages are the same boilerplate and cannot reconstruct
either.

    python3 companions.py
"""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from function import MARKS            # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "companion_layer.jsonl.gz"
YEARS = {1444, 1445, 1446}
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
W = 500
BLOCK = re.compile(r"[.؛\n]")

# ---- PHASE 3: canonicalisation, deterministic only.
# Each entry maps a normalised matched string to a canonical identity. Nothing
# is merged across a scholar and a book, or across two books by one scholar.
# A form not listed here keeps its own normalised string as its identity and
# is marked resolved=False, so an unrecognised variant is visible rather than
# silently folded into a neighbour.
CANON = {
    # jurists
    "ابن تيمية": ("J.IBN_TAYMIYYA", "Ibn Taymiyya"),
    "شيخ الاسلام": ("J.IBN_TAYMIYYA", "Ibn Taymiyya"),
    "ابن القيم": ("J.IBN_QAYYIM", "Ibn al-Qayyim"),
    "ابن قدامة": ("J.IBN_QUDAMA", "Ibn Qudama"),
    "محمد بن ابراهيم": ("J.MUHAMMAD_B_IBRAHIM", "Muhammad b. Ibrahim"),
    # books
    "كشاف القناع": ("B.KASHSHAF", "كشاف القناع"),
    "مجموع الفتاوى": ("B.MAJMU_FATAWA", "مجموع الفتاوى"),
    "مجموع فتاوى": ("B.MAJMU_FATAWA", "مجموع الفتاوى"),
    "منتهى الارادات": ("B.MUNTAHA", "منتهى الإرادات"),
    "الروض المربع": ("B.RAWD", "الروض المربع"),
    "مطالب اولي النهى": ("B.MATALIB", "مطالب أولي النهى"),
    "زاد المعاد": ("B.ZAD", "زاد المعاد"),
    "المغني": ("B.MUGHNI", "المغني"),
    "الانصاف": ("B.INSAF", "الإنصاف"),
    # maxims, by their own text
    "الضرر يزال": ("M.DARAR_YUZAL", "الضرر يزال"),
    "الاصل براءة الذمة": ("M.BARAA", "الأصل براءة الذمة"),
    "اليقين لا يزول بالشك": ("M.YAQIN", "اليقين لا يزول بالشك"),
    "العادة محكمة": ("M.ADA_MUHAKKAMA", "العادة محكمة"),
    "الخراج بالضمان": ("M.KHARAJ", "الخراج بالضمان"),
    "الاصل في العقود": ("M.ASL_UQUD", "الأصل في العقود"),
    # hadith transmission markers: the identity is the collection named
    "رواه البخاري": ("H.BUKHARI", "رواه البخاري"),
    "اخرجه البخاري": ("H.BUKHARI", "رواه البخاري"),
    "رواه مسلم": ("H.MUSLIM", "رواه مسلم"),
    "اخرجه مسلم": ("H.MUSLIM", "رواه مسلم"),
    "متفق عليه": ("H.MUTTAFAQ", "متفق عليه"),
    "رواه احمد": ("H.AHMAD", "رواه أحمد"),
    "اخرجه احمد": ("H.AHMAD", "رواه أحمد"),
    "رواه ابو داود": ("H.ABU_DAWUD", "رواه أبو داود"),
    "رواه الترمذي": ("H.TIRMIDHI", "رواه الترمذي"),
    "اخرجه الترمذي": ("H.TIRMIDHI", "رواه الترمذي"),
    "رواه النسائي": ("H.NASAI", "رواه النسائي"),
    "رواه ابن ماجه": ("H.IBN_MAJA", "رواه ابن ماجه"),
    "اخرجه البيهقي": ("H.BAYHAQI", "أخرجه البيهقي"),
    "اخرجه الدارقطني": ("H.DARAQUTNI", "أخرجه الدارقطني"),
}
ALIF = str.maketrans("أإآىة", "ااايه")


def norm(s):
    s = MARKS.sub("", s)
    s = re.sub(r"\s+", " ", s).strip().translate(ALIF)
    return re.sub(r"[^ء-ي ]", "", s)


# The table above is written in ordinary orthography; lookups arrive
# orthographically normalised (أإآ->ا, ى->ي, ة->ه). Normalising the keys by
# the same function is the whole of the alias handling: two strings merge only
# when they are IDENTICAL after that normalisation. Nothing is merged on
# similarity, and the share of resolutions that needed it is reported.
CANON_N = {norm(k): v for k, v in CANON.items()}
assert len(CANON_N) == len(CANON), "two canonical keys collide after norm"

# A prophetic report whose collection is not named. «صلى الله عليه وسلم» and
# the ligature ﷺ are the formula that follows a mention of the Prophet; they
# identify no collection and are not evidence that one was consulted. They are
# kept as an identity of their own -- untraceable hadith -- rather than
# guessed into a collection. PHASE 29 counts them.
UNTRACED_HADITH = {norm(x) for x in (
    "صلى الله عليه وسلم", "عليه الصلاة والسلام", "حديث النبي",
    "حديث حسن", "حديث صحيح", "في الحديث الصحيح")}
GENERIC_RULES = ("fiqh.unattributed", "principle.settled", "custom.trade",
                 "maxim.named", "quran.citation", "discretion.named")


def canonical(rule, raw):
    """-> (identity, label, resolved, merged_by_alias_handling)"""
    n = norm(raw)
    if raw and not n and "\uFDFA" in raw:
        # ﷺ is a single ligature character and survives no letter filter
        n = norm("صلى الله عليه وسلم")
    if n in UNTRACED_HADITH:
        return "GENERIC.hadith.untraced", "hadith, no collection named", False, False
    if n in CANON_N:
        cid, label = CANON_N[n]
        return cid, label, True, n not in CANON
    # the generic rules name no source at all; they are their own identity
    if rule in GENERIC_RULES:
        return f"GENERIC.{rule}", rule, False, False
    return f"RAW.{n[:40]}", n[:40], False, False


def fingerprint(text, a, b):
    """A hash of the surrounding wording, stripped of anything specific."""
    w = norm(text[max(0, a - 90):b + 90])
    w = re.sub(r"\b\w{1,2}\b", " ", w)
    return hashlib.sha1(re.sub(r"\s+", " ", w).encode()).hexdigest()[:12]


def main():
    index, order = M.build(REGISTRY)
    n = docs = 0
    with gzip.open(OUT, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": {
            "years": sorted(YEARS), "window": W,
            "fields": "j y city ct voice type rule cid label resolved "
                      "merged instBlock artBlock instW artW tmpl",
            "note": "one row per non-statutory authority mention. NO judgment "
                    "text: tmpl is a hash of a normalised window and cannot be "
                    "inverted. instBlock/artBlock is the nearest statutory "
                    "citation in the same sentence-like block; instW/artW the "
                    "nearest within +-500 characters. Proximity is "
                    "co-occurrence, not legal dependence.",
            "identityUniverse": "bounded by authority.py's vocabulary: an "
                                "authority it cannot name is absent here, so "
                                "every count is a floor"}}, ensure_ascii=False)
                 + "\n")
        for rec in judgments():
            y = year_of(rec)
            if y not in YEARS:
                continue
            text, s = rec["text"], rec.get("sections") or {}
            spans = V.segments(text, s)
            rea = [(a, b) for a, b, v in spans if v == "reasoning"]
            if not rea:
                continue
            docs += 1
            quotes = A.quoted_spans(text) if hasattr(A, "quoted_spans") else []
            ments = A.mentions(text, s, index, order)
            stat = [(m["at"], m["instrument"], m["article"]) for m in ments
                    if m["type"] == "statute" and not m.get("inQuote")
                    and m.get("instrument")]
            cuts = sorted({c for a, b in rea
                           for c in [a] + [x.end() + a for x in
                                           BLOCK.finditer(text[a:b])] + [b]})

            def blk(p):
                lo = 0
                for c in cuts:
                    if c <= p:
                        lo = c
                    else:
                        return (lo, c)
                return (lo, len(text))

            for m in ments:
                if m["type"] not in NONSTATUTE or m.get("inQuote"):
                    continue
                voice = A.voice(m)
                if voice not in ("court_reasoning", "party_argument",
                                 "recital"):
                    continue
                at = m["at"]
                # recover the matched string for this rule at this offset
                raw = ""
                for t, rid, pat, _ in A.COMPILED:
                    if rid != m["rule"]:
                        continue
                    mm = pat.match(text, at) or pat.search(text, at, at + 60)
                    if mm:
                        raw = mm.group(0)
                    break
                cid, label, resolved, merged = canonical(m["rule"], raw)
                mb = blk(at)
                ib = [(p, i, ar) for p, i, ar in stat if mb[0] <= p < mb[1]]
                iw = [(p, i, ar) for p, i, ar in stat if abs(p - at) <= W]
                nb = min(ib, key=lambda x: abs(x[0] - at)) if ib else None
                nw = min(iw, key=lambda x: abs(x[0] - at)) if iw else None
                fh.write(json.dumps({
                    "j": rec["id"], "y": y,
                    "city": rec.get("city") or "", "ct": rec.get("court_type") or "",
                    "voice": ("court" if voice == "court_reasoning" else "party"),
                    "type": m["type"], "rule": m["rule"],
                    "cid": cid, "label": label, "resolved": resolved,
                    "merged": merged,
                    "instBlock": nb[1] if nb else None,
                    "artBlock": nb[2] if nb else None,
                    "instW": nw[1] if nw else None,
                    "artW": nw[2] if nw else None,
                    "tmpl": fingerprint(text, at, at + max(1, len(raw))),
                }, ensure_ascii=False) + "\n")
                n += 1
    print(f"{n:,} non-statutory mentions from {docs:,} judgments -> "
          f"{OUT.name} ({OUT.stat().st_size/1e6:.1f} MB gzipped)")


if __name__ == "__main__":
    main()
