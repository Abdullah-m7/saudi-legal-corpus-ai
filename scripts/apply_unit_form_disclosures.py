#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Say so when a record is not an article.

The corpus stores every unit of every instrument in fields named for articles —
`article_number`, `article_key`, `number_label_ar` — because one schema across
743 tracks is worth more than a faithful shape per track. That is a deliberate
trade, and it is only honest while every track whose units are NOT articles says
so, because a reader who does not know cites «المادة (3)» for something the
source calls «الجدول (3)» or «البند ثالثاً».

Tracks built by the gazette pipeline already carry that disclosure: the ordinal-
band and numbered-clause forms write one at build time. The LLM-readiness audit
asked the question of the whole corpus and found 81 tracks holding at least one
non-article unit, 54 of them disclosing it and 27 not — the 27 being older
hand-built tracks that predate the convention.

This writes the missing disclosure, and writes it from the DATA: each one names
the exact labels that track stores and how many records carry them. Nothing is
generalised from one track to another and nothing is asserted that the artifact
does not already contain.

The units found, and what they are:

  جداول ومَلاحق   «الجدول (١)», «الملحق رقم (١)», «مرفق (١)», «جدول المقابل المالي»
                  — schedules and annexes attached to the instrument
  بنود            «أولاً», «البند ثانياً», «تمهيد», «مقدمة» — ordinal bands
  قواعد           «القاعدة الأولى:» — the Code of Judicial Conduct numbers rules
  ترقيم خاص       «١/٢», «أولا - 1», «1» — an implementing regulation numbering
                  its provisions against the law article each one implements
  لوائح مواد      «لائحة المادة الأولى» — per-article sub-regulations

Run with --apply to write; without it, reports and changes nothing.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from audit_corpus_llm_readiness import ARTICLE_LABEL_RE, FORM_DISCLOSURE_KEYS  # noqa: E402

OUT_DIR = os.path.join(ROOT, "reports", "corpus_llm_readiness_audit")
DISCLOSURE_KEY = "%s_units_that_are_not_articles"

# One artifact's only "non-article" label is not a different KIND of unit at all:
# «المادية الحادية والستون» in the Law of Sharia Procedure is «المادة» misspelt in
# the official MOJ PDF, and the corpus preserves the typo deliberately — its
# validator asserts the label verbatim. Writing the generic text there would tell
# a reader that record is not an article, which is false. It gets its own note
# instead, because the typo IS worth disclosing: a reader searching «المادة
# الحادية والستون» in that track will not match the label.
SOURCE_TYPO_LABELS = {
    "sharia_procedure/law": (
        "sharia_procedure_law_article_61_label_carries_a_source_typo",
        "**عنوان المادة الحادية والستين محفوظٌ بخطئه كما في المصدر**: يقرأ «الماد**ية** الحادية "
        "والستون» لا «المادة». **والخطأ خطأ ملف وزارة العدل الرسمي**، وقد أُبقي حرفياً — "
        "ومدقِّق هذا المسار يؤكد بقاءه نصاً — لأن المستودع ينقل ما نشرته الجهة لا ما يُظن أنها "
        "أرادته.\n\n**وأثرُه على البحث**: من يبحث في هذا المسار عن «المادة الحادية والستون» "
        "**لن يطابق العنوان المخزَّن**. والمادة نفسها مادةٌ أصيلة لا وحدةٌ من نوع آخر، ونصّها "
        "وموضعها وترقيمها سليمة؛ الخلل في لفظ العنوان وحده."),
}

# Each kind is recognised from the label itself, and named in the disclosure by
# what the source calls it — never by a category invented here.
KINDS = [
    ("جداول", re.compile(r"جدول|الجدول")),
    ("ملاحق ومرفقات", re.compile(r"ملحق|مرفق")),
    ("بنود", re.compile(r"^\s*(?:ال)?بند\b|^\s*(?:أولا|أولاً|ثانيا|ثانياً|ثالثا|ثالثاً|"
                        r"رابعا|رابعاً|خامسا|خامساً|سادسا|سادساً|سابعا|سابعاً|ثامنا|ثامناً|"
                        r"تاسعا|تاسعاً|عاشرا|عاشراً)\b|^\s*(?:تمهيد|مقدمة)\b")),
    ("قواعد", re.compile(r"^\s*القاعدة\b")),
    ("لوائح مواد", re.compile(r"^\s*لائحة\s+المادة\b")),
    ("ترقيم خاص", re.compile(r"^\s*[0-9٠-٩]|[٠-٩]\s*/\s*[٠-٩]|"
                             r"^\s*(?:أولا|ثانيا|ثالثا)\s*-\s*\d")),
]


def artifacts(track):
    for pattern in ("sources/%s/official_source/*.json" % track,
                    "sources/%s/*/official_source/*.json" % track):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            yield path


def classify(labels):
    kinds, unclassified = [], []
    for lab in labels:
        for name, rx in KINDS:
            if rx.search(lab):
                if name not in kinds:
                    kinds.append(name)
                break
        else:
            unclassified.append(lab)
    return kinds, unclassified


def save(path, doc):
    raw = open(path, encoding="utf-8").read()
    indent = 1 if re.search(r"^\s\"", raw, re.M) else 2
    text = json.dumps(doc, ensure_ascii=False, indent=indent)
    if raw.endswith("\n"):
        text += "\n"
    open(path, "w", encoding="utf-8").write(text)


def disclosure_text(track, kinds, examples, n_units, n_total):
    kind_phrase = "، و".join(kinds) if kinds else "وحدات غير مُبوَّبة بـ«المادة»"
    sample = "، ".join("«%s»" % e for e in examples[:4])
    return (
        "**ليست كل سجلات هذا المسار مواد.** منها **%d سجلاً من %d** وحداتٌ من نوع آخر — %s — "
        "وهذا ما تسمّيه الأداة نفسها، مثل: %s.\n\n"
        "**والحقول في هذا المستودع موحَّدة عمداً** (`article_number` و`article_key` و"
        "`number_label_ar`) لأن مخططاً واحداً عبر مئات المسارات أنفعُ من شكلٍ مطابقٍ لكل مسار "
        "على حدة؛ **غير أن هذه المقايضة لا تصحّ إلا بالإفصاح**. فقيمة `article_number` في هذه "
        "السجلات **موضعية** للترتيب والفهرسة، **ولا يُدَّعى بها أن الوحدة «مادة»**.\n\n"
        "**فلا يصح الاستشهاد بسجلٍ منها بوصفه «المادة (كذا)» من هذه الأداة**؛ الاستشهاد الصحيح "
        "**باللفظ المنشور** كما هو محفوظ في `number_label_ar`."
        % (n_units, n_total, kind_phrase, sample))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    written, skipped = [], []

    # Counted per ARTIFACT, not per track. «sharia_procedure» holds a law whose
    # single non-article label is a preserved source typo, and an implementing
    # regulation numbering 637 provisions «١/١» against the law articles they
    # implement. Summing them would write «638 of 880 records are not articles»
    # onto the law's artifact, which is false about that document.
    for pattern in ("sources/*/official_source/*.json", "sources/*/*/official_source/*.json"):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, os.path.join(ROOT, "sources"))
            tid = rel.split(os.sep)[0]
            component = rel.split(os.sep)[-3] if rel.count(os.sep) == 3 else None
            name = "%s/%s" % (tid, component) if component else tid
            try:
                doc = json.load(open(path, encoding="utf-8"))
            except Exception:                                      # noqa: BLE001
                continue
            arts = doc.get("articles") or {}
            units, total = [], 0
            for rec in arts.values():
                if not isinstance(rec, dict):
                    continue
                total += 1
                lab = (rec.get("number_label_ar") or "").strip()
                if lab and not ARTICLE_LABEL_RE.match(lab):
                    units.append(lab)
            if not units:
                continue

            blob = open(path, encoding="utf-8").read()
            key = DISCLOSURE_KEY % tid
            if any(k in blob for k in FORM_DISCLOSURE_KEYS) or key in blob:
                skipped.append({"artifact": name, "reason": "already discloses its numbering form"})
                continue

            seen, examples = set(), []
            for lab in units:
                if lab not in seen:
                    seen.add(lab)
                    examples.append(lab)
            kinds, unclassified = classify(examples)
            if name in SOURCE_TYPO_LABELS:
                key, text = SOURCE_TYPO_LABELS[name]
                if key in blob:
                    skipped.append({"artifact": name, "reason": "source typo already disclosed"})
                    continue
                kinds = ["خطأ إملائي في المصدر محفوظ حرفياً"]
            else:
                text = disclosure_text(tid, kinds, examples, len(units), total)

            if args.apply:
                disc = doc.setdefault("known_unresolved_discrepancies", [])
                if not any(isinstance(d, dict) and d.get("article_key") == key for d in disc):
                    disc.append({"article_key": key, "description": text})
                    save(path, doc)
            written.append({"artifact": name, "non_article_records": len(units),
                            "total_records": total, "kinds": kinds,
                            "example_labels": examples[:6],
                            "labels_not_matching_any_kind": unclassified[:6]})

    report = {
        "generated_note": (
            "Writes, for every track holding units that are not articles and saying nothing "
            "about it, a disclosure naming the exact labels that track stores and how many "
            "records carry them. The corpus stores every unit in article-named fields on "
            "purpose — one schema across 743 tracks is worth more than a faithful shape per "
            "track — and that trade is only honest while each such track says so, because a "
            "reader who does not know cites «المادة (3)» for what the source calls «الجدول (3)». "
            "Gazette-built tracks already write this at build time; these are older hand-built "
            "tracks that predate the convention. Every disclosure is generated from the "
            "artifact's own labels; nothing is generalised from one track to another."),
        "applied": bool(args.apply),
        "tracks_disclosed": len(written),
        "tracks_already_disclosing": len(skipped),
        "disclosures": written,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "unit_form_disclosures.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("%s %d tracks; %d already disclosing"
          % ("disclosed" if args.apply else "would disclose", len(written), len(skipped)))
    for w in written:
        flag = "  <-- unclassified: %s" % w["labels_not_matching_any_kind"] \
            if w["labels_not_matching_any_kind"] else ""
        print("   %-42s %4d/%-5d %s%s"
              % (w["artifact"][:42], w["non_article_records"], w["total_records"],
                 "/".join(w["kinds"]), flag))
    print("wrote reports/corpus_llm_readiness_audit/unit_form_disclosures.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
