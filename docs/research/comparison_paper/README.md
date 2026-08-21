# Paper 6 — The Second Jurisdiction

*Working title: does the finding travel? Applying a provenance schema
prospectively to a second state's published law.*

Paper 5 (`../provenance_paper/`) measured whether one state's official legal
record was available and internally consistent when someone tried to use it at
scale, and proposed a five-field provenance schema for publishers of official
data. It has one weakness it states openly: **n = 1**. It argues that the
method transfers to other jurisdictions and to non-legal public data, and an
argument is not a demonstration.

This is the demonstration. It is not a replication.

## Why the United Kingdom

Two reasons, and the second matters more than the first.

**It separates the two properties paper 5 says are distinct.** That paper's
central claim is that *availability* and *internal consistency* are different
failures with different remedies, and that a single confidence score collapses
them. The Saudi corpus is a weak demonstration of that claim because both
properties are impaired at once. `legislation.gov.uk` is the clean case: a
documented API, permanent URIs, a 5.9 MB document served in 1.5 seconds — and,
by the service's own published metadata, text that does not reflect the law in
force.

**The inconsistency is declared, machine-readable and national in scope.** Each
Act's metadata carries a `ukm:UnappliedEffects` block: amendments enacted but
not yet incorporated into the text the same service displays. The Data
Protection Act 2018 carries **309 such effects, 307 of them marked
`RequiresApplied="true"`**. That is the same class of defect as the four Saudi
instruments whose portal text and amendment log disagree — except that here the
publisher declares it, and it can be counted across a whole statute book rather
than found by hand.

The comparison is therefore not "a worse publisher and a better one". It is a
publisher that fails on availability and a publisher that fails on consistency,
which is the shape paper 5 predicted and could not show.

## What is new here, beyond the second data point

Paper 5's provenance record was a **by-product**. Someone wrote down, in prose,
what each retrieval attempt returned, and the analysis had to recover a
measurement from 158 distinct free-text strings — of which 24 per cent turned
out not to be provenance at all. The paper's proposal was that five closed
fields would have carried the same information at no extra cost, because a
collector that knows how it obtained a document knows all five already.

`collect_uk.py` populates those five fields at the moment of collection,
unchanged from Table 2 of that paper. This is the first prospective use of the
schema, and it is a test of the paper's cost claim, not an illustration of it.
If the claim is false it should fail here, visibly.

## Method notes

- **`robots.txt` sets `Crawl-delay: 5`, and the collector honours it.** A full
  sweep of the Public General Acts therefore takes hours. An article about how
  publishers of official data are treated by those who consume them should not
  be built by ignoring what this one asked for.
- **`introduction/data.xml`, not `data.xml`.** The lighter endpoint carries the
  complete `UnappliedEffects` block at about a ninth of the bytes — verified
  equal on the Data Protection Act 2018, 309 elements in both. Nine times less
  traffic for the same measurement.
- **Failed attempts are recorded, not retried away.** A non-200 is evidence
  about availability, which is half of what is being measured.
- **`corroboration` is 0, not 1.** One official source taken as published, with
  nothing cross-checked against a second. Counting the source itself would
  inflate every record in the collection.

## A correction made in the first hour

The first reconnaissance sampled 20 Acts through the `/changes/affected/` feed
and found 2,487 recorded effects. That number is **not** a count of unapplied
effects: the feed counts every effect on an Act, applied and unapplied
together. Publishing it as "amendments not incorporated" would have inflated
the headline by an unknown factor.

The sound measure is the `UnappliedEffects` block in each Act's own metadata,
which is what the collector reads. This is the same trap as the base-rate error
in paper 4 (`../amendment_paper/`), and it appeared within an hour of starting.

## Reproduce

```
python3 docs/research/comparison_paper/collect_uk.py --years 2018-2020
python3 docs/research/comparison_paper/collect_uk.py --all
```

Read-only against `legislation.gov.uk`. Resumable: a year already collected is
skipped, so a long sweep can be stopped and restarted without refetching.

## Status

- [x] Jurisdiction chosen, on evidence rather than convenience: reachability,
      API, and a measurable consistency gap all verified before committing.
- [x] Collector written, with the five-field schema applied prospectively.
- [ ] Pilot sweep, then the full statute book.
- [ ] Analysis: what share of Acts, and of provisions, does the service itself
      flag as not reflecting the law in force? How old are the oldest unapplied
      effects?
- [ ] Decide the unit of comparison. Saudi figures are per *article* and per
      *instrument*; the UK equivalent is per *provision* and per *Act*, and the
      two are not the same object. This has to be settled before any number is
      reported side by side, not after.
- [ ] Venue. Not chosen, and not to be chosen before the result is known.
