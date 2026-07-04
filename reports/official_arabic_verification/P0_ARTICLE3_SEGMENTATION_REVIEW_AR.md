# مراجعة P0 — المادة الثالثة: جنسية الشركة (مشكلة تقطيع)
# P0 Review — Article 3 (جنسية الشركة): segmentation issue

> **هذه مراجعة تقطيع بأولوية P0 فقط، وليست تحققًا ولا استشارة قانونية.** المادة الثالثة **لا**
> يجري التحقق منها هنا. **لم يُغيَّر** نص المرشح، **ولم تُرقَّ** أي مادة. النص المرشح يبقى
> `ingested_unverified` و`article_by_article_verified` يبقى `false`.
>
> This is a **P0 segmentation review only — not verification, not legal advice.** Article 3 is
> **not** being verified. Candidate text is **not** changed. **No promotion occurred.**

## النتيجة / Result

- **هل عُثر على المادة الثالثة في المصدر الرسمي الممسوح؟ نعم.** / Was Article 3 found in the
  official scanned source? **YES.**
- **الموقع / Location:**
  - الملف الجزء / part file:
    `inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_01_pages_001_020.pdf`
  - رقم الصفحة داخل الحزمة / page within packet: **6**
  - رقم الصفحة داخل الجزء / page within part: **6**
- **مقتطف الدليل من الـOCR / OCR evidence snippet:**

```
المادة الثالئة: جنسية الشركة:
تعد الشركة التي تؤسس وفمًا لأحكام النظام سعودية الجنسية» ويجب أن يكون مركزها الرئيس في المملكة.
```

## سبب المشكلة / Root cause

- أخطأ الـOCR في استخراج ترتيب المادة في العنوان: **«الثالثة» → «الثالئة»** (إبدال حرف)، فلم
  يطابق المُحاذي (المعتمد على الترتيب) المادة الثالثة، فوُسمت `missing_in_official_source`.
- **نصّ المادة موجود** في الصفحة 6 ويطابق نص المرشح (تشابه بعد التطبيع = **0.9787**؛ الفروق ضجيج
  OCR فقط، مثل «وفمًا/وفقًا» و«»/،»).
- OCR mis-read the heading ordinal (**الثالثة → الثالئة**), so the ordinal-based segmentation
  aligner missed Article 3. The article body **is present** on page 6 and matches the candidate
  (normalized similarity **0.9787**; differences are OCR noise only).

## التصنيف / Classification

- **`segmentation_ocr_miss`** — المادة موجودة في المصدر الرسمي؛ المشكلة كانت خطأ OCR في العنوان،
  وليست غياب المادة. / the article exists in the official source; the issue was an OCR heading
  error, not an absent article.

## المراجعة البصرية / Visual review

- **لم تُستخدم مراجعة بصرية** لأن دليل الـOCR قاطع (العنوان + النص موجودان في الصفحة 6). فحص بصري
  للصفحة 6 اختياري للتأكيد فقط. / Visual review **not used** — the OCR evidence is conclusive;
  an optional visual spot-check of page 6 may confirm.

## الخطوة التالية الموصى بها / Recommended next step

- **(A)** اعتبار هذه المشكلة P0 **محلولة كـ«OCR segmentation miss»** (المادة موجودة في الصفحة 6 من
  الحزمة) ضمن **PR لاحق لتحديث قائمة المراجعة** — دون ترقية ودون تغيير أي نص. / mark this P0 as
  **resolved (OCR segmentation miss)** in a later **queue-update PR** — no promotion, no text change.
- **(B)** غير مطلوب في العادة؛ يُلجأ للمراجعة البصرية اليدوية فقط إن رغب المالك بتأكيد إضافي. / manual
  visual review only if the owner wants extra confirmation.

**هذا الـPR لا يرقّي أي مادة ولا يغيّر أي نص. العربية هي اللغة الحاكمة. ليست استشارة قانونية.**
This PR promotes no article and changes no text. Arabic is governing. Not legal advice.
