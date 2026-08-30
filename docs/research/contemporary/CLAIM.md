# Research claim: speaker identity structures legal authority

Not a manuscript. A claim package: the question, the result, the effect sizes,
what would have falsified it, and what did.

## QUESTION

**Why does speaker identity matter for empirical legal measurement?**

Empirical legal work counts citations in judgments. Almost all of it counts
them over the whole document. A judgment, however, is not one voice: it
contains the parties' pleadings as well as the court's reasons, and the
publisher concatenates them into a single text. If the two sides invoke
systematically *different kinds* of legal authority, then a whole-document
count is not a noisy measure of judicial reasoning — it is a measure of
something else, and the error does not shrink with sample size.

This asks whether that is so, in a corpus where the segmentation can be done
and hand-validated.

## PRIMARY RESULT

Computed only from the validated pipeline, contemporary_3y (1444–1446,
28,090 judgments), quoted passages excluded, under both voice specifications
(`claim.py`; the gate that forced two specifications is in `GATE.md`).

| authority | bench's reasons | party STRICT | party WIDE | survives both |
|---|---:|---:|---:|---|
| contract | 0.86 % | 14.83 % | 10.03 % | **yes, 11.7–17.2×** |
| legal maxim | 1.08 % | 4.64 % | 3.10 % | **yes, 2.9–4.3×** |
| custom | 0.94 % | 3.79 % | 2.69 % | **yes, 2.9–4.0×** |
| fiqh, named source | 14.78 % | 8.10 % | 6.09 % | **yes, 0.41–0.55×** |
| discretion named | 1.72 % | 0.55 % | 0.36 % | **yes, 0.21–0.32×** |
| judicial principle | 1.54 % | 1.00 % | 0.78 % | **yes, 0.51–0.65×** |
| statute | 70.60 % | 55.11 % | 69.03 % | no |
| Qur'an | 2.46 % | 3.69 % | 2.25 % | no |
| hadith | 6.01 % | 8.29 % | 5.67 % | no |

n = 62,256 court mentions; 10,283 party strict; 30,486 party wide.

**Six of nine authority types are used at systematically different rates by
the bench and by the litigants inside the same judgments; three are not.**

## EFFECT SIZES

Ratios are party share ÷ court share; the interval spans the two
specifications, which bracket the true party population.

```
contract              11.7×  to  17.2×      party
legal maxim            2.9×  to   4.3×      party
custom                 2.9×  to   4.0×      party
judicial principle     1.5×  to   2.0×      court   (0.51-0.65 inverted)
fiqh, named source     1.8×  to   2.4×      court   (0.41-0.55 inverted)
discretion             3.1×  to   4.8×      court   (0.21-0.32 inverted)
─────────────────────────────────────────
statute                0.98× to   1.28×     no stable direction
Qur'an                 0.91× to   1.50×     no stable direction
hadith                 0.94× to   1.38×     no stable direction
```

The contract is the largest effect in the corpus and the one least sensitive
to specification.

## ROBUSTNESS

**Across views** — the ratio of party to court share, strict specification:

| authority | c5y | c3y | post_Evidence | post_CTL |
|---|---:|---:|---:|---:|
| contract | 16.76 / 11.29 | 17.24 / 11.66 | 16.73 / 11.25 | 17.79 / 12.47 |
| legal_maxim | 4.04 / 2.68 | 4.3 / 2.87 | 4.04 / 2.68 | 5.31 / 3.54 |
| custom | 3.89 / 2.72 | 4.03 / 2.86 | 3.89 / 2.74 | 4.06 / 2.87 |
| fiqh_source | 0.55 / 0.41 | 0.55 / 0.41 | 0.55 / 0.41 | 0.52 / 0.44 |
| discretion | 0.29 / 0.19 | 0.32 / 0.21 | 0.3 / 0.19 | 0.11 / 0.14 |
| judicial_principle | 0.65 / 0.48 | 0.65 / 0.51 | 0.65 / 0.48 | 0.64 / 0.54 |
| statute | 0.78 / 0.98 | 0.78 / 0.98 | 0.78 / 0.98 | 0.8 / 0.96 |
| quran | 1.51 / 0.91 | 1.5 / 0.91 | 1.52 / 0.92 | 1.83 / 1.19 |
| hadith | 1.42 / 0.95 | 1.38 / 0.94 | 1.42 / 0.96 | 1.41 / 0.95 |

Each cell is *strict / wide*. A ratio above 1 leans party, below 1 leans
court. **The six survivors keep their sign in all four views under both
specifications, and their rank order is unchanged. The three failures fail in
all four.** Nothing in this result depends on which window is chosen.

**Across specifications** — the whole point of the two columns above. Six
survive, three do not, and the three that do not are reported as failures
rather than dropped.

**Conditioning on the statutory role** (PHASE C, and the sharpest test):
restrict to non-statutory mentions only, so that no mention can be procedural
by instrument and the "the court just cites procedure more" explanation
cannot operate.

| authority | court | party | ratio |
|---|---:|---:|---:|
| contract | 2.93 % | 33.04 % | **11.3×** |
| legal maxim | 3.67 % | 10.33 % | **2.8×** |
| custom | 3.21 % | 8.45 % | **2.6×** |
| fiqh, named | 50.26 % | 18.05 % | **0.36×** |
| discretion | 5.84 % | 1.23 % | **0.21×** |
| judicial principle | 5.25 % | 2.23 % | 0.42× |
| Qur'an | 8.38 % | 8.21 % | 0.98 |
| hadith | 20.46 % | 18.46 % | 0.90 |

court n = 18,303, party n = 4,616. **Every surviving contrast survives the
conditioning, at the same magnitude; the two null results stay null.** The
divergence is not an artefact of the bench citing procedure.

A second, related fact from the same stratification: within *statutory*
citations alone, 92.4 per cent of the bench's are to procedural instruments
against 74.7 per cent of the parties'. Parties reach for substantive statute
three times as often, proportionally. That is the same phenomenon in the one
type that showed no overall difference.

## NEGATIVE CONTROLS

Yes, and they were not chosen in advance — they were three claims that failed.

- **Qur'an**: 0.91–1.50×. No stable direction.
- **hadith**: 0.94–1.38×. No stable direction.
- **statute**: 0.98–1.28×. No stable direction once the whole pleadings
  segment is counted.

Scripture and statute are **shared vocabulary**: both sides reach for them at
indistinguishable rates. This is what makes the six survivors informative
rather than an artefact of a classifier that separates any two populations.

## LIMITATIONS

1. **Commercial-heavy corpus.** 95 per cent of the 50,666 judgments are from
   commercial courts; 28 are personal status. Nothing here is a claim about
   Saudi adjudication generally.
2. **Published judgments.** Selection into publication is not random and, in
   this corpus, the share carrying reasons moved from 2 to 88 per cent across
   the span. Every figure here is conditioned on that.
3. **Speaker attribution is bracketed, not solved.** The gate measured the
   court bucket at 12/12 and the strict party bucket at 10/12, and the recital
   at 7/12. That is why two specifications are reported. There is no third
   arbiter.
4. **Invocations, not reasons.** A court may decide from the contract and
   write the statute, or the reverse. Nothing here separates those.
5. **Six known extractor blind spots** remain (`citation_forms.py`), bounded
   at half a point of composition by `coverage_sensitivity.py`.

## FALSIFICATION — what would have made us withdraw

Written before the gate, and one of them fired:

- **If the court bucket had been mis-attributed** — the gate would have shown
  reasoning mentions assigned to parties. It showed 12/12 correct.
- **If the contrasted cells had been dirty** — arm 3 would have found types
  misassigned inside the contrast. It found 80/80 clean.
- **If the contrast had vanished under the wide specification** — it does, for
  statute, Qur'an and hadith. **Those three were withdrawn.** The remaining six
  did not vanish.
- **If conditioning on statutory role had removed it** — PHASE C. It did not;
  the contrast widened.
- What would still falsify it: a hand-read sample of *whole recitals* showing
  that the contract-heavy passages are the court's narration rather than the
  parties' words. The gate's arm 3 is evidence against that, on 8 items, and
  8 items is not many.

## WHAT THIS IS NOT

Not causal. Not a claim that courts ignore contracts — a court that decides a
contract case necessarily construes the contract; the finding is about which
authorities it *cites* when it writes its reasons. Not a claim about all
Saudi courts, and not a claim about all legal systems: it is one jurisdiction
where the measurement can be validated, offered as a reason to check the same
thing elsewhere.

## WITHIN-JUDGMENT TRANSITIONS (PHASE D)

The strongest test of all, because it holds the dispute constant: in the
4,313 judgments where both a party mention and a court mention are
identified, what does the bench reach for given what the party raised?

**There is no translation.** The column that would show it — the rate at
which the bench answers with statute — is flat:

```
party raises          n      expected   lift
statute            2,844      2,806     1.01
contract             675        703     0.96
fiqh                 366        387     0.95
maxim                270        284     0.95
Qur'an               257        262     0.98
hadith               496        499     0.99
custom               247        253     0.98
```

Whatever is argued, the bench applies statute at the same rate. What *is*
above expectation is the diagonal:

```
custom  -> custom     3.92×      fiqh   -> fiqh    1.59×
contract-> contract   3.65×      Qur'an -> Qur'an  1.64×
principle->principle  2.08×      maxim  -> maxim   1.63×
```

So the shape is not reframing. **The statutory floor is invariant — the same
procedural articles regardless of what was argued — while the non-statutory
layer is responsive: the bench answers a contract point with the contract and
a custom point with custom, three to four times more often than chance.**

That is a better result than the one looked for, and it should not be called
"legal-authority translation", because it is the opposite: the court engages
the litigant's chosen non-statutory ground rather than converting it.
