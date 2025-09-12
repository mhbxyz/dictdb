# Roadmap

This roadmap focuses on concrete improvements and extensions derived from the current codebase. Use it to file issues, group milestones, and track progress.

## Improvements
2) Transactions & Batching
- Transaction layer: add explicit `begin_transaction()`, `commit_transaction()`, `rollback_transaction()` APIs, plus context‑manager sugar for `with db.transaction(): ...`.
- Atomicity & isolation: treat multiple INSERT/UPDATE/DELETE operations as a single atomic unit; consider simple table‑scoped locking or optimistic concurrency to prevent conflicts under concurrent access.
- Logging & recovery: record per‑transaction operation logs to enable precise rollback and aid debugging; ensure rollback restores both table data and indexes.
- Batching: support batch insert/update with partial‑failure reporting when not inside a transaction; encourage transaction use for all‑or‑nothing semantics.
- Testing: simulate concurrent readers/writers and verify isolation; property tests confirm invariants and atomicity across failures.
- Acceptance: transactions preserve integrity under concurrency; rollbacks are lossless; benchmarks quantify overhead of isolation mechanisms.

3) Robust, Atomic Persistence
- JSON/pickle: write to temp + `fsync` + atomic `replace()`; add `_meta` = `{format: "dictdb", version: 1}` and checksum.
- Strict loader: validate `_meta` and reject mismatches.
- Acceptance: crash simulations never corrupt files; loader detects invalid inputs.

4) On‑Disk Mode & Per‑Query Durability
- Open databases directly from a file (e.g., `DictDB.open(path, mode="ondisk")`) where each INSERT/UPDATE/DELETE is durably persisted.
- Add a lightweight WAL/journal (JSONL/NDJSON) recording operations; crash‑safe recovery on startup; periodic checkpoint/compaction to a full snapshot.
- Configurable sync policy: `sync="always"|"batch"|"os"` (fsync per op vs timed/batched flush); expose `commit()` for manual barriers.
- Backpressure and error handling: surface I/O errors to callers; ensure in‑memory and on‑disk states stay consistent or roll back.
- Acceptance: after each successful mutating call in durable mode, state survives process crash; recovery replays journal; compaction keeps file size bounded; benchmarks quantify overhead.

5) Indexing & Simple Planner
- Use `SortedIndex` for range queries (`<, <=, >, >=`) and BETWEEN.
- Add composite and unique indexes; `rebuild_index(field)` and stats for selectivity hints.
- Acceptance: range filters avoid full scans; uniqueness enforced; benchmarks show speedups.

6) Performance & Memory
- Stream JSON directly without building a large intermediate state; avoid unnecessary copies in `select()`.
- Optional fast JSON backend behind a feature flag; micro‑opt index paths.
- Acceptance: reduced peak memory during save; no API changes.

7) Schema & Validation
- Copy `schema` on `Table.__init__` before mutating; support `defaults`, `nullable`, coercion hooks, and field validators.
- Add unique constraints independent of PK.
- Acceptance: no caller side‑effects; helpful, typed errors; validation optional but predictable.

8) Primary Key Strategies
- Support `pk_generator: Callable[[], Any]`; guard auto‑int to integers; document monotonic guarantees.
- Acceptance: custom PK works across insert/update/delete; collision tests included.

9) Backup Manager Enhancements
- Retention policy (max files/age), compression option, backoff on repeated failures.
- Skip backups if unchanged since last snapshot; expose `on_success`/`on_error` hooks.
- Acceptance: predictable retention; fewer redundant backups; surfaced errors.

10) CLI
- Ship a `dictdb` CLI: `init`, `load <path>`, `query "<expr>"`, `export --format json|csv` with exit codes.
- Packaging via `pyproject.toml` `[project.scripts]`; integration tests under `tests/test_cli.py`.
- Acceptance: smoke tests pass; docs include examples.

11) Advanced Query Capabilities
- Aggregate functions: explore SQL-like aggregates (e.g., COUNT, SUM, AVG, MIN, MAX) operating over in-memory dictionaries and projections; design API that composes with `where`, `order_by`, and `grouping` primitives.
- JOIN-like operations: investigate joining over nested/related dictionaries (e.g., parent->child keys) to mimic relational behavior; start with equi-joins on primary/foreign key patterns; consider denormalized materialized views.
- Subqueries and complex filters: evaluate nested queries and subselects reusable inside `where` clauses and projections; define evaluation order and cost model for small datasets.
- User-defined functions (UDFs): allow safe, user-supplied callables in `where` and computed columns with a constrained signature and optional sandboxing.
- Performance & scalability: prototype each feature, measure overhead vs. current indexed scans, and plan staged rollout gated by benchmarks and user feedback.
- Acceptance: documented APIs with examples; unit tests covering correctness and edge cases; micro-benchmarks showing acceptable overhead (or feature flags to disable); graceful fallbacks when features are unsupported.

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
