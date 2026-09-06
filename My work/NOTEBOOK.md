# Chronological lab notebook

This is a contemporaneous record of hypotheses, commands, results, and
revisions. Numbers below point to generated files rather than being copied from
an untracked notebook cell.

## 2026-09-06 - Scope and first inspection

**Hypothesis.** The starter report's two sections can be audited from the
provided code and CSV, but the 10-line corpora cannot support language-routing
claims.

**Inspection command.**

```powershell
rg --files -g '!node_modules' -g '!dist'
Get-Content -Raw starter_kit\REPORT_v0.md
Get-Content -Raw starter_kit\fertility.py
Get-Content -Raw starter_kit\bench\model_spec.md
Get-Content -Raw starter_kit\bench\bench_log.csv
```

**Result.** The sample has 10 English and 10 Hindi lines, including repeated
spaces. The report's numbers match the intern script's default behavior; this
is a reproducibility lead, not evidence that its recommendation is valid.

## 2026-09-06 - Corpus selection

**Hypothesis.** A parallel test set lets one compare the tokens used to express
the same message in each language.

**Dead end.** The Hugging Face `facebook/flores` mirror returned HTTP 401
because it is gated in this environment. I did not use an unverified mirror.

**Revision and command.** The FLORES documentation links Meta's public archive.
I downloaded that archive and prepared exactly the five complete devtest files:

```powershell
curl.exe -L --fail --silent --show-error -o tmp\flores\flores200_dataset.tar.gz https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz
.\.audit-venv\Scripts\python.exe '.\My work\partA\scripts\prepare_flores.py' --archive tmp\flores\flores200_dataset.tar.gz
```

**Result.** English, Hindi, Kannada, Tamil, and Telugu each have 1,012 aligned lines.
Leading/trailing Unicode whitespace is removed as file-boundary noise; interior
whitespace remains unchanged. The archive SHA-256 is
`b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6`;
see `partA/data/flores200_devtest/manifest.json`.

## 2026-09-06 - Script audit experiments

**Hypothesis.** `split(" ")` is a harmless spelling of `split()`.

**Experiment.** Run exact-intern and whitespace-only-fixed variants on the
provided sample and FLORES, holding the GPT-2 tokenizer and casing fixed:

```powershell
.\.audit-venv\Scripts\python.exe '.\My work\partA\scripts\run_analysis.py'
```

**Result and revision.** It is not harmless. English sample mean fertility goes
from 1.2652 to 1.2831 (+1.41%), and Hindi from 7.4485 to 7.5985 (+2.01%). The
double spaces had become empty words. I changed the corrected definition to
Unicode-whitespace `split()`.

**Hypothesis.** Lowercasing merely removes English casing noise.

**Experiment.** Compare `intern_exact` and `case_preserved_literal_space` on
the same FLORES English lines in `partA/results/audit_variants_gpt2.csv`.

**Result and revision.** Lowercasing changes GPT-2's English token total from
27,044 to 27,994 (+3.51%). It is input mutation, not neutral preprocessing; I
preserve case for the deployment estimate.

**Hypothesis.** Tokens per whitespace word should be the routing headline.

**Experiment.** Compare all denominators and their English ratios in
`partA/results/cross_language_ratios.csv`.

**Result and revision.** The denominator changes the claim. For GPT-2, Hindi
is 6.34× English per whitespace word but 7.42× per matched sentence. A word is
not a fixed semantic unit across these languages. I discarded the word metric
as the headline and use aggregate tokens per parallel sentence instead.

**Check of suspicious code.** The NFC probe gives `café` 3 GPT-2 tokens in NFC
and 4 in raw NFD, but 3 for both after NFC. Normalization stays.

## 2026-09-06 - Corpus-boundary whitespace hygiene

**Hypothesis.** Leading/trailing spaces in source sentence files are harmless
because the corrected analysis uses aggregate counts.

**Experiment.** Count leading/trailing whitespace and body tokens before and
after stripping only sentence boundaries. Kannada has 13 leading and 73
trailing boundary-space rows: GPT-2 falls from 367,465 to 367,366 tokens
(-99), while XLM-R does not change. Hindi falls from 200,704 to 200,688
(-16); English and Tamil do not change.

**Revision.** Boundary spaces are serialization artifacts and were affecting
GPT-2 unequally. Corpus preparation now applies `strip()` before NFC
normalization, documents the choice, and preserves interior whitespace. I
reran every generated result after this change.

## 2026-09-06 - Capacity reconciliation

**Hypothesis.** The high long-context `reported_tok_s` measures output
generation speed and should scale linearly with batch.

**Experiment.**

```powershell
.\.audit-venv\Scripts\python.exe '.\My work\partB\analyze_bench.py'
```

**Result and revision.** For batch 24, `reported_tok_s` is exactly
(prompt + output) tokens / wall time. Actual output goodput is
24 × 512 / 61.16 = 200.916 tok/s, not 1,607.4. At batch 32, KV utilization
pins at 0.97 and seven sequences are preempted; throughput falls. The
recommendation became length-aware admission control at 24 long requests,
not “pack more context.”

## 2026-09-06 - Verification

```powershell
.\.audit-venv\Scripts\python.exe -m unittest discover -s '.\My work\partA\tests' -v
```

**Result.** All three targeted tests passed: Unicode whitespace no longer makes
empty words, grapheme counting keeps a combining sequence together, and the
prepared corpus has no boundary whitespace.
