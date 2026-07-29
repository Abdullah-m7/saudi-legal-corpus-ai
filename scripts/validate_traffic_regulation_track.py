#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
Traffic Law track (86 records: 74 اصلية, 11 معدلة [Articles 7, 16, 17, 21, 23,
47, 50, 51, 54, 59, 68], 1 ملغاة [Article 80], 0 مضافة; 8 chapters; 85 numbered
articles plus المادة الخمسون مكرر).

AMENDMENT STATE: the founding text of Resolution 2249 (10/3/1441H) updated with
all five gazette-confirmed amending decisions of the Minister of Interior --
3148 (26/2/1443, adds 47/2), 18243 (5/12/1443, replaces Article 23 in full),
5622 (1/4/1444, amends 7/1/3/2), 1924 (1/5/1447, deletes 21/1/4) and 5330
(16/12/1447, adds the seven المركبات ذاتية القيادة paragraphs 16/1/5, 17/2/13,
50/12, 51/7, 54/9, 59/5, 68/4). None adds an article, so the count stays 86.
Checks [2m] below assert each of the five is actually present, that superseded
wording is preserved rather than discarded, that the deleted clause 21/1/4 is
FLAGGED and NOT removed, and that the unrecovered Article 47/2 penalty table
stays disclosed as a gap rather than being quietly filled in or dropped.

VERIFICATION TIER -- see the generator's module docstring and
sources/traffic/regulation/official_source/traffic_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (per this corpus's standard methodology) but has NO dedicated lawId page
for this Implementing Regulation at all (only for the base Traffic Law), and all
.gov.sa hosts plus an archive.org copy were connection-reset this pass (recorded,
not circumvented). The PRIMARY source is an official SCANNED Ministry of Interior
document of Ministerial Resolution No. 2249 (10/3/1441H) -- page 1 is the
stamped/signed resolution itself -- extracted via direct vision reading
cross-checked against an independent tesseract-ara OCR pass. Articles 1-8 were
independently cross-validated against qanoniah.com's born-digital text (100% for
six, 99.0% for Article 2; Article 7's divergence confirms its amendment). This
resolution SUPERSEDES the prior Resolution 7019/1429H. This validator does not
re-adjudicate any of this; it only checks internal self-consistency of the text
this track actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "traffic", "regulation", "official_source",
                   "traffic_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "traffic", "regulation", "verified",
                       "traffic_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "traffic", "regulation", "verified",
                       "traffic_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "traffic_regulation_arabic_legal_llm",
                   "traffic_regulation_legal_llm_001_086.json")
N = 86                 # total records
N_NUMBERED = 85        # distinct numbered articles (1..85); the 86th is 50 مكرر
KEY_RE = r"traffic_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 74, "معدلة": 11, "ملغاة": 1, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 8

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
STATUS_REPEALED = "REPEALED"
AMENDED_KEYS = {"traffic_regulation_art_007", "traffic_regulation_art_016",
                "traffic_regulation_art_017", "traffic_regulation_art_021",
                "traffic_regulation_art_023", "traffic_regulation_art_047",
                "traffic_regulation_art_050", "traffic_regulation_art_051",
                "traffic_regulation_art_054", "traffic_regulation_art_059",
                "traffic_regulation_art_068"}
REPEALED_KEYS = {"traffic_regulation_art_080"}
ADDED_KEYS: set[str] = set()
MUKARRAR_KEYS = {"traffic_regulation_art_050_mukarrar"}
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in REPEALED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_REPEALED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "traffic_regulation_gap_map_candidate_confirmed",
    "traffic_regulation_supersedes_7019_1429",
    "traffic_regulation_boe_no_dedicated_page",
    "traffic_regulation_source_scanned_pdf_vision_ocr_tier",
    "traffic_regulation_current_version_not_ingested",
    "traffic_regulation_art7_amendment_confirmed_by_divergence",
    "traffic_regulation_art23_47_amendment_secondary_source_only",
    "traffic_regulation_art80_repealed_from_source_footnote",
    "traffic_regulation_mukarrar_classified_original",
    "traffic_regulation_law_text_not_reingested",
    "traffic_regulation_annex_tables_not_modeled",
    "traffic_regulation_points_system_not_the_1443_points_regulation",
    "traffic_regulation_ocr_slashnum_reconstruction",
    # added by the 15/2/1448H maintenance pass (five amending decisions applied)
    "traffic_regulation_art47_2_penalty_table_gazette_pdf_gap",
    "traffic_regulation_decision_5622_issue_date_variant",
    "traffic_regulation_decision_1924_single_source_number_and_date",
    "traffic_regulation_prior_source_two_decisions_stale",
}
# The five amending decisions applied to this track. Every one of them must stay
# recorded, with its number, in the track-level amendment_history.
REQUIRED_AMENDING_DECISIONS = ("3148", "18243", "5622", "1924", "5330")
AR = "ء-ي"
# genuine non-Arabic tokens present verbatim in the source (allow-list)
ALLOWED_LATIN = {"FIA"}


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        # the "هـ" Hijri-date marker (before == "ه") is legitimate, not decorative
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def _has_bad_latin(text):
    stripped = text
    for tok in ALLOWED_LATIN:
        stripped = stripped.replace(tok, "")
    return bool(re.search(r"[A-Za-z<>&]", stripped))


def _iter_chapter_ranges(chs):
    for ch in chs:
        m = re.search(r"(\d+)\s*-\s*(\d+)", ch["articles"])
        yield (int(m.group(1)), int(m.group(2)))


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

    # exactly one mukarrar, numbered 50
    muk = [k for k in arts if re.match(KEY_RE, k) and re.match(KEY_RE, k).group(2) is not None]
    if set(muk) != MUKARRAR_KEYS:
        e.append("[1b] mukarrar key set mismatch: got %s" % sorted(muk))
    for k in muk:
        if not arts[k].get("is_mukarrar"):
            e.append("[1b] %s: is_mukarrar must be True" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N_NUMBERED + 1)):
        missing = sorted(set(range(1, N_NUMBERED + 1)) - covered)
        extra = sorted(covered - set(range(1, N_NUMBERED + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or _has_bad_latin(a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if not a.get("verification_tier"):
            e.append("[2] %s: missing verification_tier" % k)
        if k in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/repealed/added article missing history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: unchanged article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) + str(h.get("note", ""))
                           for h in src["amendment_history"])
        if "2249" not in decrees:
            e.append("[2k] amendment_history must reference founding resolution 2249")
        if "7019" not in decrees:
            e.append("[2k] amendment_history must reference superseded resolution 7019")
        if "636" not in decrees:
            e.append("[2k] amendment_history must reference the Article-80 repeal (CoM 636)")
        for dec in REQUIRED_AMENDING_DECISIONS:
            if dec not in decrees:
                e.append("[2k] amendment_history must reference amending decision %s" % dec)
        if "غير مؤكد" in decrees:
            e.append("[2k] amendment_history still carries an unconfirmed-date entry; all five "
                     "amending decisions are gazette-dated")

    # ---- the five applied amendments must actually be present in the text ----
    # decision 5330 (16/12/1447) -- seven self-driving-vehicle paragraphs
    for key, clause in (("traffic_regulation_art_016", "16/1/5-"),
                        ("traffic_regulation_art_017", "17/2/13-"),
                        ("traffic_regulation_art_050", "50/12-"),
                        ("traffic_regulation_art_051", "51/7-"),
                        ("traffic_regulation_art_054", "54/9-"),
                        ("traffic_regulation_art_059", "59/5-"),
                        ("traffic_regulation_art_068", "68/4-")):
        t = arts.get(key, {}).get("text", "")
        if clause not in t or "ذاتية القيادة" not in t:
            e.append("[2m] %s: missing clause %s added by Decision 5330" % (key, clause))
        h = " ".join(str(x.get("decree", "")) for x in arts.get(key, {}).get("history", []))
        if "5330" not in h:
            e.append("[2m] %s: history must cite Decision 5330" % key)

    # decision 5622 (1/4/1444) -- clause 7/1/3/2 replaced, original preserved in history
    a7t = arts.get("traffic_regulation_art_007", {}).get("text", "")
    if "7/1/3/2- يشترط لصرف اللوحات الدبلوماسية أو القنصلية" not in a7t:
        e.append("[2m] Article 7 must carry the 5622-amended text of clause 7/1/3/2")
    if "ممن يحملون الصفة الدبلوماسية" in a7t:
        e.append("[2m] Article 7 still carries the superseded 1441 wording of 7/1/3/2 in its text")
    a7h = " ".join(str(x.get("decree", "")) + str(x.get("description", ""))
                   for x in arts.get("traffic_regulation_art_007", {}).get("history", []))
    if "5622" not in a7h or "ممن يحملون الصفة الدبلوماسية" not in a7h:
        e.append("[2m] Article 7 history must cite Decision 5622 AND preserve the superseded "
                 "1441 wording (nothing is discarded)")

    # decision 1924 (1/5/1447) -- clause 21/1/4 FLAGGED deleted, text NEVER removed
    a21 = arts.get("traffic_regulation_art_021", {})
    a21t = a21.get("text", "")
    if "21/1/4- وجود ضمان بنكي بمبلغ (مائتي) ألف ريال." not in a21t:
        e.append("[2m] Article 21: deleted clause 21/1/4 text must be PRESERVED, never removed")
    if "محذوفة" not in a21t or "1924" not in a21t:
        e.append("[2m] Article 21: clause 21/1/4 must carry an explicit deletion flag citing 1924")
    if "1924" not in " ".join(str(x.get("decree", "")) for x in a21.get("history", [])):
        e.append("[2m] Article 21 history must cite Decision 1924")

    # decision 18243 (5/12/1443) -- Article 23 replaced in full, original preserved in history
    a23 = arts.get("traffic_regulation_art_023", {})
    a23t = a23.get("text", "")
    for need in ("23/1-", "23/2/1-", "23/10-", "الهيئة السعودية للمواصفات والمقاييس والجودة"):
        if need not in a23t:
            e.append("[2m] Article 23 missing %r from the 18243 replacement text" % need)
    if len(a23t) < 2000:
        e.append("[2m] Article 23 looks like the pre-18243 restatement, not the full replacement")
    a23h = " ".join(str(x.get("decree", "")) + str(x.get("description", ""))
                    for x in a23.get("history", []))
    if "18243" not in a23h or "بالاتفاق بين وزير الداخلية ووزير النقل" not in a23h:
        e.append("[2m] Article 23 history must cite Decision 18243 AND preserve the superseded "
                 "1441 text (nothing is discarded)")

    # decision 3148 (26/2/1443) -- 47/2 chapeau ingested; its table is a DISCLOSED GAP.
    # The gap must stay disclosed: never silently filled, never quietly dropped.
    a47 = arts.get("traffic_regulation_art_047", {})
    a47t = a47.get("text", "")
    if "47/2- مع عدم الإخلال بأي عقوبة أشد" not in a47t:
        e.append("[2m] Article 47 must carry the verbatim 47/2 chapeau added by Decision 3148")
    if "فجوة معلنة غير محلولة" not in a47t or "32" not in a47t:
        e.append("[2m] Article 47 must keep the 47/2 penalty-table gap FLAGGED inline "
                 "(32 rows + clause 47/2/1 not recovered)")
    if re.search(r"(?m)^47/2/1-", a47t):
        e.append("[2m] Article 47 appears to contain reconstructed 47/2 table content; that "
                 "table was never recovered and must not be invented")
    if "3148" not in " ".join(str(x.get("decree", "")) for x in a47.get("history", [])):
        e.append("[2m] Article 47 history must cite Decision 3148")

    # preamble (the resolution text itself) must be present and carry the key facts
    pre = src.get("preamble_ar") or ""
    if not pre:
        e.append("[2p] missing preamble_ar (the resolution 2249 text recovered from page 1)")
    else:
        if "2249" not in pre:
            e.append("[2p] preamble_ar must contain resolution number 2249")
        if "7019" not in pre:
            e.append("[2p] preamble_ar must record supersession of 7019 (clause ثانياً)")
        if "عبدالعزيز بن سعود" not in pre:
            e.append("[2p] preamble_ar must contain the signing Minister of Interior's name")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("traffic_regulation_art_001", {})
    if "تسري أحكام هذا النظام" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected scope wording")
    art2 = arts.get("traffic_regulation_art_002", {})
    if "هيكل المركبة" not in art2.get("text", "") or "التفحيط" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected definitions (هيكل المركبة / التفحيط)")
    art7 = arts.get("traffic_regulation_art_007", {})
    if art7.get("legal_status_ar") != "معدلة" or "اللوحات" not in art7.get("text", ""):
        e.append("[2j] Article 7 must be معدلة and cover vehicle plate types")
    art50m = arts.get("traffic_regulation_art_050_mukarrar", {})
    if not art50m or "تجارية" not in art50m.get("text", "") \
            or art50m.get("number_label_ar") != "المادة الخمسون مكرر":
        e.append("[2j] المادة الخمسون مكرر must be present, is_mukarrar, cover المراكز التجارية")
    art76 = arts.get("traffic_regulation_art_076", {})
    if "90" not in art76.get("text", "") or "سحب" not in art76.get("text", ""):
        e.append("[2j] Article 76 must carry the demerit-points system (90 points / licence "
                 "withdrawal) as issued by Resolution 2249")
    art80 = arts.get("traffic_regulation_art_080", {})
    if art80.get("legal_status_ar") != "ملغاة" or "مجلس أعلى للمرور" not in art80.get("text", ""):
        e.append("[2j] Article 80 must be ملغاة and preserve its (repealed) Supreme Traffic "
                 "Council text verbatim, not deleted")
    else:
        hist = " ".join(str(h.get("decree", "")) + str(h.get("description", ""))
                        for h in art80.get("history", []))
        if "636" not in hist:
            e.append("[2j] Article 80 history must cite the repealing instrument (CoM 636)")
    if src.get("decree") != "القرار الوزاري رقم (2249)" \
            or src.get("decree_date_hijri") != "10/3/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Resolution "
                 "2249, 10/3/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")

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
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if "7019" not in str(summary.get("supersedes", "")):
        e.append("[4b] summary must record supersession of 7019/1429H")

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Traffic Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Traffic Law")
    print("  - 86 records: 74 اصلية, 11 معدلة (Articles 7, 16, 17, 21, 23, 47, 50, 51, 54, 59,")
    print("    68), 1 ملغاة (Article 80), 0 مضافة")
    print("  - 8 chapters; 85 numbered articles plus المادة الخمسون مكرر (commercial-centre licensing)")
    print("  - Ministerial Resolution (Minister of Interior) No. (2249), 10/3/1441H, under the")
    print("    Traffic Law (Royal Decree M/85) -- SUPERSEDES the prior Resolution 7019/1429H")
    print("    (verbatim clause ثانياً in the resolution text on page 1 of the primary source)")
    print("  - VERIFICATION TIER: PRIMARY official scanned MOI document (page 1 = stamped/signed")
    print("    resolution); vision reading cross-checked against tesseract-ara OCR. laws.boe.gov.sa")
    print("    checked first but has no dedicated lawId page for this Implementing Regulation at all.")
    print("    Articles 1-8 cross-validated against qanoniah.com born-digital text: 100% for six")
    print("    articles, 99.0% for Article 2 (cosmetic); Article 7's 51.5% divergence confirms its")
    print("    amendment and that the scan is the original 1441 issuance.")
    print("  - INGESTED VERSION: the 1441 as-issued text UPDATED with all five gazette-confirmed")
    print("    amending decisions of the Minister of Interior, each re-verified against")
    print("    uqn.gov.sa this pass (qanoonsa.com as second source where indexed):")
    print("      3148  26/2/1443H  adds 47/2 (chapeau only -- see the disclosed gap below)")
    print("      18243 5/12/1443H  REPLACES Article 23 in full (10 clauses + fine tables)")
    print("      5622  1/4/1444H   amends 7/1/3/2 (diplomatic/consular plates)")
    print("      1924  1/5/1447H   DELETES 21/1/4 (SAR 200,000 showroom bank guarantee)")
    print("      5330  16/12/1447H adds 16/1/5, 17/2/13, 50/12, 51/7, 54/9, 59/5, 68/4")
    print("                        (المركبات ذاتية القيادة)")
    print("    None adds an article, so the record count stays 86. Superseded 1441 wording for")
    print("    Articles 7 and 23 is preserved in their history, never discarded.")
    print("  - DELETION: clause 21/1/4 is FLAGGED محذوفة inline with its text preserved verbatim")
    print("    (never removed); Article 21 reclassified اصلية -> معدلة.")
    print("  - REPEAL: Article 80 (Supreme Traffic Council) flagged ملغاة on an explicit footnote")
    print("    in the primary scan itself (Council of Ministers Resolution 636, 23/10/1438H); its")
    print("    text is preserved verbatim, never deleted.")
    print("  - DISCLOSED UNRESOLVED GAP: Article 47/2's 32-row violation/penalty table and its")
    print("    clause 47/2/1 are NOT ingested. The gazette text page stops at the chapeau and the")
    print("    annexed gazette PDF's text layer is corrupted by a ToUnicode/font-encoding defect")
    print("    (Arabic extracts as Latin mojibake). It was NOT transcribed from the corrupted")
    print("    layer and NOT reconstructed. Flagged inline in Article 47 and in")
    print("    known_unresolved_discrepancies; OCR-on-rendered-images is the follow-up route.")
    print("  - SOURCE CAUTION recorded for future passes: the track's prior basis (the 1441")
    print("    scanned MOI document) was TWO decisions stale in the sense that it gave no notice")
    print("    at all of decisions 1924 and 5330; treat it as a historical founding text, not a")
    print("    current consolidated one, and re-scan the gazette past 5330 (16/12/1447H).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
