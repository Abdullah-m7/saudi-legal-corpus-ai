# Paper 6 — The Second Jurisdiction

*Ninety-Three Per Cent of a Backlog Is Not a Backlog: Reading a Public
Publisher's Own Quality Signal.*

## The finding, and the two withdrawn versions of it

`legislation.gov.uk` flags **14,407** effects across the modern statute book as
not applied to the text it displays. Read as a backlog — which is how the flag
reads, and how this study first read it — that is a very large number.

It overstates by a factor of **131**:

| | Effects | Share |
|---|---|---|
| Prospective — enacted, no commencement date | 13,396 | 93.0% |
| Commencement scheduled, date still future | 901 | 6.3% |
| **In force now, not applied** | **99** | **0.7%** |
| In force, no date recorded | 11 | 0.1% |

Only the last two describe text that does not reflect the law. That is **9 Acts
of 1,578** (0.6%), across 77 provisions.

**The service meets its published three-month target without exception.** The
longest any amendment has been in force and unapplied is **21 days** — and all
99 dated cases share one commencement, three weeks before the analysis date, in
the Pension Schemes Act 2021 and its Northern Ireland counterpart. The entire
population of out-of-date text in the modern UK statute book is a single
commencement event.

### It took three attempts to measure

1. **`RequiresApplied="true"`** → 513 Acts, 14,407 effects. Withdrawn: the flag
   says only that an effect is not applied, not that it should be.
2. **Excluding `Prospective="true"`** → 84 Acts, 1,011 effects. Also wrong: an
   effect can have a settled commencement date that is still in the future. A
   date fixed for next March is no more in force than no date at all.
3. **Excluding future commencement dates** → 9 Acts, 110 effects. Verified
   independently.

A second claim was withdrawn with the first, and it was the sharper one. Two
drafts said commencement dates are not published, and concluded that the
publisher withholds the field needed to check its own standard. Every effect
carries it, in `ukm:InForce`. The duration figures above are a subtraction over
that field.

### Why the error is the contribution

Everything needed to read this record correctly is published. The failure is
arrangement: the flag that invites the wrong conclusion is an **attribute** on
the effect; the fact that corrects it is a **child element** inside it. A
consumer parsing attributes — the ordinary way to read this format — gets the
first and not the second, and the publisher's own prose calls all four states
"unapplied effects", so checking the documentation confirms the wrong reading.

The companion study asks publishers to ship the strength of the evidence with
the text. Here it is shipped, completely and machine-readably, and the default
reading is still wrong by two orders of magnitude. Publishing the
distinguishing fact is not sufficient. Where it sits, relative to the fact that
invites the error, decides what most readers conclude.

## Venue

**Recommended: ACM *Digital Government: Research and Practice*, as a Case
Study.** Its own description of that type — "field-based reports reflecting on
lessons learned from novel experiments" — is a literal description of this
article, and its 2,000–4,000 word band fits the manuscript as written, with no
padding and no cutting. Double-anonymous review; the audience is government
data, metadata and digital governance, which is exactly this article's.

The alternative in the same journal is a Research Paper at 8,000–12,000 words,
three times the current length. The material exists — the availability figures
that were recorded but deliberately not compared, the method in full, the
narrative of three successive corrections, and a literature section — but it is
days of work, and the risk is real: the sharpest thing this article has is a
short, hard result, and tripling it to meet a band would bury that under
apparatus.

If it is rejected as too slight, expansion is still open, and by then a
reviewer's report says *where* to expand. That is better than guessing now.

Two practical points. ACM has been fully open access since January 2026, so
acceptance triggers an APC; waivers exist, as with paper 5. And submission is a
PDF in the ACM large format template rather than Word — a LaTeX manuscript
makes that cheap but not free.

*Government Information Quarterly* carries more weight and was not assessed:
its guide-for-authors sits behind a CAPTCHA that this environment cannot pass,
and after the errors recorded above, no requirement here is going to be written
down from memory.

## Quality review — what it caught

Run as with papers 1–5, after the rebuild. Four defects, one of them the same
class that review caught in three earlier papers: a sentence that survived a
revision and now asserted something the corrected data contradicts.

1. **A claim about an Act that does not exist.** The schema section argued its
   point with "an Act whose displayed text omits hundreds of enacted
   amendments". Under the corrected measure the whole statute book holds 110
   such effects across 9 Acts. The argument never needed the size, so it now
   makes the point without it — and says so.
2. **A self-contradiction.** The method section said an unapplied effect "is a
   property of the data as published: any reader, on any network, at any time,
   obtains the same count." The article's entire finding is that readers obtain
   different counts depending on which fields they parse. The claim is now
   split: reproducible in principle, not agreed in practice, and the difference
   between those two is what the paper is about.
3. **Reasoning built for a backlog that is not there.** The section on the
   service standard closed by saying any finding "has to be about the queue's
   tail rather than its existence". There is no tail. The standard's real role
   is that it makes compliance testable, which is what the paragraph now says.
4. **An omission that weakened the contribution.** The article reported being
   wrong by a factor of 131 without mentioning that the first correction was
   also wrong. That second failure is the sharper one — excluding prospective
   effects is the obvious fix and still overstates tenfold — and it is now in
   the introduction, because "each stage looked correct until the next field
   was read" is the paper's argument, not an aside.

Everything below this line predates the correction and is kept because the
sequence that produced it is part of the record.

---

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

## A measure that had to be renamed before it became a number

The analysis first reported "oldest outstanding amendment: enacted 1982, 6
years unincorporated". Both halves were wrong, and the second was wrong in an
interesting way.

`AffectingYear` is the year of the instrument that makes the amendment. It is
not the date the amendment took effect, and it is not bounded by the age of the
Act being amended. **The Transport Act 1982 amends the Road Traffic Act 1988**:
provisions that were never commenced in 1982 bite, once commenced, on a later
consolidating Act. In 1988 alone, 20 unapplied effects have an affecting
instrument older than the Act they affect.

So a subtraction of years measures nothing. Commencement dates are not in this
metadata, which means the duration an amendment has gone unincorporated
**cannot be computed from this collection at all**. What can be stated exactly
is narrower: the affecting instrument dates from year Y, and the effect is
still unapplied as at a stated date. The analysis now says that, takes the date
as `--as-of` rather than reading today's clock silently, and records the value
in the results so the same files give the same answer.

The Road Traffic Act 1988 is the case worth keeping either way: the official
service displays a text that omits **261 enacted amendments**, some of them
from an Act passed six years before it.

## The unit of comparison, settled

Paper 5 reports Saudi figures per *article* and per *instrument*. The UK
equivalents are per *provision* and per *Act*, and the README carried this as
an open question because a count of affected provisions is not a share without
a denominator.

The denominator was already in the bytes being fetched and thrown away.
`ukm:Statistics` gives `BodyParagraphs`, `ScheduleParagraphs` and
`TotalParagraphs` per Act. A Saudi article is a numbered provision in the body
of an instrument, so `BodyParagraphs` is the closer analogue — but affected
provisions do sit in schedules, so both totals are reported and neither is
presented as *the* answer.

## The confound that would have deflated the headline

The same response carries `ukm:DocumentStatus`. The service maintains some Acts
in **revised** form and serves others only **as enacted**.

An Act that is not maintained carries no unapplied effects **because nobody is
applying any** — not because its text is current. In a count of "Acts
displaying text known to be out of date" it would sit in the denominator
looking clean and pull the share down. Nothing in the effects block reveals
this; only the status field does.

The analysis now reports the share over the maintained set as well as over
everything retrieved, states the gap, and counts the unmaintained Acts that
carry an unapplied effect anyway.

`dc:modified` is kept for the same kind of reason: it is the date the service
last revised the record, which separates a standing backlog from work in
progress.

All three fields cost one extra parse and no extra request. The sweep was
restarted so every record carries them.

## Two collectors, and what they cost

The sweep was restarted several times as the collector learned what the
endpoint offers. On one of those restarts the old process was not killed:
`pgrep -f ... | head -1` returned the shell wrapper's pid, not the
interpreter's, so `kill` hit the wrong thing and the previous sweep kept
running.

For about ten minutes **two collectors ran at once**. Two consequences, and the
second is the one that matters.

The visible one: the old process wrote 1990 and 1991 without the new metadata
fields while the new process wrote 1988 with them. That surfaced as a
nonsensical reading — 46 Acts appearing to publish no `DocumentStatus` and no
paragraph statistics, and 15 of those "unmaintained" Acts carrying unapplied
effects, which contradicted the reason the field had just been added. The two
year files were deleted and recollected; the real distribution is 93 `revised`
to 8 `final`, with every Act publishing a paragraph count.

The one worth recording: **for those ten minutes this collection was hitting
`legislation.gov.uk` at twice the crawl delay it declares**, in a project whose
argument is about how publishers of official data are treated by the people who
consume them. Nothing was harmed at that volume, and it is written down here
rather than quietly fixed, because a paper that asks publishers to be honest
about their own defects has no business hiding its own.

Killing a background process is now done by the interpreter's pid, read from
`ps`, and verified gone before anything restarts.

## A ratio with a numerator and denominator from different sets

While the stale-process artefact was being traced, the per-provision figure was
found to be computing affected provisions across **every** retrieved Act and
body paragraphs across only the Acts that publish a count. Both sides of the
fraction were drawn from different sets, and the rate came out inflated.

It now takes both from the same set and reports how many Acts were excluded.
With clean data no Act is excluded — but the guard stays, because the fault was
invisible while the numbers looked plausible, which is the only kind of fault
that reaches print.

## The assumption the whole paper rests on, checked

Everything here reads `RequiresApplied="true"` as *this amendment is in force
and is not in the text the service displays*. That reading came from the shape
of the data, not from the publisher, and if it were wrong every number would be
worthless. It is the paper's single highest-risk assumption and it was checked
before any number was written up.

legislation.gov.uk states it directly: **"If the primary legislation on
legislation.gov.uk has any unapplied effects, we flag them in the 'Changes to
Legislation' banner on the website."** The reading holds.

The same page gave something better than confirmation.

## A publisher that states a service standard, and publishes no way to check it

legislation.gov.uk commits to a target: **"We aim to incorporate new amendments
into the text of the legislation within three months of those amendments coming
into force."**

Two consequences, and they pull in opposite directions. Both belong in the
paper.

**Against overclaiming.** A three-month target means the expected steady state
is *not* zero unapplied effects. "33 of 93 Acts are affected" is therefore not
by itself a failure — some backlog is the design. Any finding has to be about
the tail, not the existence, of the queue.

**The finding.** Compliance with that target cannot be computed from what the
service publishes. The target is measured from *coming into force*, and
commencement dates are not in this metadata — the Transport Act 1982 amending
the Road Traffic Act 1988 shows how far commencement can lag enactment. So the
publisher states a standard for the currency of its own text and does not
publish the one field that would let a user verify it against any particular
provision.

That is paper 5's argument arriving from the other direction. Paper 5 asked
publishers to ship the strength of the evidence with the text, on the grounds
that a user cannot otherwise tell which case they are in. Here the publisher
has gone further than almost anyone — it declares the defect, per provision,
in machine-readable form — and a user still cannot tell whether any given
flagged provision is inside the three-month window or years past it.

What can be reported is the distribution of affecting-instrument years among
unapplied effects, stated as what it is: the age of the amending instrument,
not the age of the breach.

Source: <https://www.legislation.gov.uk/understanding-legislation>

## Where the numbers stand (partial: 1988–1989)

The sweep is still running. These are the **two** years collected so far — 101
Acts — and they will change. They are recorded because the shape of the result
is already clear and because the measures below are the ones the publisher's
own service standard forces.

A first version of this section said "1988–1991". It was wrong, and the way it
was wrong is worth keeping: 1990 and 1991 were collected by the stale second
process, deleted with it, and then **skipped** by the surviving process, which
had already passed those years while their files still existed. The collector
skips a year whose file is present, which is the right behaviour for resuming
and the wrong behaviour when a file is removed behind it. Re-running the same
command after the sweep fills only the gaps, and that is queued below.

Two measures answer the "some backlog is the design" objection directly.

**The tail.** 60.2 per cent of unapplied effects come from an instrument ten or
more years old; 30.7 per cent from one twenty or more years old. This is the
age of the *amending instrument*, not of the breach — commencement can lag
enactment by decades, and the Transport Act 1982 proves it. But it is also the
only date the publisher gives a user, which is the point.

**Backlog or neglect.** Seventeen Acts were revised by the service **within the
last year** and still carry an effect from an instrument ten or more years old.
A record nobody has touched would have a stale last-modified date; these do
not. The Road Traffic Act 1988 was revised on 2026-06-29 — seven weeks before
the analysis date — and still displays text omitting **222 effects**, the
oldest from 1982. The Opticians Act 1989 was revised in January 2025 and
carries 100, the oldest from 2008.

That is an actively maintained record with a standing queue, not an abandoned
one, which is a sharper and more uncomfortable finding than a backlog would be.

## Two risks checked before the data was complete

**Are the effects listed on an Act actually about that Act?** If some were
about a different instrument, the per-Act attribution would be wrong and the
concentration figures with it. Checked directly: 4,313 effects, **zero** whose
`AffectedURI` points anywhere but the Act carrying them. Attribution is exact
and nothing is double-counted.

**Do wholly repealed Acts contaminate the result?** Barely, in the numerator —
4 of the affected Acts are repealed and they carry 5 effects out of 4,313. But
48 repealed Acts sit in the *denominator*, and a repealed Act has no live text
to be out of date, exactly as a `final` one has no revised text. Reporting only
the denominator that flatters the finding is the error this analysis exists to
avoid, so all three are reported:

| Denominator | Affected |
|---|---|
| all 368 retrieved | 32.9% |
| 360 maintained in revised form | 33.6% |
| 312 revised and not repealed | 37.5% |

The service records repeal in the Act's title rather than in a metadata field,
so that last row is title-derived and labelled as such in the output.

## The old queue is a handful of instruments, not diffuse neglect

Banding the ages for figure 1 hid the structure that matters. The per-year
distribution has three parts:

- a **recent working queue** — 424 effects from 2024, 469 from 2025, 865 from
  2026, which is what any three-month target produces under volume;
- a **trough** at 2017–2021 — 11, 10, 64, 49, 3 — showing the service does work
  through its queue;
- an **old tail that is spiky, not decaying** — 240 from 2002, 235 from 2006,
  269 from 2012, 287 from 2015.

Each spike turns out to be one instrument. 258 of the 2012 spike's 325 effects
come from a single amending Act; 205 of 2002's 290; 155 of 2006's 240. Across
the whole pre-2022 tail, **ten instruments hold 44.9 per cent** of 2,914
effects drawn from 226 distinct instruments.

So the old backlog is not a service falling behind across the board. It is a
small, identifiable set of amending instruments nobody has worked through — a
different problem, with a different and much cheaper remedy. It is also the
same shape paper 4 found in Saudi amendment activity, where the ten most active
decrees accounted for 35.4 per cent of article-amendment pairs.

**The instruments are recorded by identifier and deliberately not named.**
Their titles sit in `ukm:AffectingTitle`, a child element rather than an
attribute, which the collector's attribute-based parse never captured. Naming
them from memory instead is precisely the fault that reached paper 4's opening
paragraph before review caught it. The collector now captures the title, and
the names wait for data that carries them — obtainable from about twenty
targeted requests rather than a second full sweep.

## An independent recomputation, and the trap it fell into first

`analyse_uk.py` has accumulated denominators, guards and exclusions. Each was
added for a reason, and together they are enough machinery to be wrong in a way
that still looks plausible. `verify_uk.py` recounts the headline figures from
the raw year files by the most obvious route available and compares.

It shares no code with the analysis on purpose. Two implementations that import
the same helper agree by construction, which proves nothing.

Its first run reported a mismatch on **every** figure — 595 Acts against 525,
6,026 effects against 5,156. Nothing was wrong. The results file had been built
before the last two years landed, so a live recomputation was being compared
against a stale snapshot, and the uniform gap was exactly the 70 Acts collected
in between. The verifier now runs the analysis itself before comparing, and the
reason is written into its docstring so the next person does not spend the same
ten minutes.

With that fixed, all seven figures agree.

## No number is typed into this manuscript

Every figure in papers 1 to 5 was typed into the manuscript by hand and caught,
if at all, by review afterwards. Review found a wrong share in paper 3, a wrong
count and a wrong top-ten figure in paper 4, and a wrong article count in paper
5. Four defects of one kind — and each had survived several careful readings,
because a plausible number in prose looks exactly like a correct one.

This paper removes the class instead of checking for it.

`numbers.py` turns `uk_analysis_results.json` into LaTeX macros. The manuscript
writes `\nActsRetrieved`, never `590`, and the macros are regenerated before
every compile. A figure cannot go stale, cannot be mistyped, and cannot
disagree with the analysis, because only one copy of it exists.

`check_numbers.py` enforces it, since the mechanism is worthless if the
manuscript quietly types a digit anyway. It rejects anything shaped like a
measurement — a thousands-separated count, a decimal, a percentage — while
leaving years, section numbers and citations alone. Self-tested against a decoy
containing all four cases: it flags `1{,}402` and `35.1 per cent`, and passes
`art 60 in 1988` and a Zenodo DOI.

Its first run on the real manuscript produced a false positive —
`margin=2.5cm`, a package option — so the check now reads only the body. A
guard that flags layout settings trains its author to ignore it, which is worse
than having none.

The mechanism also produced a failure worth recording, because the error it
raises points nowhere near its cause. A LaTeX control sequence is letters only,
so `\nTailEffects10` parses as `\nTailEffects` followed by the characters
`10`, and the compiler reports *Missing \begin{document}* at a line in the
generated file. `numbers.py` now refuses to emit a macro name containing a
digit, which turns a baffling compile error into a plain sentence at the point
of generation.

## The two quotations, checked against the page rather than a summary

The article quotes the publisher twice, and both quotations reached this
project through a summarising fetch rather than the page itself. A paraphrase
presented as a quotation would be a serious defect in a paper whose argument is
that publishers should be held to what they say, so both were checked against
the raw HTML.

Both are verbatim. The check also turned up a sentence worth adding — *Clicking
on the banner reveals the outstanding changes* — and, more importantly, a
context problem the extract had hidden.

The quotations sit a few lines after a passage about legislation originating
from the EU. If the three-month commitment were scoped to EU-derived
amendments, this article's framing would overstate it badly. Parsing the page's
heading structure settles it: both sentences fall under **Our editorial
practice and timescales**, and *Legislation originating from the EU* is a
separate heading that comes afterwards. The commitment is general. The footnote
now cites the heading and says why.

## Reproduce

```
python3 docs/research/comparison_paper/collect_uk.py --years 2018-2020
python3 docs/research/comparison_paper/collect_uk.py --all
```

Read-only against `legislation.gov.uk`. Resumable: a year already collected is
skipped, so a long sweep can be stopped and restarted without refetching.

## First result — the 2023 pilot

57 Acts, one request each, `Crawl-delay` honoured.

**Consistency.** 11 of the 56 Acts retrieved (19.6 per cent) carry at least one
effect the service flags as enacted but not incorporated into the text it
displays, and those 11 carry **232 such effects between them**. The largest are
the Levelling-up and Regeneration Act 2023 (96), the Seafarers' Wages Act 2023
(69) and the Online Safety Act 2023 (24) — the last a statute cited
internationally, whose official text does not reflect 24 effects the same
service records against it.

**Availability — not attributable yet.** The sweep saw one retrieval failure in
57 and three responses over ten seconds (14.4 s, 47.0 s, 49.5 s) against a
median of 0.45 s. It is tempting to report that even a well-resourced service
has measurable friction. It has not been established:

- the failed Act returned 200 on three immediate re-attempts, in 0.89 s, 0.24 s
  and 0.12 s, so the failure was transient;
- a control of six requests through the same proxy to an unrelated stable host
  returned 200 every time, all under half a second — which neither convicts nor
  clears the proxy on six requests.

**The confound this exposes is larger than the pilot.** The Saudi figures were
collected from an ordinary network; these are collected from a datacentre
address behind an agent proxy. Comparing "20 per cent unreachable" with "1.8
per cent" across two networks and two periods is not a comparison. This is the
same error the collector's author refused to make an hour earlier, when three
regional portals returned 403 to this environment and that was recorded as an
artefact rather than a measurement.

Three ways out, to be settled before any availability figure is reported:

1. **Restrict the comparison to consistency**, the axis a network cannot
   contaminate: an unapplied effect is a property of the data, not of its
   delivery. Cleanest, and sufficient on its own for paper 5's central claim.
2. **Build a designed control** — measure the proxy's own failure rate over
   thousands of requests to stable hosts and subtract it.
3. **Re-collect from the same network as the Saudi corpus**, so the two
   environments match.

**What the pilot did settle.** The five-field schema captured the one failure in
its `discrepancy` field at collection time, with the HTTP status and the curl
error, and cost nothing to populate. That is the first practical evidence for
paper 5's cost claim, which until now was an argument.

## Status

- [x] Jurisdiction chosen, on evidence rather than convenience: reachability,
      API, and a measurable consistency gap all verified before committing.
- [x] Collector written, with the five-field schema applied prospectively.
- [x] Pilot sweep (2023) — see above.
- [x] **The environment confound is settled by narrowing the claim, not by
      controlling for it: the comparison is restricted to consistency.** The
      pilot recorded one timeout in 57 and three responses over ten seconds
      against a 0.45-second median. Tempting to report as friction on a
      gold-standard service; it is not reportable. Re-attempting the failed Act
      returned 200 three times in under a second, so the failure was transient,
      and this collector runs from a datacentre address behind a proxy while the
      Saudi collection ran from the author's own network, at a different time,
      against portals that have since changed. A proxy control fixes the network
      half of that and leaves the time half untouched — and the Saudi
      measurement cannot be re-run, which is the very point paper 5 makes about
      contemporaneous evidence. Paying for a number that stays incomparable is
      the wrong trade.

      Consistency has none of that problem. An unincorporated amendment is a
      property of the data *as published*: any reader, on any network, at any
      time, gets the same count. In an article whose argument is about
      verifiability, that is not the lesser measure.
- [x] Availability data is still collected and will still be published — the
      field costs nothing extra — but labelled observer-relative and used only
      within a jurisdiction, never set against the Saudi figure. Publishing data
      at its true strength is not the same as discarding it.
- [x] **The schema needs `discrepancy` to record who declared it.** Applied to
      a well-run API, four of the five fields are constant — one value each for
      `source_class`, `retrieval_route`, `corroboration` and `transformation`
      across every record. That is the schema behaving correctly, not failing:
      it costs nothing here precisely because there is nothing to say.

      But the defect this study is about was invisible to all five. An Act
      whose text omits 222 enacted amendments was retrieved perfectly —
      official-primary, live, no transformation, nothing to report — so under
      the schema as written it is indistinguishable from an Act with no
      unapplied effects at all.

      The schema does not have to be extended to fix that. Its purpose line for
      `discrepancy` is "is there a known problem with this record?", and a
      publisher flagging its own text as not current is exactly that. What
      paper 5's field *values* leave out is that a discrepancy can be
      **declared by the source** as well as **found by the collector**, and a
      null means something different in each case: found-by-collector cost two
      sources and a comparison, so a null may only mean nobody looked hard
      enough; declared-by-source costs nothing to record, so a null means the
      publisher did not say. One null field standing for both is the same
      collapse paper 5 objects to when a single confidence score stands for
      availability and consistency at once.

      Over the collection so far, 82 records carry a source-declared
      discrepancy and none a collector-found one. In the Saudi corpus it was
      the reverse: four self-contradicting instruments, every one of them found
      by hand. Same defect class, opposite provenance — which is the argument
      for the sub-field and, incidentally, for asking publishers to declare
      rather than asking consumers to discover.
- [x] **The deeper refinement, which corrects my own first statement of it.**
      An earlier note here said `retrieval_route` is observer-relative while
      `corroboration` and `discrepancy` are not. That was wrong, and wrong in a
      way that pointed at something better. A discrepancy the *collector* finds
      is observer-relative in exactly the way a retrieval route is — it depends
      on which sources that collector consulted. Only a *source-declared* one
      is reproducible.

      So the division is not between fields. It is between what a value
      describes:

      | Field | Describes |
      |---|---|
      | `source_class` | the **record** — whose copy this is |
      | `retrieval_route` | the **encounter** — whether the live source answered *us* |
      | `corroboration` | the **encounter** — how many sources *we* found agreeing |
      | `transformation` | the **encounter** — what *we* had to do to the bytes we got |
      | `discrepancy` | either, depending on `declared_by` |

      Four of the five describe the encounter. **That is why the availability
      half of this comparison had to be abandoned** — not a network accident a
      control could have fixed, but the structure of the schema. Encounters do
      not compare across collections, because the two encounters differ before
      the two records do.

      The practical consequence goes back to paper 5's own proposal. That paper
      asks *publishers* to populate these fields. If a publisher does, the
      encounter fields describe the publisher's encounter with its own source —
      a different thing again, and not comparable with a consumer's. A
      provenance schema intended for cross-collection use has to mark which of
      its fields are encounter-relative. Paper 5's does not, and this
      jurisdiction is what made that visible. Using it
      prospectively showed something paper 5 did not distinguish.
      `retrieval_route` is **observer-relative** — its value depends on who
      collected, from where, and when, so it does not compare across
      collections. `corroboration` and `discrepancy` are not: they are
      properties of the record itself, and any reader reproduces them. Paper 5
      treats the five alike. They are not, and the difference was found by using
      the schema rather than by thinking about it. This belongs in paper 6 as a
      correction to paper 5, which is what a second jurisdiction should produce:
      not "the number repeated" but "the instrument learned something about
      itself".
- [x] **Second pass added for failed retrievals, once the comparison narrowed.**
      The collector deliberately does not retry: a non-200 is evidence about
      availability, and retrying it away erases the measurement. That was right
      while availability was in the comparison. It is not right now — a failed
      retrieval no longer buys a measurement, it only costs an Act's worth of
      coverage in the consistency count. `--retry-failures` makes one further
      attempt and **keeps both**: the first stays untouched, the second is
      recorded beside it, and the discrepancy note becomes
      `retrieval-failed-then-recovered` rather than being deleted. A reader can
      see that the document arrived on a second try.

      Both failures so far behaved identically: a 60-second timeout on a
      document of a few kilobytes, which then returned in under a second.
      `ukpga/1988/2` is 6.5 KB and answered in 0.60s and 0.38s on re-attempt.
      That is a connection that never opened — this collector's network, not
      the service — and it is the second piece of evidence for narrowing the
      comparison.
- [x] **A connect timeout that turned out to do nothing — kept, because
      measuring that is the point.**
      Two of the first twelve requests of the sweep died the same way as the
      pilot's one: sixty seconds, no bytes. Every success in the collection
      answers in under two seconds. There is no middle — a request either
      returns at once or its connection never opens — so `--connect-timeout 10`
      loses no real response and stops the sweep spending a minute on each dead
      socket. At the observed rate that alone would have added hours of waiting
      to a run already pinned to a five-second crawl delay.

      **That reasoning was wrong, and the field added to support it is what
      disproved it.** `time_connect` is ~0.0002 s on successes and failures
      alike, because outbound traffic goes through a local proxy that accepts
      instantly; the connect phase never reaches the origin. No connect timeout
      can bound a stall beyond it. The flag has no effect, the apparent
      improvement after adding it was the transient clearing on its own, and
      four requests have since died the same way at exactly 60.02 s.

      Two claims made earlier here are withdrawn. `time_connect` does **not**
      separate *could not reach the host* from *host was slow to answer* — down
      a proxy it separates nothing, being constant — so it was never a third
      piece of evidence that the failures are this collector's network. That
      conclusion still holds on the evidence that remains (re-attempts succeed
      in under a second, every time), but on two legs rather than three.

      `--max-time` is the lever that would actually bound the waste, and every
      success in this collection answers in under two seconds. Lowering it is
      queued for the next full run rather than done mid-sweep: four wasted
      minutes across nine years of Acts is not worth a fifth restart, and the
      retry pass recovers the coverage.
- [ ] Full sweep of the statute book (1988–2026 running; extend earlier if the
      backlog reaches further back than the modern era).
- [ ] **Name the ten instruments behind the old queue**, from
      `ukm:AffectingTitle`, by re-fetching only the Acts that carry those
      effects — about twenty requests, not another sweep. Until then the
      finding is stated by identifier.
- [x] **The 1988 start date was tested, and the assumption behind it was
      wrong.** The range was chosen on the belief that unapplied effects
      accumulate in modern legislation and earlier years would return zeros. A
      sample of twenty Acts from 1968, 1975, 1980 and 1985 found **five**
      carrying unapplied effects and **218** effects in total. The **Highways
      Act 1980** alone carries **132** — a heavily used statute whose displayed
      text omits that many enacted amendments.

      So the sweep does exclude real data, and every total reported here is a
      **lower bound on the statute book** rather than a census of it. That is
      now stated in the manuscript's limits rather than left as an unexamined
      range. Extending the sweep is time, not method: at the declared crawl
      delay the pre-1988 book is many hours.

      Two caveats on the probe itself. It is a convenience sample of the
      highest-numbered Acts in four years, not a random one. And the 1925 and
      1948 feeds returned no Acts in the expected form, so nothing is claimed
      about those years either way.
- [ ] Sweep the pre-1988 book if the paper's claim needs a census rather than
      a floor. Not obviously required: a floor is enough for the argument, and
      saying so is more honest than a total that quietly stops at 1988. The range was
      chosen on the assumption that unapplied effects accumulate in modern
      legislation and that earlier years would return zeros. The data now
      undercuts that assumption: effects sitting on 1988 Acts come from
      instruments as old as 1982, so age of Act and age of effect are not the
      same axis. A sample of pre-1988 Acts settles whether the range excludes
      real data — and it is queued rather than run now, because issuing extra
      requests alongside the running sweep is exactly the rate-doubling
      recorded above as a fault.
- [ ] **Re-run the same command after the sweep to fill 1990 and 1991**, which
      were skipped after their files were deleted behind the running collector.
      Because a year is skipped only when its file exists, the same invocation
      collects exactly the missing years and nothing else.
- [ ] Analysis: what share of Acts, and of provisions, does the service itself
      flag as not reflecting the law in force? How old are the oldest unapplied
      effects?
- [ ] Decide the unit of comparison. Saudi figures are per *article* and per
      *instrument*; the UK equivalent is per *provision* and per *Act*, and the
      two are not the same object. This has to be settled before any number is
      reported side by side, not after.
- [ ] Venue. Not chosen, and not to be chosen before the result is known.

## Files

| File | Purpose |
|---|---|
| `collect_uk.py` | Collects the Acts and populates paper 5's five-field schema at collection time. |
| `analyse_uk.py` | Produces every number, from the collection only. |
| `verify_uk.py` | Recomputes the headline figures by a separate route and compares. |
| `numbers.py` | Turns the results into LaTeX macros; the manuscript holds no digits. |
| `check_numbers.py` | Refuses a manuscript that types a number the analysis owns. |
| `numbers.tex` | Generated macros. Never edited. |
| `main.tex` / `main.pdf` | The manuscript. Holds no digits; carries an `\anonfalse` switch. |
| `uk_analysis_results.json` | Generated results snapshot. |
| `make_figures.py` | Figures 1 and 2, as PNG, TIFF and EPS. |
| `fig1_age_bands.*` / `fig2_maintained_and_stale.*` | The two figures. |
| `uk_collection/` | One JSON per year; regenerated by the collector, not committed. |
