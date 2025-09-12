# Development Guide

## Environment
- Python 3.13+
- Prefer uv for dependency management.

```
make setup
```

## Common Tasks
- Lint: `make lint`
- Format: `make format` (auto-fix: `make fix`)
- Type check: `make typecheck`
- Tests: `make test`
- Coverage: `make coverage`
- Build: `make build`

## Pre-commit Hooks
- Install: `make hooks-install`
- Run all: `make hooks-run`
- Update hooks: `make hooks-update`

## CI
- CI: `.github/workflows/ci.yml`
- Release: `.github/workflows/release.yml`
- Publishing details: `docs/publishing.md`

