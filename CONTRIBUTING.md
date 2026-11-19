# Contributing to Mockup Workflow

## Set up the environment

```bash
make setup   # creates .venv and installs dependencies
make test    # checks that everything works
make run     # starts the app in the browser
```

## Branches

- `main` always works and is what gets released.
- Each change goes in its own branch, created from `main`:
  - `feature/…` for something new, such as `feature/export-pdf`.
  - `fix/…` to fix a bug, such as `fix/inner-shadow`.
  - `docs/…` for documentation.
- When the change is finished and the tests pass, it is merged into `main`.

## Commits

- **Message:** in English, imperative mood and short. One summary line and, if needed, a paragraph explaining why.
  - Good: `Add saturation adjustment to nodes`
  - Bad: `changes`, `fix`, `wip`
- **Scope:** one commit per idea. Do not mix a fix with a new feature.
- **Data:** do not commit user data (gallery, workflows, results) or build output. `.gitignore` already excludes them.

## Before merging into `main`

1. `make test` passes.
2. If you change the engine (`engine.py`), check fidelity with a real PSD: `make test PSD=path.psd`, or
   `make check PSD=path.psd` to see the numbers. The mean error must stay below 1/255.
3. If you change the interface, review it in light and dark mode, and in a narrow window.
4. If you change the `.mwf` format, update [docs/file-format.md](docs/file-format.md) and keep reading older
   files. If older files stop opening, bump the format version in `version.py` and the
   MAJOR version.
5. Note the change in the `## [Unreleased]` section of the [CHANGELOG](CHANGELOG.md), under the right heading:
   Added, Changed, Fixed or Removed.

## Versions

Semantic versioning (`MAJOR.MINOR.PATCH`). The version lives only in `version.py`; everything else (app,
packaging, "About", CLI) reads it from there.

To release:

```bash
make release VERSION=1.1.0
```

This command:
- Checks that there are no uncommitted changes.
- Bumps the version and dates the CHANGELOG (it expects a `## [Unreleased]` section).
- Runs the tests.
- Builds the app and creates `releases/Mockup-Workflow-1.1.0-macOS.zip`.
- Creates the commit `Version 1.1.0` and the tag `v1.1.0`.

Released versions are listed with `git tag`, and the changes between two of them with
`git log v1.0.0..v1.1.0 --oneline`.

## Code style

- **Language:** commit messages, code comments, docstrings, user-facing messages, errors and UI texts are in
  English.
- **Python:**
  - Lines up to 120 characters.
- **Interface:**
  - HTML, CSS and JavaScript with no dependencies or build step.
  - Colors always through the `:root` variables (and their dark mode equivalents).
- **User-facing messages:** say what happened and how to fix it.
