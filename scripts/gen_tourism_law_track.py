#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Tourism Law track (نظام السياحة, Royal Decree M/18,
26/1/1444H / ~2022G).

VERIFICATION TIER -- see sources/tourism/law/official_source/
tourism_law_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law (7d777c66-d28b-43de-9305-af23013b1738) but the live
portal returned HTTP 503 (WebFetch) / connection-reset (direct curl). The
Umm al-Qura official gazette page for the decree (uqn.gov.sa/?p=17246) also
returned HTTP 503 via WebFetch, and a direct curl fetch returned an
un-rendered Vue/SPA shell (template placeholders, no content) -- it requires
JavaScript execution unavailable to the fetch tools used. web.archive.org was
explicitly refused by the WebFetch tool, and a direct curl through the proxy
returned HTTP 403; neither was bypassed.

SOURCES USED (TIER_2):
  * ORIGINAL full text (all 19 articles): an OFFICIAL Saudi GOVERNMENT PDF
    published directly by the Ministry of Tourism itself (cdn.mt.gov.sa,
    "Saudi-Tourism-Regulation-Ar-V014.pdf") -- the ministry entrusted with
    administering this exact law. Fetched directly (HTTP 200, 12 pages),
    extracted via pdftotext -layout, and cross-checked article-by-article
    against nezams.com (independent legal aggregator, HTTP 200, exactly 19
    "subject" elements subject-1..subject-19, spelled-ordinal labels
    المادة الأولى..التاسعة عشرة, no باب/فصل headers). Content matched for all
    19 articles (only PDF-extraction-only artifacts from justified-text
    line-wrapping and an embedded font's Lam-Alef ligature handling, not
    textual differences).
  * SUPPLEMENTARY, ENGLISH-ONLY, REFERENCE-ONLY cross-check: the official
    Bureau of Experts (Council of Ministers) translation, republished via
    misa.gov.sa (Tourism-Law.pdf, dated "August 24, 2022", last update
    "September 26, 2022"). Used ONLY to confirm article count (19), the flat
    (no-chapter) structure, and the substantive content/order of each
    article -- NEVER as a source of Arabic wording. Arabic governs; English
    was not used to correct or supply any Arabic text.

Not TIER_1 because the canonical BOE portal page itself (and the Umm al-Qura
gazette page) could not be retrieved or archived directly this pass.

19 records: all 19 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة. The statute has NO
chapter/باب/فصل divisions (flat 1-19); section_ar is empty for every article
by design.

NAMED-PREDECESSOR REPEAL CONFIRMED: Article 18 states verbatim "يحل النظام
محل نظام السياحة -الصادر بالمرسوم الملكي رقم (م/2) وتاريخ 9 /1/ 1436هـ- ويلغي
ما يتعارض معه من أحكام." Independently corroborated from the OTHER direction:
the predecessor law's own nezams.com record shows its "النفاذ" (effective)
field as "غير ساري، ألغي بصدور نظام السياحة الصادر بالمرسوم الملكي رقم (م/18)
وتاريخ 1444/1/26هـ". The predecessor's own name is also "نظام السياحة" (its
nezams.com CLASSIFICATION field reads "أنظمة السياحة والآثار" -- a category
label, not the law's own name). The predecessor's full text was NOT ingested
in this pass (one-law-per-track convention) -- flagged as a separate
follow-up candidate.

NO KNOWN AMENDMENTS to this (the current, M/18) law as of this pass:
nezams.com's own "التعديلات" field for this law reads "لم يجرى عليه تعديل."
Ten-plus separate Implementing Regulations have since been issued under this
law (hospitality facilities, travel and tourism services, tourist
destinations, tourist visas, inspection, violations committee, etc., all
published at cdn.mt.gov.sa) -- these are follow-up candidates, out of scope
for this track (one-law-per-track convention).

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; in-word decorative tatweel removed (هـ/جـ preserved);
double/nbsp spaces removed; mid-sentence line-wrap artifacts (a literal
<br/> falling mid-clause in the nezams.com source markup, e.g. Article 6
item د) rejoined into a single paragraph -- display-layer only, no legal
text altered. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tourism", "law", "official_source",
                   "tourism_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "tourism", "law", "verified")
RECORDS = os.path.join(OUT_VER, "tourism_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "tourism_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "tourism_arabic_legal_llm",
                        "tourism_law_legal_llm_001_019.json")

LAW_ID = "sa-tourism-law-m-18-1444"
LAW_AR = "نظام السياحة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"tourism_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات").split())


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


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa HAS a dedicated lawId page for this law "
            "(7d777c66-d28b-43de-9305-af23013b1738) but it was unreachable this pass "
            "(HTTP 503 live; the Umm al-Qura gazette page also 503'd via WebFetch and "
            "returned an un-rendered SPA shell via direct curl; web.archive.org refused "
            "by WebFetch and 403 via direct proxy curl, neither bypassed). ORIGINAL full "
            "text is from an OFFICIAL government PDF published directly by the Ministry "
            "of Tourism (cdn.mt.gov.sa, Saudi-Tourism-Regulation-Ar-V014.pdf), cross-"
            "checked verbatim against nezams.com, and structurally cross-checked (English, "
            "reference-only) against the official BOE translation (via misa.gov.sa) -> "
            "TIER_2. 19 articles, flat (no chapters), all اصلية. Article 18 REPEALS the "
            "prior Tourism Law (Royal Decree M/2, 9/1/1436H) by name -- a genuine "
            "named-predecessor repeal, independently confirmed on the predecessor's own "
            "nezams.com status record. No known amendments to this law as of this pass. "
            "See verification_methodology_note and known_unresolved_discrepancies in the "
            "source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/18 (26/1/1444H), CoM Resolution 79 (25/1/1444H), published "
            "Umm al-Qura 7/2/1444H. Original full text from an official Ministry of "
            "Tourism PDF (cdn.mt.gov.sa) cross-checked against nezams.com; structurally "
            "cross-checked (English, reference-only) against the official BOE translation "
            "(misa.gov.sa). laws.boe.gov.sa dedicated lawId page "
            "(7d777c66-d28b-43de-9305-af23013b1738) and the Umm al-Qura gazette page were "
            "unreachable this pass (live 503 / un-rendered SPA; Wayback refused/403, not "
            "bypassed) -> TIER_2. Repeals the prior Tourism Law (Royal Decree M/2, "
            "9/1/1436H) by name (Article 18) -- confirmed on both sides.")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/18 وتاريخ 26/1/1444هـ، وقرار مجلس الوزراء رقم 79 وتاريخ "
               "25/1/1444هـ (منشور بأم القرى 7/2/1444هـ). النص الأصلي الكامل من PDF رسمي بموقع "
               "وزارة السياحة (cdn.mt.gov.sa) متقاطع مع nezams.com، ومتقاطع بنيويا (إنجليزي، "
               "مرجعي فقط) مع الترجمة الرسمية لهيئة الخبراء (misa.gov.sa). الصفحة المخصصة على "
               "laws.boe.gov.sa (lawId 7d777c66-d28b-43de-9305-af23013b1738) وصفحة الجريدة "
               "الرسمية أم القرى تعذر الوصول إليهما حيا هذه الجولة (503/واجهة غير مصيرة؛ Wayback "
               "مرفوض/403، لم يُتجاوَز) -- TIER_2. يلغي نظام السياحة السابق (م/2، 1436هـ) بالاسم "
               "(المادة 18) -- مؤكد من الاتجاهين.")


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
        ver.append({"law_key": "tourism", "law_component": "law",
                    "language": "ar",
                    "record_layer": "TOURISM_LAW_ARABIC_VERIFIED_TEXT",
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
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "tourism-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "tourism/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام السياحة" % a["number_label_ar"]],
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
    json.dump({"law_key": "tourism",
               "layer": "TOURISM_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-tourism-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة؛ كلها أصلية)",
               "title_en": ("Tourism Law — Arabic LLM-ready layer "
                            "(19 records: all original, no amendments)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Tourism Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
