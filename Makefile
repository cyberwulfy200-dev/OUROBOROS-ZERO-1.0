# Makefile for OUROBOROS-ZERO

.PHONY: help install test run docker-build docker-run clean lint format

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
DOCKER := docker
DOCKER_COMPOSE := docker-compose
IMAGE_NAME := ouroboros-zero
IMAGE_TAG := 1.0-ZERO

# Default target
help:
	@echo "OUROBOROS-ZERO - Available Commands"
	@echo "===================================="
	@echo "  🐍 The Eternal Serpent Commands"
	@echo "===================================="
	@echo "  install        - Install dependencies"
	@echo "  test          - Run tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  run           - Run the replicator"
	@echo "  run-dev       - Run in development mode"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  docker-up     - Start with docker-compose"
	@echo "  docker-down   - Stop docker-compose"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with black"
	@echo "  clean         - Clean build artifacts"
	@echo "  backup        - Backup database"
	@echo "  logs          - Show logs"

# Installation
install:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Installing dependencies..."
	./venv/bin/$(PIP) install -r requirements.txt
	@echo "Creating directories..."
	mkdir -p data logs backups
	@echo "Installation complete!"

# Testing
test:
	@echo "Running tests..."
	$(PYTEST) tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term

test-quick:
	@echo "Running quick tests..."
	$(PYTEST) tests/ -v -x

# Running
run:
	@echo "🐍 Awakening OUROBOROS-ZERO..."
	$(PYTHON) src/ouroboros_zero.py

run-dev:
	@echo "🐍 Starting in development mode..."
	OUROBOROS_ENV=development $(PYTHON) src/ouroboros_zero.py

# Docker operations
docker-build:
	@echo "Building Docker image..."
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	$(DOCKER) tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):latest

docker-run:
	@echo "🐍 Releasing the serpent in Docker..."
	$(DOCKER) run -d \
		--name ouroboros \
		--network host \
		-v $$(pwd)/data:/app/data \
		-v $$(pwd)/logs:/app/logs \
		-v $$(pwd)/config:/app/config:ro \
		$(IMAGE_NAME):$(IMAGE_TAG)

docker-up:
	@echo "Starting services with docker-compose..."
	$(DOCKER_COMPOSE) up -d

docker-down:
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

docker-logs:
	@echo "Following Docker logs..."
	$(DOCKER_COMPOSE) logs -f

docker-clean:
	@echo "Cleaning Docker resources..."
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) rmi $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):latest

# Code quality
lint:
	@echo "Running linters..."
	flake8 src/ tests/
	pylint src/
	mypy src/

format:
	@echo "Formatting code with black..."
	black src/ tests/

# Maintenance
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/
	@echo "Clean complete!"

backup:
	@echo "Creating database backup..."
	mkdir -p backups
	cp data/replicator.db backups/replicator_$$(date +%Y%m%d_%H%M%S).db
	@echo "Backup created in backups/"

logs:
	@echo "Showing recent logs..."
	tail -50 logs/replicator.log

logs-follow:
	@echo "Following logs..."
	tail -f logs/replicator.log

# Database operations
db-init:
	@echo "Initializing database..."
	$(PYTHON) -c "import asyncio; from src.database_handler import DatabaseHandler; asyncio.run(DatabaseHandler().connect())"

db-stats:
	@echo "Database statistics..."
	$(PYTHON) -c "import asyncio; from src.database_handler import DatabaseHandler; db = DatabaseHandler(); asyncio.run(db.connect()); print(asyncio.run(db.get_clone_statistics())); asyncio.run(db.disconnect())"

# Setup development environment
dev-setup: install
	@echo "Setting up development environment..."
	./venv/bin/$(PIP) install black flake8 mypy pylint pytest-cov
	@echo "Development setup complete!"

# Create release
release:
	@echo "Creating OUROBOROS-ZERO release package..."
	mkdir -p release
	tar -czf release/OUROBOROS-ZERO_$(IMAGE_TAG).tar.gz \
		src/ config/ tests/ docs/ \
		requirements.txt Dockerfile docker-compose.yml \
		Makefile README.md
	@echo "Release package created: release/OUROBOROS-ZERO_$(IMAGE_TAG).tar.gz"
