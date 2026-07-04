# ضمان جودة دفعة المعالجة الصينية P0-001
# Chinese remediation batch P0-001 — QA

> **مراجعة جودة/مقارنة فقط، وليست مراجعة قانونية بشرية مكتملة، وليست استشارة قانونية.** لم يُعدَّل النص الصيني المعالَج في هذا الـPR.

## ملخص تنفيذي / Executive summary

- **نطاق الدفعة:** P0-001 فقط.
- **المواد (20):** 61، 62، 63، 64، 65، 67، 68، 69، 70، 73، 74، 76، 78، 79، 80، 81، 82، 83، 84، 85.
- **QA لا يُعد مراجعة قانونية بشرية مكتملة** (`human_legal_review_completed = false`).
- **العربية هي النص الحاكم**؛ الإنجليزية إرشاد ثانوي فقط.
- **الصينية داخلية فقط، وغير رسمية وغير ملزِمة وغير حاكمة.**
- **لم تُنشأ طبقة 281 كاملة، ولا محاذاة ثلاثية.**

## جدول المواد / Article table

| المادة | العنوان | قرار QA | المطابقة الدلالية | الاكتمال القانوني | ملاحظات مانعة | الإجراء التالي |
|---|---|---|---|---|---|---|
| 61 | بيانات نظام الشركة الأساس | `qa_pass_with_minor_fix_recommended` | pass | complete | لا يوجد | `revise_minor_issues` |
| 62 | الاكتتاب في الأسهم | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 63 | الاكتتاب خلال مرحلة التأسيس | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 64 | إيداع قيمة الأسهم | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 65 | قيد الشركة لدى السجل التجاري | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 67 | الترشح لعضوية مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 68 | انتخاب أعضاء مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 69 | انتهاء دورة مجلس الإدارة أو اعتزال أعضائه | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 70 | إنهاء عضوية المتغيب عن الحضور | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 73 | الرقابة على مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 74 | عقد القروض والتصرف في أصول الشركة | `qa_pass_with_minor_fix_recommended` | pass | complete | لا يوجد | `revise_minor_issues` |
| 76 | مكافأة أعضاء مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 78 | توزيع الاختصاصات في مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 79 | تمثيل الشركة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 80 | اجتماعات مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 81 | الإنابة في حضور الاجتماعات وسريان قرارات مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 82 | إصدار القرارات في الأمور العاجلة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 83 | محاضر اجتماعات مجلس الإدارة | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 84 | اجتماع الجمعية العامة للمساهمين | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |
| 85 | اختصاصات الجمعية العامة غير العادية | `qa_pass_for_internal_reference_pending_human_review` | pass | complete | لا يوجد | `retain_pending_human_review` |

## ملخص / Summary

- **pass:** 18
- **minor fix:** 2
- **blocked:** 0
- **failed:** 0

## توصية / Recommendation

جميع المواد **pass/minor فقط**: يُنشأ لاحقًا PR لتطبيق التصحيحات الطفيفة (المادتان 61 و74)، أو الانتقال بحذر إلى **P0-002** بعد موافقة عبدالله. تبقى المراجعة القانونية البشرية معلّقة.

**العربية هي اللغة الحاكمة. الصينية داخلية غير رسمية وغير مُلزِمة وغير حاكمة. ليست استشارة قانونية.**
Arabic is governing. Chinese is internal, non-official, non-binding, non-governing. Not legal advice.
