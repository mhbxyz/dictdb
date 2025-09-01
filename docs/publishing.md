# Publishing Workflow

This repository publishes to PyPI via GitHub Actions and python‑semantic‑release. Releases are driven by Conventional Commits on the `main` branch.

## How It Works
- Trigger: push to `main` runs `.github/workflows/release.yml`.
- Quality gates: Ruff lint, MyPy type check, and pytest coverage run.
- Versioning: `semantic-release` determines the next version from commit messages and updates `pyproject.toml` and `CHANGELOG.md`.
- Publishing: `semantic-release publish` creates a GitHub Release and uploads the built package to PyPI (Hatchling).

## Required Secrets
- `PYPI_TOKEN`: PyPI token with publish scope for the project.
- `GITHUB_TOKEN`: Provided automatically by GitHub (used for tags/Releases).

## Commit Conventions (summary)
- `feat:` → minor release; `fix:` → patch release; `feat!` or `BREAKING CHANGE:` in body → major release. Other types (`docs:`, `chore:`, `refactor:`) do not publish unless configured to.

## Files Involved
- Workflow: `.github/workflows/release.yml`
- Config: `pyproject.toml` `[tool.semantic_release]` (upload_to_pypi=true, branch=main)

## Local Dry‑Run
Preview next release without publishing:

```
uv run semantic-release publish --noop --skip-build
```

Or preview version only:

```
uv run semantic-release version --noop
```

## Troubleshooting
- No release created: ensure branch is `main` and commits follow Conventional Commits.
- Permission errors: verify `PYPI_TOKEN` is set in repo secrets; workflow permissions include `contents: write`.
- Version mismatch: confirm `pyproject.toml:version` matches the last released tag or let semantic‑release update it.

