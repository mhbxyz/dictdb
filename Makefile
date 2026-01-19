# DictDB Development Makefile
# ===========================

UV ?= uv
PYTHON ?= $(UV) run python
PYTEST ?= $(UV) run pytest

.PHONY: help
.DEFAULT_GOAL := help

help: ## Show available targets
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup & Dependencies:"
	@grep -E '^(setup|sync|clean):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Code Quality:"
	@grep -E '^(check|format|lint|fix|typecheck):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Testing:"
	@grep -E '^(test|test-v|test-fast|coverage):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Benchmarks:"
	@grep -E '^(benchmark|bench):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Documentation:"
	@grep -E '^(docs|docs-serve):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Git Hooks:"
	@grep -E '^(hooks-install|hooks-run|hooks-update):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Build:"
	@grep -E '^(build):.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Setup & Dependencies
# =============================================================================

.PHONY: setup sync clean

setup: ## First-time setup: install uv and sync dependencies
	pip install $(UV)
	$(UV) sync --group dev
	$(UV) run pre-commit install --hook-type pre-commit --hook-type pre-push
	@echo "\n✓ Setup complete. Run 'make check' to verify."

sync: ## Sync dependencies (including dev group)
	$(UV) sync --group dev

clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf build dist *.egg-info
	rm -rf coverage.xml htmlcov .coverage
	rm -rf __pycache__ **/__pycache__
	rm -rf site
	@echo "✓ Cleaned"

# =============================================================================
# Code Quality
# =============================================================================

.PHONY: check format lint fix typecheck

check: format lint typecheck test ## Run all checks (format, lint, typecheck, test)

format: ## Format code with Ruff
	$(UV) run ruff format

lint: ## Run Ruff linter
	$(UV) run ruff check .

fix: ## Auto-fix lint issues
	$(UV) run ruff check --fix .

typecheck: ## Type-check with MyPy (strict)
	$(UV) run mypy --strict src/dictdb tests

# =============================================================================
# Testing
# =============================================================================

.PHONY: test test-v test-fast coverage

test: ## Run all tests
	$(PYTEST) -q

test-v: ## Run tests with verbose output
	$(PYTEST) -v

test-fast: ## Run tests, stop on first failure
	$(PYTEST) -x -q

coverage: ## Run tests with coverage report
	$(UV) run coverage run -m pytest --maxfail=1 --disable-warnings -q
	$(UV) run coverage report -m
	$(UV) run coverage xml
	@echo "\n✓ Coverage report: coverage.xml"

# =============================================================================
# Benchmarks
# =============================================================================

ROWS ?= 10000
ITERATIONS ?= 10
AGE ?= 30
SEED ?= 42
OUT ?=
PROFILE ?=

.PHONY: benchmark bench

benchmark: ## Run benchmark with default parameters
	$(PYTHON) scripts/benchmark.py

bench: ## Run benchmark with custom parameters (ROWS, ITERATIONS, AGE, SEED, OUT, PROFILE)
	$(PYTHON) scripts/benchmark.py \
		--rows $(ROWS) \
		--iterations $(ITERATIONS) \
		--age $(AGE) \
		--seed $(SEED) \
		$(if $(PROFILE),--profile,) \
		$(if $(OUT),--json-out $(OUT),)

# =============================================================================
# Documentation
# =============================================================================

.PHONY: docs docs-serve

docs: ## Build documentation
	$(UV) run --group docs mkdocs build --strict
	@echo "\n✓ Documentation built in site/"

docs-serve: ## Serve documentation locally
	$(UV) run --group docs mkdocs serve

# =============================================================================
# Git Hooks
# =============================================================================

.PHONY: hooks-install hooks-run hooks-update

hooks-install: ## Install pre-commit hooks
	$(UV) pip install pre-commit
	$(UV) run pre-commit install --hook-type pre-commit --hook-type pre-push
	@echo "✓ Hooks installed"

hooks-run: ## Run all hooks on all files
	$(UV) run pre-commit run --all-files --show-diff-on-failure

hooks-update: ## Update hook versions
	$(UV) run pre-commit autoupdate

# =============================================================================
# Build
# =============================================================================

.PHONY: build

build: ## Build sdist and wheel
	$(UV) pip install hatchling
	$(PYTHON) -m hatchling build -t sdist -t wheel
	@echo "\n✓ Built in dist/"
