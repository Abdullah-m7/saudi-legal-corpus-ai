#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Sports Law track (نظام الرياضة; 97
records, ALL اصلية [0 معدلة, 0 ملغاة, 0 مضافة, 0 مكرر]; 11 أبواب, 4 of them
subdivided into فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/sports/law/official_source/sports_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa and
mos.gov.sa were BOTH unreachable this pass (HTTP 503 / TLS connection-reset
across WebFetch and direct curl, multiple attempts each; web.archive.org
egress-blocked and NOT bypassed). The official Umm al-Qura gazette's own JSON
API (uqn.gov.sa) confirmed the decree identity/date/preamble directly, but not
the substantive articles. The full 97-article text rests on two independent
non-derivative aggregators (nezams.com primary, qanoonsa.com cross-check),
verified verbatim article-by-article -> TIER_3. This validator does not
re-adjudicate provenance; it only checks internal self-consistency and that
every discrepancy is still recorded.

MATERIAL FACTS checked: 11 أبواب covering 1-97 with no gaps/overlaps; 4 أبواب
carry nested فصول that also partition their range with no gaps/overlaps; every
article's section_ar matches its chapter_structure position; Article 96
carries the named predecessor-repeal text; Article 97 carries the 180-day
effective-date text; no amendments exist (all اصلية; consolidated_amended_law
== False).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sports", "law", "official_source",
                   "sports_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "sports", "law", "verified",
                       "sports_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "sports", "law", "verified",
                       "sports_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "sports_arabic_legal_llm",
                   "sports_law_legal_llm_001_097.json")
N = 97
KEY_RE = r"sports_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 97, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "sports_law_boe_and_mos_official_sources_unreachable",
    "sports_law_named_repeal_of_predecessor_m55_1407h",
    "sports_law_effective_date_separate_from_decree_date",
    "sports_law_no_official_full_text_source_tier3",
    "sports_law_implementing_regulations_not_yet_issued",
    "sports_law_brand_new_no_amendments_yet",
    "sports_law_arabic_indic_digit_style_normalized_to_western",
    "sports_law_flat_chapters_vs_subdivided_chapters",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")

# Expected chapter/فصل structure: (label_ar substring, first, last, [فصل ranges])
EXPECTED_CHAPTERS = [
    ("الباب الأول", 1, 6, []),
    ("الباب الثاني", 7, 40, [(7, 13), (14, 17), (18, 19), (20, 22), (23, 33), (34, 37), (38, 40)]),
    ("الباب الثالث", 41, 50, [(41, 43), (44, 44), (45, 45), (46, 47), (48, 48), (49, 49), (50, 50)]),
    ("الباب الرابع", 51, 55, []),
    ("الباب الخامس", 56, 57, []),
    ("الباب السادس", 58, 60, []),
    ("الباب السابع", 61, 64, []),
    ("الباب الثامن", 65, 69, []),
    ("الباب التاسع", 70, 75, [(70, 73), (74, 75)]),
    ("الباب العاشر", 76, 87, [(76, 81), (82, 85), (86, 87)]),
    ("الباب الحادي عشر", 88, 97, []),
]


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
    for p in (SRC, RECORDS, SUMMARY, LLM):
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # Chapter structure: 11 أبواب, ranges tile 1..97 with no gaps/overlaps
    chs = src.get("chapter_structure") or []
    if len(chs) != len(EXPECTED_CHAPTERS):
        e.append("[1c] expected %d أبواب, found %d" % (len(EXPECTED_CHAPTERS), len(chs)))
    else:
        for i, ((label_sub, lo, hi, fasl_ranges), entry) in enumerate(zip(EXPECTED_CHAPTERS, chs)):
            if label_sub not in (entry.get("label_ar") or ""):
                e.append("[1c] باب #%d: expected label containing %r, got %r"
                         % (i + 1, label_sub, entry.get("label_ar")))
            want_articles = "%d-%d" % (lo, hi) if lo != hi else str(lo)
            if entry.get("articles") != want_articles:
                e.append("[1c] باب #%d (%s): articles range %r != expected %r"
                         % (i + 1, label_sub, entry.get("articles"), want_articles))
            sub = entry.get("chapters") or []
            if len(sub) != len(fasl_ranges):
                e.append("[1c] باب #%d (%s): expected %d فصول, found %d"
                         % (i + 1, label_sub, len(fasl_ranges), len(sub)))
            else:
                for j, ((flo, fhi), fentry) in enumerate(zip(fasl_ranges, sub)):
                    want_f = "%d-%d" % (flo, fhi) if flo != fhi else str(flo)
                    if fentry.get("articles") != want_f:
                        e.append("[1c] باب #%d فصل #%d: articles %r != expected %r"
                                 % (i + 1, j + 1, fentry.get("articles"), want_f))
        # tiling check: every article 1..97 covered exactly once by the أبواب ranges
        covered = []
        for (_, lo, hi, _) in EXPECTED_CHAPTERS:
            covered.extend(range(lo, hi + 1))
        if sorted(covered) != list(range(1, N + 1)):
            e.append("[1c] أبواب ranges do not exactly tile 1..%d: %s" % (N, sorted(covered)))

    def _expected_section(n):
        for (label_sub, lo, hi, fasl_ranges) in EXPECTED_CHAPTERS:
            if lo <= n <= hi:
                if not fasl_ranges:
                    return label_sub  # substring check only
                for (flo, fhi) in fasl_ranges:
                    if flo <= n <= fhi:
                        return label_sub  # substring check only (فصل title varies)
        return None

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        # Every article MUST carry a non-empty section_ar (this statute has أبواب)
        if not (a.get("section_ar") or "").strip():
            e.append("[2] %s: section_ar must be non-empty (statute has أبواب)" % k)
        exp_sub = _expected_section(n)
        if exp_sub and exp_sub not in (a.get("section_ar") or ""):
            e.append("[2] %s: section_ar %r does not contain expected باب label %r"
                     % (k, a.get("section_ar"), exp_sub))
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # header-stripping sanity: no article body should still start with a
        # باب/فصل heading line (those belong in section_ar / chapter_structure)
        if re.match(r"^(الباب|الفصل)\b", a["text"]):
            e.append("[2n] %s: text still starts with a الباب/الفصل heading; must be stripped" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record the founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "م/121" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/121")

    # spot-checks anchoring key facts
    art1 = arts.get("sports_law_art_001", {}).get("text", "")
    if "نظام الرياضة" not in art1 or "الرياضة:" not in art1:
        e.append("[2j] Article 1 missing expected definitions header")
    art7 = arts.get("sports_law_art_007", {}).get("text", "")
    if "اللجنة" not in art7 or "أولمبي" not in art7:
        e.append("[2j] Article 7 missing expected Olympic Committee definition")
    art37 = arts.get("sports_law_art_037", {}).get("text", "")
    if "رأس مال" not in art37:
        e.append("[2j] Article 37 missing expected minimum-capital clause")
    art58 = arts.get("sports_law_art_058", {}).get("text", "")
    if "المنشطات" not in art58:
        e.append("[2j] Article 58 missing expected anti-doping committee clause")
    art77 = arts.get("sports_law_art_077", {}).get("text", "")
    if "غرامة" not in art77:
        e.append("[2j] Article 77 missing expected penalties clause")
    art95 = arts.get("sports_law_art_095", {}).get("text", "")
    if "اللوائح" not in art95 or "مائة وثمانين" not in art95:
        e.append("[2j] Article 95 missing expected implementing-regulations 180-day mandate")
    art96 = arts.get("sports_law_art_096", {}).get("text", "")
    for token in ("يحل النظام محل", "م/55", "1407"):
        if token not in art96:
            e.append("[2j] Article 96 (repeal) missing expected token %r" % token)
    art97 = arts.get("sports_law_art_097", {}).get("text", "")
    if "مائة وثمانين" not in art97:
        e.append("[2j] Article 97 missing expected 180-day effective-date clause")

    if src.get("decree") != "المرسوم الملكي رقم م/121" or src.get("decree_date_hijri") != "10/6/1447":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/121, 10/6/1447H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (brand-new, no amendments yet)")
    pre = src.get("preamble_ar", "")
    if not pre or "414" not in pre or "نظام الرياضة" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 414 and the law name")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if (r.get("is_amended")) != (r["article_key"] in AMENDED_KEYS):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Sports Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Sports Law (نظام الرياضة)")
    print("  - 97 records: ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة, 0 مكرر) -- brand-new founding statute")
    print("  - 11 أبواب covering 1-97 (7 flat, 4 subdivided into فصول: الثاني[7], الثالث[7],")
    print("    التاسع[2], العاشر[3]); every article's section_ar matches its chapter position")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa and mos.gov.sa both unreachable this")
    print("    pass (503 / TLS reset across WebFetch and direct curl, multiple attempts each;")
    print("    web.archive.org egress-blocked and NOT bypassed). Full text from nezams.com")
    print("    (primary) cross-checked verbatim article-by-article against qanoonsa.com")
    print("    (independent secondary); decree identity/date/preamble officially confirmed via")
    print("    the Umm al-Qura gazette's own JSON API (uqn.gov.sa)")
    print("  - Royal Decree M/121 (10/6/1447H, ~1 Dec 2025G), CoM Resolution 414 (4/6/1447H),")
    print("    published Umm al-Qura issue 5129 (21/6/1447H / 12 Dec 2025G); entry into force")
    print("    180 days after publication (~June 2026G) -- kept separate from decree date")
    print("  - NAMED predecessor repeal: Article 96 supersedes Royal Decree M/55 (19/10/1407H,")
    print("    following CoM Resolution 226, 13/9/1407H) -- the Basic Law of Sports Federations")
    print("    and the Saudi Arabian Olympic Committee")
    print("  - Follow-up candidate NOT ingested: Implementing Regulations (Article 95 mandate,")
    print("    not yet issued as of this track's preparation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
