# Compiles and runs the LTspice simulation, prints a clean results
# table, then runs a real regression check (dark = off, bright = on).
# Requires LTspice (free, Windows/macOS): winget install --id=AnalogDevices.LTspice -e
#
# Usage:
#   powershell -File sim/run.ps1             # run + print results table
#   powershell -File sim/run.ps1 -Check      # same, plus exit non-zero on regression failure

param([switch]$Check)

$ErrorActionPreference = "Stop"
$simDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$cir = Join-Path $simDir "light_alarm.cir"

$candidates = @(
    "$env:LOCALAPPDATA\Programs\ADI\LTspice\LTspice.exe",
    "C:\Program Files\ADI\LTspice\LTspice.exe",
    "C:\Program Files (x86)\ADI\LTspice\LTspice.exe"
)
$exe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
    $found = Get-Command LTspice.exe -ErrorAction SilentlyContinue
    if ($found) { $exe = $found.Source }
}
if (-not $exe) {
    Write-Error "LTspice.exe not found. Install it with: winget install --id=AnalogDevices.LTspice -e"
    exit 1
}

Write-Output "Using LTspice: $exe"
$proc = Start-Process -FilePath $exe -ArgumentList "-b", "-ascii", "`"$cir`"" -PassThru -Wait
if ($proc.ExitCode -ne 0) {
    Write-Error "LTspice exited with code $($proc.ExitCode)"
    exit $proc.ExitCode
}

$raw = Join-Path $simDir "light_alarm.raw"
python (Join-Path $simDir "parse_results.py") $raw

if ($Check) {
    Write-Output ""
    python (Join-Path $simDir "check_regression.py") $raw
    exit $LASTEXITCODE
}
