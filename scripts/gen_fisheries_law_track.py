#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Fisheries / Marine Resources Law track (نظام صيد واستثمار
وحماية الثروات المائية الحية في المياه الإقليمية للمملكة العربية السعودية, Royal Decree
M/9, 27/3/1408H -- a REPEALED former MEWA-sector base law).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It is built
from scratch this pass, at the request of the project owner following a prior light-pass
scan that noted repeated HTTP 503s from laws.boe.gov.sa and could not confirm the article
count. This pass resolves that: the primary source (laws.boe.gov.sa) was reached directly
via the Wayback Machine (not egress-blocked this pass), across TWO independent snapshots
six years apart (21 Nov 2019 and 16 Nov 2025), with byte-identical article text.

CRITICAL FACT -- THIS LAW IS CURRENTLY REPEALED (لاغي), NOT IN FORCE. laws.boe.gov.sa's
own "الحالة" (status) field shows "ساري" in the Nov 2019 snapshot and "لاغي" in every
snapshot from Aug 2021 onward -- consistent with the Agriculture Law (Royal Decree M/64,
10/8/1442H) entering into force ~90 days after its 20/8/1442H gazette publication (~mid-
2021G). The repeal is effected by clause (Second/1) of the Agriculture Law's OWN issuing
Royal Decree (M/64) and the accompanying Council of Ministers Resolution (431), which name
this Law explicitly by title, number and date among five repealed instruments -- the SAME
fact already independently recorded in this corpus's own agriculture track (see
sources/agriculture/law/official_source/agriculture_law_official_source.json, field
supersedes_ar). This is an in-corpus cross-check in addition to BOE's own direct,
twice-confirmed status field. This track does NOT delete or silently omit anything on
account of the repeal -- the full verbatim text of all 13 articles is preserved, and the
repeal is flagged prominently via the top-level legal_status_ar="لاغي" and a dedicated
repealed_by_ar field, distinct from any individual article's own legal_status_ar.

STRUCTURE -- 13 articles, flat (no chapter/part divisions -- confirmed by BOE's own
article-list rendering, no فصل/باب heading appears anywhere). 12 articles اصلية; 1 (Article
10) معدلة (amended by Royal Decree M/58, 16/9/1437H, adding a تشهير/publication penalty
clause per BOE's own per-article amendment note -- BOE's own main running text for Article
10 still shows the pre-amendment wording, so the added clause is recorded in that article's
history, not silently merged into its text, mirroring this corpus's environmental_law
Article-1 precedent for a stale-main-body-vs-amendment-note situation). 0 مضافة. 0 ملغاة at
the individual-article level: BOE's own per-article CSS tags 12 of the 13 articles
"canceled-article" and Article 10 "changed-article", but this is interpreted (and disclosed
in known_unresolved_discrepancies) as reflecting the WHOLE document's repeal at the
per-article rendering level, not 13 independent per-article repeal events -- so no
individual article carries legal_status_ar="ملغاة" in this track; the whole-law repeal is
recorded only at the top level (legal_status_ar / repealed_by_ar).

VERIFICATION TIER -- TIER_1. Full verbatim text obtained DIRECTLY from this corpus's
designated primary source (laws.boe.gov.sa) via the Wayback Machine (not a secondary
aggregator), self-consistent across two independent snapshots six years apart, plus
in-corpus cross-check (this corpus's own agriculture track) and external corroboration
(ECOLEX, InforMEA, Lexis Middle East). One genuine, EXPLICITLY UNRESOLVED secondary-source
conflict is flagged and NOT silently resolved: ECOLEX/InforMEA (citing FAOLEX) describe 17
articles under 4 headings, contradicting BOE's own confirmed 13-article flat structure;
FAOLEX's own Arabic PDF was fetched but its embedded font encoding is corrupted
(unreadable), so this conflict could not be independently adjudicated via that source --
BOE is trusted as the corpus's designated primary source, but the conflict is recorded, not
hidden. See known_unresolved_discrepancies in the source artifact before relying on this
track.

An Implementing Regulation is known to exist (Ministerial Decision No. 21911, 27/3/1409H,
per Lexis Middle East) but its text was NOT verified this pass and is NOT ingested -- it is
flagged as a follow-up candidate only (fisheries_law_regulation), per the "one law per
pass, only ingest a regulation if fully verifiable" rule. Any follow-up pass must first
determine whether that Implementing Regulation was itself repealed/superseded along with
its parent law.

Diacritics (tashkeel) are, UNUSUALLY for this corpus, PRESERVED verbatim in this track (not
stripped): the text here comes directly from BOE itself (not a secondary aggregator as in
agriculture_law), and BOE's own displayed text retains partial original 1980s-style Saudi
legal typesetting diacritics on scattered letters -- stripping them would be an
unrequested silent alteration of primary-source content. Only pure whitespace technical
artifacts (consecutive spaces from BOE's own HTML term-highlighting markup) are collapsed
to single spaces, per this corpus's internal double-space quality guard.

Arabic governs; no translation/paraphrase/interpretation of the Arabic text. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "fisheries_law", "law", "official_source",
                   "fisheries_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "fisheries_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "fisheries_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "fisheries_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "fisheries_law_arabic_legal_llm",
                        "fisheries_law_legal_llm_001_013.json")

LAW_ID = "sa-fisheries-law-m9-1408"
LAW_AR = "نظام صيد واستثمار وحماية الثروات المائية الحية في المياه الاقليمية للمملكة العربية السعودية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"fisheries_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"fisheries_law_art_010"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير هذا لها منه فيها بها").split())


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

    governing_source_note = (
        "Arabic governs; this is a REPEALED (لاغي) former base law (Royal Decree M/9, "
        "27/3/1408H) -- a brand-new track built from scratch this pass, not previously in "
        "this corpus. It was superseded in its entirety by clause Second/1 of the "
        "Agriculture Law's issuing Royal Decree (M/64, 10/8/1442H), NOT by any provision "
        "inside this law's own 13 articles; the same fact is already independently recorded "
        "in this corpus's agriculture track. laws.boe.gov.sa returned HTTP 503 live this "
        "pass but was reached directly via the Wayback Machine across two independent "
        "snapshots (2019, 2025) with byte-identical text -- TIER_1, direct primary-source "
        "verification, not a secondary aggregator. One secondary-source conflict (ECOLEX/"
        "InforMEA citing FAOLEX: 17 articles/4 headings) is explicitly flagged as "
        "UNRESOLVED, not hidden -- see known_unresolved_discrepancies and "
        "verification_methodology_note in the source artifact before relying on this track."
    )

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
        ver.append({"law_key": "fisheries_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "FISHERIES_LAW_ARABIC_VERIFIED_TEXT",
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
                    "law_current_force_status_ar": src.get("legal_status_ar"),
                    "governing_source_note": governing_source_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "fisheries-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "fisheries_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام صيد واستثمار وحماية الثروات المائية الحية"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "law_current_force_status_ar": src.get("legal_status_ar"),
                    "source_trust": {"source_authority": (
                        "Royal Decree No. (M/9), 27/3/1408H (Council of Ministers Resolution "
                        "No. 14, 21/1/1408H) -- a REPEALED former base law: superseded in its "
                        "entirety by clause Second/1 of the Agriculture Law's issuing Royal "
                        "Decree (M/64, 10/8/1442H), not by any provision within this law's own "
                        "text. Verbatim text obtained directly from laws.boe.gov.sa (this "
                        "corpus's designated primary source) via the Wayback Machine, "
                        "cross-verified across two independent snapshots (2019, 2025) with "
                        "byte-identical text. TIER_1."),
                                     "source_authority_ar": (
                        "المرسوم الملكي رقم (م/9) وتاريخ 27/3/1408هـ (قرار مجلس الوزراء رقم 14 "
                        "وتاريخ 21/1/1408هـ) — نظام لاغٍ حاليا: أُلغي بالكامل بموجب البند "
                        "(ثانيا/1) من مرسوم إصدار نظام الزراعة (م/64، 1442هـ)، لا من داخل متن "
                        "مواد هذا النظام نفسه. النص الحرفي مستمد مباشرة من laws.boe.gov.sa "
                        "(المصدر الأساسي المعتمد لهذه المدونة) عبر أرشيف Wayback Machine، "
                        "ومؤكد عبر لقطتين مستقلتين (2019 و2025) متطابقتين حرفيا. المستوى TIER_1."),
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "law_current_force_status_ar": src.get("legal_status_ar"),
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "fisheries_law",
               "layer": "FISHERIES_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "repealed_by_ar": src.get("repealed_by_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-fisheries-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": (LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (13 مادة؛ 12 "
                            "أصلية، 1 معدلة، 0 مضافة، 0 ملغاة على مستوى المادة؛ دون تقسيم إلى "
                            "فصول؛ النظام بأكمله لاغٍ حاليا -- انظر law_current_force_status_ar)"),
               "title_en": ("The Saudi Arabian Fisheries / Marine Resources Law (Royal Decree "
                            "M/9, 27/3/1408H) — Arabic LLM-ready layer (13 records: 12 "
                            "original, 1 amended, 0 added, 0 individually-repealed articles; "
                            "no chapter divisions; the WHOLE LAW is currently REPEALED -- see "
                            "law_current_force_status_ar on every record)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 13], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "law_current_force_status_ar": src.get("legal_status_ar"),
               "repealed_by_ar": src.get("repealed_by_ar"),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Fisheries Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
