#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Law of Audiovisual Media track (نظام الإعلام المرئي والمسموع,
Royal Decree M/33, 25/3/1439H / ~13 December 2017G; amended by Council of Ministers
Resolution No. 374, 28/6/1440H / ~5 March 2019G).

VERIFICATION TIER -- see sources/audiovisual_media/law/official_source/
audiovisual_media_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated lawId
page for this law (ed5fdbc0-c183-4a8a-a8b7-a9ed004b5900) but the live portal
returned HTTP 503 (WebFetch) / HTTP 000 connection-reset (direct curl).
web.archive.org was NOT attempted -- the WebFetch tool itself refused this host
("Claude Code is unable to fetch from web.archive.org") and this was not bypassed.

SOURCES USED (TIER_2):
  * PRIMARY full text (all 25 articles): nezams.com (independent legal aggregator),
    fetched directly (HTTP 200) and parsed programmatically: exactly 25 "subject"
    elements (subject-1..subject-25), spelled-ordinal labels المادة الأولى..
    الخامسة والعشرون, matching the declared article_count exactly.
  * STRONG CROSS-CHECK: an archived print/scan of the actual laws.boe.gov.sa portal
    Viewer page (dated 15/8/2020, hosted via cyrilla.org, an independent legal-
    rights document archive) -- shows the government letterhead, decree number
    (م/33) and date (25/3/1439هـ), the full Royal Decree and Council of Ministers
    Resolution (170) preambles (incl. the 12-month compliance grace period), and
    verbatim text for Article 1 (all 16 definitions) and Articles 6-10 and 21-25.
    Every sampled portion matched nezams.com's text CHARACTER FOR CHARACTER.
  * INDEPENDENT OFFICIAL CROSS-CHECK: the official Bureau of Experts (BOE) English
    translation of this Law (Official Translation Department, otd@boe.gov.sa),
    hosted at misa.gov.sa (Ministry of Investment of Saudi Arabia). Confirms 25
    articles, no chapter divisions, and its Appendix quotes the SAME amendment
    (Council of Ministers Resolution No. 374, 28/6/1440H = 5 March 2019G) renaming
    "Minister/Ministry of Culture and Information" to "Minister/Ministry of Media" --
    in exact agreement with nezams.com's quoted Arabic resolution text, though
    produced completely independently (BOE itself vs. an independent Arabic
    aggregator).

Not TIER_1 because the canonical BOE portal page itself was not retrieved LIVE by
this session (only cross-verified via a third-party archived capture of it).

25 records: 24 اصلية, 1 معدلة (art 1), 0 ملغاة, 0 مضافة. The statute has NO
chapter/باب/فصل divisions (flat 1-25); section_ar is empty for every article by
design. Article 1 was amended by a PURE horizontal terminology substitution
(Resolution 374 renamed "Minister/Ministry of Culture and Information" to
"Minister/Ministry of Media" wherever mentioned) -- no new definition item was
added and no other article's operative wording changed; the CURRENT enacted text
of Article 1 (as originally published, unmodified) is stored in `text`, with the
substitution note preserved verbatim in history[type=amendment_current] -- the
same treatment the associations_ngo_law track uses for an analogous horizontal
substitution (Resolution 618) affecting its own Article 1.

NO PREDECESSOR REPEAL: Article 25 is only a generic conflict clause ("this Law
shall repeal any provisions conflicting therewith") -- no named prior law/
regulation/resolution is repealed. This is a founding statute for the audiovisual
media sector.

DISTINCT FROM press (نظام المطبوعات والنشر, Royal Decree M/32, 3/9/1421H, already
a separate track in this corpus): Article 1's definitions of "Preliminary
Committee" and "Appeal Committee" merely CROSS-REFERENCE committees formed under
that other law -- not a merge, not an overlap of governing text.

OUT OF SCOPE (follow-up candidates, not ingested this pass): the Implementing
Regulation (Article 23 mandates issuance within 90 days); and the GCAM
establishment regulation (Council of Ministers Resolution No. 332, 16/10/1433H,
referenced in this decree's own preamble) which separately founded the General
Commission/Authority for Audiovisual Media as an institution.

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; double/nbsp spaces removed -- display-layer only, no legal text
altered. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "audiovisual_media", "law", "official_source",
                   "audiovisual_media_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "audiovisual_media", "law", "verified")
RECORDS = os.path.join(OUT_VER, "audiovisual_media_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "audiovisual_media_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "audiovisual_media_arabic_legal_llm",
                        "audiovisual_media_law_legal_llm_001_025.json")

LAW_ID = "sa-audiovisual-media-law-m-33-1439"
LAW_AR = "نظام الإعلام المرئي والمسموع"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"audiovisual_media_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {
    "audiovisual_media_law_art_001",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة الوزارة الوزير المرخص الرئيس المجلس").split())


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
            "(ed5fdbc0-c183-4a8a-a8b7-a9ed004b5900) but it was unreachable this pass "
            "(HTTP 503 live / connection reset; web.archive.org refused by the WebFetch "
            "tool itself and NOT bypassed). PRIMARY full text is from nezams.com "
            "(independent legal aggregator, exactly 25 subject elements), strongly "
            "cross-checked against an archived print/scan of the actual BOE portal "
            "Viewer page (via cyrilla.org, dated 15/8/2020, character-for-character "
            "match on every sampled article) and against the official BOE English "
            "translation (via misa.gov.sa) whose Appendix independently confirms the "
            "1440H amendment (CoM Resolution 374) -> TIER_2. 25 articles, flat (no "
            "chapters); art 1 معدلة (pure ministry/minister terminology substitution, "
            "no content change), all others اصلية; no repeal of any predecessor. "
            "DISTINCT from press (نظام المطبوعات والنشر, M/32 1421H) -- only a "
            "cross-reference for two committees, not a merge. See "
            "verification_methodology_note and known_unresolved_discrepancies in the "
            "source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/33 (25/3/1439H), CoM Resolution 170 (24/3/1439H); amended "
            "by CoM Resolution 374 (28/6/1440H) for art 1 (Minister/Ministry of Culture "
            "and Information -> Minister/Ministry of Media, terminology only). Original "
            "full text from nezams.com cross-checked against an archived BOE portal "
            "scan (cyrilla.org) and the official BOE English translation (misa.gov.sa) "
            "whose Appendix independently confirms the amendment. laws.boe.gov.sa "
            "dedicated lawId page (ed5fdbc0-c183-4a8a-a8b7-a9ed004b5900) unreachable "
            "this pass (live 503; Wayback refused by tool, not bypassed) -> TIER_2")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/33 وتاريخ 25/3/1439هـ، وقرار مجلس الوزراء رقم 170 وتاريخ "
               "24/3/1439هـ؛ عُدلت المادة الأولى (تسمية الوزارة/الوزير فقط) بقرار مجلس الوزراء "
               "رقم 374 وتاريخ 28/6/1440هـ. النص الأصلي الكامل من nezams.com متقاطع مع صورة "
               "مؤرشفة لبوابة هيئة الخبراء (cyrilla.org) ومع الترجمة الإنجليزية الرسمية "
               "(misa.gov.sa) التي يؤكد ملحقها التعديل استقلالا. الصفحة المخصصة على "
               "laws.boe.gov.sa (lawId ed5fdbc0-c183-4a8a-a8b7-a9ed004b5900) غير قابلة "
               "للوصول هذه الجولة (503 حيا، وWayback رفضته الأداة ولم يُتجاوَز) -- TIER_2")


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
        ver.append({"law_key": "audiovisual_media", "law_component": "law",
                    "language": "ar",
                    "record_layer": "AUDIOVISUAL_MEDIA_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "audiovisual-media-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "audiovisual_media/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الإعلام المرئي والمسموع" % a["number_label_ar"]],
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
    json.dump({"law_key": "audiovisual_media",
               "layer": "AUDIOVISUAL_MEDIA_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-audiovisual-media-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة؛ 24 أصلية، 1 معدلة)",
               "title_en": ("Law of Audiovisual Media — Arabic LLM-ready layer "
                            "(25 records: 24 original, 1 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Audiovisual Media Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
