# Routing recommendation - corrected headline

**Decision.** Do not use `REPORT_v0.md`'s “Hindi is 6×” estimate to route or
budget traffic. On 1,012 aligned FLORES devtest sentences, GPT-2 BPE requires
198.31 Hindi tokens per matched sentence versus 26.72 English (7.42×); Kannada
and Tamil are 13.58× and 15.54×. In the same experiment, the multilingual
XLM-R SentencePiece tokenizer needs only 1.25×, 1.35×, and 1.35× English,
respectively. The full result and exact commands are reproducible in this
repository.

**Recommendation.** Make “tokenizer/model family supports the target scripts”
a required gate for any Indic routing decision. Evaluate a production-capable
multilingual model/tokenizer alongside the incumbent on representative
language-and-intent traffic, then route only after quality and actual latency
meet their gates. Do not swap a tokenizer under an existing model: the
vocabulary, embeddings, and weights are coupled. These counts demonstrate why
a multilingual model path merits evaluation; they do not license a standalone
tokenizer substitution or prove end-to-end quality.

**Metric.** Use aggregate **body tokens per parallel sentence** as the design
comparison. It holds the intended semantic request constant, unlike words,
characters, or bytes. For production monitoring, track the **P95 input-token
count per successful request**, stratified by detected language, canonical
intent, and model version. A rise or gap beyond the offline estimate is direct
evidence that the corpus stopped representing traffic.

**Biggest caveat.** FLORES is edited parallel web prose, not Indian assistant
traffic. It omits code-switching, Romanized text, typos, multi-turn context,
and the product's output distribution. Its tokenizer result must be verified
on privacy-safe, intent-stratified production samples before financial
planning. It also cannot compare model quality: XLM-R here is a tokenizer
diagnostic, not a recommendation to deploy XLM-R as a generative assistant.
