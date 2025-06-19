# ElizaOS Swarm Development Makefile

.PHONY: help install test coverage lint format demo validate clean
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "ElizaOS Swarm Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies for development
	pip install -e .[test,dev]
	pip install -r requirements.txt

test: ## Run all tests with coverage
	pytest tests/ -q -m "not slow" \
		--cov=agents --cov=eliza --cov=scheduler \
		--cov-report=term-missing --disable-warnings

test-unit: ## Run only unit tests
	pytest tests/ -v --ignore=tests/phase4/ -m "not integration"

test-integration: ## Run integration tests
	pytest tests/phase4/ -v --tb=short

coverage: ## Generate coverage report
	pytest tests/ --cov=agents --cov=eliza --cov=scheduler \
		--cov-report=html --cov-report=xml
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run linting checks
	black --check --diff agents/ eliza/ scheduler/ tests/
	isort --check-only --diff agents/ eliza/ scheduler/ tests/
	flake8 agents/ eliza/ scheduler/ tests/
	mypy agents/ eliza/ scheduler/

format: ## Format code
	black agents/ eliza/ scheduler/ tests/
	isort agents/ eliza/ scheduler/ tests/

validate: ## Validate persona configuration files
	python -m eliza.config.schema --persona-dir persona
	@echo "✅ All persona files validated successfully"

demo: ## Run swarm demo (dry run)
	python scripts/demo_swarm.py --dry --duration 60 --verbose

demo-quick: ## Run quick 30-second demo
	python scripts/demo_swarm.py --dry --duration 30

demo-live: ## Run live demo (requires Twitter API keys)
	python scripts/demo_swarm.py --live --duration 300 --verbose

security: ## Run security scan
	bandit -r agents/ eliza/ scheduler/ -f text

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: ## Build package
	python -m build

release-check: ## Check if ready for release
	@echo "🔍 Running release readiness checks..."
	$(MAKE) validate
	$(MAKE) test
	$(MAKE) lint
	$(MAKE) security
	@echo "✅ All checks passed! Ready for release."

# CI-specific targets
ci-test: ## Run tests in CI environment
	pytest tests/ -v --cov=agents --cov=eliza --cov=scheduler \
		--cov-report=xml --cov-fail-under=85 --tb=short

ci-demo: ## Run demo in CI environment
	timeout 60s python scripts/demo_swarm.py --dry --duration 30 || [ $$? -eq 124 ]

# Development workflow
dev-setup: install validate demo-quick ## Set up development environment
	@echo "🎉 Development environment ready!"
	@echo "Try: make test && make demo"

pre-commit: format lint test ## Run pre-commit checks
	@echo "✅ Pre-commit checks passed"

# Documentation
docs: ## Generate documentation
	@echo "📚 Documentation generation not implemented yet"
	@echo "Visit: https://elizaos.github.io/eliza"

# Version management
version: ## Show current version
	@python -c "import pyproject; print(pyproject.__version__)" 2>/dev/null || \
	grep -E '^version = ' pyproject.toml | cut -d'"' -f2

# Utilities
redis-start: ## Start Redis server (for testing)
	@if command -v redis-server >/dev/null 2>&1; then \
		redis-server --daemonize yes --port 6379; \
		echo "🔴 Redis started on port 6379"; \
	else \
		echo "❌ Redis not installed. Install with: apt install redis-server"; \
	fi

redis-stop: ## Stop Redis server
	@if pgrep redis-server >/dev/null; then \
		pkill redis-server; \
		echo "🔴 Redis stopped"; \
	else \
		echo "Redis not running"; \
	fi

# Performance testing
perf-test: ## Run performance tests
	@echo "⚡ Running performance tests..."
	python -m pytest tests/ -v -m "slow" --tb=short

# Phase verification
verify-phase4: ## Verify Phase 4 implementation
	python scripts/verify_phase4.py

# Git hooks
install-hooks: ## Install git hooks
	@echo "🪝 Installing git hooks..."
	echo "#!/bin/bash\nmake pre-commit" > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks installed" 