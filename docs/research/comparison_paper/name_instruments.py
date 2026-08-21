#!/usr/bin/env python3
"""Fetch the titles of the instruments behind the old queue, from the source.

The analysis can say that ten instruments hold a third of the old backlog but
not which ten, because `ukm:AffectingTitle` is a child element and the
collector's attribute parse missed it. Supplying the names from memory instead
is the fault that reached paper 4's opening paragraph before review caught it,
so they are fetched.

One request per instrument, at the publisher's declared crawl delay, writing
`instrument_titles.json` for the analysis to read. Cheap: the instruments are
counted in tens, not thousands.
"""

import json
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "uk_analysis_results.json"
OUT = HERE / "instrument_titles.json"
CRAWL_DELAY = 5.0


def title_for(uri):
    path = uri.split("/id/")[-1]
    url = f"https://www.legislation.gov.uk/{path}/introduction/data.xml"
    body = subprocess.run(["curl", "-sS", "-L", "--max-time", "40", url],
                          capture_output=True, text=True).stdout
    m = re.search(r"<dc:title>([^<]*)</dc:title>", body)
    return m.group(1) if m else None


def main():
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    wanted = [row["affecting_uri"]
              for row in r["old_queue_concentration"]["top_10"]]
    have = {}
    if OUT.exists():
        have = json.loads(OUT.read_text(encoding="utf-8"))
    for uri in wanted:
        if have.get(uri):
            continue
        have[uri] = title_for(uri)
        print(f"  {uri.split('/id/')[-1]:<20s} {have[uri]}")
        time.sleep(CRAWL_DELAY)
    OUT.write_text(json.dumps(have, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    missing = [u for u in wanted if not have.get(u)]
    if missing:
        print(f"\nno title found for: {missing}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
