#!/usr/bin/env python3
"""Check a draft pleading against what the published record actually shows.

A lawyer drafting a claim relies on articles and on judgments. Both can be
relied on badly, and neither mistake is visible while writing:

  an article that no published judgment has ever applied
  an article number the instrument does not have
  an article the courts recite in procedural narration and almost never
      reason from — cited as though it were a rule the bench applies
  a judgment relied on by number that was reversed on appeal
  the articles that travel with the ones cited, and are missing here

Every one of those is a question about the record, and the record is on disk.
So the same extractor that read fifty thousand judgments is turned around and
pointed at the draft: the citations are pulled out of the lawyer's own text,
matched to instrument and article, and looked up.

WHAT THIS IS NOT. It gives no opinion on the merits, does not say whether a
citation is apt, and never writes a sentence about what a court meant. It
reports counts, quotes judgments verbatim, and names its own limits: the
corpus is what the Ministry publishes, 95 per cent of it commercial, so
«no judgment cites this» means «none in the published record», which is a
different thing from «never applied».

    python3 check_brief.py draft.txt [--out report.md]
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ANALYSIS = HERE.parent / "arabic_paper"
CITATOR = HERE.parent / "citator"
INDEX = HERE / "index"
sys.path.insert(0, str(ANALYSIS))

import arabic_ordinals as A         # noqa: E402
import match_instruments as M       # noqa: E402
import voice_attribution as V       # noqa: E402

REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
SIZES = ANALYSIS / "applied_articles_results.json"

# «الحكم رقم ٤٤٣٠١٥٨٣٠٤», «القضية رقم (2711)», «الصك رقم 439243491»
JUDGMENT_REF = re.compile(
    r"(?:الحكم|حكم|القضية|قضية|الصك|صك)\s*(?:رقم)?\s*[:：]?\s*"
    r"[\(\[]?\s*([0-9٠-٩][0-9٠-٩/\-]{1,19})\s*[\)\]]?")

APPEAL_AR = {"affirmed": "أُيِّد", "reversed": "نُقض أو أُلغي",
             "substituted": "أُلغي وحُكم مجددًا", "varied": "عُدِّل",
             "not_admitted": "لم يُقبل الاعتراض شكلًا",
             "other_disposition": "فُصل على وجهٍ آخر",
             "unclear": "لم يتبيّن من المنطوق",
             "no_appeal": "لا استئناف في السجلّ"}
DIGITS = str.maketrans("0123456789,", "٠١٢٣٤٥٦٧٨٩٬")


def clean_label(label, num):
    return (label or f"المادة {num}").rstrip(" :：").strip()


def ar(n):
    return f"{n:,}".translate(DIGITS)


def pct(a, b):
    return "—" if not b else f"{a / b * 100:.0f}٪".translate(DIGITS)


def load():
    articles = json.loads((INDEX / "articles.json").read_text(encoding="utf-8"))
    judgments = json.loads((INDEX / "judgments.json").read_text(encoding="utf-8"))
    sizes = json.loads(SIZES.read_text(encoding="utf-8"))["instrument_sizes"]
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))["tracks"]
    reg = list(reg.values()) if isinstance(reg, dict) else reg
    names = {t["track_id"]: t.get("display_name_ar") or t["track_id"]
             for t in reg}
    return articles, judgments, sizes, names


def flatten(text):
    """Collapse the draft's line breaks before extraction.

    The citation pattern deliberately refuses to run across a newline, which
    is right for judgments — the collector had already collapsed their
    whitespace — and wrong for a draft, where «المادة الخامسة والستين بعد\n
    الأربعمائة» wraps in the middle of the citation and is silently missed.
    Two articles vanished from the first run of this tool for that reason.
    """
    return " ".join(text.split())


def cited_articles(text, index, order):
    """Every «المادة … من نظام …» in the draft, matched and parsed."""
    out = collections.Counter()
    unmatched, unparsed = collections.Counter(), collections.Counter()
    last = M.Recent()
    for m in V.CITE.finditer(text):
        tid, kind = M.match(m.group(2), index, order, last)
        if kind == "named":
            last.note(tid)
        if not tid:
            unmatched[" ".join(m.group(2).split())[:40]] += 1
            continue
        num, _ = A.parse(m.group(1))
        if num is None:
            unparsed[" ".join(m.group(1).split())[:30]] += 1
            continue
        out[f"{tid}/{num}"] += 1
    return out, unmatched, unparsed


def voice_note(a):
    """What the voice profile says about how this article is used."""
    v = a["by_voice"]
    total = sum(v.values())
    reasoning = v.get("reasoning", 0)
    recital = v.get("recital", 0)
    if not total:
        return None
    if reasoning / total < 0.10 and recital / total > 0.50:
        return ("**انتبه.** هذه المادة تظهر في سرد الوقائع أكثر مما تظهر في "
                f"التعليل: {pct(recital, total)} وقائع مقابل "
                f"{pct(reasoning, total)} تعليلًا. أي أن المحاكم تصف إعمالها "
                "أكثر مما تبني عليها قضاءها، فالاستناد إليها كقاعدةٍ "
                "موضوعية ضعيف.")
    if reasoning / total > 0.60:
        return (f"مادةٌ تُبنى عليها الأحكام: {pct(reasoning, total)} من "
                "استشهاداتها في تعليل المحكمة.")
    return None


def article_block(key, count, a, sizes, L):
    A_ = L.append
    tid, num = key.rsplit("/", 1)
    A_(f"### {clean_label(a['label'], num)} — {a['instrument']}\n")
    A_(f"وردت في مذكرتك **{ar(count)}** مرة."
       + (f" باب: {a['section']}." if a.get("section") else "")
       + (f" حالتها: {a['legal_status']}." if a.get("legal_status") else "")
       + "\n")
    if a.get("official_text"):
        A_("> " + a["official_text"].strip().replace("\n", "\n> ") + "\n")
    v = a["by_voice"]
    total = sum(v.values())
    A_(f"**في السجلّ:** {ar(a['citations'])} استشهادًا في "
       f"{ar(a['judgments'])} حكمًا — تعليل {pct(v.get('reasoning', 0), total)}"
       f" · وقائع {pct(v.get('recital', 0), total)}"
       f" · منطوق {pct(v.get('operative', 0), total)}"
       f" · غير محدَّد {pct(v.get('unknown', 0), total)}\n")
    note = voice_note(a)
    if note:
        A_(note + "\n")
    ap = a.get("by_appeal") or {}
    with_appeal = sum(c for k, c in ap.items() if k != "no_appeal")
    if with_appeal:
        parts = [f"{APPEAL_AR[k]} {pct(ap[k], with_appeal)}"
                 for k in ("affirmed", "reversed", "substituted",
                           "not_admitted")
                 if ap.get(k)]
        A_(f"**مصير الأحكام المطبِّقة لها** (من {ar(with_appeal)} استشهادًا "
           f"في أحكامٍ استُؤنفت): " + " · ".join(parts) + "\n")
    A_(f"<sub>التفصيل الكامل في "
       f"[`citator/{a['file']}`](../citator/{a['file']}).</sub>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", help="the draft pleading, as plain text")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    text = Path(args.draft).read_text(encoding="utf-8")
    index, order = M.build(REGISTRY)
    articles, judgments, sizes, names = load()
    cited, unmatched, unparsed = cited_articles(flatten(text), index, order)

    L = ["# فحص مذكّرة\n",
         f"المصدر: `{Path(args.draft).name}` — "
         f"{ar(len(text.split()))} كلمة.\n"]

    L.append("## المواد التي استندتَ إليها\n")
    if not cited:
        L.append("لم يُعثر على استشهادٍ نظاميٍّ بصيغة «المادة … من نظام …».\n")
    known = [(c, k) for k, c in cited.items() if k in articles]
    absent = [(c, k) for k, c in cited.items() if k not in articles]
    for count, key in sorted(known, reverse=True):
        article_block(key, count, articles[key], sizes, L)

    if absent:
        L.append("## مواد لم يستشهد بها قاضٍ في السجلّ\n")
        for count, key in sorted(absent, reverse=True):
            tid, num = key.rsplit("/", 1)
            size = sizes.get(tid)
            L.append(f"- **{names.get(tid, tid)} — المادة {num}** "
                     f"(وردت {ar(count)} مرة)"
                     + (f" — والأداة تضمّ {ar(size)} مادة"
                        + ("، فالرقم خارج نطاقها." if size and int(num) > size
                           else ", والرقم داخل نطاقها.")
                        if size else ""))
        L.append("\nوغياب المادة من السجلّ **لا يعني أنها لم تُطبَّق قط**، بل "
                 "أنها لم تظهر في الأحكام المنشورة — وهي ٩٥٪ تجارية. لكنه "
                 "يعني أنك لن تجد لها سندًا قضائيًّا منشورًا تحيل إليه.\n")

    refs = collections.Counter(
        m.group(1).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
        for m in JUDGMENT_REF.finditer(flatten(text)))
    found = {r: judgments[r] for r in refs if r in judgments}
    if refs:
        L.append("## الأحكام التي أحلتَ إليها\n")
        if not found:
            L.append("لم يُطابَق أيٌّ من أرقام الأحكام الواردة في المذكّرة "
                     "بسجلٍّ في الذخيرة.\n")
        for num, rows in found.items():
            L.append(f"**حكم {num}** — "
                     + ("سجلّان أو أكثر يحملان هذا الرقم:\n" if len(rows) > 1
                        else ""))
            for r in rows:
                warn = ("  ⚠️ **" if r["appeal"] in
                        ("reversed", "substituted") else "  ")
                L.append(f"{warn}{r['court']} ب{r['city']}، {r['date']} — "
                         f"{APPEAL_AR.get(r['appeal'], r['appeal'])}"
                         + ("**" if warn.strip().startswith("⚠️") else ""))
            L.append("")
        missing = [r for r in refs if r not in judgments]
        if missing:
            L.append(f"ولم تُطابَق: {'، '.join(missing[:10])} — وقد تكون "
                     "أرقام قضايا لا أرقام أحكام، أو من خارج الذخيرة.\n")

    seen = set(cited)
    near = collections.Counter()
    for key in cited:
        for nb in articles.get(key, {}).get("neighbours", []):
            if nb["key"] not in seen:
                near[nb["key"]] = max(near[nb["key"]], nb["share"])
    if near:
        L.append("## موادّ تسير عادةً مع ما استشهدتَ به، ولم ترد عندك\n")
        L.append("| المادة | تظهر مع مادةٍ من موادك في |\n|---|---:|")
        for key, share in near.most_common(8):
            a = articles[key]
            L.append(f"| {clean_label(a['label'], a['article_number'])} — "
                     f"{a['instrument']} | "
                     f"{pct(int(share * 100), 100)} من أحكامها |")
        L.append("\nوهذه ملاحظةُ تواردٍ في السجلّ، لا توصيةٌ قانونية: قد يكون "
                 "غيابها عن مذكّرتك صوابًا.\n")

    if unmatched or unparsed:
        L.append("## ما تعذّر على الأداة قراءته\n")
        for name, c in unmatched.most_common(5):
            L.append(f"- اسم أداة لم يُطابَق: «{name}» ({ar(c)})")
        for expr, c in unparsed.most_common(5):
            L.append(f"- رقم مادة لم يُقرأ: «{expr}» ({ar(c)})")
        L.append("")

    L.append("---\n")
    L.append("<sub>هذا الفحص يَعُدّ ويقتبس، ولا يُفتي. الذخيرة هي ما تنشره "
             "وزارة العدل — ٥٠٬٦٦٦ حكمًا، ٩٥٪ منها تجارية — فما لا يظهر فيها "
             "قد يكون مطبَّقًا في محاكم لا تُنشر أحكامها. ومصير الاستئناف "
             "مقروءٌ من منطوق حكم الاستئناف حيث حمله السجلّ.</sub>\n")

    report = "\n".join(L)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
