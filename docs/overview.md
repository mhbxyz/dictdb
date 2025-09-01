# Overview

DictDB is an in‑memory, dictionary-based database system for Python. It provides SQL‑like CRUD operations, schema validation, logging, indexing, and a fluent interface for building complex query conditions.

## Features

- Multiple Tables: manage any number of in‑memory tables within a single DictDB.
- SQL‑like CRUD: insert, select, update, and delete records with a Pythonic API.
- Schema Validation: enforce data consistency with per‑table schemas.
- Condition/Query System: build complex filters with logical and comparison operators.
- Atomic Updates: validation failures roll back the entire update.
- Logging: Loguru integration with customizable sinks and levels.
- Persistence and Backup: save/load JSON or pickle; optional backup manager.
- Indexing: hash or sorted indices to speed up equality lookups.
- Testing: fully unit‑tested with pytest.

