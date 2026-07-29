#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Real Estate Contributions Law track
(اللائحة التنفيذية لنظام المساهمات العقارية, REGA Board of Directors Resolution
(by circulation) No. (Q/M/E/H/2024/1/T), 18/07/1445H, published in the Umm
Al-Qura Official Gazette 06/08/1445H -- the currently in-force implementing
regulation of this corpus's existing real_estate_contributions_law track).

BRAND-NEW REGULATION TRACK -- this instrument was NOT previously in this corpus.
The parent law's own build flagged it explicitly as a follow-up candidate
(known_unresolved_discrepancies key
real_estate_contributions_law_implementing_regulation_not_ingested) because its
precise decision number/date and full verbatim text could not be pinned down
last pass. This pass locates and ingests it.

WHICH INSTRUMENT, AND HOW CONFIRMED -- issued pursuant to Article 37 of the Real
Estate Contributions Law (Royal Decree M/203, 28/12/1444H), which requires
REGA's Board to issue the Implementing Regulation in agreement with the Capital
Market Authority (CMA). CMA's agreement is recorded in its own letter No.
(S/24/546/1) dated 10/7/1445H (22/1/2024G), quoted in the Board resolution's own
preamble. Confirmed via FOUR independent channels: (1) rega.gov.sa's own
dedicated regulation page (born-digital HTML, fetched directly via curl,
HTTP 200) -- found under
/الأنظمة-والقرارات/الأنظمة-واللوائح-والأدلة/اللوائح/اللائحة-التنفيذية-لنظام-المساهمات-العقارية/
after an initial /المكتبة/... URL guess returned a soft 404 (HTTP 200 body, but
a Path=/not-found cookie); (2) rega.gov.sa's own hosted, scanned, King's-Board-
signed PDF of the Board resolution + regulation bundle (media/gdnl4nfg/...pdf,
20 pages, image-only -- pdftotext extracted nothing -- read visually
page-by-page in full, including two 400dpi high-resolution crops to confirm the
decision-number digit order and Article 40's exact wording character-by-
character); (3) the Umm Al-Qura Gazette's own website (uqn.gov.sa/details?p=24519,
HTTP 200, born-digital HTML, page metadata datePublished 2024-02-16T14:46:48+03:00);
(4) qanoonsa.com (an independent secondary aggregator, qanoonsa.com/p/502007/,
HTTP 200, reproduces all 40 articles plus a gazette-issue citation footer
'نشر في عدد جريدة أم القرى رقم (5020) الصادر في 16 من فبراير 2024م').

PER-ARTICLE / METADATA CROSS-VERIFICATION -- a scripted, tashkeel-and-digit-
normalized diff was run between channel (1) and channel (4) across all 40
articles and all 6 chapter headers: 37/40 articles matched exactly (aside from
routine dash/tashkeel formatting), 3/40 diverge substantively between the
{rega.gov.sa page, rega.gov.sa signed PDF} pair and the {uqn.gov.sa Gazette,
qanoonsa.com} pair -- ALL THREE are disclosed in full, unresolved, in
known_unresolved_discrepancies: (a) the Board resolution's own number's digit
order ("2024/1" per the signed PDF vs "1/2024" per the Gazette+qanoonsa);
(b) Article 8 item 11's cross-referenced article number ("الخامسة"/Art.5 per
the signed PDF+rega.gov.sa page vs "السادسة"/Art.6 per the Gazette+qanoonsa --
Art. 6, not 5, is substantively the one about the property-owner agreement, so
this may be an original drafting error preserved verbatim on REGA's own
channels); (c) Article 40's own effective-date clause ("من تاريخ العمل بالنظام"
i.e. effective from the parent Law's own effective date, per the signed PDF +
rega.gov.sa page, vs "من نشرها" i.e. effective from the Regulation's own
publication, per the Gazette+qanoonsa -- a SUBSTANTIVE difference, not merely
cosmetic). Two further, non-substantive discrepancies were also identified and
corrected with disclosure: rega.gov.sa's own live page has since been edited to
show the Ministry's CURRENT name in Article 8 item 3 (an administrative-
currency edit unrelated to the Regulation's own text -- reverted to the
historical name that the signed PDF + Gazette + qanoonsa all three agree on),
and a simple one-letter spelling typo in Chapter 3's own title on rega.gov.sa's
live page only (corrected using 3-source agreement). See the source artifact's
known_unresolved_discrepancies for the complete, exact wording of every
alternative reading.

40 articles, 7 top-level structural blocks: Articles 1-7 are general/preliminary
provisions carrying NO chapter/section title in ANY of the four independently-
fetched sources (disclosed, not fabricated -- see
known_unresolved_discrepancies), followed by six explicitly-titled chapters
(الفصل الأول..السادس) covering Articles 8-40, with chapter boundaries and
titles confirmed identically across all four sources. All 40 اصلية (original,
first issuance); 0 معدلة, 0 مضافة, 0 ملغاة (never amended as of this pass).

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. Despite FOUR
independent channels being reached (two of them directly controlled by the
issuing authority itself: its own live regulation page and its own hosted
signed/scanned PDF), and despite exact agreement across 37/40 articles and the
full chapter structure, THREE genuine, unresolved SUBSTANTIVE conflicts remain
between the {rega.gov.sa page, rega.gov.sa signed PDF} pair and the
{uqn.gov.sa Gazette, qanoonsa.com} pair (see above). This corpus's TIER_1
criterion requires 2+ independent official sources matching WITHOUT any
unresolved gap; a genuine three-point substantive conflict between official
channels, however well cross-checked and disclosed, does not meet that bar.
laws.boe.gov.sa was not checked this pass, consistent with this corpus's
convention for board-resolution-level (not royal-decree-level) regulations;
WebSearch results surfaced only the PARENT LAW's own BOE lawId, not a distinct
one for this Regulation.

Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK = "real_estate_contributions_implementing_regulation"
SRC = os.path.join(ROOT, "sources", TRACK, "law", "official_source",
                   TRACK + "_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", TRACK, "law", "verified")
RECORDS = os.path.join(OUT_VER, TRACK + "_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, TRACK + "_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", TRACK + "_arabic_legal_llm",
                        TRACK + "_legal_llm_001_040.json")

LAW_ID = "sa-real-estate-contributions-implementing-regulation-2024-1"
LAW_AR = "اللائحة التنفيذية لنظام المساهمات العقارية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"real_estate_contributions_implementing_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس الرئيس المساهمة العقارية المرخص له").split())


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
        gov_note = ("Arabic governs; this is the currently in-force Implementing "
                    "Regulation of the Real Estate Contributions Law (REGA Board "
                    "Resolution by circulation No. Q/M/E/H/2024/1/T, 18/7/1445H), "
                    "a brand-new regulation track built this pass (flagged as a "
                    "follow-up candidate by the parent real_estate_contributions_law "
                    "track's own build). Verified across FOUR independent channels: "
                    "rega.gov.sa's own regulation page, rega.gov.sa's own hosted "
                    "signed/scanned PDF (visually read in full, 20/20 pages), the "
                    "Umm Al-Qura Gazette's own website (uqn.gov.sa), and qanoonsa.com "
                    "(secondary aggregator). 37/40 articles and the full chapter "
                    "structure match exactly across all four; THREE disclosed, "
                    "UNRESOLVED substantive conflicts remain between the two "
                    "REGA-hosted channels and the Gazette+aggregator pair (decision "
                    "number digit order; Article 8 item 11's cross-referenced "
                    "article number; Article 40's own effective-date clause) -- see "
                    "known_unresolved_discrepancies in the source artifact before "
                    "relying on this track, especially for Article 40. "
                    "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED.")
        ver.append({"law_key": TRACK, "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "REAL_ESTATE_CONTRIBUTIONS_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": gov_note,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "real-estate-contributions-implementing-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "%s/law/articles/%s" % (TRACK, key),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المساهمات العقارية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("REGA Board of Directors Resolution "
                                                          "(by circulation) No. "
                                                          "(Q/M/E/H/2024/1/T), 18/7/1445H "
                                                          "(30/1/2024G) -- the Implementing "
                                                          "Regulation of the Real Estate "
                                                          "Contributions Law, issued under "
                                                          "Article 37 of that Law and in "
                                                          "agreement with the Capital Market "
                                                          "Authority. Verbatim text from "
                                                          "rega.gov.sa's own regulation page, "
                                                          "cross-verified word-for-word "
                                                          "against rega.gov.sa's own hosted "
                                                          "signed/scanned PDF (visual "
                                                          "page-by-page read, 20/20 pages), "
                                                          "the Umm Al-Qura Gazette's own "
                                                          "website (uqn.gov.sa/details?"
                                                          "p=24519), and qanoonsa.com. "
                                                          "TIER_2_PRIMARY_SECONDARY_CROSS_"
                                                          "VERIFIED -- see "
                                                          "known_unresolved_discrepancies for "
                                                          "3 disclosed substantive conflicts "
                                                          "between official channels."),
                                     "source_authority_ar": "قرار مجلس إدارة الهيئة العامة للعقار بالتمرير رقم (ق/م/إ/هـ/2024/1/ت) وتاريخ 18/7/1445هـ — اللائحة التنفيذية لنظام المساهمات العقارية، الصادرة تنفيذاً للمادة (37) من ذلك النظام وبالاتفاق مع هيئة السوق المالية. المستوى TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": TRACK,
               "layer": "REAL_ESTATE_CONTRIBUTIONS_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "gazette_publication": src.get("gazette_publication"),
               "parent_law_ar": src.get("parent_law_ar"),
               "parent_law_track_id": src.get("parent_law_track_id"),
               "legal_status_ar": src.get("legal_status_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-real-estate-contributions-implementing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (40 مادة؛ 40 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ 6 فصول مرقمة + مواد تمهيدية 1-7)",
               "title_en": ("Implementing Regulation of the Real Estate Contributions "
                            "Law (REGA Board Resolution Q/M/E/H/2024/1/T, 18/7/1445H) "
                            "— Arabic LLM-ready layer (40 records: 40 original, 0 "
                            "amended, 0 added, 0 repealed; 6 numbered chapters plus "
                            "unnumbered preliminary Articles 1-7)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 40], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Implementing Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
