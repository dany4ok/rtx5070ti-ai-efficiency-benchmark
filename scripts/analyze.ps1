# Recompute efficiency metrics from a request log plus GPU power samples. Read-only.
param(
    [string]$RequestsCsv,
    [string]$SamplesCsv,
    [double]$IdlePowerW = 0
)
$r = Import-Csv -LiteralPath $RequestsCsv
$s = Import-Csv -LiteralPath $SamplesCsv
$done = @($r | Where-Object { $_.state -eq 'done' })
if ($done.Count -eq 0) { throw 'No completed requests in ' + $RequestsCsv }
$out = [double]($done | ForEach-Object { [double]$_.tokensOut } | Measure-Object -Sum).Sum
$inp = [double]($done | ForEach-Object { [double]$_.tokensIn } | Measure-Object -Sum).Sum
$active = [double]($done | ForEach-Object { [double]$_.duration_s } | Measure-Object -Sum).Sum
$tps = @($done | ForEach-Object { [double]$_.out_tok_s } | Sort-Object)
$mean = ($s | ForEach-Object { [double]$_.powerW } | Measure-Object -Average).Average
$stamp = @($r | ForEach-Object { [DateTime]$_.at } | Sort-Object)
$window = ($stamp[-1] - $stamp[0]).TotalSeconds
$energy = $mean * $active
function Percentile($list, $p) {
    $i = [int]([Math]::Ceiling($p * $list.Count) - 1)
    if ($i -lt 0) { $i = 0 }
    if ($i -ge $list.Count) { $i = $list.Count - 1 }
    return $list[$i]
}
'requests=' + $done.Count
'output_tokens=' + $out
'prompt_tokens=' + $inp
'window_s=' + [Math]::Round($window, 1)
'active_s=' + [Math]::Round($active, 1)
'out_tok_s_active=' + [Math]::Round($out / $active, 2)
'out_tok_s_window=' + [Math]::Round($out / $window, 2)
'out_tok_s_p50=' + (Percentile $tps 0.5) + ' p95=' + (Percentile $tps 0.95) + ' min=' + $tps[0] + ' max=' + $tps[-1]
'mean_gpu_power_w=' + [Math]::Round($mean, 1)
'active_energy_j=' + [Math]::Round($energy, 0)
'tokens_per_joule_active=' + [Math]::Round($out / $energy, 4)
'joules_per_token_active=' + [Math]::Round($energy / $out, 2)
if ($IdlePowerW -gt 0) { 'idle_power_w=' + $IdlePowerW }
'voltage=N/A queue_wait=N/A cache_reuse=N/A'
