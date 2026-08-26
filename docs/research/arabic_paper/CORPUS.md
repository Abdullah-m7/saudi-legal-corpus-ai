# The Saudi Judgments Corpus

50,666 Saudi court judgments in full text, collected from the Ministry of
Justice's legal portal on 25–26 August 2026. 327 million characters across
eleven benches, 24 cities and the Hijri years 1422–1448.

This is the second corpus in this repository. The first covers legislation —
what the state enacts. This one covers what the courts do with it.

## Where it comes from

The portal at <https://laws.moj.gov.sa> renders nothing in its page source;
it is a Nuxt application that fetches everything from a public gateway. These
endpoints came from reading its own lazy-loaded bundle, and the one that
matters was invisible to every guess because the ministry spells it the
British way:

```
POST https://laws-gateway.moj.gov.sa/apis/legislations/v1/Judgements/judgements-list
GET  https://laws-gateway.moj.gov.sa/apis/legislations/v1/Judgements/get-details?id=
```

No authentication. The search body the portal itself sends:

```json
{"pageNumber": 1, "pageSize": 500, "judgmentNo": null, "decisionNo": null,
 "cityId": null, "courtTypes": 0, "courtId": null, "term": "",
 "dateFrom": null, "dateTo": null, "sortingBy": 2}
```

`term` is free text matched inside the body of the judgment, not just its
title. It matches morphologically: a query for `المستهلك` returns judgments
whose text only ever says `للمستهلك`.

## Contents

| Bench | Judgments |
|---|---|
| المحكمة التجارية | 48,124 |
| المحكمة العليا — الهيئة الدائمة | 1,459 |
| محكمة الاستئناف | 556 |
| المحكمة العليا | 280 |
| المحكمة العامة | 193 |
| محكمة الأحوال الشخصية — الأحكام القديمة | 25 |
| المحكمة العمالية | 14 |
| مجلس القضاء الأعلى — الهيئة الدائمة | 10 |
| محكمة الأحوال الشخصية | 3 |
| محكمة الاستئناف الجزائية المتخصصة | 1 |
| التجاري — القديم | 1 |

Riyadh 22,677 · Jeddah 11,155 · Dammam 9,261 · Makkah 2,108 · Madinah 1,866,
across 24 cities. Concentrated on 1444H (18,812) and 1442H (10,774).

Judgment length: median 4,640 characters, 90th percentile 12,425, longest
96,583.

## Layout

```
judgments_index.jsonl     50,666 metadata records, one per line
judgments/*.jsonl         507 shards of 100 judgments each, full text
collect_all_judgments.py  the collector, two stages
redact.py                 the masking pass described below
```

Shards are 100 judgments because the collection took fourteen hours across a
container that does not live that long. Each shard is committed and pushed
the moment it is written, so an interruption costs at most a hundred
judgments and a later run skips every id already in a shard. The collection
was cut short twice — at 24,300 and at 45,900 — and lost nothing either time.

## A record

```json
{
  "id": "...", "case_number": "...", "judgment_number": "...",
  "hijri_date": "1445-09-04", "hijri_year": 1445,
  "gregorian_date": "2024-03-14T00:00:00",
  "court": "المحكمة التجارية", "court_type": "Lawsuit", "city": "الرياض",
  "is_appeal": false, "title": "القضية رقم ... لعام 1445هـ",
  "has_judgment": true, "has_appeal": false,
  "sections": {"judgmentTextofRulling": "...", "judgmentReasons": "..."},
  "text": "...", "characters": 4569,
  "provenance": {
    "source_class": "official primary — the publisher's own gateway",
    "retrieval_route": "GET .../Judgements/get-details?id=",
    "corroboration": "index record and detail record agree on the judgment number and court",
    "transformation": "HTML fragments stripped to plain text; whitespace collapsed; sections kept separately as well as concatenated",
    "discrepancy": null,
    "retrieved_at": "2026-08-26T..."
  }
}
```

Sections are kept both separately and concatenated: a study of judicial
reasoning wants `judgmentReasons` alone, an embedding wants `text`.

The `provenance` block carries the five fields the provenance paper in this
repository proposed. The point of proposing a schema is to live under it.

## Known defects

**The pagination is not stable, and one pass silently misses judgments.**
The first complete pass returned 49,515 of the 50,638 the endpoint itself
reported. That gap was not duplicates: re-fetching page 7 afterwards returned
seven ids the pass had never seen, with no page having failed. Records shift
between pages while the listing is read. Six sweeps were needed — +908, +188,
+2, +1, +0, +0 — before two consecutive sweeps added nothing. Anyone who
pages this endpoint once and trusts `totalCount` will believe they have
everything and be wrong by about 2%.

**The corpus is live.** The reported total went 50,634 → 50,638 → 50,652 →
50,662 over the hours of collection. Every record therefore carries
`retrieved_at`, and the index is 50,666: more than any single reading of the
count, because it accumulates across sweeps.

**`is_appeal` is false in all 50,666 records.** The field exists in the API
and is never populated. Any classification built on it is built on nothing.

**The detail endpoint sometimes refuses what the index lists.** 55 judgments
returned no detail record on first request. All 55 succeeded on a later pass,
so the corpus is complete, but the failure is intermittent rather than
permanent and a single-pass collector would have dropped them without
noticing.

**The publisher's redaction is inconsistent, and this corpus corrects it.**
The ministry masks identities with `(...)` — 869,183 times, in 98.4% of
judgments. Not everywhere. A scan of all 50,666 found 73 national ID or
civil-registry numbers stated beside a full name, 122 mobile numbers
including named lawyers and arbitrators, and one judgment where the identity
number is masked while the mobile number two words later is not.

`redact.py` masks 540 such identifiers across 134 judgments, using the
publisher's own marker so our redaction cannot be told from theirs. Bare
ten-digit numbers are kept: most are commercial registrations, which are
public by design, and a number attached to no name identifies nobody. Court
addresses at `moj.gov.sa` are kept as institutional. Names are kept — they
are what the ministry chose to publish.

Earlier commits on this branch carry the text as collected, before the mask
was applied.

## Regenerating it

```bash
python3 collect_all_judgments.py --stage index   # ~20 min per sweep
python3 collect_all_judgments.py --stage text    # ~14 hours, resumable
python3 redact.py                                # then always this
```

The collector paces itself so that requests start at least a second apart,
which is the limit the ministry's own client imposes on itself. `robots.txt`
allows everything and advertises `sitemap-judicial-decisions.xml`, so these
pages are published for indexing. The sitemap lists 10,000 of the judgments
and was used as an independent check on the sweeps: on the final pass it
carried nothing the sweeps had missed.

## Standing

The judgments are Crown-published public records; the ministry states that it
publishes them to spread judicial awareness and to let researchers study what
the courts decide. This repository redistributes them with the publisher's
redaction repaired, not weakened. Anyone using the corpus for research on
individuals rather than on adjudication should not be using it.
