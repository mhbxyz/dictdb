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

4) Query DSL & Results
- Add `IN`, `contains`, `startswith/endswith`, `order_by`, `limit/offset`, projections with aliases.
- Provide a tiny expression parser reused by the CLI (string → `Query`).
- Acceptance: new operators covered by tests; deterministic ordering and pagination.

5) Schema & Validation
- Copy `schema` on `Table.__init__` before mutating; support `defaults`, `nullable`, coercion hooks, and field validators.
- Add unique constraints independent of PK.
- Acceptance: no caller side‑effects; helpful, typed errors; validation optional but predictable.

6) Primary Key Strategies
- Support `pk_generator: Callable[[], Any]`; guard auto‑int to integers; document monotonic guarantees.
- Acceptance: custom PK works across insert/update/delete; collision tests included.


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


## Nice‑To‑Haves
- Generated API docs (pdoc/Sphinx) with examples and tutorial notebooks.
- Export/import connectors (CSV, NDJSON) and a simple HTTP server for remote access.
- CI micro‑benchmarks with trend reporting.

## Notes
- Keep read paths fast with read locks and short critical sections.
- Add concurrency and corruption tests; include range‑index benchmarks.
