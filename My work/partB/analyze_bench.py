#!/usr/bin/env python3
"""Derive KV capacity and honest output goodput from the provided benchmark."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


PART_B = Path(__file__).resolve().parent
WORKSPACE_ROOT = PART_B.parents[1]
BENCHMARK = WORKSPACE_ROOT / "starter_kit" / "bench" / "bench_log.csv"

# Values transcribed directly from bench/model_spec.md.  Units are decimal GB,
# matching the specification's 24 GB and 1.6 GB figures.
LAYERS = 28
KV_HEADS = 8
HEAD_DIM = 128
BYTES_PER_ELEMENT = 2  # fp16
GPU_MEMORY_GB = 24.0
GPU_MEMORY_UTILIZATION = 0.92
MODEL_PARAMETERS = 4.2e9
NON_KV_OVERHEAD_GB = 1.6
MAX_MODEL_LEN = 4096


def main() -> None:
    kv_bytes_per_token = LAYERS * KV_HEADS * HEAD_DIM * BYTES_PER_ELEMENT * 2  # K and V
    managed_memory_bytes = GPU_MEMORY_GB * 1e9 * GPU_MEMORY_UTILIZATION
    weight_bytes = MODEL_PARAMETERS * BYTES_PER_ELEMENT
    non_kv_bytes = NON_KV_OVERHEAD_GB * 1e9
    kv_budget_bytes = managed_memory_bytes - weight_bytes - non_kv_bytes
    max_kv_tokens = kv_budget_bytes / kv_bytes_per_token
    max_4096_sequences = math.floor(max_kv_tokens / MAX_MODEL_LEN)

    capacity = {
        "kv_bytes_per_token": kv_bytes_per_token,
        "kv_kib_per_token": kv_bytes_per_token / 1024,
        "managed_memory_bytes": managed_memory_bytes,
        "weight_bytes": weight_bytes,
        "non_kv_overhead_bytes": non_kv_bytes,
        "kv_budget_bytes": kv_budget_bytes,
        "max_kv_tokens": max_kv_tokens,
        "max_4096_token_sequences_floor": max_4096_sequences,
        "calculation": "28 layers * 8 KV heads * 128 head dim * 2 bytes * 2 (K,V)",
    }

    reconciled = []
    with BENCHMARK.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            batch = int(row["batch_size"])
            prompt = int(row["prompt_len"])
            generated = int(row["gen_len"])
            requests = int(row["num_requests"])
            seconds = float(row["wall_clock_s"])
            reported = float(row["reported_tok_s"])
            total_work = requests * (prompt + generated)
            output_work = requests * generated
            reconciled.append(
                {
                    **row,
                    "total_prompt_plus_output_tokens": total_work,
                    "output_tokens": output_work,
                    "recomputed_reported_tok_s": total_work / seconds,
                    "output_goodput_tok_s": output_work / seconds,
                    "goodput_from_reported_tok_s": reported * generated / (prompt + generated),
                }
            )

    with (PART_B / "bench_reconciliation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(reconciled[0]))
        writer.writeheader()
        writer.writerows(reconciled)
    (PART_B / "capacity_results.json").write_text(json.dumps(capacity, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(capacity, indent=2))
    print(f"Wrote {PART_B / 'bench_reconciliation.csv'}")


if __name__ == "__main__":
    main()
