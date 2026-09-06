#!/usr/bin/env python3
"""Reproduce the tokenizer audit and write machine-readable evidence tables."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

import regex
import sentencepiece as spm
import tiktoken


PART_A = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PART_A.parent
WORKSPACE_ROOT = REPOSITORY_ROOT.parent
LANGUAGES = ("eng_Latn", "hin_Deva", "kan_Knda", "tam_Taml", "tel_Telu")
XLMR_SPM_URL = "https://huggingface.co/FacebookAI/xlm-roberta-base/resolve/main/sentencepiece.bpe.model"
XLMR_SPM_PATH = PART_A / "data" / "tokenizers" / "xlm-roberta-base" / "sentencepiece.bpe.model"


@dataclass(frozen=True)
class Tokenizer:
    name: str
    encode: Callable[[str], list[int]]


def load_tokenizers() -> list[Tokenizer]:
    gpt2 = tiktoken.get_encoding("gpt2")
    if not XLMR_SPM_PATH.exists():
        XLMR_SPM_PATH.parent.mkdir(parents=True, exist_ok=True)
        request = Request(XLMR_SPM_URL, headers={"User-Agent": "tokenizer-audit/1.0"})
        with urlopen(request) as response, XLMR_SPM_PATH.open("wb") as destination:
            destination.write(response.read())
    if XLMR_SPM_PATH.stat().st_size < 100_000:
        raise ValueError(f"Unexpectedly small XLM-R SentencePiece model: {XLMR_SPM_PATH}")
    xlm_r = spm.SentencePieceProcessor(model_file=str(XLMR_SPM_PATH))
    return [
        Tokenizer("gpt2", gpt2.encode),
        # XLM-R adds <s> and </s> at the wrapper level.  Calling the official
        # SentencePiece model directly counts only the input text, matching
        # GPT-2's body-token convention.
        Tokenizer("xlm-roberta-base", lambda text: xlm_r.encode(text, out_type=int)),
    ]


def read_lines(path: Path) -> list[str]:
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def graphemes(text: str) -> int:
    return len(regex.findall(r"\X", text))


def summary(lines: list[str], encode: Callable[[str], list[int]]) -> dict[str, float | int]:
    """Aggregate totals are appropriate for a workload of all corpus requests."""
    token_counts = [len(encode(line)) for line in lines]
    word_counts = [len(line.split()) for line in lines]
    grapheme_counts = [graphemes(line) for line in lines]
    byte_counts = [len(line.encode("utf-8")) for line in lines]
    if not all(word_counts) or not all(grapheme_counts) or not all(byte_counts):
        raise ValueError("Found a sentence with a zero denominator")
    total_tokens = sum(token_counts)
    return {
        "sentences": len(lines),
        "total_tokens": total_tokens,
        "total_whitespace_words": sum(word_counts),
        "total_grapheme_clusters": sum(grapheme_counts),
        "total_utf8_bytes": sum(byte_counts),
        "tokens_per_whitespace_word": total_tokens / sum(word_counts),
        "tokens_per_grapheme_cluster": total_tokens / sum(grapheme_counts),
        "tokens_per_utf8_byte": total_tokens / sum(byte_counts),
        "tokens_per_parallel_sentence": total_tokens / len(lines),
        "mean_line_tokens_per_word": statistics.mean(t / w for t, w in zip(token_counts, word_counts)),
    }


def line_fertility(lines: list[str], encode: Callable[[str], list[int]], *, lowercase: bool, literal_space: bool) -> dict[str, float | int]:
    """Exact intern-style variants, used only to isolate individual effects."""
    prepared = [unicodedata.normalize("NFC", line).lower() if lowercase else unicodedata.normalize("NFC", line) for line in lines]
    words = [line.split(" ") if literal_space else line.split() for line in prepared]
    tokens = [len(encode(line)) for line in prepared]
    return {
        "tokens": sum(tokens),
        "words": sum(len(group) for group in words),
        "mean_line_tokens_per_word": statistics.mean(count / len(group) for count, group in zip(tokens, words)),
        "aggregate_tokens_per_word": sum(tokens) / sum(len(group) for group in words),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-dir", type=Path, default=PART_A / "data" / "flores200_devtest")
    parser.add_argument("--results-dir", type=Path, default=PART_A / "results")
    args = parser.parse_args()
    corpus_dir, results_dir = args.corpus_dir.resolve(), args.results_dir.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)

    lines_by_language = {language: read_lines(corpus_dir / f"{language}.txt") for language in LANGUAGES}
    counts = {language: len(lines) for language, lines in lines_by_language.items()}
    if set(counts.values()) != {1012}:
        raise ValueError(f"Expected 1,012 aligned rows per language, got {counts}")

    tokenizers = load_tokenizers()
    metric_rows: list[dict[str, object]] = []
    ratio_rows: list[dict[str, object]] = []
    all_metrics: dict[tuple[str, str], dict[str, float | int]] = {}
    for tokenizer in tokenizers:
        for language in LANGUAGES:
            metrics = summary(lines_by_language[language], tokenizer.encode)
            all_metrics[(tokenizer.name, language)] = metrics
            metric_rows.append({"tokenizer": tokenizer.name, "language": language, **metrics})
        english = all_metrics[(tokenizer.name, "eng_Latn")]
        for language in LANGUAGES:
            current = all_metrics[(tokenizer.name, language)]
            ratio_rows.append(
                {
                    "tokenizer": tokenizer.name,
                    "language": language,
                    "sentence_cost_vs_english": current["tokens_per_parallel_sentence"] / english["tokens_per_parallel_sentence"],
                    "word_metric_vs_english": current["tokens_per_whitespace_word"] / english["tokens_per_whitespace_word"],
                    "grapheme_metric_vs_english": current["tokens_per_grapheme_cluster"] / english["tokens_per_grapheme_cluster"],
                    "byte_metric_vs_english": current["tokens_per_utf8_byte"] / english["tokens_per_utf8_byte"],
                }
            )
    write_csv(results_dir / "corrected_metrics.csv", metric_rows)
    write_csv(results_dir / "cross_language_ratios.csv", ratio_rows)

    # Evidence for the original code's three separable choices.  GPT-2 is used
    # here because it is the tokenizer in REPORT_v0.md.
    gpt2 = next(tokenizer for tokenizer in tokenizers if tokenizer.name == "gpt2")
    corpora = {
        "provided_smoke_sample": {
            "eng_Latn": read_lines(WORKSPACE_ROOT / "starter_kit" / "corpus_sample" / "eng_sample.txt"),
            "hin_Deva": read_lines(WORKSPACE_ROOT / "starter_kit" / "corpus_sample" / "hin_sample.txt"),
        },
        "flores200_devtest": lines_by_language,
    }
    variants = (
        ("intern_exact", True, True),
        ("whitespace_split_fixed", True, False),
        ("case_preserved_literal_space", False, True),
        ("case_and_whitespace_fixed", False, False),
    )
    audit_rows: list[dict[str, object]] = []
    for corpus, languages in corpora.items():
        for language, lines in languages.items():
            for variant, lowercase, literal_space in variants:
                audit_rows.append(
                    {
                        "corpus": corpus,
                        "language": language,
                        "variant": variant,
                        "lowercase": lowercase,
                        "literal_space_split": literal_space,
                        **line_fertility(lines, gpt2.encode, lowercase=lowercase, literal_space=literal_space),
                    }
                )
    write_csv(results_dir / "audit_variants_gpt2.csv", audit_rows)

    # NFC is intentional preprocessing: canonical equivalents should tokenize
    # the same after normalization, rather than depend on their code-point form.
    composed = "café"
    decomposed = unicodedata.normalize("NFD", composed)
    normalization_rows = []
    for form, text in (("NFC", composed), ("NFD", decomposed)):
        normalization_rows.append(
            {
                "input_form": form,
                "unicode_codepoints": " ".join(f"U+{ord(char):04X}" for char in text),
                "raw_gpt2_tokens": len(gpt2.encode(text)),
                "after_nfc_gpt2_tokens": len(gpt2.encode(unicodedata.normalize("NFC", text))),
            }
        )
    write_csv(results_dir / "normalization_probe.csv", normalization_rows)

    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "tiktoken": tiktoken.__version__,
        "sentencepiece": spm.__version__,
        "gpt2_counting": "tiktoken.get_encoding('gpt2').encode(text)",
        "xlm_roberta_counting": "SentencePieceProcessor(sentencepiece.bpe.model).encode(text, out_type=int)",
        "special_tokens_counted": False,
    }
    (results_dir / "environment.json").write_text(json.dumps(environment, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote results to {results_dir}")


if __name__ == "__main__":
    main()
