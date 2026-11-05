# RTX 5070 Ti — AI GPU Efficiency Benchmark

Measures how much AI output an NVIDIA GPU produces per unit of energy, using only real inference traffic. No synthetic prompts, no extra requests, no GPU setting changes.

**Primary metric:** `tokens/J = generated output tokens / GPU energy consumed during the measured workload`.

## Verified measurement — real traffic, stock settings

One measurement window on 2026-11-05 (Europe/Bucharest). Model `coder-iq1_m`, engine: local Strata host with the model resident. GPU: NVIDIA GeForce RTX 5070 Ti, driver 621.01, power limit 252 W (driver hard minimum 250 W, maximum 300 W), SM clocks at 2880 MHz against a 3090 MHz ceiling, no cap applied.

| Metric | Value |
| --- | --- |
| Real inference requests | 60 |
| Observation window | 1652.5 s |
| Active inference | 1521.7 s (92% of the window) |
| Output tokens | 45,419 |
| Prompt tokens | 3,815,668 |
| Output tok/s during active inference | 29.85 |
| Output tok/s over the whole window | 27.48 |
| Per-request output rate | P50 56.4, P95 67.9, min 37.2, max 75.2 |
| Mean GPU power during inference | 185.1 W |
| GPU utilization | 89-100% |
| Idle GPU power | 98.3 W |
| VRAM | 14.52 / 15.90 GB (as reported by the monitor) |
| GPU temperature | 53.9 C |
| Energy during active inference | 281,675 J |
| **Tokens/J (active inference)** | **0.1612** (6.20 J/token) |
| Whole session since engine start | 2,480,116 J (688.9 Wh) -> 0.0183 tokens/J (54.6 J/token) |
| GPU voltage | N/A (not reported by the driver) |
| Queue waiting | N/A |
| Cache reuse / context reprocessing | N/A |
| Per-request GPU power | N/A (only aggregate sampling was available) |

Active-inference efficiency counts only the seconds where the GPU was generating tokens. Whole-session efficiency also includes idle and waiting time, which is why the two figures differ by about 9x. Every number above recomputes from the shipped files: [`data/real-traffic-requests.csv`](data/real-traffic-requests.csv) and [`data/gpu-samples.csv`](data/gpu-samples.csv).

## Configurations compared

| Configuration | Real-traffic tokens/J | Real-traffic tok/s | Status |
| --- | --- | --- | --- |
| Stock: 252 W limit, no clock cap | 0.1612 | 29.85 | measured |
| 250 W power limit | N/A | N/A | applied and restored; no real traffic recorded. Also unusable: driver minimum is 250 W |
| Clock cap 2000 MHz | N/A | N/A | applied and restored; no real traffic recorded |
| Clock cap 2200 MHz | N/A | N/A | applied and restored; no real traffic recorded |
| Undervolt | N/A | N/A | not measurable with the NVIDIA driver |

Three earlier single-run probes (stock 118.1 W / 63.9 tok/s / 0.1094 tokens/J; 2000 MHz 91.3 W / 72.9 tok/s / 0.1078; 2200 MHz 106.6 W / 91.8 tok/s / 0.1217) are excluded from ranking: prompts were about 50x shorter than real chat traffic, concurrency differed, and the values are mutually inconsistent. They are listed for transparency only.

**Winners across configurations: N/A.** Only the stock configuration has comparable real-traffic data.

## Recommended change (not applied)

- Parameter: SM clock ceiling (`nvidia-smi -lgc`)
- Current value: 3090 MHz ceiling, no cap applied
- Proposed value: 2200 MHz ceiling
- Expected change in tokens/J: N/A (no comparable real-traffic measurement at that cap)
- Expected change in tokens/sec: N/A
- Evidence: a power limit below 250 W is refused by the driver, and voltage cannot be read, so the SM clock ceiling is the only usable lever
- Confidence: Low
- Missing measurement: about 30 minutes of real chat traffic at 2200 MHz, compared with the 25.4 minutes of stock traffic already logged, then restore stock settings. Applying a cap needs an elevated Windows prompt; nothing here was applied automatically.

## Community leaderboard

Ranked by tokens/J inside each comparable group: same GPU, same model, same quantization, same workload type. Rows from different groups are never ranked together.

| Group | GPU | Model / quantization | Engine | Avg GPU power | Output tok/s | Tokens/J | Verification | Contributor | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A: RTX 5070 Ti, coder-iq1_m, chat traffic | RTX 5070 Ti (VRAM as reported: 15.9 GB) | coder-iq1_m, quantization N/A | Strata local host | 185.1 W | 29.85 | 0.1612 | self-measured, raw data published | dany4ok | [`data/`](data/) |

Submissions enter the leaderboard as self-measured. A maintainer has to reproduce a result before it can be called independently verified; automation never marks that status.

## Methodology

1. Passive monitoring only: `nvidia-smi` queries at 1 s intervals plus the inference engine's own request log. Nothing is sent to the model.
2. Requests are counted as they complete naturally. Window = first to last request timestamp. Active time = sum of request durations.
3. Energy during inference = mean measured power x active seconds. Idle power is reported separately, never mixed into the active figure.
4. Percentiles are computed over per-request output rates; system throughput is computed over the whole window.
5. Model, quantization, context size, output length, and concurrency are recorded per submission. Measurements from different models are never combined into one ranking.
6. Missing measurements stay N/A. Nothing is estimated or extrapolated.

## Scripts

- [`scripts/sample-gpu.ps1`](scripts/sample-gpu.ps1) — passive GPU sampling: utilization, VRAM, temperature, power draw, SM clocks, power limit. Read-only.
- [`scripts/analyze.ps1`](scripts/analyze.ps1) — recomputes totals, throughput, percentiles, energy, and tokens/J from the two CSV files.
- [`scripts/restore-clock.ps1`](scripts/restore-clock.ps1) — puts SM clocks back to driver defaults after a cap was applied by the user. Run it only yourself.
- [`scripts/validate_benchmarks.py`](scripts/validate_benchmarks.py) — checks submitted CSVs and issue bodies, recalculates tokens/J, rejects inconsistent math, flags suspicious rows.

## Privacy

Numerical benchmark telemetry only. No prompts, chat messages, API keys, credentials, client identifiers, or hostnames. Submitted datasets are stripped of identifying fields before publishing. Contributor submissions are accepted only after the contributor confirms the data is safe to publish.

## Contributing

Open a **Submit Benchmark Results** issue, or send a Pull Request that adds a CSV under `data/` using the benchmark template. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

GitHub Actions validate submissions on every Pull Request and on new issues. Validation reports math and completeness only; it never marks a result as independently verified.

## License

MIT. See [`LICENSE`](LICENSE).

