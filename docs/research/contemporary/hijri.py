#!/usr/bin/env python3
"""Tabular Islamic calendar arithmetic, so a commencement rule can be computed.

A Saudi statute typically commences a fixed number of DAYS after publication,
and the corpus is indexed in hijri QUARTERS. Turning one into the other needs
day arithmetic in a calendar whose month lengths are astronomical.

This uses the standard tabular (arithmetical) Islamic calendar. It is not the
Umm al-Qura calendar and can differ from an observed date by about a day. That
is stated wherever a date computed here is reported, and at quarter resolution
it is immaterial except for a date landing on a quarter boundary, which is
flagged rather than resolved.

    python3 hijri.py        # round-trip self-test
"""


def h2jd(y, m, d):
    """Hijri (y, m, d) -> Julian Day Number, tabular Islamic calendar."""
    return (11 * y + 3) // 30 + 354 * y + 30 * m - (m - 1) // 2 + d + 1948440 - 385


def jd2h(jd):
    jd = int(jd)
    l = jd - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = (((10985 - l) // 5316) * ((50 * l) // 17719)
         + (l // 5670) * ((43 * l) // 15238))
    l = (l - ((30 - j) // 15) * ((17719 * j) // 50)
         - (j // 16) * ((15238 * j) // 43) + 29)
    m = (24 * l) // 709
    d = l - (709 * m) // 24
    return 30 * n + j - 30, m, d


def jd2g(jd):
    """Julian Day Number -> proleptic Gregorian (y, m, d)."""
    a = int(jd) + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    dd = (4 * c + 3) // 1461
    e = c - (1461 * dd) // 4
    mm = (5 * e + 2) // 153
    return (100 * b + dd - 4800 + (mm + 2) // 12,
            mm + 3 - 12 * (mm // 10),
            e - (153 * mm + 2) // 5 + 1)


def quarter(y, m):
    return (y, (m - 1) // 3 + 1)


def add_days(y, m, d, n):
    return jd2h(h2jd(y, m, d) + n)


def fmt(y, m, d):
    return f"{y:04d}-{m:02d}-{d:02d}H"


def fmt_g(jd):
    y, m, d = jd2g(jd)
    return f"{y:04d}-{m:02d}-{d:02d}G"


def days_between(a, b):
    """a, b as (y, m, d) hijri."""
    return h2jd(*b) - h2jd(*a)


def main():
    bad = 0
    for y in range(1350, 1460):
        for m in range(1, 13):
            for d in (1, 10, 20, 29):
                if jd2h(h2jd(y, m, d)) != (y, m, d):
                    bad += 1
    print(f"round-trip failures over 1350-1459H: {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
