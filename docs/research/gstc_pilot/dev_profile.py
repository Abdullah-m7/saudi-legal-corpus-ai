#!/usr/bin/env python3
"""What the hand-labelled GSTC_DEV set says a citation parser must handle.

Every number in the README beside this file comes from here. Run it after any
change to the labels; do not retype a figure.

    python3 dev_profile.py            # human-readable
    python3 dev_profile.py --json     # machine-readable, for numbers.tex
"""

import collections
import json
import re
import sys
from pathlib import Path

DEV = Path(__file__).resolve().parent / "gstc_dev.json"


def shape(form):
    if form is None:
        return "absent"
    if re.fullmatch(r"\(\d+\)", form):
        return "digits in parentheses"
    if re.fullmatch(r"\d+", form):
        return "bare digits"
    if re.fullmatch(r"رقم \(\d+\)", form):
        return "رقم then digits"
    if form.startswith("("):
        return "words in parentheses"
    return "bare words"


def profile():
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    items = dev["items"]
    if not dev.get("annotated"):
        sys.exit("gstc_dev.json is not annotated")
    labels = [i["label"] for i in items]
    cited = [l for l in labels if l["isCitation"]]
    n = len(cited)

    def count(key):
        return dict(collections.Counter(l[key] for l in cited).most_common())

    forms = collections.Counter(shape(l["articleForm"]) for l in cited)
    spelled = sum(v for k, v in forms.items() if "words" in k)
    return {
        "sampled": len(items),
        "citations": n,
        "nonCitations": len(items) - n,
        "instrumentSource": count("instrumentSource"),
        "segment": count("segment"),
        "instrument": count("instrument"),
        "articleForm": dict(forms.most_common()),
        "articleSpelledOut": spelled,
        "withParagraph": sum(1 for l in cited if l["paragraph"]),
        "instrumentUnresolvable": sum(1 for l in cited if l["instrument"] is None),
        # the claim-bearing figure: how much of what looks like a citation is
        # the tribunal's own, rather than a party's or a list of authorities
        "tribunalReasoningShare": round(
            100 * count("segment").get("reasoning", 0) / n, 1),
        "nonLocalInstrumentShare": round(
            100 * (n - count("instrumentSource").get("local", 0)) / n, 1),
    }


if __name__ == "__main__":
    p = profile()
    if "--json" in sys.argv:
        print(json.dumps(p, ensure_ascii=False, indent=1))
    else:
        print(f"sampled {p['sampled']}, citations {p['citations']}, "
              f"non-citations {p['nonCitations']}")
        for key in ("instrumentSource", "segment", "articleForm", "instrument"):
            print(f"\n{key}")
            for k, v in p[key].items():
                print(f"  {v:3d}  {k}")
        print(f"\narticle number spelled out : {p['articleSpelledOut']}")
        print(f"paragraph or subparagraph  : {p['withParagraph']}")
        print(f"instrument not resolvable  : {p['instrumentUnresolvable']}")
        print(f"tribunal's own reasoning   : {p['tribunalReasoningShare']}%")
        print(f"instrument not local       : {p['nonLocalInstrumentShare']}%")
