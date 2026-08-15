#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Carry the corpus's disclosures to the place its text is actually read.

This repository discloses relentlessly. 2,778 disclosures across 673 tracks say
which articles a human read off a page image, which texts carry the lam-alef
damage that is in the official PDFs themselves, which units are tables rather
than articles, which instruments have a later amendment notice, which source
typo was kept verbatim rather than corrected.

Every one of them lives in `sources/<track>/official_source/*.json`, and nothing
that reads this corpus opens that file. The unified LLM index — the layer a model
retrieves from — carries fourteen fields, and not one of them is a caveat. So a
model quoting an article that rests on one person's eyes, or that its own track
says may no longer be current, quotes it with exactly the confidence of an
article verified twice over.

A disclosure that is not visible where the text is used is decoration. This layer
resolves every disclosure to the records it governs and emits it in a form small
enough to travel with them.

TWO CLASSES, BECAUSE THEY ARE NOT EQUAL

Dumping 2,778 notes on 21,000 records equally would be as unhelpful as dumping
none: the reader cannot tell which ones change the answer. So each is sorted:

  MATERIAL — changes how the text should be used or cited. It was read by eye;
  it carries encoding damage; its unit is a table, not an article; its source
  skips a number; a later amendment notice exists; it is a treaty and its force
  differs from a statute's; a defect was preserved verbatim.

  PROVENANCE — says how the text was obtained and is worth knowing, but does not
  change what the provision says. Only one source could be checked; the issuance
  number was not stated; a secondary portal was unreachable; tashkeel was
  stripped.

Anything that matches neither is carried through as `other` WITH its key, so a
disclosure is never silently dropped for failing to fit a category.

Read-only over sources/; writes the layer and its summary.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
FRESHNESS = os.path.join(ROOT, "data", "corpus_freshness_manifest",
                         "corpus_freshness_manifest.json")
OUT_DIR = os.path.join(ROOT, "data", "corpus_caveat_layer")

# code -> (class, matcher over the disclosure key with the track prefix removed,
#          one-line Arabic statement of what it means for a reader)
MATERIAL = [
    # First in the list because it outranks every other caveat: the others qualify
    # how a text may be cited, this one says it may not be cited as law at all.
    # It was added the day the corpus first recorded a track of its own as repealed,
    # and the omission was not theoretical — the disclosure was written, the layer
    # matched none of its patterns, and the most consequential statement the corpus
    # can make about a text fell through into `other`, where no reading surface
    # looks. A vocabulary that silently absorbs what it does not recognise reports
    # the same success whether it understood the input or not.
    ("repealed", re.compile(r"repealed_in_full|repealed_by|no_longer_in_force"),
     "هذا النصّ **ملغى** ولا يُستشهد به بوصفه سارياً — وبيان الإلغاء وتاريخه في إفصاح المسار"),
    ("visual_reading", re.compile(r"adjudicated_by_visual_reading"),
     "سجلات من هذا المسار قُرئت من صورة الصفحة وطوبقت بعين إنسان لا بقناة نصّ آلية"),
    ("encoding_damage", re.compile(r"letter_transposition|pdf_extraction|encoding"),
     "نصّ هذا المسار يحمل خلل انقلاب لام-ألف الذي أثبت المستودع أنه في ملفات الجهات الرسمية نفسها"),
    ("duplicate_text", re.compile(r"same_instrument_held_twice|implementing_text_restates"),
     "نصّ هذا المسار يتكرر في المستودع تحت اسم آخر"),
    ("source_defect_preserved", re.compile(r"source_defect_preserved|source_typo|label_carries_a_source_typo"),
     "خلل في المصدر الرسمي أُبقي حرفياً ولم يُصحَّح، فقد لا يطابق البحثُ بالصيغة المتوقَّعة"),
    ("not_an_article", re.compile(r"units_that_are_not_articles|numbering_form_is_"),
     "وحدات هذا المسار ليست كلها «مواد» — منها جداول وملاحق وبنود — فلا تُستشهد بوصفها مواد"),
    ("numbering_gap", re.compile(r"numbering_gap|article_\d+_not_recovered|_not_held"),
     "ترقيم المصدر يتخطى رقماً أو أكثر، والثغرة معلنة في `missing_article_numbers`"),
    ("currency_risk", re.compile(r"amended_after_edition_on_file|currency|staleness|rebuilt_from_later_reissue"),
     "صدر تعديل منشور بعد الطبعة المحفوظة، ولم يثبت أن النصّ المخزَّن يستوعبه"),
    ("treaty", re.compile(r"is_a_ratified_international_agreement"),
     "هذه اتفاقية دولية لا تشريع داخلي، ومصدر قوتها ونطاق تطبيقها يختلفان"),
    ("article_specific", re.compile(r"_art_(?:\d+|all)$"),
     "على هذه المادة بعينها إفصاحٌ خاص"),
]
PROVENANCE = [
    ("single_source", re.compile(r"source_is_gazette_html_only|single_source")),
    ("no_decision_number", re.compile(r"no_decision_number")),
    ("secondary_source_unreachable", re.compile(r"boe_|unreachable|wayback")),
    ("no_structural_headings", re.compile(r"no_baab|no_chapter|no_inline_article_titles|no_structure")),
    ("normalisation", re.compile(r"tashkeel|normalization|normalisation")),
    ("title_resembles_another_track", re.compile(r"title_resembles")),
    ("companion_not_ingested", re.compile(r"not_ingested|out_of_scope|_estimate_confirmed|_batch_confirmed")),
    ("date_not_pinpointed", re.compile(r"date_not_pinpointed|date_unconfirmed")),
]
ARTICLE_KEY = re.compile(r"_art_(\d{1,4})$")

# Two codes describe SOME records of a track, not all of it, and attaching them
# track-wide says something false about the rest. «14 of 20 records were read by
# eye» must not mark the other six; «this track holds tables as well as articles»
# must not mark the articles.
#
# Both are resolved per record instead:
#   visual_reading  — from the record keys the track's validator declares
#   not_an_article  — from the record's own printed label
VISUALLY_ADJUDICATED_RE = re.compile(
    r"^VISUALLY_ADJUDICATED\s*=\s*(.+?)(?=\n[A-Z_]+\s*=|\ndef |\Z)", re.S | re.M)
N_RE = re.compile(r"^\s*N(?:_RECORDS)?\s*=\s*(\d+)", re.M)
ARTICLE_LABEL_RE = re.compile(
    r"^\(?\s*(?:ال)?مادة\b"
    r"|^(?:ال)?(?:أول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر|حادي)"
    r"(?:ة|ه)?\b(?!\s*[:：])")
PER_RECORD_CODES = {"visual_reading", "not_an_article"}


def visually_adjudicated_keys():
    """{record_key} the track validators declare were matched by eye."""
    out = set()
    for vpath in glob.glob(os.path.join(ROOT, "scripts", "validate_*_track*.py")):
        src = open(vpath, encoding="utf-8").read()
        m = VISUALLY_ADJUDICATED_RE.search(src)
        if not m:
            continue
        n = N_RE.search(src)
        try:
            keys = eval(m.group(1).strip(),                          # noqa: S307
                        {"N": int(n.group(1)) if n else 0, "range": range})
        except Exception:                                            # noqa: BLE001
            continue
        out.update(str(k) for k in keys)
    return out


def artifact_key_map():
    """(source dir, component, article number) -> artifact record key.

    Keyed by COMPONENT as well as track, because a corpus that holds both a law
    and its implementing regulation has an article 28 in each. Collapsing them
    made a law-only visual adjudication mark the regulation's article too, and
    telling a reader that a machine-verified record was read by eye is a false
    statement about verification — worse than saying nothing."""
    out = {}
    all_keys = set()
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in glob.glob(os.path.join(ROOT, pattern)):
            parts = os.path.relpath(path, os.path.join(ROOT, "sources")).split(os.sep)
            src_dir = parts[0]
            component = parts[1] if len(parts) == 4 else None
            try:
                doc = json.load(open(path, encoding="utf-8"))
            except Exception:                                        # noqa: BLE001
                continue
            for key, rec in (doc.get("articles") or {}).items():
                if not isinstance(rec, dict):
                    continue
                n = rec.get("article_number")
                if not isinstance(n, int):
                    m = ARTICLE_KEY.search(key)
                    n = int(m.group(1)) if m else None
                all_keys.add(key)
                if n is not None:
                    out.setdefault((src_dir, component, n), key)
    out[("__keys__", None, 0)] = all_keys
    return out


def record_artifact_keys(rec, keymap):
    """Every artifact key this index record could BE — exactly, never by guess.

    `article_path` is «<dir>/<component>/articles/<key or number>», so the last
    segment is often the artifact key itself; where it is only a number, the
    first two segments identify the artifact and the number selects the key."""
    out = set()
    path = rec.get("article_path") or ""
    parts = path.split("/")
    # Accept the path's last segment only when it IS a key of some artifact.
    # Pattern-matching «_art_» instead rejected «..._appendix_001» — a real key —
    # and fell back to the numeric lookup, which resolved appendix 1 to ARTICLE 1
    # and would have attached one record's caveats to a different record.
    if parts and parts[-1] in keymap.get(("__keys__", None, 0), ()):
        out.add(parts[-1])
    try:
        n = int(str(rec.get("article_number")).strip())
    except (TypeError, ValueError):
        n = None
    if n is not None and len(parts) >= 2:
        src_dir, component = parts[0], parts[1]
        for k in ((src_dir, component, n), (src_dir, None, n)):
            hit = keymap.get(k)
            if hit:
                out.add(hit)
    return out


def non_article_record_keys():
    """{record_key} whose own printed label is not an article's."""
    out = set()
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in glob.glob(os.path.join(ROOT, pattern)):
            try:
                doc = json.load(open(path, encoding="utf-8"))
            except Exception:                                        # noqa: BLE001
                continue
            for key, rec in (doc.get("articles") or {}).items():
                if not isinstance(rec, dict):
                    continue
                lab = (rec.get("number_label_ar") or "").strip()
                if lab and not ARTICLE_LABEL_RE.match(lab):
                    out.add(key)
    return out


def artifacts():
    seen = set()
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            if path in seen:
                continue
            seen.add(path)
            tid = os.path.relpath(path, os.path.join(ROOT, "sources")).split(os.sep)[0]
            try:
                yield tid, path, json.load(open(path, encoding="utf-8"))
            except Exception:                                      # noqa: BLE001
                continue


def classify(key, track):
    bare = key[len(track) + 1:] if key.startswith(track + "_") else key
    for code, rx, _text in MATERIAL:
        if rx.search(bare):
            return "material", code
    for code, rx in PROVENANCE:
        if rx.search(bare):
            return "provenance", code
    return "other", bare


def main():
    material_text = {c: t for c, _r, t in MATERIAL}

    # freshness flags are a caveat too, and they live in a different layer
    fresh = {}
    if os.path.exists(FRESHNESS):
        for t in json.load(open(FRESHNESS, encoding="utf-8"))["tracks"]:
            codes = []
            if t.get("published_amendment_after_edition_on_file"):
                codes.append("currency_risk")
            if t.get("known_source_staleness_risk"):
                codes.append("currency_risk")
            if codes:
                fresh[t["track_id"]] = sorted(set(codes))

    track_caveats = defaultdict(lambda: {"material": set(), "provenance": set(),
                                         "other": [], "per_article": defaultdict(set)})
    total = 0
    for tid, path, doc in artifacts():
        bucket = track_caveats[tid]
        for x in doc.get("known_unresolved_discrepancies") or []:
            if not isinstance(x, dict) or not x.get("article_key"):
                continue
            total += 1
            key = x["article_key"]
            cls, code = classify(key, tid)
            m = ARTICLE_KEY.search(key)
            if m and cls == "material":
                bucket["per_article"][int(m.group(1))].add(code)
            elif cls == "material":
                bucket["material"].add(code)
            elif cls == "provenance":
                bucket["provenance"].add(code)
            else:
                bucket["other"].append(key)
        bucket["artifact"] = os.path.relpath(path, ROOT)

    for tid, codes in fresh.items():
        track_caveats[tid]["material"].update(codes)

    # resolve onto index records
    visual_keys = visually_adjudicated_keys()
    non_article_keys = non_article_record_keys()
    keymap = artifact_key_map()
    records = [json.loads(l) for l in open(INDEX, encoding="utf-8") if l.strip()]
    rows = []
    stat = Counter()
    for r in records:
        b = track_caveats.get(r["corpus"])
        if not b:
            continue
        mat = set(b["material"])
        try:
            n = int(str(r.get("article_number")).strip())
        except (TypeError, ValueError):
            n = None
        if n is not None and n in b["per_article"]:
            mat |= b["per_article"][n]
        # the two that describe some records only: keep them only where true
        alt_keys = record_artifact_keys(r, keymap)
        for code, truth in (("visual_reading", visual_keys),
                            ("not_an_article", non_article_keys)):
            if code in mat and not (alt_keys & truth):
                mat.discard(code)
        if not mat and not b["provenance"] and not b["other"]:
            continue
        rows.append({
            "record_id": r["record_id"], "corpus": r["corpus"],
            "caveats_material": sorted(mat),
            "caveats_provenance": sorted(b["provenance"]),
            "caveats_other_keys": sorted(set(b["other"]))[:6],
            "caveat_summary_ar": (" | ".join(material_text[c] for c in sorted(mat)
                                             if c in material_text) or None),
            "disclosures_ref": "%s#known_unresolved_discrepancies" % b["artifact"],
        })
        for c in mat:
            stat[c] += 1

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "corpus_caveat_layer.jsonl"), "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "schema_version": "1.0.0",
        "generated_by": "scripts/gen_corpus_caveat_layer.py",
        "read_only_derived_layer": True,
        "purpose_note": (
            "Carries the corpus's own disclosures to the layer its text is read from. Every one "
            "of the 2,778 disclosures lives in a source artifact that nothing reading this "
            "corpus opens, and the unified index — what a model actually retrieves — carried no "
            "caveat field at all. A model quoting an article that rests on one person's eyes, or "
            "that its own track says may no longer be current, quoted it with the confidence of "
            "an article verified twice over. Caveats are split into MATERIAL (changes how the "
            "text should be used or cited) and PROVENANCE (how it was obtained), because "
            "presenting 2,778 notes as equals is as unhelpful as presenting none. Anything "
            "matching neither is carried through as `other` with its key, so nothing is dropped "
            "for failing to fit a category."),
        "disclosures_read": total,
        "tracks_with_disclosures": len([t for t, b in track_caveats.items()
                                        if b["material"] or b["provenance"] or b["other"]]),
        "index_records": len(records),
        "records_carrying_a_caveat": len(rows),
        "records_carrying_a_material_caveat": sum(1 for r in rows if r["caveats_material"]),
        "material_caveat_counts": dict(stat.most_common()),
        "material_caveat_meanings_ar": material_text,
    }
    with open(os.path.join(OUT_DIR, "corpus_caveat_layer_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)

    print("disclosures read: %d over %d tracks" % (total, summary["tracks_with_disclosures"]))
    print("records carrying a caveat: %d of %d (%d with a MATERIAL one)"
          % (len(rows), len(records), summary["records_carrying_a_material_caveat"]))
    for c, n in stat.most_common():
        print("   %-28s %d" % (c, n))
    print("\nwrote data/corpus_caveat_layer/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
