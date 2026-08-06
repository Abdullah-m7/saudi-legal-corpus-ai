#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move the corpus's own judgments out of its tests and into the record.

Three times in one sitting a repair was proposed for something this repository
had already decided: the arbitration label anomaly, the duplicate «٣/١٠٤» in the
Law of Sharia Procedure's implementing regulation, the «المادية» typo in the law
itself. Each time a track validator refused the change and named the reason. The
corpus knew — and said so only to whoever ran the tests.

That is a real gap for a reader, and a worse one for a model. Someone looking at
«المادة الحادية والعشرون» on article 31 has no way to learn it is the official
text's own misprint faithfully preserved; someone quoting an article that a
human transcribed from a page image, because the text channel could not be
trusted, has no way to learn that either. Both facts live in
`known_unresolved_discrepancies` on every other subject.

Two kinds are written here, and each is generated from the validator's own
declaration — never from a judgment made now:

  VISUALLY ADJUDICATED — 213 articles across 43 tracks were read off a page
  image and matched by eye, because OCR or the PDF text layer was unavailable or
  untrustworthy for those articles. The disclosure names the count, the share of
  the track, and the article keys, so a reader can weigh any one of them.

  A PRESERVED SOURCE DEFECT — a validator comment marking a typo, a numbering
  anomaly, or text kept verbatim against the temptation to correct it. The
  comment is quoted as the evidence it is, and the reader is told the corpus
  transcribed rather than corrected.

Run with --apply to write; without it, reports and changes nothing.
"""

from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "reports", "corpus_text_quality_audit")

VISUAL_KEY = "%s_articles_adjudicated_by_visual_reading"
PRESERVED_KEY = "%s_source_defect_preserved_verbatim"

VISUAL_RE = re.compile(r"^VISUALLY_ADJUDICATED\s*=\s*(.+?)(?=\n[A-Z_]+\s*=|\ndef |\Z)", re.S | re.M)
N_RE = re.compile(r"^\s*N(?:_RECORDS)?\s*=\s*(\d+)", re.M)
PRESERVED_RE = re.compile(
    r"^\s*#\s*(.*(?:typo|anomal|preserved verbatim|verbatim as published|"
    r"flag-don't-correct|not silently (?:corrected|fixed)).*)$", re.M | re.I)


def track_key(vpath):
    name = os.path.basename(vpath)[len("validate_"):]
    for suffix in ("_tracks.py", "_track.py"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def artifact_for(track):
    """The artifact whose validator this is.

    Matched on track+component first («sharia_procedure_law»), because matching
    the bare track id would attribute a law's judgments to its regulation."""
    best = None
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in glob.glob(os.path.join(ROOT, pattern)):
            parts = os.path.relpath(path, os.path.join(ROOT, "sources")).split(os.sep)
            tid = parts[0]
            comp = parts[-3] if len(parts) == 4 else None
            key = "%s_%s" % (tid, comp) if comp else tid
            if key == track:
                return path
            if tid == track and best is None:
                best = path
    return best


def visual_articles(src):
    m = VISUAL_RE.search(src)
    if not m:
        return []
    n = N_RE.search(src)
    env = {"N": int(n.group(1)) if n else 0, "range": range}
    try:
        keys = eval(m.group(1).strip(), env)                        # noqa: S307
    except Exception:                                               # noqa: BLE001
        return []
    return sorted(str(k) for k in keys)


def save(path, doc):
    raw = open(path, encoding="utf-8").read()
    indent = 1 if re.search(r"^\s\"", raw, re.M) else 2
    text = json.dumps(doc, ensure_ascii=False, indent=indent)
    if raw.endswith("\n"):
        text += "\n"
    open(path, "w", encoding="utf-8").write(text)


def visual_text(keys, total):
    shown = "، ".join("`%s`" % k for k in keys[:12])
    more = "" if len(keys) <= 12 else " … وبقيتها في `%s`." % "scripts/validate_*_track.py"
    share = (" من أصل %d سجلاً" % total) if total else ""
    return (
        "**%d سجلاً%s في هذا المسار قوبلت بصرياً**: قرأها إنسانٌ من صورة الصفحة وطابقها بعينه، "
        "لأن قناة النصّ الآلية (OCR أو طبقة نصّ الـPDF) لم تكن متاحة أو لم تكن موثوقة لتلك "
        "المواد بعينها.\n\n"
        "**وهذا ليس تشكيكاً في النصّ بل إفصاحٌ عن سنده**: بقية سجلات المسار مؤكَّدة آلياً مقابل "
        "المصدر، وهذه مؤكَّدة بقراءةٍ بشرية. **ومن أراد الاعتماد على واحدةٍ منها في أمرٍ يُبنى "
        "عليه فليقابلها بالمصدر الرسمي بنفسه.** والسجلات هي: %s%s"
        % (len(keys), share, shown, more))


def preserved_text(comments):
    quoted = "\n".join("* «%s»" % c.strip() for c in comments[:4])
    return (
        "**خللٌ في المصدر مُبقى على حاله.** يحمل هذا المسار موضعاً أو أكثر خالف فيه النصّ "
        "الرسمي المنشور ما يُتوقَّع — خطأً إملائياً، أو شذوذاً في الترقيم، أو عنواناً مكرراً — "
        "**وقد نُقل كما نشرته الجهة ولم يُصحَّح**، لأن المستودع ينقل ما نُشر لا ما يُظن أن الجهة "
        "أرادته.\n\n**وما يؤكده مدقِّق هذا المسار نصاً**:\n%s\n\n"
        "**وأثرُه على البحث والاستشهاد**: قد لا يطابق البحثُ بالصيغة المتوقَّعة ما هو مخزَّن، "
        "والاستشهاد الصحيح باللفظ المنشور كما هو محفوظ." % quoted)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    written, skipped = [], []
    for vpath in sorted(glob.glob(os.path.join(ROOT, "scripts", "validate_*_track*.py"))):
        src = open(vpath, encoding="utf-8").read()
        track = track_key(vpath)
        keys = visual_articles(src)
        comments = [c for c in PRESERVED_RE.findall(src)
                    # a check's own label is not a statement about the source
                    if not c.strip().startswith("[")]
        if not keys and not comments:
            continue
        path = artifact_for(track)
        if not path:
            skipped.append({"track": track, "reason": "no artifact found"})
            continue
        doc = json.load(open(path, encoding="utf-8"))
        disc = doc.setdefault("known_unresolved_discrepancies", [])
        have = {d.get("article_key") for d in disc if isinstance(d, dict)}
        total = len(doc.get("articles") or {})
        added = []

        if keys:
            k = VISUAL_KEY % track
            if k not in have:
                added.append({"article_key": k, "description": visual_text(keys, total)})
        if comments:
            k = PRESERVED_KEY % track
            if k not in have:
                added.append({"article_key": k, "description": preserved_text(comments)})

        if not added:
            skipped.append({"track": track, "reason": "already disclosed"})
            continue
        if args.apply:
            disc.extend(added)
            save(path, doc)
        written.append({"track": track, "artifact": os.path.relpath(path, ROOT),
                        "visually_adjudicated_records": len(keys),
                        "track_records": total,
                        "preserved_defect_comments": comments[:4],
                        "disclosures_added": [a["article_key"] for a in added]})

    report = {
        "generated_note": (
            "Writes the corpus's own recorded judgments into the artifacts, where a reader can "
            "see them. A track validator that asserts «this label is the official text's typo, "
            "kept verbatim» or «these articles were matched by eye off a page image» is stating "
            "a fact about the source that belongs on the record, not only in a test — three "
            "times in one sitting a repair was proposed for exactly such a judgment, and only "
            "the test refused it. Each disclosure is generated from the validator's own "
            "declaration; no judgment is made here."),
        "applied": bool(args.apply),
        "tracks_disclosed": len(written),
        "visually_adjudicated_records_total": sum(w["visually_adjudicated_records"] for w in written),
        "disclosures": written,
        "skipped": skipped,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "adjudication_disclosures.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("%s %d tracks (%d visually-adjudicated records); %d skipped"
          % ("disclosed" if args.apply else "would disclose", len(written),
             sum(w["visually_adjudicated_records"] for w in written), len(skipped)))
    for w in written[:45]:
        print("   %-46s visual=%-4d %s"
              % (w["track"][:46], w["visually_adjudicated_records"],
                 ",".join(x.rsplit("_", 3)[-1] for x in w["disclosures_added"])))
    print("wrote reports/corpus_text_quality_audit/adjudication_disclosures.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
