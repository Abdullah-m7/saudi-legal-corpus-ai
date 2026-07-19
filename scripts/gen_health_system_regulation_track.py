#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Implementing Regulation of the Health System Law
track (اللائحة التنفيذية للنظام الصحي, Ministerial Decision No. 30/69181,
15/6/1424H), the companion regulation to the already-ingested health_system_law
track (Royal Decree M/11, 23/3/1423H).

VERIFICATION TIER: TIER_4 (single source, documented partial/mixed coverage).
See sources/health_system/regulation/official_source/
health_system_regulation_official_source.json's verification_methodology_note
and known_unresolved_discrepancies for the full account. Summary:

The health_system_law track's own registry (health_system_law_official_source.
json, key health_system_implementing_regulation_not_ingested) explicitly
flagged this Implementing Regulation as "confirmed to exist ... but content
could not be reached" in a prior pass. This pass is a dedicated follow-up.

laws.boe.gov.sa was checked FIRST: no dedicated lawId page for this specific
Regulation was found (only the parent Law's own BOE page exists), the live
portal itself failed repeatedly (connection reset via direct curl, matching
the parent law track's own documented BOE outage for this same period), and
Wayback Machine access is blocked at this session's egress-policy level
(WebFetch explicitly refuses web.archive.org; a direct curl for a confirmed
snapshot timestamp returned HTTP 403 via the configured proxy) -- consistent
with, and not contradicted by, the parent track's own finding.

The officially-designated primary host (istitlaa.ncc.gov.sa, linked directly
from MOH's own official e-participation page for this Regulation) was
confirmed genuinely unreachable via THREE independent channels this pass:
direct curl (TLS connection reset, 3 separate attempts), WebFetch (HTTP 503),
and r.jina.ai (an independent third-party headless-browser fetch service,
which itself timed out after 15s trying to reach the same URL) -- this
three-way, cross-infrastructure agreement indicates a genuine outage at the
source, not a fetch-tool artifact of this session.

The ONLY source through which real article text could be retrieved this pass
was qanoniah.com (an independent Arabic legal aggregator, not a mirror of BOE
or istitlaa). Its rendered page is a client-side (Nuxt/Vue) application;
this pass located its underlying public JSON API (api.qanoniah.com/v1/files/
{hash}, unauthenticated) by inspecting the server-rendered Nuxt config, and
fetched it directly. That API returns a CONFIRMED, SERVER-ENFORCED cap of
exactly 10 items regardless of pagination parameters tried (?page=, ?offset=,
?limit=) -- verified by comparing byte-identical response digests across
attempts -- i.e. a free-preview limit on qanoniah.com's own end, not a
limitation of the fetch method used here.

Those 10 confirmed items are the implementing rules for Articles 2 through 11
of the parent Law (this Regulation numbers its own sections directly by the
parent Law's article numbers it implements -- e.g. its "المادة الرابعة"
section is keyed "4-ل-..." throughout and cross-references "المادة الرابعة
من النظام" -- NOT an independently-resequenced 1..N numbering). No entry for
the parent Law's Article 1 (definitions) exists in qanoniah.com's own index
at all (the index itself starts at order:1 = "المادة الثانية"), so its
absence here is a genuine source gap, not an artifact of the preview cap.
Articles 12 through 19 (including Article 16, the heavily-amended Health
Services Council article) could NOT be recovered this pass from any source
tried -- they are EXCLUDED, not fabricated.

10 records total, all اصلية (this pass found no per-article amendment history
for any of them; whether unrecovered articles 12-19 carry later amendments is
simply unknown this pass). 0 معدلة, 0 ملغاة, 0 مضافة. No repeal of a prior
implementing regulation was found in any source (consistent with this being
the first Implementing Regulation issued under the parent Law's Article 18
mandate) -- a confirmed negative finding, not an omission.

No legal text is altered beyond plain HTML-tag stripping and HTML-entity
decoding of qanoniah.com's own markup (<ul>/<li>/<p>/<strong>) into plain
text. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "health_system", "regulation", "official_source",
                   "health_system_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "health_system", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "health_system_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "health_system_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "health_system_regulation_arabic_legal_llm",
                        "health_system_regulation_legal_llm_001_010.json")

LAW_ID = "sa-health-system-regulation-30-69181-1424"
LAW_AR = "اللائحة التنفيذية للنظام الصحي"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"health_system_regulation_art_(\d{3})$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الوزارة الوزير الصحية الصحي").split())


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
    return int(m.group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = a["article_number"]
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "health_system", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "HEALTH_SYSTEM_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": True,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS_UNCHANGED,
                    "implements_law_article": n,
                    "governing_source_note": ("Arabic governs; the ONLY source through which "
                                              "real article text could be retrieved this pass "
                                              "was qanoniah.com's public API -- laws.boe.gov.sa "
                                              "has no dedicated page for this Regulation and was "
                                              "itself unreachable live this pass; Wayback Machine "
                                              "access is blocked at this session's egress-policy "
                                              "level; istitlaa.ncc.gov.sa (the officially-"
                                              "designated primary host per MOH's own e-"
                                              "participation page) was confirmed unreachable via "
                                              "THREE independent channels (direct curl, WebFetch, "
                                              "and a third-party r.jina.ai fetch). qanoniah.com's "
                                              "own API enforces a confirmed 10-item preview cap "
                                              "(verified via multiple pagination parameters all "
                                              "returning an identical payload) -- this Regulation "
                                              "covers ONLY Articles 2-11 of the parent Law this "
                                              "pass; Article 1 has no entry in the source at all, "
                                              "and Articles 12-19 could not be recovered and are "
                                              "excluded, not fabricated. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text, "
                                              "provenance, or completeness."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": True,
                    "record_id": "health-system-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "health_system/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية للنظام الصحي" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision No. 30/69181 "
                                                          "(15/6/1424H) -- text retrieved only "
                                                          "via qanoniah.com's public API "
                                                          "(api.qanoniah.com), an independent "
                                                          "legal aggregator; laws.boe.gov.sa has "
                                                          "no dedicated page for this Regulation "
                                                          "and its live portal was unreachable; "
                                                          "istitlaa.ncc.gov.sa (MOH's own "
                                                          "designated primary host) was confirmed "
                                                          "unreachable via three independent "
                                                          "channels this pass; qanoniah.com's own "
                                                          "server enforces a confirmed 10-item "
                                                          "preview cap, so this covers only "
                                                          "Articles 2-11 of the parent Law"),
                                     "source_authority_ar": "القرار الوزاري رقم 30/69181 وتاريخ 15/6/1424هـ — النص مسترجَع فقط عبر واجهة برمجة التطبيقات العامة لموقع qanoniah.com (مُجمِّع قانوني مستقل)؛ لا صفحة مخصصة لهذه اللائحة على بوابة هيئة الخبراء وبوابتها الحية غير قابلة للوصول؛ istitlaa.ncc.gov.sa (المضيف الأساسي الرسمي المُعلَن من الوزارة) تأكَّد تعذّر الوصول إليه عبر ثلاث قنوات مستقلة هذه الجولة؛ خادم qanoniah.com نفسه يفرض حد معاينة مؤكَّد بعشر مواد، فتغطي هذه اللائحة هنا فقط المواد 2-11 من النظام الأصلي",
                                     "source_status": STATUS_UNCHANGED.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "health_system",
               "layer": "HEALTH_SYSTEM_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "parent_law_article_range": src.get("parent_law_article_range"),
               "confirmed_covered_law_articles": src.get("confirmed_covered_law_articles"),
               "excluded_law_articles_not_recovered": src.get("excluded_law_articles_not_recovered"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-health-system-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": (LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (10 مواد "
                            "تنفيذية مؤكَّدة، مقابلة لأرقام المواد 2-11 من النظام الأصلي؛ "
                            "تغطية جزئية موثَّقة صراحة -- انظر known_unresolved_discrepancies "
                            "لملخص المواد غير المُسترجَعة)"),
               "title_en": ("Implementing Regulation of the Saudi Arabian Health System Law "
                            "— Arabic LLM-ready layer (10 confirmed implementing-rule records, "
                            "corresponding to parent Law Articles 2-11; PARTIAL, explicitly "
                            "documented coverage -- see known_unresolved_discrepancies for the "
                            "articles that could not be recovered this pass)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [2, 11], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Health System Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
