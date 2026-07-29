#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Road Transport Law track (نظام النقل البري على
الطرق, Royal Decree M/188, 24/8/1446H (23 February 2025) -- the currently
in-force Road Transport Law, administered by the General Authority for
Transport (TGA, تنظيم الهيئة العامة للنقل)).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام النقل البري على الطرق is a single,
self-standing Royal-Decree law (M/188, 24/8/1446H), published in Umm Al-Qura
Gazette Issue (5073), 28 February 2025. Unlike several other tracks in this
corpus, the OFFICIAL Umm Al-Qura Gazette portal itself (uqn.gov.sa/details?
p=27037) was reached LIVE this pass (curl, HTTP 200, ~818KB page) and its own
"article-content" body contains the Law's full 34 articles verbatim, along
with page metadata ("1446-8-29 / 28-02-2025") matching this pass's task brief
exactly (Issue 5073, 28 Feb 2025). This is a genuine PRIMARY government
source -- the Gazette's own publication portal, not a secondary aggregator
and not a wayback snapshot.

laws.boe.gov.sa (this corpus's other usual primary source) was checked FIRST
per standard methodology: a dedicated WebSearch for
"site:laws.boe.gov.sa نظام النقل البري على الطرق" returned no dedicated lawId
page for this specific, very recently published (Feb 2025) law -- only
related transport-sector laws (Railway Law, Traffic Law, National Center for
Transport Safety, road-construction-by-individuals regulation, General
Transport Authority's own establishing regulation). Direct curl attempts
against both a BOE search endpoint and the bare domain both returned
"Connection reset by peer", matching this corpus's well-documented BOE-
unreachability pattern this session. tga.gov.sa (TGA's own regulations page,
located via WebSearch at /ar/Regulations/Regulation/4711) was also attempted
directly but is likewise unreachable this pass (curl: connection reset;
WebFetch: HTTP 503).

Per this pass's fallback instructions, the uqn.gov.sa text was cross-verified
article-by-article (all 34 articles, via a Python diff after full Unicode
normalization: Eastern->Western digits, tashkeel/tanween stripped, RLM marks
removed, dash-style and thousands-separator variants unified) against TWO
independent secondary sources: qanoonsa.com (three pages: the 34-article Law,
the enacting Royal Decree M/188 itself, and Council of Ministers Resolution
614 itself) and nezams.com (one page containing the Law's full text, an
independent metadata table, the Royal Decree's full text, and the CoM
Resolution's full text). All 34 articles matched byte-for-byte after
normalization across all three sources -- zero substantive differences; only
five purely cosmetic patterns (digit script, RLM-driven spacing around
em-dashes, thousands-separator convention, Arabic vs. Latin percent sign, and
a qanoonsa.com-added footer line after Article 34) were found and fully
resolved (see known_unresolved_discrepancies).

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT: Article 33 (the last
substantive Article before the closing publication Article 34) states
verbatim: "يحل النظام محل نظام النقل العام على الطرق بالمملكة العربية
السعودية، الصادر بالمرسوم الملكي رقم (م/25) وتاريخ 21/6/1397هـ، ويلغي جميع ما
يتعارض معه." This matches this corpus's contractors_classification_law
pattern (repeal inside a numbered Article), NOT its railway_law pattern
(repeal only in the enacting decree's own clause) -- neither the enacting
Royal Decree (M/188) nor CoM Resolution 614 that preceded it mentions the
repealed predecessor (M/25, 1397H) anywhere in their own text.

The enacting Royal Decree (M/188) itself additionally carries several
transitional/substantive provisions in its OWN clauses (Second through
Fifth) that are NOT inside any of the Law's 34 numbered Articles: an Aramco
hydrocarbon-transport concession carve-out; a one-year (extendable +6 months)
transitional compliance period for existing transport establishments; a
rail/maritime-fare-setting power for TGA's Board (mirroring, for different
sectors, Article 18 of the Law itself); and an exception for unlicensed
foreign trucks, penalized from the Law's publication date itself rather than
after the normal 180-day deferred effective date in Article 34. These are
recorded in preamble_ar/issuing_authority_ar, not in any articles record.

VERIFICATION TIER -- TIER_2. Exactly ONE official/primary source
(uqn.gov.sa, the Official Gazette's own live portal) was reached and used as
the governing text for all 34 articles, cross-verified article-by-article
against two independent secondary sources (qanoonsa.com, nezams.com) with
full agreement after normalization. laws.boe.gov.sa was checked FIRST per
standard methodology but has no dedicated page for this brand-new law and is
itself unreachable this pass; tga.gov.sa (TGA's own regulations page) was
also attempted and is unreachable this pass. Because no SECOND official/
primary source was reached (TIER_1 requires 2+ independently-produced
official sources, and never counts a private aggregator as one of the two
required legs), this track is TIER_2, not TIER_1.

34 articles, NO فصل/باب chapter structure in the source text itself (a
directly-numbered law running straight from Article 1 to Article 34, exactly
like this corpus's contractors_classification_law); all 34 اصلية; 0 معدلة, 0
ملغاة, 0 مضافة. Diacritics (tashkeel, incl. tanween and shadda) are stripped
uniformly and digits normalized to Western, consistent with this corpus's
other tracks; the single genuine tatweel character in the source (the "هـ"
Hijri-year abbreviation in Article 33) is preserved, not stripped.

IMPLEMENTING REGULATIONS -- OUT OF SCOPE this pass by explicit task
instruction. Article 32 requires TGA's Board to issue "اللوائح" (plural)
within 180 days of publication; per this pass's task brief this is actually a
large, not-yet-clearly-scoped cluster of 6-8+ activity-specific TGA
regulations (bus, taxi, specialized transport, school transport, heavy
freight, car rental, delivery) plus a separate Public Transport Users'
Rights Regulation -- none of these were researched or ingested this pass;
flagged as a follow-up candidate cluster requiring its own dedicated research
pass first to even enumerate them accurately.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "road_transport_law", "law", "official_source",
                   "road_transport_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "road_transport_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "road_transport_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "road_transport_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "road_transport_law_arabic_legal_llm",
                        "road_transport_law_legal_llm_001_034.json")

LAW_ID = "sa-road-transport-law-m188-1446"
LAW_AR = "نظام النقل البري على الطرق"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"road_transport_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس النقل البري الطرق").split())


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
        ver.append({"law_key": "road_transport_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ROAD_TRANSPORT_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Road Transport Law (Royal Decree M/188, 24/8/1446H "
                                              "/ 23 Feb 2025), a brand-new base-law track built "
                                              "from scratch this pass (not previously in this "
                                              "corpus). Article 33 OF THE LAW ITSELF states it "
                                              "replaces the prior General Road Transport Law "
                                              "(M/25, 21/6/1397H). Text fetched directly LIVE from "
                                              "uqn.gov.sa (the Official Umm Al-Qura Gazette's own "
                                              "portal, HTTP 200) and cross-verified article-by-"
                                              "article against two independent secondary sources "
                                              "(qanoonsa.com, nezams.com) with full agreement after "
                                              "Unicode normalization. laws.boe.gov.sa was checked "
                                              "FIRST per standard methodology but has no dedicated "
                                              "page for this brand-new law and is itself "
                                              "unreachable this pass; tga.gov.sa was also attempted "
                                              "and is unreachable this pass. TIER_2. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably "
                                              "that Implementing Regulations (a large, not-yet-"
                                              "scoped cluster of activity-specific TGA regulations) "
                                              "are explicitly OUT OF SCOPE this pass."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "road-transport-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "road_transport_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام النقل البري على الطرق" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/188), 24/8/1446H "
                                                          "(Council of Ministers Resolution 614, "
                                                          "19/8/1446H; Shura Council Resolutions "
                                                          "69/8, 110/11, 183/18) — the currently "
                                                          "in-force Road Transport Law, published "
                                                          "in Umm Al-Qura Gazette Issue 5073 (28 "
                                                          "Feb 2025). By its own Article 33 -- not "
                                                          "the enacting decree -- it replaces the "
                                                          "prior General Road Transport Law (M/25, "
                                                          "21/6/1397H). Verbatim text fetched "
                                                          "directly LIVE from uqn.gov.sa (the "
                                                          "Official Gazette's own portal) and "
                                                          "cross-verified article-by-article "
                                                          "against qanoonsa.com and nezams.com. "
                                                          "laws.boe.gov.sa has no dedicated page "
                                                          "for this brand-new law and is itself "
                                                          "unreachable this pass; tga.gov.sa also "
                                                          "unreachable. TIER_2."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/188) وتاريخ 24/8/1446هـ (قرار مجلس الوزراء رقم (614) وتاريخ 19/8/1446هـ؛ قرارات مجلس الشورى 69/8، 110/11، 183/18) — نظام النقل البري على الطرق النافذ حاليا، المنشور في جريدة أم القرى، العدد (5073)، بتاريخ 28 فبراير 2025م. يحل -بنص المادة الثالثة والثلاثين منه ذاتها، لا بنص مرسوم الإصدار- محل نظام النقل العام على الطرق السابق (م/25، 21/6/1397هـ). النص الحرفي جُلب مباشرة وحيا من uqn.gov.sa (بوابة جريدة أم القرى الرسمية ذاتها) وتحقق منه مادة مادة مقابل qanoonsa.com وnezams.com. laws.boe.gov.sa لا يملك صفحة مخصصة لهذا النظام حديث النشر وهو ذاته غير قابل للوصول هذه الجولة؛ tga.gov.sa أيضا غير قابل للوصول. المستوى TIER_2.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "road_transport_law",
               "layer": "ROAD_TRANSPORT_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-road-transport-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (34 مادة؛ 34 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Saudi Arabian Road Transport Law (Royal Decree M/188, "
                            "24/8/1446H) — Arabic LLM-ready layer (34 records: 34 original, 0 "
                            "amended, 0 added, 0 repealed; no chapter structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 34], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Road Transport Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
