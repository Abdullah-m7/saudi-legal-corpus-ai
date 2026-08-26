#!/usr/bin/env python3
"""Match a statutory citation in a judgment to an instrument in the registry.

The first matcher left 9.8% of citations unmatched. Reading the unmatched
names showed three distinct failures, not one:

  variant     judgments write نظام المحكمة التجارية, singular, where the
              registry title is نظام المحاكم التجارية, plural — 1,706 hits
              on one variant alone. The registry also writes trademark law as
              «قانون (نظام) العلامات التجارية», and the parenthetical breaks
              a containment test against the نظام form a judgment uses.

  anaphora    «ذات النظام», «اللائحة ذاتها», «النظام نفسه», «لائحة النظام» —
              a citation to whatever instrument the judgment named last. Close
              to a thousand of them, and none carries a name to match.

  runaway     «من النظام على النحو الآتي: أ- إرسال رسالة …» — a bare النظام
              followed by the quoted text of the article. The capture ran into
              the quotation, so the name was nonsense and the citation lost.

The third is the same failure as the second: a bare النظام or اللائحة with no
name is always anaphoric. So the matcher resolves them against the last
instrument matched earlier in the same judgment, and counts them separately,
because a resolved reference is a weaker observation than a named one and a
paper should be able to report it apart.
"""

import json
import re

ANAPHOR = re.compile(
    r"^(?:ال)?(?:نظام|لائحه|لائحة)?\s*"
    r"(?:التنفيذيه|التنفيذية)?\s*(?:ل?ذات|ل?ذلكم|ل?ذلك|نفسه|نفسها|ذاته|ذاتها|"
    r"المذكور|المذكوره|السابق|اعلاه)\b")

STOP = re.compile(
    r"\s+(?:الصادر|الصادرة|المعدل|كما|وذلك|على أن|علي أن|على أنه|علي انه|"
    r"على:|علي:|التي|الذي|حيث|وقد|وحيث|المبني|المشار|بموجب|فإن|فان|وأن|وان|"
    r"إذا|اذا|قررت|رأت|رات|ونصها|ونصه|والمادة|والماده|ومادة|لسنة|لسنه|لعام|"
    r"في جميع|في حال|بأن|بان|أياً|ايا|وقراري|إلى|الي|بأنه|بانه|قد بينت|جعلت|"
    r"على النحو|علي النحو|نصت|نص|تنص|بينت|أوجبت|اوجبت|تقضي|قضت|"
    r"رقم\s*\(?م\s*/)\b")


def normalise(s):
    s = " ".join(str(s or "").split())
    s = re.sub(r"[ًٌٍَُِّْـ]", "", s)
    s = re.sub(r"[()\[\]]", " ", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    s = s.replace("ة", "ه").replace("ى", "ي")
    return " ".join(s.split())


def clean(name):
    name = " ".join(name.split())
    m = STOP.search(name)
    if m:
        name = name[:m.start()]
    name = re.split(r"\s*[-–—:]\s*", name, 1)[0]
    return name.strip(" ،.:؛()\"'").strip()


def variants(title):
    """Registry titles as a judgment might write them."""
    out = {title}
    out.add(title.replace("قانون نظام", "نظام"))
    out.add(re.sub(r"^قانون\s+", "نظام ", title))
    for a, b in (("المحاكم", "المحكمه"), ("المحكمه", "المحاكم")):
        if a in title:
            out.add(title.replace(a, b))
    return {v for v in (" ".join(x.split()) for x in out) if len(v) > 6}


def build(registry_path):
    reg = json.load(open(registry_path, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    index = {}
    for t in tracks:
        ar = t.get("display_name_ar")
        if not ar:
            continue
        for v in variants(normalise(ar)):
            index.setdefault(v, t["track_id"])
    # longest first: the implementing regulation must win over its parent law
    return index, sorted(index, key=len, reverse=True)


def match(raw, index, order, last):
    """Return (track_id, kind) where kind is 'named', 'anaphoric' or None."""
    name = normalise(clean(raw))
    if not name:
        return None, None
    bare = re.fullmatch(r"(?:ال)?(?:نظام|لائحه)(?:\s+(?:التنفيذيه))?", name)
    if bare or ANAPHOR.match(name):
        return (last, "anaphoric") if last else (None, None)
    for title in order:
        if title in name or name in title:
            return index[title], "named"
    return None, None
