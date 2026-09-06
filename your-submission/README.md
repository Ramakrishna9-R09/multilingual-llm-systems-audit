# Tokenizer and Serving Audit

This repository is a reproducible audit of the starter kit. It deliberately
separates source data, calculations, generated results, and recommendations so
that every numerical statement can be re-derived during a live defense.

## Quick start

From the directory containing this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r your-submission\requirements.txt
.\.venv\Scripts\python.exe your-submission\partA\scripts\prepare_flores.py --archive tmp\flores\flores200_dataset.tar.gz
.\.venv\Scripts\python.exe your-submission\partA\scripts\run_analysis.py
.\.venv\Scripts\python.exe your-submission\partB\analyze_bench.py
.\.venv\Scripts\python.exe -m unittest discover -s your-submission\partA\tests -v
```

Use a Python 3.12+ executable. If `--archive` is omitted,
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

No result is inferred from a chart or rounded before calculation; all tables
are generated from the checked-in scripts.

## Single-command verification

After installing the requirements, the same sequence can be run from PowerShell:

```powershell
.\your-submission\run_all.ps1 -Python .\.venv\Scripts\python.exe -FloresArchive .\tmp\flores\flores200_dataset.tar.gz
```

Omit `-FloresArchive` only when network access to the official FLORES archive
is available. The runner stops on the first failed command and reports success
only after both analyses and the unit tests finish.
