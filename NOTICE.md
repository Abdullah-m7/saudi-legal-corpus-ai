# NOTICE — Legal Content, Provenance, and Disclaimers

## Non-official reference translation

This repository contains an **internally reviewed concise reference translation** of Book One
/ الباب الأول (Articles 1–34) of the Saudi Companies Law, in Arabic and Chinese. "Internally
reviewed" means QA-reviewed against the attached reference translation source — it has **not**
yet been verified article-by-article against the official *Umm Al-Qura* text.

- **中文：** 本文件为沙特《公司法》第一编（第一条至第三十四条）完整范围的**经内部审校**参考译本，
  已对照所附参考翻译来源进行内部质检，但**尚未逐条对照官方文本核验**，采用摘要式法律表达，
  **并非官方译本或逐字全文翻译**。
- **العربية:** هذه الوثيقة ترجمة مرجعية موجزة ومراجَعة داخليًا مقابل مصدر الترجمة المرفق للباب الأول
  كاملًا من نظام الشركات السعودي، المواد 1–34، ولم تُدقَّق بعد مادةً مادةً مقابل النص الرسمي،
  **وليست ترجمة رسمية أو حرفية كاملة للنص النظامي**.

## Not legal advice

This material is provided for general reference and directed lookup only. It **does
not constitute legal advice**. The only legally binding text is the Arabic original
published in the official gazette **Umm Al-Qura (أم القرى)**. Before making any
business decision, consult the full official text and a Saudi-qualified legal advisor.

## Provenance and canonical source model

- The attached PDF (`inputs/bab1_source.pdf`) is the current **design/reference
  artifact**, not the canonical long-term source.
- The **canonical structured sources** are the JSON files under `data/`. Human-readable
  outputs (`content/`, `dist/book1.html`, `dist/book1.pdf`) are **generated from them**.
- Arabic reference summaries are **manually reconstructed Modern Standard Arabic**
  (the PDF Arabic layer extracts garbled) and are concise summaries, not statutory text.
- No article has been independently verified against the official gazette in this build.
  Unverifiable points are flagged **`NEEDS_OFFICIAL_TEXT_CHECK`**
  (see `data/qa/known_issues.json` and each article's `source.official_text_check`).

## Copyright posture

This repository contains concise reference summaries and structured metadata. It does
**not** reproduce the full official Arabic statutory text beyond what is present in the
user-provided translation source. Do not add raw copyrighted official full Arabic text
beyond that source.

## Instrument reference

- نظام الشركات — المرسوم الملكي رقم (م/132) وتاريخ 1443/12/1هـ
- Companies Law — Royal Decree No. (M/132), issued 2022.
