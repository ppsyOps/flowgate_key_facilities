<#
.SYNOPSIS
    Installs psse-utils (if needed) and runs filter-taralog-notcnv
    interactively, then opens the output folder.

.DESCRIPTION
    For non-technical end users: double-click (Run with PowerShell) or run
    from a shell. Prompts for the taralog.txt path and the .con file(s) or
    glob pattern to filter, ensures psse-utils is installed and current,
    runs filter-taralog-notcnv, then opens the output folder in Explorer.
#>

function Get-PythonCommand {
    foreach ($candidate in @(
        @{ Exe = 'python'; Args = @() },
        @{ Exe = 'py'; Args = @('-3') }
    )) {
        if (Get-Command $candidate.Exe -ErrorAction SilentlyContinue) {
            return $candidate
        }
    }
    return $null
}

function Read-PathPrompt {
    param(
        [string]$Prompt,
        [string]$Default
    )
    $suffix = if ($Default) { " [$Default]" } else { '' }
    $value = Read-Host "$Prompt$suffix"
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value.Trim('"')
}

try {
    $python = Get-PythonCommand
    if (-not $python) {
        Write-Host "Python was not found on PATH. Install Python 3.11+ and try again." -ForegroundColor Red
        exit 1
    }

    # --- Ensure psse-utils is installed and current ---
    & $python.Exe @($python.Args) -m pip show psse-utils *> $null
    $isInstalled = ($LASTEXITCODE -eq 0)
    if (-not $isInstalled) {
        Write-Host "Installing psse-utils..."
        & $python.Exe @($python.Args) -m pip install --pre --quiet psse-utils
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Install failed." -ForegroundColor Red
            exit 1
        }
    }
    else {
        $outdated = & $python.Exe @($python.Args) -m pip list --outdated --pre --format=json 2>$null |
            ConvertFrom-Json | Where-Object { $_.name -eq 'psse-utils' }
        if ($outdated) {
            Write-Host "Updating psse-utils..."
            & $python.Exe @($python.Args) -m pip install --pre --upgrade --quiet psse-utils
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Update failed." -ForegroundColor Red
                exit 1
            }
        }
    }

    # --- Prompt for inputs ---
    $taralog = Read-PathPrompt -Prompt "Path to taralog.txt"
    while (-not (Test-Path $taralog -PathType Leaf)) {
        Write-Host "File not found: $taralog" -ForegroundColor Yellow
        $taralog = Read-PathPrompt -Prompt "Path to taralog.txt"
    }
    $taralog = (Resolve-Path $taralog).Path

    $conPattern = Read-PathPrompt -Prompt "Path or glob pattern for .con file(s) (e.g. *.con)"
    while ([string]::IsNullOrWhiteSpace($conPattern)) {
        $conPattern = Read-PathPrompt -Prompt "Path or glob pattern for .con file(s) (e.g. *.con)"
    }

    $defaultOutDir = Join-Path (Split-Path $taralog -Parent) 'NotCnv_output'
    $outDir = Read-PathPrompt -Prompt "Output folder" -Default $defaultOutDir

    # --- Run ---
    Write-Host "Running filter-taralog-notcnv..."
    & $python.Exe @($python.Args) -m psse_utils.filter_taralog_notcnv `
        --taralog $taralog --con $conPattern --out-dir $outDir
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        if (Test-Path $outDir) {
            Start-Process explorer.exe $outDir
        }
        Write-Host "Done."
    }
    else {
        Write-Host "filter-taralog-notcnv exited with code $exitCode." -ForegroundColor Red
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Read-Host "Press Enter to exit..." | Out-Null
}
