# متطلبات حزمة المصدر الرسمي للنص العربي — Official Arabic Source Packet Requirements

> **الغرض / Purpose:** تحديد ما يلزم بالضبط من مادة مصدرية رسمية لبدء إدخال النص العربي
> النظامي الرسمي لنظام الشركات السعودي والتحقق منه مادةً مادةً. لا يجوز بدء الإدخال قبل توفير
> حزمة مصدر رسمية موثوقة. / This document tells the repository owner exactly what official
> source material is required before official Arabic ingestion and article-by-article
> verification can begin. **No ingestion starts without a verifiable official source packet.**

## 1. النص المطلوب / Required text

- النص العربي **الرسمي الكامل** لنظام الشركات السعودي (جميع المواد **1–281**).
- The **full official Arabic** text of the Saudi Companies Law — all **281 articles**.
- المصدر يجب أن يكون **رسميًا حكوميًا**، ويفضّل الجريدة الرسمية. / The source must be an
  **official government** source, preferably the official gazette.

## 2. المصدر المقبول / Acceptable source

مقبول / Acceptable:
- الجريدة الرسمية **أم القرى (أم القرى)** — النص المنشور رسميًا. / The official gazette
  **Umm Al-Qura**, official published text.
- المنصات الحكومية الرسمية (مثل هيئة الخبراء بمجلس الوزراء / المركز الوطني للوثائق) بصفتها
  ناشرًا رسميًا. / Official government platforms (e.g. the Bureau of Experts at the Council
  of Ministers) acting as an official publisher.

غير مقبول كمصدر قانوني رسمي / NOT acceptable as the canonical legal source:
- نسخ من مدونات أو مواقع غير رسمية، أو ملخصات، أو ترجمات. / Blog copies, unofficial
  websites, summaries, or translations.
- النص العربي المستخرَج المشوَّه من ملف الترجمة المرجعي الحالي (`inputs/`). / The garbled
  extracted Arabic layer from the current reference PDF.

## 3. صيغة الملف / File format

- ملف واحد أو أكثر بصيغة **PDF رسمي / HTML رسمي / نص UTF-8** يحوي النص العربي الرسمي.
- One or more files: **official PDF / official HTML / UTF-8 text** containing the official
  Arabic text.
- يفضَّل وجود طبقة نص قابلة للاستخراج؛ إن كان المصدر صورة مسح ضوئي، يُذكر ذلك ليُخطَّط لـ OCR
  ثم تدقيق يدوي. / A selectable text layer is preferred; if the source is a scanned image,
  say so, so OCR + manual correction can be planned.

## 4. البيانات الوصفية المطلوبة مع الحزمة / Metadata required with the packet

يرجى تزويد الحقول التالية (تُسجَّل في `data/official_arabic/ingestion_status.json`):
Please provide the following (recorded in `data/official_arabic/ingestion_status.json`):

- **رابط المصدر أو الملف / source URL or file** (`source_url_or_file_reference`).
- **نوع وثيقة المصدر / source document type** (official gazette PDF, official HTML, …).
- **الجهة المصدرة / source authority** (e.g. Umm Al-Qura).
- **تاريخ / إصدار المصدر / source date or gazette issue** (`official_gazette_issue`,
  `official_gazette_date`).
- **رقم المرسوم الملكي وتاريخه / royal decree number & Hijri date** — نظام الشركات صدر
  بالمرسوم الملكي رقم **(م/132)** وتاريخ **1443/12/01هـ**. / issued by Royal Decree No.
  **(M/132)**, dated **1443/12/01 AH**.
- **أي تعديلات أو ملاحظات نسخة / any amendments or version notes** — رقم وتاريخ أي تعديل
  لاحق. / number and date of any later amendment.

## 5. ما يحدث بعد التسليم / What happens after you provide it

- تُسجَّل الحزمة في `data/official_arabic/ingestion_status.json`، ثم يُتَّبع
  [`OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md`](OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md).
- لا تُرقَّى الملخصات العربية الحالية إلى "نص رسمي" إلا بعد التحقق مادةً مادةً. / The current
  Arabic summaries are **not** promoted to "official text" until article-by-article
  verification is complete.

**العربية هي اللغة القانونية الحاكمة. هذه المادة ليست استشارة قانونية.**
Arabic is the governing legal language. This material is not legal advice.
