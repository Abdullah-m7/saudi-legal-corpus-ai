#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the State Revenue Law track (32 records: 31
numbered articles + Article 28-bis / المادة الثامنة والعشرون مكرر; 30
اصلية / 1 معدلة / 1 مضافة; NO formal فصل/chapter structure).

DISTINCT VERIFICATION TIER -- see the generator's module docstring and
sources/state_revenue/law/official_source/state_revenue_law_official_source.json's
verification_methodology_note for the full caveat, including: (a) the
confirmed BOE stale-main-body-vs-changelog split on Article 25 (this track
DOES carry original_1431h_text for Article 25, unlike the income-tax-law
track's blanket gap, because both wordings were independently recovered to
primary-source confidence); (b) the unresolved two-source conflict over
which instrument (Royal Decree M/93 vs. Council of Ministers Resolution
198) added Article 28-bis; (c) the explicit, deliberate exclusion of an
unconfirmed July-2026 'updated' version of this law -- this track is
strictly the pre-2026-update, currently-in-force text (M/68 as amended by
M/5 and M/93)."""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "state_revenue", "law", "official_source",
                   "state_revenue_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "state_revenue", "law", "verified",
                       "state_revenue_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "state_revenue", "law", "verified",
                       "state_revenue_law_verified_summary.json")
N = 32
KEY_RE = r"state_revenue_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 30, "معدلة": 1, "مضافة": 1, "ملغاة": 0}
STATUS = "BOE_WAYBACK_X_NEZAMS_X_QANOONSA_CROSS_VERIFIED"
AMENDED_KEYS = {"state_revenue_art_025"}
ADDED_KEYS = {"state_revenue_art_028_mukarrar"}
FLAGGED_DISCREPANCY_KEYS = {
    "state_revenue_decree_vs_resolution_date_lead_correction",
    "state_revenue_art_025_boe_stale_main_body_vs_changelog",
    "state_revenue_art_028_mukarrar_instrument_conflict",
    "state_revenue_no_chapter_structure",
    "state_revenue_2026_update_unconfirmed",
}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS | ADDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    if src.get("numbered_articles_max") != 31:
        e.append("[1b] numbered_articles_max != 31")
    if src.get("mukarrar_article_keys") != ["state_revenue_art_028_mukarrar"]:
        e.append("[1b] mukarrar_article_keys unexpected: %r" % src.get("mukarrar_article_keys"))
    if src.get("chapter_structure") not in ([], None):
        e.append("[1c] expected NO chapter_structure (this law has no formal فصول), got %r"
                  % src.get("chapter_structure"))

    if src.get("decree") != "المرسوم الملكي رقم (م/68)":
        e.append("[0] unexpected decree citation: %r" % src.get("decree"))
    if src.get("decree_date_hijri") != "18/11/1431":
        e.append("[0] unexpected decree date: %r" % src.get("decree_date_hijri"))
    if src.get("council_resolution_date_hijri") != "17/11/1431":
        e.append("[0] unexpected council resolution date: %r" % src.get("council_resolution_date_hijri"))
    if src.get("decree_date_hijri") == src.get("council_resolution_date_hijri"):
        e.append("[0] decree and council resolution dates must NOT be identical "
                 "(corrects the prior unverified lead) -- got the same date")

    repealed = src.get("repealed_predecessor") or {}
    if not repealed.get("confirmed"):
        e.append("[0b] repealed_predecessor.confirmed must be true (Article 30 "
                 "explicitly repeals نظام جباية أموال الدولة)")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in ADDED_KEYS and not a.get("history"):
            e.append("[2] %s: added (مضافة) article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if k.endswith("_mukarrar") and not a.get("is_mukarrar"):
            e.append("[2] %s: mukarrar key but is_mukarrar not set" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # Article 25 must carry BOTH the current (post-M/5) and original
    # (pre-M/5, still containing "أو تقسيط") text -- this is the confirmed
    # BOE stale-main-body-vs-changelog case, not a documented gap.
    art25 = arts.get("state_revenue_art_025", {})
    if "تقسيط" in art25.get("text", ""):
        e.append("[2f] state_revenue_art_025: current text should NOT contain "
                 "'تقسيط' (removed by M/5) -- got stale/pre-amendment text in "
                 "the governing text field")
    if "تقسيط" not in art25.get("original_1431h_text", ""):
        e.append("[2f] state_revenue_art_025: original_1431h_text should "
                 "contain 'تقسيط' (the pre-amendment wording) but does not")
    hist25 = " ".join(h.get("date_hijri", "") for h in art25.get("history", []))
    if "2/1/1440" not in hist25:
        e.append("[2f] state_revenue_art_025: expected M/5 date 2/1/1440H in history")

    # Article 28-bis must record BOTH candidate amending instruments
    # (BOE's M/93 and nezams.com's Resolution 198) rather than silently
    # picking one.
    art28m = arts.get("state_revenue_art_028_mukarrar", {})
    hist28m = art28m.get("history", [])
    instr28m = " ".join(h.get("instrument", "") for h in hist28m)
    dates28m = " ".join(h.get("date_hijri", "") for h in hist28m)
    if "م/93" not in instr28m:
        e.append("[2g] state_revenue_art_028_mukarrar: expected Royal Decree "
                 "M/93 recorded in history")
    if "198" not in instr28m:
        e.append("[2g] state_revenue_art_028_mukarrar: expected Council of "
                 "Ministers Resolution 198 recorded in history (unresolved "
                 "second candidate, not silently dropped)")
    if "1/10/1443" not in dates28m or "4/4/1443" not in dates28m:
        e.append("[2g] state_revenue_art_028_mukarrar: expected both candidate "
                 "dates (1/10/1443H and 4/4/1443H) recorded in history")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))
        # The 2026-update disclosure must actually disclose non-confirmation.
        upd = next((d for d in disc if d["article_key"] == "state_revenue_2026_update_unconfirmed"), None)
        if upd is None or "unconfirmed" not in upd["description"].lower():
            e.append("[2h] state_revenue_2026_update_unconfirmed entry missing or "
                     "does not clearly disclose non-confirmation")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: not found in source articles" % r["article_key"])
            continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("original_1431h_text") != a.get("original_1431h_text"):
            e.append("[4] %s: original_1431h_text not propagated" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summ = json.load(open(SUMMARY, encoding="utf-8"))
    if summ.get("record_count") != N:
        e.append("[5] summary record_count != %d" % N)
    if summ.get("official_text_status") != STATUS:
        e.append("[5] summary official_text_status mismatch")
    if not summ.get("known_unresolved_discrepancies"):
        e.append("[5] summary missing known_unresolved_discrepancies")

    if e:
        print("FAIL: %d error(s) in State Revenue Law track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: State Revenue Law -- 32 records (30 اصلية / 1 معدلة / 1 مضافة,")
    print("  no formal فصل/chapter structure)")
    print("  - DISTINCT TIER: BOE (Wayback) x nezams.com x qanoonsa.com cross-verified")
    print("  - IN-FORCE Royal Decree M/68 (18/11/1431H, approving Council of Ministers")
    print("    Resolution 359 dated 17/11/1431H -- one day earlier, NOT the same date")
    print("    as a prior unverified lead claimed); amended by M/5 (1440H) and M/93 (1443H)")
    print("  - Article 25: BOE's stale main body vs. current changelog text confirmed;")
    print("    both original and current wording recovered to primary-source confidence")
    print("  - Article 28-bis (مضافة): genuine, but its adding instrument is disputed")
    print("    between BOE (M/93, 1/10/1443H) and nezams.com (Resolution 198, 4/4/1443H)")
    print("    -- both recorded, neither silently resolved")
    print("  - Article 30 confirms repeal of the predecessor نظام جباية أموال الدولة")
    print("    (Royal Will 41/3/2, 12/4/1359H)")
    print("  - SCOPE: excludes the unconfirmed July-2026 'updated' State Revenue Law")
    print("    (no promulgating instrument number found this pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
