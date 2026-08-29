#!/usr/bin/env python3
"""One page to carry to GFEAI 2026, generated from the same macros as the papers.

The 4th UNESCO Global Forum on the Ethics of AI, Riyadh, 14-17 September 2026.
The audience is 194 delegations of decision-makers, not journal readers, and a
booth conversation is sixty seconds. So this is not a paper summary. It is:
one sentence, three numbers, two findings that matter to *this* audience, and
a QR to the repository.

Nothing on it is typed. Every figure is read from the generated numbers.tex
files the manuscripts are typeset from, so the card cannot drift from the
papers -- which is the whole claim it makes about itself.

    python3 build_card.py     ->  gfeai_card.pdf   (A4, two sides)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
OUT = HERE / "gfeai_card.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
REPO = "https://github.com/Abdullah-m7/saudi-legal-corpus-ai"

SOURCES = [RESEARCH / "applied_law_paper" / "numbers.tex",
           RESEARCH / "appeal_paper" / "numbers.tex"]
CITATOR = RESEARCH / "citator" / "index.json"


def macros():
    out = {}
    for path in SOURCES:
        for name, raw in re.findall(
                r"\\newcommand\{\\(\w+)\}\{([^{}]*(?:\{,\}[^{}]*)*)\}",
                path.read_text(encoding="utf-8")):
            out[name] = raw.replace("{,}", ",")
    return out


def qr(url):
    import segno
    import io as _io
    buf = _io.BytesIO()
    segno.make(url, error="m").save(buf, kind="svg", scale=1, border=0,
                                    dark="#14171c", svgclass=None,
                                    lineclass=None, xmldecl=False)
    return buf.getvalue().decode()


CSS = """
@page { size: A4; margin: 14mm 15mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans", Helvetica, Arial, sans-serif;
       color: #14171c; font-size: 10.2pt; line-height: 1.5; }
.ar { direction: rtl; text-align: right;
      font-family: "Noto Naskh Arabic", serif; line-height: 1.85; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 .15em;
     letter-spacing: -.2px; }
.sub { font-size: 10pt; color: #5b646e; margin: 0 0 1.1em; }
.lede { font-size: 11.4pt; line-height: 1.55; margin: 0 0 1.3em;
        padding-bottom: 1.1em; border-bottom: 2px solid #14171c; }
.nums { display: flex; gap: 0; margin: 0 0 1.4em; }
.n { flex: 1; padding-right: 10px; }
.n b { display: block; font-size: 19pt; line-height: 1.1; letter-spacing: -.5px; }
.n span { font-size: 8.6pt; color: #5b646e; display: block; margin-top: .25em; }
h2 { font-size: 9pt; text-transform: uppercase; letter-spacing: 1.1px;
     color: #5b646e; margin: 0 0 .7em; font-weight: 700; }
.find { margin: 0 0 1.15em; padding-right: 4px; }
.find > b { display: block; font-size: 11pt; margin-bottom: .25em; }
.find p { margin: 0; color: #2b3138; }
.rule { border: none; border-top: 1px solid #d7dce1; margin: 1.4em 0; }
.foot { display: flex; align-items: center; gap: 14px;
        border-top: 2px solid #14171c; padding-top: 12px; margin-top: 1.2em; }
.foot .who { flex: 1; }
.foot .who b { font-size: 11.5pt; }
.foot .who span { display: block; color: #5b646e; font-size: 9pt; }
.qr { width: 104px; height: 104px; }
.qr svg { width: 104px; height: 104px; display: block; }
.page2 { page-break-before: always; }
.ar h1, .ar .lede, .ar h2, .ar .find > b { text-align: right; }
.ar h2 { text-transform: none; letter-spacing: 0; font-size: 10pt; }
.ar .nums { flex-direction: row-reverse; }
.ar .n { padding-right: 0; padding-left: 10px; }
.ar .foot { flex-direction: row-reverse; }
"""

EN = """
<h1>Auditable AI on a country&rsquo;s law</h1>
<p class="sub">A machine-readable corpus of Saudi legislation and adjudication
&mdash; and what it shows about grounding AI systems in national law.</p>

<p class="lede">Every article of {INSTRUMENTS} Saudi instruments, verified
against the official source. Every judgment the Ministry of Justice publishes
in full text. Joined at the level a lawyer argues: the article. Built so that
any claim made from it can be checked by anyone, from the deposited data, with
the deposited code.</p>

<div class="nums">
  <div class="n"><b>{ARTICLES}</b><span>verified articles,<br>{INSTRUMENTS} instruments</span></div>
  <div class="n"><b>{JUDGMENTS}</b><span>judgments in full text,<br>{APPEALS} with the appeal</span></div>
  <div class="n"><b>{ENTRIES}</b><span>citations matched to<br>the article cited</span></div>
</div>

<h2>Two findings for this room</h2>

<div class="find">
  <b>Coverage is not grounding.</b>
  <p>Only {CITEDSHARE}&thinsp;% of the enacted statute book is ever cited in a
  published judgment, and {PROCEDURAL}&thinsp;% of what courts do apply is
  procedural rather than substantive. A retrieval system built over the
  statute book returns law the courts never use. Grounding a model in
  &ldquo;the law&rdquo; and grounding it in the law that decides cases are
  different engineering problems, and the gap between them is measurable.</p>
</div>

<div class="find">
  <b>An evaluation set inherits the habits of whoever wrote it.</b>
  <p>The extractor here was validated against {JUDGMENTS} judgments and passed
  every check. Pointed once at a document written by a practising lawyer, it
  silently dropped half his citations: it had learned the publisher&rsquo;s
  drafting conventions as assumptions. The defect was worth {GAP} citations
  &mdash; {GAPSHARE}&thinsp;% of everything counted &mdash; and no amount of
  in-corpus testing could have found it. Held-out data from the same
  institution is not held out.</p>
</div>

<hr class="rule">

<h2>How it is kept honest</h2>
<p>No figure in any paper from this corpus is typed by hand. Each is computed
by a deposited script, written to JSON, and typeset from a generated macro; a
check refuses to build a manuscript that types one, a second refuses a result
older than the code that produced it, and a third guards the figures in the
notes. Corpus, code and checks are public.</p>

<div class="foot">
  <div class="who">
    <b>Abdullah Almohammedi</b>
    <span>abdullah.m.almohammedi@gmail.com &nbsp;&middot;&nbsp; ORCID 0009-0001-0832-0995</span>
    <span>{REPO}</span>
  </div>
  <div class="qr">{QR}</div>
</div>
"""

AR = """
<h1>ذكاءٌ اصطناعيّ قابلٌ للتدقيق على قانون دولة</h1>
<p class="sub">ذخيرة سعودية للأنظمة والأحكام مقروءةٌ آليًّا — وما تكشفه عن
إسناد نماذج الذكاء الاصطناعي إلى قانونٍ وطنيّ.</p>

<p class="lede">كلّ مادة في {INSTRUMENTS} أداةً نظامية، متحقَّقًا منها في مصدرها
الرسمي. وكلّ حكمٍ تنشره وزارة العدل بنصّه الكامل. مربوطان عند المستوى الذي
يحاجّ به المحامي: <b>المادة</b>. وبُنيت لتكون كلّ دعوى تُبنى عليها قابلةً
لأن يفحصها أيّ أحد، من البيانات المودَعة بالكود المودَع.</p>

<div class="nums">
  <div class="n"><b>{ARTICLES}</b><span>مادة متحقَّقة<br>في {INSTRUMENTS} أداة</span></div>
  <div class="n"><b>{JUDGMENTS}</b><span>حكمًا بنصّه الكامل<br>منها {APPEALS} باستئنافها</span></div>
  <div class="n"><b>{ENTRIES}</b><span>استشهادًا مسنَدًا<br>إلى المادة التي عناها</span></div>
</div>

<h2>نتيجتان تخصّان هذه القاعة</h2>

<div class="find">
  <b>التغطية ليست إسنادًا.</b>
  <p>لم يُستشهد إلا بـ{CITEDSHARE}٪ من مواد الأنظمة المسنونة في حكمٍ منشور،
  و{PROCEDURAL}٪ ممّا تطبّقه المحاكم فعلًا <b>إجرائيّ</b> لا موضوعيّ. فنظام
  استرجاعٍ مبنيّ على مدوّنة الأنظمة يُعيد قانونًا لا تستعمله المحاكم. وإسنادُ
  النموذج إلى «القانون» غيرُ إسناده إلى القانون الذي تُفصل به الخصومات —
  والفجوة بينهما قابلةٌ للقياس.</p>
</div>

<div class="find">
  <b>مجموعةُ التقييم ترث عادات من كتبها.</b>
  <p>اختُبر المستخرِج على {JUDGMENTS} حكمًا فاجتاز كلّ فحص. ثمّ وُجِّه مرّةً
  إلى مذكّرةٍ كتبها محامٍ ممارس، فأسقط نصف استشهاداته صامتًا: كان قد تعلّم
  أعراف صياغة الناشر <b>افتراضاتٍ</b>. وكلفة العيب {GAP} استشهادًا —
  {GAPSHARE}٪ من كل ما عُدّ — ولم يكن أيّ اختبارٍ داخل الذخيرة ليكشفه.
  <b>البيانات المحجوزة من المؤسسة نفسها ليست محجوزة.</b></p>
</div>

<hr class="rule">

<h2>وكيف يُضبط</h2>
<p>لا رقم في أيّ ورقةٍ من هذه الذخيرة يُكتب باليد. كلٌّ منها يُحسب بسكربتٍ
مودَع، ويُكتب إلى JSON، ويُنضَّد من ماكرو مولَّد؛ وحارسٌ يرفض بناء مخطوطةٍ
يُكتب فيها رقمٌ يدويًّا، وثانٍ يرفض نتيجةً أقدم من الكود الذي أنتجها، وثالثٌ
يحرس أرقام الملاحظات. والذخيرة والكود والحرّاس عامّة.</p>

<div class="foot">
  <div class="who">
    <b>عبدالله المحمدي</b>
    <span>abdullah.m.almohammedi@gmail.com &nbsp;&middot;&nbsp; ORCID 0009-0001-0832-0995</span>
    <span>{REPO}</span>
  </div>
  <div class="qr">{QR}</div>
</div>
"""


def main():
    if not Path(CHROME).exists():
        sys.exit(f"no browser at {CHROME}")
    m = macros()
    cit = json.loads(CITATOR.read_text(encoding="utf-8"))
    v = {
        "ARTICLES": m["nRegistryArticles"], "INSTRUMENTS": m["nInstruments"],
        "JUDGMENTS": m["nJudgments"], "APPEALS": m["nAppeals"],
        "ENTRIES": f"{cit['entries']:,}",
        "CITEDSHARE": m["nArticlesCitedShare"], "PROCEDURAL": m["nProceduralShare"],
        "GAP": m["nPrefixGap"], "GAPSHARE": m["nPrefixGapShare"],
        "REPO": REPO.replace("https://", ""), "QR": qr(REPO),
    }
    EASTERN = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

    def fill(t, arabic=False):
        for k, val in v.items():
            out = str(val)
            if arabic and k != "REPO" and k != "QR":
                out = out.replace(",", "٬").replace(".", "٫").translate(EASTERN)
            t = t.replace("{" + k + "}", out)
        return t
    html = ("<style>" + CSS + "</style>"
            "<link href='https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700"
            "&family=Noto+Naskh+Arabic:wght@400;700&display=swap' rel='stylesheet'>"
            "<div>" + fill(EN) + "</div>"
            "<div class='page2 ar'>" + fill(AR, arabic=True) + "</div>")
    page = HERE / "gfeai_card.html"
    page.write_text("<meta charset='utf-8'>" + html, encoding="utf-8")
    r = subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
                        page.as_uri()], capture_output=True, text=True)
    if r.returncode or not OUT.exists():
        sys.exit(f"chromium failed:\n{r.stderr[-2000:]}")
    page.unlink()
    pages = subprocess.run(["pdfinfo", str(OUT)], capture_output=True,
                           text=True).stdout
    print(f"wrote {OUT.name} — "
          + next(l for l in pages.splitlines() if l.startswith("Pages")))


if __name__ == "__main__":
    main()
