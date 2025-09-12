# CHANGELOG


## v1.4.0 (2025-09-12)

### Bug Fixes

- **logging, database**: Satisfy mypy strict and ruff; make check green
  ([`47266bd`](https://github.com/mhbxyz/dictdb/commit/47266bddd1a85ccfd4e3d1ad50a3f890d5f09380))

- logging: add LogFilter Protocol and type-safe sampling filter - logging: avoid passing
  format=None; always use explicit format strings - logging: conditionally apply filter to match
  Loguru’s expected types - logging: remove unused imports - database: remove redundant cast and
  unused ignore; use typed loaded_db - tooling: run make check (ruff, mypy --strict, pytest) — all
  pass

### Documentation

- Expand README quickstart; update API and logging docs
  ([`728691e`](https://github.com/mhbxyz/dictdb/commit/728691e7aac6bc46075da361b077787438ff4341))

- README: add full end-to-end quickstart (insert, index, query, update/delete, introspection,
  save/load) - Quickstart/Queries: replace Query with Condition in examples - API: document Table
  introspection (columns, count/size, len, indexed_fields, has_index, schema_fields,
  primary_key_name) and update signatures to use Condition - Logging: add JSON logging, debug
  sampling, and structured context examples - Overview: mention structured logging and introspection
  helpers - Roadmap: remove completed item 7

### Features

- **logging**: Add structured logging, JSON option, and info-level events
  ([`6539728`](https://github.com/mhbxyz/dictdb/commit/6539728438ab33e6a29fcb86d38470504baf0e3c))

- configure_logging: support JSON logs (serialize), debug sampling, and include {extra} context -
  table: bind structured context; add INFO logs for insert/update/delete and index creation -
  database: add INFO logs for init, create/drop table, save/load with table/record counts


## v1.3.0 (2025-09-12)

### Build System

- Add Makefile for common dev tasks (lint, test, typecheck, coverage, build, release)
  ([`85c0781`](https://github.com/mhbxyz/dictdb/commit/85c07818a8a213a5751db25fb2583aadc6b122e9))

- **version**: Expose runtime version from importlib.metadata
  ([`d76ca6c`](https://github.com/mhbxyz/dictdb/commit/d76ca6cdc2c09836962ff3846c8ddc48e0506cd9))

- Add dynamic __version__ in src/dictdb/__init__.py using importlib.metadata.version("dictdb") with
  a safe fallback for editable installs. - Keep semantic-release bumping project.version in
  pyproject.toml; add note to document the relationship.

### Chores

- Add pre-commit hooks and Makefile targets (install/run/update)
  ([`0dae3c9`](https://github.com/mhbxyz/dictdb/commit/0dae3c9a428407e3b9206de19208bd4b51c93d63))

### Code Style

- Apply Ruff formatting across codebase; test: remove unused import in logging test
  ([`42da13b`](https://github.com/mhbxyz/dictdb/commit/42da13bdd9a8ac2af1914149ef5ca31a7db41c7b))

### Continuous Integration

- Modernize workflow (setup-uv, caching, coverage artifact, build sanity)
  ([`3cdef32`](https://github.com/mhbxyz/dictdb/commit/3cdef3224ae15ae9c14182cb1b22ac1d3942e4f2))

- Split release workflow and add badges; docs: add publishing guide
  ([`057410c`](https://github.com/mhbxyz/dictdb/commit/057410c32fe8a00804464bd92c31df52139f184c))

### Documentation

- Add pre-commit usage to README (install, run, update)
  ([`31bcc67`](https://github.com/mhbxyz/dictdb/commit/31bcc677beb756ce21ab5df14dc3fcf412c6b177))

- Embed README docs list with relative links to docs/
  ([`93ad7b0`](https://github.com/mhbxyz/dictdb/commit/93ad7b08c51bc0134d95f7d4a95dbdff3040fbd1))

- Link README docs section to GitHub blob URLs
  ([`0e39522`](https://github.com/mhbxyz/dictdb/commit/0e3952297fc96d4b2d973100af50fc9be3473402))

- Split README into docs/ sections and simplify README with links
  ([`11cc5f6`](https://github.com/mhbxyz/dictdb/commit/11cc5f61b06a90a41f3adade8f898b6eeabcf4e8))

- Update README with persistence, backup, and indexing details
  ([`9fdeefb`](https://github.com/mhbxyz/dictdb/commit/9fdeefbb40e6b3f457f01e183b6c1ddb9f91bf9e))

- Added new sections for persistence (synchronous and asynchronous save/load) - Documented the
  BackupManager for automatic and immediate backups - Introduced indexing options with details on
  hash and sorted indexes - Updated the API reference to include new methods (async_save,
  async_load, create_index) - Revised usage examples and table of contents to reflect recent feature
  additions

This update ensures that the README is aligned with the current project capabilities.

- Update roadmap.md to reflect the evolution of the project
  ([`3a71d41`](https://github.com/mhbxyz/dictdb/commit/3a71d4116bf102344c0f5f313a9a50f865d1da5b))

- **roadmap**: Add CLI to run dictdb as a program
  ([`794a492`](https://github.com/mhbxyz/dictdb/commit/794a492fa3fad4a42bf00be313fcdc0b89fe0c99))

Adds a “Command‑Line Interface” roadmap item with proposed commands (init, load <path>, query
  "<expr>", export --format json|csv), packaging via [project.scripts], and acceptance criteria with
  smoke tests and docs examples.

- **roadmap**: Add structured roadmap with priorities, acceptance criteria, and nice-to-haves
  ([`6f93420`](https://github.com/mhbxyz/dictdb/commit/6f93420c2e5e2dbb86f96d83b08cec063134f9ba))

- **roadmap**: Refocus roadmap on actionable improvements
  ([`1c609c2`](https://github.com/mhbxyz/dictdb/commit/1c609c29d54e438765019798d2dfd5aea99ad5db))

- Remove “Strengths” section; concentrate on concurrency, atomic persistence, indexing/ planner, DSL
  features, schema/validation, PK strategies, logging/observability, backup retention,
  transactions/batching, CLI, perf/memory, and API/types. - Add concrete tasks with clear acceptance
  criteria and notes.

### Features

- **table**: Add columns(), count()/size(), len(), and introspection helpers
  ([`bc619ee`](https://github.com/mhbxyz/dictdb/commit/bc619ee31645e1ab09c59ac9a33fd1146a990355))

- Add Table.columns(), count() (alias size()), len(), indexed_fields(), has_index(),
  schema_fields(), primary_key_name() - Keep size() as alias to count() for compatibility - New
  tests: tests/test_table_introspection.py covering new helpers - Docs: remove completed roadmap
  item 12

Tests: 54 passed; mypy --strict clean

### Refactoring

- **condition**: Rename Query -> Condition; return PredicateExpr from field ops
  ([`f9162b2`](https://github.com/mhbxyz/dictdb/commit/f9162b243250b4d8adfdf844b51d5dc403727ade))

- Replace public Query wrapper with Condition; introduce PredicateExpr as internal predicate type. -
  Make Field comparison operators return PredicateExpr; update index optimization to accept
  Condition. - Update exports and all tests to new API. - tests(persistence): remove asyncio marker
  warnings by wrapping async calls with asyncio.run.


## v1.2.0 (2025-03-31)

### Features

- **benchmarking**: Add benchmark script for query performance with and without indexes
  ([`137cee1`](https://github.com/mhbxyz/dictdb/commit/137cee1261917cdaf95a5174d6639f57144c356b))

- Introduce `scripts/benchmark.py` which benchmarks DictDB's query performance using cProfile. -
  Implements three benchmarking scenarios: without an index, with a hash index and with a sorted
  index. - Populates a large dataset and measures the average execution time of a simple equality
  select query. - Module is fully documented in reStructuredText format and adheres to PEP8 with
  strong typing.

- **indexing**: Add support for user-defined indexes and automatic index updates
  ([`d7c9baa`](https://github.com/mhbxyz/dictdb/commit/d7c9baa2a0c00c9fa5fad2e07dc565664916259a))

- Implement create_index() in Table to allow creating indexes on specific fields. - Automatically
  update indexes on INSERT, UPDATE, and DELETE operations. - Accelerate SELECT queries by using
  indexes for simple equality conditions. - Update documentation and inline comments to reflect new
  indexing feature and changes.

This commit introduces indexing functionality to optimize SELECT queries.

- **indexing**: Use efficient index data structures for maintaining indices
  ([`d0604a3`](https://github.com/mhbxyz/dictdb/commit/d0604a3172f2a49644f7250a3aff7c8738ab3e87))

- Introduced a new module "index.py" defining an abstract IndexBase with two implementations:
  HashIndex (using Python's dict, a hash map) and SortedIndex (a simple sorted index using bisect to
  simulate B-tree behavior). - Updated Table.create_index() to accept an "index_type" parameter
  ("hash" or "sorted") and instantiate the corresponding index. - Refactored
  _update_indexes_on_insert, _update_indexes_on_update, and _update_indexes_on_delete in Table to
  delegate to the index object's methods. - Modified select() to use index.search() for simple
  equality conditions. - Added new tests in tests/test_indexing.py to verify the behavior of
  SortedIndex.

This commit evaluates and uses efficient data structures (hash maps and a sorted index) for
  maintaining indices and optimizes SELECT queries accordingly.


## v1.1.0 (2025-03-29)

### Documentation

- Add project logo to README.md
  ([`9b5ff9c`](https://github.com/mhbxyz/dictdb/commit/9b5ff9cdf6fdef139b899b727a22d6a1fb26bb4d))

- Add the project logo
  ([`965a44e`](https://github.com/mhbxyz/dictdb/commit/965a44ecda6f5997b60e900cc6daa5bfd665819e))

- Update documentation to remove useless line
  ([`5968ed0`](https://github.com/mhbxyz/dictdb/commit/5968ed0711431a65fc6676a99436ef531aaebca0))

### Features

- **persistence**: Add an automatic backup system that saves the current state of the database
  either periodically or immediately after significant changes
  ([`32647a8`](https://github.com/mhbxyz/dictdb/commit/32647a86da0ef3e390334f5df9a500f99b9e38d5))

The changes introducing an automatic backup system for DictDB. A new module,`backup.py`, defines a
  `BackupManager` that starts a background thread to periodically back up the database and also
  provides a manual trigger via `notify_change()`. Unit tests in `test_backup.py` verify both
  periodic and manual backup functionality.

- **persistence**: Add asynchronous save/load methods
  ([`974036d`](https://github.com/mhbxyz/dictdb/commit/974036deba9d44defca22acbc801ae2f141ca339))

Implemented async_save and async_load in DictDB using asyncio.to_thread to offload file I/O,
  ensuring that persistence operations do not block ongoing database activities. Updated
  documentation and unit tests (test_persistence.py) to cover asynchronous JSON and pickle
  operations.

- **persistence**: Add save/load functionality with pathlib support
  ([`149f471`](https://github.com/mhbxyz/dictdb/commit/149f471a3d978cea39f5caf1fed5341a6cc74df8))

- Implemented `save(filename: Union[str, Path], file_format: str)` and `load(filename: Union[str,
  Path], file_format: str)` in database.py. - Updated Table class with __getstate__ and __setstate__
  to exclude dynamic attributes from pickled state. - Refactored Field class to use a top-level
  _FieldCondition (with operator functions) ensuring picklability. - Updated relevant unit tests to
  cover persistence functionality.

### Testing

- **persistence**: Validate consistency across multiple save/load cycles
  ([`4054721`](https://github.com/mhbxyz/dictdb/commit/4054721e4a93fdcd52d5bc778f4a896371f6a383))

Added a new unit test in test_persistence.py to verify that DictDB maintains a consistent state
  across multiple save/load cycles using JSON persistence. This test saves and reloads the database
  repeatedly and compares the final state with the original.


## v1.0.0 (2025-03-26)

### Bug Fixes

- Add exceptions to handle duplicate keys and mising records
  ([`61b6ee4`](https://github.com/mhbxyz/dictdb/commit/61b6ee4cfd38a98acbf611659c7742edf116fd68))

- Add missing type annotations in tests to resolve mypy errors
  ([`d784dae`](https://github.com/mhbxyz/dictdb/commit/d784dae491f8b1285639998fdf0e7c47e16039cd))

- Specify `monkeypatch: pytest.MonkeyPatch` in `test_update_atomicity_partial_failure` for
  test_table.py - Annotate test function parameters and return types in test_table.py - Add
  `CaptureFixture[str]` type parameters in test_logging.py - Provide return type (and parameter
  types if any) for fixture functions in conftest.py

- Correct mypy path in CI workflow
  ([`d16bba3`](https://github.com/mhbxyz/dictdb/commit/d16bba3c815d189d3e9402090578eb51a7b3997f))

Update the mypy command to correctly target the 'src/dictdb' directory instead of 'dictdb', ensuring
  accurate type checks in the CI process. This resolves potential coverage and analysis issues
  during the workflow run.

- Implement record insertion with schema validation
  ([`9415cc4`](https://github.com/mhbxyz/dictdb/commit/9415cc4177a351c6554ce39d311ff45bddd9069f))

- Added SchemaValidationError to exceptions.py for handling schema mismatches. - Updated Table in
  core.py to accept an optional schema and validate records during insertion. - Updated __init__.py
  to export SchemaValidationError. - Extended unit tests in test_core.py to cover schema validation
  cases: - Valid record insertion with schema. - Handling of missing fields, extra fields, and wrong
  type values. - Auto-assignment of primary keys when using schema validation. - Verified that
  existing CRUD operations and query functionalities continue to work.

- **ci**: Fetch entire commit history for semantic-release
  ([`0f93b55`](https://github.com/mhbxyz/dictdb/commit/0f93b55650a0b7dcc10bf2ebaa7a4ecab735bcca))

- Updated the checkout step in ci.yml to use `fetch-depth: 0`. - Ensures semantic-release can
  reference older commits without encountering a missing SHA error.

- **ci**: Fix a missing part of the commands for semantic-release inside the CI workflow
  ([`3a546a3`](https://github.com/mhbxyz/dictdb/commit/3a546a30e9e7062532eafce0c9ccafd6121cfdf8))

- **core**: Add full type annotations, Query wrapper, and comprehensive module documentation
  ([`6a59bcc`](https://github.com/mhbxyz/dictdb/commit/6a59bccd8ae8847e0aabf4269cf9f9f1cf291f5a))

- Introduced Query class to safely wrap Condition objects and avoid implicit boolean conversion. -
  Added complete type annotations across all classes and methods (DictDB, Table, Field, Condition,
  Query). - Provided a detailed module-level docstring outlining purpose, components, and usage
  examples. - Refactored Table to store its name in "table_name" to enable dynamic Field access. -
  Implemented robust CRUD operations with proper exception handling (DuplicateKeyError,
  RecordNotFoundError).

- **logging**: Separate Loguru configuration and add unit tests for console/file logs
  ([`58e509f`](https://github.com/mhbxyz/dictdb/commit/58e509f0f43b206642d712a6590df9686385d821))

- Moved Loguru-based logging setup into a dedicated `logging.py` module. - Updated `core.py` to
  import and use the shared logger. - Added new tests verifying both console output (via capfd) and
  file-based logs. - Ensured CRUD operations and database initialization produce the expected log
  lines.

- **types**: Introduce centralized types module to unify shared definitions
  ([`9e735c3`](https://github.com/mhbxyz/dictdb/commit/9e735c30451289e3188c831d9d84fe51466a7410))

- Created types.py to house common type aliases: Record, Schema, Predicate - Updated references in
  condition.py, table.py, etc. to rely on these new aliases

### Chores

- Add CI Github Actions configuration
  ([`76ef306`](https://github.com/mhbxyz/dictdb/commit/76ef3064390548e021392ac77bd42d33c20d9d96))

- Add configuration file for tests
  ([`6161599`](https://github.com/mhbxyz/dictdb/commit/6161599f32eca36a0736264a7a5323b9f423bcac))

- Add coverage to project dependencies
  ([`0a29627`](https://github.com/mhbxyz/dictdb/commit/0a29627ee968e9a827832d8a7c364bccd9a4df0d))

- Add dictdb package
  ([`195f1a4`](https://github.com/mhbxyz/dictdb/commit/195f1a45a7a188550c5dbcae25adcbc11556f041))

- Add Jetbrains configuration to ignored files
  ([`c7806a9`](https://github.com/mhbxyz/dictdb/commit/c7806a9f770b4ff0df3e9a6b451529150061f450))

- Add mypy as a dev dependency and hatchling as a build system
  ([`992b8b9`](https://github.com/mhbxyz/dictdb/commit/992b8b94cc6e1c1cda631f972e2bed66bab11d56))

- Add python version file
  ([`a4fbee0`](https://github.com/mhbxyz/dictdb/commit/a4fbee069070ab20424f847a7f714d70b0430f6b))

- Add roadmap to docs
  ([`bc02708`](https://github.com/mhbxyz/dictdb/commit/bc027081b138452a2d701ff9ddf220e38857f392))

- Add uv configuration
  ([`4bebf69`](https://github.com/mhbxyz/dictdb/commit/4bebf69cb65c4bc146aa1d8a177303cf1800d0cf))

- Remove now useless core module
  ([`def27a5`](https://github.com/mhbxyz/dictdb/commit/def27a506d4fdf95dc761196af4aba5ad8d7f4c7))

- Remove testing step from CI for now
  ([`a9a8789`](https://github.com/mhbxyz/dictdb/commit/a9a8789b9a8e037206ea03acf5e6731b0bbdb35e))

- Update CI configuration to work properly
  ([`9b10413`](https://github.com/mhbxyz/dictdb/commit/9b1041388e7c47d4e4ceb6013b84832bc8cf92d7))

- Update readme and license with proper info
  ([`accb020`](https://github.com/mhbxyz/dictdb/commit/accb020ce990599749196d0484cf9b9048290ec8))

- **docs**: Add or update Sphinx-style docstrings for test methods
  ([`5eb0c5a`](https://github.com/mhbxyz/dictdb/commit/5eb0c5a5cce46c5777c24bdd16b59dbef0aae2b3))

- Added missing docstrings and updated existing ones for all test methods. - Ensured each method
  signature now has a clear Sphinx docstring including parameter descriptions. - Complies with
  project standards for clear, maintainable documentation.

- **tests**: Split test_core.py into separate condition, table, and database test files
  ([`8c9c452`](https://github.com/mhbxyz/dictdb/commit/8c9c452e3f8f9cec02538fdef574511c09d2b468))

- Moved Field/Condition/Query tests into test_condition.py - Moved Table CRUD + schema tests into
  test_table.py - Moved DictDB multi-table tests into test_database.py - Removed the now-obsolete
  test_core.py - Improved test organization and maintainability

### Continuous Integration

- Update CI pipeline to use uv for linting, type checks, and coverage
  ([`d1b5af6`](https://github.com/mhbxyz/dictdb/commit/d1b5af65a875febc76ec32a4517781650c59fb09))

- Installed uv and synced dependencies from uv.lock - Added Ruff lint check, mypy type check, and
  coverage-based tests - Ensured test, linting, and coverage steps are integrated into GitHub
  Actions

### Documentation

- Add or update Sphinx docstrings across modules
  ([`3d034b3`](https://github.com/mhbxyz/dictdb/commit/3d034b393f9aebb9a08e3859faef1f4c8c169750))

- Thoroughly reviewed and refined docstrings for all modules, functions, methods, and classes. -
  Ensured each docstring complies with standard Sphinx documentation style. - No functional changes;
  purely documentation improvements.

- Update roadmap.md
  ([`8305554`](https://github.com/mhbxyz/dictdb/commit/83055542d7bfdd7fe3829d27a71368243fefc0dc))

### Features

- **ci**: Integrate semantic-release and improve CI workflow
  ([`3679c10`](https://github.com/mhbxyz/dictdb/commit/3679c103ffd31a8efb9c28673c2d342ff3094ee5))

- Added a dedicated 'release' job that uses semantic-release to auto-bump the version, generate
  changelogs, and publish both GitHub releases and PyPI packages. - Updated pyproject.toml: - Added
  python-semantic-release to dev dependencies. - Configured [tool.semantic_release] to pull version
  from pyproject.toml, use 'main' branch, and automatically upload to PyPI. - Enabled major_on_zero
  and version_source to ensure correct SemVer handling. - Ensured GH_TOKEN and PYPI_TOKEN
  environment variables are used so that GitHub releases and PyPI publishing can occur in the
  release job.

This commit sets up fully automated semantic versioning and release processes for DictDB.

### Refactoring

- Refactor Table CRUD operations and auto-assign primary keys
  ([`5bbcdda`](https://github.com/mhbxyz/dictdb/commit/5bbcdda545c0c24dd044926dae8391c90be0e0d2))

- Update the insert method to auto-assign a primary key if missing by determining the next available
  integer key. - Rename CRUD methods by removing the '_record(s)' suffix; methods are now named
  insert, select, update, and delete. - Update tests to reflect these changes, ensuring proper
  auto-assignment and method naming.

- Restrict the creation of queries through the use of Condition
  ([`9a57b3e`](https://github.com/mhbxyz/dictdb/commit/9a57b3e6745d03f5901463e521f6f9411e79dc4b))

- **core**: Break out `core.py` into smaller modules while keeping `Table` & `Field` together
  ([`bf3fb51`](https://github.com/mhbxyz/dictdb/commit/bf3fb5182dbad1a9500f1785a438af05b59f50f4))

- Moved `Condition` and `Query` to `condition.py` - Created `table.py` for both `Table` and `Field`,
  since they’re closely related - Created `database.py` for the `DictDB` class - Updated
  `__init__.py` to re-export all public classes and functions - Removed the old `core.py` in favor
  of these new, focused modules

### Testing

- Update test suite for full DictDB module functionality and Query integration
  ([`82961c6`](https://github.com/mhbxyz/dictdb/commit/82961c68ec64549954cde612cfec23795c200940))

- Revised tests in test_core.py to use the new Query wrapper for condition expressions. - Expanded
  tests to cover all aspects of the module: Field operator overloading, Condition logic, Query
  combinations, and CRUD operations. - Updated conftest.py fixtures to create reliable Table and
  DictDB instances for testing. - Added tests for error cases to ensure proper exception raising and
  overall module stability.
