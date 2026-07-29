#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Copyright Law track (نظام حقوق المؤلف, Royal
Decree M/169, 14/8/1447H, approving Council of Ministers Resolution 560,
8/8/1447H -- published in Umm Al-Qura Gazette Year 104, Issue 5144, Friday
25 Sha'ban 1447H / 13 February 2026, pages 13-17).

BRAND-NEW TRACK, SEPARATE FROM `copyright`. This is NOT an edit of the
existing `copyright` track (نظام حماية حقوق المؤلف, Royal Decree M/41,
2/7/1424H, 28 articles). That track is untouched by this pass and MUST NOT be
deleted -- see "WHY THE PREDECESSOR SURVIVES" below.

TITLE CHANGE -- the new statute is «نظام حقوق المؤلف»; the predecessor was
«نظام حماية حقوق المؤلف». The word «حماية» is DROPPED. Confirmed from the
gazette headline, the portal page <title>, and the Law's own Article 1
definition («النظام: نظام حقوق المؤلف.»).

NOT YET IN FORCE AT BUILD TIME -- this is the single most important fact
about this track. Article 61 reads verbatim: «يعمل بالنظام بعد (مائة
وثمانين) يوما من تاريخ نشره في الجريدة الرسمية.» Gazette publication was 13
February 2026, so 13 Feb 2026 + 180 days = 12 August 2026. At this track's
build date (29 July 2026) only 166 of the 180 days had elapsed, so the Law
was NOT in force. A ONE-DAY AMBIGUITY REMAINS AND IS DELIBERATELY LEFT
UNRESOLVED: «بعد» may be read as taking effect on the 180th day itself
(2026-08-12) or on the day after the period expires (2026-08-13). No official
source reached this pass settles the reading, so the source artifact stores a
CANDIDATE RANGE ["2026-08-12", "2026-08-13"] with in_force_date_resolved =
false, never a single asserted date. (A previously circulating figure of
2026-08-01 is not derivable from any clause of the instrument and must not be
reused.)

REPEAL SITS INSIDE A NUMBERED ARTICLE, NOT IN THE ENACTING DECREE. Article 59
of the Law's own text reads verbatim: «يحل النظام محل نظام حماية حقوق
المؤلف، الصادر بالمرسوم الملكي رقم (م/41) وتاريخ 1424/7/2هـ، ويلغي كل ما
يتعارض معه من أحكام.» Royal Decree M/169's own three clauses (FIRST
approval / SECOND reciprocity / THIRD execution) and CoM Resolution 560's ten
clauses contain NO repeal language whatsoever. This matches this corpus's
road_transport_law / contractors_classification_law pattern (repeal carried
by the enacted text) and NOT its railway_law pattern (repeal only in the
enacting decree).

THE MIRROR-IMAGE CASE, AND THE INGESTION TRAP THIS TRACK EXISTS TO AVOID.
Clause SECOND (ثانيا) of Royal Decree M/169 carries a SUBSTANTIVE rule --
a foreign-reciprocity restriction on the scope of protection the Law grants
-- that has NO numbered article of its own anywhere in Articles 1-61. Any
ingestion that captures only the 61 numbered articles silently drops a live
substantive rule. This track therefore captures it explicitly and
separately, in BOTH `preamble_ar` (the full decree, verbatim) and a dedicated
`decree_clauses_outside_articles` list where the clause is flagged
`is_substantive_rule: true` and `has_corresponding_numbered_article: false`.
It is NEVER written into any article record -- decree-level content and
article-level content stay strictly distinct. The validator enforces both
halves of this: the clause must be present at decree level, and its
distinctive text must NOT appear inside any of the 61 articles.

WHY THE PREDECESSOR SURVIVES -- Article 24 keeps M/41 legally relevant even
after cutover. It extends protection, per the terms in Articles 22 and 23, to
works, performances, sound recordings and broadcasts whose protection term
«لم تنقض ... بموجب نظام حماية حقوق المؤلف السابق قبل بدء سريان هذا النظام».
Computing an accrued term therefore still requires M/41's own text. The
existing 28-article `copyright` track is consequently a permanent dependency
of this one, not a superseded artifact to be discarded.

STRUCTURE -- 61 articles, running flat from المادة الأولى to المادة الحادية
والستون with NO فصل/باب division anywhere in the published text (unlike M/41,
which had seven فصول). All 61 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة (no amendment
exists, nor could one plausibly, since the Law has not yet entered into
force).

SOURCES ACTUALLY FETCHED THIS PASS (curl, not WebFetch -- WebFetch returns an
LLM summary rather than verbatim text for these pages and is unusable for
verbatim capture):
  * uqn.gov.sa/details?p=28845                       -- the Law, 61 articles
  * uqn.gov.sa/decisions-and-regulations/4000304     -- Royal Decree M/169
  * uqn.gov.sa/details?p=28844                       -- CoM Resolution 560
  * the official gazette PDF for issue 5144 (10,895,438 bytes, 32pp,
    MD5 a250fb199e29ef7c3e0672fcda181cf4), whose pages 13 and 17 were
    rendered to independent images at 170dpi and read visually. pdftotext
    output was NOT used as a text source: it suffers ligature decomposition
    on this InDesign-generated file. The page images confirm the masthead,
    the decree, the resolution, and that the Law ends at Article 61.
  * qanoonsa.com/p/514448/ -- independent secondary cross-check; 60 of 61
    articles matched exactly after Unicode normalization, the 61st differing
    only in date-component ordering (see known_unresolved_discrepancies).

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE, per this corpus's own
taxonomy, which admits "a portal's database versus the official PDF published
by that same portal" and "a single official PDF verified via OCR / independent
page images of the same official document" as qualifying. Both hold here, with
no unresolved access gap in the Law's text. The caveat that both official legs
share one publisher (Umm Al-Qura) is disclosed explicitly in the source
artifact so a later reviewer can downgrade to TIER_2 if they require two
distinct official publishers. laws.boe.gov.sa was attempted twice and reset
the connection both times. saip.gov.sa (the administering authority under
Article 1) WAS reachable, but its complete 18-document legislation list does
not carry the new Law at all -- it still lists only M/41. That negative is
recorded rather than glossed.

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "copyright_law_1447", "law", "official_source",
                   "copyright_law_1447_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "copyright_law_1447", "law", "verified")
RECORDS = os.path.join(OUT_VER, "copyright_law_1447_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "copyright_law_1447_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "copyright_law_1447_arabic_legal_llm",
                        "copyright_law_1447_legal_llm_001_061.json")

LAW_ID = "sa-copyright-law-m169-1447"
LAW_AR = "نظام حقوق المؤلف"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"copyright_law_1447_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم النظام الهيئة المجلس الرئيس عليه عليها كانا كانوا نحو ثم أم "
            "حقوق المؤلف").split())

GOVERNING_NOTE = (
    "Arabic governs. نظام حقوق المؤلف (Royal Decree M/169, 14/8/1447H, approving CoM "
    "Resolution 560, 8/8/1447H), published in Umm Al-Qura Year 104 Issue 5144, 25/8/1447H = "
    "13 February 2026, pp. 13-17. A BRAND-NEW TRACK, SEPARATE FROM the existing `copyright` "
    "track (M/41, 2/7/1424H, 28 articles), which is untouched and must not be deleted. "
    "*** NOT YET IN FORCE at this track's build date (2026-07-29). *** Article 61 defers "
    "operation by 180 days from gazette publication: 13 Feb 2026 + 180 d = 2026-08-12, with "
    "a disclosed and UNRESOLVED one-day ambiguity (2026-08-12 vs 2026-08-13) in how «بعد» is "
    "read; the source artifact stores a candidate range, not a single date. Until then M/41 "
    "governs. Article 59 -- a numbered article of this Law, NOT a clause of the enacting "
    "decree -- replaces M/41. Conversely, clause SECOND of Royal Decree M/169 carries a "
    "substantive foreign-reciprocity restriction with NO numbered article of its own; it is "
    "recorded ONLY at decree level (preamble_ar and decree_clauses_outside_articles), never "
    "inside an article record, and an ingestion reading only Articles 1-61 will drop it. "
    "Article 24 keeps M/41 relevant after cutover for protection terms accrued beforehand. "
    "Text fetched LIVE from uqn.gov.sa (portal pages for the Law, the Decree and the "
    "Resolution) and confirmed against independently rendered page images of the official "
    "gazette PDF for issue 5144, plus a secondary cross-check against qanoonsa.com. TIER_1. "
    "Read verification_methodology_note and known_unresolved_discrepancies in the source "
    "artifact before relying on this track."
)

SOURCE_AUTHORITY_EN = (
    "Royal Decree No. (M/169), 14/8/1447H, approving Council of Ministers Resolution No. "
    "(560), 8/8/1447H (Shura Council Resolutions 305/30 of 21/11/1446H and 121/11 of "
    "10/6/1447H) — the Saudi Copyright Law, published in Umm Al-Qura Gazette Year 104, Issue "
    "5144, Friday 25 Sha'ban 1447H / 13 February 2026, pp. 13-17. 61 articles, flat (no "
    "chapters). NOT YET IN FORCE as of the 2026-07-29 build date: Article 61 defers operation "
    "180 days from publication (computes to 2026-08-12; the 2026-08-12 vs 2026-08-13 reading "
    "of «بعد» is disclosed and left unresolved). By its own Article 59 — not the enacting "
    "decree — it replaces the Copyright Protection Law (M/41, 2/7/1424H); by its Article 24 "
    "that predecessor stays relevant for accrued protection terms. Clause SECOND of the "
    "enacting decree carries a substantive foreign-reciprocity restriction that has no "
    "numbered article and is stored at decree level only. Verbatim text fetched LIVE from "
    "uqn.gov.sa and confirmed against independently rendered images of the official gazette "
    "PDF (issue 5144) and against qanoonsa.com. TIER_1."
)

SOURCE_AUTHORITY_AR = (
    "المرسوم الملكي رقم (م/169) وتاريخ 14/8/1447هـ، الموافق على قرار مجلس الوزراء رقم (560) "
    "وتاريخ 8/8/1447هـ (وقراري مجلس الشورى رقم (305/30) وتاريخ 21/11/1446هـ ورقم (121/11) "
    "وتاريخ 10/6/1447هـ) — نظام حقوق المؤلف، المنشور في جريدة أم القرى، السنة 104، العدد "
    "(5144)، الجمعة 25 شعبان 1447هـ الموافق 13 فبراير 2026م، الصفحات 13-17. إحدى وستون مادة "
    "بلا فصول. *** غير نافذ بعد وقت بناء هذا المسار (29/7/2026م): *** تؤجل المادة الحادية "
    "والستون العمل به مائة وثمانين يوما من تاريخ النشر، أي 12/8/2026م حسابا، مع غموض ليوم "
    "واحد (12 أو 13 أغسطس) مُفصح عنه وغير محسوم. ويحل -بنص المادة التاسعة والخمسين من متنه "
    "ذاته لا بنص مرسوم إصداره- محل نظام حماية حقوق المؤلف (م/41، 2/7/1424هـ)، الذي يظل مع "
    "ذلك لازما بنص المادة الرابعة والعشرين لحساب مدد الحماية المكتسبة قبل النفاذ. ويحمل "
    "البند (ثانيا) من مرسوم الإصدار قيدا موضوعيا للمعاملة بالمثل لا تقابله أي مادة مرقمة، "
    "وهو مسجل على مستوى المرسوم وحده. النص الحرفي جُلب حيا من uqn.gov.sa وأُكد بصور صفحات "
    "مستقلة من ملف الجريدة الرسمية (العدد 5144) وبمقابلة qanoonsa.com. المستوى TIER_1."
)


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

    eif = src["entry_into_force"]
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
        ver.append({"law_key": "copyright_law_1447", "law_component": "law",
                    "language": "ar",
                    "record_layer": "COPYRIGHT_LAW_1447_ARABIC_VERIFIED_TEXT",
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
                    "in_force_at_record_build": eif["in_force_at_build"],
                    "in_force_date_candidates_gregorian": eif["in_force_date_candidates_gregorian"],
                    "in_force_date_resolved": eif["in_force_date_resolved"],
                    "governing_source_note": GOVERNING_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "copyright-law-1447-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "copyright_law_1447/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام حقوق المؤلف الجديد" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "in_force_at_record_build": eif["in_force_at_build"],
                    "in_force_date_candidates_gregorian": eif["in_force_date_candidates_gregorian"],
                    "in_force_date_resolved": eif["in_force_date_resolved"],
                    "source_trust": {"source_authority": SOURCE_AUTHORITY_EN,
                                     "source_authority_ar": SOURCE_AUTHORITY_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "copyright_law_1447",
               "layer": "COPYRIGHT_LAW_1447_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "gazette_publication_gregorian": src.get("gazette_publication_gregorian"),
               "legal_status_ar": src.get("legal_status_ar"),
               "in_force_as_of_build_date": src.get("in_force_as_of_build_date"),
               "entry_into_force": eif,
               "supersedes_ar": src.get("supersedes_ar"),
               "predecessor_track_key": "copyright",
               "predecessor_must_not_be_deleted": True,
               "predecessor_retention_reason_ar": (
                   "تبقي المادة الرابعة والعشرون من هذا النظام أحكام نظام حماية حقوق المؤلف "
                   "(م/41) لازمة لحساب مدد الحماية التي لم تنقض قبل بدء سريان هذا النظام؛ "
                   "فمسار copyright ذو الثماني والعشرين مادة تبعية دائمة لهذا المسار لا "
                   "أثر ملغى."),
               "decree_clauses_outside_articles": src.get("decree_clauses_outside_articles", []),
               "decree_clauses_note_ar": (
                   "بنود مرسوم الإصدار (م/169) الثلاثة مسجلة هنا وفي preamble_ar على مستوى "
                   "الأداة، ولم يُدرج أي منها ضمن سجلات المواد الإحدى والستين. والبند "
                   "(ثانيا) منها بالذات حكم موضوعي (قيد المعاملة بالمثل مع الأجانب) لا "
                   "تقابله أي مادة مرقمة، فيسقط صمتا من أي استيعاب يقتصر على المواد 1-61."),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-copyright-law-1447-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": (LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (61 مادة؛ 61 "
                            "أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول). غير نافذ بعد وقت "
                            "البناء: يعمل به بعد (مائة وثمانين) يوما من تاريخ النشر بنص "
                            "المادة الحادية والستين، أي 12/8/2026م (أو 13/8/2026م على القراءة "
                            "الأخرى للفظ \"بعد\"؛ الغموض مفصح عنه لا محسوم)."),
               "title_en": ("The Saudi Arabian Copyright Law (Royal Decree M/169, 14/8/1447H) "
                            "— Arabic LLM-ready layer (61 records: 61 original, 0 amended, 0 "
                            "added, 0 repealed; no chapter structure). NOT YET IN FORCE at "
                            "build time: Article 61 defers operation 180 days from the "
                            "13 Feb 2026 gazette publication, computing to 2026-08-12, with "
                            "the 2026-08-12 vs 2026-08-13 reading of «بعد» disclosed and "
                            "unresolved."),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 61], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "in_force_as_of_build_date": src.get("in_force_as_of_build_date"),
               "entry_into_force": eif,
               "decree_clauses_outside_articles": src.get("decree_clauses_outside_articles", []),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Copyright Law (M/169, 1447H) records" %
          (len(ver), len(llm)))


if __name__ == "__main__":
    main()
