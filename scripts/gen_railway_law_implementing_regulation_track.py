#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Railway Law track (اللائحة
التنفيذية لنظام الخطوط الحديدية, TGA Board Resolution No. 4/1/1/2024, dated
19/12/1445H; published Umm Al-Qura Official Gazette 22/4/1446H = 25/10/2024G).
Implementing regulation of the railway_law base-law track already in this
corpus (Royal Decree M/159, 22/8/1445H, 50 articles) -- NOT touched this pass.

VERIFICATION TIER -- see sources/railway_law_implementing_regulation/law/
official_source/railway_law_implementing_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

TWO INDEPENDENT OFFICIAL/PRIMARY SOURCES, both fetched and both server-
rendered (not AI-summarized):
  (1) tga.gov.sa/Regulations/Read/2086 -- the administering authority's
      (General Authority for Transport, TGA) own official regulations
      portal. The LIVE page is unreachable this pass (curl: connection
      reset; WebFetch: HTTP 503); a confirmed Wayback Machine snapshot
      (20250117203855, fetched via the archive's raw 'if_' rendering) IS
      server-rendered and carries the full 91-article body inline (Bootstrap
      accordion HTML), parsed with BeautifulSoup using a block-aware text
      serializer (only <p>/<li>/<div>/<tr> boundaries insert a newline, not
      every inline <strong>/<span> tag -- a self-discovered and corrected
      naive-extraction bug, see the source artifact's methodology note).
  (2) uqn.gov.sa/details?p=26674 -- the Umm Al-Qura OFFICIAL GAZETTE's own
      dedicated page for this exact Regulation, fetched LIVE (HTTP 200, zero
      reachability gap, no Wayback needed). A companion Gazette page
      (uqn.gov.sa/details?p=26673) carries the TGA Board Resolution's own
      text verbatim (number, date, basis), confirming the Resolution's
      citation independently of any press source.

CROSS-CHECK: all 91 articles diffed programmatically (Python, digit/hamza/
tashkeel-normalized, enumeration-marker-stripped) between the two sources.
38 matched byte-for-byte immediately; the remaining 53 differed only in
punctuation placement or grammatical case-ending (never in a monetary
amount, deadline, or substantive obligation) -- each of the 53 was read
manually in full. ONE genuine spelling divergence was found and resolved
(Article 15: TGA's site reads "استفياء" -- a plain typo -- vs. the Gazette's
correct "استيفاء"; the Gazette's spelling was adopted for that one word).

TWO STRUCTURAL ANOMALIES ON TGA'S OWN WEBSITE, BOTH INDEPENDENTLY RESOLVED
BY THE GAZETTE (see known_unresolved_discrepancies for full detail):
  - A stray, non-numbered accordion item titled "المادة الاربعون:" (holding
    only an effective-date sentence) is wedged between Article 39 and the
    violations table on TGA's site -- entirely ABSENT from the Gazette,
    which flows directly from Article 39 to the true Article 40. Confirmed
    as a TGA-side leftover artifact, not governing text; not modeled as an
    article (this track's 91-article count matches the Gazette exactly).
  - TGA's site labels Chapters 5 and 6 "أمن وسلامة الخطوط الحديدية ومرافقها"
    and "التحقيق في حوادث الخطوط الحديدية وعوارضها" respectively -- neither
    title matches those chapters' actual articles (licensing fees; license
    cancellation/suspension grounds). The Gazette gives the CORRECT titles
    ("المقابل المالي"; "حالات إلغاء الترخيص أو تعليقه"), adopted here.

GOVERNING TEXT: the Umm Al-Qura Gazette (uqn.gov.sa) is used as the stored/
governing text for all 91 articles (higher statutory authority, zero
reachability gap, retains explicit "أ- ب- 1- 2-" sub-item enumeration that
TGA's own site's CSS-numbered <li> markup drops from its text nodes). TGA's
site served as the independent cross-check AND as the sole source for the
violations/penalties table's actual figures (see below).

VIOLATIONS TABLE (جدول المخالفات والعقوبات, 25 violations): referenced by
Article 86 in BOTH sources by name only (published as a separate PDF
attachment on both portals, per their own "تحميل" links); TGA's site
uniquely embeds the table's full HTML <table> (25 numbered rows) inline.
Parsed row-by-row with a custom rowspan/colspan-aware grid builder (never
naive tag-stripping), yielding exactly 25 violations -- matching the Saudi
Press Agency's own official wire (spa.gov.sa) verbatim count ("حددت اللائحة
25 مخالفة"). Merged as prose into Article 86's own stored text (the article
that incorporates it by reference), consistent with this corpus's estab-
lished pattern for commercial_register_regulation and mining_investment_
implementing_regulation.

TIER: TIER_1 -- two independent, genuinely official/primary sources (TGA's
own administering-authority portal + the Umm Al-Qura Official Gazette) were
each reached and agree, article-by-article, in substance across all 91
articles (punctuation/case-ending-level variance only, one typo resolved).
Further corroborated (article/violation counts, adoption date) by three
independent press sources (spa.gov.sa official wire, argaam.com, sabq.org).

91 articles, 16 فصول (1-1 / 2-3 / 4-7 / 8-25 / 26-27 / 28-32 / 33-33 / 34-36
/ 37-39 / 40-41 / 42-54 / 55-56 / 57-59 / 60-71 / 72-89 / 90-91); all 91
اصلية; 0 معدلة, 0 ملغاة, 0 مضافة. consolidated_amended_law=False (this is
the sole known founding version; no amendment evidence found via either
source). Arabic governs; no translation/paraphrase/interpretation performed.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "railway_law_implementing_regulation", "law",
                   "official_source", "railway_law_implementing_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "railway_law_implementing_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "railway_law_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "railway_law_implementing_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "railway_law_implementing_regulation_arabic_legal_llm",
                        "railway_law_implementing_regulation_legal_llm_001_091.json")

LAW_ID = "sa-railway-law-implementing-regulation-tga-4-1-1-2024"
LAW_AR = "اللائحة التنفيذية لنظام الخطوط الحديدية"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير المرخص الرخصة رخصة الهيئة المجلس الرئيس").split())
KEY_RE = r"railway_law_implementing_regulation_art_(\d{3})$"


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    governing_source_note = (
        "Arabic governs. TWO independent official/primary sources: (1) tga.gov.sa (General "
        "Authority for Transport's own regulations portal), live unreachable this pass, reached "
        "via a Wayback Machine snapshot (20250117203855) that IS server-rendered; (2) uqn.gov.sa "
        "(Umm Al-Qura OFFICIAL GAZETTE)'s own dedicated page for this Regulation, fetched LIVE with "
        "zero reachability gap. All 91 articles cross-checked programmatically between the two; "
        "38 matched byte-for-byte immediately, the remaining 53 differed only in punctuation/case-"
        "ending (one typo resolved: Article 15 'استفياء'->'استيفاء' per the Gazette). GOVERNING "
        "TEXT = the Gazette (higher statutory authority, retains explicit 'أ- ب- 1- 2-' sub-item "
        "enumeration TGA's own site drops). TGA's site independently resolved as carrying two "
        "stale/erroneous artifacts NOT present in the Gazette: a stray non-numbered 'Article 40' "
        "effective-date fragment, and mismatched titles for Chapters 5-6 (fees; license "
        "cancellation) -- both corrected using the Gazette, see known_unresolved_discrepancies. "
        "Violations table (25 rows, referenced by Article 86) was present as an in-body HTML "
        "<table> ONLY on TGA's site (both sources otherwise reference it as a separate PDF "
        "attachment); parsed rowspan/colspan-aware and merged into Article 86's own text -- count "
        "matches spa.gov.sa's official wire verbatim ('حددت اللائحة 25 مخالفة'). TIER_1: two "
        "independent official/primary sources agree, article-by-article, across all 91 articles."
    )
    source_authority_ar = (
        "قرار مجلس إدارة الهيئة العامة للنقل رقم (4/1/1/2024) وتاريخ 19/12/1445هـ، منشور كاملاً في "
        "جريدة أم القرى الرسمية بتاريخ 22/4/1446هـ الموافق 25/10/2024م. نص حاكم من مصدرين رسميين "
        "مستقلين متطابقين: موقع الهيئة العامة للنقل (tga.gov.sa، عبر أرشيف Wayback) وجريدة أم "
        "القرى الرسمية (uqn.gov.sa، مجلوبة حية مباشرة). اعتُمد نص الجريدة حاكماً؛ حسم مستقلاً شذوذي "
        "'المادة الاربعون' الزائفة وعنواني الفصلين الخامس والسادس على موقع الهيئة. جدول المخالفات "
        "والعقوبات (25 مخالفة) مدمج داخل نص المادة السادسة والثمانين، مصدره الوحيد جدول HTML مضمَّن "
        "على موقع الهيئة، مؤكَّد العدد بواسطة وكالة الأنباء السعودية الرسمية. TIER_1."
    )

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        section = a.get("section_ar") or ""
        ver.append({"law_key": "railway_law_implementing_regulation",
                    "law_component": "regulation", "language": "ar",
                    "record_layer": "RAILWAY_LAW_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": bool(a.get("is_mukarrar")),
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": governing_source_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": bool(a.get("is_mukarrar")), "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "railway-law-implementing-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "railway_law_implementing_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الخطوط الحديدية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": (
                                        "TGA Board Resolution No. (4/1/1/2024), 19/12/1445H, "
                                        "published Official Gazette 22/4/1446H (25/10/2024G). "
                                        "Governing text from two independent official sources: "
                                        "tga.gov.sa (Wayback archive) and the Umm Al-Qura Official "
                                        "Gazette (uqn.gov.sa, fetched live). TIER_1."),
                                     "source_authority_ar": source_authority_ar,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "railway_law_implementing_regulation",
               "layer": "RAILWAY_LAW_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "base_law_key": src.get("base_law_key"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "gazette_publication": src.get("gazette_publication"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-railway-law-implementing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (91 مادة؛ 91 أصلية، "
                                     "0 معدلة، 0 مضافة، 0 ملغاة؛ 16 فصلاً)",
               "title_en": ("Implementing Regulation of the Railway Law — Arabic LLM-ready layer "
                            "(91 records: 91 original, 0 amended, 0 added, 0 repealed; 16 فصول)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 91], "text_status": "UNCHANGED",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Railway Law Implementing Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
