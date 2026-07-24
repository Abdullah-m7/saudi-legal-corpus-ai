#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Civil Defense Law track (نظام الدفاع المدني,
Royal Decree M/10, 10/5/1406H / ~1986G).

VERIFICATION TIER -- see sources/civil_defense/law/official_source/
civil_defense_law_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law (f09eda85-7150-4803-b87a-a9a700f189f3) but the live
portal returned HTTP 503 (WebFetch). The public-consultation platform
istitlaa.ncc.gov.sa ALSO has dedicated per-article pages for this specific law
(category Military/998, e.g. project/Pages/Article_030.aspx) suggesting a
maintained current-text view, but it too returned HTTP 503 (WebFetch) / connection
reset (direct curl). web.archive.org was NOT attempted (environment-blocked for
this session, documented across this corpus and never bypassed).

SOURCES USED FOR THE ORIGINAL 1406H TEXT (TIER_3, all 36 articles):
  * mohamah.net (independent legal-advice aggregator) -- fetched directly via
    curl (HTTP 200), full text of the Royal Decree preamble, CoM Resolution 25,
    and all 36 articles extracted from HTML.
  * islamport.com (الموسوعة الشاملة -- a long-established Islamic/legal-text
    archive, INDEPENDENT of mohamah.net) -- fetched directly via curl (HTTP 200,
    windows-1256 encoding), same full text. Cross-checked article-by-article
    (post tashkeel/whitespace normalization): 36/36 articles match verbatim in
    legal substance; only cosmetic differences (dash glyph, space-before-
    punctuation, abjad vs. standard-alphabet sub-item lettering -- both
    internally self-consistent) plus ONE single-word discrepancy in Article 11
    resolved via internal document-consistency (see
    civil_defense_law_article11_cross_source_discrepancy in the source
    artifact's known_unresolved_discrepancies).

AMENDMENTS -- CONFIRMED TO EXIST, CURRENT TEXT NOT CONFIRMED (the single most
important honesty flag for this track): saudipedia.com (a Ministry-of-Media-
affiliated online encyclopedia citing the Council of Ministers' Bureau of
Experts, fetched directly HTTP 200) states verbatim that "the majority of the
law's articles were amended on various dates," naming Article 5 (amended
1436H/2015G) and Article 28 (amended 1424H/2003G) as examples. Two amending
Royal Decrees were corroborated across multiple independent web-search results:
M/66 (2/10/1424H) and M/63 (13/9/1436H). This pass could NOT retrieve the
verbatim CURRENT (post-amendment) text of either from any directly-reachable
source (BOE and istitlaa both 503; the specific Umm al-Qura gazette pages for
these two decrees could not be resolved with available URL patterns, though the
uqn.gov.sa domain itself IS directly reachable for other pages).

Consequently: Articles 5 and 28 are flagged legal_status_ar=معدلة, but the
`text` field for BOTH stores ONLY the confirmed ORIGINAL 1406H wording (cross-
verified as above) -- NOT a fabricated "current" replacement. Each carries a
single history[type=original] entry whose decree_note explains, in full, that
the current in-force wording is unconfirmed. This deliberately deviates from
this corpus's usual amended-article convention (original + amendment_current)
because the amendment_current text is genuinely unknown -- inventing one would
violate this repository's core trust rule. saudipedia's "majority of articles"
claim further means the true amendment scope almost certainly EXCEEDS what
could be confirmed here; the other 34 articles are "اصلية" only in the sense of
"not specifically identified as amended this pass," not an ironclad guarantee.

36 records: 34 اصلية, 2 معدلة (arts 5, 28 -- original text only, current text
unconfirmed), 0 ملغاة, 0 مضافة. The statute has NO chapter/باب/فصل divisions
(flat 1-36); section_ar is empty for every article by design.

NO NAMED PREDECESSOR LAW REPEAL: Article 35 is a general conflict-clause only
("يلغي هذا النظام كل ما يتعارض مع أحكامه"), naming no specific predecessor
law. (The enacting CoM Resolution 25's preamble DOES revoke three prior CoM
resolutions about Civil Defense Council membership/composition -- administrative
instruments, not substantive predecessor laws -- preserved verbatim in
preamble_ar only.)

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; space-before-punctuation and double/nbsp spaces removed --
display-layer only, no legal text altered. Decorative kashida in هـ/جـ
preserved. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_defense", "law", "official_source",
                   "civil_defense_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "civil_defense", "law", "verified")
RECORDS = os.path.join(OUT_VER, "civil_defense_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "civil_defense_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "civil_defense_arabic_legal_llm",
                        "civil_defense_law_legal_llm_001_036.json")

LAW_ID = "sa-civil-defense-law-m-10-1406"
LAW_AR = "نظام الدفاع المدني"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_UNCONFIRMED = "AMENDED_CURRENT_TEXT_UNCONFIRMED"
KEY_RE = r"civil_defense_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {
    "civil_defense_law_art_005",
    "civil_defense_law_art_028",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم مجلس الدفاع المدني وزير الداخلية").split())


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
        return STATUS_AMENDED_UNCONFIRMED
    return STATUS_UNCHANGED


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa HAS a dedicated lawId page for this law "
            "(f09eda85-7150-4803-b87a-a9a700f189f3) and istitlaa.ncc.gov.sa HAS dedicated "
            "per-article pages (Military/998) but BOTH were unreachable this pass (HTTP 503; "
            "web.archive.org environment-blocked and NOT bypassed). ORIGINAL 1406H full text "
            "(all 36 articles) is cross-verified verbatim between mohamah.net and "
            "islamport.com (independent, non-derivative sources) -> TIER_3 for the base text. "
            "Articles 5 and 28 are KNOWN to have been amended (Royal Decrees M/63 13/9/1436H "
            "and M/66 2/10/1424H respectively, per saudipedia.com citing the Bureau of "
            "Experts) but the CURRENT verbatim replacement text could NOT be confirmed from "
            "any reachable source this pass -- the `text` field for these two articles stores "
            "ONLY the confirmed ORIGINAL 1406H wording, flagged legal_status_ar=معدلة, NOT a "
            "fabricated current text. saudipedia.com further states 'the majority of the law's "
            "articles were amended on various dates' -- the true amendment scope across four "
            "decades likely EXCEEDS what could be confirmed here; see "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance, especially for "
            "articles 5 and 28.")

SRC_AUTH = ("Royal Decree M/10 (10/5/1406H), CoM Resolution 25 (23/1/1406H). Original full "
            "text from mohamah.net cross-checked verbatim against islamport.com (independent, "
            "non-derivative) -> TIER_3. Known amendments (Royal Decree M/66 2/10/1424H "
            "touching at least Article 28; Royal Decree M/63 13/9/1436H touching at least "
            "Article 5) confirmed to EXIST via saudipedia.com (citing the Bureau of Experts) "
            "and multiple independent web searches, but their verbatim CURRENT text could NOT "
            "be confirmed this pass (BOE/istitlaa unreachable; specific Umm al-Qura decree "
            "pages unresolved) -- original 1406H text preserved, NOT fabricated as current.")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/10 وتاريخ 10/5/1406هـ، وقرار مجلس الوزراء رقم 25 وتاريخ "
               "23/1/1406هـ. النص الأصلي الكامل من mohamah.net متقاطع حرفيا مع islamport.com "
               "(مصدر مستقل غير مشتق) -- TIER_3. التعديلات المؤكدة الوجود (المرسوم الملكي "
               "م/66 وتاريخ 2/10/1424هـ يمس المادة الثامنة والعشرين على الأقل؛ والمرسوم "
               "الملكي م/63 وتاريخ 13/9/1436هـ يمس المادة الخامسة على الأقل) مؤكدة عبر "
               "سعوديبيديا (تستشهد بهيئة الخبراء) وبحث ويب مستقل متعدد، لكن نصها الحرفي "
               "الحالي تعذر تأكيده هذه الجولة (BOE واستطلاع غير قابلين للوصول؛ صفحات أم "
               "القرى المحددة لم يتيسر تحديد رابطها) -- النص الأصلي لعام 1406هـ محفوظ، غير "
               "ملفق كنص حالي.")


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
        ver.append({"law_key": "civil_defense", "law_component": "law",
                    "language": "ar",
                    "record_layer": "CIVIL_DEFENSE_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "civil-defense-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "civil_defense/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الدفاع المدني" % a["number_label_ar"]],
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
    json.dump({"law_key": "civil_defense",
               "layer": "CIVIL_DEFENSE_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-civil-defense-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (36 مادة؛ 34 أصلية، 2 معدلة نصها الحالي غير مؤكد)",
               "title_en": ("Civil Defense Law — Arabic LLM-ready layer "
                            "(36 records: 34 original, 2 known-amended with unconfirmed "
                            "current text)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 36], "text_status": STATUS_AMENDED_UNCONFIRMED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Civil Defense Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
