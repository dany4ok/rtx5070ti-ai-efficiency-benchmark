# Restore SM clocks to driver defaults after a clock cap was applied by the user.
# Nothing in this repository applies a cap. Run this script yourself, elevated.
param([string]$GpuIndex = '0')
$smi = Join-Path $env:SystemRoot 'System32\nvidia-smi.exe'
if (-not (Test-Path -LiteralPath $smi)) { throw 'nvidia-smi not found at ' + $smi }
Write-Host ('Resetting SM clock limits on GPU index ' + $GpuIndex + ' (needs an elevated shell).')
& $smi -rgc -i $GpuIndex
if ($LASTEXITCODE -ne 0) { throw 'nvidia-smi -rgc failed with exit code ' + $LASTEXITCODE }
& $smi --query-gpu=clocks.sm,clocks.max.sm,power.limit --format=csv,noheader
Write-Host 'Clock limits reset. Confirm clocks.max.sm returned to the stock ceiling.'
