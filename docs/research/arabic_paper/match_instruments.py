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

A fourth failure was silent, and worse, because it produced a confident wrong
answer rather than none. Matching was containment in either direction over
titles sorted longest first, so «المادة ١٦ من نظام المحاكم التجارية» — the
jurisdiction article of the law — matched «اللائحة التنفيذية لنظام المحاكم
التجارية», whose title contains the law's title. It sent 12,956 citations to
the implementing regulation, and did the same to نظام الإثبات against its
procedural manuals and to نظام المرافعات الشرعية against its regulation. The
direction of containment carries the meaning: a citation that spells out the
regulation's title should match the regulation (longest title wins), but a
citation that names only the law must match the law (shortest title wins).
Exact equality is tried before either.

Anaphora has a direction too. «من النظام» and «من اللائحة» do not refer to
the same thing, and resolving both to whichever instrument was named last
sends an article of the law into the regulation's file whenever the
regulation happened to be named more recently — which, in a commercial
judgment, it usually was. The referent is kept by kind: النظام resolves to
the last law named in that judgment, اللائحة to the last regulation.
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
    # judgments call an implementing regulation «لائحة نظام كذا» as often as
    # they spell out «اللائحة التنفيذية لنظام كذا»
    m = re.match(r"^(?:ال)?لائحه التنفيذيه ل(.+)$", title)
    if m:
        out.add("لائحه " + m.group(1))
        out.add("اللائحه " + m.group(1))
    return {v for v in (" ".join(x.split()) for x in out) if len(v) > 6}


# One definition, imported by every script that reports a procedural share,
# so that the paper and the notes cannot quietly disagree about what counts.
PROCEDURAL = frozenset({
    "commercial_courts_law", "commercial_courts_implementing_regulation",
    "sharia_procedure_law", "sharia_procedure_implementing_regulation",
    "evidence_law", "evidence_procedural_manuals", "evidence_expertise_rules",
    "arbitration_law", "arbitration_implementing_regulation",
    "law_practice_law", "law_practice_implementing_regulation",
    "enforcement_law", "enforcement_implementing_regulation",
    "judiciary_law", "bankruptcy_case_rules",
})

KINDS = {}          # track_id -> 'regulation' | 'law', filled by build()

REGULATION = re.compile(r"^(?:ال)?(?:لائح|لوائح|قواعد)")


class Recent:
    """The last instrument named in a judgment, kept by kind, for anaphora."""

    __slots__ = ("law", "regulation", "any")

    def __init__(self):
        self.law = self.regulation = self.any = None

    def note(self, tid):
        self.any = tid
        if KINDS.get(tid) == "regulation":
            self.regulation = tid
        else:
            self.law = tid

    def pick(self, name):
        if "لائح" in name:
            return self.regulation or self.any
        if "نظام" in name:
            return self.law or self.any
        return self.any


def build(registry_path):
    reg = json.load(open(registry_path, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    index = {}
    for t in tracks:
        ar = t.get("display_name_ar")
        if not ar:
            continue
        title = normalise(ar)
        KINDS[t["track_id"]] = (
            "regulation" if REGULATION.match(title) else "law")
        for v in variants(title):
            index.setdefault(v, t["track_id"])
    return index, sorted(index, key=len, reverse=True)


def match(raw, index, order, last):
    """Return (track_id, kind) where kind is 'named', 'anaphoric' or None."""
    name = normalise(clean(raw))
    if not name:
        return None, None
    bare = re.fullmatch(r"(?:ال)?(?:نظام|لائحه)(?:\s+(?:التنفيذيه))?", name)
    if bare or ANAPHOR.match(name):
        if last is None:
            return None, None
        tid = last.pick(name) if isinstance(last, Recent) else last
        return (tid, "anaphoric") if tid else (None, None)
    if name in index:
        return index[name], "named"
    # the citation spells out a title: the longest one it contains wins, so
    # «اللائحة التنفيذية لنظام المحاكم التجارية» beats «نظام المحاكم التجارية»
    for title in order:
        if title in name:
            return index[title], "named"
    # the citation is shorter than any title: the shortest title containing it
    # wins, because «نظام الإثبات» is the law, not its procedural manuals
    for title in reversed(order):
        if name in title:
            return index[title], "named"
    return None, None
