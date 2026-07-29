#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the System for the Management of Seized and Confiscated Funds in
Money-Laundering Crimes, Related Predicate Crimes, and Terrorist-Financing
Crimes track (نظام إدارة الأموال المحجوزة والمصادرة في جرائم غسل الأموال
والجرائم الأصلية المرتبطة بها وجرائم تمويل الإرهاب), issued by Royal Decree
No. (M/1) dated 2/1/1448H (17/6/2026G), based on Council of Ministers
Resolution No. (16) dated 1/1/1448H (16/6/2026G) and Shura Council Resolution
No. (298/24) dated 18/10/1447H, published in the Umm Al-Qura Official Gazette,
Issue No. (5164), dated 3/1/1448H (18/6/2026G) -- a BRAND-NEW instrument, one
of the newest in this corpus (weeks old as of this build pass).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus,
and is DISTINCT from this corpus's pre-existing aml/aml_law and
aml_regulation tracks (neither touched this pass): those govern the
underlying AML/CTF offence and compliance regime, while this track governs
the custody/asset-management of funds ALREADY seized or confiscated in such
cases, administered by the General Authority for the Guardianship of Minors'
and Similarly-Situated Persons' Funds (الهيئة العامة للولاية على أموال
القاصرين ومن في حكمهم), coordinating with the Ministry of Finance and the
competent courts.

VERIFICATION TIER -- see this track's own official_source.json for the full
account (verification_methodology_note / known_unresolved_discrepancies).
Summary:

TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. One official/primary source
was reached directly this pass: the Umm Al-Qura Official Gazette's own live
page (https://www.uqn.gov.sa/decisions-and-regulations/4001359), fetched
successfully twice independently (via WebFetch and via direct curl with full
browser headers, both HTTP 200), reproducing the full verbatim text of all
15 articles plus the System's title, CoM Resolution number/date, and Gazette
issue number/date. No second independent OFFICIAL source could be reached
this pass: laws.boe.gov.sa (this corpus's usual primary source) returned a
connection reset; wilayah.gov.sa (the administering authority's own site)
does not yet appear to host this brand-new system and also returned a
connection reset on direct access.

Additional independent triangulation: three separate pages on qanoonsa.com
(an independent, non-governmental secondary aggregator) were fetched
directly via curl (HTTP 200 each): the Royal Decree M/1 text
(qanoonsa.com/p/516401/), the Council of Ministers Resolution 16 text
(qanoonsa.com/p/516402/), and the System's own full 15-article text
(qanoonsa.com/p/516403/). The qanoonsa.com system-text page matches the
uqn.gov.sa page word-for-word for every article's substantive content, with
ONE disclosed exception: the uqn.gov.sa page carries an explicit official
notice ("تنويه") stating it presents an amended/corrected version following
a correction received by the Gazette, dated 25/1/1448H (10/7/2026G) --
approximately three weeks after the original 18/6/2026G publication that
qanoonsa.com's system-text page (dated 17/6/2026G) mirrors. The only actual
difference between the two orderings is that the "confiscated funds to
treasury" article (Article 14 in the original ordering) was moved to
Article 11 in the amended/current ordering, with the following three
articles (confidential information, termination of the Authority's task,
issuance of the Implementing Regulation) shifting from originally being
Articles 11-13 to now being Articles 12-14. No article's substantive wording
changed between the two orderings -- only positional numbering. This track
stores the CURRENT (post-renumbering) ordering as displayed live on
uqn.gov.sa as of this build pass. See known_unresolved_discrepancies in the
source artifact for the full account, including a correction of this
track's own commissioning brief's approximate Gregorian date equivalence.

15 articles, no chapters/فصول (a flat, single-block statute); all 15 اصلية
(single edition, only a disclosed pure renumbering, no substantive
amendment). Diacritics (tashkeel) are stripped uniformly from article
bodies, consistent with this corpus's convention. One digit-script variance
is deliberately preserved, not silently normalized: Article 8 paragraph 3
uses Arabic-Indic "٣٠" (matching identically on both uqn.gov.sa and
qanoonsa.com), while the rest of the System uses Western digits (e.g. "10%"
in Articles 10 and 11).

NOT YET IN FORCE -- Article 15 provides the System takes effect 90 days
after its Gazette-publication date (18/6/2026G), i.e. around 16/9/2026G, a
date still in the future as of this track's build date (2026-07-28). The
Authority's Board must issue the Implementing Regulation within 90 days of
gazette publication (Article 14); none was found this pass, consistent with
that deadline not yet having elapsed. Council of Ministers Resolution 16's
own clause "Secondly" additionally establishes a standing inter-ministerial
oversight committee -- a mechanism created by the CoM Resolution itself, not
one of the System's own 15 articles, and therefore not ingested as an
article.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "seized_confiscated_funds_management_system", "law",
                   "official_source", "seized_confiscated_funds_management_system_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "seized_confiscated_funds_management_system", "law", "verified")
RECORDS = os.path.join(OUT_VER, "seized_confiscated_funds_management_system_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "seized_confiscated_funds_management_system_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "seized_confiscated_funds_management_system_arabic_legal_llm",
                        "seized_confiscated_funds_management_system_legal_llm_001_015.json")

LAW_ID = "sa-seized-confiscated-funds-management-system-m1-1448"
LAW_AR = "نظام إدارة الأموال المحجوزة والمصادرة في جرائم غسل الأموال والجرائم الأصلية المرتبطة بها وجرائم تمويل الإرهاب"
STATUS = "UQN_GAZETTE_LIVE_HTML_PRIMARY_QANOONSA_TRIPLE_PAGE_CROSSVERIFIED_ARTICLE_RENUMBERING_DISCLOSED"
KEY_RE = r"seized_confiscated_funds_management_system_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس بذلك تلك").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        text = a["text"]
        section = a.get("section_ar", "")
        ver.append({"law_key": "seized_confiscated_funds_management_system", "law_component": "law",
                    "language": "ar",
                    "record_layer": "SEIZED_CONFISCATED_FUNDS_MANAGEMENT_SYSTEM_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the Umm "
                                              "Al-Qura Official Gazette's own live page "
                                              "(uqn.gov.sa/decisions-and-regulations/"
                                              "4001359), cross-checked against three "
                                              "independent qanoonsa.com pages (Royal "
                                              "Decree M/1, CoM Resolution 16, and the "
                                              "System's own full text). One disclosed, "
                                              "purely positional renumbering (not a "
                                              "substantive text change) was found between "
                                              "the original 18/6/2026G gazette publication "
                                              "(mirrored by qanoonsa.com) and the current "
                                              "live uqn.gov.sa page, which carries its own "
                                              "explicit amendment notice dated "
                                              "25/1/1448H -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact before relying on this "
                                              "track's article numbering. laws.boe.gov.sa "
                                              "and wilayah.gov.sa (the administering "
                                              "authority's own site) were both "
                                              "unreachable this pass. "
                                              "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. "
                                              "The System is issued but NOT YET IN FORCE "
                                              "(takes effect 90 days after its "
                                              "18/6/2026G gazette publication, i.e. "
                                              "around 16/9/2026G)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "text_complete": a.get("text_complete", True),
                    "record_id": "seized-confiscated-funds-management-system-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "seized_confiscated_funds_management_system/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام إدارة الأموال المحجوزة والمصادرة"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree No. (M/1), "
                                                          "2/1/1448H (17/6/2026G), on "
                                                          "Council of Ministers "
                                                          "Resolution No. (16), "
                                                          "1/1/1448H (16/6/2026G) -- "
                                                          "cross-verified via the Umm "
                                                          "Al-Qura Official Gazette's own "
                                                          "live page (uqn.gov.sa, entry "
                                                          "4001359) and three independent "
                                                          "qanoonsa.com pages. One "
                                                          "disclosed article-renumbering "
                                                          "correction (no substantive "
                                                          "text change) -- see source "
                                                          "artifact. "
                                                          "TIER_2_PRIMARY_SECONDARY_"
                                                          "CROSS_VERIFIED. Not yet in "
                                                          "force (effective ~16/9/2026G)."),
                                     "source_authority_ar": ("المرسوم الملكي رقم (م/1) "
                                                            "وتاريخ 2/1/1448هـ (الموافق "
                                                            "17/6/2026م)، بناء على قرار "
                                                            "مجلس الوزراء رقم (16) وتاريخ "
                                                            "1/1/1448هـ -- تم التحقق عبر "
                                                            "صفحة جريدة أم القرى الحية "
                                                            "(uqn.gov.sa، السجل 4001359) "
                                                            "وثلاث صفحات مستقلة على "
                                                            "qanoonsa.com. تعديل ترقيمي "
                                                            "واحد مفصح عنه (بلا تغيير "
                                                            "جوهري في النص) -- انظر ملف "
                                                            "المصدر. المستوى "
                                                            "TIER_2_PRIMARY_SECONDARY_"
                                                            "CROSS_VERIFIED. غير ساري "
                                                            "بعد (ينفذ نحو 16/9/2026م)."),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "seized_confiscated_funds_management_system",
               "layer": "SEIZED_CONFISCATED_FUNDS_MANAGEMENT_SYSTEM_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src.get("chapter_structure", []),
               "amendment_history": src.get("amendment_history", []),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-seized-confiscated-funds-management-system-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة، "
                           "اصلية جميعها؛ صادر وغير ساري بعد)",
               "title_en": ("System for the Management of Seized and Confiscated Funds in "
                            "Money-Laundering Crimes, Related Predicate Crimes, and "
                            "Terrorist-Financing Crimes — Arabic LLM-ready layer (15 "
                            "records, all original/اصلية; issued but not yet in force)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Seized/Confiscated Funds Management System records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
