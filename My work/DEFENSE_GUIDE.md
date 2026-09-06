# Defense guide - derive, do not recite

This is a short preparation aid for the 30-minute defense. It contains only
claims already measured in the repository. Before the session, run
`run_all.ps1`, open the CSV files it produces, and be ready to re-derive each
number from first principles.

## Three-minute narrative

1. `REPORT_v0.md` was treated as a hypothesis rather than an authority.
2. I replaced its 10-line smoke test with 1,012 line-aligned FLORES devtest
   translations in English, Hindi, Kannada, and Tamil, then preserved case and
   counted body tokens only.
3. GPT-2's per-parallel-sentence cost gap is much larger than the report said
   (Hindi 7.42x; Kannada 13.58x; Tamil 15.54x), while XLM-R's tokenizer is
   1.25-1.35x. That supports evaluating a multilingual *model family*, not
   swapping a tokenizer beneath a deployed model.
4. The serving report mixed prompt-plus-output throughput with generated-token
   goodput. Batch 24's 1,607.4 reported tok/s is 200.9 output tok/s; the
   batch-32 collapse aligns with KV saturation and sequence preemption.
5. The product-style recommendation is deliberately reversible: a prompt-only,
   feature-flagged test in Hindi and Kannada with human gates, before training
   or adding a rewriter.

## Numbers to re-derive

| Question | Derivation |
|---|---|
| Why 112 KiB KV/token? | `2 (K,V) * 28 layers * 8 KV heads * 128 dims * 2 fp16 bytes = 114,688 bytes = 112 KiB`. |
| Why ~25 full sequences? | `(24e9 * .92 - 4.2e9 * 2 - 1.6e9) / 114,688 / 4,096 = 25.71`; floor to ~25. |
| Why is batch-24 goodput 200.9? | `(24 requests * 512 output tokens) / 61.16 seconds = 200.916`. |
| Independent goodput check | `1,607.4 * 512 / (3,584 + 512) = 200.925`; difference is rounded input. |
| Why use parallel sentences? | The denominator approximately fixes message meaning, while a whitespace word, grapheme, and byte measure different language-dependent units. |

## Likely counterfactuals

**“If the runtime uses fp8 KV cache?”** KV bytes/token halves to 56 KiB; the
same simplified memory calculation roughly doubles token capacity. It may
change quality/performance, so measure it rather than assume it is free.

**“Why not deploy XLM-R?”** XLM-R here is a tokenizer diagnostic and is an
encoder model. The experiment has not evaluated generative quality, latency,
or a compatible serving model.

**“What would overturn the routing recommendation?”** Privacy-safe,
intent-stratified production samples could show a different token distribution,
or a multilingual candidate could fail quality/latency gates. The production
monitor is P95 input tokens per successful request by language, intent, and
model version.

**“Why not batch 48?”** Its reported tok/s has already dropped to 1,298.5,
output goodput to 162.3, KV utilization is 0.97, and 23 sequences were
preempted. More admitted long requests make the system less useful.

## Live-edit readiness

Be ready to add an `argparse` option that changes one thing at a time, then
re-run the analysis and explain the new result. Safe examples are a
`--limit-sentences` input-size option or a `--preserve-case` switch. Do not
claim a result before rerunning the script and reading its generated CSV.
