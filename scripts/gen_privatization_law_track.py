#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Privatization Law track (نظام التخصيص,
Royal Decree M/63, 5/8/1442H / 2021G).

VERIFICATION TIER -- see sources/privatization/law/official_source/
privatization_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa DOES have a
dedicated lawId page for this law (8af67ec1-6776-4f67-abb4-ad0900eadf2f) but the
live portal returned HTTP 503 (WebFetch) / HTTP 000 connection-reset (direct
curl) on repeated attempts -- the same pattern documented for the water,
electricity and agriculture tracks this session. web.archive.org is an
org-egress-policy block and was NOT routed around.

OFFICIAL SOURCE THAT WAS REACHED (this is what lifts the tier above the
water/electricity/agriculture TIER_3 tracks): an OFFICIAL GOVERNMENT PDF
published by the Ministry of Investment (misa.gov.sa) and issued by the National
Center for Privatization (National Center for Privatization & PPP, ncp.gov.sa)
was fetched directly (HTTP 200, ~800KB). It CONFIRMED: (1) the article count is
exactly 45 (sequential المادة الأولى ... المادة الخامسة والأربعون, the last one
on page 19 before the "القواعد المنظمة للتخصيص" section begins); (2) the law is
FLAT -- no أبواب/فصول chapter divisions; (3) verbatim spot-check matches --
Article 45 ("يلغي النظام كل ما يتعارض معه من أحكام، ويعمل به بعد مضي (مائة
وعشرين) يوما ...") and Article 44 (NCP board issues the Implementing Regulation
+ competition/contract templates) both match nezams.com word-for-word. NOTE:
pdftotext reverses some in-word letter-groups in this particular PDF ("عرشة" for
"عشرة"), so the FULL governing text was adopted from nezams.com (unreversed), and
the MISA/NCP PDF was used only for count/structure confirmation and verbatim
spot-checking (where the checked words are correctly ordered).

FULL GOVERNING TEXT: nezams.com (an independent Arabic legal-text aggregator,
NOT a BOE mirror), fetched directly via curl (HTTP 200). Its 45 "subject" HTML
elements (subject-1 .. subject-45, spelled-ordinal labels المادة الأولى ...
المادة الخامسة والأربعون) supplied every article verbatim. Its page metadata
states explicitly "التعديلات: لم يجر عليه تعديل" (no amendment). Identity/preamble
were also independently confirmed via WebSearch indexing of BOE's own content and
the Umm Al-Qura gazette page (uqn.gov.sa/?p=638, titled "مرسوم ملكي رقم (م/63)").

TIER_2 (honestly assessed, with a disclosed reservation that a strict reading of
"governing text adopted FROM the primary" could grade it TIER_3): one primary
OFFICIAL source reached (MISA/NCP PDF, HTTP 200) and used to confirm the
governing text at the count/structure/spot-verbatim level, plus full comparative
audit against the non-government secondary nezams.com (from which the full body
text is taken), without a full article-by-article confirmation from a second
independent OFFICIAL source. Not overstated.

45 records, ALL اصلية (45 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة). The law is FLAT: a
single chapter_structure entry covers 1-45 and section_ar carries the uniform
value "نظام التخصيص" for every article -- NO thematic chapter titles were
invented. No inline per-article titles beyond spelled-ordinal "المادة ..."
labels -- no title_ar field is used.

REPEAL: Article 45 is a GENERIC conflict-only clause (contrast the water track's
NAMED repeal). The NAMED repeals live in the accompanying Council of Ministers
Resolution 436 (item ثانياً: CoM decisions 60/1418H, 257/1421H, 219/1423H, and
the repealed Supreme Economic Council decision 1/23/1423H approving the
privatization strategy) -- these are CoM/SEC instruments, not standalone
Royal-Decree laws, preserved in full in preamble_ar and flagged for a repo-level
supersession graph (owner's call).

TASHKEEL: nezams.com's source text carries partial tashkeel (harakat). Harakat
are stripped uniformly for consistency with this corpus's majority; tatweel is
preserved only in the Hijri "هـ" marker. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "privatization", "law", "official_source",
                   "privatization_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "privatization", "law", "verified")
RECORDS = os.path.join(OUT_VER, "privatization_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "privatization_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "privatization_arabic_legal_llm",
                        "privatization_law_legal_llm_001_045.json")

LAW_ID = "sa-privatization-law-m-63-1442"
LAW_AR = "نظام التخصيص"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"privatization_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم التخصيص المركز الوزارة الجهة").split())


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
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    gov_note = ("Arabic governs; laws.boe.gov.sa DOES have a dedicated lawId page for this law "
                "(8af67ec1-6776-4f67-abb4-ad0900eadf2f) but the live portal was unreachable this "
                "pass (HTTP 503 / connection reset; web.archive.org egress-blocked and NOT "
                "bypassed). An OFFICIAL government PDF (misa.gov.sa, issued by the National Center "
                "for Privatization, HTTP 200) WAS reached and confirmed the 45-article count, the "
                "flat no-chapter structure, and verbatim spot-checks of Articles 44-45; the full "
                "governing text is from nezams.com (independent aggregator, HTTP 200), whose "
                "metadata states the law has had NO amendments. Identity/preamble independently "
                "confirmed via WebSearch indexing of BOE's own content and the Umm Al-Qura gazette. "
                "All 45 articles are اصلية. Article 45 is a GENERIC conflict-repeal clause; the "
                "NAMED repeals are in the accompanying CoM Resolution 436 (preserved in preamble_ar). "
                "See verification_methodology_note and known_unresolved_discrepancies in the source "
                "artifact before relying on this track's text or provenance.")
    gov_note_ar = ("العربية هي اللغة الحاكمة؛ لبوابة هيئة الخبراء (laws.boe.gov.sa) صفحة مخصصة لهذا "
                   "النظام (lawId 8af67ec1-6776-4f67-abb4-ad0900eadf2f) لكنها غير قابلة للوصول هذه "
                   "الجولة (503/إعادة تعيين الاتصال؛ أرشيف الإنترنت محظور ولم يُتجاوَز). جُلب ملف "
                   "رسمي حكومي (misa.gov.sa، صادر عن المركز الوطني للتخصيص، HTTP 200) وأكّد عدد "
                   "المواد (45) والبنية المسطحة (بلا أبواب/فصول) وتطابق العيّنة النصية (المادتان 44 "
                   "و45)؛ النص الحاكم الكامل من nezams.com (مصدر مستقل، HTTP 200) الذي تنص بياناته "
                   "على عدم وجود أي تعديل. أُكّدت الهوية والديباجة مستقلا عبر فهرسة محرك البحث لمحتوى "
                   "البوابة وصفحة أم القرى. جميع المواد الـ45 اصلية. المادة 45 بند إلغاء عام؛ "
                   "الإلغاءات المسماة في قرار مجلس الوزراء المرافق 436 (محفوظ في preamble_ar).")

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
        ver.append({"law_key": "privatization", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PRIVATIZATION_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "privatization-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "privatization/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام التخصيص" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/63 (5/8/1442H), CoM "
                                                          "Resolution 436 (3/8/1442H) — full text "
                                                          "from nezams.com (independent aggregator); "
                                                          "article count (45), flat no-chapter "
                                                          "structure and Articles 44-45 verbatim "
                                                          "independently confirmed via the OFFICIAL "
                                                          "MISA/National Center for Privatization "
                                                          "PDF (HTTP 200); identity/preamble also "
                                                          "confirmed via WebSearch indexing of BOE's "
                                                          "own content and the Umm Al-Qura gazette; "
                                                          "laws.boe.gov.sa's dedicated lawId page "
                                                          "(8af67ec1-6776-4f67-abb4-ad0900eadf2f) "
                                                          "was unreachable this pass (live 503; "
                                                          "Wayback egress-blocked, not bypassed)"),
                                     "source_authority_ar": gov_note_ar,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "privatization",
               "layer": "PRIVATIZATION_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-privatization-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (45 مادة؛ 45 أصلية)",
               "title_en": "Saudi Arabian Privatization Law — Arabic LLM-ready layer (45 records: 45 original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 45], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Privatization Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
