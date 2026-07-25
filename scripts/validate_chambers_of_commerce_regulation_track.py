#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Chambers of Commerce
Law track (اللائحة التنفيذية لنظام الغرف التجارية; 63 records: 62 اصلية, 1 معدلة
(Article 10), 0 ملغاة, 0 مضافة).

VERIFICATION TIER -- see the generator's module docstring and sources/
chambers_of_commerce_regulation/law/official_source/
chambers_of_commerce_regulation_official_source.json's verification_methodology_note
for the full account: primary text from the Umm Al-Qura gazette (Wayback archive of
uqn.gov.sa/?p=7074, since the live site is JS-rendered), cross-checked article-by-
article against an official Federation of Saudi Chambers (fsc.org.sa) PDF -> TIER_2.
Article 10 carries a confirmed 2025 amendment (Ministerial Decision No. 87); a SEPARATE
proposed amendment to Article 44 was floated for public consultation in Jan 2025 but is
NOT adopted as of this pass (recorded honestly as a pending, unadopted draft, not
merged into Article 44's text). This validator does not re-adjudicate provenance; it
only checks internal self-consistency and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "chambers_of_commerce_regulation", "law", "official_source",
                   "chambers_of_commerce_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "chambers_of_commerce_regulation", "law", "verified",
                       "chambers_of_commerce_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "chambers_of_commerce_regulation", "law", "verified",
                       "chambers_of_commerce_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "chambers_of_commerce_regulation_arabic_legal_llm",
                   "chambers_of_commerce_regulation_legal_llm_001_063.json")
N = 63
KEY_RE = r"chambers_of_commerce_regulation_art_(\d{3})"
LAW_NAME = "Implementing Regulation of the Chambers of Commerce Law"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 62, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
TRUSTED = {"MATCHES_UQN_GAZETTE_X_FSC_INDEPENDENT_CROSS_CHECK"}
AMENDED_KEYS = {"chambers_of_commerce_regulation_art_010"}
ADDED_KEYS: set = set()
REPEALED_KEYS: set = set()
FLAGGED_DISCREPANCY_KEYS = {
    "chambers_of_commerce_regulation_boe_no_dedicated_page",
    "chambers_of_commerce_regulation_uqn_live_site_js_rendered",
    "chambers_of_commerce_regulation_art_015_numbering_divergence",
    "chambers_of_commerce_regulation_art_040_table_linearized",
    "chambers_of_commerce_regulation_art_010_amendment_secondary_source_only",
    "chambers_of_commerce_regulation_founding_resolution_indirect_confirmation",
    "chambers_of_commerce_regulation_art_053_period_markers_source_inconsistency",
    "chambers_of_commerce_regulation_tashkeel_stripped",
    "chambers_of_commerce_regulation_nbsp_double_space_stripped",
    "chambers_of_commerce_regulation_art_044_draft_amendment_not_adopted",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts if re.match(KEY_RE, k))
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a complete 1..%d sequence" % N)
    if any(k.endswith("_mukarrar") for k in arts):
        e.append("[1c] unexpected mukarrar keys")

    chs = src.get("chapter_structure")
    if not chs or len(chs) < 5:
        e.append("[1d] this regulation has its own chapter/باب structure; "
                 "chapter_structure must be populated (non-flat, unlike anti_smoking_regulation)")

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("status") not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a.get("status")))
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected status divergence" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if re.search(r"(?<![0-9])[A-Za-z](?![0-9])", a["text"]):
            e.append("[2] %s: unexpected latin leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if k in AMENDED_KEYS and len(a.get("history") or []) < 2:
            e.append("[2] %s: amended article must carry both current and original "
                     "history entries" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # Article 10: current text must reflect the 6/9/12 tiers, NOT the original 9/12/15/18
    art10 = arts.get("chambers_of_commerce_regulation_art_010", {})
    t10 = art10.get("text", "")
    for token in ("(ستة)", "(تسعة)", "(اثنا عشر)", "(50,000)", "(100,000)"):
        if token not in t10:
            e.append("[2j] Article 10 current text missing expected token %r "
                     "(post-Decision-87 tiers: 6/9/12)" % token)
    if "(خمسة عشر)" in t10 or "(ثمانية عشر)" in t10:
        e.append("[2j] Article 10 current text should NOT carry the pre-2025 "
                 "9/12/15/18 tiers")
    hist = art10.get("history") or []
    if len(hist) >= 2:
        types = {h.get("type") for h in hist}
        if types != {"amendment_current", "original"}:
            e.append("[2j] Article 10 history must contain exactly amendment_current + original")
        orig = next((h for h in hist if h.get("type") == "original"), {})
        if "(ثمانية عشر)" not in orig.get("text", ""):
            e.append("[2j] Article 10 original history text should carry the pre-2025 "
                     "9/12/15/18 tiers")

    # Article 44: must remain UNADOPTED / original -- honesty gate for the pending draft
    art44 = arts.get("chambers_of_commerce_regulation_art_044", {})
    if art44.get("legal_status_ar") != "اصلية":
        e.append("[2k] Article 44 must remain اصلية -- the draft amendment was NOT "
                 "confirmed adopted this pass")
    t44 = art44.get("text", "")
    if "جهات استشارية لا تقل عن (خمسة)" not in t44:
        e.append("[2k] Article 44 must retain its ORIGINAL committee-of->=5-firms wording "
                 "(not the unadopted draft's single-firm wording)")
    if "تختار الجمعية العمومية للغرفة الجهة الاستشارية" not in t44:
        e.append("[2k] Article 44 must retain its ORIGINAL clause (ب) (deleted in the "
                 "unadopted draft)")

    pending = src.get("pending_draft_amendments")
    if not pending:
        e.append("[2l] missing pending_draft_amendments (Article 44 draft must be recorded)")
    else:
        if not any(p.get("article_key") == "chambers_of_commerce_regulation_art_044"
                   and p.get("status") == "NOT_ADOPTED_AS_OF_THIS_PASS" for p in pending):
            e.append("[2l] pending_draft_amendments must record Article 44 as "
                     "NOT_ADOPTED_AS_OF_THIS_PASS")

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

    if src.get("founding_resolution_confirmed") is not True:
        e.append("[2g] founding_resolution_confirmed should be True (confirmed, but only "
                 "indirectly via a later decree's recital -- see "
                 "founding_resolution_confirmation_method)")
    if not src.get("founding_resolution_confirmation_method"):
        e.append("[2g] missing founding_resolution_confirmation_method (must disclose "
                 "the INDIRECT nature of this confirmation)")

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2m] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "10" not in decrees or "87" not in decrees:
            e.append("[2m] amendment_history must reference both Decision 10 (founding) "
                     "and Decision 87 (Article 10 amendment)")

    if src.get("preamble_ar") not in ("", None):
        e.append("[2n] preamble_ar must be empty -- no founding decree preamble/enacting "
                 "text was located this pass; a non-empty value would risk fabrication")

    if src.get("legal_status_ar") != "ساري":
        e.append("[2o] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2o] consolidated_amended_law must be True (Article 10 carries a "
                 "confirmed amendment)")
    if src.get("law_component") != "regulation":
        e.append("[2o] law_component must be 'regulation'")

    # committed provenance snapshot (if present) re-hashes; snapshot file is optional in
    # this standalone track (Wayback URL + timestamp recorded either way)
    prov = src.get("provenance", {})
    snap = prov.get("archive_snapshot")
    if snap and snap.get("committed"):
        f = os.path.join(ROOT, snap["committed"])
        if os.path.isfile(f) and snap.get("sha256"):
            if hashlib.sha256(open(f, "rb").read()).hexdigest() != snap["sha256"]:
                e.append("[3] committed snapshot sha256 mismatch")

    # verified records
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
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
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
    if not summary.get("pending_draft_amendments"):
        e.append("[4b] summary must carry pending_draft_amendments")

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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in %s track:" % (len(e), LAW_NAME))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: %s — %d records (62 اصلية, 1 معدلة, 0 ملغاة, 0 مضافة)" % (LAW_NAME, N))
    print("  - source: Umm Al-Qura official gazette (uqn.gov.sa/?p=7074) via Wayback archive")
    print("    (live site is JS-rendered); cross-checked against an official Federation of")
    print("    Saudi Chambers (fsc.org.sa) PDF, article-by-article, zero content diffs")
    print("  - VERIFICATION TIER: TIER_2. Confirmed amendment: Article 10 (Ministerial")
    print("    Decision No. 87, 12/5/1447H), corroborated by an independent news source")
    print("  - Article 44 draft amendment (Jan 2025 public consultation) NOT found adopted")
    print("    as of this pass -- recorded honestly as a pending, unadopted draft; Article")
    print("    44's text here is its original, unamended form")
    print("  - complete 1..%d (no مكرر); own chapter/باب structure; Arabic governs" % N)
    return 0


if __name__ == "__main__":
    sys.exit(main())
