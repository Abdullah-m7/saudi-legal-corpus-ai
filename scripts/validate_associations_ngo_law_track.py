#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Law of Associations and Civil Institutions
track (نظام الجمعيات والمؤسسات الأهلية; 44 records: 43 اصلية, 1 معدلة [art 1],
0 ملغاة, 0 مضافة; FLAT statute -- no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/associations_ngo/law/official_source/
associations_ngo_law_official_source.json's verification_methodology_note for
the full account: laws.boe.gov.sa's own indexing shows two different lawId
values for this law's name and the live portal was unreachable this pass
(HTTP 503 / connection reset; web.archive.org egress-blocked and NOT
bypassed). PRIMARY full text is nezams.com, independently cross-checked
against a menarights.org PDF for article count and the closing articles'
verbatim text -> TIER_3. This validator does not re-adjudicate provenance; it
only checks internal self-consistency and that every discrepancy is still
recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); 19 titled
articles carry section_ar, the other 25 have section_ar == ""; article 1
(only) carries amendment history for the two Resolution-618 definitions;
Articles 7/25/38 are explicitly exempted from the Resolution-618 horizontal
substitution and remain اصلية; Article 43 carries the named repeal of the
predecessor Charitable Associations and Institutions Regulation (CoM
Resolution 107, 25/6/1410H).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "associations_ngo", "law", "official_source",
                   "associations_ngo_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "associations_ngo", "law", "verified",
                       "associations_ngo_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "associations_ngo", "law", "verified",
                       "associations_ngo_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "associations_ngo_arabic_legal_llm",
                   "associations_ngo_law_legal_llm_001_044.json")
N = 44
KEY_RE = r"associations_ngo_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 43, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
TITLED_NUMS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 25, 29, 38, 39}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = {"associations_ngo_law_art_001"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "associations_ngo_law_boe_dedicated_page_exists_but_unreachable",
    "associations_ngo_law_named_repeal_of_predecessor_res107_1410",
    "associations_ngo_law_res618_horizontal_substitution_almarkaz",
    "associations_ngo_law_competent_authority_res61_amended_by_res367",
    "associations_ngo_law_res618_note_typo_alwizarah_preserved",
    "associations_ngo_law_flat_no_bab_or_fasl_structure",
    "associations_ngo_law_tashkeel_and_kashida_normalized",
    "associations_ngo_law_implementing_regulation_out_of_scope",
    "associations_ngo_law_administration_moved_to_ncnp",
    "associations_ngo_law_gregorian_date_not_pinpointed",
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] this statute is flat (no chapters); chapter_structure must be [] but is %r"
                 % (chs,))

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
        has_section = bool(a.get("section_ar"))
        if (n in TITLED_NUMS) != has_section:
            e.append("[2] %s: section_ar presence must match TITLED_NUMS membership" % k)
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
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            if len(hist) != 2:
                e.append("[2m] %s: expected exactly 2 history entries (two Resolution-618 notes)" % k)
            for h in hist:
                if "618" not in (h.get("decree_note") or ""):
                    e.append("[2m] %s: history entry must cite CoM Resolution 618" % k)

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
        e.append("[2k] missing amendment_history (must record founding + amending decrees)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "م/8" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/8")
        if "618" not in decrees:
            e.append("[2k] amendment_history must reference amending resolution 618")
        if "367" not in decrees:
            e.append("[2k] amendment_history must reference amending resolution 367")

    # spot-checks anchoring key facts
    art1 = arts.get("associations_ngo_law_art_001", {}).get("text", "")
    if "الجمعية" not in art1 or "المؤسسة" not in art1:
        e.append("[2j] Article 1 missing expected definitions")
    art7 = arts.get("associations_ngo_law_art_007", {}).get("text", "")
    if "صندوق دعم الجمعيات" not in art7:
        e.append("[2j] Article 7 missing expected support-fund provision")
    if arts.get("associations_ngo_law_art_007", {}).get("legal_status_ar") != "اصلية":
        e.append("[2j] Article 7 must remain اصلية (explicitly exempted from Resolution 618)")
    if arts.get("associations_ngo_law_art_025", {}).get("legal_status_ar") != "اصلية":
        e.append("[2j] Article 25 must remain اصلية (explicitly exempted from Resolution 618)")
    if arts.get("associations_ngo_law_art_038", {}).get("legal_status_ar") != "اصلية":
        e.append("[2j] Article 38 must remain اصلية (explicitly exempted from Resolution 618)")
    art42 = arts.get("associations_ngo_law_art_042", {}).get("text", "")
    if "تسعين" not in art42:
        e.append("[2j] Article 42 missing expected 90-day implementing-regulation mandate")
    art43 = arts.get("associations_ngo_law_art_043", {}).get("text", "")
    if "107" not in art43 or "1410" not in art43.replace("هـ", "").replace(" ", ""):
        e.append("[2j] Article 43 missing expected named repeal of CoM Resolution 107 (1410H)")
    if "يلغي" not in art43 and "تلغى" not in art43 and "يُلغى" not in art43:
        e.append("[2j] Article 43 missing expected repeal verb")
    art44 = arts.get("associations_ngo_law_art_044", {}).get("text", "")
    if "تسعين" not in art44:
        e.append("[2j] Article 44 missing expected 90-day effective-date clause")

    if src.get("decree") != "المرسوم الملكي رقم م/8" or src.get("decree_date_hijri") != "19/2/1437":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/8, 19/2/1437H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS amendments incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "المرسوم الملكي" not in pre:
        e.append("[2j] preamble_ar must be present and reference the Royal Decree")

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
    if summary.get("consolidated_amended_law") is not True:
        e.append("[4b] summary consolidated_amended_law must be True")

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
        print("FAIL: %d error(s) in Associations/NGO Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Law of Associations and Civil Institutions (نظام الجمعيات والمؤسسات الأهلية)")
    print("  - 44 records: 43 اصلية, 1 معدلة (art 1), 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-44, NO chapters/فصول (chapter_structure == []); 19")
    print("    articles carry an internal section_ar heading, the other 25 have none")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa indexing shows two conflicting lawId")
    print("    values for this law's name and the live portal was unreachable this pass (HTTP 503;")
    print("    web.archive.org egress-blocked and NOT bypassed). PRIMARY full text from nezams.com,")
    print("    independently cross-checked against a menarights.org PDF for article count and the")
    print("    closing articles' verbatim text")
    print("  - Royal Decree M/8 (19/2/1437H, ~2015G), CoM Resolution 61 (18/2/1437H), published Umm")
    print("    al-Qura 7/3/1437H; amended by CoM Resolution 618 (20/10/1442H: two new definitions in")
    print("    art 1 + horizontal substitution except arts 7/25/38) and CoM Resolution 367")
    print("    (29/6/1443H: competent-authority annex only, not a numbered article)")
    print("  - NAMED PREDECESSOR REPEAL: Article 43 explicitly repeals the Charitable Associations")
    print("    and Institutions Regulation (CoM Resolution 107, 25/6/1410H) -- flagged for the")
    print("    corpus-wide supersession/repeal graph (predecessor not itself ingested)")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation (Ministerial Resolution")
    print("    73739, 11/6/1437H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
