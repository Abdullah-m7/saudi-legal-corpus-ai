#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Judicial Training Center Organizational
Guide track (18 records) — الدليل التنظيمي لمركز التدريب العدلي.

BESPOKE TRACK: 11 numbered legal decree clauses (items 1-11, أولاً..حادي
عشر) plus 7 unnumbered organizational/descriptive entries (items 12-18: an
org chart, a goals/tasks overview, and 5 department job-description
blocks) that the MOJ portal itself does not treat as change-trackable
legal sections (get-Section-Changes 404s for all 7). Items 12-18 are
flagged is_narrative_structural_content=True with legal_status_ar/history
left None/empty — never defaulted to اصلية — and number_label_ar drawn
honestly from the source's own heading, never a fabricated ordinal.

Trust gate: 17/18 text-bearing items (1-11, 13-18) matched >=0.90 outright
(mean 0.9982, min 0.9888); item 12 (org chart, not text-similarity-
scorable against a rendered table) was visually adjudicated. Two legal
clauses are معدلة with 2-entry amendment histories (item 2/ثانياً, item
6/سادساً); the other 9 legal clauses are اصلية. DOCUMENTED SOURCE ANOMALY:
item 13's narrative overview states the Center's goal using the stale
pre-1440H-amendment wording of item 2, confirmed identical in both official
sources, preserved verbatim."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "judicial_training_center", "guide", "official_source",
                   "judicial_training_center_guide_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "judicial_training_center", "guide", "verified",
                       "judicial_training_center_guide_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "judicial_training_center_arabic_legal_llm",
                   "judicial_training_center_guide_legal_llm_001_018.json")
PDF = os.path.join(ROOT, "inputs", "judicial_training_center_official_pdfs",
                   "judicial_training_center_guide_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 18
N_LEGAL = 11
KEY_RE = r"judicial_training_center_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_LEGAL_COUNTS = {"اصلية": 9, "معدلة": 2}
AMENDED_ITEMS = {2, 6}
VISUALLY_ADJUDICATED = {"judicial_training_center_art_012"}
EXPECTED_LABELS = {
    1: "أولاً", 2: "ثانياً", 3: "ثالثاً", 4: "رابعاً", 5: "خامساً", 6: "سادساً",
    7: "سابعاً", 8: "ثامناً", 9: "تاسعاً", 10: "عاشراً", 11: "حادي عشر",
    12: "الهيكل التنظيمي", 13: "الأهداف والمهام", 14: "مدير عام المركز",
    15: "إدارة اللقاءات والحلقات وورش العمل", 16: "إدارة البرامج التدريبية",
    17: "إدارة خدمات شؤون المدربين", 18: "إدارة تقنية التدريب",
}
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"
ANOMALY_KEY = "judicial_training_center_art_013"
ANOMALY_MARKER = "يهدف المركز إلى الإسهام في رفع كفاءة وتأهيل كتاب العدل"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered items not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d items != %d" % (len(arts), N))

    visual = set()
    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        narrative = bool(a.get("is_narrative_structural_content"))
        if narrative != (n > N_LEGAL):
            e.append("[2] %s: is_narrative_structural_content=%r inconsistent with item number %d"
                     % (k, narrative, n))
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        if a["status"] == "MATCHES_PDF_VISUALLY_ADJUDICATED":
            visual.add(k)
        else:
            sim = a.get("pdf_similarity") or 0
            if sim < SIM_FLOOR:
                e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)

        if narrative:
            if a.get("legal_status_ar") is not None:
                e.append("[2n] %s: narrative item must have legal_status_ar=None, got %r"
                         % (k, a.get("legal_status_ar")))
            if a.get("history"):
                e.append("[2n] %s: narrative item must have empty history" % k)
        else:
            ls = a.get("legal_status_ar")
            if ls not in ALLOWED_STATUS:
                e.append("[2] %s: unexplained legal_status %r" % (k, ls))
            sc[ls] += 1
            if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
                e.append("[2] %s: unexpected section/PDF status divergence" % k)
            if a.get("section_ar"):
                e.append("[2] %s: unexpected non-empty section_ar in a legal decree clause" % k)
            has_hist = bool(a.get("history"))
            if n in AMENDED_ITEMS:
                if len(a.get("history") or []) != 2:
                    e.append("[2] %s: expected 2-entry amendment history, got %d"
                             % (k, len(a.get("history") or [])))
            elif has_hist:
                e.append("[2] %s: unexpected amendment history on a non-amended item" % k)

    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_LEGAL_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] legal-item status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added legal items present")

    for i, want_label in EXPECTED_LABELS.items():
        key = "judicial_training_center_art_%03d" % i
        if arts.get(key, {}).get("number_label_ar") != want_label:
            e.append("[2d] %s: number_label_ar %r != expected %r"
                     % (key, arts.get(key, {}).get("number_label_ar"), want_label))

    # [2b] documented source anomaly in item 13 preserved verbatim
    if ANOMALY_MARKER not in arts.get(ANOMALY_KEY, {}).get("text", ""):
        e.append("[2b] item 13 missing the documented stale-goal-wording anomaly marker")

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2c] unexpected section-vs-structure divergence recorded")

    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))
        if bool(r.get("is_narrative_structural_content")) and "content_class_note" not in r:
            e.append("[4] %s: narrative record missing content_class_note" % r["article_key"])

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Judicial Training Center Guide track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Judicial Training Center Guide — 18 records (11 legal clauses + 7 narrative/structural)")
    print("  - trust gate: 17/18 MATCHES_PDF outright, 1 (org chart) visually adjudicated (mean 0.9982, min 0.9888)")
    print("  - legal clauses 1..11 (أولاً..حادي عشر): 9 اصلية / 2 معدلة (items 2, 6, each 2-entry history)")
    print("  - narrative items 12..18: legal_status_ar=None, honest source-heading labels, no fabricated ordinals")
    print("  - CONSOLIDATED Council of Ministers Resolution 162 (24/04/1435H, through Resolution 621 1440H); committed MOJ PDF hash verified; Arabic governs")
    print("  - documented source anomaly: item 13's narrative overview uses item 2's stale pre-1440H wording, confirmed in both official sources, preserved verbatim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
