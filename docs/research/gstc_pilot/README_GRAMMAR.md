# The citation layer

Four pieces, each with one job, none specific to a publisher.

    docs/research/canon/canonical.py       character-level repairs, gated on evidence
    docs/research/citation/numerals.py     Arabic ordinals as drafting writes them
    docs/research/citation/instruments.py  one key per instrument
    docs/research/citation/grammar.py      the staged parse

## Why stages

A single regex reported 90.9 per cent on ministry judgments and 0.0 per cent
on the tax committees' digests, and nothing in it could say which of the two
corpora it had learned. The stages are separate because the failures are:

    DETECTION            an article expression is present at all
    ARTICLE EXPRESSION   its number, however written
    PARAGRAPH            its paragraph -- prefixed, postfixed or packed
    INSTRUMENT           the instrument named in the same attachment
    ANAPHORA             the instrument named elsewhere and resumed
    ATTRIBUTION          whose citation this is

Each reports its own verdict and each can be switched off, so `ablate.py` can
apportion a gap instead of asserting a cause for it.

## Detection has no stop-word list

An article citation is the word «مادة» followed by a number. The ordinary noun
-- «مادة الفحم الحجري», the coal; «المادة المصدرة», the exported material --
is not followed by one, and that is the whole test. Two of 120 sampled
occurrences in the digests are the ordinary noun, and both sit in reasoning
text, where a citation would be expected.

## Refusal is a result

Three places where the grammar returns nothing, deliberately:

- **A name that cannot be completed.** PDF wrapping breaks instrument names
  across lines. The grammar rejoins one only when the rejoined text *equals* a
  name the corpus states cleanly. Where the line after the break belongs to a
  different part of the page -- linearisation, not drafting -- nothing matches
  and the answer is nothing.
- **A proximal anaphor with the wrong antecedent.** «الالئحة ذاتها» means the
  one just named. Where the one just named is not a لائحة, the reference is
  broken; reaching past it to the next candidate is a guess with a citation
  attached.
- **An article with no instrument anywhere.** One sampled citation gives
  «المادة الحادية عشر» and never says of what.

Both gold sets label these as unresolvable, so a parser that answers there
scores as wrong. That asymmetry is the point: a confidently wrong instrument
is worse for every downstream claim than an honest gap.

## Where the grammar admits it is guessing

Ministry judgments pack article and paragraph into one expression, and **not
in a fixed order**: «93/1» is article 93 paragraph 1, «2/76» is article 76
paragraph 2. Where one side is a letter there is nothing to decide. Where both
are digits, the only regularity holding across every attested case is that the
article is the larger number. That is a heuristic, so the record carries
`packedAmbiguous: true` and any count depending on the article number can drop
those rows.

## The instrument gazetteer

Instrument names arrive broken by line wrapping and extended by clauses that no
punctuation separates. Both are answered by asking the corpus what names it
states cleanly, and taking the **shortest** such name that begins what was
read.

Shortest, not longest, and only names attested more than once. A name that has
run into the next clause is itself attested, so a longest-match rule lets one
over-run certify the next; and a name attested exactly once may be an artefact
of a single broken line -- «نظام المر افعات», where justification put a space
inside the word -- which the shortest-match rule would otherwise prefer over
the real name.

The gazetteer holds names only, is built only from hard-terminated mentions,
and is scoped to the corpus being processed. No content crosses between
documents.

## Attribution is two answers, not one

`enclosingSection` is structural: the last heading before this point.
`segment` is what the citation is. They differ, and the difference is a
finding, not a defect. A decision narrates a party's argument inside its own
account of the facts and gives it no heading; verbs of saying recover most of
those, and the residue is a limit of what a heading-and-cue reading can do.

Both matter more than they look. In the committees' digests only 22.9 per cent
of what a detector finds is the tribunal's own citation; the rest is a party's,
a reporter's list of authorities, or the boilerplate closing every decision. In
ministry judgments it is 80.9 per cent. Counting citations across the two
without segmenting compares a court's reasoning with a reporter's bibliography.

## Running it

    python3 matrix.py                       # both sources, every stage
    python3 evaluate.py --set moj --errors  # what is still wrong, and how
    python3 ablate.py                       # what each rule and stage contributes
    python3 dev_profile.py                  # what the labels say must be handled
