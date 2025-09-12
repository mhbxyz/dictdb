# Variables
UV ?= uv

.PHONY: help setup install-uv sync lint format fix typecheck test coverage build clean benchmark bench release-dry-run release-version-dry-run release check hooks-install hooks-run hooks-update

.DEFAULT_GOAL := help

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## ' Makefile | sort | awk 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

install-uv: ## Install uv via pip
	pip install $(UV)

setup: install-uv sync ## Install uv and sync dev dependencies

sync: ## Sync dependencies (including dev group)
	$(UV) sync --group dev

lint: ## Run Ruff lint checks
	$(UV) run ruff check .

format: ## Format code with Ruff formatter
	$(UV) run ruff format

fix: ## Auto-fix lint issues with Ruff
	$(UV) run ruff check --fix .

typecheck: ## Type-check with MyPy (strict)
	$(UV) run mypy --strict src/dictdb tests

test: ## Run tests with pytest
	$(UV) run pytest -q

coverage: ## Run tests with coverage and generate XML report
	$(UV) run coverage run -m pytest --maxfail=1 --disable-warnings -q
	$(UV) run coverage report -m
	$(UV) run coverage xml

build: ## Build sdist and wheel using Hatchling
	$(UV) pip install hatchling
	$(UV) run python -m hatchling build -t sdist -t wheel

clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist *.egg-info coverage.xml htmlcov .coverage

benchmark: ## Run the benchmark script
	$(UV) run python scripts/benchmark.py

# Benchmark with parameters (override with e.g. ROWS=20000 ITERATIONS=20 AGE=30 SEED=123 OUT=results.json PROFILE=1)
ROWS ?= 10000
ITERATIONS ?= 10
AGE ?= 30
SEED ?= 42
OUT ?=
PROFILE ?=

bench: ## Run the benchmark with tunables and optional JSON output
	$(UV) run python scripts/benchmark.py \
		--rows $(ROWS) \
		--iterations $(ITERATIONS) \
		--age $(AGE) \
		--seed $(SEED) \
		$(if $(PROFILE),--profile,) \
		$(if $(OUT),--json-out $(OUT),)

release-dry-run: ## Semantic-release dry run (no publish)
	$(UV) run semantic-release publish --noop --skip-build

release-version-dry-run: ## Show next version without changes
	$(UV) run semantic-release version --noop

release: ## Run semantic-release (version, changelog, publish)
	$(UV) run semantic-release version
	$(UV) run semantic-release changelog
	$(UV) run semantic-release publish

check: format lint typecheck test ## Run formatter, linter, type checks, and tests

hooks-install: ## Install pre-commit and set up git hooks
	$(UV) pip install pre-commit
	$(UV) run pre-commit install --hook-type pre-commit --hook-type pre-push

hooks-run: ## Run all pre-commit hooks on the repository
	$(UV) run pre-commit run --all-files --show-diff-on-failure

hooks-update: ## Update hook versions defined in .pre-commit-config.yaml
	$(UV) run pre-commit autoupdate
