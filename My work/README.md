# Tokenizer and Serving Audit

This repository is a reproducible audit of the starter kit. It deliberately
separates source data, calculations, generated results, and recommendations so
that every numerical statement can be re-derived during a live defense.

The company-supplied `starter_kit/` is deliberately local-only. Before running
the complete audit, place the original supplied folder beside `My work/`; it is
excluded from GitHub to avoid publishing company material.

## Quick start

From the directory containing this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r '.\My work\requirements.txt'
.\.venv\Scripts\python.exe '.\My work\partA\scripts\prepare_flores.py' --archive tmp\flores\flores200_dataset.tar.gz
.\.venv\Scripts\python.exe '.\My work\partA\scripts\run_analysis.py'
.\.venv\Scripts\python.exe '.\My work\partB\analyze_bench.py'
.\.venv\Scripts\python.exe -m unittest discover -s '.\My work\partA\tests' -v
```

Use a Python 3.12+ executable and retain the local `starter_kit/` folder
alongside `My work/`. If `--archive` is omitted,
`prepare_flores.py` downloads the official FLORES-200
archive from the source recorded in its manifest. The prepared corpus is the
complete 1,012-sentence `devtest` split for English, Hindi, Kannada, and Tamil.
It contains translations aligned by line number.

## Layout

- `NOTEBOOK.md` is the chronological lab record, including the correction of
  an initial denominator choice.
- `partA/` contains corpus preparation, tokenizer analysis, audit evidence,
  results, and the routing memo.
- `partB/` contains a script that derives the capacity and goodput results
  directly from the supplied model specification and benchmark CSV.
- `partC/memo.md` is the three-week product decision memo.
- `AI_USAGE.md` describes the use and limitations of AI assistance.

## Reproducibility boundaries

The two tokenizer assets are public model/tokenizer files fetched on first
run: OpenAI's `gpt2` encoding via `tiktoken`, and XLM-R's official
SentencePiece model from `FacebookAI/xlm-roberta-base`. Counts exclude model
special tokens for both tokenizers. The exact local package versions are
pinned above.

No result is inferred from a chart or rounded before calculation. The FLORES
tables are generated from checked-in scripts; the audit and benchmark
reconciliation additionally require the local company-supplied inputs.

## Single-command verification

After installing the requirements, the same sequence can be run from PowerShell:

```powershell
& '.\My work\run_all.ps1' -Python .\.venv\Scripts\python.exe -FloresArchive .\tmp\flores\flores200_dataset.tar.gz
```

Omit `-FloresArchive` only when network access to the official FLORES archive
is available. The runner stops on the first failed command and reports success
only after both analyses and the unit tests finish.
