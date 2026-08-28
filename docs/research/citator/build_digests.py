#!/usr/bin/env python3
"""Digests for the most-cited articles: what the citator's raw entries hide.

The citator answers «show me every judgment on article 16». For the busiest
articles that answer is 13,000 entries long, and a practitioner cannot read
it. A digest is the same material, counted:

  where the citation sits          reasoning · recital · operative
  who is speaking inside الوقائع   the court's own narration, or not
  which courts and which years     the spread, not one example
  the recurring formulations       near-identical sentences, clustered,
                                   each quoted verbatim from one judgment
  which articles travel with it    co-citation inside the same judgment

WHAT A DIGEST IS NOT. It contains no sentence about what a court meant. Every
quoted line is a judgment's own words with its number, court, city and date.
The counts are counts. Where a heuristic is used — attribution inside
الوقائع, near-duplicate clustering — the digest says so on the page.

Recurring formulations are found by banded MinHash over character 5-grams,
which is fast but chains A to C through B. So the clusters are used only to
propose an exemplar, and the number printed beside each exemplar is then
measured directly: how many of that segment's sentences share at least half
their 5-grams with the quoted one. That is a claim a reader can check against
the JSON. It is similarity of wording, not of meaning.
"""

import collections
import json
import re
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTS = HERE / "articles"
OUT = HERE / "digests"
TOP = 20

DIAC = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
BREAK = re.compile(r"[.؛\n]")
SOFT = re.compile(r"[،,]")
LEFT, RIGHT = 200, 240

VOICE_AR = {"reasoning": "تعليل المحكمة", "recital": "الوقائع",
            "operative": "المنطوق", "unknown": "غير محدَّد"}

APPEAL_AR = {"affirmed": "أُيِّد", "reversed": "نُقض أو أُلغي",
             "substituted": "أُلغي وحُكم مجددًا", "varied": "عُدِّل",
             "not_admitted": "لم يُقبل الاعتراض شكلًا",
             "other_disposition": "فُصل على وجهٍ آخر",
             "unclear": "لم يتبيّن من المنطوق"}


def norm(s):
    s = DIAC.sub("", s)
    s = re.sub(r"[أإآٱ]", "ا", s)
    s = s.replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"\(\s*\.\.\.\s*\)", "§", s)
    s = re.sub(r"[0-9٠-٩]+", "#", s)
    s = re.sub(r"[^\w\s§#]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clause(passage, at):
    """The words around the citation, cut at the nearest clause boundary.

    A whole Arabic sentence in a judgment can run for a thousand characters,
    which is useless both for comparing one citation against another and for
    quoting. The window is bounded first, then trimmed to a full stop inside
    it, and failing that to a comma, and failing that to a word boundary.
    `cut` records that the window, not the text, decided where it ended.
    """
    lo, hi = max(0, at - LEFT), min(len(passage), at + RIGHT)
    seg, off = passage[lo:hi], at - lo
    left = max((m.end() for m in BREAK.finditer(seg, 0, off)), default=None)
    if left is None:
        left = max((m.end() for m in SOFT.finditer(seg, 0, off)), default=None)
    cut_left = left is None
    if cut_left:
        left = 0 if lo == 0 else (seg.find(" ") + 1)
    m = BREAK.search(seg, off) or SOFT.search(seg, off)
    cut_right = m is None
    right = len(seg) if cut_right else m.start()
    if cut_right and hi < len(passage):
        right = seg.rfind(" ", off)
        right = len(seg) if right < 0 else right
    text = " ".join(seg[left:right].split())
    return (text or None), (cut_left and lo > 0) or (cut_right and hi < len(passage))


HASHES, BANDS = 16, 4
SEEDS = [0x9e3779b9 * (i + 1) & 0xFFFFFFFF for i in range(HASHES)]


def grams(text):
    return frozenset(text[i:i + 5] for i in range(max(1, len(text) - 4)))


def sketch(gs):
    if not gs:
        return None
    enc = [g.encode("utf-8") for g in gs]
    return tuple(min(zlib.crc32(g, s) for g in enc) for s in SEEDS)


def jaccard(a, b):
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter) if inter else 0.0


def cluster(rows):
    """Candidate groups: the largest banded-MinHash buckets, largest first.

    Buckets rather than connected components, because union-find chains A to
    C through B and hands back one bucket holding most of the corpus. A
    bucket is items agreeing on four independent minima at once, which is a
    strong enough signal to propose an exemplar from — and the exemplar is
    verified afterwards anyway.
    """
    per = HASHES // BANDS
    buckets = collections.defaultdict(list)
    for i, r in enumerate(rows):
        sk = r["sketch"]
        if sk is None:
            continue
        for b in range(BANDS):
            buckets[(b, sk[b * per:(b + 1) * per])].append(i)
    return sorted(buckets.values(), key=len, reverse=True)


DIGITS = str.maketrans("0123456789,", "٠١٢٣٤٥٦٧٨٩٬")


def ar(n):
    return f"{n:,}".translate(DIGITS)


def plain(s):
    """Digits with no grouping — years are not quantities."""
    return str(s).translate(DIGITS)


def pct(a, b):
    return "—" if not b else f"{a / b * 100:.1f}٪".translate(
        str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def load_articles():
    """Every article file's key facts, and its judgment ids for co-citation."""
    index = json.loads((HERE / "index.json").read_text(encoding="utf-8"))
    rows = []
    for inst in index["by_instrument"]:
        tid = inst["track_id"]
        meta = json.loads((HERE / "instruments" / f"{tid}.json").read_text(
            encoding="utf-8"))
        for num, a in meta["articles"].items():
            rows.append((a["citations"], tid, int(num), meta["instrument"]))
    rows.sort(reverse=True)
    return rows


def judgment_sets(rows):
    """(tid, num) -> set of judgment ids, for every article in the citator."""
    out = {}
    for _, tid, num, _ in rows:
        d = json.loads((ARTS / tid / f"{num}.json").read_text(encoding="utf-8"))
        out[(tid, num)] = {e["judgment_id"] for e in d["judgments"]}
    return out


def digest(tid, num, sets, labels):
    d = json.loads((ARTS / tid / f"{num}.json").read_text(encoding="utf-8"))
    ent = d["judgments"]
    n = len(ent)
    jset = {e["judgment_id"] for e in ent}
    voices = collections.Counter(e["voice"] for e in ent)
    attribution = collections.Counter(
        e.get("attribution") for e in ent if e["voice"] == "recital")
    courts = collections.Counter(e["court"] for e in ent)
    cities = collections.Counter(e["city"] for e in ent)
    years = collections.Counter((e["hijri_date"] or "")[:4] for e in ent)

    for e in ent:
        cl, cut = clause(e["passage"], e["at"])
        e["_clause"], e["_cut"] = cl, cut
        e["_grams"] = grams(norm(cl)) if cl else frozenset()
        e["sketch"] = sketch(e["_grams"]) if cl else None

    L = []
    A = L.append
    title = f"{d['label'] or f'المادة {num}'} من {d['instrument']}"
    A(f"# {title.replace(':', '')}\n")
    A(f"**{ar(n)}** استشهادًا في **{ar(len(jset))}** حكمًا"
      f" — {d.get('legal_status') or 'حالة غير مسجَّلة'}"
      + (f" — باب: {d['section']}" if d.get("section") else "") + "\n")
    if d.get("official_text"):
        A("> " + d["official_text"].strip().replace("\n", "\n> ") + "\n")
        A("<sub>النصّ الرسمي كما هو موثَّق في ذخيرة الأنظمة.</sub>\n")
    else:
        A("<sub>لا يحمل السجلّ نصًّا رسميًّا موثَّقًا لهذه المادة، "
          "والاستشهادات أدناه من الأحكام وحدها.</sub>\n")

    A("## أين يقع الاستشهاد\n")
    A("| الموضع | العدد | النسبة |\n|---|---:|---:|")
    for v in ("reasoning", "recital", "operative", "unknown"):
        if voices[v]:
            A(f"| {VOICE_AR[v]} | {ar(voices[v])} | {pct(voices[v], n)} |")
    A("")
    if voices["recital"]:
        c = attribution["court"]
        A(f"وداخل الوقائع، **{ar(c)}** من أصل {ar(voices['recital'])} "
          f"({pct(c, voices['recital'])}) تقع في جملةٍ فاعلُها الدائرة أو "
          "المحكمة — أي أنها سرد المحكمة لإجراءٍ باشرته، لا حجّةٌ رُفعت "
          "إليها. والباقي لم يُنسب، وفيه حجج الخصوم وفيه سردٌ لم تُلتقط "
          "قرينته؛ فالرقم حدٌّ أدنى لصوت المحكمة لا قسمةٌ بينهما.\n")

    A("## المحاكم والسنوات\n")
    A("| المحكمة | العدد | | المدينة | العدد | | السنة | العدد |")
    A("|---|---:|---|---|---:|---|---|---:|")
    ys = sorted(y for y in years if y)
    top_c, top_t = courts.most_common(6), cities.most_common(6)
    rows_n = max(len(top_c), len(top_t), len(ys))
    for i in range(rows_n):
        a = f"{top_c[i][0]} | {ar(top_c[i][1])}" if i < len(top_c) else " | "
        b = f"{top_t[i][0]} | {ar(top_t[i][1])}" if i < len(top_t) else " | "
        c = f"{plain(ys[i])} | {ar(years[ys[i]])}" if i < len(ys) else " | "
        A(f"| {a} | | {b} | | {c} |")
    A("")

    appeal = collections.Counter(e.get("appeal") for e in ent)
    with_appeal = sum(v for k, v in appeal.items() if k != "no_appeal")
    if with_appeal:
        A("## مصير الأحكام أمام الاستئناف\n")
        A(f"من {ar(n)} استشهادًا بهذه المادة، **{ar(with_appeal)}** يقع في حكمٍ "
          f"يحمل السجلُّ نفسه قرار الاستئناف فيه:\n")
        A("| المآل | استشهادات | من ذوات الاستئناف |\n|---|---:|---:|")
        for k in ("affirmed", "reversed", "substituted", "varied",
                  "not_admitted", "other_disposition", "unclear"):
            if appeal[k]:
                A(f"| {APPEAL_AR[k]} | {ar(appeal[k])} | "
                  f"{pct(appeal[k], with_appeal)} |")
        A("")
        A("**واقرأ هذا الجدول على وجهه.** «أُيِّد» تعني أن ذلك الحكم بعينه صمد، "
          "لا أن ما فهمه من المادة صار مبدأً. و«نُقض» لا تعني أن المادة "
          "أُسيء تطبيقها — فقد يُنقض الحكم لسببٍ آخر فيه لا صلة له بها. "
          "والمآل مقروءٌ من منطوق حكم الاستئناف وحده، وما لم يُصرَّح به "
          "«لم يتبيّن».\n")

    for v in ("reasoning", "recital"):
        rows = [e for e in ent if e["voice"] == v and e["_clause"]]
        if len(rows) < 20:
            continue
        exemplars, covered = [], set()
        for g in cluster(rows)[:40]:
            if len(exemplars) == 3:
                break
            whole = sorted((i for i in g if not rows[i]["_cut"]),
                           key=lambda i: len(rows[i]["_clause"]))
            if not whole:
                continue
            pick = rows[whole[len(whole) // 2]]
            near = {i for i, r in enumerate(rows)
                    if jaccard(r["_grams"], pick["_grams"]) >= 0.5}
            if len(near) < 5 or (covered and
                                 len(near & covered) > len(near) / 2):
                continue
            exemplars.append((pick, len(near)))
            covered |= near
        if not exemplars:
            continue
        exemplars.sort(key=lambda x: -x[1])
        count = {1: "الصيغة", 2: "الصيغتان", 3: "الصيغ الثلاث"}[len(exemplars)]
        A(f"## الصيغ المتكررة في {VOICE_AR[v]}\n")
        A(f"من {ar(len(rows))} جملةً تحمل الاستشهاد في هذا الموضع، "
          f"تغطي {count} أدناه {pct(len(covered), len(rows))}. وكل رقمٍ "
          "منها عدد الجمل التي تشترك مع المقتبس في نصف مقاطعه الحرفية فأكثر "
          "— تشابه لفظٍ محسوب، لا وحدة معنى.\n")
        for pick, n_near in exemplars:
            A(f"**{ar(n_near)} استشهادًا بصيغةٍ كهذه** "
              f"({pct(n_near, len(rows))} من {VOICE_AR[v]}):\n")
            A("> " + pick["_clause"])
            A(f">\n> — {pick['court']} ب{pick['city']}، حكم رقم "
              f"{pick['judgment_number']}، {pick['hijri_date']}\n")

    co = []
    for key, other in sets.items():
        if key == (tid, num):
            continue
        share = len(jset & other)
        if share:
            co.append((share, key))
    co.sort(reverse=True)
    if co:
        A("## مواد يُستشهد بها في الأحكام نفسها\n")
        A("| المادة | أحكام مشتركة | من أحكام هذه المادة |\n|---|---:|---:|")
        for share, key in co[:10]:
            A(f"| {labels[key]} | {ar(share)} | {pct(share, len(jset))} |")
        A("")

    A("## حدود\n")
    A("- الأحكام المنشورة ٩٥٪ تجارية؛ فغياب محكمةٍ أو سنةٍ من الجدول أعلاه "
      "قد يعني أنها لا تنشر، لا أنها لم تطبّق المادة.\n"
      "- موضع الاستشهاد مقروءٌ من عناوين الحكم نفسه؛ وما خلا منها فموضعه "
      "«غير محدَّد» ولم يُخمَّن.\n"
      "- نسبة الوقائع المنسوبة للمحكمة قرينةٌ لفظية، صحّتها ٣٧ من ٤٠ في "
      "عيّنةٍ قُرئت باليد؛ انظر `../../arabic_paper/voice_attribution.py`.\n"
      "- كل مقطعٍ منقولٌ بنصّه من حكمه، والأسماء محجوبة `(...)`.\n")
    A(f"\n<sub>المصدر: [`articles/{tid}/{num}.json`](../articles/{tid}/{num}.json)"
      f" — يحمل الاستشهادات {ar(n)} كاملةً.</sub>\n")
    return "\n".join(L)


def main():
    OUT.mkdir(exist_ok=True)
    rows = load_articles()
    labels = {(tid, num): f"{lab} من {inst}".replace(":", "")
              for _, tid, num, inst in rows
              for lab in [f"المادة {num}"]}
    print("reading judgment ids for co-citation …", flush=True)
    sets = judgment_sets(rows)
    top = rows[:TOP]
    written = set()
    index = ["# خلاصات المواد الأكثر استشهادًا\n",
             "صفحةٌ لكل مادةٍ من العشرين الأكثر استشهادًا في الذخيرة: "
             "أين يقع الاستشهاد، ومن المتكلّم، وأي صيغةٍ تتكرر، وأي مادةٍ "
             "تسافر معها.\n",
             "| # | المادة | استشهادات | تعليل | وقائع |",
             "|---:|---|---:|---:|---:|"]
    for rank, (n, tid, num, inst) in enumerate(top, 1):
        text = digest(tid, num, sets, labels)
        name = f"{tid}__{num}.md"
        (OUT / name).write_text(text, encoding="utf-8")
        written.add(name)
        d = json.loads((ARTS / tid / f"{num}.json").read_text(encoding="utf-8"))
        v = collections.Counter(e["voice"] for e in d["judgments"])
        index.append(f"| {ar(rank)} | [{labels[(tid, num)]}]({name}) | {ar(n)} "
                     f"| {pct(v['reasoning'], n)} | {pct(v['recital'], n)} |")
        print(f"  {rank:>2}. {tid} م{num} — {n:,}", flush=True)
    for stale in OUT.glob("*.md"):
        if stale.name != "README.md" and stale.name not in written:
            stale.unlink()
    # The closing sentence quotes two of the table's own cells. It used to type
    # them, and they went stale the moment the citation pattern was corrected:
    # the table above said 83.2 and 2.4 while the sentence below said 82.9 and
    # 2.2. A generated page that hand-types a figure it just generated is worse
    # than one that never generated it, because the reader trusts it.
    d90 = json.loads((ARTS / "commercial_courts_implementing_regulation" /
                      "90.json").read_text(encoding="utf-8"))
    n90 = d90["citations"]
    v90 = collections.Counter(e["voice"] for e in d90["judgments"])
    index.append("\nوالترتيب بعدد الاستشهادات، والعدد ليس أهمية. فالمادة "
                 "التسعون — الجلسة التحضيرية — يقع "
                 f"{pct(v90['recital'], n90)} من استشهاداتها في سرد الوقائع و"
                 f"{pct(v90['reasoning'], n90)} في التعليل: مادةٌ يكثر وصفُ "
                 "إعمالها، لا مادةٌ تدور عليها الخصومة. وعمود «تعليل» أصدق "
                 "من عمود «استشهادات».\n")
    (OUT / "README.md").write_text("\n".join(index), encoding="utf-8")


if __name__ == "__main__":
    main()
