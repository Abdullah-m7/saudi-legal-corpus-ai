#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Protection from Abuse Law track
(نظام الحماية من الإيذاء; 17 records: 14 اصلية, 3 معدلة [arts 7, 12, 13],
0 ملغاة, 0 مضافة; FLAT statute -- no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/protection_from_abuse/law/official_source/
protection_from_abuse_law_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa HAS a dedicated lawId page for this law
(83f450eb-7985-461f-b053-a9a700f2ba08) but it was unreachable this pass (HTTP
503 live / connection reset; web.archive.org egress-blocked and NOT bypassed).
ORIGINAL full text is from an OFFICIAL Ministry of Finance regulations-library
PDF (mof.gov.sa, Diwan Malaki circular 41930) cross-checked against nezams.com;
the 1443H amendment (arts 7/12/13, Royal Decree M/72 / CoM Resolution 427) is
confirmed by the Umm al-Qura OFFICIAL GAZETTE (uqn.gov.sa) X nezams.com ->
TIER_2. This validator does not re-adjudicate provenance; it only checks
internal self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); the 3 amended
articles carry both original and amendment_current history whose current text
equals `text`; NO predecessor repeal exists; the child_protection_law
distinction is recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "protection_from_abuse", "law", "official_source",
                   "protection_from_abuse_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "protection_from_abuse", "law", "verified",
                       "protection_from_abuse_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "protection_from_abuse", "law", "verified",
                       "protection_from_abuse_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "protection_from_abuse_arabic_legal_llm",
                   "protection_from_abuse_law_legal_llm_001_017.json")
N = 17
KEY_RE = r"protection_from_abuse_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 14, "معدلة": 3, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = {
    "protection_from_abuse_law_art_007",
    "protection_from_abuse_law_art_012",
    "protection_from_abuse_law_art_013",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "protection_from_abuse_boe_dedicated_page_exists_but_unreachable",
    "protection_from_abuse_amendment_m72_1443h_arts_7_12_13",
    "protection_from_abuse_art7_consolidation_note",
    "protection_from_abuse_ministry_now_hrsd",
    "protection_from_abuse_implementing_regulation_out_of_scope",
    "protection_from_abuse_distinct_from_child_protection_law",
    "protection_from_abuse_no_named_predecessor_repeal",
    "protection_from_abuse_tashkeel_stripped",
    "protection_from_abuse_gregorian_date_not_pinpointed",
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
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    # continuous 1..17, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # FLAT statute: chapter_structure MUST be empty (no chapters/فصول)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] this statute is flat (no chapters); chapter_structure must be [] but is %r"
                 % (chs,))

    sc = Counter()
    for k, a in arts.items():
        # NOTE: this corpus stores `status` as a descriptive free-text verification
        # string (not a fixed enum); we only require it be present and non-empty.
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
        # FLAT statute: section_ar MUST be empty for every article (no chapter titles)
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat statute" % k)
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
        # amended-article history integrity
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if "amendment_current" not in types or "original" not in types:
                e.append("[2m] %s: amended history must include amendment_current AND original" % k)
            cur = next((h for h in hist if h.get("type") == "amendment_current"), None)
            if cur and cur.get("text") != a["text"]:
                e.append("[2m] %s: history amendment_current text must equal current `text`" % k)
            if cur and "م/72" not in (cur.get("decree_note") or ""):
                e.append("[2m] %s: amendment_current decree_note must cite Royal Decree م/72" % k)
            orig = next((h for h in hist if h.get("type") == "original"), None)
            if orig and orig.get("text") == a["text"]:
                e.append("[2m] %s: original history text must DIFFER from amended current text" % k)

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
        if "م/52" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/52")
        if "م/72" not in decrees:
            e.append("[2k] amendment_history must reference amending decree م/72")

    # spot-checks anchoring key facts
    art1 = arts.get("protection_from_abuse_law_art_001", {}).get("text", "")
    if "الإيذاء" not in art1 or "إساءة المعاملة" not in art1:
        e.append("[2j] Article 1 missing expected abuse definition")
    art2 = arts.get("protection_from_abuse_law_art_002", {}).get("text", "")
    if "يهدف" not in art2:
        e.append("[2j] Article 2 missing expected objectives header")
    art7 = arts.get("protection_from_abuse_law_art_007", {}).get("text", "")
    if "أوراقه الثبوتية" not in art7:
        e.append("[2j] Article 7 (amended) missing added paragraph 6 (أوراقه الثبوتية)")
    art12 = arts.get("protection_from_abuse_law_art_012", {}).get("text", "")
    if "نظام الإجراءات الجزائية" not in art12 or "أشهر" not in art12:
        e.append("[2j] Article 12 (amended) missing expected replacement text")
    art13 = arts.get("protection_from_abuse_law_art_013", {}).get("text", "")
    for token in ("ثلاثمائة", "ذوي الإعاقة", "السجن"):
        if token not in art13:
            e.append("[2j] Article 13 (amended) missing expected token %r" % token)
    art16 = arts.get("protection_from_abuse_law_art_016", {}).get("text", "")
    if "اللائحة" not in art16 or "تسعين" not in art16:
        e.append("[2j] Article 16 missing expected implementing-regulation mandate")
    art17 = arts.get("protection_from_abuse_law_art_017", {}).get("text", "")
    if "تسعين" not in art17:
        e.append("[2j] Article 17 missing expected 90-day effective-date clause")

    # NO predecessor repeal anywhere (founding statute)
    for k, a in arts.items():
        if re.search(r"يلغى|يُلغى|يلغي|إلغاء كل|كل ما يتعارض", a["text"]):
            e.append("[2j] %s: unexpected repeal clause in a founding statute with no repeal" % k)

    if src.get("decree") != "المرسوم الملكي رقم م/52" or src.get("decree_date_hijri") != "15/11/1434":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/52, 15/11/1434H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS amendments incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "332" not in pre or "نظام الحماية من الإيذاء" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 332 and the law name")

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
        print("FAIL: %d error(s) in Protection from Abuse Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Protection from Abuse Law (نظام الحماية من الإيذاء)")
    print("  - 17 records: 14 اصلية, 3 معدلة (arts 7, 12, 13), 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-17, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (83f450eb-7985-461f-b053-a9a700f2ba08) but was unreachable this pass (live HTTP 503;")
    print("    web.archive.org egress-blocked and NOT bypassed). ORIGINAL full text from an official")
    print("    Ministry of Finance regulations-library PDF (mof.gov.sa, Diwan Malaki circular 41930)")
    print("    cross-checked verbatim against nezams.com; the 1443H amendment (arts 7/12/13) confirmed")
    print("    via the Umm al-Qura official gazette (uqn.gov.sa) X nezams.com")
    print("  - Royal Decree M/52 (15/11/1434H, ~2013G), CoM Resolution 332 (19/10/1434H), published")
    print("    Umm al-Qura 24/12/1434H; amended by Royal Decree M/72 (6/8/1443H) / CoM Resolution 427")
    print("    (5/8/1443H): Article 7 gained a paragraph (6); Articles 12 and 13 were fully replaced")
    print("  - NO predecessor repeal (founding statute; Article 17 is only the 90-day effective date)")
    print("  - DISTINCT from child_protection_law (نظام حماية الطفل, M/14 1436H): general vs")
    print("    child-specific; share only a co-amendment link via decree M/72, no textual overlap")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation (Ministerial Resolution")
    print("    43047, 8/5/1435H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
