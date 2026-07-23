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
    "BOE_WAYBACK_PRIMARY_X_BFC_OCR_X_NEZAMS_CROSS_VERIFIED": TIER_1,
    "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503": TIER_2,
    "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_2,
    "BOE_WAYBACK_ARCHIVE_X_SAMA_RULEBOOK_PDF_X_NEZAMS_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_1,
    "BOE_WAYBACK_ARCHIVE_X_NEZAMS_X_BOE_OFFICIAL_ENGLISH_TRANSLATION_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_1,
    "BOE_WAYBACK_ARCHIVE_X_SOCPA_OFFICIAL_PDF_X_QANOONSA_CROSS_VERIFIED_BOE_MAIN_BODY_CONFIRMED_STALE_FOR_AMENDED_ARTICLES": TIER_1,
    "BOE_WAYBACK_DUAL_SNAPSHOT_X_FAOLEX_MIRROR_X_NEZAMS_X_QANOONSA_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_2,
    "BOE_WAYBACK_SIX_SNAPSHOT_X_AWQAF_GOV_SCANNED_DECREE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_1,
    "BOE_WAYBACK_THREE_SNAPSHOT_X_SAUDIENG_SA_OFFICIAL_SITE_X_PRESS_CORROBORATION_LIVE_BOE_UNREACHABLE": TIER_1,
    "BOE_WAYBACK_SIX_SNAPSHOT_X_MOMAH_GOV_SA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_1,
    "BOE_NEAR_LIVE_WAYBACK_X_MEDIA_GOV_SA_OFFICIAL_PDF_X_WIPO_LEX_X_NEZAMS_QANOONSA_CURRENCY_CHECKED_CONFIRMED_CURRENT": TIER_1,
    "BOE_WAYBACK_THREE_SNAPSHOT_X_SAUDIENG_SA_OFFICIAL_PDF_X_QANOONSA_QANONIAH_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE": TIER_1,
    "BOE_WAYBACK_THREE_SNAPSHOT_X_NEZAMS_X_INDEPENDENT_NEWS_CORROBORATION_LIVE_BOE_UNREACHABLE": TIER_2,
    "PREMIUM_RESIDENCY_LAW_BOE_LIVE_UNREACHABLE_WAYBACK_MULTI_SNAPSHOT_2019_2025_X_MISA_OFFICIAL_CONSOLIDATED_PDF_CROSS_VERIFIED": TIER_1,

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
    "BOE_WAYBACK_SEVEN_SNAPSHOT_X_QANOONSA_COM_RESOLUTION_805_X_NEZAMS_CROSS_VERIFIED": TIER_2,
    "SFDA_PDF_VISUAL_TRANSCRIPTION_SINGLE_SOURCE_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE": TIER_2,
    "HRSD_GOV_SA_PRIMARY_X_QANOONSA_LEXISMIDDLEEAST_CROSS_VERIFIED_BOE_CONFIRMED_STALE_FOR_THIS_TOPIC": TIER_2,
    "BOE_WAYBACK_THREE_SNAPSHOT_X_NEZAMS_QISTAS_X_UMM_AL_QURA_GAZETTE_M11_AMENDMENT_CROSS_VERIFIED": TIER_2,
    "NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QISTAS_STRUCTURAL_PARTIAL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED": TIER_2,
    "NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QANOONSA_STRUCTURAL_FULL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED": TIER_2,
    "SFDA_GOV_SA_BORN_DIGITAL_PDF_2025_06_UPLOAD_X_QANOONSA_COM_X_QISTAS_COM_CROSSCHECK_BOE_NO_DEDICATED_LAWID_LIVE_UNREACHABLE_WAYBACK_CONTENT_BLOCKED": TIER_2,

    # --- Tier 3: primary official portal confirmed unreachable; 2+ independent secondary
    #     sources agree with each other, with zero primary confirmation. ---
    "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_3,
    "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_3,
    "SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE": TIER_3,
    "TIER_3_SECONDARY_MULTI_SOURCE_ONLY_BOE_DOES_NOT_INDEX_THIS_LAW_MOI_PDF_UNREACHABLE": TIER_3,
    "NEZAMS_X_QANOONSA_COM_RESOLUTION_151_CROSS_VERIFIED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE": TIER_3,
    "QANOONSA_COM_RAW_HTML_DIRECT_FETCH_MAR2026_PUBLISH_APR2026_WAYBACK_JUL2026_LIVE_STABLE_X_NCAR_GOV_SA_OFFICIAL_ARCHIVE_METADATA_CROSSCHECK_X_QANONIAH_COM_INDEX_CONFIRM_BOE_NO_DEDICATED_LAWID_MOI_GDP_UNREACHABLE_UQN_GOV_SA_REACHABLE_BUT_SPECIFIC_GAZETTE_PAGE_NOT_LOCATED_THIS_PASS": TIER_3,
    "MOI_GOV_SA_WAYBACK_TRIPLE_SNAPSHOT_BYTE_IDENTICAL_X_NEZAMS_DECREE_CONFIRM_X_ALRIYADH_2005_CONTEMPORANEOUS_FULLTEXT_CROSSVERIFIED_BOE_NO_DEDICATED_PAGE": TIER_2,
    "NEZAMS_COM_SINGLE_FULLTEXT_AGGREGATOR_BOE_UNREACHABLE_MULTISOURCE_METADATA_CROSSCHECK_CONFIRMED_M44_SUPERSEDES_M56": TIER_3,
    "NEZAMS_COM_INDEPENDENT_AGGREGATOR_BOE_DEDICATED_PAGE_EXISTS_BUT_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_MULTISOURCE_METADATA_CROSSCHECK_VIA_WEBSEARCH": TIER_3,
    "ZATCA_GOV_SA_OFFICIAL_CONSOLIDATED_PDF_TENTH_EDITION_2025_04_DUAL_PYMUPDF_GEOMETRIC_X_TESSERACT_OCR_RECONCILED_BOE_NO_DEDICATED_LAWID_PAGE": TIER_3,
    "ZATCA_GOV_SA_X_GSTC_GOV_SA_DUAL_GOVERNMENT_COPY_CROSSCHECK_PYMUPDF_COORDINATE_RECONSTRUCTION_BOE_NO_DEDICATED_LAWID_PAGE": TIER_3,
    "NEZAMS_COM_SINGLE_FULLTEXT_AGGREGATOR_BOE_UNREACHABLE_MULTISOURCE_METADATA_CROSSCHECK_MISA_ENGLISH_PDF_CONFIRMS_STRUCTURE": TIER_3,
    "QANONIAH_COM_PRIMARY_X_WIPO_LEX_OFFICIAL_ARABIC_PDF_DUAL_INDEPENDENT_SOURCE_PARTIAL_SCOPE_ARTS_1_5_OF_90_BOE_NO_DEDICATED_LAWID_PAGE_GAC_ISSUER_UNREACHABLE": TIER_2,
    "AML_GOV_SA_SCANNED_PDF_X_QANONIAH_COM_BORN_DIGITAL_API_RECONCILED_10_OF_25_ARTICLES_OCR_ADJUDICATED_15_BOE_NO_DEDICATED_LAWID_PAGE": TIER_3,
    "WIPO_LEX_OFFICIAL_SAIP_LETTERHEAD_PDF_DUAL_INDEPENDENT_EXTRACTION_PIPELINE_RECONCILED_X_QANOONSA_STRUCTURAL_CROSSCHECK_BOE_NO_DEDICATED_LAWID_PAGE": TIER_3,
    "MC_GOV_SA_OFFICIAL_BORN_DIGITAL_PAGE_X_MINISTRY_OWN_SCANNED_PDF_WORD_FOR_WORD_CROSSCHECK_X_QANONIAH_LEXISMIDDLEEAST_ARGAAM_MITHAQ_BOE_NO_DEDICATED_LAWID_PAGE": TIER_1,
    "FRANCHISING_SA_UMM_AL_QURA_GAZETTE_REPRODUCTION_X_AUNKLAW_VERBATIM_CROSSCHECK_X_LEXISMIDDLEEAST_STRUCTURAL_BOE_LAWID_PAGE_ONLY_FOR_BASE_LAW": TIER_2,
    "MOI_OFFICIAL_SCANNED_DOCUMENT_DUAL_VISION_OCR_PIPELINE_X_QANONIAH_COM_BORN_DIGITAL_PARTIAL_CROSSCHECK_ARTS_1_8_OF_86_BOE_NO_DEDICATED_LAWID_PAGE": TIER_3,
    "QANOONSA_COM_PRIMARY_UMM_AL_QURA_5057_REPRODUCTION_X_QISTAS_COM_PARTIAL_CROSSCHECK_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE": TIER_2,
    "QANOONSA_COM_CONSOLIDATED_TEXT_X_QISTAS_COM_APPENDIX_CROSSCHECK_BOE_NO_DEDICATED_LAWID_PAGE": TIER_2,
    "UMM_AL_QURA_GAZETTE_4888_OFFICIAL_HTML_X_OFFICIAL_BORN_DIGITAL_PDF_DUAL_RENDERING_SAME_ISSUE_996_PERCENT_WORDLEVEL_BOE_NO_DEDICATED_LAWID_PAGE": TIER_1,
    "MEWA_GOV_SA_OFFICIAL_BORN_DIGITAL_PDF_X_QANONIAH_COM_WORDLEVEL_CROSSCHECK_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE": TIER_2,
    "MEWA_OFFICIAL_SCANNED_DECISION_PDF_VISUALLY_READ_X_QANONIAH_COM_CLEAN_HTML_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE": TIER_2,
    "QANONIAH_COM_PRIMARY_TEXT_MULTISOURCE_CITATION_CROSSCHECK_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE": TIER_2,

    # --- Tier 4: single-sourced for a meaningful part, and/or explicit mixed/per-article
    #     confidence split documented in the track's own official_text_status. ---
    "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER": TIER_4,
    "QANONIAH_COM_PUBLIC_API_10_ITEM_PREVIEW_CAP_PARTIAL_COVERAGE_ARTICLES_2_11_BOE_NO_DEDICATED_PAGE_ISTITLAA_UNREACHABLE_WAYBACK_BLOCKED": TIER_4,
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
    "BOE_WAYBACK_ARCHIVE_PRIMARY_X_QISTAS_PARTIAL_STRUCTURAL_CROSSCHECK_LIVE_BOE_UNREACHABLE_M7_1434H_AMENDED_TEXT_NOT_INCORPORATED": TIER_4,
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
    "cooperative_health_insurance_law": (
        "official_text_status='BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503': "
        "بوابة هيئة الخبراء (BOE) الحية متعذرة الوصول (إعادة تعيين اتصال)، لكن نسخة "
        "أرشيف Wayback Machine لصفحة BOE نفسها كانت متاحة (تطلّب رابط http:// وليس "
        "https://) واستُخدمت كمصدر رسمي أساسي واحد، وقورنت حرفياً مع مصدر ثانوي واحد "
        "(nezams.com) — مصدر رسمي واحد + تدقيق مقارن ثانوي، يطابق تعريف TIER_2 "
        "تماماً. نص تعديل المادة الرابعة لعام 1440هـ يستند إلى nezams.com حصراً "
        "(بوابة BOE تذكر القرار 472 دون إيراد نصه)؛ راجع has_per_article_variation "
        "لهذا التمايز."
    ),
    "healthcare_professions_law": (
        "official_text_status='BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_"
        "UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية متعذرة الوصول، لكن نسخة أرشيف "
        "Wayback Machine لصفحة BOE نفسها كانت متاحة عبر https:// (وليس http://، عكس "
        "النمط الملحوظ في مسار الضمان الصحي التعاوني) واستُخدمت كمصدر رسمي أساسي "
        "واحد، وقورنت مع مصدر ثانوي واحد (nezams.com، جلب حي) — مصدر رسمي واحد + "
        "تدقيق مقارن ثانوي، يطابق تعريف TIER_2؛ عُزِّز التطابق الهيكلي (الفصول/"
        "الفروع) إضافة بمقارنة بنية موقع وزارة الصحة الرسمي (moh.gov.sa) دون "
        "اعتماده كمصدر نصي مستقل ثانٍ."
    ),
    "finance_lease_law": (
        "official_text_status='BOE_WAYBACK_ARCHIVE_X_SAMA_RULEBOOK_PDF_X_NEZAMS_"
        "TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية "
        "متعذرة الوصول، لكن نسخة أرشيف Wayback Machine لصفحة BOE نفسها كانت "
        "متاحة عبر https:// واستُخدمت كمصدر رسمي أساسي، وقورنت مع مصدر رسمي "
        "ثانٍ (نسخة PDF الرسمية من دليل مؤسسة النقد rulebook.sama.gov.sa) ومصدر "
        "ثالث ثانوي (nezams.com، جلب حي) — مصدران رسميان متقاربان + تدقيق "
        "ثانوي، يطابق تعريف TIER_1 (مصدرين رسميين فأكثر متقاربين)، مماثل لنمط "
        "finance_companies_law (BOE عبر Wayback × bfc.gov.sa)."
    ),
    "maritime_commercial_law": (
        "official_text_status='BOE_WAYBACK_ARCHIVE_X_NEZAMS_X_BOE_OFFICIAL_"
        "ENGLISH_TRANSLATION_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE': بوابة هيئة "
        "الخبراء (BOE) الحية متعذرة الوصول، لكن نسختي أرشيف Wayback Machine "
        "لصفحة BOE العربية وترجمتها الإنجليزية الرسمية كانتا متاحتين عبر "
        "https:// — مصدران رسميان (نسخة عربية ونسخة إنجليزية من BOE نفسها) "
        "متقاربان، مع تدقيق مقارن ثانوي (nezams.com) — يطابق تعريف TIER_1 "
        "(مصدرين رسميين فأكثر متقاربين)، رغم أن أحدهما ترجمة إنجليزية لا "
        "نصاً عربياً مستقلاً بالكامل. راجع has_per_article_variation للمواد "
        "316-325 التي اعتُمدت فيها الترجمة الإنجليزية حصراً بدلاً من "
        "nezams.com بسبب خلل تكرار محتوى في ذلك الموقع لهذا النطاق تحديداً."
    ),
    "finance_companies_law": (
        "official_text_status='BOE_WAYBACK_PRIMARY_X_BFC_OCR_X_NEZAMS_CROSS_VERIFIED': "
        "بوابة هيئة الخبراء (BOE) الحية متعذرة الوصول (503 مباشرة، 422 عبر r.jina.ai)، "
        "لكن نسخة أرشيف Wayback Machine لصفحة BOE نفسها كانت متاحة وتُعامَل كمصدر "
        "أساسي، وقورنت برمجياً (فرق نصي مطبَّع) مع نسخة PDF الرسمية من bfc.gov.sa "
        "(نطاق حكومي .gov.sa آخر، حُوِّلت عبر OCR بسبب خط/cmap تالف في النسخة "
        "الأصلية) — مصدران رسميان (نطاقي .gov.sa) متقاربان دون أي فارق جوهري عبر "
        "الأربعين مادة الأصلية، وهو ما يطابق تعريف TIER_1 (مصدرين رسميين متقاربين). "
        "لكن نص تعديل 2024 (المرسوم الملكي م/272) نفسه لا يستند إلا إلى مصدر ثانوي "
        "واحد (qanoonsa.com) مقارَناً بمصدر ثانوي آخر (حواشي nezams.com) — دون أي "
        "تأكيد رسمي مباشر لنص هذا التعديل تحديداً؛ راجع has_per_article_variation "
        "لهذا التمايز."
    ),
    "gcc_anti_dumping_law": (
        "official_text_status='BOE_WAYBACK_ARCHIVE_PRIMARY_X_QISTAS_PARTIAL_STRUCTURAL_"
        "CROSSCHECK_LIVE_BOE_UNREACHABLE_M7_1434H_AMENDED_TEXT_NOT_INCORPORATED': بوابة "
        "هيئة الخبراء (BOE) الحية متعذرة الوصول (503)، واعتُمدت نسختا أرشيف Wayback "
        "Machine لنفس صفحة القانون (بفارق ~20 شهراً بينهما) كمصدر أساسي — متطابقتان "
        "تماماً — مع تدقيق هيكلي جزئي فقط من مصدر ثانٍ (qistas.com، المواد 1-3 فقط "
        "وليس النص الكامل). هذا مصدر رسمي أساسي واحد + تدقيق ثانوي جزئي، وهو ما يطابق "
        "تعريف TIER_2 من حيث آلية الجلب وحدها؛ إلا أن هذا المسار يُصنَّف TIER_4 "
        "('أحادي المصدر لجزء ذي حجم معتبر... أو موثّق صراحة بثقة متفاوتة') بسبب اكتشاف "
        "دليل قوي (WIPO Lex + ديباجة قانون سعودي منفصل ونافذ صادر 2022) على أن المرسوم "
        "الملكي م/7 (20/3/1434هـ) اعتمد نسخة معدَّلة من هذا القانون الموحد بهيكل مختلف "
        "(15 مادة بدل 17 وفق نسخة الأمانة العامة لمجلس التعاون الرسمية)، بينما صفحة "
        "BOE الأساسية المعتمدة هنا لا تُشير إطلاقاً إلى م/7 عبر لقطتين بفارق ~20 شهراً. "
        "لم يتسنَّ الحصول على نص أم القرى لـم/7 ولا محتوى فعلي من روابط WIPO Lex "
        "الكاملة (غلاف JS فارغ لكل الروابط المجرَّبة)، فتم اعتماد نص BOE المُتحقَّق منه "
        "الأصلي بدلاً من استبداله بنص التعديل غير المؤكَّد — وهذا بالضبط نمط 'ثقة "
        "متفاوتة على مستوى المسار كاملاً' الذي يبرر TIER_4، مماثل من حيث المبدأ (لا "
        "الحقيقة) لسابقة نظام المرور (traffic_law) في توثيق شك جدي حول حداثة المصدر "
        "دون حسمه ضمناً أو إسقاطه بصمت. راجع known_unresolved_discrepancies في "
        "official_source.json لهذا المسار للتفاصيل الكاملة؛ هذا خطر توثيقي حي غير "
        "مُسوَّى، وليس نتيجة نهائية."
    ),
    "accounting_auditing_law": (
        "official_text_status='BOE_WAYBACK_ARCHIVE_X_SOCPA_OFFICIAL_PDF_X_QANOONSA_CROSS_"
        "VERIFIED_BOE_MAIN_BODY_CONFIRMED_STALE_FOR_AMENDED_ARTICLES': بوابة هيئة الخبراء "
        "(BOE) الحية متعذرة الوصول، لكن نسخة أرشيف Wayback Machine لصفحة BOE نفسها اعتُمدت "
        "كمصدر أساسي، وقورنت بمصدر رسمي ثانٍ (نسخة PDF الرسمية من الهيئة السعودية "
        "للمراجعين والمحاسبين SOCPA نفسها، الجهة المنظِّمة للمهنة) ومصدر ثانوي ثالث "
        "(qanoonsa.com، صفحتان مستقلتان) — مصدران رسميان (BOE وSOCPA) متقاربان على كامل "
        "المواد الـ22، وهو ما يطابق تعريف TIER_1 (مصدرين رسميين فأكثر متقاربين)، مماثل "
        "لنمط finance_companies_law (BOE عبر Wayback × bfc.gov.sa). خلل مؤكَّد (وليس افتراضاً) "
        "على صفحة BOE نفسها: خمس مواد (1، 4، 5، 19، 20) تحمل علامة 'مادة معدَّلة' ونافذة "
        "تعديلات تقتبس نص المرسوم الملكي م/169 (1446هـ) بدقة، بينما النص الرئيسي المعروض "
        "لنفس هذه المواد ظل قديماً (ما قبل م/169) بشكل متطابق حرفياً عبر ثلاث لقطات أرشيفية "
        "بفارق 8+ أشهر — تم اعتماد نص نافذة التعديلات (المؤكَّد عبر PDF الهيئة) لا النص "
        "الرئيسي الراكد. راجع has_per_article_variation للمادة الأولى تحديداً، التي تحمل "
        "تعديلاً ثانياً أحدث (قرار مجلس الوزراء 283، 1447هـ) لم يصل بعد إلى أي لقطة BOE "
        "ويستند فقط إلى PDF الهيئة وqanoonsa.com دون أي تأكيد رسمي مباشر له."
    ),
    "nazaha_law": (
        "official_text_status='BOE_WAYBACK_DUAL_SNAPSHOT_X_FAOLEX_MIRROR_X_NEZAMS_X_"
        "QANOONSA_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية "
        "متعذرة الوصول، واعتُمدت نسختا أرشيف Wayback Machine لصفحة BOE نفسها (بفارق ~15.5 "
        "شهراً بينهما) كمصدر أساسي — متطابقتان حرفياً تماماً — مع نقطة زمنية ثالثة مستقلة "
        "(نسخة PDF مستضافة على FAOLEX تبيّن أنها لقطة متصفح محفوظة لنفس صفحة BOE بتاريخ "
        "جلب مختلف، وليست مصدراً رسمياً مستقلاً بذاته) ومصدرين ثانويين (nezams.com، جزئي "
        "للمواد 1-14 فقط، وqanoonsa.com، تدقيق هيكلي كامل لجميع المواد الـ24). هذا مصدر "
        "رسمي أساسي واحد فعلياً (BOE عبر لقطتين متطابقتين) + تدقيق ثانوي مزدوج، وهو ما "
        "يطابق تعريف TIER_2 (مصدر رسمي أساسي واحد + تدقيق ثانوي) وليس TIER_1، إذ لا يوجد "
        "مصدر رسمي ثانٍ مستقل بذاته (نسخة FAOLEX هي نسخة من نفس محتوى BOE لا مصدراً "
        "مستقلاً). راجع official_source.json الخاص بالمسار لتفاصيل الجهات السابقة "
        "(الهيئة الوطنية لمكافحة الفساد، أ/65 و1432هـ؛ الدمج بموجب أ/277، 1441هـ) والإحالة "
        "الحرجة إلى نص المرسوم الملكي م/25 الذي يُلزم تحديث مسار anti_bribery_law الحالي "
        "بمتابعة مستقلة."
    ),
    "awqaf_law": (
        "official_text_status='BOE_WAYBACK_SIX_SNAPSHOT_X_AWQAF_GOV_SCANNED_DECREE_X_"
        "NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية "
        "متعذرة الوصول، واعتُمدت ست لقطات أرشيف Wayback Machine مستقلة لصفحة BOE نفسها "
        "(تمتد من 21 نوفمبر 2019 إلى 12 ديسمبر 2025) كمصدر أساسي، متطابقة حرفياً على 23 "
        "من 25 مادة عبر كل اللقطات، وقورنت بمصدر رسمي ثانٍ مستقل بذاته (نسخة ممسوحة "
        "ضوئياً للمرسوم الملكي الأصلي الموقّع من الملك سلمان، مستضافة على الموقع الرسمي "
        "لنفس الجهة المنظِّمة web.awqaf.gov.sa، قُرئت بصرياً إذ لا تحوي طبقة نص) ومصدر "
        "ثانوي (nezams.com). مصدران رسميان (BOE وweb.awqaf.gov.sa، نطاق .gov.sa منفصل "
        "فعلياً وليس نسخة من نفس محتوى BOE كحال FAOLEX في مسار nazaha_law) متقاربان، وهو "
        "ما يطابق تعريف TIER_1 (مصدرين رسميين فأكثر متقاربين)، مماثل لنمط "
        "finance_companies_law (BOE عبر Wayback × bfc.gov.sa). راجع "
        "has_per_article_variation للمادتين 6 و21 اللتين تحملان تناقضاً مؤكَّداً (لا "
        "افتراضياً) بين سجل تعديلات BOE ونصه الرئيسي الراكد، مفصَّلاً في "
        "official_source.json الخاص بالمسار."
    ),
    "saudi_engineers_law": (
        "official_text_status='BOE_WAYBACK_THREE_SNAPSHOT_X_SAUDIENG_SA_OFFICIAL_SITE_X_"
        "PRESS_CORROBORATION_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية "
        "متعذرة الوصول، واعتُمدت ثلاث لقطات أرشيف Wayback Machine مستقلة لصفحة BOE "
        "نفسها (تمتد من 15 نوفمبر 2019 إلى 15 سبتمبر 2025) كمصدر أساسي، وقورنت بمصدر "
        "رسمي ثانٍ مستقل بذاته (الموقع الرسمي للهيئة السعودية للمهندسين نفسها "
        "saudieng.sa، ثلاث لقطات 2017-2022، نطاق منفصل فعلياً) ومصدر ثانوي (تغطية "
        "صحفية من الشرق الأوسط للمادة الأولى). مصدران رسميان (BOE وsaudieng.sa) "
        "متقاربان، وهو ما يطابق تعريف TIER_1 (مصدرين رسميين فأكثر متقاربين)، مماثل "
        "لنمط awqaf_law (BOE عبر Wayback × web.awqaf.gov.sa). راجع "
        "has_per_article_variation للمادتين 1 و6 اللتين تحملان تناقضاً مؤكَّداً (لا "
        "افتراضياً) بين سجل تعديلات BOE ونصه الرئيسي الراكد على كل من BOE وموقع "
        "الهيئة نفسه، مفصَّلاً في official_source.json الخاص بالمسار."
    ),
    "municipal_councils_law": (
        "official_text_status='BOE_WAYBACK_SIX_SNAPSHOT_X_MOMAH_GOV_SA_OFFICIAL_PDF_X_"
        "NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية "
        "أعادت خطأ HTTP 503، واعتُمدت ست لقطات أرشيف Wayback Machine مستقلة لصفحة BOE "
        "نفسها (تمتد من 22 نوفمبر 2019 إلى 12 ديسمبر 2025، دون أي فرق نصي أو تعديل "
        "مسجَّل طوال هذه الفترة) كمصدر أساسي، وقورنت بمصدر رسمي ثانٍ مستقل بذاته (موقع "
        "وزارة الشؤون البلدية والقروية والإسكان الرسمي momah.gov.sa، نسختا PDF رسميتان "
        "بتاريخين مستقلين 2022 و2025، نطاق منفصل فعلياً عن BOE) ومصدر ثانوي للمطابقة "
        "(nezams.com). مصدران رسميان (BOE وmomah.gov.sa) متقاربان تماماً (69 مادة دون "
        "أي فارق)، وهو ما يطابق تعريف TIER_1 (مصدرين رسميين فأكثر متقاربين)، مماثل "
        "لنمط awqaf_law وsaudi_engineers_law (BOE عبر Wayback × موقع الجهة الرسمي "
        "الخاص بها). لا يحمل هذا المسار has_per_article_variation إذ لم يُعثر على أي "
        "تعديل مطلقاً منذ صدور النظام، وهو استقرار مؤكَّد إيجابياً وليس افتراضياً، مفصَّل "
        "في official_source.json الخاص بالمسار."
    ),
    "press_law": (
        "official_text_status='BOE_NEAR_LIVE_WAYBACK_X_MEDIA_GOV_SA_OFFICIAL_PDF_X_"
        "WIPO_LEX_X_NEZAMS_QANOONSA_CURRENCY_CHECKED_CONFIRMED_CURRENT': بوابة هيئة "
        "الخبراء (BOE) الحية متعذرة الوصول، واعتُمدت لقطة أرشيف Wayback Machine شبه "
        "حية (26 فبراير 2026، أي قبل هذا البناء بنحو 5 أشهر فقط) كمصدر أساسي، وقورنت "
        "هيكلياً بمصدر رسمي ثانٍ مستقل بذاته (ملف PDF الرسمي لوزارة الإعلام media.gov.sa "
        "لهذا النظام تحديداً، نطاق منفصل فعلياً عن BOE) ومصدرين ثانويين للمطابقة "
        "(WIPO Lex، ومطابقة الرقم والتاريخ بدقة؛ nezams.com/qanoonsa.com). مصدران "
        "رسميان (BOE وmedia.gov.sa) متقاربان، وهو ما يطابق تعريف TIER_1 (مصدرين "
        "رسميين فأكثر متقاربين)، مماثل لنمط awqaf_law وmunicipal_councils_law (BOE "
        "عبر Wayback × موقع الجهة الرسمي الخاص بها). يحمل هذا المسار فحص تحقق من "
        "الحداثة (currency check) أثبت أن النظام لا يزال سارياً رغم وجود مسودة نظام "
        "إعلام شامل لم تُسنّ بعد. لا يحمل has_per_article_variation إذ عولجت جميع "
        "المواد الست المعدَّلة (5، 9، 36، 37، 38، 40) بمنهجية واحدة متسقة (اعتماد نص "
        "سجل التعديلات المقتبس بثقة كاملة)، وليس بثقة متفاوتة لكل مادة، مفصَّل في "
        "official_source.json الخاص بالمسار."
    ),
    "engineering_practice_law": (
        "official_text_status='BOE_WAYBACK_THREE_SNAPSHOT_X_SAUDIENG_SA_OFFICIAL_PDF_X_"
        "QANOONSA_QANONIAH_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء "
        "(BOE) الحية متعذرة الوصول، واعتُمدت ثلاث لقطات أرشيف Wayback Machine مستقلة "
        "لصفحة BOE نفسها (تمتد من 14 نوفمبر 2019 إلى 25 فبراير 2026، نص رئيسي متطابق "
        "حرفياً طوال هذه الفترة) كمصدر أساسي، وقورنت بمصدر رسمي ثانٍ مستقل بذاته (موقع "
        "الهيئة السعودية للمهندسين الرسمي saudieng.sa، ملف PDF مستضاف ذاتياً، لقطة "
        "يونيو 2025، مطابق حرفياً للمواد 2-17) ومصدر ثانوي للمطابقة الهيكلية "
        "(qanoonsa.com/qanoniah.com). مصدران رسميان (BOE وsaudieng.sa) متقاربان، وهو "
        "ما يطابق تعريف TIER_1 (مصدرين رسميين فأكثر متقاربين)، مماثل لنمط "
        "saudi_engineers_law وawqaf_law (BOE عبر Wayback × موقع الجهة الرسمي الخاص "
        "بها). راجع has_per_article_variation للمادة الأولى التي تحمل تناقضاً "
        "ثلاثياً مؤكَّداً (لا افتراضياً) بين نص BOE الرئيسي الراكد، ونص سجل تعديلات "
        "BOE نفسه (الذي لا تتطابق عبارته 'قبل' مع نص BOE الرئيسي عند أي لقطة)، ونص "
        "saudieng.sa الحالي المختلف بدوره — تناقض من نفس فئة سابقة awqaf_law المادة "
        "6، مفصَّل في official_source.json الخاص بالمسار."
    ),
    "nationality_law": (
        "official_text_status='BOE_WAYBACK_THREE_SNAPSHOT_X_NEZAMS_X_INDEPENDENT_NEWS_"
        "CORROBORATION_LIVE_BOE_UNREACHABLE': بوابة هيئة الخبراء (BOE) الحية متعذرة "
        "الوصول، واعتُمدت ثلاث لقطات أرشيف Wayback Machine مستقلة لصفحة BOE نفسها "
        "(تمتد من 19 نوفمبر 2019 إلى 14 يناير 2026) كمصدر رسمي وحيد، وقورنت بمصدر "
        "ثانوي (nezams.com، إعادة إنتاج مستقلة لهوية المرسوم وملاحظات التعديل) "
        "ومصادر ثانوية/صحفية إضافية (Arab News، Amwaj Media، Middle East Monitor، "
        "Investment Migration Council) لتأكيد التعديل الأخير فقط. بخلاف تصنيف "
        "الوكيل الباحث الأولي (الذي اقترح TIER_1)، هذا مصدر رسمي/أساسي **واحد فقط** "
        "(BOE عبر Wayback)، وليس مصدرين رسميين متقاربين — nezams.com والمصادر "
        "الصحفية كلها مجمِّعات/تغطية ثانوية، وليست مصدراً رسمياً مستقلاً بذاته "
        "(بخلاف saudieng.sa أو web.awqaf.gov.sa في مسارات أخرى، وهي مواقع الجهة "
        "التنظيمية نفسها). هذا يطابق تعريف TIER_2 (مصدر رسمي واحد + تدقيق ثانوي)، "
        "مماثل لسابقة nazaha_law (BOE عبر Wayback × مرآة FAOLEX لنفس صفحة BOE، "
        "وليست مصدراً منفصلاً فعلياً). راجع has_per_article_variation لإعادة "
        "البناء النظيف لـ11 مادة من سجل تعديلات BOE نفسه، تماشياً مع سابقة "
        "press_law/accounting_auditing_law، مفصَّل في official_source.json الخاص "
        "بالمسار."
    ),
    "residency_law": (
        "official_text_status='TIER_3_SECONDARY_MULTI_SOURCE_ONLY_BOE_DOES_NOT_INDEX_THIS_"
        "LAW_MOI_PDF_UNREACHABLE': بوابة هيئة الخبراء (laws.boe.gov.sa) لا تُفهرس هذا "
        "النظام (1371هـ) إطلاقاً — تُفهرس فقط نظام الإقامة المميزة (م/106، 1440هـ) "
        "المختلف تماماً وغير ذي الصلة. الصفحة الرسمية الخاصة بوزارة الداخلية "
        "(moi.gov.sa) لم تكن قابلة للوصول لا مباشرة ولا عبر أرشيف Wayback. لذلك لا "
        "يوجد أي مصدر رسمي/أساسي واحد قابل للتحقق لهذا المسار، وهو ما يطابق تماماً "
        "تعريف TIER_3 (لا مصدر رسمي متاح، مصدرين ثانويين مستقلين فأكثر متطابقين). "
        "اعتمد المسار على نسخة ثانوية موثقة رسمياً ومتداولة، تطابقت حرفياً عبر ثلاثة "
        "مصادر مستقلة (mohamah.net × rakadvocate.blogspot.com × islamport.com)، مع "
        "استخدام نسخة الهيئة الوطنية لحقوق الإنسان (NSHR) للتدقيق الهيكلي فقط (نصها "
        "تالف بسبب مشكلة ترميز خط CID، غير صالح للاستخدام المباشر). هذا مماثل لنمط "
        "gcc_anti_dumping_law وغيره من مسارات TIER_3 (مصدر رسمي متعذر الوصول كلياً، "
        "الاعتماد الكامل على تطابق مصادر ثانوية مستقلة). راجع الملاحظات الخاصة "
        "بالمسار لثلاثة تناقضات حقيقية موثقة: تضارب في رقم/تاريخ قرار إضافة المادة "
        "5 مكرر عبر ثلاثة استشهادات في المصدر المجمَّع نفسه، وخطأ مطبعي محتمل في "
        "ملاحظة التعديل الثاني للمادة 52، ونص المادة 61 مكرر المستبعد عمداً لعدم "
        "القدرة على استرجاعه من أي مصدر."
    ),
    "civil_status_law": (
        "official_text_status='BOE_WAYBACK_SEVEN_SNAPSHOT_X_QANOONSA_COM_RESOLUTION_805_X_"
        "NEZAMS_CROSS_VERIFIED': بوابة هيئة الخبراء (BOE) الحية متعذرة الوصول، واعتُمدت سبع "
        "لقطات أرشيف Wayback Machine مستقلة لصفحة BOE نفسها (تمتد من 13 نوفمبر 2019 إلى 15 "
        "فبراير 2026، نص متطابق حرفياً في كل لقطة) كمصدر رسمي وحيد، وقورنت بـqanoonsa.com "
        "(عرض نص قرار مجلس الوزراء 805 المتعلق بتعديل 2024) وnezams.com (تأكيد هوية المرسوم "
        "التأسيسي والتعديلات السابقة). بخلاف تصنيف الوكيل الباحث الأولي (الذي اقترح TIER_1)، "
        "هذا مصدر رسمي/أساسي **واحد فقط** (BOE عبر Wayback) — قرار مجلس الوزراء 805 لم يُطّلع "
        "عليه من بوابة حكومية رسمية مباشرة، وإنما عبر قراءة qanoonsa.com له، وهو موقع تجميع "
        "قانوني خاص وليس بوابة حكومية (نفس الدور الذي يلعبه qanoonsa.com عبر هذه المدونة بأكملها "
        "كمصدر تدقيق هيكلي ثانوي دوماً، لا كمصدر رسمي مستقل مطلقاً — انظر press_law وnazaha_law "
        "وaccounting_auditing_law)، وnezams.com مجمِّع ثانوي معروف أيضاً. هذا يطابق تعريف TIER_2 "
        "(مصدر رسمي واحد + تدقيق ثانوي)، مماثل لسابقتي nationality_law وnazaha_law. راجع "
        "notes الخاصة بالمسار لإعادة البناء النظيف من سجل تعديلات BOE نفسه لـ24 مادة معدَّلة "
        "بمنهجية موحدة (لا يوجد has_per_article_variation هنا)."
    ),
}

# Tracks with documented, non-negligible confidence variation ACROSS the articles WITHIN the
# same track (as opposed to a uniform track-wide tier). `has_per_article_variation=true` for
# these; the note points back at the track's own official_source.json rather than
# recomputing anything.
PER_ARTICLE_VARIATION_NOTE = {
    "travel_documents_law": (
        "المواد المعدَّلة بالمرسوم الملكي م/11 (1443هـ) تحديداً (10، 10 مكرر، الفقرة 3 من "
        "المادة 11) مؤكَّدة عبر جريدة أم القرى الرسمية نفسها إضافة إلى BOE وnezams.com/"
        "qistas.com، بمستوى ثقة يوازي TIER_1 لهذه الفئة الفرعية وحدها؛ بقية مواد المسار "
        "(بما فيها المواد المعدَّلة الأخرى 2، 4، 6، 12) تستند إلى BOE عبر Wayback زائد "
        "مصادر ثانوية خاصة فقط، دون تأكيد من جريدة أم القرى أو مصدر رسمي ثانٍ؛ راجع "
        "official_source.json الخاص بالمسار."
    ),
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
    "finance_companies_law": (
        "المواد الأصلية الأربعون (قبل تعديل 2024) مصدرها مزدوج رسمي (أرشيف Wayback "
        "لبوابة BOE × نسخة bfc.gov.sa الرسمية المحوَّلة عبر OCR)، متطابقة دون فارق "
        "جوهري. أما نص تعديل 2024 (المرسوم الملكي م/272، يمس المواد 1، 5، 11، 12، "
        "16-21، 29 والمادة 36 مكرر المضافة) فمصدره ثانوي حصراً (qanoonsa.com × حواشي "
        "nezams.com) دون أي تأكيد أولي مباشر لنصه تحديداً؛ راجع official_source.json "
        "الخاص بالمسار."
    ),
    "cooperative_health_insurance_law": (
        "17 مادة غير معدَّلة + الصياغتان (1420هـ و1425هـ) للمادتين المعدَّلتين (4، 14) "
        "مصدرها مزدوج (أرشيف Wayback لبوابة BOE × nezams.com)، متطابقة حرفياً دون "
        "فارق. أما نص تعديل المادة الرابعة لعام 1440هـ (القرار 472) فمصدره ثانوي "
        "واحد فقط (nezams.com) — بوابة BOE تذكر القرار نفسه دون إيراد نصه؛ راجع "
        "official_source.json الخاص بالمسار."
    ),
    "maritime_commercial_law": (
        "381 من 391 مادة مصدرها مزدوج رسمي/ثانوي (أرشيف Wayback لبوابة BOE "
        "العربية × nezams.com)، متطابقة حرفياً دون فارق جوهري (بعد تطبيع "
        "فروق تجميلية في المسافات وعلامات الاقتباس وترتيب التشكيل). أما "
        "المواد 316-325 (أحكام التأمين البحري) فاعتُمد فيها أرشيف الترجمة "
        "الإنجليزية الرسمية لبوابة BOE بدلاً من nezams.com، بعد اكتشاف خلل "
        "تكرار محتوى في نسخة nezams.com لهذا النطاق تحديداً (تأكيد مستقل بعد "
        "البناء وجد أن النطاق يقرأ الآن كأحكام تأمين بحري متتابعة ومتمايزة "
        "وليست مكررة)؛ راجع official_source.json الخاص بالمسار."
    ),
    "accounting_auditing_law": (
        "17 مادة غير معدَّلة + نص التعديل الأول (م/169، 1446هـ) للمواد الخمس المعدَّلة "
        "(1، 4، 5، 19، 20) مصدرها مزدوج رسمي (أرشيف Wayback لبوابة BOE — نافذة "
        "التعديلات لا النص الرئيسي الراكد — × نسخة SOCPA الرسمية) متطابقة دون فارق "
        "جوهري. أما تعديل المادة الأولى الثاني والأحدث (قرار مجلس الوزراء 283، "
        "1447هـ، تعميم تعريف 'الوزير') فمصدره ثانوي حصراً (PDF الهيئة SOCPA × "
        "qanoonsa.com) دون أي رقم مرسوم ملكي معروف يُصدره ودون أي تأكيد من بوابة BOE "
        "على الإطلاق؛ راجع official_source.json الخاص بالمسار."
    ),
    "awqaf_law": (
        "23 مادة غير معدَّلة مصدرها مزدوج رسمي (ست لقطات Wayback لبوابة BOE × نسخة "
        "الأوقاف الممسوحة ضوئياً)، متطابقة دون فارق جوهري. أما المادة السادسة (تشكيل "
        "مجلس الإدارة) فتحمل تناقضاً مؤكَّداً غير محلول: سجل BOE يوثّق أربعة تعديلات "
        "(قرارات مجلس الوزراء 262/1438هـ، 618/1442هـ، 638/1442هـ، 651/1443هـ) بينما "
        "النص الرئيسي لبوابة BOE ظل ثابتاً دون تغيير عبر جميع اللقطات الست من 2019 إلى "
        "2025، بل إن نص 'قبل التعديل' الموثّق في سجل BOE نفسه لا يطابق النص التاريخي "
        "الفعلي أيضاً — اعتُمد النص الرئيسي الراكد كما هو دون دمج افتراضي. أما المادة "
        "الحادية والعشرون (الرسوم) فتحمل تعديلاً واحداً واضحاً وموثَّقاً بالكامل (المرسوم "
        "الملكي م/72، 1444هـ) في سجل BOE، لم ينعكس بعد في النص الرئيسي رغم مرور أكثر من "
        "عامين — اعتُمد نص سجل التعديلات المقتبس كنص حالي، تماشياً مع سابقة "
        "accounting_auditing_law لهذا النمط تحديداً، وتأكَّد بتغطية صحفية مستقلة؛ راجع "
        "official_source.json الخاص بالمسار للتفاصيل الكاملة."
    ),
    "saudi_engineers_law": (
        "7 مواد غير معدَّلة مصدرها مزدوج رسمي (ثلاث لقطات Wayback لبوابة BOE × الموقع "
        "الرسمي للهيئة saudieng.sa)، متطابقة دون فارق جوهري. أما المادة الأولى (الجهة "
        "المشرفة) فتحمل تناقضاً مؤكَّداً: سجل BOE يوثّق نقل الإشراف بموجب قرار مجلس "
        "الوزراء 57، 1442هـ، بينما النص الرئيسي على كل من بوابة BOE وموقع الهيئة نفسه "
        "ظل ثابتاً بصياغة 'وزارة التجارة' القديمة عبر جميع اللقطات — اعتُمد نص سجل "
        "التعديلات المقتبس، وتأكَّد بتغطية صحفية مستقلة (الشرق الأوسط). أما المادة "
        "السادسة (تشكيل مجلس الإدارة) فتحمل تعديلين متتاليين موثَّقين بالكامل (المرسوم "
        "الملكي م/60، 1425هـ، ثم قرار مجلس الوزراء 388، 1443هـ) — اعتُمد النص الأحدث "
        "الكامل (388)، مؤكَّداً حرفياً من موقع الهيئة الرسمي، بينما ظل النص الرئيسي "
        "لبوابة BOE عالقاً على صياغة 2002 الأصلية طوال الفترة؛ راجع official_source.json "
        "الخاص بالمسار للتفاصيل الكاملة."
    ),
    "engineering_practice_law": (
        "16 مادة غير معدَّلة مصدرها مزدوج رسمي (ثلاث لقطات Wayback لبوابة BOE × ملف "
        "PDF الرسمي لموقع الهيئة saudieng.sa)، متطابقة حرفياً دون فارق جوهري. أما "
        "المادة الأولى (التعريفات، الجهة المشرفة) فتحمل تناقضاً ثلاثياً غير محلول: "
        "سجل BOE يوثّق نقل الإشراف بموجب قرار مجلس الوزراء 250، 1444هـ، لكن عبارته "
        "'قبل' لا تطابق نص BOE الرئيسي الثابت عند أي من اللقطات الثلاث (والذي يسبق "
        "القرار نفسه بنحو 3 سنوات)، بينما يعرض ملف saudieng.sa الحالي صياغة رابعة "
        "مختلفة بدورها تعكس إعادة تسمية إدارية لاحقة غير مسجَّلة في سجل BOE — لم "
        "يُدمج نص مركَّب افتراضياً؛ اعتُمد نص BOE الرئيسي الثابت كما هو، وصُنِّفت "
        "المادة معدَّلة (بناءً على تصنيف BOE نفسه)، ووُثِّق التناقض الثلاثي كاملاً، "
        "تماشياً مع سابقة awqaf_law المادة 6؛ راجع official_source.json الخاص "
        "بالمسار للتفاصيل الكاملة."
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
