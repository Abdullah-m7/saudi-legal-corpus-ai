#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Protection from Abuse Law track (نظام الحماية من الإيذاء,
Royal Decree M/52, 15/11/1434H / ~2013G; amended by Royal Decree M/72,
6/8/1443H / 2022G).

VERIFICATION TIER -- see sources/protection_from_abuse/law/official_source/
protection_from_abuse_law_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY BOE PORTAL ACCESS FAILED THIS PASS: laws.boe.gov.sa HAS a dedicated
lawId page for this law (83f450eb-7985-461f-b053-a9a700f2ba08) but the live
portal returned HTTP 503 (WebFetch) / HTTP 000 connection-reset (direct curl).
web.archive.org was NOT attempted (organization egress-policy block on that
host for this session, documented across this corpus and never bypassed).

SOURCES USED (TIER_2):
  * ORIGINAL full text (all 17 articles): an OFFICIAL Saudi GOVERNMENT PDF in
    the Ministry of Finance regulations library (mof.gov.sa) reproducing the
    Diwan Malaki circular No. 41930 (16/11/1434H) -- carries the Royal Decree
    (M/52) image, the Council of Ministers Resolution (332) image, and the full
    17-article statute as adopted by the Bureau of Experts. Fetched directly
    (HTTP 200) and read page-by-page. Cross-checked verbatim against nezams.com
    (independent legal aggregator, HTTP 200, exactly 17 "subject" elements
    subject-1..subject-17, spelled-ordinal labels المادة الأولى..السابعة عشرة).
  * AMENDMENT (arts 7, 12, 13; Royal Decree M/72, 6/8/1443H / CoM Resolution
    427, 5/8/1443H): the Umm al-Qura OFFICIAL GAZETTE (uqn.gov.sa, decree page
    p=19142, HTTP 200) cross-checked against nezams.com's quoted replacement
    text. Key phrases independently confirmed in the Umm al-Qura text
    (أوراقه الثبوتية / الفصل فيها قضاء / لا تقل عن (6) أشهر / ثلاثمائة /
    سقوط جنينها / حرض غيره أو اتفق معه / نظام الإجراءات الجزائية / 427 / م/72).

Not TIER_1 because the canonical BOE portal page itself could not be retrieved
or archived directly this pass.

17 records: 14 اصلية, 3 معدلة (arts 7, 12, 13), 0 ملغاة, 0 مضافة. The statute
has NO chapter/باب/فصل divisions (flat 1-17); section_ar is empty for every
article by design. Article 7 was amended by ADDING paragraph (6) to the
original five; Articles 12 and 13 were fully REPLACED. For each amended article
the CURRENT (as-amended) text is stored in `text`; the pre-amendment text is
preserved in history[type=original] and the amended text in
history[type=amendment_current].

NO PREDECESSOR REPEAL: unlike the water_law track, this statute repeals no named
predecessor and has no generic conflict clause (Article 17 is only the 90-day
effective-date rule) -- it is a founding statute.

DISTINCT FROM child_protection_law: this is a GENERAL anti-abuse statute (all
victims); the Child Protection Law (نظام حماية الطفل, Royal Decree M/14,
25/2/1436H) is a separate instrument. They share only a co-amendment link (both
amended by decree M/72) -- not a merge, no textual overlap.

TASHKEEL stripped uniformly (corpus-majority convention); curly quotes
straightened; double/nbsp spaces removed -- display-layer only, no legal text
altered. Arabic governs; no translation/paraphrase/interpretation. Read-only
over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "protection_from_abuse", "law", "official_source",
                   "protection_from_abuse_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "protection_from_abuse", "law", "verified")
RECORDS = os.path.join(OUT_VER, "protection_from_abuse_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "protection_from_abuse_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "protection_from_abuse_arabic_legal_llm",
                        "protection_from_abuse_law_legal_llm_001_017.json")

LAW_ID = "sa-protection-from-abuse-law-m-52-1434"
LAW_AR = "نظام الحماية من الإيذاء"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"protection_from_abuse_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = {
    "protection_from_abuse_law_art_007",
    "protection_from_abuse_law_art_012",
    "protection_from_abuse_law_art_013",
}
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


GOV_NOTE = ("Arabic governs; laws.boe.gov.sa HAS a dedicated lawId page for this law "
            "(83f450eb-7985-461f-b053-a9a700f2ba08) but it was unreachable this pass "
            "(HTTP 503 live / connection reset; web.archive.org egress-blocked and NOT "
            "bypassed). ORIGINAL full text is from an OFFICIAL government PDF in the "
            "Ministry of Finance regulations library (mof.gov.sa, Diwan Malaki circular "
            "41930) carrying the M/52 decree, CoM Resolution 332 and the full 17-article "
            "statute, cross-checked verbatim against nezams.com. The 1443H amendment of "
            "articles 7/12/13 (Royal Decree M/72, CoM Resolution 427) is confirmed by the "
            "Umm al-Qura OFFICIAL GAZETTE (uqn.gov.sa) cross-checked against nezams.com "
            "-> TIER_2. 17 articles, flat (no chapters); arts 7/12/13 معدلة, all others "
            "اصلية; no repeal of any predecessor. DISTINCT from child_protection_law (they "
            "share only a co-amendment link via decree M/72). See "
            "verification_methodology_note and known_unresolved_discrepancies in the "
            "source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Royal Decree M/52 (15/11/1434H), CoM Resolution 332 (19/10/1434H), published "
            "Umm al-Qura 24/12/1434H; amended by Royal Decree M/72 (6/8/1443H) / CoM "
            "Resolution 427 (5/8/1443H) for arts 7, 12, 13. Original full text from an "
            "official Ministry of Finance regulations-library PDF (mof.gov.sa, Diwan Malaki "
            "circular 41930) cross-checked against nezams.com; amendment confirmed via the "
            "Umm al-Qura official gazette (uqn.gov.sa) X nezams.com. laws.boe.gov.sa "
            "dedicated lawId page (83f450eb-7985-461f-b053-a9a700f2ba08) unreachable this "
            "pass (live 503; Wayback egress-blocked, not bypassed) -> TIER_2")

SRC_AUTH_AR = ("المرسوم الملكي رقم م/52 وتاريخ 15/11/1434هـ، وقرار مجلس الوزراء رقم 332 وتاريخ "
               "19/10/1434هـ (منشور بأم القرى 24/12/1434هـ)؛ عُدلت المواد 7 و12 و13 بالمرسوم "
               "الملكي رقم م/72 وتاريخ 6/8/1443هـ (قرار مجلس الوزراء 427، 5/8/1443هـ). النص "
               "الأصلي الكامل من PDF رسمي بمكتبة أنظمة وزارة المالية (mof.gov.sa، تعميم الديوان "
               "الملكي 41930) متقاطع مع nezams.com؛ التعديل مؤكد من الجريدة الرسمية أم القرى "
               "(uqn.gov.sa) وnezams.com. الصفحة المخصصة على laws.boe.gov.sa "
               "(lawId 83f450eb-7985-461f-b053-a9a700f2ba08) غير قابلة للوصول هذه الجولة "
               "(503 حيا، ولقطة Wayback محظورة ولم تُتجاوَز) -- TIER_2")


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
        ver.append({"law_key": "protection_from_abuse", "law_component": "law",
                    "language": "ar",
                    "record_layer": "PROTECTION_FROM_ABUSE_LAW_ARABIC_VERIFIED_TEXT",
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
                    "record_id": "protection-from-abuse-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "protection_from_abuse/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الحماية من الإيذاء" % a["number_label_ar"]],
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
    json.dump({"law_key": "protection_from_abuse",
               "layer": "PROTECTION_FROM_ABUSE_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-protection-from-abuse-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 مادة؛ 14 أصلية، 3 معدلة)",
               "title_en": ("Law of Protection from Abuse — Arabic LLM-ready layer "
                            "(17 records: 14 original, 3 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 17], "text_status": STATUS_AMENDED_DATED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Protection from Abuse Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
