# مراجعة ترجمة الباب الأول الصينية — ملف PDF الأصلي
# Bab 1 original Chinese PDF — translation review

> **هذه مراجعة/جرد مصدر فقط، وليست ترجمة رسمية ولا استشارة قانونية.** لم يُنشأ أي سجل Chinese LLM-ready، ولم تُصحَّح الترجمة، ولم يُعدَّل ملف الـPDF.

## المصدر / Source

- **مصدر الملف / source file:** `inputs/chinese_translation_source_pdfs/saudi_companies_law_ar_zh_bab1_full.pdf`
- **SHA-256:** `e0928753c163dc80264d2a3f10e75621e7b7133f03d04ebf4a312c1342d50374`
- **عدد الصفحات / pages:** 31 · **الحجم / size:** 630844 bytes
- **طريقة الاستخراج / extraction:** pypdf_text_layer + 第N条 heading segmentation
- **نطاق الباب الأول / scope:** المواد **1–34**

## الوضع القانوني / Posture

- **هل الترجمة الصينية رسمية؟** **لا** (`official_translation = false`).
- **هل الصينية حاكمة؟** **لا، العربية هي اللغة الحاكمة** (`governing = ar`).
- **هل الملف يصلح مباشرة كـChinese LLM-ready كامل؟** **لا** (`llm_ready_as_full_translation = false` لكل المواد).
- الصينية **ترجمة عمل/مرجع داخلية فقط، غير مُلزِمة** (`not_binding = true`).

## ملخص التصنيف العام / Classification summary

- `materially_incomplete_needs_retranslation`: **8**
- `mostly_aligned_but_condensed`: **21**
- `summary_needs_expansion`: **5**
- **مواد تحتاج توسعة/إعادة ترجمة / need expansion or retranslation:** 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 21
- **مواد تصلح كمرجع داخلي / usable as internal reference:** 34/34

## جدول المواد 1–34 / Articles 1–34

| المادة | درجة المطابقة | حالة التغطية | كاملة LLM؟ | مرجع داخلي؟ | الإجراء المقترح |
|---|---|---|---|---|---|
| 1 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 2 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 3 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 4 | low | `summary_needs_expansion` | لا | نعم | `expand_from_arabic_before_llm_ready` |
| 5 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 6 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 7 | low | `summary_needs_expansion` | لا | نعم | `expand_from_arabic_before_llm_ready` |
| 8 | low | `summary_needs_expansion` | لا | نعم | `expand_from_arabic_before_llm_ready` |
| 9 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 10 | low | `summary_needs_expansion` | لا | نعم | `expand_from_arabic_before_llm_ready` |
| 11 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 12 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 13 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 14 | low | `materially_incomplete_needs_retranslation` | لا | نعم | `retranslate_full_from_arabic_before_llm_ready` |
| 15 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 16 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 17 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 18 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 19 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 20 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 21 | low | `summary_needs_expansion` | لا | نعم | `expand_from_arabic_before_llm_ready` |
| 22 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 23 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 24 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 25 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 26 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 27 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 28 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 29 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 30 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 31 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 32 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 33 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |
| 34 | medium | `mostly_aligned_but_condensed` | لا | نعم | `expand_condensed_details_from_arabic_then_review` |

## أهم المواد التي تحتاج توسعة أو إعادة ترجمة / Key articles needing work

- **المادة 1 — التعريفات:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: تعريف كل مصطلح (لا مجرد سرد المصطلحات)
- **المادة 2 — تعريف الشركة:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: المساهمة بمال أو عمل أو بهما؛ اقتسام الربح والخسارة
- **المادة 3 — جنسية الشركة:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: أغلب عناصر النص العربي غير مُغطّاة أو مضغوطة بشدة
- **المادة 4 — أشكال الشركات:** `summary_needs_expansion` — عناصر ناقصة/مضغوطة: تفاصيل إجرائية/فرعية مضغوطة مقارنة بالنص العربي الرسمي
- **المادة 5 — اسم الشركة:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: قاعدة الاسم بالعربية أو لغة أخرى؛ اشتقاق الاسم من الغرض/الاسم/الشريك/اسم مبتكر؛ موافقة الشريك/المساهم السابق أو الورثة؛ الالتزام بنظام الأسماء التجارية
- **المادة 7 — وثائق تأسيس الشركة:** `summary_needs_expansion` — عناصر ناقصة/مضغوطة: نماذج/إرشادات الوزارة
- **المادة 8 — قيد وثائق تأسيس الشركة:** `summary_needs_expansion` — عناصر ناقصة/مضغوطة: الشكل الكتابي/البطلان؛ متطلبات التعديل؛ المسؤولية التضامنية
- **المادة 9 — اكتساب الشخصية الاعتبارية:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: المصروفات بعد القيد؛ المسؤولية عند عدم إتمام التأسيس
- **المادة 10 — أغراض الشركة:** `summary_needs_expansion` — عناصر ناقصة/مضغوطة: تفاصيل إجرائية/فرعية مضغوطة مقارنة بالنص العربي الرسمي
- **المادة 11 — اتفاق الشركاء والميثاق العائلي:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: الورثة؛ سياسة العمل/التوظيف لأفراد العائلة؛ التصرف في الحصص/الأسهم؛ تسوية المنازعات
- **المادة 12 — البيانات الواجب تضمينها في وثائق الشركة:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: عنوان المركز الرئيس؛ البريد الإلكتروني إن وجد؛ رأس المال المدفوع
- **المادة 14 — تقديم الحصة:** `materially_incomplete_needs_retranslation` — عناصر ناقصة/مضغوطة: قاعدة حق الانتفاع/الاستعمال (الإيجار)؛ عائد العمل يعود للشركة؛ استثناء حقوق الملكية الفكرية
- **المادة 21 — الرقابة على حسابات الشركة:** `summary_needs_expansion` — عناصر ناقصة/مضغوطة: تفاصيل إجرائية/فرعية مضغوطة مقارنة بالنص العربي الرسمي

## التوصية للمرحلة التالية / Recommendation

لا يُنصح بتحويل ملف الباب الأول مباشرة إلى طبقة Chinese LLM-ready كاملة. يوصى باعتماده أولًا كمصدر ترجمة صينية داخلي تحت المراجعة، ثم إنشاء مرحلة لاحقة لتوسيع/تصحيح المواد ذات النقص قبل بناء الطبقة الصينية.

**العربية هي اللغة الحاكمة. الصينية ترجمة داخلية غير رسمية وغير مُلزِمة. ليست استشارة قانونية.**
Arabic is governing. Chinese is an internal, non-official, non-binding working translation. Not legal advice.
