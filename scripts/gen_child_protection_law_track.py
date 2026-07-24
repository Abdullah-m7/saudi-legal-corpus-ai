#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Child Protection Law track (نظام حماية الطفل,
Royal Decree M/14, 3/2/1436H / ~2014G), as amended by CoM Resolution 427 /
Royal Decree M/72 (1443H).

VERIFICATION TIER -- see sources/child_protection/law/official_source/
child_protection_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY SOURCE ACCESS FAILED THIS PASS: laws.boe.gov.sa DOES have a dedicated
lawId page for this law (2d3cb83a-0379-4cde-8e0b-a9a700f272bd) but the live
portal returned HTTP 503 (WebFetch) / HTTP 000 connection-reset (direct curl)
on repeated attempts. Wayback Machine was NOT attempted (web.archive.org is an
organization egress-policy block for this session, per other tracks in this
corpus -- not routed around).

SECONDARY SOURCES: (1) nezams.com (an independent Arabic legal-text aggregator),
fetched via curl (HTTP 200), supplied the full verbatim text -- 26 "subject"
elements (subject-1..subject-26): 25 numbered articles + one added mukarrar
(Article 23-mukarrar). (2) An OFFICIAL government document -- the Ministry of
Justice's Adl-journal PDF (adlm.moj.gov.sa/attach/1462.pdf, HTTP 200) -- carries
the official ORIGINAL (1436H) text and independently confirmed the decree
identity (M/14, 3/2/1436H), the five-chapter structure (identical titles), and
that the original comprised 25 articles ending at Article 25 with NO mukarrar
and no 1443H references (i.e. pre-amendment). Its Arabic PDF extraction carried
bidi/ligature reordering artifacts, so it was used for identity/structure/count
confirmation, not char-level verbatim; verbatim text is from nezams. (3) The
1443H amendment (CoM 427, RD M/72) was independently confirmed via WebSearch
indexing of the Umm Al-Qura official gazette (uqn.gov.sa) and multiple
independent secondaries. -> TIER_3.

26 records: 21 اصلية, 4 معدلة (Articles 12, 15, 19, 23), 0 ملغاة, 1 مضافة
(Article 23-mukarrar). 5 chapters (فصول).

AMENDED-ARTICLE TEXT POLICY (a documented, intentional divergence from
commercial_agencies_law's current-text-in-body policy): for the 4 amended
articles, the `text` field carries the ORIGINAL verbatim wording (double-
confirmed: nezams body + the official MOJ PDF), and the verbatim CoM-427
amendment instruction -- including the added/replaced wording -- is preserved in
`history`. The post-amendment CONSOLIDATED text was NOT reconstructed into
`text`, because no reachable source (BOE unreachable) provided a verbatim
consolidated text and this corpus's trust rule forbids silent merging; the
amendment is loudly flagged (legal_status_ar=معدلة, status=AMENDED_DATED,
history). The added Article 23-mukarrar carries its added verbatim text in
`text` (it has no "original").

DISTINCTNESS: this is نظام حماية الطفل (child welfare/rights), a DISTINCT statute
from this corpus's juveniles_law (نظام الأحداث, M/113 1439H, 24 articles,
criminal-justice treatment of minors) and from the separate protection_from_abuse
candidate (نظام الحماية من الإيذاء). Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "child_protection", "law", "official_source",
                   "child_protection_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "child_protection", "law", "verified")
RECORDS = os.path.join(OUT_VER, "child_protection_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "child_protection_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "child_protection_arabic_legal_llm",
                        "child_protection_law_legal_llm_001_025.json")

LAW_ID = "sa-child-protection-law-m-14-1436"
LAW_AR = "نظام حماية الطفل"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_ADDED_DATED = "ADDED_DATED"
KEY_RE = r"child_protection_law_art_(\d{3})(?:_mukarrar)?$"
AMENDED_KEYS: set[str] = {
    "child_protection_law_art_012",
    "child_protection_law_art_015",
    "child_protection_law_art_019",
    "child_protection_law_art_023",
}
ADDED_KEYS: set[str] = {"child_protection_law_art_023_mukarrar"}
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الطفل الجهات ذات العلاقة").split())


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
    return (n, 1) if key.endswith("_mukarrar") else (n, 0)


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    if key in ADDED_KEYS:
        return STATUS_ADDED_DATED
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
        ver.append({"law_key": "child_protection", "law_component": "law",
                    "language": "ar",
                    "record_layer": "CHILD_PROTECTION_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; laws.boe.gov.sa HAS a dedicated "
                                              "lawId page for this law "
                                              "(2d3cb83a-0379-4cde-8e0b-a9a700f272bd) but it was "
                                              "unreachable this pass (HTTP 503 live; Wayback NOT "
                                              "attempted -- egress-policy-blocked, not bypassed). "
                                              "Full verbatim text is from nezams.com (independent "
                                              "aggregator, HTTP 200); the decree identity, the "
                                              "five-chapter structure and the original 25-article "
                                              "text were independently confirmed by the OFFICIAL "
                                              "Ministry of Justice Adl-journal PDF (pre-amendment "
                                              "1436H version), and the 1443H amendment (CoM 427 / "
                                              "RD M/72) via the Umm Al-Qura gazette and WebSearch. "
                                              "For the 4 amended articles the text field is the "
                                              "ORIGINAL verbatim wording, with the verbatim CoM-427 "
                                              "amendment preserved in history (NOT silently "
                                              "merged) -- see verification_methodology_note and "
                                              "known_unresolved_discrepancies before relying on "
                                              "this track's text or provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "child-protection-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "child_protection/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام حماية الطفل" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/14 (3/2/1436H), CoM "
                                                          "Resolution 50 (24/1/1436H); amended by "
                                                          "CoM Resolution 427 (5/8/1443H) / Royal "
                                                          "Decree M/72 (6/8/1443H). Full text from "
                                                          "nezams.com (independent aggregator); "
                                                          "decree identity, 5-chapter structure and "
                                                          "original 25-article text independently "
                                                          "confirmed via the OFFICIAL Ministry of "
                                                          "Justice Adl-journal PDF (pre-amendment), "
                                                          "and the 1443H amendment via the Umm "
                                                          "Al-Qura gazette and WebSearch; "
                                                          "laws.boe.gov.sa's dedicated lawId page "
                                                          "(2d3cb83a-0379-4cde-8e0b-a9a700f272bd) "
                                                          "was unreachable this pass (live 503; "
                                                          "Wayback egress-blocked, not bypassed)"),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/14) وتاريخ 3/2/1436هـ، وقرار مجلس الوزراء رقم (50) وتاريخ 24/1/1436هـ؛ وعُدِّل بقرار مجلس الوزراء رقم (427) وتاريخ 5/8/1443هـ (المرسوم الملكي م/72، 6/8/1443هـ). النص الكامل من nezams.com (مصدر ثانوي مستقل)، مع تحقق مستقل من هوية المرسوم وبنية الفصول الخمسة والنص الأصلي (25 مادة) عبر وثيقة مجلة العدل الرسمية بوزارة العدل (سابقة للتعديل)، وتحقق التعديل عبر جريدة أم القرى ونتائج البحث؛ الصفحة المخصصة على laws.boe.gov.sa (lawId 2d3cb83a-0379-4cde-8e0b-a9a700f272bd) غير قابلة للوصول هذه الجولة (503 حيا، وWayback محظور ولم يُتجاوَز)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "child_protection",
               "layer": "CHILD_PROTECTION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", True),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-child-protection-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (26 سجلا؛ 21 أصلية، 4 معدلة، 1 مضافة)",
               "title_en": "Saudi Arabian Child Protection Law — Arabic LLM-ready layer (26 records: 21 original, 4 amended, 1 added)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "includes_mukarrar": ["child_protection_law_art_023_mukarrar"],
               "text_status": "CONSOLIDATED_WITH_DATED_AMENDMENTS",
               "consolidated_amended_law": src.get("consolidated_amended_law", True),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Child Protection Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
