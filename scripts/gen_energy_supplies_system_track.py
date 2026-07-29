#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Energy Supplies System track (نظام إمدادات الطاقة, Royal Decree
M/80, 4/6/1444H -- the currently in-force law regulating energy allocation
across ten named consumption sectors -- electricity generation, oil refining,
petrochemicals, water desalination, industry, mining, agriculture,
construction, telecommunications, and transport/logistics -- plus licensing of
natural-gas/gas-liquids/hydrogen activities, administered by the Ministry of
Energy).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام إمدادات الطاقة is a single,
self-standing Royal-Decree law (M/80, 4/6/1444H, on CoM Resolution 374,
3/6/1444H; Shura Council Resolution 304/45, 28/11/1443H), entering into force
60 days after Official Gazette publication (except Article 3, effective
immediately from the Decree's own issuance date). Confirmed via cross-checked
independent sources:
(1) laws.boe.gov.sa carries it under lawId
c1777105-e927-4fa8-978d-af9900e23e18 -- the exact URL supplied for this task.
The LIVE portal returned "Connection reset by peer" on direct curl and HTTP
503 via WebFetch this pass, but a SINGLE web.archive.org snapshot (captured
2025-10-17) was reached directly via HTTPS curl (HTTP 200, 69365 bytes) and
reproduces the actual BOE page content (confirmed via the data-lawid value
embedded in the page's own "report an issue" / "request notification"
buttons, matching the supplied lawId exactly), including the full Royal
Decree preamble, the full CoM Resolution 374 text, an official metadata table
(issuance date 4/6/1444H = 28/12/2022; publication date 13/6/1444H =
6/1/2023; status "ساري"; an official brief confirming the repeal of the
"Gas Supply and Pricing System" of 1424H and the Article-3 early-effect
carve-out), and all 12 articles.
(2) nezams.com (the exact URL supplied for this task,
nezams.com/نظام-إمدادات-الطاقة/) was fetched live via direct curl (HTTP 200,
205789 bytes) and independently reproduces the same preamble, CoM
Resolution, and all 12 articles (12 HTML "subject" elements, id="subject-1"
through "subject-12", matching the BOE snapshot's 12 <article_item> elements
exactly) -- word-for-word matching in legal content, with only immaterial
formatting/decorative variances (decorative kashida placement in 2 articles;
one missing comma in Article 5(1); inconsistent thousands-separator glyphs in
Article 8's two SAR-20-million penalty clauses) -- see known_unresolved_
discrepancies in the source artifact for the full, disclosed account.
(3) akhbaar24.com (the exact URL supplied for this task) substantively
corroborates the predecessor-law repeal, the 60-day commencement, the ten
named sectors, and the SAR-20-million penalty ceiling; one apparent
discrepancy (a claimed "2-year" regulation-issuance deadline) was resolved in
favor of the two-source-verified Article 11 text (60 days) -- the 2-year
figure in fact belongs to the CoM Resolution's separate transitional
license-correction clause, not to regulation issuance; see
known_unresolved_discrepancies.
(4) The Umm Al-Qura Gazette's own official site (uqn.gov.sa/?p=21225, found
via WebSearch and fetched live via curl, HTTP 200) is a client-side
JavaScript/Vue single-page application; its static HTML carried no
extractable article text this pass, so it was NOT used as a storage source
(see known_unresolved_discrepancies).

STORAGE-TEXT CHOICE -- nezams.com's extraction was used as the stored `text`
field (not BOE's), because nezams's HTML embeds explicit digit-dash
enumeration ("1-", "2-", "أ-", "ب-") for sub-clauses within articles (e.g.
Articles 3 and 8), matching this corpus's storage convention (see
petroleum_petrochemical_materials_law and real_estate_contributions_law),
whereas BOE's HTML renders the same sub-clauses as an <ol><li> list with no
literal digit in the extractable text layer (the numbering is CSS-rendered
only). The underlying legal content is identical between the two sources;
only formatting/decorative differences remain, all disclosed.

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT: Article 12 (المادة
الثانية عشرة, the law's final article) states verbatim: "يعمل بالنظام بعد
(ستين) يوما من تاريخ نشره في الجريدة الرسمية، ويحل محل نظام إمدادات الغاز
وتسعيره الصادر بالمرسوم الملكي رقم (م/36) وتاريخ 25/6/1424هـ، ويلغي كل ما
يتعارض معه من أحكام." This exact wording is identical between the BOE
snapshot and nezams.com (module immaterial slash-spacing only), and the
repealed predecessor's identity/date is independently corroborated by BOE's
own official brief ("يحل هذا النظام محل نظام إمدادات الغاز وتسعيره لعام
1424هـ") and by akhbaar24.com. The enacting Royal Decree's own clause
"Third" -- repeated in CoM Resolution 374's clause "Third" -- additionally
carves out a TRANSITIONAL EXCEPTION: licenses issued under the repealed M/36
law remain valid, with licensees required to correct their status within 2
years (submitting a correction plan within 1 year), extendable by the
Minister of Energy up to 6 additional years. Clause "Second" of both
instruments also carves out an early-effect exception for Article 3 (the
Energy Allocation Committee), which takes effect from the Decree's own
issuance date rather than after the general 60-day commencement period.
These clauses live in the preamble/CoM-resolution text, outside the 12
numbered Articles.

VERIFICATION TIER -- TIER_2. Exactly ONE official/primary source
(laws.boe.gov.sa) was reached this pass -- via a SINGLE web.archive.org
snapshot, since the live portal itself returned a connection-reset error on
direct curl and HTTP 503 via WebFetch -- and it matches (word-for-word in
legal content, disclosed immaterial formatting variances only) the
nezams.com text used for storage, with additional partial corroboration from
akhbaar24.com. This is NOT classified TIER_1 because Tier 1 requires either
two independent official sources agreeing, or at least two independent
archived snapshots of the same official source -- here only one BOE snapshot
was available (confirmed via the Wayback Availability API; the CDX API for
discovering further snapshots was blocked by network egress policy this
pass). It is stronger than TIER_3 because a genuine official primary source
(BOE) WAS reached and used to verify the full text, not merely secondary
aggregators. See verification_methodology_note and known_unresolved_
discrepancies in the source artifact for the full account and an explicit
recommendation to re-verify against a live/second BOE snapshot when
available.

12 articles, NO chapter/فصل structure (a short, flat, directly-numbered law);
all 12 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة (a brand-new 2023 law -- no
amendments possible/found this pass). Diacritics (tashkeel) and decorative
kashida are stripped uniformly from article bodies (not from preamble_ar /
com_resolution_ar, which retain nezams.com's own natural tashkeel); Eastern
Arabic-Indic digits are normalized to Western digits throughout. The source's
one disclosed inconsistency in thousands-separator glyphs for the SAR
20,000,000 penalty figure (Article 8) is preserved exactly as sourced per
this corpus's no-silent-correction policy -- see known_unresolved_
discrepancies.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "energy_supplies_system", "law", "official_source",
                   "energy_supplies_system_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "energy_supplies_system", "law", "verified")
RECORDS = os.path.join(OUT_VER, "energy_supplies_system_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "energy_supplies_system_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "energy_supplies_system_arabic_legal_llm",
                        "energy_supplies_system_legal_llm_001_012.json")

LAW_ID = "sa-energy-supplies-system-m80-1444"
LAW_AR = "نظام إمدادات الطاقة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"energy_supplies_system_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير الطاقة").split())


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
        ver.append({"law_key": "energy_supplies_system", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ENERGY_SUPPLIES_SYSTEM_ARABIC_VERIFIED_TEXT",
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
                                              "Energy Supplies System (Royal Decree M/80, "
                                              "4/6/1444H), a brand-new base-law track built "
                                              "from scratch this pass (not previously in this "
                                              "corpus). Article 12 OF THE LAW ITSELF states it "
                                              "replaces the prior Gas Supply and Pricing System "
                                              "(M/36, 25/6/1424H). laws.boe.gov.sa was checked "
                                              "FIRST per standard methodology; its live portal "
                                              "is unreachable this pass (connection reset / "
                                              "HTTP 503), but a SINGLE web.archive.org snapshot "
                                              "(2025-10-17) was reached and matches the "
                                              "nezams.com text used for storage word-for-word "
                                              "in legal content (disclosed immaterial "
                                              "formatting variances only). TIER_2. See "
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
                    "record_id": "energy-supplies-system-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "energy_supplies_system/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام إمدادات الطاقة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/80), "
                                                          "4/6/1444H (Council of Ministers "
                                                          "Resolution 374, 3/6/1444H; Shura "
                                                          "Council Resolution 304/45, "
                                                          "28/11/1443H) — the currently "
                                                          "in-force Energy Supplies System, "
                                                          "which by its own Article 12 "
                                                          "replaces the prior Gas Supply and "
                                                          "Pricing System (M/36, 25/6/1424H). "
                                                          "Text cross-verified word-for-word "
                                                          "against a single web.archive.org "
                                                          "snapshot of the official "
                                                          "laws.boe.gov.sa portal (live portal "
                                                          "unreachable this pass), plus "
                                                          "akhbaar24.com partial "
                                                          "corroboration. TIER_2."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/80) وتاريخ 4/6/1444هـ (قرار مجلس الوزراء رقم (374) وتاريخ 3/6/1444هـ؛ قرار مجلس الشورى رقم (304/45) وتاريخ 28/11/1443هـ) — نظام إمدادات الطاقة النافذ حالياً، الذي يحل -بنص المادة الثانية عشرة منه ذاتها- محل نظام إمدادات الغاز وتسعيره السابق (م/36، 25/6/1424هـ). النص تحقق منه كلمة بكلمة مقابل لقطة أرشيفية وحيدة لبوابة laws.boe.gov.sa الرسمية (البوابة الحية غير قابلة للوصول هذه الجولة)، إضافة إلى تحقق جزئي من akhbaar24.com. المستوى TIER_2.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "energy_supplies_system",
               "layer": "ENERGY_SUPPLIES_SYSTEM_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-energy-supplies-system-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (12 مادة؛ 12 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Energy Supplies System (Royal Decree M/80, 4/6/1444H) — "
                            "Arabic LLM-ready layer (12 records: 12 original, 0 amended, 0 "
                            "added, 0 repealed; no chapter structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 12], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Energy Supplies System records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
