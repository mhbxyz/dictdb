# Roadmap

This roadmap captures strengths, improvement opportunities, and concrete next steps gathered during a project review. Use it to open issues, group milestones, and track progress.

## Strengths
- Clear project structure (`src/`, `tests/`, focused modules), tidy public API.
- Solid pytest coverage across CRUD, schema, indexing, logging, persistence.
- Modern dev/CI: uv + lockfile, Makefile, pre-commit, split CI/Release, semantic‑release to PyPI.
- Features: fluent query DSL, atomic updates with rollback, Loguru integration, simple backups, JSON/pickle + async persistence.

## Prioritized Improvements
1) Concurrency & Backup Safety
- Add coarse RW‑lock at `DictDB` level; wrap CRUD/select/save/load for consistent snapshots.
- Optionally snapshot the DB (deep copy) before save to avoid long locks.
- Acceptance: backups never race with writes; tests simulate concurrent writes during save.

2) Persistence Robustness
- Atomic writes: write to temp file, then rename.
- Embed metadata in JSON: `{ "_meta": {"format": "dictdb", "version": 1}, ... }` for future migrations.
- Acceptance: corrupted/partial files avoided; loader validates `_meta`.

3) Indexing Beyond Equality
- Extend `SortedIndex` with range search; detect `<, <=, >, >=` in `select()`.
- (Optional) simple composite keys for multi‑field equality.
- Acceptance: range queries use index; measurable speedup in benchmarks.

4) Logging Consistency
- Unify Loguru formatting (f‑strings or `{}` style placeholders). Fix `configure_logging()` debug message.
- Acceptance: consistent logs; no stray `%s` placeholders.

5) Schema Ergonomics
- Copy provided `schema` in `Table.__init__` before mutation (PK insert).
- Document JSON‑persistence type limits; consider extension hooks.
- Acceptance: no caller side‑effects; clearer docs/tests.

6) Primary Key Generation
- Support optional `pk_generator: Callable[[], Any]`; default auto‑int guarded to int‑only.
- Acceptance: custom PK strategies work; errors clear for non‑int auto IDs.

7) Error Semantics Documentation
- Clarify that `update()`/`delete()` raise `RecordNotFoundError` on 0 matches; document rationale.
- Acceptance: API docs updated; tests assert behavior.

8) Types & API Polish
- Reduce `Any`/`cast` where feasible; add helpers like `Table.columns()` for discoverability.
- Acceptance: stricter MyPy passes unchanged; improved IDE hints.

9) Performance Nits
- Stream JSON directly to file; micro‑opt index maintenance already optimized on update.
- Acceptance: simpler I/O path; no behavior change.

## Nice‑To‑Haves
- Generated API docs (pdoc/Sphinx) under `docs/` to sync with code.
- Example notebooks for queries, indexing, backups.
- Lightweight benchmark target in CI (workflow_dispatch or nightly) reporting basic timings.

## Notes
- When implementing locks, keep read‑heavy selects fast (prefer read locks, short critical sections).
- Add tests for concurrent backup and for index‑backed range filters.
