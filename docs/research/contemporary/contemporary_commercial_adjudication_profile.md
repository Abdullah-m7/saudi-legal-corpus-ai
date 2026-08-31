# Contemporary commercial adjudication: a generated profile

Published Saudi commercial judgments, 1444–1446 AH. Every figure is read
from a results file, by `profile.py`. **Not a profile of the Saudi**
**judiciary**: 95 per cent of this corpus is commercial and it is published
judgments only.

## Corpus

| judgments | 28,090 |
|---|---:|
| carrying reasons | 23,626 (84.1 %) |
| median reasons length | 1,540 chars |
| authority mentions, bench | 62,256 |
| authority mentions, parties (strict / wide) | 10,283 / 30,486 |

## Who invokes what

| authority | bench | party (strict) | party (wide) |
|---|---:|---:|---:|
| statute | 70.60 % | 55.11 % | 69.03 % |
| contract | 0.86 % | 14.83 % | 10.03 % |
| fiqh_source | 14.78 % | 8.10 % | 6.09 % |
| legal_maxim | 1.08 % | 4.64 % | 3.10 % |
| quran | 2.46 % | 3.69 % | 2.25 % |
| hadith | 6.01 % | 8.29 % | 5.67 % |
| judicial_principle | 1.54 % | 1.00 % | 0.78 % |
| custom | 0.94 % | 3.79 % | 2.69 % |
| discretion | 1.72 % | 0.55 % | 0.36 % |

## How the bench reasons

| shape of the reasons | judgments | share |
|---|---:|---:|
| statute only | 12,641 | 53.5 % |
| hybrid | 6,781 | 28.7 % |
| none | 2,830 | 12.0 % |
| non statute only | 1,374 | 5.8 % |

Within hybrid reasoning, the commonest combinations (1445):

- STATUTE+FIQH_SOURCE — 40.4 %
- STATUTE+HADITH — 11.2 %
- STATUTE+JUDICIAL_PRINCIPLE — 10.4 %
- STATUTE+FIQH_SOURCE+HADITH — 6.8 %
- STATUTE+HADITH+QURAN — 6.7 %

## Where the two sides meet

| level | median Jaccard | no overlap | identical |
|---|---:|---:|---:|
| authority family | 0.500 | 26.9 % | 34.1 % |
| instrument | 0.333 | 42.5 % | 15.5 % |
| article | 0.000 | 80.2 % | 3.0 % |
| article, structural removed | 0.000 | 78.5 % | 6.8 % |
| article, dispute-specific only | 0.000 | 56.5 % | 24.9 % |

- P(shared instrument | both cite statute) = **56.2 %**
- P(shared article | shared instrument) = **35.3 %**
- P(shared article | both cite statute) = 19.8 %

## The operational core

- **7 articles** carry 50 % of the bench's statutory citations; 34 carry 75 %; 108 carry 90 %; 929 distinct articles in all
- the top 50 is **67.4 % structural procedural**, 19.9 % dispute-specific, 12.8 % ambiguous
- by function: jurisdiction 27.3 %, proof_rules 19.9 %, service_notice 16.5 %, other 12.8 %, appeal_finality 6.5 %

| rank | article | citations | cumulative |
|---:|---|---:|---:|
| 1 | commercial_courts_law art. 16 | 8,626 | 20.57 % |
| 2 | commercial_courts_law art. 30 | 4,571 | 31.47 % |
| 3 | evidence_law art. 29 | 3,780 | 40.49 % |
| 4 | commercial_courts_implementing_regulation art. 164 | 1,370 | 43.76 % |
| 5 | sharia_procedure_law art. 76 | 1,367 | 47.02 % |
| 6 | commercial_courts_law art. 78 | 1,230 | 49.95 % |
| 7 | evidence_law art. 21 | 1,029 | 52.4 % |
| 8 | evidence_law art. 17 | 840 | 54.41 % |

## Enacted against operational

| instrument | enacted | ever cited by the bench | % |
|---|---:|---:|---:|
| commercial_courts_law | 96 | 75 | 78.1 % |
| evidence_law | 129 | 96 | 74.4 % |
| sharia_procedure_law | 242 | 104 | 43.0 % |
| commercial_courts_implementing_regulation | 281 | 119 | 42.3 % |
| companies_law | 281 | 130 | 46.3 % |
| arbitration_law | 58 | 30 | 51.7 % |
| civil_transactions_law | 721 | 95 | 13.2 % |
| bankruptcy_law | 231 | 34 | 14.7 % |

## What a retrieval system would learn

Ranking 1,617 articles three ways:

| | full ∩ court | full ∩ party | court ∩ party |
|---|---:|---:|---:|
| top 10 | 8 | 7 | 5 |
| top 50 | 43 | 29 | 23 |
| top 100 | 84 | 68 | 55 |

Spearman: full/court 0.835, court/party **0.564**.

## Standing limitations

- commercial and published; not the Saudi judiciary
- party attribution is bracketed by two specifications, not solved
- the operational core measures adjudicatory visibility, not legal importance
- six citation forms remain invisible to the extractor, bounded at half a
  point of composition
- one primary annotator; no inter-annotator agreement is claimed
