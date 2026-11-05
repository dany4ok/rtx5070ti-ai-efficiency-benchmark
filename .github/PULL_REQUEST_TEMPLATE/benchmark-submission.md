## Benchmark contribution

Add real-world measurement rows under \`data/\`.

- [ ] CSV follows \`data/schema.json\` (benchmark-submission-v1)
- [ ] No prompts, chat text, API keys, credentials, client identifiers, hostnames, or paths
- [ ] Model, quantization, engine, power limit, clocks, and workload recorded
- [ ] Missing measurements written as N/A, never estimated
- [ ] \`python scripts/validate_benchmarks.py data/*.csv\` passes locally
- [ ] Real inference traffic only, no synthetic benchmark prompts
- [ ] Contributor confirms the data is safe to publish

Verification status stays self-measured. CI checks structure and arithmetic only.

