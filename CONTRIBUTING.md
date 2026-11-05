# Contributing

You can add your own real-world measurements to this leaderboard.

## What is accepted

Numerical telemetry only:

- GPU model and VRAM
- NVIDIA driver version and operating system
- AI model, quantization, inference engine and version
- GPU power limit, clock configuration, mean power draw
- Generated output tokens, output tokens/sec, tokens/J
- Measurement duration, number of inference requests
- The raw CSV or a link to it
- How you measured

## What is never accepted

- Prompts, chat messages, transcripts
- API keys, tokens, credentials
- Client identifiers, hostnames, usernames, home paths
- GPU settings you want this repository to apply automatically

Before submitting, confirm that the data is safe to publish. Strip identifying columns from your CSV.

## Two ways to submit

1. **Issue form** — choose *Submit Benchmark Results* and fill every field. Write `N/A` for anything you could not measure. Do not estimate.
2. **Pull Request** — add `data/<your-name>-<date>.csv` following `data/schema.json`, one row per measurement group, and use the benchmark Pull Request template.

## How submissions are treated

- Automation checks CSV structure, required fields, and arithmetic (tokens/J recomputed from power, duration and tokens).
- Inconsistent or suspicious numbers are rejected or flagged for manual review.
- Every submission starts as **self-measured**. Only a maintainer who reproduces the measurement may mark it **independently verified**.
- Results are ranked only against rows in the same hardware, model, quantization, and workload group.

## Measurement rules

- Use your normal AI traffic. Do not generate synthetic benchmark prompts.
- Sample GPU power at 1 s intervals while requests run, and record idle power separately.
- Report active-inference and whole-window efficiency separately.
- Keep raw files, since reproduction needs them.

## Pull request checks

`python scripts/validate_benchmarks.py data/*.csv` must pass locally before you open a PR. CI runs the same check and never executes contributor scripts.

