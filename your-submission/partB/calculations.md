# Part B - Capacity reconciliation

The generated values in `capacity_results.json` and
`bench_reconciliation.csv` come from `python analyze_bench.py`. Arithmetic
uses decimal GB because `model_spec.md` gives a 24 GB GPU and a 1.6 GB overhead
in those units.

## B1. KV-cache capacity

Each token stores a K and a V vector for each layer:

```text
2 (K,V) × 28 layers × 8 KV heads × 128 dimensions × 2 bytes/fp16
= 114,688 bytes/token = 112 KiB/token
```

```text
managed GPU memory = 24.0 GB × 0.92                    = 22.08 GB
fp16 weights       = 4.2 billion parameters × 2 bytes =  8.40 GB
non-KV overhead                                          =  1.60 GB
KV budget                                               = 12.08 GB

12,080,000,000 / 114,688 = 105,329 KV tokens
105,329 / 4,096 = 25.71 => approximately 25 full sequences
```

This predicts a safe operating point just below 25 full 4,096-token
reservations. The long-context log agrees: batch 24 reaches 0.93 KV utilization
without preemption; batch 32 reaches 0.97 and preempts seven sequences. The
one-sequence difference is expected from block allocation, scheduler reserve,
and the deliberately approximate 1.6 GB overhead.

## B2. The long-context anomaly

| Long-prompt batch | Reported tok/s | Output goodput tok/s | KV util. | Preempted sequences | ITL p50 (ms) |
|---:|---:|---:|---:|---:|---:|
| 4 | 565.4 | 70.7 | 0.16 | 0 | 51.33 |
| 8 | 902.6 | 112.8 | 0.31 | 0 | 62.26 |
| 16 | 1311.4 | 163.9 | 0.62 | 0 | 77.20 |
| 24 | 1607.4 | 200.9 | 0.93 | 0 | 96.07 |
| 32 | 1384.0 | 173.0 | 0.97 | 7 | 101.79 |
| 48 | 1298.5 | 162.3 | 0.97 | 23 | 100.00 |

At batch 24 the KV pool is nearly full but stable. At 32 and 48 it is pinned
at 0.97, sequences are preempted, TTFT rises from 500.5 ms (batch 24) to
636.9/955.4 ms, and even the inflated reported throughput falls. This is a
KV-capacity admission failure, not a lack of compute saturation.

**Change.** Put near-4K-context requests in a length-aware admission pool with
at most 24 admitted sequences; queue excess requests explicitly. Do not apply
the same cap to short requests - their batch-64 row has only 0.47 KV use. The
test predicts admitted long requests regain the batch-24 output goodput of
200.9 tok/s: +16.1% versus the batch-32 row (173.0) and +23.8% versus batch 48
(162.3). Their internal TTFT should return toward the observed 500.5 ms, while
any unavoidable wait is visible as queue time rather than hidden scheduler
preemption.

## B3. Reported tok/s is not output goodput

The harness's `reported_tok_s` divides **prompt + generated** tokens by wall
time. It is therefore dominated by the 3,584-token prompt in the long sweep.
For batch 24, the honest generated-token goodput is 200.9 tok/s, independently
derived in two ways:

```text
(24 requests × 512 generated tokens) / 61.16 s = 200.916 tok/s

1,607.4 reported tok/s × 512 / (3,584 + 512) = 200.925 tok/s
```

The tiny difference is rounding in `reported_tok_s`. Longer prompts do not
therefore “give better throughput” in the capacity sense. At batch 16, short
requests deliver 294.5 generated tok/s while long requests deliver 163.9. Nor
will batch 48 deliver 3,200 tok/s: it produces 162.3 generated tok/s and
preempts 23 sequences. The report should distinguish prefill-inclusive
throughput from generated-token goodput, show latency, and size long-context
admission against KV capacity.

## B4. Confirmation metric

Pull the serving scheduler's cumulative **sequence-preemption counter** (for
vLLM, `vllm:num_preemptions_total`; in this log, `preempted_seqs`). Under the
KV-exhaustion explanation it should remain zero at or below the 24-sequence
long-context cap and rise abruptly when 4,096-token reservations exceed the KV
budget. That thresholded change is more diagnostic than GPU utilization,
because the latter can be high for healthy work as well.
