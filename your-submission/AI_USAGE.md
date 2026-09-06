# AI usage disclosure

I used Codex as a programming and research assistant to inspect the starter
kit, propose experiment structure, draft the preparation/analysis scripts,
derive candidate calculations, and edit this repository. I used its web access
to locate the FLORES documentation, official public archive, and XLM-R model
card.

I did **not** treat generated prose as evidence. Every numerical claim in this
submission was regenerated locally from the checked-in scripts and their saved
CSV/JSON outputs. The corpus archive's SHA-256 is in the manifest; tokenizer
versions are pinned; and commands appear in `NOTEBOOK.md`.

AI initially suggested using a generic Hugging Face dataset loader and an
`AutoTokenizer` wrapper. In this environment, the FLORES mirror was gated and
the wrapper installation was interrupted. I instead used the official Meta
archive and the official XLM-R SentencePiece model directly, then documented
that change. AI also made it easy to overstate the tokenizer comparison; the
final memo explicitly rejects a standalone tokenizer swap and flags the lack of
product-traffic and quality validation.

No external LLM inference API, paid dataset, or fabricated benchmark output was
used. The Part C memo is a decision proposal, not a claim that native-speaker
evaluation has occurred. I understand that I must be able to re-run and explain
every command, formula, assumption, and limitation during the defense.
