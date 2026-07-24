#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Cooperative Societies Law track
(نظام الجمعيات التعاونية; 44 records, ALL اصلية -- 0 معدلة, 0 ملغاة, 0 مضافة;
9 أبواب / chapters).

VERIFICATION TIER -- see the generator's module docstring and
sources/cooperative_societies/law/official_source/
cooperative_societies_law_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa HAS a dedicated lawId page for this law
(confirmed via search-engine indexing) but it was unreachable this pass (HTTP
503 live; web.archive.org refused by the fetch tool itself, not bypassed).
FULL TEXT is cross-verified across FOUR independent sources (livestockhafr.org,
bibliotdroit.com, home.cbq.org.sa, and a corroborating OCR pass on a
cscs.org.sa-hosted scanned Ministry booklet) plus a structural confirmation
from mohamah.net -> TIER_3. This validator does not re-adjudicate provenance;
it only checks internal self-consistency and that every discrepancy is still
recorded.

MATERIAL FACTS checked: 9-chapter structure (chapter_structure has exactly 9
entries covering articles 1-44 contiguously with no gaps/overlaps); ALL 44
articles اصلية (no amendments enacted); Article 43 carries the named repeal of
the predecessor Cooperative Societies System (Royal Decree 26, 25/6/1382H) and
its Subsidy Bylaw (CoM Resolution 419); the internal CoM-419-date inconsistency
and the livestockhafr.org 'تعديلات المادة' rendering artifact are both
recorded as known_unresolved_discrepancies rather than silently resolved.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cooperative_societies", "law", "official_source",
                   "cooperative_societies_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cooperative_societies", "law", "verified",
                       "cooperative_societies_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "cooperative_societies", "law", "verified",
                       "cooperative_societies_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cooperative_societies_arabic_legal_llm",
                   "cooperative_societies_law_legal_llm_001_044.json")
N = 44
KEY_RE = r"cooperative_societies_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 44, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
N_CHAPTERS = 9

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "cooperative_societies_law_boe_dedicated_page_exists_but_unreachable",
    "cooperative_societies_law_com419_date_inconsistency",
    "cooperative_societies_law_named_predecessor_repeal",
    "cooperative_societies_law_pending_unenacted_draft_amendment",
    "cooperative_societies_law_livestockhafr_tadeelat_almadda_artifact",
    "cooperative_societies_law_predecessor_not_ingested",
    "cooperative_societies_law_implementing_regulation_out_of_scope",
    "cooperative_societies_law_administering_body_now_hrsd_and_cscs",
    "cooperative_societies_law_gregorian_date_not_pinpointed",
    "cooperative_societies_law_tashkeel_stripped",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before not in ("ه", "ج")
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

    # continuous 1..44, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # CHAPTERED statute: chapter_structure must have exactly N_CHAPTERS entries,
    # contiguously covering 1..N with no gaps or overlaps.
    chs = src.get("chapter_structure") or []
    if len(chs) != N_CHAPTERS:
        e.append("[1c] expected %d chapters (أبواب), found %d" % (N_CHAPTERS, len(chs)))
    else:
        expected_next = 1
        for ch in chs:
            if ch.get("first_article") != expected_next:
                e.append("[1c] chapter %r: first_article %r != expected %d"
                         % (ch.get("label_ar"), ch.get("first_article"), expected_next))
            if ch.get("last_article", -1) < ch.get("first_article", 0):
                e.append("[1c] chapter %r: last_article before first_article" % ch.get("label_ar"))
            if not ch.get("label_ar") or "الباب" not in ch["label_ar"]:
                e.append("[1c] chapter entry missing a البا label_ar: %r" % ch)
            expected_next = ch.get("last_article", expected_next) + 1
        if expected_next != N + 1:
            e.append("[1c] chapters do not contiguously cover articles 1..%d (ended at %d)"
                     % (N, expected_next - 1))

    def _chapter_for(n):
        for ch in chs:
            if ch.get("first_article", 10**9) <= n <= ch.get("last_article", -1):
                return ch["label_ar"]
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
        # This statute has no per-article subject headings; section_ar must be empty.
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty (no per-article subject headings)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if "الباب " in a["text"]:
            e.append("[2f] %s: chapter-header text leaked into article body" % k)
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
        if _chapter_for(n) is None:
            e.append("[2n] %s: article %d not covered by any chapter range" % (k, n))

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
        if "م/14" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/14")

    # spot-checks anchoring key facts
    art1 = arts.get("cooperative_societies_law_art_001", {}).get("text", "")
    if "الوزارة" not in art1 or "الجمعية العمومية" not in art1:
        e.append("[2j] Article 1 missing expected definitions")
    art3 = arts.get("cooperative_societies_law_art_003", {}).get("text", "")
    if "اثني عشر" not in art3:
        e.append("[2j] Article 3 missing expected 12-member minimum")
    art29 = arts.get("cooperative_societies_law_art_029", {}).get("text", "")
    if "مجلس للجمعيات" not in art29:
        e.append("[2j] Article 29 missing expected Council-of-Cooperative-Societies clause")
    art42 = arts.get("cooperative_societies_law_art_042", {}).get("text", "")
    if "تسعون" not in art42 and "تسعين" not in art42:
        e.append("[2j] Article 42 missing expected implementing-regulation mandate")
    art43 = arts.get("cooperative_societies_law_art_043", {}).get("text", "")
    for token in ("يحل هذا النظام محل", "26", "1382", "419"):
        if token not in art43:
            e.append("[2j] Article 43 missing expected named-repeal token %r" % token)
    art44 = arts.get("cooperative_societies_law_art_044", {}).get("text", "")
    if "تسعين" not in art44:
        e.append("[2j] Article 44 missing expected 90-day effective-date clause")

    if src.get("decree") != "المرسوم الملكي رقم م/14" or src.get("decree_date_hijri") != "10/3/1429":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/14, 10/3/1429H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no enacted amendments exist)")
    pre = src.get("preamble_ar", "")
    if not pre or "73" not in pre or "نظام الجمعيات التعاونية" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 73 and the law name")

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
        if not r.get("chapter_ar"):
            e.append("[4] %s: missing chapter_ar in verified record" % r["article_key"])
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
        print("FAIL: %d error(s) in Cooperative Societies Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Cooperative Societies Law (نظام الجمعيات التعاونية)")
    print("  - 44 records, ALL اصلية -- 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - 9 أبواب (chapters), contiguously covering articles 1-44 with no gaps")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa has a confirmed dedicated lawId page")
    print("    but was unreachable this pass (live HTTP 503; web.archive.org refused by the fetch")
    print("    tool itself, not bypassed). Full text cross-verified across FOUR independent")
    print("    sources (livestockhafr.org, bibliotdroit.com, home.cbq.org.sa, cscs.org.sa-hosted")
    print("    scan) plus a structural confirmation from mohamah.net")
    print("  - Royal Decree M/14 (10/3/1429H, ~2008G), CoM Resolution 73 (9/3/1429H)")
    print("  - NAMED PREDECESSOR REPEAL: Article 43 explicitly repeals the prior Cooperative")
    print("    Societies System (Royal Decree 26, 25/6/1382H) and its Subsidy Bylaw (CoM")
    print("    Resolution 419) -- flagged for the corpus-wide supersession/repeal graph")
    print("  - NO enacted amendment found; a draft amendment is under public consultation on")
    print("    istitlaa.ncc.gov.sa / eparticipation.my.gov.sa but is NOT yet enacted")
    print("  - Unresolved discrepancies flagged (not silently fixed): an internal 3-way date")
    print("    inconsistency for CoM Resolution 419, and a single-source rendering artifact")
    print("    ('تعديلات المادة' label after Articles 30-34 in one PDF export only)")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation (hosted by cscs.org.sa")
    print("    alongside the base law)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
