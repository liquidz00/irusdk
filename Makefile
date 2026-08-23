SHELL 		:= /bin/bash
UV			:= uv
VENV_DIR	:= .venv

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install:  ## Install with default dependencies
	$(UV) sync

install-dev:  ## Install with dev dependencies
	$(UV) sync --extra dev

uninstall:  ## Remove the .venv directory
	rm -rf $(VENV_DIR)

clean:  ## Remove caches, build artifacts, and the .venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf .venv coverage/ dist/ build/ *.egg-info .coverage htmlcov/ docs/_build/

lint:  ## Check Python formatting + ruff lint
	$(UV) run ruff format --check .
	$(UV) run ruff check .

format:  ## Auto-format Python files
	$(UV) run ruff format .
	$(UV) run ruff check . --fix

lock:  ## Refresh uv.lock without upgrading dependencies
	$(UV) lock

upgrade:  ## Upgrade dependencies in uv.lock and re-sync
	$(UV) lock --upgrade
	$(UV) sync --extra dev

pre-commit-install:  ## Install pre-commit hooks
	$(UV) run pre-commit install

pre-commit-run:  ## Run pre-commit hooks against every file in the repo
	$(UV) run pre-commit run --all-files

test:  ## Run the unit test suite
	$(UV) run pytest tests/ -m "not integration"

test-integration:  ## Run integration tests against a live Iru tenant
	$(UV) run pytest tests/ -m integration

test-cov:  ## Run tests with terminal coverage report
	$(UV) run pytest tests/ -m "not integration" --cov=src --cov-report=term-missing

test-cov-html:  ## Generate HTML coverage report under coverage/htmlcov/
	$(UV) run pytest tests/ -m "not integration" --cov=src --cov-report=html
	@echo "Coverage report generated in coverage/htmlcov/index.html"

docs: install-dev  ## Build Sphinx documentation into docs/_build/
	# -W matches .readthedocs.yaml's fail_on_warning, so RTD can't fail on a warning that passed here.
	$(UV) run sphinx-build -b html -W --keep-going docs/ docs/_build/

build:  ## Build sdist and wheel under dist/
	$(UV) build --sdist --wheel
