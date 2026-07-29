#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Excise Tax Implementing Regulation track
(اللائحة التنفيذية للضريبة الانتقائية, Board of Directors Resolution No.
(9-1-17), 13 Ramadan 1438H, issued under the Excise Tax Law, Royal Decree M/86,
27/8/1438H, and the GCC Unified Excise Tax Agreement).

Companion track to this corpus's excise_tax_law track (added in the same pass).

VERIFICATION TIER -- TIER_2 (one official source + an independent secondary
cross-check covering 58 of the 67 records). See
excise_tax_regulation_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY SOURCE: ZATCA's own official consolidated Arabic PDF of the Excise Tax
Implementing Regulation, downloaded directly from zatca.gov.sa this pass
(HTTP 200, 52 pages, born-digital Adobe Illustrator file, internal CreationDate
2 April 2026, ModDate 17 June 2026). Its cover prints the complete chain of six
resolutions and it carries numbered footnotes attributing individual amendments
to individual articles and paragraphs.

DECISION-NUMBER DIRECTION (resolved with official evidence, not assumed): this
PDF draws hyphenated resolution numbers with their groups reversed
("17-1-9" for 9-1-17, "25-06-06" for 06-06-25). The correct direction was
established from ZATCA's OWN regulation page, whose HTML prose reads
"... (06-06-25) وتاريخ 2025/12/28م" -- the reverse of what the PDF draws. The
page's direction is adopted; the raw drawn form is recorded in
known_unresolved_discrepancies.

SECONDARY CROSS-CHECK: nezams.com's independent rendering of the Regulation as
it stood in 1440H (58 articles). The numbering is offset -- nezams 1-8 map to
current 1-8, nezams 9-58 map to current 15-64 -- because the Tax Stamps chapter
(current Articles 9-14) was inserted later. 15 articles matched EXACTLY
letter-for-letter; 28 more exceed 0.90 similarity with differences that are
orthographic or the renumbering of internal cross-references; the remainder are
substantive and correspond to amendments the official file's own footnotes
document. ZATCA's text governs everywhere; the secondary source was never used
to correct a single Arabic character.

REAL RECORD COUNT: 67, not 64. The highest article number is indeed
(الرابعة والستون) = 64 -- which is the figure this corpus's census recorded --
but the Regulation additionally contains THREE مكرر articles (22 مكرر,
37 مكرر, 52 مكرر). The real count 67 is used and the divergence from the census
is recorded explicitly. 48 اصلية / 16 معدلة / 3 مضافة, 23 chapters.

AMENDMENTS: the two most recent amending resolutions -- (13-1-23), 15 Rajab
1444H, and (06-06-25), 8 Rajab 1447H / 28 December 2025 -- ARE attributed
article-by-article by the official file's own footnotes and are consolidated
here with those footnotes preserved verbatim in each article's history. The
three earlier resolutions printed on the same cover -- (8-2-19), (2-3-19) and
(14-6-22) -- are consolidated into the running text WITHOUT any per-article
footnote, so which articles they changed cannot be determined from this source;
that is flagged, not guessed.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "excise_tax_regulation", "law", "official_source",
                   "excise_tax_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "excise_tax_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "excise_tax_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "excise_tax_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "excise_tax_regulation_arabic_legal_llm",
                        "excise_tax_regulation_legal_llm_001_067.json")

LAW_ID = "sa-excise-tax-regulation-9-1-17-1438"
LAW_AR = "اللائحة التنفيذية للضريبة الانتقائية"
STATUS = "ZATCA_OFFICIAL_CONSOLIDATED_PDF_X_SECONDARY_CROSS_VERIFIED"
KEY_RE = r"excise_tax_regulation_art_(\d{3})(_mukarrar)?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها إليه "
            "عليها الهيئة الضريبة الضريبية للضريبة تلك ذلك هذه التالية").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text.replace("ـ", "")).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    return (int(m.group(1)), 1 if m.group(2) else 0)


GOV_NOTE = ("Arabic governs. PRIMARY source: ZATCA's own official consolidated "
            "Arabic PDF of the Excise Tax Implementing Regulation (zatca.gov.sa, "
            "HTTP 200, 52 pages, born-digital), whose cover prints all six "
            "resolutions and whose numbered footnotes attribute the (13-1-23) and "
            "(06-06-25) amendments article by article. CROSS-CHECK: nezams.com's "
            "independent 1440H rendering (58 articles, offset numbering) -- 15 "
            "articles matched letter-for-letter, all divergences documented, "
            "ZATCA's wording governing everywhere. The nine records with no "
            "secondary counterpart (Articles 9-14 and the three مكرر articles) "
            "rest on the official file alone and govern this track's TIER_2 "
            "rating. laws.boe.gov.sa, the Wayback Machine and r.jina.ai were all "
            "unreachable/blocked this pass. The three pre-2023 amending "
            "resolutions are consolidated without per-article attribution -- see "
            "known_unresolved_discrepancies. The English ZATCA version was never "
            "used.")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for i, key in enumerate(keys, 1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        mk = bool(m.group(2))
        ls = a.get("legal_status_ar")
        text = a["text"]
        title = a.get("title_ar", "")
        label = a["number_label_ar"] + ((": " + title) if title else "")
        ver.append({"law_key": "excise_tax_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "EXCISE_TAX_REGULATION_ARABIC_VERIFIED_TEXT",
                    "record_index": i,
                    "article_number": n, "is_mukarrar": mk, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "verification_tier": src["verification_tier"],
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": mk, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "excise-tax-regulation-llm-art-%03d%s"
                                 % (n, "-mukarrar" if mk else ""),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "excise_tax_regulation/law/articles/%03d%s"
                                    % (n, "m" if mk else ""),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنفيذية للضريبة الانتقائية"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("ZATCA Board of Directors "
                                                          "Resolution No. (9-1-17), "
                                                          "13 Ramadan 1438H, under the Excise "
                                                          "Tax Law (Royal Decree M/86) — "
                                                          "ZATCA official consolidated PDF, "
                                                          "cross-verified against an "
                                                          "independent secondary source "
                                                          "(TIER_2)"),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة العامة "
                                                             "للزكاة والدخل رقم (9-1-17) "
                                                             "وتاريخ 13 رمضان 1438هـ، الصادر "
                                                             "استنادًا إلى نظام الضريبة "
                                                             "الانتقائية (م/86) — النسخة "
                                                             "الرسمية الموحّدة لهيئة الزكاة "
                                                             "والضريبة والجمارك، مع تحقّق "
                                                             "متقاطع من مصدر ثانوي مستقل"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "verification_tier": src["verification_tier"],
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "excise_tax_regulation",
               "layer": "EXCISE_TAX_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "verification_tier": src["verification_tier"],
               "verification_tier_basis": src["verification_tier_basis"],
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_hijri_as_printed": src["decree_date_hijri_as_printed"],
               "highest_article_number": src["highest_article_number"],
               "mukarrar_count": src["mukarrar_count"],
               "consolidated_amended_law": True,
               "parent_law": src["parent_law"],
               "cover_page_verbatim_ar": src["cover_page_verbatim_ar"],
               "amendment_history": src["amendment_history"],
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-excise-tax-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": (LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية "
                            "(67 سجلًّا: 64 مادة مرقَّمة + 3 مواد مكرر؛ نص موحّد: "
                            "48 أصلية، 16 معدّلة، 3 مضافة)"),
               "title_en": ("Implementing Regulation of the Saudi Excise Tax — Arabic "
                            "LLM-ready layer (67 records: 64 numbered articles + 3 مكرر, "
                            "consolidated)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 64], "mukarrar_count": src["mukarrar_count"],
               "text_status": STATUS,
               "verification_tier": src["verification_tier"],
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Excise Tax Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
