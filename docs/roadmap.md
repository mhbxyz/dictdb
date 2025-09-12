# Roadmap

This roadmap focuses on concrete improvements and extensions derived from the current codebase. Use it to file issues, group milestones, and track progress.

## Prioritized Improvements
1) Concurrency & Thread Safety
- Add table‑scoped RW locks; guard CRUD and index updates; ensure `BackupManager` reads consistent snapshots.
- Optional snapshotting before save to reduce lock contention.
- Acceptance: no races between writes and save/backup; concurrent tests pass.

2) Robust, Atomic Persistence
- JSON/pickle: write to temp + `fsync` + atomic `replace()`; add `_meta` = `{format: "dictdb", version: 1}` and checksum.
- Strict loader: validate `_meta` and reject mismatches.
- Acceptance: crash simulations never corrupt files; loader detects invalid inputs.

3) Indexing & Simple Planner
- Use `SortedIndex` for range queries (`<, <=, >, >=`) and BETWEEN.
- Add composite and unique indexes; `rebuild_index(field)` and stats for selectivity hints.
- Acceptance: range filters avoid full scans; uniqueness enforced; benchmarks show speedups.

5) Schema & Validation
- Copy `schema` on `Table.__init__` before mutating; support `defaults`, `nullable`, coercion hooks, and field validators.
- Add unique constraints independent of PK.
- Acceptance: no caller side‑effects; helpful, typed errors; validation optional but predictable.

6) Primary Key Strategies
- Support `pk_generator: Callable[[], Any]`; guard auto‑int to integers; document monotonic guarantees.
- Acceptance: custom PK works across insert/update/delete; collision tests included.

7) On‑Disk Mode & Per‑Query Durability
- Open databases directly from a file (e.g., `DictDB.open(path, mode="ondisk")`) where each INSERT/UPDATE/DELETE is durably persisted.
- Add a lightweight WAL/journal (JSONL/NDJSON) recording operations; crash‑safe recovery on startup; periodic checkpoint/compaction to a full snapshot.
- Configurable sync policy: `sync="always"|"batch"|"os"` (fsync per op vs timed/batched flush); expose `commit()` for manual barriers.
- Backpressure and error handling: surface I/O errors to callers; ensure in‑memory and on‑disk states stay consistent or roll back.
- Acceptance: after each successful mutating call in durable mode, state survives process crash; recovery replays journal; compaction keeps file size bounded; benchmarks quantify overhead.


8) Backup Manager Enhancements
- Retention policy (max files/age), compression option, backoff on repeated failures.
- Skip backups if unchanged since last snapshot; expose `on_success`/`on_error` hooks.
- Acceptance: predictable retention; fewer redundant backups; surfaced errors.

9) Transactions & Batching
- Context‑manager transactions with rollback on error; batch insert/update with partial‑failure reporting.
- Acceptance: atomic multi‑record changes; property tests confirm invariants.

10) CLI
- Ship a `dictdb` CLI: `init`, `load <path>`, `query "<expr>"`, `export --format json|csv` with exit codes.
- Packaging via `pyproject.toml` `[project.scripts]`; integration tests under `tests/test_cli.py`.
- Acceptance: smoke tests pass; docs include examples.

11) Performance & Memory
- Stream JSON directly without building a large intermediate state; avoid unnecessary copies in `select()`.
- Optional fast JSON backend behind a feature flag; micro‑opt index paths.
- Acceptance: reduced peak memory during save; no API changes.


12) Developer Tooling & Scripts
- Dev productivity:
  - `scripts/run_all.py` One-shot ruff format && ruff check && mypy && pytest runner with nice summary and non-zero on failure,
  - `scripts/typecov.py` Combine MyPy + Coverage summary, failing if coverage or types fall below thresholds,
  - `scripts/changed_tests.py` Run only tests affected by recent git changes (maps changed paths to tests),
  - `scripts/repl.py` Small interactive REPL to create tables, insert/select, and inspect indexes for manual poking.
- Performance/load:
  - `scripts/bench_matrix.py` Run the benchmark across matrix of rows/iterations/seeds and write a JSON/CSV table,
  - `scripts/profile_select.py` cProfile/py-spy wrappers for hot queries; emits stats and optional flamegraph,
  - `scripts/memory_probe.py` Measure memory footprint across dataset sizes and operations (insert/select/save).
- QA/robustness:
  - `scripts/persist_stress.py` Repeated save/load cycles with randomized data and formats; checks integrity, timings,
  - `scripts/corrupt_fuzzer.py` Mutate saved JSON/pickle files (truncate/flip bytes) to ensure loader errors correctly,
  - `scripts/concurrency_stress.py`  Threaded writers + readers to shake out races; tunable threads/ops/duration,
  - `scripts/backup_sandbox.py` Exercise BackupManager with short intervals, induced failures, and retention policy simulation.
- Data/schema:
  - `scripts/gen_data.py` Generate realistic fixture datasets (users/products) to JSON/NDJSON; parameterized sizes and skew,
  - `scripts/schema_audit.py` Validate table schemas against sample data files; reports mismatches and stats.
- Docs/release:
  - `scripts/docs_check_links.py` Validate intra-repo doc links after restructures; prints broken links with suggestions,
  - `scripts/release_notes.py` Generate draft release notes from Conventional Commits since last tag; groups by type.
- CI/utility:
  - `scripts/ci_local.py` Mirror CI steps locally with the same commands/env; optional step selection,
  - `scripts/coverage_diff.py` Show coverage deltas compared to main (via last CI artifact or local baseline).
- Acceptance: each script has argparse `--help`, sensible exit codes, minimal logging by default, is cross‑platform, gets a Makefile target (when appropriate), and a short entry in docs.


## Nice‑To‑Haves
- Generated API docs (pdoc/Sphinx) with examples and tutorial notebooks.
- Export/import connectors (CSV, NDJSON) and a simple HTTP server for remote access.
- CI micro‑benchmarks with trend reporting.

## Notes
- Keep read paths fast with read locks and short critical sections.
- Add concurrency and corruption tests; include range‑index benchmarks.
