# Source C: what the securities committees publish, and what may be taken

The programme's third goal is a genuinely zero-shot test — a publisher whose
documents have never touched this parser, opened once, with no development
set built from it. GSTC is now saturated as a development source and
GSTC_TEST2 is spent; MOJ_TEST was valid for the architecture frozen at the
time. A third source is the only remaining way to learn something new about
generalisation.

The Committees for Resolution of Securities Disputes (لجان الفصل في منازعات
الأوراق المالية, CRSD) were the preferred candidate, and this records what
was checked before anything was taken.

## Access and policy

`crsd.org.sa` redirects to `crsd.gov.sa`. Its robots.txt, fetched
2026-08-30, is short:

```
User-agent: *
Disallow: /_layouts/
Disallow: /_vti_bin/
Disallow: /_catalogs/
Sitemap: https://crsd.gov.sa:443/sitemap.xml
```

Everything outside those three prefixes is permitted. The sitemap holds 500
URLs and lists no decisions: 318 of them are press announcements.

## What is published

The open-data section (`/ar/OpenData/`) declares nine collections. Two are
decisions:

- **قرارات لجنة الفصل المختزلة** — abridged decisions of the Resolution
  Committee, first instance
- **قرارات لجنة الاستئناف المختزلة** — abridged decisions of the Appeal
  Committee

Both are PDF document libraries. `Style Library/Portal/js/decisions.js`, the
site's own listing script, builds each link as

```js
var url = `${_spPageContextInfo.webServerRelativeUrl}/Documents/${item.LinkFilename}`;
```

so a decision lives at `/ar/OpenData/ResolutionDecisions/Documents/<decision
number>.pdf`, and that path is **not** disallowed by robots.

Two courts, one appealing the other, decision-numbered, Hijri-dated. For a
project whose central measurement is which articles a bench applies, this is
close to an ideal third source.

## Why it cannot be taken yet

The listing is the problem, not the documents. `decisions.js` calls
`ReturnDataFromList`, and `utils.js` shows where that goes:

```js
const url = Lang.LangUrl + '/_LAYOUTS/15/CRSD.Internet/PortalHandler.ashx?' + query;
```

**The only enumeration route the site offers is under `/_layouts/`, which its
own robots.txt disallows.** The `_api` REST route appears once in the
principles page and is commented out; a single probe of it from this network
returned the portal's access-error page with a support ID, which is a WAF
response and is not evidence either way about the source.

So the position is: the documents are permitted, the index to them is not.
Enumerating the library by any route the publisher has closed would be
exactly the circumvention this project has undertaken not to do.

Three lawful ways forward, none of which is mine to choose:

1. **Ask.** Write to the General Secretariat and request the decision list,
   or permission to use the handler. They publish a helpdesk address.
2. **A different allowed index.** If the publisher exposes a library view
   outside `/_layouts/`, it can be used. This was not tested, because testing
   it means guessing an endpoint.
3. **A different Source C.** The Board of Grievances and the national
   open-data portal were both unreachable from this session's network
   (connection reset at the proxy, and HTTP 503) — which says nothing about
   whether they are available, only that they were not available here.

## Licensing

Every page carries `جميع الحقوق محفوظة للأمانة العامة للجان الفصل في منازعات
الأوراق المالية © 2025`. There is no open licence anywhere on the site, and
the open-data section states none. Reading these documents for research is
one thing; redistributing their text in this repository is another, and this
repository will not carry CRSD text unless a licence or a permission says it
may.

## Privacy

`/ar/MediaCenter/Lawsuits/` publishes class-action tracking pages. One of the
attachments on the page examined is titled **«قائمة أسماء المنضمين في
الدعوى»** — a list of the names of individuals who joined the claim. Any
ingestion of this publisher needs an exclusion rule of the kind
`INVENTORY.md` already applies to eleven GSTC collections, written before a
single file is read rather than after.

## What was taken, and what it showed

Eight PDFs were taken: the **Judicial Bulletin** (النشرة القضائية), volumes
one to eight, each linked statically from `/ar/OpenData/Magazines/` at an
allowed path. They were downloaded once, two seconds apart, and are held
outside the repository.

They are not a decision corpus. They are a newsletter — statistics,
committee news, summaries — 8,000 to 12,000 characters of extracted text
each, and **thirteen occurrences of «المادة» across all eight volumes
together**. As an evaluation set that is nothing. It would have been easy to
mistake for one from the name alone.

They did show something. The text layer of six of the eight is written in
**Arabic Presentation Forms-B** — the ligature block, U+FB50–U+FEFF —
between 619 and 5,841 codepoints per volume:

```
>>> canonicalise("ﺍﻟﻤﺎﺩﺓ (٢٩) ﻣﻦ ﻧﻈﺎﻡ ﺍﻹﺛﺒﺎﺕ")["canonical"]
'ﺍﻟﻤﺎﺩﺓ (29) ﻣﻦ ﻧﻈﺎﻡ ﺍﻹﺛﺒﺎﺕ'          # digits fixed, letters not
>>> "المادة" in canonicalise(...)["canonical"]
False
>>> "المادة" in unicodedata.normalize("NFKC", ...)
True
```

`canonical.py` strips tatweel, repairs bidi, swaps the transposed lam-alef
and normalises digits. It does not apply NFKC, so a presentation-form
document yields **zero** citations and looks, to every downstream count, like
a document that cites nothing. This is a **fourth corruption family**,
distinct from the three `EXTRACTION.md` records:

| family | detector | recovery |
|---|---|---|
| permutation (bidi, lam-alef, brackets) | — | canonicalisation |
| substitution (broken ToUnicode) | letter-frequency depression | none |
| substitution with dropped glyphs | fragmentation rate | none |
| **presentation forms** | **codepoints in U+FB50–U+FEFF** | **NFKC** |

**The fix is one line and is not being made.** The parser is frozen; more to
the point, CRSD is a candidate held-out source, and a parser repaired against
a source is a parser that can no longer be tested on it. The family is
recorded here so the repair can be made deliberately, before the zero-shot
set is opened, and declared when it is.

## Status

PHASE 12 is complete and PHASE 13 is **blocked**, on a policy question rather
than a technical one. No zero-shot number exists for Source C, and none is
claimed. The eight bulletins are held outside the repository and are not
evidence of anything except the fourth corruption family.
