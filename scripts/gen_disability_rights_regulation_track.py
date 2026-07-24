#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Rights of Persons with
Disabilities Law track (اللائحة التنفيذية لنظام حقوق الأشخاص ذوي الإعاقة,
Resolution No. 26 of the Board of Directors of the Authority for the Care of
Persons with Disabilities, 29/10/1445H [29 Shawwal 1445H] / ~8 May 2024G).
This is the companion-regulation follow-up candidate explicitly flagged by
this corpus's own disability_rights_law track (see sources/disability_rights/
law/official_source/disability_rights_law_official_source.json,
known_unresolved_discrepancies key
disability_rights_law_implementing_regulation_out_of_scope). This track
ingests it. Article 31 of the base Law (Royal Decree M/27, 11/2/1445H)
mandates the Authority's Board issue this Implementing Regulation within 120
days of the Law's issuance, after coordination with relevant entities.

VERIFICATION TIER -- see sources/disability_rights_regulation/law/
official_source/disability_rights_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the official Umm al-Qura Gazette portal itself (uqn.gov.sa)
-- the dedicated page for the Regulation's full text (uqn.gov.sa/details?
p=24967; a 301 redirect to www.uqn.gov.sa was followed automatically, final
HTTP 200, ~963 KB) carries the complete text as direct HTML (NOT a scanned
image/PDF), making this a direct primary government source for the text
itself. The accompanying approval-resolution page (uqn.gov.sa/details?
p=24966) was also fetched directly (HTTP 200, ~786 KB) and carries the full
resolution text (clauses أولا/ثانيا), though it does not restate the
resolution's own number (26) within its operative text (normal for board
resolutions; the number is archival metadata).

SECONDARY SOURCE (cross-verified verbatim): qanoonsa.com -- two pages,
/p/503307/ (full regulation text) and /p/503306/ (approval resolution text),
both fetched directly via curl (HTTP 200). qanoonsa.com's own page title for
the resolution ("قرار رقم (26)") is the source that confirms the resolution
number 26 explicitly (not shown in the uqn.gov.sa operative text itself), and
its resolution-page footer supplies the Umm al-Qura issue number (5033, dated
24 May 2024G) -- also not explicitly shown on the uqn.gov.sa page as
retrieved this pass (which only carries an internal article-add date of 17
May 2024G, not necessarily the same as the printed issue's cover date).

ARTICLE-BY-ARTICLE CROSS-CHECK: all 45 articles were diffed programmatically
between uqn.gov.sa (primary) and qanoonsa.com (secondary) after normalizing
diacritics/digit-style/whitespace. 15/45 matched byte-for-byte; the other
30/45 differed only in cosmetic ways confined to the qanoonsa.com copy (its
own numbering-punctuation style "1." vs uqn.gov.sa's "1", and isolated
qanoonsa-only typos: "أدله" for "أدلة", "زملاءه" for "زملائه", "وسائلة" (an
extra letter) for "وسائل", "ذو" for "ذي" in one grammatical position). One
single-word variance was not resolved with full confidence (Article 1:
"كل من" on uqn.gov.sa vs "كلا من" on qanoonsa.com) -- the OFFICIAL uqn.gov.sa
wording ("كل من") is what this track stores. No article showed any
substantive/legal difference between the two sources.

NOT TIER_1 (multiple PRIMARY sources) because laws.boe.gov.sa -- which per
WebSearch results shares the base Law's lawId page rather than hosting a
dedicated lawId page for this Regulation -- was checked first per this
corpus's standard methodology but returned "Recv failure: Connection reset
by peer" on direct curl (same live-access failure recorded for the base Law
track); this was NOT circumvented. web.archive.org was not re-attempted this
pass (confirmed egress-blocked for this session in the base Law track).
IS TIER_2 (primary + secondary cross-verified) on the strength of uqn.gov.sa
(official Umm al-Qura Gazette portal, direct HTML text, no OCR/vision step
needed) cross-checked verbatim article-by-article against qanoonsa.com.

CHAPTER-COUNT DISCREPANCY DISCLOSED, NOT SILENTLY RESOLVED: the PRIMARY
uqn.gov.sa text explicitly shows 12 chapters (الفصل الأول..الفصل الثاني
عشر: الأحكام الختامية), while a THIRD independent source (argaam.com, a
well-known Saudi financial/economic news outlet) states "11 فصلا، تتضمن 45
مادة" -- and qanoonsa.com's own copy of the text omits an <h3> header for
the 12th chapter (though it DOES contain Articles 43-45's text in full, just
without that chapter heading rendered). This track adopts 12 chapters,
following the direct primary government source, and records the 11-vs-12
discrepancy explicitly rather than picking a number silently. The article
count of 45 is undisputed across all three sources.

NAME-COLLISION WARNING: web searches for amendments to this regulation
surface an unrelated EGYPTIAN law of near-identical Arabic name ("اللائحة
التنفيذية لقانون حقوق الأشخاص ذوي الإعاقة رقم 10 لسنة 2018", amended by
Egyptian PM resolutions 820/2020 and 2500/2024) -- NOT this Saudi
regulation. No evidence was found of any amendment to the actual Saudi
Regulation covered by this track since its issuance (29 Shawwal 1445H)
through this research date (2026-07-24); nezams.com carries no dedicated
page for this Regulation at all (only for the base Law).

45 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة). 12 chapters (فصول): Ch.1
أحكام عامة (1-3); Ch.2 إمكانية الوصول (4-6); Ch.3 إمكانية الوصول والترتيبات
التيسيرية في الدعوى الجزائية (7-7); Ch.4 حق التنقل (8-12); Ch.5 حق التعليم
(13-20); Ch.6 حق الصحة (21-28); Ch.7 التوظيف وفرص العمل (29-32); Ch.8 أماكن
العبادة ومرافقها (33-33); Ch.9 الوعي المجتمعي (34-34); Ch.10 حق الوصول
للمحتوى المقروء والمرئي والمسموع (35-37); Ch.11 الدعم الاجتماعي والاقتصادي
(38-42); Ch.12 الأحكام الختامية (43-45).

ANNEX NOT MODELED: الملحق (1) (a table of compensatory/assistive medical
devices) follows Article 45 on both sources as a separate HTML table, not a
numbered article -- not modeled as a record here, matching how this corpus's
other regulation tracks treat annex tables (cf.
traffic_regulation_annex_tables_not_modeled).

Diacritics (tashkeel) are stripped uniformly for consistency with this
corpus's other tracks (harakat range U+064B-U+0652 plus related marks).
Decorative in-word tatweel introduced by the source document's justified-text
formatting is stripped, while legitimate tatweel after the letter ه (the
alphabetic list-marker "هـ-" and the Hijri-date suffix "هـ") is retained,
matching this corpus's established _bad_tatweel convention. Arabic governs;
no translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "disability_rights_regulation", "law", "official_source",
                   "disability_rights_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "disability_rights_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "disability_rights_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "disability_rights_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "disability_rights_regulation_arabic_legal_llm",
                        "disability_rights_regulation_legal_llm_001_045.json")

LAW_ID = "sa-disability-rights-regulation-res-26-1445"
LAW_AR = "اللائحة التنفيذية لنظام حقوق الأشخاص ذوي الإعاقة"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"disability_rights_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة الجهة المعنية الأشخاص ذوي الإعاقة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def _top_status(key):
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; PRIMARY source is the official Umm al-Qura Gazette portal "
            "(uqn.gov.sa) itself -- the Regulation's dedicated page (details?p=24967) carries "
            "the full text as direct HTML, not a scanned image, and was fetched directly (HTTP "
            "200). Cross-checked verbatim article-by-article against qanoonsa.com (an "
            "independent secondary aggregator) -> TIER_2. 45 articles, 12 chapters (فصول); ALL "
            "اصلية (no amendment found since issuance). laws.boe.gov.sa shares the base Law's "
            "lawId page rather than hosting a dedicated page for this Regulation, and was "
            "unreachable live this pass (connection reset), not circumvented. A THIRD source "
            "(argaam.com) states 11 chapters, not 12 -- this track follows the primary "
            "uqn.gov.sa source's explicit 12-chapter structure and discloses the discrepancy "
            "rather than resolving it silently. See verification_methodology_note and "
            "known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance.")

SRC_AUTH = ("Resolution No. (26) of the Board of Directors of the Authority for the Care of "
            "Persons with Disabilities (29/10/1445H [29 Shawwal], ~8 May 2024G), issued under "
            "Article 31 of the Law of Rights of Persons with Disabilities (Royal Decree M/27, "
            "11/2/1445H). Full text from uqn.gov.sa (official Umm al-Qura Gazette portal, "
            "primary) cross-checked verbatim against qanoonsa.com (independent secondary "
            "source) -> TIER_2. Resolution number and gazette issue number (5033, 24 May 2024G) "
            "confirmed via qanoonsa.com only, not shown explicitly in the uqn.gov.sa operative "
            "text as retrieved this pass.")

SRC_AUTH_AR = ("قرار مجلس إدارة هيئة رعاية الأشخاص ذوي الإعاقة رقم (26) وتاريخ 29/10/1445هـ (29 "
               "شوال، ~8 مايو 2024م)، صادر استنادا إلى المادة الحادية والثلاثين من نظام حقوق "
               "الأشخاص ذوي الإعاقة (المرسوم الملكي م/27، 11/2/1445هـ). النص الكامل من uqn.gov.sa "
               "(بوابة جريدة أم القرى الرسمية، مصدر أساسي) متقاطع حرفيا مع qanoonsa.com (مصدر "
               "ثانوي مستقل) -- TIER_2. رقم القرار ورقم عدد الجريدة (5033، 24 مايو 2024م) مؤكدان "
               "من qanoonsa.com فقط، غير ظاهرين صراحة في نص uqn.gov.sa التشغيلي كما استُرجع هذه "
               "الجولة.")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        ver.append({"law_key": "disability_rights_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "DISABILITY_RIGHTS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "disability-rights-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "disability_rights_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام حقوق الأشخاص ذوي الإعاقة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "disability_rights_regulation",
               "layer": "DISABILITY_RIGHTS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-disability-rights-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (45 مادة أصلية)",
               "title_en": ("Implementing Regulation of the Rights of Persons with Disabilities "
                            "Law — Arabic LLM-ready layer (45 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 45], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Disability Rights Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
