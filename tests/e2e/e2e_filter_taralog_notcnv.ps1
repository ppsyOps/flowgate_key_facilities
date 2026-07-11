<#
.SYNOPSIS
    Portable end-to-end test for the filter-taralog-notcnv console command.

.DESCRIPTION
    Self-contained: uses only the synthetic fixtures checked into
    tests/data/ (no real system data, no external dependencies beyond the
    project's own venv). Installs the project in editable mode into the
    repo's .venv if not already present, runs the installed
    `filter-taralog-notcnv` console command against the fixtures into a
    throwaway temp directory, and asserts the expected output.

.EXAMPLE
    pwsh -File tests\e2e\e2e_filter_taralog_notcnv.ps1
    powershell -File tests\e2e\e2e_filter_taralog_notcnv.ps1
#>

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$DataDir = Join-Path $RepoRoot "tests\data"
$Venv = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$Exe = Join-Path $Venv "Scripts\filter-taralog-notcnv.exe"

Write-Host "== filter-taralog-notcnv e2e =="

if (-not (Test-Path $Exe)) {
    Write-Host "filter-taralog-notcnv console command not found -- installing the project into $Venv."
    Push-Location $RepoRoot
    try {
        if (Get-Command pdm -ErrorAction SilentlyContinue) {
            pdm install
        } elseif (Test-Path $VenvPython) {
            & $VenvPython -m pip install --pre -e $RepoRoot
        } else {
            python -m venv $Venv
            & $VenvPython -m pip install --pre -e $RepoRoot
        }
    } finally {
        Pop-Location
    }
}

if (-not (Test-Path $Exe)) {
    throw "filter-taralog-notcnv.exe not found at $Exe after install. Run 'pdm install' (or 'pip install --pre -e .') in $RepoRoot manually."
}

$OutDir = Join-Path ([System.IO.Path]::GetTempPath()) ("filter_taralog_notcnv_e2e_" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $OutDir | Out-Null

try {
    $taralog = Join-Path $DataDir "taralog_sample.txt"
    $conGlob = Join-Path $DataDir "sample_*.con"

    Write-Host "Running: filter-taralog-notcnv --taralog $taralog --con `"$conGlob`" --out-dir $OutDir"
    $outputLines = & $Exe --taralog $taralog --con $conGlob --out-dir $OutDir 2>&1
    $outputLines | ForEach-Object { Write-Host $_ }
    $output = ($outputLines | Out-String)

    if ($LASTEXITCODE -ne 0) {
        throw "filter-taralog-notcnv exited with code $LASTEXITCODE"
    }

    $outA = Join-Path $OutDir "sample_a-NotCnv.con"
    $outB = Join-Path $OutDir "sample_b-NotCnv.con"

    if (-not (Test-Path $outA)) { throw "Missing expected output: $outA" }
    if (-not (Test-Path $outB)) { throw "Missing expected output: $outB" }

    $textA = Get-Content $outA -Raw
    $textB = Get-Content $outB -Raw

    $checks = @(
        @{ Text = $textA; Pattern = "FAKE LINE ALPHA 138_SRT-A"; File = "sample_a-NotCnv.con" }
        @{ Text = $textA; Pattern = "FAKE LINE GAMMA 500_SRT-A"; File = "sample_a-NotCnv.con" }
        @{ Text = $textA; Pattern = "FAKE UNIT DELTA 1_SRT-A"; File = "sample_a-NotCnv.con" }
        @{ Text = $textB; Pattern = "FAKE UNIT ECHO 2_SRT-A"; File = "sample_b-NotCnv.con" }
    )
    foreach ($c in $checks) {
        if ($c.Text -notmatch [regex]::Escape($c.Pattern)) {
            throw "Expected '$($c.Pattern)' in $($c.File) but it was not found."
        }
    }
    if ($textA -match [regex]::Escape("FAKE LINE BETA 138_SRT-A")) {
        throw "sample_a-NotCnv.con should NOT contain the non-NotCnv 'FAKE LINE BETA' block."
    }
    if ($output -notmatch "kept=3, skipped=1") {
        throw "Expected 'kept=3, skipped=1' in stdout for sample_a.con, got:`n$output"
    }
    if ($output -notmatch "kept=2, skipped=1") {
        throw "Expected 'kept=2, skipped=1' in stdout for sample_b.con, got:`n$output"
    }

    Write-Host "PASS: filter-taralog-notcnv e2e"
    exit 0
}
finally {
    Remove-Item -Recurse -Force $OutDir -ErrorAction SilentlyContinue
}
