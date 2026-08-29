#!/usr/bin/env python3
"""Instrument names as texts write them, folded to one key per instrument.

One instrument carries four names in 120 hand-labelled citations -- «الالئحة
التنفيذية لجباية الزكاة», «لائحة جباية الزكاة», «الالئحة التنفيذية لنظام
الزكاة», «لائحة جباية الزكاة الصادرة بعام 1438ه» -- and is sometimes given
only by the ministerial decision number that issued it. Counting cited
instruments without folding these counts one instrument as four.

Folding is by rule, not by a hand-written alias list per corpus: the rules are
(1) drop the issuing clause, (2) fold orthographic variants of ال/لا, (3) fold
«لائحة X» and «الالئحة التنفيذية لنظام X» onto the regulation of X, (4) treat
«النظام الضريبي» as «نظام ضريبة الدخل» where the corpus attests it. Rule (4)
is corpus knowledge and is flagged as such, because it is the only rule here
that could be wrong in another corpus.
"""

import re

ISSUING = re.compile(r"\s*(?:الصادر[ةه]?|المصدق[ةه]?|الموقع[ةه]?)\b.*$")
YEAR = re.compile(r"\s*(?:الصادرة?\s*)?(?:بعام|لعام|عام)\s*\d{3,4}\s*ه?\s*$")
SPACES = re.compile(r"\s+")

_FOLD = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})

# «الالئحة» is how the corpus's text layer renders «اللائحة»; both occur.
LAM_ALEF = ((r"الالئحة", "اللائحة"), (r"الئحة", "لائحة"), (r"الالسحة", "اللائحة"))

# corpus-attested alternative names. Each one is a claim about this corpus.
ALIASES = {
    "النظام الضريبي": "نظام ضريبة الدخل",
    "اللائحة التنفيذية للنظام الضريبي": "اللائحة التنفيذية لنظام ضريبة الدخل",
    "اللائحة التنفيذية لضريبة الدخل": "اللائحة التنفيذية لنظام ضريبة الدخل",
    "اللائحة التنفيذية لضريبة القيمة المضافة":
        "اللائحة التنفيذية لنظام ضريبة القيمة المضافة",
    "لائحة جباية الزكاة": "اللائحة التنفيذية لجباية الزكاة",
    "اللائحة التنفيذية لنظام الزكاة": "اللائحة التنفيذية لجباية الزكاة",
    "لائحة الزكاة": "اللائحة التنفيذية لجباية الزكاة",
    "قواعد عمل اللجان": "قواعد عمل لجان الفصل في المخالفات والمنازعات الضريبية",
    "قواعد عمل اللجان الضريبية":
        "قواعد عمل لجان الفصل في المخالفات والمنازعات الضريبية",
    "قواعد عمل لجان الفصل في المخالفات المنازعات الضريبية":
        "قواعد عمل لجان الفصل في المخالفات والمنازعات الضريبية",
    "قواعد وإجراءات عمل اللجان الضريبية":
        "قواعد عمل لجان الفصل في المخالفات والمنازعات الضريبية",
    # ministry judgments abbreviate the procedure law to its distinguishing
    # word alone: «ال مادة74 مرافعات»
    "مرافعات": "نظام المرافعات الشرعية",
    "نظام المحكمة التجارية": "نظام المحكمة التجارية",
    "لائحة نظام المحاكم التجارية":
        "اللائحة التنفيذية لنظام المحاكم التجارية",
    "اللائحة التنفيذية لنظام المحكمة التجارية":
        "اللائحة التنفيذية لنظام المحاكم التجارية",
    "نظام الاثبات": "نظام الإثبات",
    "نظام الافلاس": "نظام الإفلاس",
}


def canonical(name):
    """One key per instrument, or None for None. Never invents a name."""
    if not name:
        return None
    text = SPACES.sub(" ", name).strip()
    text = ISSUING.sub("", text)
    text = YEAR.sub("", text).strip(" ،؛.")
    for wrong, right in LAM_ALEF:
        text = text.replace(wrong, right)
    text = SPACES.sub(" ", text).strip()
    folded = "".join(text.split()).translate(_FOLD)
    for alias, target in ALIASES.items():
        if "".join(alias.split()).translate(_FOLD) == folded:
            return target
    # «لائحة جباية الزكاة الصادرة بالقرار الوزاري رقم (2082)» already trimmed;
    # a bare «الالئحة التنفيذية» carries no instrument and is not a name.
    if folded in {"".join(x.split()).translate(_FOLD)
                  for x in ("اللائحة التنفيذية", "اللائحة", "النظام")}:
        return None
    return text


def _tight(name):
    """Fold for comparison only: drop every space, fold the alef seats.

    Three of the five development digests insert spaces inside words on
    justified lines, so «نظام المر افعات الشرعية» and «نظام المرافعات الشرعية»
    reach a comparison as different strings while being one instrument. The
    display name keeps its spaces; only the comparison drops them.
    """
    return "".join(name.split()).translate(_FOLD)


def same(a, b):
    """True when two surface names denote one instrument."""
    ca, cb = canonical(a), canonical(b)
    if ca is None or cb is None:
        return ca is None and cb is None
    return _tight(ca) == _tight(cb)
