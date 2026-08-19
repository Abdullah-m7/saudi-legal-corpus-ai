#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The instruments this corpus is missing, named by their own amending decrees.

A FOURTH DISCOVERY CHANNEL, AND THE MOST PRECISE ONE. This repository already
looks for what it is missing three ways: it asks official portals what exists, it
sweeps the gazette archive, and it reads its own held regulations for a «النظام:
…» clause naming a parent it does not hold. Each yields a NAME. A name is a weak
handle — titles are shortened, reworded, and shared between an instrument and its
implementing regulation.

This channel yields a name AND its issuing decree AND that decree's date, because
that is how a Saudi amending decree is written. Every one of them opens by
reciting what it is amending:

    وبعد الاطلاع على تنظيم الهيئة السعودية للمقاولين، الصادر بقرار مجلس الوزراء
    رقم (510) وتاريخ 23/11/1436هـ.

That single line is the strongest form a coverage gap can take. «This corpus is
missing something called roughly X» can be argued with; «this corpus is missing
تنظيم الهيئة السعودية للمقاولين, issued by Council of Ministers Decision 510 of
23/11/1436H» can be looked up, requested from the issuing body, or matched
against any other source — and it can be checked against what the corpus DOES
hold on the decree number alone, which no title-matcher can do.

HOW IT WAS FOUND, WHICH IS THE POINT. Not by design. The repeal sweep listed the
notices that matched no held track instead of dropping them, and one of them —
«إلغاء المادة الخامسة عشرة من تنظيم هيئة المدن والمناطق الاقتصادية الخاصة» — was
not a repeal of anything held at all. Its own text named the missing parent of
nine held special-economic-zone tracks, with its royal order and date. This
audit generalises that accident: of the 533 amendment-shaped notices in the
archive, 308 name no held track, and 201 of those name an INSTRUMENT TYPE, so
their preambles should each recite an instrument the corpus may not have.

WHAT IS FILTERED, AND WHY THE FILTER IS NARROW. A preamble recites everything the
decision looked at: the Basic Law of Governance, committee recommendations,
memoranda, telegrams. Only a recital whose subject BEGINS with an instrument type
word is kept, and recitals naming a recommendation/memorandum/telegram are
dropped by name. The rest is reported as extracted, without interpretation.

AND WHAT A HIT DOES NOT MEAN. That the corpus does not hold an instrument under
that title is a statement about titles until the decree number is checked too,
which is why both are recorded and both are compared. An instrument may also be
deliberately out of scope. Nothing here is a to-do list; it is a measured,
citable inventory of what the corpus can prove it lacks.

Network: fetches only uqn.gov.sa/details pages, which robots.txt permits, and
only pages already present in this corpus's own harvested index. Retries only on
transport errors, never on an HTTP status. Exit 0; an audit, not a gate.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "reports", "gazette_ingestion_backlog",
                     "gazette_title_index.json")
OUT = os.path.join(ROOT, "reports", "named_but_unheld_instruments",
                   "named_but_unheld_instruments.json")

# A recital: «وبعد الاطلاع على <subject>، الصادر بـ<issuing instrument>.»
RECITAL_RE = re.compile(
    r"وبعد\s+الاطلاع\s+على\s+(.{6,150}?)[،,]?\s*الصادر\s*(?:ة|بـ)?\s*(?:ب)?(?:موجب\s*)?"
    r"([^\n]{6,120}?)\s*[.،]")
# Only a subject that BEGINS with an instrument type word is an instrument.
TYPE_HEAD_RE = re.compile(
    r"^(?:ال)?(?:نظام|تنظيم|لائحة|اللائحة|قواعد|القواعد|ضوابط|الضوابط|تعليمات|"
    r"التعليمات|الترتيبات|النظام\s+الأساس)")
# A preamble recites these too, and none of them is an instrument.
NOT_AN_INSTRUMENT_RE = re.compile(r"توصية|مذكرة|برقية|المعاملة|محضر|خطاب")
# The gazette writes «(م/ 4)» and «(م/25)» and «رقم 70273» — the number may carry
# spaces INSIDE the parentheses. A pattern that stopped at the first space read
# «(م/ 4)» as «م/», which has no digits, so every royal decree written that way was
# reported as missing no matter what the corpus holds. A parenthesised number is
# read to its closing bracket; only an unbracketed one stops at whitespace.
DECREE_NUM_RE = re.compile(r"رقم\s*\(\s*([^)\n]{1,16}?)\s*\)|رقم\s*([^\s,،.]{1,12})")
DATE_RE = re.compile(r"وتاريخ\s*([0-9\s/]{6,16})هـ")

# Recited titles that ARE held, under a title the decree writes differently.
# Adjudicated by hand and named here rather than absorbed by a similarity
# threshold: a threshold that swallowed this one would swallow «تنظيم الهيئة
# السعودية للمحامين» too, which scores the same against «تنظيم الهيئة السعودية
# للسياحة» and is a genuinely different authority. Claiming a gap that is not
# there is the same error as missing one, pointing the other way.
HELD_UNDER_A_VARIANT_TITLE = {
    "اللائحة التنفيذية لنظام العمل وملحقاتها":
        "held as labor_regulation, with its five annexes as their own tracks "
        "(labor_annex1..5) — the decree recites the regulation AND its annexes "
        "as one title, which this corpus stores as six",
}


def _mod(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(ROOT, "scripts", "%s.py" % name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def page_body(fetcher, uid):
    url = ("https://www.uqn.gov.sa/details?p=%s" % uid if not uid.startswith("400")
           else "https://www.uqn.gov.sa/decisions-and-regulations/%s" % uid)
    raw = fetcher(url)
    if not raw:
        return None, url
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t)
    i = max(t.find("بعون الله"), t.find("قرار رقم"), t.find("إن مجلس الوزراء"))
    return (t[i:i + 4000] if i > 0 else t[:4000]), url


def _digits(s):
    return tuple(int(x) for x in re.findall(r"\d+", s or ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=0, help="stop after N pages")
    args = ap.parse_args()

    cur = _mod("audit_corpus_currency")
    net = _mod("refresh_gazette_title_index")
    index = json.load(open(INDEX, encoding="utf-8"))["index"]
    tracks = cur.track_editions()
    held_toks = {tid: cur.toks(a) for tid, (a, _d, _e, _p) in tracks.items()}
    held_titles = {cur.norm_ar(a): tid for tid, (a, _d, _e, _p) in tracks.items()}

    # The decree number each held track records AS ITS OWN — read from the fields
    # that state a track's issuing instrument, never from the whole file.
    #
    # Reading the whole file was tried first and it hid a real gap: تنظيم الهيئة
    # العامة للمنشآت الصغيرة والمتوسطة, issued by Decision (301), was reported as
    # already held because the string «رقم (301)» appears INCIDENTALLY in two
    # unrelated artifacts — a number cited in passing inside some other law's text.
    # A coverage audit that errs toward "we already have it" is worse than useless;
    # it manufactures the silence it is supposed to break.
    held_decrees = {}
    for tid, (_a, _d, _e, path) in tracks.items():
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):                                 # noqa: BLE001
            continue
        own = " ".join(str(doc.get(k) or "") for k in
                       ("decree", "decree_number", "legal_basis_ar",
                        "issuing_authority_ar", "decree_date_hijri"))
        for num in re.findall(r"رقم\s*\(?\s*([^)\s\"]{1,12})\s*\)?", own):
            held_decrees.setdefault(_digits(num), set()).add(tid)

    targets = []
    for uid, v in index.items():
        title = v.get("title") or ""
        if not cur.AMENDMENT_RE.search(title):
            continue
        nt = cur.toks(title)
        if len(nt) < cur.MIN_SHARED:
            continue
        if not cur.notice_subject_types(title):
            continue
        if any(tt and len(cur.shared_words(nt, tt)) >= cur.MIN_SHARED
               and len(cur.shared_words(nt, tt)) / len(tt) >= cur.MIN_TRACK_COVER
               for tt in held_toks.values()):
            continue
        targets.append((v.get("date", ""), uid, title))
    targets.sort()
    if args.limit:
        targets = targets[:args.limit]
    print("amendment notices naming an instrument type and NO held track: %d"
          % len(targets))

    found, unreachable = {}, []
    for n, (date, uid, title) in enumerate(targets, 1):
        body, url = page_body(net.fetch_page, uid)
        if not body:
            unreachable.append({"page_id": uid, "date": date, "title_ar": title})
            continue
        for subject, issued_by in RECITAL_RE.findall(body):
            subject = subject.strip()
            if NOT_AN_INSTRUMENT_RE.search(subject) or not TYPE_HEAD_RE.match(subject):
                continue
            nm = DECREE_NUM_RE.search(issued_by)
            num = (nm.group(1) or nm.group(2)) if nm else None
            dt = DATE_RE.search(issued_by)
            if subject in HELD_UNDER_A_VARIANT_TITLE:
                continue
            key = cur.norm_ar(subject)
            e = found.setdefault(key, {
                "instrument_ar": subject,
                "issued_by_ar": issued_by.strip(),
                "decree_number": num,
                "decree_date_hijri": dt.group(1).strip() if dt else None,
                "named_by_notices": [],
            })
            e["named_by_notices"].append(
                {"date": date, "page_id": uid, "url": url, "notice_title_ar": title})
        if n % 25 == 0:
            print("  %d/%d fetched, %d instrument(s) named so far"
                  % (n, len(targets), len(found)), flush=True)

    # is it held? by title, or by its decree number
    for key, e in found.items():
        e["held_by_title"] = held_titles.get(key)
        d = _digits(e["decree_number"])
        e["tracks_recording_that_decree_number"] = sorted(held_decrees.get(d, ())) if d else []
        e["held"] = bool(e["held_by_title"]) or bool(e["tracks_recording_that_decree_number"])

    # A claimed gap must be adjudicable. For every instrument reported as not held,
    # the closest held track is named with its overlap, because «the corpus does not
    # hold this title» and «the corpus does not hold this instrument» are different
    # sentences: «اللائحة التنفيذية لنظام العمل وملحقاتها» is the held Labor
    # Implementing Regulation with three words added, and reporting it as missing
    # would be a fabricated gap — the same error as a missed one, pointing the other way.
    for e in found.values():
        nt = cur.toks(e["instrument_ar"])
        best = (0.0, None, None)
        for tid, (a, _d, _e2, _p) in tracks.items():
            tt = held_toks.get(tid)
            if not tt:
                continue
            j = len(cur.shared_words(nt, tt)) / max(1, len(nt | tt))
            if j > best[0]:
                best = (round(j, 2), tid, a)
        e["nearest_held_track"] = {"jaccard": best[0], "track_id": best[1],
                                   "title_ar": best[2]}

    # WHO DEPENDS ON WHAT IS MISSING. An inventory is a list; a dependency is a
    # reason. For each instrument not held, the held artifacts that NAME it are
    # recorded, and any of those whose parent law the cross-reference graph could
    # not resolve is flagged — acquiring one such instrument closes that track's
    # parent reference.
    #
    # Matched on the NAME only. A first pass also matched on the decree number and
    # reported 18 instruments as depended-upon; matching on the name alone reports
    # 4. The difference was entirely decision numbers cited IN PASSING inside other
    # laws' text — «قرار مجلس الوزراء رقم (487)» appearing in an artifact about
    # liquefied gas does not mean that artifact depends on تنظيم دارة الملك
    # عبدالعزيز. This is the same trap the held-test fell into a few lines above,
    # sprung a second time in the same audit and in the opposite direction: there it
    # invented coverage, here it invented dependency. A bare number is not a citation.
    art_blobs = []
    for tid, (_a, _d, _e, path) in tracks.items():
        try:
            art_blobs.append((tid, open(os.path.join(ROOT, path), encoding="utf-8").read()))
        except OSError:
            continue
    unresolved, stranded = set(), {}
    graph_path = os.path.join(ROOT, "data", "corpus_cross_reference_graph",
                              "corpus_cross_reference_graph.json")
    if os.path.exists(graph_path):
        graph = json.load(open(graph_path, encoding="utf-8"))
        unresolved = set(graph.get("parent_law_resolution", {}).get("unresolved_tracks", []))
        for r in graph.get("references", []):
            if r.get("type") == "parent_law_unresolved":
                stranded[r["source_track_id"]] = stranded.get(r["source_track_id"], 0) + 1
    for e in found.values():
        key = e["instrument_ar"].strip()[:34]
        named_by = sorted({tid for tid, blob in art_blobs if key in blob})
        parents = [t for t in named_by if t in unresolved]
        e["named_by_held_artifacts"] = named_by
        e["would_resolve_the_parent_of"] = parents
        e["stranded_references_it_would_close"] = sum(stranded.get(t, 0) for t in parents)

    missing = [e for e in found.values() if not e["held"]]
    with_id = [e for e in missing if e["decree_number"] and e["decree_date_hijri"]]
    missing.sort(key=lambda e: (-len(e.get("named_by_held_artifacts") or []),
                                -len(e["named_by_notices"])))

    print("\ninstruments recited by those notices:        %d" % len(found))
    print("  already held (by title or decree number):  %d" % (len(found) - len(missing)))
    print("  NOT held:                                  %d" % len(missing))
    print("  of those, named WITH decree number + date: %d" % len(with_id))
    print("  pages unreachable:                         %d" % len(unreachable))
    depended = [e for e in missing if e["named_by_held_artifacts"]]
    print("  NOT held AND named by a held artifact:     %d" % len(depended))
    print("  ...of which an unresolved parent:          %d"
          % sum(1 for e in depended if e["would_resolve_the_parent_of"]))
    for e in missing[:25]:
        print("\n  %d notice(s) | %s" % (len(e["named_by_notices"]), e["instrument_ar"][:88]))
        print("       %s" % (e["issued_by_ar"][:96]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "**قناةُ اكتشافٍ رابعة، وهي أدقُّها**. القنواتُ الثلاث السابقة تُخرج **اسماً**، "
            "والاسمُ مقبضٌ ضعيف: العناوين تُختصر وتُعاد صياغتُها وتشترك بين الأداة ولائحتها "
            "التنفيذية. **وهذه تُخرج الاسمَ ورقمَ الإصدار وتاريخَه معاً**، لأن المرسوم "
            "المعدِّل يفتتح دائماً بذكر ما يعدِّله: «وبعد الاطلاع على تنظيم الهيئة السعودية "
            "للمقاولين، الصادر بقرار مجلس الوزراء رقم (510) وتاريخ 23/11/1436هـ». "
            "**وهذا أقوى شكلٍ تتّخذه فجوةُ تغطية**: «ينقصه شيءٌ اسمه تقريباً كذا» يُجادَل "
            "فيها، و«ينقصه تنظيمُ الهيئة السعودية للمقاولين الصادر بالقرار (510) وتاريخ "
            "23/11/1436هـ» **تُطلَب من جهة الإصدار وتُقابَل برقم القرار وحده** — وهو ما لا "
            "يستطيعه مطابِقُ عناوين. **وكيف وُجدت القناة؟ بالمصادفة**: مسحُ الإلغاءات سرد "
            "ما لم يُطابق بدل أن يُسقطه، فكان أحدُها يسمّي **النظامَ الأمّ** لتسعة مسارات "
            "محمولة. **وما لا يعنيه الوجود هنا**: أن المستودع لا يحمل عنواناً ليس حكماً "
            "نهائياً حتى يُقابَل رقمُ القرار أيضاً — ولذلك يُسجَّلان معاً ويُقابَلان معاً."),
        "amendment_notices_probed": len(targets),
        "instruments_recited": len(found),
        "already_held": len(found) - len(missing),
        "not_held": len(missing),
        "not_held_with_a_decree_number_and_date": len(with_id),
        "pages_unreachable": unreachable,
        "held_under_a_variant_title": HELD_UNDER_A_VARIANT_TITLE,
        "instruments": missing,
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
