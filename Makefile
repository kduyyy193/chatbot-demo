PYTHON = python3
PIP = pip3
PACKAGES ?= fastapi uvicorn transformers torch pydantic-settings mypy pytest pytest-asyncio httpx numpy

install:
	@echo "Installing dependencies: $(PACKAGES)"
	@$(PIP) install $(PACKAGES)
	@echo "Updating requirements.txt..."
	@$(PIP) freeze > requirements.txt

run:
	@$(PYTHON) -m src.main

docker-up:
	@docker-compose up --build

docker-down:
	@docker-compose down

clean:
	@docker system prune -f

type-check:
	@echo "Running MyPy type checking..."
	@mypy src/

help:
	@echo "Available commands:"
	@echo "  make install [PACKAGES='lib1 lib2 ...'] - Install specified packages and update requirements.txt"
	@echo "  make run                        - Run the app locally (no Docker)"
	@echo "  make docker-up                  - Build and run with Docker Compose"
	@echo "  make docker-down                - Stop Docker Compose"
	@echo "  make clean                      - Clean unused Docker resources"
	@echo "  make type-check                 - Run MyPy type checking"
	@echo "  make help                       - Show this help message"
	@echo "Example: make install PACKAGES='requests numpy'"

.PHONY: install run docker-up docker-down clean type-check help