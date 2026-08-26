#!/usr/bin/env python3
"""Read a Saudi article number as a judgment writes it.

Four in ten citations spell the number out — «الخامسة والتسعون بعد المائة» —
three in ten use Latin digits, one and a half in ten Arabic-Indic, and the
rest carry a paragraph after a slash. A join at article level has to read all
of them or it silently measures only the ones written in digits, which is a
sample of convenience masquerading as a census.

Returns (article, paragraph). The paragraph is whatever followed a slash:
«المادة 78/1/ب» is article 78, paragraph "1/ب".
"""

import re

UNITS = {
    "الاولى": 1, "الأولى": 1, "الحادية": 1, "الحادي": 1,
    "الثانية": 2, "الثاني": 2, "الثالثة": 3, "الثالث": 3,
    "الرابعة": 4, "الرابع": 4, "الخامسة": 5, "الخامس": 5,
    "السادسة": 6, "السادس": 6, "السابعة": 7, "السابع": 7,
    "الثامنة": 8, "الثامن": 8, "التاسعة": 9, "التاسع": 9,
}
TENS = {
    "العاشرة": 10, "العاشر": 10,
    "العشرون": 20, "العشرين": 20, "الثلاثون": 30, "الثلاثين": 30,
    "الاربعون": 40, "الأربعون": 40, "الاربعين": 40, "الأربعين": 40,
    "الخمسون": 50, "الخمسين": 50, "الستون": 60, "الستين": 60,
    "السبعون": 70, "السبعين": 70, "الثمانون": 80, "الثمانين": 80,
    "التسعون": 90, "التسعين": 90,
}
HUNDREDS = {
    "المائة": 100, "المئة": 100, "المائه": 100, "المئه": 100,
    "المائتين": 200, "المئتين": 200, "المائتان": 200, "المئتان": 200,
    "الثلاثمائة": 300, "الثلاثمئة": 300, "الاربعمائة": 400, "الأربعمائة": 400,
    "الخمسمائة": 500, "الستمائة": 600, "السبعمائة": 700, "الثمانمائة": 800,
    "التسعمائة": 900,
}
# Judgments also write the hundreds without the article: «المادة مائتين».
HUNDREDS.update({k.lstrip("ال"): v for k, v in list(HUNDREDS.items())})
HUNDREDS.update({"مائتـين": 200, "مئتـين": 200})

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _strip(word):
    return re.sub(r"[ًٌٍَُِّْـ]", "", word)


def parse(raw):
    """(article:int|None, paragraph:str|None)"""
    if not raw:
        return None, None
    s = " ".join(str(raw).translate(ARABIC_DIGITS).split())
    s = re.sub(r"^(?:رقم|المادة|الماده)\s*", "", s).strip(" ()[]")

    para = None
    # «المادة 443 فقرة (أ)» marks the paragraph in words rather than a slash
    m = re.search(r"\s*فقر[ةه]\s*\(?\s*([^\)\s]+)", s)
    if m:
        para = m.group(1).strip("()")
        s = s[:m.start()].strip()
    if "/" in s:
        head, _, tail = s.partition("/")
        para = para or " ".join(tail.split()) or None
        s = head.strip()

    m = re.fullmatch(r"(\d{1,4})\s*", s)
    if m:
        return int(m.group(1)), para

    # spelled out: units + tens, then «بعد المائة» style offsets
    words = [_strip(w) for w in re.split(r"\s+|و(?=ال)", s) if w]
    total = base = 0
    after = 0
    seen = False
    i = 0
    while i < len(words):
        w = words[i].lstrip("و")
        if w in UNITS:
            base += UNITS[w]; seen = True
        elif w in TENS:
            base += TENS[w]; seen = True
        elif w in ("عشرة", "عشر"):
            base += 10; seen = True
        elif w == "بعد" and i + 1 < len(words):
            nxt = _strip(words[i + 1]).lstrip("و")
            if nxt in HUNDREDS:
                after = HUNDREDS[nxt]; i += 1
        elif w in HUNDREDS and not seen:
            base += HUNDREDS[w]; seen = True
        i += 1
    total = base + after
    return (total, para) if seen and total else (None, para)
