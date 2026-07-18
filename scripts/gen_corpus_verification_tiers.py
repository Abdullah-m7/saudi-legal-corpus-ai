#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Verification Tiers — Derived, Additive Classification Layer

Reads the canonical corpus registry (data/corpus_registry/corpus_registry.json) and derives
a SMALL, FIXED, queryable confidence taxonomy for all 121 tracks, so a downstream consumer
(e.g. a RAG application) can filter programmatically (e.g. "Tier 1 only").

This is a READ-ONLY, PURELY ADDITIVE derived layer:
  - It does NOT modify any of the 121 existing track files, the registry, or any track's own
    official_text_status / source_authority / notes / official_source.json.
  - It does NOT recompute or second-guess any track's own per-article verification data
    (e.g. Traffic Law's `verification_tier` field, Capital Market Law's 12 flagged articles,
    Income Tax's Chapter 10 gap) — those already live in each track's own official_source.json.
    Here we only flag `has_per_article_variation=true` and point back at that track's own
    documentation with a one-line note.

TAXONOMY (4 fixed tiers — see reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md
for the full Arabic write-up of the judgment calls behind every non-obvious assignment):

  TIER_1_PRIMARY_MULTI_SOURCE
      2+ independently-produced OFFICIAL/PRIMARY sources agree with no unresolved reachability
      gap: e.g. MOJ portal database cross-checked against the MOJ's own published PDF; two
      different government authorities (BOE + ZATCA/SAMA/MISA/MCIT/MOF/CMA/HRSD/Board of
      Grievances/SDAIA) agreeing; or a single official PDF verified via an independent
      OCR / rendered-page-image pass of the SAME official document. A private secondary
      aggregator (nezams.com, qadha.org.sa, wikisource, law-firm blogs, etc.) is never one of
      the two legs required for Tier 1.

  TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED
      Exactly one official/primary source was reached and used as the governing text, cross-
      verified against non-governmental secondary/reference sources (nezams.com, qadha.org.sa,
      FAOLEX structural checks, press corroboration, etc.). No second independent OFFICIAL
      source confirms the wording.

  TIER_3_SECONDARY_MULTI_SOURCE_ONLY
      The primary official portal (typically BOE) was confirmed UNREACHABLE this build pass;
      the text rests entirely on 2+ independent non-governmental secondary sources agreeing
      with each other, with zero primary-source confirmation obtained.

  TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE
      Single-sourced (primary or secondary) for a meaningfully-sized part of the track with no
      cross-check at all, AND/OR the track's own official_text_status is explicitly a
      documented mixed/per-article-confidence split (e.g. Traffic Law, Capital Market Law,
      Anti-Bribery Law, Income Tax's Chapter 10, Basic Law of Governance, Anti-Harassment Law,
      Shura Council Law). Per the task instructions, per-article-varying tracks are placed here
      using the WEAKEST meaningfully-sized portion, not the strongest.

Reads:
    data/corpus_registry/corpus_registry.json
Writes:
    data/corpus_verification_tiers/corpus_verification_tiers.json

Usage:
    python3 scripts/gen_corpus_verification_tiers.py
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
OUT_DIR = os.path.join(ROOT, "data", "corpus_verification_tiers")
OUT_PATH = os.path.join(OUT_DIR, "corpus_verification_tiers.json")

TIER_1 = "TIER_1_PRIMARY_MULTI_SOURCE"
TIER_2 = "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED"
TIER_3 = "TIER_3_SECONDARY_MULTI_SOURCE_ONLY"
TIER_4 = "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE"

TIER_ORDER = [TIER_1, TIER_2, TIER_3, TIER_4]

TAXONOMY_AR = {
    TIER_1: (
        "مصدران رسميان مستقلان على الأقل (أو أكثر) متطابقان دون أي فجوة وصول غير محلولة — "
        "مثل قاعدة بيانات بوابة وزارة العدل مقابل نسخة PDF الرسمية المنشورة من نفس البوابة، أو "
        "هيئة البيعة/هيئة الخبراء (BOE) مقابل جهة حكومية أخرى (زكاة وضريبة وجمارك، ساما، "
        "الاستثمار، الاتصالات...)، أو مستند PDF رسمي واحد تم التحقق منه عبر تمريرة OCR / صور "
        "صفحات مستقلة لنفس المستند الرسمي."
    ),
    TIER_2: (
        "مصدر رسمي أساسي واحد تم الوصول إليه واعتماد نصه الحاكم، مع تدقيق مقارن مقابل مصادر "
        "ثانوية غير حكومية (nezams.com، qadha.org.sa، تغطية صحفية، فحص هيكلي في FAOLEX، إلخ) "
        "دون تأكيد نصي من مصدر رسمي ثانٍ مستقل."
    ),
    TIER_3: (
        "تعذّر الوصول إلى البوابة الرسمية الأساسية (عادة بوابة هيئة الخبراء BOE) في جولة البناء "
        "هذه؛ يستند النص بالكامل إلى مصدرين ثانويين مستقلين (أو أكثر) متطابقين مع بعضهما البعض، "
        "دون أي تأكيد من مصدر رسمي أساسي."
    ),
    TIER_4: (
        "أحادي المصدر (رسمي أو ثانوي) لجزء ذي حجم معتبر من المسار دون أي تدقيق مقارن، و/أو "
        "المسار موثّق صراحة بأنه ذو ثقة متفاوتة على مستوى المادة (مثل نظام المرور، نظام السوق "
        "المالية، نظام مكافحة الرشوة، الفصل العاشر من نظام ضريبة الدخل، النظام الأساسي للحكم، "
        "نظام مكافحة جريمة التحرش، نظام مجلس الشورى)."
    ),
}

# ---------------------------------------------------------------------------
# Mapping from each track's own `official_text_status` string (as authored in
# corpus_registry.json) to a tier. One entry per DISTINCT status string found in the
# registry. Where a status string is shared by multiple tracks (e.g. the 64 tracks using
# the MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF "double-official" pipeline), this single
# mapping entry covers all of them.
# ---------------------------------------------------------------------------
STATUS_TIER_MAP = {
    # --- Tier 1: 2+ genuinely official/primary sources agree, or a primary PDF verified
    #     via an independent OCR/image pass of the same document, no reachability gap. ---
    "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF": TIER_1,
    "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED": TIER_1,
    "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT": TIER_1,
    "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF": TIER_1,
    "OWNER_PROVIDED_CROSS_CHECKED_MOJ_PORTAL": TIER_1,
    "MIRROR_TEXT_CROSS_CHECKED_AGAINST_OFFICIAL_MOF_PDF": TIER_1,
    "REEXTRACTED_FROM_OFFICIAL_MOF_PDF_CROSS_CHECKED": TIER_1,
    "HRSD_CONSOLIDATED_CROSS_CHECKED_BOE": TIER_1,
    "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED_LAW_QUOTES": TIER_1,
    "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED": TIER_1,
    "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED": TIER_1,
    "HRSD_OFFICIAL_PDF_ACTUALTEXT_OCR_IMAGE_CROSS_CHECKED": TIER_1,
    "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED_BILINGUAL_FORM": TIER_1,
    "BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED": TIER_1,
    "BOE_PORTAL_TRIPLE_SOURCE_EXHAUSTIVE_VERIFIED": TIER_1,
    "BOE_PORTAL_PRIMARY_SOURCE_MCIT_PDF_CROSS_CHECKED": TIER_1,
    "GOVERNMENT_AGENCY_OFFICIAL_PDF_PRIMARY_SOURCE_BOE_ARCHIVE_CROSS_VERIFIED": TIER_1,
    "ZATCA_OFFICIAL_PDF_X_BOE_PORTAL_CROSS_VERIFIED": TIER_1,

    # --- Tier 2: one official/primary source reached, cross-checked against secondary /
    #     private-aggregator sources only (nezams.com, qadha.org.sa, FAOLEX structural-only,
    #     press corroboration, etc.). ---
    "BOE_WAYBACK_SNAPSHOT_UNODC_ENGLISH_SUBSTANCE_VERIFIED": TIER_2,
    "DUAL_PRIMARY_SOURCE_BOE_WAYBACK_X_NEZAMS_CROSS_VERIFIED": TIER_2,
    "SAMA_OFFICIAL_PDF_OCR_X_NEZAMS_CROSS_VERIFIED": TIER_2,
    "BOE_PORTAL_WAYBACK_X_FAOLEX_CROSS_VERIFIED": TIER_2,
    "MISA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_2,
    "BOE_PORTAL_WAYBACK_X_NEZAMS_CROSS_VERIFIED": TIER_2,
    "BOE_PROXY_X_NEZAMS_X_QADHA_REFERENCE_TRIPLE_VERIFIED": TIER_2,
    "BOE_WAYBACK_X_GREEN_ORG_PDF_X_NEZAMS_TRIPLE_VERIFIED_ART1_BOE_SELF_CONTRADICTION": TIER_2,
    "BOE_WAYBACK_X_NEZAMS_FULL_CROSS_VERIFIED": TIER_2,
    "BOE_WAYBACK_X_NEZAMS_SPOTCHECK_X_OKAZ_ALRIYADH_CORROBORATED": TIER_2,

    # --- Tier 3: primary official portal confirmed unreachable; 2+ independent secondary
    #     sources agree with each other, with zero primary confirmation. ---
    "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_3,
    "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_3,
    "SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_3,

    # --- Tier 4: single-sourced for a meaningful part, and/or explicit mixed/per-article
    #     confidence split documented in the track's own official_text_status. ---
    "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER": TIER_4,
    "SINGLE_PRIMARY_SOURCE_WIPO_STRUCTURAL_CROSS_CHECK_MANUAL_LIGATURE_CORRECTION": TIER_4,
    "SECONDARY_SOURCE_STRUCTURAL_WIPO_CROSS_CHECK_BOE_UNREACHABLE": TIER_4,
    "WIPO_LEX_PRIMARY_PDF_X_BOE_STATUS_CARD_CROSS_VERIFIED": TIER_4,
    "BOE_PORTAL_PROXY_RETRIEVED_QANONIAH_SPOT_CROSS_VERIFIED": TIER_4,
    "NEZAMS_PRIMARY_X_RAKADVOCATE_SPOT_CHECKED": TIER_4,
    "BOE_PROXY_X_NEZAMS_PATTERN_VERIFIED_MIXED_CONFIDENCE": TIER_4,
    "BOE_WAYBACK_X_ZATCA_PDF_X_GSTC_PDF_X_NEZAMS_CROSS_VERIFIED_CH10_BOE_ONLY": TIER_4,
    "BOE_WAYBACK_PRIMARY_X_NEZAMS_SPOTCHECK_X_QANOONSA_STRUCTURE_VERIFIED": TIER_4,
    "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_VERIFIED": TIER_4,
    "WIPOLEX_M45_CONSOLIDATED_X_BOE_PLAINTEXT_STALE_TERMINOLOGY_CROSS_VERIFIED": TIER_4,
    "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE": TIER_4,
}

# Tracks whose `official_text_status` field is absent (None) in the registry — these are the
# 4 earliest/foundational tracks, predating the official_text_status verification-tiering
# convention used by every other track. Assigned by directly reading their own notes /
# manifests (see METHODOLOGY doc): companies_law's own law-profile records
# official_source_status="ingested_unverified"; the two implementing-regulations tracks have
# a single official source (Umm Al-Qura Gazette) with only internal hash/record-count
# integrity checks (not independent cross-verification); the closure-audit track inherits
# the tier of the two tracks it audits.
NULL_STATUS_TRACK_TIER = {
    "companies_law": TIER_4,
    "implementing_regulations_general": TIER_4,
    "implementing_regulations_listed_joint_stock": TIER_4,
    "implementing_regulations_arabic_program_closure": TIER_4,
}

# Custom, track-specific rationale text overriding the generic per-tier template below.
# Used where the generic template would be too thin to let the repo owner audit the call.
RATIONALE_OVERRIDE = {
    "companies_law": (
        "لا يحمل official_text_status قيمة مسجّلة لهذا المسار (من أقدم مسارات المدونة، سابق "
        "لاعتماد حقل official_text_status). ملف بيانات القانون الخاص به يسجّل صراحة "
        "official_source_status='ingested_unverified' للنص العربي المقدَّم من المالك، ولا يوثّق "
        "أي تدقيق مقارن مقابل مصدر مستقل ثانٍ."
    ),
    "implementing_regulations_general": (
        "لا يحمل official_text_status قيمة مسجّلة. المصدر الوحيد هو نسخة أم القرى الرسمية "
        "(uqn.gov.sa)؛ تقرير إغلاق البرنامج (closure audit) يتحقق فقط من تطابق البصمة الرقمية "
        "(hash) الداخلية للنص المُستوعَب مع نفسه، وليس من تدقيق مقارن مقابل نسخة مستقلة ثانية."
    ),
    "implementing_regulations_listed_joint_stock": (
        "لا يحمل official_text_status قيمة مسجّلة. المصدر الوحيد هو نسخة أم القرى الرسمية "
        "(uqn.gov.sa) الصادرة عن مجلس هيئة السوق المالية؛ تقرير إغلاق البرنامج يتحقق فقط من "
        "تطابق البصمة الرقمية الداخلية، وليس من تدقيق مقارن مقابل نسخة مستقلة ثانية."
    ),
    "implementing_regulations_arabic_program_closure": (
        "مسار تدقيق إغلاق مشتق (closure/status audit) يراجع اكتمال المسارين العامّ والخاص "
        "بشركات المساهمة المدرجة فقط؛ لا يحمل هو نفسه نصاً قانونياً أساسياً، ويرث تصنيف "
        "المسارين اللذين يدقّقهما."
    ),
    "board_of_grievances_law": (
        "official_text_status='BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED': "
        "25 من 26 مادة تحققت عبر قناتين رسميتين لنفس الجهة (ملف DOCX الرسمي لديوان المظالم "
        "مقابل نسخة PDF الرسمية المعتمدة، بمطابقة بصرية تامة 1.0)، مع تعزيز من WIPO Lex. المادة "
        "الوحيدة المعدَّلة (4) يوثَّق نطاقها وجوهرها رسمياً عبر بيان مجلس الوزراء (SPA)، لكن "
        "صياغتها الحرفية مأخوذة من عرض ثانوي للجريدة الرسمية بمستوى ثقة أدنى قليلاً — موثَّق في "
        "official_source.json الخاص بالمسار."
    ),
    "anti_cyber_crime_law": (
        "official_text_status='BOE_PORTAL_TRIPLE_SOURCE_EXHAUSTIVE_VERIFIED': تحقق شامل (لا "
        "عيّنة) مادة بمادة عبر ثلاثة مصادر رسمية مستقلة (بوابة هيئة الخبراء BOE + ترجمة هيئة "
        "الاتصالات الرسمية عبر WIPO Lex + نسخة موثّقة رسمياً من وزارة المالية)، تطابقت جميعها "
        "حرفياً على كل المواد الـ16 — أقوى تحقق في هذه المدونة."
    ),
    "electronic_transactions_law": (
        "official_text_status يصف نفسه صراحة بأنه 'SINGLE_PRIMARY_SOURCE' (مصدر رسمي واحد "
        "فقط): بوابة BOE تعذّر الوصول إليها، واعتُمد بدلاً منها مستند PDF رسمي بديل (ديوان "
        "الترجمة الرسمية)، مع تدقيق هيكلي فقط (وليس حرفياً) مقابل WIPO Lex، وفجوة موثّقة وغير "
        "محلولة حول ترقيم المواد بعد إلغاء الفصل السادس."
    ),
    "copyright_law": (
        "official_text_status='SECONDARY_SOURCE_STRUCTURAL_WIPO_CROSS_CHECK_BOE_UNREACHABLE': "
        "تعذّر الوصول إلى BOE؛ النص الحرفي الكامل يستند إلى مصدر ثانوي واحد فقط (qadha.org.sa)، "
        "مع تحقق هيكلي فقط (وليس حرفياً) مقابل WIPO Lex وتحقق جزئي من مدونة مقابل الصياغة "
        "القديمة فقط. ملاحظة إضافية: القانون مؤكَّد أنه سيُستبدل اعتباراً من 2026-08-01 بموجب "
        "المرسوم الملكي م/169، الذي لم يتيسّر التحقق من نصه الكامل بعد."
    ),
    "trademark_law": (
        "official_text_status='WIPO_LEX_PRIMARY_PDF_X_BOE_STATUS_CARD_CROSS_VERIFIED': الصياغة "
        "الحرفية الكاملة تستند إلى مصدر واحد (نسخة WIPO Lex)، مع تأكيد حالة 'ساري' فقط (وليس "
        "الصياغة) عبر بطاقة نظام BOE المضمَّنة. تعارض موثَّق وغير محلول مع مصدرين ثانويين "
        "(misa.gov.sa وnezams.com) لا يزالان يعرضان القانون الملغى لعام 2002."
    ),
    "franchise_law": (
        "official_text_status='BOE_PORTAL_PROXY_RETRIEVED_QANONIAH_SPOT_CROSS_VERIFIED': "
        "بوابة BOE (مصدر رسمي) تم الوصول إليها لكامل النص، لكن التدقيق المقارن مع qanoniah.com "
        "اقتصر على 4 من 27 مادة فقط (1، 2، 4، 5)؛ 23 مادة (85%) تبقى أحادية المصدر دون تدقيق "
        "مقارن مستقل."
    ),
    "civil_aviation_law": (
        "official_text_status='NEZAMS_PRIMARY_X_RAKADVOCATE_SPOT_CHECKED': تعذّر الوصول إلى "
        "BOE بالكامل؛ المصدر الفعلي هو موقع ثانوي واحد (nezams.com) لكل المواد الـ180، مع تحقق "
        "مقارن من مصدر ثانٍ (rakadvocate) اقتصر على مادتين فقط (1 و180) — أي أن نحو 99% من "
        "المواد أحادية المصدر الثانوي دون أي تحقق مقارن."
    ),
    "traffic_law": (
        "official_text_status='BOE_PROXY_X_NEZAMS_PATTERN_VERIFIED_MIXED_CONFIDENCE' — ثقة "
        "متفاوتة موثّقة صراحة على مستوى المادة عبر حقل verification_tier الخاص بالمسار نفسه: "
        "67 من 86 سجلاً بتصنيف PRIMARY_INDEPENDENTLY_CONFIRMED مقابل 19 سجلاً بتصنيف "
        "SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE (تعتمد على موثوقية نمط nezams.com وحدها، وبوابة "
        "BOE مؤكَّد أنها متجاوَزة زمنياً لهذا النظام). التصنيف هنا يعتمد الجزء الأضعف."
    ),
    "capital_market_law": (
        "official_text_status='MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER' — أعقد حالة في "
        "هذه المدونة: 55 من 68 سجلاً تحققت جيداً (نص 2003 الأصلي أو نص محدَّث مُستقى من موقع "
        "هيئة السوق المالية)، لكن 12 مادة (المحور الفعلي لإعادة الهيكلة بموجب م/16 لعام 2019) "
        "لم يتيسّر استرجاع صياغتها الحالية، فأُدرجت كنص تاريخي (2003) معلَّم صراحة بأنه ليس "
        "النص الساري؛ وسجل إضافي (المادة 20 مكرر) أُعيد بناؤه من وصف نصي لا من قراءة مباشرة. "
        "التصنيف هنا يعتمد الجزء الأضعف (الـ12 مادة + السجل المُعاد بناؤه)."
    ),
    "anti_bribery_law": (
        "official_text_status='MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER' — أضعف مستوى "
        "تحقق مستخدَم في هذه المدونة على الإطلاق حسب توصيف المسار نفسه: 16 مادة غير معدَّلة "
        "تستند إلى مصدر أساسي واحد (نسخة ممسوحة تحمل شعار هيئة الخبراء) مع تعزيز موضوعي (لا "
        "حرفي) من مصدر ثانٍ، بينما 9 مواد معدَّلة/مضافة تستند إلى تقارب موقعين ثانويين يُشتبه "
        "بأنهما يتشاركان مصدراً واحداً في الأصل — لم يتحقق أي تأكيد أساسي حرفي لأي منها."
    ),
    "income_tax_law": (
        "official_text_status='BOE_WAYBACK_X_ZATCA_PDF_X_GSTC_PDF_X_NEZAMS_CROSS_VERIFIED_"
        "CH10_BOE_ONLY' — يذكر اسم الحالة نفسه الفجوة: 69 من 81 مادة تحققت عبر 3-4 مصادر (BOE "
        "+ زكاة وضريبة وجمارك + gstc.gov.sa + nezams.com)، لكن الفصل العاشر بالكامل (12 مادة، "
        "44-55) يعتمد على مصدرين فقط (BOE + nezams)، إذ اكتفت المصادر الحكومية بإشعار إلغاء "
        "مجرَّد دون النص البديل الكامل؛ كما تحمل 7 مواد أخرى تعديلاً موثَّقاً من حاشية "
        "زكاة/ضريبة/جمارك وحدها دون تأكيد على مستوى الفقرة. التصنيف هنا يعتمد الجزء الأضعف "
        "(الفصل العاشر + المواد السبع)."
    ),
    "environmental_law": (
        "official_text_status يذكر صراحة 'ART1_BOE_SELF_CONTRADICTION': 48 من 49 مادة تطابقت "
        "حرفياً عبر ثلاثة مصادر (BOE عبر أرشيف Wayback + green.org.sa + nezams.com)، لكن تعريف "
        "'الجهة المختصة' في المادة 1 يقوم على تناقض داخلي موثَّق في بيانات BOE نفسها (النص "
        "الأساسي مقابل سجل التعديلات الخاص بها)، حُلّ بالاعتماد على تعزيز ثانوي واحد فقط "
        "(qanoonsa.com)."
    ),
    "social_insurance_law": (
        "official_text_status='BOE_WAYBACK_PRIMARY_X_NEZAMS_SPOTCHECK_X_QANOONSA_STRUCTURE_"
        "VERIFIED': مصدر رسمي (BOE عبر Wayback) اعتُمد للنص الكامل، لكن التدقيق المقارن الحرفي "
        "مقابل nezams.com اقتصر على 5 من 63 مادة فقط؛ الباقي (58 مادة، نحو 92%) أحادي المصدر "
        "الرسمي دون تحقق حرفي مقارن (فقط تأكيد هيكلي من qanoonsa.com)."
    ),
    "social_insurance_legacy_law": (
        "official_text_status='BOE_WAYBACK_X_NEZAMS_SPOTCHECK_X_OKAZ_ALRIYADH_CORROBORATED': "
        "مصدر رسمي (BOE عبر Wayback) لكامل النص، مع تدقيق مقارن حرفي عبر nezams.com لأكثر من "
        "20 من 71 مادة إضافة إلى 100% من سجلات تعديل المواد التسع المعدَّلة/المضافة، وتعزيز "
        "صحفي مستقل (عكاظ/الرياض) لصياغة المادة 37 تحديداً — تغطية أقوى من أغلب مسارات "
        "nezams-فقط، لكنها تبقى دون التأكيد الرسمي المزدوج الكامل."
    ),
    "zakat_law": (
        "official_text_status='ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_VERIFIED': بوابة "
        "هيئة الخبراء (BOE) تعذّر الوصول إليها عبر جولتي بحث وبناء منفصلتين (503 في كل مرة)؛ "
        "الصياغة الحرفية الكاملة للمواد الـ128 تستند إلى مصدر رسمي واحد فقط (نسخة PDF الرسمية "
        "من ZATCA)، وبوابة أم القرى (uqn.gov.sa) استُخدمت فقط للتحقق الموجَّه من حقيقتين محددتين "
        "(تاريخ القرار 1007 وعنوان المادة 13)، وليس كتدقيق حرفي كامل ثانٍ — أدنى من TIER_2 التي "
        "تتطلب تدقيقاً مقارناً شاملاً، وليس موضعياً فقط."
    ),
    "customs_law": (
        "official_text_status='ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE': "
        "بوابة هيئة الخبراء (BOE) تعذّر الوصول إليها في جولة البناء هذه (إعادة تعيين اتصال "
        "curl، وخطأ 503 عبر WebFetch)؛ الصياغة الحرفية الكاملة لكل المواد تستند إلى مصدر "
        "رسمي واحد فقط (نسخة PDF الرسمية الموحَّدة من ZATCA، مشتركة مع مسار اللائحة "
        "التنفيذية)، دون أي تدقيق مقارن من مصدر ثانٍ إطلاقاً — لا حتى تحقق موضعي كما في "
        "نظام جباية الزكاة، بل غياب كامل للتدقيق المقارن."
    ),
    "customs_regulation": (
        "official_text_status='ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE': نفس "
        "تصنيف نظام الجمارك الموحد (customs_law) — مصدر واحد فقط (نسخة ZATCA الرسمية "
        "المشتركة)، بوابة BOE متعذرة الوصول، دون أي تدقيق مقارن مستقل."
    ),
    "patent_law": (
        "official_text_status='WIPOLEX_M45_CONSOLIDATED_X_BOE_PLAINTEXT_STALE_TERMINOLOGY_"
        "CROSS_VERIFIED': الصياغة الحالية الحاكمة لكل المواد الـ66 تستند إلى مصدر واحد (نسخة "
        "WIPO Lex الموحَّدة حتى التعديل 2023)، وإن جرى التحقق منها عبر ثلاث طرق استخراج مستقلة "
        "لنفس المستند (تمريرتا OCR + استخراج طبقة النص الأصلية). بوابة BOE (مصدر رسمي ثانٍ) "
        "مؤكَّدة أنها متجاوَزة زمنياً على محورين: لم تُدرِج تعديل 2023 إطلاقاً، ولثلاث من أربع "
        "مواد عُدِّلت 2018 (35، 42، 63) يعرض نصها المعروض صياغة ما قبل 2018 رغم أن سجل تعديلاتها "
        "الخاص يصف التعديل بشكل صحيح — فهي تؤكد المعلومات الوصفية وتاريخ التعديل والصياغة "
        "الأصلية القابلة للاسترجاع، لا الصياغة الحالية. أقرب لنمط نظام العلامات التجارية "
        "(WIPO Lex أساسي x بطاقة حالة BOE) من نمط تحقق مزدوج رسمي كامل."
    ),
    "anti_fraud_law": (
        "official_text_status='SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE': "
        "بوابة هيئة الخبراء (BOE) تعذّر الوصول إليها في جولتي بحث وبناء منفصلتين (503 عند "
        "رابطين مختلفين)؛ الصياغة الحرفية الكاملة للمواد الـ30 تستند إلى ثلاثة مصادر ثانوية "
        "مستقلة متقاربة فيما بينها (nezams.com، mustsharik.com، mohamah.net)، دون أي تأكيد "
        "أولي من مصدر رسمي إطلاقاً — يطابق تعريف TIER_3 تماماً (مصدر رسمي متعذر + مصدرين "
        "ثانويين فأكثر متقاربين)، مثل نمط triple_arabic_secondary المستخدم لمسارات أخرى. "
        "التعديل الثاني للمادة الخامسة (إضافة وزارة الصحة) يبقى محل خلاف غير محسوم بين "
        "المصادر الثانوية نفسها على نوع الأداة التشريعية ورقمها — موثَّق شفافاً في "
        "known_unresolved_discrepancies الخاص بالمسار، لا مخفياً."
    ),
}

# Tracks with documented, non-negligible confidence variation ACROSS the articles WITHIN the
# same track (as opposed to a uniform track-wide tier). `has_per_article_variation=true` for
# these; the note points back at the track's own official_source.json rather than
# recomputing anything.
PER_ARTICLE_VARIATION_NOTE = {
    "board_of_grievances_law": (
        "المادة 4 (المعدَّلة الوحيدة) موثَّقة بمستوى ثقة أدنى قليلاً من بقية الـ25 مادة "
        "(verified_against_wipo_lex + مطابقة بصرية 1.0)؛ راجع official_source.json الخاص "
        "بالمسار."
    ),
    "basic_law_of_governance": (
        "المادة 5 تحمل verification_tier مختلفاً (SECONDARY_SOURCE_PLUS_PRIMARY_OCR_CONFIRMED_"
        "AMENDMENT) عن بقية الـ82 مادة (BOE + تدقيق عيّني موسّع مقابل WIPO Lex)؛ راجع "
        "official_source.json الخاص بالمسار."
    ),
    "anti_harassment_law": (
        "المادة 6 (فقرتها المضافة) تستند إلى تقارب صحفي/عنوان الجريدة الرسمية لا إلى نص أساسي "
        "مقروء مباشرة، خلافاً للمواد السبع الأخرى (بوابة BOE + تعدد مصادر ثانوية)؛ راجع "
        "official_source.json الخاص بالمسار."
    ),
    "shura_council_law": (
        "المادة 3 (نصها الحالي المعدَّل 2013) مؤكَّدة عبر مصدر حكومي أساسي (وكالة الأنباء "
        "السعودية)، بينما بقية الـ29 مادة تستند إلى تقارب ثلاثة مصادر ثانوية فقط، مع فجوة "
        "مصدرية غير محلولة لتعديل 1422هـ؛ راجع official_source.json الخاص بالمسار."
    ),
    "capital_market_law": (
        "12 من 68 سجلاً (المواد 1، 20-23، 25-30، 59) أُدرجت كنص تاريخي 2003 معلَّم صراحة، "
        "وسجل إضافي (20 مكرر) أُعيد بناؤه من وصف؛ لكل منها verification_tier خاص به مختلف عن "
        "بقية المسار؛ راجع official_source.json الخاص بالمسار."
    ),
    "anti_bribery_law": (
        "16 سجلاً غير معدَّل بتصنيف SINGLE_PRIMARY_SOURCE_TOPICAL_CORROBORATION مقابل 9 سجلات "
        "معدَّلة/مضافة بتصنيف SECONDARY_SOURCE_CONVERGENCE_UNVERIFIED_PRIMARY؛ راجع "
        "official_source.json الخاص بالمسار (verification_tier لكل سجل)."
    ),
    "traffic_law": (
        "67 من 86 سجلاً بتصنيف PRIMARY_INDEPENDENTLY_CONFIRMED مقابل 19 سجلاً "
        "(18 مادة معدَّلة + المادة 50 مكرر) بتصنيف SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE؛ "
        "راجع official_source.json الخاص بالمسار (حقل verification_tier لكل سجل)."
    ),
    "income_tax_law": (
        "الفصل العاشر (المواد 44-55، 12 مادة) يعتمد على مصدرين فقط (BOE+nezams) بدل نمط "
        "3-4 مصادر المعتاد في بقية المسار؛ 7 مواد أخرى (9، 12، 13، 17، 43، 63، 65) معلَّمة "
        "معدَّلة استناداً إلى حاشية زكاة/ضريبة/جمارك وحدها؛ راجع official_source.json الخاص "
        "بالمسار."
    ),
    "environmental_law": (
        "المادة 1 (تعريف الجهة المختصة) وحدها تحمل تناقضاً داخلياً موثَّقاً في مصدر BOE "
        "نفسه، محلولاً بتعزيز ثانوي واحد فقط؛ بقية الـ48 مادة تطابقت حرفياً عبر ثلاثة مصادر "
        "مستقلة؛ راجع official_source.json الخاص بالمسار."
    ),
    "social_insurance_law": (
        "5 من 63 مادة فقط (1، 16، 30، 44، 63) خضعت لتدقيق مقارن حرفي مقابل nezams.com؛ "
        "الباقي أحادي مصدر (BOE) مع تأكيد هيكلي فقط؛ راجع official_source.json الخاص بالمسار."
    ),
    "social_insurance_legacy_law": (
        "أكثر من 20 من 71 مادة خضعت لتدقيق مقارن حرفي مقابل nezams.com، إضافة إلى 100% من "
        "سجلات تعديل المواد التسع المعدَّلة/المضافة؛ بقية المواد غير المعدَّلة أحادية مصدر "
        "(BOE) دون تدقيق حرفي مباشر؛ راجع official_source.json الخاص بالمسار."
    ),
    "franchise_law": (
        "4 من 27 مادة فقط (1، 2، 4، 5) خضعت لتدقيق مقارن مقابل qanoniah.com (وعرض ذلك "
        "الموقع نفسه غير مكتمل)؛ 23 مادة أحادية المصدر (BOE) دون تدقيق مقارن؛ راجع "
        "official_source.json الخاص بالمسار."
    ),
    "civil_aviation_law": (
        "مادتان فقط (1 و180) من أصل 180 خضعتا لتدقيق مقارن بين مصدرين ثانويين "
        "(nezams.com وrakadvocate.blogspot.com)؛ بقية المواد أحادية مصدر ثانوي (nezams.com) "
        "دون بوابة BOE أساسية متاحة؛ راجع official_source.json الخاص بالمسار."
    ),
}


def build_entries(registry: dict) -> list[dict]:
    tracks = registry.get("tracks", [])
    entries = []
    for t in tracks:
        track_id = t["track_id"]
        status = t.get("official_text_status")

        if status is None:
            tier = NULL_STATUS_TRACK_TIER.get(track_id, TIER_4)
        else:
            tier = STATUS_TIER_MAP.get(status)
            if tier is None:
                raise SystemExit(
                    f"gen_corpus_verification_tiers: unmapped official_text_status "
                    f"'{status}' for track '{track_id}'. Add it to STATUS_TIER_MAP."
                )

        if track_id in RATIONALE_OVERRIDE:
            rationale = RATIONALE_OVERRIDE[track_id]
        else:
            generic = {
                TIER_1: "مصدران رسميان مستقلان (أو أكثر) متطابقان دون فجوة وصول.",
                TIER_2: "مصدر رسمي واحد، مدقَّق مقارنةً بمصادر ثانوية غير حكومية فقط.",
                TIER_3: "المصدر الرسمي الأساسي متعذّر الوصول؛ الاعتماد كليةً على مصدرين "
                        "ثانويين مستقلين متطابقين.",
                TIER_4: "أحادي المصدر لجزء معتبر من المسار، أو ثقة متفاوتة موثّقة صراحة.",
            }[tier]
            rationale = f"official_text_status='{status}': {generic}"

        has_variation = track_id in PER_ARTICLE_VARIATION_NOTE
        entries.append({
            "track_id": track_id,
            "tier": tier,
            "tier_rationale": rationale,
            "has_per_article_variation": has_variation,
            "per_article_variation_note": PER_ARTICLE_VARIATION_NOTE.get(track_id, ""),
        })
    return entries


def main() -> int:
    if not os.path.isfile(REGISTRY_PATH):
        print(f"ERROR: registry not found at {REGISTRY_PATH}", file=sys.stderr)
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    entries = build_entries(registry)
    entries.sort(key=lambda e: e["track_id"])

    summary = {tier: 0 for tier in TIER_ORDER}
    for e in entries:
        summary[e["tier"]] += 1

    variation_count = sum(1 for e in entries if e["has_per_article_variation"])

    out = {
        "schema_version": "1.0",
        "generated_by": "scripts/gen_corpus_verification_tiers.py",
        "generated_date": registry.get("generated_date"),
        "source_registry": "data/corpus_registry/corpus_registry.json",
        "source_registry_generated_date": registry.get("generated_date"),
        "methodology_doc": "reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md",
        "read_only_derived_layer": True,
        "notes": (
            "Purely additive, derived classification layer. Does not alter any of the 121 "
            "tracks' own official_text_status/source_authority/notes/official_source.json. "
            "Per-article confidence variation already documented inside a track's own "
            "official_source.json is NOT recomputed here; only flagged via "
            "has_per_article_variation with a one-line pointer back to that track."
        ),
        "taxonomy": TAXONOMY_AR,
        "tier_order": TIER_ORDER,
        "total_tracks": len(entries),
        "summary_by_tier": summary,
        "tracks_with_per_article_variation": variation_count,
        "tracks": entries,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}")
    print(f"Total tracks: {len(entries)}")
    for tier in TIER_ORDER:
        print(f"  {tier}: {summary[tier]}")
    print(f"  has_per_article_variation=true: {variation_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
