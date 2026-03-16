.PHONY: init test play serve dev clean

# Install dependencies and set up the virtual environment
init:
	poetry install

# Run all tests
test:
	poetry run pytest

# Run the CLI game
play:
	poetry run python main.py

# Run the web server (production)
serve:
	poetry run uvicorn app:app --host 0.0.0.0 --port 8000

# Run the web server with hot-reload (development)
dev:
	poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Remove generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -o -name "*.pyo" | xargs rm -f 2>/dev/null || true
	rm -rf .pytest_cache dist build *.egg-info
