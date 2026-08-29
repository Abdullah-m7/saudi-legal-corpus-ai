# Submission kit — *Arab Law Quarterly* (Brill)

Read from the journal's own Instructions for Authors, revised 24 June 2025.

| | |
|---|---|
| Journal | *Arab Law Quarterly* (ALQ), Brill |
| Scope | «the leading English language scholarly publication on all matters relating to the law and legal systems of the 22 states in the Arab League». Its listed subject areas include, ninth of ten, **«Studies of legislatures and legislative process within the Arab world»** |
| Review | **Double blind.** A separate title page carries the names and contact details «and will not be accessible to the referees» |
| Fees | **None.** Subscription journal; no submission fee and no article processing charge |
| Length | **7,500–20,000 words.** Ours: 8,002 including footnotes |
| Abstract | **≤ 150 words, one paragraph.** Ours: 139 |
| Keywords | 3–8. Ours: 6 |
| Headings | Numbered, three levels, title case, flush left |
| Citations | **Footnotes, in the journal's own style**, ending with a full stop; `ibid.` and `supra note x`; DOIs where available |
| Files | Word source files, not PDF only. Figures separate, ≥300 dpi |
| Submit | Editorial Manager — `editorialmanager.com/alq` |

The journal states that it «encourage[s] submissions from those who are
underrepresented, including without limitation women and those working in the
global south generally, and the Arab world in particular».

## Submitted

**Submitted to *Arab Law Quarterly* on 29 August 2026, as an Article.
Submission reference `ALQS2600172`.** The editorial office has acknowledged
receipt; a manuscript number follows once the submission clears its checks
and is assigned to an editor.

Four files went up: the anonymised manuscript, the title page, and the two
figures as separate EPS. The proof the publisher built was read page by page
before approval, and the first build was rejected and rebuilt -- see below.

## The defect the proof caught

Two footnotes said «see the data availability statement below». That
statement is gated on `\ifanon`, correctly, because it carries the repository
address that names the author -- so in the anonymised manuscript there was
nothing below, twice, in a paper whose argument rests on its data being
inspectable.

No guard here could have caught it: the anonymity audit checks what appears,
and nothing compares a cross-reference against the build that resolves it.
The publisher's own proof caught it. Both footnotes are now gated too, and the
anonymised text says where the statement is and why it is not printed.

## Why here, before the law reviews

Two desk rejections this month came from offering Saudi law to readers with no
stake in it: the *Journal of Legal Analysis* on scope, and *Statute Law
Review* with a suggestion to try a company-law journal. ALQ's readers are
defined by that stake.

It also removes the cost the law-review route charges. US law reviews are not
anonymous and an unaffiliated author is read at a disadvantage; ALQ is double
blind, so the referee sees the work and not the author line. And there is no
fee, no waiver to wait for, and no basket of twelve.

**What it costs:** one chance rather than a dozen, months rather than weeks,
and exclusivity — this manuscript may be at ALQ *or* at law reviews, never
both.

## What changed for ALQ

**Footnotes.** Twenty-six converted from Bluebook to the journal's house form:
initials before surnames, single quotation marks for article and chapter
titles, italics for books and periodicals, `(Place: Publisher, year)`, and
`supra note x` in place of a bare `supra`. Bluebook's small capitals are gone,
which the journal's «use italics sparingly … do not use all capital letters»
rules out anyway.

**Two DOIs added**, verified against Crossref rather than recalled: Katz and
Bommarito is *Artificial Intelligence and Law* 22(4) (2014): 337–374,
`10.1007/s10506-014-9160-8`; Coupette and others is *Frontiers in Physics* 9
(2021), art. 658463, `10.3389/fphy.2021.658463`.

**Place and publisher given only where verified.** Dickerson (Boston: Little,
Brown) and Scalia and Garner (St. Paul, MN: Thomson/West) were confirmed
against a bibliographic record; Xanthaki's *Thornton's* and *Bennion* carry
their publisher without a place, and Xanthaki's 2014 monograph carries
neither, because those were not confirmed. The journal asks for information
«as complete as possible», not for a guess.

**The abstract was cut from 207 words to 139**, against a 150-word cap.

**Document properties are now scrubbed and audited.** ALQ requires that «the
names of these files and the document properties should also be anonymised».
`build.py` blanks every `docProps` field that can name a person, and the
anonymity audit now reads **every part of the .docx archive as bytes** rather
than the rendered text — the projection that let a repository URL hide in a
footnote part of paper 9.

## What to upload

| File | |
|---|---|
| `submission_manuscript.docx` | **Anonymised.** 8,002 words including footnotes. |
| `submission_title_page.docx` | Title, author, contact, abstract, keywords, declarations. Referees never see it. |
| `fig1_funnel.eps`, `fig2_adjudication.eps` | Separate files, as the journal requires. |

## If ALQ declines: US law reviews

The Bluebook build is **commit `09340f9`** in git history, complete and
checked. The two citation systems cannot coexist in one source, and the
article cannot be at a peer-reviewed journal and at law reviews at the same
time — so the Bluebook version waits there rather than in the working tree.

## The simultaneous-submission rule, which changes everything

US law reviews **expect** an article to be under consideration at many
journals at once. That is the norm, not a breach: authors submit through
Scholastica to dozens, and use an offer from one to expedite the others.

So one Bluebook conversion buys many chances rather than one — which is the
whole reason for choosing this route over *The Loophole*, where a single
submission is a single chance.

**It also forbids what the peer-reviewed route requires.** This article may be
under simultaneous consideration at law reviews, *or* at one peer-reviewed
journal, and never both. The cover letter says which regime it is in.

## What this route costs, stated plainly

**Law reviews are not anonymous, and student editors read the author line.**
An independent researcher with no institutional affiliation is at a structural
disadvantage there that a double-anonymous journal removes. That cost is real
and it is being paid deliberately, for the academic line the professional
journals cannot give.

**And two desk rejections this month came from offering work to readers with
no stake in it.** JLEG's stated scope is legislation and its reform, which is
what this article is about — but it is a US journal, and the jurisdiction is
not. The article's general framing, done for exactly this reason, is what has
to carry it.

## What changed for Bluebook

Twenty-six footnotes converted from OSCOLA. Saudi and Commonwealth statutes
take Rule 20's foreign form — *Competition Law, Royal Decree No. M/75
(29/6/1440H), art. 1 (Saudi Arabia)* — books and periodical names are set in
large and small capitals, article titles in italics, `and others` becomes
`et al.`, and `2nd edn` becomes `2d ed.`

Three foreign statutes were verified rather than recalled: the Interpretation
Act 1978 is c. 30; the Acts Interpretation Act 1901 (Cth) is No. 2 of 1901;
the Canadian Interpretation Act is R.S.C. 1985, c. I-21.

## If the law reviews decline

*The Loophole*, the journal of the Commonwealth Association of Legislative
Counsel: no fee, non-members welcome, 8,000 words including footnotes, a
200-word abstract, and email to the Editor in Chief. It has no impact factor
and is **not in DOAJ** — a professional journal, not an indexed academic one —
but its readers are the practising drafters this article's conclusion
addresses, and it has no submission window to miss.

Not the *European Journal of Law Reform*: Constantin Stefanou, who signed the
Statute Law Review rejection, was its managing editor from 2012 to 2022 and
remains on its advisory board.
