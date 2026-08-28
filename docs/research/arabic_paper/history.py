#!/usr/bin/env python3
"""Figures about this project's own history, which no current script recomputes.

Almost every number in these papers is a measurement: a script reads the
corpus, writes a JSON, and make_numbers.py turns that into a macro. A few are
not. What a superseded extraction pattern failed to see is a fact about a
version of the code that no longer exists, and re-deriving it would mean
shipping the broken pattern beside the working one purely so a sentence in a
paper could cite it.

So it is recorded here, with its provenance, and read from here by anything
that reports it. That puts it under the same guard as everything else: prose
cannot retype it, because prose types a macro.

This module imports nothing and is imported by no analysis script, so adding
to it cannot make a result file stale.
"""

# The citation pattern in voice_attribution.py accepts the prefixes Arabic
# attaches to «مادة»: ال، لل، بال، كال، فال، وال، ول، بل، ب، ل، و. An earlier
# version anchored on «المادة» alone and so never saw «وفقاً للمادة» or
# «استناداً للمادة», which are among the commonest forms in judicial
# reasoning. No check run against the judgments could see the gap --- the
# corpus shares the drafting habits that made those forms rare in it. It
# surfaced when the extractor was pointed at a practising lawyer's draft and
# silently dropped two of his four articles.
PREFIX_GAP = 16_682            # citations the «المادة»-only pattern never saw
PREFIX_GAP_SHARE = 15.7        # per cent of everything counted at the time

# Hand-read validation of the actor attribution in the statement of the case:
# forty attributions read against their judgments, thirty-seven correct.
VOICE_SAMPLE = 40
VOICE_CORRECT = 37
