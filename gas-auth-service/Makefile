.PHONY: run shell build up down restart logs test lint

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

shell:
	python

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	pytest

lint:
	# Add linting commands here (e.g., black, ruff)
	@echo "Linting..."
