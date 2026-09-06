[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Python,

    [string]$FloresArchive
)

$ErrorActionPreference = 'Stop'

function Invoke-PythonStep {
    param([string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python step failed with exit code ${LASTEXITCODE}: $($Arguments -join ' ')"
    }
}

$submission = $PSScriptRoot
$prepare = Join-Path $submission 'partA\scripts\prepare_flores.py'
$analysis = Join-Path $submission 'partA\scripts\run_analysis.py'
$bench = Join-Path $submission 'partB\analyze_bench.py'
$tests = Join-Path $submission 'partA\tests'

Write-Host '1/4 Preparing the FLORES corpus'
$prepareArgs = @($prepare)
if ($FloresArchive) {
    $prepareArgs += @('--archive', $FloresArchive)
}
Invoke-PythonStep $prepareArgs

Write-Host '2/4 Running tokenizer analysis'
Invoke-PythonStep @($analysis)

Write-Host '3/4 Reconciling serving benchmarks'
Invoke-PythonStep @($bench)

Write-Host '4/4 Running targeted tests'
Invoke-PythonStep @('-m', 'unittest', 'discover', '-s', $tests, '-v')

Write-Host 'All reproducibility checks passed.'
