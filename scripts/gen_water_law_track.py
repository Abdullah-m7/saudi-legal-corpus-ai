#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Water Law track (نظام المياه,
Royal Decree M/159, 11/11/1441H / 2020G).

VERIFICATION TIER -- see sources/water/law/official_source/
water_law_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY SOURCE ACCESS FAILED THIS PASS: laws.boe.gov.sa DOES have a dedicated
lawId page for this law (57261279-94b7-4ddc-8ad2-abf100d246be) -- unlike some
Board-level executive regulations -- but the live portal returned HTTP 503
(WebFetch) / HTTP 000 connection-reset (direct curl) on repeated attempts. The
usual fallback (Wayback Machine) was also unavailable: archive.org's own
availability API confirmed a snapshot of THIS page exists (12 Dec 2025,
timestamp 20251212221437), but fetching the snapshot content from
web.archive.org returned HTTP 403 -- an organization egress-policy block on
that host for this session, which was NOT routed around (this corpus has a
firm rule against egress-policy bypass, and other tracks -- health_system,
food -- documented the identical block).

SECONDARY SOURCES: nezams.com (an independent Arabic legal-text aggregator,
NOT a BOE mirror), fetched directly via curl (HTTP 200), supplied the full
verbatim text of all 77 articles, extracted programmatically from its raw
"subject" HTML elements (77 elements confirmed, subject-1 through subject-77,
spelled-ordinal labels المادة الأولى ... المادة السابعة والسبعون). Its own
page metadata states explicitly "التعديلات: لم يجر عليه تعديل" (no amendment
has been made). Independently, WebSearch results indexing laws.boe.gov.sa's
own content returned a verbatim match for Article 74's text, the decree
identity (M/159, 11/11/1441H; CoM 710, 9/11/1441H), the SAR-20-million penalty
ceiling, the Saudi Water Code mandate, and the 17-chapter structure -- a
second, independent confirmation not derived from nezams.com.

77 records, ALL اصلية (15... no: 77 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة). 17
chapters (فصول). No inline per-article titles beyond spelled-ordinal "المادة
..." labels -- no title_ar field is used; section_ar carries each article's
chapter title.

PREDECESSOR REPEAL (a MATERIAL distinction from this corpus's
health_system_law and food_law tracks): Article 75 does NOT use a generic
conflict-only clause. It EXPLICITLY repeals three NAMED predecessor laws by
decree number and date: (1) نظام مصالح المياه والصرف الصحي (M/22, 23/6/1391H)
and its regulations; (2) نظام المحافظة على مصادر المياه (M/34, 24/8/1400H) and
its regulations; (3) نظام مياه الصرف الصحي المعالجة وإعادة استخدامها (M/6,
13/2/1421H) and its implementing regulation. These are real, named supersession
links, flagged for a repo-level repeal/supersession graph (owner's call).

TASHKEEL: nezams.com's source text carries partial tashkeel (harakat). Harakat
are stripped uniformly for consistency with this corpus's BOE-family majority
(unvocalized); tatweel is preserved only in the Hijri "هـ" marker. This
DIVERGES from this corpus's health_system_law track (same nezams.com source,
which kept tashkeel) -- the divergence is intentional and disclosed. No legal
text is altered beyond that display-layer normalization and the HTML->text
conversion. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "water", "law", "official_source",
                   "water_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "water", "law", "verified")
RECORDS = os.path.join(OUT_VER, "water_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "water_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "water_arabic_legal_llm",
                        "water_law_legal_llm_001_077.json")

LAW_ID = "sa-water-law-m-159-1441"
LAW_AR = "نظام المياه"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"water_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم المياه الوزارة الوزير الهيئة").split())


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
        ver.append({"law_key": "water", "law_component": "law",
                    "language": "ar",
                    "record_layer": "WATER_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; laws.boe.gov.sa DOES have a "
                                              "dedicated lawId page for this law "
                                              "(57261279-94b7-4ddc-8ad2-abf100d246be) but it was "
                                              "unreachable this pass (HTTP 503 live; the confirmed "
                                              "Wayback snapshot is egress-policy-blocked at "
                                              "web.archive.org and was NOT bypassed). Full text is "
                                              "from nezams.com (an independent aggregator, HTTP "
                                              "200), whose own metadata states the law has had NO "
                                              "amendments; the decree identity, Article 74's "
                                              "verbatim text, the SAR-20m penalty ceiling and the "
                                              "17-chapter structure were independently confirmed "
                                              "via WebSearch indexing of BOE's own content. All 77 "
                                              "articles are اصلية. Article 75 EXPLICITLY repeals "
                                              "three NAMED predecessor laws (M/22 1391H, M/34 "
                                              "1400H, M/6 1421H) -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text or "
                                              "provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "water-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "water/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام المياه" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree M/159 (11/11/1441H), CoM "
                                                          "Resolution 710 (9/11/1441H) — full text "
                                                          "from nezams.com (independent "
                                                          "aggregator), decree identity / Article "
                                                          "74 text / penalty ceiling / 17-chapter "
                                                          "structure independently confirmed via "
                                                          "WebSearch indexing of BOE's own "
                                                          "content; laws.boe.gov.sa's dedicated "
                                                          "lawId page "
                                                          "(57261279-94b7-4ddc-8ad2-abf100d246be) "
                                                          "was unreachable this pass (live 503; "
                                                          "Wayback snapshot egress-blocked, not "
                                                          "bypassed)"),
                                     "source_authority_ar": "المرسوم الملكي رقم م/159 وتاريخ 11/11/1441هـ، وقرار مجلس الوزراء رقم 710 وتاريخ 9/11/1441هـ — النص الكامل من nezams.com (مصدر ثانوي مستقل)، مع تحقق مستقل من هوية المرسوم ونص المادة الرابعة والسبعين وسقف الغرامة وبنية الفصول السبعة عشر عبر فهرسة محرك البحث لمحتوى بوابة هيئة الخبراء ذاتها؛ الصفحة المخصصة على laws.boe.gov.sa (lawId 57261279-94b7-4ddc-8ad2-abf100d246be) غير قابلة للوصول هذه الجولة (503 حيا، ولقطة Wayback محظورة ولم تُتجاوَز)",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "water",
               "layer": "WATER_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-water-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (77 مادة؛ 77 أصلية)",
               "title_en": "Saudi Arabian Water Law — Arabic LLM-ready layer (77 records: 77 original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 77], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Water Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
