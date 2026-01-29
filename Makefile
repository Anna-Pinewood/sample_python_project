.PHONY: format lint test check install pre-commit-install

# Install dev dependencies
install:
	uv pip install -e ".[dev]"

# Format code with ruff
format:
	ruff format src conf tests
	ruff check --fix src conf tests

# Lint code (ruff + mypy)
lint:
	ruff check src conf tests
	mypy src conf

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=src --cov-report=term-missing

# Full check: lint + test
check: lint test

# Install pre-commit hooks
pre-commit-install:
	pre-commit install
