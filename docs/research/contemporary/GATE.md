# The validation gate, and what it cost

Three gold samples, each with a job. This is the third and last.

| sample | seed | role | outcome |
|---|---|---|---|
| 1 | 23 | development | found six defects; **burned** by driving their repair |
| 2 | 47 | type validation | 126/126 correct at the type level |
| 3 | 71 | **final gate** | 1 of 3 arms failed; the headline claim was re-specified, and three of its nine contrasts withdrawn |

The design of sample 3 — arms, sizes and **pass criteria** — was written into
`gate.py` and committed before a single label was read. That matters, because
one arm failed and a design written afterwards would have been written to
pass.

## What the gate was for

Sample 2 validated the *type* of each mention. The headline result is about
the *voice*: that a litigant argues from the contract and the bench does not.
Voice had never been checked by hand. If it were wrong, the result would be an
artefact of the classifier rather than a fact about the corpus.

## Results against the pre-declared criteria

**Arm 1 — the three recall fixes made after sample 2 was read.** Threshold:
≥ 7 of 9 each.

| rule | correct | verdict |
|---|---|---|
| `fiqh.book` («مجموع فتاوى» without the article) | 9/9 | pass |
| `fiqh.unattributed` (bare «متقرر فقهاً») | 9/9 | pass |
| `statute.possessive` («في لائحتها الأولى») | 8/9 | pass |

The single failure is worth recording: «العقد المبرم بين الطرفين **- المرفق
في النظام -** والمتضمن في مادته: (الخامسة)». «النظام» there is the court's
*electronic filing system*, not a statute, and the referent test read it as
one. The rule fires 300 times in the view, so this costs on the order of
thirty misassignments and moves nothing.

**Arm 2 — voice. FAILED.** Threshold: ≥ 85 % overall and ≥ 80 % within each
of the two contrasted buckets.

| assigned voice | correct | |
|---|---|---|
| court_reasoning | **12/12 = 100 %** | passes its own threshold |
| party_argument | **10/12 = 83 %** | passes its own threshold |
| recital | 7/12 = 58 % | |
| operative | 8/12 = 67 % | |
| **overall** | **37/48 = 77.1 %** | **below 85 %** |

The two buckets the claim contrasts both pass. The failure is entirely in the
other two, and it is not random:

- **recital** — five of twelve were party pleadings with no cue near the
  mention: a claim form's numbered grounds, a party's own «الأسانيد الشرعية»
  list, one party answering another. Four of those five were statute or
  maxim.
- **operative** — four of twelve were reasoning content that the segmenter
  placed after «حكمت الدائرة», mostly in records carrying two concatenated
  judgments.

**Arm 3 — the five contrasted type/voice cells. PASSED, 80/80.** Every cell
was clean and every contrast kept its direction. One nuance was recorded
rather than scored away: several of the court's contract mentions are the
bench *reading or narrating the parties' contract* inside its own reasons,
which inflates an already tiny court share rather than deflating it.

## What was done about the failure

Not a patch. The frozen rule said the result would be "withdrawn, not
patched" if arm 2 failed, and the diagnosis says precisely what went wrong:
the cue-based party column is an **under-count** of party speech, and the
missed speech leans statute and maxim — exactly the direction that could
manufacture a divergence.

So the contrast was recomputed under **two** specifications, strict and wide
(`claim.py`), and only what survives both is claimed. That is not a rescue: it
replaces a cue-based attribution with a bracket around it, and it cost the
claim three of its nine contrasts.

| contrast | first version | after the gate |
|---|---|---|
| contract, maxim, custom, named fiqh, discretion, judicial principle | claimed | **survive both** |
| statute (1.3× court) | claimed | **withdrawn** — 0.98× under the wide spec |
| Qur'an (1.5× party) | claimed | **withdrawn** — 0.91× |
| hadith (1.4× party) | claimed | **withdrawn** — 0.94× |

The three withdrawn contrasts became the negative controls the result had
been missing.

## The stop condition, and that it is now met

Arm 2 failed on its letter, and the failure did not touch a central result:
it re-specified one and removed three over-claims. Under the standing rule —
return to parser work only if validation destroys a central result, or a known
defect changes a claim materially — **parser work stops here.** No fourth
sample. The known extractor gaps in `citation_forms.py` remain unrepaired and
`coverage_sensitivity.py` bounds them at half a point of composition.
