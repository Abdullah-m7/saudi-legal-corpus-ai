#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the E-Invoicing Regulation track (لائحة الفوترة الإلكترونية), ZATCA
Board of Directors Decision No. (2-6-20), dated 4 Rabi' al-Thani 1442H.

This track is the CONFIRMATION pass for a prior research lead that was
explicitly flagged MEDIUM confidence, corroborated only across secondary
qanoonsa.com-style listings, and NOT yet cross-checked against a primary
source. This pass performed that check and confirms the citation.

PRIMARY SOURCE: fetched directly (HTTP 200, via curl) from ZATCA's own site,
both language versions:
  - https://zatca.gov.sa/ar/E-Invoicing/Introduction/LawsAndRegulations/
    Documents/E-invoicing-Regulations.pdf (Arabic, governing, 6 pages)
  - https://zatca.gov.sa/en/E-Invoicing/Introduction/LawsAndRegulations/
    Documents/E-invoicing-Regulations.pdf (English official translation, 7
    pages; the file's own disclaimer states Arabic governs)
Both give an identical 7-article structure: Article 1 (Definitions), 2
(Purpose and scope), 3 (Persons subject to the Regulation), 4 (Provisions
related to Electronic Invoices/Notes), 5 (Technical specifications and
procedural rules), 6 (General provisions), 7 (Enforcement and obligation).

laws.boe.gov.sa: live fetch returned HTTP 503; repeated site:laws.boe.gov.sa
web search found NO dedicated lawId page for this decision at all (only
unrelated results for the separate Electronic Transactions Law) -- consistent
with this corpus's established pattern for Board/Governor-level decisions
(food_regulation, vat_regulation, anti_smoking_regulation).

CROSS-CHECK (independent secondary source): an identical-content PDF hosted
on aflaksolutions.com (a private tax-consulting site, cover-dated "November
2020") was fetched (HTTP 200) and diffed article-by-article against the
ZATCA file -- verbatim match throughout (formatting/line-wrap differences
only). Decision number/date additionally corroborated across qanoonsa.com,
lexismiddleeast.com, afiflaw.com, and general web search results. A
qanoniah.com page with a matching exact title exists but is a JS-rendered
Nuxt SPA whose body could not be extracted (confirms existence, not used as
a text source).

VERIFICATION TIER: TIER_2 -- one official primary source reached and adopted
(zatca.gov.sa) with no independent second GOVERNMENT source available (BOE
has no page; the Umm al-Qura Gazette site, uqn.gov.sa, is a Vue.js SPA whose
article content could not be fetched this pass), cross-verified against an
independent private secondary source with word-for-word agreement.

7 articles, ALL اصلية (0 معدلة, 0 مضافة, 0 ملغاة). Confirmed this pass: the
~24 subsequent "phase" decisions (رقم متسلسل, "تطبيق المرحلة ن لربط أنظمة
الفوترة الإلكترونية") and the separate, broader Governor Controls Resolution
("الضوابط والمتطلبات...") are ALL issued under the express delegation in this
Regulation's own Article 6(B) -- rollout schedules and technical/procedural
detail, not textual amendments to any of these 7 articles. No repeal of any
predecessor instrument is stated anywhere in the text (expected: e-invoicing
is a new requirement layered onto -- not replacing -- Article 53 of the VAT
Implementing Regulation; see Article 2(B): "an integral part of the VAT
Implementing Regulation and is complementary to it").

A Gregorian-date discrepancy is disclosed, not silently resolved to false
certainty: ZATCA's own English PDF cover prints "December 4th 2020", while
independently converting 4 Rabi' al-Thani 1442H (via the hijridate library)
gives 19 November 2020 -- matching the independent aflaksolutions.com
mirror's cover ("November 2020"). The most likely explanation (internally
consistent with Article 7(B)'s 12-month countdown producing the universally
-cited 4 December 2021 Phase-1 deadline) is that 4 December 2020 is the
Official Gazette PUBLICATION date, distinct from the ~19 November 2020 Board
decision date -- but this is not pinned to a primary Umm al-Qura Gazette
record this pass (uqn.gov.sa is a Vue.js SPA; direct fetch returned only
unrendered template markup). Five minor spelling inconsistencies (a missing
hamza on the same five words, in the same five spots, in BOTH independently
-fetched files) are preserved verbatim, not "corrected", per this corpus's
no-silent-edit rule -- see known_unresolved_discrepancies in the source
artifact.

Diacritics (tashkeel) stripped uniformly for consistency with this corpus's
other tracks. A systematic embedded-font ligature-reversal defect (shared
identically by both the ZATCA and aflaksolutions.com files, confirming it is
a shared-source PDF/font defect rather than a tool-specific extraction bug)
was fixed via a small, explicit, individually-verified substitution list
during hand-transcription of the official_source.json input -- not a blind
global regex. Arabic governs; no translation/paraphrase/interpretation
performed on the Arabic text. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "einvoicing_regulation", "law", "official_source",
                   "einvoicing_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "einvoicing_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "einvoicing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "einvoicing_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "einvoicing_regulation_arabic_legal_llm",
                        "einvoicing_regulation_legal_llm_001_007.json")

LAW_ID = "sa-einvoicing-regulation-2-6-20-1442h"
LAW_AR = "لائحة الفوترة الإلكترونية"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"einvoicing_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة المحافظ").split())


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


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa is unreachable this pass (HTTP 503) and has NO "
            "dedicated lawId page for this ZATCA Board decision at all (repeated targeted web "
            "search found none). PRIMARY source: zatca.gov.sa's own official PDF (Arabic + "
            "English translation, both fetched directly, HTTP 200) -- 7 articles, ALL اصلية. "
            "CROSS-CHECKED word-for-word against an independent mirror on aflaksolutions.com "
            "(verbatim match) and against decision-number/date corroboration across multiple "
            "other secondary sources (qanoonsa.com, lexismiddleeast.com, afiflaw.com) -> "
            "TIER_2. Confirmed: the ~24 subsequent 'phase' decisions and the separate Governor "
            "Controls Resolution are rollout-schedule/technical-detail instruments issued under "
            "this Regulation's own Article 6(B) delegation, NOT textual amendments to these 7 "
            "articles. No repeal of any predecessor instrument. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact (including a disclosed, not-fully-pinned Gregorian publication-date "
            "question, and five cross-verified minor spelling inconsistencies preserved "
            "verbatim) before relying on this track's text or provenance.")

SRC_AUTH = ("E-Invoicing Regulation, issued by ZATCA (at the time, GAZT) Board of Directors "
            "Decision No. (2-6-20), dated 4 Rabi' al-Thani 1442H. Full text from ZATCA's own "
            "official site (zatca.gov.sa), cross-checked word-for-word against an independent "
            "mirror (aflaksolutions.com) -> TIER_2. 7 articles, all اصلية -- no amendments "
            "confirmed to the founding text; ~24 subsequent phase decisions are rollout "
            "schedules issued under this Regulation's own Article 6(B), not textual amendments.")

SRC_AUTH_AR = ("لائحة الفوترة الإلكترونية، الصادرة بقرار مجلس إدارة هيئة الزكاة والضريبة "
               "والجمارك (وقتها الهيئة العامة للزكاة والدخل) رقم (2-6-20) وتاريخ 4 ربيع "
               "الثاني 1442هـ. النص الكامل من الموقع الرسمي لهيئة الزكاة والضريبة والجمارك "
               "(zatca.gov.sa)، مطابق حرفيا لمصدر ثانٍ مستقل (aflaksolutions.com) -- "
               "TIER_2. 7 مواد، جميعها أصلية -- لا تعديلات مؤكدة على النص التأسيسي؛ قرارات "
               "المراحل اللاحقة (قرابة 24 قرارا) جداول تطبيق صادرة بموجب تفويض المادة "
               "السادسة (ب) من هذه اللائحة نفسها، وليست تعديلات نصية.")


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
        ver.append({"law_key": "einvoicing_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "EINVOICING_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": a.get("verification_tier"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "einvoicing-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "einvoicing_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من لائحة الفوترة الإلكترونية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"], "verification_tier": a.get("verification_tier"),
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
    json.dump({"law_key": "einvoicing_regulation",
               "layer": "EINVOICING_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-einvoicing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (7 مواد؛ 7 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("E-Invoicing Regulation — Arabic LLM-ready layer (7 records: 7 "
                            "original, 0 amended, 0 added, 0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 7], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready E-Invoicing Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
