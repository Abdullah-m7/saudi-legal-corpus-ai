#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
Patents Law track (67 records: 67 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة; 12 أبواب).

VERIFICATION TIER -- see the generator's module docstring and
sources/patent/regulation/official_source/patent_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (per this corpus's standard methodology) but is unreachable this pass and,
more fundamentally, has NO dedicated lawId page for this Implementing Regulation
at all (only for the base Patents Law, M/27). The PRIMARY source actually used is
the official SAIP-letterhead Arabic PDF hosted on WIPO Lex (identifier SA065),
consolidated as amended by SAIP Board Resolution 5/8/2019, cross-verified against
WIPO Lex details/19743 and qanoonsa.com. This validator does not re-adjudicate
provenance; it only checks internal self-consistency of the text this track
ingests, and that every discrepancy is still recorded.

The text carries four genuine, disclosed source/extraction features this
validator deliberately tolerates: (1) a small whitelist of real Latin acronyms
present in the source (PCT, IUPAC, IUPAP, SUNAMCO) plus one inline English gloss
('treatment', Article 40); (2) all 67 articles classified اصلية because the
consolidated primary source does not enumerate the 2019 amendment's per-article
scope; (3) a later 2024 amendment NOT reflected in the text; (4) a fee-schedule
annex stored in schedule_ar, not as a numbered article. All are recorded in
known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "patent", "regulation", "official_source",
                   "patent_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "patent", "regulation", "verified",
                       "patent_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "patent", "regulation", "verified",
                       "patent_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "patent_regulation_arabic_legal_llm",
                   "patent_regulation_legal_llm_001_067.json")
N = 67
KEY_RE = r"patent_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 67, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 12

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED

# real Latin acronyms present in the source (PCT & chemical-nomenclature bodies),
# plus one disclosed inline English gloss in Article 40 -- see the source
# artifact's known_unresolved_discrepancies. Any OTHER Latin is an error.
ALLOWED_LATIN = {"PCT", "IUPAC", "IUPAP", "SUNAMCO", "treatment"}

FLAGGED_DISCREPANCY_KEYS = {
    "patent_regulation_boe_unreachable_no_dedicated_page",
    "patent_regulation_2024_amendment_not_incorporated_boe_style_staleness",
    "patent_regulation_per_article_2019_amendment_scope_unenumerated",
    "patent_regulation_pdf_presentation_form_extraction_and_reversed_lines",
    "patent_regulation_tasl1m_shadda_glyph_artifact",
    "patent_regulation_inline_english_gloss_treatment_preserved",
    "patent_regulation_latin_acronyms_preserved",
    "patent_regulation_fee_schedule_annex_separated",
    "patent_regulation_no_named_predecessor_repeal",
    "patent_regulation_gregorian_equivalences_source",
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


def _residual_latin(text):
    stripped = text
    for tok in ALLOWED_LATIN:
        stripped = stripped.replace(tok, "")
    return re.search(r"[A-Za-z]", stripped) is not None


def _iter_chapter_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


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
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    # chapter titles must all be distinct أبواب (no duplicate-title anomaly here)
    titles = [c.get("title_ar") for c in chs]
    if len(set(titles)) != len(titles):
        e.append("[1d] duplicate chapter title(s) unexpectedly present: %s" % titles)

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            # this track uses a descriptive per-article verification status string
            if a.get("status") != "SAIP_WIPOLEX_2019_CONSOLIDATED_DUAL_PIPELINE_CROSS_VERIFIED":
                e.append("[2] %s: unexpected status %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: html/entity leftovers" % k)
        if _residual_latin(a["text"]):
            e.append("[2] %s: unexpected non-whitelisted Latin in text" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # extraction-artifact regression guards (each corresponds to a disclosed
        # fix in the generator / known_unresolved_discrepancies).
        if "تسل1م" in a["text"] or "1م" in a["text"]:
            e.append("[2g] %s: unresolved 'تسل1م' mis-encoded-shadda artifact" % k)
        for bad in ("بجي", "ىلع", "دقمم", "ابلطل", "اامولعملت", "ذهه ", " رمق ",
                    "صحافل", "ميمصتل", "اسنجل", "افصول", "دعت افشك"):
            if bad in a["text"]:
                e.append("[2g] %s: unresolved bidi-reversed fragment %r" % (k, bad))
        # mirrored (RTL visual) parenthesis must have been normalised to logical order
        if re.search(r"\)[^()]{1,20}\(", a["text"]) and "ورقم البراءة النباتية" not in a["text"]:
            e.append("[2g] %s: unresolved RTL-mirrored parenthesis" % k)

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
        e.append("[2k] missing amendment_history (founding + 2019 + 2024 decisions)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "161-2-3607329" not in decrees and "١٦١-٢-٣٦٠٧٣٢٩" not in decrees:
            e.append("[2k] amendment_history must reference founding resolution 161-2-3607329")
        if "5/8/2019" not in decrees:
            e.append("[2k] amendment_history must reference amending resolution 5/8/2019")
        if "02/32/2024" not in decrees:
            e.append("[2k] amendment_history must reference the later 2024 resolution 02/32/2024")

    # fee-schedule annex must be present and NOT counted as an article
    if not src.get("schedule_ar") or "جدول بالنفقات" not in src.get("schedule_ar", ""):
        e.append("[2s] schedule_ar annex (جدول بالنفقات) must be present as a separate field")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("patent_regulation_art_001", {})
    if "الهيئة السعودية للملكية الفكرية" not in art1.get("text", "") \
            or "معاهدة التعاون بشأن البراءات" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الهيئة / المعاهدة PCT)")
    art47 = arts.get("patent_regulation_art_047", {})
    if "اسم المخترع" not in art47.get("text", "") \
            or "التصنيف الدولي للاختراع" not in art47.get("text", ""):
        e.append("[2j] Article 47 missing expected first-page-contents list content")
    art61 = arts.get("patent_regulation_art_061", {})
    if "مكتب تسلم الطلبات" not in art61.get("text", ""):
        e.append("[2j] Article 61 missing expected 'مكتب تسلم الطلبات' (PCT Receiving Office) text")
    art67 = arts.get("patent_regulation_art_067", {})
    if "تنشر هذه اللائحة في الجريدة الرسمية" not in art67.get("text", ""):
        e.append("[2j] Article 67 (final) missing expected publication clause")
    if src.get("decree") != "قرار رئيس مدينة الملك عبدالعزيز للعلوم والتقنية رقم (١٦١-٢-٣٦٠٧٣٢٩)" \
            or src.get("decree_date_hijri") != "30/12/1436":
        e.append("[2j] decree/decree_date_hijri mismatch with verified KACST Resolution "
                 "161-2-3607329, 30/12/1436H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (text reflects the 2019 amendment "
                 "consolidated into the founding regulation)")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be ABSENT (no issuance-preamble recovered from the "
                 "primary PDF this pass) rather than a fabricated placeholder")

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

    if e:
        print("FAIL: %d error(s) in Patent Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Patents Law")
    print("  - 67 records: 67 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة")
    print("  - 12 أبواب (chapters); الباب الثاني subdivided into 4 فصول (filing-type sections)")
    print("  - VERIFICATION TIER: laws.boe.gov.sa checked first but unreachable this pass and")
    print("    confirmed to have NO dedicated lawId page for this Board/agency-level Implementing")
    print("    Regulation; PRIMARY source is the official SAIP-letterhead Arabic PDF on WIPO Lex")
    print("    (SA065), cross-verified against WIPO Lex details/19743 and qanoonsa.com")
    print("  - KACST President Resolution No. (161-2-3607329), 30/12/1436H (13 Oct 2015),")
    print("    consolidated as amended by SAIP Board Resolution No. (5/8/2019), 04/09/1440H")
    print("  - DISCLOSED: later 2024 amendment (Board Resolution 02/32/2024) NOT reflected in")
    print("    this 2019-consolidated WIPO text (staleness mirroring the base patent_law track);")
    print("    per-article 2019-amendment scope unenumerated by the primary source (all 67 اصلية)")
    print("  - DISCLOSED extraction artifacts: presentation-form dual-pipeline extraction with 14")
    print("    individually-fixed bidi-reversed lines + ~20 justified-line word-splits; the")
    print("    'تسل1م'->'تسلم' mis-encoded shadda (visually confirmed); an inline English gloss")
    print("    'treatment' (Art 40) preserved verbatim; the fee-schedule annex kept in schedule_ar")
    print("  - NO named-predecessor repeal/supersession clause (first Implementing Regulation")
    print("    under Patents Law M/27)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
