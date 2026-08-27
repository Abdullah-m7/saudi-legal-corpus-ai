#!/usr/bin/env python3
"""A citator for Saudi statutory law: which judgments applied which article.

A practitioner drafting a claim asks one question of a provision — how have
the courts applied it? For Saudi law there is no public tool that answers it.
The materials to build one are already here: 50,666 judgments in full text,
106,337 statutory citations matched to article level, and the verified text
of the articles themselves.

An entry is one citation, and carries
  the article, with its official verified text where the corpus holds it
  the judgment that cites it — court, city, Hijri date, judgment number
  the passage around the citation, so the reader sees the application
  whose voice it is: the statement of the case, the court's own reasoning,
  or the operative part — and, inside the statement of the case, whether the
  citation is the court's own narration or a party's argument

That last field is what makes this worth more than a search box. «The court
held» and «counsel argued» are different facts, and a citator that conflates
them misleads the person relying on it. The judgments carry their own
structure — الوقائع then الأسباب then حكمت الدائرة — and where those headings
are present the segment is recorded; where they are not, the voice is marked
unknown rather than guessed. A record can hold two judgments, first instance
and appeal, and each is segmented on its own; see
../arabic_paper/voice_attribution.py.

A first build called the pre-الأسباب segment *pleadings*. That was wrong, and
wrong in a way that mattered: الوقائع is written by the court, and a great
deal of it is the court's own procedural narration — «وتشير الدائرة إلى أنها
عقدت هذه الجلسة التحضيرية بناءً على المادة التسعين». Counting that as an
argument put to the court overstates the bar and understates the bench. The
segment is now named `recital` for what it is, and every citation inside it
carries an `attribution` field: `court` where the sentence names the bench as
the actor, `unattributed` otherwise. See ../arabic_paper/voice_attribution.py
for the cue lists and the hand validation.

WHAT THIS IS NOT
It is not a summary, a headnote, or an interpretation. Every passage is the
judgment's own words, quoted with its citation. Nothing here is generated
prose about what a court meant. A tool that a lawyer might rely on must not
put words in a court's mouth.

Output
  citator/articles/<track_id>/<n>.json   one article and every judgment on it
  citator/instruments/<track_id>.json    that instrument's articles, summarised
  citator/index.json                     instruments, counts, article ranges

One file per article, because that is the unit of the question. Holding a
whole instrument in one file put 65 MB behind a lookup of one provision, and
GitHub warned about it; a practitioner wanting article 90 should fetch
article 90.
"""

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ANALYSIS = REPO / "docs" / "research" / "arabic_paper"
sys.path.insert(0, str(ANALYSIS))

import arabic_ordinals as A      # noqa: E402
import match_instruments as M    # noqa: E402
import voice_attribution as V    # noqa: E402

REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
SHARDS = sorted((ANALYSIS / "judgments").glob("*.jsonl"))
OUT = HERE / "instruments"

CITE = re.compile(
    r"الماد[ةه]\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+((?:نظام|لائحة|النظام|اللائحة)[^\.،؛\n\)]{0,60})")
BEFORE, AFTER = 260, 340


def article_texts(tracks):
    """The verified Arabic text of each article, where the corpus holds it."""
    out = {}
    for t in tracks:
        tid = t["track_id"]
        for p in (t.get("data_paths") or []):
            path = REPO / str(p)
            if not str(p).endswith(".jsonl") or not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                num = r.get("article_number")
                if not isinstance(num, int):
                    continue
                out[(tid, num)] = {
                    "label": r.get("number_label_ar"),
                    "section": r.get("section_ar"),
                    "text": r.get("article_text_verified"),
                    "legal_status": r.get("legal_status_ar"),
                    "repealed": bool(r.get("is_repealed")),
                    "amended": bool(r.get("is_amended")),
                }
            break
    return out


def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    names = {t["track_id"]: t.get("display_name_ar") for t in tracks}
    index, order = M.build(REGISTRY)
    arts = article_texts(tracks)
    print(f"verified article text available for {len(arts):,} articles")

    entries = collections.defaultdict(lambda: collections.defaultdict(list))
    seen = collections.Counter()
    n = cites = 0

    for si, shard in enumerate(SHARDS, 1):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            text = r["text"]
            spans = V.segments(text, r.get("sections"))
            last = M.Recent()
            for m in CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                num, para = A.parse(m.group(1))
                if num is None:
                    continue
                cites += 1
                attribution = None
                voice = V.voice_at(spans, m.start())
                if voice == "recital":
                    attribution = V.attribute(text, m.start())[0]
                    if attribution == "party":
                        attribution = "unattributed"
                a = max(0, m.start() - BEFORE)
                b = min(len(text), m.end() + AFTER)
                entries[tid][num].append({
                    "judgment_id": r["id"],
                    "judgment_number": r["judgment_number"],
                    "court": r["court"], "city": r["city"],
                    "hijri_date": r["hijri_date"],
                    "paragraph": para,
                    "voice": voice,
                    "attribution": attribution,
                    "passage": text[a:b],
                    "at": m.start() - a,
                })
                seen[(tid, num)] += 1
        if si % 50 == 0:
            print(f"  shard {si}/{len(SHARDS)}: {n:,} judgments, {cites:,} entries")

    OUT.mkdir(exist_ok=True)
    ARTS = HERE / "articles"
    ARTS.mkdir(exist_ok=True)
    summary = []
    for tid, articles in sorted(entries.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())):
        payload = {
            "track_id": tid,
            "instrument": names.get(tid),
            "articles_with_citations": len(articles),
            "entries": sum(len(v) for v in articles.values()),
            "articles": {},
        }
        folder = ARTS / tid
        folder.mkdir(exist_ok=True)
        for num in sorted(articles):
            rows = sorted(articles[num], key=lambda e: (e["hijri_date"] or ""))
            meta = arts.get((tid, num), {})
            by_voice = dict(collections.Counter(e["voice"] for e in rows))
            court_recital = sum(1 for e in rows if e["attribution"] == "court")
            record = {
                "track_id": tid, "instrument": names.get(tid),
                "article_number": num,
                "label": meta.get("label"),
                "section": meta.get("section"),
                "official_text": meta.get("text"),
                "legal_status": meta.get("legal_status"),
                "citations": len(rows),
                "by_voice": by_voice,
                "recital_by_court": court_recital,
                "judgments": rows,
            }
            (folder / f"{num}.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
            payload["articles"][str(num)] = {
                "article_number": num, "label": meta.get("label"),
                "section": meta.get("section"),
                "has_official_text": bool(meta.get("text")),
                "legal_status": meta.get("legal_status"),
                "citations": len(rows), "by_voice": by_voice,
                "recital_by_court": court_recital,
                "file": f"articles/{tid}/{num}.json",
            }
        (OUT / f"{tid}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        summary.append({"track_id": tid, "instrument": names.get(tid),
                        "articles": len(articles), "entries": payload["entries"]})

    (HERE / "index.json").write_text(json.dumps({
        "judgments_searched": n, "entries": cites,
        "instruments": len(entries),
        "articles": sum(len(v) for v in entries.values()),
        "with_official_text": sum(
            1 for tid in entries for num in entries[tid] if (tid, num) in arts),
        "by_instrument": summary,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{n:,} judgments, {cites:,} citator entries")
    print(f"  {len(entries)} instruments, "
          f"{sum(len(v) for v in entries.values()):,} distinct articles")
    print(f"  wrote {len(summary)} instrument files and index.json")


if __name__ == "__main__":
    main()
