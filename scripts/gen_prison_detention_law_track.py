#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Prison and Detention Law track (نظام السجن والتوقيف,
Royal Decree M/31, 21/6/1398H / ~1978G; amended by Royal Decree M/75
14/9/1428H, Royal Decree M/45 11/9/1430H, Royal Decree M/28 1/5/1435H, and
Council of Ministers Resolution 217 29/4/1439H).

VERIFICATION TIER -- see sources/prison_detention/law/official_source/
prison_detention_law_official_source.json's verification_methodology_note for
the full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law (19945fe2-e690-4b24-9ab0-a9a700f17d03, confirmed to
exist via web search results) but the live portal returned HTTP 503 (WebFetch)
/ HTTP 000 connection-reset (direct curl, including a bare root-domain probe).
An official Ministry of Interior PDF ("Prison regulations.pdf", moi.gov.sa)
also exists but was likewise unreachable this pass (same failure pattern).
web.archive.org was NOT attempted -- WebFetch itself reported it is unable to
fetch from that host for this session; this was not bypassed.

SOURCES USED (TIER_3):
  * PRIMARY full text (all 31 articles, including the three amendment
    passages quoted in-page): nezams.com (independent legal aggregator),
    fetched directly (HTTP 200), 31 numbered "subject" elements.
  * INDEPENDENT cross-check of the ORIGINAL (pre-amendment) text for every
    article: islamport.com / al-Mawsuea al-Shamela (windows-1256 encoded
    archive, fetched directly HTTP 200) -- an archive independent of
    nezams.com that predates (or never incorporated) the three amendments,
    and matches nezams.com's quoted "original" text verbatim (diacritic-only
    differences) for articles 4, 20 and 25, and matches all other 28 articles
    verbatim. islamport.com also independently supplies the ordinal label for
    Article 31 ("المادة الحادية والثلاثون"), which nezams.com's own <h4>
    dropped (a scraping artifact on nezams' side; the article body text
    itself is intact and identical on both sites).

Because no live/archived access to the canonical BOE portal or the MOI PDF
could be obtained this pass (with no policy bypass attempted), and only
nezams.com (not independently corroborated) supplies the amendment TEXT
itself, this track is honestly kept at TIER_3.

31 records: 28 اصلية, 3 معدلة (arts 4, 20, 25), 0 ملغاة, 0 مضافة. The statute
has NO chapter/باب/فصل divisions (flat 1-31, confirmed by an exhaustive scan
of the primary source text for "الباب"/"الفصل" -- zero hits); section_ar is
empty for every article by design.

Article 4 is UNIQUE in this corpus: it was amended TWICE across two different
decades -- Royal Decree M/28 (1/5/1435H) then Council of Ministers Resolution
217 (29/4/1439H, superseding the first amendment). All three versions are
preserved: history[type=original] (1398H), history[type=amendment_intermediate]
(M/28, 1435H -- superseded but never discarded), and history[type=
amendment_current] (Resolution 217, 1439H -- also the current `text`). No
Royal Decree could be found this pass formally promulgating Resolution 217's
amendment (flagged as an unresolved research gap, NOT asserted as a settled
fact that a CoM Resolution alone amended a Royal-Decree statute).

Articles 20 and 25 each carry a single ordinary amendment: Article 20 (Royal
Decree M/75, 14/9/1428H) deleted the flogging penalty (former paragraph 3)
and a dependent phrase; Article 25 (Royal Decree M/45, 11/9/1430H) added
paragraph (b) on additional pardon time for education/training program
completion, renaming the original text paragraph (a).

NO PREDECESSOR REPEAL FOUND: no repeal clause (named or general) was found in
the text; Article 31 is only the publication-effective-date rule with no
90-day grace period (unlike more modern statutes in this corpus). This is
recorded as "not confirmed either way" rather than asserted as a founding
statute, since absence of evidence of repeal is not evidence of its absence
for a law this old.

Implementing Regulation(s) referenced (Article 30 and others) are OUT OF
SCOPE for this track (one-instrument-per-pass rule) -- flagged as a follow-up
candidate.

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; in-word decorative kashida removed (هـ/جـ preserved); stray
space-before-punctuation (a nezams.com HTML-editor artifact) cleaned up --
display-layer only, no legal text altered. Arabic-Indic numerals preserved
verbatim as they appear per-article in the source (no numeral-system
conversion). Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "prison_detention", "law", "official_source",
                   "prison_detention_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "prison_detention", "law", "verified")
RECORDS = os.path.join(OUT_VER, "prison_detention_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "prison_detention_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "prison_detention_arabic_legal_llm",
                        "prison_detention_law_legal_llm_001_031.json")

LAW_ID = "sa-prison-detention-law-m-31-1398"
LAW_AR = "نظام السجن والتوقيف"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"prison_detention_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {
    "prison_detention_law_art_004",
    "prison_detention_law_art_020",
    "prison_detention_law_art_025",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات السجن التوقيف المسجون الموقوف").split())


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
            "(19945fe2-e690-4b24-9ab0-a9a700f17d03) and an official Ministry of Interior PDF also exists "
            "(moi.gov.sa, 'Prison regulations.pdf'), but BOTH were unreachable this pass (HTTP 503 / "
            "connection reset on repeated attempts, including a bare root-domain probe; web.archive.org "
            "was not attempted -- WebFetch itself reported it cannot fetch that host this session, and "
            "this was not bypassed). ORIGINAL full text (all 31 articles) is cross-verified verbatim "
            "between nezams.com (primary, carries the amendment passages in-page) and islamport.com / "
            "al-Mawsuea al-Shamela (independent pre-amendment archive) -> TIER_3. 31 articles, flat (no "
            "chapters); arts 4/20/25 معدلة, all others اصلية. Article 4 is UNIQUE: amended TWICE (Royal "
            "Decree M/28, 1435H, then CoM Resolution 217, 1439H) -- all three text versions preserved "
            "(original / amendment_intermediate / amendment_current). No repeal of any named predecessor "
            "was found, but this is recorded as unconfirmed rather than asserted, given the statute's age. "
            "See verification_methodology_note and known_unresolved_discrepancies in the source artifact "
            "before relying on this track's text or provenance -- in particular the suspected transcription "
            "typo in Article 4's current text ('وسلة' vs 'وسيلة') and the unresolved question of whether a "
            "CoM Resolution alone (217, 1439H) can amend a Royal-Decree statute without an accompanying "
            "Royal Decree.")

SRC_AUTH = ("Royal Decree M/31 (21/6/1398H), CoM Resolution 441 (8/6/1398H); amended by Royal Decree M/75 "
            "(14/9/1428H, art 20), Royal Decree M/45 (11/9/1430H, art 25), Royal Decree M/28 (1/5/1435H, "
            "art 4, 1st amendment), and CoM Resolution 217 (29/4/1439H, art 4, 2nd amendment, superseding "
            "the 1st). Full original text cross-checked verbatim between nezams.com and islamport.com "
            "(al-Mawsuea al-Shamela); amendment texts confirmed only via nezams.com's in-page quotations. "
            "laws.boe.gov.sa's dedicated lawId page (19945fe2-e690-4b24-9ab0-a9a700f17d03) and an official "
            "MOI PDF both exist but were unreachable this pass (HTTP 503/connection-reset; Wayback not "
            "attempted per WebFetch's own host restriction, not bypassed) -> TIER_3")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/31 وتاريخ 21/6/1398هـ، وقرار مجلس الوزراء رقم 441 وتاريخ 8/6/1398هـ؛ "
               "عُدلت المادة 20 بالمرسوم الملكي م/75 (14/9/1428هـ)، والمادة 25 بالمرسوم الملكي م/45 "
               "(11/9/1430هـ)، والمادة 4 مرتين: بالمرسوم الملكي م/28 (1/5/1435هـ) ثم بقرار مجلس الوزراء "
               "217 (29/4/1439هـ). النص الأصلي الكامل متطابق حرفيا بين nezams.com وislamport.com (الموسوعة "
               "الشاملة)؛ نصوص التعديلات نفسها مؤكدة من نص nezams.com المقتبس فقط. صفحة laws.boe.gov.sa "
               "المخصصة (lawId 19945fe2-e690-4b24-9ab0-a9a700f17d03) وملف PDF رسمي لوزارة الداخلية كلاهما "
               "موجود لكن تعذر الوصول إليهما هذه الجولة (503/إعادة تعيين الاتصال؛ لم تُحاوَل أرشيف Wayback "
               "بسبب قيد من أداة الجلب نفسها لم يُتجاوَز) -- TIER_3")


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
        ver.append({"law_key": "prison_detention", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PRISON_DETENTION_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "prison-detention-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "prison_detention/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام السجن والتوقيف" % a["number_label_ar"]],
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
    json.dump({"law_key": "prison_detention",
               "layer": "PRISON_DETENTION_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-prison-detention-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (31 مادة؛ 28 أصلية، 3 معدلة)",
               "title_en": ("Law of Prison and Detention — Arabic LLM-ready layer "
                            "(31 records: 28 original, 3 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 31], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Prison and Detention Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
