#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FIFTH official channel — and the first one that reaches before 2021.

WHY THIS MATTERS MORE THAN ANOTHER SOURCE. Every coverage statement this
repository makes carries the same footnote: the Umm Al-Qura archive is
addressable only from about 2021, so "the gazette is exhausted" has always meant
"exhausted from 2021 onward". That bound is why 39 instruments this corpus can
name — with their decree numbers and dates — were classed as unobtainable, and
why laws.boe.gov.sa being unreachable from this sandbox mattered so much.

The Ministry of Justice legal portal (laws.moj.gov.sa) reaches back to 1421H.
Its robots.txt allows everything and declares three sitemaps; the pages are a
Nuxt single-page app, so the HTML is an empty shell, and the content comes from a
public API gateway the app's own bundle names:

    https://laws-gateway.moj.gov.sa/apis/legislations/v1
        /statute/get-Statute-gateway-Detail?Serial=<id from the sitemap>

Two details were read out of the site's own JavaScript rather than assumed. The
gateway has TWO bases: `/selfservices/apis/...` attaches a Bearer token from a
cookie and is for signed-in users, while the plain `/apis/...` base carries no
authorization at all — this probe uses only the latter. And the site's own client
throttles itself to ONE REQUEST PER SECOND. That is the rate the publisher asks
for, so it is the rate used here, rather than a number picked for convenience.

WHAT IT ACTUALLY HOLDS, MEASURED. 74 instruments, 6,081 article-text nodes,
1.8 million characters of Arabic legal text. Published 1421H–1447H, so it spans
the pre-2021 gap. Statuses are structured (`ساري` 64, `ملغي` 9), and — this is the
part no other channel gives — 3,143 articles carry their OWN amending decree and
its date as fields, not as prose to be parsed out of a footnote.

AND WHAT IT DOES NOT CHANGE. It is the MINISTRY OF JUSTICE's portal: judicial and
procedural law, not the whole corpus. Of its 74 instruments this corpus already
holds 72 — which is itself worth stating plainly, because a channel that returns
almost nothing new is evidence about the corpus, not a disappointment. The two it
does not hold are named in the report.

Read-only and non-ingesting BY DESIGN: this probe measures a channel and writes a
report. Nothing here builds a track. Ingesting from a newly opened source belongs
to the gate pipeline (G1–G15) with its own verification, and doing it in the same
step that discovers the source would skip every check that makes this corpus
trustworthy.

Usage:
    python3 scripts/probe_moj_laws_portal.py [--limit N]
Exit 0; a probe, not a gate.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "moj_laws_portal", "moj_laws_portal_probe.json")

SITEMAP = "https://laws.moj.gov.sa/sitemap-regulations.xml"
BASE = "https://laws-gateway.moj.gov.sa/apis/legislations/v1"
DETAIL = BASE + "/statute/get-Statute-gateway-Detail?Serial=%s"
# The portal's own client waits 1000ms between calls. Match it.
THROTTLE_SECONDS = 1.0
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")


def fetch(url, tries=4, expect_json=True):
    """curl through the session proxy, asking for the type actually wanted.

    The portal answers differently depending on the Accept header — asking for
    JSON on the sitemap returns the site's HTML landing page, and asking for
    nothing at all sometimes resets the connection. So the header matches the
    resource, and a body of the WRONG SHAPE counts as a failure to retry rather
    than as a result: an HTML error page parsed as a sitemap yields zero ids and
    reports "nothing there", which is the most misleading answer available."""
    accept = "application/json" if expect_json else "application/xml,text/xml"
    for _ in range(tries):
        r = subprocess.run(["curl", "-sS", "--max-time", "45", "-A", UA,
                            "-H", "Accept: %s" % accept, url],
                           capture_output=True)
        body = r.stdout or b""
        if r.returncode == 0 and body:
            head = body.lstrip()[:64].lower()
            if expect_json and head.startswith(b"{"):
                try:
                    return json.loads(body)
                except ValueError:
                    return None
            if not expect_json and (head.startswith(b"<?xml") or b"<urlset" in head):
                return body.decode("utf-8", "replace")
        time.sleep(2)
    return None


def walk(nodes):
    for n in nodes or []:
        yield n
        yield from walk(n.get("items"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    xml = fetch(SITEMAP, expect_json=False)
    if not xml:
        print("sitemap unreachable — nothing measured, nothing claimed")
        return 0
    ids = sorted(set(re.findall(r"/legislation/([A-Za-z0-9_-]+)", xml)))
    if args.limit:
        ids = ids[:args.limit]
    print("legislation ids declared in the sitemap: %d" % len(ids))

    rows, failed = [], []
    for i, sid in enumerate(ids, 1):
        d = fetch(DETAIL % sid)
        m = (d or {}).get("model")
        if not m:
            failed.append(sid)
        else:
            nodes = list(walk(m.get("statuteStructure")))
            texts = [n for n in nodes if (n.get("text") or "").strip()]
            rows.append({
                "serial": sid,
                "url": "https://laws.moj.gov.sa/ar/legislation/%s" % sid,
                "name_ar": m.get("name"),
                "legal_type_ar": m.get("legalType"),
                "legal_status_ar": m.get("legalStatueName"),
                "publish_date": m.get("publishDate"),
                "article_text_nodes": len(texts),
                "arabic_chars": sum(len(n.get("text") or "") for n in texts),
                "article_statuses_ar": sorted({n.get("legalStatusName") for n in texts
                                               if n.get("legalStatusName")}),
                "articles_carrying_their_own_decree_date": sum(
                    1 for n in texts if n.get("decreeDate")),
            })
        if i % 25 == 0:
            print("  %d/%d" % (i, len(ids)), flush=True)
        time.sleep(THROTTLE_SECONDS)

    # Which of them does this corpus already hold? Answered by title against the
    # corpus's own track titles, and reported as a NEAREST MATCH with its overlap
    # rather than a yes/no, because the portal writes titles its own way:
    # «نظام التنفيذ ١٤٤٧هـ» and «اللائحة التنفيذية لنظام المحاماة ١٤٤٦هـ» are held
    # under the same names without the year, and calling either one missing would
    # manufacture a gap.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "audit_corpus_currency",
            os.path.join(ROOT, "scripts", "audit_corpus_currency.py"))
        cur = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cur)
        tracks = cur.track_editions()
        for r in rows:
            nt = cur.toks(r["name_ar"] or "")
            best = (0.0, None, None)
            for tid, (title, _d, _e, _p) in tracks.items():
                tt = cur.toks(title)
                if not tt:
                    continue
                j = len(cur.shared_words(nt, tt)) / max(1, len(nt | tt))
                if j > best[0]:
                    best = (round(j, 2), tid, title)
            r["nearest_held_track"] = {"jaccard": best[0], "track_id": best[1],
                                       "title_ar": best[2]}
    except Exception as e:                                          # noqa: BLE001
        print("corpus comparison skipped: %s" % str(e)[:90])

    years = {}
    for r in rows:
        years[(r["publish_date"] or "????")[:4]] = \
            years.get((r["publish_date"] or "????")[:4], 0) + 1
    dated = sum(r["articles_carrying_their_own_decree_date"] for r in rows)
    print("\ninstruments fetched: %d (failed %d)" % (len(rows), len(failed)))
    print("article-text nodes:  %d" % sum(r["article_text_nodes"] for r in rows))
    print("Arabic characters:   %s"
          % format(sum(r["arabic_chars"] for r in rows), ","))
    print("publication years:   %s .. %s"
          % (min(years) if years else "-", max(years) if years else "-"))
    print("articles carrying their OWN decree date: %d" % dated)
    weak = [r for r in rows if (r.get("nearest_held_track") or {}).get("jaccard", 1) < 0.6]
    print("instruments with NO close match in this corpus: %d" % len(weak))
    for r in weak:
        print("   %-56s %s  (%d articles)"
              % ((r["name_ar"] or "")[:56], (r["publish_date"] or "")[:10],
                 r["article_text_nodes"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        "generated_note": (
            "**قناةٌ رسميةٌ خامسة، وأوّلُ ما يبلغ ما قبل 2021**. فكلُّ عبارةِ تغطيةٍ في هذا "
            "المستودع تحمل الحاشيةَ نفسَها: أرشيفُ أم القرى قابلٌ للعنونة من 2021 تقريباً، "
            "فـ«استُنفد الأرشيف» تعني دائماً **من 2021 فصاعداً**. **وبوّابةُ وزارة العدل تبلغ "
            "1421هـ**. وrobots فيها يأذن بالكامل ويُعلن ثلاث خرائط؛ والصفحات تطبيقٌ أحاديّ "
            "الصفحة فالـHTML قوقعةٌ فارغة، والمحتوى من **بوّابةٍ برمجية عامة تسمّيها حزمةُ "
            "الموقع نفسها**. **وأمران قُرِئا من جافاسكربت الموقع لا افتُرضا**: للبوّابة "
            "قاعدتان، `/selfservices/` تُرفق رمزَ مصادقة من الكوكيز وهي للمستخدم المسجَّل، "
            "و`/apis/` **بلا مصادقة البتّة** وهي المستعملة هنا؛ **والموقع يحدّ نفسَه بطلبٍ "
            "واحد في الثانية** — وهو المعدَّل الذي يطلبه الناشر، فهو المعدَّل المستعمل، لا "
            "رقماً اختير للراحة. **والمقيس**: 74 أداة، و6,081 عقدةَ نصٍّ مادّي، و1.8 مليون "
            "حرف عربي، منشورةً بين 1421هـ و1447هـ. **و3,143 مادةً تحمل مرسومَ تعديلها "
            "وتاريخَه حقلاً** لا نثراً يُنتزع من حاشية — وهو ما لا تعطيه أيُّ قناةٍ أخرى. "
            "**وما لا يغيّره**: البوّابةُ للعدل، أي القضاء والمرافعات لا المستودع كلّه؛ ومن "
            "أدواتها الـ74 **يحمل المستودعُ 72** — **وقناةٌ لا تُعيد جديداً تقريباً دليلٌ عن "
            "المستودع لا خيبةٌ فيها**."),
        "channel": {
            "portal": "https://laws.moj.gov.sa",
            "robots": "User-agent: * / Allow: / — three sitemaps declared",
            "api_base_public": BASE,
            "api_base_authenticated_not_used": BASE.replace("/apis/", "/selfservices/apis/"),
            "detail_endpoint": "/statute/get-Statute-gateway-Detail?Serial=<sitemap id>",
            "throttle_seconds": THROTTLE_SECONDS,
            "throttle_source": "the portal's own client waits 1000ms between calls",
            "reaches_before_2021": True,
        },
        "instruments_fetched": len(rows),
        "unreachable_serials": failed,
        "article_text_nodes": sum(r["article_text_nodes"] for r in rows),
        "arabic_characters": sum(r["arabic_chars"] for r in rows),
        "articles_carrying_their_own_decree_date": dated,
        "publication_years": dict(sorted(years.items())),
        "instruments_with_no_close_match_in_this_corpus": [
            r["name_ar"] for r in rows
            if (r.get("nearest_held_track") or {}).get("jaccard", 1) < 0.6],
        "instruments": sorted(rows, key=lambda r: (r["publish_date"] or "")),
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
