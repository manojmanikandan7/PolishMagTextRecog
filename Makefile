.PHONY: help install install-dev build clean test lint format type-check run build-app

# Default target
help:
	@echo "Polish Magazine Text Recognition - Development Commands"
	@echo "====================================================="
	@echo ""
	@echo "Installation:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run          Run the interactive transcriber"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  type-check   Run type checking with mypy"
	@echo ""
	@echo "Building:"
	@echo "  build        Build the package"
	@echo "  build-app    Build standalone executable"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make install-dev  # Install dev dependencies"
	@echo "  make run          # Run the application"
	@echo "  make build-app    # Create executable"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Development
run:
	python src/text_recog/interactive_transcriber.py

# Building
build:
	python -m build

build-app:
	python3 build_app.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete