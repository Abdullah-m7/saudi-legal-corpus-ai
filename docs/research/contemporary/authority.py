#!/usr/bin/env python3
"""What kind of legal authority is a court invoking, and who is invoking it?

Nine types, the ones a Saudi commercial judgment actually reaches for. Every
rule below carries an id and an attested example, so a reader can audit the
classifier by reading it rather than by trusting it. The rule ids survive into
the gold sheet and into the results, which is the only way a disagreement
between a human reading and this module can be localised.

  statute        an article of a نظام or لائحة, via voice_attribution.CITE
  contract       an article or clause of the parties' own instrument
  fiqh_source    a jurist, a book of fiqh, or an unattributed appeal to fiqh
  legal_maxim    a قاعدة فقهية invoked as a rule
  quran          scripture, distinguished from hadith because they are
                 different authorities doing different work
  hadith         prophetic tradition
  judicial_principle  what the courts have settled among themselves
  custom         العرف, العادة, commercial practice
  discretion     the court naming its own discretionary power as the ground

Three of these were built from a census rather than a guess
(`arabic_paper/discretion_census.py`): 36 candidate markers were counted
across all 50,666 judgments first, four scored zero and were dropped. A zero
from a broken search reads exactly like a finding, and this project has been
caught by that before.

WHAT THE FIRST GOLD SAMPLE CHANGED. 126 rule hits and 80 random reasoning
sentences were read by hand (seed 23) before any of this was believed. It
found six defects, every one of which is repaired here and none of which
would have been visible from the rule text alone:

  contract.possessive fired on «نظام التحكيم في مادته (١١)» — a STATUTE in
    instrument-first order, not a contract. Eight of its nine sampled hits
    were statutes. It now requires that no نظام or لائحة be named just before.
  custom.trade fired inside the quoted text of article 164 of the commercial
    regulation, whose own words list «العرف، أو العادة المستقرة» as a factor
    the court must weigh. Seven of nine sampled hits were the statute
    speaking, not the court. Quoted spans are now excluded everywhere.
  hadith.citation matched «المتفق عليه» — «the agreed-upon» — as though it
    were «متفق عليه», the hadith grading. Four of nine. Hence 16,279 hits.
  discretion matched «ما تراه الدائرة», which is ordinary evaluative
    language, not discretion named as a ground. That alternative is dropped.
  the speaker cue was unreliable inside the reasons, which are the court's by
    construction; the nearest-cue heuristic read «قال ابن قدامة» as a party
    because a party was mentioned nearby. Voice is now decided structurally.
  and the recall half found markers with no rule at all: «المستقر فقهاً»,
    «المقرر قضاءً», the ligature ﷺ, «الكتاب والسنة», «حديث حسن صحيح».

WHAT THIS MODULE DOES NOT DO. It does not decide whether an authority is doing
substantive or procedural work in the sentence. For statutes that is read off
the instrument, which is validated (`match_instruments.PROCEDURAL`). For
everything else it is reported as unknown rather than guessed, because a maxim
can carry either and a marker count cannot see which.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402

# ---------------------------------------------------------------- the rules
# (type, rule id, pattern, an example attested in the corpus)
RULES = [
    # ---- the parties' own instrument. Ordered before nothing in particular,
    # but kept apart from statute because «المادة الخامسة من العقد» is not law.
    ("contract", "contract.article",
     r"(?:ال)?ماد[ةه]\s*(?:رقم\s*)?\(?\s*[^\)\n]{1,24}?\s*\)?\s*من\s+"
     r"(?:هذا\s+)?(?:ال)?عقد",
     "«المادة السابعة من العقد»"),
    # «في مادته (N)» carries no instrument of its own: the referent is
    # whatever was named before it. In the validation sample every single one
    # of these was a STATUTE in instrument-first order -- «نظام الإثبات في
    # مادته (29/1)» -- a form CITE cannot see at all. A fixed-width lookbehind
    # cannot reach the name, so the referent is resolved in code, in
    # `mentions`, by reading the 70 characters before the match.
    ("contract", "contract.possessive",
     r"(?:في|وفق|بموجب|نص\s+في)\s+(?:ماد[ةت]ه|لائحت[هها]|نظامه[ا]?)"
     r"\s*:?\s*\(?\s*(?:[\d٠-٩]{1,3}|الأولى|الثانية|الثالثة|الرابعة|الخامسة)",
     "«والمتضمن في مادته: (5)» · «نظام الإثبات في مادته (29/1)»"),
    ("contract", "contract.clause",
     r"(?:ال)?بند\s+(?:ال)?[^\s]{2,14}\s+من\s+(?:ال)?عقد"
     r"|(?:ال)?بند\s+(?:ال)?(?:أول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر)"
     r"[^\.،؛\n]{0,12}من\s+(?:ال)?عقد",
     "«البند العاشر من العقد»"),

    # ---- fiqh, named
    ("fiqh_source", "fiqh.jurist",
     r"ابن\s+تيمية|ابن\s+القيم|ابن\s+قدامة|محمد\s+بن\s+إبراهيم|شيخ\s+الإسلام",
     "«قال شيخ الإسلام ابن تيمية رحمه الله»"),
    ("fiqh_source", "fiqh.book",
     r"مجموع\s+(?:ال)?فتاوى|كشاف\s+القناع|منتهى\s+الإرادات|الروض\s+المربع"
     r"|مطالب\s+أولي\s+النهى|زاد\s+المعاد|(?<![ء-ي])المغني(?![ء-ي])"
     r"|(?<![ء-ي])الإنصاف(?![ء-ي])",
     "«وجاء في كشاف القناع (419/3)»"),
    # unattributed appeal to fiqh: the same authority without a source
    ("fiqh_source", "fiqh.unattributed",
     r"(?:ال)?م[قست]?[تق]?قرر\s+فقه|(?:ال)?مستقر\s+فقه|(?:ال)?م[تق]?قرر\s+شرع"
     r"|عند\s+الفقهاء|لدى\s+الفقهاء|جمهور\s+الفقهاء|أهل\s+العلم"
     r"|نص\s+الفقهاء|الكتاب\s+والسنة|(?<![ء-ي])الراجح(?![ء-ي])",
     "«ولما كان المقرر فقهاً وقضاءً» · «ومن المستقر فقهًا القضاءُ على الغائب»"),

    # ---- maxims
    ("legal_maxim", "maxim.named",
     r"القاعدة\s+الفقهية|القواعد\s+الفقهية|القاعدة\s+الكلية",
     "«وللقاعدة الفقهية: الضرر يزال»"),
    ("legal_maxim", "maxim.text",
     r"الضرر\s+يزال|الأصل\s+براءة\s+الذمة|اليقين\s+لا\s+يزول\s+بالشك"
     r"|العادة\s+محكمة|الخراج\s+بالضمان|الأصل\s+في\s+العقود",
     "«ولأن الأصل عدم السداد»"),

    # ---- scripture, split because they are different authorities
    ("quran", "quran.citation",
     r"قال\s+(?:الله\s+)?تعالى|لقول[هـ]?\s+تعالى|قول[هـ]?\s+تعالى"
     r"|قال\s+عز\s+وجل",
     "«ولقوله تعالى: يا أيها الذين آمنوا أوفوا بالعقود»"),
    # «المتفق عليه» is «the agreed-upon» and is not the hadith grading
    # «متفق عليه». The lookbehind for an Arabic letter is what separates them.
    ("hadith", "hadith.citation",
     r"صلى\s+الله\s+عليه\s+وسلم|\uFDFA|عليه\s+الصلاة\s+والسلام"
     r"|(?<![ء-ي])متفق\s+عليه(?![اة])"
     r"|رواه\s+(?:البخاري|مسلم|أحمد|أبو\s+داود|الترمذي|النسائي|ابن\s+ماجه)"
     r"|أخرجه\s+(?:البخاري|مسلم|البيهقي|الترمذي|الدارقطني|أحمد)"
     r"|حديث\s+(?:حسن|صحيح|النبي)|في\s+الحديث\s+الصحيح",
     "«ولقوله صلى الله عليه وسلم: على اليد ما أخذت حتى تؤديه»"),

    # ---- what the judiciary has settled among itself
    ("judicial_principle", "principle.settled",
     r"استقر\s+(?:عليه\s+)?القضاء|ما\s+استقر\s+عليه\s+القضاء"
     r"|جرى\s+(?:عليه\s+)?العمل\s+القضائي|المبادئ\s+القضائية"
     r"|ما\s+استقرت\s+عليه\s+الأحكام|استقر\s+عليه\s+قضاء"
     r"|الم[قت]?[تق]?قرر\s+قضاء|جرت\s+(?:به\s+)?(?:أغلب\s+)?الأحكام"
     r"|جرى\s+عليه\s+قضاء",
     "«حيث استقر القضاء على أن الإقرار بالكتابة كالإقرار باللسان»"),

    # ---- custom and commercial practice
    # «العرف، أو العادة المستقرة» dropped as a standalone marker: it is the
    # wording of article 164 of the commercial regulation, quoted in tens of
    # thousands of judgments, and it is the statute speaking, not the court.
    ("custom", "custom.trade",
     r"العرف\s+التجاري|العرف\s+الجاري|جرى\s+(?:بذلك\s+)?العرف"
     r"|المتعارف\s+عليه|تعارف\s+عليه\s+التجار|جرى\s+العرف"
     r"|(?<![ء-ي])كعرف(?![ء-ي])|الأعراف\s+التجارية",
     "«وهو ما استقرت عليه التعاملات التجارية وتعارف عليه التجار»"),

    # ---- the court naming its own power as the ground
    # «ما تراه الدائرة» is dropped: «وهو ما تراه الدائرة كافيًا» is a court
    # weighing evidence, which every judgment does, not a court naming
    # discretion as the ground it decides on.
    ("discretion", "discretion.named",
     r"السلطة\s+التقديرية|سلطة\s+تقديرية|ولاية\s+تقديرية"
     r"|للدائرة\s+من\s+سلطة|سلطة\s+التقدير|بما\s+لها\s+من\s+سلطة"
     r"|(?<![ء-ي])الاجتهاد(?![ء-ي])",
     "«ولما للدائرة من سلطة تقديرية في تقدير أتعاب المحاماة»"),
]
COMPILED = [(t, rid, re.compile(p), ex) for t, rid, p, ex in RULES]
# what «مادته» can hang on, looking back
BEFORE_INSTRUMENT = re.compile(r"(?:ال)?(?:نظام|لائحة|اللائحة|أنظمة)"
                               r"[^\.؛\n]{0,50}$")
BEFORE_CONTRACT = re.compile(r"(?:ال)?(?:عقد|اتفاقية|الاتفاق|ملحق)"
                             r"[^\.؛\n]{0,50}$")
TYPES = ["statute", "contract", "fiqh_source", "legal_maxim", "quran",
         "hadith", "judicial_principle", "custom", "discretion"]

# «المادة (5) من العقد» also matches nothing in CITE, which requires the
# instrument word to be نظام or لائحة, so contract and statute cannot
# double-count. Asserted in tests rather than assumed.


# A judgment quotes the statutes it applies, at length, and the quoted words
# are the legislator's rather than the court's. Article 164 of the commercial
# regulation lists «العرف، أو العادة المستقرة» among the factors a court must
# weigh, and it is quoted in tens of thousands of judgments: counting those as
# the court invoking custom is not a small error, it is the largest single
# error the first gold sample found.
#
# A quotation opens after a cue -- «ونصها:», «نصت على أنه», «ما نصه» -- and
# runs to the closing mark of whichever it opened with. Unclosed quotations
# are given a bounded run rather than swallowing the rest of the judgment.
QUOTE_OPEN = re.compile(
    r"(?:ونص[هاّ]{0,3}|نص[تّ]?\s+عل[يى]\s*(?:أنه|أن)?|ما\s+نصه|جاء\s+فيها?"
    r"|والتي\s+تنص|تنص\s+عل[يى]|يلي)\s*:?\s*[\"“«\(]")
CLOSERS = {'"': '"', '\u201c': '\u201d', '\u00ab': '\u00bb', '(': ')'}
QUOTE_MAX = 1800


def quoted_spans(text):
    """(start, end) of every passage the judgment is quoting, not writing."""
    out = []
    for m in QUOTE_OPEN.finditer(text):
        opener = text[m.end() - 1]
        close = CLOSERS.get(opener)
        end = -1
        if close:
            end = text.find(close, m.end())
        if end < 0 or end - m.end() > QUOTE_MAX:
            end = min(len(text), m.end() + QUOTE_MAX)
        out.append((m.end(), end))
    return out


def _overlaps(a, b, spans):
    return any(x < b and a < y for x, y in spans)


def _in_quote(at, quotes):
    """Membership is tested on the START offset only.

    CITE's instrument capture is greedy enough to run past the end of the
    citation and into the «ونصها:"» that opens the quotation of the very
    article it is citing, so an end-inclusive test marked the citation itself
    as quoted. Where a mention begins is what decides whose words it is.
    """
    return any(a <= at < b for a, b in quotes)


def mentions(text, sections, index=None, order=None):
    """Every authority mention in one judgment, with who invoked it and where.

    Returns dicts carrying: type, rule, offset, segment (recital / reasoning /
    operative / unknown), speaker (court / party / unattributed), and for
    statutes the instrument track, article number and procedural flag.
    """
    spans = V.segments(text, sections or {})
    quotes = quoted_spans(text)
    out = []
    claimed = []          # statute spans, so contract rules cannot re-read them

    last = M.Recent()
    for m in V.CITE.finditer(text):
        tid = kind = None
        if index is not None:
            tid, kind = M.match(m.group(2), index, order, last)
            if kind == "named":
                last.note(tid)
        seg = V.voice_at(spans, m.start())
        speaker = _speaker(text, spans, m.start())
        claimed.append((m.start(), m.end()))
        out.append({
            "type": "statute", "rule": "statute.cite", "at": m.start(),
            "segment": seg, "speaker": speaker,
            "inQuote": _in_quote(m.start(), quotes),
            "instrument": tid, "instrumentNamed": kind,
            "article": m.group(1).strip()[:24],
            "procedural": (tid in M.PROCEDURAL) if tid else None,
        })

    for typ, rid, pat, _ in COMPILED:
        for m in pat.finditer(text):
            if typ == "contract" and _overlaps(m.start(), m.end(), claimed):
                continue
            if rid == "contract.possessive":
                # whose article is it? Read back to the noun it hangs on.
                before = text[max(0, m.start() - 70):m.start()]
                if BEFORE_INSTRUMENT.search(before):
                    typ, rid = "statute", "statute.possessive"
                elif not BEFORE_CONTRACT.search(before):
                    continue          # referent unrecoverable: do not guess
            out.append({
                "type": typ, "rule": rid, "at": m.start(),
                "segment": V.voice_at(spans, m.start()),
                "speaker": _speaker(text, spans, m.start()),
                "inQuote": _in_quote(m.start(), quotes),
                "instrument": None, "instrumentNamed": None,
                "article": None, "procedural": None,
            })
    out.sort(key=lambda d: d["at"])
    return out


def _speaker(text, spans, at):
    """court / party / unattributed, read in the segment the mention sits in."""
    for a, b, _ in spans:
        if a <= at < b:
            who, _, _ = V.attribute(text[a:b], at - a)
            return who
    return "unattributed"


def voice(mention):
    """Who is speaking, decided structurally rather than by a nearby cue.

    The first gold sample settled this. Inside «الأسباب:» the author is the
    bench, by construction: the reasons are what the court wrote. The
    nearest-cue heuristic read «قال ابن قدامة في الكافي» as a party because
    the sentence before it mentioned «المدعي وكالة», and three of the sampled
    reasoning items were mislabelled that way. The one real exception is a
    party submission the court reproduces, which is a quotation, so it is
    caught by the quote spans rather than by a cue.

    The recital is the opposite case: it is mostly the parties' pleadings in
    the court's narration, so there the cue is informative and is used.
    """
    seg, who = mention["segment"], mention["speaker"]
    if seg == "reasoning":
        return "party_in_reasons" if mention.get("inQuote") and who == "party" \
            else "court_reasoning"
    if seg == "recital":
        return "party_argument" if who == "party" else "recital"
    if seg == "operative":
        return "operative"
    return "unknown"


if __name__ == "__main__":
    print(f"{len(COMPILED)} rules over {len(TYPES)} types\n")
    for t, rid, _, ex in COMPILED:
        print(f"  {t:<20}{rid:<24}{ex}")
