# Passive GPU sampling. Read-only: it queries nvidia-smi and writes a CSV.
# It never changes clocks, power limits, voltages, or running processes.
param(
    [int]$IntervalSeconds = 1,
    [int]$Samples = 300,
    [string]$OutFile = 'gpu-samples.csv'
)

$smi = Join-Path $env:SystemRoot 'System32\nvidia-smi.exe'
if (-not (Test-Path -LiteralPath $smi)) { throw 'nvidia-smi not found at ' + $smi }
$query = 'timestamp,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,clocks.sm,power.limit'
if (-not (Test-Path -LiteralPath $OutFile)) {
    'at_utc,util_pct,vram_used_gb,vram_total_gb,temp_c,power_w,clocks_sm_mhz,power_limit_w' | Out-File -LiteralPath $OutFile -Encoding utf8
}
for ($i = 0; $i -lt $Samples; $i++) {
    $line = (& $smi --query-gpu=$query --format=csv,noheader,nounits).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'nvidia-smi failed with exit code ' + $LASTEXITCODE }
    $f = $line.Split(',')
    $row = @((
        [DateTime]::UtcNow.ToString('o'),
        [double]$f[1],
        [Math]::Round([double]$f[2] / 1024, 2),
        [Math]::Round([double]$f[3] / 1024, 2),
        [double]$f[4],
        [double]$f[5],
        [double]$f[6],
        [double]$f[7]
    )) -join ','
    $row | Out-File -LiteralPath $OutFile -Encoding utf8 -Append
    if ($i -lt $Samples - 1) { Start-Sleep -Seconds $IntervalSeconds }
}
Write-Host ('Wrote ' + $Samples + ' samples to ' + $OutFile)
