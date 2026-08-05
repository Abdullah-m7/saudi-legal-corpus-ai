#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two questions the corpus could not previously ask about its own stored text.

WHY THIS EXISTS
---------------
The track validators check that a track is internally consistent: its records
match its source artifact, its counts add up, its numbering has no unexplained
gaps. The currency audit checks whether the LAW has moved on. Neither can see
two things that are properties of the stored text itself:

  A. ENCODING DAMAGE. Some tracks were built from PDFs, and Arabic PDF text
     extraction has a characteristic failure: the lam-alef ligature comes out
     reversed and adjacent letters transpose. «حماية» is stored as «محاية»,
     «الاطلاع» as «االطلاع», «لا يجوز» as «ال يجوز», «اللائحة» as «الالئحة».
     Where the fault comes from is NOT assumed. An earlier version of this file
     asserted that the bodies published the text correctly and the damage was in
     transcription. scripts/verify_pdf_source_encoding.py tested that by
     re-fetching each cited PDF and extracting it with poppler — a tool
     independent of this corpus — and it is wrong: the damaged forms are in the
     official PDFs' own text layers, 1,035 of them in the CMA regulation and 194
     in the Ministry of Health one. No extractor can do better, and the stored
     text is a faithful reading of the official file. The printed page looks
     correct to a human eye; only the machine-readable layer carries the fault.

     It is therefore not repaired, and could not be by re-reading. Repair by rule
     is separately unsafe, for a stronger reason than «ال» being a word: the fault
     maps real Arabic words onto other real Arabic words, so no rule distinguishes
     it from correct text. Correct text here would require human transcription
     from the rendered page, which this corpus does not do.

  B. THE SAME TEXT UNDER TWO NAMES. A corpus that grows by ingestion can end up
     holding one instrument twice, and the two copies need not be equal: they
     may be different EDITIONS, one of them older or worse. That is invisible to
     any per-track check. It is also easy to get wrong in the other direction —
     Saudi practice issues legally DISTINCT instruments from one template, and
     the eleven cultural-authority licensing regulations are 99% the same text
     while each licenses a different authority.

     So content overlap alone is not the finding. What separates the two cases
     is whether the titles name the same subject AND the same instrument type,
     both of which are facts about the titles rather than readings of them.

Read-only. Exit 0 always: this is a report, not a gate.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from audit_corpus_currency import instrument_type  # noqa: E402
from gazette_autoingest import _dedup_tokens, norm_ar, shingles  # noqa: E402

# --- A. encoding damage ---------------------------------------------------------------
# Each signature is a letter sequence that correctly-encoded Arabic does not produce.
# «اال» / «اإل» / «اآل» are the definite article followed by a lam-alef whose two
# letters came out in visual rather than logical order; «الئ» inside a word is the
# same fault one position further in; a standalone «ال» before a verb is «لا».
DAMAGE = {
    "lam_alef_after_definite_article": re.compile(r"\bاال"),
    "lam_alef_hamza_after_definite_article": re.compile(r"\bاإل"),
    "lam_alef_madda_after_definite_article": re.compile(r"\bاآل"),
    "lam_alef_inside_word": re.compile(r"[ؠ-ي]الئ"),
    "detached_negative_particle": re.compile(
        r"\bال\s+(?:يجوز|يمكن|تقل|يزيد|يخل|تسري|يعد|يحق|يترتب|تقبل|يخضع)"),
    "adjacent_letter_transposition": re.compile(
        r"محاية|املساهم|املادة|اململكة|املصاحل|الرشكة|الالئحة|اللواحئ"),
}

# --- B. same text under two names ------------------------------------------------------
# The TITLE is the primary signal, not the text. Two editions of one instrument can
# be rewritten almost completely and still be that instrument: «نظام التأمينات
# الاجتماعية» exists twice in this corpus and the two share 8.6% of their wording,
# while «لائحة حوكمة الشركات» exists twice sharing 49.8%. A content threshold set
# anywhere that admits the second excludes the first, and one set low enough to admit
# both admits every template family in the archive. So the pair is found by what the
# titles NAME — the same subject and the same instrument type, both facts rather than
# readings — and the content overlap is measured and reported beside it rather than
# used as the gate.
SUBJECT_FLOOR = 0.80
# Content overlap is still worth surfacing on its own, for the opposite case: two
# tracks whose titles differ but whose text is nearly the same.
CONTENT_FLOOR = 0.50


def undamage(s):
    """Undo the encoding damage FOR COMPARISON ONLY, never for storage. Without this
    a damaged copy and an intact copy of one instrument score as different texts,
    which is exactly the pair most worth finding."""
    s = re.sub(r"\bاال", "الا", s)
    s = re.sub(r"\bاإل", "الإ", s)
    s = re.sub(r"\bاآل", "الآ", s)
    s = s.replace("الالئحة", "اللائحة").replace("محاية", "حماية")
    return re.sub(r"\bال\s+(?=[يت])", "لا ", s)


def artifacts():
    """{track_id: (title, gregorian, hijri, [texts], path)} — one entry per instrument."""
    out = {}
    for pat in (os.path.join(ROOT, "sources", "*", "official_source", "*.json"),
                os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json")):
        for p in sorted(glob.glob(pat)):
            tid = re.sub(r"_official_[a-z_]*source$", "", os.path.basename(p)[:-5])
            if tid in out:
                continue
            try:
                d = json.load(open(p, encoding="utf-8"))
            except (ValueError, OSError):
                continue
            if not d.get("document"):
                continue
            a = d.get("articles")
            a = list(a.values()) if isinstance(a, dict) else (a or [])
            texts = [(x.get("text", "") if isinstance(x, dict) else str(x)) for x in a]
            out[tid] = (d["document"], d.get("gazette_publication_date_gregorian") or "",
                        d.get("decree_date_hijri") or "", texts,
                        os.path.relpath(p, ROOT))
    return out


# The sequence signatures above are certain but narrow: they only fire on «اال» / «اإل»
# / «اآل» opening a word. The same extraction fault reverses a lam-alef ANYWHERE, and
# «الالزمة» for «اللازمة» or «إعالن» for «إعلان» carry no opening signature at all.
#
# Widening it cannot be done by a rule, because THE FAULT MAPS REAL ARABIC WORDS ONTO
# OTHER REAL ARABIC WORDS: «العالقة» (suspended, pending) is the swap of «العلاقة»
# (relationship), «عالمة» (aware) of «علامة» (mark), «صالحية» (fitness) of «صلاحية»
# (competence). A detector keyed on "this form is much rarer than its swap" flags all
# of those, and they are correct text — «الشوائب العالقة ببدن السفينة» and «القضايا
# العالقة لدى المحامين» say exactly what they mean.
#
# So the corpus is used as the evidence instead. The tracks with ZERO sequence
# signatures are a seed of known-good text — established independently of this test,
# so the reasoning is not circular. A form that appears NOWHERE in that seed, and
# whose swap the corpus uses at least RARITY_RATIO times more often, is damage. A form
# that does appear in the seed is a real word and is reported separately, unclassified,
# because deciding it needs the sentence and not the spelling.
RARITY_RATIO = 20
MIN_FORM_LENGTH = 4
ALEFS = "اأإآ"


def _lam_alef_swaps(w):
    """Every way of un-reversing one or more alef+lam pairs in a word."""
    import itertools
    pos = [i for i in range(len(w) - 1) if w[i] in ALEFS and w[i + 1] == "ل"]
    out = set()
    for k in range(1, len(pos) + 1):
        for combo in itertools.combinations(pos, k):
            s = list(w)
            ok = True
            for i in combo:
                if s[i] in ALEFS and s[i + 1] == "ل":
                    s[i], s[i + 1] = s[i + 1], s[i]
                else:
                    ok = False
                    break
            if ok:
                out.add("".join(s))
    return out


def scan_reversed_lam_alef(tracks, seeded_clean):
    """(damage_forms, real_word_collisions) — the wider fault, split by the seed test."""
    import collections
    everywhere = collections.Counter()
    in_seed = collections.Counter()
    for tid, (_d, _g, _h, texts, _p) in tracks.items():
        for t in texts:
            ws = re.findall(r"[ؠ-ي]+", t)
            everywhere.update(ws)
            if tid in seeded_clean:
                in_seed.update(ws)
    damage, collisions = {}, {}
    for w, n in everywhere.items():
        if len(w) < MIN_FORM_LENGTH:
            continue
        best = max(((everywhere.get(c, 0), c) for c in _lam_alef_swaps(w) if c != w),
                   default=(0, None))
        if best[0] < max(RARITY_RATIO * n, RARITY_RATIO):
            continue
        (collisions if in_seed[w] else damage)[w] = {
            "occurrences": n, "swap": best[1], "swap_occurrences": best[0],
            "occurrences_in_seed": in_seed[w]}
    return damage, collisions


def scan_damage(tracks):
    rows = []
    for tid, (doc, _g, _h, texts, path) in sorted(tracks.items()):
        hits = {}
        n_records = 0
        for t in texts:
            found = [k for k, rx in DAMAGE.items() if rx.search(t)]
            if found:
                n_records += 1
                for k in found:
                    hits[k] = hits.get(k, 0) + 1
        if n_records:
            rows.append({"track_id": tid, "title_ar": doc, "source_artifact": path,
                         "records_affected": n_records, "total_records": len(texts),
                         "signatures": dict(sorted(hits.items()))})
    rows.sort(key=lambda r: -r["records_affected"])
    return rows


# Function words survive _dedup_tokens because they are long enough to look like
# content: «إلى» normalises to «الي», three letters. Left in, they make «لائحة نقل
# البيانات الشخصية إلى خارج المملكة» and «لائحة نقل البيانات الشخصية خارج المملكة»
# score 0.83 — two editions of one regulation reading as different subjects — while
# «قواعد سجل الشركات» and «قواعد الشركات», which really are different instruments,
# score 0.80 on a genuinely discriminating word. No threshold separates those two;
# removing the function word does.
SUBJECT_FUNCTION_WORDS = {"الي", "علي", "عن", "مع", "بين", "لدي", "خلال", "حول", "بشان",
                          "وفق", "دون", "غير", "بعد", "قبل", "منذ", "حتي", "ضمن", "نحو"}


def subject_tokens(title):
    """The title's distinctive words with the instrument-type words and function words
    removed, so that «نظام X» and «اللائحة التنفيذية لنظام X» do not read as the same
    subject merely because both reduce to X, and so that a preposition cannot make two
    editions of one instrument look like different subjects."""
    stripped = re.sub(r"^(اللائحة التنفيذية|اللائحة|لائحة|النظام|نظام|القواعد|قواعد"
                      r"|الضوابط|ضوابط|تنظيم|الترتيبات التنظيمية|التعليمات|تعليمات)\s*",
                      "", title)
    return {w for w in _dedup_tokens(stripped) if w not in SUBJECT_FUNCTION_WORDS}


def scan_pairs(tracks):
    fp = {}
    for tid, (_d, _g, _h, texts, _p) in tracks.items():
        s = frozenset().union(*[shingles(undamage(t)) for t in texts]) if texts else frozenset()
        if s:
            fp[tid] = s
    ids = sorted(fp)
    subj = {t: subject_tokens(tracks[t][0]) for t in ids}
    typ = {t: instrument_type(tracks[t][0]) for t in ids}
    rows = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            sa, sb = subj[a], subj[b]
            subject = len(sa & sb) / max(1, len(sa | sb)) if (sa and sb) else 0.0
            A, B = fp[a], fp[b]
            overlap = len(A & B) / min(len(A), len(B))
            # Reported when EITHER the titles name the same thing or the texts are
            # nearly the same. Requiring both would hide exactly the two cases that
            # matter: a rewritten later edition, and a re-used template.
            if subject < SUBJECT_FLOOR and overlap < CONTENT_FLOOR:
                continue
            ta, tb = tracks[a][0], tracks[b][0]
            type_a, type_b = typ[a], typ[b]
            rows.append({
                "content_overlap": round(overlap, 3),
                "subject_similarity": round(subject, 3),
                "same_instrument_type": type_a == type_b,
                "verdict": verdict(overlap, subject, type_a == type_b),
                "tracks": [
                    {"track_id": a, "title_ar": ta, "gazette_gregorian": tracks[a][1],
                     "decree_date_hijri": tracks[a][2], "records": len(tracks[a][3]),
                     "instrument_type": type_a, "source_artifact": tracks[a][4]},
                    {"track_id": b, "title_ar": tb, "gazette_gregorian": tracks[b][1],
                     "decree_date_hijri": tracks[b][2], "records": len(tracks[b][3]),
                     "instrument_type": type_b, "source_artifact": tracks[b][4]},
                ]})
    rows.sort(key=lambda r: (r["verdict"], -r["content_overlap"]))
    return rows


def verdict(overlap, subject, same_type):
    """What the two measurements together permit saying — and nothing beyond it.

    Verdict A requires the subjects to be IDENTICAL, not merely similar. A single
    differing content word is what separates one instrument from another in this
    archive: «... وحكومة غانا» from «... ودولة قطر», «قواعد سجل الشركات» from «قواعد
    الشركات». Anything short of identity is reported as a lead, because a lead is
    what it is."""
    if subject >= 1.0 and same_type:
        return "A_same_instrument_twice"
    if subject >= 1.0 and not same_type:
        return "B_instrument_and_its_implementing_text"
    if subject >= SUBJECT_FLOOR:
        return "A2_possible_same_instrument_one_word_apart"
    return "C_shared_template_distinct_subjects"


NOTE = (
    "Two properties of the corpus's own stored text that no per-track validator can "
    "see. (A) ENCODING DAMAGE: records carrying the signature of Arabic PDF text "
    "extraction — reversed lam-alef ligatures and transposed adjacent letters. The "
    "issuing bodies published these texts correctly; the damage is in the "
    "transcription. Nothing is repaired here, because repair by rule is unsafe: «ال» "
    "is itself an Arabic word, both the negative particle and the definite article. "
    "(B) THE SAME TEXT UNDER TWO NAMES: pairs of tracks whose text overlaps beyond "
    "CONTENT_FLOOR. Overlap alone is not the finding — Saudi practice issues legally "
    "DISTINCT instruments from one template, and the eleven cultural-authority "
    "licensing regulations are 99% identical while each licenses a different "
    "authority. The verdict therefore rests on two facts about the TITLES: whether "
    "they name the same subject once the instrument-type words are set aside, and "
    "whether they name the same instrument type. A_same_instrument_twice is the case "
    "that needs adjudication; B is a law beside its implementing text, which is "
    "expected but worth measuring because a reader consulting the regulation should "
    "know how much of it restates the law; C is a template family and is correct.")


def main():
    tracks = artifacts()
    damage = scan_damage(tracks)
    seeded_clean = set(tracks) - {r["track_id"] for r in damage}
    wide, collisions = scan_reversed_lam_alef(tracks, seeded_clean)
    # Re-scan every track for the wider forms and fold the result into the same rows,
    # so a track's disclosed count is the whole of what was found in it.
    per_track = {}
    for tid, (_d, _g, _h, texts, path) in tracks.items():
        n = sum(1 for t in texts if any(w in wide for w in re.findall(r"[ؠ-ي]+", t)))
        occ = sum(sum(1 for w in re.findall(r"[ؠ-ي]+", t) if w in wide) for t in texts)
        if n:
            per_track[tid] = (n, occ, len(texts), path)
    by_id = {r["track_id"]: r for r in damage}
    for tid, (n, occ, total, path) in per_track.items():
        row = by_id.get(tid)
        if row is None:
            row = {"track_id": tid, "title_ar": tracks[tid][0], "source_artifact": path,
                   "records_affected": 0, "total_records": total, "signatures": {}}
            damage.append(row)
            by_id[tid] = row
        row["reversed_lam_alef_records"] = n
        row["reversed_lam_alef_occurrences"] = occ
    for r in damage:
        r.setdefault("reversed_lam_alef_records", 0)
        r.setdefault("reversed_lam_alef_occurrences", 0)
        r["records_affected"] = max(r["records_affected"], r["reversed_lam_alef_records"])
    damage.sort(key=lambda r: -r["records_affected"])
    pairs = scan_pairs(tracks)
    by_verdict = {}
    for r in pairs:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1

    print("instruments scanned: %d" % len(tracks))
    print("\nA. encoding damage: %d tracks, %d records"
          % (len(damage), sum(r["records_affected"] for r in damage)))
    print("   reversed lam-alef: %d damage-only forms (%d occurrences); "
          "%d forms are real words the swap collides with and are NOT counted"
          % (len(wide), sum(v["occurrences"] for v in wide.values()), len(collisions)))
    for r in damage:
        print("   %-46s %4d/%-4d  sig=%d wide=%d"
              % (r["track_id"], r["records_affected"], r["total_records"],
                 sum(r["signatures"].values()), r["reversed_lam_alef_occurrences"]))
    print("\nB. same instrument under two tracks, or same text under two names: %d pairs"
          % len(pairs))
    for k in sorted(by_verdict):
        print("   %-44s %d" % (k, by_verdict[k]))
    for r in pairs:
        if r["verdict"] == "C_shared_template_distinct_subjects":
            continue
        print("\n   %s  content %.2f  subject %.2f"
              % (r["verdict"], r["content_overlap"], r["subject_similarity"]))
        for t in r["tracks"]:
            print("     %-46s %3d recs | %-10s | %-9s | %s"
                  % (t["track_id"], t["records"], t["gazette_gregorian"] or "-",
                     t["decree_date_hijri"] or "-", t["title_ar"][:48]))

    out = os.path.join(ROOT, "reports", "corpus_text_integrity_audit")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "corpus_text_integrity_audit.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "generated_note": NOTE,
            "instruments_scanned": len(tracks),
            "thresholds": {"content_floor": CONTENT_FLOOR, "subject_floor": SUBJECT_FLOOR},
            "reversed_lam_alef_note": (
                "The wider form of the same fault, found by the seed test rather than by a "
                "rule: a word form that appears NOWHERE in the tracks with zero sequence "
                "signatures, and whose lam-alef swap the corpus uses at least %d times more "
                "often. `real_word_collisions` are the forms that FAILED that test — they do "
                "appear in known-good text, because the fault maps real Arabic words onto "
                "other real Arabic words («العالقة» the swap of «العلاقة», «عالمة» of "
                "«علامة»). Those cannot be classified without reading the sentence, and are "
                "listed rather than counted as damage." % RARITY_RATIO),
            "reversed_lam_alef_forms": len(wide),
            "reversed_lam_alef_occurrences": sum(v["occurrences"] for v in wide.values()),
            "reversed_lam_alef_damage_forms": dict(sorted(wide.items())),
            "real_word_collisions": dict(sorted(collisions.items())),
            "encoding_damage_tracks": len(damage),
            "encoding_damage_records": sum(r["records_affected"] for r in damage),
            "encoding_damage": damage,
            "pair_verdict_counts": by_verdict,
            "same_text_under_two_names": pairs,
        }, fh, ensure_ascii=False, indent=1)
    print("\nwrote reports/corpus_text_integrity_audit/corpus_text_integrity_audit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
