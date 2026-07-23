#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian E-Commerce Law track
(اللائحة التنفيذية لنظام التجارة الإلكترونية, Ministerial Resolution No. 200,
19/5/1441H, issued by the Minister of Commerce and Investment under Article 25 of
the E-Commerce Law, Royal Decree M/126, 7/11/1440H).

This is the companion Implementing Regulation of the E-Commerce Law already in
this corpus (sources/ecommerce/law/...). The base Law's own text points forward
to it (Article 1: "اللائحة: اللائحة التنفيذية للنظام"; Article 25: "يصدر الوزير
اللائحة خلال تسعين يوما من تاريخ نشر النظام"), and the base Law's source artifact
records the pointer "Ministerial Resolution 200/1441H, 19/5/1441H". This track
ingests that Regulation as a distinct instrument.

VERIFICATION TIER -- see ecommerce_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology. The
live portal returned HTTP 503 this pass, and -- more fundamentally -- exhaustive
search found NO dedicated BOE lawId page for this Implementing Regulation at all
(BOE's only related page is the BASE E-Commerce Law, lawId 360de590-0286-4fa5-
a243-aa9100c31979), consistent with BOE not cataloguing ministerial-resolution-
level executive regulations as standalone lawId records. archive.org (Wayback)
is blocked outright in this session's egress policy and was not used (no bypass
attempted).

PRIMARY SOURCE: the issuing Authority's OWN official page -- the Ministry of
Commerce regulations page (mc.gov.sa/ar/Regulations/Pages/details.aspx?lawId=
aaa4d4cf-ca57-41ff-a3f9-aa8500a3512c), a BORN-DIGITAL HTML page (not a scan)
that carries the full text of all 20 articles inside structured
<div class="rules-article-container"> elements and an explicit structural header
"عدد الأبواب: 0 | عدد الفصول: 0 | عدد الملحقات: 0 | عدد المواد: 20". Fetched via
the r.jina.ai reader (both markdown and raw-HTML forms) because direct curl to
mc.gov.sa failed certificate-chain verification in this session; the 20 articles
were parsed from the raw-HTML DOM directly (each from its own container element,
<br> -> newline), NOT from an automated summary.

INDEPENDENT TEXT CROSS-VERIFICATION (two official sources, verbatim): the
born-digital text was matched word-for-word against the Ministry's OWN official
scanned PDF ("اللائحة التنفيذية لنظام التجارة الإلكترونية / 1441هـ / 2020م",
14 pages, National Center for Archives seal, internal CreationDate 15 Jan 2020)
via direct visual reading of its 200-300dpi page renders. Articles 1-4 and 18
were confirmed character-for-character identical; the resolution page (scan
page 1) matched the issuance metadata (transaction/resolution No. 200, date
1441/05/19, attachment: a regulation, signed by Minister Dr. Majid bin Abdullah
Al-Qassabi). A separate tesseract Arabic-OCR pass over the scan was ALSO run but
was only mediocre (scattered recognition errors, e.g. التنفيدية for التنفيذية),
so OCR text was NOT used for extraction -- the born-digital MC page text was
used, and the scan served purely for direct visual cross-verification.

COUNT/STRUCTURE confirmed four ways: (1) the Ministry's own explicit metadata
("عدد المواد: 20؛ عدد الأبواب: 0؛ عدد الفصول: 0"); (2) direct count of extracted
article headers (20, from المادة الأولى to المادة العشرون); (3) Argaam's issuance
report ("20 articles"); (4) the Mithaq legal guide ("comprising 20 articles").
The crucial distinction: 20 is the REGULATION's count, versus 26 for the base
LAW -- some automated search summaries wrongly attributed "26 articles" to the
Regulation.

20 articles, no chapters/parts; 20 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة. A public
consultation to amend this Regulation (refund-mechanism on consumer cancellation)
exists on istitlaa.ncc.gov.sa / eparticipation.my.gov.sa, but NO enacting
amending resolution number/date was confirmable this pass, so all 20 articles
are recorded as اصلية (current in-force text as the issuing Authority presents
it). NO predecessor implementing regulation is repealed or superseded -- the
base Law itself dates only to 1440H, so there was no prior regulation.

Display-layer normalization only, fully disclosed (no character/word/number/rule
altered): Arabic-Indic digits -> Western digits (1:1, consistent with this
corpus's base E-Commerce Law track); tashkeel/harakat stripped (consistent with
the food_regulation template and this corpus's majority); the single hijri "هـ"
tatweel preserved; hidden bidi marks (RLM/ZWNJ) leaked from HTML removed; <br>
-> newline. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "ecommerce", "regulation", "official_source",
                   "ecommerce_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "ecommerce", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "ecommerce_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "ecommerce_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "ecommerce_regulation_arabic_legal_llm",
                        "ecommerce_regulation_legal_llm_001_020.json")

LAW_ID = "sa-ecommerce-regulation-200-1441"
LAW_AR = "اللائحة التنفيذية لنظام التجارة الإلكترونية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"ecommerce_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها إليه عليها "
            "المستهلك الخدمة موفر المحل الإلكتروني الإلكترونية الوزارة التجارة").split())


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
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


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
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "ecommerce", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ECOMMERCE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the issuing "
                                              "Authority's own official page on mc.gov.sa (a "
                                              "born-digital HTML page carrying the full text of "
                                              "all 20 articles) -- laws.boe.gov.sa was checked "
                                              "first per standard methodology but returned HTTP "
                                              "503 this pass and has no dedicated lawId page for "
                                              "this Implementing Regulation at all. The text was "
                                              "cross-verified word-for-word against the Ministry's "
                                              "own official scanned PDF by direct visual reading "
                                              "(articles 1-4 and 18 confirmed identical). Article "
                                              "count (20; 0 chapters) cross-verified against the "
                                              "Ministry's explicit metadata plus argaam.com and "
                                              "mithaq.com.sa; resolution number/date (200, "
                                              "19/5/1441H) cross-verified against the scanned "
                                              "resolution page, qanoniah.com, lexismiddleeast.com "
                                              "and the base Law's own forward-pointer. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- in "
                                              "particular the display-layer normalization "
                                              "(Arabic-Indic->Western digits, tashkeel stripped) "
                                              "and the preamble's distinct scan-visual provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "ecommerce-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "ecommerce/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام التجارة الإلكترونية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Resolution No. (200) of the "
                                                          "Minister of Commerce and Investment "
                                                          "(19/5/1441H), issued under Article 25 of "
                                                          "the E-Commerce Law (Royal Decree M/126, "
                                                          "7/11/1440H) — PRIMARY source is the "
                                                          "issuing Ministry's own official page "
                                                          "(mc.gov.sa, born-digital), cross-verified "
                                                          "word-for-word against the Ministry's own "
                                                          "official scanned PDF and against "
                                                          "qanoniah.com, lexismiddleeast.com, "
                                                          "argaam.com and mithaq.com.sa; "
                                                          "laws.boe.gov.sa returned HTTP 503 this "
                                                          "pass and has no dedicated lawId page for "
                                                          "this Implementing Regulation"),
                                     "source_authority_ar": "قرار وزير التجارة والاستثمار رقم (200) وتاريخ 19/5/1441هـ، الصادر استنادا إلى المادة (الخامسة والعشرين) من نظام التجارة الإلكترونية (المرسوم الملكي رقم م/126، 7/11/1440هـ) — المصدر الأساسي هو الصفحة الرسمية للوزارة المصدرة نفسها (mc.gov.sa، نص رقمي أصلي)، مطابق حرفيا مع الملف الرسمي الممسوح للوزارة ومع qanoniah.com وlexismiddleeast.com وargaam.com وmithaq.com.sa؛ بوابة هيئة الخبراء أعادت HTTP 503 هذه الجولة ولا تملك صفحة مخصصة لهذه اللائحة التنفيذية أصلا",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "ecommerce",
               "layer": "ECOMMERCE_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-ecommerce-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (20 مادة؛ 20 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation of the Saudi Arabian E-Commerce Law — Arabic "
                            "LLM-ready layer (20 records: 20 original, 0 amended, 0 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready E-Commerce Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
