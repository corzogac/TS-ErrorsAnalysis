# Makefile for TS-ErrorsAnalysis

.PHONY: help build run stop clean test logs shell

help:
	@echo "TS-ErrorsAnalysis - Docker Commands"
	@echo ""
	@echo "  make build       - Build Docker image"
	@echo "  make run         - Run containers (development mode)"
	@echo "  make run-prod    - Run containers (production mode)"
	@echo "  make stop        - Stop containers"
	@echo "  make clean       - Remove containers and images"
	@echo "  make logs        - View container logs"
	@echo "  make shell       - Open shell in API container"
	@echo "  make test        - Run tests"
	@echo ""

build:
	docker-compose build

run:
	docker-compose up -d
	@echo "API running at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"

run-prod:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production API running at http://localhost:8000"

stop:
	docker-compose down
	docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

clean: stop
	docker-compose down -v --rmi local
	rm -rf data/*.db

logs:
	docker-compose logs -f

shell:
	docker-compose exec api /bin/bash

test:
	docker-compose exec api python -m pytest tests/

restart: stop run

# Development helpers
dev-install:
	pip install -r requirements.txt -r api/requirements.txt

dev-run:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
