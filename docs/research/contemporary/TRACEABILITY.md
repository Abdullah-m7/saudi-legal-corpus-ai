# How much of what a court cites can be looked up?

Two questions that turn out to be one, and both matter more for what can be
built on this corpus than for anything about Saudi law itself.

## 1 · Three retrieval universes

For a legal assistant grounded on Saudi materials, three candidate corpora.
The measure is set membership, not model performance: does the authority the
court actually used exist in that universe at all?

**A — the statute book.** It covers **all** of the court's authority in 61.1
per cent of judgments, **part** of it in 31.6 per cent, and **none** of it in
7.2. Across all 70,231 authority mentions in the bench's voice, 70.6 per cent
are statutory.

**B — whole published judgments.** Everything the court used is somewhere in
the document, so recall is complete by construction. What it costs is
precision: **only 68.8 per cent of the authority inside a judgment is the
court's own.** Roughly three authority mentions in ten belong to the recital
or to a party's argument. A retriever grounded on whole judgments is a
retriever that treats what a losing advocate cited as law.

**C — the court-reasoning layer.** Complete and clean, because the voice is
attributed. That is not a neutral comparison — the layer is derived from the
judgments — but it is what the derivation buys: the 31 per cent that B mixes
in is exactly what the speaker paper measured, and here it has a price tag.

## 2 · Traceability of the authority itself

Underneath retrieval is a harder limit. An «المقرر فقهاً وقضاءً» names no
jurist, no book and no page. It cannot be retrieved from any corpus, however
complete, because the judgment does not say what to retrieve.

Each mention is placed by the extractor's own rule id, so the assignment is
mechanical and auditable:

| class | share of the court's 70,231 mentions |
|---|---:|
| RESOLVED_STATUTE — instrument and article both resolved | 66.8 % |
| NAMED_SOURCE — jurist, book, named maxim, verse, hadith | **18.2 %** |
| UNNAMED — no source to follow | **11.2 %** |
| UNRESOLVED_STATUTE — a statutory citation whose article did not resolve | 3.8 % |

The unnamed share is not spread evenly. It is a property of certain kinds of
authority:

| authority type | mentions | names a source |
|---|---:|---:|
| Qur'an | 1,700 | 100 % |
| hadith | 4,144 | 100 % |
| contract | 625 | 88.6 % |
| **fiqh** | **10,289** | **59.9 %** |
| legal maxim | 801 | 31.2 % |
| judicial principle | 1,114 | 0 % |
| custom | 675 | 0 % |
| judicial discretion | 1,305 | 0 % |

Scripture is always traceable — a chamber that quotes a verse quotes it. Fiqh
is traceable three times in five: 6,163 of the 10,289 mentions name a jurist
or a book, and the remaining 40.1 per cent — 4,126 mentions — are «المقرر
فقهاً» or «المستقر شرعاً» with nothing to follow. Settled judicial practice and trade custom are, by their nature, never
attributed to a locatable source.

**This is not a criticism of drafting.** A chamber writes for the parties in
front of it, and a party does not need a page reference to «الأصل بقاء الدين
في الذمة». What it is, is a measurable bound on what any outside reader — a
researcher, a replication, a retrieval system — can do with the record.

## 3 · Per judgment, and over time

Share of the court's own authority mentions that a reader could follow from
the citation alone: median **100 per cent**, quartile 80, mean 87.4, and
**69.4 per cent of judgments are fully traceable** (95 % CI 68.9–70.0).

Most judgments are entirely followable, because most judgments cite only
statutes. The problem is concentrated in the ones that reason from fiqh.

Over the window, traceability rises for a reason that has nothing to do with
citation practice:

| year | resolved statute | named source | unnamed |
|---|---:|---:|---:|
| 1443 | 62.5 % | 16.2 % | 13.0 % |
| 1444 | 65.7 % | 19.5 % | 11.4 % |
| 1445 | 69.7 % | 16.9 % | 10.6 % |
| 1446 | 74.6 % | 14.6 % | 7.8 % |

The statutory share grows and everything else is diluted with it — the same
arithmetic as the fiqh trend in `COMPLETENESS.md` §8. Nothing here says
chambers are attributing better; the resolved-statute column is doing the
work, and the unresolved-statute column falling from 8.3 to 2.9 per cent is
this repository's own extractor improving on the same corpus rather than the
corpus changing.

## 4 · What this is for

Question 8 of the asset goal — *how much judicial authority is independently
traceable* — now has a number and its components. Question 9 — *what does
statute-only legal AI miss* — has coverage bounds rather than an anecdote:
it is right about six judgments in ten, incomplete in three, and blind in one.

The components are kept as components. No single traceability score is
published, because "traceable" means something different for a statute article
(resolvable to enacted text) than for a hadith (locatable in a canonical
collection) than for a maxim (attributable to a tradition but rarely to a
page), and averaging those would produce a number nobody could interpret.
