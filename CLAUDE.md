# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal Flask web application containerized with Docker, using `uv` for fast Python dependency management.

## Architecture

- **main.py**: Single-file Flask application serving a basic HTTP endpoint
- **Dockerfile**: Multi-stage build using official Python 3.10.19-slim base and `uv` for dependency installation
- **pyproject.toml**: Modern Python packaging configuration (PEP 621) declaring project metadata and dependencies
- **uv.lock**: Lockfile ensuring reproducible dependency resolution across environments

## Dependency Management with uv

This project uses `uv` (astral-sh/uv), a fast Rust-based Python package manager, instead of pip. Key differences:

### Adding Dependencies

```bash
# Add a package (auto-updates pyproject.toml and uv.lock)
uv add <package-name>

# Add with version constraint
uv add "flask>=3.0.0"

# Add development dependency
uv add --dev pytest
```

After adding dependencies, commit both `pyproject.toml` and `uv.lock` to git.

### Syncing Environment

```bash
# Install/sync dependencies from lockfile
uv sync

# Update all dependencies to latest compatible versions
uv sync --upgrade
```

### Removing Dependencies

```bash
uv remove <package-name>
```

## Docker Commands

### Build

```bash
docker build -t flask-uv-app .
```

### Run

```bash
docker run -p 5000:5000 flask-uv-app
```

The application will be accessible at `http://localhost:5000`.

## Key Docker Implementation Details

The Dockerfile uses `uv sync --frozen --no-dev` which:
- `--frozen`: Fails if lockfile is out of sync (ensures reproducibility)
- `--no-dev`: Excludes development dependencies from the image

The CMD uses `uv run python main.py` instead of direct `python main.py` to ensure execution within the managed virtual environment.

## Project Structure

```
/
├── main.py          # Flask application entry point
├── Dockerfile       # Container definition
├── pyproject.toml   # Dependency declarations
├── uv.lock          # Locked dependency versions (commit to git)
├── .dockerignore    # Excludes .venv, docs, etc. from Docker context
├── .gitignore       # Excludes .venv and Python artifacts
└── docs/            # Documentation (excluded from Docker image)
```

## Important Notes

1. **Always commit uv.lock**: The lockfile ensures identical dependency versions across all environments
2. **Virtual environment location**: `uv sync` creates `.venv/` locally; this directory is excluded from Docker builds
3. **Flask runs on 0.0.0.0:5000**: Required for Docker networking (listening on all interfaces)
