.PHONY: init install build test serve api dev clean

# ── Python ───────────────────────────────────────────────────
# Install Python dependencies
init:
	poetry install

# Run all Python tests
test:
	poetry run pytest

# ── Frontend ─────────────────────────────────────────────────
# Install npm dependencies
install:
	cd frontend && npm install

# Build Svelte app into frontend/dist/
build:
	cd frontend && npm run build

# ── Servers ──────────────────────────────────────────────────
# Production: build frontend then start Python server
serve: build
	poetry run uvicorn app:app --host 0.0.0.0 --port 8000

# Python API only (pair with `make dev` in a second terminal)
api:
	poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Vite dev server — hot-reload frontend, proxies /ws → localhost:8000
dev:
	cd frontend && npm run dev

# ── Cleanup ──────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -o -name "*.pyo" | xargs rm -f 2>/dev/null || true
	rm -rf .pytest_cache frontend/dist
