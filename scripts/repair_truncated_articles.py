#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Put back the words this corpus cut off its own articles.

The text-quality audit found articles that end mid-sentence — «... التعرّضات
الخاضعة لمتطلبات رأس المال لمخاطر السوق المنصوص عليها في» — while asserting
`text_complete: true`. The cause was in this repository, not in the gazette.

`segment()` strips a chapter heading left at the end of an article's text, and
its pattern consumed everything from the chapter word to the end of the line.
When an article's last sentence CITED a chapter — «المنصوص عليها في الفصل
الثاني من هذا الباب، ولا يشمل ذلك التعرّضات لصفقات عقود المشتقات.» — the
stripper matched at «الفصل الثاني» and deleted the rest of the provision with it.
The gazette's own page carries the full sentence; the corpus threw it away.

The stripper now tests the preceding token and leaves a citation alone. This
script repairs the artifacts that were built before it did.

WHAT IT WILL CHANGE, AND WHAT IT REFUSES TO:

  * it re-fetches each track's OWN cited gazette page and re-segments it with the
    current segmenter — the source governs, as it does everywhere else here;
  * it rewrites an article ONLY when the stored text is a strict PREFIX of what
    the source now yields. That is the whole safety argument: a strict prefix
    means the repair only ever restores a tail the corpus itself removed, and can
    never substitute different words for words already on file;
  * every other disagreement — the source yielding SHORTER text, or text that
    diverges rather than extends — is reported and left untouched, because those
    are edition differences or segmentation changes and neither is settled by
    this script.

Run with --apply to write; without it, it reports and changes nothing.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gazette_autoingest as G                                      # noqa: E402

OUT_DIR = os.path.join(ROOT, "reports", "corpus_text_quality_audit")
PAGE_ID_RE = re.compile(r"(?:details\?p=|decisions-and-regulations/)(\d+)")
CACHE = os.environ.get("GAZETTE_PAGE_CACHE", "")


def url_for(uid):
    return ("https://www.uqn.gov.sa/decisions-and-regulations/%s" % uid
            if uid.startswith("400") else "https://www.uqn.gov.sa/details?p=%s" % uid)


def fetch(uid, tmpdir):
    """The track's own cited page. A cache directory may be supplied through
    GAZETTE_PAGE_CACHE so a repeated run does not re-hit the gazette."""
    if CACHE:
        for name in (uid + ".html",):
            p = os.path.join(CACHE, name)
            if os.path.exists(p) and os.path.getsize(p) > 2000:
                return p
    p = os.path.join(tmpdir, uid + ".html")
    if os.path.exists(p) and os.path.getsize(p) > 2000:
        return p
    r = subprocess.run(["curl", "-sS", "--max-time", "45", url_for(uid)],
                       capture_output=True, text=True)
    if r.returncode == 0 and len(r.stdout) > 2000:
        open(p, "w", encoding="utf-8").write(r.stdout)
        return p
    return None


def artifacts():
    for path in sorted(glob.glob(os.path.join(ROOT, "sources", "*", "official_source", "*.json"))):
        tid = os.path.basename(os.path.dirname(os.path.dirname(path)))
        yield tid, path


def save(path, doc):
    """Preserve each artifact's own JSON formatting; the corpus's files differ in
    indent and trailing newline, and rewriting that is noise in a diff whose
    whole point is the article text."""
    raw = open(path, encoding="utf-8").read()
    indent = 1 if re.search(r"^\s\"", raw, re.M) else 2
    text = json.dumps(doc, ensure_ascii=False, indent=indent)
    if raw.endswith("\n"):
        text += "\n"
    open(path, "w", encoding="utf-8").write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the repairs")
    ap.add_argument("--tmpdir", default=os.path.join(ROOT, ".page_cache"))
    args = ap.parse_args()
    os.makedirs(args.tmpdir, exist_ok=True)

    repaired, refused, unreachable = [], [], []
    for tid, path in artifacts():
        doc = json.load(open(path, encoding="utf-8"))
        arts = doc.get("articles") or {}
        if not arts or not isinstance(next(iter(arts.values())), dict):
            continue
        uids = sorted(set(PAGE_ID_RE.findall(open(path, encoding="utf-8").read())))
        if len(uids) != 1:
            continue                      # multi-source tracks are not this script's business
        page = fetch(uids[0], args.tmpdir)
        if not page:
            unreachable.append({"track_id": tid, "uid": uids[0]})
            continue
        _title, body = G.page_text(page)
        segs, diag = G.segment(body)
        if diag["count"] < G.MIN_ARTICLES:
            continue
        by_num = {n: txt for n, _o, txt, _c in segs}

        touched = False
        for key, rec in sorted(arts.items()):
            old = rec.get("text", "")
            new = by_num.get(rec.get("article_number"))
            if not new or new == old:
                continue
            if new.startswith(old) and len(new) > len(old):
                repaired.append({"track_id": tid, "article_key": key,
                                 "stored_chars": len(old), "repaired_chars": len(new),
                                 "restored_tail": new[len(old):][:200]})
                if args.apply:
                    rec["text"] = new
                    touched = True
            else:
                refused.append({"track_id": tid, "article_key": key,
                                "stored_chars": len(old), "source_chars": len(new),
                                "reason": ("the source now yields SHORTER text"
                                           if len(new) < len(old) else
                                           "the source text diverges rather than extends"),
                                "stored_tail": old[-90:], "source_tail": new[-90:]})
        if touched and args.apply:
            save(path, doc)

    report = {
        "generated_note": (
            "Restores article text that this repository removed. segment() strips a chapter "
            "heading left at an article's tail, and its pattern consumed everything from the "
            "chapter word to the end of the line — so an article whose last sentence CITED a "
            "chapter lost the rest of that sentence. The stripper now tests the token before "
            "the chapter word and leaves a citation alone; this repairs the artifacts built "
            "before it did. An article is rewritten ONLY when its stored text is a strict "
            "PREFIX of what the source now yields, which is what makes the repair incapable "
            "of substituting different words for words already on file. Every other "
            "disagreement is reported untouched."),
        "applied": bool(args.apply),
        "articles_repaired": len(repaired),
        "tracks_repaired": len({r["track_id"] for r in repaired}),
        "repairs": repaired,
        "left_for_adjudication": refused,
        "pages_unreachable_this_pass": unreachable,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "truncated_article_repair.json"), "w",
              encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("%s %d articles across %d tracks; %d disagreements left for adjudication; "
          "%d pages unreachable"
          % ("repaired" if args.apply else "would repair", len(repaired),
             len({r["track_id"] for r in repaired}), len(refused), len(unreachable)))
    print("wrote reports/corpus_text_quality_audit/truncated_article_repair.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
