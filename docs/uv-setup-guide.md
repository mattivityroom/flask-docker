# Setting up UV in Flask Docker Project

## What is UV?

`uv` is a blazingly fast Python package installer and resolver written in Rust. It's 10-100x faster than `pip` and is designed to be a drop-in replacement for `pip`, `pip-tools`, and `virtualenv`.

## Why Use UV in Docker?

1. **Faster builds**: Dependencies install 10-100x faster
2. **Better dependency resolution**: More reliable than pip
3. **Smaller images**: More efficient package management
4. **Modern tooling**: Supports `pyproject.toml` standard

## Current Project Issues

Your current Dockerfile has two bugs:
1. References `requirements.txt` which doesn't exist
2. References `app.py` but your file is `main.py`

We'll fix these while setting up `uv`.

---

## UV Sync vs UV Pip Install

There are two ways to use `uv` in Docker. This guide uses the **modern `uv sync` approach**.

### Option 1: `uv sync` (Recommended - what this guide uses)
```dockerfile
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "python", "main.py"]
```
**Pros:**
- ✅ Creates a `uv.lock` file for exact reproducibility
- ✅ Everyone gets the same dependency versions (local, CI, production)
- ✅ Modern, future-proof approach
- ✅ Better for teams and production deployments

**Cons:**
- ⚠️ Requires running `uv sync` locally first
- ⚠️ Need to commit `uv.lock` to git

### Option 2: `uv pip install` (Simpler but less reproducible)
```dockerfile
RUN uv pip install --system --no-cache .
CMD ["python", "main.py"]
```
**Pros:**
- ✅ Drop-in replacement for pip
- ✅ No lockfile needed
- ✅ Simpler for small projects

**Cons:**
- ❌ Dependency versions can drift over time
- ❌ "Works on my machine" problems
- ❌ Less reproducible builds

**Our choice:** We use `uv sync` because reproducibility is critical for Docker deployments!

---

## Step-by-Step Implementation Guide

### Step 1: Create `pyproject.toml`

Create a file named `pyproject.toml` in the root of your project with this content:

```toml
[project]
name = "flask-docker"
version = "0.1.0"
description = "Flask application running in Docker"
requires-python = ">=3.10"
dependencies = [
    "flask>=3.0.0",
]
```

**What this does:**
- Defines your project metadata
- Lists Flask as a dependency
- Specifies Python version requirement
- This is the modern Python packaging standard (PEP 621)

---

### Step 2: Generate the Lockfile (Do this locally first!)

Before updating your Dockerfile, you need to generate a `uv.lock` file on your local machine:

```bash
# Install uv locally if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Generate the lockfile from pyproject.toml
uv sync
```

This creates a `uv.lock` file that locks your dependencies to exact versions. **Commit this file to git!**

**Why?**
- Ensures everyone (and every Docker build) gets the exact same dependency versions
- Prevents "works on my machine" issues
- Critical for reproducible builds

---

### Step 3: Update Your Dockerfile

Replace the content of your `Dockerfile` with:

```dockerfile
# Use official Python runtime as a parent image
FROM python:3.10.19-slim

# Copy uv binary from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory in the container
WORKDIR /app

# Copy dependency files (both pyproject.toml and uv.lock)
COPY pyproject.toml uv.lock ./

# Sync dependencies using the lockfile (creates a .venv)
RUN uv sync --frozen --no-dev

# Copy the rest of the application code
COPY . .

# Expose the port your Flask app listens on
EXPOSE 5000

# Run the Flask application using uv run
CMD ["uv", "run", "python", "main.py"]
```

**Key changes explained:**

1. `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv`
   - Copies the uv binary from the official uv Docker image
   - Multi-stage copy pattern for minimal overhead

2. `COPY pyproject.toml uv.lock ./`
   - Copies BOTH the dependency declaration AND the lockfile
   - Leverages Docker layer caching (dependencies rarely change)
   - The lockfile ensures exact reproducibility

3. `RUN uv sync --frozen --no-dev`
   - `--frozen`: Use the lockfile as-is, fail if it's out of date
   - `--no-dev`: Skip development dependencies (testing, linting, etc.)
   - Creates a `.venv` directory with all dependencies

4. `CMD ["uv", "run", "python", "main.py"]`
   - Uses `uv run` to execute Python in the managed environment
   - No need to activate the virtual environment manually
   - Fixed: Changed from `app.py` to `main.py`

---

### Step 4: (Optional) Create `.dockerignore`

Create a `.dockerignore` file to exclude unnecessary files from Docker builds:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.git
.gitignore
.DS_Store
docs/
.venv/
```

**Why?**
- Reduces build context size
- Faster builds
- Smaller images

**Important notes:**
- We exclude `.venv/` because `uv sync` creates a fresh virtual environment in Docker
- Do NOT exclude `uv.lock` - it's critical for reproducible builds!
- The `docs/` folder is excluded to keep the image smaller

---

## How to Build and Run

### Build the Docker image:
```bash
docker build -t flask-uv-app .
```

### Run the container:
```bash
docker run -p 5000:5000 flask-uv-app
```

### Test it:
Open your browser and go to: `http://localhost:5000`

You should see: "Hello from Flask in a Docker container!"

---

## Adding More Dependencies

### Method 1: Using `uv add` (Recommended!)

The easiest way to add dependencies is using `uv add`:

```bash
# Add a single dependency
uv add requests

# Add multiple dependencies
uv add requests python-dotenv

# Add with specific version
uv add "flask==3.0.0"

# Add development dependencies (testing, linting)
uv add --dev pytest black ruff
```

**What `uv add` does:**
- ✅ Automatically updates `pyproject.toml`
- ✅ Automatically updates `uv.lock`
- ✅ Installs the package locally

Then just commit and rebuild:

```bash
# Commit changes
git add pyproject.toml uv.lock
git commit -m "Add requests dependency"

# Rebuild Docker image
docker build -t flask-uv-app .
```

### Method 2: Manual Edit (Alternative)

If you prefer to edit manually:

**Step 1:** Edit `pyproject.toml`:

```toml
[project]
name = "flask-docker"
version = "0.1.0"
description = "Flask application running in Docker"
requires-python = ">=3.10"
dependencies = [
    "flask>=3.0.0",
    "requests>=2.31.0",      # Add this
    "python-dotenv>=1.0.0",  # Add this
]
```

**Step 2:** Regenerate the lockfile:

```bash
uv sync
```

**Step 3:** Commit and rebuild:

```bash
git add pyproject.toml uv.lock
git commit -m "Add requests and python-dotenv dependencies"
docker build -t flask-uv-app .
```

### Other Useful Commands

```bash
# Remove a dependency
uv remove requests

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add flask --upgrade

# See what's installed
uv pip list
```

---

## Troubleshooting

### Issue: "uv: command not found"
**Solution**: Make sure the COPY --from line is correct and you have internet access to pull the uv image.

### Issue: "No module named 'flask'"
**Solution**: Check that `uv sync` ran successfully during build. Look for errors in build logs.

### Issue: "lockfile is out of date"
**Solution**: Run `uv sync` locally to regenerate `uv.lock`, then commit it to git and rebuild.

### Issue: "COPY failed: file not found: uv.lock"
**Solution**: You forgot to generate the lockfile! Run `uv sync` locally first (see Step 2).

### Issue: Build is slow
**Solution**:
- Make sure you copy `pyproject.toml` and `uv.lock` before copying all code (layer caching)
- Docker caches layers, so dependency installation should be fast on subsequent builds

### Issue: "ModuleNotFoundError" at runtime
**Solution**: Make sure you're using `uv run` in the CMD, not just `python`. The virtual environment needs to be activated.

---

## Performance Comparison

**Before (with pip):**
```
Installing dependencies... 45 seconds
```

**After (with uv):**
```
Installing dependencies... 2-5 seconds
```

---

## Next Steps

Once you have this working, you can:
1. Add a `docker-compose.yml` for easier management
2. Set up environment variables with `.env` files
3. Add more Flask routes and features
4. Set up a database connection
5. Create a production-ready Dockerfile with multi-stage builds

---

## Quick Reference

### First-time setup:
```bash
# 1. Create pyproject.toml (see Step 1)
# 2. Install uv locally
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Generate lockfile
uv sync

# 4. Update Dockerfile (see Step 3)
# 5. Build and run
docker build -t flask-uv-app .
docker run -p 5000:5000 flask-uv-app
```

### When adding dependencies:
```bash
# 1. Add dependency (auto-updates pyproject.toml and uv.lock)
uv add requests

# 2. Commit changes
git add pyproject.toml uv.lock
git commit -m "Add requests dependency"

# 3. Rebuild Docker image
docker build -t flask-uv-app .
```

### Common uv commands:
```bash
# Add dependencies
uv add flask                    # Add latest version
uv add "flask>=3.0.0"          # Add with version constraint
uv add --dev pytest            # Add dev dependency
uv remove requests             # Remove dependency

# Sync and update
uv sync                        # Install/update from lockfile
uv sync --upgrade              # Update all dependencies

# List packages
uv pip list                    # Show installed packages
```

### Key files to commit to git:
- ✅ `pyproject.toml` - Your dependency declarations
- ✅ `uv.lock` - Locked dependency versions (critical!)
- ✅ `Dockerfile` - Your container definition
- ✅ `.dockerignore` - Build optimization
- ❌ `.venv/` - Never commit this (add to .gitignore)

---

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv Docker Guide](https://docs.astral.sh/uv/guides/integration/docker/)
- [Python Packaging Guide (pyproject.toml)](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
