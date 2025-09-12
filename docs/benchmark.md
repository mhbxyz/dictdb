Benchmarking DictDB
===================

This guide explains how to benchmark DictDB’s SELECT performance with and without indexes.

What it measures
- Average runtime of an equality filter on a single field (`age`).
- Three scenarios: no index, hash index, and sorted index.
- Deterministic dataset via a random seed for fair comparisons.

Script entry point
- Script: `scripts/benchmark.py`
- Query: `Condition(table.age == <AGE>)`
- Outputs average time per scenario and speedups vs. no index.

Quick start
- Default: `python scripts/benchmark.py`
- With parameters:
  - `python scripts/benchmark.py --rows 20000 --iterations 20 --age 30 --seed 123`
  - Profile: `python scripts/benchmark.py --profile`
  - JSON results: `python scripts/benchmark.py --json-out results.json`

Make targets
- Simple run: `make benchmark`
- Tunable run with optional JSON:
  - `make bench ROWS=20000 ITERATIONS=20 AGE=30 SEED=123`
  - Write JSON: `make bench OUT=results.json`
  - Profile: `make bench PROFILE=1`

Flags
- `--rows`: number of records (default 10000)
- `--iterations`: repetitions per scenario (default 10)
- `--age`: equality value used in the query (default 30)
- `--seed`: RNG seed for reproducible data (default 42)
- `--profile`: enable cProfile
- `--json-out`: write results to a JSON file

Notes
- The benchmark minimizes logging overhead to avoid skewing timings.
- The script returns a structured result internally for reuse in programmatic runs.

