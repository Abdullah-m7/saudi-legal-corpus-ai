#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Law of Associations and Civil Institutions track
(نظام الجمعيات والمؤسسات الأهلية, Royal Decree M/8, 19/2/1437H / ~2015G).

VERIFICATION TIER -- see sources/associations_ngo/law/official_source/
associations_ngo_law_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa indexing shows TWO
different lawId values for this law's name (37e0768f-8e3c-493a-b951-a9a700f2bbb1
and b97fcccb-3c26-4fe2-9c61-a9a700f2bc4e; which one is the live canonical
record could not be determined without live access) and the live portal
returned HTTP 503 (WebFetch) / HTTP 000 connection-reset (direct curl), across
several attempts. web.archive.org was NOT attempted (organization egress-policy
block on that host for this session, documented across this corpus and never
bypassed).

SOURCES USED (TIER_3):
  * PRIMARY full text (all 44 articles): nezams.com (independent legal
    aggregator), fetched directly (HTTP 200), exactly 44 "subject" elements
    subject-1..subject-44.
  * INDEPENDENT cross-check: a PDF hosted by menarights.org ("KSA_Law on
    NGOs 2015"), fetched directly (HTTP 200) and OCR/text-extracted via
    pdftotext -- independently confirmed the article count (44), the verbatim
    text of the closing articles (42: 90-day implementing-regulation mandate;
    43: named repeal of the predecessor Charitable Associations and
    Institutions Regulation; 44: 90-day effective date), the preamble/CoM
    Resolution (61), and spot-checked mid-document articles (5, 8, 11, 30, 35,
    39, 41). The BOE portal's own search-index snippets separately confirmed
    the decree identity (M/8, 19/2/1437H) and substantive provisions (no
    seizure of public-benefit-association funds without a judicial ruling;
    expropriation right for public benefit).

Because full live/archived access to the canonical BOE portal page could not
be obtained this pass (with no policy bypass attempted), this track is
honestly kept at TIER_3 -- not TIER_1/TIER_2 -- despite two independent
corroborating sources for the full text.

44 records: 43 اصلية, 1 معدلة (article 1 only), 0 ملغاة, 0 مضافة. The statute
has NO division into chapters/أبواب/فصول (flat, confirmed by both sources);
19 of the 44 articles carry their own internal subject heading in the source
(stored in section_ar), the rest have none (section_ar == "").

Article 1 is the ONLY article classified معدلة: Council of Ministers
Resolution No. 618 (20/10/1442H) inserted two NEW definitions into Article 1
("المركز": the National Center for the Non-Profit Sector; "المجلس": the
Center's board) alongside the original defined terms -- a distinct textual
addition, preserved in history[]. Resolution 618 ALSO horizontally substitutes
"the Center"/"the Board" for "the Ministry"/"the Minister" throughout the
statute EXCEPT in Articles 7, 25 and 38 (which are explicitly exempted and
carry a source note to that effect) -- this repo-wide substitution is recorded
in known_unresolved_discrepancies rather than rewritten into each affected
article's stored text, so no other article is marked معدلة for it: the bodies
of all other articles remain exactly as published (الوزارة/الوزير), per this
corpus's no-silent-rewrite rule.

NAMED PREDECESSOR REPEAL: Article 43 EXPLICITLY repeals the "Charitable
Associations and Institutions Regulation" (لائحة الجمعيات والمؤسسات الخيرية),
Council of Ministers Resolution No. 107 (25/6/1410H), plus a general residual
conflict clause. This is a genuine, precisely-named repeal link -- unlike
child_protection_law/protection_from_abuse_law (both founding statutes with NO
repeal clause) -- and is flagged for the corpus-wide supersession/repeal graph
(the repealed 1410H regulation is not itself ingested as a separate track).

Implementing Regulation (Ministerial Resolution No. 73739, 11/6/1437H) is OUT
OF SCOPE for this track (one-instrument-per-pass rule) -- flagged as a
documented follow-up candidate.

TASHKEEL stripped uniformly (corpus-majority convention); in-word decorative
kashida removed (Hijri-era marker هـ and the two enumeration letters هـ/جـ
preserved); curly quotes straightened -- display-layer only, no legal text
altered. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "associations_ngo", "law", "official_source",
                   "associations_ngo_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "associations_ngo", "law", "verified")
RECORDS = os.path.join(OUT_VER, "associations_ngo_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "associations_ngo_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "associations_ngo_arabic_legal_llm",
                        "associations_ngo_law_legal_llm_001_044.json")

LAW_ID = "sa-associations-ngo-law-m-8-1437"
LAW_AR = "نظام الجمعيات والمؤسسات الأهلية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"associations_ngo_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {"associations_ngo_law_art_001"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات").split())


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


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa indexing shows two different lawId values for "
            "this law's name (37e0768f-8e3c-493a-b951-a9a700f2bbb1 and "
            "b97fcccb-3c26-4fe2-9c61-a9a700f2bc4e), and the live portal was unreachable this "
            "pass (HTTP 503 / connection reset; web.archive.org egress-blocked and NOT "
            "bypassed). PRIMARY full text is from nezams.com, independently cross-checked "
            "against a menarights.org PDF (KSA_Law on NGOs 2015) for article count, closing "
            "articles' verbatim text, the preamble, and mid-document spot-checks -> TIER_3. "
            "44 articles, flat (no chapters); Article 1 only is معدلة (Resolution 618 inserted "
            "two new definitions); Articles 7/25/38 are explicitly EXEMPTED from Resolution "
            "618's horizontal الوزارة/الوزير->المركز/المجلس substitution and remain اصلية. "
            "Article 43 EXPLICITLY repeals the predecessor Charitable Associations and "
            "Institutions Regulation (CoM Resolution 107, 25/6/1410H) -- a genuine named "
            "repeal, flagged for the corpus-wide supersession graph. See "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/8 (19/2/1437H), CoM Resolution 61 (18/2/1437H), published Umm "
            "al-Qura 7/3/1437H; amended by CoM Resolution 618 (20/10/1442H, definitions + "
            "horizontal substitution except arts 7/25/38) and CoM Resolution 367 (29/6/1443H, "
            "competent-authority designation in the enacting resolution's annex). Full text "
            "from nezams.com, independently cross-checked against a menarights.org PDF "
            "(KSA_Law on NGOs 2015) and BOE portal search-index snippets. laws.boe.gov.sa's "
            "own indexing shows two conflicting lawId values for this law's name; live portal "
            "access failed this pass (HTTP 503; Wayback egress-blocked, not bypassed) -> "
            "TIER_3")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/8 وتاريخ 19/2/1437هـ، وقرار مجلس الوزراء رقم 61 وتاريخ "
               "18/2/1437هـ (منشور بأم القرى 7/3/1437هـ)؛ عُدل بقرار مجلس الوزراء رقم 618 وتاريخ "
               "20/10/1442هـ (تعريفان جديدان + إحلال أفقي عدا المواد 7 و25 و38) وقرار مجلس "
               "الوزراء رقم 367 وتاريخ 29/6/1443هـ (تحديد الجهة المختصة في ملحق قرار الإصدار). "
               "النص الكامل من nezams.com، متحقق منه مستقلا عبر ملف PDF بمنظمة menarights.org "
               "وفهرسة بوابة هيئة الخبراء. فهرسة laws.boe.gov.sa نفسها تعرض رقمي lawId مختلفين "
               "لاسم هذا النظام؛ تعذر الوصول الحي هذه الجولة (503؛ لقطة Wayback محظورة ولم "
               "تُتجاوَز) -- TIER_3")


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
        ver.append({"law_key": "associations_ngo", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ASSOCIATIONS_NGO_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "associations-ngo-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "associations_ngo/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الجمعيات والمؤسسات الأهلية" % a["number_label_ar"]],
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
    json.dump({"law_key": "associations_ngo",
               "layer": "ASSOCIATIONS_NGO_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-associations-ngo-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (44 مادة؛ 43 أصلية، 1 معدلة)",
               "title_en": ("Law of Associations and Civil Institutions — Arabic LLM-ready "
                            "layer (44 records: 43 original, 1 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 44], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Associations/NGO Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
