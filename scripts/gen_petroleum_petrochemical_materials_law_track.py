#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Petroleum and Petrochemical Materials Law track (نظام المواد
البترولية والبتروكيماوية, Royal Decree M/139, 12/7/1446H -- the currently
in-force law regulating petroleum and petrochemical operations, licensing, and
penalties, administered by the Ministry of Energy).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام المواد البترولية والبتروكيماوية is
a single, self-standing Royal-Decree law (M/139, 12/7/1446H, on CoM Resolution
473, 7/7/1446H; Shura Council Resolution 80/8, 2/5/1446H), published in the
Umm Al-Qura Gazette, issue 5066, 24 January 2025, entering into force 90 days
after publication. Confirmed via cross-checked independent sources:
(1) laws.boe.gov.sa carries it under its own dedicated lawId
48da5c0f-b5a6-4e93-b76c-b33200be0330 (seen via WebSearch), with the
PREDECESSOR law's lawId (e102ee5b-3046-41c5-9515-a9ea000206eb, نظام التجارة
بالمنتجات البترولية) also independently located. The LIVE portal itself
returned "Connection reset by peer" on direct curl this pass, but a SINGLE
web.archive.org snapshot (captured 2026-01-17) was reached directly via HTTPS
curl (HTTP 200, 95541 bytes) and reproduces the actual BOE page content
(confirmed via the LawId value embedded in the page's own "report an issue"
form), including the full Royal Decree preamble, the full CoM Resolution 473
text, and all 22 articles. (2) qanoonsa.com (three linked pages, all fetched
live via direct curl, HTTP 200) independently reproduces the same preamble,
CoM Resolution, and all 22 articles -- word-for-word matching the BOE snapshot
except 4 disclosed immaterial variances (two comma-placement differences in
Articles 12 and 14; one hamza-spelling variant in Article 17, "المشار اليه"
in BOE vs. "المشار إليه" elsewhere including BOE's own Articles 14/15/16,
likely a BOE-side typo; one percent-sign glyph difference in Article 19,
qanoonsa's Arabic "٪" vs. BOE's raw HTML showing a stray mixed-script "(2٠%)").
(3) nezams.com independently confirms the PREDECESSOR law's identity and its
repeal ("غير ساري: ألغي... بصدور النظام الجديد الصادر بموجب المرسوم الملكي رقم
(م/139) وتاريخ 12/7/1446هـ"). (4) argaam.com (an independent Saudi financial
news secondary source) substantively corroborates the Gazette issue number
(5066), the 22-article count, Article 5's licensing requirement, Article 15's
export-penalty tiers, and Article 21's repeal clause.

STORAGE-TEXT CHOICE -- qanoonsa.com's extraction was used as the stored
`text` field (not BOE's), because qanoonsa's HTML embeds explicit digit-dash
enumeration ("1-", "2-", "أ-", "ب-") for sub-clauses within articles, matching
this corpus's storage convention (see real_estate_contributions_law), whereas
BOE's HTML renders the same sub-clauses as an <ol><li> list with no literal
digit in the extractable text layer (the numbering is CSS-rendered only). The
underlying legal content is identical between the two sources; only this
formatting/rendering choice differs.

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT: Article 21 (المادة
الحادية والعشرون) states verbatim: "يحل النظام محل نظام التجارة بالمنتجات
البترولية، الصادر بالمرسوم الملكي رقم (م / 18) وتاريخ 28 / 1 / 1439هـ، ويلغي
ما يتعارض معه من أحكام." This exact wording is identical between the BOE
snapshot and qanoonsa.com, and the repealed predecessor's identity/date is
independently corroborated by nezams.com and argaam.com. The enacting Royal
Decree's own clause (Second) -- repeated in CoM Resolution 473's clause
(Second) -- additionally carves out a TRANSITIONAL EXCEPTION: licenses issued
under the repealed M/18 law remain valid, with licensees required to correct
their status within 2 years (submitting a correction plan within 1 year),
extendable by the Minister of Energy up to 6 additional years. This exception
lives in the preamble/CoM-resolution text, outside the 22 numbered Articles.

VERIFICATION TIER -- TIER_2. Exactly ONE official/primary source
(laws.boe.gov.sa) was reached this pass -- via a SINGLE web.archive.org
snapshot, since the live portal itself returned a connection-reset error on
direct curl -- and it matches (nearly word-for-word, 4 disclosed immaterial
variances only) the qanoonsa.com text used for storage, with additional
structural/substantive corroboration from nezams.com and argaam.com. This is
NOT classified TIER_1 because Tier 1 requires either two independent official
sources agreeing, or at least two independent archived snapshots of the same
official source -- here only one BOE snapshot was available (confirmed via
the Wayback Availability API, which returned exactly one capture for this
lawId). It is stronger than TIER_3 because a genuine official primary source
(BOE) WAS reached and used to verify the full text, not merely secondary
aggregators. See verification_methodology_note and known_unresolved_
discrepancies in the source artifact for the full account and an explicit
recommendation to re-verify against a live/second BOE snapshot when available.

22 articles, NO chapter/فصل structure (a short, flat, directly-numbered law);
all 22 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة (a brand-new 2025 law -- no amendments
possible/found this pass). Diacritics (tashkeel) are stripped uniformly from
article bodies for consistency with this corpus's other BOE-family tracks;
digits are normalized to Western digits throughout (the source's one instance
of a percent sign, "٪", is preserved as sourced, per this corpus's no-silent-
correction policy -- see known_unresolved_discrepancies).

IMPLEMENTING REGULATION -- referenced via qanoonsa.com/p/514706 ("اللائحة
التنفيذية لنظام المواد البترولية والبتروكيماوية") but NOT built this pass; its
full verbatim text could not be reached and verified within reasonable effort.
Flagged as a follow-up candidate track
(petroleum_petrochemical_materials_regulation, law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "petroleum_petrochemical_materials_law", "law", "official_source",
                   "petroleum_petrochemical_materials_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "petroleum_petrochemical_materials_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "petroleum_petrochemical_materials_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "petroleum_petrochemical_materials_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "petroleum_petrochemical_materials_law_arabic_legal_llm",
                        "petroleum_petrochemical_materials_law_legal_llm_001_022.json")

LAW_ID = "sa-petroleum-petrochemical-materials-law-m139-1446"
LAW_AR = "نظام المواد البترولية والبتروكيماوية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"petroleum_petrochemical_materials_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير المواد البترولية البتروكيماوية العمليات").split())


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
        ver.append({"law_key": "petroleum_petrochemical_materials_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PETROLEUM_PETROCHEMICAL_MATERIALS_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this is the currently in-force "
                                              "Petroleum and Petrochemical Materials Law (Royal "
                                              "Decree M/139, 12/7/1446H), a brand-new base-law "
                                              "track built from scratch this pass (not "
                                              "previously in this corpus). Article 21 OF THE "
                                              "LAW ITSELF states it replaces the prior Petroleum "
                                              "Products Trading Law (M/18, 28/1/1439H). "
                                              "laws.boe.gov.sa was checked FIRST per standard "
                                              "methodology; its live portal is unreachable this "
                                              "pass (connection reset), but a SINGLE "
                                              "web.archive.org snapshot (2026-01-17) was reached "
                                              "and matches the qanoonsa.com text used for "
                                              "storage nearly word-for-word (4 disclosed "
                                              "immaterial variances only). TIER_2. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "petroleum-petrochemical-materials-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "petroleum_petrochemical_materials_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المواد البترولية والبتروكيماوية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/139), "
                                                          "12/7/1446H (Council of Ministers "
                                                          "Resolution 473, 7/7/1446H; Shura "
                                                          "Council Resolution 80/8, 2/5/1446H) "
                                                          "— the currently in-force Petroleum "
                                                          "and Petrochemical Materials Law, "
                                                          "which by its own Article 21 replaces "
                                                          "the prior Petroleum Products Trading "
                                                          "Law (M/18, 28/1/1439H). Text "
                                                          "cross-verified word-for-word against "
                                                          "a single web.archive.org snapshot of "
                                                          "the official laws.boe.gov.sa portal "
                                                          "(live portal unreachable this pass), "
                                                          "plus nezams.com and argaam.com "
                                                          "structural/substantive corroboration. "
                                                          "TIER_2."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/139) وتاريخ 12/7/1446هـ (قرار مجلس الوزراء رقم (473) وتاريخ 7/7/1446هـ؛ قرار مجلس الشورى رقم (80/8) وتاريخ 2/5/1446هـ) — نظام المواد البترولية والبتروكيماوية النافذ حالياً، الذي يحل -بنص المادة الحادية والعشرين منه ذاتها- محل نظام التجارة بالمنتجات البترولية السابق (م/18، 28/1/1439هـ). النص تحقق منه كلمة بكلمة مقابل لقطة أرشيفية وحيدة لبوابة laws.boe.gov.sa الرسمية (البوابة الحية غير قابلة للوصول هذه الجولة)، إضافة إلى تحقق هيكلي وموضوعي من nezams.com وargaam.com. المستوى TIER_2.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "petroleum_petrochemical_materials_law",
               "layer": "PETROLEUM_PETROCHEMICAL_MATERIALS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-petroleum-petrochemical-materials-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (22 مادة؛ 22 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Petroleum and Petrochemical Materials Law (Royal Decree M/139, "
                            "12/7/1446H) — Arabic LLM-ready layer (22 records: 22 original, 0 "
                            "amended, 0 added, 0 repealed; no chapter structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 22], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Petroleum and Petrochemical Materials Law records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
