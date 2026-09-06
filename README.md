# AI Team Intern Assignment - Evidence-Driven Audit

This repository audits the tokenizer and serving conclusions in the provided
starter kit. The deliverable lives in [`your-submission/`](your-submission/)
and is intentionally structured as a small reproducible research repository:
data provenance, code, generated results, decision memos, a chronological
lab notebook, and an honest AI-use disclosure are kept separate.

## Start here

1. Read [`your-submission/README.md`](your-submission/README.md) for setup and
   reproducibility.
2. Read [`your-submission/partA/memo.md`](your-submission/partA/memo.md),
   [`your-submission/partB/calculations.md`](your-submission/partB/calculations.md),
   and [`your-submission/partC/memo.md`](your-submission/partC/memo.md) for
   the decisions.
3. Read [`your-submission/NOTEBOOK.md`](your-submission/NOTEBOOK.md) for the
   hypothesis-to-revision record.

## Reproduce

After creating a Python 3.12+ virtual environment and installing
`your-submission/requirements.txt`, run:

```powershell
.\your-submission\run_all.ps1 -Python .\.venv\Scripts\python.exe -FloresArchive .\tmp\flores\flores200_dataset.tar.gz
```

Omit `-FloresArchive` only when network access to Meta's official FLORES-200
archive is available. The runner stops on any failed step and succeeds only
after corpus preparation, tokenizer analysis, serving reconciliation, and unit
tests finish.

## Repository layout

- `starter_kit/` - the supplied audit target, preserved unchanged.
- `your-submission/` - the complete submission and reproducible analysis.

See [`NOTICE.md`](NOTICE.md) for third-party dataset and tokenizer attribution.
