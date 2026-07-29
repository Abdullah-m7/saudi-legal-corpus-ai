#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Railway Law track (نظام الخطوط الحديدية, Royal
Decree M/159, 22/8/1445H (3/3/2024) -- the currently in-force Railway Law,
administered by the General Authority for Transport (TGA), in coordination
with the Ministry of Transport and Logistics).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام الخطوط الحديدية is a single,
self-standing Royal-Decree law (M/159, 22/8/1445H), published in Umm Al-Qura
Gazette Issue (5024), 15 March 2024. laws.boe.gov.sa (this corpus's usual
first official source) was checked FIRST per standard methodology: dedicated
lawId pages were located via WebSearch for BOTH this new law
(302fe435-6f39-4170-b12b-b13700bf55bd) and its repealed predecessor
(f8b0846c-4a2c-49f2-bff3-a9a700f2ef2e -- the same URL supplied in this pass's
task brief), but the live portal is unreachable (curl: "Connection reset by
peer"; WebFetch: HTTP 503) and even the one available web.archive.org
snapshot (timestamp 20260215010913, confirmed to exist via the
archive.org/wayback/available API) returned HTTP 403 / connection-reset on
every direct fetch attempt. uqn.gov.sa (Umm Al-Qura Gazette's own portal) was
also attempted directly (HTTP 200, ~850KB page) but its search results are
rendered client-side (JavaScript) and were not present in the fetched static
HTML.

Per this pass's own explicit fallback instructions, the governing text was
instead taken directly (via curl, HTTP 200, NOT merely an AI-summarized
WebFetch) from qanoonsa.com -- three independent pages on that one domain:
/p/502403/ (the Law's full 50 articles), /p/502402/ (the enacting Royal
Decree M/159's own text), and /p/502401/ (Council of Ministers Resolution
692's own text) -- and cross-verified, article by article, against a SECOND,
fully independent source: nezams.com (also fetched directly via curl, HTTP
200). A Python script (not eyeballing) normalized both sides (Eastern->
Western digits, harakat/tashkeel stripped, Farsi-yeh/Arabic-decimal-separator
variants unified) and diffed all 50 articles: 48/50 matched byte-for-byte
after normalization; the remaining 2 were a purely decorative-tatweel list-
marker variant (article 9, no wording difference) and one genuine
qanoonsa.com-side duplication glitch in Article 1 (see below), corrected
using nezams.com's independent, grammatically-sound reading. The enacting
Royal Decree's and the Council of Ministers Resolution's repeal clauses
(each independently fetched) are byte-for-byte identical to each other,
reinforcing confidence in that specific text. Three further independent news
sources -- spa.gov.sa (Saudi Press Agency, official), argaam.com, and
sabq.org -- all corroborate, verbatim in substance, the companion 91-article
Implementing Regulation's TGA-board adoption on 25 October 2024.

ARTICLE 1 DUPLICATION GLITCH DISCOVERED AND CORRECTED -- qanoonsa.com's copy
of Article 1 read "نظام الخطوط الحديدية الراكب: كل من صعد ..." (nonsensical:
a defined-term list entry cannot itself start with "نظام الخطوط الحديدية").
nezams.com's independent copy reads simply "الراكب: كل من صعد ..." -- grammatically
sound and consistent with every other single-word defined term in the same
Article. This one glitch was corrected using nezams.com; every other word of
all 50 articles matches qanoonsa.com byte-for-byte after normalization.

SUPERSESSION -- CONFIRMED, but NOT inside any of the Law's own 50 numbered
Articles (Articles 49-50 deal only with the Implementing Regulation mandate
and entry into force). The repeal is stated in the ENACTING ROYAL DECREE
itself (clause "ثانيا"), word-for-word identical in the prior Council of
Ministers Resolution 692's own clause "ثانيا": "يحل النظام -المشار إليه في
البند (أولا) من هذا المرسوم- عند نفاذه، محل نظام النقل بالخطوط الحديدية
الصادر بالمرسوم الملكي رقم (م / 33) بتاريخ 24 / 5 / 1433هـ، ويلغي كل ما
يتعارض معه من أحكام." This differs from this corpus's contractors_classification_law
track (where the repeal is inside the law's own numbered Article 19) --
disclosed explicitly, not silently normalized to look the same.

VERIFICATION TIER -- TIER_3. Zero official/primary government source was
actually reached this pass (laws.boe.gov.sa unreachable live AND via its one
located wayback snapshot; uqn.gov.sa's search results not renderable without
JS). Two fully independent secondary/aggregator sources (qanoonsa.com,
nezams.com) were fetched directly and cross-verified article-by-article with
near-total (48/50 immediate, 50/50 after 2 disclosed, non-substantive fixes)
agreement. This matches this corpus's own TIER_3 definition: "primary
official portal confirmed unreachable; 2+ independent secondary sources
agree with each other, with zero primary confirmation."

50 articles, NO formal فصل/باب chapter labels in the source text itself (a
directly-numbered law with 10 unlabeled topical section headings instead --
recorded via section_ar only, not fabricated "الفصل X" labels); all 50
اصلية; 0 معدلة, 0 ملغاة, 0 مضافة. Diacritics (tashkeel) are stripped
uniformly and digits normalized to Western, consistent with this corpus's
other tracks.

IMPLEMENTING REGULATION -- exists (per spa.gov.sa, argaam.com, and sabq.org:
TGA Board adopted it 22 Rabi' al-Thani 1446H / 25 October 2024, 91 articles)
but NOT built this pass; flagged as a follow-up candidate track
(railway_regulation, law_component "regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "railway_law", "law", "official_source",
                   "railway_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "railway_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "railway_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "railway_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "railway_law_arabic_legal_llm",
                        "railway_law_legal_llm_001_050.json")

LAW_ID = "sa-railway-law-m159-1445"
LAW_AR = "نظام الخطوط الحديدية"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"railway_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس الخطوط الحديدية").split())


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
        ver.append({"law_key": "railway_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "RAILWAY_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Railway Law (Royal Decree M/159, 22/8/1445H), a "
                                              "brand-new base-law track built from scratch this "
                                              "pass (not previously in this corpus). The Law "
                                              "replaces the prior Railway Transport Law (M/33, "
                                              "24/5/1433H) by clause (Second) of its own ENACTING "
                                              "ROYAL DECREE -- NOT inside any of its 50 numbered "
                                              "Articles. Text fetched directly from qanoonsa.com "
                                              "(three independent pages: the 50-article Law, the "
                                              "Royal Decree M/159, and CoM Resolution 692) and "
                                              "cross-verified article-by-article against the fully "
                                              "independent nezams.com. laws.boe.gov.sa was checked "
                                              "FIRST per standard methodology but unreachable this "
                                              "pass (live: connection reset/HTTP 503; its one "
                                              "located wayback snapshot: HTTP 403/connection reset "
                                              "on every attempt). TIER_3. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably the "
                                              "disclosed Article-1 duplication-glitch correction and "
                                              "the decree-level (not article-level) repeal clause."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "railway-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "railway_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الخطوط الحديدية" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/159), 22/8/1445H "
                                                          "(Council of Ministers Resolution 692, "
                                                          "17/8/1445H; Shura Council Resolution "
                                                          "279/43, 22/11/1443H) — the currently "
                                                          "in-force Railway Law, published in Umm "
                                                          "Al-Qura Gazette Issue 5024 (15 March "
                                                          "2024). By its enacting Royal Decree's "
                                                          "own clause (Second) -- not any numbered "
                                                          "Article of the Law itself -- it replaces "
                                                          "the prior Railway Transport Law (M/33, "
                                                          "24/5/1433H). Verbatim text fetched "
                                                          "directly from qanoonsa.com and "
                                                          "cross-verified article-by-article "
                                                          "against the independent nezams.com "
                                                          "(one disclosed Article-1 duplication-"
                                                          "glitch correction). laws.boe.gov.sa "
                                                          "unreachable this pass, live and via its "
                                                          "one located wayback snapshot. TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/159) وتاريخ 22/8/1445هـ (قرار مجلس الوزراء رقم (692) وتاريخ 17/8/1445هـ؛ قرار مجلس الشورى رقم (279/43) وتاريخ 22/11/1443هـ) — نظام الخطوط الحديدية النافذ حاليا، المنشور في جريدة أم القرى، العدد (5024)، بتاريخ 15 مارس 2024م. يحل -بنص البند (ثانيا) من مرسوم إصداره ذاته، لا بنص أي مادة من مواده- محل نظام النقل بالخطوط الحديدية السابق (م/33، 24/5/1433هـ). النص الحرفي جُلب مباشرة من qanoonsa.com وتحقق منه مادة مادة مقابل nezams.com المستقل (مع تصحيح مفصح عنه لعلة تكرار واحدة في المادة الأولى). laws.boe.gov.sa غير قابل للوصول هذه الجولة حيا وعبر لقطته الأرشيفية الوحيدة المرصودة. المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "railway_law",
               "layer": "RAILWAY_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-railway-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (50 مادة؛ 50 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ عشرة أقسام موضوعية غير مرقمة بلفظ الفصل)",
               "title_en": ("The Saudi Arabian Railway Law (Royal Decree M/159, 22/8/1445H) — "
                            "Arabic LLM-ready layer (50 records: 50 original, 0 amended, 0 added, "
                            "0 repealed; 10 unlabeled topical section headings, no formal فصل "
                            "numbering in the source)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 50], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Railway Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
