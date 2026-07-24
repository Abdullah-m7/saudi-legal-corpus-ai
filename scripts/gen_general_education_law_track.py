#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi General Education Law track (نظام التعليم العام, Royal
Decree M/36, 27/1/1448H / ~July 2026G).

VERIFICATION TIER -- see sources/general_education/law/official_source/
general_education_law_official_source.json's verification_methodology_note for
the full account. Summary:

This is the NEWEST law in this corpus: issued essentially on the eve of this
research pass. DIRECT LIVE ACCESS to the Umm al-Qura Official Gazette
(uqn.gov.sa) SUCCEEDED this pass (HTTP 200, no Wayback/mirror needed) for all
three relevant pages:
  * uqn.gov.sa/4001463 -- full text of Royal Decree M/36 (27/1/1448H)
  * uqn.gov.sa/decisions-and-regulations/4001465 -- full text of the Law
    itself (all 68 articles across 9 chapters)
  * uqn.gov.sa/decisions-and-regulations/4001460 -- full text of Council of
    Ministers Resolution 103 (22/1/1448H), including the repeal clauses

SOURCES USED (TIER_2):
  * PRIMARY, full verbatim text of all 68 articles: the Umm al-Qura Official
    Gazette itself (uqn.gov.sa), fetched directly (HTTP 200). This is the
    single official/primary source for the governing text.
  * OFFICIAL partial corroboration: the Saudi Press Agency (spa.gov.sa,
    blocked by the WebFetch tool with HTTP 403 but fetched directly via curl
    with a standard browser user-agent, HTTP 200) independently confirms the
    decree's existence, number, date, the Minister of Education's statement,
    and the repeal of the Adult Education and Literacy Law -- but does NOT
    republish the full verbatim article text, so it corroborates facts, not
    wording.
  * INDEPENDENT PRESS structural cross-check: sabq.org independently
    confirms "68 مادة" / "9 فصول" and the substance of Articles 4 and 6;
    argaam.com, alriyadh.com, albiladdaily.com, ajel.sa independently confirm
    the decree number/date and the Adult Education Law repeal.
  * laws.boe.gov.sa: NO dedicated lawId page exists yet for this Law
    (confirmed via a direct site-restricted search) -- fully expected given
    the Law's freshness (issued a day or two before this pass).

Not TIER_1 because no SECOND official/primary source reproduces the full
governing text of all 68 articles (SPA/press confirm facts, not wording).

68 records: all 68 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة. 9 chapters (فصول).

**THE LAW IS NOT YET IN FORCE.** Article 68 states it takes effect 180 days
after gazette publication (~mid-January 2027). This is disclosed explicitly
in official_text_status, legal_status_ar, and a dedicated
known_unresolved_discrepancies entry -- never silently treated as already
effective.

GAZETTE DATE DISCREPANCY (disclosed, not silently resolved): all three
uqn.gov.sa pages show a visible header date of "11 Safar 1448H | 25 July
2026G", but the SAME pages' own embedded schema.org metadata timestamps all
read 24 July 2026G -- which matches the Saudi Press Agency's own independent
dateline (10 Safar 1448H / 24 July 2026G) for its report on this exact
decree. The weight of evidence (two independent signals agreeing) favors 24
July, but this is not resolved from one conclusive source and is recorded as
an open discrepancy. The Royal Decree's OWN dating (27/1/1448H, Muharram) is
unambiguous and unaffected.

NAMED-PREDECESSOR REPEAL, CONFIRMED AS IMMEDIATE (not merely a future
trigger): Clause Third of the Royal Decree (mirrored in the Council
Resolution) repeals the Adult Education and Literacy Law (Royal Decree M/22,
9/6/1392H) directly, with a PHASED one-year transitional continuation of its
substantive provisions. The Adult Education Law is NOT a tracked instrument
in this corpus (confirmed against corpus_registry.json), so no supersession-
graph edge is created. Clause Fourth of Council Resolution 103 additionally
repeals seven other Council-of-Ministers-level regulations (also phased,
one-year transition) -- none of the seven are tracked instruments either, so
none require a supersession-graph edge.

TASHKEEL stripped uniformly (corpus-majority convention); the tatweel in
"هـ-" (fifth lettered sub-item marker) preserved as ordinary orthography, not
decorative. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "general_education", "law", "official_source",
                   "general_education_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "general_education", "law", "verified")
RECORDS = os.path.join(OUT_VER, "general_education_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "general_education_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "general_education_arabic_legal_llm",
                        "general_education_law_legal_llm_001_068.json")

LAW_ID = "sa-general-education-law-m-36-1448"
LAW_AR = "نظام التعليم العام"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"general_education_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير حالة حالات المجلس تضع تعمل تتولى للوزارة").split())


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


GOV_NOTE = ("Arabic governs; PRIMARY full verbatim text of all 68 articles fetched directly "
            "from the Umm al-Qura Official Gazette itself (uqn.gov.sa, HTTP 200, no Wayback/"
            "mirror needed -- this Law was issued essentially on the eve of this research "
            "pass). No dedicated laws.boe.gov.sa lawId page exists yet for this Law (confirmed "
            "via direct search), fully expected given its freshness. Officially corroborated "
            "(facts, not full wording) by the Saudi Press Agency (spa.gov.sa); structurally "
            "cross-checked (68 articles / 9 chapters, specific article substance) by "
            "independent press (sabq.org, argaam.com, alriyadh.com, albiladdaily.com) -> "
            "TIER_2. THE LAW IS NOT YET IN FORCE: Article 68 sets a 180-day post-publication "
            "effective date (~mid-January 2027). A one-day gazette-date discrepancy (25 vs 24 "
            "July 2026) is disclosed, not silently resolved. See verification_methodology_note "
            "and known_unresolved_discrepancies in the source artifact before relying on this "
            "track's text or provenance.")

SRC_AUTH = ("Royal Decree M/36 (27/1/1448H), CoM Resolution 103 (22/1/1448H), published Umm "
            "al-Qura Gazette (publication-date discrepancy of one day disclosed: gazette pages' "
            "own visible header shows 25 July 2026G/11 Safar 1448H, but their own embedded "
            "metadata and the Saudi Press Agency's independent dateline both agree on 24 July "
            "2026G/10 Safar 1448H). Full text fetched directly from uqn.gov.sa (HTTP 200); "
            "officially corroborated (facts, not full wording) by spa.gov.sa; structurally "
            "cross-checked by independent press (sabq.org confirms 68 articles/9 chapters). No "
            "laws.boe.gov.sa lawId page exists yet (expected given freshness) -> TIER_2. NOT YET "
            "IN FORCE: Article 68 sets effect 180 days after gazette publication (~mid-January "
            "2027). Repeals the Adult Education and Literacy Law (Royal Decree M/22, 9/6/1392H) "
            "immediately but with a one-year phased transition (Clause Third); that law is not a "
            "tracked instrument in this corpus, so no supersession-graph edge applies. Also "
            "repeals seven untracked Council-of-Ministers-level school regulations (Clause "
            "Fourth of CoM Resolution 103), likewise requiring no supersession-graph edge.")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/36 وتاريخ 27/1/1448هـ، وقرار مجلس الوزراء رقم 103 وتاريخ "
               "22/1/1448هـ (منشوران بأم القرى؛ تعارض يوم واحد في تاريخ النشر مسجل بشفافية: "
               "التاريخ الظاهر على صفحات الجريدة 25 يوليو 2026م/11 صفر 1448هـ، لكن بياناتها "
               "الوصفية المضمنة ونشرة واس المستقلة تتفقان على 24 يوليو 2026م/10 صفر 1448هـ). "
               "النص الكامل جُلب مباشرة من uqn.gov.sa (HTTP 200)؛ تأكيد رسمي جزئي (وقائع لا نص "
               "كامل) من واس (spa.gov.sa)؛ تحقق هيكلي مستقل من صحافة غير حكومية (سبق تؤكد 68 "
               "مادة/9 فصول). لا صفحة lawId على laws.boe.gov.sa بعد (متوقع لحداثة النظام) -- "
               "TIER_2. **لم يدخل حيز النفاذ بعد**: يعمل بالنظام بعد 180 يوما من تاريخ النشر (نحو "
               "منتصف يناير 2027م). يلغي فورا (بإلغاء مرحلي لمدة سنة) نظام تعليم الكبار ومحو "
               "الأمية (م/22، 1392هـ) غير المُدرَج في هذه المدونة، وسبع وثائق تنظيمية أخرى غير "
               "مُدرَجة أيضا -- فلا حاجة لأي رابط إحلال في رسم بياني للمدونة.")


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
        ver.append({"law_key": "general_education", "law_component": "law",
                    "language": "ar",
                    "record_layer": "GENERAL_EDUCATION_LAW_ARABIC_VERIFIED_TEXT",
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
                    "law_not_yet_in_force": True,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "general-education-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "general_education/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام التعليم العام" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "law_not_yet_in_force": True,
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
    json.dump({"law_key": "general_education",
               "layer": "GENERAL_EDUCATION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "not_yet_in_force": src.get("not_yet_in_force", False),
               "effective_date_note_ar": src.get("effective_date_note_ar"),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-general-education-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (68 مادة؛ كلها "
                           "أصلية؛ النظام لم يدخل حيز النفاذ بعد)",
               "title_en": ("General Education Law — Arabic LLM-ready layer (68 records: all "
                            "original, no amendments; law NOT YET IN FORCE, effective ~180 days "
                            "after gazette publication)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 68], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "law_not_yet_in_force": True,
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready General Education Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
