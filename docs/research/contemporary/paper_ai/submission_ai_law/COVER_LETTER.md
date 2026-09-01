Dear Editors,

Please consider the manuscript **“What Preprocessing Does to Legal Retrieval”** for publication in *Artificial Intelligence and Law*.

The paper studies a practical evaluation problem in legal AI: when a corpus intervention changes retrieval performance, how much of that change is attributable to the semantic class removed and how much is simply due to having less evidence in the index? We test this on a temporally fenced statutory-article retrieval task built from 105,575 resolved citations in published Saudi commercial judgments.

The central controlled result is that removing recurring legal wording lowers MRR@10 by 0.0241, compared with 0.0089 for same-volume random removal. The targeted loss is therefore 2.7 times the mean volume-only loss, while the same intervention is volume-equivalent on a different downstream corpus analysis. A second experiment decomposes frozen-index loss against a same-volume live-index control, leaving 70%, 64%, and 62% of the measured one-, two-, and four-quarter loss associated with age rather than shrinkage.

The manuscript deliberately does not claim novelty for BM25, citation-context retrieval, matched-budget controls, downstream evaluation of boilerplate removal, or temporal retrieval analysis. Its contribution is the controlled legal-retrieval evidence and the resulting bounded evaluation recommendation for legal-corpus preprocessing.

The work is reproducible through version-controlled code and result artifacts, and the manuscript documents material use of generative-AI research assistance while retaining human accountability for the scientific claims and submission.

Thank you for considering the manuscript.

Sincerely,

`[CORRESPONDING AUTHOR — CONFIRM BEFORE SUBMISSION]`
