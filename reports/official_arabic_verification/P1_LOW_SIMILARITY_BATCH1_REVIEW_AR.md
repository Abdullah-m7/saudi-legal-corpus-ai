# مراجعة الدفعة 1 — مواد P1 الأقل تشابهًا
# P1 Low-Similarity Batch 1 — Manual Review

> **هذه مراجعة/فرز للدفعة فقط، وليست تحققًا ولا استشارة قانونية.** لم يُغيَّر أي نص مرشح، ولم تُرقَّ أي مادة، ولم تُوسم أي مادة بأنها `verified_against_official_gazette`. النص المرشح يبقى `ingested_unverified` و`article_by_article_verified` يبقى `false`.
>
> This is a **batch review / triage only — not verification, not legal advice.** No candidate text was changed; no article was promoted; the candidate remains `ingested_unverified` and `article_by_article_verified` remains `false`.

## الاختيار / Selection

- **batch_id:** `P1_LOW_SIMILARITY_BATCH1` · **batch_size:** `10`
- **طريقة الاختيار / selection_method:** أقل 10 مواد P1 تشابهًا من قائمة المراجعة. / the 10 lowest-similarity P1 articles from the manual-review queue.
- **المواد المختارة / selected articles:** 147, 140, 76, 110, 277, 221, 71, 123, 138, 228

| المادة / art | العنوان / title | التشابه / similarity | التصنيف / classification | الثقة / confidence | المصدر / source page |
|---|---|---|---|---|---|
| 147 | القوائم المالية وتقرير عن نشاط الشركة | 0.0346 | `likely_ocr_noise` | low | صفحة 58 / page 58 |
| 140 | بيانات نظام الشركة الأساس | 0.0459 | `segmentation_or_alignment_drift` | medium | صفحة 32 / page 32 |
| 76 | مكافأة أعضاء مجلس الإدارة | 0.1116 | `segmentation_or_alignment_drift` | medium | صفحة 39 / page 39 |
| 110 | تعديل الحقوق أو الالتزامات المتصلة بالأسهم | 0.1150 | `segmentation_or_alignment_drift` | medium | صفحة 54 / page 54 |
| 277 | إصدار اللوائح | 0.1219 | `likely_ocr_noise` | low | صفحة 119 / page 119 |
| 221 | تحول الشركة غير الربحية | 0.1231 | `likely_ocr_noise` | low | صفحة 97 / page 97 |
| 71 | الإفصاح عن المصلحة في الأعمال والعقود | 0.1353 | `segmentation_or_alignment_drift` | medium | صفحة 36 / page 36 |
| 123 | تكوين الاحتياطيات | 0.1379 | `segmentation_or_alignment_drift` | medium | صفحة 53 / page 53 |
| 138 | مفهوم شركة المساهمة المبسطة | 0.1883 | `segmentation_or_alignment_drift` | medium | صفحة 64 / page 64 |
| 228 | نفاذ قرار الاندماج | 0.2076 | `segmentation_or_alignment_drift` | medium | صفحة 99 / page 99 |

## تفاصيل كل مادة / Per-article detail

### المادة 147 — القوائم المالية وتقرير عن نشاط الشركة

- **التشابه / similarity:** `0.0346` (كان P1 / was P1)
- **التصنيف / classification:** `likely_ocr_noise`
- **الثقة / confidence:** `low`
- **ملخص الدليل / evidence summary:** article_title_located_in_source_but_body_opening_not_exact_matched_consistent_with_heavy_ocr_noise
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 58 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_03_pages_041_060.pdf) / found — packet page 58
- **مقتطف المرشح / candidate snippet:** يجب على رئيس شركة المساهمة المبسطة أو مديرها أو مجلس إدارتها -بحسب الأحوال- في نهاية كل سنة مالية للشركة، أن يعد القوائم المالية للشركة وتقريرًا عن نشاطها ومركزها المالي عن السنة المالية المنقضية، ويضمّن هذا التقرير الطر
- **مقتطف الـOCR / OCR snippet:** يحب على رئيس شركة المساهمة المبسطة أو مديرها أو مجلس إدارتما بحسب الأحوال- في نحاية كل سنة مالية  ‏للشركة» أن يعد القوائم المالية للشركة وتقريرًا عن نشاطها ومركزها الماللي عن السنة المالية المنقضية» ويضمّن هذا التقرير
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: treat as OCR noise; no candidate change

### المادة 140 — بيانات نظام الشركة الأساس

- **التشابه / similarity:** `0.0459` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 32 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_02_pages_021_040.pdf) / found — packet page 32
- **مقتطف المرشح / candidate snippet:** يجب أن يشتمل النظام الأساس لشركة المساهمة المبسطة بصفة خاصة على البيانات الآتية:

- أ- اسم الشركة.
- ب- المركز الرئيس للشركة.
- ج- غرض الشركة.
- د- رأس مال الشركة المصرح به -إن وجد- والمصدر والمدفوع منه.
- هـ- عدد الأسهم
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ يحب أن يشتمل النظام الأساس لشركة المساهمة المبسطة بصفة خاصة على البيانات الآنية:  ‏أ- اسم الشركة. ب- للركز الرئيس للشركة. ج- غرض الشركة.  ‏د- رأس مال الشركة للصرح به -إن وجذ- والمصدر والمدفوع منه.  ‏ه- عدد الأسهم؛ و
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

### المادة 76 — مكافأة أعضاء مجلس الإدارة

- **التشابه / similarity:** `0.1116` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 39 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_02_pages_021_040.pdf) / found — packet page 39
- **مقتطف المرشح / candidate snippet:** يبين نظام الشركة الأساس طريقة مكافأة أعضاء مجلس الإدارة، ويجوز أن تكون هذه المكافأة مبلغًا معينًا، أو بدل حضور عن الجلسات، أو مزايا عينية، أو نسبة معينة من صافي الأرباح، ويجوز الجمع بين اثنتين أو أكثر مما تقدم، ويجوز كذل
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ يبين نظام الشركة الأساس طريقة مكافأة أعضاء مجلس الإدارة» ويجوز أن تكون هذه المكافأة مبلعًا معيئاء أو بدل حضور عن الجلسات» أو مزايا عينية؛ أو نسبة معينة من صافي الأرباح» ويجوز الجمع بين اثنتين أو أكثر ثما تقدمء ويجوز
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

### المادة 110 — تعديل الحقوق أو الالتزامات المتصلة بالأسهم

- **التشابه / similarity:** `0.1150` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 54 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_03_pages_041_060.pdf) / found — packet page 54
- **مقتطف المرشح / candidate snippet:** إذا كانت أسهم الشركة من أنواع وفئات مختلفة أو كان نظام الشركة الأساس يسمح بإصدار أنواع وفئات مختلفة من الأسهم، فيشترط لتعديل أو إلغاء أيّ من الحقوق أو الالتزامات أو القيود المتصلة بالأسهم، أو لتحويل أي نوع أو فئة من الأس
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ إذاكانت أسهم الشركة من أنواع وفئات مختلفة أو كان نظام الشركة الأساس يسمح بإصدار أنواع وفىات مختلفة من الأسهم؛ فيشترط لتعديل أو إلغاء أي من الحقوق أو الالتزامات أو القيود المتصلة بالأسهم؛ أو لتحويل أي نوع أو فئة من ا
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

### المادة 277 — إصدار اللوائح

- **التشابه / similarity:** `0.1219` (كان P1 / was P1)
- **التصنيف / classification:** `likely_ocr_noise`
- **الثقة / confidence:** `low`
- **ملخص الدليل / evidence summary:** article_title_located_in_source_but_body_opening_not_exact_matched_consistent_with_heavy_ocr_noise
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 119 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_06_pages_101_119.pdf) / found — packet page 119
- **مقتطف المرشح / candidate snippet:** يصدر الوزير ومجلس الهيئة اللوائح، كل فيما يخصه، خلال مدة أقصاها (مائة وثمانون) يومًا من تاريخ نشر النظام، وتبين اللوائح القواعد والمدد والإجراءات، وتحدد الوثائق أو البيانات اللازمة لتنفيذ أحكام النظام، وتبين ضوابط استعما
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ يصدر الوزير ومجلس اميئة اللوائح» كل فيما يخصه؛ خلال مدة أقصاها (ماثة وثمانون) يومًا من تاريخ نشر النظام» وتبين اللوائح القواعد والمدد والإجراءات» وتحدد الوثائق أو البيانات اللازمة لتنفيذ أحكام النظام» وتبين ضوابط اس
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: treat as OCR noise; no candidate change

### المادة 221 — تحول الشركة غير الربحية

- **التشابه / similarity:** `0.1231` (كان P1 / was P1)
- **التصنيف / classification:** `likely_ocr_noise`
- **الثقة / confidence:** `low`
- **ملخص الدليل / evidence summary:** article_title_located_in_source_but_body_opening_not_exact_matched_consistent_with_heavy_ocr_noise
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 97 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_05_pages_081_100.pdf) / found — packet page 97
- **مقتطف المرشح / candidate snippet:** مع مراعاة حكم الفقرة (1) من المادة (العشرين بعد المائتين) من النظام، يجوز تحول الشركة غير الربحية الخاصة دون العامة إلى أي شكل من الشركات ما لم ينص عقد تأسيس الشركة أو نظامها الأساس على غير ذلك، على أن يصرف ما زاد على رأ
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ مع مراعاة حكم الفقرة ‎)١(‏ من للمادة (العشرين بعد المائتين) من النظام: يجوز تحول الشركة غير الريحية الخاصة دون العامة إلى أي شكل من الشركات ما لم ينص عقد تأسيس الشركة أو نظامها الأساس على غير ذلك» على أن يصرف ما زاد
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: treat as OCR noise; no candidate change

### المادة 71 — الإفصاح عن المصلحة في الأعمال والعقود

- **التشابه / similarity:** `0.1353` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 36 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_02_pages_021_040.pdf) / found — packet page 36
- **مقتطف المرشح / candidate snippet:** مع مراعاة حكم المادة (السابعة والعشرين) من النظام، يجب على عضو مجلس الإدارة فور علمه بأي مصلحة له سواء مباشرة أو غير مباشرة في الأعمال والعقود التي تكون لحساب الشركة، أن يبلغ المجلس بذلك، ويثبت هذا الإبلاغ في محضر اجتماع
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ مع مراعاة حكم المادة (السابعة والعشرين) من النظام؛ يجب على عضو مجلس الإدارة فور علمه بأي مصلحة له سواء مباشرة أو غير مباشرة في الأعمال والعقود التي تكون لحساب الشركة» أن يبلغ امجلس بذلك؛ وينبت  يانه لخدف" المي بكي 1
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

### المادة 123 — تكوين الاحتياطيات

- **التشابه / similarity:** `0.1379` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 53 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_03_pages_041_060.pdf) / found — packet page 53
- **مقتطف المرشح / candidate snippet:** يجوز النص في نظام الشركة الأساس على تجنيب نسبة معينة من صافي الأرباح لتكوين احتياطي يخصص للأغراض التي يحددها النظام الأساس. وللجهة المختصة وضع ضوابط تكوين الاحتياطيات.

للجمعية العامة العادية -عند تحديد نصيب الأسهم في صا
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ يجوز النص في نظام الشركة الأساس على تحنيب نسبة معينة من صانئي الأرباح لتكوين احتياطي يخصص للأغراض التي يحددها النظام الأساس. وللجهة المختصة وضع ضوابط نكوين الاحتياطيات.  ‏؟- للجمعية العامة العادية -عند تحديد نصيب ال
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

### المادة 138 — مفهوم شركة المساهمة المبسطة

- **التشابه / similarity:** `0.1883` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 64 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_04_pages_061_080.pdf) / found — packet page 64
- **مقتطف المرشح / candidate snippet:** تسري على شركة المساهمة المبسطة فيما لم يرد به نص خاص في هذا الباب، وبما يتفق مع طبيعتها، أحكام شركة المساهمة عدا المواد: (الحادية والستين)، و(الثالثة والستين)، ومن (السابعة والستين) إلى (الحادية والسبعين)، ومن (الرابعة و
- **مقتطف الـOCR / OCR snippet:** ‎-١‏ تسري على شركة المساهمة المبسطة فيما لم يرد به نص خاص في هذا الباب؛ وبما يتفق مع طبيعتهاء أحكام شركة المساهمة عدا المواد: (الحادية والستين)» و(الثالثة والستين)» ومن (السابعة والستين) إلى (الحادية والسبعين)» ومن (الرا
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

### المادة 228 — نفاذ قرار الاندماج

- **التشابه / similarity:** `0.2076` (كان P1 / was P1)
- **التصنيف / classification:** `segmentation_or_alignment_drift`
- **الثقة / confidence:** `medium`
- **ملخص الدليل / evidence summary:** distinctive_body_phrase_found_verbatim_in_source_but_per_article_alignment_span_mismatched
- **الموقع في المصدر / source location:** موجود — صفحة الحزمة 99 (inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/nizam_alsharikat_1443h_part_05_pages_081_100.pdf) / found — packet page 99
- **مقتطف المرشح / candidate snippet:** يسري قرار الاندماج ويعد نافذًا من تاريخ قيد بيانات الشركة المندمجة في سجل الشركة الدامجة لدى السجل التجاري، وفيما عدا ذلك يسري قرار الاندماج ويعد نافذًا من تاريخ قيد الشركة الناشئة عنه لدى السجل التجاري.
- **مقتطف الـOCR / OCR snippet:** يسري قرار الاندماج ويعد نافدًا من تاريخ قيد بيانات الشركة المندمجة في سجل الشركة الدامجة لدى السجل  ‏التجاري» وفيما عدا ذلك يسري قرار الاندماج ويعد نافدًا من تاريخ قيد الشركة الناشئة عنه لدى السجل التجاري.  ‎5   المملكة
- **الإجراء التالي الموصى به / recommended next action:** later queue-update PR: re-bucket as OCR/segmentation artifact (not a text change)

## ملخص الدفعة حسب التصنيف / Batch summary by classification

- `likely_ocr_noise`: **3**
- `segmentation_or_alignment_drift`: **7**

- **مواد بثقة منخفضة / low-confidence articles:** 147, 277, 221
- **مواد باختلاف جوهري محتمل / possible substantive difference:** لا يوجد / none

## سير العمل التالي الموصى به / Recommended next workflow

- **A)** تحديث تصنيفات القائمة لاحقًا (PR تحديث قائمة) للحالات عالية الثقة من ضجيج الـOCR / انحراف التقطيع. / A later queue-update PR re-classifying the high-confidence OCR/segmentation cases (no text change).
- **B)** مراجعة يدوية بصرية للحالات منخفضة الثقة أو ذات الاختلاف الجوهري المحتمل. / Manually inspect the low-confidence / possible-substantive-difference cases.
- **C)** إنشاء PR تصحيح/ترقية **لاحقًا فقط** إذا دعم الدليل ذلك من مصدر رسمي غير الـOCR. / Only later create a correction/promotion PR if the evidence supports it, from an official (non-OCR) source.

**هذه المراجعة لا تُرقّي ولا تتحقق ولا تصحّح ولا تغيّر أي نص قانوني. العربية هي اللغة الحاكمة. ليست استشارة قانونية.**
This review does not promote, verify, correct, or modify any legal text. Arabic is governing. Not legal advice.
