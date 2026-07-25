#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian BANKING CONTROL LAW IMPLEMENTATION RULES track
(قواعد تطبيق أحكام نظام مراقبة البنوك) -- Ministerial Resolution No. 2149/3,
dated 14/10/1406H (21/6/1986G), issued by the Minister of Finance and National
Economy (Mohammed Aba Al-Khail) under Article 26 of the Banking Control Law
(Royal Decree M/5, 22/2/1386H), and circulated to all banks operating in the
Kingdom under cover of a circular signed by the then SAMA Governor (Hamad
Al-Sayari).

STRUCTURE NOTE -- this is a SINGLE instrument (one Ministerial Resolution, one
circular), NOT a modern "لائحة تنفيذية" and NOT a multi-instrument combination
like the electricity_regulation track. It is organized into FIVE SECTIONS
(أولاً..خامساً), each implementing a specific article of the Banking Control
Law:
  Section I   (أولاً)   -> Article 16 (lending limits / monetary matters) -- 10 provisions
  Section II  (ثانياً)  -> Article 12 (board-member/director appointments) -- 4 provisions
  Section III (ثالثاً)  -> Article 17 (periodic data submission to SAMA)   -- 2 provisions
  Section IV  (رابعاً)  -> Article 18 (inspection procedures)              -- 4 provisions
  Section V   (خامساً)  -> Article 22 (enforcement measures)               -- 11 provisions
Total: 31 provisions. Each provision record carries `section_key` ("I".."V"),
`section_item_number` (local 1-based position within its section), and
`native_marker_ar` (the literal marker printed in the source: plain digits for
Sections I/II/III/V, parenthesized digits "(1)".."(4)" for Section IV -- the
only section whose intro sentence has no separate dash-numbered wrapper level)
-- mirroring the `instrument_part`/`part_article_number`/`part_number_label_ar`
pattern used by the electricity_regulation track, adapted for a single
instrument with five internally-numbered sections rather than two independent
issuing instruments.

PROVISION-COUNT METHODOLOGY -- one explicit, uniformly-applied rule across all
five sections: count the FIRST enumeration level that appears immediately
after each section's introductory colon as one provision each; any deeper
nesting (lettered sub-clauses (أ)-(ط)/(أ)-(هـ) in Section I, parenthetical
sub-items (1)-(7) in Section II/III) stays embedded in its parent provision's
`text`, unsplit -- consistent with how this corpus's other tracks (e.g.
electricity_regulation's Article 1 definitions list) keep nested enumerations
inside one article's text rather than fragmenting further. This yields 31
(10+4+2+4+11), which differs from a WebFetch-generated English-language
summary of the same page's tally (8/3/7/4/11) -- that summary counted
different nesting levels inconsistently across sections (see the source
artifact's `known_unresolved_discrepancies` entry
`banking_control_regulation_item_numbering_intrinsic_continuations` for the
full reconciliation).

VERIFICATION TIER -- TIER_2. Two primary sources were fetched directly this
pass, both HTTP 200 via direct curl through this environment's configured
proxy (contrary to an earlier report of a connection reset hitting
www.sama.gov.sa directly -- the reachable official domain for this instrument
is rulebook.sama.gov.sa, SAMA's own Rulebook subdomain, not the main
www.sama.gov.sa site, which itself returned an internal error page via
WebFetch this pass): (1) the live Arabic Rulebook page
(rulebook.sama.gov.sa/ar/قواعد-تطبيق-أحكام-نظام-مراقبة-البنوك-0, marked
"نافذ"/in-force on the page itself), and (2) its own linked archival PDF
(SAMA_AR_1429_VER1.pdf -- a born-digital text PDF, not a scan, decoded via
pdfplumber). Both agree verbatim on all 31 provisions' substance, order, and
section grouping, with exactly two disclosed variances (regulator-name
terminology, and one item's numeral) -- see
`known_unresolved_discrepancies` in the source artifact for the full,
undeleted account, including an unresolved question about an unexplained
single revision-history boundary dated 08 Nov 2017 that this pass could not
access (login-gated) to confirm or rule out as substantive.

31 provisions total; all 31 اصلية (no confirmed substantive amendment this
pass); 0 معدلة, 0 ملغاة, 0 مضافة. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "banking_control_regulation", "law", "official_source",
                   "banking_control_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "banking_control_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "banking_control_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "banking_control_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "banking_control_regulation_arabic_legal_llm",
                        "banking_control_regulation_legal_llm_001_031.json")

LAW_ID = "sa-banking-control-regulation-implementation-rules-2149-3-1406"
DOC_AR = "قواعد تطبيق أحكام نظام مراقبة البنوك"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"banking_control_regulation_art_(\d{3})$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم البنك البنوك المركزي البند القسم أولاً ثانياً ثالثاً رابعاً خامساً").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [DOC_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    return int(m.group(1))


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


GOVERNING_NOTE = (
    "Arabic governs; this record is ONE of the 31 provisions of the Banking Control Law "
    "Implementation Rules (Ministerial Resolution No. 2149/3, 14/10/1406H) -- see this "
    "record's section_key field for which of the five sections (I=Art.16, II=Art.12, "
    "III=Art.17, IV=Art.18, V=Art.22) it belongs to. Fetched directly this pass from "
    "rulebook.sama.gov.sa (SAMA's own Rulebook subdomain, live page marked نافذ/in-force) "
    "and cross-checked against its own linked archival PDF (SAMA_AR_1429_VER1.pdf, decoded "
    "via pdfplumber) -- both agree verbatim except two disclosed variances (a regulator-name "
    "terminology update, and one item's numeral). TIER_2. See verification_methodology_note, "
    "verbatim_normalization_note, and known_unresolved_discrepancies in the source artifact "
    "before relying on this track -- in particular the disclosed, unresolved question about "
    "an unexplained Nov-2017 revision-history boundary that could not be accessed this pass."
)

SOURCE_AUTHORITY_AR = (
    "قواعد تطبيق أحكام نظام مراقبة البنوك -- القرار الوزاري رقم 2149/3 وتاريخ 14/10/1406هـ، الصادر عن "
    "وزير المالية والاقتصاد الوطني استنادا إلى المادة 26 من نظام مراقبة البنوك (م/5، 22/2/1386هـ)، ومُعمَّم "
    "على جميع البنوك بتعميم من محافظ مؤسسة النقد العربي السعودي. النص الحرفي من الصفحة الحية لكتيّب قواعد "
    "البنك المركزي السعودي (rulebook.sama.gov.sa)، مع تحقق مقابل من ملف PDF الأرشيفي المرتبط منها مباشرة. "
    "المستوى TIER_2."
)

SOURCE_AUTHORITY_EN = (
    "Banking Control Law Implementation Rules -- Ministerial Resolution No. 2149/3, dated "
    "14/10/1406H, issued by the Minister of Finance and National Economy under Article 26 of "
    "the Banking Control Law (M/5, 22/2/1386H), circulated to all banks under cover of a "
    "circular from the then SAMA Governor. Verbatim text from the live SAMA Rulebook page "
    "(rulebook.sama.gov.sa), cross-checked against its own linked archival PDF. TIER_2."
)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    sections_by_key = {s["section_key"]: s for s in src["sections"]}

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = _sort_key(key)
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        section_key = a["section_key"]
        ver.append({"law_key": "banking_control_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "BANKING_CONTROL_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "section_key": section_key,
                    "section_item_number": a["section_item_number"],
                    "native_marker_ar": a["native_marker_ar"],
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": GOVERNING_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        sec = sections_by_key[section_key]
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "section_key": section_key,
                    "section_item_number": a["section_item_number"],
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "banking-control-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s (%s) — %s" % (DOC_AR, sec["ordinal_ar"], a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (sec["ordinal_ar"], a["number_label_ar"]),
                    "article_path": "banking_control_regulation/law/%s/articles/%s" % (section_key, key),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": [
                        "%s من قواعد تطبيق أحكام نظام مراقبة البنوك" % a["number_label_ar"],
                        "%s البند %s" % (sec["ordinal_ar"], a["native_marker_ar"]),
                        "تطبيقا لأحكام %s من نظام مراقبة البنوك" % sec["base_law_article_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SOURCE_AUTHORITY_EN,
                                     "source_authority_ar": SOURCE_AUTHORITY_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": DOC_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "banking_control_regulation",
               "layer": "BANKING_CONTROL_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "legal_status_ar": src.get("legal_status_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "instrument_type_ar": src.get("instrument_type_ar"),
               "instrument_type_note_ar": src.get("instrument_type_note_ar"),
               "sections": src["sections"],
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "verbatim_normalization_note": src.get("verbatim_normalization_note"),
               "regulator_rename_footnote_ar": src.get("regulator_rename_footnote_ar"),
               "pdf_archival_text_variant_note_ar": src.get("pdf_archival_text_variant_note_ar"),
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-banking-control-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": (DOC_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (31 بندا موزعة على 5 "
                            "أقسام؛ 31 اصلية، 0 معدلة، 0 مضافة، 0 ملغاة)"),
               "title_en": ("Banking Control Law Implementation Rules — Arabic LLM-ready layer "
                            "(31 records across 5 sections: 31 original, 0 amended, 0 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 31], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Banking Control Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
